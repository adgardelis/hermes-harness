# HERMES HARNESS benchmark summary

- Generated (UTC): 2026-09-07T02:01:29+00:00
- Module under test: `tools/tool_result_storage.py` @ `49b044a322b5a87e4f45fb18e73d09d0b204165e`
- Environment: Darwin 25.6.0 (arm64), Apple M5 Max, Python 3.11.15 (CPython), cryptography 50.0.0
- Cache telemetry: N/A offline (schema in benchmarks/README.md)
- Timed reps per measurement: 3 (median reported)

## Profiles (derived by the module's `budget_for_context_window`)

| profile | context window (tokens) | per-result budget (chars) | per-turn budget (chars) | preview (chars) |
|---|---|---|---|---|
| profile-32k | 32,768 | 19,660 | 39,321 | 1,500 |
| profile-131k | 131,072 | 78,643 | 157,286 | 1,500 |
| profile-1m | 1,048,576 | 100,000 | 200,000 | 1,500 |

## Single-result workloads

| workload | profile | before (chars) | after (chars) | reduction | persist e2e (ms) | spill write (ms) | resolve (ms) | fidelity | head in preview | tail in preview | middle recovered | tail recovered | cross-session denied |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| terminal_log | profile-32k | 479,888 | 1,926 | 0.9960 | 0.723 | 0.544 | 0.341 | PASS | True | False | True | True | True |
| terminal_log | profile-131k | 479,888 | 1,926 | 0.9960 | 0.715 | 0.591 | 0.304 | PASS | True | False | True | True | True |
| terminal_log | profile-1m | 479,888 | 1,926 | 0.9960 | 0.575 | 0.569 | 0.317 | PASS | True | False | True | True | True |
| web_extract | profile-32k | 319,867 | 1,767 | 0.9945 | 0.477 | 0.405 | 0.244 | PASS | True | False | True | True | True |
| web_extract | profile-131k | 319,867 | 1,767 | 0.9945 | 0.417 | 0.374 | 0.223 | PASS | True | False | True | True | True |
| web_extract | profile-1m | 319,867 | 1,767 | 0.9945 | 0.498 | 0.39 | 0.21 | PASS | True | False | True | True | True |
| repo_search | profile-32k | 399,926 | 1,897 | 0.9953 | 0.454 | 0.426 | 0.257 | PASS | True | False | True | True | True |
| repo_search | profile-131k | 399,926 | 1,897 | 0.9953 | 0.459 | 0.504 | 0.253 | PASS | True | False | True | True | True |
| repo_search | profile-1m | 399,926 | 1,897 | 0.9953 | 0.445 | 0.414 | 0.245 | PASS | True | False | True | True | True |
| json_output | profile-32k | 441,689 | 1,924 | 0.9956 | 0.49 | 0.454 | 0.251 | PASS | True | False | True | True | True |
| json_output | profile-131k | 441,689 | 1,924 | 0.9956 | 0.428 | 0.4 | 0.243 | PASS | True | False | True | True | True |
| json_output | profile-1m | 441,689 | 1,924 | 0.9956 | 0.454 | 0.678 | 0.257 | PASS | True | False | True | True | True |

## Turn-budget workload (multiple large tools in one turn)

| profile | results | before (chars) | after (chars) | reduction | enforce (ms) | spilled | recovered exact | fidelity |
|---|---|---|---|---|---|---|---|---|
| profile-32k | 5 | 599,454 | 9,504 | 0.9841 | 1.57 | 5 | 5 | PASS |
| profile-131k | 5 | 599,454 | 127,452 | 0.7874 | 1.346 | 4 | 4 | PASS |
| profile-1m | 5 | 599,454 | 127,452 | 0.7874 | 1.55 | 4 | 4 | PASS |

No workload errors.

Characters are used as a tokenizer-independent proxy for tokens (~4 chars/token, matching the module's own conversion constant). Numbers are from a single machine and must not be generalized into a universal savings percentage.
