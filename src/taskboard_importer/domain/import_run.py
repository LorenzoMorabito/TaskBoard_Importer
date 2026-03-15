"""Import run execution tracking models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass
class PublishResult:
    """Result of publishing a single task to GitHub.
    
    Attributes:
        task_id: ID of the published task
        github_issue_number: GitHub issue number created/updated
        project_item_id: GitHub Projects v2 item ID
        publish_status: Status (success, failed, skipped)
        action: Action performed (create, update, skip)
        phase_label: Phase label assigned
        section_ref: Source section reference
        matched_by: How the task was matched to existing issue
        previous_hash: Previous content hash
        new_hash: New content hash
        updated_issue_number: Issue number if updated
        project_sync_status: Project synchronization status
        error_message: Error details if failed
    """

    task_id: str
    github_issue_number: Optional[int]
    project_item_id: Optional[str]
    publish_status: str
    action: str = ""
    phase_label: str = ""
    section_ref: str = ""
    matched_by: str = ""
    previous_hash: str = ""
    new_hash: str = ""
    updated_issue_number: Optional[int] = None
    project_sync_status: str = ""
    error_message: str = ""

    def to_dict(self) -> Dict[str, object]:
        """Convert result to dictionary representation."""
        return asdict(self)


@dataclass
class ImportRun:
    """Complete record of an import execution.
    
    Attributes:
        run_id: Unique ID for this import run
        actor: User or system performing the import
        source_version: Version hash of source file
        target_project: Target GitHub project
        result_summary: Overall summary of results
        task_fingerprints: Map of task_id to content hash
        publish_results: List of publish results for each task
    """

    run_id: str
    actor: str
    source_version: str
    target_project: str
    result_summary: Dict[str, object]
    task_fingerprints: Dict[str, str]
    publish_results: List[PublishResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """Convert run to dictionary representation."""
        return {
            "run_id": self.run_id,
            "actor": self.actor,
            "source_version": self.source_version,
            "target_project": self.target_project,
            "result_summary": self.result_summary,
            "task_fingerprints": self.task_fingerprints,
            "publish_results": [result.to_dict() for result in self.publish_results],
        }
