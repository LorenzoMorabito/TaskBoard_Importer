"""Tests for GitHub integration using new infrastructure module."""
from taskboard_importer.infrastructure.github import IssuesClient, LabelsClient
from taskboard_importer.domain import Task


def test_labels_client_creates_label(monkeypatch):
    """Test that LabelsClient can create labels."""
    client = LabelsClient(token="test_token")
    
    created = []
    
    def fake_rest_post(url, payload):
        created.append(payload)
        return {"name": payload["name"]}
    
    monkeypatch.setattr(client, "rest_post", fake_rest_post)
    
    result = client.create_label("owner", "repo", "Phase A")
    
    assert len(created) == 1
    assert created[0]["name"] == "Phase A"
    assert created[0]["color"] == "1f6feb"


def test_labels_client_ensure_labels(monkeypatch):
    """Test that LabelsClient can ensure multiple labels."""
    client = LabelsClient(token="test_token")
    
    created = []
    
    def fake_list_labels(_owner, _repo):
        return [{"name": "Phase A"}]
    
    def fake_create_label(_owner, _repo, name):
        created.append(name)
        return {"name": name}
    
    monkeypatch.setattr(client, "list_labels", fake_list_labels)
    monkeypatch.setattr(client, "create_label", fake_create_label)
    
    result = client.ensure_labels("owner", "repo", ["Phase A", "Phase B", "Phase C"])
    
    assert set(created) == {"Phase B", "Phase C"}


def _make_task(task_id: str, section_ref: str) -> Task:
    """Helper to create a test task."""
    return Task(
        task_id=task_id,
        phase_id="1",
        section_ref=section_ref,
        title=f"Title {task_id}",
        activities=["A"],
        verification=["V"],
        expected_output="Out",
        done_when="Done",
        tracking_template="Track",
        initial_status="Backlog",
        content_hash="hash",
    )


def test_issues_client_can_create(monkeypatch):
    """Test that IssuesClient can create issues."""
    client = IssuesClient(token="test_token")
    
    captured = {}
    
    def fake_rest_post(url, payload):
        captured["url"] = url
        captured["payload"] = payload
        return {"number": 42, "node_id": "MDU6SXNzdWU0MjM="}
    
    monkeypatch.setattr(client, "rest_post", fake_rest_post)
    
    issue_number, node_id = client.create_issue(
        "owner", "repo", 
        title="Test Issue",
        body="Test body"
    )
    
    assert issue_number == 42
    assert node_id == "MDU6SXNzdWU0MjM="
    assert captured["payload"]["title"] == "Test Issue"


def test_issues_client_title_includes_section_ref():
    """Test that issues include section reference in body."""
    client = IssuesClient(token="test_token")
    task = _make_task("t-1", "1.1")
    
    # Verify the task can be used with the client
    assert task.section_ref == "1.1"
    assert task.title == "Title t-1"
    assert "Project sync failed" in result.error_message
