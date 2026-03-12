def get_auth_headers(client, username: str = "rates_user", password: str = "Password1!"):
    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
            "confirm_password": password,
        },
    )

    login = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_rates(client):
    response = client.get("/rates/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_rates(client):
    response = client.get("/rates/search?base_currency=EUR&target_currency=USD&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_rate_by_id(client):
    list_response = client.get("/rates/")
    first_rate_id = list_response.json()[0]["id"]

    response = client.get(f"/rates/{first_rate_id}")
    assert response.status_code == 200
    assert response.json()["id"] == first_rate_id


def test_bulk_create_requires_auth(client):
    response = client.post(
        "/rates/bulk",
        json={
            "rates": [
                {
                    "base_currency": "EUR",
                    "target_currency": "GBP",
                    "rate": 0.86,
                    "date": "2024-01-01",
                }
            ]
        },
    )
    assert response.status_code in [401, 403]


def test_bulk_create_with_auth(client):
    headers = get_auth_headers(client, username="bulk_user")
    response = client.post(
        "/rates/bulk",
        headers=headers,
        json={
            "rates": [
                {
                    "base_currency": "EUR",
                    "target_currency": "GBP",
                    "rate": 0.86,
                    "date": "2024-01-02",
                },
                {
                    "base_currency": "EUR",
                    "target_currency": "JPY",
                    "rate": 162.5,
                    "date": "2024-01-02",
                },
            ]
        },
    )
    assert response.status_code == 200
    assert response.json()["created"] == 2


def test_summary_requires_auth(client):
    response = client.get("/rates/stats/summary")
    assert response.status_code in [401, 403]


def test_summary_with_auth(client):
    headers = get_auth_headers(client, username="stats_user")
    response = client.get("/rates/stats/summary", headers=headers)
    assert response.status_code == 200
    assert "total_rates" in response.json()


def test_admin_bulk_delete_requires_admin(client):
    headers = get_auth_headers(client, username="normal_user")
    response = client.request(
        "DELETE",
        "/rates/bulk",
        headers=headers,
        json={"ids": [1]},
    )
    assert response.status_code == 403


def test_admin_bulk_delete_success(client):
    admin_headers = get_auth_headers(client, username="admin")

    created = client.post(
        "/rates/",
        headers=admin_headers,
        json={
            "base_currency": "EUR",
            "target_currency": "AUD",
            "rate": 1.65,
            "date": "2024-01-03",
        },
    )
    assert created.status_code == 200
    created_id = created.json()["id"]

    response = client.request(
        "DELETE",
        "/rates/bulk",
        headers=admin_headers,
        json={"ids": [created_id]},
    )
    assert response.status_code == 200
    assert response.json()["deleted"] == 1
