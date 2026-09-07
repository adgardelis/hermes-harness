"""Deterministic synthetic workload generators for the HERMES HARNESS benchmark.

All payloads are 100% synthetic, generated from ``random.Random(seed)`` with a
fixed seed per workload, so any machine reproduces byte-identical fixtures.
Every workload plants sentinel facts at the head, middle, and tail so the
benchmark can measure head/tail evidence survival in previews and exact
recovery of the omitted middle.

No real user data, no real sessions, no secrets.
"""

from __future__ import annotations

import json
import random
import string

# Sentinel markers. Deterministic (not random) so a run can be audited against
# this file without re-generating payloads.
def _sentinel(workload: str, position: str) -> str:
    return f"SENTINEL-{workload.upper()}-{position.upper()}-7f3a9c2e"


# Planted fact for workload 2 (web extraction). This string is the "needle" the
# model would lose under naive middle-truncation.
PLANTED_FACT = (
    "PLANTED-FACT: The fictional Zorblax comet reaches perihelion every 417 "
    "years and was last observed in the year 1609."
)

_WORDS = (
    "alpha beta gamma delta epsilon zeta theta lambda sigma omega build "
    "compile link fetch parse render query index cache shard vertex fragment "
    "kernel driver socket packet buffer stream thread mutex ledger quorum"
).split()

_PATH_WORDS = (
    "src main lib core util net io fs db api cli gui test bench docs vendor"
).split()


def _rand_word(rng: random.Random) -> str:
    return rng.choice(_WORDS)


def _rand_text(rng: random.Random, n_words: int) -> str:
    return " ".join(_rand_word(rng) for _ in range(n_words))


def _pad_to_size(rng: random.Random, parts: list[str], target_chars: int,
                 line_fn) -> str:
    """Append generated lines until the joined payload reaches target_chars."""
    body = "\n".join(parts)
    while len(body) < target_chars:
        line = line_fn()
        parts.append(line)
        body += "\n" + line
    return body


# --------------------------------------------------------------------------
# Workload 1: long terminal / build output
# --------------------------------------------------------------------------

def terminal_log(target_chars: int = 480_000, seed: int = 1001) -> str:
    rng = random.Random(seed)
    head = _sentinel("terminal", "head")
    mid = _sentinel("terminal", "middle")
    tail = _sentinel("terminal", "tail")

    def line() -> str:
        kind = rng.random()
        if kind < 0.55:
            return (f"[{rng.randint(0, 86400):08d}] gcc -O2 -c "
                    f"src/{rng.choice(_PATH_WORDS)}/{_rand_word(rng)}_"
                    f"{rng.randint(0, 9999)}.c -o build/{_rand_word(rng)}.o")
        if kind < 0.8:
            return (f"warning: unused variable '{_rand_word(rng)}_{rng.randint(0, 999)}' "
                    f"[-Wunused-variable] at {_rand_word(rng)}.h:{rng.randint(1, 4000)}")
        if kind < 0.95:
            return f"  {_rand_text(rng, 12)}"
        return (f"ld: linking build/lib{_rand_word(rng)}.a "
                f"({rng.randint(1, 900)} objects, {rng.randint(1, 4096)} KB)")

    parts = [
        "$ make -j8 all",
        f"[00000000] {head} build started",
    ]
    # Fill the first ~40% before planting the middle sentinel.
    body = _pad_to_size(rng, parts, int(target_chars * 0.45), line)
    parts.append(f"[{rng.randint(0, 86400):08d}] {mid} mid-build checkpoint passed")
    body = _pad_to_size(rng, parts, target_chars - 200, line)
    parts.append(f"[{rng.randint(0, 86400):08d}] {tail} build finished: 0 errors")
    return "\n".join(parts)


# --------------------------------------------------------------------------
# Workload 2: web extraction with a fact planted in the omitted middle
# --------------------------------------------------------------------------

def web_extract(target_chars: int = 320_000, seed: int = 2002) -> str:
    rng = random.Random(seed)
    head = _sentinel("web", "head")
    mid = _sentinel("web", "middle")
    tail = _sentinel("web", "tail")

    def para() -> str:
        n = rng.randint(18, 40)
        text = _rand_text(rng, n)
        return text.capitalize() + "."

    parts = [
        "<extracted-text source=\"https://example.invalid/articles/comets\">",
        f"# Astronomy Notes  {head}",
        "",
    ]
    body = _pad_to_size(rng, parts, int(target_chars * 0.5), para)
    # The planted fact lives in the middle — exactly the region a preview omits.
    parts.append(f"{PLANTED_FACT}  [{mid}]")
    parts.append("")
    body = _pad_to_size(rng, parts, target_chars - 300, para)
    parts.append(f"End of extracted article.  {tail}")
    parts.append("</extracted-text>")
    return "\n\n".join(parts) if False else "\n".join(parts)


# --------------------------------------------------------------------------
# Workload 3: repository-wide search output
# --------------------------------------------------------------------------

def repo_search(target_chars: int = 400_000, seed: int = 3003) -> str:
    rng = random.Random(seed)
    head = _sentinel("search", "head")
    mid = _sentinel("search", "middle")
    tail = _sentinel("search", "tail")
    term = "handle_spill"

    def match_line() -> str:
        path = (f"{rng.choice(_PATH_WORDS)}/{rng.choice(_PATH_WORDS)}/"
                f"{_rand_word(rng)}_{rng.randint(0, 999)}.py")
        lineno = rng.randint(1, 5000)
        col = rng.randint(1, 120)
        ctx = _rand_text(rng, rng.randint(6, 14))
        return f"{path}:{lineno}:{col}: def {term}_{_rand_word(rng)}({ctx}):"

    parts = [
        f"$ rg --column '{term}' --stats  # {head}",
    ]
    body = _pad_to_size(rng, parts, int(target_chars * 0.5), match_line)
    parts.append(f"src/tools/deep/{_rand_word(rng)}.py:2049:9: {mid} def {term}_checkpoint():")
    body = _pad_to_size(rng, parts, target_chars - 200, match_line)
    parts.append(f"4317 matches in 812 files  {tail}")
    return "\n".join(parts)


# --------------------------------------------------------------------------
# Workload 4: structured JSON output
# --------------------------------------------------------------------------

def json_output(target_chars: int = 300_000, seed: int = 4004) -> str:
    rng = random.Random(seed)
    head = _sentinel("json", "head")
    mid = _sentinel("json", "middle")
    tail = _sentinel("json", "tail")

    records = [{
        "id": 0,
        "marker": head,
        "name": "record-00000",
        "value": 0,
        "tags": ["synthetic", "benchmark"],
    }]
    i = 1
    # Grow the record list until the serialized form reaches the target.
    while True:
        records.append({
            "id": i,
            "name": f"record-{i:05d}",
            "value": rng.randint(0, 10**9),
            "score": round(rng.uniform(0, 1), 6),
            "tags": [_rand_word(rng) for _ in range(rng.randint(1, 5))],
            "blob": "".join(rng.choice(string.ascii_lowercase) for _ in range(40)),
        })
        i += 1
        if i % 200 == 0 and len(json.dumps(records)) > target_chars * 0.5 \
                and not any(r.get("marker") == mid for r in records):
            records.append({"id": i, "marker": mid, "name": f"record-{i:05d}",
                            "value": -1})
            i += 1
        if i % 200 == 0 and len(json.dumps(records)) > target_chars - 4_000:
            break
    records.append({"id": i, "marker": tail, "name": f"record-{i:05d}",
                    "value": -2})
    return json.dumps({"generated": "synthetic", "records": records}, indent=2)


# --------------------------------------------------------------------------
# Workload 5: multiple large tool results in one assistant turn
# --------------------------------------------------------------------------

def multi_tool_turn(per_result_chars: int = 120_000, n_results: int = 5,
                    seed: int = 5005) -> list[dict]:
    """Return tool-message dicts like the agent loop collects in one turn.

    Aggregate size (~600K chars) exceeds every profile's turn budget, so
    ``enforce_turn_budget`` must spill results until the turn fits.
    """
    rng = random.Random(seed)
    messages: list[dict] = []
    for k in range(n_results):
        head = _sentinel("turn", f"r{k}-head")
        mid = _sentinel("turn", f"r{k}-middle")
        tail = _sentinel("turn", f"r{k}-tail")

        def line() -> str:
            return (f"tool{k} event={rng.randint(0, 10**6)} "
                    f"status={rng.choice(['ok', 'ok', 'ok', 'warn'])} "
                    f"{_rand_text(rng, 10)}")

        parts = [f"=== tool {k} output start {head} ==="]
        _pad_to_size(rng, parts, int(per_result_chars * 0.5), line)
        parts.append(f"--- {mid} ---")
        _pad_to_size(rng, parts, per_result_chars - 200, line)
        parts.append(f"=== tool {k} output end {tail} ===")
        messages.append({
            "role": "tool",
            "tool_call_id": f"bench-call-{k:04d}",
            "content": "\n".join(parts),
        })
    return messages


WORKLOADS = {
    "terminal_log": terminal_log,
    "web_extract": web_extract,
    "repo_search": repo_search,
    "json_output": json_output,
    "multi_tool_turn": multi_tool_turn,
}
