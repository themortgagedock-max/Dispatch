# Marina Vale: Copy Deck (verified 2026-10-12)

Every claim below was checked against the live Marina code (`tmd-marina-chat` v1.3.0,
deployed 2026-09-29). It matches the copy on themortgagedock.com/marina/ after
themortgagedock-max/themortgagedock-site PR #14 merges. Use these blocks for Google Business
Profile, social bios, email signatures, partner one-pagers, and anything else off the site.

House rules applied: no em or en dashes, "Eli Sanderlin" (never "Eli O."), no rate promises,
"not a commitment to lend" near anything financial.

---

## 1. One-liner (bio, meta description, ~150 characters)

> Marina Vale is a free AI mortgage concierge for coastal Florida. Flood zones, flood insurance
> budgets, boat and bridge data, inspection reports, and financing, answered 24/7.

## 2. Short bio (~50 words)

> Meet Marina Vale, The Mortgage Dock's AI mortgage concierge. Give her an address and she pulls
> the flood zone, a flood insurance budget from real local policies, and the tide, depth, and
> bridge data that matters if you own a boat. She reads inspection reports, answers 24/7, and
> hands you to Eli Sanderlin when you are ready.

## 3. What she can do today

**Live lookups by address**
- FEMA flood zone, special flood hazard area status, and base flood elevation
- Flood insurance budget range from actual NFIP policies in that ZIP code and zone (a budget, not a quote)
- Property basics (beds, baths, square feet, year built, last sale) and an estimated value range
- NOAA tide predictions (48 hours), charted depths, and Army Corps maintained channel depth
- The lowest fixed bridge between the dock and open water, checked against your boat's air draft
- DockScore: a 0 to 100 rating of how well a waterfront property works for boating
- Boat-first search: ranks waterfront areas in Florida, the Carolinas, and the Chesapeake by bridge clearance and depth

**Documents, photos, voice**
- Reads uploaded PDFs, inspection report links, and photos, then writes a Property Intelligence Brief
- Voice: talk to her in a supported browser such as Chrome; she answers out loud
- Save any longer answer as a PDF or a clean client copy to share
- Add to your phone's home screen and she opens like an app

**Knowledge**
- Coastal insurance: wind and flood as separate policies, Citizens, Risk Rating 2.0, elevation certificates
- Condo and HOA risk: Milestone Inspections, SIRS, special assessments, warrantability
- Loan program fit: conventional, jumbo, DSCR, bank statement, foreign national, VA, HELOC, non-warrantable condo
- Investor math: how DSCR loans qualify, what short term rental income lenders count

**Handoff**
- Gives a link to book 15 minutes with Eli when a question needs a licensed human

## 4. For Realtor partners

> Realtor partners get a personal Marina link. Buyers who open it see your name and brokerage,
> Marina greets them on your behalf, and any Property Intelligence Brief she writes for them is
> prepared for you. She never refers your buyer to another agent. Marina Pro, a fully custom
> version with your face, your voice, and your listings, is coming. Join the waitlist at
> themortgagedock.com/realtor-partners/.

## 5. Disclaimer (use near any CTA)

> Marina Vale is an AI assistant providing general education only. She is not a licensed
> mortgage loan originator. Nothing she says is a commitment to lend, an offer of credit, or a
> quote of rates, terms, or approval. Flood insurance figures are planning budgets, not quotes.
> Eli Sanderlin, NMLS #1983384. Coast2Coast Mortgage, LLC, NMLS #376205. Equal Housing Lender.

---

## Do NOT claim (not live as of 2026-10-12)

| Claim | Reality |
|---|---|
| Spanish / bilingual | English only. No Spanish in the prompt or voice settings. |
| SMS, Facebook, Instagram | Website chat only. The GHL Conversation AI bot is switched off. |
| Rent estimates | Not wired. Only RentCast property and value endpoints are called. |
| Coastal Risk Score inside Marina | Mentioned in her prompt, no code behind it. |
| Books appointments | Gives a static `/strategy` booking link, no calendar integration. |
| "Texts Eli a summary" | No SMS code exists, even though her script offers it. |
| Remembers you next visit | Chat page memory is per browser tab. |
| "8 clarity tools" (Coastal Risk Clarity Report, Condo Approval Scan, etc.) | Not part of Marina. These came from planning docs, not the live product. |
