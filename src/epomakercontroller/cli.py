# src/epomakercontroller/cli.py
"""Simple CLI for the EpomakerController package."""

import click
import tkinter as tk

from .commands.data.constants import Profile
from .configs.configs import load_main_config
from .epomakercontroller import EpomakerController
from .utils.sensors import print_temp_devices
from .utils.keyboard_gui import RGBKeyboardGUI

CONFIG_MAIN = load_main_config()


@click.group()
def cli() -> None:
    """A simple CLI for the EpomakerController."""
    pass


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
def upload_image(image_path: str) -> None:
    """Upload an image to the Epomaker device.

    Args:
        image_path (str): The path to the image file to upload.
    """
    try:
        controller = EpomakerController(CONFIG_MAIN)
        if controller.open_device():
            print(
                "Uploading, you should see the status on the keyboard screen.\n"
                "The keyboard will be unresponsive during this process."
            )
            controller.send_image(image_path)
            click.echo("Image uploaded successfully.")
    except Exception as e:
        click.echo(f"Failed to upload image: {e}")
    controller.close_device()


@cli.command()
@click.argument("r", type=int)
@click.argument("g", type=int)
@click.argument("b", type=int)
def set_rgb_all_keys(r: int, g: int, b: int) -> None:
    """Set RGB colour for all keys.

    Args:
        r (int): The red value (0-255).
        g (int): The green value (0-255).
        b (int): The blue value (0-255).
    """
    try:
        controller = EpomakerController(CONFIG_MAIN)
        if controller.open_device():
            controller.set_rgb_all_keys(r, g, b)
            click.echo(f"All keys set to RGB({r}, {g}, {b}) successfully.")
    except Exception as e:
        click.echo(f"Failed to set RGB for all keys: {e}")
    controller.close_device()


@cli.command()
def cycle_light_modes() -> None:
    """Cycle through the light modes."""
    try:
        controller = EpomakerController(CONFIG_MAIN)
        if not controller.open_device():
            click.echo("Failed to open device.")
            return

        print(f"Cycling through {len(Profile.Mode)} modes, waiting 5 seconds on each")
        controller.cycle_light_modes()

        click.echo("Cycled through all light modes successfully.")
    except Exception as e:
        click.echo(f"Failed to cycle light modes: {e}")
    controller.close_device()


@cli.command()
def send_time() -> None:
    """Send the current time to the Epomaker device."""
    try:
        controller = EpomakerController(CONFIG_MAIN)
        if controller.open_device():
            controller.send_time()
            click.echo("Time sent successfully.")
    except Exception as e:
        click.echo(f"Failed to send time: {e}")
    controller.close_device()


@cli.command()
@click.argument("temperature", type=int)
def send_temperature(temperature: int) -> None:
    """Send temperature to the Epomaker screen.

    Args:
        temperature (int): The temperature value in C (0-100).
    """
    try:
        controller = EpomakerController(CONFIG_MAIN)
        if controller.open_device():
            controller.send_temperature(temperature)
            click.echo("Temperature sent successfully.")
    except Exception as e:
        click.echo(f"Failed to send temperature: {e}")
    controller.close_device()


@cli.command()
@click.argument("cpu", type=int)
def send_cpu(cpu: int) -> None:
    """Send CPU usage percentage to the Epomaker screen.

    Args:
        cpu (int): The CPU usage percentage (0-100).
    """
    try:
        controller = EpomakerController(CONFIG_MAIN)
        if controller.open_device():
            controller.send_cpu(cpu)
            click.echo("CPU usage sent successfully.")
    except Exception as e:
        click.echo(f"Failed to send CPU usage: {e}")
    controller.close_device()


@cli.command()
@click.option(
    "--test",
    "test_mode",
    is_flag=True,
    help="Start daemon in test mode, sending random data.",
)
@click.argument("temp_key", type=str, required=False)
def start_daemon(temp_key: str | None, test_mode: bool) -> None:
    """Start a daemon to update the CPU usage and optionally a temperature.

    Args:
        temp_key (str): A label corresponding to the device to monitor.
        test_mode (bool): Send random ints instead of real values.
    """
    try:
        controller = EpomakerController(CONFIG_MAIN)
        if not controller.open_device():
            click.echo("Failed to open device.")
            return
        controller.start_daemon(temp_key, test_mode)

    except KeyboardInterrupt:
        click.echo("Daemon interrupted by user.")
    except Exception as e:
        click.echo(f"Error in start-daemon: {e}")
    controller.close_device()


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
    if print_info:
        click.echo("Printing all available information about the connected keyboard.")
        controller = EpomakerController(CONFIG_MAIN)
        if not controller.open_device(only_info=True):
            click.echo("Failed to open device.")
            return
    elif generate_udev:
        click.echo("Generating udev rule for the connected keyboard.")
        # Init controller to get the PID
        controller = EpomakerController(CONFIG_MAIN)
        if not controller.open_device(only_info=True):
            click.echo("Failed to open device.")
            return
        controller.generate_udev_rule()
    else:
        click.echo("No dev tool specified.")


@cli.command()
def set_keys() -> None:
    """Open a simple GUI to set individual key colours."""
    controller = EpomakerController(CONFIG_MAIN)
    if not controller.open_device():
        click.echo("Failed to open device.")
        return

    root = tk.Tk()
    RGBKeyboardGUI(
        root, controller.send_keys, controller.config_layout, controller.config_keymap
    )

    def on_close() -> None:
        controller.close_device()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


@cli.command()
@click.argument("key_index", type=int)
@click.argument("key_combo", type=int)
def remap_keys(key_index: int, key_combo: int) -> None:
    """Remap key functionality using a KeyboardKey index (from) and a USB HID index (to)"""
    controller = EpomakerController(CONFIG_MAIN)
    if controller.open_device():
        controller.remap_keys(key_index, key_combo)
    controller.close_device()


@cli.command()
@click.option("--filter", default=None, help="Filter the keymap by key name")
def show_keymap(filter: str | None) -> None:
    controller = EpomakerController(CONFIG_MAIN, dry_run=True)
    data = controller.config_keymap.data
    assert data is not None, "ERROR: Config has no data"

    to_show = list(data)
    if filter:
        to_show = [item for item in data if filter.lower() in item["name"].lower()]

    for item in to_show:
        print(f"{item['name']}: {item['value']}")


if __name__ == "__main__":
    cli()
