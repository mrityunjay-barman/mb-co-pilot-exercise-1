from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_activity_list():
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert expected_keys <= set(activities["Chess Club"].keys())


def test_signup_adds_participant_and_returns_success_message():
    # Arrange
    activity_name = "Chess Club"
    email = "test-student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate-student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={email}"

    client.post(signup_url)

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Gym Class"
    email = "remove-me@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={email}"
    remove_url = f"/activities/{activity_name}/participants?email={email}"

    client.post(signup_url)

    # Act
    response = client.delete(remove_url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "missing-student@mergington.edu"
    remove_url = f"/activities/{activity_name}/participants?email={email}"

    # Act
    response = client.delete(remove_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
