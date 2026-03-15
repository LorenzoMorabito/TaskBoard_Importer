"""Task fingerprinting via content hashing."""

import hashlib
import json

from ..domain import Task


def compute_task_hash(task: Task) -> str:
    """Compute SHA256 fingerprint of task content for deduplication.
    
    Hash includes:
    - title
    - activities
    - verification criteria
    - expected output
    - done when criteria
    - tracking template
    - initial status
    
    Args:
        task: Task to hash
        
    Returns:
        Hex digest of SHA256 hash
    """
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
