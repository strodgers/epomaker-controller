"""The main goal of this file is to prevent appearance of "magic" symbols in code,
and provide a single point of project configuration
"""
import os
import tempfile


# Where user config is written.
#
# True  -- the user's config directory ($XDG_CONFIG_HOME, else ~/.config).
# False -- alongside the installed package.
#
# Note that on a pip or distro install the package directory is usually
# root-owned, is replaced on upgrade, and is shared between users, so False
# means config may fail to save, be lost on update, or collide.
USE_XDG_CONFIG_DIR = True

if USE_XDG_CONFIG_DIR:
    CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
        os.path.expanduser("~"), ".config"
    )
    CONFIG_DIRECTORY = os.path.join(CONFIG_HOME, "epomaker-controller")
else:
    CONFIG_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CONFIG_NAME = "config.json"

# OS dependent path
ROOT_FOLDER = "/"
if os.name == "nt":
    # Windows root
    ROOT_FOLDER = os.path.abspath(os.getenv("APPDATA") + "/epomaker_controller/") + "/"
    if not os.path.exists(ROOT_FOLDER):
        os.mkdir(ROOT_FOLDER)

TMP_FOLDER = os.path.join(tempfile.gettempdir(), "epomaker_controller")
ETC_FOLDER = os.path.abspath(ROOT_FOLDER + "etc/")

# Create folder on Windows
if os.name == "nt":
    if not os.path.exists(ETC_FOLDER):
        os.mkdir(ETC_FOLDER)

RULE_FILE_PATH = ETC_FOLDER + "/udev/rules.d/99-epomaker-rt100.rules"
TMP_FILE_PATH = TMP_FOLDER + "/99-epomaker-rt100.rules"
PATH_TO_DEFAULT_CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "default.json"
)

DAEMON_TIME_DELAY = 1.6
