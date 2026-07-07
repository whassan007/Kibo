---
name: united-states-data-subject-rights
description: >-
  Intake, verify, and fulfill US consumer-rights requests (know, delete, correct, opt-out of sale/sharing, limit sensitive PI, appeal) within state deadlines, honoring opt-out preference signals.
jurisdiction: United States
task_domain: Data Subject Rights & Inquiry Management
version: 1.0
---

# SKILL: Data Subject Rights & Inquiry Management — United States

## Purpose
Intake, verify, and fulfill US consumer-rights requests (know, delete, correct, opt-out of sale/sharing, limit sensitive PI, appeal) within state deadlines, honoring opt-out preference signals.

## Controlling frameworks & key obligations
- **CCPA/CPRA rights:** know/access, delete, correct, opt-out of sale/sharing, limit use/disclosure of sensitive PI, non-discrimination, and appeal (in opt-out states).
- **Opt-out preference signals:** Global Privacy Control (GPC) must be honored as a valid opt-out of sale/sharing in CA, CO, CT and a growing list of states.
- **Authorized agents:** permitted; verify agent authority plus consumer identity.

## Operational workflow
1. Intake request via webform / toll-free / email / GPC signal and classify by type and requester state.
2. Verify identity proportionate to sensitivity (MFA / cryptographic challenge); for deletion, use a higher tier.
3. Query all systems (CRM, marketing, data warehouse, SaaS, unstructured stores) to assemble the footprint.
4. Apply redaction/severance to remove third-party PII.
5. Execute: produce data export, propagate deletion + opt-out to all service providers/contractors, obtain confirmations.
6. Log fulfillment with timestamps; route denials/appeals to human review.

## Statutory deadlines & thresholds
- **CCPA response:** within **45 days**, extendable by a further **45 days** (90 total) with notice.
- **Opt-out of sale/sharing:** act as soon as feasibly possible, within **15 business days** of a GPC signal.
- Verification required before disclosure/deletion.

## Guardrails (mandatory)
- Never disclose another individual's PII; always sever third-party data.
- Never delete on an unverified request.
- Honor GPC even where the consumer has not separately submitted a request.

## Authoritative references
- California AG CCPA consumer rights: https://oag.ca.gov/privacy/ccpa
- CPPA: https://cppa.ca.gov
