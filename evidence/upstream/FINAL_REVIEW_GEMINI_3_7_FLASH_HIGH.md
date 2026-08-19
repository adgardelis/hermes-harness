# Final Antigravity Review — Gemini 3.7 Flash High

**Frozen commit:** `d0155e2c83011ef0ed7b5b1d39bf2640c3daa5dc`  
**Base:** `origin/main` (`b359db72ee53e052a31066f9fcac2f3ba0566a49`)

## VERDICT: GO

### Release blockers

None.

### Confirmed findings

- AES-GCM uses a random 96-bit nonce, a key deterministically derived from the 128-bit random bearer token, and associated data binding the session-scope hash and plaintext digest.
- Filenames contain `sha256(capability)` rather than the bearer token.
- Restart recovery is process-independent because the URI carries the random token used to derive the key.
- Wrong-session and tampered capabilities fail closed with a generic error.
- Scoped write failure returns a bounded preview and never downgrades to a predictable path.
- Writes use exclusive creation and owner-only permissions; reads validate lstat/fstat identity, file type, POSIX mode/ownership, symlink/reparse status, AEAD tag, and digest. FIFO reads are nonblocking and rejected.
- Codex MCP exposes a capability-only reader and uses the MCP session ID.
- Direct transport, concurrent/sequential agent paths, and local/remote `execute_code` RPC propagate session scope.
- Legacy callers without session context retain the existing path behavior.

### Independent test evidence

```text
tests/tools/test_tool_result_capability.py: 13 passed
tests/agent/transports/test_hermes_tools_mcp_server.py: 12 passed
tests/run_agent/test_tool_call_incremental_persistence.py + capability suite: 26 passed
tests/tools/test_code_execution.py: 43 passed
```

### Non-blocking observation

`TestRpcTokenAuthorization._drive_server` could explicitly call `shutdown(SHUT_RDWR)` before socket close to make background-thread termination more deterministic in combined-suite runs. This is test hygiene, not a production blocker.

### Key citations

- `tools/tool_result_storage.py:101-116` — locator, AAD, key derivation
- `tools/tool_result_storage.py:214-236` — exclusive encrypted write
- `tools/tool_result_storage.py:255-310` — scope, filesystem, AEAD, digest checks
- `tools/tool_result_storage.py:509-534` — scoped fail-closed and legacy fallback
- `agent/transports/hermes_tools_mcp_server.py:155-172` — capability-only MCP reader
- `tools/file_tools.py:1689-1697` — capability resolution before backend paths
- `tools/code_execution_tool.py:661,753,1031,1335` — nested session propagation
