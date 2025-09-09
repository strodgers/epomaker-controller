from src.epomakercontroller.utils.decorators import noexcept


def test_noexcept():
    @noexcept("An error occurred: ")
    def cause_exception():
        """Some docstring"""
        raise RuntimeError("I'm an error")

    cause_exception()
    # Ensure that decorator did not shadow function name and docstring
    assert cause_exception.__doc__ == "Some docstring"
