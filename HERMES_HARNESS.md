# HERMES HARNESS

**Canonical product name:** **HERMES HARNESS**  
**Status:** Installed, active, launchd-supervised, and upgrade-guarded in Hermes Studio.  
**Research provenance:** DeepSeek Harness (DSH) was a design and measurement source. It is not the installed runtime and is not the product name.

## Naming rule

Use **HERMES HARNESS** for the Hermes-native context and tool-result economy system.

Use **DeepSeek Harness** or **DSH** only when referring to:

- the external research repository;
- its original architecture or measurements;
- historical evidence describing how a mechanism was selected;
- source-attribution or comparative analysis.

Do not describe the live system as “DeepSeek Harness installed in Hermes.” The accurate statement is:

> **HERMES HARNESS is active in Hermes. It incorporates selected, measured ideas from DeepSeek Harness through Hermes-native implementation.**

## Current HERMES HARNESS capability

HERMES HARNESS currently provides the deployed token-economy and recoverability layer:

1. central model-facing tool-result budgeting;
2. context-window-scaled per-result and per-turn budgets;
3. compact inline previews for oversized results;
4. encrypted spill storage;
5. opaque `hermes-spill://` recovery capabilities;
6. same-session authorization and cross-session denial;
7. capability recovery through `read_file` and Codex MCP;
8. session propagation through nested `execute_code` RPC;
9. cleanup, compatibility checking, and upgrade regression alerts.

It does not install or run the external DSH runtime, Cordis kernel, DSH web application, or AST Code Mode.

## Runtime identity

- Reviewed implementation commit: `d0155e2c83011ef0ed7b5b1d39bf2640c3daa5dc`
- Upstream draft PR: https://github.com/NousResearch/hermes-agent/pull/89582
- Active source tree: `/Users/anastasios/.hermes/profiles/anastasios/workspace/worktrees/result-spill-upstream-current`
- Upgrade watchdog: `/Users/anastasios/.hermes/scripts/result-spill-upgrade-guard.py`
- Watchdog schedule: every six hours, silent when healthy, delivered to all configured channels on a new regression.

Internal module/config names such as `tool_result_storage`, `result_spill`, and `tools.result_spill` remain implementation identifiers for compatibility. They do not change the product name.
