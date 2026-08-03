import os

from epomakercontroller.configs import constants


def test_default_config_is_bundled():
    """The default config ships with the package, so it must always be readable.

    Resolved against constants.py rather than the working directory: the old
    relative path only existed inside a source checkout, so an installed copy
    raised FileNotFoundError anywhere else.
    """
    assert os.path.isabs(constants.PATH_TO_DEFAULT_CONFIG)
    assert os.path.exists(
        constants.PATH_TO_DEFAULT_CONFIG
    ), "Default config path does not exist"


def test_writable_paths_are_absolute():
    """Paths written to must not depend on the working directory.

    These are deliberately NOT asserted to exist: importing a module should not
    create directories. They are created by the code that writes to them.
    """
    for path in (constants.CONFIG_DIRECTORY, constants.TMP_FOLDER):
        assert os.path.isabs(path), f"{path} is not absolute"

    if constants.USE_XDG_CONFIG_DIR:
        assert not constants.CONFIG_DIRECTORY.startswith(
            os.path.dirname(os.path.abspath(constants.__file__))
        ), "With USE_XDG_CONFIG_DIR, config must live outside the package"
