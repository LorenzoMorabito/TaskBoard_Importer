"""Tests for import orchestration functionality."""
import pytest


def _coerce_project_number(value):
    """Helper to coerce environment value to project number."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid project number: {value}")


def test_coerce_project_number_from_env_string():
    assert _coerce_project_number("12") == 12


def test_coerce_project_number_none_or_empty():
    assert _coerce_project_number(None) is None
    assert _coerce_project_number("") is None


def test_coerce_project_number_invalid():
    with pytest.raises(ValueError):
        _coerce_project_number("abc")
