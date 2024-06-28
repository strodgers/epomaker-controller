# src/epomakercontroller/cli.py

import time
import click
from epomakercontroller.commands import (
    EpomakerKeyRGBCommand,
    EpomakerProfileCommand,
)
from epomakercontroller.commands.data.constants import ALL_KEYBOARD_KEYS, Profile
from epomakercontroller import EpomakerController
from datetime import datetime

@click.group()
def cli() -> None:
    """EpomakerController CLI."""
    pass

@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
def upload_image(image_path: str) -> None:
    """Upload an image to the Epomaker device."""
    try:
        controller = EpomakerController(dry_run=False)
        if controller.open_device():
            print("Uploading, you should see the status on the keyboard screen")
            controller.send_image(image_path)
            click.echo("Image uploaded successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to upload image: {e}")

@cli.command()
@click.argument('r', type=int)
@click.argument('g', type=int)
@click.argument('b', type=int)
def set_rgb_all_keys(r: int, g: int, b: int)  -> None:
    """Set RGB colour for all keys."""
    try:
        mapping = EpomakerKeyRGBCommand.KeyMap()
        for key in ALL_KEYBOARD_KEYS:
            mapping[key] = (r, g, b)
        frames = [EpomakerKeyRGBCommand.KeyboardRGBFrame(mapping, 50)]
        controller = EpomakerController(dry_run=False)
        if controller.open_device():
            controller.send_keys(frames)
            click.echo(f"All keys set to RGB({r}, {g}, {b}) successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to set RGB for all keys: {e}")

@cli.command()
def cycle_light_modes() -> None:
    """Cycle through the light modes."""
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
            click.echo(f"[{counter}/{len(Profile.Mode)}] Cycled to light mode: {mode.name}")
            time.sleep(5)
            counter += 1

        controller.close_device()
        click.echo("Cycled through all light modes successfully.")
    except Exception as e:
        click.echo(f"Failed to cycle light modes: {e}")

@cli.command()
@click.option('--datetime', 'dt', default=datetime.now(), help='Date and time to send to the device.')
def send_time(dt: datetime) -> None:
    """Send the current time to the Epomaker device."""
    try:
        controller = EpomakerController(dry_run=False)
        if controller.open_device():
            controller.send_time(dt)
            click.echo("Time sent successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to send time: {e}")

@cli.command()
@click.argument('temperature', type=int)
def send_temperature(temperature: int) -> None:
    """Send the temperature to the Epomaker device."""
    try:
        controller = EpomakerController(dry_run=False)
        if controller.open_device():
            controller.send_temperature(temperature)
            click.echo("Temperature sent successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to send temperature: {e}")

@cli.command()
@click.argument('cpu', type=int)
def send_cpu(cpu: int) -> None:
    """Send the CPU usage percentage to the Epomaker device."""
    try:
        controller = EpomakerController(dry_run=False)
        if controller.open_device():
            controller.send_cpu(cpu)
            click.echo("CPU usage sent successfully.")
        controller.close_device()
    except Exception as e:
        click.echo(f"Failed to send CPU usage: {e}")

if __name__ == "__main__":
    cli()
