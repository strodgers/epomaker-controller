from dataclasses import dataclass
from typing import Iterator
from ..configs.configs import Config


@dataclass(frozen=True)
class KeyboardKey:
    name: str
    value: int
    display_str: str | None = None

    def __post_init__(self) -> None:
        # If no display string, just use the name
        if not self.display_str:
            object.__setattr__(
                self, "display_str", self.name
            )  # Get around dataclass being frozen


class KeyboardKeys:
    """This class holds each keyboard key index along with it's name and display string"""

    def __init__(self, config: Config) -> None:
        assert config.data is not None, "ERROR: Config has no data"

        self.all_keys = [KeyboardKey(**key) for key in config.data]
        self.name_to_key_dict = {}
        for key in self.all_keys:
            self.name_to_key_dict[key.name] = key

    def __iter__(self) -> Iterator[KeyboardKey]:
        for key in self.all_keys:
            yield key

    def get_key_by_name(self, name: str) -> KeyboardKey | None:
        return self.name_to_key_dict.get(name, None)
