"""Tests for workspace management using new infrastructure module."""
import os

from taskboard_importer.infrastructure.workspace import scaffold_project, load_project_config


def test_init_project_creates_structure(tmp_path):
    """Test that scaffold_project creates expected directory structure."""
    root = tmp_path / "proj"
    
    # Create scaffold
    scaffold_project(project_path=str(root))
    
    # Verify directory structure
    assert os.path.exists(os.path.join(str(root), "roadmap"))
    assert os.path.exists(os.path.join(str(root), "outputs"))
    assert os.path.exists(os.path.join(str(root), "docs"))
    assert os.path.exists(os.path.join(str(root), "state"))
    assert os.path.exists(os.path.join(str(root), "rules"))
    assert os.path.exists(os.path.join(str(root), "attachments"))
    
    # Create a minimal config file for testing
    config_path = os.path.join(str(root), "project.yaml")
    with open(config_path, "w") as f:
        f.write("title: Test Project\n")
        f.write("repo_owner: test_owner\n")
        f.write("repo_name: test_repo\n")
    
    # Verify config can be loaded
    config = load_project_config(str(root))
    assert config.get("title") == "Test Project"
    assert config.get("repo_owner") == "test_owner"
