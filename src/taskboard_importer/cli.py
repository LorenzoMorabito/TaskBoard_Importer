from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import Dict

from .github_adapter import GitHubAdapter
from .normalizer import normalize_project
from .parser_markdown import parse_markdown
from .workspace import get_project_config, init_project


def _path_from_project(project_path: str, rel: str) -> str:
    return os.path.abspath(os.path.join(project_path, rel))


def _resolve_project_paths(config: Dict[str, object], project_path: str) -> Dict[str, str]:
    paths = config.get("paths", {}) if isinstance(config.get("paths"), dict) else {}
    roadmap = paths.get("roadmap", "roadmap/roadmap.md")
    outputs = paths.get("outputs", "outputs")
    rules = paths.get("rules", "rules/publish_rules.yml")
    return {
        "roadmap": _path_from_project(project_path, roadmap),
        "outputs": _path_from_project(project_path, outputs),
        "rules": _path_from_project(project_path, rules),
    }


def cmd_init_project(args: argparse.Namespace) -> int:
    root = init_project(
        path=args.path,
        slug=args.slug,
        title=args.title,
        owner=args.owner,
        template_profile=args.template,
        description=args.description or "",
    )
    print(f"Project initialized at {root}")
    return 0


def cmd_import_roadmap(args: argparse.Namespace) -> int:
    config = get_project_config(args.project)
    paths = _resolve_project_paths(config, args.project)

    github = config.get("github", {}) if isinstance(config.get("github"), dict) else {}
    repo_owner = args.repo_owner or github.get("repo_owner") or os.getenv("REPO_OWNER")
    repo_name = args.repo_name or github.get("repo_name") or os.getenv("REPO_NAME")
    project_number = args.project_number or github.get("project_number") or os.getenv("PROJECT_NUMBER")
    default_status = args.default_status or os.getenv("DEFAULT_STATUS", "Backlog")

    output_json = os.path.join(paths["outputs"], "import.json")
    manifest = os.path.join(paths["outputs"], "manifest.json")

    cmd = [
        sys.executable,
        "-m",
        "taskboard_importer.run_import",
        "--input",
        paths["roadmap"],
        "--output-json",
        output_json,
        "--manifest",
        manifest,
        "--dedupe-policy",
        args.dedupe_policy,
    ]

    if args.previous_manifest:
        cmd.extend(["--previous-manifest", args.previous_manifest])
    if args.dry_run:
        cmd.append("--dry-run")
    if args.yes:
        cmd.append("--yes")
    if repo_owner:
        cmd.extend(["--repo-owner", str(repo_owner)])
    if repo_name:
        cmd.extend(["--repo-name", str(repo_name)])
    if project_number:
        cmd.extend(["--project-number", str(project_number)])
    if default_status:
        cmd.extend(["--default-status", str(default_status)])

    return subprocess.call(cmd)


def cmd_bootstrap_github(args: argparse.Namespace) -> int:
    config = get_project_config(args.project)
    paths = _resolve_project_paths(config, args.project)

    github = config.get("github", {}) if isinstance(config.get("github"), dict) else {}
    repo_owner = args.repo_owner or github.get("repo_owner") or os.getenv("REPO_OWNER")
    repo_name = args.repo_name or github.get("repo_name") or os.getenv("REPO_NAME")
    project_number = args.project_number or github.get("project_number") or os.getenv("PROJECT_NUMBER")
    token = args.token or os.getenv("GITHUB_TOKEN")

    if not repo_owner or not repo_name or not token:
        print("Missing repo_owner/repo_name/token for bootstrap")
        return 1

    project = parse_markdown(paths["roadmap"])
    project = normalize_project(project, default_status="Backlog")
    phase_titles = {phase.phase_id: phase.title for phase in project.phases}
    phase_labels = [phase_titles.get(task.phase_id, task.phase_id) for phase in sum([p.tasks for p in project.phases], [])]

    adapter = GitHubAdapter(
        token=token,
        repo_owner=str(repo_owner),
        repo_name=str(repo_name),
        project_number=int(project_number) if project_number else None,
        default_status=None,
        dry_run=False,
    )

    try:
        adapter.precheck()
    except Exception as exc:  # noqa: BLE001
        print(f"Precheck failed: {exc}")
        return 1

    adapter.ensure_labels(phase_labels)
    print("Bootstrap GitHub completed (labels ensured).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Taskboard Initializer CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init-project", help="Create a new project workspace")
    init.add_argument("--slug", required=True)
    init.add_argument("--title", required=True)
    init.add_argument("--path", required=True)
    init.add_argument("--owner", default="")
    init.add_argument("--template", default="standard")
    init.add_argument("--description", default="")
    init.set_defaults(func=cmd_init_project)

    imp = sub.add_parser("import-roadmap", help="Import roadmap using project.yaml config")
    imp.add_argument("--project", required=True)
    imp.add_argument("--dry-run", action="store_true")
    imp.add_argument("--yes", action="store_true")
    imp.add_argument("--dedupe-policy", default="skip", choices=["skip", "create", "update"])
    imp.add_argument("--previous-manifest")
    imp.add_argument("--repo-owner")
    imp.add_argument("--repo-name")
    imp.add_argument("--project-number")
    imp.add_argument("--default-status")
    imp.set_defaults(func=cmd_import_roadmap)

    boot = sub.add_parser("bootstrap-github", help="Ensure labels and precheck GitHub")
    boot.add_argument("--project", required=True)
    boot.add_argument("--repo-owner")
    boot.add_argument("--repo-name")
    boot.add_argument("--project-number")
    boot.add_argument("--token")
    boot.set_defaults(func=cmd_bootstrap_github)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
