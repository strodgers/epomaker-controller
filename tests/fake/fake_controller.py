from __future__ import annotations
import typing

from epomakercontroller.commands.EpomakerCommand import EpomakerCommand
from epomakercontroller.controllers.controller import ControllerBase
from epomakercontroller.epomakercontroller import EpomakerConfig

if typing.TYPE_CHECKING:
    from epomakercontroller.configs.configs import Config


class FakeController(ControllerBase):
    """
    This fixture should help in testing low-level functionality.
    Overrides some behaviour, related to HID devices. This approach
    will disconnect unit tests from physical devices.
    """

    def __init__(self,  config_main: Config, dry_run: bool) -> None:
        super().__init__()
        self.config = EpomakerConfig(config_main)


    def open_device(self):
        pass

    def close_device(self):
        pass

    def _send_command(self, command: EpomakerCommand):
        pass
