def test_volatility(client):

    response = client.get("/volatility?base=EUR&target=USD")

    assert response.status_code == 200


def test_trend(client):

    response = client.get("/trend?base=EUR&target=USD")

    assert response.status_code == 200


def test_same_currency_analytics_message(client):

    response = client.get("/volatility?base=USD&target=USD")

    assert response.status_code == 422
    assert "same currency" in response.json()["detail"].lower()
