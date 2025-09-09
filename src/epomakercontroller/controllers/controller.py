from __future__ import annotations
import typing
import signal

from abc import abstractmethod


if typing.TYPE_CHECKING:
    from types import FrameType
    from typing import Optional


class ControllerBase:
    """
    Just a base class for every type of controller.
    I assume you plan to support multiple keyboard types. Must be useful
    """

    @abstractmethod
    def try_open_device(self):
        # Resource lock
        raise NotImplementedError

    @abstractmethod
    def try_close_device(self):
        # Resource unlock
        raise NotImplementedError

    def __enter__(self):
        self.try_open_device()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.try_close_device()

    def _setup_signal_handling(self) -> None:
        """Sets up signal handling to close the HID device on termination."""
        signal.signal(signal.SIGINT, self._signal_handler)  # Handle Ctrl+C
        signal.signal(signal.SIGTERM, self._signal_handler)  # Handle termination

    def _signal_handler(self, sig: int, _: Optional[FrameType]) -> None:
        """Handles signals to ensure the HID device is closed."""
        self.try_close_device()
        exit(sig)   # Pass code to system
