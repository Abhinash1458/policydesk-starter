"""Premium calculator — pure functions, no database.

    premium = sum_insured x base_rate x age_factor x tenure_factor x add_on_factor
    (never less than MIN_PREMIUM)

Age factor
    < 25     -> 1.2 (Motor)  /  0.8 (Health, Term Life)
    25 - 45  -> 1.0
    46 - 60  -> 1.3
    > 60     -> 1.6

Tenure factor
    1 yr -> 1.0    2 yr -> 0.95    3 yr -> 0.90

Add-ons
    Health  CRITICAL_ILLNESS   +15%
    Motor   ZERO_DEPRECIATION  +10%

These rules are deliberately simple so they can be unit-tested (Lab 5).
"""
from datetime import date

from app.models import ProductCode

MIN_PREMIUM = 1000.0

TENURE_FACTORS = {1: 1.0, 2: 0.95, 3: 0.90}

ADD_ONS: dict[ProductCode, dict[str, float]] = {
    ProductCode.HEALTH: {"CRITICAL_ILLNESS": 0.15},
    ProductCode.MOTOR: {"ZERO_DEPRECIATION": 0.10},
    ProductCode.TERM_LIFE: {},
}


class PricingError(ValueError):
    """Raised when a quote request breaks a business rule."""


def age_on(dob: date, on: date | None = None) -> int:
    """Completed years between `dob` and `on` (default: today)."""
    on = on or date.today()
    years = on.year - dob.year
    if (on.month, on.day) < (dob.month, dob.day):
        years -= 1
    return years


def age_factor(age: int, product: ProductCode) -> float:
    if age < 0:
        raise PricingError("Age cannot be negative")
    if age <= 25:
        return 1.2 if product == ProductCode.MOTOR else 0.8
    if age <= 45:
        return 1.0
    if age <= 60:
        return 1.3
    return 1.6


def tenure_factor(tenure_years: int) -> float:
    try:
        return TENURE_FACTORS[tenure_years]
    except KeyError:
        raise PricingError(f"Tenure must be 1, 2 or 3 years (got {tenure_years})") from None


def add_on_factor(product: ProductCode, add_ons: list[str]) -> float:
    """1.0 plus the sum of every valid add-on loading for this product."""
    allowed = ADD_ONS.get(product, {})
    factor = 1.0
    for code in add_ons:
        code = code.strip().upper()
        if not code:
            continue
        if code not in allowed:
            raise PricingError(f"Add-on {code} is not available for {product.value}")
        factor += allowed[code]
    return factor


def parse_add_ons(raw: str | None) -> list[str]:
    return [c.strip().upper() for c in (raw or "").split(",") if c.strip()]


def calculate_premium(
    *,
    sum_insured: float,
    base_rate: float,
    age: int,
    tenure_years: int,
    product: ProductCode,
    add_ons: list[str] | None = None,
    min_sum_insured: float | None = None,
    max_sum_insured: float | None = None,
) -> float:
    """Return the annual premium in rupees, rounded to 2 decimals."""
    if sum_insured <= 0:
        raise PricingError("Sum insured must be positive")
    if min_sum_insured is not None and sum_insured < min_sum_insured:
        raise PricingError(f"Sum insured must be at least {min_sum_insured:,.0f}")
    if max_sum_insured is not None and sum_insured > max_sum_insured:
        raise PricingError(f"Sum insured cannot exceed {max_sum_insured:,.0f}")

    premium = (
        sum_insured
        * base_rate
        * age_factor(age, product)
        * tenure_factor(tenure_years)
        * add_on_factor(product, add_ons or [])
    )
    return float(int(max(premium, MIN_PREMIUM)))
