#!/usr/bin/env python3
"""HERMES HARNESS public benchmark runner (issue #1).

Measures the capability-spill mechanism in Hermes Agent's
``tools/tool_result_storage.py`` at the pinned upstream commit, across
synthetic workloads and context-window budget profiles:

- model-facing input characters before vs. after persistence;
- end-to-end persist latency, raw spill-write latency, resolve latency;
- exact round-trip recovery fidelity (byte equality);
- head/tail sentinel survival in the inline preview vs. the recovered body;
- turn-budget behavior for the multi-tool workload;
- provider cache telemetry: recorded as N/A offline (schema documented in
  benchmarks/README.md). No fabricated numbers.

Stdlib + ``cryptography`` only. Cross-platform (macOS/Linux/Windows).

Usage:
    python3 benchmarks/run_benchmarks.py --out results/<dir> [--check] \
        [--module-path /path/to/hermes-agent-at-49b044a]

The module path must point at a checkout of Hermes Agent commit
49b044a322b5a87e4f45fb18e73d09d0b204165e. Locally we use a git worktree;
CI can use a shallow fetch of that commit instead (see benchmarks/README.md).

NOTE: this benchmark intentionally imports the module's private
``_write_capability_spillover`` to time the raw spill write. That is a
research measurement of exactly this commit, not a supported API surface.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fixtures  # noqa: E402

PINNED_COMMIT = "49b044a322b5a87e4f45fb18e73d09d0b204165e"
DEFAULT_MODULE_PATH = "/tmp/hh-bench-49b044a"

# Context windows (tokens) for the benchmark profiles. Per-result / per-turn
# char budgets are NOT hardcoded here — they are derived at runtime by the
# module's own budget_for_context_window() so the benchmark measures the
# module's real scaling behavior.
PROFILE_CONTEXT_WINDOWS = {
    "profile-32k": 32_768,
    "profile-131k": 131_072,
    "profile-1m": 1_048_576,
}

REPS = 3  # timed repetitions per measurement; median reported
SESSION_ID = "bench-session-0001"
WRONG_SESSION_ID = "bench-session-9999"

_URI_RE = re.compile(r"hermes-spill://v1/[0-9a-f]{64}/[0-9a-f]{64}/[0-9a-f]{32}")


def _cpu_brand() -> str:
    if sys.platform == "darwin":
        try:
            out = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, timeout=5,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except Exception:
            pass
    return platform.processor() or "unknown"


def _median_ms(samples: list[float]) -> float:
    return round(statistics.median(samples) * 1000.0, 3)


def _time_calls(fn, reps: int = REPS):
    """Return (last_result, median_ms)."""
    samples = []
    result = None
    for _ in range(reps):
        t0 = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - t0)
    return result, _median_ms(samples)


def run_benchmarks(module_path: str) -> dict:
    # Isolate all spill artifacts in a private temp HERMES_HOME; cleaned up by
    # the caller. Set before any module call that resolves get_hermes_home().
    hermes_home = tempfile.mkdtemp(prefix="hh-bench-hermes-home-")
    os.environ["HERMES_HOME"] = hermes_home

    sys.path.insert(0, module_path)
    import cryptography  # noqa: E402
    from tools import tool_result_storage as trs  # noqa: E402
    from tools import budget_config  # noqa: E402

    # Derived profiles: the module's own scaling function is the source of truth.
    profiles = {}
    for name, window in PROFILE_CONTEXT_WINDOWS.items():
        cfg = budget_config.budget_for_context_window(window)
        profiles[name] = {
            "context_window_tokens": window,
            "per_result_budget_chars": cfg.default_result_size,
            "per_turn_budget_chars": cfg.turn_budget,
            "preview_size_chars": cfg.preview_size,
            "config": cfg,
        }

    # Pre-generate all fixture payloads once (profiles share them).
    payloads = {
        name: gen() for name, gen in fixtures.WORKLOADS.items()
        if name != "multi_tool_turn"
    }

    results = []
    failures = []

    for wname, content in payloads.items():
        for pname, prof in profiles.items():
            rec = _run_single_result_workload(
                trs, wname, content, pname, prof, failures)
            results.append(rec)

    # Workload 5: turn-budget enforcement across multiple large tool results.
    for pname, prof in profiles.items():
        rec = _run_turn_budget_workload(trs, pname, prof, failures)
        results.append(rec)

    out = {
        "benchmark": "hermes-harness issue #1 public benchmark",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "module": {
            "repo": "NousResearch/hermes-agent (upstream proposal)",
            "commit": PINNED_COMMIT,
            "file": "tools/tool_result_storage.py",
            "note": ("Private function _write_capability_spillover imported "
                     "for raw spill-write timing; research use only."),
        },
        "environment": {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "cpu": _cpu_brand(),
            "python": sys.version.split()[0],
            "python_implementation": platform.python_implementation(),
            "cryptography": cryptography.__version__,
        },
        "cache_telemetry": {
            "available": False,
            "prompt_cache_hit_tokens": None,
            "prompt_cache_miss_tokens": None,
            "note": ("N/A offline: no provider API is called by this "
                     "benchmark. Schema documented in benchmarks/README.md."),
        },
        "profiles": {
            name: {k: v for k, v in prof.items() if k != "config"}
            for name, prof in profiles.items()
        },
        "reps_per_measurement": REPS,
        "results": results,
        "failures": failures,
    }
    return out, hermes_home


def _sentinel_positions(wname: str, content: str) -> dict:
    """Locate planted sentinels; used for head/tail survival checks."""
    base = {
        "terminal_log": "TERMINAL",
        "web_extract": "WEB",
        "repo_search": "SEARCH",
        "json_output": "JSON",
    }[wname]
    return {
        "head": f"SENTINEL-{base}-HEAD-7f3a9c2e",
        "middle": f"SENTINEL-{base}-MIDDLE-7f3a9c2e",
        "tail": f"SENTINEL-{base}-TAIL-7f3a9c2e",
    }


def _run_single_result_workload(trs, wname, content, pname, prof, failures):
    cfg = prof["config"]
    threshold = prof["per_result_budget_chars"]
    sentinels = _sentinel_positions(wname, content)
    tool_name = f"bench_{wname}"
    before_chars = len(content)
    error = None
    fidelity = False
    persisted_msg = ""
    uri = None
    recovered = ""
    persist_ms = spill_ms = resolve_ms = None
    cross_session_denied = None

    try:
        # End-to-end model-facing path (preview build + spill write + message).
        persisted_msg, persist_ms = _time_calls(
            lambda: trs.maybe_persist_tool_result(
                content=content,
                tool_name=tool_name,
                tool_use_id=f"{tool_name}-0001",
                env=None,
                config=cfg,
                threshold=threshold,
                session_id=SESSION_ID,
            )
        )
        m = _URI_RE.search(persisted_msg)
        if m:
            uri = m.group(0)
        # Raw spill-write timing (private API; research measurement only).
        raw_uri, spill_ms = _time_calls(
            lambda: trs._write_capability_spillover(content, SESSION_ID))
        # Resolve timing + exact-byte fidelity from the persisted-message URI.
        if uri is not None:
            recovered, resolve_ms = _time_calls(
                lambda: trs.resolve_spill_capability(uri, SESSION_ID))
            fidelity = recovered == content
            # Cross-session denial: must raise SpillCapabilityError.
            try:
                trs.resolve_spill_capability(uri, WRONG_SESSION_ID)
                cross_session_denied = False
            except trs.SpillCapabilityError:
                cross_session_denied = True
        if uri is None:
            raise RuntimeError("no capability URI in persisted message")
        if raw_uri is None:
            raise RuntimeError("_write_capability_spillover returned None")
    except Exception as exc:  # record failure cases, don't hide them
        error = f"{type(exc).__name__}: {exc}"
        failures.append({"workload": wname, "profile": pname, "error": error})

    preview_region = persisted_msg  # the whole model-facing replacement
    rec = {
        "workload": wname,
        "profile": pname,
        "kind": "single_result",
        "input_chars_before": before_chars,
        "inline_chars_after": len(persisted_msg),
        "chars_reduction_ratio": (
            round(1 - len(persisted_msg) / before_chars, 6)
            if before_chars else None
        ),
        "persist_e2e_ms": persist_ms,
        "spill_write_ms": spill_ms,
        "resolve_ms": resolve_ms,
        "fidelity_exact_bytes": fidelity,
        "head_sentinel_in_preview": sentinels["head"] in preview_region,
        "tail_sentinel_in_preview": sentinels["tail"] in preview_region,
        "middle_sentinel_in_preview": sentinels["middle"] in preview_region,
        "head_sentinel_recovered": sentinels["head"] in recovered,
        "middle_sentinel_recovered": sentinels["middle"] in recovered,
        "tail_sentinel_recovered": sentinels["tail"] in recovered,
        "cross_session_denied": cross_session_denied,
        "error": error,
    }
    return rec


def _run_turn_budget_workload(trs, pname, prof, failures):
    cfg = prof["config"]
    messages = fixtures.multi_tool_turn()
    before_total = sum(len(m["content"]) for m in messages)
    error = None
    enforce_ms = None
    spilled = 0
    resolved_ok = 0
    head_in_preview = 0
    fidelity_all = True

    try:
        def _enforce():
            # Fresh deep copy each rep so repeated reps don't see already-
            # persisted messages.
            import copy
            msgs = copy.deepcopy(messages)
            return trs.enforce_turn_budget(
                msgs, env=None, config=cfg, session_id=SESSION_ID)
        enforced, enforce_ms = _time_calls(_enforce)

        after_total = sum(len(m["content"]) for m in enforced)
        for idx, (orig, msg) in enumerate(zip(messages, enforced)):
            content = msg["content"]
            if trs.PERSISTED_OUTPUT_TAG in content:
                spilled += 1
                if (f"SENTINEL-TURN-R{idx}-HEAD-7f3a9c2e" in content):
                    head_in_preview += 1
                m = _URI_RE.search(content)
                if m:
                    try:
                        rec = trs.resolve_spill_capability(
                            m.group(0), SESSION_ID)
                        if rec != orig["content"]:
                            fidelity_all = False
                        else:
                            resolved_ok += 1
                    except trs.SpillCapabilityError:
                        fidelity_all = False
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        failures.append({"workload": "multi_tool_turn", "profile": pname,
                         "error": error})
        after_total = before_total

    return {
        "workload": "multi_tool_turn",
        "profile": pname,
        "kind": "turn_budget",
        "n_tool_results": len(messages),
        "input_chars_before": before_total,
        "inline_chars_after": after_total,
        "chars_reduction_ratio": (
            round(1 - after_total / before_total, 6) if before_total else None
        ),
        "enforce_turn_budget_ms": enforce_ms,
        "results_spilled": spilled,
        "spilled_results_recovered_exact": resolved_ok,
        "head_sentinel_in_preview_count": head_in_preview,
        "fidelity_exact_bytes": fidelity_all and error is None,
        "error": error,
    }


def write_summary(data: dict, path: str) -> None:
    lines = []
    env = data["environment"]
    lines.append("# HERMES HARNESS benchmark summary")
    lines.append("")
    lines.append(f"- Generated (UTC): {data['generated_utc']}")
    lines.append(f"- Module under test: `{data['module']['file']}` @ "
                 f"`{data['module']['commit']}`")
    lines.append(f"- Environment: {env['os']} {env['os_release']} "
                 f"({env['machine']}), {env['cpu']}, "
                 f"Python {env['python']} "
                 f"({env['python_implementation']}), "
                 f"cryptography {env['cryptography']}")
    lines.append(f"- Cache telemetry: N/A offline "
                 f"(schema in benchmarks/README.md)")
    lines.append(f"- Timed reps per measurement: "
                 f"{data['reps_per_measurement']} (median reported)")
    lines.append("")
    lines.append("## Profiles (derived by the module's "
                 "`budget_for_context_window`)")
    lines.append("")
    lines.append("| profile | context window (tokens) | per-result budget "
                 "(chars) | per-turn budget (chars) | preview (chars) |")
    lines.append("|---|---|---|---|---|")
    for name, p in data["profiles"].items():
        lines.append(
            f"| {name} | {p['context_window_tokens']:,} | "
            f"{p['per_result_budget_chars']:,} | "
            f"{p['per_turn_budget_chars']:,} | {p['preview_size_chars']:,} |")
    lines.append("")
    lines.append("## Single-result workloads")
    lines.append("")
    lines.append("| workload | profile | before (chars) | after (chars) | "
                 "reduction | persist e2e (ms) | spill write (ms) | "
                 "resolve (ms) | fidelity | head in preview | "
                 "tail in preview | middle recovered | tail recovered | "
                 "cross-session denied |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in data["results"]:
        if r["kind"] != "single_result":
            continue
        lines.append(
            f"| {r['workload']} | {r['profile']} | "
            f"{r['input_chars_before']:,} | {r['inline_chars_after']:,} | "
            f"{r['chars_reduction_ratio']:.4f} | {r['persist_e2e_ms']} | "
            f"{r['spill_write_ms']} | {r['resolve_ms']} | "
            f"{'PASS' if r['fidelity_exact_bytes'] else 'FAIL'} | "
            f"{r['head_sentinel_in_preview']} | "
            f"{r['tail_sentinel_in_preview']} | "
            f"{r['middle_sentinel_recovered']} | "
            f"{r['tail_sentinel_recovered']} | "
            f"{r['cross_session_denied']} |")
    lines.append("")
    lines.append("## Turn-budget workload (multiple large tools in one turn)")
    lines.append("")
    lines.append("| profile | results | before (chars) | after (chars) | "
                 "reduction | enforce (ms) | spilled | recovered exact | "
                 "fidelity |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in data["results"]:
        if r["kind"] != "turn_budget":
            continue
        lines.append(
            f"| {r['profile']} | {r['n_tool_results']} | "
            f"{r['input_chars_before']:,} | {r['inline_chars_after']:,} | "
            f"{r['chars_reduction_ratio']:.4f} | "
            f"{r['enforce_turn_budget_ms']} | {r['results_spilled']} | "
            f"{r['spilled_results_recovered_exact']} | "
            f"{'PASS' if r['fidelity_exact_bytes'] else 'FAIL'} |")
    lines.append("")
    if data["failures"]:
        lines.append("## Failures")
        lines.append("")
        for f in data["failures"]:
            lines.append(f"- {f['workload']} / {f['profile']}: {f['error']}")
        lines.append("")
    else:
        lines.append("No workload errors.")
        lines.append("")
    lines.append("Characters are used as a tokenizer-independent proxy for "
                 "tokens (~4 chars/token, matching the module's own "
                 "conversion constant). Numbers are from a single machine "
                 "and must not be generalized into a universal savings "
                 "percentage.")
    lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True,
                    help="output directory for raw_results.json + summary.md")
    ap.add_argument("--module-path", default=DEFAULT_MODULE_PATH,
                    help="path to a Hermes Agent checkout at commit "
                         f"{PINNED_COMMIT} (default: {DEFAULT_MODULE_PATH})")
    ap.add_argument("--check", action="store_true",
                    help="exit nonzero if any fidelity < 100% or a workload "
                         "errored")
    args = ap.parse_args()

    if not os.path.isdir(args.module_path):
        print(f"error: module path not found: {args.module_path}",
              file=sys.stderr)
        return 2

    data, hermes_home = run_benchmarks(args.module_path)

    os.makedirs(args.out, exist_ok=True)
    raw_path = os.path.join(args.out, "raw_results.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    write_summary(data, os.path.join(args.out, "summary.md"))

    # Clean up spill artifacts (ciphertext only, but not part of the results).
    import shutil
    shutil.rmtree(hermes_home, ignore_errors=True)

    n_fail = len(data["failures"])
    n_bad_fidelity = sum(
        1 for r in data["results"] if not r["fidelity_exact_bytes"])
    print(f"wrote {raw_path}")
    print(f"results: {len(data['results'])}  failures: {n_fail}  "
          f"fidelity<100%: {n_bad_fidelity}")
    # Surface failure details in the job log too, so CI diagnosis does not
    # depend on the artifact upload succeeding.
    for f in data["failures"]:
        print(f"FAILURE {f['workload']} / {f['profile']}: {f['error']}",
              file=sys.stderr)

    if args.check and (n_fail or n_bad_fidelity):
        print("CHECK FAILED", file=sys.stderr)
        return 1
    if args.check:
        print("CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
