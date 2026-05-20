from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from webgen_eval.evaluator import Dimensions, EvalResult
from webgen_eval.refine import render_score_table, run_refinement_loop


def _make_result(overall: float, critique: str = "some critique") -> EvalResult:
    return EvalResult(
        overall=overall,
        dimensions=Dimensions(
            visual_clarity=overall,
            responsiveness=overall,
            functional_completeness=overall,
            code_quality=overall,
        ),
        critique=critique,
    )


FAKE_HTML = "<html><body>test</body></html>"


@patch("webgen_eval.refine.evaluate")
@patch("webgen_eval.refine.generate_html", return_value=FAKE_HTML)
def test_single_pass_when_above_threshold(mock_gen, mock_eval, tmp_path):
    mock_eval.return_value = _make_result(8.0)
    results = run_refinement_loop("a simple page", threshold=7.5, output_dir=tmp_path)
    assert len(results) == 1
    mock_gen.assert_called_once()
    assert mock_gen.call_args.kwargs["refinement_context"] is None


@patch("webgen_eval.refine.evaluate")
@patch("webgen_eval.refine.generate_html", return_value=FAKE_HTML)
def test_refinement_runs_second_pass(mock_gen, mock_eval, tmp_path):
    first = _make_result(6.0, critique="needs improvement")
    second = _make_result(8.0, critique="looks great")
    mock_eval.side_effect = [first, second]

    results = run_refinement_loop("a simple page", threshold=7.5, output_dir=tmp_path)

    assert len(results) == 2
    assert mock_gen.call_count == 2
    # Second call must pass the first result's critique as refinement_context
    second_call = mock_gen.call_args_list[1]
    assert second_call.kwargs["refinement_context"] == "needs improvement"


@patch("webgen_eval.refine.evaluate")
@patch("webgen_eval.refine.generate_html", return_value=FAKE_HTML)
def test_caps_at_max_extra_passes(mock_gen, mock_eval, tmp_path):
    mock_eval.return_value = _make_result(5.0)
    results = run_refinement_loop("a simple page", threshold=7.5, max_extra_passes=2, output_dir=tmp_path)
    assert len(results) == 3
    assert mock_gen.call_count == 3


def test_render_score_table_columns():
    r1 = _make_result(6.0, critique="needs work")
    r2 = _make_result(8.0, critique="better")
    table = render_score_table([r1, r2])
    assert len(table.columns) == 3  # Dimension + v1 + v2 (Δ)
    assert table.row_count == 5    # 4 dimensions + overall
