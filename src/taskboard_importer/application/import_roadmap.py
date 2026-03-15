"""Main import roadmap orchestrator.

Coordinates the complete pipeline:
1. Parse Markdown
2. Normalize and classify
3. Deduplicate against previous state
4. Publish to GitHub (if not dry-run)
5. Save manifest and results
"""

import json
import os
from typing import Dict, List, Optional

from ..domain import ImportRun, ProjectImport, PublishResult, validate_project
from ..parsing import parse_markdown
from ..policies import normalize_project
from ..sync import (
    compute_task_hash,
    load_manifest_details,
    plan_dedupe,
    save_manifest,
)


def _flatten_tasks(project: ProjectImport) -> List:
    """Flatten phases into single task list."""
    tasks = []
    for phase in project.phases:
        tasks.extend(phase.tasks)
    return tasks


def _count_summary_only_phases(project: ProjectImport) -> int:
    """Count phases with summary but no tasks."""
    return len(
        [
            phase
            for phase in project.phases
            if not phase.tasks and (phase.summary or "").strip()
        ]
    )


def _count_task_policies(tasks: List) -> Dict[str, int]:
    """Count tasks by publish policy."""
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


def import_roadmap(
    input_path: str,
    output_json: Optional[str] = None,
    manifest_json: Optional[str] = None,
    previous_manifest: Optional[str] = None,
    dedupe_policy: str = "skip",
    publish_to_github: bool = False,
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
    token: Optional[str] = None,
    project_number: Optional[int] = None,
    default_status: str = "Backlog",
    dry_run: bool = True,
) -> tuple[ProjectImport, List[PublishResult], ImportRun]:
    """Execute complete import pipeline.
    
    Args:
        input_path: Path to Markdown roadmap
        output_json: Path to write normalized import.json
        manifest_json: Path to write manifest.json with results
        previous_manifest: Path to previous manifest for deduplication
        dedupe_policy: 'skip', 'create', or 'update'
        publish_to_github: Whether to publish (ignored if dry_run=True)
        repo_owner: GitHub repo owner
        repo_name: GitHub repo name
        token: GitHub token
        project_number: GitHub project number
        default_status: Default task status
        dry_run: If True, preview only
        
    Returns:
        Tuple of (ProjectImport, PublishResults, ImportRun)
    """
    # 1. PARSE
    project = parse_markdown(input_path)

    # 2. NORMALIZE
    project = normalize_project(project, default_status=default_status)

    # 3. VALIDATE
    errors = validate_project(project)
    if errors:
        raise ValueError(f"Project validation failed:\n" + "\n".join(errors))

    # 4. FLATTEN AND ANALYZE
    flat_tasks = _flatten_tasks(project)
    policy_counts = _count_task_policies(flat_tasks)
    summary_only_phases = _count_summary_only_phases(project)

    # 5. DEDUPLICATE
    prev_fingerprints, prev_issue_map, prev_project_item_map = load_manifest_details(
        previous_manifest
    )
    decisions = plan_dedupe(flat_tasks, prev_fingerprints, policy=dedupe_policy)

    # 6. PUBLISH
    publish_results: List[PublishResult] = []
    phase_titles = {phase.phase_id: phase.title for phase in project.phases}

    if dry_run:
        # Generate dry-run results
        for decision in decisions:
            task = decision.task
            policy = getattr(task, "publish_policy", "") or "unknown"

            if policy == "publish_as_issue":
                action = "dry_run" if decision.action != "skip" else "skipped"
                status = "dry_run"
            elif policy == "publish_as_doc_issue":
                action = "doc_issue_deferred"
                status = "deferred"
            else:
                action = "policy_skip"
                status = "skipped"

            publish_results.append(
                PublishResult(
                    task_id=task.task_id,
                    github_issue_number=None,
                    project_item_id=None,
                    publish_status=status,
                    action=action,
                    phase_label=phase_titles.get(task.phase_id, task.phase_id),
                    section_ref=task.section_ref,
                    matched_by=decision.matched_by or "section_ref",
                    previous_hash=decision.previous_hash,
                    new_hash=task.content_hash,
                    project_sync_status="skipped",
                )
            )
    else:
        # Real GitHub publishing
        if not (token and repo_owner and repo_name):
            raise ValueError(
                "GitHub publish requires: token, repo_owner, repo_name"
            )
        
        from ..infrastructure.github import IssuesClient, ProjectsV2Client
        
        issues_client = IssuesClient(token, dry_run=False)
        projects_client = ProjectsV2Client(token, dry_run=False) if project_number else None
        project_id = None
        
        if projects_client and project_number:
            try:
                project_id = projects_client.get_project_id(
                    repo_owner, repo_name, project_number
                )
            except Exception as e:
                print(f"Warning: Could not retrieve project {project_number}: {e}")
        
        for decision in decisions:
            task = decision.task
            policy = getattr(task, "publish_policy", "") or "unknown"
            
            if policy not in ["publish_as_issue", "publish_as_doc_issue"]:
                # Skip non-publishable policies
                publish_results.append(
                    PublishResult(
                        task_id=task.task_id,
                        github_issue_number=None,
                        project_item_id=None,
                        publish_status="skipped",
                        action="policy_skip",
                        phase_label=phase_titles.get(task.phase_id, task.phase_id),
                        section_ref=task.section_ref,
                        matched_by=decision.matched_by or "section_ref",
                        previous_hash=decision.previous_hash,
                        new_hash=task.content_hash,
                        project_sync_status="not_applicable",
                    )
                )
                continue
            
            # Build issue content
            title = f"[{task.task_id}] {task.title}" if task.title else f"[{task.task_id}] Task"
            body = task.description or ""
            labels = []
            if task.task_type:
                labels.append(task.task_type)
            
            issue_number = None
            issue_node_id = None
            project_item_id = None
            action = None
            status = None
            sync_status = "pending"
            
            try:
                if decision.action == "create":
                    # Create new issue
                    issue_number, issue_node_id = issues_client.create_issue(
                        repo_owner=repo_owner,
                        repo_name=repo_name,
                        title=title,
                        body=body,
                        labels=labels if labels else None,
                    )
                    action = "created"
                    status = "published"
                    
                    # Add to project if configured
                    if project_id and issue_node_id:
                        try:
                            project_item_id = projects_client.add_issue_to_project(
                                project_id, issue_node_id
                            )
                            sync_status = "synced"
                        except Exception as e:
                            print(f"Warning: Could not add issue to project: {e}")
                            sync_status = "sync_failed"
                
                elif decision.action == "update":
                    # Update existing issue
                    if decision.matched_by == "github_issue_number":
                        issue_number = int(decision.previous_hash or 0)
                    if issue_number:
                        issues_client.update_issue(
                            repo_owner=repo_owner,
                            repo_name=repo_name,
                            issue_number=issue_number,
                            title=title,
                            body=body,
                            labels=labels if labels else None,
                        )
                        action = "updated"
                        status = "published"
                        sync_status = "synced"
                    else:
                        # Cannot find issue to update
                        action = "update_failed"
                        status = "error"
                        sync_status = "sync_failed"
                
                else:  # skip
                    action = "skipped"
                    status = "skipped"
                    sync_status = "not_applicable"
            
            except Exception as e:
                action = "error"
                status = "error"
                sync_status = "sync_failed"
                print(f"Error publishing task {task.task_id}: {e}")
            
            publish_results.append(
                PublishResult(
                    task_id=task.task_id,
                    github_issue_number=issue_number,
                    project_item_id=project_item_id,
                    publish_status=status,
                    action=action,
                    phase_label=phase_titles.get(task.phase_id, task.phase_id),
                    section_ref=task.section_ref,
                    matched_by=decision.matched_by or "section_ref",
                    previous_hash=decision.previous_hash,
                    new_hash=task.content_hash,
                    project_sync_status=sync_status,
                )
            )

    # 7. SAVE OUTPUTS
    if output_json:
        os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(project.to_dict(), f, indent=2, ensure_ascii=True)

    # 8. CREATE IMPORT RUN RECORD
    from ..domain import generate_run_id

    run_id = generate_run_id()
    task_fingerprints = {task.task_id: task.content_hash for task in flat_tasks}

    result_summary = {
        "total_tasks": len(flat_tasks),
        "policy_counts": policy_counts,
        "summary_only_phases": summary_only_phases,
        "publish_results_count": len(publish_results),
        "dedupe_policy": dedupe_policy,
        "decisions": {
            "create": len([d for d in decisions if d.action == "create"]),
            "update": len([d for d in decisions if d.action == "update"]),
            "skip": len([d for d in decisions if d.action == "skip"]),
        },
    }

    import_run = ImportRun(
        run_id=run_id,
        actor="taskboard-importer",
        source_version=project.source_hash,
        target_project=repo_name or "unknown",
        result_summary=result_summary,
        task_fingerprints=task_fingerprints,
        publish_results=publish_results,
    )

    # 9. SAVE MANIFEST
    if manifest_json:
        os.makedirs(os.path.dirname(manifest_json) or ".", exist_ok=True)
        save_manifest(manifest_json, import_run.to_dict())

    return project, publish_results, import_run
