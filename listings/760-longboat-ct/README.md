# 760 Longboat Ct, Longboat Key, FL 34228: listing microsite

Co-branded property site for **Jesse Griffin (Century 21 Beggins Enterprises)**, with financing by
**Eli Sanderlin (The Mortgage Dock)**. Listed $840,000 on 2026-09-23.

| File | What it is |
|---|---|
| `page.html` | Single source. Artifact-ready fragment (no doctype/head/body); published to claude.ai as-is. |
| `index.html` | Built, deployable full document (Netlify, Cloudflare Pages, any static host). **Do not hand-edit.** Run `python3 build.py`. |
| `build.py` | Wraps `page.html` into `index.html` and adds OG/share meta. |
| `qa.py` | TMD pre-ship sweep: dashes, banned words, phone, name form, NMLS IDs, EHO, stale limits, JSON-LD, FAQ schema exact match. |

Edit `page.html`, then `python3 build.py && python3 qa.py`.

## What's on the page

- **All-in monthly cost** (hero + calculator): P&I, post-sale property tax, wind/HO, flood, PMI/dues. Conforming vs jumbo flag against the 2026 limit; Florida doc stamp (0.35%) and intangible (0.2%) taxes on the note.
- **Property tax at the buyer's price**: the seller's 2025 bill ($773) vs the post-sale reset; homestead (2026 indexed $51,411), second home, Save Our Homes portability, and an **Amendment 3 (Nov 3, 2026 ballot)** toggle with the Dec 31, 2026 residency split. Full millage table.
- **Flood + wind planning ranges** driven by elevation vs BFE, roof age, hip roof, and opening protection.
- **Before-you-offer checklist** (saved per browser) with a **Copy checklist** button that copies the whole list as a ready-to-send email to the buyer's agent, including their live estimates and `[done]` marks, plus an "Open in email" shortcut and a preview. North End Village facts, verified agent and lender license blocks, FAQ with matching FAQPage schema, and a full compliance footer.
- **Copy my scenario** button: buyer copies their numbers to send to Eli. All finance CTAs point to `themortgagedock.com/strategy` with `utm_campaign=760_longboat_ct`.

## Data and verification log (retrieved 2026-10-22)

| Fact | Value | Source |
|---|---|---|
| Parcel / county | 77955-0000-3, Manatee, tax area LK | PropertyRadar (Manatee PAO roll) |
| Beds / baths / sq ft / lot | 3 / 2 / 1,242 / 9,409 (88 ft frontage) | PropertyRadar, ModelMatch |
| Year built / construction | 1920, wood frame, 1 story, gable/hip roof | PropertyRadar |
| Flood | Zone AE, FIRM 12081C0291F, eff. 2021-08-10 | PropertyRadar (FEMA NFHL) |
| 2025 roll | Land $419,125, improvements $15, assessed $419,140, taxes $773 | PropertyRadar |
| Listing | Active, $840,000, listed 2026-09-23, agent Jesse Griffin | ModelMatch MLS feed, PropertyRadar |
| Jesse Griffin license | SL3081650, Sales Associate, Current/Active to 03/31/2028, licensed 04/07/2004, PLLC qual. 08/19/2024 | Florida DBPR, direct lookup |
| Brokerage | Beggins Enterprises Inc d/b/a Century 21 Beggins Enterprises, CQ271428; employed since 06/11/2014 | Florida DBPR |
| LBK branch | BO2026009, 7000 Gulf of Mexico Dr, Longboat Key 34228 | Florida DBPR |
| Jesse contact | (941) 822-6165, jessegriffin@c21be.com | ModelMatch agent record |
| Millage (2025 adopted, Bayside) | 14.8362 total = school 6.3040 + non-school 8.5322 | Manatee PAO 2025 Final Adopted Millage; FLDOE; SWFWMD; Longboat Observer |
| Homestead 2026 | $25,000 + $26,411 indexed = $51,411 | FL Dept. of Revenue (Amendment 5 CPI adjustment) |
| Amendment 3 | $150k (2027) / $250k (2028+) non-school for FL residents by 12/31/2026; ~$50k for 4 yrs for later arrivals; non-homestead cap 10% to 5%; needs 60% | FL House staff analysis CS/HJR 1F; Manatee/Pinellas PAO FAQs |
| Conforming limit 2026 | $832,750 (Manatee is baseline) | FHFA (via secondary sources) |
| Flood benchmark | Manatee Zone AE NFIP avg $1,614/yr | OpenFEMA policy snapshot, Aug 2026 |

### Not verified, confirm before wide distribution

1. **Bedrooms.** County says 3; one portal's listing text says 2 + Murphy bed. Page shows 3 with a footnote.
2. **Jesse's phone** (941) 822-6165 is from ModelMatch. Confirm it's the number Jesse wants published.
3. **Tax district.** Bayside is inferred from location (east of Gulf of Mexico Dr). Confirm on the TRIM notice.
4. **Non-ad valorem amount.** Uses the $773 total bill as a ceiling. Replace with the actual line items from the tax bill.
5. **Insurance ranges** are modeled planning ranges, not quotes. Swap in real quotes once the Elevation Certificate is in hand.
6. **Listing photos.** None included. Portal copies (Realtor.com, Zolo, Zillow) are copyrighted and MLS-licensed, so get the originals from Jesse (MLS photo download or Dropbox). Put them in `photos/`, add `{src, alt}` entries to `PHOTOS` in `page.html`, and the gallery appears automatically. For the artifact, publish the photos as supporting files alongside the page.

### Kept off the page on purpose

Owner names, loan balances, and the 2019 sale price ($460,000) are not on the page. They're in public records but
not something a listing partner wants on the listing. The 2025 roll shows **$15 in improvement value**, and county
records list the exterior wall as **"asbestos frame."** Both are worth raising privately with Jesse: was the structure
storm-damaged in 2024, what did the restoration replace, and is there a substantial-improvement history with the Town?

## Compliance

- Florida Rule 61J2-10.025: the registered brokerage name appears with the agent name on every agent block and in the footer. Century 21 franchise line "Each office is independently owned and operated" included.
- NMLS #1983384 (Eli) and #376205 (Coast2Coast Mortgage, LLC), Equal Housing Opportunity mark, "not a commitment to lend", and the freedom-to-choose-a-lender line are all present. The REALTOR mark isn't used (membership unverified).
- Payment figures are labeled as examples, not offers of credit, rate quotes, APRs, or Loan Estimates.
- **RESPA Section 8:** a lender-built marketing site for a referral partner's listing can be treated as a "thing of value." Before this goes live under Jesse's name, either split the cost proportionally (documented co-marketing agreement) or keep it clearly positioned as The Mortgage Dock's own advertising.

## Deploy

- **Preview:** published as a private claude.ai artifact (link in the PR).
- **Public:** drop `index.html` on any static host. Suggested: a new Cloudflare Pages project (e.g. `760longboat.themortgagedock.com`) or a path on the main site via `~/tmd-deploy` per the `tmd-site-deploy` skill. After deploy, verify with `curl` + `grep -c "760 Longboat"`, not a cached fetch.
