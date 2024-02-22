from enum import Enum
from dataclasses import dataclass
from typing import Iterator


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

class KeyMap:
    """Map a KeyboardKey index to an RGB value."""
    def __init__(self) -> None:
        self.key_map: dict[int, tuple[int, int, int]] = {}

    def __getitem__(self, key: KeyboardKey) -> tuple[int, int, int]:
        return self.key_map[key.value]

    def __setitem__(self, key: KeyboardKey, value: tuple[int, int, int]) -> None:
        self.key_map[key.value] = value

    def __iter__(self) -> Iterator[tuple[int, tuple[int, int, int]]]:
        return iter(self.key_map.items())

@dataclass(frozen=True)
class KeyboardRGBFrame:
    """A keyboard frame consists of a map of keys to RGB values as well as a time in milliseconds
    to display the frame."""
    key_map: KeyMap
    time_ms: int
    length: int = 7
    index: int = 0
