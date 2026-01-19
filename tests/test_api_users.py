import pytest


@pytest.mark.asyncio
async def test_register_login_and_get_me(client):
    # Register
    resp = await client.post(
        "/api/v1/users/register",
        json={"email": "u1@example.com", "username": "u1", "password": "secret"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "u1@example.com"

    # Login
    resp2 = await client.post(
        "/api/v1/users/login",
        json={"email": "u1@example.com", "password": "secret"},
    )
    assert resp2.status_code == 200
    token = resp2.json().get("access_token")
    assert token

    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    resp3 = await client.get("/api/v1/users/me", headers=headers)
    assert resp3.status_code == 200
    me = resp3.json()
    assert me["email"] == "u1@example.com"
