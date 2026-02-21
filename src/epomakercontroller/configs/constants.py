"""
The main goal of this file is to prevent appearance of "magic" symbols in code,
and provide a single point of project configuration
"""
import os


CONFIG_DIRECTORY = ".epomaker-controller"
CONFIG_NAME = "config.json"

# OS dependent path
ROOT_FOLDER = "/"
if os.name == "nt":
    # Windows root
    ROOT_FOLDER = os.path.abspath(os.getenv("APPDATA") + "/epomaker_controller/") + "/"
    if not os.path.exists(ROOT_FOLDER):
        os.mkdir(ROOT_FOLDER)

TMP_FOLDER = os.path.abspath("./.epomaker_controller")
ETC_FOLDER = os.path.abspath(ROOT_FOLDER + "etc/")

# Create folder on Windows
if os.name == "nt":
    if not os.path.exists(ETC_FOLDER):
        os.mkdir(ETC_FOLDER)

# Create temp folder in project path on Linux as well
if not os.path.exists(TMP_FOLDER):
    os.mkdir(TMP_FOLDER)

RULE_FILE_PATH = ETC_FOLDER + "/udev/rules.d/99-epomaker-rt100.rules"
TMP_FILE_PATH = TMP_FOLDER + "/99-epomaker-rt100.rules"
PATH_TO_DEFAULT_CONFIG = "src/epomakercontroller/configs/default.json"

DAEMON_TIME_DELAY = 1.6
