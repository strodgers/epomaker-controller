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

    def __del__(self) -> None:
        elapsed_time = time.time() - self.start_time
        remaining_time = self.min_duration - elapsed_time
        # Ensure we do not sleep for a negative amount of time
        if remaining_time > 0:
            time.sleep(remaining_time)
