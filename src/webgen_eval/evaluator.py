import json
import re

import anthropic
from pydantic import BaseModel, ValidationError

from webgen_eval.generator import MODEL, load_prompt


class Dimensions(BaseModel):
    visual_clarity: float
    responsiveness: float
    functional_completeness: float
    code_quality: float


class EvalResult(BaseModel):
    overall: float
    dimensions: Dimensions
    critique: str


def _sentinel(exc: Exception) -> EvalResult:
    return EvalResult(
        overall=0.0,
        dimensions=Dimensions(
            visual_clarity=0.0,
            responsiveness=0.0,
            functional_completeness=0.0,
            code_quality=0.0,
        ),
        critique=f"Parse error: {exc}",
    )


def parse_eval_response(text: str) -> EvalResult:
    """Extract and validate EvalResult from model text. Never raises."""
    # 1. Try raw JSON
    try:
        data = json.loads(text)
        return EvalResult(**data)
    except (json.JSONDecodeError, ValidationError, KeyError, TypeError):
        pass

    # 2. Try fenced ```json block
    match = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            return EvalResult(**data)
        except (json.JSONDecodeError, ValidationError, KeyError, TypeError) as exc:
            return _sentinel(exc)

    return _sentinel(ValueError("No JSON content found in response"))


def evaluate(html: str) -> EvalResult:
    """Send html to the judge Claude call and return a validated EvalResult."""
    system_prompt = load_prompt("judge.txt")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": html}],
    )
    return parse_eval_response(response.content[0].text)
