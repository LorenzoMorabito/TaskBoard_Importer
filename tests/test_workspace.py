"""Tests for workspace orchestration and config loading."""

import importlib

init_workspace_module = importlib.import_module(
    "taskboard_importer.application.init_workspace"
)
from taskboard_importer.infrastructure.workspace.project_config import (
    get_config_value,
    load_project_config,
)


def test_init_workspace_delegates_to_scaffold_and_config(monkeypatch, tmp_path):
    calls = {}

    def fake_scaffold(project_path, template_path):
        calls["scaffold"] = (project_path, template_path)

    def fake_create_config(project_path, **kwargs):
        calls["config"] = (project_path, kwargs)

    monkeypatch.setattr(init_workspace_module, "scaffold_project", fake_scaffold)
    monkeypatch.setattr(
        init_workspace_module, "create_project_config", fake_create_config
    )

    init_workspace_module.init_workspace(
        project_path=str(tmp_path),
        title="Demo",
        template_path="template",
        repo_owner="owner",
        repo_name="repo",
        project_number=9,
    )

    assert calls["scaffold"] == (str(tmp_path), "template")
    assert calls["config"][0] == str(tmp_path)
    assert calls["config"][1]["title"] == "Demo"
    assert calls["config"][1]["project_number"] == 9


def test_load_project_config_reads_yaml(tmp_path):
    config_path = tmp_path / "project.yaml"
    config_path.write_text(
        "github:\n  repo_owner: owner\n  repo_name: repo\npublishing:\n  default_status: Ready\n",
        encoding="utf-8",
    )

    config = load_project_config(str(tmp_path))

    assert config["github"]["repo_owner"] == "owner"
    assert get_config_value(config, "publishing.default_status") == "Ready"
