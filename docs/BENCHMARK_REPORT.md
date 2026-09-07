# Benchmark report — HERMES HARNESS capability spill (issue #1)

- **Run date (UTC):** 2026-09-07
- **Module under test:** `tools/tool_result_storage.py` @
  `49b044a322b5a87e4f45fb18e73d09d0b204165e` (Hermes Agent upstream proposal)
- **Machine:** macOS 26.6.2 (Darwin 25.6.0), arm64, Apple M5 Max
- **Interpreter:** CPython 3.11.15, `cryptography` 50.0.0
- **Runner:** `benchmarks/run_benchmarks.py` (stdlib + `cryptography` only)
- **Raw data:** `results/2026-09-07-macos-arm64/raw_results.json`
- **Data:** 100% synthetic, deterministic seeded fixtures; no real sessions,
  secrets, or provider calls. Capability URIs never leave process memory.

## Methodology

Five synthetic workloads (seeded, byte-reproducible) are pushed through the
module's real public path: `maybe_persist_tool_result` for single results and
`enforce_turn_budget` for the multi-tool turn, with `session_id` set so the
session-capability path (`_write_capability_spillover` /
`resolve_spill_capability`) is exercised. Three context-window profiles
(32K / 131K / 1M tokens) derive their budgets from the module's own
`budget_for_context_window()` (see `docs/PROFILES.md`).

Per case we record: model-facing chars before/after; end-to-end persist
latency; raw spill-write latency; resolve latency (medians of 3 reps);
exact-byte round-trip fidelity; head/middle/tail sentinel survival in the
inline preview vs. the recovered body; and cross-session denial. Characters
are the token proxy (~4 chars/token, the module's own constant).

## Headline results

**Every recoverable case round-tripped byte-identically: fidelity 15/15 =
100%.** Every cross-session resolve raised `SpillCapabilityError`. Every head
sentinel survived in the inline preview; every tail sentinel was correctly
absent from the preview and present in the recovered body; the planted
middle fact (`web_extract`) was absent from the preview and recovered exactly.

### Single-result workloads

| workload | profile | before (chars) | after (chars) | reduction | persist e2e (ms) | spill write (ms) | resolve (ms) | fidelity |
|---|---|---|---|---|---|---|---|---|
| terminal_log | 32k | 479,888 | 1,926 | 0.9960 | 1.674 | 0.889 | 0.324 | PASS |
| terminal_log | 131k | 479,888 | 1,926 | 0.9960 | 0.861 | 0.814 | 0.332 | PASS |
| terminal_log | 1m | 479,888 | 1,926 | 0.9960 | 0.758 | 1.164 | 0.312 | PASS |
| web_extract | 32k | 319,867 | 1,767 | 0.9945 | 0.465 | 0.533 | 0.224 | PASS |
| web_extract | 131k | 319,867 | 1,767 | 0.9945 | 0.648 | 0.868 | 0.259 | PASS |
| web_extract | 1m | 319,867 | 1,767 | 0.9945 | 0.664 | 0.692 | 0.234 | PASS |
| repo_search | 32k | 399,926 | 1,897 | 0.9953 | 0.889 | 0.583 | 0.222 | PASS |
| repo_search | 131k | 399,926 | 1,897 | 0.9953 | 0.447 | 0.441 | 0.494 | PASS |
| repo_search | 1m | 399,926 | 1,897 | 0.9953 | 0.976 | 0.671 | 0.239 | PASS |
| json_output | 32k | 441,689 | 1,924 | 0.9956 | 0.587 | 0.567 | 0.275 | PASS |
| json_output | 131k | 441,689 | 1,924 | 0.9956 | 0.455 | 0.428 | 0.244 | PASS |
| json_output | 1m | 441,689 | 1,924 | 0.9956 | 0.461 | 0.455 | 0.269 | PASS |

### Turn-budget workload (5 × ~120K chars in one assistant turn)

| profile | before (chars) | after (chars) | reduction | enforce (ms) | spilled | recovered exact | fidelity |
|---|---|---|---|---|---|---|---|
| 32k | 599,454 | 9,504 | 0.9841 | 1.820 | 5 | 5 | PASS |
| 131k | 599,454 | 127,452 | 0.7874 | 1.987 | 4 | 4 | PASS |
| 1m | 599,454 | 127,452 | 0.7874 | 1.772 | 4 | 4 | PASS |

Behavior matches the design: under the tight 32K turn budget (39,321 chars)
all five results spill; under 131K/1M the largest results spill until the
aggregate fits (one ~120K result stays inline, since 4 spilled previews +
120K < 157,286). All spilled results recovered byte-identically in-session.

## What the numbers support

- On these synthetic oversized workloads, the mechanism replaces ~320K–600K
  model-facing chars with ~1.8K–9.5K chars of preview + capability reference
  (a >98% reduction *for these oversized cases*) while preserving exact
  recovery. This is a workload-specific observation, **not** a universal
  token-savings percentage.
- Spill overhead is millisecond-scale on this machine: raw encrypted write
  ≈ 0.4–1.2 ms, resolve (read + AEAD verify + digest check) ≈ 0.2–0.5 ms for
  320K–480K-char payloads. End-to-end persist (preview + write + message
  build) stays under 2 ms.
- Budget scaling behaves as designed: identical spill behavior across
  profiles for oversized single results; turn-level spilling adapts to the
  per-turn budget.
- Security behavior holds under the benchmark's checks: head evidence stays
  visible, middle/tail evidence survives only in the encrypted artifact, and
  cross-session resolution fails closed.

## Failure cases observed

**macOS run: none.** `failures` in `raw_results.json` is empty and `--check`
passed (fidelity < 100% or any workload error would exit nonzero). The
cross-session denial probe is the deliberate negative case and behaved as
specified (`SpillCapabilityError` raised in 12/12 single-result cases).

**Windows (CI): one genuine upstream bug found — see next section.**

## Windows finding: upstream text-mode read in `resolve_spill_capability`

Found by this benchmark on `windows-latest` CI (run 34075450968: 12/15
cases erroring with `SpillCapabilityError`, 15/15 fidelity fails) and
confirmed by an in-CI diagnostic (run 34075741893):

- At the pinned commit, `resolve_spill_capability`
  (`tools/tool_result_storage.py` L278–281) opens the ciphertext with
  `os.open(path, os.O_RDONLY | _O_NOFOLLOW | O_NONBLOCK)` — **without
  `os.O_BINARY`**. On Windows the CRT then reads in text mode.
- Measured on the runner: a 5,028-byte ciphertext file read back as **121
  bytes** in default (text) mode — truncated at the first `0x1A` (Ctrl+Z)
  byte of the random ciphertext, with CRLF folding as a second corruption
  source. Reading the same file with `os.O_BINARY` returned all 5,028 bytes
  and decrypted round-trip **byte-exact**; decrypting the text-mode read
  failed with `InvalidTag`.
- Consequence: on Windows, every same-session recovery fails with
  `SpillCapabilityError`. The failure is **closed** — availability loss,
  never wrong bytes: scope, AEAD tag, and digest all still verify when the
  read is done correctly. There is no integrity or confidentiality impact.
- The write path is unaffected (`os.fdopen(fd, "wb")` is binary), which is
  why the asymmetry went unnoticed: upstream's own Windows suite
  (`tests/tools/test_tool_result_capability.py`) also fails — 4 tests
  deterministically, 1 (`test_handler_forwards_hidden_session_scope`)
  flakily, since small ciphertexts only sometimes contain `0x1A`/CRLF.

**How the benchmark treats it (no patching, no fake pass):** the pinned
module is measured as-is. `fidelity_exact_bytes` records the module's real
resolve result (`false` on Windows). On Windows only, a case whose sole
deviation is this documented bug is reported as `KNOWN-ISSUE (payload
intact)`: the artifact is verified intact at rest via an explicit
`O_BINARY` read using the module's own scope/filename/key/AAD derivation
(`_binary_read_resolve` in `run_benchmarks.py`), and `--check` accepts only
that exact deviation on that platform. Any other failure, on any platform,
fails the check. In CI, the 5 resolve-dependent upstream tests are
deselected from the Windows gate (documented in `ci.yml`) and run in a
non-gating step so a future fixed upstream commit becomes visible.

**Upstream fix:** add `os.O_BINARY` (via `getattr(os, "O_BINARY", 0)`) to
the resolve-side `os.open()`. Worth proposing on PR #89582.

**CI status:** full matrix green (run 34076237564 — ubuntu/macos/windows ×
py3.11/3.12 benchmark legs + Windows reparse job). Windows legs report
`known-upstream-issue: 15`; POSIX legs report true 100% fidelity.

## Honest limits

- **Chars are a proxy, not tokens.** The ~4 chars/token ratio is the module's
  own conversion constant; real tokenizer counts will differ per model.
- **Single machine, single run.** Latencies on an Apple M5 Max with a fast
  local SSD; absolute ms values do not transfer to other hardware, and the
  benchmark measures the local backend path only (no docker/ssh/modal
  sandbox spill).
- **Synthetic payloads.** Real tool output differs in structure; fidelity is
  content-independent (exact bytes + digest), but preview usefulness is not
  measured here.
- **No provider cache telemetry.** Offline run: cache fields are recorded as
  N/A with a reserved schema (`benchmarks/README.md`); no numbers fabricated.
- **Oversized cases only.** All fixtures exceed every profile's per-result
  threshold by design; the benchmark does not measure the no-op path for
  small results (where the mechanism returns content unchanged).

## Reproduce

Exact commands, fixture descriptions, and environment facts:
`benchmarks/README.md`. Profile derivations: `docs/PROFILES.md`.
