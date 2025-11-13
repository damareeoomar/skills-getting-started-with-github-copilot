import importlib
from importlib import import_module

from fastapi.testclient import TestClient
import pytest


@pytest.fixture(autouse=True)
def app_module():
    # reload module for test isolation (reset in-memory data)
    mod = import_module("src.app")
    importlib.reload(mod)
    return mod


def test_get_activities(app_module):
    client = TestClient(app_module.app)
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow(app_module):
    client = TestClient(app_module.app)
    email = "pytest_user@example.com"

    # ensure not present
    r = client.get("/activities")
    assert email not in r.json()["Chess Club"]["participants"]

    # signup
    r = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    r = client.get("/activities")
    assert email in r.json()["Chess Club"]["participants"]

    # unregister
    r = client.post(f"/activities/Chess%20Club/unregister?email={email}")
    assert r.status_code == 200

    r = client.get("/activities")
    assert email not in r.json()["Chess Club"]["participants"]


def test_unregister_nonexistent_returns_404(app_module):
    client = TestClient(app_module.app)
    r = client.post(
        "/activities/Chess%20Club/unregister?email=doesnotexist@example.com"
    )
    assert r.status_code == 404
