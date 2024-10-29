from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path
from typing import Any

import epomakercontroller.configs.configs
import epomakercontroller.configs.layouts
import epomakercontroller.configs.keymaps
import importlib.resources as pkg_resources


class ConfigType(Enum):
    CONF_MAIN = 0
    CONF_LAYOUT = 1
    CONF_KEYMAP = 2


DEFAULT_MAIN_CONFIG = {
    "VENDOR_ID": 0x3151,
    "PRODUCT_IDS_WIRED": [0x4010, 0x4015],
    "PRODUCT_IDS_24G": [0x4011, 0x4016],
    "USE_WIRELESS": False,
    "DEVICE_DESCRIPTION_REGEX": "ROYUAN .* System Control",
    # The file will be looked for in the install location first, otherwise use a full filepath
    "CONF_LAYOUT_PATH": "EpomakerRT100-UK-ISO.json",
    "CONF_KEYMAP_PATH": "EpomakerRT100.json",
}


@dataclass
class Config:
    type: ConfigType
    filename: str
    data: dict[Any, Any] | None = None

    def __post_init__(self) -> None:
        # If data not set manually, load it from the filename
        if not self.data:
            with open(self._find_config_path(self.filename, self.type), "r", encoding="utf-8") as f:
                self.data = json.load(f)
                return

        assert self.data is not None, "ERROR: Config has no data"

    @staticmethod
    def _find_config_path(filename: str, type: ConfigType) -> str:
        # If the filename exists, use that
        if os.path.exists(filename):
            return os.path.realpath(filename)

        # Otherwise check for installed files
        if type == ConfigType.CONF_LAYOUT:
            with pkg_resources.path(
                epomakercontroller.configs.layouts, filename
            ) as path:
                return str(path)
        elif type == ConfigType.CONF_KEYMAP:
            with pkg_resources.path(
                epomakercontroller.configs.keymaps, filename
            ) as path:
                return str(path)

        raise AttributeError(f"Unsupported ConfigType: {type.name}")

    def __getitem__(self, key: str) -> Any:
        assert self.data is not None, "ERROR: Config has no data"
        if key not in self.data:
            print(f"Key {key} not found in {self.type.name}")
            return None
        return self.data[key]


def get_main_config_directory() -> Path:
    home_dir = Path.home()
    config_dir = home_dir / ".epomaker-controller"
    return config_dir


def create_default_main_config(config_file: Path) -> None:
    with open(config_file, 'w', encoding="utf-8") as f:
        json.dump(DEFAULT_MAIN_CONFIG, f, indent=4)


def save_main_config(config: Config) -> None:
    config_dir = get_main_config_directory()
    config_file = config_dir / "config.json"
    with open(config_file, 'w', encoding="utf-8") as f:
        json.dump(config.data, f, indent=4)


def setup_main_config() -> Path:
    config_dir = get_main_config_directory()
    config_file = config_dir / "config.json"

    # Create the config directory if it doesn't exist
    if not config_dir.exists():
        print(f"Creating config directory at {config_dir}")
        config_dir.mkdir(parents=True)

    # Create the default config file if it doesn't exist
    if not config_file.exists():
        print(f"Creating default config file at {config_file}")
        create_default_main_config(config_file)

    return config_file


def verify_main_config(in_config: Config) -> Config:
    assert (
        in_config.type == ConfigType.CONF_MAIN
    ), "ERROR: verify_main_config only for Configs of type CONF_MAIN"
    assert in_config.data is not None, "ERROR: Config has no data"

    # Ensure no unsupported entries are present
    extra_keys = set(in_config.data.keys()) - set(DEFAULT_MAIN_CONFIG.keys())
    if extra_keys:
        raise ValueError(f"ERROR: Unsupported config entries found: {extra_keys}")

    # Merge the default values with the provided config, ensuring no missing keys
    out_config = Config(
        type=in_config.type,
        filename=in_config.filename,
        data={**DEFAULT_MAIN_CONFIG, **in_config.data},
    )

    # Write config back
    save_main_config(out_config)

    return out_config


def load_main_config() -> Config:
    config_file = setup_main_config()

    config = Config(ConfigType.CONF_MAIN, config_file.as_posix())

    return verify_main_config(config)


def get_all_configs() -> dict[ConfigType, Config]:
    # First load the main config file
    main_config = load_main_config()
    assert main_config.data is not None, "ERROR: Config has no data"

    # Use keyboard and layout configs as per main config
    conf_layout_path = main_config.data["CONF_LAYOUT_PATH"]
    conf_keymap_path = main_config.data["CONF_KEYMAP_PATH"]

    all_configs = {
        ConfigType.CONF_MAIN: main_config,
        ConfigType.CONF_LAYOUT: Config(ConfigType.CONF_LAYOUT, conf_layout_path),
        ConfigType.CONF_KEYMAP: Config(ConfigType.CONF_KEYMAP, conf_keymap_path),
    }

    return all_configs
