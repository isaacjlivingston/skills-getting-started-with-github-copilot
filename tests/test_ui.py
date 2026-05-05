from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_duplicate_signup_is_rejected():
    # Arrange
    activity_name = "Chess Club"
    email = "Michael@mergington.edu"  # already enrolled in seed data (lowercased)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 409
    assert response.json() == {"detail": "Student is already signed up for this activity"}
    assert activities[activity_name]["participants"].count("michael@mergington.edu") == 1


def test_signup_normalizes_email_case():
    # Arrange
    activity_name = "Chess Club"
    email = "NEW@Mergington.EDU"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert "new@mergington.edu" in activities[activity_name]["participants"]


def test_signup_full_activity_shows_error():
    # Arrange — fill Art Club (max 16) to capacity
    activity_name = "Art Club"
    activity = activities[activity_name]
    while len(activity["participants"]) < activity["max_participants"]:
        activity["participants"].append(f"filler{len(activity['participants'])}@mergington.edu")

    # Act — simulate the UI submitting the signup form
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "latecomer@mergington.edu"},
    )

    # Assert — UI should receive an error it can display to the student
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_full_activity_shows_error():
    # Arrange — fill Art Club (max 16) to capacity
    activity_name = "Art Club"
    activity = activities[activity_name]
    while len(activity["participants"]) < activity["max_participants"]:
        activity["participants"].append(f"filler{len(activity['participants'])}@mergington.edu")

    # Act — simulate the UI submitting the signup form
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "latecomer@mergington.edu"},
    )

    # Assert — UI should receive an error it can display to the student
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"