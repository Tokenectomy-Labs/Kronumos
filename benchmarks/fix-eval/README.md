# Kronumos `--fix` Public Evaluation Harness

A transparent, zero-dependency, multi-language evaluation suite for verifying `kronumos --fix` end-to-end on real bug classes (Python, JavaScript/Node.js, and Rust).

## Design Principles

- **Zero external dependencies:** Every task runs offline with standard toolchains (`python3 -m unittest`, `node --test`, `cargo test --offline`).
- **Strict isolation:** Each task runs in a fresh temporary workspace with an isolated `KRONUMOS_STATE_DIR` so prior Knowledge Crystals never leak across runs.
- **Independent verification:** The harness verifies baseline failure before invoking `kronumos --fix`, independently re-runs the test suite after exit, verifies truthful exit codes (`0` on pass, non-zero on unresolved), and verifies `0 dirty diff` rollback on unresolved tasks.

## Task Suite (8 Tasks)

| ID | Language | Category | Bug Description |
|---|---|---|---|
| `py_01_zero_division_guard` | Python | ZeroDivisionError | Margin ratio helper crashes on `0` denominator |
| `py_02_off_by_one_pagination` | Python | Boundary / Off-by-one | Paginator drops last item per page and miscomputes total pages |
| `py_03_rlock_cache_deadlock` | Python | Concurrency Deadlock | `get_or_set` acquires non-reentrant `threading.Lock` twice via `set()` |
| `py_04_multifile_discount_bug` | Python | Multi-file Logic | Percent discount treated as multiplier (`10` vs `0.10`) across `pricing.py` + `cart.py` |
| `js_01_null_guard_parser` | JavaScript | Null Dereference | Config merger throws `TypeError` on `null`/`undefined` nested sections |
| `js_02_rate_limiter_window` | JavaScript | Window Boundary | Sliding-window limiter allows `limit + 1` requests and mishandles expiry |
| `rs_01_slice_bounds_panic` | Rust | Panic / Bounds | Windowed mean helper panics on empty slice or `window == 0` |
| `rs_02_parse_kv_unescape` | Rust | Parser Edge Case | `KEY=VALUE` parser truncates values containing `=` and keeps surrounding quotes |

## Usage

```bash
# 1. Offline deterministic Symbolic APR only (0 LLM calls)
python3 benchmarks/fix-eval/run_eval.py --mode symbolic

# 2. Full Kronumos Cloud Gateway (requires `kronumos login` or `KRONUMOS_TOKEN`)
python3 benchmarks/fix-eval/run_eval.py --mode cloud

# 3. Both modes
python3 benchmarks/fix-eval/run_eval.py --mode both
```

Results are written to `benchmarks/fix-eval/results/<mode>_latest.json` and `benchmarks/fix-eval/results/<mode>_latest.md`.
