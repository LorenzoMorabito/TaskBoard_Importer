"""Sync planning with deduplication strategy."""

from dataclasses import dataclass
from typing import Dict, Iterable, List

from ..domain import Task
from .fingerprints import compute_task_hash


@dataclass
class DedupeDecision:
    """Decision for a single task in sync operation."""

    task: Task
    action: str
    """Action to take: 'create', 'update', or 'skip'"""

    previous_hash: str = ""
    """Hash from previous manifest (if any)"""

    matched_by: str = ""
    """How task was matched: 'section_ref' or 'task_id'"""


def plan_dedupe(
    tasks: Iterable[Task], previous: Dict[str, str], policy: str = "skip"
) -> List[DedupeDecision]:
    """Plan synchronization actions based on deduplication policy.
    
    Policies:
    - 'skip' (default): Skip unchanged tasks, create new ones
    - 'create': Always create new issues
    - 'update': Create new, update changed, skip unchanged
    
    Args:
        tasks: Iterable of tasks to plan
        previous: Dict of previous task_id/section_ref -> content_hash
        policy: Deduplication policy
        
    Returns:
        List of DedupeDecision objects
    """
    decisions: List[DedupeDecision] = []

    for task in tasks:
        matched_by = ""
        existing_hash = None

        # Look for existing task by section_ref or task_id
        if task.section_ref in previous:
            existing_hash = previous[task.section_ref]
            matched_by = "section_ref"
        elif task.task_id in previous:
            existing_hash = previous[task.task_id]
            matched_by = "task_id"

        # Apply policy
        if policy == "create":
            decisions.append(
                DedupeDecision(
                    task=task,
                    action="create",
                    previous_hash=existing_hash or "",
                    matched_by=matched_by,
                )
            )
            continue

        if policy == "skip":
            if existing_hash and task.content_hash == existing_hash:
                decisions.append(
                    DedupeDecision(
                        task=task,
                        action="skip",
                        previous_hash=existing_hash,
                        matched_by=matched_by,
                    )
                )
            else:
                decisions.append(
                    DedupeDecision(
                        task=task,
                        action="create",
                        previous_hash=existing_hash or "",
                        matched_by=matched_by,
                    )
                )
            continue

        if policy == "update":
            if existing_hash and task.content_hash == existing_hash:
                decisions.append(
                    DedupeDecision(
                        task=task,
                        action="skip",
                        previous_hash=existing_hash,
                        matched_by=matched_by,
                    )
                )
            elif existing_hash:
                decisions.append(
                    DedupeDecision(
                        task=task,
                        action="update",
                        previous_hash=existing_hash,
                        matched_by=matched_by,
                    )
                )
            else:
                decisions.append(
                    DedupeDecision(
                        task=task,
                        action="create",
                        previous_hash="",
                        matched_by=matched_by,
                    )
                )
            continue

    return decisions
