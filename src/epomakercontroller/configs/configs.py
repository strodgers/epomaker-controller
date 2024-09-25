from dataclasses import dataclass
from enum import Enum
import json

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
            with pkg_resources.path(epomakercontroller.configs.layouts, self.filename) as path:
                config_path = str(path)
        elif self.type == ConfigType.CONF_KEYMAP:
            with pkg_resources.path(epomakercontroller.configs.keymaps, self.filename) as path:
                config_path = str(path)

        with open(config_path, "r") as f:
            self.data = json.load(f)
