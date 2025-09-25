import os
from pathlib import Path
from epomakercontroller.configs import configs
from epomakercontroller.configs.configs import ConfigType


def test_create_config(monkeypatch):
    def fake_get_directory() -> Path:
        current_dir = Path(os.path.abspath(__file__)).parent
        return current_dir / "data" / "config"

    configs.create_default_main_config(fake_get_directory()/"config.json")
    assert os.path.exists(Path(os.path.abspath(__file__)).parent / "data" / "config" / "config.json")


def test_load_main_config(monkeypatch):
    def fake_get_directory() -> Path:
        current_dir = Path(os.path.abspath(__file__)).parent
        return current_dir / "data" / "config"

    monkeypatch.setattr(configs, "get_main_config_directory", fake_get_directory)
    main = configs.load_main_config()
    assert main.type == configs.ConfigType.CONF_MAIN

    assert isinstance(main, configs.Config)


def test_get_all_configs(monkeypatch):
    def fake_get_directory() -> Path:
        current_dir = Path(os.path.abspath(__file__)).parent
        return current_dir / "data" / "config"

    monkeypatch.setattr(configs, "get_main_config_directory", fake_get_directory)

    all_conf = configs.get_all_configs()

    assert len(all_conf) == 3
    assert ConfigType.CONF_MAIN in all_conf
    assert ConfigType.CONF_KEYMAP in all_conf
    assert ConfigType.CONF_LAYOUT in all_conf


def test_config_creation():
    def fake_get_directory() -> Path:
        current_dir = Path(os.path.abspath(__file__)).parent
        return current_dir / "data" / "config"

    strpath = (fake_get_directory() / "test_data.json").__str__()
    assert os.path.exists(strpath)
    config = configs.Config(0, strpath)
    assert config

    # Random value access check
    assert config["test_val1"] == 1
    assert config["test_val2"] == 2

    # Default return check
    assert not config["test_val3"]
