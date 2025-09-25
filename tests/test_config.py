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

    # Merge check
    config.type = ConfigType.CONF_MAIN
    config = configs.verify_main_config(config)
    assert "VENDOR_ID" in config


def test_default_main_config():
    """
    This test was created during DEFAULT_MAIN_CONFIG dict migration
    That made migration a test-driven process. That guarantees that nothing was broken in process
    """

    DEFAULT_MAIN_CONFIG = {
        "VENDOR_ID": 0x3151,
        "PRODUCT_IDS_WIRED": [0x4010, 0x4015],
        "PRODUCT_IDS_24G": [0x4011, 0x4016],
        "USE_WIRELESS": False,
        "DEVICE_DESCRIPTION_REGEX": "ROYUAN .* System Control",
        "CONF_LAYOUT_PATH": "EpomakerRT100-UK-ISO.json",
        "CONF_KEYMAP_PATH": "EpomakerRT100.json",
    }

    def fake_get_directory() -> Path:
        current_dir = Path(os.path.abspath(__file__)).parent
        return current_dir / "data" / "config"

    path = fake_get_directory() / "new_main_config.json"
    try:
        configs.create_default_main_config(path)
        main = configs.Config(ConfigType.CONF_MAIN, (fake_get_directory() / "new_main_config.json").__str__())

        assert main

        for key, value in DEFAULT_MAIN_CONFIG.items():
            assert main[key] == value
    finally:
        if os.path.exists(path):
            os.remove(path)
