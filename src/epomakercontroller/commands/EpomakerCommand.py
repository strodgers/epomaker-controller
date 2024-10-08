"""Module for constructing commands to send to the Epomaker keyboard."""

import dataclasses
from typing import Iterator
from .reports.Report import Report, ReportCollection
import numpy as np
import numpy.typing as npt


@dataclasses.dataclass(frozen=True)
class CommandStructure:
    """The structure of a command.

    The structure defines the number of starter, data, and footer reports in a command.

    Parameters:
        number_of_starter_reports (int): The number of starter reports (default: 1).
        All commands will have at least one of these, it is a header that contains
        some command ID and potentially a smal amount of data (eg CPU usage).
        number_of_data_reports (int): The number of data reports (default: 0). This
        is the main data payload of the command, eg an image.
        number_of_footer_reports (int): The number of footer reports (default: 0). This
        is a footer that tells the device that the command is complete.
    """

    number_of_starter_reports: int = 1
    number_of_data_reports: int = 0
    number_of_footer_reports: int = 0

    def __len__(self) -> int:
        """Returns the total number of reports in the command.

        Returns:
            int: The total number of reports.
        """
        return (
            self.number_of_starter_reports
            + self.number_of_data_reports
            + self.number_of_footer_reports
        )


class EpomakerCommand:
    """A command is basically just a wrapper around a numpy array of bytes.

    The command must have x dimension of 128 bytes and be padded with zeros if
    the command is less than 128 bytes.

    The command may have a y dimension of at least 1, and more if the command
    is a series of packets to be sent (eg image, key colours). Each row of extra
    packets must also have an associated header according to the commannd type.
    """

    def __init__(
        self,
        initial_report: Report,
        structure: CommandStructure | None = None,
    ) -> None:
        """Initializes the command with an initial report.

        Args:
            initial_report (Report): The initial report.
            structure (CommandStructure): The structure of the command (default: None).
        """
        if not structure:
            structure = CommandStructure()
        self.reports: ReportCollection = ReportCollection()
        self.structure: CommandStructure = structure
        # If there are data reports, the command must be prepared before sending
        self.report_data_prepared: bool = structure.number_of_data_reports == 0
        self.report_footer_prepared: bool = structure.number_of_footer_reports == 0
        self._insert_report(initial_report)

    def _insert_report(self, report: Report) -> None:
        assert report.index < len(self.structure), (
            f"Report index {report.index} exceeds the number of reports "
            f"{len(self.structure)}."
        )
        # assert report.index not in [r.index for r in self.reports], (
        #     f"Report index {report.index} already exists."
        #     )
        self.reports.append(report)

    @staticmethod
    def _np16_to_np8(data_16bit: npt.NDArray[np.uint16]) -> npt.NDArray[np.uint8]:
        """Converts a numpy array of 16-bit numbers to 8-bit numbers.

        Args:
            data_16bit (npt.NDArray[np.uint16]): The 16-bit data.

        Returns:
            npt.NDArray[np.uint8]: The 8-bit data.
        """
        new_shape = (data_16bit.shape[0], data_16bit.shape[1] * 2)
        data_8bit_flat = np.empty(data_16bit.size * 2, dtype=np.uint8)

        data_8bit_flat[0::2] = (data_16bit >> 8).flatten()  # High bytes
        data_8bit_flat[1::2] = (data_16bit & 0xFF).flatten()  # Low bytes

        return data_8bit_flat.reshape(new_shape)

    def __iter__(self) -> Iterator[Report]:
        """Iterates over the reports in the command.

        Yields:
            Iterator[Report]: The reports in the command.
        """
        for report in self.reports:
            yield report

    def __getitem__(self, key: int) -> Report:
        """Gets a report by index.

        Args:
            key (int): The index of the report.

        Returns:
            Report: The report.
        """
        report = next((r for r in self.reports if r.index == key), None)
        assert report is not None, f"Report {key} not found."
        return report

    def iter_report_bytes(self) -> Iterator[bytes]:
        """Iterates over the report bytes in the command.

        Yields:
            Iterator[bytes]: The report bytes.
        """
        for report_bytes in self.reports.iter_report_bytes():
            yield report_bytes
