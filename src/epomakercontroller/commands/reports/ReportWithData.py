import dataclasses

from .Report import Report


@dataclasses.dataclass()
class ReportWithData(Report):
    def __init__(
        self,
        header_format_string: str,
        checksum_index: int | None,
        index: int,
        header_format_values: dict[str, int] = dataclasses.field(default_factory=dict),
        report_bytearray: bytearray | None = None,
        header_length: int | None = None,
        report_data: bytearray | None = None,
        prepared: bool = False,
    ) -> None:
        super().__init__(
            header_format_string,
            checksum_index,
            index,
            False,
            header_format_values,
            report_bytearray,
            header_length,
        )
        self.report_data: bytearray | None = report_data
        self.prepared: bool = prepared
        if self.report_data is not None:
            self.prepared = True

    def add_data(self, data: bytes) -> None:
        assert self.prepared is False, "Report data has already been set."
        assert (
            self.report_bytearray is not None
        ), "Report bytearray must be set before adding data."
        self.report_data = bytearray(data)
        self.report_bytearray += self.report_data
        self._pad()
        self.prepared = True

    # def __getitem__(self, key: int | slice) -> bytes:
    #     assert self.report_bytearray is not None, "Report bytearray must be set before getting."
    #     assert self.report_data is not None, "Report data must be set before getting."
    #     return bytes((self.report_bytearray + self.report_data)[key])
