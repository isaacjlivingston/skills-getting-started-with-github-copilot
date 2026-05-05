from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_duplicate_signup_is_rejected():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "Michael@mergington.edu"},
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activities["Chess Club"]["participants"].count("michael@mergington.edu") == 1