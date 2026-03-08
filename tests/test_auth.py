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