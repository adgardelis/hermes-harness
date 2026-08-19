# HERMES HARNESS — Live and Upgrade-Permanence Record

Date: 2026-08-19

**Canonical product name:** **HERMES HARNESS**. DeepSeek Harness/DSH is research provenance only. Internal `result_spill` and `tool_result_storage` identifiers remain compatibility-oriented implementation names.

## Live source

- Repository: `/Users/anastasios/.hermes/hermes-agent`
- Live commit: `c491fb1cbf0637e2a1d38398effb31da46faf65e`
- Recovery tag: `hermes-result-spill-v1`
- Complete recovery bundle: `evidence/hermes-result-spill-v1.bundle`
- Bundle SHA-256: `1e81d99f64577d96c665608c51cf060c2cc9d2e8388a2eff72681fa7b7dca03c`
- Bundle verification: complete history, tag resolves to the exact live commit.

## Verification

- Live focused integration suite: 222 passed + 5 subtests.
- Final corrected branch focused suite: 210 passed + 5 subtests.
- Repeated execute_code/session-propagation suite: 5 consecutive green runs, 53 tests + 5 subtests each.
- Post-correction independent Gemini review: GO; 59 transport/code-execution assertions green.
- Production-path Hindsight canary proved spill, omitted-middle absence inline, same-session rehydration, extraction/recall, and disposable-bank deletion.
- Bundled/base defaults remain `enabled: false`, `enabled_session_ids: []`.
- The `anastasios` profile was explicitly enabled after gate closure. A live
  profile-configured 30 KB probe spilled to a 1,361-byte inline capability,
  resolved byte-identically in the same session, and its canary directory was
  removed afterward.

## Upgrade permanence

A deterministic, no-agent watchdog runs every six hours:

- Cron id: `d618c09f87e1`
- Script: `/Users/anastasios/.hermes/scripts/result-spill-upgrade-guard.py`
- Healthy behavior: silent, exit 0.
- Checks: required source seams, default-off state, real spill capability emission, same-session round trip, cross-session rejection.
- First manual and cron executions: healthy.
- Deduplicated regression alerts prevent repeat spam.

Normal updates preserve the local commit history or fail with an explicit merge/rebase conflict. If an update rewrites or removes the feature, the external watchdog detects the missing source/behavior. The verified bundle permits exact restoration even if the checkout history is lost. Unknown incompatible future source shapes are never patched silently; the guard alerts rather than claiming success.

## Final correction closure

Kimi identified that Codex MCP could receive a capability but lacked a capability-only reader. This was fixed by exposing an MCP `read_file` that accepts only `hermes-spill://v1/...`, rejects ordinary filesystem paths without dispatch, and forwards the exact captured Hermes session scope. The threaded test mock leak was replaced with explicit dispatcher injection; production behavior remains unchanged when no injection is supplied.

Gemini independently re-reviewed these corrective bytes and returned `VERDICT: GO`.
