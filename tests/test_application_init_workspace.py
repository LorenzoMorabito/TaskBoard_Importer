"""Tests for workspace initialization in the application layer."""

import importlib

init_workspace_module = importlib.import_module(
    "taskboard_importer.application.init_workspace"
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
