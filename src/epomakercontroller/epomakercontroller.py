"""EpomakerController module.

This module contains the EpomakerController class, which represents a controller
for an Epomaker USB HID device.
"""

import dataclasses
from datetime import datetime
from json import dumps
import os
import time
from typing import Any, Optional
import hid  # type: ignore[import-not-found]
import signal
import subprocess
from types import FrameType
import re

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
# Some Epomaker keyboards seem to have have different product IDs
PRODUCT_IDS_WIRED = [0x4010, 0x4015]
PRODUCT_IDS_24G = [0x4011, 0x4016]

USE_WIRELESS = False
PRODUCT_IDS = PRODUCT_IDS_WIRED
if USE_WIRELESS:
    PRODUCT_IDS += PRODUCT_IDS_24G


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
        vendor_id: int = VENDOR_ID,
        dry_run: bool = True,
    ) -> None:
        """Initializes the EpomakerController object.

        Args:
            vendor_id (int): The vendor ID of the USB HID device.
            dry_run (bool): Whether to run in dry run mode (default: True).
        """
        self.vendor_id = vendor_id
        self.device = hid.device()
        self.dry_run = dry_run
        self.device_list: list[dict[str, Any]] = []
        print(
            """WARNING: If this program errors out or you cancel early, the keyboard
              may become unresponsive. It should work fine again if you unplug and plug
               it back in!"""
        )

        # Set up signal handling
        self._setup_signal_handling()

    def _setup_signal_handling(self) -> None:
        """Sets up signal handling to close the HID device on termination."""
        signal.signal(signal.SIGINT, self._signal_handler)  # Handle Ctrl+C
        signal.signal(signal.SIGTERM, self._signal_handler)  # Handle termination

    def _signal_handler(self, sig: int, frame: Optional[FrameType]) -> None:
        """Handles signals to ensure the HID device is closed."""
        self.close_device()
        os._exit(0)  # Exit immediately after closing the device

    def __del__(self) -> None:
        """Destructor to ensure the device is closed."""
        self.close_device()

    def open_device(self, only_info: bool = False) -> bool:
        """Opens the USB HID device and prints device information.

        Args:
            only_info (bool): Print device information and exit (default: False).

        Raises:
            ValueError: If no device is found with the specified interface number.

        Returns:
            bool: True if the device is opened successfully, False otherwise.
        """
        if self.dry_run:
            print("Dry run: skipping device open")
            return True

        product_id = self._find_product_id()
        if not product_id:
            raise ValueError("No Epomaker RT100 devices found")

        if only_info:
            self._print_device_info()
            return True

        # Find the device with the specified interface number so we can open by path
        # This way we don't block usage of the keyboard whilst the device is open
        device_path = self._find_device_path()
        if device_path is None:
            raise ValueError(
                "No device found"
            )
        self._open_device(device_path)

        return self.device is not None

    def _find_product_id(self) -> int | None:
        """Finds the product ID of the device using a list of possible product IDs.

        Returns:
            int | None: The product ID if found, None otherwise.
        """
        for pid in PRODUCT_IDS:
            self.device_list = hid.enumerate(self.vendor_id, pid)
            if self.device_list:
                return pid
        return None

    def _open_device(self, device_path: bytes) -> None:
        """Opens the USB HID device.

        Args:
            device_path (bytes): The path to the device.
        """
        try:
            self.device = hid.device()
            self.device.open_path(device_path)
        except IOError as e:
            print(
                f"Failed to open device: {e}\n"
                "Please make sure the device is connected\n"
                "and you have the necessary permissions.\n\n"
                "You may need to run this program as root or with sudo, or\n"
                "set up a udev rule to allow access to the device.\n\n"
            )
            self.device = None

    def generate_udev_rule(self) -> None:
        """Generates a udev rule for the connected keyboard."""
        rule_content = (
            f"# Epomaker RT100 keyboard\n"
            f'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{self.vendor_id:04x}", '
            f'ATTRS{{idProduct}}=="{self._find_product_id():04x}", MODE="0666", '
            'GROUP="plugdev"\n\n'
        )

        rule_file_path = "/etc/udev/rules.d/99-epomaker-rt100.rules"

        print("Generating udev rule for Epomaker RT100 keyboard")
        print(f"Rule content:\n{rule_content}")
        print(f"Rule file path: {rule_file_path}")
        print("Please enter your password if prompted")

        # Write the rule to a temporary file
        temp_file_path = "/tmp/99-epomaker-rt100.rules"
        with open(temp_file_path, "w") as temp_file:
            temp_file.write(rule_content)

        # Move the file to the correct location, reload rules

        move_command = ["mv", temp_file_path, rule_file_path]
        reload_command = ["udevadm", "control", "--reload-rules"]
        trigger_command = ["udevadm", "trigger"]

        if os.geteuid() != 0:
            # Use sudo if not root
            move_command = ["sudo"] + move_command
            reload_command = ["sudo"] + reload_command
            trigger_command = ["sudo"] + trigger_command

        subprocess.run(move_command, check=True)
        subprocess.run(reload_command, check=True)
        subprocess.run(trigger_command, check=True)

        print("Rule generated successfully")

    def _print_device_info(self) -> None:
        """Prints device information."""
        devices = self.device_list.copy()
        for device in devices:
            device["path"] = device["path"].decode("utf-8")
            device["vendor_id"] = f"0x{device['vendor_id']:04x}"
            device["product_id"] = f"0x{device['product_id']:04x}"
        print(
            dumps(
                devices,
                indent="  ",
            )
        )

    @dataclasses.dataclass
    class HIDInfo:
        device_name: str
        event_path: str
        hid_path: Optional[str] = None

    @staticmethod
    def _find_device_path() -> Optional[bytes]:
        """Finds the device path with the specified interface number.

        Returns:
            Optional[bytes]: The device path if found, None otherwise.
        """
        description = r"ROYUAN .* System Control"
        input_dir = "/sys/class/input"
        hid_infos = EpomakerController._get_hid_infos(input_dir, description)

        if not hid_infos:
            print(f"No events found with description: '{description}'")
            return None

        EpomakerController._populate_hid_paths(hid_infos)

        return EpomakerController._select_device_path(hid_infos)

    @staticmethod
    def _get_hid_infos(input_dir: str, description: str) -> list[HIDInfo]:
        """Retrieve HID information based on the given description."""
        hid_infos = []
        for event in os.listdir(input_dir):
            if event.startswith("event"):
                device_name_path = os.path.join(input_dir, event, "device", "name")
                try:
                    with open(device_name_path, "r") as f:
                        device_name = f.read().strip()
                        if re.search(description, device_name):
                            event_path = os.path.join(input_dir, event)
                            hid_infos.append(
                                EpomakerController.HIDInfo(device_name, event_path)
                            )
                except FileNotFoundError:
                    continue
        return hid_infos

    @staticmethod
    def _populate_hid_paths(hid_infos: list[HIDInfo]) -> None:
        """Populate the HID paths for each HIDInfo object in the list."""
        for hi in hid_infos:
            device_symlink = os.path.join(hi.event_path, "device")
            if not os.path.islink(device_symlink):
                print(f"No 'device' symlink found in {hi.event_path}")
                continue

            hid_device_path = os.path.realpath(device_symlink)
            match = re.search(r"\b\d+-[\d.]+:\d+\.\d+\b", hid_device_path)
            hi.hid_path = match.group(0) if match else None

    @staticmethod
    def _select_device_path(hid_infos: list[HIDInfo]) -> Optional[bytes]:
        """Select the appropriate device path based on interface preference."""
        device_name_filter = "Wireless" if USE_WIRELESS else "Wired"
        filtered_devices = [h for h in hid_infos if device_name_filter in h.device_name]

        if not filtered_devices:
            print(f"Could not find {device_name_filter} interface")
            return None

        selected_device = filtered_devices[0]
        return (
            selected_device.hid_path.encode("utf-8")
            if selected_device.hid_path
            else None
        )

    def _send_command(
        self, command: EpomakerCommand.EpomakerCommand, sleep_time: float = 0.1
    ) -> None:
        """Sends a command to the HID device.

        Args:
            command (EpomakerCommand): The command to send.
            sleep_time (float): The time to sleep between sending packets
                (default: 0.1).
        """
        assert command.report_data_prepared, "Report data not prepared"
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
            r = range(0, 100)  # 0 to 99
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

    def send_temperature(self, temperature: int | None, delay_seconds: int = 1) -> None:
        """Sends the temperature to the HID device.

        Args:
            temperature (int): The temperature value in C (0-99).
            delay_seconds (int): Time waited after command is sent.

        Raises:
            ValueError: If the temperature is not in the range 0-99.
        """
        if not temperature:
            # Don't do anything if temperature is None
            return
        if not self._assert_range(temperature):
            raise ValueError("Temperature must be in range 0-99: ", temperature)
        temperature_command = EpomakerTempCommand.EpomakerTempCommand(temperature)
        print(f"Sending temperature {temperature}C")
        self._send_command(temperature_command)
        time.sleep(delay_seconds)

    def send_cpu(self, cpu: int, delay_seconds: int = 1) -> None:
        """Sends the CPU percentage to the HID device.

        Args:
            cpu (int): The CPU percentage to send.
            delay_seconds (int): Time waited after command is sent.

        Raises:
            ValueError: If the CPU percentage is not in the range 0-100 and
                from_daemon is False.
        """
        if not self._assert_range(cpu):
            raise ValueError("CPU percentage must be in range 0-100")
        cpu_command = EpomakerCpuCommand.EpomakerCpuCommand(cpu)
        print(f"Sending CPU {cpu}%")
        self._send_command(cpu_command)
        time.sleep(delay_seconds)

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
