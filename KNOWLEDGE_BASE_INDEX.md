# HERMES HARNESS Knowledge Base — Study Index

This directory is the decision-grade knowledge base for **HERMES HARNESS**, the Hermes-native context and tool-result economy system. DeepSeek Harness (DSH) remains its external research provenance, not the deployed product name. The conclusion is **Borrow, Don't Adopt**: retain DSH as a design specimen, and integrate only mechanisms that survive measurement against Hermes.

## Recommended reading order

1. **Canonical name and live scope** — [`HERMES_HARNESS.md`](HERMES_HARNESS.md)
2. **Decision and live status** — [`FINALIZATION.md`](FINALIZATION.md)
3. **Executive evidence and gates** — [`evidence/GATE.md`](evidence/GATE.md)
4. **Full technical textbook** — [`textbook/textbook.md`](textbook/textbook.md)
5. **Measured loss/trade study** — [`evidence/sim/LOSS_STUDY.md`](evidence/sim/LOSS_STUDY.md)
6. **Fresh simulation results** — [`evidence/sim/SIM_RESULTS.md`](evidence/sim/SIM_RESULTS.md)
7. **Independent ship reviews**
   - [`reviews/review_ship_sol.md`](reviews/review_ship_sol.md) — original REVISE gate
   - [`reviews/review_ship_recheck_grok.md`](reviews/review_ship_recheck_grok.md) — final GO
   - [`reviews/review_ship_recheck_gem31pro.md`](reviews/review_ship_recheck_gem31pro.md) — final GO
7. **Review history and adjudication** — [`reviews/CONSOLIDATED.md`](reviews/CONSOLIDATED.md)

## Evidence-bearing artifacts

### Source-grounded textbook

- [`textbook/textbook.md`](textbook/textbook.md) — 25-chapter master document.
- [`textbook/claim_ledger.jsonl`](textbook/claim_ledger.jsonl) — authoritative claim records.
- [`textbook/coverage_map.json`](textbook/coverage_map.json) — claim-to-section coverage.
- [`textbook/appendix/quarantined_agent_additions_20260817.jsonl`](textbook/appendix/quarantined_agent_additions_20260817.jsonl) — quarantined phantom regeneration records; not silently deleted.
- [`textbook/appendix/README.md`](textbook/appendix/README.md) — status of historical lane extracts.

### Measurements and simulations

- [`evidence/results.json`](evidence/results.json) — P0 benchmark measurements.
- [`evidence/spill_audit.json`](evidence/spill_audit.json) — existing Hermes spill primitive audit.
- [`evidence/sim/README.md`](evidence/sim/README.md) — simulation runner and target selection.
- [`evidence/sim/run_all.sh`](evidence/sim/run_all.sh) — all five simulations; defaults to live Hermes source and temp writes.
- [`evidence/sim/sim1_workload.json`](evidence/sim/sim1_workload.json) — real-workload replay.
- [`evidence/sim/sim2_chaos.json`](evidence/sim/sim2_chaos.json) — failure and attack matrix.
- [`evidence/sim/sim3_cache.json`](evidence/sim/sim3_cache.json) — deterministic-pointer/cache stability.
- [`evidence/sim/sim4_e2e.json`](evidence/sim/sim4_e2e.json) — real dispatcher E2E.
- [`evidence/sim/sim5_metrics.json`](evidence/sim/sim5_metrics.json) — tokens, latency, integrity, tail survival.

### Implementation references

- Reviewed worktree: `/Users/anastasios/deepseek-harness-research/p1/hermes-agent` at `384bce6aba`.
- Live source: `/Users/anastasios/.hermes/hermes-agent` at `fc36c6348f`.
- Feature module: `/Users/anastasios/.hermes/hermes-agent/tools/result_spill.py`.
- Central seam: `/Users/anastasios/.hermes/hermes-agent/model_tools.py`.
- Default config: `/Users/anastasios/.hermes/hermes-agent/hermes_cli/config_defaults.py`.

## Decision boundaries

- **Integrated:** P1 generic spill-first, deterministic pointer, bounded head/tail preview, fail-open behavior.
- **Default:** off in both base and `anastasios` profile resolution.
- **Not integrated:** DSH runtime, Cordis, DSH web app, SurfaceOp, duplicated pruner/spill modules.
- **Not authorized:** P2 or any enabled production canary until G1–G5 and G8 in `evidence/GATE.md` close.

## Reproduce the current checks

From `evidence/sim/`:

```bash
bash run_all.sh
```

From live Hermes source:

```bash
scripts/run_tests.sh \
  tests/tools/test_result_spill.py \
  tests/tools/test_result_spill_seam.py \
  tests/test_model_tools.py \
  tests/test_transform_tool_result_hook.py
```

Validate the textbook:

```bash
python3 /Users/anastasios/.claude/skills/author-technical-textbook/scripts/validate_textbook_package.py \
  /Users/anastasios/deepseek-harness-research/textbook
```

These commands prove the disabled integration and evidence package. They do not authorize enablement.
