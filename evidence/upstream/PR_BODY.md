## What does this PR do?

Extends Hermes Agent's existing persisted tool-result system with opaque, same-session recovery capabilities.

Oversized model-facing tool results receive a `hermes-spill://v1/...` capability instead of exposing a host cache path. The complete payload is AES-GCM encrypted at rest and can be recovered through Hermes `read_file` only by the session that minted the capability. Direct transports, Codex MCP, concurrent/sequential tool execution, and nested `execute_code` RPC preserve the same session scope.

This is the recoverable capability layer developed as part of **HERMES HARNESS**, a Hermes-native context and tool-result economy project. DeepSeek Harness was research provenance; this PR does not add its runtime, Cordis, web application, SurfaceOp, or AST Code Mode.

The implementation extends `tools/tool_result_storage.py`; it does not introduce a second spill engine or a new model tool.

## Related Issue

Related to #23200, #70949, and #415. Also compared against the overlapping path-oriented draft #85480 and storage-hardening PR #80760; this PR's distinct scope is encrypted, opaque, session-bound recovery.

## Type of Change

- [x] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] 🔒 Security fix
- [x] ✅ Tests (adding or improving test coverage)

## Changes Made

- Add session-bound capability minting and resolution in `tools/tool_result_storage.py`.
- Encrypt scoped spill payloads with AES-GCM and authenticate session scope plus plaintext digest.
- Hide bearer tokens from filenames and validate scope, digest, symlink/reparse metadata, file identity, type, ownership, mode, AEAD tag, and plaintext digest.
- Intercept capabilities in `tools/file_tools.py` before ordinary backend/path routing.
- Propagate session IDs through `agent/tool_executor.py`, `model_tools.py`, and nested local/remote `execute_code` RPC.
- Add a capability-only `read_file` handler to the Hermes MCP transport; ordinary filesystem paths remain rejected there.
- Add focused regression tests for exact recovery, cross-session denial, encrypted storage, filesystem attacks, scoped write failure, MCP transport, central dispatch, and RPC propagation.

## How to Test

```bash
python -m pytest -q \
  tests/tools/test_tool_result_capability.py \
  tests/run_agent/test_tool_call_incremental_persistence.py \
  tests/tools/test_code_execution.py \
  tests/tools/test_code_execution_modes.py

uv run --extra mcp python -m pytest -q \
  tests/agent/transports/test_hermes_tools_mcp_server.py

python -m pytest -q \
  tests/agent/transports/test_codex_app_server_runtime.py \
  tests/run_agent/test_codex_app_server_integration.py \
  tests/cli/test_cli_codex_context_reference.py \
  tests/agent/transports/test_codex_transport.py

python -m pytest -q \
  tests/test_transform_tool_result_hook.py \
  tests/run_agent/test_run_agent.py \
  -k 'session_id or transform_tool_result'

python -m ruff check \
  tools/tool_result_storage.py tools/file_tools.py tools/code_execution_tool.py \
  model_tools.py agent/tool_executor.py agent/transports/hermes_tools_mcp_server.py \
  tests/tools/test_tool_result_capability.py \
  tests/agent/transports/test_hermes_tools_mcp_server.py \
  tests/run_agent/test_tool_call_incremental_persistence.py \
  tests/tools/test_code_execution.py tests/tools/test_code_execution_modes.py

git diff --check origin/main...HEAD
scripts/run_tests.sh
```

Verification after the final rebase onto current `origin/main` (`5dd15872a6`):

- 106 passed + 7 subtests — capability/storage, incremental persistence, execute-code local/mode coverage.
- 12 passed — Hermes MCP transport under the pinned MCP extra.
- 147 passed — Codex app-server runtime/integration, context reference, and transport.
- 6 passed, 260 deselected — dispatch session-ID and transform-hook focus.
- Ruff passed on all changed Python files.
- `py_compile` passed on changed production modules and the capability test.
- `git diff --check` passed.
- Stable patch ID is unchanged from the independently reviewed pre-rebase commit: `629678ef5cc8f0c2b7a7bcad56040c096ac62df3`.
- Full `scripts/run_tests.sh` differential was run immediately before the final five-commit upstream advance: the feature and a clean sparse checkout of exact base `74f99af470` both reported the same 81 failures across the same 23 files. None of those files is changed by this PR. After the final rebase to `5dd15872a6`, every affected suite above was rerun green and the stable patch ID remained unchanged.

## Checklist

### Code

- [x] I've read the Contributing Guide.
- [x] My commit follows Conventional Commits.
- [x] I searched existing PRs and issues and documented the overlapping work above.
- [x] My PR contains only changes related to this capability/security layer.
- [ ] I've run the preferred full wrapper, but this macOS environment is not baseline-green: feature and exact-base runs both report the same 81 failures in the same 23 unrelated files. The differential is clean and the affected suites pass; GitHub CI remains the platform-matrix arbiter.
- [x] I've added tests for my changes.
- [x] I've tested on macOS 26.4, Apple Silicon.

### Documentation & Housekeeping

- [x] Documentation update: N/A — no public config or user-facing command is added.
- [x] `cli-config.yaml.example`: N/A — no config keys are added or changed.
- [x] `CONTRIBUTING.md` / `AGENTS.md`: N/A — no workflow or architecture policy is changed.
- [x] Cross-platform impact considered; Windows reparse metadata and POSIX filesystem boundaries have focused coverage.
- [x] Tool descriptions/schemas updated where behavior changed: the MCP reader is explicitly capability-only and rejects ordinary paths.

## Screenshots / Logs

Not applicable. The behavior and security boundaries are exercised by automated tests and exact recovery probes.
