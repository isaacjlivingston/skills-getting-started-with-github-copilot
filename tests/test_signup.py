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