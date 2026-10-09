import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from app import activities, app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_participants():
    snapshot = {name: list(details["participants"]) for name, details in activities.items()}
    yield
    for name, participants in snapshot.items():
        activities[name]["participants"] = participants


def test_list_activities_returns_every_activity():
    response = client.get("/activities")
    assert response.status_code == 200
    assert set(response.json()) == set(activities)


def test_signup_adds_the_student():
    response = client.post("/activities/Chess Club/signup", params={"email": "new@mergington.edu"})
    assert response.status_code == 200
    assert "new@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_twice_is_rejected():
    client.post("/activities/Chess Club/signup", params={"email": "twice@mergington.edu"})
    response = client.post("/activities/Chess Club/signup", params={"email": "twice@mergington.edu"})
    assert response.status_code == 400
    assert activities["Chess Club"]["participants"].count("twice@mergington.edu") == 1


def test_signup_for_unknown_activity_returns_404():
    response = client.post("/activities/Quidditch/signup", params={"email": "someone@mergington.edu"})
    assert response.status_code == 404
