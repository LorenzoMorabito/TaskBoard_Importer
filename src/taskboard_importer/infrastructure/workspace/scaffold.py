"""Project workspace scaffolding and initialization."""

import os
import shutil
from typing import Optional


def scaffold_project(
    project_path: str, template_path: Optional[str] = None
) -> None:
    """Create project workspace structure.
    
    Creates directories:
    - roadmap/
    - outputs/
    - rules/
    - docs/
    - attachments/
    - state/
    
    Args:
        project_path: Root path for project
        template_path: Optional template directory to copy from
    """
    os.makedirs(project_path, exist_ok=True)

    subdirs = [
        "roadmap",
        "outputs",
        "rules",
        "docs",
        "attachments",
        "state",
    ]

    for subdir in subdirs:
        dir_path = os.path.join(project_path, subdir)
        os.makedirs(dir_path, exist_ok=True)

    # Copy template if provided
    if template_path and os.path.exists(template_path):
        for item in os.listdir(template_path):
            src = os.path.join(template_path, item)
            dst = os.path.join(project_path, item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            elif not os.path.exists(dst):
                shutil.copy2(src, dst)


def create_project_config(
    project_path: str,
    title: str,
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
    project_number: Optional[int] = None,
) -> None:
    """Create project.yaml configuration file.
    
    Args:
        project_path: Project root path
        title: Project title
        repo_owner: GitHub repo owner (optional)
        repo_name: GitHub repo name (optional)
        project_number: GitHub project number (optional)
    """
    import json

    config = {
        "title": title,
        "paths": {
            "roadmap": "roadmap/roadmap.md",
            "outputs": "outputs",
            "rules": "rules",
            "docs": "docs",
        },
    }

    if repo_owner or repo_name or project_number:
        github_config = {}
        if repo_owner:
            github_config["repo_owner"] = repo_owner
        if repo_name:
            github_config["repo_name"] = repo_name
        if project_number:
            github_config["project_number"] = project_number
        config["github"] = github_config

    config_path = os.path.join(project_path, "project.yaml")
    # Use YAML if pyyaml available, else JSON
    try:
        import yaml
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    except ImportError:
        # Fall back to JSON with .json extension
        config_path = os.path.join(project_path, "project.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
