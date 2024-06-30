"""ReportWithData module.

This module contains the ReportWithData class, which extends the Report class
to include additional data handling functionality.
"""

import dataclasses
from typing import Optional

from .Report import Report


@dataclasses.dataclass()
class ReportWithData(Report):
    """Represents a report with additional data."""

    def __init__(
        self,
        header_format_string: str,
        checksum_index: Optional[int],
        index: int,
        header_format_values: Optional[dict[str, int]] = None,
        report_bytearray: Optional[bytearray] = None,
        header_length: Optional[int] = None,
        report_data: Optional[bytearray] = None,
        prepared: bool = False,
    ) -> None:
        """Initializes the ReportWithData object.

        Args:
            header_format_string (str): The header format string.
            checksum_index (int | None): The checksum index.
            index (int): The report index.
            header_format_values (dict[str, int] | None): The header format values.
            report_bytearray (bytearray | None): The report bytearray.
            header_length (int | None): The header length.
            report_data (bytearray | None): The report data.
            prepared (bool): Whether the report data is prepared.
        """
        if header_format_values is None:
            header_format_values = {}
        super().__init__(
            header_format_string,
            checksum_index,
            index,
            False,
            header_format_values,
            report_bytearray,
            header_length,
        )
        self.report_data: Optional[bytearray] = report_data
        self.prepared: bool = prepared
        if self.report_data is not None:
            self.prepared = True

    def add_data(self, data: bytes) -> None:
        """Adds data to the report.

        Args:
            data (bytes): The data to add.
        """
        assert not self.prepared, "Report data has already been set."
        assert (
            self.report_bytearray is not None
        ), "Report bytearray must be set before adding data."
        self.report_data = bytearray(data)
        self.report_bytearray += self.report_data
        self._pad()
        self.prepared = True
