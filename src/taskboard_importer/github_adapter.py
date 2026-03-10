from __future__ import annotations

import json
import os
import time
from typing import Dict, List, Optional, Tuple

import requests

from .schema import ProjectImport, PublishResult, Task


class GitHubAdapter:
    def __init__(
        self,
        token: str,
        repo_owner: str,
        repo_name: str,
        project_number: Optional[int] = None,
        default_status: Optional[str] = None,
        dry_run: bool = False,
    ) -> None:
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.project_number = project_number
        self.default_status = default_status
        self.dry_run = dry_run
        self.rest_base = "https://api.github.com"
        self.graphql_url = "https://api.github.com/graphql"

    def publish_project(self, project: ProjectImport) -> List[PublishResult]:
        results: List[PublishResult] = []
        phase_labels = [phase.title for phase in project.phases for _ in phase.tasks]
        self.ensure_labels(phase_labels)
        for phase in project.phases:
            for task in phase.tasks:
                results.append(self._publish_task(task, phase_label=phase.title))
        return results

    def publish_tasks(self, tasks: List[Task], phase_titles: Dict[str, str]) -> List[PublishResult]:
        results: List[PublishResult] = []
        phase_labels = [phase_titles.get(task.phase_id, task.phase_id) for task in tasks]
        self.ensure_labels(phase_labels)
        for task in tasks:
            phase_label = phase_titles.get(task.phase_id, task.phase_id)
            results.append(self._publish_task(task, phase_label=phase_label))
        return results

    def update_tasks(
        self,
        tasks: List[Task],
        phase_titles: Dict[str, str],
        issue_map: Dict[str, int],
        project_item_map: Dict[str, str],
    ) -> List[PublishResult]:
        results: List[PublishResult] = []
        phase_labels = [phase_titles.get(task.phase_id, task.phase_id) for task in tasks]
        self.ensure_labels(phase_labels)
        for task in tasks:
            phase_label = phase_titles.get(task.phase_id, task.phase_id)
            issue_number = issue_map.get(task.task_id) or issue_map.get(task.section_ref)
            project_item_id = project_item_map.get(task.task_id) or project_item_map.get(task.section_ref)
            if not issue_number:
                results.append(self._publish_task(task, phase_label=phase_label))
                continue
            results.append(self._update_task(task, phase_label, issue_number, project_item_id))
        return results

    def precheck(self) -> None:
        self._rest_get(f"{self.rest_base}/user")
        self._rest_get(f"{self.rest_base}/repos/{self.repo_owner}/{self.repo_name}")
        if self.project_number:
            self._get_project_id()

    def _publish_task(self, task: Task, phase_label: str) -> PublishResult:
        if self.dry_run:
            return PublishResult(
                task_id=task.task_id,
                github_issue_number=None,
                project_item_id=None,
                publish_status="dry_run",
                action="dry_run",
                phase_label=phase_label,
                section_ref=task.section_ref,
                matched_by="section_ref",
                previous_hash="",
                new_hash=task.content_hash,
                project_sync_status="skipped",
            )

        issue_number = None
        project_item_id = None
        try:
            issue_number, node_id = self._create_issue(task, phase_label)
            if self.project_number and node_id:
                project_item_id = self._add_to_project(node_id)
                if project_item_id and self.default_status:
                    self._set_project_status(project_item_id, self.default_status)
            status = "published"
            if self.project_number:
                project_sync_status = "found" if project_item_id else "missing"
            else:
                project_sync_status = "skipped"
            return PublishResult(
                task_id=task.task_id,
                github_issue_number=issue_number,
                project_item_id=project_item_id,
                publish_status=status,
                action="created",
                phase_label=phase_label,
                section_ref=task.section_ref,
                matched_by="section_ref",
                previous_hash="",
                new_hash=task.content_hash,
                project_sync_status=project_sync_status,
            )
        except Exception as exc:  # noqa: BLE001
            return PublishResult(
                task_id=task.task_id,
                github_issue_number=issue_number,
                project_item_id=project_item_id,
                publish_status="error",
                action="failed",
                phase_label=phase_label,
                section_ref=task.section_ref,
                matched_by="section_ref",
                previous_hash="",
                new_hash=task.content_hash,
                error_message=str(exc),
                project_sync_status="failed",
            )

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def _request(
        self,
        method: str,
        url: str,
        json_payload: Optional[Dict[str, object]] = None,
        timeout: int = 30,
    ) -> requests.Response:
        attempt = 0
        while True:
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self._headers(),
                    json=json_payload,
                    timeout=timeout,
                )
            except requests.RequestException as exc:
                if attempt >= 2:
                    raise RuntimeError(f"Request failed: {exc}") from exc
                attempt += 1
                time.sleep(1 + attempt)
                continue

            if response.status_code in {429, 500, 502, 503, 504}:
                if attempt >= 2:
                    return response
                attempt += 1
                retry_after = response.headers.get("Retry-After")
                delay = int(retry_after) if retry_after and retry_after.isdigit() else (1 + attempt)
                time.sleep(delay)
                continue

            return response

    def _rest_get(self, url: str) -> Dict[str, object]:
        response = self._request("GET", url)
        if response.status_code >= 300:
            raise RuntimeError(f"GET failed: {response.status_code} {response.text}")
        return response.json()

    def _rest_post(self, url: str, payload: Dict[str, object]) -> Dict[str, object]:
        response = self._request("POST", url, json_payload=payload)
        if response.status_code >= 300:
            raise RuntimeError(f"POST failed: {response.status_code} {response.text}")
        return response.json()

    def _rest_patch(self, url: str, payload: Dict[str, object]) -> Dict[str, object]:
        response = self._request("PATCH", url, json_payload=payload)
        if response.status_code >= 300:
            raise RuntimeError(f"PATCH failed: {response.status_code} {response.text}")
        return response.json()

    def _create_issue(self, task: Task, phase_label: str) -> Tuple[int, str]:
        url = f"{self.rest_base}/repos/{self.repo_owner}/{self.repo_name}/issues"
        body = self._render_issue_body(task)
        payload = {
            "title": task.title,
            "body": body,
            "labels": [phase_label],
        }
        data = self._rest_post(url, payload)
        return data.get("number"), data.get("node_id")

    def _render_issue_body(self, task: Task) -> str:
        lines = []
        lines.append(f"Section: {task.section_ref}")
        lines.append("")
        if task.activities:
            lines.append("Activities:")
            for item in task.activities:
                lines.append(f"- [ ] {item}")
            lines.append("")
        if task.verification:
            lines.append("Verification:")
            for item in task.verification:
                lines.append(f"- {item}")
            lines.append("")
        if task.expected_output:
            lines.append("Expected output:")
            lines.append(task.expected_output)
            lines.append("")
        if task.done_when:
            lines.append("Done when:")
            lines.append(task.done_when)
            lines.append("")
        if task.tracking_template:
            lines.append("Tracking:")
            lines.append(task.tracking_template)
            lines.append("")
        lines.append(f"Status: {task.initial_status}")
        return "\n".join(lines).strip()

    def _graphql(self, query: str, variables: Dict[str, object]) -> Dict[str, object]:
        response = self._request(
            "POST",
            self.graphql_url,
            json_payload={"query": query, "variables": variables},
        )
        if response.status_code >= 300:
            raise RuntimeError(f"GraphQL error: {response.status_code} {response.text}")
        payload = response.json()
        if "errors" in payload:
            raise RuntimeError(f"GraphQL errors: {payload['errors']}")
        return payload["data"]

    def ensure_labels(self, labels: List[str]) -> List[str]:
        unique = {label.strip() for label in labels if label and label.strip()}
        if not unique:
            return []

        try:
            existing = self._list_labels()
        except Exception:
            return []

        missing = [label for label in unique if label not in existing]
        failed: List[str] = []
        for label in missing:
            try:
                self._create_label(label)
            except Exception:
                failed.append(label)
        return failed

    def _list_labels(self) -> List[str]:
        url = f"{self.rest_base}/repos/{self.repo_owner}/{self.repo_name}/labels?per_page=100"
        data = self._rest_get(url)
        if isinstance(data, list):
            return [item.get("name") for item in data if item.get("name")]
        return []

    def _create_label(self, name: str) -> None:
        url = f"{self.rest_base}/repos/{self.repo_owner}/{self.repo_name}/labels"
        payload = {
            "name": name,
            "color": "1f6feb",
            "description": "Auto-created phase label",
        }
        self._rest_post(url, payload)

    def _update_task(
        self,
        task: Task,
        phase_label: str,
        issue_number: int,
        project_item_id: Optional[str],
    ) -> PublishResult:
        try:
            url = f"{self.rest_base}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}"
            payload = {
                "title": task.title,
                "body": self._render_issue_body(task),
                "labels": [phase_label],
            }
            self._rest_patch(url, payload)
            project_sync_status = "skipped"
            recovered_item_id: Optional[str] = None
            if self.project_number and self.default_status:
                if project_item_id:
                    self._set_project_status(project_item_id, self.default_status)
                    project_sync_status = "found"
                else:
                    try:
                        project_id = self._get_project_id()
                        issue_node_id = self._get_issue_node_id(issue_number)
                        recovered_item_id = self._find_project_item_id(project_id, issue_node_id)
                        if recovered_item_id:
                            self._set_project_status(recovered_item_id, self.default_status)
                            project_item_id = recovered_item_id
                            project_sync_status = "recovered"
                        else:
                            project_sync_status = "missing"
                    except Exception as exc:  # noqa: BLE001
                        project_sync_status = "failed"
                        return PublishResult(
                            task_id=task.task_id,
                            github_issue_number=issue_number,
                            project_item_id=project_item_id,
                            publish_status="updated",
                            action="updated",
                            phase_label=phase_label,
                            section_ref=task.section_ref,
                            matched_by="section_ref",
                            previous_hash="",
                            new_hash=task.content_hash,
                            updated_issue_number=issue_number,
                            project_sync_status=project_sync_status,
                            error_message=f"Project sync failed: {exc}",
                        )
            return PublishResult(
                task_id=task.task_id,
                github_issue_number=issue_number,
                project_item_id=project_item_id,
                publish_status="updated",
                action="updated",
                phase_label=phase_label,
                section_ref=task.section_ref,
                matched_by="section_ref",
                previous_hash="",
                new_hash=task.content_hash,
                updated_issue_number=issue_number,
                project_sync_status=project_sync_status,
            )
        except Exception as exc:  # noqa: BLE001
            return PublishResult(
                task_id=task.task_id,
                github_issue_number=issue_number,
                project_item_id=project_item_id,
                publish_status="error",
                action="failed",
                phase_label=phase_label,
                section_ref=task.section_ref,
                matched_by="section_ref",
                previous_hash="",
                new_hash=task.content_hash,
                updated_issue_number=issue_number,
                error_message=str(exc),
                project_sync_status="failed",
            )

    def _get_project_id(self) -> str:
        if not self.project_number:
            raise RuntimeError("Project number is required")

        query = """
        query($login: String!, $number: Int!) {
          organization(login: $login) {
            projectV2(number: $number) { id }
          }
          user(login: $login) {
            projectV2(number: $number) { id }
          }
        }
        """
        data = self._graphql(query, {"login": self.repo_owner, "number": self.project_number})
        org_project = data.get("organization", {}) or {}
        user_project = data.get("user", {}) or {}
        project = org_project.get("projectV2") or user_project.get("projectV2")
        if not project:
            raise RuntimeError("Project not found")
        return project["id"]

    def _get_status_field(self, project_id: str) -> Optional[Dict[str, object]]:
        query = """
        query($project: ID!) {
          node(id: $project) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2FieldCommon {
                    id
                    name
                  }
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options { id name }
                  }
                }
              }
            }
          }
        }
        """
        data = self._graphql(query, {"project": project_id})
        fields = data.get("node", {}).get("fields", {}).get("nodes", [])
        for field in fields:
            if field.get("name", "").lower() == "status" and "options" in field:
                return field
        return None

    def _add_to_project(self, issue_node_id: str) -> str:
        project_id = self._get_project_id()
        mutation = """
        mutation($project: ID!, $content: ID!) {
          addProjectV2ItemById(input: {projectId: $project, contentId: $content}) {
            item { id }
          }
        }
        """
        data = self._graphql(mutation, {"project": project_id, "content": issue_node_id})
        return data["addProjectV2ItemById"]["item"]["id"]

    def _set_project_status(self, item_id: str, status_name: str) -> None:
        project_id = self._get_project_id()
        field = self._get_status_field(project_id)
        if not field:
            return
        option = None
        for opt in field.get("options", []) or []:
            if opt.get("name") == status_name:
                option = opt
                break
        if not option:
            return
        mutation = """
        mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $project,
            itemId: $item,
            fieldId: $field,
            value: { singleSelectOptionId: $value }
          }) {
            item { id }
          }
        }
        """
        self._graphql(
            mutation,
            {"project": project_id, "item": item_id, "field": field["id"], "value": option["id"]},
        )

    def _get_issue_node_id(self, issue_number: int) -> str:
        url = f"{self.rest_base}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}"
        data = self._rest_get(url)
        node_id = data.get("node_id")
        if not node_id:
            raise RuntimeError("Issue node_id not found")
        return node_id

    def _find_project_item_id(self, project_id: str, issue_node_id: str) -> Optional[str]:
        query = """
        query($project: ID!, $after: String) {
          node(id: $project) {
            ... on ProjectV2 {
              items(first: 50, after: $after) {
                nodes {
                  id
                  content {
                    ... on Issue { id }
                  }
                }
                pageInfo { hasNextPage endCursor }
              }
            }
          }
        }
        """
        cursor = None
        while True:
            data = self._graphql(query, {"project": project_id, "after": cursor})
            items = data.get("node", {}).get("items", {})
            for node in items.get("nodes", []) or []:
                content = node.get("content") or {}
                if content.get("id") == issue_node_id:
                    return node.get("id")
            page = items.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                break
            cursor = page.get("endCursor")
        return None
