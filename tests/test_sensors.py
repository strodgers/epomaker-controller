from epomakercontroller.utils.sensors import select_temp_device


def test_select_temp_device_prefers_cpu_sensor() -> None:
    temps = {
        "NVIDIA-GPU-0": 70.0,
        "coretemp-0": 52.0,
        "coretemp-1": 55.0,
    }

    assert select_temp_device(temps) == "coretemp-1"


def test_select_temp_device_uses_generic_sensor_before_gpu() -> None:
    temps = {
        "NVIDIA-GPU-0": 70.0,
        "nvme-0": 44.0,
    }

    assert select_temp_device(temps) == "nvme-0"


def test_select_temp_device_falls_back_to_gpu() -> None:
    temps = {
        "NVIDIA-GPU-0": 70.0,
        "NVIDIA-GPU-1": 72.0,
    }

    assert select_temp_device(temps) == "NVIDIA-GPU-1"


def test_select_temp_device_returns_none_without_sensors() -> None:
    assert select_temp_device({}) is None
