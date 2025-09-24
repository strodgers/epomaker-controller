import os
from pathlib import Path
from epomakercontroller.configs import configs


def test_load_main_config(monkeypatch):
    def fake_get_directory():
        current_dir = Path(os.path.abspath(__file__)).parent
        return current_dir / "data" / "config"

    monkeypatch.setattr(configs, "get_main_config_directory", fake_get_directory)
    main = configs.load_main_config()

    assert main.type == configs.ConfigType.CONF_MAIN
