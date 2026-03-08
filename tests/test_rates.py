def test_get_rates(client):

    response = client.get("/rates/")

    assert response.status_code == 200