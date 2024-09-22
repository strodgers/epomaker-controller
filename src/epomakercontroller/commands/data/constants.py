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
    display_str: str


@dataclass(frozen=True)
class KK:
    ESC = KeyboardKey("ESC", 0, "Esc")
    BACKQUOTE = KeyboardKey("BACKQUOTE", 1, "`")
    TAB = KeyboardKey("TAB", 2, "Tab")
    CAPS = KeyboardKey("CAPS", 3, "Caps")
    LEFT_SHIFT = KeyboardKey("LEFT_SHIFT", 4, "Shift")
    LEFT_CTRL = KeyboardKey("LEFT_CTRL", 5, "Ctrl")
    F1 = KeyboardKey("F1", 6, "F1")
    NUMROW_1 = KeyboardKey("NUMROW_1", 7, "1")
    Q = KeyboardKey("Q", 8, "Q")
    A = KeyboardKey("A", 9, "A")
    BACKSLASH = KeyboardKey("BACKSLASH", 10, "\\")
    DIAL = KeyboardKey("DIAL", 11, "Dial")
    F2 = KeyboardKey("F2", 12, "F2")
    NUMROW_2 = KeyboardKey("NUMROW_2", 13, "2")
    W = KeyboardKey("W", 14, "W")
    S = KeyboardKey("S", 15, "S")
    Z = KeyboardKey("Z", 16, "Z")
    LEFT_WIN = KeyboardKey("LEFT_WIN", 17, "Win")
    F3 = KeyboardKey("F3", 18, "F3")
    NUMROW_3 = KeyboardKey("NUMROW_3", 19, "3")
    E = KeyboardKey("E", 20, "E")
    D = KeyboardKey("D", 21, "D")
    X = KeyboardKey("X", 22, "X")
    LEFT_ALT = KeyboardKey("LEFT_ALT", 23, "Alt")
    F4 = KeyboardKey("F4", 24, "F4")
    NUMROW_4 = KeyboardKey("NUMROW_4", 25, "4")
    R = KeyboardKey("R", 26, "R")
    F = KeyboardKey("F", 27, "F")
    C = KeyboardKey("C", 28, "C")
    F5 = KeyboardKey("F5", 30, "F5")
    NUMROW_5 = KeyboardKey("NUMROW_5", 31, "5")
    T = KeyboardKey("T", 32, "T")
    G = KeyboardKey("G", 33, "G")
    V = KeyboardKey("V", 34, "V")
    F6 = KeyboardKey("F6", 36, "F6")
    NUMROW_6 = KeyboardKey("NUMROW_6", 37, "6")
    Y = KeyboardKey("Y", 38, "Y")
    H = KeyboardKey("H", 39, "H")
    B = KeyboardKey("B", 40, "B")
    SPACE = KeyboardKey("SPACE", 41, " ")
    F7 = KeyboardKey("F7", 42, "F7")
    NUMROW_7 = KeyboardKey("NUMROW_7", 43, "7")
    U = KeyboardKey("U", 44, "U")
    J = KeyboardKey("J", 45, "J")
    N = KeyboardKey("N", 46, "N")
    F8 = KeyboardKey("F8", 48, "F8")
    NUMROW_8 = KeyboardKey("NUMROW_8", 49, "8")
    I = KeyboardKey("I", 50, "I")
    K = KeyboardKey("K", 51, "K")
    M = KeyboardKey("M", 52, "M")
    RIGHT_ALT = KeyboardKey("RIGHT_ALT", 53, "AltGr")
    F9 = KeyboardKey("F9", 54, "F9")
    NUMROW_9 = KeyboardKey("NUMROW_9", 55, "9")
    O = KeyboardKey("O", 56, "O")
    L = KeyboardKey("L", 57, "L")
    COMMA = KeyboardKey("COMMA", 58, ",")
    FN = KeyboardKey("FN", 59, "Fn")
    F10 = KeyboardKey("F10", 60, "F10")
    NUMROW_0 = KeyboardKey("NUMROW_0", 61, "0")
    P = KeyboardKey("P", 62, "P")
    SEMICOLON = KeyboardKey("SEMICOLON", 63, ";")
    DOT = KeyboardKey("DOT", 64, ".")
    RIGHT_CTRL = KeyboardKey("RIGHT_CTRL", 65, "Ctrl")
    F11 = KeyboardKey("F11", 66, "F11")
    NUMROW_MINUS = KeyboardKey("NUMROW_MINUS", 67, "-")
    OPEN_SQBR = KeyboardKey("OPEN_SQBR", 68, "[")
    QUOTE = KeyboardKey("QUOTE", 69, "'")
    SLASH = KeyboardKey("SLASH", 70, "/")
    LEFT = KeyboardKey("LEFT", 71, "←")
    F12 = KeyboardKey("F12", 72, "F12")
    NUMROW_EQUAL = KeyboardKey("NUMROW_EQUAL", 73, "=")
    CLOSE_SQBR = KeyboardKey("CLOSE_SQBR", 74, "]")
    HASH = KeyboardKey("HASH", 75, "#")
    RIGHT_SHIFT = KeyboardKey("RIGHT_SHIFT", 76, "Shift")
    DOWN = KeyboardKey("DOWN", 77, "↓")
    DEL = KeyboardKey("DEL", 78, "Del")
    BACKSPACE = KeyboardKey("BACKSPACE", 79, "Backspace")
    ENTER = KeyboardKey("ENTER", 80, "Enter")
    NUMPAD_4 = KeyboardKey("NUMPAD_4", 81, "4")
    UP = KeyboardKey("UP", 82, "↑")
    RIGHT = KeyboardKey("RIGHT", 83, "→")
    PGUP = KeyboardKey("PGUP", 84, "PgUp")
    NUMLOCK = KeyboardKey("NUMLOCK", 85, "Num")
    NUMPAD_7 = KeyboardKey("NUMPAD_7", 86, "7")
    NUMPAD_5 = KeyboardKey("NUMPAD_5", 87, "5")
    NUMPAD_1 = KeyboardKey("NUMPAD_1", 88, "1")
    NUMPAD_0 = KeyboardKey("NUMPAD_0", 89, "0")
    PGDOWN = KeyboardKey("PGDOWN", 90, "PgDn")
    NUMPAD_SLASH = KeyboardKey("NUMPAD_SLASH", 91, "/")
    NUMPAD_8 = KeyboardKey("NUMPAD_8", 92, "8")
    NUMPAD_6 = KeyboardKey("NUMPAD_6", 93, "6")
    NUMPAD_2 = KeyboardKey("NUMPAD_2", 94, "2")
    NUMPAD_DOT = KeyboardKey("NUMPAD_DOT", 95, ".")
    NUMPAD_MINUS = KeyboardKey("NUMPAD_MINUS", 96, "-")
    NUMPAD_ASTERISK = KeyboardKey("NUMPAD_ASTERISK", 97, "*")
    NUMPAD_9 = KeyboardKey("NUMPAD_9", 98, "9")
    NUMPAD_PLUS = KeyboardKey("NUMPAD_PLUS", 99, "+")
    NUMPAD_3 = KeyboardKey("NUMPAD_3", 100, "3")
    NUMPAD_ENTER = KeyboardKey("NUMPAD_ENTER", 101, "Enter")


ALL_KEYBOARD_KEYS = [value for name, value in vars(KK).items() if not name.startswith('__')]
KEYBOARD_KEYS_NAME_DICT = {
    name: value for name, value in vars(KK).items() if isinstance(value, KeyboardKey)
}
