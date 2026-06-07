import copy

test_activity = "Chess Club"
new_email = "newstudent@mergington.edu"

from fastapi.testclient import TestClient
from src.app import activities, app

client = TestClient(app)


import pytest


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_name = test_activity

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity_name in data
    assert "description" in data[expected_activity_name]
    assert "schedule" in data[expected_activity_name]
    assert "participants" in data[expected_activity_name]


def test_signup_adds_new_participant():
    # Arrange
    activity_name = test_activity
    email = new_email
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = test_activity
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant():
    # Arrange
    activity_name = test_activity
    participant_email = activities[activity_name]["participants"][0]
    assert participant_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={participant_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = test_activity
    missing_email = "missing_student@mergington.edu"
    assert missing_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={missing_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"


def test_missing_activity_returns_404_for_signup_and_unregister():
    # Arrange
    missing_activity = "Nonexistent Club"
    email = new_email

    # Act
    signup_response = client.post(f"/activities/{missing_activity}/signup?email={email}")
    unregister_response = client.delete(f"/activities/{missing_activity}/unregister?email={email}")

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert unregister_response.status_code == 404
    assert unregister_response.json()["detail"] == "Activity not found"
