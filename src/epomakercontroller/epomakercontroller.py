import datetime
import math
import time
from enum import Enum
import numpy as np
import hid
import cv2

from epomakercontroller.data.command_data import image_data_prefix

VENDOR_ID = 0x3151
PRODUCT_ID = 0x4010
IMAGE_DIMENSIONS = (162, 173)
BUFF_LENGTH: int = 128

class EpomakerCommands(Enum):
    """Init commands for various functions of the RT100 keyboard.

    Args:
        Enum (TIME): Set the time on the keyboard.
        Enum (TEMP): Set the temperature on the keyboard.
        Enum (CPU): Set the CPU percentage on the keyboard.
        Enum (IMAGE): Set the image on the keyboard.
    """
    TIME: str = "28000000000000d7"
    TEMP: str = "2a000000000000d5"
    CPU: str = "22000000000000dd63007f0004000800"
    IMAGE: str = "a5000100f4da008b0000a2ad"

class EpomakerController:
    """
    EpomakerController class represents a controller for an Epomaker USB HID device.

    Attributes:
        vendor_id (int): The vendor ID of the USB HID device.
        product_id (int): The product ID of the USB HID device.
        device (hid.device): The HID device object.

    Methods:
        open_device(vendor_id, product_id): Opens the USB HID device and prints device information.
        send_basic_command(command, command_type): Sends a command to the HID device.
        close_device(): Closes the USB HID device.
        format_current_time(): Gets the current time and formats it into the required byte string
        format.
    """

    def __init__(self, vendor_id: int=VENDOR_ID, product_id: int=PRODUCT_ID,
                 dry_run: bool=True) -> None:
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = hid.device()
        self.dry_run = dry_run

    def open_device(self) -> bool:
        """
        Opens the USB HID device and prints device information.
        Returns True if the device is successfully opened.
        """
        if self.dry_run:
            print("Dry run: skipping device open")
            return True
        try:
            self.device.open(self.vendor_id, self.product_id)
            print(f"Manufacturer: {self.device.get_manufacturer_string()}")
            print(f"Product: {self.device.get_product_string()}")
            print(f"Serial No: {self.device.get_serial_number_string()}")
            return True
        except Exception as e:
            print(f"Failed to open device: {e}")
            return False

    def send_basic_command(self, command: str, command_type: EpomakerCommands) -> None:
        """
        Sends a command to the HID device.
        """
        print(f"Sending command: {command_type.name} - {command}")
        self._send_basic_command(command_type.value + command)

    @staticmethod
    def _pad_command(command: str, buff_lenth: int = BUFF_LENGTH) -> str:
        """
        Pads the command with 0s to make it buff_lenth characters long.
        """
        return command + "00" * (int(buff_lenth / 2) - len(command) // 2)

    def _send_basic_command(self, command: str, sleep_time: float=0.1, pad: bool=True) -> None:
        """
        Sends a hexadecimal command to the HID device.
        """
        if len(command) != BUFF_LENGTH:
            if len(command) % 2 != 0:
                print("Command length must be a multiple of 2")
                return
            elif len(command) > BUFF_LENGTH:
                print("Command length must be less than BUFF_LENGTH")
                return
            elif len(command) < BUFF_LENGTH:
                if pad:
                    command = self._pad_command(command)
                else:
                    raise ValueError("Command length must be BUFF_LENGTH")

        # Remove colons and convert to bytes
        command = command.replace(":", "")
        data_hex = bytes.fromhex(command)
        if self.dry_run:
            print(f"Dry run: skipping command send: {data_hex!r}")
            return
        if self.device:
            self.device.send_feature_report(data_hex)
            time.sleep(sleep_time)


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

    def send_image(self, image_path: str, log_to_file: str = ".send_image_bytes.log") -> None:
        """
        Sends an image to the HID device.
        It is expecting a 16-bit RGB565 image with dimensions of 162x173.
        For some reason the data is also sent flipped vertically and rotated 90 degrees.
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


        # self.device.close()
        image_data = ""
        for row in image_16bit:
            image_data += ''.join([hex(val)[2:].zfill(4) for val in row])

        # Initialize the command
        self.send_basic_command("", EpomakerCommands.IMAGE)
        buffer_length = BUFF_LENGTH - len(image_data_prefix[0])

        with open(log_to_file, "w", encoding="utf-8") as file:
            chunks = math.floor(len(image_data) / buffer_length)
            i = 0
            while i < chunks:
                image_byte_segment = image_data[i*buffer_length:(i+1)*buffer_length]
                file.write(f"{image_byte_segment}\n")
                try:
                    command = image_data_prefix[i] + image_data[i*buffer_length:(i+1)*buffer_length]
                    self._send_basic_command(command, sleep_time=0.05, pad=False)
                except Exception as e:
                    print(f"Exception while sending image data: {e}")
                file.write(f"{command}\n")
                i += 1


            # Send the remainders
            command = image_data_prefix[i] + image_data[i*buffer_length:]
            self._send_basic_command(command, sleep_time=0.05)
            pass



        # Send the image data
        pass

    @staticmethod
    def format_current_time() -> str:
        """
        Gets the current time and formats it into the required byte string format.
        Returns the formatted command string to send to the device.
        """
        now = datetime.datetime.now()
        print("Using current time:", now)

        # Example of formatting for a specific date and time format
        # Adjust the formatting based on your specific requirements
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second

        # Convert to hexadecimal strings
        year_hex = f"{year:04x}"
        month_hex = f"{month:02x}"
        day_hex = f"{day:02x}"
        hour_hex = f"{hour:02x}"
        minute_hex = f"{minute:02x}"
        second_hex = f"{second:02x}"

        command = f"{year_hex}{month_hex}{day_hex}{hour_hex}{minute_hex}{second_hex}"

        return command

    def close_device(self) -> None:
        """
        Closes the USB HID device.
        """
        if self.device:
            self.device.close()

    def __del__(self) -> None:
        self.close_device()

