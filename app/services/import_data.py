from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate


def import_ecb_data(csv_path: str = "data/eurofxref-hist.csv") -> int:
    csv_file = Path(csv_path)

    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"CSV file not found: {csv_file}") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"CSV file is empty: {csv_file}") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Failed to parse CSV file: {csv_file}") from exc

    if "Date" not in df.columns:
        raise ValueError("CSV must include a 'Date' column")

    db = SessionLocal()
    imported_count = 0

    try:
        for _, row in df.iterrows():
            try:
                parsed_date = datetime.strptime(str(row["Date"]), "%Y-%m-%d").date()
            except ValueError:
                continue

            for currency in df.columns:
                if currency == "Date":
                    continue

                rate = row[currency]
                if pd.isna(rate):
                    continue

                try:
                    rate_value = float(rate)
                except (TypeError, ValueError):
                    continue

                exchange = ExchangeRate(
                    base_currency="EUR",
                    target_currency=currency,
                    rate=rate_value,
                    date=parsed_date,
                )
                db.add(exchange)
                imported_count += 1

        db.commit()
        return imported_count
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("Failed to import ECB data into the database") from exc
    finally:
        db.close()


if __name__ == "__main__":
    print("IMPORT SCRIPT STARTED")
    imported = import_ecb_data()
    print(f"Data import complete ({imported} rows)")
