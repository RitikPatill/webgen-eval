import pytest

from webgen_eval.generator import slug, extract_html


def test_slug_basic():
    assert slug("dark-mode SaaS landing page") == "dark-mode-saas-landing-page"


def test_slug_special_chars():
    result = slug("Hello, World! (2024)")
    assert all(c in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in result)


def test_slug_truncates():
    assert len(slug("a" * 100)) <= 50


def test_slug_no_leading_trailing_hyphens():
    result = slug("---foo---")
    assert not result.startswith("-")
    assert not result.endswith("-")


def test_extract_html_fenced_block():
    text = "```html\n<html><body>hello</body></html>\n```"
    result = extract_html(text)
    assert "<html>" in result
    assert "hello" in result


def test_extract_html_no_tag_fallback():
    text = "```\n<!DOCTYPE html>\n<html><body>hi</body></html>\n```"
    result = extract_html(text)
    assert "<!DOCTYPE html>" in result


def test_extract_html_raises_on_missing():
    with pytest.raises(ValueError):
        extract_html("no code here")
