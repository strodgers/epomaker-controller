from typing import Iterator
from datetime import datetime
import dataclasses
import numpy as np
import cv2

IMAGE_DIMENSIONS = (162, 173)
BUFF_LENGTH: int = 128 // 2  # 128 bytes / 2 bytes per hex value

@dataclasses.dataclass
class PacketHeaderFormat:
    prefix: bytearray
    suffix: bytearray
    suffix_final: bytearray


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
        self.packet_header_format: PacketHeaderFormat | None = None # Must be defined in the subclass
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

    def insert_packet_headers(self, packet_headers: list[bytearray]) -> None:
        """Inserts headers for each packet in the command."""
        if self.packet_header_length == -1:
            raise ValueError("Header length must be set before inserting headers.")
        if self.total_packets - 1 != len(packet_headers):
            raise ValueError("Number of headers must match the number of packets.")

        header_data = np.array(packet_headers, dtype=np.uint8)

        self.command[1:, :self.packet_header_length] = header_data

    def __iter__(self) -> Iterator[bytes]:
        for packet in self.command:
            yield np.ndarray.tobytes(packet)

    @staticmethod
    def _calculate_checksum(buffer: bytes) -> bytes:
        sum_bits = 0
        for byte in buffer:
            sum_bits += byte
        if sum_bits == 0:
            return bytes(0)
        # Only use the lower 8 bits
        checksum = 0xff - sum_bits.to_bytes(2)[1]
        return checksum.to_bytes()

    def _generate_header_data(self) -> Iterator[bytearray]:
        if self.packet_header_format is None:
            raise ValueError("Packet header format must be defined before generating header data.")

        i = 0
        prefix = self.packet_header_format.prefix
        suffix = self.packet_header_format.suffix
        while i < self.total_packets - 2:
            data = prefix + bytearray.fromhex(f"{i:04x}")[::-1]  + suffix
            checksum = self._calculate_checksum(data)
            yield data + checksum
            i += 1
        
        suffix = self.packet_header_format.suffix_final
        data = prefix + bytearray.fromhex(f"{i:04x}")[::-1]  + suffix
        checksum = self._calculate_checksum(data)
        yield data + checksum

class EpomakerImageCommand(EpomakerCommand):
    """A command for sending images to the keyboard."""
    def __init__(self) -> None:
        initialization_data = bytearray.fromhex("a5000100f4da008b0000a2ad")
        packet_header_length = 8
        total_packets = 1002
        super().__init__(initialization_data, packet_header_length, total_packets)

        self.packet_header_format = PacketHeaderFormat(
            prefix=bytearray.fromhex("25000100"),
            suffix=bytearray.fromhex("38"),
            suffix_final=bytearray.fromhex("34")
            )
        header_data = [
            data for data in self._generate_header_data()
        ]

        super().insert_packet_headers(header_data)
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
        self.command[1:, self.packet_header_length:] = image_data

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

# test = EpomakerCommand(bytearray.fromhex("28000000000000d7"), packet_header_length=8, total_packets=1002)
# header_data = []
# for item in image_data_prefix:
#     header_data.append(bytearray.fromhex(item))
# test.insert_packet_headers(header_data)
