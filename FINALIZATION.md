# HERMES HARNESS — Hermes Studio P1 Finalization Record

**Finalized:** 2026-08-18  
**Decision:** Path C — borrow the measured mechanism; do not adopt the DSH runtime.  
**Live state:** merged into Hermes source, **disabled by default**.  
**Enablement state:** **NOT AUTHORIZED** until G1–G5 and G8 close.

> Naming update (2026-08-19): the Hermes-native product is **HERMES HARNESS**. “DeepSeek Harness” and “DSH” below identify only the external research source or historical evidence. Later gate-closure and active-runtime state is recorded in `HERMES_HARNESS.md` and `evidence/PERMANENCE.md`.

## 1. What was finalized

This is not a DeepSeek Harness runtime installation and not a desktop UI plugin. It is one generic Hermes core policy at the existing model-facing result boundary:

1. oversized plain-text tool results are thresholded in UTF-8 bytes;
2. when enabled, the complete payload is written first through Hermes's existing private spill primitives;
3. the model receives a deterministic retrieval pointer plus bounded head/tail preview;
4. storage, quota, path, or race failures return the original result unchanged;
5. the current default is `tools.result_spill.enabled: false`.

The change adds no model tool, no tool schema, no system-prompt text, and does not rewrite previously exposed conversation history.

## 2. Source identities

| Object | Identity |
|---|---|
| DSH research subject | `47f9438` |
| Hermes base | `9504edbaea29ce249864a1be05819d972f8fae8d` |
| Reviewed P1 worktree | `384bce6abaf4f5483e8f156f0965d94e8a314357` |
| Live Hermes after integration | `fc36c6348f` |
| Live source root | `/Users/anastasios/.hermes/hermes-agent` |
| Review worktree | `/Users/anastasios/deepseek-harness-research/p1/hermes-agent` |

Seven reviewed commits were cherry-picked in order. Their live SHAs are:

1. `98bafd031e` — central generic result-spill policy;
2. `7aa5eb1406` — byte budgeting, pre-write eviction, profile-safe root;
3. `7db3e100b8` — task fallback, read-only config, execute-code exemption;
4. `4ad9ee52c3` — cross-check corrections and config consistency;
5. `2f5b997667` — deterministic pointers, grace eviction, notice floor;
6. `f6a312ea4c` — identical-race dedupe reuse;
7. `fc36c6348f` — G7 tail preview.

## 3. Live changed paths

- `hermes_cli/config_defaults.py`
- `model_tools.py`
- `tools/result_spill.py`
- `tests/tools/test_result_spill.py`
- `tests/tools/test_result_spill_seam.py`

Each live blob was compared with the corresponding reviewed `384bce6aba` blob and matched exactly. No transient review artifacts (`p1_diff.patch`, `probe.py`) remain.

## 4. Configuration and runtime boundary

Resolved configuration was checked through the Hermes CLI in both contexts:

- base home: `false`
- `anastasios` profile home: `false`

A fresh process from neutral `/tmp`, with ambient `PYTHONPATH` removed and only the exact live root supplied, imported:

`/Users/anastasios/.hermes/hermes-agent/tools/result_spill.py`

The same probe passed a 60 KB result through the default configuration and verified:

- returned result unchanged;
- no spill directory created;
- `preview_tail_chars = 200` available for a later gated canary.

No live config file was edited. No Studio/gateway service was restarted. Existing processes therefore were not disturbed; fresh processes can import the integrated source, while the feature remains inert.

## 5. Independent review closure

| Gate | Result |
|---|---|
| Original Sol ship gate | REVISE: F1 validator, F2 G1–G8 enumeration, F3 stale simulation prose |
| F1 repair | textbook validator PASS (0 failures); 692-claim authoritative set restored |
| F2 repair | GATE.md explicitly enumerates G1–G8 |
| F3 repair | simulation docs tied to reviewed/final bytes; G7 0% → 100% recorded |
| Grok 4.6 xhigh re-check | GO merge-with-disabled |
| Gemini 3.1 Pro High re-check | GO merge-with-disabled |
| Grok residual | stale generated `tail_loss_note`; corrected and regenerated before finalization |

## 6. Fresh destination verification

### Canonical affected suite

`scripts/run_tests.sh` on the four affected test files:

- **4 files**
- **61 tests passed**
- **0 failed**

`py_compile` also passed for the three production modules.

### Five live-target simulations

All five scripts now accept `HERMES_AGENT_TREE` and default to the live source. The final run used temp spill/config directories and read `state.db` read-only.

| Simulation | Fresh result |
|---|---|
| Real-workload replay | 5,000 messages; 120 spills; 0 fail-open; 22.06% context bytes saved |
| Failure/attack chaos | symlink, wrong-content, quota, absurd-ID, distinct-race, identical-race checks all true |
| Prompt-cache stability | 3/3 spilling fixtures stable; 63.24% bytes saved on the pathological fixture |
| Real dispatcher E2E | spill marker present; pointer resolves exactly; file 0600; dir 0700; temp home only |
| Benefit metrics | 21.59% estimated token savings; 100% pointer integrity; 100% tail-window survival; 73/73 stable digests |

### Textbook package

The authoritative package validator returned:

`RESULT: PASS (0 failure(s))`

### Whole-repository suite baseline

The full live suite is not globally green, but the failures were replayed rather than waved away:

- pre-P1 base `9504edb`: **73 failures in 19 files**;
- clean reviewed P1 tree: **the same 73 failures in the same 19 files**;
- live tree: **74 failures in 20 files**;
- the one live-only failure is `tests/plugins/test_hindsight_root_guard.py`, associated with pre-existing unrelated Hindsight edits.

Therefore P1 introduced no full-suite failure. The unrelated baseline remains real work and is not silently reclassified as passing.

## 7. Preservation and recovery record

Before integration, all eight unrelated dirty live files were SHA-256 recorded and backed up at:

`/Users/anastasios/deepseek-harness-research/backups/pre-result-spill-merge-20260818T120514Z`

After integration, all eight hashes matched their pre-merge values. A stale, zero-byte `.git/index.lock` with no process holder or Git operation marker was quarantined into that backup. One aborted sequencer attempt was fully rolled back; pre-existing hashes and P1 paths were verified before the successful cherry-pick.

Do not use `git reset` to roll this feature back: the live branch contains unrelated work. If rollback is ever required, keep the feature disabled and revert the seven P1 commits newest-to-oldest after a fresh conflict/dirty-tree preflight.

## 8. Enablement gates still open

The source integration is finished; the canary is not.

- **G1:** TTL sweep and global disk cap.
- **G2:** principal decision on raw-secret redaction versus 0600/0700 storage.
- **G3:** Docker/SSH/Modal path visibility.
- **G4:** production prompt-cache and token telemetry on at least two provider families.
- **G5:** complete MCP session threading.
- **G6:** keep `enabled: false` until G1–G5 close.
- **G7:** closed — 200-byte tail window implemented and measured 100% on the sample.
- **G8:** Hindsight extraction recovery probe plus explicit acceptance of the FTS trade.

## 9. Final decision

**P1 is finalized as a reviewed, byte-verified, disabled-by-default Hermes integration.** It is safe to study and retain in the live source. It is **not** authorized for production enablement, and P2/SurfaceOp remains unapproved.
