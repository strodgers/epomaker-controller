import functools
from src.epomakercontroller.logger.logger import Logger


def noexcept(custom_message : str):
    """
    Basic decorator that prevents error propagation and process death.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                Logger.log_error(custom_message + e.__str__())

        return wrapper
    return decorator
