"""GitHub bootstrap orchestrator.

Sets up GitHub repository and project for integration.
"""

from typing import Optional

from ..infrastructure.github.client import GitHubClient
from ..infrastructure.github.labels import LabelsClient


def bootstrap_github(
    token: str,
    repo_owner: str,
    repo_name: str,
    create_labels: Optional[list[str]] = None,
) -> None:
    """Bootstrap GitHub repository for use with importer.
    
    Prepares:
    - Validates GitHub access
    - Creates phase labels
    - Sets up project integration (if applicable)
    
    Args:
        token: GitHub personal access token
        repo_owner: GitHub repo owner
        repo_name: GitHub repo name
        create_labels: List of labels to create
    """
    client = GitHubClient(token, dry_run=False)

    # Validate access
    client.validate_token()

    # Create labels
    if create_labels:
        labels_client = LabelsClient(token)
        labels_client.ensure_labels(repo_owner, repo_name, create_labels)
