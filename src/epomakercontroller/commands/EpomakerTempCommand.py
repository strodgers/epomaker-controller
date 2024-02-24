from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report


class EpomakerTempCommand(EpomakerCommand):
    """A command for setting the temperature on the keyboard."""

    def __init__(self, temp: int) -> None:
        initialization_data = "2a000000000000d5" + f"{temp:02x}"
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)
