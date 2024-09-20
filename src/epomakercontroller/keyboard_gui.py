import tkinter as tk
from tkinter.colorchooser import askcolor as askcolour  # thats right
from .commands.data.constants import KK, KeyboardKey
from .commands.EpomakerKeyRGBCommand import KeyMap, KeyboardRGBFrame
from typing import Callable


class RGBKeyboardGUI:
    def __init__(self, root: tk.Tk, callback: Callable[[list[KeyboardRGBFrame]], None]):
        self.root = root
        self.root.title("RGB Keyboard (UK ISO Layout)")
        self.key_btn_dict: dict[KeyboardKey, tk.Button] = {}
        self.selected_key: set[KeyboardKey] = set()
        self.key_colours: dict[KeyboardKey, str | None] = {}
        self.setup_ui()
        self.root.bind("<Return>", self.apply_colour_to_selected_keys)

        self.frame = KeyboardRGBFrame(key_map=KeyMap())
        self.callback = callback

    def _strip_keyname(self, key: str) -> str:
        dont_need_in_name = ["NUMROW", "NUMPAD", "LEFT_", "RIGHT_"]
        for dont_need in dont_need_in_name:
            key = key.replace(dont_need, "")
        return key.strip("_")

    def setup_ui(self) -> None:
        layout = [
            [
                KK.ESC,
                KK.F1,
                KK.F2,
                KK.F3,
                KK.F4,
                KK.F5,
                KK.F6,
                KK.F7,
                KK.F8,
                KK.F9,
                KK.F10,
                KK.F11,
                KK.F12,
                None,
                KK.DEL,
                KK.PGUP,
                KK.PGDOWN,
                KK.DIAL,
            ],
            [
                KK.BACKQUOTE,
                KK.NUMROW_1,
                KK.NUMROW_2,
                KK.NUMROW_3,
                KK.NUMROW_4,
                KK.NUMROW_5,
                KK.NUMROW_6,
                KK.NUMROW_7,
                KK.NUMROW_8,
                KK.NUMROW_9,
                KK.NUMROW_0,
                KK.NUMROW_MINUS,
                KK.NUMROW_EQUAL,
                KK.BACKSPACE,
                None,
                KK.NUMLOCK,
                KK.NUMPAD_SLASH,
                KK.NUMPAD_ASTERISK,
                KK.NUMPAD_MINUS,
            ],
            [
                KK.TAB,
                KK.Q,
                KK.W,
                KK.E,
                KK.R,
                KK.T,
                KK.Y,
                KK.U,
                KK.I,
                KK.O,
                KK.P,
                KK.LEFT_BRACKET,
                KK.RIGHT_BRACKET,
                KK.ENTER,
                None,
                KK.NUMPAD_7,
                KK.NUMPAD_8,
                KK.NUMPAD_9,
                KK.NUMPAD_PLUS,
            ],
            [
                KK.CAPS,
                KK.A,
                KK.S,
                KK.D,
                KK.F,
                KK.G,
                KK.H,
                KK.J,
                KK.K,
                KK.L,
                KK.SEMICOLON,
                KK.QUOTE,
                KK.HASH,
                None,
                None,
                KK.NUMPAD_4,
                KK.NUMPAD_5,
                KK.NUMPAD_6,
            ],
            [
                KK.LEFT_SHIFT,
                KK.BACKSLASH,
                KK.Z,
                KK.X,
                KK.C,
                KK.V,
                KK.B,
                KK.N,
                KK.M,
                KK.COMMA,
                KK.DOT,
                KK.SLASH,
                KK.RIGHT_SHIFT,
                KK.UP,
                None,
                KK.NUMPAD_1,
                KK.NUMPAD_2,
                KK.NUMPAD_3,
                KK.NUMPAD_ENTER,
            ],
            [
                KK.LEFT_CTRL,
                KK.LEFT_WIN,
                KK.LEFT_ALT,
                KK.SPACE,
                KK.RIGHT_ALT,
                KK.FN,
                KK.RIGHT_CTRL,
                None,
                KK.LEFT,
                KK.DOWN,
                KK.RIGHT,
                KK.NUMPAD_0,
                KK.NUMPAD_DOT,
            ],
        ]

        special_keys = {
            KK.BACKSPACE: {"width": 8},
            KK.TAB: {"width": 7},
            KK.CAPS: {"width": 7},
            KK.ENTER: {"width": 6, "height": 4, "rowspan": 2},
            KK.LEFT_SHIFT: {"width": 7},
            KK.RIGHT_SHIFT: {"width": 9},
            KK.LEFT_CTRL: {"width": 5},
            KK.RIGHT_CTRL: {"width": 5},
            KK.SPACE: {"width": 20, "columnspan": 5},
            KK.LEFT_ALT: {"width": 5},
            KK.RIGHT_ALT: {"width": 5},
            KK.FN: {"width": 5},
            KK.ESC: {"padx": (2, 10)},
            KK.DEL: {"padx": (10, 2)},
            KK.NUMPAD_ENTER: {"height": 6, "rowspan": 2},
            KK.NUMPAD_PLUS: {"height": 6, "rowspan": 2},
        }

        for row, keys in enumerate(layout):
            col_offset = 0
            for col, key in enumerate(keys):
                if key is None:
                    col_offset += 1
                    continue

                special_key = special_keys.get(key, {})

                width = special_key.get("width", 4)
                height = special_key.get("height", 2)
                columnspan = special_key.get("columnspan", 1)
                rowspan = special_key.get("rowspan", 1)
                padx = special_key.get("padx", 2)
                pady = special_key.get("pady", 2)

                btn = tk.Button(
                    self.root,
                    text=self._strip_keyname(key.name),
                    width=width,
                    height=height,
                    command=lambda k=key: self.select_key(k),
                )

                btn.grid(
                    row=row,
                    column=col_offset,
                    columnspan=columnspan,
                    rowspan=rowspan,
                    padx=padx,
                    pady=pady,
                )
                self.key_btn_dict[key] = btn
                self.key_colours[key] = None
                col_offset += columnspan

    def select_key(self, key: KeyboardKey) -> None:
        if key in self.selected_key:
            self.selected_key.remove(key)
            self.key_btn_dict[key].config(relief=tk.RAISED)
        else:
            self.selected_key.add(key)
            self.key_btn_dict[key].config(relief=tk.SUNKEN)

    def apply_colour_to_selected_keys(self, _: object) -> None:
        if self.selected_key:
            first_key = next(iter(self.selected_key))
            initial_colour = self.key_colours.get(first_key, None)
            colour = askcolour(initial_colour)[1]
            if colour:
                for key in self.selected_key:
                    self.key_btn_dict[key].config(bg=colour, relief=tk.RAISED)
                    self.key_colours[key] = colour

                r, g, b = (
                    int(colour[1:3], 16),
                    int(colour[3:5], 16),
                    int(colour[5:7], 16),
                )
                to_add_frame = KeyboardRGBFrame.from_keys(self.selected_key, (r, g, b))
                self.frame.overlay(to_add_frame)
                self.callback([self.frame])

                print(f"Set {self.selected_key} keys to {colour}")
        self.selected_key.clear()
