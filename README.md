# WebGen-Eval: LLM Webpage Generator with Auto-Evaluation Loop


> **Video walkthrough:** https://youtu.be/W6eU-3fZ-tI
> **60-second overview:** https://youtu.be/IrCMZNa9lSc

> Generate HTML/CSS pages from text prompts, then score and refine them with an LLM-as-judge evaluation loop.

<!-- TODO: replace with a 5-10 second demo gif. Record with ScreenToGif on
     Windows or peek on macOS. Save to docs/demo.gif and update path here. -->
![demo](docs/demo.gif)

## What it is

WebGen-Eval takes a plain-English description and produces a polished, self-contained HTML/CSS/JS file — no external CDN, no build step, no framework. A second Claude instance (the "judge") then scores the output across four dimensions: visual clarity, responsiveness, functional completeness, and code quality. If the overall score falls below a configurable threshold, the critique is fed back to the generator for a revised pass. The loop runs up to two extra rounds and stops as soon as the threshold is cleared.

The terminal shows a Rich table with per-dimension scores and deltas across every iteration, colour-coded green for improvements and red for regressions.

## Quickstart

```bash
git clone https://github.com/RitikPatill/webgen-eval.git
cd webgen-eval

# Python 3.11+ required
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install -e .

export ANTHROPIC_API_KEY="sk-ant-..."

webgen-eval generate "dark-mode SaaS landing page"
```

## Usage

Generate a webpage and let the refinement loop run to completion:

```bash
webgen-eval generate "interactive to-do list app"
# writes output/interactive-to-do-list-app_v1.html (and _v2, _v3 if refined)
# prints a Rich score table when done
```

Override the output directory or the score threshold:

```bash
webgen-eval generate "product landing page for a specialty coffee brand" \
    --output site/ \
    --threshold 8.5
```

**Options**

| Flag | Default | Description |
|------|---------|-------------|
| `--output`, `-o` | `output/` | Directory for generated HTML and eval JSON files |
| `--threshold`, `-t` | `7.5` | Overall score (0–10) at which the loop stops early |

Running the first example above produces output like this in the terminal:

```
                   WebGen-Eval — score table
┌───────────────────────────┬──────┬──────────────┐
│ Dimension                 │   v1 │      v2 (Δ)  │
├───────────────────────────┼──────┼──────────────┤
│ Visual Clarity            │  7.0 │  8.5 (+1.5)  │
│ Responsiveness            │  6.5 │  7.5 (+1.0)  │
│ Functional Completeness   │  7.5 │  8.0 (+0.5)  │
│ Code Quality              │  8.0 │  8.0 ( 0.0)  │
├───────────────────────────┼──────┼──────────────┤
│ Overall                   │  7.3 │  8.0 (+0.7)  │
└───────────────────────────┴──────┴──────────────┘
Final HTML saved → output/dark-mode-saas-landing-page_v2.html
```

## Architecture

```
prompt
  │
  ▼
Generator (Claude) ──► self-contained HTML file
  │
  ▼
Judge (Claude) ──► EvalResult {overall, dimensions{4}, critique}
  │
  ├─ score ≥ threshold ──► Rich table + done
  │
  └─ score < threshold  (up to 2 extra passes)
       │
       └─ critique ──► Generator (with critique as context) ──► repeat
```

## Project structure

```
webgen-eval/
├── prompts/            # system prompts for generator and judge
├── src/webgen_eval/    # package source
│   ├── __main__.py     # Typer CLI entry point
│   ├── generator.py    # Claude call, HTML extraction, file write
│   ├── evaluator.py    # judge call, Pydantic EvalResult model
│   └── refine.py       # refinement loop and Rich score-table renderer
├── examples/           # three worked runs (prompt, final HTML, eval JSON)
├── tests/              # pytest unit tests for all three modules
├── output/             # generated files at runtime (gitignored)
├── requirements.txt    # pinned runtime deps
├── requirements-dev.txt
└── pyproject.toml
```

## Examples

Three worked runs are committed under `examples/`. Each directory contains `prompt.txt`, `output.html` (final iteration), and `eval_final.json`.

| # | Prompt | Iterations | Final score |
|---|--------|------------|-------------|
| 01 | dark-mode SaaS landing page | 2 | 8.0 / 10 |
| 02 | interactive to-do list app | 2 | 8.4 / 10 |
| 03 | product landing page for a specialty coffee brand | 1 | 8.6 / 10 |

## Roadmap

- [ ] Headless browser screenshot capture so the judge can score rendered output, not just source
- [ ] Configurable model ID via CLI flag (`--model claude-opus-4-6`)
- [ ] Batch mode: read a file of prompts and produce a summary report
- [ ] W3C validation pass surfaced as a fifth eval dimension
- [ ] Streaming output during generation so long passes show progress

## License

MIT — see [LICENSE](LICENSE).

---

Built autonomously by [autodev](https://github.com/RitikPatill/autodev),
a multi-agent orchestrator I designed. Each commit in this repo was
authored by me; the implementation work was performed by Sonnet under
the orchestrator's control. Read the orchestrator's README to see how.
