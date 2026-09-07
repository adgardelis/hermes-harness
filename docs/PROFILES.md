# Benchmark profiles

Profiles are **not** invented by the benchmark. Each profile is a model
context-window size (in tokens), and the per-result / per-turn char budgets
are derived at runtime by the module's own
`tools/budget_config.py::budget_for_context_window()` at the pinned commit
`49b044a322b5a87e4f45fb18e73d09d0b204165e`. The benchmark calls that function
and measures whatever it returns.

## Module defaults and scaling constants (from the source)

From `tools/budget_config.py`:

| constant | value | meaning |
|---|---|---|
| `DEFAULT_RESULT_SIZE_CHARS` | 100,000 | per-result persistence threshold (cap) |
| `DEFAULT_TURN_BUDGET_CHARS` | 200,000 | per-turn aggregate budget (cap) |
| `DEFAULT_PREVIEW_SIZE_CHARS` | 1,500 | inline preview size after persistence |
| `_CHARS_PER_TOKEN` | 4 | token↔char conversion (matches the estimator) |
| `_PER_RESULT_WINDOW_FRACTION` | 0.15 | max window fraction for one tool result |
| `_PER_TURN_WINDOW_FRACTION` | 0.30 | max window fraction for a whole turn |
| `_MIN_RESULT_SIZE_CHARS` | 8,000 | per-result floor |
| `_MIN_TURN_BUDGET_CHARS` | 16,000 | per-turn floor |

Derivation:

```
window_chars = context_window_tokens * 4
per_result   = clamp(window_chars * 0.15, min=8_000,  max=100_000)
per_turn     = clamp(window_chars * 0.30, min=16_000, max=200_000)
preview      = 1_500 (constant)
```

## Profiles used in this benchmark

| profile | context window (tokens) | per-result budget (chars) | per-turn budget (chars) | preview (chars) |
|---|---|---|---|---|
| `profile-32k` | 32,768 | 19,660 | 39,321 | 1,500 |
| `profile-131k` | 131,072 | 78,643 | 157,286 | 1,500 |
| `profile-1m` | 1,048,576 | 100,000 (capped) | 200,000 (capped) | 1,500 |

These values appear verbatim in each run's `raw_results.json` under
`profiles`, so a reader can confirm the benchmark measured the module's real
scaling rather than a hand-tuned copy.

Notes:

- `profile-1m` hits the historical default caps; any window ≥ ~167K tokens
  caps per-result at 100K chars, and ≥ ~333K tokens caps per-turn at 200K
  chars. Large models are byte-identical to the module's fixed defaults.
- Small windows scale budgets down proportionally so a single spilled result
  cannot approach the whole window (upstream issue #23767 motivation).
- The benchmark passes the per-result budget as an explicit `threshold` to
  `maybe_persist_tool_result`, which also bypasses the per-tool registry
  lookup — the registry requires the full Hermes runtime and is out of scope
  for an offline benchmark of this module.
