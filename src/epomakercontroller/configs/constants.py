"""
The main goal of this file is to prevent appearance of "magic" symbols in code,
and provide a single point of project configuration
"""


CONFIG_DIRECTORY = ".epomaker-controller"
CONFIG_NAME = "config.json"

# Todo: Create default.json here and paste the contents of this dict there
DEFAULT_MAIN_CONFIG = {
    "VENDOR_ID": 0x3151,
    "PRODUCT_IDS_WIRED": [0x4010, 0x4015],
    "PRODUCT_IDS_24G": [0x4011, 0x4016],
    "USE_WIRELESS": False,
    "DEVICE_DESCRIPTION_REGEX": "ROYUAN .* System Control",
    # The file will be looked for in the install location first, otherwise use a full filepath
    "CONF_LAYOUT_PATH": "EpomakerRT100-UK-ISO.json",
    "CONF_KEYMAP_PATH": "EpomakerRT100.json",
}
