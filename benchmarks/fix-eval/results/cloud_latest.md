# Kronumos `--fix` Reproducible Evaluation Report

- **Generated (UTC):** `2026-11-21T00:43:53Z`
- **Binary:** `kronumos 1.3.0`
- **Mode:** `cloud`
- **Resolved:** **8/8** (100.0%)
- **Exit Code Truthfulness:** `8/8`
- **Zero Dirty Diff on Unresolved:** `True`
- **Total Tokens (In / Out):** `23,697 in / 2,320 out`
- **Total Duration:** `81.05s`

| Task | Lang | Category | Result | Exit | Clean Rollback | Time | Turns | Tokens (In/Out) |
|---|---|---|---|---|---|---|---|---|
| `js_01_null_guard_parser` | JavaScript | Null Dereference | **PASS** | `0` | n/a | 12.95s | 1 | 1,767 / 280 |
| `js_02_rate_limiter_window` | JavaScript | Window Boundary | **PASS** | `0` | n/a | 23.86s | 2 | 4,127 / 522 |
| `py_01_zero_division_guard` | Python | ZeroDivisionError | **PASS** | `0` | n/a | 0.33s | 0 | 0 / 0 |
| `py_02_off_by_one_pagination` | Python | Boundary / Off-by-one | **PASS** | `0` | n/a | 15.21s | 3 | 7,895 / 345 |
| `py_03_rlock_cache_deadlock` | Python | Concurrency Deadlock | **PASS** | `0` | n/a | 8.68s | 1 | 2,009 / 321 |
| `py_04_multifile_discount_bug` | Python | Multi-file Logic | **PASS** | `0` | n/a | 4.03s | 1 | 1,748 / 187 |
| `rs_01_slice_bounds_panic` | Rust | Panic / Bounds | **PASS** | `0` | n/a | 6.84s | 1 | 1,723 / 257 |
| `rs_02_parse_kv_unescape` | Rust | Parser Edge Case | **PASS** | `0` | n/a | 9.15s | 2 | 4,428 / 408 |

## Reproduce Locally

```bash
python3 benchmarks/fix-eval/run_eval.py --mode cloud
```
