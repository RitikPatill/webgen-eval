from pathlib import Path

import typer
from rich.console import Console

from webgen_eval.generator import slug
from webgen_eval.refine import render_score_table, run_refinement_loop

app = typer.Typer()


@app.callback()
def _root():
    """WebGen-Eval: generate and evaluate webpages with LLM-as-judge."""


@app.command()
def generate(
    description: str = typer.Argument(..., help="Plain-English description of the webpage to generate."),
    output: str = typer.Option("", "--output", "-o", help="Output directory or HTML file path."),
    threshold: float = typer.Option(7.5, "--threshold", "-t", help="Min overall score before stopping refinement."),
):
    """Generate a polished HTML webpage from a plain-English description."""
    if output and not output.endswith(".html"):
        output_dir = Path(output)
    else:
        output_dir = Path("output")

    results = run_refinement_loop(description, threshold=threshold, output_dir=output_dir)

    console = Console()
    console.print(render_score_table(results))

    base = slug(description)
    final_path = output_dir / f"{base}_v{len(results)}.html"
    typer.echo(f"Final HTML saved \u2192 {final_path}")


if __name__ == "__main__":
    app()
