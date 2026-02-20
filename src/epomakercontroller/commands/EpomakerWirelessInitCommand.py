"""
Todo: write docstrings for this class
"""

from .EpomakerCommand import EpomakerCommand, CommandStructure
from .reports.Report import Report


class EpomakerWirelessInitCommand(EpomakerCommand):
    CHUNKS = [
        "f60a",
        "8f00000000000070",
        "fc",
        "8700000000000078",
        "fc",
        "800000000000007f",
        "fc",
        "ad00000000000052",
        "fc",
        "840000000000007b",
        "fc",
        "850000000000007a",
        "fc",
        "8700000000000078",
        "fc",
        "8600000000000079",
        "fc",
        "910000000000006e",
        "fc",
        "920000000000006d",
        "fc",
        "9700000000000068"
        "fc",
    ]

    def __init__(self):
        initialization_data = "fe40"
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        structure = CommandStructure(
            number_of_starter_reports=1,
            number_of_data_reports=len(self.CHUNKS),
            number_of_footer_reports=0,
        )
        super().__init__(initial_report, structure)

    def prepare_from_sequence(self) -> None:
        for report_index in range(0, self.structure.number_of_data_reports):
            chunk = self.CHUNKS[report_index]
            report = Report(chunk, index=report_index + self.structure.number_of_starter_reports, checksum_index=None)
            self._insert_report(report)

        self.report_data_prepared = True
