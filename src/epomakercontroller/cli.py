# src/epomakercontroller/cli.py
"""Simple CLI for the EpomakerController package."""

import time
import click
from epomakercontroller.commands import (
    EpomakerKeyRGBCommand,
    EpomakerProfileCommand,
)
from epomakercontroller.commands.data.constants import ALL_KEYBOARD_KEYS, Profile
from epomakercontroller import EpomakerController
import psutil

# From testing using my own keyboard, this interface works for the controller whilst
# not interfering with the keyboard's normal operation.
INTERFACE_NUMBER = 1

@click.group()
def cli() -> None:
    """A simple CLI for the EpomakerController."""
    pass


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("-i", "--interface", type=int, default=INTERFACE_NUMBER)
def upload_image(image_path: str, interface: int) -> None:
    """Upload an image to the Epomaker device.

    Args:
        image_path (str): The path to the image file to upload.
        interface (int): The HID interface number to use.
    """
    try:
        controller = EpomakerController(interface, dry_run=False)
        if controller.open_device():
            print("Uploading, you should see the status on the keyboard screen")
            controller.send_image(image_path)
            click.echo("Image uploaded successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to upload image: {e}")


@cli.command()
@click.argument("r", type=int)
@click.argument("g", type=int)
@click.argument("b", type=int)
@click.option("-i", "--interface", type=int, default=INTERFACE_NUMBER)
def set_rgb_all_keys(r: int, g: int, b: int, interface: int) -> None:
    """Set RGB colour for all keys.

    Args:
        r (int): The red value (0-255).
        g (int): The green value (0-255).
        b (int): The blue value (0-255).
        interface (int): The HID interface number to use.
    """
    try:
        mapping = EpomakerKeyRGBCommand.KeyMap()
        for key in ALL_KEYBOARD_KEYS:
            mapping[key] = (r, g, b)
        frames = [EpomakerKeyRGBCommand.KeyboardRGBFrame(mapping, 50)]
        controller = EpomakerController(interface, dry_run=False)
        if controller.open_device():
            controller.send_keys(frames)
            click.echo(f"All keys set to RGB({r}, {g}, {b}) successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to set RGB for all keys: {e}")


@cli.command()
@click.option("-i", "--interface", type=int, default=INTERFACE_NUMBER)
def cycle_light_modes(interface: int) -> None:
    """Cycle through the light modes.

    Args:
        interface (int): The HID interface number to use.
    """
    try:
        controller = EpomakerController(interface, dry_run=False)
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

        controller.close_device()
        click.echo("Cycled through all light modes successfully.")
    except Exception as e:
        click.echo(f"Failed to cycle light modes: {e}")


@cli.command()
@click.option("-i", "--interface", type=int, default=INTERFACE_NUMBER)
def send_time(interface: int) -> None:
    """Send the current time to the Epomaker device.

    Args:
        interface (int): The HID interface number to use.
    """
    try:
        controller = EpomakerController(interface, dry_run=False)
        if controller.open_device():
            controller.send_time()
            click.echo("Time sent successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to send time: {e}")


@cli.command()
@click.argument("temperature", type=int)
@click.option("-i", "--interface", type=int, default=INTERFACE_NUMBER)
def send_temperature(temperature: int, interface: int) -> None:
    """Send temperature to the Epomaker screen.

    Args:
        temperature (int): The temperature value in C (0-100).
        interface (int): The HID interface number to use.
    """
    try:
        controller = EpomakerController(interface, dry_run=False)
        if controller.open_device():
            controller.send_temperature(temperature)
            click.echo("Temperature sent successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to send temperature: {e}")


@cli.command()
@click.argument("cpu", type=int)
@click.option("-i", "--interface", type=int, default=INTERFACE_NUMBER)
def send_cpu(cpu: int, interface: int) -> None:
    """Send CPU usage percentage to the Epomaker screen.

    Args:
        cpu (int): The CPU usage percentage (0-100).
        interface (int): The HID interface number to use.
    """
    try:
        controller = EpomakerController(interface, dry_run=False)
        if controller.open_device():
            controller.send_cpu(cpu)
            click.echo("CPU usage sent successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to send CPU usage: {e}")


@cli.command()
@click.argument("temp_key", type=str, required=False)
@click.option("-i", "--interface", type=int, default=INTERFACE_NUMBER)
def start_daemon(temp_key: str | None, interface: int) -> None:
    """Start a daemon to update the CPU usage and optionally a temperature.

    Args:
        temp_key (str): A label corresponding to the device to monitor.
        interface (int): The HID interface number to use.
    """
    try:
        controller = EpomakerController(interface, dry_run=False)
        while True:
            if not controller.open_device():
                click.echo("Failed to open device.")
                return
            # Set current time and date
            controller.send_time()

            # Get CPU usage
            cpu_usage = round(psutil.cpu_percent(interval=1))
            click.echo(f"CPU Usage: {cpu_usage}%")
            controller.send_cpu(int(cpu_usage), from_daemon=True)

            # Get device temperature using the provided key
            if temp_key:
                try:
                    temps = psutil.sensors_temperatures()
                    if temp_key in temps:
                        cpu_temp = temps[temp_key][0].current
                        rounded_cpu_temp = round(cpu_temp)
                        click.echo(
                            f"CPU Temperature ({temp_key}): {rounded_cpu_temp}°C"
                        )
                        controller.send_temperature(rounded_cpu_temp)
                    else:
                        available_keys = list(temps.keys())
                        click.echo(
                            (f"Temperature key {temp_key!r} not found."
                             f"Available keys: {available_keys}")
                        )
                except AttributeError:
                    click.echo("Temperature monitoring not supported on this system.")

            controller.close_device()

            time.sleep(3)
    except KeyboardInterrupt:
        click.echo("Daemon interrupted by user.")
    except Exception as e:
        click.echo(f"Failed to start daemon: {e}")


@cli.command()
def list_temp_devices() -> None:
    """List available temperature devices."""
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            click.echo("No temperature sensors found.")
            return

        for key, entries in temps.items():
            click.echo(f"\nTemperature key: {key}")
            for entry in entries:
                click.echo(f"  Label: {entry.label or 'N/A'}")
                click.echo(f"  Current: {entry.current}°C")
                click.echo(f"  High: {entry.high or 'N/A'}°C")
                click.echo(f"  Critical: {entry.critical or 'N/A'}°C")
    except AttributeError:
        click.echo("Temperature monitoring not supported on this system.")


@cli.command()
@click.argument("print_all_info", type=str, required=False)
def dev(print_all_info: bool | None) -> None:
    """Various dev tools.

    Args:
        print_all_info (str): Print all available information about the connected keyboard.
    """

    if print_all_info:
        click.echo("Printing all available information about the connected keyboard.")
        controller = EpomakerController(INTERFACE_NUMBER, dry_run=False)
        if not controller.open_device(only_info=True):
            click.echo("Failed to open device.")
            return
    else:
        click.echo("No dev tool specified.")


if __name__ == "__main__":
    cli()
