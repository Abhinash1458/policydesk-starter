// PolicyDesk — small progressive enhancements for the quote form.
// Live premium estimate mirrors app/services/pricing.py (server is the source of truth).
(function () {
  const form = document.getElementById("quote-form");
  if (!form) return;

  const customer = form.querySelector("#customer_id");
  const product = form.querySelector("#product_id");
  const sumInsured = form.querySelector("#sum_insured");
  const tenure = form.querySelector("#tenure_years");
  const hint = document.getElementById("product-hint");
  const live = document.getElementById("live-premium");
  const checks = form.querySelectorAll(".check");

  const TENURE = { 1: 1.0, 2: 0.95, 3: 0.9 };
  const ADD_ONS = { CRITICAL_ILLNESS: 0.15, ZERO_DEPRECIATION: 0.10 };
  const MIN_PREMIUM = 1000;

  const inr = (n) => "₹" + n.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function ageOf(dob) {
    const d = new Date(dob), t = new Date();
    let a = t.getFullYear() - d.getFullYear();
    if (t.getMonth() < d.getMonth() || (t.getMonth() === d.getMonth() && t.getDate() < d.getDate())) a--;
    return a;
  }

  function ageFactor(age, code) {
    if (age < 25) return code === "MOTOR" ? 1.2 : 0.8;
    if (age <= 45) return 1.0;
    if (age <= 60) return 1.3;
    return 1.6;
  }

  function syncAddOns() {
    const code = product.selectedOptions[0]?.dataset.code;
    checks.forEach((c) => {
      const on = c.dataset.for === code;
      c.style.display = on ? "" : "none";
      if (!on) c.querySelector("input").checked = false;
    });
  }

  function update() {
    const p = product.selectedOptions[0];
    const c = customer.selectedOptions[0];
    if (p && p.dataset.code) {
      hint.textContent = `Base rate ${p.dataset.rate} · Sum insured ${inr(+p.dataset.min)} – ${inr(+p.dataset.max)}`;
      sumInsured.min = p.dataset.min;
      sumInsured.max = p.dataset.max;
    }
    if (!(p && p.dataset.code && c && c.dataset.dob && +sumInsured.value > 0)) { live.textContent = "—"; return; }
    let addOn = 1.0;
    form.querySelectorAll("input[name=add_ons]:checked").forEach((i) => (addOn += ADD_ONS[i.value] || 0));
    const premium = +sumInsured.value * +p.dataset.rate * ageFactor(ageOf(c.dataset.dob), p.dataset.code) * TENURE[tenure.value] * addOn;
    live.textContent = inr(Math.max(premium, MIN_PREMIUM)) + " / year";
  }

  product.addEventListener("change", () => { syncAddOns(); update(); });
  [customer, sumInsured, tenure].forEach((el) => el.addEventListener("input", update));
  form.addEventListener("change", update);
  syncAddOns();
  update();
})();
