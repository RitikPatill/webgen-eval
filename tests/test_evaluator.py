import json
from unittest.mock import MagicMock, patch

from webgen_eval.evaluator import EvalResult, Dimensions, evaluate, parse_eval_response

VALID_DATA = {
    "overall": 8.5,
    "dimensions": {
        "visual_clarity": 9.0,
        "responsiveness": 8.0,
        "functional_completeness": 8.5,
        "code_quality": 8.5,
    },
    "critique": "Solid layout with good contrast.",
}


def test_parse_valid_json():
    result = parse_eval_response(json.dumps(VALID_DATA))
    assert isinstance(result, EvalResult)
    assert result.overall == 8.5
    assert result.dimensions.visual_clarity == 9.0
    assert result.critique == "Solid layout with good contrast."


def test_parse_fenced_json():
    fenced = f"```json\n{json.dumps(VALID_DATA)}\n```"
    result = parse_eval_response(fenced)
    assert isinstance(result, EvalResult)
    assert result.overall == 8.5
    assert result.dimensions.responsiveness == 8.0


def test_parse_malformed_returns_sentinel():
    result = parse_eval_response("this is not json at all !!!")
    assert isinstance(result, EvalResult)
    assert result.overall == 0.0
    assert result.critique.startswith("Parse error")


def test_parse_missing_field_returns_sentinel():
    # Missing 'critique' key — Pydantic should reject it
    incomplete = {
        "overall": 7.0,
        "dimensions": {
            "visual_clarity": 7.0,
            "responsiveness": 7.0,
            "functional_completeness": 7.0,
            "code_quality": 7.0,
        },
        # no 'critique'
    }
    result = parse_eval_response(json.dumps(incomplete))
    assert result.overall == 0.0
    assert result.critique.startswith("Parse error")


def test_evaluate_calls_api():
    fake_text = json.dumps(VALID_DATA)

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=fake_text)]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("webgen_eval.evaluator.anthropic.Anthropic", return_value=mock_client):
        result = evaluate("<html><body>test</body></html>")

    assert isinstance(result, EvalResult)
    assert result.overall == 8.5

    call_kwargs = mock_client.messages.create.call_args
    assert call_kwargs.kwargs["system"] is not None
    assert "<html><body>test</body></html>" in call_kwargs.kwargs["messages"][0]["content"]
