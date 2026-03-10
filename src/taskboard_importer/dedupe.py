from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .schema import Task


def compute_task_hash(task: Task) -> str:
    payload = {
        "title": task.title,
        "activities": task.activities,
        "verification": task.verification,
        "expected_output": task.expected_output,
        "done_when": task.done_when,
        "tracking_template": task.tracking_template,
        "initial_status": task.initial_status,
    }
    raw = json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_manifest(path: str) -> Dict[str, str]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data.get("task_fingerprints", {})


def load_manifest_details(path: str) -> Tuple[Dict[str, str], Dict[str, int], Dict[str, str]]:
    if not path or not os.path.exists(path):
        return {}, {}, {}
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    fingerprints = data.get("task_fingerprints", {})
    issue_map: Dict[str, int] = {}
    project_item_map: Dict[str, str] = {}
    for result in data.get("publish_results", []) or []:
        task_id = result.get("task_id")
        section_ref = result.get("section_ref")
        issue_number = result.get("github_issue_number") or result.get("updated_issue_number")
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


@dataclass
class DedupeDecision:
    task: Task
    action: str
    previous_hash: str = ""
    matched_by: str = ""


def plan_dedupe(tasks: Iterable[Task], previous: Dict[str, str], policy: str = "skip") -> List[DedupeDecision]:
    decisions: List[DedupeDecision] = []

    for task in tasks:
        matched_by = ""
        existing = None
        if task.section_ref in previous:
            existing = previous.get(task.section_ref)
            matched_by = "section_ref"
        elif task.task_id in previous:
            existing = previous.get(task.task_id)
            matched_by = "task_id"
        if policy == "create":
            decisions.append(
                DedupeDecision(task=task, action="create", previous_hash=existing or "", matched_by=matched_by)
            )
            continue
        if policy == "skip":
            if existing and task.content_hash == existing:
                decisions.append(
                    DedupeDecision(task=task, action="skip", previous_hash=existing, matched_by=matched_by)
                )
            else:
                decisions.append(
                    DedupeDecision(task=task, action="create", previous_hash=existing or "", matched_by=matched_by)
                )
            continue
        if policy == "update":
            if existing and task.content_hash == existing:
                decisions.append(
                    DedupeDecision(task=task, action="skip", previous_hash=existing, matched_by=matched_by)
                )
            elif existing:
                decisions.append(
                    DedupeDecision(task=task, action="update", previous_hash=existing, matched_by=matched_by)
                )
            else:
                decisions.append(DedupeDecision(task=task, action="create", previous_hash="", matched_by=matched_by))
            continue

    return decisions
