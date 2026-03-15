"""Tests for GitHub bootstrap orchestration."""

import importlib

bootstrap_module = importlib.import_module(
    "taskboard_importer.application.bootstrap_github"
)


def test_bootstrap_github_validates_token_and_creates_labels(monkeypatch):
    calls = {"validated": 0, "labels": None}

    class FakeGitHubClient:
        def __init__(self, token, dry_run=False):
            self.token = token

        def validate_token(self):
            calls["validated"] += 1
            return True

    class FakeLabelsClient:
        def __init__(self, token):
            self.token = token

        def ensure_labels(self, repo_owner, repo_name, labels):
            calls["labels"] = (repo_owner, repo_name, labels)

    monkeypatch.setattr(bootstrap_module, "GitHubClient", FakeGitHubClient)
    monkeypatch.setattr(bootstrap_module, "LabelsClient", FakeLabelsClient)

    bootstrap_module.bootstrap_github(
        token="token",
        repo_owner="owner",
        repo_name="repo",
        create_labels=["Phase 1", "Documentation"],
        project_number=3,
    )

    assert calls["validated"] == 1
    assert calls["labels"] == ("owner", "repo", ["Phase 1", "Documentation"])
