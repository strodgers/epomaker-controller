"""
The main goal of this file is to prevent appearance of "magic" symbols in code,
and provide a single point of project configuration
"""


CONFIG_DIRECTORY = ".epomaker-controller"
CONFIG_NAME = "config.json"

RULE_FILE_PATH = "/etc/udev/rules.d/99-epomaker-rt100.rules"

TMP_FOLDER = "/tmp/"
TMP_FILE_PATH = TMP_FOLDER + "99-epomaker-rt100.rules"

PATH_TO_DEFAULT_CONFIG = "src/epomakercontroller/configs/default.json"
