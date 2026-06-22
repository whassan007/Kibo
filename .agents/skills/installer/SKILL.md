---
name: installer
id: kibo-installer
version: 1.0.0
scope: Workspace
description: |
  Handles the physical installation and integration of KIBO modules into client environments.
  Applies modules layer-by-layer starting with telemetry, deploy to staging, and routing production gates.
  Triggers on deployment tasks, module installation (kibo-net, kibo-rag, etc.), staging testing, and production cutover requests.
---

# Installer Skill

## Mandate & Role
The Installer crew integrates and deploys KIBO OS modules into target customer stacks. It respects strict sandbox boundaries and operates autonomously only within staging environments, routing production transitions to human operators.

## Execution Triggers
Active execution of this skill occurs upon user requests or agent signals to:
- Deploy modules to a client environment.
- Provision or configure Tailscale meshes (kibo-net), Vector databases (kibo-rag), Ollama model routing (kibo-gateway), or MCP servers (kibo-connect).
- Perform compliance or staging smoke tests.

## Installation Protocols
1. **Layer Sequencing**: Build bottom-up (1. Foundation -> 2. Network/Security -> 6. Telemetry/Observability) to secure a telemetry-first observable foundation before deploying value-heavy top layers (3. Knowledge/RAG, 4. Model Services, etc.).
2. **Environment Gating**: The crew is authorized to deploy autonomously only to *Staging*. Production deployment must trigger a human gate request (`human_approves_production`) that routes to the judgment queue.
