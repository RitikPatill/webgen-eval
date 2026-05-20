import re
from pathlib import Path

import anthropic

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:50]


def extract_html(text: str) -> str:
    # Primary: fenced ```html block
    match = re.search(r"```html\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: any fenced block containing <!DOCTYPE
    match = re.search(r"```[^\n]*\n(<!DOCTYPE.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    raise ValueError("No fenced HTML block found in model response.")


def generate_html(
    description: str,
    output_path: Path,
    refinement_context: str | None = None,
) -> str:
    system_prompt = load_prompt("generator.txt")
    client = anthropic.Anthropic()
    user_content = description
    if refinement_context:
        user_content += (
            "\n\n---\nPrevious version was evaluated. Critique:\n"
            + refinement_context
            + "\n\nGenerate an improved version that addresses the above feedback."
        )
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    html = extract_html(message.content[0].text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return html
