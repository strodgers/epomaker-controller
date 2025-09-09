from __future__ import annotations
import importlib.resources as pkg_resources

import typing
import os
import json

from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from src.epomakercontroller.logger.logger import Logger

import epomakercontroller.configs.layouts
import epomakercontroller.configs.keymaps

from .constants import CONFIG_DIRECTORY, CONFIG_NAME, DEFAULT_MAIN_CONFIG


if typing.TYPE_CHECKING:
    from typing import Optional, Any


class ConfigType(Enum):
    CONF_MAIN = 0
    CONF_LAYOUT = 1
    CONF_KEYMAP = 2


MODULE_BY_CONFIG_TYPE = {
    ConfigType.CONF_LAYOUT: epomakercontroller.configs.layouts,
    ConfigType.CONF_KEYMAP: epomakercontroller.configs.keymaps
}


@dataclass
class Config:
    type: ConfigType
    filename: str
    data: dict[Any, Any] | None = None

    def __post_init__(self) -> None:
        # If data not set manually, load it from the filename
        if self.data:
            return

        with open(self._find_config_path(self.filename, self.type), "r", encoding="utf-8") as f:
            self.data = json.load(f)

    @staticmethod
    def _find_config_path(filename: str, config_type: ConfigType) -> str:
        # If the filename exists, use that
        if os.path.exists(filename):
            return os.path.realpath(filename)

        with pkg_resources.path(
            MODULE_BY_CONFIG_TYPE[config_type], filename
        ) as path:
            return str(path)

    def __getitem__(self, key: str) -> Any:
        return self.data.get(key)


def get_main_config_directory() -> Path:
    home_dir = Path(os.path.abspath(os.curdir))
    config_dir = home_dir / CONFIG_DIRECTORY
    return config_dir


def create_default_main_config(config_file: Path) -> None:
    with open(config_file, 'w', encoding="utf-8") as f:
        json.dump(DEFAULT_MAIN_CONFIG, f, indent=4)


def save_main_config(config: Config) -> None:
    config_dir = get_main_config_directory()
    config_file = config_dir / CONFIG_NAME
    with open(config_file, 'w', encoding="utf-8") as f:
        json.dump(config.data, f, indent=4)


def setup_main_config() -> Path:
    config_dir = get_main_config_directory()
    config_file = config_dir / CONFIG_NAME

    if not config_dir.exists():
        Logger.log_info(f"Creating config directory at {config_dir}")
        config_dir.mkdir(parents=True)

    if not config_file.exists():
        Logger.log_info(f"Creating default config file at {config_file}")
        create_default_main_config(config_file)

    return config_file


def verify_main_config(in_config: Config) -> Optional[Config]:
    if in_config.type != ConfigType.CONF_MAIN:
        Logger.log_error("verify_main_config only for Configs of type CONF_MAIN")
        return None

    if not in_config.data:
        Logger.log_error("Config has no data")
        return None

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


def get_all_configs() -> Optional[dict[ConfigType, Config]]:
    # First load the main config file
    main_config = load_main_config()

    # Use keyboard and layout configs as per main config
    conf_layout_path = main_config["CONF_LAYOUT_PATH"]
    conf_keymap_path = main_config["CONF_KEYMAP_PATH"]

    all_configs = {
        ConfigType.CONF_MAIN: main_config,
        ConfigType.CONF_LAYOUT: Config(ConfigType.CONF_LAYOUT, conf_layout_path),
        ConfigType.CONF_KEYMAP: Config(ConfigType.CONF_KEYMAP, conf_keymap_path),
    }

    return all_configs
