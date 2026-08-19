## HERMES HARNESS

This PR contributes the recoverable tool-result capability layer of **HERMES HARNESS**, the Hermes-native context and tool-result economy system.

**Naming boundary:** DeepSeek Harness/DSH is research provenance only. This is not an installation of the DSH runtime; it is a native extension of Hermes Agent's existing result-storage architecture.

## Summary

- bind oversized model-facing tool results to opaque `hermes-spill://v1/...` capabilities scoped to the current Hermes session;
- resolve capabilities host-side through `read_file` before ordinary backend path routing;
- preserve the existing path-based spillover behavior only for legacy callers without session context;
- support direct transports and Codex MCP, including capability-only `read_file` registration;
- propagate session scope through concurrent/sequential agent execution and nested local/remote `execute_code` RPC calls.

## Security properties

- scoped persistence fails closed to a bounded preview if capability storage is unavailable; it never downgrades to a predictable host or sandbox path;
- payloads are AES-GCM authenticated ciphertext at rest;
- the bearer token is present only in the URI; filenames contain its SHA-256 locator, not the token itself;
- the session scope and plaintext digest are authenticated as AES-GCM associated data;
- resolution validates session scope, bearer token-derived filename, symlink/reparse status, opened-file identity, regular-file type, POSIX mode/ownership where available, AEAD tag, and plaintext digest;
- FIFO/device replacements are opened nonblocking and rejected as non-regular files;
- ordinary filesystem paths remain rejected by the Codex capability reader.

## Compatibility

- capability encryption keys are deterministically derived from the random bearer token in the URI, so valid capabilities remain recoverable after process restart without a profile-wide secret;
- local, Docker, SSH, Modal, and Daytona legacy spill behavior is unchanged for callers without a session ID;
- direct `model_tools.handle_function_call` transports now use the same persistence seam as the agent executor;
- `execute_code` forwards the parent session ID through both UDS and remote file-RPC dispatch.

## Verification

Fresh focused runs on commit `d0155e2c83011ef0ed7b5b1d39bf2640c3daa5dc`:

- `152 passed, 7 subtests passed` — result capability/storage, Codex MCP, execute-code local/mode coverage, incremental persistence;
- `57 passed` — Codex app-server runtime/integration and context tracking;
- `9 passed` — dispatch session-ID and transform-hook behavior;
- `1 passed` — capability-specific `read_file` path;
- `git diff --check` clean;
- changed production modules compile with `py_compile`.

A broad macOS `tests/tools/test_file_tools.py` run has two unrelated existing assertions that expect `/tmp/...` while the implementation canonicalizes it to `/private/tmp/...`; the capability-specific read path passes.

## Scope

This extends the existing `tools/tool_result_storage.py` mechanism rather than introducing a second storage engine. It does not add the DeepSeek Harness runtime, Cordis, web application, or SurfaceOp abstractions.
