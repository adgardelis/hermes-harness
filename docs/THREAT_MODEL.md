# HERMES HARNESS — Threat model and attack matrix

Scope: the session-bound spill/recovery mechanism at upstream Hermes Agent commit
`49b044a322b5a87e4f45fb18e73d09d0b204165e` (draft PR NousResearch/hermes-agent#89582).
Line references below are to `tools/tool_result_storage.py` (624 lines) and
`tools/file_tools.py` at that commit. Test references are to
`tests/tools/test_tool_result_capability.py` (270 lines) at the same commit.
`tests/tools/test_result_spill.py` does **not** exist at that commit; the earlier
legacy spill tests were folded into the capability suite.

## 1. System overview and trust boundaries

Oversized tool results are written to `$HERMES_HOME/cache/spillover` as
`spill_{scope}_{digest}_{locator}.bin`: AES-GCM ciphertext whose key is
`SHA-256(capability)`, where `capability` is a 128-bit random token
(`secrets.token_hex(16)`). AAD binds `hermes-spill-v1:{scope}:{digest}`. The
model receives a bounded preview plus an opaque URI
`hermes-spill://v1/{scope}/{digest}/{capability}`. `resolve_spill_capability`
re-checks scope, filesystem invariants, AEAD tag, and plaintext digest before
returning bytes.

Trust boundaries:

- **Model-facing boundary.** The provider sees only the preview and the URI.
  Recovery re-enters through Hermes `read_file` (`tools/file_tools.py:1691`
  routes `hermes-spill://v1/` paths to `resolve_spill_capability` before any
  backend path handling, `:1632–1635`).
- **Filesystem boundary.** The spillover dir lives host-side under
  `$HERMES_HOME`. It is trusted to be 0700, owner-only, and free of attacker
  pre-planted entries. Resolution defends individual files against
  symlink/reparse/FIFO/device substitution.
- **Session/capability boundary.** The scope is `SHA-256(session_id)`; a URI
  minted for one session must not resolve in another. The capability token is
  a bearer secret: possession equals decryptability.
- **Provider boundary.** The URI and preview cross the provider API. Payload
  bytes do not, unless the same session later recovers them.

## 2. Assets

- **Payload confidentiality at rest.** Full tool output on disk must not be
  plaintext. Enforced by AES-GCM write (`_write_capability_spillover`).
- **Payload integrity and exact recovery.** Recovered bytes must equal the
  spilled bytes. Enforced by GCM tag plus post-decrypt SHA-256 digest
  comparison with `hmac.compare_digest`.
- **Capability unforgeability / confidentiality.** The URI contains the key
  material; it must be unguessable and must not leak into host paths, logs,
  or filenames. Filename uses `SHA-256(capability)`, not the token itself.
- **Session isolation.** Cross-session resolution must fail closed.
- **Fail-closed degradation.** When capability minting fails for a scoped
  session, the model must not receive a predictable host path or a raw host
  path downgrade.

## 3. Attacker models

1. **Malicious tool output content.** A tool returns adversarial bytes (path
   strings, URI-shaped text, heredoc markers) hoping to influence later
   handling or exfiltrate other payloads.
2. **Cross-session process as the same OS user.** A second Hermes session
   (different `session_id`) holds or guesses another session's URI and calls
   `read_file` on it.
3. **Other local OS user.** No access to `$HERMES_HOME` expected; relies on
   mode/ownership enforcement.
4. **Prompt injection seeking capability exfiltration.** Injected text tries
   to make the model print a previously seen URI or re-resolve it across a
   session boundary.
5. **Spill-dir tampering.** An attacker (or accident) renames, swaps,
   symlink-substitutes, chmods, or rewrites spill files between write and
   read.

## 4. Attack matrix

| # | Attack | Vector | Defense in code (commit `49b044a`) | Residual risk | Test / evidence |
|---|---|---|---|---|---|
| 1 | Cross-session recovery | Session B submits session A's URI to `read_file` | Scope check with `hmac.compare_digest` against `SHA-256(session_id)` in `resolve_spill_capability` (~L262–267) | Low. Scope is a hash of the session id; protection assumes distinct session ids are not guessable-but-equal. Unverified: session-id entropy is an upstream property, not enforced here | `test_cross_session_and_tampered_capabilities_fail_closed`; `test_reused_tool_call_id_cannot_collide_across_sessions` |
| 2 | Capability guessing / brute force | Attacker fabricates URIs | 128-bit random capability (`secrets.token_hex(16)`) + strict URI grammar `_CAPABILITY_URI_RE` (~L80–86) | Low for remote injection; same-user local attacker can list the spill dir — see limitations | Grammar rejection covered inside cross-session test |
| 3 | Plaintext at rest | Spill dir read directly | AES-GCM encrypt before write; file created `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW`, mode 0600; dir 0700 (`_write_capability_spillover`, ~L199–L240) | Key is in the URI, not a separate keystore — see limitations | `test_capability_payload_is_not_plaintext_at_rest_or_named_with_bearer_token` |
| 4 | Bearer-token leak via filename | `ls` of spill dir reveals capability | Filename stores `SHA-256(capability)` locator, not the token (`_capability_filename`) | Low | Same test as #3 |
| 5 | Path downgrade on storage failure | Scoped session fails open to predictable host path | Explicit no-downgrade branch in `maybe_persist_tool_result`: emits bounded preview with "no recovery path was emitted" | None identified for scoped sessions; legacy unscoped callers still get host paths by design | `test_scoped_write_failure_never_downgrades_to_host_path` |
| 6 | Symlink swap before read | Replace spill file with symlink to attacker file | `os.lstat` + `S_ISLNK` check, `O_NOFOLLOW` on open, `lstat`/`fstat` dev+ino identity check (`resolve_spill_capability`, ~L270–L295) | TOCTOU window between `lstat` and `open` is narrowed by `O_NOFOLLOW` + dev/ino re-check but not eliminated on filesystems lacking `O_NOFOLLOW` (`_O_NOFOLLOW` falls back to 0, e.g. some Windows builds) | `test_symlink_swap_and_payload_tampering_fail_closed` |
| 7 | Windows reparse-point swap | Junction/reparse substitution | `st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT` checked from `lstat` metadata before open | Only as strong as the metadata the OS reports; covered by a mock-based test, not yet by a real NTFS junction test — CI (v0.2) is intended to close this | `test_reparse_metadata_is_rejected_before_open` |
| 8 | FIFO/device substitution | Block or hang the reader on a special file | `O_NONBLOCK` on open, `S_ISREG` check on `fstat` | Low on POSIX; special-file semantics differ on Windows | `test_fifo_replacement_fails_closed_without_blocking` |
| 9 | Permission/ownership weakening | Attacker chmods/chowns the file | Mode must equal exactly 0600 (non-Windows), `st_uid` must equal `os.getuid()` | On Windows the mode check is skipped (`os.name == "nt"`); NTFS ACLs are the only control, and they are not verified by this code | Indirectly via tamper tests |
| 10 | Ciphertext/payload tampering | Rewrite spill file contents | GCM tag (InvalidTag → fail closed) + post-decrypt SHA-256 digest vs URI digest, constant-time compare | None identified | Tamper half of `test_symlink_swap_and_payload_tampering_fail_closed` |
| 11 | Error-message path leak | Exception strings reveal host paths | Single safe error string `_SAFE_CAPABILITY_ERROR`; all `OSError`/`UnicodeDecodeError`/`InvalidTag` collapse into it (`from None`) | Low | Implicit across suite (all failure tests assert only `SpillCapabilityError`) |
| 12 | Malicious content crafting fake spill notices | Tool output containing `<persisted-output>` or fake URIs | Model-side parsing is upstream; recovery still requires a real capability that passes scope+AEAD+digest, so forged URIs fail closed at resolve time | A forged notice could waste turns (DoS-flavored), not leak data. Unverified: no dedicated test for content mimicking the tag | None at this commit — gap worth flagging |
| 13 | Prompt injection exfiltrating a URI | Model asked to print a previously seen URI to an attacker-controlled channel | Out of mechanism scope — the URI is a bearer token and the model legitimately holds it. Mitigation is provider/agent-level output policy, not this layer | Real and documented; see limitations | N/A — architectural boundary |
| 14 | Concurrent cleanup vs read | Hourly/`_prune_spillover_once` sweep deletes a file mid-resolution | Deletion is by mtime age (24h default); a live read race yields `OSError` → fail closed, never wrong bytes | Availability loss only; no integrity impact | Unverified — no explicit race test |

## 5. Known limitations and out of scope

- **The URI is the key.** The AES key is `SHA-256(capability)`, and the
  capability travels inside the URI shown to the model. Anyone who obtains
  the URI *and* can execute in the same session scope *and* pass the local
  file checks can decrypt. There is no separate key store, key rotation, or
  per-file key. This is a deliberate bearer-capability design, documented
  here so it is not mistaken for envelope encryption.
- **Same-user local attacker with full filesystem access** is out of scope.
  Such an attacker can read `$HERMES_HOME/cache/spillover`, wait for a URI to
  appear in a transcript or log, and attempt resolution in-process; the
  dev/ino/mode/owner checks do not defend against the owning user.
- **Other local OS users** are defended only by 0700 dir / 0600 file modes
  and the `st_uid` check. On Windows the mode check is skipped; protection
  rests on default NTFS ACLs, which this code does not verify (unverified in
  CI today — the reparse-point CI job in v0.2 narrows but does not close
  this).
- **Prompt-injection exfiltration (attack #13)** is an agent-governance
  problem. The mechanism guarantees that an injected URI replay *in another
  session* fails closed; it cannot stop the owning session from being
  talked into revealing data.
- **Redaction boundary.** The preview (`generate_preview`) is a byte-count
  truncation with newline snapping — it does not redact secrets. A secret in
  the first `preview_size` chars of a tool result reaches the provider
  exactly as it would without spilling. Spilling changes where the *full*
  payload lives, not what the preview exposes.
- **Cleanup races and lifetime.** Spill files persist up to
  `SPILLOVER_MAX_AGE_HOURS` (24h) or until gateway housekeeping /
  once-per-process prune removes them. There is no per-session revocation:
  a URI remains valid for its session until the file ages out.
- **Legacy unscoped path.** Callers without a `session_id` still receive
  host or sandbox paths (documented in the module docstring). Those paths
  are outside this capability threat model.
- **TOCTOU residue.** The `lstat` → `open(O_NOFOLLOW)` → `fstat` sequence is
  the standard narrowing pattern; on platforms where `O_NOFOLLOW` is absent
  the race window is larger. Marked unverified for Windows pending the CI
  reparse-point job.
- **Availability.** Nothing here prevents an attacker with spill-dir write
  access from deleting payloads (denial of recovery). Integrity is
  protected; availability is not.

Where a claim above could not be tied to source or tests at commit
`49b044a`, it is marked **unverified** rather than asserted.
