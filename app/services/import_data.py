import pandas as pd
from datetime import datetime

from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate

print("IMPORT SCRIPT STARTED")

def import_ecb_data(csv_path="data/eurofxref-hist.csv"):

    df = pd.read_csv(csv_path)

    db = SessionLocal()

    for _, row in df.iterrows():

        date = datetime.strptime(row["Date"], "%Y-%m-%d")

        for currency in df.columns:

            if currency == "Date":
                continue

            rate = row[currency]

            if pd.isna(rate):
                continue

            try:
                rate = float(rate)
            except:
                continue

            exchange = ExchangeRate(
                base_currency="EUR",
                target_currency=currency,
                rate=rate,
                date=date
            )

            db.add(exchange)

    db.commit()
    db.close()

    print("Data import complete")

if __name__ == "__main__":
    import_ecb_data()