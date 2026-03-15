"""Tests for CLI entry points."""

import sys
from types import SimpleNamespace

from taskboard_importer.presentation import cli


def test_init_project_uses_expected_argument_names(monkeypatch, tmp_path):
    calls = {}

    def fake_init_workspace(**kwargs):
        calls.update(kwargs)

    monkeypatch.setattr(cli, "init_workspace", fake_init_workspace)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "taskboard",
            "init-project",
            "--path",
            str(tmp_path),
            "--title",
            "Demo",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
        ],
    )

    assert cli.main() == 0
    assert calls["project_path"] == str(tmp_path)
    assert calls["title"] == "Demo"


def test_import_roadmap_cli_resolves_config_and_env(monkeypatch, tmp_path):
    project_dir = tmp_path / "project"
    roadmap_dir = project_dir / "roadmap"
    roadmap_dir.mkdir(parents=True)
    (roadmap_dir / "roadmap.md").write_text("# Demo\n# 1. Phase\n", encoding="utf-8")

    captured = {}

    def fake_load_project_config(path):
        assert path == str(project_dir)
        return {
            "github": {
                "repo_owner": "config-owner",
                "repo_name": "config-repo",
                "project_number": 7,
            },
            "publishing": {"default_status": "Ready"},
        }

    def fake_import_roadmap(**kwargs):
        captured.update(kwargs)
        return (SimpleNamespace(), [], SimpleNamespace())

    monkeypatch.setattr(cli, "load_project_config", fake_load_project_config)
    monkeypatch.setattr(cli, "import_roadmap", fake_import_roadmap)
    monkeypatch.setenv("GITHUB_TOKEN", "env-token")
    monkeypatch.setattr(
        sys,
        "argv",
        ["taskboard", "import-roadmap", "--project", str(project_dir)],
    )

    assert cli.main() == 0
    assert captured["publish_to_github"] is True
    assert captured["repo_owner"] == "config-owner"
    assert captured["repo_name"] == "config-repo"
    assert captured["project_number"] == 7
    assert captured["token"] == "env-token"
    assert captured["default_status"] == "Ready"
    assert captured["dry_run"] is False


def test_bootstrap_github_cli_uses_create_labels(monkeypatch, tmp_path):
    captured = {}

    def fake_load_project_config(path):
        return {
            "github": {"repo_owner": "cfg-owner", "repo_name": "cfg-repo"},
            "labels": ["Documentation", "Phase 1"],
        }

    def fake_bootstrap_github(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(cli, "load_project_config", fake_load_project_config)
    monkeypatch.setattr(cli, "bootstrap_github", fake_bootstrap_github)
    monkeypatch.setenv("GITHUB_TOKEN", "env-token")
    monkeypatch.setattr(
        sys,
        "argv",
        ["taskboard", "bootstrap-github", "--project", str(tmp_path)],
    )

    assert cli.main() == 0
    assert captured["repo_owner"] == "cfg-owner"
    assert captured["repo_name"] == "cfg-repo"
    assert captured["create_labels"] == ["Documentation", "Phase 1"]
    assert captured["token"] == "env-token"
