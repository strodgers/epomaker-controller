from dataclasses import dataclass
from enum import Enum
import json
from typing import Any, Dict

from click import Path

import epomakercontroller.configs.configs
import epomakercontroller.configs.layouts
import epomakercontroller.configs.keymaps
import importlib.resources as pkg_resources

class ConfigType(Enum):
    CONF_LAYOUT = 0
    CONF_KEYMAP = 1

@dataclass
class Config:
    type: ConfigType
    filename: str

    def __post_init__(self) -> None:
        config_path = None
        if self.type == ConfigType.CONF_LAYOUT:
            config_path = pkg_resources.path(epomakercontroller.configs.layouts, self.filename)
        elif self.type == ConfigType.CONF_KEYMAP:
            config_path = pkg_resources.path(epomakercontroller.configs.keymaps, self.filename)

        with open(
            str(config_path), "r"
        ) as f:
            self.data = json.load(f)
