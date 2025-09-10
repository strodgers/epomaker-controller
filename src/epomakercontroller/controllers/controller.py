from __future__ import annotations
import typing
import signal

from abc import ABCMeta, abstractmethod

if typing.TYPE_CHECKING:
    from types import FrameType
    from typing import Optional


class ControllerBase(metaclass=ABCMeta):
    """
    Just a base class for every type of controller.
    I assume you plan to support multiple keyboard types. Must be useful
    """
    def __init__(self):
        self.__ready = False

    @property
    def ready(self):
        return self.__ready

    @abstractmethod
    def open_device(self):
        # Resource lock
        raise NotImplementedError

    @abstractmethod
    def close_device(self):
        # Resource unlock
        raise NotImplementedError

    def __enter__(self):
        self.__ready = self.open_device()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_device()

    def _setup_signal_handling(self) -> None:
        """Sets up signal handling to close the HID device on termination."""
        signal.signal(signal.SIGINT, self._signal_handler)  # Handle Ctrl+C
        signal.signal(signal.SIGTERM, self._signal_handler)  # Handle termination
        signal.signal(signal.SIGQUIT, self._signal_handler) 

    def _signal_handler(self, sig: int, _: Optional[FrameType]) -> None:
        """Handles signals to ensure the HID device is closed."""
        self.close_device()
        exit(sig)   # Pass code to system
