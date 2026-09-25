# Lab 1 — The premium calculator

*45 minutes · `app/services/pricing.py` · tests: `tests/test_lab1_pricing.py`, `tests/test_lab1_quotes.py`, `tests/test_lab1_pages.py`*

## The problem statement

> **An agent selects a customer and a product, enters the sum insured, tenure and add-ons, and gets an annual premium.**
>
> `premium = sum_insured × base_rate × age_factor × tenure_factor × add_on_factor`, never below ₹1,000, rounded to 2 decimals.
>
> | Rule | Values |
> |---|---|
> | Age factor | under 25 → 1.2 for Motor, 0.8 for Health and Term Life · 25–45 → 1.0 · 46–60 → 1.3 · over 60 → 1.6 · negative age is an error |
> | Tenure factor | 1 yr → 1.0 · 2 yr → 0.95 · 3 yr → 0.90 · anything else is an error |
> | Add-ons | Health `CRITICAL_ILLNESS` +15 % · Motor `ZERO_DEPRECIATION` +10 % · each **adds** to the factor (1.0 + 0.15) · an add-on the product doesn't offer is an error |
> | Sum insured | must be > 0 and inside the product's min/max |
>
> **Acceptance:** Priya Nair (born 25 Aug 1990) · Health Shield (rate 0.03) · ₹5,00,000 · 1 year → **₹15,000.00**. `POST /api/quotes` → 201 / 404 / 422. *Get a quote* screen shows the premium.

The same rules are in the docstring at the top of `pricing.py` — **attach that file to every prompt**. Until this lab is done the quote form and `POST /api/quotes` answer **501 "Lab 1: implement calculate_premium"** — that's expected.

## Step 0 — see it fail (2 min)

```
pytest tests/test_lab1_pricing.py -q      # NotImplementedError everywhere
```
Browser: *Get a quote* → any values → the 501 message.

## Part A — one function per prompt (25 min)

After **each** prompt: paste, `pytest tests/test_lab1_pricing.py -q`, read the function aloud.

**A1 · `age_factor`** — 📎 `#file:app/services/pricing.py`
```
ROLE: senior Python engineer. CONTEXT: the attached file — rules in the module docstring. TASK: implement age_factor(age, product) only.
CONSTRAINTS: age < 0 -> PricingError("Age cannot be negative"); age < 25 -> 1.2 if product == ProductCode.MOTOR else 0.8;
age <= 45 -> 1.0; age <= 60 -> 1.3; else 1.6. 25 is NOT under 25. No new imports. FORMAT: the function only.
```
🔍 `age_factor(25, MOTOR)` → **1.0** · `age_factor(60, HEALTH)` → **1.3** · `age_factor(61, HEALTH)` → **1.6**
⚠️ `age <= 25` — the most common bug in the room. Log it if you got it.

**A2 · `tenure_factor`**
```
Implement tenure_factor(tenure_years) only: TENURE_FACTORS[tenure_years]; on KeyError raise
PricingError(f"Tenure must be 1, 2 or 3 years (got {tenure_years})") from None. Four lines max.
```
🔍 `tenure_factor(4)` raises **PricingError**, not `KeyError`.

**A3 · `add_on_factor`**
```
Implement add_on_factor(product, add_ons) only. factor = 1.0; for each code: strip+upper; skip blanks;
if code not in ADD_ONS[product] raise PricingError(f"Add-on {code} is not available for {product.value}");
else factor += ADD_ONS[product][code]. ADD the loadings, never multiply. add_on_factor(HEALTH, ["critical_illness"]) == 1.15.
```
🔍 `add_on_factor(TERM_LIFE, ["CRITICAL_ILLNESS"])` raises · `add_on_factor(HEALTH, ["", " "])` → 1.0
⚠️ multiplies (`factor *= 1 + pct`) instead of adding.

**A4 · `calculate_premium`**
```
Implement calculate_premium(...) only, keeping the keyword-only signature. Order: sum_insured <= 0 -> PricingError("Sum insured must be positive");
if min_sum_insured given and sum_insured < it -> PricingError(f"Sum insured must be at least {min_sum_insured:,.0f}");
if max given and sum_insured > it -> PricingError(f"Sum insured cannot exceed {max_sum_insured:,.0f}");
premium = sum_insured * base_rate * age_factor(age, product) * tenure_factor(tenure_years) * add_on_factor(product, add_ons or []);
return round(max(premium, MIN_PREMIUM), 2).
```
🔍 by hand: 5,00,000 × 0.03 × 1.0 × 1.0 = **15,000.0**. `pytest tests/test_lab1_pricing.py` → all green.
⚠️ rounds before the minimum · returns `int` · crashes on `add_ons=None`.

### The code you should end up with

```python
def age_factor(age: int, product: ProductCode) -> float:
    """Return the multiplier for this age band and product. See the rules at the top of the file."""
    if age < 0:
        raise PricingError("Age cannot be negative")
    if age < 25:
        return 1.2 if product == ProductCode.MOTOR else 0.8
    if age <= 45:
        return 1.0
    if age <= 60:
        return 1.3
    return 1.6


def tenure_factor(tenure_years: int) -> float:
    """Return the tenure discount multiplier, or raise PricingError for an unsupported tenure."""
    try:
        return TENURE_FACTORS[tenure_years]
    except KeyError:
        raise PricingError(f"Tenure must be 1, 2 or 3 years (got {tenure_years})") from None


def add_on_factor(product: ProductCode, add_ons: list[str]) -> float:
    """1.0 plus the sum of every valid add-on loading for this product. Blank entries are ignored."""
    available = ADD_ONS[product]
    factor = 1.0
    for code in add_ons:
        code = code.strip().upper()
        if not code:
            continue
        if code not in available:
            raise PricingError(f"Add-on {code} is not available for {product.value}")
        factor += available[code]
    return factor


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
    return round(max(premium, MIN_PREMIUM), 2)
```

## Part B — prove it end to end (10 min)

1. `pytest tests/test_lab1_pricing.py tests/test_lab1_quotes.py -q` → green (quotes API needs no code change — it already calls your calculator).
2. Browser: *Get a quote* → Priya Nair · Health Shield · 500000 · 1 year → **₹15,000.00** → the quote page. *Quotes* in the nav lists it as **Open**.
3. Swagger: `POST /api/quotes` with `tenure_years: 4` → **422** with a readable message; `customer_id: 99` → **404**.
4. Ask the AI for trouble: `Give me 5 inputs where calculate_premium could still be wrong, with expected vs actual.` Turn one into a test.

## Part C — review and commit (8 min)

📎 `#file:app/services/pricing.py`
```
Review against this checklist, report only problems: 1. any <= where the rule says "under"/"over"? 2. MIN_PREMIUM applied before rounding?
3. any import not in requirements.txt? 4. add-ons added, not multiplied? 5. does every error path raise PricingError with a message a user could read?
```
```
git add -A && git commit -m "Lab 1: quotation calculator" && git push
```
Actions tab → green. **Done when:** `pytest tests/test_lab1_pricing.py tests/test_lab1_quotes.py tests/test_lab1_pages.py` green · ₹15,000.00 on screen · one AI mistake logged.
