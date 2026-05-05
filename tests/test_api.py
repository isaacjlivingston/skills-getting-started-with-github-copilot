from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_root_redirects_to_index():
    # Arrange — no local state needed

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (301, 302, 307)
    assert response.headers["location"].endswith("/static/index.html")


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all():
    # Arrange — no local state needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert len(response.json()) == len(activities)


def test_get_activities_shape():
    # Arrange — no local state needed

    # Act
    response = client.get("/activities")

    # Assert
    for _name, details in response.json().items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_new_student():
    # Arrange
    activity_name = "Chess Club"
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_remove_existing_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # enrolled in seed data

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_remove_normalizes_email_case():
    # Arrange — seed a mixed-case email directly to prove normalization works on stored values
    activity_name = "Chess Club"
    activities[activity_name]["participants"].append("MixedCase@Mergington.EDU")
    email_input = "mixedcase@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email_input},
    )

    # Assert
    assert response.status_code == 200
    assert "MixedCase@Mergington.EDU" not in activities[activity_name]["participants"]


def test_remove_non_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_remove_unknown_activity_returns_404():
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
