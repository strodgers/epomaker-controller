# src/epomakercontroller/cli.py
"""Simple CLI for the EpomakerController package."""

import time
import click
from .commands import (
    EpomakerKeyRGBCommand,
    EpomakerProfileCommand,
)
from .commands.data.constants import ALL_KEYBOARD_KEYS, Profile
from .epomakercontroller import EpomakerController
from .keyboard_gui import RGBKeyboardGUI
from .epomaker_utils import get_cpu_usage, get_device_temp, print_temp_devices

import tkinter as tk
import importlib.resources as pkg_resources
import epomakercontroller.configs.layouts

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
        controller = EpomakerController(dry_run=False)
        if controller.open_device():
            print("Uploading, you should see the status on the keyboard screen.\n"
                  "The keyboard will be unresponsive during this process.")
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
        mapping = EpomakerKeyRGBCommand.KeyMap()
        for key in ALL_KEYBOARD_KEYS:
            mapping[key] = (r, g, b)
        frames = [EpomakerKeyRGBCommand.KeyboardRGBFrame(key_map=mapping)]
        controller = EpomakerController(dry_run=False)
        if controller.open_device():
            controller.send_keys(frames)
            click.echo(f"All keys set to RGB({r}, {g}, {b}) successfully.")
    except Exception as e:
        click.echo(f"Failed to set RGB for all keys: {e}")
    controller.close_device()


@cli.command()
def cycle_light_modes() -> None:
    """Cycle through the light modes.

    """
    try:
        controller = EpomakerController(dry_run=False)
        if not controller.open_device():
            click.echo("Failed to open device.")
            return

        print(f"Cycling through {len(Profile.Mode)} modes, waiting 5 seconds on each")
        counter = 1
        for mode in Profile.Mode:
            profile = Profile(
                mode=mode,
                speed=Profile.Speed.DEFAULT,
                brightness=Profile.Brightness.DEFAULT,
                dazzle=Profile.Dazzle.OFF,
                option=Profile.Option.OFF,
                rgb=(180, 180, 180),
            )
            command = EpomakerProfileCommand.EpomakerProfileCommand(profile)
            controller._send_command(command)
            click.echo(
                f"[{counter}/{len(Profile.Mode)}] Cycled to light mode: {mode.name}"
            )
            time.sleep(5)
            counter += 1

        click.echo("Cycled through all light modes successfully.")
    except Exception as e:
        click.echo(f"Failed to cycle light modes: {e}")
    controller.close_device()


@cli.command()
def send_time() -> None:
    """Send the current time to the Epomaker device.

    """
    try:
        controller = EpomakerController(dry_run=False)
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
        controller = EpomakerController(dry_run=False)
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
        controller = EpomakerController(dry_run=False)
        if controller.open_device():
            controller.send_cpu(cpu)
            click.echo("CPU usage sent successfully.")
    except Exception as e:
        click.echo(f"Failed to send CPU usage: {e}")
    controller.close_device()


@cli.command()
@click.option("--test", "test_mode", is_flag=True, help="Start daemon in test mode, sending random data.")
@click.argument("temp_key", type=str, required=False)
def start_daemon(temp_key: str | None, test_mode: bool) -> None:
    """Start a daemon to update the CPU usage and optionally a temperature.

    Args:
        temp_key (str): A label corresponding to the device to monitor.
    """
    try:
        controller = EpomakerController(dry_run=False)
        if not controller.open_device():
            click.echo("Failed to open device.")
            return

        first = True
        while True:

            if first:
                # Set current time and date
                controller.send_time()
                first = False

            # Send CPU usage
            controller.send_cpu(get_cpu_usage(test_mode), from_daemon=True)
            time.sleep(1)

            # Get device temperature using the provided key
            controller.send_temperature(get_device_temp(temp_key, test_mode))
            time.sleep(1)

    except KeyboardInterrupt:
        click.echo("Daemon interrupted by user.")
    except Exception as e:
        click.echo(f"Failed to start daemon: {e}")
    controller.close_device()


@cli.command()
def list_temp_devices() -> None:
    """List available temperature devices."""
    print_temp_devices()


@cli.command()
@click.option("--print", "print_info", is_flag=True, help="Print all available information about the connected keyboard.")
@click.option("--udev", "generate_udev", is_flag=True, help="Generate a udev rule for the connected keyboard.")
def dev(print_info: bool, generate_udev: bool) -> None:
    """Various dev tools.

    Args:
        print_info (bool): Print information about the connected keyboard.
        generate_udev (bool): Generate a udev rule for the connected keyboard.
    """
    if print_info:
        click.echo("Printing all available information about the connected keyboard.")
        controller = EpomakerController(dry_run=False)
        if not controller.open_device(only_info=True):
            click.echo("Failed to open device.")
            return
    elif generate_udev:
        click.echo("Generating udev rule for the connected keyboard.")
        # Init controller to get the PID
        controller = EpomakerController(dry_run=False)
        if not controller.open_device(only_info=True):
            click.echo("Failed to open device.")
            return
        controller.generate_udev_rule()
    else:
        click.echo("No dev tool specified.")


@cli.command()
@click.argument("config_file", type=str, required=False)
def set_keys(config_file: str | None) -> None:
    """Open a simple GUI to set individual key colours.

    Args:
        config_file: A custom layout as generated by keyboard-layout-editor.com
    """
    controller = EpomakerController(dry_run=False)
    if not controller.open_device():
        click.echo("Failed to open device.")
        return

    if not config_file:
        # Default to UK ISO
        with pkg_resources.path(epomakercontroller.configs.layouts, "EpomakerRT100-UK-ISO.json") as config_path:
            config_file = str(config_path)

    root = tk.Tk()
    RGBKeyboardGUI(root, controller.send_keys, config_file)

    def on_close() -> None:
        controller.close_device()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    cli()
