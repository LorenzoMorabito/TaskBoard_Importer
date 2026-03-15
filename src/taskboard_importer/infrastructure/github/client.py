"""Low-level GitHub REST and GraphQL client."""

from typing import Any, Dict, Optional

import requests


class GitHubClient:
    """Base GitHub API client for REST and GraphQL calls."""

    def __init__(
        self, token: str, dry_run: bool = False, timeout: int = 30
    ) -> None:
        """Initialize GitHub client.
        
        Args:
            token: GitHub personal access token or app token
            dry_run: If True, don't make actual API calls
            timeout: Request timeout in seconds
        """
        self.token = token
        self.dry_run = dry_run
        self.timeout = timeout
        self.rest_base = "https://api.github.com"
        self.graphql_url = "https://api.github.com/graphql"
        self._rate_limit_remaining = None
        self._rate_limit_reset = None

    def _headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "taskboard-importer",
        }

    def rest_get(self, url: str) -> Dict[str, Any]:
        """Make GET request to REST API.
        
        Args:
            url: Full URL to endpoint
            
        Returns:
            Response JSON as dict
            
        Raises:
            requests.RequestException: On HTTP error
        """
        if self.dry_run:
            return {}

        response = requests.get(
            url, headers=self._headers(), timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def rest_post(self, url: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to REST API.
        
        Args:
            url: Full URL to endpoint
            json: Request body as dict
            
        Returns:
            Response JSON as dict
            
        Raises:
            requests.RequestException: On HTTP error
        """
        if self.dry_run:
            return {"dry_run": True}

        response = requests.post(
            url, headers=self._headers(), json=json, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def rest_patch(self, url: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """Make PATCH request to REST API.
        
        Args:
            url: Full URL to endpoint
            json: Request body as dict
            
        Returns:
            Response JSON as dict
            
        Raises:
            requests.RequestException: On HTTP error
        """
        if self.dry_run:
            return {"dry_run": True}

        response = requests.patch(
            url, headers=self._headers(), json=json, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Optional variables dict
            
        Returns:
            Response data dict
            
        Raises:
            requests.RequestException: On HTTP error
            ValueError: If server returns GraphQL errors
        """
        if self.dry_run:
            return {"data": {}}

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            self.graphql_url,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            raise ValueError(f"GraphQL errors: {data['errors']}")

        return data.get("data", {})

    def validate_token(self) -> bool:
        """Validate that token is valid and accessible.
        
        Returns:
            True if token is valid
            
        Raises:
            requests.RequestException: On authentication error
        """
        self.rest_get(f"{self.rest_base}/user")
        return True
