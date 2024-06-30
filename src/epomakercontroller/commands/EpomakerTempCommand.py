"""Command for setting the temperature on the keyboard."""

from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report


class EpomakerTempCommand(EpomakerCommand):
    """A command for setting the temperature on the keyboard."""

    def __init__(self, temp: int) -> None:
        """Initializes the command with the temperature value.

        Args:
            temp (int): The temperature value in C (0-100).
        """
        initialization_data = "2a000000000000d5" + f"{temp:02x}"
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)
