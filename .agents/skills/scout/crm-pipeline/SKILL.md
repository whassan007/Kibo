# CRM Pipeline Automation

## Metadata
- ID: kibo-crm-scout
- Name: CRM Tool Sequencer & Pitfall Guard
- Version: 1.0.0
- Scope: Workspace (Project-Specific)

## Description
Provides parameter guidance and guardrails for interacting with CRM APIs (HubSpot, Salesforce). It handles lead routing, stage updates, and pipeline synchronization logic.

## Boundaries
- **Draft, Don't Dispatch**: Never trigger external notifications, state deployments, or client-facing emails directly. Stage modifications must be logged as staged state mutations for verification.
- Enforce strict parameter validation matching target CRM field types before calling execution tools.

## Operational Strategy
- **Sequencing**: When modifying a customer record, always query for the record existence first, retrieve the current lifecycle stage, calculate mutations, and output a validated JSON payload.
