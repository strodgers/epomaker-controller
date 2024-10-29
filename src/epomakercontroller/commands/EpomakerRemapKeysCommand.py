"""Command for remapping the function of a key on the keyboard.

The key to be remapped will use an index internal to the keyboard, loaded in via a keymap
config file (see KeyboardKey and ConfigType.CONF_KEYMAP)

The key (or combination of keys) to be remapped _to_ will use standard USB HID codes, see
https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf#page=53
"""

from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report


class EpomakerRemapKeysCommand(EpomakerCommand):
    """A command for remapping a key on the keyboard

    Args:
        key_index (int): The index used internally by the keyboard to be remapped.
        key_combo (int): They key to be bound to, using USB HID codes.
    """

    def __init__(self, key_index: int, key_combo: int) -> None:
        check_sum = 0xFF - (0x13 + key_index)
        initialization_data = (
            f"1300{key_index:02x}00000000{check_sum:02x}0000{key_combo:02x}"
        )
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)
