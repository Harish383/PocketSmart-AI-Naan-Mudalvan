import os

os.environ[
    "DATABASE_PATH"
] = "/tmp/pocketsmart_test.db"

os.environ[
    "SECRET_KEY"
] = "test-secret"


from fastapi.testclient import TestClient

from app.main import app

from app.database import init_db


init_db()


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_register_login_and_home():

    email = (
        "test_user@example.com"
    )

    register_response = client.post(
        "/register",
        data={
            "name": "Test User",
            "email": email,
            "password": "password123"
        }
    )

    if register_response.status_code == 409:

        client.post(
            "/login",
            data={
                "email": email,
                "password": "password123"
            }
        )

    assert register_response.status_code in (
        200,
        409
    )


    response = client.post(
        "/generate-home",
        json={
            "budget": 50000,

            "currency": "INR",

            "style": "modern",

            "rooms": [
                {
                    "name": "Living Room",

                    "items": [
                        {
                            "name": "LED light",
                            "quantity": 2
                        }
                    ]
                }
            ]
        }
    )


    assert response.status_code == 200

    assert (
        response.json()
        ["result"]
        ["planner_type"]
        == "home"
    )


def test_unauthorized():

    unauthenticated_client =
        TestClient(app)

    response = (
        unauthenticated_client
        .get("/session-info")
    )

    assert response.status_code == 401
