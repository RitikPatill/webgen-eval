import typer

app = typer.Typer()


@app.callback()
def _root():
    """WebGen-Eval: generate and evaluate webpages with LLM-as-judge."""


@app.command()
def generate(
    description: str = typer.Argument(..., help="Plain-English description of the webpage to generate."),
    output: str = typer.Option("output.html", "--output", "-o", help="Path for the generated HTML file."),
    threshold: float = typer.Option(7.5, "--threshold", "-t", help="Min overall score before stopping refinement."),
):
    """Generate a polished HTML webpage from a plain-English description."""
    typer.echo(f"[stub] Would generate webpage for: {description!r}")


if __name__ == "__main__":
    app()
