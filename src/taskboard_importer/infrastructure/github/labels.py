"""GitHub Labels management."""

from typing import List

from .client import GitHubClient


class LabelsClient(GitHubClient):
    """GitHub Labels API operations."""

    def create_label(
        self, repo_owner: str, repo_name: str, name: str, color: str = "0366d6"
    ) -> None:
        """Create a label in repository.
        
        Args:
            repo_owner: Repository owner login
            repo_name: Repository name
            name: Label name
            color: Label color (hex, without #)
        """
        url = f"{self.rest_base}/repos/{repo_owner}/{repo_name}/labels"
        payload = {"name": name, "color": color, "description": name}
        self.rest_post(url, payload)

    def list_labels(self, repo_owner: str, repo_name: str) -> List[str]:
        """List all labels in repository.
        
        Args:
            repo_owner: Repository owner login
            repo_name: Repository name
            
        Returns:
            List of label names
        """
        url = f"{self.rest_base}/repos/{repo_owner}/{repo_name}/labels?per_page=100"
        data = self.rest_get(url)
        return [label["name"] for label in data]

    def ensure_labels(
        self, repo_owner: str, repo_name: str, label_names: List[str]
    ) -> None:
        """Ensure labels exist, creating if needed.
        
        Args:
            repo_owner: Repository owner login
            repo_name: Repository name
            label_names: List of label names to ensure
        """
        existing = self.list_labels(repo_owner, repo_name)
        existing_set = set(existing)

        for label_name in label_names:
            if label_name not in existing_set:
                try:
                    self.create_label(repo_owner, repo_name, label_name)
                except Exception:
                    # Label might exist or be invalid, continue
                    pass
