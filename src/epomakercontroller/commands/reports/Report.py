"""Report module.

This module contains the Report and ReportCollection classes, which represent
wrappers around bytearrays that are sent to the keyboard.
"""

import dataclasses
from typing import Iterator

BUFF_LENGTH: int = 128 // 2  # 128 bytes / 2 bytes per hex value


@dataclasses.dataclass()
class Report:
    """Represents the data that is sent to the keyboard."""

    header_format_string: str
    checksum_index: int | None
    index: int
    pad_on_init: bool = True
    header_format_values: dict[str, int] = dataclasses.field(default_factory=dict)
    report_bytearray: bytearray | None = None
    header_length: int | None = None

    def __post_init__(self) -> None:
        """Initializes the report after the dataclass is created."""
        if self.header_format_values == {}:
            self.report_bytearray = bytearray.fromhex(self.header_format_string)
        else:
            self.report_bytearray = bytearray.fromhex(
                self.header_format_string.format(**self.header_format_values)
            )
        self.header_length = len(self.report_bytearray)
        if self.checksum_index is not None:
            self.report_bytearray += self._calculate_checksum(self._get_header())
        assert len(self.report_bytearray) <= BUFF_LENGTH, (
            f"Report length {len(self.report_bytearray)} exceeds the maximum length "
            f"of {BUFF_LENGTH}."
        )
        self.header_length = len(self.report_bytearray)
        if self.pad_on_init:
            self._pad()

    def _pad(self) -> None:
        """Pads the report header with zeros to the maximum length."""
        assert (
            self.report_bytearray is not None
        ), "Report bytearray must be set before padding."
        self.report_bytearray += bytes(BUFF_LENGTH - len(self.report_bytearray))

    @staticmethod
    def _calculate_checksum(buffer: bytes) -> bytes:
        """Calculates the checksum for the given buffer.

        Args:
            buffer (bytes): The buffer to calculate the checksum for.

        Returns:
            bytes: The calculated checksum.
        """
        sum_bits = sum(buffer) & 0xFF
        checksum = (0xFF - sum_bits) & 0xFF
        return bytes([checksum])

    def _get_checksum(self) -> bytes:
        """Gets the checksum from the report bytearray.

        Returns:
            bytes: The checksum bytes.
        """
        assert (
            self.report_bytearray is not None
        ), "Report bytearray must be set before getting."
        assert (
            self.checksum_index is not None
        ), "Checksum index must be set before getting."
        return self[self.checksum_index]

    def _get_header(self) -> bytes:
        """Gets the header from the report bytearray.

        Returns:
            bytes: The header bytes.
        """
        assert (
            self.header_length is not None
        ), "Header length must be set before getting."
        assert (
            self.report_bytearray is not None
        ), "Report bytearray must be set before getting."
        return self.report_bytearray[: self.header_length]

    def __getitem__(self, key: int | slice) -> bytes:
        """Gets the byte or slice of bytes from the report bytearray.

        Args:
            key (int | slice): The key to get bytes for.

        Returns:
            bytes: The bytes from the report bytearray.
        """
        assert (
            self.report_bytearray is not None
        ), "Report bytearray must be set before getting."
        return bytes(self.report_bytearray[key])

    def __len__(self) -> int:
        """Gets the length of the report bytearray.

        Returns:
            int: The length of the report bytearray.
        """
        if self.report_bytearray is None:
            return 0
        return len(self.report_bytearray)

    def get_all_bytes(self) -> bytearray | None:
        """Gets all the bytes from the report bytearray.

        Returns:
            bytearray | None: The report bytearray.
        """
        assert (
            self.report_bytearray is not None
        ), "Report bytearray must be set before getting all bytes."
        return self.report_bytearray


@dataclasses.dataclass()
class ReportCollection:
    """Represents a collection of reports."""

    reports: list[Report] = dataclasses.field(default_factory=list)

    def __iter__(self) -> Iterator[Report]:
        """Iterates over the reports in the collection.

        Yields:
            Iterator[Report]: The reports in the collection.
        """
        for report in self.reports:
            yield report

    def __getitem__(self, key: int) -> Report:
        """Gets a report by index.

        Args:
            key (int): The index of the report to get.

        Returns:
            Report: The report at the specified index.
        """
        return self.reports[key]

    def __len__(self) -> int:
        """Gets the number of reports in the collection.

        Returns:
            int: The number of reports.
        """
        return len(self.reports)

    def __setitem__(self, report: Report) -> None:
        """Adds a report to the collection.

        Args:
            report (Report): The report to add.
        """
        assert report.index not in [
            r.index for r in self.reports
        ], f"Report index {report.index} already exists."
        assert (
            report.report_bytearray is not None
        ), "Report bytearray must be set before adding."
        self.reports.append(report)

    def append(self, report: Report) -> None:
        """Appends a report to the collection.

        Args:
            report (Report): The report to append.
        """
        assert report.index not in [
            r.index for r in self.reports
        ], f"Report index {report.index} already exists."
        assert (
            report.report_bytearray is not None
        ), "Report bytearray must be set before adding."
        self.reports.append(report)
        self.reports.sort(key=lambda x: x.index)

    def iter_report_bytes(self) -> Iterator[bytes]:
        """Iterates over the bytearrays of the reports in the collection.

        Yields:
            Iterator[bytes]: The bytearrays of the reports.
        """
        for report in self.reports:
            assert (
                report.report_bytearray is not None
            ), "Report bytearray must be set before iterating."
            yield report.report_bytearray
