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
INTERFACE_NUMBER = 1

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
        print("WARNING: If this program errors out or you cancel early, the keyboard may become unresponsive. It should work fine again if you unplug and plug it back in!")


    def open_device(self) -> bool:
        """
        Opens the USB HID device and prints device information.
        Returns True if the device is successfully opened.
        """
        if self.dry_run:
            print("Dry run: skipping device open")
            return True
        try:
            # Find the device with the specified interface number so we can open by path
            # This way we don't block usage of the keyboard whilst the device is open
            device_list = hid.enumerate(self.vendor_id, self.product_id)
            device_path = None
            for device in device_list:
                if device['interface_number'] == INTERFACE_NUMBER:
                    device_path = device['path']
                    break

            if device_path is None:
                raise ValueError(f"No device found with interface number {INTERFACE_NUMBER}")

            self.device = hid.device()
            self.device.open_path(device_path)
            # print(f"Manufacturer: {self.device.get_manufacturer_string()}")
            # print(f"Product: {self.device.get_product_string()}")
            # print(f"Serial No: {self.device.get_serial_number_string()}")
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

    @staticmethod
    def _assert_range(value: int, r: range = range(0, 100)) -> bool:
        return value in r

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
        if not self._assert_range(temperature):
            raise ValueError("Temperature must be in range 0-100")
        temperature_command = EpomakerTempCommand.EpomakerTempCommand(temperature)
        self._send_command(temperature_command)

    def send_cpu(self, cpu: int, from_daemon: bool=False) -> None:
        """
        Sends the CPU percentage to the HID device.
        """
        if not from_daemon:
            if not self._assert_range(cpu):
                raise ValueError("CPU percentage must be in range 0-100")
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
            self.device = None

    def __del__(self) -> None:
        self.close_device()
