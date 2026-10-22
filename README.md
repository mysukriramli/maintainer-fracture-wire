# Maintainer Fracture Wire

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Autonomous Machine Feed](https://img.shields.io/badge/Feed-Autonomous_6h-blue.svg)](data/today.json)

An autonomous software supply-chain risk radar engineered for **AI coding agents (Cursor, Devin, Copilot Workspace), architecture reviewers, and automated procurement systems**.

Predicts open-source library abandonment, maintainer burnout, and continuity risk before breaking failures occur by combining release cadence decay, maintainer bus-factor concentration, and downstream dependent reach.

---

## 📡 Live Machine Endpoints (Zero-Auth / Fastly Edge CDN)

| Endpoint | Format | Consumer Purpose |
| :--- | :--- | :--- |
| [`data/today.json`](data/today.json) | JSON | Active maintainer fracture scores, probability ratings, and mitigation directives. |
| [`data/remediation_queue.jsonl`](data/remediation_queue.jsonl) | JSONL | Streaming queue for CI/CD dependency linters and architectural bots. |
| [`data/llms.txt`](data/llms.txt) | Markdown | Token-efficient digest for Cursor, Claude Code, and Copilot prompts. |
| `data/archive/YYYY/MM/` | JSON | Permanent historical log tracking package health decay over years. |

---

## 🤖 Directives Emitted

- `FORK_AND_PIN`: High ecosystem reach package with critical maintainer decay; fork internally to protect continuity.
- `VENDOR_PACKAGE`: Single-maintainer concentration risk; copy source into vendor directory to avoid remote takeover.
- `MIGRATE_WITHIN_90_DAYS`: Package deprecated or release cadence dormant (>365 days); schedule active migration to recommended alternatives.
- `ADD_SECONDARY_IMPLEMENTATION`: Moderate continuity risk; architect dual-driver abstraction layer.
- `MAINTAINER_HEALTHY`: Active multi-maintainer cadence; safe for new project adoption.
