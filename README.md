# Kronumos

Terminal coding agent in Rust. Prunes noisy stack traces locally in 0.4ms, checks Tree-sitter AST before writing to disk, and rolls back failed fixes automatically.

Website: [kronumos.com](https://kronumos.com) · Docs: [kronumos.com/docs](https://kronumos.com/docs) · Research: [labs.kronumos.com](https://labs.kronumos.com)

## Install

```bash
# Linux / macOS
curl -fsSL https://kronumos.com/install.sh | bash

# Windows (PowerShell)
irm https://kronumos.com/install.ps1 | iex

# npx
npx kronumos
```

## Reproduce the Public `--fix` Evaluation (8/8)

Zero-dependency multi-language test suite across Python, Rust, and JavaScript (`benchmarks/fix-eval/`):

```bash
git clone https://github.com/Tokenectomy-Labs/Kronumos.git
cd Kronumos

# Offline 0-LLM Symbolic APR only
python3 benchmarks/fix-eval/run_eval.py --mode symbolic

# Full Kronumos Cloud run (8/8 pass, 23,697 in / 2,320 out tokens, 0 dirty diffs)
python3 benchmarks/fix-eval/run_eval.py --mode cloud
```

See [benchmarks/fix-eval/README.md](benchmarks/fix-eval/README.md) for task definitions and methodology.

## SWE-bench Verified (500 Issues) Report

Full empirical breakdown of the 500-issue Princeton SWE-bench Verified study (blind single-turn 7B model + Rust Sub-Cortex: 38,412 → 3,009 avg prompt tokens, 79/79 clean GNU `patch -p1` apply, 421 safely blocked with 0 dirty diffs, 10 resolved blind):

- [BENCHMARK_500_REPORT.md](BENCHMARK_500_REPORT.md)

## License

See [LICENSE](LICENSE).
