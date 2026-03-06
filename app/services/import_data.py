import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate


def import_ecb_data(csv_path="data/eurofxref-hist.csv"):

    df = pd.read_csv(csv_path)

    db: Session = SessionLocal()

    for _, row in df.iterrows():
        date = datetime.strptime(row["Date"], "%Y-%m-%d")

        for currency, rate in row.items():
            if currency == "Date" or pd.isna(rate):
                continue

            exchange = ExchangeRate(
                base_currency="EUR",
                target_currency=currency,
                rate=float(rate),
                date=date
            )

            db.add(exchange)

    db.commit()
    db.close()

    print("Data import complete.")


if __name__ == "__main__":
    import_ecb_data()