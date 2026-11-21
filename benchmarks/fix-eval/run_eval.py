#!/usr/bin/env python3
"""
Kronumos Reproducible --fix Evaluation Harness.

Runs `kronumos --fix` against a multi-language suite (Python, JavaScript/Node, Rust)
in isolated temporary workspaces with isolated KRONUMOS_STATE_DIR, independently
verifies baseline failure and post-fix pass/fail, checks 0-dirty-diff rollback
integrity on unresolved tasks, and emits JSON + Markdown reports.

Usage:
  python3 benchmarks/fix-eval/run_eval.py --mode symbolic
  python3 benchmarks/fix-eval/run_eval.py --mode cloud
  python3 benchmarks/fix-eval/run_eval.py --mode both
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASKS_DIR = ROOT / "tasks"
RESULTS_DIR = ROOT / "results"

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
TOK_RE = re.compile(r"Token Usage \(In / Out\):\s+([\d,]+)\s+in\s*/\s*([\d,]+)\s+out")
PRUNE_RE = re.compile(r"Sub-Cortex Pruned:\s+([\d,]+)\s+lines\s+\(~([\d,]+)\s+tok")
TURNS_RE = re.compile(r"Conversation Turns:\s+(\d+)\s+turns")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def snapshot_hashes(workspace: Path) -> dict:
    hashes = {}
    for p in sorted(workspace.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(workspace).as_posix()
        parts = rel.split("/")
        if rel == "Cargo.lock" or any(
            seg in {"__pycache__", ".pytest_cache", "target", ".git", ".kronumos", "node_modules"}
            for seg in parts
        ):
            continue
        hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


def parse_telemetry(output: str) -> dict:
    clean = strip_ansi(output)
    tokens_in = 0
    tokens_out = 0
    lines_pruned = 0
    tokens_saved = 0
    turns = 0

    m_tok = TOK_RE.search(clean)
    if m_tok:
        tokens_in = int(m_tok.group(1).replace(",", ""))
        tokens_out = int(m_tok.group(2).replace(",", ""))

    m_prune = PRUNE_RE.search(clean)
    if m_prune:
        lines_pruned = int(m_prune.group(1).replace(",", ""))
        tokens_saved = int(m_prune.group(2).replace(",", ""))

    m_turns = TURNS_RE.search(clean)
    if m_turns:
        turns = int(m_turns.group(1))

    symbolic_solved = (
        "Symbolic APR" in clean and "VERIFIED" in clean and tokens_in == 0 and tokens_out == 0
    )

    return {
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "lines_pruned": lines_pruned,
        "tokens_saved": tokens_saved,
        "turns": turns,
        "symbolic_solved": symbolic_solved,
    }


def resolve_kronumos_bin(cli_bin: str) -> str:
    if cli_bin:
        return cli_bin
    for cand in [
        "/home/nans/.cargo/bin/kronumos",
        str(ROOT.parent.parent / "engines/kronumos-core/target/release/kronumos"),
        shutil.which("kronumos") or "",
    ]:
        if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    raise FileNotFoundError("Could not find kronumos binary. Pass --bin /path/to/kronumos.")


def run_single_task(task_dir: Path, mode: str, kronumos_bin: str, max_iter: int, timeout_s: int) -> dict:
    meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    task_id = meta["id"]
    test_cmd = meta["test_cmd"]
    lang = meta["language"]
    category = meta["category"]

    with tempfile.TemporaryDirectory(prefix=f"kronumos_eval_{task_id}_") as tmp:
        tmp_path = Path(tmp)
        ws = tmp_path / "workspace"
        state_dir = tmp_path / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(task_dir / "repo", ws)

        before_hashes = snapshot_hashes(ws)

        # 1. Confirm baseline fails before running kronumos
        base_env = os.environ.copy()
        base_env["PYTHONDONTWRITEBYTECODE"] = "1"
        baseline = subprocess.run(
            test_cmd,
            shell=True,
            cwd=str(ws),
            env=base_env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if baseline.returncode == 0:
            raise RuntimeError(f"Task {task_id} baseline unexpectedly PASSED! Fixture is broken.")

        # 2. Build kronumos --fix invocation
        env = os.environ.copy()
        env["KRONUMOS_STATE_DIR"] = str(state_dir)
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        cmd = [
            kronumos_bin,
            "--fix",
            "--workspace",
            str(ws),
            "--test-cmd",
            test_cmd,
            "--max-iterations",
            str(max_iter),
        ]
        if mode == "symbolic":
            # Force 0-LLM: point cloudflare backend to a closed loopback port with max-iterations 1
            # so ONLY local deterministic Symbolic APR can resolve the task (0 network / 0 LLM calls).
            cmd.extend([
                "--backend",
                "cloudflare",
                "--cf-url",
                "http://127.0.0.1:9",
                "--cf-key",
                "symbolic-only-offline",
            ])
        elif mode == "cloud":
            cmd.extend(["--backend", "cloudflare"])
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        t0 = time.monotonic()
        timed_out = False
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(ws),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
            rc = proc.returncode
            combined_out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            rc = 124
            combined_out = (
                (exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
                + "\n"
                + (exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
            )
        duration_s = round(time.monotonic() - t0, 2)

        # 3. Independently verify test suite after kronumos exits
        try:
            verify = subprocess.run(
                test_cmd,
                shell=True,
                cwd=str(ws),
                env=base_env,
                capture_output=True,
                text=True,
                timeout=30,
            )
            verify_passed = verify.returncode == 0
        except subprocess.TimeoutExpired:
            verify_passed = False

        after_hashes = snapshot_hashes(ws)
        changed_files = sorted(
            k for k in set(before_hashes) | set(after_hashes)
            if before_hashes.get(k) != after_hashes.get(k)
        )
        dirty_on_fail = (not verify_passed) and len(changed_files) > 0
        exit_code_truthful = (verify_passed and rc == 0) or ((not verify_passed) and rc != 0)

        telem = parse_telemetry(combined_out)
        return {
            "id": task_id,
            "language": lang,
            "category": category,
            "mode": mode,
            "test_cmd": test_cmd,
            "resolved": verify_passed,
            "cli_exit_code": rc,
            "exit_code_truthful": exit_code_truthful,
            "dirty_on_fail": dirty_on_fail,
            "changed_files": changed_files,
            "timed_out": timed_out,
            "duration_secs": duration_s,
            "turns": telem["turns"],
            "tokens_in": telem["tokens_in"],
            "tokens_out": telem["tokens_out"],
            "tokens_saved": telem["tokens_saved"],
            "lines_pruned": telem["lines_pruned"],
            "symbolic_solved": telem["symbolic_solved"],
        }


def write_markdown_report(summary: dict, out_path: Path) -> None:
    lines = [
        "# Kronumos `--fix` Reproducible Evaluation Report",
        "",
        f"- **Generated (UTC):** `{summary['generated_at']}`",
        f"- **Binary:** `{summary['kronumos_version']}`",
        f"- **Mode:** `{summary['mode']}`",
        f"- **Resolved:** **{summary['resolved_count']}/{summary['total_tasks']}** ({summary['pass_rate_pct']}%)",
        f"- **Exit Code Truthfulness:** `{summary['truthful_exit_count']}/{summary['total_tasks']}`",
        f"- **Zero Dirty Diff on Unresolved:** `{summary['clean_rollback_ok']}`",
        f"- **Total Tokens (In / Out):** `{summary['total_tokens_in']:,} in / {summary['total_tokens_out']:,} out`",
        f"- **Total Duration:** `{summary['total_duration_secs']}s`",
        "",
        "| Task | Lang | Category | Result | Exit | Clean Rollback | Time | Turns | Tokens (In/Out) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in summary["results"]:
        res_str = "PASS" if r["resolved"] else ("TIMEOUT" if r["timed_out"] else "FAIL")
        rb_str = "n/a" if r["resolved"] else ("OK (0 dirty)" if not r["dirty_on_fail"] else f"DIRTY ({','.join(r['changed_files'])})")
        lines.append(
            f"| `{r['id']}` | {r['language']} | {r['category']} | **{res_str}** | `{r['cli_exit_code']}` | {rb_str} | {r['duration_secs']}s | {r['turns']} | {r['tokens_in']:,} / {r['tokens_out']:,} |"
        )
    lines.extend([
        "",
        "## Reproduce Locally",
        "",
        "```bash",
        f"python3 benchmarks/fix-eval/run_eval.py --mode {summary['mode']}",
        "```",
        "",
    ])
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Kronumos --fix reproducible eval harness")
    parser.add_argument("--mode", choices=["symbolic", "cloud", "both"], default="symbolic")
    parser.add_argument("--bin", default="", help="Path to kronumos binary")
    parser.add_argument("--max-iterations", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--task", default="", help="Optional single task id filter")
    args = parser.parse_args()

    kronumos_bin = resolve_kronumos_bin(args.bin)
    ver_proc = subprocess.run([kronumos_bin, "--version"], capture_output=True, text=True)
    version_str = (ver_proc.stdout or ver_proc.stderr or "unknown").strip()

    task_dirs = sorted(p for p in TASKS_DIR.iterdir() if p.is_dir() and (p / "task.json").is_file())
    if args.task:
        task_dirs = [p for p in task_dirs if p.name == args.task]
    if not task_dirs:
        print("No tasks found.", file=sys.stderr)
        return 1

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    modes = ["symbolic", "cloud"] if args.mode == "both" else [args.mode]

    for mode in modes:
        print(f"\n=== Running Kronumos Eval ({mode}) | {version_str} | {len(task_dirs)} tasks ===")
        results = []
        for tdir in task_dirs:
            res = run_single_task(
                tdir,
                mode=mode,
                kronumos_bin=kronumos_bin,
                max_iter=1 if mode == "symbolic" else args.max_iterations,
                timeout_s=args.timeout,
            )
            status = "PASS" if res["resolved"] else "FAIL"
            print(
                f"  [{status}] {res['id']} ({res['language']}) "
                f"exit={res['cli_exit_code']} time={res['duration_secs']}s "
                f"tok={res['tokens_in']}/{res['tokens_out']} dirty_on_fail={res['dirty_on_fail']}"
            )
            results.append(res)

        resolved_count = sum(1 for r in results if r["resolved"])
        truthful_count = sum(1 for r in results if r["exit_code_truthful"])
        clean_rollback_ok = all(not r["dirty_on_fail"] for r in results)
        summary = {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "kronumos_version": version_str,
            "mode": mode,
            "total_tasks": len(results),
            "resolved_count": resolved_count,
            "pass_rate_pct": round((resolved_count / len(results)) * 100.0, 1),
            "truthful_exit_count": truthful_count,
            "clean_rollback_ok": clean_rollback_ok,
            "total_tokens_in": sum(r["tokens_in"] for r in results),
            "total_tokens_out": sum(r["tokens_out"] for r in results),
            "total_duration_secs": round(sum(r["duration_secs"] for r in results), 2),
            "results": results,
        }

        json_path = RESULTS_DIR / f"{mode}_latest.json"
        md_path = RESULTS_DIR / f"{mode}_latest.md"
        json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        write_markdown_report(summary, md_path)
        print(
            f"Summary ({mode}): {resolved_count}/{len(results)} resolved ({summary['pass_rate_pct']}%), "
            f"truthful_exit={truthful_count}/{len(results)}, clean_rollback={clean_rollback_ok}, "
            f"tokens={summary['total_tokens_in']:,}in/{summary['total_tokens_out']:,}out"
        )
        print(f"Wrote {json_path} and {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
