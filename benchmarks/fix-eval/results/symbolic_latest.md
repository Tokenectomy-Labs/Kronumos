# Kronumos `--fix` Reproducible Evaluation Report

- **Generated (UTC):** `2026-11-20T20:26:53Z`
- **Binary:** `kronumos 1.3.0`
- **Mode:** `symbolic`
- **Resolved:** **1/8** (12.5%)
- **Exit Code Truthfulness:** `8/8`
- **Zero Dirty Diff on Unresolved:** `True`
- **Total Tokens (In / Out):** `0 in / 0 out`
- **Total Duration:** `6.49s`

| Task | Lang | Category | Result | Exit | Clean Rollback | Time | Turns | Tokens (In/Out) |
|---|---|---|---|---|---|---|---|---|
| `js_01_null_guard_parser` | JavaScript | Null Dereference | **FAIL** | `1` | OK (0 dirty) | 0.83s | 1 | 0 / 0 |
| `js_02_rate_limiter_window` | JavaScript | Window Boundary | **FAIL** | `1` | OK (0 dirty) | 0.77s | 1 | 0 / 0 |
| `py_01_zero_division_guard` | Python | ZeroDivisionError | **PASS** | `0` | n/a | 0.46s | 0 | 0 / 0 |
| `py_02_off_by_one_pagination` | Python | Boundary / Off-by-one | **FAIL** | `1` | OK (0 dirty) | 0.71s | 1 | 0 / 0 |
| `py_03_rlock_cache_deadlock` | Python | Concurrency Deadlock | **FAIL** | `1` | OK (0 dirty) | 1.75s | 1 | 0 / 0 |
| `py_04_multifile_discount_bug` | Python | Multi-file Logic | **FAIL** | `1` | OK (0 dirty) | 0.74s | 1 | 0 / 0 |
| `rs_01_slice_bounds_panic` | Rust | Panic / Bounds | **FAIL** | `1` | OK (0 dirty) | 0.62s | 1 | 0 / 0 |
| `rs_02_parse_kv_unescape` | Rust | Parser Edge Case | **FAIL** | `1` | OK (0 dirty) | 0.61s | 1 | 0 / 0 |

## Reproduce Locally

```bash
python3 benchmarks/fix-eval/run_eval.py --mode symbolic
```
