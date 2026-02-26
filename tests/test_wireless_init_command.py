from epomakercontroller.commands.EpomakerPollCommand import EpomakerPollCommand
from epomakercontroller.commands.EpomakerWirelessInitCommand import EpomakerWirelessInitCommand
from fake.fake_controller import FakeEpomakerController
import epomakercontroller.cli as cli


def test_wireless_command_init_data():
    controller = FakeEpomakerController(cli.CONFIG_MAIN)
    controller.send_wireless_init()

    assert controller.commands
    reports = controller.commands[2].reports  # First will be poll command
    assert reports
    assert reports[0].header_format_string == "fe40"

    for index in range(1, len(reports)):
        assert EpomakerWirelessInitCommand.CHUNKS[index - 1] == reports[index].header_format_string


def test_wireless_poll():
    controller = FakeEpomakerController(cli.CONFIG_MAIN)
    controller.send_wireless_init()

    assert controller.commands
    controller.commands.pop(2)

    for command in controller.commands:
        assert isinstance(command, EpomakerPollCommand)
        assert command.reports[0].header_format_string == "f7"  # Poll command
