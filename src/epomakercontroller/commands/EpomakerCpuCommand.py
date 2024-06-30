"""Command for setting the CPU usage on the keyboard."""

from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report


class EpomakerCpuCommand(EpomakerCommand):
    """A command for setting the CPU usage on the keyboard."""

    def __init__(self, cpu: int) -> None:
        """Initializes the command with the CPU usage value.

        Args:
            cpu (int): The CPU usage percentage (0-100).
        """
        initialization_data = "22000000000000dd63007f0004000800" + f"{cpu:02x}"
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)
