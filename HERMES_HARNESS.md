# HERMES HARNESS

**Canonical product name:** **HERMES HARNESS**

**Status:** Public research preview; active in a reference Hermes Studio deployment; proposed upstream.

**Research provenance:** DeepSeek Harness (DSH) was a design and measurement source. It is not the installed runtime and is not the product name.

## Naming rule

Use **HERMES HARNESS** for the Hermes-native context and tool-result economy system.

Use **DeepSeek Harness** or **DSH** only when referring to:

- the external research repository;
- its original architecture or measurements;
- historical evidence describing how a mechanism was selected;
- source attribution or comparative analysis.

Do not describe the live system as “DeepSeek Harness installed in Hermes.” The accurate statement is:

> **HERMES HARNESS is an improved, Hermes-native adaptation of DeepSeek Harness—selectively integrating its strongest ideas with capabilities already native to Hermes.**

## Current capability

HERMES HARNESS currently provides:

1. central model-facing tool-result budgeting;
2. context-window-scaled per-result and per-turn budgets;
3. compact inline previews for oversized results;
4. encrypted spill storage;
5. opaque `hermes-spill://` recovery capabilities;
6. same-session authorization and cross-session denial;
7. capability recovery through `read_file` and Codex MCP;
8. session propagation through nested `execute_code` RPC;
9. cleanup, compatibility checking, and upgrade regression alerts.

It does not install or run the external DSH runtime, Cordis kernel, DSH web application, SurfaceOp, or AST Code Mode.

## Public runtime identity

- Current upstream-ready commit: `49b044a322b5a87e4f45fb18e73d09d0b204165e`
- Stable reviewed patch ID: `629678ef5cc8f0c2b7a7bcad56040c096ac62df3`
- Upstream draft PR: https://github.com/NousResearch/hermes-agent/pull/89582
- Public repository: https://github.com/adgardelis/hermes-harness

Internal module/config names such as `tool_result_storage`, `result_spill`, and `hermes-spill://` remain implementation identifiers for compatibility. They do not change the product name.
