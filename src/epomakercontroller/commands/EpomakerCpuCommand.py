from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report


class EpomakerCpuCommand(EpomakerCommand):
    """A command for setting the CPU usage on the keyboard."""

    def __init__(self, cpu: int) -> None:
        initialization_data = "22000000000000dd63007f0004000800" + f"{cpu:02x}"
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)
