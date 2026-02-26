"""Command for polling the keyboard on 2.4Ghz wireless."""

from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report


class EpomakerPollCommand(EpomakerCommand):
    """A command for polling the keyboard on 2.4Ghz wireless."""

    def __init__(self) -> None:
        """Initializes the poll.
        """
        initialization_data = "f7"
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)
