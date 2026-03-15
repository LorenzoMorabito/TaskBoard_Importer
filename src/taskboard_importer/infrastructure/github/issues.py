"""GitHub Issues management."""

from typing import Any, Dict, List, Optional

from .client import GitHubClient


class IssuesClient(GitHubClient):
    """GitHub Issues API operations."""

    def create_issue(
        self,
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
    ) -> tuple[int, str]:
        """Create a new issue.
        
        Args:
            repo_owner: Repository owner login
            repo_name: Repository name
            title: Issue title
            body: Issue body/description
            labels: Optional list of label names
            
        Returns:
            Tuple of (issue_number, node_id)
        """
        url = f"{self.rest_base}/repos/{repo_owner}/{repo_name}/issues"
        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels

        data = self.rest_post(url, payload)
        return data["number"], data["node_id"]

    def update_issue(
        self,
        repo_owner: str,
        repo_name: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> None:
        """Update an existing issue.
        
        Args:
            repo_owner: Repository owner login
            repo_name: Repository name
            issue_number: Issue number
            title: New title (optional)
            body: New body (optional)
            labels: New labels (optional)
        """
        url = f"{self.rest_base}/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
        payload = {}
        if title:
            payload["title"] = title
        if body:
            payload["body"] = body
        if labels:
            payload["labels"] = labels

        self.rest_patch(url, payload)

    def get_issue(
        self, repo_owner: str, repo_name: str, issue_number: int
    ) -> Dict[str, Any]:
        """Get issue details.
        
        Args:
            repo_owner: Repository owner login
            repo_name: Repository name
            issue_number: Issue number
            
        Returns:
            Issue details dict
        """
        url = f"{self.rest_base}/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
        return self.rest_get(url)

    def list_issues(
        self, repo_owner: str, repo_name: str, labels: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List issues in repository.
        
        Args:
            repo_owner: Repository owner login
            repo_name: Repository name
            labels: Optional label filter
            
        Returns:
            List of issue dicts
        """
        url = f"{self.rest_base}/repos/{repo_owner}/{repo_name}/issues"
        params = {"state": "all", "per_page": 100}
        if labels:
            params["labels"] = ",".join(labels)

        issues = []
        page = 1
        while True:
            params["page"] = page
            # Construct URL with params
            page_url = f"{url}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
            page_issues = self.rest_get(page_url)
            if not page_issues:
                break
            issues.extend(page_issues)
            page += 1

        return issues
