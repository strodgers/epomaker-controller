import os

import epomakercontroller.cli as cli
from fake.fake_controller import FakeEpomakerController
from epomakercontroller.commands.EpomakerImageCommand import EpomakerImageCommand


def test_send_image():
    controller = FakeEpomakerController(cli.CONFIG_MAIN)
    controller.send_image(os.path.abspath("tests/data/calibration.png"))

    assert controller.commands
    assert isinstance(controller.commands[-1], EpomakerImageCommand)


def test_send_image_wrong_path():
    """
    No fail, but no command being executed
    """

    controller = FakeEpomakerController(cli.CONFIG_MAIN)
    controller.send_image(os.path.abspath("tests/data/calibration_nonexistent.png"))

    assert not controller.commands


def test_wrong_format():
    controller = FakeEpomakerController(cli.CONFIG_MAIN)

    controller.send_temperature(-100)
    assert not controller.commands

    controller.send_cpu(101)
    assert not controller.commands

    controller.send_cpu(99)
    assert controller.commands

    controller.commands.clear()

    controller.send_temperature(90)
    assert controller.commands
