# Marina Vale Intelligence: Recommended Plan

**Status:** PROPOSAL. Nothing in this plan has been built or deployed. It needs Eli's approval first.
**Read first:** [AUDIT.md](AUDIT.md). Every "exists" claim below is backed there.

**The goal:** measure the full journey: Social post → Marina → property research → identified lead → Realtor referral → mortgage opportunity. Do it with real recorded events, inside the systems that already exist.

---

## 0. Decisions Eli needs to make before the build

Each item has a recommendation. Nothing in Phase 1 waits on items 1 and 2; Phase 4 activation does.

| # | Decision | Recommendation | Why |
|---|---|---|---|
| 1 | Send the Realtor co-branding arrangement to Coast2Coast compliance. This covers Marina Pro ("free for active Realtor partners" on the public page) and the existing `?ref=` co-branding. | **Yes, before onboarding any new Realtor.** In the meantime, ship Realtor links as tracking links with only the existing "Shared with you by" line. | A free co-branded lead tool given to referral sources, and conditioned on being "active", is the kind of arrangement RESPA Section 8 reviews target. This is the "genuinely questionable" case C2C policy §11 says to escalate. |
| 2 | Align Marina's chat consent text with the website's TCPA consent (`tcpa-v3-2026-10`). | **Yes,** with C2C sign-off on the wording. | The chat text does not mention automated technology or the texting provider. Any automated SMS workflow that fires on a Marina tag would then rest on weaker consent than the website collects. |
| 3 | Realtor ownership rule. | **First valid Realtor link wins for 90 days.** Later Realtor links are logged and shown in an "attribution conflicts" list for Eli. Only Eli can reassign, and every reassignment is logged. | Stops poaching and URL tampering, and keeps people in charge of disputes. |
| 4 | Let Marina leads trigger the existing "Website Lead - Notify Eli" alert. | **Yes,** after Eli confirms in the GHL UI that the workflow only notifies Eli and sends nothing to the lead. Then Marina also applies `website-lead`. | Today a consented Marina lead can sit in GHL with no alert (AUDIT bottom line 6). |
| 5 | Where the dashboard lives. | **A small separate Worker, `tmd-marina-admin`,** behind Cloudflare Access, opened from a GHL custom menu link labelled "Command Center". | No new platform, and no admin code inside the public chat Worker. It also uses the GHL sidebar link the Oct 8 audit found is available. |
| 6 | Existing transcript storage: full transcripts in KV for 90 days, plus up to 3,500 characters of visitor text in the GHL note. | **Leave it unchanged in this project.** Decide separately. | Changing it affects Marina's memory and Eli's follow-up context. This project only promises that the new tracking stores no message text. |

---

## 1. What can be reused

| Existing piece | Reuse it for |
|---|---|
| `tmd-marina-chat` Worker, v1.5.1 bundle (passes 46/46 functional and 16/16 behavior checks) | The host for server-side events, attribution capture and Realtor link validation. It is extended, not rewritten. |
| `MARINA_SESSIONS` KV and `tmdRateLimited()` | Rate limiting the new public event endpoint. The KV `agent_ref:*` records stay as a legacy fallback. |
| `resolveAgent()`, `renderMarinaPage()` and the `/*__AGENT_JSON__*/` injection | Co-branding rendering. The record source moves from KV to D1 with a KV fallback. The page markup is untouched. |
| `tmdCaptureWebsiteLead()`: upsert, separate tag call, note, opportunity, owner | The lead path for chat-typed contacts **and** the new offer form. It gains attribution fields. Consent logic stays exactly as it is. |
| `tmdConsentReply()`, consent versioning, consent note | Unchanged. Offer forms reuse the same consent record format. |
| `tmdOriginAllowed()` | Origin checks on the event endpoint and the offer form. |
| `tmdIsTestLead()`, `TMD_OWN_PHONES`, `TMD_OWN_EMAILS` | Flagging internal and test traffic so it is excluded from metrics. |
| The `[[HANDOFF]]` marker (v1.5.x) | The trigger for `financing_requested`. |
| The ZIP derived inside `fetchPropertyIntel()` | Property location rollups without storing street addresses. |
| Test harness `mortgage-dock-platform/docs/marina-v1.4.0/test_marina.mjs`, which mocks Anthropic, GHL, ElevenLabs and KV | The regression suite. It is extended with a mock D1 and the new tests. |
| GHL Main Lead Pipeline and Referral Partners pipeline | Opportunities and the Realtor's own CRM record. No new pipelines. |
| GHL fields Property Area, Loan Interest, Brokerage Name, Realtor Photo URL, Agent Updates OK | Reused where they fit. Only Marina-specific attribution fields are new. |
| Site `fireEvent()` / `data-event` click tracking and GA4 | Kept for site-level analytics. Marina's numbers come from D1. GA4 is a cross-check, not the source of truth. |
| `lead.js` source and tag conventions (`source-*`, `loan-*`, `sms-consent-*`) | One shared taxonomy, so website-form and Marina leads report together. |
| `mortgage-dock-platform/assets/brand.css` | Dashboard styling. Copied, not forked. |
| Archive snapshot convention `tmd-marina-chat_vX_LIVE_ROLLBACK_<date>.js` and the dashboard-paste deploy | Unchanged deploy and rollback path. |
| D1, already used elsewhere in the Cloudflare account (Oct 8 audit) | The analytics store. No new vendor. |

**Considered and not chosen:**
- **GA4 alone.** GA4 cannot see server-side tool calls, cannot enforce Realtor ownership, and cannot be joined to GHL leads per Realtor without sending personal data to Google.
- **PostHog, Segment or Mixpanel.** Each is a new vendor and a new data processor, which the brief rules out without a reason. They are not needed at this volume.
- **Workers Analytics Engine.** Good for very high-volume time series. It has no updates or joins, and this data needs both (Realtors, leads, outcomes).
- **KV.** It cannot aggregate.

---

## 2. Missing functionality (the build list)

1. An anonymous first-party visitor ID and a server-computed analytics session (30 minutes of inactivity ends a session).
2. UTM, campaign code and referrer capture on both entry points, with first touch kept and every later touch logged.
3. Server-side Realtor link validation (exists and active) and first-touch Realtor ownership.
4. An event store and the nine required events, plus a few supporting ones (message count, offers, topic labels).
5. Bot and internal-traffic flags, with de-duplication rules that keep counts honest.
6. Value-first lead offers in the chat UI, plus a short consented form.
7. GHL attribution fields and tags, a no-duplicate opportunity rule, and an hourly read-only outcome sync.
8. The `tmd-marina-admin` dashboard: Overview, Realtors, Campaigns, Property Intelligence.
9. Realtor onboarding: profile, approved branding, generated link, QR code, preview, activate or deactivate, activity view, compliance gate.
10. A link builder for campaign links (LinkedIn, Facebook, email, SMS, QR, Realtor site, paid).
11. Website patch: the homepage widget and `/marina/` pass attribution to Marina, and `/marina/` gets GA4.
12. A privacy policy update for first-party analytics, plus an opt-out that honors Global Privacy Control.

---

## 3. Recommended architecture

```
 LinkedIn / Facebook / email / SMS / QR / Realtor site / paid / direct
        │  links carry ?c=<campaign> and/or UTM, and ?ref=<realtor> for Realtor links
        ▼
 themortgagedock.com (Netlify)                 api.themortgagedock.com/chat
   homepage widget, /marina/ ─── POST /chat ──► tmd-marina-chat Worker (existing)
   (sends first-touch UTM + referrer once)        │ validates ref, sets visitor cookie,
                                                  │ writes server-side events
                                                  ├─► KV MARINA_SESSIONS (existing, unchanged)
                                                  ├─► D1 tmd_marina_intel (NEW)
                                                  └─► GHL upsert/tags/note/opportunity (existing + attribution)

 tmd-marina-admin Worker (NEW, behind Cloudflare Access)
   dashboard · Realtor onboarding · link + QR builder
   ├─ reads/writes D1 tmd_marina_intel (same database)
   ├─ hourly cron: GHL opportunities (read-only token) → D1 lead_outcomes
   └─ opened from a GHL custom menu link "Command Center"
```

### 3.1 Identity (pseudonymous; never "who")
- **Visitor ID `tmd_vid`.**
  - A random UUID in a first-party cookie set by the Worker on `.themortgagedock.com`: `Secure; HttpOnly; SameSite=Lax; Max-Age` of 13 months.
  - The chat page sends it automatically. The homepage widget sends it once it calls `/chat` with `credentials: 'include'`. For that, the Worker echoes allow-listed origins with `Access-Control-Allow-Credentials: true`. Other origins keep `*` without credentials, so unknown embeds are not broken.
  - If the cookie is absent or blocked, the client may send a `localStorage` ID instead, and the session is tagged `id_source=client`.
- **Analytics session.**
  - Computed server-side per visitor: a new session starts after 30 minutes with no events.
  - This is separate from the existing conversation ID, which keeps working unchanged for Marina's memory.
- **What the dashboard can honestly say:** "browsers", not "people".
  - One person on two devices counts as 2.
  - Cleared cookies start a new visitor.
  - Safari can cap cookie lifetimes, so repeat visits on iPhones will be undercounted.
  - The dashboard states these limits on screen.
- **Never used:** fingerprinting, IP storage in D1, cross-site identifiers, or "identifying" anonymous visitors. A visitor becomes a named person only by voluntarily submitting contact details with consent.
- **Global Privacy Control.** With `Sec-GPC: 1` or the site opt-out cookie present:
  - no visitor cookie is set;
  - events are recorded against the session only;
  - the session is marked `opted_out`, and the dashboard counts it in sessions but not in unique visitors.

### 3.2 Campaign attribution
- **Captured on the first request of each analytics session:**
  - allow-listed parameters `c`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`;
  - whether `gclid`, `fbclid` or `li_fat_id` is present (yes/no only; the values are never stored);
  - the referrer **host only**;
  - the landing path without its query string.
- **Homepage widget:** it reads these on the visitor's *landing* page on themortgagedock.com, keeps them in `sessionStorage`, and sends them with the first chat message. Without this, a visitor who lands from LinkedIn and opens the widget later would look "direct".
- **First touch** is written once per visitor and never overwritten. **Every** session's touch is stored, which gives last touch and the full path.
- **Channel derivation (first match wins):**
  1. `c=<code>`: the campaign record's channel, from the link builder. Preferred, because it ends UTM typos.
  2. `utm_medium`:
     - `qr` → qr
     - `sms` or `text` → sms
     - `email` → email
     - `cpc`, `ppc`, `paid` or `paid_social` → paid
     - `social` → linkedin, facebook or other_social, by `utm_source`
  3. Referrer host:
     - linkedin.com or lnkd.in → linkedin
     - facebook.com, fb.me or l.facebook.com → facebook
     - google, bing, duckduckgo → organic_search
     - a registered Realtor website domain → realtor_site
     - our own domains → internal (see the homepage handling above)
     - anything else → referral
  4. Nothing → direct.
- **Known limit:** social in-app browsers often strip referrers, so untagged social clicks land in "direct". The link builder makes tagging the default.

### 3.3 Realtor referral links and ownership
- **Link format:** `https://api.themortgagedock.com/chat?ref=<code>`, kept so every existing link keeps working.
  - New codes are generated by the server, for example `vale-k7q2`: a slug plus 4 random characters, so they cannot be guessed or enumerated.
  - Legacy hand-picked codes keep rendering as they do today until Eli reviews them.
- **Validation happens on the server for every request.**
  - **Valid code:** the code exists and its status is `active`. That means branding plus attribution.
  - **Inactive or unknown code:** generic Marina, no `ref-` tag, no attribution. A `ref_rejected` diagnostic event is logged.
  - The browser's `ref` value is never trusted for ownership. The server decides.
- **Ownership:** first valid Realtor within 90 days, kept on the visitor record.
  - If a later visit arrives on a different Realtor's link, that Realtor's branding is shown, because they shared the link. Ownership does not move, and an `attribution_conflict` row is queued for Eli.
  - At lead time, the GHL Realtor fields are written **only if empty**. A contact that already has a referring Realtor keeps it, and the conflict is queued.
  - Reassignment is an admin action, written to `audit_log`.
- **What this cannot stop, stated plainly:** a person who clears cookies and comes back through another Realtor's link looks like a new visitor until they submit contact details. At that point the GHL check above catches it.

### 3.4 Event specification

All events are written to D1. Server-side events are the source of truth.

**Client-sent events:**
- Allowed only for things the server cannot see: widget opened, PDF export click, offer click.
- They go to `POST /chat/event`, which checks the origin, enforces a name allow-list and a props allow-list, caps the payload at 2 KB, and is rate-limited.
- They are flagged `origin='client'`.

| Event | Fired by | When | De-duplication | Props (allow-list; no free text) |
|---|---|---|---|---|
| `marina_opened` | client | Chat page JS has run, or the widget was opened | once per session per surface | `surface` (chat_page, widget, marina_page) |
| `realtor_link_visited` | server | `GET /chat` with a valid, active `ref` | once per session per Realtor (raw hits counted separately) | `realtor_id` |
| `chat_started` | server | First `POST /chat` with a message in a session | once per session | `surface` |
| `property_search_started` | server | Tool call begins: `get_property_intel`, `get_marine_intel` or `match_boat_to_areas` | per call | `tool`, `zip` (if parseable), `region` (boat matcher) |
| `property_search_completed` | server | Tool returns | per call; "properties researched" counts distinct `property_key` per session | `tool`, `ok`, `zip`, `flood_zone_class` (A/V/X/unknown), `property_key` (HMAC of the normalized address) |
| `report_requested` | server / client | An inspection brief is built, the PDF export is clicked, or the report offer is accepted | per request | `kind` (inspection_brief, pdf_export, report_offer) |
| `contact_submitted` | server | Consent granted and capture attempted (typed contact or offer form) | once per lead signature | `via` (chat_typed, offer_form), `capture_status` |
| `financing_requested` | server | A `[[HANDOFF]]` marker, or the financing offer accepted | once per session | `via` (handoff_marker, offer) |
| `repeat_visit` | server | A new session for a visitor who already has an earlier session | once per session | `days_since_last` |
| `message_sent` (supporting) | server | Every chat turn | none (it is a count) | `topics` (labels), `input_tokens`, `output_tokens`, `model` |
| `offer_shown`, `offer_clicked`, `consent_declined`, `ref_rejected` (supporting) | server / client | As named | once per session per kind | `kind` |

**Topic labels** come from keyword rules run on each message server-side, with no extra model call. Only the labels are stored. The labels:
- flood_zone, flood_insurance, wind_roof_4pt, insurance_cost
- condo_hoa, investor_dscr, short_term_rental, boating_dock_bridge
- taxes_homestead, first_time_buyer, refinance_equity, reverse_62plus
- self_employed, itin_foreign_national, jumbo, rates_question

**Token counts** per turn give a real **AI cost per lead** for the first time. Marina runs on Opus, so this is the number that shows whether Marina pays for herself.

### 3.5 Counting rules (no inflated numbers)

| Metric | Definition |
|---|---|
| Visits | Analytics sessions with `marina_opened` or `chat_started`, excluding `is_bot` and `is_internal` |
| Unique visitors | Distinct `visitor_id` across those sessions. Labelled "browsers (approx.)". |
| Chat sessions | Sessions with `chat_started` |
| Engaged sessions | Sessions with 2 or more visitor messages, or a completed property search. **Realtors are ranked on this, not on clicks.** |
| Properties researched | Distinct `property_key` per session where the search completed with `ok`, summed |
| Returning visitors | Distinct visitors with `repeat_visit` in the date range |
| Identified leads | Distinct GHL contacts captured with consent (`leads` table) |
| Financing inquiries | Sessions with `financing_requested` |
| Mortgage opportunities | Marina-attributed GHL opportunities, from the sync |
| Qualified | Opportunities a person has moved to App Sent or later. Marina never decides qualification. |
| Funded | Opportunities in Closed / Funded |

**What is excluded from counts:**
- **Bots:** user-agent bot patterns, plus page loads where JavaScript never ran. Raw Realtor-link hits are still shown in their own column.
- **Internal traffic:** the admin preview, a `tmd_internal` cookie Eli sets once from the dashboard, and test leads (`tmdIsTestLead`, Eli's own numbers and emails).
- **De-duplication:** once-per-session events are enforced by a unique index (`INSERT OR IGNORE`), not by application logic alone.

### 3.6 Data model (D1 database `tmd_marina_intel`; additive and new; touches no existing database)

```sql
CREATE TABLE realtors (
  id TEXT PRIMARY KEY, code TEXT UNIQUE NOT NULL, display_name TEXT NOT NULL,
  brokerage TEXT NOT NULL, license_no TEXT, email TEXT, phone TEXT, photo_url TEXT,
  website_host TEXT, ghl_contact_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('draft','compliance_review','active','inactive','legacy_review')),
  compliance_approved_by TEXT, compliance_approved_at TEXT, agreement_ref TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE campaigns (
  id TEXT PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, channel TEXT NOT NULL,
  utm_source TEXT, utm_medium TEXT, utm_campaign TEXT, utm_content TEXT,
  realtor_id TEXT REFERENCES realtors(id), created_at TEXT NOT NULL, notes TEXT
);
CREATE TABLE visitors (
  visitor_id TEXT PRIMARY KEY, first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL,
  first_touch_id TEXT, owner_realtor_id TEXT, owner_set_at TEXT,
  session_count INTEGER NOT NULL DEFAULT 0, is_internal INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY, visitor_id TEXT, started_at TEXT NOT NULL, last_event_at TEXT NOT NULL,
  surface TEXT, touch_id TEXT, realtor_id TEXT, device_class TEXT, id_source TEXT,
  is_bot INTEGER NOT NULL DEFAULT 0, is_internal INTEGER NOT NULL DEFAULT 0, opted_out INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE touches (
  id TEXT PRIMARY KEY, visitor_id TEXT, session_id TEXT NOT NULL, ts TEXT NOT NULL,
  channel TEXT NOT NULL, campaign_id TEXT, utm_source TEXT, utm_medium TEXT, utm_campaign TEXT,
  utm_content TEXT, utm_term TEXT, click_id_kind TEXT, referrer_host TEXT, landing_path TEXT, realtor_id TEXT
);
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, name TEXT NOT NULL, origin TEXT NOT NULL,
  visitor_id TEXT, session_id TEXT NOT NULL, realtor_id TEXT, touch_id TEXT, props TEXT,
  once_key TEXT UNIQUE   -- set only for once-per-session events, e.g. "<session>:chat_started"
);
CREATE INDEX events_name_ts ON events(name, ts);
CREATE INDEX events_realtor_ts ON events(realtor_id, ts);
CREATE TABLE leads (
  id TEXT PRIMARY KEY, created_at TEXT NOT NULL, visitor_id TEXT, session_id TEXT,
  ghl_contact_id TEXT, realtor_id TEXT, first_touch_id TEXT, last_touch_id TEXT,
  interest TEXT, via TEXT, consent_version TEXT, capture_status TEXT
);
CREATE TABLE lead_outcomes (
  ghl_opportunity_id TEXT PRIMARY KEY, ghl_contact_id TEXT NOT NULL, pipeline TEXT, stage TEXT,
  status TEXT, monetary_value REAL, synced_at TEXT NOT NULL
);
CREATE TABLE attribution_conflicts (
  id TEXT PRIMARY KEY, ts TEXT NOT NULL, visitor_id TEXT, ghl_contact_id TEXT,
  owner_realtor_id TEXT, other_realtor_id TEXT, resolved_by TEXT, resolved_at TEXT, resolution TEXT
);
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, actor TEXT NOT NULL,
  action TEXT NOT NULL, entity TEXT NOT NULL, before_json TEXT, after_json TEXT
);
```

**What the analytics tables never hold:** message text, names, emails, phone numbers, street addresses or IP addresses. The only personal data in D1 is on the `realtors` table (the business contact details of the partners themselves) and the `ghl_contact_id` pointer.

**Retention, enforced by a purge cron:**
- events: 25 months;
- visitors: 13 months after last seen;
- touches and sessions: follow their visitor.

### 3.7 Value-first lead offers (Phase 2)
- **The server decides when to offer.** The chat response gains an optional `offer` object. The chat page and widget render it as a card with a button. The chat itself is never blocked.
- **Trigger rules:**
  - Never on the first turn.
  - At most one offer every 3 turns.
  - Never again in a session after a decline.
- **The offers:**
  - **Detailed coastal property report.** Shown after a completed property search. Copy: "Want Eli to follow up with a detailed report on this property?" It is fulfilled by a person, not sent automatically. The Oct 8 audit found the existing `tmd-coast-report` engine can mislabel risk when a lookup fails, so it is not wired to send anything until it is repaired.
  - **Talk to a licensed mortgage professional.** Shown after a financing topic label or 4 or more messages.
  - **Financing assistance.** Shown when Marina emits `[[HANDOFF]]`.
  - **Realtor-branded property review.** Only on active Realtor links, and **only after decision 1 is approved.** Sharing the review with the Realtor also needs the borrower's authorization (the GHL `Agent Updates OK` field).
- **The form:**
  - Fields: first name, email, optional phone, prefilled interest.
  - The approved consent checkbox text (decision 2), required for phone contact.
  - A link to the privacy policy and a honeypot field.
  - Spanish copy alongside English, because Marina is bilingual.
  - The server re-validates everything and reuses the existing consent record format.

### 3.8 GHL mapping (Phase 2)
- **New contact custom fields (7):**
  - `mv_first_channel`
  - `mv_first_campaign`
  - `mv_first_touch_date`
  - `mv_last_channel`
  - `mv_referring_realtor` ("Name, Brokerage (code)")
  - `mv_referring_realtor_code`
  - `mv_interest` (Property report / Financing / Realtor review / Licensed professional / General)
- **When fields are written:** first-touch and Realtor fields only when empty, which means reading the contact after upsert.
- **Buyer Agent fields:** the existing `Buyer Agent *` fields are **not** touched automatically. A referring Realtor is not necessarily the buyer's agent, so a person confirms that.
- **Tags:**
  - New: `source-marina`, `mv-ch-<channel>`, `mv-int-<interest>`.
  - `ref-<code>`, only for validated codes.
  - Existing Marina tags are kept.
  - `website-lead`, only after decision 4.
- **Note:** one attribution line is added to the existing note, for example "First touch: LinkedIn / campaign X on 2026-10-30. This visit: QR. Realtor: Name (first touch)."
- **Opportunity rule:**
  - Create one only if the contact has **no open opportunity** in Main Lead Pipeline. That is checked by searching opportunities for the contact before creating.
  - This replaces today's "new contacts only" rule. It still prevents duplicates, and it also catches a returning contact who now asks for financing.
- **No messages, ever:** the integration only writes data. Before any new tag ships, Eli confirms in the GHL UI that no published workflow fires on it, because the workflow API is unavailable.
- **Outcome sync:**
  - Hourly cron in `tmd-marina-admin` with a **separate read-only GHL token** (contacts and opportunities read scopes).
  - It refreshes opportunity stage and status for every lead in D1.
  - Volume is a few hundred calls a day at most, far below GHL API limits.

### 3.9 Dashboard (Phase 3), `tmd-marina-admin`
- **Access:** Cloudflare Access on the hostname, with email one-time PIN for Eli's addresses. The Worker also verifies the Access JWT on every request, as defense in depth.
- **GHL link:** a custom menu link opens it in a new tab. Embedding it in the GHL iframe is untested, and Access login screens may not render inside an iframe.
- **Overview:** visits, unique visitors, chat sessions, engaged sessions, properties researched, returning visitors, identified leads, financing inquiries, opportunities, qualified, funded, AI cost per lead. Includes a date range, a "compare to previous period" toggle, and the exclusion toggles.
- **Realtors:**
  - Table of active Realtors with link, raw link hits, visits, engaged sessions, properties researched, buyer inquiries (leads), financing inquiries, opportunities, qualified, funded.
  - Ranked by engaged sessions, then qualified opportunities.
  - Includes the attribution conflicts queue.
- **Campaigns:**
  - By channel: Facebook vs LinkedIn, email vs SMS, QR vs direct.
  - By campaign and by `utm_content` (individual posts).
  - Each with visit-to-chat, chat-to-lead and lead-to-opportunity rates.
  - Rates are hidden when fewer than 20 sessions back them, with a "not enough data yet" label.
- **Property intelligence:**
  - Top ZIPs researched, flood zone class mix, topic labels over time, and the most common coastal concerns by ZIP.
  - Any ZIP with fewer than 3 sessions is grouped into "other", so a single visitor cannot be singled out.
- **What it shows of people:** no lead names or contact details. Lead rows link to the GHL contact instead.
- **Data source:** every number is a SQL query over recorded rows. There is no sample data, and empty states say "no data yet."

### 3.10 Realtor onboarding (Phase 4, inside `tmd-marina-admin`)
1. **Create profile:**
   - Fields: display name, brokerage (required), Florida license number, email, phone, website domain.
   - It searches GHL by email first and links the existing contact (Referral Partners pipeline) rather than creating a duplicate.
2. **Approved co-branding:**
   - Allow-listed fields only: display name, brokerage, headshot URL, one approved greeting variant.
   - Brokerage is always shown with the Realtor's name. Florida real estate advertising rules likely require the brokerage name; confirm with compliance.
   - Disclosures stay locked: NMLS and Equal Housing in the footer.
3. **Generate link:** a server-generated code. A copy button.
4. **QR code:**
   - Generated in the browser with a vendored open-source (MIT) QR library. No external service.
   - It encodes the link plus `utm_medium=qr&utm_source=print&utm_content=<placement>`.
   - Downloads as PNG and SVG.
5. **Preview:**
   - Opens the chat page with a short-lived signed `preview` token, so a draft or inactive profile renders.
   - Preview sessions are flagged internal. Contact capture shows "preview mode" and sends nothing to GHL.
6. **Activate or deactivate:**
   - **Activate stays disabled until the compliance fields are filled:** approver, date, agreement reference. That is how the "flag for compliance review" rule is enforced rather than just documented.
   - Deactivate takes effect immediately: the link falls back to generic Marina with no attribution.
   - Every change is written to `audit_log`.
7. **Activity:** a per-Realtor funnel, trend and campaign breakdown, with an aggregate-only export (counts, no borrower data) Eli can share with the Realtor if compliance allows.
- **Legacy import:**
  - A one-time "Import existing links" action reads KV `agent_ref:*` and creates `legacy_review` rows.
  - Legacy codes keep working during review, so the current behavior is preserved.
  - The chat Worker looks up D1 first, then KV.
  - The existing `/agents` API keeps working and writes through to D1.

---

## 4. Implementation phases and dependencies

The order follows a spending brake: **measure before building more.**
- Phase 1 alone answers the question that matters today. GHL holds zero Marina chat leads; is that a traffic problem or a conversion problem?
- Run Phase 1 for about two weeks before deciding how much of Phases 3 and 4 is worth building.

| Phase | Builds | Depends on | Estimated effort |
|---|---|---|---|
| **0. Prerequisites** (no code) | Confirm the live version at `/chat/healthz`. Snapshot the live bundle as `_LIVE_ROLLBACK_`. Check the Cloudflare plan. Create the D1 database and run the schema. Eli submits decision 1 to C2C and answers 2 to 6. | None | Eli: about 30 minutes. C2C: their timeline. |
| **1. Tracking foundation** | In `tmd-marina-chat`: visitor cookie, analytics sessions, touch capture, Realtor validation (D1, then KV fallback), server events, `/chat/event`, bot and internal flags, topic labels, token logging. **Dark-launched** behind `MV_TRACKING` and inert when the D1 binding is missing. Site PR: the widget and `/marina/` pass attribution, and `/marina/` gets GA4. A plain admin page with raw counts so numbers can be read from day one. | Phase 0 (D1 binding) | 2 sessions plus a site PR |
| **2. Lead offers and GHL attribution** | Offer cards and form, GHL fields and tags, the opportunity rule, the outcome sync cron. | Phase 1. GHL custom fields created. Decisions 2 and 4. | 1 to 2 sessions |
| **3. Dashboard** | Overview, Realtors, Campaigns, Property Intelligence, link builder. | Phase 1 data. Cloudflare Access set up. | 2 sessions |
| **4. Realtor onboarding** | Profile, branding, link, QR, preview, activate, activity, legacy import. | Phase 3 shell. **Activation depends on decision 1.** | 1 to 2 sessions |
| **5. QA and rollout** | Section 7 tests, staging soak, production enable. | Each phase ships through it | Runs within each phase |

**Ship gates:**
- Each phase ships separately.
- None reaches production without Eli's approval of that phase's test results.

---

## 5. Security and compliance

### Security (built into the design)
- **Admin access:** the admin surface is only behind Cloudflare Access, plus JWT verification in the Worker. No home-made login.
- **Least-privilege secrets:**
  - The admin Worker gets its own secret and a **read-only** GHL token.
  - It does not reuse `MARINA_WEBHOOK_SECRET`. The Oct 8 audit found that secret unlocks endpoints across at least 8 Workers.
- **Public event endpoint:** origin allow-list, IP rate limit (reuses the existing helper), event-name and property allow-lists, 2 KB cap, no free text.
- **Ownership trust:** Realtor ownership and attribution are computed only on the server. Client values are hints at most.
- **Session IDs:** analytics session IDs are issued by the server with `crypto.randomUUID()`. Legacy client conversation IDs keep working for Marina's memory only.
- **Fail-open analytics:** if D1 is down, chat still works and the event is dropped with a log line. Lead capture never depends on D1.
- **No secrets in pages:** a test scans every rendered page and response for key-like strings.
- **Realtor data isolation:**
  - Version 1 has no Realtor logins, so there is no cross-Realtor read path.
  - A future Realtor portal would need per-Realtor signed tokens, server-side `realtor_id` scoping, and isolation tests before launch.
- **Out of scope, reported privately:** two items in the website `lead.js` function. A separate task was suggested to Eli.

### Compliance flags (items needing review, not legal conclusions)
1. **RESPA Section 8 (Regulation X, 12 CFR 1024.14).**
   - The issues:
     - The public FAQ says Marina Pro is "free for active Realtor partners. There are no tiers and no invoice."
     - The existing co-branded page (Realtor name in the banner, greeting and brief) is a branded marketing asset given to referral sources.
     - The Oct 8 audit found the `tmd-realtor-comarketing` Worker keys on paid-sounding tags (`realtor-pro/elite/enterprise-active`), which conflicts with "no tiers".
   - **Needs C2C compliance review before new Realtors are onboarded.** Rewording the FAQ is also recommended in the meantime.
   - Internal rankings must never drive anything of value to a Realtor: lead routing, perks, featured placement, co-marketing subsidies.
2. **Sharing borrower activity with Realtors.** It needs the borrower's authorization (privacy, GLBA). Version 1 shares aggregate counts only, and only if compliance allows.
3. **TCPA and the Florida Telephone Solicitation Act.**
   - Align the chat consent text with the website's v3 consent (decision 2) before any automated text could fire from a Marina-applied tag.
   - The privacy policy sentence "By submitting your phone number through our forms or chat, you consent to receive ... marketing text messages" implies consent that the chat flow deliberately does not assume. Ask compliance whether to remove or reword it.
4. **Advertising disclosures on co-branded pages.**
   - Keep the NMLS and Equal Housing footer, which already exists.
   - Always show the brokerage with the Realtor's name.
   - Never imply the Realtor is the lender.
   - Marina's existing "no rates" rules stay in force.
5. **Data rights.**
   - Marina's property tool uses RentCast value data. The Oct 8 audit says written resale and display permission was never confirmed.
   - Internal dashboards are fine. A Realtor-branded report built on that data waits on permission.
6. **Privacy policy update.** Describe the first-party Marina analytics cookie, what is and is not stored, retention, and the opt-out (Global Privacy Control honored).

---

## 6. Expected operating costs

| Item | Cost | Notes |
|---|---|---|
| Cloudflare D1 | **About $0 extra** | Free plan: 5M rows read and 100k rows written per day, 5 GB. Workers Paid ($5/month, likely already in place since D1, R2 and Browser Rendering are in use; confirm in billing): 25B reads and 50M writes per month included. Even 10,000 chat sessions a month at about 15 rows each is about 150k writes a month. ([D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/)) |
| `tmd-marina-admin` Worker and hourly cron | About $0 extra | Inside existing Workers allowances at this traffic |
| Cloudflare Access | $0 | The Zero Trust free plan covers small teams (up to 50 users). Confirm on the account. |
| GHL API | $0 | Included in the current GHL plan |
| Anthropic | **$0 extra** | No added model calls. Topic labels are keyword rules. Token logging measures what is already spent. |
| QR codes | $0 | Open-source library, generated in the browser |
| GA4 | $0 | Existing |
| **Total new monthly cost** | **About $0** | The real cost driver stays Opus per chat turn. This project is what finally measures it per lead. |

No paid service is added. If one ever becomes necessary, it comes back to Eli with a cost first.

---

## 7. Testing strategy

### 1. Regression (every phase)
- Run the existing harness (47 checks, all network mocked) and the 1.5.1 behavior tests (16) against the new bundle.
- Both must pass, apart from the known hardcoded version check, which gets updated.

### 2. New automated tests (Node, with a D1 mock backed by `node:sqlite` so real SQL runs)

**Attribution and ownership**
- First touch is kept across sessions.
- Last touch updates.
- A second Realtor link does not change ownership and queues a conflict.
- Unknown and inactive codes give no branding and no `ref-` tag.
- A tampered `ref` in the POST body is ignored.

**Counting**
- Once-per-session events cannot double count.
- Bot user agents and no-JavaScript hits are excluded.
- Internal and test leads are excluded.
- Repeat visits fire only after 30 minutes of inactivity.
- Small cells stay suppressed.

**Leads and GHL**
- The same email twice gives one contact and no second opportunity.
- An existing contact with a Realtor field set is not overwritten.
- Consent declined means nothing sent.
- Unclear consent stays pending.
- An offer form without the consent box is rejected.
- Contact capture in preview mode sends nothing.

**Failure, retry and limits**
- D1 failure leaves chat working.
- GHL 429 and 5xx responses are retried with backoff and then recorded as failed, without crashing.
- The event endpoint rejects bad origins, unknown names, oversized payloads and bursts.

**Security**
- No secret-like strings in rendered pages.
- Admin routes refuse requests without a valid Access JWT.
- The read-only GHL token cannot write (mocked).

**Privacy**
- No message text, emails, phones or addresses appear in any D1 row after a full scripted conversation that includes all of them.

### 3. Staging
- A separate `tmd-marina-chat-staging` Worker on workers.dev, with its own D1 database.
- GHL writes go to contacts tagged `automated-test` (the tag already exists) and are deleted after each run.

### 4. Browser checks
- Playwright (preinstalled in the build environment) at 375 px and 1280 px.
- Chat page and homepage widget: open, chat, offer card, form, consent, voice toggle, co-branded banner, QR scan of a generated code.

### 5. Live smoke after each deploy
- `/chat/healthz` shows the new version.
- Run the v1.4 consent check, then delete the test contact.
- One tagged test link shows up in the dashboard with the right channel.

### 6. Rule for reporting results
Results are reported as actually run. Nothing is marked passed without its output.

---

## 8. Deployment and rollback

### Deployment (keeps today's dashboard-paste model)
1. Snapshot the current live code into `tmd-claude-archive/workers/` as `_LIVE_ROLLBACK_<date>.js`.
2. Create the D1 database `tmd_marina_intel`, run the schema in the D1 console, and bind it to `tmd-marina-chat` as `MV_DB`. Leave `MV_TRACKING` unset.
3. Paste the new bundle. Verify healthz and the v1.4 consent smoke test. Tracking is still off, so behavior is unchanged.
4. Set `MV_TRACKING=on`. Make one tagged test visit and confirm the rows land. Watch error logs for 24 hours.
5. Merge the site PR (widget and `/marina/` attribution, `/marina/` GA4). Netlify auto-deploys.
6. Deploy `tmd-marina-admin`, put Cloudflare Access on its hostname, and add the GHL custom menu link.
7. Phases 2 to 4 repeat steps 1, 3 and 4, each behind its own flag: `MV_OFFERS`, `MV_GHL_ATTRIB`, `MV_REALTOR_D1`.

### Rollback (seconds, no data loss)
- **Turn off just the new part:** unset the relevant `MV_*` flag. Chat reverts to current behavior immediately.
- **Code rollback:** Cloudflare dashboard → Workers & Pages → `tmd-marina-chat` → Deployments → previous version → Rollback. Or paste the `_LIVE_ROLLBACK_` file.
- **Site rollback:** revert the PR, or roll back the Netlify deploy.
- **Data:** the D1 database is new and additive. KV keys, existing Realtor records and GHL data are never deleted or rewritten. GHL fields are written only when empty, so a rollback leaves nothing inconsistent.

### Risks
- **Stale Mac source.** Deploying `src/index.ts` from the Mac with wrangler would wipe v1.4 and later. Retire that copy or reconcile it first.
- **Missing binding.** Pasting code that expects `MV_DB` before the binding exists is safe by design: the code checks for it and stays inert.

---

## 9. Notes for future development agents
- **Where Marina's source lives:** the latest bundle in `tmd-claude-archive/workers/`. It is an esbuild bundle: `env2` is `env`, and `__name(...)` lines are build artifacts. Patch it with labeled find-and-replace edits that fail loudly, following the pattern of `mortgage-dock-platform/docs/marina-v1.4.0/apply_fixes.py`.
- **Running the harness:** `node test_marina.mjs <bundle>.mjs`. Copy the bundle to `.mjs` first.
- **Session rules:**
  - Do not write `claude/HANDOFF.md` unless Eli confirms that session owns it.
  - `claude/TOOLS_INDEX.md` is the authoritative inventory and lives in the Claude Project. Update it when these components ship.
- **This repo is public:** no contact data, CRM IDs or security specifics here.
