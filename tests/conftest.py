import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.main import app
from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate


@pytest.fixture(scope="module")
def client():

    db = SessionLocal()

    existing = (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency == "EUR",
            ExchangeRate.target_currency == "USD"
        )
        .first()
    )

    if not existing:
        rate = ExchangeRate(
            base_currency="EUR",
            target_currency="USD",
            rate=1.1,
            date=date(2024, 1, 1)
        )

        db.add(rate)
        db.commit()

    db.close()

    return TestClient(app)