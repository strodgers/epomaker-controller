from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class KeyboardKey:
    name: str
    value: int
    display_str: str


class KeyboardKeys:
    """This class holds each keyboard key index along with it's name and display string"""
    def __init__(self, config_file: Path) -> None:
        # Load the JSON
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to open KeyboardKeys config file {config_file}: {e}")

        self.all_keys = [KeyboardKey(**key) for key in data]
        self.key_to_name_dict = {}
        for key in self.all_keys:
            self.key_to_name_dict[key] = key.name

    def __iter__(self) -> Iterator[KeyboardKey]:
        for key in self.all_keys:
            yield key

    def get_name_of_key(self, key: KeyboardKey) -> str | None:
        return self.key_to_name_dict.get(key, None)



# ALL_KEYBOARD_KEYS = [value for name, value in vars(KK).items() if not name.startswith('__')]
# KEYBOARD_KEYS_NAME_DICT = {
#     name: value for name, value in vars(KK).items() if isinstance(value, KeyboardKey)
# }

