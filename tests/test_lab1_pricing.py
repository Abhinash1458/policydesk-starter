"""Lab 1 — premium calculator. These fail on the starter and pass once pricing.py is implemented.

Every age band and its boundaries (24/25, 45/46, 60/61), each tenure, add-ons, the minimum premium,
invalid input, and a worked example calculated by hand.
"""
from datetime import date

import pytest

from app.models import ProductCode
from app.services.pricing import (
    MIN_PREMIUM,
    PricingError,
    add_on_factor,
    age_factor,
    age_on,
    calculate_premium,
    parse_add_ons,
    tenure_factor,
)

pytestmark = pytest.mark.lab


def test_premium_worked_example():
    # 5,00,000 x 0.03 (Health base rate) x 1.0 (age 36) x 1.0 (1 yr) = 15,000
    assert calculate_premium(
        sum_insured=500000, base_rate=0.03, age=36, tenure_years=1, product=ProductCode.HEALTH
    ) == 15000.0


# ---- age bands ----------------------------------------------------------------

@pytest.mark.parametrize("age,expected", [(0, 0.8), (24, 0.8), (25, 1.0), (45, 1.0), (46, 1.3), (60, 1.3), (61, 1.6), (90, 1.6)])
def test_age_factor_health_bands_and_boundaries(age, expected):
    assert age_factor(age, ProductCode.HEALTH) == expected


@pytest.mark.parametrize("age,expected", [(18, 1.2), (24, 1.2), (25, 1.0)])
def test_age_factor_motor_loads_under_25(age, expected):
    assert age_factor(age, ProductCode.MOTOR) == expected


def test_age_factor_term_life_matches_health():
    assert age_factor(22, ProductCode.TERM_LIFE) == 0.8


def test_negative_age_is_rejected():
    with pytest.raises(PricingError):
        age_factor(-1, ProductCode.HEALTH)


# ---- tenure -------------------------------------------------------------------

@pytest.mark.parametrize("years,expected", [(1, 1.0), (2, 0.95), (3, 0.90)])
def test_tenure_factor(years, expected):
    assert tenure_factor(years) == expected


@pytest.mark.parametrize("years", [0, 4, -1])
def test_unsupported_tenure_is_rejected(years):
    with pytest.raises(PricingError):
        tenure_factor(years)


# ---- add-ons ------------------------------------------------------------------

def test_add_on_factor_health_critical_illness():
    assert add_on_factor(ProductCode.HEALTH, ["CRITICAL_ILLNESS"]) == pytest.approx(1.15)


def test_add_on_factor_motor_zero_depreciation_case_insensitive():
    assert add_on_factor(ProductCode.MOTOR, ["zero_depreciation"]) == pytest.approx(1.10)


def test_add_on_factor_ignores_blanks_and_defaults_to_one():
    assert add_on_factor(ProductCode.TERM_LIFE, ["", "  "]) == 1.0
    assert add_on_factor(ProductCode.HEALTH, []) == 1.0


def test_add_on_not_offered_by_product_is_rejected():
    with pytest.raises(PricingError):
        add_on_factor(ProductCode.HEALTH, ["ZERO_DEPRECIATION"])


def test_parse_add_ons_normalises():
    assert parse_add_ons(" critical_illness , x ") == ["CRITICAL_ILLNESS", "X"]
    assert parse_add_ons(None) == []


# ---- calculate_premium --------------------------------------------------------

def test_all_factors_combine():
    # 8,00,000 x 0.025 x 1.2 (motor, age 22) x 0.95 (2 yr) x 1.10 (zero dep) = 25,080
    premium = calculate_premium(
        sum_insured=800000, base_rate=0.025, age=22, tenure_years=2,
        product=ProductCode.MOTOR, add_ons=["ZERO_DEPRECIATION"],
    )
    assert premium == pytest.approx(25080.0)


def test_minimum_premium_applies():
    # 60,000 x 0.004 x 0.8 = 192 -> floor to 1,000
    assert calculate_premium(sum_insured=60000, base_rate=0.004, age=20, tenure_years=1, product=ProductCode.TERM_LIFE) == MIN_PREMIUM


def test_result_is_rounded_to_two_decimals():
    premium = calculate_premium(sum_insured=123457, base_rate=0.03, age=50, tenure_years=3, product=ProductCode.HEALTH)
    assert premium == round(premium, 2)


@pytest.mark.parametrize("sum_insured", [0, -5000])
def test_non_positive_sum_insured_is_rejected(sum_insured):
    with pytest.raises(PricingError):
        calculate_premium(sum_insured=sum_insured, base_rate=0.03, age=30, tenure_years=1, product=ProductCode.HEALTH)


def test_sum_insured_outside_product_limits_is_rejected():
    with pytest.raises(PricingError):
        calculate_premium(sum_insured=50000, base_rate=0.03, age=30, tenure_years=1, product=ProductCode.HEALTH,
                          min_sum_insured=100000, max_sum_insured=5000000)
    with pytest.raises(PricingError):
        calculate_premium(sum_insured=6000000, base_rate=0.03, age=30, tenure_years=1, product=ProductCode.HEALTH,
                          min_sum_insured=100000, max_sum_insured=5000000)


def test_age_on_counts_completed_years():
    assert age_on(date(1990, 8, 25), on=date(2026, 8, 24)) == 35
    assert age_on(date(1990, 8, 25), on=date(2026, 8, 25)) == 36
