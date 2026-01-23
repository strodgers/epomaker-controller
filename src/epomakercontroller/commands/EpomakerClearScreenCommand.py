from epomakercontroller.commands.EpomakerCommand import EpomakerCommand
from epomakercontroller.commands.reports.Report import Report


class EpomakerClearScreenCommand(EpomakerCommand):
    """
    Clear screen command. Resets the image, does not affect telemetry information on the screen
    """

    def __init__(self) -> None:
        """
        Initialize URB data with 0xAC command to clear the screen.
        """
        header = 0xAC
        footer = 0xFF - header

        initialization_data = f"{header:x}000000000000{footer:x}"
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)
