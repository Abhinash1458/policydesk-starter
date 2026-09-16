"""Unit tests for the premium calculator (Lab 1 reference)."""
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
    tenure_factor,
)


# ---- age --------------------------------------------------------------------
def test_age_on_before_and_after_birthday():
    dob = date(2000, 6, 15)
    assert age_on(dob, date(2026, 6, 14)) == 25
    assert age_on(dob, date(2026, 6, 15)) == 26


@pytest.mark.parametrize(
    "age,product,expected",
    [
        (24, ProductCode.MOTOR, 1.2),
        (24, ProductCode.HEALTH, 0.8),
        (24, ProductCode.TERM_LIFE, 0.8),
        (25, ProductCode.MOTOR, 1.0),   # band boundary
        (45, ProductCode.HEALTH, 1.0),
        (46, ProductCode.HEALTH, 1.3),  # band boundary
        (60, ProductCode.HEALTH, 1.3),
        (61, ProductCode.HEALTH, 1.6),  # band boundary
        (0, ProductCode.HEALTH, 0.8),
    ],
)
def test_age_factor_bands(age, product, expected):
    assert age_factor(age, product) == expected


def test_negative_age_rejected():
    with pytest.raises(PricingError):
        age_factor(-1, ProductCode.HEALTH)


# ---- tenure -----------------------------------------------------------------
@pytest.mark.parametrize("years,expected", [(1, 1.0), (2, 0.95), (3, 0.90)])
def test_tenure_factor(years, expected):
    assert tenure_factor(years) == expected


def test_tenure_out_of_range():
    with pytest.raises(PricingError):
        tenure_factor(4)


# ---- add-ons ----------------------------------------------------------------
def test_add_on_factor_health_critical_illness():
    assert add_on_factor(ProductCode.HEALTH, ["CRITICAL_ILLNESS"]) == pytest.approx(1.15)


def test_add_on_factor_motor_zero_dep():
    assert add_on_factor(ProductCode.MOTOR, ["zero_depreciation"]) == pytest.approx(1.10)


def test_add_on_not_available_for_product():
    with pytest.raises(PricingError):
        add_on_factor(ProductCode.TERM_LIFE, ["CRITICAL_ILLNESS"])


def test_no_add_ons_is_neutral():
    assert add_on_factor(ProductCode.HEALTH, []) == 1.0
    assert add_on_factor(ProductCode.HEALTH, ["", " "]) == 1.0


# ---- full premium -----------------------------------------------------------
def test_premium_worked_example():
    # 5,00,000 x 0.03 x 1.0 (age 36) x 1.0 (1 yr) = 15,000
    assert calculate_premium(
        sum_insured=500000, base_rate=0.03, age=36, tenure_years=1, product=ProductCode.HEALTH
    ) == 15000.0


def test_premium_with_all_factors():
    # 8,00,000 x 0.025 x 1.2 (age 22 motor) x 0.95 (2 yr) x 1.10 (zero dep) = 25,080
    assert calculate_premium(
        sum_insured=800000, base_rate=0.025, age=22, tenure_years=2,
        product=ProductCode.MOTOR, add_ons=["ZERO_DEPRECIATION"],
    ) == pytest.approx(25080.0)


def test_minimum_premium_applies():
    assert calculate_premium(
        sum_insured=10000, base_rate=0.004, age=30, tenure_years=1, product=ProductCode.TERM_LIFE
    ) == MIN_PREMIUM


def test_premium_is_rounded_to_paise():
    p = calculate_premium(sum_insured=123456, base_rate=0.03, age=50, tenure_years=3, product=ProductCode.HEALTH)
    assert p == round(p, 2)


@pytest.mark.parametrize("sum_insured", [0, -1000])
def test_non_positive_sum_insured_rejected(sum_insured):
    with pytest.raises(PricingError):
        calculate_premium(sum_insured=sum_insured, base_rate=0.03, age=30, tenure_years=1, product=ProductCode.HEALTH)


def test_sum_insured_limits_enforced():
    with pytest.raises(PricingError):
        calculate_premium(sum_insured=50000, base_rate=0.03, age=30, tenure_years=1,
                          product=ProductCode.HEALTH, min_sum_insured=100000)
    with pytest.raises(PricingError):
        calculate_premium(sum_insured=6000000, base_rate=0.03, age=30, tenure_years=1,
                          product=ProductCode.HEALTH, max_sum_insured=5000000)
