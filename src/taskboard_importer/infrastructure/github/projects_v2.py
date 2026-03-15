"""GitHub Projects V2 API operations."""

from typing import Any, Dict, List, Optional

from .client import GitHubClient


class ProjectsV2Client(GitHubClient):
    """GitHub Projects V2 GraphQL API operations."""

    def get_project_id(self, repo_owner: str, repo_name: str, project_number: int) -> str:
        """Get project node ID by number.
        
        Args:
            repo_owner: Repository owner login
            repo_name: Repository name
            project_number: Project number
            
        Returns:
            Project node ID
        """
        query = """
        query ($owner: String!, $repo: String!, $number: Int!) {
            repository(owner: $owner, name: $repo) {
                projectV2(number: $number) {
                    id
                }
            }
        }
        """
        variables = {"owner": repo_owner, "repo": repo_name, "number": project_number}
        data = self.graphql(query, variables)
        return data["repository"]["projectV2"]["id"]

    def add_issue_to_project(
        self, project_id: str, content_id: str
    ) -> str:
        """Add issue to project.
        
        Args:
            project_id: Project node ID
            content_id: Issue/PR node ID
            
        Returns:
            Project item ID
        """
        query = """
        mutation ($project: ID!, $content: ID!) {
            addProjectV2ItemById(input: {projectId: $project, contentId: $content}) {
                item {
                    id
                }
            }
        }
        """
        variables = {"project": project_id, "content": content_id}
        data = self.graphql(query, variables)
        return data["addProjectV2ItemById"]["item"]["id"]

    def set_project_field(
        self,
        project_id: str,
        item_id: str,
        field_id: str,
        value: str,
    ) -> None:
        """Set project field value on item.
        
        Args:
            project_id: Project node ID
            item_id: Project item ID
            field_id: Field node ID
            value: Field value
        """
        query = """
        mutation ($project: ID!, $item: ID!, $field: ID!, $value: String!) {
            updateProjectV2ItemFieldValue(
                input: {
                    projectId: $project
                    itemId: $item
                    fieldId: $field
                    value: {singleSelectOptionId: $value}
                }
            ) {
                projectV2Item {
                    id
                }
            }
        }
        """
        variables = {
            "project": project_id,
            "item": item_id,
            "field": field_id,
            "value": value,
        }
        self.graphql(query, variables)

    def list_project_fields(self, project_id: str) -> List[Dict[str, Any]]:
        """List project fields.
        
        Args:
            project_id: Project node ID
            
        Returns:
            List of field dicts with name and ID
        """
        query = """
        query ($project: ID!) {
            node(id: $project) {
                ... on ProjectV2 {
                    fields(first: 20) {
                        nodes {
                            ... on ProjectV2Field {
                                id
                                name
                            }
                            ... on ProjectV2SingleSelectField {
                                id
                                name
                                options {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"project": project_id}
        data = self.graphql(query, variables)
        return data["node"]["fields"]["nodes"]
