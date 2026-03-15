"""Tests for sync module (fingerprinting, deduplication)."""

import pytest

from taskboard_importer.domain import Task
from taskboard_importer.sync import (
    compute_task_hash,
    detect_drift,
    plan_dedupe,
    DedupeDecision,
)


class TestFingerprinting:
    """Test task content hashing."""

    def test_compute_task_hash(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            activities=["Activity 1"],
            verification=["Check"],
            expected_output="Output",
            done_when="When done",
        )
        hash_value = compute_task_hash(task)

        assert len(hash_value) == 64  # SHA256 hex
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_compute_task_hash_deterministic(self):
        task1 = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            activities=["Activity"],
        )
        task2 = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            activities=["Activity"],
        )
        hash1 = compute_task_hash(task1)
        hash2 = compute_task_hash(task2)
        assert hash1 == hash2

    def test_compute_task_hash_changes_with_content(self):
        task1 = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            activities=["Activity"],
        )
        task2 = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            activities=["Different activity"],
        )
        hash1 = compute_task_hash(task1)
        hash2 = compute_task_hash(task2)
        assert hash1 != hash2


class TestDeduplication:
    """Test deduplication planning."""

    def test_plan_dedupe_skip_policy_unchanged(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            activities=["Activity"],
        )
        task_hash = compute_task_hash(task)
        task.content_hash = task_hash  # Set the hash on the task
        previous = {"1.1": task_hash}

        decisions = plan_dedupe([task], previous, policy="skip")

        assert len(decisions) == 1
        assert decisions[0].action == "skip"

    def test_plan_dedupe_skip_policy_changed(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            activities=["New activity"],
        )
        previous = {"1.1": "old_hash_value"}

        decisions = plan_dedupe([task], previous, policy="skip")

        assert len(decisions) == 1
        assert decisions[0].action == "create"

    def test_plan_dedupe_create_policy(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
        )
        previous = {"1.1": "some_hash"}

        decisions = plan_dedupe([task], previous, policy="create")

        assert len(decisions) == 1
        assert decisions[0].action == "create"

    def test_plan_dedupe_update_policy_changed(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            activities=["New activity"],
        )
        previous = {"1.1": "old_hash"}

        decisions = plan_dedupe([task], previous, policy="update")

        assert len(decisions) == 1
        assert decisions[0].action == "update"


class TestDriftDetection:
    """Test drift detection."""

    def test_detect_drift_new_tasks(self):
        task1 = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
        )
        task2 = Task(
            task_id="1.2",
            phase_id="1",
            section_ref="1.2",
            title="Task 2",
        )
        previous = {}

        report = detect_drift([task1, task2], previous)

        assert report.total_tasks == 2
        assert report.new_tasks == 2
        assert report.updated_tasks == 0
        assert report.unchanged_tasks == 0

    def test_detect_drift_removed_tasks(self):
        previous = {"1.1": "hash", "1.2": "hash"}

        report = detect_drift([], previous)

        assert report.total_tasks == 0
        assert report.removed_tasks == 2
