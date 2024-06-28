from datetime import datetime
import time
import hid

from .commands import (
    EpomakerCommand,
    EpomakerImageCommand,
    EpomakerTimeCommand,
    EpomakerTempCommand,
    EpomakerCpuCommand,
    EpomakerKeyRGBCommand,
)
from .commands.data.constants import BUFF_LENGTH

VENDOR_ID = 0x3151
PRODUCT_ID = 0x4010


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

    def __init__(
        self,
        vendor_id: int = VENDOR_ID,
        product_id: int = PRODUCT_ID,
        dry_run: bool = True,
    ) -> None:
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
            self.device.set_nonblocking(1)
            print(f"Manufacturer: {self.device.get_manufacturer_string()}")
            print(f"Product: {self.device.get_product_string()}")
            # Commenting this out as it's always some symbol
            # print(f"Serial No: {self.device.get_serial_number_string()}")
            print("WARNING: If this program errors out or you cancel early, the keyboard may become unresponsive. It should work fine again if you unplug and plug it back in!")
            return True
        except Exception as e:
            print(f"Failed to open device: {e}")
            return False

    def _send_command(
        self, command: EpomakerCommand.EpomakerCommand, sleep_time: float = 0.1
    ) -> None:
        """
        Sends a command to the HID device.
        """
        assert command.report_data_prepared
        for packet in command:
            assert len(packet) == BUFF_LENGTH
            if self.dry_run:
                print(f"Dry run: skipping command send: {packet!r}")
            elif self.device:
                self.device.send_feature_report(packet.get_all_bytes())
            time.sleep(sleep_time)

    def send_image(self, image_path: str) -> None:
        """
        Sends an image to the HID device.
        """
        image_command = EpomakerImageCommand.EpomakerImageCommand()
        image_command.encode_image(image_path)
        self._send_command(image_command, sleep_time=0.01)

    def send_time(self, time: datetime = datetime.now()) -> None:
        """
        Sends the current time to the HID device.
        """
        time_command = EpomakerTimeCommand.EpomakerTimeCommand(time)
        self._send_command(time_command)

    def send_temperature(self, temperature: int) -> None:
        """
        Sends the temperature to the HID device.
        """
        temperature_command = EpomakerTempCommand.EpomakerTempCommand(temperature)
        self._send_command(temperature_command)

    def send_cpu(self, cpu: int) -> None:
        """
        Sends the CPU percentage to the HID device.
        """
        cpu_command = EpomakerCpuCommand.EpomakerCpuCommand(cpu)
        self._send_command(cpu_command)

    def send_keys(self, frames: list[EpomakerKeyRGBCommand.KeyboardRGBFrame]) -> None:
        rgb_command = EpomakerKeyRGBCommand.EpomakerKeyRGBCommand(frames)
        self._send_command(rgb_command)

    def close_device(self) -> None:
        """
        Closes the USB HID device.
        """
        if self.device:
            self.device.close()

    def __del__(self) -> None:
        self.close_device()
