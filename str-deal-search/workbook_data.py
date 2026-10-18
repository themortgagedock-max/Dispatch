"""Listing facts and research inputs for build_workbook.py.

Every income figure is quoted/derived from the listing remarks (seller-stated, unverified)
as of AS_OF. Offer prices are our negotiating targets, not list prices.
"""

AS_OF = "2026-10-18"

BUYER = [
    ("Credit score (FICO)", 800, "0", "Per broker; top DSCR pricing tier."),
    ("Cash earmarked for down + closing", 150000, '$#,##0', "Per broker."),
    ("Brokerage (reserves / extra down)", 550000, '$#,##0', "Per broker. CPA: check capital gains before liquidating."),
    ("Checking (EMD)", 60000, '$#,##0', "Per broker. Earnest money 3-5% to compete."),
]

COUNTY_TAX = [
    ("Manatee", 0.0150, "Unincorporated ~13.3 mills (2025) + city + non-ad valorem; reset to purchase price."),
    ("Sarasota", 0.0135, "11.47 mills countywide (2025); City of Sarasota ~14.9 mills."),
    ("Pinellas", 0.0175, "Placeholder pending research: ~17-21 mills incl. city + non-ad valorem."),
    ("Lee", 0.0170, "Placeholder: Cape Coral/Fort Myers ~16-19 mills + assessments."),
    ("Charlotte", 0.0165, "Placeholder."),
    ("Collier", 0.0120, "Placeholder: lowest millage on the coast (~11-12 mills)."),
]

Z = "https://www.zillow.com/homedetails/"

MANATEE_SARASOTA = {
    "sheet": "Manatee-Sarasota",
    "title": "Manatee + Sarasota County: STR / Seasonal Candidates with Documented Income",
    "subtitle": (f"Active as of {AS_OF}. Screened ~600 listings across Zillow (14 keyword sweeps), Redfin, brokerages "
                 "and STR marketplaces. Yellow rows = recommended."),
    "scenario_rows": [0, 1, 2],
    "rows": [
        dict(rank=1, address="8404 43rd Ave Terrace W", city="Bradenton 34209", county="Manatee", type="SFR",
             specs="4/2 / 1,430 / 1978", list=584900, offer=560000, credit=0.03, gross=85000,
             basis="\"almost $85,000 in gross revenue over the past 12 months\" (T12)", flood="Unknown", pool="Y",
             hoa=0, profile="STR", last_sale="$595,000 (Aug 2023)", dom=21, highlight=True,
             notes=("Heated pool + spa, no HOA, turnkey; full 2021 reno (roof/HVAC/windows/plumbing/electric). "
                    "First Street flood 7/10; neighbor parcel AE/X: get FEMA zone + elevation cert + CLUE. "
                    "Featured in national STR newsletter 9/29: move fast. Uninc. Manatee: nightly legal."),
             url=Z + "8404-43rd-Avenue-Ter-W-Bradenton-FL-34209/45762957_zpid/"),
        dict(rank=2, address="5318 17th St W (duplex)", city="Bradenton 34207", county="Manatee", type="Duplex",
             specs="2 units / 1,740 / 1971", list=475000, offer=460000, credit=0, gross=73000,
             basis="Unit B Airbnb \"over $53,000 in 2025\" + Unit A LTR (est. ~$20k/yr; rent not stated)",
             flood="Unknown", pool="N", hoa=0, profile="STR", last_sale="$420,000 (Apr 2024)", dom=14,
             highlight=True, income_note="$53k STR (2025, partial owner use) + ~$20k/yr LTR est. from 2026 rental listings ($1,700-2,100/mo).",
             notes=("Zoned RSF-6 and listed as SFR: confirm legal nonconforming duplex. Confirm lender blends STR + LTR income. "
                    "Opex model applies STR costs to all income (conservative)."),
             url=Z + "5318-17th-St-W-Bradenton-FL-34207/45773289_zpid/"),
        dict(rank=3, address="2801 23rd Ave W (\"Beachin' Escape\")", city="Bradenton 34205", county="Manatee",
             type="SFR", specs="4/2 / 1,906 (PR 1,564) / 1968", list=645000, offer=600000, credit=0.03,
             gross=89000, basis="\"$89,000 gross vacation-rental revenue in 2025\"; \"$91,500 in booked 2026 revenue\"",
             flood="Unknown", pool="Y", hoa=0, profile="STR", last_sale="$474,000 (Mar 2024)", dom=23, highlight=True,
             notes=("Strongest track record. Appraisal risk: +36% vs 2024 purchase; public record 1,564 sf vs 1,906 marketed "
                    "(possible unpermitted space); contract fell through 9/27-9/29: ask why. Listed by Locals Property Mgmt."),
             url=Z + "2801-23rd-Ave-W-Bradenton-FL-34205/45755850_zpid/"),
        dict(rank=4, address="2245 Bahia Vista St (duplex)", city="Sarasota 34239", county="Sarasota", type="Duplex",
             specs="2/1 + 1/1 / 1,652 / 1936", list=475000, offer=455000, credit=0, gross=60000,
             basis="\"currently generates more than $60,000 annually\"; income + expenses available",
             flood="X", pool="N", hoa=0, profile="STR", last_sale="Listed $545k (May 2025) -> $475k", dom=78,
             notes="City of Sarasota 7-night minimum + annual registration/inspection. 1936 build: 4-point/insurance risk. 2025 roof. Land-value upside.",
             url=Z + "2245-Bahia-Vista-St-Sarasota-FL-34239/454647806_zpid/"),
        dict(rank=5, address="1415 36th St W (\"Bamboo Lagoon\")", city="Bradenton 34205", county="Manatee", type="SFR",
             specs="3/2 / 1,176 / 1972", list=474999, offer=474999, gross=54000,
             basis="\"$45,200 gross revenue YTD at 86% occupancy\"; 4.99 stars / 82 reviews; bookings convey",
             flood="X", pool="Y", hoa=0, profile="STR", last_sale="$349,000 (Dec 2024)", dom=18,
             income_note="$45.2k YTD through ~Sep annualized for SWFL seasonality (~80% of year) -> ~$54k.",
             notes="Appraisal risk: +36% vs Dec 2024 purchase. Pool likely added after purchase.",
             url=Z + "1415-36th-St-W-Bradenton-FL-34205/45748314_zpid/"),
        dict(rank=6, address="3409 18th Avenue Dr W", city="Bradenton 34205", county="Manatee", type="SFR",
             specs="3/2 / 1,644 / 1971", list=529000, offer=515000, gross=60000,
             basis="\"over $53,000 in bookings so far this year\"", flood="Unknown", pool="Y", hoa=0, profile="STR",
             last_sale="$525,000 (Jun 2024)", dom=58,
             income_note="$53k YTD bookings (Aug) annualized conservatively to ~$60k; bookings may include future stays.",
             notes="Two price cuts ($550k -> $529k). Roof 2024. City of Bradenton zoning (R1C): STR certificate required.",
             url=Z + "3409-18th-Avenue-Dr-W-Bradenton-FL-34205/45748742_zpid/"),
        dict(rank=7, address="2142 Waldemere St", city="Sarasota 34239", county="Sarasota", type="SFR",
             specs="3/2 / 1,170 / 1952", list=524900, offer=505000, gross=50157,
             basis="\"$50,157 gross rental revenue in 2025 and $55,323 in 2024\"; Jan-Apr ~$8k/mo",
             flood="X", pool="N", hoa=0, profile="STR", last_sale="$440,000 (Jun 2023)", dom=16,
             notes="City 7-night min. \"Previously operated\": confirm still active. Sold as-is; metal roof 2026.",
             url=Z + "2142-Waldemere-St-Sarasota-FL-34239/47620052_zpid/"),
        dict(rank=8, address="7405 12th Ave W", city="Bradenton 34209", county="Manatee", type="SFR",
             specs="2/2 / 1,469 / 1973", list=550000, offer=530000, gross=48000,
             basis="\"just under a year... nearly $45,000 in rental income\"", flood="Unknown", pool="Y", hoa=8,
             profile="STR", last_sale="$75,000 (2016)", dom=12,
             notes="<12 months history; 2BR. Solar 'majority owned': check lien on remainder.",
             url=Z + "7405-12th-Ave-W-Bradenton-FL-34209/45745183_zpid/"),
        dict(rank=9, address="2705 2nd Ave W", city="Bradenton 34205", county="Manatee", type="SFR",
             specs="2/1 / 1,198 / 1925", list=385000, offer=360000, gross=40000,
             basis="\"currently brings in $40K/year in gross income\"", flood="X", pool="N", hoa=0, profile="STR",
             last_sale="$240,000 (May 2021)", dom=214,
             notes="377 cumulative DOM: very negotiable. 1BA, 1925: insurance. City of Bradenton certificate.",
             url=Z + "2705-2nd-Ave-W-Bradenton-FL-34205/45741187_zpid/"),
        dict(rank=10, address="4711 Hollingsworth Ave (3 units)", city="Sarasota 34233", county="Sarasota",
             type="Triplex", specs="3 furnished units / 1,696 / 1981", list=655000, offer=655000, gross=102000,
             basis="\"averaging approximately $102,000 in annual revenue during 2024-2025\"; OM available",
             flood="Unknown", pool="N", hoa=0, profile="Seasonal", last_sale="$350,000 (Feb 2022)", dom=5,
             notes=("Unincorporated Sarasota County: <30-day banned in this zoning -> 30-day+ model. Zestimate ~$325k: "
                    "will NOT appraise for DSCR. Seller financing offered: pursue only on seller terms."),
             url=Z + "4711-Hollingsworth-Ave-Sarasota-FL-34233/47500769_zpid/"),
        dict(rank=11, address="4440 47th Ave W #102 (Shorewalk condo)", city="Bradenton 34210", county="Manatee",
             type="Condo", specs="2/2 / 1,174 / 1989", list=279000, offer=279000, gross=44000,
             basis="\"Gross rental earnings for January-June are $29,300\"; 4.96 stars", flood="Unknown", pool="N",
             hoa=477, profile="STR", last_sale="", dom=55,
             income_note="Jan-Jun $29.3k (peak half) annualized to ~$44k: verify T12.",
             notes="Cheapest entry. Shorewalk rental pool may be underwritten as condotel/non-warrantable (75% LTV, fewer lenders).",
             url=Z + "4440-47th-Ave-W-102-Bradenton-FL-34210/45764495_zpid/"),
        dict(rank=12, address="539 Forest Way (Cedars East, LBK)", city="Longboat Key 34228", county="Sarasota",
             type="Townhome", specs="2/2.5 / 1,440 / 1990", list=639000, offer=639000, gross=50000,
             basis="\"~$50,000 average annual rental payout revenue, after Airbnb and VRBO fees\"", flood="AE",
             pool="N", hoa=945, profile="STR", last_sale="", dom=27,
             notes="Shown as a reject example: $945/mo HOA + max 26 rentals/yr kills DSCR.",
             url=Z + "539-Forest-Way-539-Longboat-Key-FL-34228/465464113_zpid/"),
    ],
    "watchlist_title": "Operating STRs with no $ in listing: request T12 payouts (could become candidates)",
    "watchlist": [
        dict(address="8403 13th Ave NW", city="Bradenton 34209", price=619000,
             evidence="\"highly successful, income-generating VRBO\"; no rental restrictions; outside flood zone; 147 DOM, 3 cuts",
             url=Z + "8403-13th-Ave-NW-Bradenton-FL-34209/45787788_zpid/"),
        dict(address="926 Plum Tree Ln", city="Sarasota 34243 (Manatee Co.)", price=524900,
             evidence="\"active, successful vacation rental with daily rentals allowed\"; no HOA",
             url=Z + "926-Plum-Tree-Ln-Sarasota-FL-34243/45782588_zpid/"),
        dict(address="2714 42nd St W", city="Bradenton 34205", price=499000,
             evidence="4BR pool; \"currently operating as a successful short-term rental\"",
             url=Z + "2714-42nd-St-W-Bradenton-FL-34205/45757545_zpid/"),
        dict(address="120 60th St W", city="Bradenton 34209", price=450000,
             evidence="\"proven rental history available upon request\"; 7 price cuts ($549k -> $450k)",
             url=Z + "120-60th-St-W-Bradenton-FL-34209/45743370_zpid/"),
        dict(address="1214 21st St W", city="Bradenton 34205", price=625000,
             evidence="\"ESTABLISHED SUCCESSFUL SHORT-TERM RENTAL\"; salt pool + spa; impact windows",
             url=Z + "1214-21st-St-W-Bradenton-FL-34205/45749331_zpid/"),
        dict(address="6215 Rodgers Ave", city="Sarasota 34231", price=419999,
             evidence="\"proven Airbnb performer\"; near Siesta; 291 DOM. County 30-day rule applies -> seasonal only",
             url=Z + "6215-Rodgers-Ave-Sarasota-FL-34231/47517098_zpid/"),
        dict(address="1664 Lakeview Pl", city="Englewood 34223", price=374900,
             evidence="\"proven vacation rental\", pool, 1-month minimum (seasonal model)",
             url=Z + "1664-Lakeview-Pl-Englewood-FL-34223/47591926_zpid/"),
    ],
}

# Filled after the Pinellas sweep (see PINELLAS rows below).
PINELLAS = {
    "sheet": "Pinellas",
    "title": "Pinellas County: STR / Seasonal Candidates with Documented Income",
    "subtitle": f"Active as of {AS_OF}. Same method: Zillow keyword sweeps with full remarks + jurisdiction rules.",
    "scenario_rows": [],
    "rows": [],
    "watchlist_title": "Operating STRs with no $ in listing: request T12 payouts",
    "watchlist": [],
}

CANDIDATE_SHEETS = [MANATEE_SARASOTA, PINELLAS]

MARKETS = {}

RULES = {
    "headers": ["County", "Jurisdiction", "Min stay (SFH)", "Registration / cost", "Occupancy / other",
                "SFH nightly STR viable?", "Source"],
    "widths": [11, 26, 22, 34, 30, 16, 50],
    "rows": [
        ["Manatee", "Unincorporated (W. Bradenton, Cortez, Parrish, LWR-Manatee)", "None today",
         "No ordinance yet; draft: registration, inspections, ~$600/yr", "Pending ordinance", "Yes (rules pending)",
         "fox13news.com/news/manatee-county-short-term-rental-rules-cost"],
        ["Manatee", "City of Bradenton", "None found", "Certificate, Ord. 3093 (~$300 initial / $150 renewal)",
         "2/bedroom + 2 or 1 per 150 sf; max 12", "Yes", "cityofbradenton.com/vacarentals"],
        ["Manatee", "Anna Maria", "None found", "Annual, ~$104.78 per allowed occupant",
         "Lesser of 2/BR+2 or 8 total", "Yes (8-person cap)", "amisun.com"],
        ["Manatee", "Holmes Beach", "30 days in R-1/R-1AA; 7 nights R-2 to R-4", "2-yr certificate $545 ($782 proposed)",
         "2/BR or 6", "R-2+ only", "islandreal.com"],
        ["Manatee", "Bradenton Beach", "Not found", "TPLE lodging license (fee proposal pending)", "2/BR+2 discussed", "Yes", "islander.org"],
        ["Sarasota", "City of Sarasota", "7 nights", "Annual registration + annual reinspection; ~$500 new / $350 renewal",
         "2/BR+2, max 10", "Weekly only", "shumaker.com (Ord. 25-5560)"],
        ["Sarasota", "Unincorporated (Siesta Key SFH, Gulf Gate, Nokomis, Osprey, Englewood)", "30 days (UDC 124-131, pre-2011)",
         "-", "Only RMF zoning on barrier islands exempt", "No: seasonal only", "scgov.net code enforcement guide"],
        ["Sarasota/Manatee", "Longboat Key", "30 days (except tourism-zoned/grandfathered)", "$200 initial / $150 per 2 yrs",
         "-", "No", "Town of Longboat Key FAQ"],
        ["Sarasota", "Venice", "Transient use of SF districts restricted (Code 86-151)", "BTR", "-", "Likely no: verify",
         "lajollacpa.org (Costello STVR)"],
        ["Sarasota", "North Port", "None found", "State DBPR license + tax registration", "-", "Likely yes", "airdna.co"],
        ["Both", "Guest taxes", "-", "13% total: 6% tourist development + 7% sales tax. Manatee: owner remits TDT (no platform agreement).",
         "-", "-", "taxcollector.com; sarasotataxcollector.gov"],
    ],
}

CHECKLIST = [
    [1, "12-24 months of Airbnb/VRBO payout reports or PM owner statements",
     "Proves income for DSCR; gross must exclude 13% taxes; break out cleaning fees and platform-fee basis."],
    [2, "Tourist development tax filings (county tax collector)", "Independent cross-check of the payouts."],
    [3, "Future bookings ledger + whether bookings convey", "Day-one income; assign or refund deposits at closing."],
    [4, "FEMA flood zone + elevation certificate", "AE vs X changes flood premium by ~$3.5k/yr and DSCR by ~0.08x."],
    [5, "CLUE report + any Helene/Milton damage, repairs, permits", "FEMA 50% substantial-improvement rule; hidden flood history."],
    [6, "Current insurance declarations page (carrier, premium, wind/flood)", "Real premium vs model; insurability as an STR."],
    [7, "Local STR registration/certificate + any code violations", "Confirms legal operation; transfer requirements."],
    [8, "Furniture/equipment inventory list", "Conveys by contract (not financeable); value for tax basis."],
    [9, "Utility bills (12 months)", "Validates the $6k/yr fixed-cost assumption."],
    [10, "Property-manager / cleaner contacts and terms", "Continuity; co-host at 10-15% is what makes cash flow work."],
]

SOURCES = [
    ["Listings", "Zillow (igolaizola/zillow-scraper-ppe + maxcopell detail scraper via Apify): remarks, price + tax history", "https://www.zillow.com"],
    ["Listings", "Redfin listing pages (flood score, status, price history)", "https://www.redfin.com"],
    ["8404 43rd Ave Ter W", "STR newsletter feature (Sep 29, 2026)", "https://www.theoffersheet.com/p/85k-revenue-on-this-584k-bradenton-str"],
    ["STR benchmarks", "Rabbu market pages (T12 to Apr 2026)", "https://rabbu.com/airbnb-data/bradenton-fl"],
    ["STR benchmarks", "AirROI / Airbtics / AirDNA public market pages", "https://www.airroi.com"],
    ["DSCR terms", "Angel Oak STR program (80% at 720+, DSCR >= 1.0)", "https://angeloakms.com/programs/investor-cash-flow-mortgage-program/"],
    ["DSCR terms", "Deephaven STR income: 12-mo receipts net of mgmt", "https://deephavenmortgage.com/dscr-short-term-rental"],
    ["Rates", "Freddie Mac PMMS 30-yr 7.40% (10/15/2026)", "https://fred.stlouisfed.org/graph/?g=1XU7Y"],
    ["Insurance", "Citizens: flood required on wind policies by 1/1/2027", "https://news4jax.com/news/local/2025/09/16/flood-insurance-will-be-mandatory-for-most-citizens-property-insurance-policyholders-by-2027"],
    ["Market", "RASM Q3 2026 market report", "https://www.myrasm.com/q3-2026"],
    ["Tourism", "Manatee June 2026 bed tax record $4.61M", "https://www.islander.org/?p=85726"],
]
