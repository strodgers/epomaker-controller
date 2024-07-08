"""EpomakerController module.

This module contains the EpomakerController class, which represents a controller
for an Epomaker USB HID device.
"""

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
    """EpomakerController class represents a controller for an Epomaker USB HID device.

    Attributes:
        vendor_id (int): The vendor ID of the USB HID device.
        product_id (int): The product ID of the USB HID device.
        device (hid.device): The HID device object.
        dry_run (bool): Whether to run in dry run mode.

    Methods:
        open_device: Opens the USB HID device and prints device information.
        send_basic_command: Sends a command to the HID device.
        close_device: Closes the USB HID device.
        format_current_time: Gets the current time and formats it into the required
            byte string format.
    """

    def __init__(
        self,
        interface_number: int,
        vendor_id: int = VENDOR_ID,
        product_id: int = PRODUCT_ID,
        dry_run: bool = True,
    ) -> None:
        """Initializes the EpomakerController object.

        Args:
            interface_number (int): The interface number of the USB HID device to use.
            vendor_id (int): The vendor ID of the USB HID device.
            product_id (int): The product ID of the USB HID device.
            dry_run (bool): Whether to run in dry run mode (default: True).
        """
        self.interface_number = interface_number
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = hid.device()
        self.dry_run = dry_run
        print(
            """WARNING: If this program errors out or you cancel early, the keyboard
              may become unresponsive. It should work fine again if you unplug and plug
               it back in!"""
        )

    def open_device(self, only_info: bool = False) -> bool:
        """Opens the USB HID device and prints device information.

        Args:
            only_info (bool): Whether to only print device information and exit (default: False).

        Returns:
            bool: True if the device is opened successfully, False otherwise.

        Raises:
            ValueError: If no device is found with the specified interface number.
        """
        if self.dry_run:
            print("Dry run: skipping device open")
            return True
        try:
            # Find the device with the specified interface number so we can open by path
            # This way we don't block usage of the keyboard whilst the device is open
            device_list = hid.enumerate(self.vendor_id, self.product_id)
            if only_info:
                import pprint
                pprint.pprint(device_list)
                return True
            device_path = None
            for device in device_list:
                if device["interface_number"] == self.interface_number:
                    device_path = device["path"]
                    break

            if device_path is None:
                available_devices = [device["interface_number"] for device in device_list]
                raise ValueError(
                    f"No device found with interface number {self.interface_number}\n"
                    f"Available devices: {available_devices}"
                )

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
        """Sends a command to the HID device.

        Args:
            command (EpomakerCommand): The command to send.
            sleep_time (float): The time to sleep between sending packets
                (default: 0.1).
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
    def _assert_range(value: int, r: range | None = None) -> bool:
        """Asserts that a value is within a specified range.

        Args:
            value (int): The value to check.
            r (range): The range to check against (default: None).

        Returns:
            bool: True if the value is within the range, False otherwise.
        """
        if not r:
            r = range(0, 100)
        return value in r

    def send_image(self, image_path: str) -> None:
        """Sends an image to the HID device.

        Args:
            image_path (str): The path to the image file.
        """
        image_command = EpomakerImageCommand.EpomakerImageCommand()
        image_command.encode_image(image_path)
        self._send_command(image_command, sleep_time=0.01)

    def send_time(self, time: datetime | None = None) -> None:
        """Sends `time` to the HID device.

        Args:
            time (datetime): The time to send (default: None).
        """
        if not time:
            time = datetime.now()
        time_command = EpomakerTimeCommand.EpomakerTimeCommand(time)
        self._send_command(time_command)

    def send_temperature(self, temperature: int) -> None:
        """Sends the temperature to the HID device.

        Args:
            temperature (int): The temperature value in C (0-100).

        Raises:
            ValueError: If the temperature is not in the range 0-100.
        """
        if not self._assert_range(temperature):
            raise ValueError("Temperature must be in range 0-100")
        temperature_command = EpomakerTempCommand.EpomakerTempCommand(temperature)
        self._send_command(temperature_command)

    def send_cpu(self, cpu: int, from_daemon: bool = False) -> None:
        """Sends the CPU percentage to the HID device.

        Args:
            cpu (int): The CPU percentage to send.
            from_daemon (bool): Indicates if the command is from a daemon process
                (default: False).

        Raises:
            ValueError: If the CPU percentage is not in the range 0-100 and
                from_daemon is False.
        """
        if not from_daemon:
            if not self._assert_range(cpu):
                raise ValueError("CPU percentage must be in range 0-100")
        cpu_command = EpomakerCpuCommand.EpomakerCpuCommand(cpu)
        self._send_command(cpu_command)

    def send_keys(self, frames: list[EpomakerKeyRGBCommand.KeyboardRGBFrame]) -> None:
        """Sends key RGB frames to the HID device.

        Args:
            frames (list): The list of KeyboardRGBFrame to send.
        """
        rgb_command = EpomakerKeyRGBCommand.EpomakerKeyRGBCommand(frames)
        self._send_command(rgb_command)

    def close_device(self) -> None:
        """Closes the USB HID device."""
        if self.device:
            self.device.close()
            self.device = None

    def __del__(self) -> None:
        """Destructor to ensure the device is closed."""
        self.close_device()
