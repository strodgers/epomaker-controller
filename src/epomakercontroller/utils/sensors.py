from typing import Any
import psutil
import random


def get_cpu_usage(test_mode: bool = False) -> int:
    if test_mode:
        return random.randint(0, 99)
    return int(round(psutil.cpu_percent(interval=1)))


def get_device_temp(temp_key: str | None, test_mode: bool = False) -> int | None:
    if test_mode:
        return random.randint(0, 99)

    if not temp_key:
        return None

    temps = get_temp_devices()
    if not temps:
        return 0

    if temp_key in temps:
        cpu_temp = temps[temp_key][0].current
        return int(round(cpu_temp))

    else:
        available_keys = list(temps.keys())
        print(
            (
                f"Temperature key {temp_key!r} not found."
                f"Available keys: {available_keys}"
            )
        )

    return 0


def get_temp_devices() -> Any:
    try:
        return psutil.sensors_temperatures()
    except AttributeError:
        print("Temperature monitoring not supported on this system.")

    return None


def print_temp_devices() -> None:
    temps = get_temp_devices()
    if not temps:
        print("No temperature sensors found.")
        return

    for key, entries in temps.items():
        print(f"\nTemperature key: {key}")
        for entry in entries:
            print(f"  Label: {entry.label or 'N/A'}")
            print(f"  Current: {entry.current}°C")
            print(f"  High: {entry.high or 'N/A'}°C")
            print(f"  Critical: {entry.critical or 'N/A'}°C")
