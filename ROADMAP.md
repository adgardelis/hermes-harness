# HERMES HARNESS roadmap

## v0.1 — Public research preview

- [x] Canonical naming and scope
- [x] Session-bound opaque capabilities
- [x] AES-GCM encrypted spill storage
- [x] Hermes `read_file` recovery
- [x] Codex MCP capability reader
- [x] Nested `execute_code` session propagation
- [x] Independent final security/correctness review
- [x] Upstream Hermes Agent draft PR
- [x] Upgrade-regression guard for the reference deployment

## v0.2 — Public proof package

- [ ] Reproducible benchmark harness using representative Hermes tool workloads
- [ ] Before/after input-token, latency, and recovery-fidelity report
- [ ] Multiple provider/context-window profiles
- [ ] Threat model and attack matrix
- [ ] Cross-platform CI, including Windows reparse-point coverage
- [ ] Short recorded demonstration

## v0.3 — Supported adoption path

- [ ] Resolve upstream maintainer feedback
- [ ] Publish compatibility matrix by Hermes Agent version
- [ ] Provide a supported installation/rollback path
- [ ] Add status and observability surfaces without payload leakage
- [ ] Document upgrade migration from reference deployment to upstream release

## Future research

- Active-surface projection only if benchmarks show it improves on native Hermes compaction
- Broader content-aware preview strategies without breaking deterministic recovery
- Provider cache telemetry that contains no user payloads
- Shared benchmark submissions from the Hermes community

Roadmap items are directional, not promises. Security and upstream compatibility take priority over feature count.
