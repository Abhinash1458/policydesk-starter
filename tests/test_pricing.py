"""Lab 1, Part D — tests for the premium calculator.

One example is given. Generate the rest with AI, then *validate*: run them, read them, find the one it got wrong.
Cover every age band and its boundaries (24/25, 45/46, 60/61), each tenure, add-ons, the minimum premium,
invalid input (age -1, sum insured 0 or negative, tenure 4) and a worked example you calculated by hand.
"""
from app.models import ProductCode
from app.services.pricing import calculate_premium


def test_premium_worked_example():
    # 5,00,000 x 0.03 (Health base rate) x 1.0 (age 36) x 1.0 (1 yr) = 15,000
    assert calculate_premium(
        sum_insured=500000, base_rate=0.03, age=36, tenure_years=1, product=ProductCode.HEALTH
    ) == 15000.0


# TODO (Lab 1): add your tests below.
