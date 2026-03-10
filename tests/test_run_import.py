import pytest

from taskboard_importer.run_import import _coerce_project_number


def test_coerce_project_number_from_env_string():
    assert _coerce_project_number("12") == 12


def test_coerce_project_number_none_or_empty():
    assert _coerce_project_number(None) is None
    assert _coerce_project_number("") is None


def test_coerce_project_number_invalid():
    with pytest.raises(ValueError):
        _coerce_project_number("abc")
