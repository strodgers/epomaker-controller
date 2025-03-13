"""Command for sending images to the Epomaker keyboard."""

import os
import cv2
import numpy as np

from .EpomakerCommand import EpomakerCommand, CommandStructure
from .data.constants import IMAGE_DIMENSIONS
from .reports.Report import Report, BUFF_LENGTH
from .reports.ReportWithData import ReportWithData

SUPPORTED_FORMATS = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"]

class EpomakerImageCommand(EpomakerCommand):
    """A command for sending images to the keyboard."""

    def __init__(self) -> None:
        """Initializes the command."""
        initialization_data = "a5000100f4da008b0000a2ad"
        self.report_data_header_length = 8
        structure = CommandStructure(
            number_of_starter_reports=1,
            number_of_data_reports=1000,
            number_of_footer_reports=1,
        )
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report, structure)

    def get_data_reports(self) -> list[ReportWithData]:
        """Returns the data reports.

        Returns:
            list[ReportWithData]: The data reports.
        """
        return [r for r in self.reports if isinstance(r, ReportWithData)]

    @staticmethod
    def _encode_rgb565(r: int, g: int, b: int) -> int:
        # Mask the bits of each color to fit the 5-6-5 format
        r_565 = (r & 0b11111000) << 8  # Red: 5 bits
        g_565 = (g & 0b11111100) << 3  # Green: 6 bits
        b_565 = (b & 0b11111000) >> 3  # Blue: 5 bits

        # Combine the channels into one 16-bit number
        rgb_565 = r_565 | g_565 | b_565

        return rgb_565

    @staticmethod
    def _decode_rgb565(pixel: int) -> tuple[int, int, int]:
        r = (pixel & 0xF800) >> 8  # Red: 5 bits
        g = (pixel & 0x07E0) >> 3  # Green: 6 bits
        b = (pixel & 0x001F) << 3  # Blue: 5 bits

        # We need to adjust them because we're expanding to 8 bits per channel
        r |= r >> 5
        g |= g >> 6
        b |= b >> 5

        return (r, g, b)

    def encode_image(self, image_path: str) -> None:
        """Encode an image to 16-bit RGB565.

        Encode an image to 16-bit RGB565 according to IMAGE_DIMENSIONS and accounting
        for packet headers. The image is also rotated and flipped since this seems to be
        what the keyboard is expecting.

        Args:
            image_path (str): The path to the image file.
        """
        _, extension = os.path.splitext(image_path)
        assert extension in SUPPORTED_FORMATS, f"Unsupported format\nSupported formats are: {SUPPORTED_FORMATS}"
        image = cv2.imread(image_path)
        assert not isinstance(image, type(None)), f"Failed reading {image_path}"
        image = cv2.resize(image, IMAGE_DIMENSIONS)
        image = cv2.flip(image, 0)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image_16bit = np.zeros(
            (IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1]), dtype=np.uint16
        )
        try:
            for y in range(image.shape[0]):
                for x in range(image.shape[1]):
                    r, g, b = image[y, x]
                    image_16bit[y, x] = self._encode_rgb565(r, g, b)
        except Exception as e:
            print(f"Exception while converting image: {e}")

        image_8bit_flattened = np.ndarray.flatten(self._np16_to_np8(image_16bit))
        data_buff_length = BUFF_LENGTH - self.report_data_header_length
        data_buff_pointer = 0
        for report_index in range(0, self.structure.number_of_data_reports):
            report_index_bytes = report_index.to_bytes(2, "big")
            report = ReportWithData(
                header_format_string="25000100{report_index_bytes_upper:02x}{report_index_bytes_lower:02x}38",
                index=report_index + self.structure.number_of_starter_reports,
                header_format_values={
                    "report_index_bytes_upper": report_index_bytes[1],
                    "report_index_bytes_lower": report_index_bytes[0],
                },
                checksum_index=7,
            )
            report.add_data(
                image_8bit_flattened[
                    data_buff_pointer : data_buff_pointer + data_buff_length
                ].tobytes()
            )
            data_buff_pointer += data_buff_length
            self._insert_report(report)

        assert len(self.get_data_reports()) == self.structure.number_of_data_reports, (
            f"Expected {self.structure.number_of_data_reports} reports, got "
            f"{len(self.get_data_reports())}."
        )

        self.report_data_prepared = True

        # Add the footer report
        footer_index_bytes = (
            self.structure.number_of_starter_reports
            + self.structure.number_of_data_reports
            - self.structure.number_of_footer_reports
        ).to_bytes(2, "big")
        footer_report = ReportWithData(
            header_format_string="25000100{footer_index_bytes_upper:02x}{footer_index_bytes_lower:02x}34",
            index=self.structure.number_of_starter_reports
            + self.structure.number_of_data_reports,
            header_format_values={
                "footer_index_bytes_upper": footer_index_bytes[1],
                "footer_index_bytes_lower": footer_index_bytes[0],
            },
            checksum_index=7,
        )
        footer_report.add_data(
            image_8bit_flattened[
                data_buff_pointer : data_buff_pointer + data_buff_length
            ].tobytes()
        )
        # Need some padding at the end of the image data
        footer_report._pad()
        self._insert_report(footer_report)

        self.report_footer_prepared = True

        assert len(self.reports) == len(
            self.structure
        ), f"Expected {len(self.structure)} reports, got {len(self.reports)}."
