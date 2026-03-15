"""Sync and deduplication module."""

from .fingerprints import compute_task_hash
from .manifest_store import load_manifest, load_manifest_details, save_manifest
from .sync_planner import DedupeDecision, plan_dedupe
from .drift_report import DriftReport, detect_drift

__all__ = [
    "compute_task_hash",
    "load_manifest",
    "load_manifest_details",
    "save_manifest",
    "DedupeDecision",
    "plan_dedupe",
    "DriftReport",
    "detect_drift",
]

