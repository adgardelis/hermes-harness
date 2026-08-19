# HERMES HARNESS

**HERMES HARNESS** is the Hermes-native context and tool-result economy system for Hermes Agent and Hermes Studio.

> DeepSeek Harness (DSH) is research provenance only. HERMES HARNESS is not a deployment or fork of the DSH runtime. It is a native Hermes implementation built from mechanisms that survived source review, measurement, security hardening, and Hermes-specific integration testing.

## Active capability

HERMES HARNESS currently provides:

- model-facing tool-result budgeting;
- context-window-scaled per-result and per-turn budgets;
- compact inline previews for oversized results;
- AES-GCM encrypted spill storage;
- opaque `hermes-spill://` recovery capabilities;
- same-session recovery and cross-session denial;
- recovery through Hermes `read_file` and Codex MCP;
- session propagation through nested `execute_code` RPC;
- cleanup and upgrade-regression monitoring.

It does **not** install the external DSH runtime, Cordis kernel, DSH web application, SurfaceOp, or AST Code Mode.

## Upstream contribution

The recoverable session-capability layer is proposed to Hermes Agent in:

- [NousResearch/hermes-agent#89582](https://github.com/NousResearch/hermes-agent/pull/89582)
- Reviewed commit: `d0155e2c83011ef0ed7b5b1d39bf2640c3daa5dc`

## Repository contents

- `HERMES_HARNESS.md` — canonical naming, scope, and runtime identity.
- `KNOWLEDGE_BASE_INDEX.md` — decision-grade study index.
- `FINALIZATION.md` — historical integration decision and evidence boundary.
- `evidence/PERMANENCE.md` — live and upgrade-permanence record.
- `evidence/upstream/PR_BODY.md` — upstream contribution description.
- `evidence/upstream/FINAL_REVIEW_GEMINI_3_7_FLASH_HIGH.md` — final independent review.
- `evidence/upstream/0001-bind-persisted-results-to-session-capabilities.patch` — frozen patch artifact.

## Naming rule

Always capitalize the product name as **HERMES HARNESS**.

Use “DeepSeek Harness” or “DSH” only for the external research source, its original architecture, or historical comparative evidence.
