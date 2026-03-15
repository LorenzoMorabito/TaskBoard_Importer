"""Workspace initialization orchestrator."""

import os
from typing import Optional

from ..infrastructure.workspace import create_project_config, scaffold_project


def init_workspace(
    project_path: str,
    title: str,
    template_path: Optional[str] = None,
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
    project_number: Optional[int] = None,
) -> None:
    """Initialize a new project workspace.
    
    Creates project structure and configuration:
    - Directory scaffold (roadmap/, outputs/, rules/, doc/, etc.)
    - Configuration file (project.yaml)
    - GitHub configuration (optional)
    
    Args:
        project_path: Root path for new project
        title: Project title
        template_path: Optional template directory to copy from
        repo_owner: GitHub repo owner (optional)
        repo_name: GitHub repo name (optional)
        project_number: GitHub project number (optional)
    """
    # Create scaffold
    scaffold_project(project_path, template_path)

    # Create config
    create_project_config(
        project_path,
        title=title,
        repo_owner=repo_owner,
        repo_name=repo_name,
        project_number=project_number,
    )
