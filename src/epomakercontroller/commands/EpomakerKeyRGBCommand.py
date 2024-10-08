"""EpomakerKeyRGBCommand module.

This module contains the EpomakerKeyRGBCommand class, which represents a
command to change a selection of keys to specific RGB values on an Epomaker
keyboard.
"""

from dataclasses import dataclass
from typing import Iterator

from .EpomakerCommand import EpomakerCommand, CommandStructure
from ..utils.keyboard_keys import KeyboardKeys, KeyboardKey
from .reports.Report import Report, BUFF_LENGTH
from .reports.ReportWithData import ReportWithData


class KeyMap:
    """Map a KeyboardKey index to an RGB value."""

    def __init__(self, all_keys: KeyboardKeys) -> None:
        """Initializes the KeyMap."""
        self.key_map: dict[KeyboardKey, tuple[int, int, int]] = {}
        for key in all_keys:
            self.key_map[key] = (0, 0, 0)

    def __getitem__(self, key: KeyboardKey) -> tuple[int, int, int]:
        """Gets the RGB value for a given key.

        Args:
            key (KeyboardKey): The key to get the RGB value for.

        Returns:
            tuple[int, int, int]: The RGB value for the key.
        """
        return self.key_map[key]

    def __setitem__(self, key: KeyboardKey, value: tuple[int, int, int]) -> None:
        """Sets the RGB value for a given key.

        Args:
            key (KeyboardKey): The key to set the RGB value for.
            value (tuple[int, int, int]): The RGB value to set.
        """
        self.key_map[key] = value

    def __iter__(self) -> Iterator[tuple[KeyboardKey, tuple[int, int, int]]]:
        """Iterates over the key map.

        Returns:
            Iterator[tuple[int, tuple[int, int, int]]]: An iterator over the key map.
        """
        return iter(self.key_map.items())


@dataclass(frozen=True)
class KeyboardRGBFrame:
    """A frame of RGB values for a keyboard.

    A keyboard frame consists of a map of keys to RGB values and a time in
    milliseconds to display the frame.
    """

    key_map: KeyMap
    time_ms: int = 0
    index: int = 0

    def overlay(
        self, overlay_keys: set[KeyboardKey], colour: tuple[int, int, int]
    ) -> None:
        for key in overlay_keys:
            self.key_map[key] = colour


class EpomakerKeyRGBCommand(EpomakerCommand):
    """Change a selection of keys to specific RGB values."""

    def __init__(self, frames: list[KeyboardRGBFrame]) -> None:
        """Initializes the EpomakerKeyRGBCommand with a list of frames.

        Args:
            frames (list[KeyboardRGBFrame]): The list of frames to send.
        """
        initialization_data = "18000000000000e7"
        self.report_data_header_length = 8
        data_reports_per_frame = 7
        structure = CommandStructure(
            number_of_starter_reports=1,
            number_of_data_reports=len(frames) * data_reports_per_frame,
            number_of_footer_reports=0,
        )
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report, structure)

        report_index = 1
        data_buffer_length = BUFF_LENGTH - self.report_data_header_length
        for frame in frames:
            for this_frame_report_index in range(0, data_reports_per_frame):
                report = ReportWithData(
                    (
                        "19{this_frame_report_index:02x}{frame_index:02x}"
                        "{total_frames:02x}{frame_time:02x}0000"
                    ),
                    index=report_index,
                    header_format_values={
                        "this_frame_report_index": this_frame_report_index,
                        "frame_index": frame.index,
                        "total_frames": len(frames),
                        "frame_time": frame.time_ms,
                    },
                    checksum_index=7,
                )
                # Zero out the data buffer
                data_byterarray = bytearray(data_buffer_length)
                for key, rgb in frame.key_map:
                    # For each key, set the RGB values in the data buffer
                    for i, colour in enumerate(rgb):
                        # R, G, B individually
                        this_frame_colour_index = (
                            (key.value * 3)
                            - (this_frame_report_index * data_buffer_length)
                            + i
                        )
                        if 0 <= this_frame_colour_index < len(data_byterarray):
                            data_byterarray[this_frame_colour_index] = colour
                report.add_data(data_byterarray)
                self._insert_report(report)
                report_index += 1

        self.report_data_prepared = True

    def get_data_reports(self) -> list[ReportWithData]:
        """Returns the data reports.

        Returns:
            list[ReportWithData]: The data reports.
        """
        return [r for r in self.reports if isinstance(r, ReportWithData)]

    def report_data_contain_index(self, report: ReportWithData, index: int) -> bool:
        """Checks if the provided report contains the specified index.

        Uses BUFF_LENGTH - self.report_data_header_length so this function
        can be used before the data is set.

        Args:
            report (ReportWithData): The report to check.
            index (int): The index to check.

        Returns:
            bool: True if the report contains the index, False otherwise.
        """
        report_index_count = 0
        data_buffer_length = BUFF_LENGTH - self.report_data_header_length
        for report in self.get_data_reports():
            report_data = report[self.report_data_header_length :]
            if report_index_count <= index < (report_index_count + data_buffer_length):
                return True
            report_index_count += len(report_data)
        return False
