"""Build STR_DSCR_Analysis.xlsx: live-formula DSCR / cash / cash-flow model per market.

Inputs (blue) are hardcoded listing facts and offer levers; every metric is an
Excel formula that reads the Assumptions tab, so changing a rate, tax rate,
insurance figure, or down payment % reflows the whole workbook.

Run:  python3 build_workbook.py  -> writes STR_DSCR_Analysis.xlsx next to this file.
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from workbook_data import (
    AS_OF, BUYER, CANDIDATE_SHEETS, CHECKLIST, COUNTY_TAX, KEYS_MARKETS, MARKETS, RULES, SOURCES, SUMMARY,
    SUMMARY_NOTES,
)
from propertyradar_data import PR_BENCH, PR_META, PR_ROWS, PR_VERIFY

OUT = Path(__file__).with_name("STR_DSCR_Analysis.xlsx")

FONT = "Arial"
BLUE = Font(name=FONT, size=10, color="0000FF")
BLACK = Font(name=FONT, size=10, color="000000")
GREEN = Font(name=FONT, size=10, color="008000")
BOLD = Font(name=FONT, size=10, bold=True)
TITLE = Font(name=FONT, size=14, bold=True, color="1F3864")
SUB = Font(name=FONT, size=10, italic=True, color="595959")
HDR_FONT = Font(name=FONT, size=10, bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor="1F3864")
CALC_HDR_FILL = PatternFill("solid", fgColor="2E75B6")
YELLOW = PatternFill("solid", fgColor="FFFF00")
BAND = PatternFill("solid", fgColor="F2F2F2")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

USD = '$#,##0;($#,##0);"-"'
PCT = '0.0%;(0.0%);"-"'
PCT3 = '0.000%'
DSCR = '0.00"x"'

A = "Assumptions"  # sheet name (no spaces -> no quoting needed)


def _cell(ws, ref, value, font=BLACK, fmt=None, fill=None, align=None, border=True):
    c = ws[ref]
    c.value = value
    c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if align:
        c.alignment = align
    if border:
        c.border = BOX
    return c


def build_assumptions(wb):
    ws = wb.active
    ws.title = A
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 38
    for col in "CDEFGH":
        ws.column_dimensions[col].width = 14
    ws.column_dimensions["I"].width = 70

    ws["B1"] = "STR / Seasonal DSCR Model: Assumptions"
    ws["B1"].font = TITLE
    ws["B2"] = (f"As of {AS_OF}. Blue = input you can change. Yellow = key lever. "
                "Black = formula. Green = pulled from another tab.")
    ws["B2"].font = SUB

    # Buyer
    r = 4
    _cell(ws, f"B{r}", "BUYER", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"C{r}", "Value", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"I{r}", "Note / source", HDR_FONT, fill=HDR_FILL)
    for i, (label, val, fmt, note) in enumerate(BUYER, start=r + 1):
        _cell(ws, f"B{i}", label)
        _cell(ws, f"C{i}", val, BLUE, fmt)
        _cell(ws, f"I{i}", note, SUB, align=WRAP)

    # Loan terms. Fixed cell positions referenced by every candidate formula.
    r = 10
    _cell(ws, f"B{r}", "LOAN TERMS (DSCR)", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"C{r}", "Value", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"I{r}", "Note / source", HDR_FONT, fill=HDR_FILL)
    loan_rows = [
        ("Rate at LTV > 75% (i.e., 80% LTV)", 0.075, PCT3, "Placeholder for 800 FICO STR DSCR. Overwrite with live rate sheet."),
        ("Rate at LTV > 70% to 75%", 0.0725, PCT3, "Placeholder. Overwrite with live rate sheet."),
        ("Rate at LTV <= 70%", 0.07125, PCT3, "Placeholder. Overwrite with live rate sheet."),
        ("Amortization (months)", 360, "0", "30-year fixed."),
        ("Default down payment %", 0.25, PCT, "Recommended 25% (rate tier + DSCR + cash flow). Each candidate row can override."),
        ("Closing costs (% of price)", 0.04, PCT, "Points/fees, FL doc stamps 0.35% + intangible 0.2% of loan, title, 12-mo prepaid insurance, escrow."),
        ("Reserves required (months PITIA)", 6, "0", "Covered by brokerage; shown for lender sizing only."),
        ("Lender income haircut (counted share of gross)", 0.80, PCT, "Many STR DSCR lenders count ~80% of gross or T12 net of mgmt. Use DSCR (haircut) column to qualify."),
        ("Default base insurance ($/yr): HO + wind + $1M STR liability", 7000, USD, "Mainland CBS home ~$500k. Per-county overrides in the county table below (e.g., Monroe/Keys)."),
    ]
    for i, (label, val, fmt, note) in enumerate(loan_rows, start=r + 1):
        _cell(ws, f"B{i}", label)
        key = label.startswith(("Rate", "Default down"))
        _cell(ws, f"C{i}", val, BLUE, fmt, fill=YELLOW if key else None)
        _cell(ws, f"I{i}", note, SUB, align=WRAP)
    # C11 rate80, C12 rate75, C13 rate70, C14 term, C15 default down, C16 closing,
    # C17 reserves, C18 haircut, C19 insurance

    # Flood by zone: B22:C25
    r = 21
    _cell(ws, f"B{r}", "FLOOD INSURANCE BY FEMA ZONE ($/yr)", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"C{r}", "$/yr", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"I{r}", "Note / source", HDR_FONT, fill=HDR_FILL)
    flood = [("X", 1000, "Citizens requires flood on all wind policies by 1/1/2027, including X zones."),
             ("AE", 4500, "NFIP Risk Rating 2.0 est.; elevation certificate drives price."),
             ("VE", 9000, "Coastal high-hazard; avoid for this buyer."),
             ("Unknown", 2000, "Placeholder until FEMA zone verified.")]
    for i, (z, v, note) in enumerate(flood, start=r + 1):
        _cell(ws, f"B{i}", z)
        _cell(ws, f"C{i}", v, BLUE, USD)
        _cell(ws, f"I{i}", note, SUB, align=WRAP)

    # County tax: B28:C(28+n)
    r = 27
    _cell(ws, f"B{r}", "BY COUNTY: PROPERTY TAX (% of price, non-homestead) + BASE INSURANCE", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"C{r}", "Tax rate", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"D{r}", "Base ins. $/yr", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"I{r}", "Note / source", HDR_FONT, fill=HDR_FILL)
    for i, rec in enumerate(COUNTY_TAX, start=r + 1):
        cty, v, ins, note = rec if len(rec) == 4 else (rec[0], rec[1], None, rec[2])
        _cell(ws, f"B{i}", cty)
        _cell(ws, f"C{i}", v, BLUE, PCT3)
        if ins is None:
            _cell(ws, f"D{i}", "=$C$19", BLACK, USD)
        else:
            _cell(ws, f"D{i}", ins, BLUE, USD, fill=YELLOW)
        _cell(ws, f"I{i}", note, SUB, align=WRAP)
    tax_first, tax_last = r + 1, r + len(COUNTY_TAX)

    # Opex profiles
    r = tax_last + 2
    hdr = ["OPERATING PROFILE", "Mgmt", "Platform", "Cleaning", "Maint/Supplies", "CapEx", "Non-mgmt total"]
    for j, h in enumerate(hdr):
        _cell(ws, f"{get_column_letter(2 + j)}{r}", h, HDR_FONT, fill=HDR_FILL, align=CENTER)
    _cell(ws, f"I{r}", "Note / source", HDR_FONT, fill=HDR_FILL)
    profiles = [
        ("STR", 0.20, 0.10, 0.10, 0.08, 0.05,
         "Nightly/weekly. Full-service PM 18-30% locally; Airbnb host-only fee 15.5% (blended 10%); "
         "cleaning ~10% of gross (offset if guest-paid fees are inside the seller's gross)."),
        ("Seasonal", 0.12, 0.02, 0.03, 0.06, 0.05,
         "30-day+ furnished (snowbird Jan-Apr, travel nurses, insurance displacement). Fewer turns."),
    ]
    prof_first = r + 1
    for i, (name, mg, pl, cl, mt, cx, note) in enumerate(profiles, start=r + 1):
        _cell(ws, f"B{i}", name)
        for j, v in enumerate((mg, pl, cl, mt, cx)):
            _cell(ws, f"{get_column_letter(3 + j)}{i}", v, BLUE, PCT)
        _cell(ws, f"H{i}", f"=SUM(D{i}:G{i})", BLACK, PCT)
        _cell(ws, f"I{i}", note, SUB, align=WRAP)
    prof_last = prof_first + len(profiles) - 1

    r = prof_last + 2
    _cell(ws, f"B{r}", "FIXED OPERATING COSTS ($/yr)", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"C{r}", "$/yr", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"I{r}", "Note / source", HDR_FONT, fill=HDR_FILL)
    fixed = [("Utilities (power, water, internet, streaming)", 6000, "Owner-paid in furnished rentals."),
             ("Pool + lawn + pest (with pool)", 3000, ""),
             ("Lawn + pest (no pool)", 1200, "")]
    fixed_row = r + 1
    for i, (label, v, note) in enumerate(fixed, start=r + 1):
        _cell(ws, f"B{i}", label)
        _cell(ws, f"C{i}", v, BLUE, USD)
        _cell(ws, f"I{i}", note, SUB, align=WRAP)

    refs = {
        "rate80": f"{A}!$C$11", "rate75": f"{A}!$C$12", "rate70": f"{A}!$C$13",
        "term": f"{A}!$C$14", "down": f"{A}!$C$15", "closing": f"{A}!$C$16",
        "reserves": f"{A}!$C$17", "haircut": f"{A}!$C$18", "ins": f"{A}!$C$19",
        "zones": f"{A}!$B$22:$B$25", "zone_cost": f"{A}!$C$22:$C$25",
        "counties": f"{A}!$B${tax_first}:$B${tax_last}", "county_tax": f"{A}!$C${tax_first}:$C${tax_last}",
        "county_ins": f"{A}!$D${tax_first}:$D${tax_last}",
        "profiles": f"{A}!$B${prof_first}:$B${prof_last}",
        "mgmt": f"{A}!$C${prof_first}:$C${prof_last}",
        "nonmgmt": f"{A}!$H${prof_first}:$H${prof_last}",
        "util": f"{A}!$C${fixed_row}", "pool": f"{A}!$C${fixed_row + 1}", "nopool": f"{A}!$C${fixed_row + 2}",
    }
    ws.freeze_panes = "B4"
    return refs


CAND_COLS = [
    # (header, width, kind)  kind: in = input (blue), calc = formula, txt = text input
    ("Rank", 6, "in"), ("Address", 30, "txt"), ("City / ZIP", 18, "txt"), ("County", 10, "in"),
    ("Type", 11, "txt"), ("Bd/Ba/SqFt/Yr", 15, "txt"), ("List Price", 12, "in"),
    ("Offer Price", 12, "in"), ("Seller Credit %", 9, "in"), ("Down Pmt %", 8, "in"),
    ("Stated Gross Income ($/yr)", 13, "in"), ("Income Basis (seller-stated)", 34, "txt"),
    ("Flood Zone", 9, "in"), ("Pool", 6, "in"), ("HOA ($/mo)", 9, "in"),
    ("Ins Override ($/yr)", 10, "in"), ("Profile", 9, "in"),
    # calcs
    ("Loan Amount", 12, "calc"), ("Rate", 8, "calc"), ("P&I ($/mo)", 10, "calc"),
    ("Taxes ($/mo)", 10, "calc"), ("Ins + Flood ($/mo)", 10, "calc"), ("PITIA ($/mo)", 11, "calc"),
    ("DSCR (gross)", 9, "calc"), ("DSCR (lender haircut)", 10, "calc"),
    ("Cash to Close", 12, "calc"), ("Reserves (6 mo)", 11, "calc"),
    ("Opex excl. Mgmt ($/yr)", 12, "calc"), ("Mgmt ($/yr)", 11, "calc"),
    ("Cash Flow Self-Managed ($/yr)", 13, "calc"), ("Cash Flow Full PM ($/yr)", 12, "calc"),
    ("Gross Yield", 8, "calc"), ("Cap Rate (w/ PM)", 8, "calc"),
    # reference
    ("Last Sale", 16, "txt"), ("DOM", 6, "in"), ("Key Risks / Notes", 50, "txt"), ("Listing Link", 14, "txt"),
]
COL = {h: get_column_letter(i + 1) for i, (h, _, _) in enumerate(CAND_COLS)}


def cand_formulas(row, R):
    c = {h: f"{COL[h]}{row}" for h in COL}
    ltv = f"(1-{c['Down Pmt %']})"
    prof = c["Profile"]
    return {
        "Loan Amount": f"={c['Offer Price']}*{ltv}",
        "Rate": f"=IF({ltv}>0.75,{R['rate80']},IF({ltv}>0.7,{R['rate75']},{R['rate70']}))",
        "P&I ($/mo)": f"=PMT({c['Rate']}/12,{R['term']},-{c['Loan Amount']})",
        "Taxes ($/mo)": f"={c['Offer Price']}*INDEX({R['county_tax']},MATCH({c['County']},{R['counties']},0))/12",
        "Ins + Flood ($/mo)": (f"=IF(ISNUMBER({c['Ins Override ($/yr)']}),{c['Ins Override ($/yr)']},"
                               f"INDEX({R['county_ins']},MATCH({c['County']},{R['counties']},0))"
                               f"+INDEX({R['zone_cost']},MATCH({c['Flood Zone']},{R['zones']},0)))/12"),
        "PITIA ($/mo)": f"={c['P&I ($/mo)']}+{c['Taxes ($/mo)']}+{c['Ins + Flood ($/mo)']}+{c['HOA ($/mo)']}",
        "DSCR (gross)": f"=IFERROR({c['Stated Gross Income ($/yr)']}/12/{c['PITIA ($/mo)']},0)",
        "DSCR (lender haircut)": f"=IFERROR({c['Stated Gross Income ($/yr)']}*{R['haircut']}/12/{c['PITIA ($/mo)']},0)",
        "Cash to Close": f"={c['Offer Price']}*{c['Down Pmt %']}+{c['Offer Price']}*({R['closing']}-{c['Seller Credit %']})",
        "Reserves (6 mo)": f"={c['PITIA ($/mo)']}*{R['reserves']}",
        "Opex excl. Mgmt ($/yr)": (f"={c['Stated Gross Income ($/yr)']}*INDEX({R['nonmgmt']},MATCH({prof},{R['profiles']},0))"
                                   f"+{R['util']}+IF({c['Pool']}=\"Y\",{R['pool']},{R['nopool']})"),
        "Mgmt ($/yr)": f"={c['Stated Gross Income ($/yr)']}*INDEX({R['mgmt']},MATCH({prof},{R['profiles']},0))",
        "Cash Flow Self-Managed ($/yr)": f"={c['Stated Gross Income ($/yr)']}-{c['Opex excl. Mgmt ($/yr)']}-{c['PITIA ($/mo)']}*12",
        "Cash Flow Full PM ($/yr)": f"={c['Cash Flow Self-Managed ($/yr)']}-{c['Mgmt ($/yr)']}",
        "Gross Yield": f"=IFERROR({c['Stated Gross Income ($/yr)']}/{c['Offer Price']},0)",
        "Cap Rate (w/ PM)": (f"=IFERROR(({c['Stated Gross Income ($/yr)']}-{c['Opex excl. Mgmt ($/yr)']}"
                             f"-{c['Mgmt ($/yr)']})/{c['Offer Price']},0)"),
    }


FMT = {
    "List Price": USD, "Offer Price": USD, "Seller Credit %": PCT, "Down Pmt %": PCT,
    "Stated Gross Income ($/yr)": USD, "HOA ($/mo)": USD, "Ins Override ($/yr)": USD, "Loan Amount": USD, "Rate": PCT3,
    "P&I ($/mo)": USD, "Taxes ($/mo)": USD, "Ins + Flood ($/mo)": USD, "PITIA ($/mo)": USD,
    "DSCR (gross)": DSCR, "DSCR (lender haircut)": DSCR, "Cash to Close": USD, "Reserves (6 mo)": USD,
    "Opex excl. Mgmt ($/yr)": USD, "Mgmt ($/yr)": USD, "Cash Flow Self-Managed ($/yr)": USD,
    "Cash Flow Full PM ($/yr)": USD, "Gross Yield": PCT, "Cap Rate (w/ PM)": PCT, "DOM": "0", "Rank": "0",
}


def build_candidates(wb, R, spec):
    ws = wb.create_sheet(spec["sheet"])
    ws["A1"] = spec["title"]
    ws["A1"].font = TITLE
    ws["A2"] = spec["subtitle"]
    ws["A2"].font = SUB
    ws["A3"] = ("Edit blue cells (Offer Price, Seller Credit %, Down Pmt %, Income, Flood Zone, Ins Override) to rerun. "
                "Ins Override (blank = county base + flood) is for condos with master wind/flood policies. "
                "Qualify on DSCR (lender haircut) >= 1.00; >= 1.15 preferred. Income is seller-stated until "
                "verified with platform payout reports.")
    ws["A3"].font = SUB
    hrow = 5
    for i, (h, w, kind) in enumerate(CAND_COLS, start=1):
        col = get_column_letter(i)
        ws.column_dimensions[col].width = w
        _cell(ws, f"{col}{hrow}", h, HDR_FONT, fill=CALC_HDR_FILL if kind == "calc" else HDR_FILL, align=CENTER)
    ws.row_dimensions[hrow].height = 42

    first = hrow + 1
    for k, rec in enumerate(spec["rows"]):
        row = first + k
        f = cand_formulas(row, R)
        vals = {
            "Rank": rec.get("rank"), "Address": rec["address"], "City / ZIP": rec["city"],
            "County": rec["county"], "Type": rec["type"], "Bd/Ba/SqFt/Yr": rec["specs"],
            "List Price": rec["list"], "Offer Price": rec.get("offer", rec["list"]),
            "Seller Credit %": rec.get("credit", 0), "Down Pmt %": rec.get("down", f"={R['down']}"),
            "Stated Gross Income ($/yr)": rec["gross"], "Income Basis (seller-stated)": rec["basis"],
            "Flood Zone": rec.get("flood", "Unknown"), "Pool": rec.get("pool", "N"),
            "HOA ($/mo)": rec.get("hoa", 0), "Ins Override ($/yr)": rec.get("ins"),
            "Profile": rec.get("profile", "STR"),
            "Last Sale": rec.get("last_sale", ""), "DOM": rec.get("dom"),
            "Key Risks / Notes": rec.get("notes", ""), "Listing Link": None,
        }
        for h, _, kind in CAND_COLS:
            ref = f"{COL[h]}{row}"
            if kind == "calc":
                _cell(ws, ref, f[h], BLACK, FMT.get(h))
            elif h == "Listing Link":
                c = _cell(ws, ref, "Zillow" if rec.get("url") else "", BLUE)
                if rec.get("url"):
                    c.hyperlink = rec["url"]
                    c.font = Font(name=FONT, size=10, color="0563C1", underline="single")
            else:
                v = vals[h]
                font = GREEN if isinstance(v, str) and v.startswith("=") else BLUE
                _cell(ws, ref, v, font, FMT.get(h), align=WRAP if kind == "txt" else None)
        if rec.get("highlight"):
            for h in ("Address", "DSCR (lender haircut)", "Cash to Close"):
                ws[f"{COL[h]}{row}"].fill = YELLOW
        if k % 2 == 1:
            for h, _, kind in CAND_COLS:
                cell = ws[f"{COL[h]}{row}"]
                if cell.fill.fgColor.rgb in (None, "00000000"):
                    cell.fill = BAND
        if rec.get("income_note"):
            ws[f"{COL['Stated Gross Income ($/yr)']}{row}"].comment = Comment(rec["income_note"], "Analyst")
    last = first + len(spec["rows"]) - 1
    if not spec["rows"]:
        ws["A6"] = "Pending: Pinellas sweep results."
        ws["A6"].font = SUB
        return first, last

    dv_flood = DataValidation(type="list", formula1=f"={A}!$B$22:$B$25", allow_blank=False)
    dv_prof = DataValidation(type="list", formula1='"STR,Seasonal"', allow_blank=False)
    dv_pool = DataValidation(type="list", formula1='"Y,N"', allow_blank=False)
    for dv, h in ((dv_flood, "Flood Zone"), (dv_prof, "Profile"), (dv_pool, "Pool")):
        ws.add_data_validation(dv)
        dv.add(f"{COL[h]}{first}:{COL[h]}{last}")

    if spec.get("watchlist"):
        r = last + 3
        ws[f"A{r}"] = spec["watchlist_title"]
        ws[f"A{r}"].font = BOLD
        r += 1
        heads = ["Address", "City / ZIP", "Price", "Evidence (no $ in listing)", "Ask agent for", "Link"]
        cols = [COL["Address"], COL["City / ZIP"], COL["List Price"], COL["Income Basis (seller-stated)"],
                COL["Key Risks / Notes"], COL["Listing Link"]]
        for h, col in zip(heads, cols):
            _cell(ws, f"{col}{r}", h, HDR_FONT, fill=HDR_FILL, align=CENTER)
        for w in spec["watchlist"]:
            r += 1
            _cell(ws, f"{cols[0]}{r}", w["address"], BLUE, align=WRAP)
            _cell(ws, f"{cols[1]}{r}", w["city"], BLUE, align=WRAP)
            _cell(ws, f"{cols[2]}{r}", w["price"], BLUE, USD)
            _cell(ws, f"{cols[3]}{r}", w["evidence"], BLUE, align=WRAP)
            _cell(ws, f"{cols[4]}{r}", w.get("ask", "T12 payout reports + TDT filings"), BLUE, align=WRAP)
            c = _cell(ws, f"{cols[5]}{r}", w.get("link_label", "Zillow"), BLUE)
            c.hyperlink = w["url"]
            c.font = Font(name=FONT, size=10, color="0563C1", underline="single")
    ws.freeze_panes = ws[f"C{first}"]
    return first, last


def build_scenarios(wb, R, picks):
    """picks: list of (sheet_name, row) for candidates to run at 20/25/30% down."""
    ws = wb.create_sheet("Down Pmt Scenarios")
    ws["A1"] = "Down Payment Scenarios: 20% vs 25% vs 30%"
    ws["A1"].font = TITLE
    ws["A2"] = ("Green cells pull offer price, credit, income, flood, pool, HOA and profile from the market tabs; "
                "rate tier follows LTV from Assumptions. Change a down % (blue) to test other levels.")
    ws["A2"].font = SUB
    heads = ["Property", "Down %", "Offer Price", "Seller Credit %", "Gross ($/yr)", "Loan", "Rate", "P&I ($/mo)",
             "PITIA ($/mo)", "DSCR (gross)", "DSCR (haircut)", "Cash In (down + closing - credit)",
             "Cash Flow Self-Managed ($/yr)", "Cash Flow Full PM ($/yr)", "Cash-on-Cash (self)",
             "Marginal Return on Extra Cash vs Prior Row"]
    widths = [34, 8, 12, 9, 12, 12, 8, 11, 11, 9, 9, 15, 14, 13, 10, 15]
    for i, (h, w) in enumerate(zip(heads, widths), start=1):
        col = get_column_letter(i)
        ws.column_dimensions[col].width = w
        _cell(ws, f"{col}4", h, HDR_FONT, fill=HDR_FILL, align=CENTER)
    ws.row_dimensions[4].height = 42
    row = 5
    for sheet, src in picks:
        q = f"'{sheet}'!" if " " in sheet or "-" in sheet else f"{sheet}!"
        s = {h: f"{q}${COL[h]}${src}" for h in COL}
        for j, d in enumerate((0.20, 0.25, 0.30)):
            r = row
            ltv = f"(1-B{r})"
            _cell(ws, f"A{r}", f"={s['Address']}", GREEN)
            _cell(ws, f"B{r}", d, BLUE, PCT, fill=YELLOW)
            _cell(ws, f"C{r}", f"={s['Offer Price']}", GREEN, USD)
            _cell(ws, f"D{r}", f"={s['Seller Credit %']}", GREEN, PCT)
            _cell(ws, f"E{r}", f"={s['Stated Gross Income ($/yr)']}", GREEN, USD)
            _cell(ws, f"F{r}", f"=C{r}*{ltv}", BLACK, USD)
            _cell(ws, f"G{r}", f"=IF({ltv}>0.75,{R['rate80']},IF({ltv}>0.7,{R['rate75']},{R['rate70']}))", BLACK, PCT3)
            _cell(ws, f"H{r}", f"=PMT(G{r}/12,{R['term']},-F{r})", BLACK, USD)
            pitia = (f"=H{r}+C{r}*INDEX({R['county_tax']},MATCH({s['County']},{R['counties']},0))/12"
                     f"+IF(ISNUMBER({s['Ins Override ($/yr)']}),{s['Ins Override ($/yr)']},"
                     f"INDEX({R['county_ins']},MATCH({s['County']},{R['counties']},0))"
                     f"+INDEX({R['zone_cost']},MATCH({s['Flood Zone']},{R['zones']},0)))/12+{s['HOA ($/mo)']}")
            _cell(ws, f"I{r}", pitia, BLACK, USD)
            _cell(ws, f"J{r}", f"=IFERROR(E{r}/12/I{r},0)", BLACK, DSCR)
            _cell(ws, f"K{r}", f"=IFERROR(E{r}*{R['haircut']}/12/I{r},0)", BLACK, DSCR)
            _cell(ws, f"L{r}", f"=C{r}*B{r}+C{r}*({R['closing']}-D{r})", BLACK, USD)
            opex = (f"E{r}*INDEX({R['nonmgmt']},MATCH({s['Profile']},{R['profiles']},0))+{R['util']}"
                    f"+IF({s['Pool']}=\"Y\",{R['pool']},{R['nopool']})")
            _cell(ws, f"M{r}", f"=E{r}-({opex})-I{r}*12", BLACK, USD)
            _cell(ws, f"N{r}", f"=M{r}-E{r}*INDEX({R['mgmt']},MATCH({s['Profile']},{R['profiles']},0))", BLACK, USD)
            _cell(ws, f"O{r}", f"=IFERROR(M{r}/L{r},0)", BLACK, PCT)
            if j == 0:
                _cell(ws, f"P{r}", "-", BLACK, align=CENTER)
            else:
                _cell(ws, f"P{r}", f"=IFERROR((M{r}-M{r - 1})/(L{r}-L{r - 1}),0)", BLACK, PCT)
            row += 1
        row += 1
    ws.freeze_panes = "B5"


PR_COLS = [
    # (header, width, kind)  kind: in = input (blue), txt = text input, calc = formula, link = Assumptions link (green)
    ("Address", 26, "txt"), ("City / ZIP", 17, "txt"), ("County", 10, "in"), ("Market (benchmark)", 22, "in"),
    ("Type", 13, "txt"), ("Beds", 6, "in"), ("Baths", 6, "in"), ("SqFt", 7, "in"), ("Year", 6, "in"),
    ("List Price", 11, "in"), ("DOM", 6, "in"), ("Last Sale Date", 11, "txt"), ("Last Sale Price", 11, "in"),
    ("Est. Equity", 11, "in"), ("Owner Type", 13, "txt"), ("Absentee", 8, "in"), ("Pool", 6, "in"),
    ("Flood Zone", 8, "in"), ("Tier", 15, "txt"),
    ("Down %", 7, "link"), ("Loan", 11, "calc"), ("Rate", 7, "calc"), ("PITIA ($/mo)", 10, "calc"),
    ("Req. Gross DSCR 1.00 ($/yr)", 12, "calc"), ("Req. Gross DSCR 1.25 ($/yr)", 12, "calc"),
    ("Cash to Close", 11, "calc"), ("Beds (screen)", 7, "calc"), ("Benchmark Gross ($/yr)", 11, "calc"),
    ("Benchmark / Req. 1.00", 9, "calc"), ("DSCR Screen", 10, "calc"), ("Notes", 60, "txt"),
]
PR_COL = {h: get_column_letter(i + 1) for i, (h, _, _) in enumerate(PR_COLS)}
PR_FMT = {"List Price": USD, "Last Sale Price": USD, "Est. Equity": USD, "Down %": PCT, "Loan": USD, "Rate": PCT3,
          "PITIA ($/mo)": USD, "Req. Gross DSCR 1.00 ($/yr)": USD, "Req. Gross DSCR 1.25 ($/yr)": USD,
          "Cash to Close": USD, "Benchmark Gross ($/yr)": USD, "Benchmark / Req. 1.00": DSCR, "SqFt": "#,##0",
          "Year": "0", "DOM": "0", "Beds (screen)": "0"}


def build_propertyradar(wb, R):
    """PropertyRadar pull: required-rent screen at list price. Inputs blue, formulas black, Assumptions links green."""
    ws = wb.create_sheet("PropertyRadar")
    ws["A1"] = "PropertyRadar Pull: Listed Absentee-Owned Homes, Required-Rent Screen"
    ws["A1"].font = TITLE
    ws["A2"] = (f"As of {PR_META['as_of']}. PropertyRadar has no rental income, so the screen asks: what gross rent does "
                "this house need to hit DSCR 1.00 / 1.25 after the lender haircut, at list price and the default down "
                "payment? Required gross = PITIA x 12 x target / haircut. Compare to the market benchmark (blue, editable).")
    ws["A2"].font = SUB
    r = 3
    for label, text in [("Credits", PR_META["credits"]), ("Criteria", PR_META["common"])] + list(PR_META["tiers"]):
        _cell(ws, f"A{r}", label, BOLD, border=False)
        ws[f"B{r}"] = text
        ws[f"B{r}"].font = SUB
        ws[f"B{r}"].alignment = WRAP
        ws.merge_cells(f"B{r}:P{r}")
        ws.row_dimensions[r].height = 26
        r += 1

    # Verification lookups on the Summary picks
    r += 1
    vh = ["Summary pick", "Owner type", "Mail = property", "Exemption?", "Last sale", "Last sale $", "Loan balance",
          "AVM", "Equity %", "List price", "DOM", "Listed", "Finding"]
    for j, h in enumerate(vh):
        _cell(ws, f"{get_column_letter(1 + j)}{r}", h, HDR_FONT, fill=HDR_FILL, align=CENTER)
    ws.merge_cells(f"M{r}:AE{r}")
    for rec in PR_VERIFY:
        r += 1
        for j, v in enumerate(rec):
            col = get_column_letter(1 + j)
            fmt = PCT if j == 8 else ("0" if j == 10 else (USD if isinstance(v, (int, float)) else None))
            _cell(ws, f"{col}{r}", v, BLUE, fmt, align=WRAP if j == 12 else None)
        ws.merge_cells(f"M{r}:AE{r}")
        ws.row_dimensions[r].height = 40
    r += 1

    # Screen targets + benchmark table
    r += 1
    _cell(ws, f"A{r}", "SCREEN TARGETS", HDR_FONT, fill=HDR_FILL)
    _cell(ws, f"B{r}", "Value", HDR_FONT, fill=HDR_FILL)
    t1, t2 = r + 1, r + 2
    _cell(ws, f"A{t1}", "DSCR target (floor)")
    _cell(ws, f"B{t1}", 1.00, BLUE, DSCR, fill=YELLOW)
    _cell(ws, f"A{t2}", "DSCR target (preferred)")
    _cell(ws, f"B{t2}", 1.25, BLUE, DSCR, fill=YELLOW)
    _cell(ws, f"D{r}", "BENCHMARK GROSS ($/yr) BY MARKET", HDR_FONT, fill=HDR_FILL)
    for j, h in enumerate(["3BR no pool", "3BR pool", "4BR+ no pool", "4BR+ pool"]):
        _cell(ws, f"{get_column_letter(5 + j)}{r}", h, HDR_FONT, fill=HDR_FILL, align=CENTER)
    ws.merge_cells(f"I{r}:P{r}")
    _cell(ws, f"I{r}", "Basis", HDR_FONT, fill=HDR_FILL)
    b_first = r + 1
    for k, (mkt, *vals) in enumerate(PR_BENCH):
        rr = b_first + k
        _cell(ws, f"D{rr}", mkt)
        for j, v in enumerate(vals):
            _cell(ws, f"{get_column_letter(5 + j)}{rr}", v, BLUE, USD)
    b_last = b_first + len(PR_BENCH) - 1
    ws[f"I{b_first}"] = ("Analyst estimates anchored to seller-stated incomes already in this workbook (West Bradenton "
                         "4BR pool $63-89k; Seminole $71k; Largo $51k; Cape Coral $60k). Sarasota County and Siesta Key "
                         "rows are 30-day+ seasonal (county 30-day minimum). Overwrite with AirDNA/PriceLabs comps.")
    ws[f"I{b_first}"].font = SUB
    ws[f"I{b_first}"].alignment = WRAP
    ws.merge_cells(f"I{b_first}:P{b_last}")
    bench_mk = f"$D${b_first}:$D${b_last}"
    bench_val = f"$E${b_first}:$H${b_last}"

    hrow = b_last + 2
    for i, (h, w, kind) in enumerate(PR_COLS, start=1):
        col = get_column_letter(i)
        ws.column_dimensions[col].width = w
        _cell(ws, f"{col}{hrow}", h, HDR_FONT, fill=CALC_HDR_FILL if kind in ("calc", "link") else HDR_FILL,
              align=CENTER)
    ws.row_dimensions[hrow].height = 42

    first = hrow + 1
    for k, rec in enumerate(PR_ROWS):
        row = first + k
        c = {h: f"{PR_COL[h]}{row}" for h in PR_COL}
        ltv = f"(1-{c['Down %']})"
        req = (f"={c['PITIA ($/mo)']}*12*{{t}}/{R['haircut']}")
        formulas = {
            "Down %": f"={R['down']}",
            "Loan": f"={c['List Price']}*{ltv}",
            "Rate": f"=IF({ltv}>0.75,{R['rate80']},IF({ltv}>0.7,{R['rate75']},{R['rate70']}))",
            "PITIA ($/mo)": (f"=PMT({c['Rate']}/12,{R['term']},-{c['Loan']})"
                             f"+{c['List Price']}*INDEX({R['county_tax']},MATCH({c['County']},{R['counties']},0))/12"
                             f"+(INDEX({R['county_ins']},MATCH({c['County']},{R['counties']},0))"
                             f"+INDEX({R['zone_cost']},MATCH({c['Flood Zone']},{R['zones']},0)))/12"),
            "Req. Gross DSCR 1.00 ($/yr)": req.format(t=f"$B${t1}"),
            "Req. Gross DSCR 1.25 ($/yr)": req.format(t=f"$B${t2}"),
            "Cash to Close": f"={c['List Price']}*({c['Down %']}+{R['closing']})",
            "Beds (screen)": f"=IF(ISNUMBER({c['Beds']}),{c['Beds']},IF({c['SqFt']}>=2000,4,3))",
            "Benchmark Gross ($/yr)": (f"=IFERROR(INDEX({bench_val},MATCH({c['Market (benchmark)']},{bench_mk},0),"
                                       f"1+IF({c['Beds (screen)']}>=4,2,0)+IF({c['Pool']}=\"Y\",1,0)),0)"),
            "Benchmark / Req. 1.00": f"=IFERROR({c['Benchmark Gross ($/yr)']}/{c['Req. Gross DSCR 1.00 ($/yr)']},0)",
            "DSCR Screen": (f"=IF(ISNUMBER(SEARCH(\"Mobile\",{c['Type']})),\"EXCLUDED\","
                            f"IF({c['Benchmark Gross ($/yr)']}>={c['Req. Gross DSCR 1.25 ($/yr)']},\"PASS\","
                            f"IF({c['Benchmark Gross ($/yr)']}>={c['Req. Gross DSCR 1.00 ($/yr)']},\"MARGINAL\",\"FAIL\")))"),
        }
        vals = {
            "Address": rec["address"], "City / ZIP": rec["city"], "County": rec["county"],
            "Market (benchmark)": rec["market"], "Type": rec["type"], "Beds": rec["beds"], "Baths": rec["baths"],
            "SqFt": rec["sqft"], "Year": rec["year"], "List Price": rec["list"], "DOM": rec["dom"],
            "Last Sale Date": rec["last_date"], "Last Sale Price": rec["last_price"], "Est. Equity": rec["equity"],
            "Owner Type": rec["owner"], "Absentee": rec["absentee"], "Pool": rec["pool"], "Flood Zone": rec["flood"],
            "Tier": rec["tier"], "Notes": rec["notes"],
        }
        for h, _, kind in PR_COLS:
            ref = f"{PR_COL[h]}{row}"
            if kind == "calc":
                _cell(ws, ref, formulas[h], BLACK, PR_FMT.get(h))
            elif kind == "link":
                _cell(ws, ref, formulas[h], GREEN, PR_FMT.get(h))
            else:
                _cell(ws, ref, vals[h], BLUE, PR_FMT.get(h), align=WRAP if h == "Notes" else None)
            if k % 2 == 1:
                ws[ref].fill = BAND
        if rec.get("highlight"):
            for h in ("Address", "DSCR Screen"):
                ws[f"{PR_COL[h]}{row}"].fill = YELLOW
    last = first + len(PR_ROWS) - 1
    dv_flood = DataValidation(type="list", formula1=f"={A}!$B$22:$B$25", allow_blank=False)
    dv_pool = DataValidation(type="list", formula1='"Y,N"', allow_blank=False)
    dv_mkt = DataValidation(type="list", formula1=f"={bench_mk}", allow_blank=False)
    for dv, h in ((dv_flood, "Flood Zone"), (dv_pool, "Pool"), (dv_mkt, "Market (benchmark)")):
        ws.add_data_validation(dv)
        dv.add(f"{PR_COL[h]}{first}:{PR_COL[h]}{last}")
    ws.auto_filter.ref = f"A{hrow}:{PR_COL['Notes']}{last}"
    ws.freeze_panes = ws[f"C{first}"]


def build_summary(wb, firsts):
    ws = wb.create_sheet("Summary", 0)
    ws["A1"] = "STR DSCR Search: Summary of Top Picks"
    ws["A1"].font = TITLE
    ws["A2"] = (f"As of {AS_OF}. Every number below is a live link (green) to the market tabs; change inputs there or on "
                "Assumptions.")
    ws["A2"].font = SUB
    heads = ["Market Tab", "Address", "City / ZIP", "Offer Price", "Stated Gross ($/yr)", "PITIA ($/mo)",
             "DSCR (gross)", "DSCR (lender haircut)", "Cash to Close", "Cash Flow Self-Managed ($/yr)",
             "Cash Flow Full PM ($/yr)", "Verdict"]
    widths = [18, 32, 20, 12, 13, 11, 9, 10, 12, 13, 12, 60]
    src = ["Address", "City / ZIP", "Offer Price", "Stated Gross Income ($/yr)", "PITIA ($/mo)", "DSCR (gross)",
           "DSCR (lender haircut)", "Cash to Close", "Cash Flow Self-Managed ($/yr)", "Cash Flow Full PM ($/yr)"]
    for i, (h, w) in enumerate(zip(heads, widths), start=1):
        col = get_column_letter(i)
        ws.column_dimensions[col].width = w
        _cell(ws, f"{col}4", h, HDR_FONT, fill=HDR_FILL, align=CENTER)
    ws.row_dimensions[4].height = 32
    for k, (sheet, idx, verdict) in enumerate(SUMMARY):
        r = 5 + k
        q = f"'{sheet}'!" if (" " in sheet or "-" in sheet) else f"{sheet}!"
        row = firsts[sheet] + idx
        _cell(ws, f"A{r}", sheet)
        for j, h in enumerate(src, start=2):
            _cell(ws, f"{get_column_letter(j)}{r}", f"={q}${COL[h]}${row}", GREEN, FMT.get(h), align=WRAP)
        _cell(ws, f"L{r}", verdict, BLACK, align=WRAP, fill=YELLOW if k == 0 else None)
    r = 5 + len(SUMMARY) + 1
    ws[f"A{r}"] = "Key takeaways"
    ws[f"A{r}"].font = BOLD
    for note in SUMMARY_NOTES:
        r += 1
        ws[f"A{r}"] = "- " + note
        ws[f"A{r}"].font = BLACK
        ws.merge_cells(f"A{r}:L{r}")
        ws[f"A{r}"].alignment = WRAP
        ws.row_dimensions[r].height = 28
    ws.freeze_panes = "B5"


def build_table_sheet(wb, name, title, subtitle, headers, widths, rows, link_col=None):
    ws = wb.create_sheet(name)
    ws["A1"] = title
    ws["A1"].font = TITLE
    ws["A2"] = subtitle
    ws["A2"].font = SUB
    for i, (h, w) in enumerate(zip(headers, widths), start=1):
        col = get_column_letter(i)
        ws.column_dimensions[col].width = w
        _cell(ws, f"{col}4", h, HDR_FONT, fill=HDR_FILL, align=CENTER)
    ws.row_dimensions[4].height = 32
    for k, rec in enumerate(rows):
        r = 5 + k
        for i, v in enumerate(rec, start=1):
            col = get_column_letter(i)
            if link_col is not None and i - 1 == link_col and v:
                c = _cell(ws, f"{col}{r}", "Link", BLUE)
                c.hyperlink = v
                c.font = Font(name=FONT, size=10, color="0563C1", underline="single")
            else:
                fmt = USD if isinstance(v, (int, float)) and abs(v) >= 1000 else None
                _cell(ws, f"{col}{r}", v, BLUE if isinstance(v, (int, float)) else BLACK, fmt, align=WRAP,
                      fill=BAND if k % 2 else None)
    ws.freeze_panes = "B5"
    return ws


def main():
    wb = Workbook()
    R = build_assumptions(wb)
    picks, firsts = [], {}
    for spec in CANDIDATE_SHEETS:
        first, _ = build_candidates(wb, R, spec)
        firsts[spec["sheet"]] = first
        for idx in spec.get("scenario_rows", []):
            picks.append((spec["sheet"], first + idx))
    build_scenarios(wb, R, picks)
    build_propertyradar(wb, R)
    if MARKETS:
        build_table_sheet(wb, "Other SWFL Markets", MARKETS["title"], MARKETS["subtitle"],
                          MARKETS["headers"], MARKETS["widths"], MARKETS["rows"])
    build_table_sheet(wb, "Keys Market Guide", KEYS_MARKETS["title"], KEYS_MARKETS["subtitle"],
                      KEYS_MARKETS["headers"], KEYS_MARKETS["widths"], KEYS_MARKETS["rows"])
    build_table_sheet(wb, "STR Rules", "STR / Minimum-Stay Rules by Jurisdiction",
                      "Verify with the city/county before contract; pre-2011 local bans survive FL preemption (F.S. 509.032(7)).",
                      RULES["headers"], RULES["widths"], RULES["rows"])
    build_table_sheet(wb, "Diligence Checklist", "Ask Every Listing Agent Before Writing an Offer",
                      "Send as one request; lender pre-reviews payouts before inspection period ends.",
                      ["#", "Item", "Why it matters"], [5, 60, 70], CHECKLIST)
    build_table_sheet(wb, "Sources", "Sources and Notes", f"Research compiled {AS_OF}.",
                      ["Topic", "Source / Note", "URL"], [28, 80, 60], SOURCES, link_col=2)
    build_summary(wb, firsts)
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
    wb.active = 0
    wb.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
