from __future__ import annotations
import typing

from epomakercontroller.commands.EpomakerCommand import EpomakerCommand
from epomakercontroller.epomakercontroller import EpomakerConfig, EpomakerController

if typing.TYPE_CHECKING:
    from epomakercontroller.configs.configs import Config


class FakeEpomakerController(EpomakerController):
    """
    This fixture should help in testing low-level functionality.
    Overrides some behaviour, related to HID devices. This approach
    will disconnect unit tests from physical devices.
    """

    def __init__(self,  config_main: Config, dry_run: bool = False) -> None:
        self.config = EpomakerConfig(config_main)
        self.dry_run = dry_run
        self.opened_in_info_mode = False

        self.is_ready = False

        self.commands = []

    def open_device(self, only_info: bool = False):
        self.opened_in_info_mode = only_info
        self.is_ready = True

    def close_device(self):
        self.is_ready = False

    def _send_command(self, command: EpomakerCommand):
        self.commands.append(command)
