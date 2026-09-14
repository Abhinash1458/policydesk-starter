"""Premium calculator — pure functions, no database.   *** LAB 4: YOUR CODE HERE ***

    premium = sum_insured x base_rate x age_factor x tenure_factor x add_on_factor
    (never less than MIN_PREMIUM, rounded to 2 decimals)

Age factor
    < 25     -> 1.2 (Motor)  /  0.8 (Health, Term Life)
    25 - 45  -> 1.0
    46 - 60  -> 1.3
    > 60     -> 1.6
    negative -> PricingError

Tenure factor
    1 yr -> 1.0    2 yr -> 0.95    3 yr -> 0.90    anything else -> PricingError

Add-ons (each adds to the factor: 1.0 + 0.15 = 1.15)
    Health  CRITICAL_ILLNESS   +15%
    Motor   ZERO_DEPRECIATION  +10%
    an add-on not available for the product -> PricingError

Sum insured
    must be > 0 and within the product's min/max (when given) -> PricingError otherwise

Every function below is deliberately simple so it can be unit-tested (Lab 5).
Tip: ask Copilot to implement one function at a time from its docstring, then read every line.
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
    """Completed years between `dob` and `on` (default: today). (Given.)"""
    on = on or date.today()
    years = on.year - dob.year
    if (on.month, on.day) < (dob.month, dob.day):
        years -= 1
    return years


def parse_add_ons(raw: str | None) -> list[str]:
    """'critical_illness, x' -> ['CRITICAL_ILLNESS', 'X']. (Given.)"""
    return [c.strip().upper() for c in (raw or "").split(",") if c.strip()]


def age_factor(age: int, product: ProductCode) -> float:
    """Return the multiplier for this age band and product. See the rules at the top of the file."""
    # TODO (Lab 4): implement the four age bands. Motor and non-Motor differ only under 25.
    raise NotImplementedError("Lab 4: implement age_factor")


def tenure_factor(tenure_years: int) -> float:
    """Return the tenure discount multiplier, or raise PricingError for an unsupported tenure."""
    # TODO (Lab 4): look it up in TENURE_FACTORS.
    raise NotImplementedError("Lab 4: implement tenure_factor")


def add_on_factor(product: ProductCode, add_ons: list[str]) -> float:
    """1.0 plus the sum of every valid add-on loading for this product. Blank entries are ignored."""
    # TODO (Lab 4): use ADD_ONS; raise PricingError for an add-on the product does not offer.
    raise NotImplementedError("Lab 4: implement add_on_factor")


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
    """Return the annual premium in rupees, rounded to 2 decimals and never below MIN_PREMIUM."""
    # TODO (Lab 4): validate sum_insured, multiply the factors, apply the minimum, round.
    raise NotImplementedError("Lab 4: implement calculate_premium")
