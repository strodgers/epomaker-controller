from typing import Iterator
from datetime import datetime
import dataclasses
import numpy as np
import cv2
import numpy.typing as npt

from .data.key_map import KeyboardKey, KeyboardRGBFrame, KeyMap

IMAGE_DIMENSIONS = (162, 173)
BUFF_LENGTH: int = 128 // 2  # 128 bytes / 2 bytes per hex value

@dataclasses.dataclass()
class Report:
    """Represents the data that is sent to the keyboard."""
    header_format_string: str
    checksum_index: int | None
    index: int
    pad_on_init: bool = True
    header_format_values: dict[str, int] = dataclasses.field(default_factory=dict)
    report_bytearray: bytearray | None = None,
    header_length: int | None = None
    def __post_init__(self) -> None:
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
            f"Report length {len(self.report_bytearray)} exceeds the maximum length of "
            f"{BUFF_LENGTH}."
            )
        self.header_length = len(self.report_bytearray)
        if self.pad_on_init:
            self._pad()

    def _pad(self) -> None:
        """Pads the report header with zeros to the maximum length."""
        assert self.report_bytearray is not None, "Report bytearray must be set before padding."
        self.report_bytearray += bytes(BUFF_LENGTH - len(self.report_bytearray))

    @staticmethod
    def _calculate_checksum(buffer: bytes) -> bytes:
        sum_bits = sum(buffer) & 0xFF
        checksum = (0xFF - sum_bits) & 0xFF
        return bytes([checksum])

    def _get_checksum(self) -> bytes:
        assert self.report_bytearray is not None, "Report bytearray must be set before getting."
        assert self.checksum_index is not None, "Checksum index must be set before getting."
        return self[self.checksum_index]

    def _get_header(self) -> bytes:
        assert self.header_length is not None, "Header length must be set before getting."
        assert self.report_bytearray is not None, "Report bytearray must be set before getting."
        return self.report_bytearray[:self.header_length]

    def __getitem__(self, key: int | slice) -> bytes:
        assert self.report_bytearray is not None, "Report bytearray must be set before getting."
        return bytes(self.report_bytearray[key])

@dataclasses.dataclass()
class ReportWithData(Report):
    def __init__(self, header_format_string: str, checksum_index: int | None, index: int,
                 header_format_values: dict[str, int] = dataclasses.field(default_factory=dict),
                 report_bytearray: bytearray | None = None,
                 header_length: int | None = None,
                 report_data: bytearray | None = None,
                 prepared: bool = False,
                 ) -> None:
        super().__init__(header_format_string, checksum_index, index, False, header_format_values,
                         report_bytearray, header_length)
        self.report_data: bytearray | None = report_data
        self.prepared: bool = prepared
        if self.report_data is not None:
            self.prepared = True

    def add_data(self, data: bytes) -> None:
        assert self.prepared is False, "Report data has already been set."
        assert self.report_bytearray is not None, "Report bytearray must be set before adding data."
        self.report_data = bytearray(data)
        self.report_bytearray += self.report_data
        self._pad()
        self.prepared = True

    # def __getitem__(self, key: int | slice) -> bytes:
    #     assert self.report_bytearray is not None, "Report bytearray must be set before getting."
    #     assert self.report_data is not None, "Report data must be set before getting."
    #     return bytes((self.report_bytearray + self.report_data)[key])

@dataclasses.dataclass(frozen=True)
class CommandStructure:
    number_of_starter_reports: int = 1
    number_of_data_reports: int = 0
    number_of_footer_reports: int = 0

    def __len__(self) -> int:
        return self.number_of_starter_reports + self.number_of_data_reports + self.number_of_footer_reports

class EpomakerCommand():
    """A command is basically just a wrapper around a numpy array of bytes.

    The command must have x dimension of 128 bytes and be padded with zeros if the command is
    less than 128 bytes.

    The command may have a y dimension of at least 1, and more if the command is a series of
    packets to be sent (eg image, key colours). Each row of extra packets must also have an
    associated header according to the commannd type.
    """
    def __init__(self,  initial_report: Report,
                 structure: CommandStructure = CommandStructure(),
                ) -> None:
        self.reports: list[Report] = []
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
        assert report.index not in [r.index for r in self.reports], (
            f"Report index {report.index} already exists."
            )
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

class EpomakerImageCommand(EpomakerCommand):
    """A command for sending images to the keyboard."""
    def __init__(self) -> None:
        initialization_data = "a5000100f4da008b0000a2ad"
        self.report_data_header_length = 8
        structure = CommandStructure(
            number_of_starter_reports=1,
            number_of_data_reports=1000,
            number_of_footer_reports=1
            )
        initial_report = Report(initialization_data, index=0, checksum_index=None)
        super().__init__(initial_report, structure)

    def get_data_reports(self) -> list[ReportWithData]:
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
        r |= (r >> 5)
        g |= (g >> 6)
        b |= (b >> 5)

        return (r, g, b)

    def encode_image(self, image_path: str) -> None:
        """
        Encode an image to 16-bit RGB565 according to IMAGE_DIMENSIONS and accounting for packet
        headers.

        The image is also rotated and flipped since this seems to be what the keyboard is expecting.
        """
        image = cv2.imread(image_path)
        image = cv2.resize(image, IMAGE_DIMENSIONS)
        image = cv2.flip(image, 0)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image_16bit = np.zeros((IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1]), dtype=np.uint16)
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
                checksum_index=7
            )
            report.add_data(image_8bit_flattened[
                data_buff_pointer:data_buff_pointer + data_buff_length
                ].tobytes())
            data_buff_pointer += data_buff_length
            self._insert_report(report)

        assert len(self.get_data_reports()) == self.structure.number_of_data_reports, (
            f"Expected {self.structure.number_of_data_reports} reports, got "
            f"{len(self.get_data_reports())}."
            )

        self.report_data_prepared = True

        # Add the footer report
        footer_index_bytes = (self.structure.number_of_starter_reports + self.structure.number_of_data_reports - self.structure.number_of_footer_reports).to_bytes(2, "big")
        footer_report = ReportWithData(
            header_format_string="25000100{footer_index_bytes_upper:02x}{footer_index_bytes_lower:02x}34",
            index=self.structure.number_of_starter_reports + self.structure.number_of_data_reports,
            header_format_values={
                    "footer_index_bytes_upper": footer_index_bytes[1],
                    "footer_index_bytes_lower": footer_index_bytes[0],
                },
            checksum_index=7
            )
        footer_report.add_data(image_8bit_flattened[
            data_buff_pointer:data_buff_pointer + data_buff_length
            ].tobytes())
        # Need some padding at the end of the image data
        footer_report._pad()
        self._insert_report(footer_report)

        self.report_footer_prepared = True

        assert len(self.reports) == len(self.structure), (
            f"Expected {len(self.structure)} reports, got {len(self.reports)}."
            )

class EpomakerKeyRGBCommand(EpomakerCommand):
    """Change a selection of keys to specific RGB values."""
    def __init__(self, frames: list[KeyboardRGBFrame]) -> None:
        initialization_data = "18000000000000e7"
        self.report_data_header_length = 8
        data_reports_per_frame = 7
        structure = CommandStructure(
            number_of_starter_reports=1,
            number_of_data_reports=len(frames) * data_reports_per_frame,
            number_of_footer_reports=0
            )
        initial_report = Report(
            initialization_data,
            index=0,
            checksum_index=None)
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
                    checksum_index=7
                    )
                # Zero out the data buffer
                data_byterarray = bytearray(data_buffer_length)
                for key_index, rgb in frame.key_map:
                    # For each key, set the RGB values in the data buffer
                    for i, colour in enumerate(rgb):
                        # R, G, B individually
                        this_frame_colour_index = (key_index * 3) - (this_frame_report_index * data_buffer_length) + i
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
            report_data = report[self.report_data_header_length:]
            if report_index_count <= index < report_index_count + data_buffer_length:
                return True
            report_index_count += len(report_data)
        return False

class EpomakerTimeCommand(EpomakerCommand):
    """A command for setting the time on the keyboard."""
    def __init__(self, time: datetime) -> None:
        initialization_data = "28000000000000d7" + self._format_time(time)
        initial_report = Report(initialization_data,
                                index=0,
                                checksum_index=None)
        super().__init__(initial_report)

    @staticmethod
    def _format_time(time: datetime) -> str:
        """
        Gets the current time and formats it into the required byte string format.
        Returns the formatted command string to send to the device.
        """
        print("Using:", time)

        # Example of formatting for a specific date and time format
        # Adjust the formatting based on your specific requirements
        year = time.year
        month = time.month
        day = time.day
        hour = time.hour
        minute = time.minute
        second = time.second

        # Convert to hexadecimal strings
        year_hex = f"{year:04x}"
        month_hex = f"{month:02x}"
        day_hex = f"{day:02x}"
        hour_hex = f"{hour:02x}"
        minute_hex = f"{minute:02x}"
        second_hex = f"{second:02x}"

        command = f"{year_hex}{month_hex}{day_hex}{hour_hex}{minute_hex}{second_hex}"

        return command

class EpomakerTempCommand(EpomakerCommand):
    """A command for setting the temperature on the keyboard."""
    def __init__(self, temp: int) -> None:
        initialization_data = "2a000000000000d5" + f"{temp:02x}"
        initial_report = Report(initialization_data,
                                index=0,
                                checksum_index=None)
        super().__init__(initial_report)

class EpomakerCpuCommand(EpomakerCommand):
    """A command for setting the CPU usage on the keyboard."""
    def __init__(self, cpu: int) -> None:
        initialization_data = "22000000000000dd63007f0004000800" + f"{cpu:02x}"
        initial_report = Report(initialization_data,
                                index=0,
                                checksum_index=None)
        super().__init__(initial_report)


# class EpomakerProfileCommand(EpomakerSimpleCommand):
#     """A command for setting the profile on the keyboard."""
#     class ProfileMode(Enum):
#         EPOMAKER_MODE_ALWAYS_ON                         = 0x01,
#         EPOMAKER_MODE_DYNAMIC_BREATHING                 = 0x02,
#         EPOMAKER_MODE_SPECTRUM_CYCLE                    = 0x03,
#         EPOMAKER_MODE_DRIFT                             = 0x04,
#         EPOMAKER_MODE_WAVES_RIPPLE                      = 0x05,
#         EPOMAKER_MODE_STARS_TWINKLE                     = 0x06,
#         EPOMAKER_MODE_STEADY_STREAM                     = 0x07,
#         EPOMAKER_MODE_SHADOWING                         = 0x08,
#         EPOMAKER_MODE_PEAKS_RISING_ONE_AFTER_ANOTHER    = 0x09,
#         EPOMAKER_MODE_SINE_WAVE                         = 0x0a,
#         EPOMAKER_MODE_CAISPRING_SURGING                 = 0x0b,
#         EPOMAKER_MODE_FLOWERS_BLOOMING                  = 0x0c,
#         EPOMAKER_MODE_LASER                             = 0x0e,
#         EPOMAKER_MODE_PEAK_TURN                         = 0x0f,
#         EPOMAKER_MODE_INCLINED_RAIN                     = 0x10,
#         EPOMAKER_MODE_SNOW                              = 0x11,
#         EPOMAKER_MODE_METEOR                            = 0x12,
#         EPOMAKER_MODE_THROUGH_THE_SNOW_NON_TRACE        = 0x13,
#         EPOMAKER_MODE_LIGHT_SHADOW                      = 0x15

#     def __init__(self, mode: ProfileMode, ) -> None:
#         initialization_data = bytearray.fromhex(
#             "07"
#             + f"{profile:02x}"
#             )
#         super().__init__(initialization_data

# test = EpomakerCommand(bytearray.fromhex("28000000000000d7"), packet_header_length=8, total_packets=1002)
# header_data = []
# for item in image_data_prefix:
#     header_data.append(bytearray.fromhex(item))
# test._insert_packet_headers(header_data)
