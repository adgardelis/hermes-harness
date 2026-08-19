# HERMES HARNESS knowledge base

This public repository contains the decision-grade core of the HERMES HARNESS evidence package.

## Read in this order

1. [README](README.md) — public explanation, status, architecture, and evidence summary
2. [Canonical scope](HERMES_HARNESS.md) — naming boundary and runtime identity
3. [Historical finalization record](FINALIZATION.md) — how the original Hermes-native direction was selected
4. [Upgrade permanence](evidence/PERMANENCE.md) — reference deployment continuity model
5. [Independent final review](evidence/upstream/FINAL_REVIEW_GEMINI_3_7_FLASH_HIGH.md)
6. [Frozen upstream patch](evidence/upstream/0001-bind-persisted-results-to-session-capabilities.patch)
7. [Roadmap](ROADMAP.md)

## Evidence boundary

The included finalization record is historical. Later gate closure, active deployment, upstream rebasing, and the HERMES HARNESS name are documented by the newer canonical and permanence records.

Local machine paths in historical internal evidence have been replaced with portable placeholders in this public package. The private source evidence remains preserved separately.

## Naming

- **HERMES HARNESS** — Hermes-native context and tool-result economy system
- **DeepSeek Harness / DSH** — external research provenance only
- `result_spill`, `tool_result_storage`, and `hermes-spill://` — compatibility-oriented internal identifiers
