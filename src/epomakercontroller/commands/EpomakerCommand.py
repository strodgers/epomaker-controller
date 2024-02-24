import dataclasses
from typing import Iterator
from .reports.Report import Report, ReportCollection
import numpy as np
import numpy.typing as npt


@dataclasses.dataclass(frozen=True)
class CommandStructure:
    number_of_starter_reports: int = 1
    number_of_data_reports: int = 0
    number_of_footer_reports: int = 0

    def __len__(self) -> int:
        return (
            self.number_of_starter_reports
            + self.number_of_data_reports
            + self.number_of_footer_reports
        )


class EpomakerCommand:
    """A command is basically just a wrapper around a numpy array of bytes.

    The command must have x dimension of 128 bytes and be padded with zeros if the command is
    less than 128 bytes.

    The command may have a y dimension of at least 1, and more if the command is a series of
    packets to be sent (eg image, key colours). Each row of extra packets must also have an
    associated header according to the commannd type.
    """

    def __init__(
        self,
        initial_report: Report,
        structure: CommandStructure = CommandStructure(),
    ) -> None:
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
        """Converts a numpy array of 16-bit numbers to 8-bit numbers."""
        new_shape = (data_16bit.shape[0], data_16bit.shape[1] * 2)
        data_8bit_flat = np.empty(data_16bit.size * 2, dtype=np.uint8)

        data_8bit_flat[0::2] = (data_16bit >> 8).flatten()  # High bytes
        data_8bit_flat[1::2] = (data_16bit & 0xFF).flatten()  # Low bytes

        return data_8bit_flat.reshape(new_shape)

    def __iter__(self) -> Iterator[Report]:
        for report in self.reports:
            yield report

    def __getitem__(self, key: int) -> Report:
        report = next((r for r in self.reports if r.index == key), None)
        assert report is not None, f"Report {key} not found."
        return report

    def iter_report_bytes(self) -> Iterator[bytes]:
        for report_bytes in self.reports.iter_report_bytes():
            yield report_bytes
