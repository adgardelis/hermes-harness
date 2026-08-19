# HERMES HARNESS launch kit

## One sentence

HERMES HARNESS is an improved adaptation of DeepSeek Harness, designed specifically to take advantage of capabilities native to Hermes.

## Short pitch

Large tool outputs waste agent context. Truncation saves tokens by destroying evidence. HERMES HARNESS moves oversized results out of immediate context, encrypts the full payload, leaves a compact preview, and gives the originating Hermes session an opaque capability for exact recovery.

## Proof points

- Native extension of Hermes Agent's existing storage, session, `read_file`, MCP, and execution layers
- AES-GCM encrypted storage with session-bound recovery
- Cross-session denial and filesystem hardening
- Independent final review: GO, no release blockers
- Upstream proposal: NousResearch/hermes-agent#89582
- No universal savings percentage claimed before a public multi-workload benchmark

## Hacker News

**Title:** HERMES HARNESS – Token economy with exact recovery for Hermes Agent

**Text:**

We studied DeepSeek Harness as a design source, but did not adopt its runtime. Instead, we built an improved Hermes-native adaptation around capabilities Hermes already owns: tool-result persistence, session identity, read_file, Codex MCP, and execute_code RPC.

Oversized tool results are replaced in model context by a compact preview and an opaque session-bound capability. The full payload is encrypted at rest and can be recovered exactly by the originating session. Cross-session reads fail closed.

The repository includes the architecture, threat boundary, focused verification evidence, independent review, frozen upstream patch, and a draft contribution to Hermes Agent. It is a research preview, not yet a one-command installer. We would especially value review of the security model and reproducible token-economy workloads.

## X / LinkedIn

Launching **HERMES HARNESS**: an improved adaptation of DeepSeek Harness designed specifically for capabilities native to Hermes.

Large tool outputs leave the model context. Exact encrypted evidence remains recoverable by the originating session.

- ✓ context-scaled budgets
- ✓ AES-GCM spill storage
- ✓ session-bound capabilities
- ✓ Hermes read_file + Codex MCP
✓ upstream PR open

No invented savings claims—public benchmarks are next.

https://github.com/adgardelis/hermes-harness

## Reddit / Discord

I have released HERMES HARNESS as a public research preview. The project adapts selected ideas from DeepSeek Harness into Hermes Agent's native architecture instead of running a second harness runtime.

The current capability layer addresses a common agent problem: huge tool results consume context repeatedly, while naive truncation destroys evidence. HERMES HARNESS spills oversized output as encrypted data, leaves a compact model-facing preview, and exposes an opaque capability that only the originating session can resolve.

I am looking for technical feedback on the threat model, cross-platform behavior, and representative workloads for an honest before/after token benchmark.

Repository: https://github.com/adgardelis/hermes-harness

Upstream PR: https://github.com/NousResearch/hermes-agent/pull/89582

## Promotion sequence

1. Ask Hermes Agent maintainers for technical feedback on the open PR; do not lead with branding inside maintainer review.
2. Publish the benchmark harness and raw workload data.
3. Record a 60–90 second terminal demo showing spill, preview, recovery, and cross-session denial.
4. Post to the Nous Research community channel for plugins/skills and Hermes development.
5. Submit to Hacker News after the benchmark and demo are public.
6. Post the same evidence package to relevant Reddit communities, X, and LinkedIn.
7. Respond quickly and technically; convert repeated questions into documentation and issues.

The fame strategy is credibility compounding: a memorable name, one clear problem, visible proof, honest limits, upstream engagement, and fast community response.
