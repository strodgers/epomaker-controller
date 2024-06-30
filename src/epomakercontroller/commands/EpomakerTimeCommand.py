"""Command for setting the time on the keyboard."""

from datetime import datetime
from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report


class EpomakerTimeCommand(EpomakerCommand):
    """A command for setting the time on the keyboard."""

    def __init__(self, time: datetime) -> None:
        """Initializes the command with the time value.

        Args:
            time (datetime): The time value.
        """
        initialization_data = "28000000000000d7" + self._format_time(time)
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report)

    @staticmethod
    def _format_time(time: datetime) -> str:
        """Gets the current time and formats it into the required byte string format.

        Args:
            time (datetime): The time to format.

        Returns:
            str: The formatted command string.
        """
        print("Using:", time)

        # Example of formatting for a specific date and time format
        # Adjust the formatting based on your specific requirements
        year = time.year
        month = time.month
        day = time.day
        hour = time.hour
        minute = time.minute
        second = time.second

        # Convert to hexadecimal strings
        year_hex = f"{year:04x}"
        month_hex = f"{month:02x}"
        day_hex = f"{day:02x}"
        hour_hex = f"{hour:02x}"
        minute_hex = f"{minute:02x}"
        second_hex = f"{second:02x}"

        command = f"{year_hex}{month_hex}{day_hex}{hour_hex}{minute_hex}{second_hex}"

        return command
