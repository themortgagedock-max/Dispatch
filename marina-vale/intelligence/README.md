# Marina Vale Intelligence

Tracking, Realtor referral and lead intelligence for Marina Vale, The Mortgage Dock's AI coastal property assistant.

**Status (2026-10-24): audit complete, plan proposed. Nothing built or deployed.** Approval is needed before any build.

| File | What it is |
|---|---|
| [AUDIT.md](AUDIT.md) | Phase 1 audit. Where Marina lives, the production version, how sessions, Realtor branding and lead capture work today, GHL state (verified live, read only), and what exists, what is partial and what is missing. |
| [PLAN.md](PLAN.md) | The other deliverables: decisions needed, reuse map, missing functionality, architecture (identity, attribution, events, data model, offers, GHL mapping, dashboard, onboarding), phases, security and compliance, costs, testing, deployment and rollback. |

## The short version

- **Realtor co-branded links already exist** (`/chat?ref=CODE`). They have no tracking, no validation and no admin UI.
- **Marina records no usage events.**
  - No events and no visitor or campaign capture.
  - No analytics on the chat page or on `/marina/`.
- **GHL capture is consent-gated and working.** Still, 0 contacts carry the `marina-chat` tag, and no Realtor-attributed Marina lead has ever been created.
- **Recommended approach:**
  - Extend the existing `tmd-marina-chat` Worker with server-side events.
  - Store them in a new Cloudflare D1 database (about $0 a month extra).
  - Add a small admin Worker behind Cloudflare Access, opened from GHL.
- **Recommended order:** measure first (Phase 1), read two weeks of real numbers, then build the dashboard and onboarding.
- **Compliance gates Realtor activation.** The public "Marina Pro is free for active Realtor partners" wording and the co-branding arrangement need Coast2Coast compliance review under RESPA Section 8.

This repository is public, so these docs leave out contact data, CRM record IDs and security specifics.
