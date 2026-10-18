"""DSCR / cash-to-close screen for STR + seasonal candidates (Manatee + Sarasota, FL).

All assumptions are explicit and adjustable at the top. Income figures are
seller-stated (unverified) unless noted.
"""
import json
import sys

RATE = 0.07875         # DSCR 30-yr fixed, STR, 80% LTV, 720+ FICO (base case)
RATE_IO = 0.08125      # interest-only option
LTV = 0.80
TERM_MO = 360
CLOSING_PCT = 0.040    # pts/fees + FL doc stamps/intangible + title + 12-mo prepaid ins + escrow
RESERVE_MO = 6         # months PITIA reserves (lender-specific: 3-12)

TAX_RATE = {"Manatee": 0.0150, "Sarasota": 0.0135}  # non-homestead incl. non-ad valorem, reset to price
INS_BASE = 7000        # rental-dwelling HO + wind + $1M STR liability, mainland CBS home
FLOOD = {"X": 1000, "AE": 4500, "VE": 9000, "?": 2000}

# Operating-expense profiles (real cash flow, NOT used by DSCR lenders)
PROFILES = {
    # nightly/weekly STR, full-service PM
    "str": {"mgmt": 0.20, "platform": 0.10, "cleaning": 0.10, "maint": 0.08, "capex": 0.05},
    # 30-day+ seasonal furnished (snowbird + off-season monthly), seasonal PM
    "seasonal": {"mgmt": 0.12, "platform": 0.02, "cleaning": 0.03, "maint": 0.06, "capex": 0.05},
}
UTIL_ANNUAL = 6000     # power, water/sewer/trash, internet, streaming (owner-paid in furnished rentals)
POOL_LAWN_PEST = 3000  # with pool; 1200 without


def pmt(principal, rate, n=TERM_MO):
    r = rate / 12
    return principal * r / (1 - (1 + r) ** -n)


def underwrite(p):
    price = p["price"]
    loan = price * LTV
    pi = pmt(loan, RATE)
    io = loan * RATE_IO / 12
    tax = price * TAX_RATE[p["county"]] / 12
    ins = (p.get("ins", INS_BASE) + FLOOD[p.get("flood", "?")]) / 12
    hoa = p.get("hoa", 0) or 0
    pitia = pi + tax + ins + hoa
    pitia_io = io + tax + ins + hoa
    gross = p["gross"]
    down = price - loan
    closing = price * CLOSING_PCT - p.get("seller_credit", 0)
    reserves = pitia * RESERVE_MO
    cash_needed = down + closing + reserves
    prof = PROFILES[p.get("profile", "str")]
    fixed = UTIL_ANNUAL + (POOL_LAWN_PEST if p.get("pool") else 1200)
    var_pm = sum(prof.values())
    var_self = var_pm - prof["mgmt"]
    noi_pm = gross * (1 - var_pm) - fixed
    noi_self = gross * (1 - var_self) - fixed
    return {
        "name": p["name"],
        "price": price,
        "gross": gross,
        "yield": gross / price,
        "PITIA": pitia,
        "DSCR": gross / 12 / pitia,
        "DSCR@80%": gross * 0.80 / 12 / pitia,
        "DSCR_IO@80%": gross * 0.80 / 12 / pitia_io,
        "cash_needed": cash_needed,
        "fits_150k": cash_needed <= 150000,
        "cf_self_yr": noi_self - pitia * 12,
        "cf_pm_yr": noi_pm - pitia * 12,
        "cap_rate_pm": noi_pm / price,
    }


def fmt(c, v):
    if c in ("yield", "cap_rate_pm"):
        return f"{v:.1%}"
    if c.startswith("DSCR"):
        return f"{v:.2f}"
    if isinstance(v, bool) or isinstance(v, str):
        return str(v)
    return f"{v:,.0f}"


if __name__ == "__main__":
    props = json.load(open(sys.argv[1]))
    rows = [underwrite(p) for p in props]
    rows.sort(key=lambda r: -r["DSCR@80%"])
    cols = ["name", "price", "gross", "yield", "PITIA", "DSCR", "DSCR@80%", "DSCR_IO@80%",
            "cash_needed", "fits_150k", "cf_self_yr", "cf_pm_yr", "cap_rate_pm"]
    print(" | ".join(cols))
    for r in rows:
        print(" | ".join(fmt(c, r[c]) for c in cols))
