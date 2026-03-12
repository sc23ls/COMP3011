from app.analytics import trend as trend_module


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


def test_latest_cross_pair(client):

    response = client.get("/latest?base=USD&target=EUR")

    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert data["rate"] > 0


def test_detect_trend_uptrend_uses_chronological_order(monkeypatch):
    series = [(f"d{i}", 1.0 + (i * 0.01)) for i in range(30)]

    monkeypatch.setattr(trend_module, "get_cross_rates", lambda db, base, target: series)
    result = trend_module.detect_trend(db=None, base="EUR", target="USD")

    assert result == "uptrend"


def test_detect_trend_downtrend_uses_chronological_order(monkeypatch):
    series = [(f"d{i}", 2.0 - (i * 0.01)) for i in range(30)]

    monkeypatch.setattr(trend_module, "get_cross_rates", lambda db, base, target: series)
    result = trend_module.detect_trend(db=None, base="EUR", target="USD")

    assert result == "downtrend"
