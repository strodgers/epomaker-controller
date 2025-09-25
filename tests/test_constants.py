import os
from epomakercontroller.configs import constants


def test_validate_path():
    """
    Add other validation here if path should exist on controller startup
    """

    assert os.path.exists(constants.TMP_FOLDER), "Temp folder does not exist"
    assert os.path.exists(constants.PATH_TO_DEFAULT_CONFIG), "Default config path does not exist"
