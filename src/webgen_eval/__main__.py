from pathlib import Path

import typer

from webgen_eval.generator import generate as _gen_html, slug as _slug

app = typer.Typer()


@app.callback()
def _root():
    """WebGen-Eval: generate and evaluate webpages with LLM-as-judge."""


@app.command()
def generate(
    description: str = typer.Argument(..., help="Plain-English description of the webpage to generate."),
    output: str = typer.Option("", "--output", "-o", help="Path for the generated HTML file."),
    threshold: float = typer.Option(7.5, "--threshold", "-t", help="Min overall score before stopping refinement."),
):
    """Generate a polished HTML webpage from a plain-English description."""
    out_path = Path(output) if output else Path("output") / f"{_slug(description)}.html"
    result = _gen_html(description, out_path)
    typer.echo(f"Generated: {result}")


if __name__ == "__main__":
    app()
