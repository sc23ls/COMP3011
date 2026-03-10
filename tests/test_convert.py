def test_convert(client):

    response = client.get(
        "/convert?base=EUR&target=USD&amount=100"
    )

    assert response.status_code == 200
    data = response.json()

    assert "converted" in data


def test_convert_same_currency(client):

    response = client.get(
        "/convert?base=USD&target=USD&amount=100"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["rate"] == 1
    assert data["converted"] == 100
