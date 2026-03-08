def test_convert(client):

    response = client.get(
        "/convert?base=EUR&target=USD&amount=100"
    )

    assert response.status_code == 200
    data = response.json()

    assert "converted" in data