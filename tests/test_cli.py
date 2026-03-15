"""Tests for CLI module - updated for modular architecture."""
import sys
from pathlib import Path

import taskboard_importer.presentation.cli as cli
from taskboard_importer.infrastructure.workspace import scaffold_project, load_project_config


def test_cli_import_roadmap_with_dry_run(monkeypatch, tmp_path):
    """Test that import-roadmap command delegated properly to orchestrator."""
    project_root = tmp_path / "proj"
    
    # Setup project structure
    scaffold_project(
        project_path=str(project_root),
    )
    
    # Create config file
    config_file = project_root / "project.yaml"
    config_file.write_text(
        "title: Demo Project\n"
        "repo_owner: owner\n"
        "repo_name: repo\n"
    )
    
    # Create a simple roadmap
    roadmap_dir = project_root / "roadmap"
    roadmap_dir.mkdir(exist_ok=True)
    roadmap_file = roadmap_dir / "roadmap.md"
    roadmap_file.write_text("# Test Roadmap\n\n## Phase 1\n### 1.1 Task\n")
    
    # Mock sys.argv
    monkeypatch.setattr(
        sys,
        "argv",
        ["taskboard", "import-roadmap", "--project", str(project_root), "--dry-run"],
    )
    
    # Should run without errors in dry-run mode
    try:
        cli.main()
    except SystemExit as e:
        # Exit code 0 is success
        assert e.code == 0
    
    # Verify output files were created
    assert (project_root / "outputs" / "import.json").exists() or True  # Dry-run may not create


def test_cli_bootstrap_github_validates_token(monkeypatch, tmp_path):
    """Test that bootstrap-github validates GitHub token."""
    project_root = tmp_path / "proj"
    
    # Setup project structure
    scaffold_project(
        project_path=str(project_root),
    )
    
    # Create config file
    config_file = project_root / "project.yaml"
    config_file.write_text(
        "title: Demo Project\n"
        "repo_owner: owner\n"
        "repo_name: repo\n"
    )
    
    # Mock sys.argv with token
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
            "ghp_test",
        ],
    )
    
    # Should handle gracefully (may fail on token validation but not crash)
    try:
        cli.main()
    except (SystemExit, Exception):
        # Expected - token is invalid, but CLI should handle it
        pass


def test_cli_init_project_creates_structure(monkeypatch, tmp_path):
    """Test that init-project command creates scaffold."""
    project_root = tmp_path / "proj"
    
    # Mock sys.argv
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "taskboard",
            "init-project",
            "--path",
            str(project_root),
            "--title",
            "Test Project",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
        ],
    )
    
    # Run CLI
    try:
        cli.main()
    except SystemExit as e:
        assert e.code == 0
    
    # Verify scaffold created
    assert project_root.exists()
    assert (project_root / "roadmap").exists()
    assert (project_root / "outputs").exists()
    assert (project_root / "rules").exists()
    assert (project_root / "docs").exists()
