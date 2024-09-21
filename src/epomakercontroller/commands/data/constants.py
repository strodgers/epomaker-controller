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


@dataclass(frozen=True)
class KeyboardKey:
    name: str
    value: int


@dataclass(frozen=True)
class KK:
    ESC = KeyboardKey("ESC", 0)
    BACKQUOTE = KeyboardKey("BACKQUOTE", 1)
    TAB = KeyboardKey("TAB", 2)
    CAPS = KeyboardKey("CAPS", 3)
    LEFT_SHIFT = KeyboardKey("LEFT_SHIFT", 4)
    LEFT_CTRL = KeyboardKey("LEFT_CTRL", 5)
    F1 = KeyboardKey("F1", 6)
    NUMROW_1 = KeyboardKey("NUMROW_1", 7)
    Q = KeyboardKey("Q", 8)
    A = KeyboardKey("A", 9)
    BACKSLASH = KeyboardKey("BACKSLASH", 10)
    DIAL = KeyboardKey("DIAL", 11)
    F2 = KeyboardKey("F2", 12)
    NUMROW_2 = KeyboardKey("NUMROW_2", 13)
    W = KeyboardKey("W", 14)
    S = KeyboardKey("S", 15)
    Z = KeyboardKey("Z", 16)
    LEFT_WIN = KeyboardKey("LEFT_WIN", 17)
    F3 = KeyboardKey("F3", 18)
    NUMROW_3 = KeyboardKey("NUMROW_3", 19)
    E = KeyboardKey("E", 20)
    D = KeyboardKey("D", 21)
    X = KeyboardKey("X", 22)
    LEFT_ALT = KeyboardKey("LEFT_ALT", 23)
    F4 = KeyboardKey("F4", 24)
    NUMROW_4 = KeyboardKey("NUMROW_4", 25)
    R = KeyboardKey("R", 26)
    F = KeyboardKey("F", 27)
    C = KeyboardKey("C", 28)
    F5 = KeyboardKey("F5", 30)
    NUMROW_5 = KeyboardKey("NUMROW_5", 31)
    T = KeyboardKey("T", 32)
    G = KeyboardKey("G", 33)
    V = KeyboardKey("V", 34)
    F6 = KeyboardKey("F6", 36)
    NUMROW_6 = KeyboardKey("NUMROW_6", 37)
    Y = KeyboardKey("Y", 38)
    H = KeyboardKey("H", 39)
    B = KeyboardKey("B", 40)
    SPACE = KeyboardKey("SPACE", 41)
    F7 = KeyboardKey("F7", 42)
    NUMROW_7 = KeyboardKey("NUMROW_7", 43)
    U = KeyboardKey("U", 44)
    J = KeyboardKey("J", 45)
    N = KeyboardKey("N", 46)
    F8 = KeyboardKey("F8", 48)
    NUMROW_8 = KeyboardKey("NUMROW_8", 49)
    I = KeyboardKey("I", 50)
    K = KeyboardKey("K", 51)
    M = KeyboardKey("M", 52)
    RIGHT_ALT = KeyboardKey("RIGHT_ALT", 53)
    F9 = KeyboardKey("F9", 54)
    NUMROW_9 = KeyboardKey("NUMROW_9", 55)
    O = KeyboardKey("O", 56)
    L = KeyboardKey("L", 57)
    COMMA = KeyboardKey("COMMA", 58)
    FN = KeyboardKey("FN", 59)
    F10 = KeyboardKey("F10", 60)
    NUMROW_0 = KeyboardKey("NUMROW_0", 61)
    P = KeyboardKey("P", 62)
    SEMICOLON = KeyboardKey("SEMICOLON", 63)
    DOT = KeyboardKey("DOT", 64)
    RIGHT_CTRL = KeyboardKey("RIGHT_CTRL", 65)
    F11 = KeyboardKey("F11", 66)
    NUMROW_MINUS = KeyboardKey("NUMROW_MINUS", 67)
    LEFT_BRACKET = KeyboardKey("LEFT_BRACKET", 68)
    QUOTE = KeyboardKey("QUOTE", 69)
    SLASH = KeyboardKey("SLASH", 70)
    LEFT = KeyboardKey("LEFT", 71)
    F12 = KeyboardKey("F12", 72)
    NUMROW_EQUAL = KeyboardKey("NUMROW_EQUAL", 73)
    RIGHT_BRACKET = KeyboardKey("RIGHT_BRACKET", 74)
    HASH = KeyboardKey("HASH", 75)
    RIGHT_SHIFT = KeyboardKey("RIGHT_SHIFT", 76)
    DOWN = KeyboardKey("DOWN", 77)
    DEL = KeyboardKey("DEL", 78)
    BACKSPACE = KeyboardKey("BACKSPACE", 79)
    ENTER = KeyboardKey("ENTER", 80)
    NUMPAD_4 = KeyboardKey("NUMPAD_4", 81)
    UP = KeyboardKey("UP", 82)
    RIGHT = KeyboardKey("RIGHT", 83)
    PGUP = KeyboardKey("PGUP", 84)
    NUMLOCK = KeyboardKey("NUMLOCK", 85)
    NUMPAD_7 = KeyboardKey("NUMPAD_7", 86)
    NUMPAD_5 = KeyboardKey("NUMPAD_5", 87)
    NUMPAD_1 = KeyboardKey("NUMPAD_1", 88)
    NUMPAD_0 = KeyboardKey("NUMPAD_0", 89)
    PGDOWN = KeyboardKey("PGDOWN", 90)
    NUMPAD_SLASH = KeyboardKey("NUMPAD_SLASH", 91)
    NUMPAD_8 = KeyboardKey("NUMPAD_8", 92)
    NUMPAD_6 = KeyboardKey("NUMPAD_6", 93)
    NUMPAD_2 = KeyboardKey("NUMPAD_2", 94)
    NUMPAD_DOT = KeyboardKey("NUMPAD_DOT", 95)
    NUMPAD_MINUS = KeyboardKey("NUMPAD_MINUS", 96)
    NUMPAD_ASTERISK = KeyboardKey("NUMPAD_ASTERISK", 97)
    NUMPAD_9 = KeyboardKey("NUMPAD_9", 98)
    NUMPAD_PLUS = KeyboardKey("NUMPAD_PLUS", 99)
    NUMPAD_3 = KeyboardKey("NUMPAD_3", 100)
    NUMPAD_ENTER = KeyboardKey("NUMPAD_ENTER", 101)


ALL_KEYBOARD_KEYS = [value for name, value in vars(KK).items() if not name.startswith('__')]
KEYBOARD_KEYS_NAME_DICT = {
    name: value for name, value in vars(KK).items() if isinstance(value, KeyboardKey)
}
