import sys
import subprocess

from taskboard_importer import cli
from taskboard_importer.workspace import init_project


def test_cli_import_roadmap_invokes_run_import(monkeypatch, tmp_path):
    project_root = tmp_path / "proj"
    init_project(
        path=str(project_root),
        slug="demo",
        title="Demo Project",
        owner="Tester",
        template_profile="standard",
    )

    called = {}

    def fake_call(cmd):
        called["cmd"] = cmd
        return 0

    monkeypatch.setattr(subprocess, "call", fake_call)

    monkeypatch.setattr(
        sys,
        "argv",
        ["taskboard", "import-roadmap", "--project", str(project_root), "--dry-run"],
    )

    cli.main()

    assert called["cmd"][0] == sys.executable
    assert "taskboard_importer.run_import" in called["cmd"]


def test_cli_bootstrap_github_ensures_labels(monkeypatch, tmp_path):
    project_root = tmp_path / "proj"
    init_project(
        path=str(project_root),
        slug="demo",
        title="Demo Project",
        owner="Tester",
        template_profile="standard",
    )

    called = {"ensure": 0}

    class FakeAdapter:
        def __init__(self, *args, **kwargs):
            pass

        def precheck(self):
            return None

        def ensure_labels(self, _labels):
            called["ensure"] += 1

    monkeypatch.setattr(cli, "GitHubAdapter", FakeAdapter)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "taskboard",
            "bootstrap-github",
            "--project",
            str(project_root),
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--token",
            "t",
        ],
    )

    cli.main()
    assert called["ensure"] == 1
