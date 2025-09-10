# src/epomakercontroller/cli.py
"""Simple CLI for the EpomakerController package."""

import click
import tkinter as tk
from functools import wraps

from .commands.data.constants import Profile
from .configs.configs import load_main_config
from .epomakercontroller import EpomakerController
from .utils.sensors import print_temp_devices
from .utils.keyboard_gui import RGBKeyboardGUI
from .utils.app_version import retrieve_app_version
from .logger.logger import Logger

CONFIG_MAIN = load_main_config()


def wrapped_command(func):
    """
    Simple wrapper around command call. Propagates function name and docstring to click
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with EpomakerController(CONFIG_MAIN) as controller:
            if not controller.ready():
                Logger.log_error("Failed to open device")
                return None

            result = func(controller, *args, **kwargs)
            return result
    return wrapper


@click.group()
@click.version_option(retrieve_app_version(), prog_name="EpomakerController")
def cli() -> None:
    """A simple CLI for the EpomakerController."""
    pass


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@wrapped_command
def upload_image(controller: EpomakerController, image_path: str) -> None:
    """Upload an image to the Epomaker device.

    Args:
        controller (EpomakerController): Passed from wrapped_command() decorator
        image_path (str): The path to the image file to upload.
    """
    controller.send_image(image_path)
    Logger.log_info("Image uploaded successfully.")


@cli.command()
@click.argument("r", type=int)
@click.argument("g", type=int)
@click.argument("b", type=int)
@wrapped_command
def set_rgb_all_keys(controller: EpomakerController, r: int, g: int, b: int) -> None:
    """Set RGB colour for all keys.

    Args:
        controller: Passed from wrapped_command() decorator
        r (int): The red value (0-255).
        g (int): The green value (0-255).
        b (int): The blue value (0-255).
    """
    controller.set_rgb_all_keys(r, g, b)
    Logger.log_info(f"All keys set to RGB({r}, {g}, {b}) successfully.")

@cli.command()
@wrapped_command
def cycle_light_modes(controller: EpomakerController) -> None:
    """Cycle through the light modes."""
    Logger.log_info(f"Cycling through {len(Profile.Mode)} modes, waiting 5 seconds on each")
    controller.cycle_light_modes()
    Logger.log_info("Cycled through all light modes successfully.")


@cli.command()
@wrapped_command
def send_time(controller: EpomakerController) -> None:
    """Send the current time to the Epomaker device."""
    controller.send_time()
    Logger.log_info("Time sent successfully.")


@cli.command()
@click.argument("temperature", type=int)
@wrapped_command
def send_temperature(controller: EpomakerController, temperature: int) -> None:
    """Send temperature to the Epomaker screen.

    Args:
        controller (EpomakerController): Passed from wrapped_command() decorator
        temperature (int): The temperature value in C (0-100).
    """
    controller.send_temperature(temperature)
    Logger.log_info("Temperature sent successfully.")


@cli.command()
@click.argument("cpu", type=int)
@wrapped_command
def send_cpu(controller: EpomakerController, cpu: int) -> None:
    """Send CPU usage percentage to the Epomaker screen.

    Args:
        controller (EpomakerController): Passed from wrapped_command() decorator
        cpu (int): The CPU usage percentage (0-100).
    """
    controller.send_cpu(cpu)
    Logger.log_info("CPU usage sent successfully.")


@cli.command()
@click.option(
    "--test",
    "test_mode",
    is_flag=True,
    help="Start daemon in test mode, sending random data.",
)
@click.argument("temp_key", type=str, required=False)
@wrapped_command
def start_daemon(controller: EpomakerController, temp_key: str | None, test_mode: bool) -> None:
    """Start a daemon to update the CPU usage and optionally a temperature.

    Args:
        controller (EpomakerController): Passed from wrapped_command() decorator
        temp_key (str): A label corresponding to the device to monitor.
        test_mode (bool): Send random ints instead of real values.
    """
    controller.start_daemon(temp_key, test_mode)


@cli.command()
def list_temp_devices() -> None:
    """List available temperature devices."""
    print_temp_devices()


@cli.command()
@click.option(
    "--print",
    "print_info",
    is_flag=True,
    help="Print all available information about the connected keyboard.",
)
@click.option(
    "--udev",
    "generate_udev",
    is_flag=True,
    help="Generate a udev rule for the connected keyboard.",
)
def dev(print_info: bool, generate_udev: bool) -> None:
    """Various dev tools.

    Args:
        print_info (bool): Print information about the connected keyboard.
        generate_udev (bool): Generate a udev rule for the connected keyboard.
    """

    # We're doing pretty much the same we were doing in if-elif-else chain,
    # but now we're doing it once

    controller = EpomakerController(CONFIG_MAIN)

    if not controller.open_device(only_info=True):
        Logger.log_error("Could not find device")
        return

    if print_info:
        # I didn't find anything that was called after the controller initialization, is SOLID rule being violated?
        pass
    elif generate_udev:
        controller.generate_udev_rule()
    else:
        # It would be better to print help string or something like that
        Logger.log_error("No dev tool specified.")
        click.echo(dev.__doc__)


@cli.command()
@wrapped_command
def set_keys(controller: EpomakerController) -> None:
    """Open a simple GUI to set individual key colours."""
    root = tk.Tk()
    RGBKeyboardGUI(
        root, controller.send_keys, controller.config_layout, controller.config_keymap
    )

    def on_close() -> None:
        # The device will be closed with context manager
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


@cli.command()
@click.argument("key_index", type=int)
@click.argument("key_combo", type=int)
@wrapped_command
def remap_keys(controller: EpomakerController, key_index: int, key_combo: int) -> None:
    """Remap key functionality using a KeyboardKey index (from) and a USB HID index (to)"""
    controller.remap_keys(key_index, key_combo)


@cli.command()
@click.option("--filter", default=None, help="Filter the keymap by key name")
def show_keymap(keymap_filter: str | None) -> None:
    controller = EpomakerController(CONFIG_MAIN, dry_run=True)
    data = controller.config_keymap.data

    # It's better not to use assert in production
    # asserts could be disabled, which will break this code segment
    if not data:
        Logger.log_error("No keymap data")
        return

    to_show = list(data)
    if keymap_filter:
        to_show = [item for item in data if keymap_filter.lower() in item["name"].lower()]

    for item in to_show:
        print(f"{item['name']}: {item['value']}")


if __name__ == "__main__":
    cli()
