from typing import Iterator
from datetime import datetime
import dataclasses
import numpy as np
import cv2

from .data.key_map import KeyboardKey, KeyboardRGBFrame, KeyMap

IMAGE_DIMENSIONS = (162, 173)
BUFF_LENGTH: int = 128 // 2  # 128 bytes / 2 bytes per hex value

@dataclasses.dataclass
class PacketHeaderFormat:
    format_string: str
    has_checksum: bool = True

class EpomakerCommand():
    """A command is basically just a wrapper around a numpy array of bytes.

    The command must have x dimension of 128 bytes and be padded with zeros if the command is
    less than 128 bytes.

    The command may have a y dimension of at least 1, and more if the command is a series of
    packets to be sent (eg image, key colours). Each row of extra packets must also have an
    associated header according to the commannd type.
    """
    def __init__(self, initialization_data: bytearray, packet_header_length: int = 0,
                 total_packets: int=1) -> None:
        self.command = np.zeros((total_packets, BUFF_LENGTH), dtype=np.uint8)
        self.packet_header_length: int = packet_header_length
        self.total_packets: int = total_packets
        # If there are multiple packets, the command must be prepared before sending
        self.packets_prepared: bool = self.total_packets == 1

        # Set the first row of the command to the initialization data
        self.command[0, :len(initialization_data)] = initialization_data

    @staticmethod
    def _np16_to_np8(data_16bit: np.ndarray[np.uint16]) -> np.ndarray[np.uint8]:
        """Converts a numpy array of 16-bit numbers to 8-bit numbers."""
        new_shape = (data_16bit.shape[0], data_16bit.shape[1] * 2)
        data_8bit_flat = np.empty(data_16bit.size * 2, dtype=np.uint8)

        data_8bit_flat[0::2] = (data_16bit >> 8).flatten()  # High bytes
        data_8bit_flat[1::2] = (data_16bit & 0xFF).flatten()  # Low bytes

        return data_8bit_flat.reshape(new_shape)

    def _insert_packet_headers(self, packet_headers: list[bytearray]) -> None:
        """Inserts headers for each packet in the command."""
        if self.packet_header_length == -1:
            raise ValueError("Header length must be set before inserting headers.")
        if self.total_packets - 1 != len(packet_headers):
            raise ValueError("Number of headers must match the number of packets.")

        header_data = np.array(packet_headers, dtype=np.uint8)

        self._get_header_view()[:,:] = header_data

    def __iter__(self) -> Iterator[bytes]:
        for packet in self.command:
            yield np.ndarray.tobytes(packet)

    def _get_data_view(self, subset: tuple[int, int] = (-1, -1)) -> np.ndarray[np.uint8]:
        """ Returns a view of the data portion of the command."""
        data_view = self.command[1:, self.packet_header_length:]
        if subset != (-1, -1):
            return data_view[subset[0]:subset[1], :]
        return data_view

    def _get_header_view(self) -> np.ndarray[np.uint8]:
        """ Returns a view of the header portion of the command."""
        return self.command[1:, :self.packet_header_length]

    def _get_instruction_view(self) -> np.ndarray[np.uint8]:
        """ Returns a view of the instruction portion of the command."""
        return self.command[:1,:]


    @staticmethod
    def _calculate_checksum(buffer: bytes) -> bytes:
        sum_bits = sum(buffer) & 0xFF
        checksum = (0xFF - sum_bits) & 0xFF
        return bytes([checksum])

    def _generate_header_data(self, packet_header_format: PacketHeaderFormat, count_range: range,
                              format_args: dict[str, int] = {}) -> Iterator[bytearray]:
        if packet_header_format is None:
            raise ValueError("Packet header must be defined before generating header data.")

        for packet_index in count_range:
            formatted_string = packet_header_format.format_string.format(
                **format_args,
                packet_index_bytes=packet_index.to_bytes(2, "big")
                )
            data = bytearray.fromhex(formatted_string)
            if packet_header_format.has_checksum:
                data += self._calculate_checksum(data)

            yield data

        # def format_bytearray(index: int, format_string: str, has_checksum: bool) -> bytearray:
        #     ret = bytearray.fromhex(format_string.format(
        #         id_bytes=index.to_bytes(2, "big")
        #         ))
        #     if has_checksum:
        #         ret += self._calculate_checksum(ret)
        #     return ret

        # i = 0
        # while i < self.total_packets - 2:
        #     yield format_bytearray(i,
        #                            packet_header_format.format_string,
        #                            packet_header_format.has_checksum,
        #                            )
        #     i += 1

        # yield format_bytearray(i,
        #                        packet_header_format.format_string_final,
        #                        packet_header_format.has_checksum,
        #                        )

class EpomakerImageCommand(EpomakerCommand):
    """A command for sending images to the keyboard."""
    def __init__(self) -> None:
        initialization_data = bytearray.fromhex("a5000100f4da008b0000a2ad")
        packet_header_length = 8
        total_packets = 1002
        super().__init__(initialization_data, packet_header_length, total_packets)

        header_data = []
        packet_header_format = PacketHeaderFormat(
            format_string="25000100{packet_index_bytes[1]:02x}{packet_index_bytes[0]:02x}38",
            )
        header_data += [
            *self._generate_header_data(
                packet_header_format,
                range(0, total_packets-2),
            )
        ]

        # End is different
        packet_header_format = PacketHeaderFormat(
            format_string="25000100{packet_index_bytes[1]:02x}{packet_index_bytes[0]:02x}34"
            )
        header_data += [
            *self._generate_header_data(
                packet_header_format,
                range(total_packets-2, total_packets-1),
            )
        ]

        # header_data = [
        #     data for data in self._generate_header_data(packet_header_format)
        # ]

        super()._insert_packet_headers(header_data)
        self.image_data = np.zeros(
            (total_packets - 1, BUFF_LENGTH - packet_header_length),
            dtype=np.uint8
            )

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

        image_8bit = self._np16_to_np8(image_16bit)
        image_data_buff_length = BUFF_LENGTH - self.packet_header_length
        image_data = np.pad(
            image_8bit.flatten(),
            (0, 4),
            "constant"
            ).reshape(((self.total_packets - 1, image_data_buff_length)))
        self._get_data_view()[:,:] = image_data
        self.packets_prepared = True


class EpomakerSimpleCommand(EpomakerCommand):
    """A command for sending simple commands to the keyboard (no extra packets)."""
    def __init__(self, command: bytearray) -> None:
        packet_header_length = 0
        total_packets = 1
        super().__init__(command, packet_header_length, total_packets)


class EpomakerTimeCommand(EpomakerSimpleCommand):
    """A command for setting the time on the keyboard."""
    def __init__(self, time: datetime) -> None:
        initialization_data = bytearray.fromhex(
            "28000000000000d7"
            + self._format_time(time)
            )
        super().__init__(initialization_data)

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

class EpomakerTempCommand(EpomakerSimpleCommand):
    """A command for setting the temperature on the keyboard."""
    def __init__(self, temp: int) -> None:
        initialization_data = bytearray.fromhex(
            "2a000000000000d5"
            + f"{temp:02x}"
            )
        super().__init__(initialization_data)

class EpomakerCpuCommand(EpomakerSimpleCommand):
    """A command for setting the CPU usage on the keyboard."""
    def __init__(self, cpu: int) -> None:
        initialization_data = bytearray.fromhex(
            "22000000000000dd63007f0004000800"
            + f"{cpu:02x}"
            )
        super().__init__(initialization_data)

class EpomakerKeyRGBCommand(EpomakerCommand):
    """Change a selection of keys to specific RGB values."""
    def __init__(self, frames: list[KeyboardRGBFrame]) -> None:
        packet_header_length = 8
        total_packets = (7*len(frames)) + 1
        super().__init__(bytearray.fromhex("18000000000000e7"), packet_header_length, total_packets)

        header_data = []
        packet_header_format = PacketHeaderFormat(
            format_string="19{packet_index_bytes[1]:02x}{frame_index:02x}{total_frames:02x}{frame_time:02x}0000",
            # format_string_final="19{id_bytes[1]:02x}0001320000"
            )
        for frame in frames:
            header_data += [
                *self._generate_header_data(
                    packet_header_format,
                    range(0, 7),
                    {
                        "frame_index": frame.index,
                        "total_frames": len(frames),
                        "frame_time": frame.time_ms,
                    }
                )
            ]
        super()._insert_packet_headers(header_data)
        for frame in frames:
            for key_index, rgb in frame.key_map:
                self._apply_keymask(key_index, rgb, frame)

    def _apply_keymask(self, key_index: int, rgb: tuple[int, int, int], frame: KeyboardRGBFrame) -> None:
        data_start = frame.index * frame.length
        data_end = data_start + frame.length
        current_packet_data = self._get_data_view((data_start, data_end))
        for i in range(3):
            data_index = np.unravel_index(
                key_index*3 + i,
                current_packet_data.shape
                )
            current_packet_data[data_index] = rgb[i]


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
