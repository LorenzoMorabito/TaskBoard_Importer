"""Manifest persistence layer."""

import json
import os
from typing import Dict, Tuple


def load_manifest(path: str) -> Dict[str, str]:
    """Load task fingerprints from previous manifest.
    
    Args:
        path: Path to manifest JSON file
        
    Returns:
        Dict of task_id/section_ref -> content_hash
    """
    if not path or not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("task_fingerprints", {})


def load_manifest_details(
    path: str,
) -> Tuple[Dict[str, str], Dict[str, int], Dict[str, str]]:
    """Load complete manifest including mappings.
    
    Args:
        path: Path to manifest JSON file
        
    Returns:
        Tuple of:
        - fingerprints: task_id -> content_hash
        - issue_map: task_id/section_ref -> github_issue_number
        - project_item_map: task_id/section_ref -> project_item_id
    """
    if not path or not os.path.exists(path):
        return {}, {}, {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fingerprints = data.get("task_fingerprints", {})
    issue_map: Dict[str, int] = {}
    project_item_map: Dict[str, str] = {}

    for result in data.get("publish_results", []) or []:
        task_id = result.get("task_id")
        section_ref = result.get("section_ref")
        issue_number = result.get("github_issue_number") or result.get(
            "updated_issue_number"
        )
        project_item_id = result.get("project_item_id")

        if task_id and issue_number:
            issue_map[task_id] = issue_number
        if section_ref and issue_number:
            issue_map[section_ref] = issue_number
        if task_id and project_item_id:
            project_item_map[task_id] = project_item_id
        if section_ref and project_item_id:
            project_item_map[section_ref] = project_item_id

    return fingerprints, issue_map, project_item_map


def save_manifest(path: str, manifest_data: dict) -> None:
    """Save manifest to JSON file.
    
    Args:
        path: Path to write manifest
        manifest_data: Complete manifest dictionary
    """
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=True)
