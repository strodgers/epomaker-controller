from enum import Enum
from dataclasses import dataclass
from typing import Iterator

BUFF_LENGTH = 128 // 2  # 128 bytes / 2 bytes per int
IMAGE_DIMENSIONS = (162, 173)


@dataclass(frozen=True)
class Profile:
    """Thanks to https://gitlab.com/CalcProgrammer1/OpenRGB/-/blob/master/Controllers/EpomakerController/EpomakerController.h"""

    class Mode(Enum):
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
        MIN = 0x00
        MAX = 0x05
        MAX_SPECIAL = 0x04
        DEFAULT = 0x04

    class Brightness(Enum):
        MIN = 0x00
        MAX = 0x04
        DEFAULT = 0x04

    class Dazzle(Enum):
        OFF = 0x07
        ON = 0x08

    class Option(Enum):
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
class KeyboardKey(Enum):
    ESC = 0
    BACKQUOTE = 1
    TAB = 2
    CAPS = 3
    LEFT_SHIFT = 4
    LEFT_CTRL = 5
    F1 = 6
    NUMROW_1 = 7
    Q = 8
    A = 9
    BACKSLASH = 10
    DIAL = 11
    F2 = 12
    NUMROW_2 = 13
    W = 14
    S = 15
    Z = 16
    LEFT_WIN = 17
    F3 = 18
    NUMROW_3 = 19
    E = 20
    D = 21
    X = 22
    LEFT_ALT = 23
    F4 = 24
    NUMROW_4 = 25
    R = 26
    F = 27
    C = 28
    F5 = 30
    NUMROW_5 = 31
    T = 32
    G = 33
    V = 34
    F6 = 36
    NUMROW_6 = 37
    Y = 38
    H = 39
    B = 40
    SPACE = 41
    F7 = 42
    NUMROW_7 = 43
    U = 44
    J = 45
    N = 46
    F8 = 48
    NUMROW_8 = 49
    I = 50
    K = 51
    M = 52
    RIGHT_ALT = 53
    F9 = 54
    NUMROW_9 = 55
    O = 56
    L = 57
    COMMA = 58
    FN = 59
    F10 = 60
    NUMROW_0 = 61
    P = 62
    SEMICOLON = 63
    DOT = 64
    RIGHT_CTRL = 65
    F11 = 66
    NUMROW_MINUS = 67
    LEFT_BRACKET = 68
    QUOTE = 69
    SLASH = 70
    LEFT = 71
    F12 = 72
    NUMROW_EQUAL = 73
    RIGHT_BRACKET = 74
    HASH = 75
    RIGHT_SHIFT = 76
    DOWN = 77
    DEL = 78
    BACKSPACE = 79
    ENTER = 80
    NUMPAD_4 = 81
    UP = 82
    RIGHT = 83
    PGUP = 84
    NUMLOCK = 85
    NUMPAD_7 = 86
    NUMPAD_5 = 87
    NUMPAD_1 = 88
    NUMPAD_0 = 89
    PGDOWN = 90
    NUMPAD_SLASH = 91
    NUMPAD_8 = 92
    NUMPAD_6 = 93
    NUMPAD_2 = 94
    NUMPAD_DOT = 95
    NUMPAD_MINUS = 96
    NUMPAD_ASTERISK = 97
    NUMPAD_9 = 98
    NUMPAD_PLUS = 99
    NUMPAD_3 = 100
    NUMPAD_ENTER = 101


ALL_KEYBOARD_KEYS = [KeyboardKey[e.name] for e in KeyboardKey]
