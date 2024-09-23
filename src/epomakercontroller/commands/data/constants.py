"""Constants for the EpomakerController commands module.

This module defines various constants used in the EpomakerController commands.
"""

from enum import Enum
from dataclasses import dataclass

BUFF_LENGTH = 128 // 2  # 128 bytes / 2 bytes per int
IMAGE_DIMENSIONS = (162, 173)


@dataclass(frozen=True)
class Profile:
    """Profile settings for the Epomaker keyboard.

    Thanks to https://gitlab.com/CalcProgrammer1/OpenRGB/-/blob/master/Controllers/
    EpomakerController/EpomakerController.h
    """

    class Mode(Enum):
        """Modes for the Epomaker keyboard."""

        ALWAYS_ON = 0x01
        DYNAMIC_BREATHING = 0x02
        SPECTRUM_CYCLE = 0x03
        DRIFT = 0x04
        WAVES_RIPPLE = 0x05
        STARS_TWINKLE = 0x06
        STEADY_STREAM = 0x07
        SHADOWING = 0x08
        PEAKS_RISING_ONE_AFTER_ANOTHER = 0x09
        SINE_WAVE = 0x0A
        CAISPRING_SURGING = 0x0B
        FLOWERS_BLOOMING = 0x0C
        LASER = 0x0E
        PEAK_TURN = 0x0F
        INCLINED_RAIN = 0x10
        SNOW = 0x11
        METEOR = 0x12
        THROUGH_THE_SNOW_NON_TRACE = 0x13
        LIGHT_SHADOW = 0x15

    class Speed(Enum):
        """Speed settings for the Epomaker keyboard."""

        MIN = 0x00
        MAX = 0x05
        MAX_SPECIAL = 0x04
        DEFAULT = 0x04

    class Brightness(Enum):
        """Brightness settings for the Epomaker keyboard."""

        MIN = 0x00
        MAX = 0x04
        DEFAULT = 0x04

    class Dazzle(Enum):
        """Dazzle settings for the Epomaker keyboard."""

        OFF = 0x07
        ON = 0x08

    class Option(Enum):
        """Option settings for the Epomaker keyboard."""

        OFF = 0x00
        ON = 0x01
        DEFAULT = 0x00
        DRIFT_RIGHT = 0x00
        DRIFT_LEFT = 0x10
        DRIFT_DOWN = 0x20
        DRIFT_UP = 0x30
        STEADY_STREAM_ZIG_ZAG = 0x00
        STEADY_STREAM_RETURN = 0x10
        CAISPRING_SURGING_OUT = 0x00
        CAISPRING_SURGING_IN = 0x10
        FLOWERS_BLOOMING_RIGHT = 0x00
        FLOWERS_BLOOMING_LEFT = 0x10
        PEAK_TURN_ANTI_CLOCKWISE = 0x00
        PEAK_TURN_CLOCKWISE = 0x10

    mode: Mode
    speed: Speed
    brightness: Brightness
    dazzle: Dazzle
    option: Option
    rgb: tuple[int, int, int]
