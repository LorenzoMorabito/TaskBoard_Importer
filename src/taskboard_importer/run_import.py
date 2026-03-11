from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from typing import Dict, List, Optional

from .dedupe import load_manifest_details, plan_dedupe
from .github_adapter import GitHubAdapter
from .normalizer import normalize_project
from .parser_markdown import parse_markdown
from .review_cli import confirm_publish, render_preview
from .schema import ImportRun, PublishResult, validate_project


def _flatten_tasks(project) -> List:
    tasks = []
    for phase in project.phases:
        tasks.extend(phase.tasks)
    return tasks


def _count_summary_only_phases(project) -> int:
    return len([phase for phase in project.phases if not phase.tasks and (phase.summary or "").strip()])


def _count_task_policies(tasks: List) -> Dict[str, int]:
    counts = {
        "publish_as_issue": 0,
        "publish_as_doc_issue": 0,
        "publish_as_note": 0,
        "skip": 0,
        "unknown": 0,
    }
    for task in tasks:
        policy = getattr(task, "publish_policy", "") or "unknown"
        if policy not in counts:
            counts["unknown"] += 1
        else:
            counts[policy] += 1
    return counts


def _policy_only_result(task, phase_titles, publish_status: str, action: str) -> PublishResult:
    return PublishResult(
        task.task_id,
        None,
        None,
        publish_status,
        action=action,
        phase_label=phase_titles.get(task.phase_id, task.phase_id),
        section_ref=task.section_ref,
        matched_by="section_ref",
        previous_hash="",
        new_hash=task.content_hash,
        project_sync_status="skipped",
    )


def _is_issue_policy(task) -> bool:
    return getattr(task, "publish_policy", "") == "publish_as_issue"


def _is_doc_issue_policy(task) -> bool:
    return getattr(task, "publish_policy", "") == "publish_as_doc_issue"


def _is_note_policy(task) -> bool:
    return getattr(task, "publish_policy", "") in {"publish_as_note", "skip"}


def _safe_makedirs(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _coerce_project_number(value: Optional[object]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid PROJECT_NUMBER '{value}'. Expected integer.") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Markdown roadmap into GitHub Project")
    parser.add_argument("--input", required=True, help="Path to markdown file")
    parser.add_argument("--output-json", default="outputs/sample_import.json")
    parser.add_argument("--manifest", default="outputs/sample_manifest.json")
    parser.add_argument("--dry-run", action="store_true", help="Do not publish to GitHub")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    parser.add_argument("--repo-owner", default=os.getenv("REPO_OWNER"))
    parser.add_argument("--repo-name", default=os.getenv("REPO_NAME"))
    parser.add_argument("--project-number", type=int, default=os.getenv("PROJECT_NUMBER"))
    parser.add_argument("--default-status", default=os.getenv("DEFAULT_STATUS", "Backlog"))
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"))
    parser.add_argument("--dedupe-policy", default="skip", choices=["skip", "create", "update"])
    parser.add_argument("--previous-manifest", default=None)

    args = parser.parse_args()
    try:
        args.project_number = _coerce_project_number(args.project_number)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    project = parse_markdown(args.input)
    project = normalize_project(project, default_status=args.default_status)

    errors = validate_project(project)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    preview = render_preview(project)
    print(preview)

    _safe_makedirs(args.output_json)
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(project.to_dict(), handle, indent=2, ensure_ascii=False)

    flat_tasks = _flatten_tasks(project)
    policy_counts = _count_task_policies(flat_tasks)
    summary_only_phases = _count_summary_only_phases(project)

    prev_fingerprints, prev_issue_map, prev_project_item_map = load_manifest_details(args.previous_manifest)
    decisions = plan_dedupe(flat_tasks, prev_fingerprints, policy=args.dedupe_policy)
    to_create = [d for d in decisions if d.action == "create"]
    to_update = [d for d in decisions if d.action == "update"]
    skipped = [d for d in decisions if d.action == "skip"]

    issue_create = [d for d in to_create if _is_issue_policy(d.task)]
    issue_update = [d for d in to_update if _is_issue_policy(d.task)]
    non_issue_decisions = [d for d in decisions if not _is_issue_policy(d.task)]
    doc_issue_decisions = [d for d in decisions if _is_doc_issue_policy(d.task)]
    note_decisions = [d for d in decisions if _is_note_policy(d.task)]

    if skipped:
        print(f"Skipped {len(skipped)} tasks due to dedupe policy.")

    publish_results: List[PublishResult] = []
    phase_titles = {phase.phase_id: phase.title for phase in project.phases}

    if args.dry_run:
        publish_results = []
        for decision in decisions:
            task = decision.task
            policy = getattr(task, "publish_policy", "") or "unknown"

            if policy == "publish_as_issue":
                action = "dry_run" if decision.action != "skip" else "skipped"
                project_sync_status = "dry_run" if decision.action != "skip" else "skipped"
            elif policy == "publish_as_doc_issue":
                action = "doc_issue_deferred"
                project_sync_status = "skipped"
            elif policy in {"publish_as_note", "skip"}:
                action = "policy_skip"
                project_sync_status = "skipped"
            else:
                action = "policy_skip"
                project_sync_status = "skipped"

            publish_results.append(
                PublishResult(
                    task.task_id,
                    None,
                    None,
                    "dry_run",
                    action=action,
                    phase_label=phase_titles.get(task.phase_id, task.phase_id),
                    section_ref=task.section_ref,
                    matched_by=decision.matched_by or "section_ref",
                    previous_hash=decision.previous_hash,
                    new_hash=task.content_hash,
                    project_sync_status=project_sync_status,
                )
            )
    else:
        if not args.repo_owner or not args.repo_name or not args.token:
            print("Missing repo owner/name/token for publish.")
            return 1
        if not args.yes and not confirm_publish():
            print("Publish cancelled.")
            return 0
        adapter = GitHubAdapter(
            token=args.token,
            repo_owner=args.repo_owner,
            repo_name=args.repo_name,
            project_number=args.project_number,
            default_status=args.default_status,
            dry_run=False,
        )
        try:
            adapter.precheck()
        except Exception as exc:  # noqa: BLE001
            print(f"Precheck failed: {exc}")
            return 1
        publish_results = []
        if issue_create:
            publish_results.extend(adapter.publish_tasks([d.task for d in issue_create], phase_titles))
        if issue_update:
            publish_results.extend(
                adapter.update_tasks(
                    [d.task for d in issue_update],
                    phase_titles,
                    prev_issue_map,
                    prev_project_item_map,
                )
            )
        if skipped:
            publish_results.extend(
                PublishResult(
                    d.task.task_id,
                    None,
                    None,
                    "skipped",
                    action="skipped",
                    phase_label=phase_titles.get(d.task.phase_id, d.task.phase_id),
                    section_ref=d.task.section_ref,
                    matched_by=d.matched_by or "section_ref",
                    previous_hash=d.previous_hash,
                    new_hash=d.task.content_hash,
                    project_sync_status="skipped",
                )
                for d in skipped if _is_issue_policy(d.task)
            )

        for decision in non_issue_decisions:
            task = decision.task
            policy = getattr(task, "publish_policy", "") or "unknown"
            if policy == "publish_as_doc_issue":
                publish_results.append(
                    _policy_only_result(task, phase_titles, publish_status="skipped", action="doc_issue_deferred")
                )
            else:
                publish_results.append(
                    _policy_only_result(task, phase_titles, publish_status="skipped", action="policy_skip")
                )

    decision_map = {d.task.task_id: d for d in decisions}
    for result in publish_results:
        decision = decision_map.get(result.task_id)
        if not decision:
            continue
        result.section_ref = decision.task.section_ref
        result.matched_by = decision.matched_by or "section_ref"
        result.previous_hash = decision.previous_hash
        result.new_hash = decision.task.content_hash

    run = ImportRun(
        run_id=str(uuid.uuid4()),
        actor=os.getenv("USERNAME", "unknown"),
        source_version=project.source_hash,
        target_project=f"{args.repo_owner}/{args.repo_name}" if args.repo_owner and args.repo_name else "dry-run",
        result_summary={
            "tasks_total": len(flat_tasks),
            "tasks_publishable_issue": policy_counts["publish_as_issue"],
            "tasks_doc_issue": policy_counts["publish_as_doc_issue"],
            "tasks_note": policy_counts["publish_as_note"],
            "tasks_policy_skip": policy_counts["skip"],
            "tasks_unknown_policy": policy_counts["unknown"],
            "summary_only_phases": summary_only_phases,
            "tasks_published": len([r for r in publish_results if r.action == "created"]),
            "tasks_updated": len([r for r in publish_results if r.action == "updated"]),
            "tasks_failed": len([r for r in publish_results if r.action == "failed"]),
            "tasks_skipped": len([r for r in publish_results if r.action == "skipped"]),
            "tasks_policy_deferred": len([r for r in publish_results if r.action in {"doc_issue_deferred", "policy_skip"}]),
            "project_sync_found": len([r for r in publish_results if r.project_sync_status == "found"]),
            "project_sync_recovered": len([r for r in publish_results if r.project_sync_status == "recovered"]),
            "project_sync_missing": len([r for r in publish_results if r.project_sync_status == "missing"]),
            "project_sync_failed": len([r for r in publish_results if r.project_sync_status == "failed"]),
            "project_sync_skipped": len([r for r in publish_results if r.project_sync_status == "skipped"]),
            "dry_run": args.dry_run,
        },
        task_fingerprints={task.section_ref: task.content_hash for task in flat_tasks},
        publish_results=publish_results,
    )

    _safe_makedirs(args.manifest)
    with open(args.manifest, "w", encoding="utf-8") as handle:
        json.dump(run.to_dict(), handle, indent=2, ensure_ascii=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
