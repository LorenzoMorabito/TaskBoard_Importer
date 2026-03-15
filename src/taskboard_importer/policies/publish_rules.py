"""Publishing rules and policies.

Defines rules for which tasks can be published, how they should be published,
and the constraints for publication.
"""

from enum import Enum
from typing import List


class PublishPolicy(Enum):
    """Policy for publishing a task."""

    PUBLISH_AS_ISSUE = "publish_as_issue"
    """Standard operational task → GitHub Issue synced to Project"""

    PUBLISH_AS_DOC_ISSUE = "publish_as_doc_issue"
    """Documentation task → Deferred (not yet published)"""

    PUBLISH_AS_NOTE = "publish_as_note"
    """Informational task → Manifest only (not published to GitHub)"""

    SKIP = "skip"
    """Explicitly skip publishing"""


class TaskType(Enum):
    """Classification of task type."""

    OPERATIONAL_TASK = "operational_task"
    """Has verification criteria → actionable"""

    CHECKLIST = "checklist"
    """Collection of checkboxes → documentation"""

    DOCUMENTATION = "documentation"
    """Reference material without verification"""

    STATUS_REGISTER = "status_register"
    """Table or status tracking → non-publishable"""


def get_publishable_policies() -> List[PublishPolicy]:
    """Get policies for tasks that should be published to GitHub.
    
    Returns:
        List of publishable policies
    """
    return [PublishPolicy.PUBLISH_AS_ISSUE]


def get_manifest_policies() -> List[PublishPolicy]:
    """Get policies for tasks that should appear in manifest only.
    
    Returns:
        List of manifest-only policies
    """
    return [
        PublishPolicy.PUBLISH_AS_DOC_ISSUE,
        PublishPolicy.PUBLISH_AS_NOTE,
        PublishPolicy.SKIP,
    ]
