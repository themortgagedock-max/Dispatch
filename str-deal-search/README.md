# STR Deal Search — Manatee + Sarasota (DSCR buyer, ~$150k cash)

| File | What it is |
|------|------------|
| `2026-10-18-manatee-sarasota-dscr-str-shortlist.md` | Ranked shortlist, buying-power math, local STR rules, cost assumptions, diligence request list, next steps. |
| `dscr_model.py` | DSCR / cash-to-close / cash-flow model. All assumptions (rate, LTV, taxes, insurance, opex profiles) are constants at the top. |
| `candidates.json` | Inputs for the screened candidates (seller-stated income). Run: `python3 dscr_model.py candidates.json` |
| `STR_DSCR_Analysis.xlsx` | Live-formula workbook: Summary, Assumptions, Manatee-Sarasota, Pinellas, Other SWFL Listings, Down Pmt Scenarios, Other SWFL Markets, STR Rules, Diligence Checklist, Sources. Edit blue cells; everything reflows. |
| `build_workbook.py` / `workbook_data.py` | Regenerates the workbook from the listing data (`python3 build_workbook.py`), then recalc with LibreOffice. |

Income figures are seller-stated from listing remarks as of 2026-10-18 and must be verified with platform payout reports.
