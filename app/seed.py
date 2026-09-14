"""Load products and demo customers from data/*.csv on first start."""
import csv
from datetime import date
from pathlib import Path

from sqlmodel import Session, select

from app.models import Customer, Product

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def seed(session: Session) -> None:
    if session.exec(select(Product)).first() is None:
        with open(DATA_DIR / "seed_products.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                session.add(
                    Product(
                        code=row["code"],
                        name=row["name"],
                        description=row["description"],
                        base_rate=float(row["base_rate"]),
                        min_sum_insured=float(row["min_sum_insured"]),
                        max_sum_insured=float(row["max_sum_insured"]),
                    )
                )

    if session.exec(select(Customer)).first() is None:
        with open(DATA_DIR / "seed_customers.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                session.add(
                    Customer(
                        name=row["name"],
                        email=row["email"],
                        phone=row["phone"],
                        date_of_birth=date.fromisoformat(row["date_of_birth"]),
                    )
                )
    session.commit()
