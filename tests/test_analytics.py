def test_volatility(client):

    response = client.get("/volatility?base=EUR&target=USD")

    assert response.status_code == 200


def test_trend(client):

    response = client.get("/trend?base=EUR&target=USD")

    assert response.status_code == 200
