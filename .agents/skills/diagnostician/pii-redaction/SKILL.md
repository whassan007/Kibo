# PII Redaction & Sanitization

## Metadata
- ID: kibo-pii-redactor
- Name: Local In-Boundary Data Sanitizer
- Version: 1.0.0
- Scope: Workspace (Project-Specific)

## Description
Intercepts, evaluates, and strips Personally Identifiable Information (PII) across 15 standard categories (including names, tokens, emails, IPs, and credentials) before data is passed to external contexts or downstream engines.

## Boundaries
- **CRITICAL**: All evaluation and parsing MUST happen locally within the environment. No network boundaries may be crossed during the sanitization phase.
- Use zero-dependency regex and deterministic token matching to maximize execution speed and predictability.

## Processing Rules
Scan incoming payloads against the following blocks:
- **Credentials/Keys**: Matches patterns for `sk-`, `nvapi-`, `ghp_`, and standard `Authorization: Bearer` headers.
- **Network Metadata**: Redacts IPv4/IPv6 blocks and unapproved internal subnets.
- **Identifiers**: Replaces detected email addresses, phone numbers, and semantic name clusters with deterministic tokens (e.g., `[REDACTED_EMAIL_1]`).
