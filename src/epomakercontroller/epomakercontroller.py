"""EpomakerController module.

This module contains the EpomakerController class, which represents a controller
for an Epomaker USB HID device.
"""
from __future__ import annotations
import typing

import dataclasses
import os
import time
import hid  # type: ignore[import-not-found]
import subprocess
import re
from typing import override
from datetime import datetime
from json import dumps

from .configs.constants import TMP_FILE_PATH, RULE_FILE_PATH
from .logger.logger import Logger
from .utils.sensors import get_cpu_usage, get_device_temp
from .utils.time_helper import TimeHelper
from .utils.keyboard_keys import KeyboardKeys

from .commands import (
    EpomakerCommand,
    EpomakerImageCommand,
    EpomakerRemapKeysCommand,
    EpomakerTimeCommand,
    EpomakerTempCommand,
    EpomakerCpuCommand,
    EpomakerKeyRGBCommand,
    EpomakerProfileCommand,
)

from .commands.data.constants import BUFF_LENGTH, Profile
from .configs.configs import Config, ConfigType, get_all_configs
from .controllers.controller import ControllerBase
from .configs.constants import DAEMON_TIME_DELAY

if typing.TYPE_CHECKING:
    from typing import Any, Optional


class EpomakerConfig:
    def __init__(self, config_main: Config) -> None:
        all_configs = get_all_configs()
        self.config_layout = all_configs.get(ConfigType.CONF_LAYOUT)
        self.config_keymap = all_configs.get(ConfigType.CONF_KEYMAP)

        self.vendor_id = config_main["VENDOR_ID"]
        self.use_wireless = config_main["USE_WIRELESS"]

        self.product_ids: list[int] = (
            config_main["PRODUCT_IDS_WIRED"]
            if not self.use_wireless
            else config_main["PRODUCT_IDS_24G"]
        )
        self.device_description = config_main["DEVICE_DESCRIPTION_REGEX"]


@dataclasses.dataclass
class HIDInfo:
    device_name: str
    event_path: str
    hid_path: Optional[str] = None


class EpomakerController(ControllerBase):
    """EpomakerController class represents a controller for an Epomaker USB HID device.

    Attributes:
        config (EpomakerConfig): The configuration of the controller.
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
        config_main: Config,
        dry_run: bool = False,
    ) -> None:
        """Initializes the EpomakerController object.

        Args:
            config_main (Config): The CONF_MAIN type configuration.
            dry_run (bool): Whether to run in dry run mode (default: False).
        """
        super().__init__()

        self.config = EpomakerConfig(config_main)

        self.device = hid.device()
        self.dry_run = dry_run
        self.device_list: list[dict[str, Any]] = []
        Logger.log_warning(
            "If this program errors out or you cancel early, the keyboard may become unresponsive. "
            "It should work fine again if you unplug and plug it back in!"
        )

        self._setup_signal_handling()

    @override
    def open_device(self, only_info: bool = False) -> bool:
        """Opens the USB HID device and prints device information.

        Args:
            only_info (bool): Print device information and exit (default: False).

        Returns:
            bool: True if the device is opened successfully, False otherwise.
        """
        if self.dry_run:
            Logger.log_info("Dry run: skipping device open")
            return True

        product_id = self._find_product_id()
        if not product_id:
            return False

        if only_info:
            return True

        # Find the device with the specified interface number so we can open by path
        # This way we don't block usage of the keyboard whilst the device is open
        device_path = self._find_device_path()
        if device_path is None:
            return False

        self._open_device(device_path)
        return self.device is not None

    @override
    def close_device(self) -> None:
        """Closes the USB HID device."""
        if not self.device:
            return

        self.device.close()
        self.device = None

    def _find_product_id(self) -> Optional[int]:
        """Finds the product ID of the device using a list of possible product IDs.

        Returns:
            int | None: The product ID if found, None otherwise.
        """

        # Todo: optimization
        for pid in self.config.product_ids:
            self.device_list = hid.enumerate(self.config.vendor_id, pid)
            if self.device_list:
                return pid

        return None

    def _open_device(self, device_path: bytes) -> None:
        """Opens the USB HID device.

        Args:
            device_path (bytes): The path to the device.
        """
        try:
            self.device.open_path(device_path)
        except IOError as e:
            Logger.log_error(
                f"Failed to open device: {e}\n"
                "Please make sure the device is connected\n"
                "and you have the necessary permissions.\n\n"
                "You may need to run this program as root or with sudo, or\n"
                "set up a udev rule to allow access to the device.\n\n"
            )
            self.device = None

    def generate_udev_rule(self) -> None:
        """Generates udev rule for the connected keyboard."""
        rule_content = (
            f"# Epomaker RT100 keyboard\n"
            f'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{self.config.vendor_id:04x}", '
            f'ATTRS{{idProduct}}=="{self._find_product_id():04x}", MODE="0666", '
            'GROUP="plugdev"\n\n'
        )

        Logger.log_info("Generating udev rule for Epomaker RT100 keyboard")
        Logger.log_info(f"Rule content:\n{rule_content}")
        Logger.log_info(f"Rule file path: {RULE_FILE_PATH}")
        Logger.log_info("Please enter your password if prompted")

        # Write the rule to a temporary file
        temp_file_path = TMP_FILE_PATH

        with open(temp_file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(rule_content)

        # Move the file to the correct location, reload rules

        move_command = ["mv", temp_file_path, RULE_FILE_PATH]
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

        Logger.log_info("Rule generated successfully")

    def print_device_info(self) -> None:
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

    def _find_device_path(self) -> Optional[bytes]:
        """Finds the device path with the specified interface number.

        Returns:
            Optional[bytes]: The device path if found, None otherwise.
        """
        input_dir = "/sys/class/input"
        hid_infos = EpomakerController._get_hid_infos(
            input_dir, self.config.device_description
        )

        if not hid_infos:
            print(f"No events found with description: '{self.config.device_description}'")
            return None

        EpomakerController._populate_hid_paths(hid_infos)

        return self._select_device_path(hid_infos)

    @staticmethod
    def _get_hid_infos(input_dir: str, description: str) -> list[HIDInfo]:
        """Retrieve HID information based on the given description."""
        hid_infos = []
        for event in os.listdir(input_dir):
            if event.startswith("event"):
                device_name_path = os.path.join(input_dir, event, "device", "name")
                try:
                    with open(device_name_path, "r", encoding="utf-8") as f:
                        device_name = f.read().strip()
                        if re.search(description, device_name):
                            event_path = os.path.join(input_dir, event)
                            hid_infos.append(
                                HIDInfo(device_name, event_path)
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

    def _select_device_path(self, hid_infos: list[HIDInfo]) -> Optional[bytes]:
        """Select the appropriate device path based on interface preference."""
        device_name_filter = "Wireless" if self.config.use_wireless else "Wired"
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

    def _send_command(self, command: EpomakerCommand.EpomakerCommand) -> None:
        """Sends a command to the HID device.

        Args:
            command (EpomakerCommand): The command to send.
        """
        # Make sure device is opened and connected
        if not self.device:
            Logger.log_error("No device connected")
            return

        try:
            self.device.get_product_string()
        except:  # noqa: E722
            raise IOError("Could not communicate with device")

        if not command.report_data_prepared:
            return

        for packet in command:
            assert len(packet) == BUFF_LENGTH
            if self.dry_run:
                print(f"Dry run: skipping command send: {packet!r}")
            else:
                self.device.send_feature_report(packet.get_all_bytes())

    @staticmethod
    def _check_range(value: int, r: range | None = None) -> bool:
        """Checks that a value is within a specified range.

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
        if not os.path.isfile(image_path):
            Logger.log_error(f"Could not find image: {image_path}")
            return

        image_command = EpomakerImageCommand.EpomakerImageCommand()
        image_command.encode_image(image_path)
        self._send_command(image_command)

    def send_time(self, time_to_send: datetime | None = None) -> None:
        """Sends `time` to the HID device.

        Args:
            time_to_send (datetime): The time to send (default: None).
        """
        if not time_to_send:
            time_to_send = datetime.now()
        time_command = EpomakerTimeCommand.EpomakerTimeCommand(time_to_send)
        self._send_command(time_command)

    def send_temperature(self, temperature: int | None) -> None:
        """Sends the temperature to the HID device.

        Args:
            temperature (int): The temperature value in C (0-99).

        Raises:
            ValueError: If the temperature is not in the range 0-99.
        """
        if not temperature:
            # Don't do anything if temperature is None
            return
        if not self._check_range(temperature):
            Logger.log_error(f"Temperature must be in range 0-99: {temperature}")
            return

        temperature_command = EpomakerTempCommand.EpomakerTempCommand(temperature)
        Logger.log_info(f"Sending temperature {temperature}C")
        self._send_command(temperature_command)

    def send_cpu(self, cpu: int) -> None:
        """Sends the CPU percentage to the HID device.

        Args:
            cpu (int): The CPU percentage to send.

        Raises:
            ValueError: If the CPU percentage is not in the range 0-100 and
                from_daemon is False.
        """
        if not self._check_range(cpu):
            Logger.log_error(f"CPU percentage must be in range 0-100, got {cpu} instead")
            return

        cpu_command = EpomakerCpuCommand.EpomakerCpuCommand(cpu)
        print(f"Sending CPU {cpu}%")
        self._send_command(cpu_command)

    def set_rgb_all_keys(self, r: int, g: int, b: int) -> None:
        # Make sure values are within range
        for value in [r, g, b]:
            self._check_range(value, range(0, 256))

        # Get all the keyboard keys
        keyboard_keys = KeyboardKeys(self.config.config_keymap)

        # Construct a KeyMap object
        mapping = EpomakerKeyRGBCommand.KeyMap(keyboard_keys)

        # Set all keys to r, g, b
        for key in keyboard_keys:
            mapping[key] = (r, g, b)

        frames = [EpomakerKeyRGBCommand.KeyboardRGBFrame(key_map=mapping)]
        self.send_keys(frames)

    def send_keys(self, frames: list[EpomakerKeyRGBCommand.KeyboardRGBFrame]) -> None:
        """Sends key RGB frames to the HID device.

        Args:
            frames (list): The list of KeyboardRGBFrame to send.
        """
        rgb_command = EpomakerKeyRGBCommand.EpomakerKeyRGBCommand(frames)
        self._send_command(rgb_command)

    def remap_keys(self, key_index: int, key_combo: int) -> None:
        key_map_command = EpomakerRemapKeysCommand.EpomakerRemapKeysCommand(
            key_index, key_combo
        )
        self._send_command(key_map_command)

    def cycle_light_modes(self, sleep_seconds: int = 5) -> None:
        for counter, mode in enumerate(Profile.Mode):
            profile = Profile(
                mode=mode,
                speed=Profile.Speed.DEFAULT,
                brightness=Profile.Brightness.DEFAULT,
                dazzle=Profile.Dazzle.OFF,
                option=Profile.Option.OFF,
                rgb=(180, 180, 180),
            )
            self.set_profile(profile)
            Logger.log_info(
                f"[{counter + 1}/{len(Profile.Mode)}] Cycled to light mode: {mode.name}"
            )
            time.sleep(sleep_seconds)
            counter += 1

    def set_profile(self, profile: Profile) -> None:
        """Set the keyboard profile."""
        profile_command = EpomakerProfileCommand.EpomakerProfileCommand(profile)
        self._send_command(profile_command)

    def start_daemon(self, temp_key: str | None, test_mode: bool) -> None:
        """Start a daemon to update the CPU usage and optionally a temperature.

        Args:
            temp_key (str): A label corresponding to the device to monitor.
            test_mode (bool): Send random ints instead of real values.
        """
        # Set current time and date
        self.send_time()

        while True:
            # Send CPU usage
            with TimeHelper(min_duration=DAEMON_TIME_DELAY):
                # self.send_cpu(get_cpu_usage(test_mode))
                # Get device temperature using the provided key
                if temp_key:
                    self.send_temperature(get_device_temp(temp_key, test_mode))
                elif test_mode:
                    self.send_temperature(get_device_temp("dummy_device", test_mode))
