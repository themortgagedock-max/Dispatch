# Marina Vale Intelligence: Phase 1 Audit

**Date:** 2026-10-24
**Method:** Read only. Nothing was built, deployed, edited, sent, or deleted.
**Sources checked:**
- Code in four repos: `themortgagedock-site`, `tmd-claude-archive`, `mortgage-dock-platform`, `cat5-command`. The last one is a separate CAT 5 Marine business and is out of scope.
- The live GoHighLevel sub-account, read-only API.
- Google Drive docs, including the Oct 8 "MDP Phase 0 Audit".
- The Marina test harnesses, run locally with every external service mocked.

**This repo is public.** Contact names, CRM record IDs and exploit-level security details are deliberately left out. They were reported to Eli directly.

### What this audit could not reach
- **The live endpoint.** This session's network policy blocks `api.themortgagedock.com` and `themortgagedock.com`.
- **The Cloudflare dashboard.** The connector failed to connect.
- **Two docs outside reach.** `claude/TOOLS_INDEX.md` and `claude/SESSION_PROTOCOL.md` live in the Claude Project and on Eli's Mac. The Oct 8 audit notes that no SESSION_PROTOCOL doc exists in Drive.
- **GHL workflow definitions.** The GHL workflow API is disabled for this sub-account.

Anything below marked **UNVERIFIED** depends on one of these.

---

## Bottom line

1. **Realtor co-branded links already exist.**
   - How they work: `/chat?ref=CODE` looks up a Realtor record in KV and renders "Shared with you by [Name] · [Brokerage]". A secret-protected `/agents` API creates and deletes records.
   - The gap: there is no tracking, validation, admin UI, QR code or activation switch around them.
2. **Marina has no usage tracking at all.**
   - No events, no visitor ID, no UTM capture.
   - GA4 is not on the Marina chat page or on the `/marina/` landing page.
   - Today nobody can say how many people opened Marina, chatted, or looked up a property.
3. **The GHL integration works and is consent-gated (v1.4.x). It is producing nothing yet.**
   - 0 contacts carry the `marina-chat` tag, which every chat-captured lead gets.
   - No `ref-*` tag has ever been created, so no Realtor-attributed Marina lead has ever reached the CRM.
4. **No admin dashboard or Command Center is running.**
   - The earlier backend, `tmd-cockpit-api`, was switched off on 2026-10-13 after the Oct 8 audit found it had no auth.
   - Per the Oct 8 audit, a GHL funnel named "Command Center" exists. It was not opened here.
5. **Two compliance items gate the Realtor program.**
   - The public Realtor page says co-branded "Marina Pro" is "free for active Realtor partners." That needs a RESPA Section 8 review.
   - Marina's chat consent text does not match the website's TCPA consent text.
   - Details are in [PLAN.md](PLAN.md#5-security-and-compliance).
6. **Marina leads probably do not alert Eli. UNVERIFIED.**
   - The only published GHL workflow ("Website Lead - Notify Eli") appears to trigger on the `website-lead` tag, per the comments in the site's `lead.js`.
   - Marina never applies that tag.

---

## 1. Where Marina lives

| Component | Location | How it deploys |
|---|---|---|
| Chat backend and full-screen chat page | Cloudflare Worker `tmd-marina-chat`, route `api.themortgagedock.com/chat*` | Eli pastes a bundled JS file into the Cloudflare dashboard editor. No `wrangler.toml` exists in any repo. |
| Source of truth for the Worker | Bundle snapshots in `tmd-claude-archive/workers/tmd-marina-chat_v*.js` | The July `src/index.ts` on Eli's Mac is stale. Deploying it would undo the October fixes (per the v1.4.2 deploy notes). |
| Homepage floating widget | `themortgagedock-site/index.html` (Netlify) | Calls `POST https://api.themortgagedock.com/chat` directly |
| `/marina/` landing page | `themortgagedock-site/marina/index.html` | Links out to the full chat page |
| Realtor partner page and Marina Pro waitlist | `themortgagedock-site/realtor-partners/` | Waitlist form goes to the Netlify `lead.js` function, then GHL |
| Storage | One KV namespace, `MARINA_SESSIONS` | It holds sessions, rate-limit counters, Realtor records (`agent_ref:*`) and backfill state |
| Models | Opus for chat turns, Sonnet for inspection-report briefs | Set in code |

### Configuration names found in the Worker code
- **KV binding:** `MARINA_SESSIONS`.
- **Secrets:** `ANTHROPIC_API_KEY`, `GHL_API_KEY`, `ELEVENLABS_API_KEY`, `TAVILY_API_KEY`, `RENTCAST_API_KEY`, `CENSUS_API_KEY`, `MARINA_WEBHOOK_SECRET`.
- **Plain variables:** `GHL_LOCATION_ID`, `GHL_PIPELINE_ID`, `GHL_STAGE_ID`, `GHL_ASSIGNED_USER_ID`, `TMD_BACKFILL`.

These are names only. Whether each one is set was not checked.

### Routes
- `GET /chat`: the chat page, with optional `?ref=`.
- `POST /chat`: one chat turn.
- `POST /chat/tts`: voice, origin-checked and rate-limited.
- `GET|POST|DELETE /agents`: Realtor records, behind the shared secret.
- `GET /internal/conversations`: full transcripts, behind the shared secret.
- `POST /chat/ghl`: the GHL bot channel. The bot is off.
- `GET /chat/healthz`: reports the version.

## 2. Production version and the v1.4.0 fixes

| Version | Date | Evidence | Status |
|---|---|---|---|
| 1.3.0 | 2026-09-29 | Bundle pulled from Cloudflare 2026-10-12 (`mortgage-dock-platform/docs/marina-v1.4.0/`) | Superseded |
| 1.4.0 | 2026-10-13 | v1.4 README says it went live by dashboard paste and the live consent test passed 2026-10-15. Corroborated today: the `contact-consent-chat` tag it creates exists in GHL. | **Deployed** |
| 1.4.1 | 2026-10-15 | README: `/chat/healthz` reported 1.4.1, and lead owner assignment was checked live | Deployed |
| 1.4.2 | 2026-10-19 (steps), 2026-10-22 (snapshot) | Archive file `tmd-marina-chat_v1.4.2_LIVE_ROLLBACK_2026-10-22.js` | Live as of 2026-10-22 (going by the snapshot's name) |
| 1.5.1 | 2026-10-23 | Bundle and tests in the archive. No deploy record found. | **UNVERIFIED** |

**Answer:** the v1.4.0 fixes were deployed, and they carry forward unchanged into 1.4.2 and 1.5.1. Production is 1.4.2 or 1.5.1. Open `https://api.themortgagedock.com/chat/healthz` to settle it.

### Test results from this audit (local, all network mocked)
- The v1.4 harness has 47 checks. It passed 46 on both 1.4.2 and 1.5.1.
- The one failure is the harness's hardcoded check that healthz reports exactly "1.4.1", which is expected on newer versions.
- The 1.5.1 behavior tests passed 16 of 16.

### What 1.5.x adds over 1.4.2
- A `[[HANDOFF]]` marker the model emits to route a lead.
- A grounding guard that hedges hard figures when no tool ran.
- DockScore shows its band only, never the number.
- An honest message when the bridge database fails to load.

## 3. How Marina handles things today

### Chat sessions
- **Full chat page:**
  - The browser makes up the session ID (`web-<timestamp>-<6 random chars>`) and keeps it in `sessionStorage`. That makes it per tab: a new tab or a return visit starts a new session.
  - The server accepts whatever ID the client sends.
- **Homepage widget:** the server issues a UUID, which the browser keeps in `localStorage`. The same conversation continues across visits in that browser.
- **Server side, KV key `session:<id>` with a 90-day TTL:**
  - The last 40 messages, both visitor and Marina, in full.
  - A small extracted profile: boat specs, budget, target areas.
  - Consent state and lead status.
- **Implication:** the two entry points cannot be joined. Repeat visits are invisible on the chat page. Nothing counts sessions.

### Users
There are no accounts and no visitor ID. That fits the requirement that nobody has to register.

### Property searches
- **Three research tools:**
  - `get_property_intel`: address in; FEMA flood zone, an automated value estimate and an NFIP flood insurance range out.
  - `get_marine_intel`: address in; depth, bridges and DockScore out.
  - `match_boat_to_areas`: boat and region in; matching areas out.
- **News tool:** `search_current_news`.
- **Inspection reports:** attached PDFs, photos or Spectora links produce a "Property Intelligence Brief".
- **Gap:** none of this is recorded as a countable event. Addresses exist only inside the stored transcript. The property tool already derives a ZIP code, which is useful for counting by area without keeping street addresses.

### Realtor branding
- **How a branded page is built:** `GET /chat?ref=CODE` resolves `agent_ref:<code>` in KV to `{code, name, brokerage, phone}`. That record is injected into the page:
  - a "Shared with you by" banner;
  - a greeting that names the Realtor;
  - inspection briefs addressed "Prepared for [Realtor]".
- **Prompt rule:** the model is told to "never refer the buyer to a different agent."
- **Managing records:** `/agents` create, list and delete need the shared secret (fixed in v1.4.0). There is no UI. Records are created by API call.
- **Gaps:**
  - The browser sends the raw `?ref=` value even when no Realtor record matches it. The server stores it, so any typed code becomes a `ref-<code>` tag in GHL.
  - There is no active or inactive status and no photo or brand fields.
  - Codes are chosen by hand, so they are guessable.
  - Attribution is kept per conversation only, using the first `ref` seen in it. Nothing stops a later conversation from carrying a different one.
  - The homepage widget never sends `ref`.
- **Unknown:** how many Realtor records exist in KV. Reading them needs the secret, so it was not checked.

### Lead capture (v1.4.x and later)
- **Trigger:** a visitor types an email or phone number. Marina appends the permission question.
- **On YES:**
  - GHL `contacts/upsert`, which de-duplicates on email or phone.
  - Separate tag call: `marina-chat`, `marina_vale_lead`, `auto-capture`, `contact-consent-chat`, plus `ref-<code>` when present.
  - A note with the consent record and up to 3,500 characters of the visitor's own messages.
  - For new contacts only, an opportunity in Main Lead Pipeline / New Lead assigned to Eli.
  - Retries with timeouts.
- **On NO:** nothing is sent, and Marina does not ask again.
- **Missing:**
  - Structured offers: a report request, financing help, a Realtor-branded review.
  - Any campaign or source data on the lead.
  - The `page` field, which neither front end sends.
- **Handoff:** detecting one only sets a flag in KV. For website chats it is never sent to GHL.

## 4. Command Center and admin system

| Asset | Status (source) |
|---|---|
| Mortgage Dock Command Center | **Not built.** Every planning doc agrees (Oct 8 audit). |
| `tmd-cockpit-api` | Earlier Command Center backend. It had no auth. Switched off 2026-10-13: no domain, workers.dev URL disabled (v1.4 README). |
| GHL funnel named "Command Center" with a `/dashboard` page | Exists per the Oct 8 audit. Not opened here. |
| GHL custom menu links | Can open an outside page inside the GHL sidebar on the white-label domain (Oct 8 audit). **Untested.** |
| `tmd-portal-dashboard`, `tmd-velocity-dashboard` | Partial, per the Oct 8 audit: one hardcoded Realtor and no login; a password page with a pipeline bug. Reference only. |
| `mortgage-dock-platform` | Static Cloudflare app for buyer intelligence (MDBI Stage 0), with a brand stylesheet. Not an admin system. Its "no build step, tested shared code" pattern is worth copying. |

## 5. GoHighLevel (verified live today, read only)

- **Pipelines:**
  - Main Lead Pipeline, 14 stages: New Lead, Contacted, App Sent, App Received, Pre-Approved, Under Contract, Processing, Underwriting, Conditional Approval, Clear to Close, Closed / Funded, Post-Close Nurture, Opt-out, Long Term Nurture.
  - Referral Partners, 6 stages: New Partner Lead, Intro Call Set, Met / Pitched, Active Partner, Sending Deals, Dormant.
- **Contact custom fields:** about 80.
  - Reusable: Lead Source, Property Area, Market Area, Loan Interest, Buyer Agent Name / Email / Phone, Agent Updates OK, Brokerage Name, Realtor Photo URL.
  - Missing: no first-touch or UTM fields, no referring-Realtor field, no Marina activity fields.
  - Stale code path: the Worker's GHL-bot path writes `marina_scenario` and `referring_agent` custom fields that do not exist. That path is unused because the bot is off.
- **Tags present:** `marina-chat`, `marina_vale_lead`, `auto-capture`, `contact-consent-chat`, `marina-pro-waitlist`, `website-lead`, `source-website`, `type-referral-partner`, `sms-consent-yes` / `-unknown`, `loan-*` interest tags, `partner-*`. **No `ref-*` tag exists.**
- **Contact counts:**

  | Tag | Contacts | Notes |
  |---|---|---|
  | `marina-chat` | **0** | |
  | `marina_vale_lead` | 1 | Entered by hand, not from the chat |
  | `marina-pro-waitlist` | 1 | A Realtor |
  | `website-lead` | 4 | |

- **Native attribution:**
  - GHL fills `attributionSource` (session source, UTM, click IDs, GA client ID) for its own forms and calendars.
  - Contacts created through the API, which is how Marina and `lead.js` create them, have it empty.
  - So Marina cannot lean on it and has to write attribution explicitly.
- **Workflows:**
  - The API returns `WORKFLOW_API_NOT_ENABLED_FOR_LOCATION`, so workflows cannot be read or created by API.
  - Per the Oct 3 Marketing OS audit, 1 of 23 is published: "Website Lead - Notify Eli". Its trigger could not be checked (see bottom line item 6).
- **Not checked:** webhooks and custom menu links (no read API).

### The second lead pipe (website forms)
- **What it does:**
  - `themortgagedock-site/netlify/functions/lead.js` serves site forms, calculator lead gates and the Realtor waitlist.
  - It upserts the contact and tags it (`website-lead`, `source-website`, a type tag, a `loan-*` tag, a consent tag).
  - It writes a note with the TCPA v3 consent record and opens an opportunity in the Main or Referral Partners pipeline.
- **Tags differ from Marina's.** Joint reporting needs one shared source taxonomy.
- **Correction to the Oct 8 audit:** that audit said `lead.js` used the retired GHL location. The current code uses the new one, so that finding is out of date.
- **Out of scope:** two security items in `lead.js` were found and reported to Eli privately.

## 6. Website and analytics

- **Hosting:** Netlify static site, auto-deploys on push to `themortgagedock-site`.
- **GA4:** on about 100 pages.
  - Click events come from `data-event` attributes: `cta_click`, `marina_open`, `lead_submit` and others.
  - Missing from: the `/marina/` page and the Worker-served chat page. **Neither has any analytics.**
- **Meta pixel:** only on the AI Field Guide page, mapping `lead_submit` to Lead.
- **UTM capture:** only the condo-financing landing page captures UTMs (hidden fields into the GHL note). No other page captures them, and none are passed to Marina. The Marketing OS content calendar puts UTMs on every post, and they are lost once a visitor reaches Marina.
- **Privacy policy:** mentions Marina, GA and cookies. It also says "By submitting your phone number through our forms or chat, you consent to receive transactional and marketing text messages." That is a compliance flag (see PLAN).

## 7. Existing tracking, attribution, referral and event logging

| Capability | Status | Where |
|---|---|---|
| Marina event logging | **Missing** | |
| Anonymous visitor ID | **Missing** | The chat page has per-tab session IDs only |
| UTM / campaign capture for Marina | **Missing** | One landing page captures UTMs for its own form only |
| Realtor referral codes | **Partial** | KV `agent_ref:*` plus `ref-<code>` tags. Not validated, no status, can be spoofed. |
| Referral ownership protection | **Missing** | First `ref` per conversation only |
| Realtor link activity metrics | **Missing** | |
| Site click analytics | **Partial** | GA4 `data-event` on site pages, not on Marina pages |
| Conversation review | **Partial** | `/internal/conversations` returns full transcripts behind the shared secret. `tmd-marina-learning-loop` is broken per the Oct 8 audit. |
| Lead attribution in GHL | **Partial** | The `source` string and a `ref-` tag |
| Funded-loan outcomes | **Exists in GHL, not linked** | Pipeline stages exist but nothing ties them back to Marina sessions or Realtors |
| Admin dashboard | **Missing** | |
| QR code generation | **Missing** | The existing `card/qr-card.png` is a static image |

## 8. Required features: exists / partial / missing

| Requirement (from the brief) | Status |
|---|---|
| A. UTM and campaign links, first-touch kept, later touches logged | Missing |
| B. Unique, persistent Realtor identifier | Partial (a KV code, hand-picked, no status) |
| B. Link opens Marina with approved co-branding | Partial (name and brokerage banner; no approval step, no photo) |
| B. Per-Realtor visits, unique visitors, chats, properties, repeats, contacts, financing, opportunities | Missing |
| B. Ownership cannot be changed by editing URL parameters | Missing |
| C. The nine named events | Missing (no event store) |
| C. Privacy-conscious anonymous ID | Missing |
| C. No storing whole transcripts unnecessarily | **Conflict.** Full transcripts already sit in KV for 90 days, and up to 3,500 characters of visitor text is copied into the GHL note. |
| D. No forced registration | Exists |
| D. Value-first offers (report, financing, Realtor review, licensed professional) | Missing (only the typed-contact consent gate exists) |
| D. Consent and disclosures | Exists for chat (v1.4). The consent text differs from the website's. |
| D. Source, campaign and Realtor captured on the lead | Partial (Realtor code only) |
| E. GHL create or update without duplicates | Exists (upsert) |
| E. Source and interest tags | Partial (Realtor tag only; no source or interest tags from chat) |
| E. Realtor attribution field | Missing |
| E. Opportunity in the right pipeline | Exists for new consented contacts |
| E. No unsolicited messages | Exists (the code sends nothing; tag-triggered workflows need checking) |
| Dashboard (overview, Realtor, campaign, property intelligence) | Missing |
| Realtor onboarding workflow (profile, branding, link, QR, preview, activate, review) | Missing (raw API only) |
