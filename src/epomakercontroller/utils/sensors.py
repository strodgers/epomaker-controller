from dataclasses import dataclass
from typing import Any
import psutil
import random


def get_cpu_usage(test_mode: bool = False) -> int:
    """Get the current CPU usage.

    Args:
        test_mode (bool): If true, return a random int between 0 and 99.

    Returns:
        int: CPU usage, or a random number if `test_mode`.
    """
    if test_mode:
        return random.randint(0, 99)
    return int(round(psutil.cpu_percent(interval=1)))


def get_device_temp(temp_key: str, test_mode: bool = False) -> int:
    """Get the temperature of a device specified by `temp_key`, or 0 if the key cannot be found.

    Args:
        temp_key (str): Key corresponding to a device.
        test_mode (bool): If true, return a random int between 0 and 99.

    Returns:
        int: The temperature of the device, 0 if not found, or a random number if `test_mode`.
    """
    if test_mode:
        return random.randint(0, 99)

    temps = _get_temp_devices()
    if not temps:
        return 0

    if temp_key in temps:
        device_temp = temps[temp_key]
        return int(round(device_temp))

    else:
        available_keys = list(temps.keys())
        print(
            (
                f"Temperature key {temp_key!r} not found."
                f"Available keys: {available_keys}"
            )
        )

    return 0


def _get_temp_devices() -> dict[str, float] | None:
    try:
        hw_temperatures = psutil.sensors_temperatures()
    except AttributeError:
        print("Temperature monitoring not supported on this system.")
        return None

    temperature_sensors: dict[str, float] = {}
    for device_name, entries in hw_temperatures.items():
        for index, entry in enumerate(entries):
            # A single device may have multiple sensors, need to be able
            # to access each one
            device_key = f"{device_name}-{index}"
            temperature_sensors[device_key] = entry.current

    return temperature_sensors


def print_temp_devices() -> None:
    temps = _get_temp_devices()
    if not temps:
        print("No temperature sensors found.")
        return

    print("{0:20} {1}".format("DEVICE KEY", "CURRENT TEMPERATURE"))
    for device_key, temp in temps.items():
        print("{0:20} {1}°C".format(device_key, temp))
