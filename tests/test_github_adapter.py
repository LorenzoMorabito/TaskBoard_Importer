from taskboard_importer.github_adapter import GitHubAdapter
from taskboard_importer.schema import Task


def test_ensure_labels_creates_missing(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=None,
        default_status=None,
        dry_run=True,
    )

    created = []

    def fake_list_labels():
        return ["Phase A"]

    def fake_create_label(name):
        created.append(name)

    monkeypatch.setattr(adapter, "_list_labels", fake_list_labels)
    monkeypatch.setattr(adapter, "_create_label", fake_create_label)

    failed = adapter.ensure_labels(["Phase A", "Phase B", "Phase C", "Phase B"])

    assert failed == []
    assert set(created) == {"Phase B", "Phase C"}


def test_create_label_payload(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=None,
        default_status=None,
        dry_run=True,
    )

    captured = {}

    def fake_rest_post(url, payload):
        captured["url"] = url
        captured["payload"] = payload
        return {}

    monkeypatch.setattr(adapter, "_rest_post", fake_rest_post)

    adapter._create_label("Phase X")

    assert captured["payload"]["name"] == "Phase X"
    assert captured["payload"]["color"] == "1f6feb"
    assert captured["payload"]["description"] == "Auto-created phase label"


def _make_task(task_id: str, section_ref: str) -> Task:
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


def test_update_tasks_uses_section_ref_mapping(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=None,
        default_status=None,
        dry_run=False,
    )
    task = _make_task("t-1", "1.1")

    called = {"update": 0}

    def fake_update_task(task_obj, phase_label, issue_number, project_item_id):
        called["update"] += 1
        assert issue_number == 123
        return "updated"

    monkeypatch.setattr(adapter, "_update_task", fake_update_task)
    monkeypatch.setattr(adapter, "_publish_task", lambda *_args, **_kwargs: "created")
    monkeypatch.setattr(adapter, "ensure_labels", lambda *_args, **_kwargs: [])

    results = adapter.update_tasks(
        [task],
        {"1": "Phase 1"},
        issue_map={"1.1": 123},
        project_item_map={},
    )

    assert called["update"] == 1
    assert len(results) == 1
    assert results[0] == "updated"


def test_update_tasks_uses_task_id_mapping(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=None,
        default_status=None,
        dry_run=False,
    )
    task = _make_task("t-10", "9.9")

    called = {"update": 0}

    def fake_update_task(task_obj, phase_label, issue_number, project_item_id):
        called["update"] += 1
        assert issue_number == 321
        return "updated"

    monkeypatch.setattr(adapter, "_update_task", fake_update_task)
    monkeypatch.setattr(adapter, "_publish_task", lambda *_args, **_kwargs: "created")
    monkeypatch.setattr(adapter, "ensure_labels", lambda *_args, **_kwargs: [])

    results = adapter.update_tasks(
        [task],
        {"1": "Phase 1"},
        issue_map={"t-10": 321},
        project_item_map={},
    )

    assert called["update"] == 1
    assert len(results) == 1
    assert results[0] == "updated"


def test_update_tasks_fallbacks_to_create(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=None,
        default_status=None,
        dry_run=False,
    )
    task = _make_task("t-2", "1.2")

    called = {"publish": 0}

    def fake_publish_task(task_obj, phase_label):
        called["publish"] += 1
        return "created"

    monkeypatch.setattr(adapter, "_update_task", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(adapter, "_publish_task", fake_publish_task)
    monkeypatch.setattr(adapter, "ensure_labels", lambda *_args, **_kwargs: [])

    results = adapter.update_tasks(
        [task],
        {"1": "Phase 1"},
        issue_map={},
        project_item_map={},
    )

    assert called["publish"] == 1
    assert len(results) == 1
    assert results[0] == "created"


def test_update_task_patch_payload(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=None,
        default_status="Todo",
        dry_run=False,
    )
    task = _make_task("t-3", "1.3")

    captured = {}

    def fake_rest_patch(url, payload):
        captured["url"] = url
        captured["payload"] = payload
        return {}

    monkeypatch.setattr(adapter, "_rest_patch", fake_rest_patch)
    monkeypatch.setattr(adapter, "_set_project_status", lambda *_args, **_kwargs: None)

    result = adapter._update_task(task, "Phase 1", 456, project_item_id=None)

    assert "/issues/456" in captured["url"]
    assert captured["payload"]["title"] == task.title
    assert "Section: 1.3" in captured["payload"]["body"]
    assert captured["payload"]["labels"] == ["Phase 1"]
    assert result.action == "updated"
    assert result.project_sync_status == "skipped"


def test_update_task_patch_error(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=None,
        default_status="Todo",
        dry_run=False,
    )
    task = _make_task("t-4", "1.4")

    def fake_rest_patch(_url, _payload):
        raise RuntimeError("boom")

    monkeypatch.setattr(adapter, "_rest_patch", fake_rest_patch)
    monkeypatch.setattr(adapter, "_set_project_status", lambda *_args, **_kwargs: None)

    result = adapter._update_task(task, "Phase 1", 999, project_item_id=None)

    assert result.action == "failed"
    assert "boom" in result.error_message
    assert result.project_sync_status == "failed"


def test_update_task_recovers_project_item(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=1,
        default_status="Todo",
        dry_run=False,
    )
    task = _make_task("t-5", "1.5")

    monkeypatch.setattr(adapter, "_rest_patch", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(adapter, "_get_project_id", lambda: "proj-1")
    monkeypatch.setattr(adapter, "_get_issue_node_id", lambda _issue: "issue-node")
    monkeypatch.setattr(adapter, "_find_project_item_id", lambda _proj, _issue: "item-9")
    called = {"status": 0}

    def fake_set_status(item_id, _status):
        assert item_id == "item-9"
        called["status"] += 1

    monkeypatch.setattr(adapter, "_set_project_status", fake_set_status)

    result = adapter._update_task(task, "Phase 1", 111, project_item_id=None)

    assert result.project_item_id == "item-9"
    assert result.project_sync_status == "recovered"
    assert called["status"] == 1


def test_update_task_no_lookup_when_project_item_present(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=1,
        default_status="Todo",
        dry_run=False,
    )
    task = _make_task("t-6", "1.6")

    monkeypatch.setattr(adapter, "_rest_patch", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(adapter, "_get_project_id", lambda: (_ for _ in ()).throw(RuntimeError("should not call")))
    monkeypatch.setattr(adapter, "_get_issue_node_id", lambda _issue: (_ for _ in ()).throw(RuntimeError("should not call")))
    monkeypatch.setattr(adapter, "_find_project_item_id", lambda _proj, _issue: (_ for _ in ()).throw(RuntimeError("should not call")))
    monkeypatch.setattr(adapter, "_set_project_status", lambda *_args, **_kwargs: None)

    result = adapter._update_task(task, "Phase 1", 222, project_item_id="item-2")

    assert result.project_sync_status == "found"


def test_update_task_project_lookup_error(monkeypatch):
    adapter = GitHubAdapter(
        token="t",
        repo_owner="owner",
        repo_name="repo",
        project_number=1,
        default_status="Todo",
        dry_run=False,
    )
    task = _make_task("t-7", "1.7")

    monkeypatch.setattr(adapter, "_rest_patch", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(adapter, "_get_project_id", lambda: (_ for _ in ()).throw(RuntimeError("lookup failed")))
    monkeypatch.setattr(adapter, "_set_project_status", lambda *_args, **_kwargs: None)

    result = adapter._update_task(task, "Phase 1", 333, project_item_id=None)

    assert result.action == "updated"
    assert result.project_sync_status == "failed"
    assert "Project sync failed" in result.error_message
