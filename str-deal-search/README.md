# STR Deal Search — Manatee + Sarasota (DSCR buyer, ~$150k cash)

| File | What it is |
|------|------------|
| `2026-10-18-manatee-sarasota-dscr-str-shortlist.md` | Ranked shortlist, buying-power math, local STR rules, cost assumptions, diligence request list, next steps. |
| `dscr_model.py` | DSCR / cash-to-close / cash-flow model. All assumptions (rate, LTV, taxes, insurance, opex profiles) are constants at the top. |
| `candidates.json` | Inputs for the screened candidates (seller-stated income). Run: `python3 dscr_model.py candidates.json` |
| `STR_DSCR_Analysis.xlsx` | Live-formula workbook: Summary, Assumptions, Manatee-Sarasota, Pinellas, Other SWFL Listings, Monroe (Keys), Down Pmt Scenarios, PropertyRadar, Other SWFL Markets, STR Rules, Diligence Checklist, Sources. Edit blue cells; everything reflows. |
| `propertyradar_data.py` | Sanitized PropertyRadar pull (2026-10-19): 193 listed absentee-owned homes, property facts only (no owner names, mailing addresses or contact data). Feeds the PropertyRadar tab's required-rent screen. |
| `build_workbook.py` / `workbook_data.py` | Regenerates the workbook from the listing data (`python3 build_workbook.py`), then recalc with LibreOffice. |

Income figures are seller-stated from listing remarks as of 2026-10-18 and must be verified with platform payout reports.

PropertyRadar pull (report section 11): 193 credits used of 250. Nothing in it beats #1 (8404 43rd Ave Ter W). 930 SW 37th Ter, Cape Coral (licensed vacation rental, no $ figures) was added to the SWFL watch list.
