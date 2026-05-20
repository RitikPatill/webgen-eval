# WebGen-Eval

A CLI tool that generates polished, self-contained HTML/CSS/JS webpages from plain-English descriptions, then scores and refines them using an LLM-as-judge evaluation loop.

## Status

**M3 — llm-as-judge evaluator complete.** `evaluator.py` exposes `evaluate(html) -> EvalResult`, a validated Pydantic model with four 0–10 dimension scores and a critique string. A judge system prompt lives at `prompts/judge.txt`.

| Component | State |
|-----------|-------|
| Repo scaffold (`src`-layout, `pyproject.toml`) | done |
| CLI entry point (`webgen-eval generate`) | done |
| Generator (Claude → HTML) | done |
| Judge (Claude → Pydantic scores) | done |
| Refinement loop | planned |
| Rich score-table display | planned |

## Problem Statement

LLM-as-judge evaluation is one of the fastest-growing patterns in applied AI engineering. Most public demos either show raw generation with no eval, or academic benchmarks with no generation artifact. WebGen-Eval combines both in a single runnable CLI: it generates a webpage, scores it across four dimensions, feeds the critique back into a refinement pass, and displays score deltas in a Rich terminal table.

## Architecture

Target architecture (M3 implemented; M4–M5 planned):

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
├── prompts/
│   ├── generator.txt        # system prompt for the HTML generator
│   └── judge.txt            # system prompt for the LLM-as-judge evaluator
├── src/
│   └── webgen_eval/
│       ├── __init__.py      # package version
│       ├── __main__.py      # CLI entry point (Typer)
│       ├── generator.py     # Claude call + HTML extraction + file write
│       └── evaluator.py     # judge Claude call + Pydantic EvalResult model
├── output/                  # generated HTML files (gitignored except .gitkeep)
├── tests/
│   ├── __init__.py
│   ├── test_generator.py    # unit tests for slug() and extract_html()
│   └── test_evaluator.py    # unit tests for parse_eval_response() and evaluate()
├── requirements.txt         # pinned runtime deps
├── requirements-dev.txt     # pytest (dev only)
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
# Generate a webpage (output auto-named from the description slug)
python -m webgen_eval generate "dark-mode SaaS landing page"
# → writes output/dark-mode-saas-landing-page.html

# Equivalent using the installed console script (after pip install -e .)
webgen-eval generate "dark-mode SaaS landing page"

# Specify a custom output path
python -m webgen_eval generate "a product landing page for a coffee brand" \
    --output landing.html
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--output`, `-o` | *(auto-slug)* | Path for the generated HTML file |
| `--threshold`, `-t` | `7.5` | Minimum overall score to stop refinement (used in M4+) |

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Examples

Example prompts with generated HTML and JSON eval reports will be added in a future milestone under `examples/`.

## Roadmap

| Milestone | Deliverable |
|-----------|-------------|
| M1 — scaffold | Repo structure, stub CLI, pinned deps (done) |
| M2 — generator | Claude prompt → self-contained HTML output, saved to disk (done) |
| M3 — judge | Pydantic score model, judge prompt, JSON eval report (done) |
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
