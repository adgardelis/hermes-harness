# Contributing to HERMES HARNESS

Thank you for helping improve Hermes-native context economy.

## Principles

1. **Evidence before claims.** Token, latency, security, and fidelity claims must include reproducible commands and raw results.
2. **Hermes-native before parallel machinery.** Prefer existing Hermes storage, sessions, tools, transports, and lifecycle seams over a second runtime.
3. **Exact recovery over lossy truncation.** Savings must not silently destroy evidence.
4. **Fail closed at security boundaries.** Capability scope, filesystem identity, and cryptographic validation are load-bearing.
5. **Upstream-compatible changes.** Keep patches narrow and suitable for review by Hermes Agent maintainers.

## Good contributions

- Reproducible before/after token-economy workloads
- Windows reparse-point and cross-platform filesystem tests
- New transport/session-propagation coverage
- Security review and threat-model improvements
- Documentation and diagrams
- Small upstream-compatible fixes

## Workflow

1. Open an issue describing the problem, evidence, and proposed acceptance criteria.
2. Fork the repository and create a focused branch.
3. Add or update a test that would fail without the change.
4. Keep production changes minimal.
5. Run the affected Hermes Agent suites.
6. Include exact commands and outputs in the pull request.

Do not include secrets, live spill payloads, API tokens, user session data, or private filesystem paths in reports.
