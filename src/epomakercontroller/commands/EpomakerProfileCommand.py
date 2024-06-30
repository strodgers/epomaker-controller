"""Command for setting the profile on the keyboard."""

from .EpomakerCommand import EpomakerCommand
from .reports.Report import Report
from .data.constants import Profile


class EpomakerProfileCommand(EpomakerCommand):
    """A command for setting the profile on the keyboard."""

    def __init__(self, profile: Profile) -> None:
        """Initializes the command with the profile values.

        Args:
            profile (Profile): The profile values.
        """
        initialization_data = (
            "07"
            f"{profile.mode.value:02x}"
            f"{profile.speed.value:02x}"
            f"{profile.brightness.value:02x}"
            f"{profile.option.value|profile.dazzle.value:02x}"
            f"{profile.rgb[0]:02x}"
            f"{profile.rgb[1]:02x}"
            f"{profile.rgb[2]:02x}"
        )
        initial_report = Report(initialization_data, index=0, checksum_index=8)
        super().__init__(initial_report)
