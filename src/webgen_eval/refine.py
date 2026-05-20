from pathlib import Path

from rich.table import Table
from rich.text import Text

from webgen_eval.evaluator import EvalResult, evaluate
from webgen_eval.generator import generate_html, slug

_DIMENSIONS = [
    ("visual_clarity", "Visual Clarity"),
    ("responsiveness", "Responsiveness"),
    ("functional_completeness", "Functional Completeness"),
    ("code_quality", "Code Quality"),
]


def run_refinement_loop(
    description: str,
    threshold: float = 7.5,
    max_extra_passes: int = 2,
    output_dir: Path = Path("output"),
) -> list[EvalResult]:
    output_dir.mkdir(parents=True, exist_ok=True)
    base = slug(description)
    results: list[EvalResult] = []
    critique: str | None = None

    for iteration in range(max_extra_passes + 1):
        version = iteration + 1
        html_path = output_dir / f"{base}_v{version}.html"
        html = generate_html(description, html_path, refinement_context=critique)
        result = evaluate(html)
        (output_dir / f"{base}_v{version}_eval.json").write_text(
            result.model_dump_json(indent=2), encoding="utf-8"
        )
        results.append(result)
        if result.overall >= threshold:
            break
        critique = result.critique

    return results


def render_score_table(results: list[EvalResult]) -> Table:
    table = Table(show_header=True, header_style="bold")
    table.add_column("Dimension", style="bold", justify="left")
    for i, _ in enumerate(results):
        header = f"v{i + 1}" if i == 0 else f"v{i + 1} (\u0394)"
        table.add_column(header, justify="right")

    def _score_cell(score: float, prev: float | None) -> Text | str:
        if prev is None:
            return f"{score:.1f}"
        delta = score - prev
        style = "green" if delta > 0 else ("red" if delta < 0 else "dim")
        return Text(f"{score:.1f} ({delta:+.1f})", style=style)

    for attr, label in _DIMENSIONS:
        row: list[Text | str] = [label]
        for i, result in enumerate(results):
            score = getattr(result.dimensions, attr)
            prev = getattr(results[i - 1].dimensions, attr) if i > 0 else None
            row.append(_score_cell(score, prev))
        table.add_row(*row)

    # Overall row
    overall_row: list[Text | str] = ["Overall"]
    for i, result in enumerate(results):
        prev_overall = results[i - 1].overall if i > 0 else None
        overall_row.append(_score_cell(result.overall, prev_overall))
    table.add_row(*overall_row)

    return table
