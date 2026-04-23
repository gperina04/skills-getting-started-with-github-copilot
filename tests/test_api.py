from copy import deepcopy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src import app as app_module

INITIAL_ACTIVITIES = deepcopy(app_module.activities)
client = TestClient(app_module.app)


def encode(value: str) -> str:
    return quote(value, safe="")


def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))


# Use a pytest fixture if pytest is available in the environment.
try:
    import pytest

    @pytest.fixture(autouse=True)
    def activity_reset_fixture():
        reset_activities()
        yield

except ImportError:
    # Fallback when pytest is not installed yet.
    reset_activities()


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_success():
    reset_activities()
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(
        f"/activities/{encode(activity)}/signup?email={encode(email)}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in app_module.activities[activity]["participants"]


def test_signup_duplicate_returns_400():
    reset_activities()
    activity = "Chess Club"
    email = "michael@mergington.edu"
    response = client.post(
        f"/activities/{encode(activity)}/signup?email={encode(email)}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_success():
    reset_activities()
    activity = "Chess Club"
    email = "daniel@mergington.edu"
    response = client.delete(
        f"/activities/{encode(activity)}/unregister?email={encode(email)}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in app_module.activities[activity]["participants"]


def test_unregister_missing_participant_returns_404():
    reset_activities()
    activity = "Chess Club"
    email = "missing@mergington.edu"
    response = client.delete(
        f"/activities/{encode(activity)}/unregister?email={encode(email)}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"
