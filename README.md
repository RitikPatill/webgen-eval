# WebGen-Eval

A CLI tool that generates polished, self-contained HTML/CSS/JS webpages from plain-English descriptions, then scores and refines them using an LLM-as-judge evaluation loop.

## Status

**M1 — scaffold complete.** The repo structure, package, and CLI skeleton are in place. The `generate` command accepts all planned arguments but currently prints a stub message; generation and evaluation logic ships in M2+.

| Component | State |
|-----------|-------|
| Repo scaffold (`src`-layout, `pyproject.toml`) | done |
| CLI entry point (`webgen-eval generate`) | stub |
| Generator (Claude → HTML) | planned |
| Judge (Claude → Pydantic scores) | planned |
| Refinement loop | planned |
| Rich score-table display | planned |

## Problem Statement

LLM-as-judge evaluation is one of the fastest-growing patterns in applied AI engineering. Most public demos either show raw generation with no eval, or academic benchmarks with no generation artifact. WebGen-Eval combines both in a single runnable CLI: it generates a webpage, scores it across four dimensions, feeds the critique back into a refinement pass, and displays score deltas in a Rich terminal table.

## Architecture

Target architecture (fully implemented in M2–M4):

```
┌─────────────────────────────────────────────────────────┐
│  CLI  (typer)                                           │
│   └─ generate "your description"                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Generator (Claude)                                     │
│   Prompt: semantic HTML5 + inline CSS, no CDN           │
│   Output: self-contained .html file                     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Judge (Claude)                                         │
│   Input: generated HTML                                 │
│   Output (Pydantic): {                                  │
│     overall: float,                                     │
│     dimensions: {                                       │
│       visual_clarity, responsiveness,                   │
│       functional_completeness, code_quality             │
│     },                                                  │
│     critique: str                                       │
│   }                                                     │
└─────────────────┬───────────────────────────────────────┘
                  │
          score < threshold?
                  │ yes
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Refinement Loop (up to 2 iterations)                   │
│   Feeds critique back to Generator as extra context     │
│   Re-runs Judge on revised HTML                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Rich Display                                           │
│   Terminal table: per-dimension scores + deltas         │
│   across all iterations                                 │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
webgen-eval/
├── src/
│   └── webgen_eval/
│       ├── __init__.py      # package version
│       └── __main__.py      # CLI entry point (stub)
├── requirements.txt         # pinned deps
├── pyproject.toml           # build config + console-script entry point
├── LICENSE
└── .gitignore
```

## Installation

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd webgen-eval

# 2. Create a virtual environment (Python 3.11+)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install the package in editable mode
pip install -e .

# 5. Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

```bash
# Basic usage
python -m webgen_eval generate "a personal portfolio page with a dark theme"

# Specify output file and score threshold
python -m webgen_eval generate "a product landing page for a coffee brand" \
    --output landing.html \
    --threshold 8.0
```

> **Note:** The `generate` command is currently a stub. Running it prints
> `[stub] Would generate webpage for: ...` and exits. Full generation and
> evaluation logic will be wired in M2.

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--output`, `-o` | `output.html` | Path for the generated HTML file |
| `--threshold`, `-t` | `7.5` | Minimum overall score to stop refinement |

## Examples

Example prompts with generated HTML and JSON eval reports will be added in a future milestone under `examples/`.

## Roadmap

| Milestone | Deliverable |
|-----------|-------------|
| M1 — scaffold | Repo structure, stub CLI, pinned deps (done) |
| M2 — generator | Claude prompt → self-contained HTML output, saved to disk |
| M3 — judge | Pydantic score model, judge prompt, JSON eval report |
| M4 — refinement loop | Critique feedback → re-generation, up to N iterations |
| M5 — Rich display | Terminal table with per-dimension scores and iteration deltas |
| M6 — examples | Sample prompts, generated HTML files, and eval reports under `examples/` |

<!-- TODO: update this table as milestones ship -->

## Contributing

1. Fork the repo and create a feature branch.
2. Follow the existing code style (no external formatters required for now).
3. Open a PR with a clear description of what changed and why.

## License

MIT License — see [LICENSE](LICENSE) for details.
