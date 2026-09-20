"""Seed data loaded on first start: products and customers from data/*.csv, plus two ready-made policies.

The two policies exist so that claims can be filed and reviewed even before the premium calculator
(Phase 2, Example 4) is implemented. Their premiums are the values the calculator will produce.
"""
import csv
from datetime import date, timedelta
from pathlib import Path

from sqlmodel import Session, select

from app.models import Customer, Policy, Product, Quote

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# (customer email, product code, sum insured, tenure years, add-ons, premium, start date, vehicle)
SEED_POLICIES = [
    ("priya.nair@example.com", "HEALTH", 500000, 1, "", 15000.0, date(2026, 1, 1), None),
    ("rohan.das@example.com", "MOTOR", 800000, 2, "ZERO_DEPRECIATION", 20900.0, date(2026, 3, 1), "TS09AB1234"),
]


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

    if session.exec(select(Policy)).first() is None:
        for n, (email, code, sum_insured, tenure, add_ons, premium, start, vehicle) in enumerate(SEED_POLICIES, 1):
            customer = session.exec(select(Customer).where(Customer.email == email)).one()
            product = session.exec(select(Product).where(Product.code == code)).one()
            quote = Quote(
                customer_id=customer.id, product_id=product.id, sum_insured=sum_insured,
                tenure_years=tenure, add_ons=add_ons, premium=premium,
            )
            session.add(quote)
            session.commit()
            session.refresh(quote)
            session.add(
                Policy(
                    quote_id=quote.id,
                    policy_number=f"PD-{code}-{start.year}-{n:05d}",
                    customer_id=customer.id,
                    product_id=product.id,
                    sum_insured=sum_insured,
                    premium=premium,
                    start_date=start,
                    end_date=start + timedelta(days=365 * tenure) - timedelta(days=1),
                    vehicle_registration=vehicle,
                )
            )
        session.commit()
