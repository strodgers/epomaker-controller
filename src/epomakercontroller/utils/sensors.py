import random
import psutil
import gpustat
from pynvml import NVMLError

from epomakercontroller.logger.logger import Logger

CPU_SENSOR_PREFIXES = (
    "coretemp",
    "k10temp",
    "zenpower",
    "cpu_thermal",
    "soc_thermal",
    "acpitz",
)
GPU_SENSOR_MARKERS = (
    "nvidia",
    "geforce",
    "radeon",
    "amdgpu",
)


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

    available_keys = list(temps.keys())
    # pylint: disable=bad-builtin
    print(
        (
            f"Temperature key {temp_key!r} not found."
            f"Available keys: {available_keys}"
        )
    )
    return 0


def select_temp_device(temps: dict[str, float] | None = None) -> str | None:
    """Select a sensible default temperature sensor from available devices.

    Prefer CPU/SoC sensors and avoid GPU sensors by default. GPU queries can be
    comparatively expensive or disruptive on some systems, so automatic daemon
    mode should choose them only when no better sensor is available.
    """
    if temps is None:
        temps = _get_temp_devices()

    if not temps:
        return None

    def sensor_rank(item: tuple[str, float]) -> tuple[int, float, str]:
        key, temp = item
        key_lower = key.lower()

        if any(key_lower.startswith(prefix) for prefix in CPU_SENSOR_PREFIXES):
            priority = 0
        elif any(marker in key_lower for marker in GPU_SENSOR_MARKERS):
            priority = 2
        else:
            priority = 1

        return priority, -float(temp), key

    return min(temps.items(), key=sensor_rank)[0]


def _get_temp_devices() -> dict[str, float] | None:
    try:
        hw_temperatures = psutil.sensors_temperatures()
    except AttributeError:
        Logger.log_error("Temperature monitoring not supported on this system.")
        return None
    try:
        gpu_stats = gpustat.new_query()
    except OSError as e:
        Logger.log_error(f"No NVIDIA sensors available: {e.strerror}")
        gpu_stats = None
    except NVMLError as e:
        Logger.log_error(f"No NVIDIA driver available: {e}")
        gpu_stats = None

    temperature_sensors: dict[str, float] = {}
    for device_name, entries in hw_temperatures.items():
        for index, entry in enumerate(entries):
            # A single device may have multiple sensors, need to be able
            # to access each one
            device_key = f"{device_name}-{index}"
            temperature_sensors[device_key] = entry.current

    # Append any NVIDIA sensors
    if gpu_stats:
        for index, gpu_stat in enumerate(gpu_stats):
            if "name" in gpu_stat.keys() and "temperature.gpu" in gpu_stat.keys():
                device_name = gpu_stat["name"].replace(" ", "-")
                device_key = f"{device_name}-{index}"
                temperature_sensors[device_key] = gpu_stat["temperature.gpu"]

    return temperature_sensors


def print_temp_devices() -> None:
    """Print available temperature sensors by key and current temperature."""
    temps = _get_temp_devices()
    if not temps:
        Logger.log_error("No temperature sensors found.")
        return

    selected_key = select_temp_device(temps)
    key_width = len(max(temps.keys(), key=len))
    # pylint: disable=bad-builtin
    print(f"{'DEVICE KEY':<{key_width}}  CURRENT TEMPERATURE  AUTO")

    for device_key, temp in temps.items():
        auto_marker = "*" if device_key == selected_key else ""
        # pylint: disable=bad-builtin
        print(f"{device_key:<{key_width}}  {temp}°C  {auto_marker}")
