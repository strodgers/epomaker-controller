import time


class TimeHelper:
    """
    A helper class to ensure a minimum amount of time has passed between its creation and deletion.

    This class starts a timer when it is initialized. When it is deleted, it calculates the total
    elapsed time and enforces a delay to ensure that the specified minimum time has passed.

    Args:
        min_duration (float): The minimum total duration (in seconds) that should pass between the
                              creation and deletion of the instance.
    """
    def __init__(self, min_duration: float) -> None:
        self.min_duration = min_duration
        self.start_time = time.time()

    def __lock(self):
        self.start_time = time.time()

    def __free(self):
        elapsed_time = time.time() - self.start_time
        remaining_time = self.min_duration - elapsed_time
        if remaining_time > 0:
            time.sleep(remaining_time)

    def __enter__(self):
        self.__lock()

    def __exit__(self, *_, **__):
        self.__free()
