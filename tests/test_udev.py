import os
import stat
import subprocess

from epomakercontroller.configs.configs import ConfigType, get_all_configs
from epomakercontroller.configs.constants import OLD_RULE_FILE_PATH, RULE_FILE_PATH
from epomakercontroller.epomakercontroller import EpomakerController


def make_controller() -> EpomakerController:
    return EpomakerController(get_all_configs()[ConfigType.CONF_MAIN], dry_run=True)


def test_rule_covers_every_keyboard_without_world_access():
    rule = make_controller().udev_rule()
    assert 'ATTRS{idProduct}=="4010|4015|5002|4011|4016"' in rule
    assert 'TAG+="uaccess"' in rule
    assert "0666" not in rule
    assert os.path.basename(RULE_FILE_PATH) < "73-seat-late.rules"
    lines = rule.splitlines()
    assert lines[0].startswith("#")
    assert lines[1].startswith('SUBSYSTEM=="usb", ')
    assert "GROUP=" not in rule


def test_rule_is_installed_owned_by_root(monkeypatch):
    calls = []
    temp_files = []

    def fake_run(command, check):
        assert check
        calls.append(command)
        if "install" in command:
            source = command[-2]
            temp_files.append(source)
            assert not stat.S_IMODE(os.stat(source).st_mode) & 0o077

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    make_controller().generate_udev_rule()

    assert calls[0][:7] == ["install", "-o", "root", "-g", "root", "-m", "0644"]
    assert calls[0][-1] == RULE_FILE_PATH
    assert ["rm", "-f", OLD_RULE_FILE_PATH] in calls
    assert not any(command[0] == "mv" for command in calls)
    assert not os.path.exists(temp_files[0])
