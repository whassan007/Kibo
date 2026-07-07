# Backend & API Review
`agent_gateway.py` heavily overloaded.
- N+1 queries detected in Inbox.
- Idempotency lacking on decision endpoint.
Migration to async architecture recommended.

_Auto-generated on 2026-07-06T23:49:31.643688_
