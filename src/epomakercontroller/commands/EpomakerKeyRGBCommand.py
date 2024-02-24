from dataclasses import dataclass

from .EpomakerCommand import EpomakerCommand, CommandStructure
from .reports.Report import Report, BUFF_LENGTH
from .reports.ReportWithData import ReportWithData
from .data.constants import KeyboardKey
from typing import Iterator


class KeyMap:
    """Map a KeyboardKey index to an RGB value."""

    def __init__(self) -> None:
        self.key_map: dict[int, tuple[int, int, int]] = {}

    def __getitem__(self, key: KeyboardKey) -> tuple[int, int, int]:
        return self.key_map[key.value]

    def __setitem__(self, key: KeyboardKey, value: tuple[int, int, int]) -> None:
        self.key_map[key.value] = value

    def __iter__(self) -> Iterator[tuple[int, tuple[int, int, int]]]:
        return iter(self.key_map.items())


@dataclass(frozen=True)
class KeyboardRGBFrame:
    """A keyboard frame consists of a map of keys to RGB values as well as a time in milliseconds
    to display the frame."""

    key_map: KeyMap
    time_ms: int
    length: int = 7
    index: int = 0


class EpomakerKeyRGBCommand(EpomakerCommand):
    """Change a selection of keys to specific RGB values."""

    def __init__(self, frames: list[KeyboardRGBFrame]) -> None:
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
                    "19{this_frame_report_index:02x}{frame_index:02x}{total_frames:02x}{frame_time:02x}0000",
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
                for key_index, rgb in frame.key_map:
                    # For each key, set the RGB values in the data buffer
                    for i, colour in enumerate(rgb):
                        # R, G, B individually
                        this_frame_colour_index = (
                            (key_index * 3)
                            - (this_frame_report_index * data_buffer_length)
                            + i
                        )
                        if 0 <= this_frame_colour_index < len(data_byterarray):
                            data_byterarray[this_frame_colour_index] = colour
                report.add_data(data_byterarray)
                self._insert_report(report)
                report_index += 1

    def get_data_reports(self) -> list[ReportWithData]:
        return [r for r in self.reports if isinstance(r, ReportWithData)]

    def report_data_contain_index(self, report: ReportWithData, index: int) -> bool:
        """Checks if the provided report contains the specified index if all the data portions of
        the reports were to be indexed linearly.

        Uses BUFF_LENGTH - self.report_data_header_length so this function can be used before
        the data is set.
        """
        report_index_count = 0
        data_buffer_length = BUFF_LENGTH - self.report_data_header_length
        for report in self.get_data_reports():
            report_data = report[self.report_data_header_length :]
            if report_index_count <= index < report_index_count + data_buffer_length:
                return True
            report_index_count += len(report_data)
        return False
