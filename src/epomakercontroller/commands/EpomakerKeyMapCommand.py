""""""  # TODO

from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report


class EpomakerKeyMapCommand(EpomakerCommand):
    """"""  # TODO

    def __init__(self, key_index: int, key_combo: int) -> None:
        check_sum = 0xff - (0x13 + key_index)
        initialization_data = f"1300{key_index:02x}00000000{check_sum:02x}0000{key_combo:02x}"
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)
