from uuid import uuid4


def register_and_login(client, username: str, password: str = "Password1!"):
    register = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
            "confirm_password": password,
        },
    )
    assert register.status_code == 200

    login = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def test_register(client):

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "Password1!",
            "confirm_password": "Password1!"
        }
    )

    assert response.status_code in [200, 400]


def test_login(client):

    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "Password1!"
        }
    )

    assert response.status_code == 200


def test_get_me(client):
    username = f"profile_{uuid4().hex[:8]}"
    token = register_and_login(client, username)

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["username"] == username


def test_update_me_username_returns_new_token(client):
    username = f"rename_{uuid4().hex[:8]}"
    token = register_and_login(client, username)

    new_username = f"renamed_{uuid4().hex[:8]}"
    update_response = client.put(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": new_username},
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["username"] == new_username
    assert "access_token" in updated

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {updated['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == new_username


def test_update_me_password(client):
    username = f"pwd_{uuid4().hex[:8]}"
    original_password = "Password1!"
    new_password = "Password2!"
    token = register_and_login(client, username, original_password)

    update_response = client.put(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": original_password,
            "new_password": new_password,
            "confirm_new_password": new_password,
        },
    )
    assert update_response.status_code == 200

    old_login = client.post(
        "/auth/login",
        json={"username": username, "password": original_password},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        json={"username": username, "password": new_password},
    )
    assert new_login.status_code == 200
