"""Drift detection and reporting."""

from dataclasses import dataclass, field
from typing import Dict, List

from ..domain import Task


@dataclass
class DriftReport:
    """Report on differences between source and previous state.
    
    Tracks what changed, what was removed, what's new.
    """

    total_tasks: int = 0
    new_tasks: int = 0
    updated_tasks: int = 0
    unchanged_tasks: int = 0
    removed_tasks: int = 0

    new_task_ids: List[str] = field(default_factory=list)
    updated_task_ids: List[str] = field(default_factory=list)
    unchanged_task_ids: List[str] = field(default_factory=list)
    removed_task_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "total_tasks": self.total_tasks,
            "new_tasks": self.new_tasks,
            "updated_tasks": self.updated_tasks,
            "unchanged_tasks": self.unchanged_tasks,
            "removed_tasks": self.removed_tasks,
            "new_task_ids": self.new_task_ids,
            "updated_task_ids": self.updated_task_ids,
            "unchanged_task_ids": self.unchanged_task_ids,
            "removed_task_ids": self.removed_task_ids,
        }


def detect_drift(
    current_tasks: List[Task], previous_hashes: Dict[str, str]
) -> DriftReport:
    """Detect differences between current and previous state.
    
    Args:
        current_tasks: Current list of tasks
        previous_hashes: Previous task_id/section_ref -> hash mapping
        
    Returns:
        DriftReport with summary and details
    """
    from .fingerprints import compute_task_hash

    report = DriftReport(total_tasks=len(current_tasks))

    current_ids = set()
    previous_ids = set(previous_hashes.keys())

    for task in current_tasks:
        task_hash = compute_task_hash(task)
        current_ids.add(task.task_id)

        if task.task_id in previous_hashes:
            if task_hash == previous_hashes[task.task_id]:
                report.unchanged_task_ids.append(task.task_id)
                report.unchanged_tasks += 1
            else:
                report.updated_task_ids.append(task.task_id)
                report.updated_tasks += 1
        elif task.section_ref in previous_hashes:
            if task_hash == previous_hashes[task.section_ref]:
                report.unchanged_task_ids.append(task.task_id)
                report.unchanged_tasks += 1
            else:
                report.updated_task_ids.append(task.task_id)
                report.updated_tasks += 1
        else:
            report.new_task_ids.append(task.task_id)
            report.new_tasks += 1

    # Find removed tasks
    removed = previous_ids - current_ids
    report.removed_task_ids = list(removed)
    report.removed_tasks = len(removed)

    return report
