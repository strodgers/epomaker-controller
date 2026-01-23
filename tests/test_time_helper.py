import pytest

import time
from epomakercontroller.utils.time_helper import TimeHelper


@pytest.mark.parametrize(
    'waitTime', [2, 4]
)
def test_time_helper_general(waitTime):
    curTime = time.time()

    with TimeHelper(waitTime):
        pass

    elapsedTime = time.time() - curTime
    assert elapsedTime >= waitTime
