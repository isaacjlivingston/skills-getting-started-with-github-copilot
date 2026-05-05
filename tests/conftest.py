from copy import deepcopy

import pytest

from src.app import activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)
