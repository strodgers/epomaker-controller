import tkinter as tk
from tkinter.colorchooser import askcolor as askcolour   # thats right

from .keyboard_keys import KeyboardKey, KeyboardKeys
from .commands.EpomakerKeyRGBCommand import KeyMap, KeyboardRGBFrame
from typing import Callable
from .configs.configs import Config

DEFAULT_KEY_WIDTH = 8
DFAULT_KEY_HEIGHT = 4


class RGBKeyboardGUI:
    def __init__(self, root: tk.Tk, callback: Callable[[list[KeyboardRGBFrame]], None], config: Config):
        self.config_data = config.data
        keyboard_keys = KeyboardKeys(config)
        self.frame = KeyboardRGBFrame(KeyMap(keyboard_keys))

        self.root = root
        self.root.title("RGB Keyboard (UK ISO Layout)")
        self.key_btn_dict: dict[KeyboardKey, tk.Button] = {}
        self.selected_key: set[KeyboardKey] = set()
        self.key_colours: dict[KeyboardKey, str | None] = {}

        self.col_offset = 0
        self.row_offset = 0
        self.key_width = DEFAULT_KEY_WIDTH
        self.key_height = DFAULT_KEY_HEIGHT

        self.layout_data = config.data

        self.setup_ui()
        self.root.bind("<Return>", self.apply_colour_to_selected_keys)

        self.callback = callback

    def _strip_keyname(self, key: str) -> str:
        dont_need_in_name = ["NR", "NP", "LEFT_", "RIGHT_"]
        for dont_need in dont_need_in_name:
            key = key.replace(dont_need, "")
        return key.strip("_")

    def _handle_customization(self, item: tuple[str, int]) -> bool:
        identifier, value = item
        if identifier == "w":
            self.key_width = int(DEFAULT_KEY_WIDTH * value)
            return True
        elif identifier == "h":
            self.key_height = int(DFAULT_KEY_HEIGHT * value)
            return True
        elif identifier == "x":
            self.col_offset += int(DEFAULT_KEY_WIDTH * value)
        elif identifier == "y":
            self.row_offset += int(DFAULT_KEY_HEIGHT * value)
        else:
            print(f"Warning: Unknown customization identifier: {identifier}")

        return False

    def _create_key_callback(self, key: KeyboardKey) -> Callable[[], None]:
        def on_key_selected() -> None:
            self.select_key(key)
        return on_key_selected

    def setup_ui(self) -> None:
        customized = False
        for row in self.config_data:
            keyboardkeys_row: list[KeyboardKey] = []
            for col in row:
                if isinstance(col, dict):
                    # A dictionary entry means set some customizations for the proceeding key
                    for item in col.items():
                        customized = customized or self._handle_customization(item)
                else:
                    display_str = col
                    state: Literal['normal', 'active', 'disabled'] = "disabled"

                    # Dummy method to do nothing
                    def noop() -> None:
                        pass
                    command = noop

                    # Get the corresponding key if it exists
                    key = KEYBOARD_KEYS_NAME_DICT.get(col, None)
                    if key:
                        display_str = key.display_str
                        state = "normal"
                        command = self._create_key_callback(key)
                        keyboardkeys_row.append(key)
                    else:
                        print(
                            f"Warning: key from config json with name {col} does not match any KeyboardKey"
                        )

                    # Create the button
                    btn = tk.Button(
                        self.root,
                        text=display_str,
                        width=self.key_width,
                        height=self.key_height,
                        command=command,
                        state=state,
                    )
                    # Add to grid
                    btn.grid(
                        row=self.row_offset,
                        column=self.col_offset,
                        columnspan=self.key_width,
                        rowspan=self.key_height,
                    )

                    if key:
                        self.key_btn_dict[key] = btn
                        self.key_colours[key] = None

                    self.col_offset += self.key_width

                    # Reset customizations
                    if customized:
                        customized = False
                        self.key_width = DEFAULT_KEY_WIDTH
                        self.key_height = DFAULT_KEY_HEIGHT

            self.row_offset += DFAULT_KEY_HEIGHT
            self.col_offset = 0

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
                self.frame.overlay(self.selected_key, (r, g, b))
                self.callback([self.frame])

                print(f"Set {','.join([k.name for k in self.selected_key])} keys to {colour}")
        self.selected_key.clear()
