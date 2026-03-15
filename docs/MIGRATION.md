# Guida Migrazione: Da Monolita a Architettura Modulare

Questo documento spiega come il codice legacy è stato trasformato nella nuova architettura modulare, permettendoti di:
1. Capire dove trovare il tuo codice
2. Adattare custom logic al nuovo modulo
3. Riusare componenti singoli

## Mapping Moduli

### 1. Schema → Domain

**Vecchio** (`schema.py`):
```python
@dataclass
class Task:
    task_id: str
    title: str
    activities: List[str]
    done_when: str
    # ...

@dataclass
class Phase:
    phase_id: str
    section_ref: str
    title: str
    tasks: List[Task]
```

**Nuovo** (`domain/project_spec.py`):
```python
from taskboard_importer.domain import Task, Phase, ProjectImport

# Stessi campi, plus:
# - content_hash: str (per dedup)
# - task_type: str (per classificazione)
# - publish_policy: str (per publish)
```

**Migration Path**:
```python
# Vecchio
from taskboard_importer.schema import Task, Phase

# Nuovo
from taskboard_importer.domain import Task, Phase
```

### 2. Parser Markdown → Parsing

**Vecchio** (`parser_markdown.py`):
```python
def parse_roadmap_md(content: str):
    """Parse Markdown roadmap file"""
    # Regex matching H1, H2, bullets
    # Ritorna dict con phases e tasks
```

**Nuovo** (`parsing/roadmap_parser.py`):
```python
from taskboard_importer.parsing import parse_markdown

project = parse_markdown("roadmap.md")
# Ritorna ProjectImport con Phase e Task objects
```

**Migration Path**:
```python
# Vecchio
from taskboard_importer.parser_markdown import parse_roadmap_md
data = parse_roadmap_md(content)

# Nuovo
from taskboard_importer.parsing import parse_markdown
project = parse_markdown("roadmap.md")

# Convertire dict → ProjectImport
tasks = project.tasks  # List[Task]
phases = project.phases  # List[Phase]
```

### 3. Normalizer → Policies

**Vecchio** (`normalizer.py`):
```python
def normalize_project(project: dict):
    """Fill defaults, classify tasks, compute hashes"""
    # task_type = classify(task)
    # publish_policy = map(task_type)
    # content_hash = hash(task)
```

**Nuovo** (`policies/classification.py` + `sync/fingerprints.py`):
```python
from taskboard_importer.policies import normalize_project
from taskboard_importer.sync import compute_task_hash

project = normalize_project(project)  # Classificazione + defaults
for task in project.tasks:
    task.content_hash = compute_task_hash(task)
```

**Migration Path**:
```python
# Vecchio - single function
normalized = normalize_project(raw_data)

# Nuovo - split in steps
project = parse_markdown("roadmap.md")
project = normalize_project(project)
for task in project.tasks:
    task.content_hash = compute_task_hash(task)

# Vantaggi: puoi skippar specific steps se necessario
```

### 4. Dedupe → Sync

**Vecchio** (`dedupe.py`):
```python
def dedupe_tasks(tasks: List[Task], 
                 previous_manifest: dict,
                 policy: str = "skip"):
    """Compare with previous, return decisions"""
    # Check content_hash vs previous
    # Return create/update/skip decisions
```

**Nuovo** (`sync/sync_planner.py`):
```python
from taskboard_importer.sync import plan_dedupe, load_manifest

previous = load_manifest("outputs/manifest.json")
decisions = plan_dedupe(tasks, previous, policy="skip")

for decision in decisions:
    if decision.action == "create":
        publish_issue(decision.task)
    elif decision.action == "update":
        update_issue(decision.task, decision.previous_hash)
```

**Migration Path**:
```python
# Vecchio
from taskboard_importer.dedupe import dedupe_tasks
decisions = dedupe_tasks(tasks, manifest, "skip")

# Nuovo
from taskboard_importer.sync import plan_dedupe, load_manifest
manifest = load_manifest("outputs/manifest.json")
decisions = plan_dedupe(tasks, manifest, "skip")
```

**Nuove Features**:
- `DedupeDecision` dataclass con metadata completo
- `detect_drift()` per analizzare task removed/added
- Fingerprinting separato per riuso

### 5. GitHub Adapter → Infrastructure.github

**Vecchio** (`github_adapter.py`):
```python
class GitHubAdapter:
    def create_issue(self, owner, repo, title, body):
        # REST call
        
    def create_label(self, owner, repo, label_name):
        # REST call
        
    def get_project(self, owner, repo):
        # GraphQL call
```

**Nuovo** (`infrastructure/github/`):
```python
from taskboard_importer.infrastructure.github import (
    IssuesClient, LabelsClient, ProjectsV2Client
)

issues = IssuesClient(token="ghp_xxx")
labels = LabelsClient(token="ghp_xxx")
projects = ProjectsV2Client(token="ghp_xxx")

# Single responsibility - each client handles one domain
issue_num = issues.create_issue("owner", "repo", "Title", "Body")
labels.ensure_labels("owner", "repo", ["Phase1", "Phase2"])
project_id = projects.get_project_id("owner", "repo")
```

**Migration Path**:
```python
# Vecchio - single class
from taskboard_importer.github_adapter import GitHubAdapter
adapter = GitHubAdapter(token="ghp_xxx")
issue_num = adapter.create_issue("owner", "repo", "Title", "Body")

# Nuovo - separate clients
from taskboard_importer.infrastructure.github import IssuesClient
issues = IssuesClient(token="ghp_xxx")
issue_num, node_id = issues.create_issue("owner", "repo", "Title", "Body")
```

**Vantaggi**:
- Ogni client riusabile indipendentemente
- Mocking più facile per test
- Custom clients extension-ready (subclass)

### 6. Workspace → Infrastructure.workspace

**Vecchio** (`workspace.py`):
```python
def make_workspace(project_path: str):
    """Initialize project scaffold"""
    # Create roadmap/, docs/, outputs/, etc
    
def get_project_config(project_path: str):
    """Load project.yaml or project.json"""
```

**Nuovo** (`infrastructure/workspace/`):
```python
from taskboard_importer.infrastructure.workspace import (
    scaffold_project,
    load_project_config,
    find_template
)

scaffold_project(
    path="./projects/my-roadmap",
    title="My Roadmap",
    repo_owner="kirey",
    repo_name="my-repo"
)

config = load_project_config("./projects/my-roadmap")
template = find_template("standard")
```

**Migration Path**:
```python
# Vecchio
from taskboard_importer.workspace import make_workspace, get_project_config
make_workspace("./my-project")
cfg = get_project_config("./my-project")

# Nuovo
from taskboard_importer.infrastructure.workspace import scaffold_project, load_project_config
scaffold_project("./my-project", "My Project", "owner", "repo")
cfg = load_project_config("./my-project")
```

### 7. Run Import → Application.import_roadmap

**Vecchio** (`run_import.py`):
```python
def main(input_path, previous_manifest, dedupe_policy, dry_run):
    """Full pipeline orchestration"""
    # 1. Parse Markdown
    # 2. Normalize
    # 3. Dedupe
    # 4. Publish to GitHub (if not dry_run)
    # 5. Save manifest
    # 6. Return telemetry
```

**Nuovo** (`application/import_roadmap.py`):
```python
from taskboard_importer.application import import_roadmap

project, results, run = import_roadmap(
    input_path="roadmap.md",
    output_json="outputs/import.json",
    manifest_json="outputs/manifest.json",
    previous_manifest="outputs/manifest-v1.json",
    dedupe_policy="update",
    dry_run=True,
    github_config=None,  # Optional GitHub integration
    dedupe_skip_policy=None  # Optional custom policy
)

# project: ProjectImport - parsed + normalized
# results: List[PublishResult] - per-task publish decisions
# run: ImportRun - telemetry (start_time, end_time, tasks_count, etc)
```

**Migration Path**:
```python
# Vecchio - manual orchestration
from taskboard_importer import parser_markdown, normalizer, dedupe
content = read_file(input_path)
parsed = parser_markdown.parse_roadmap_md(content)
normalized = normalizer.normalize_project(parsed)
manifest = read_json(previous_manifest)
decisions = dedupe.dedupe_tasks(normalized["tasks"], manifest, dedupe_policy)
# ... publish to GitHub
# ... save manifest

# Nuovo - single orchestrator
from taskboard_importer.application import import_roadmap
project, results, run = import_roadmap(
    input_path=input_path,
    manifest_json=output_manifest,
    dedupe_policy=dedupe_policy,
    dry_run=dry_run
)
```

### 8. CLI → Presentation.cli

**Vecchio** (`cli.py`):
```python
# Single entry point with subcommands
# Commands: init-project, import-roadmap, bootstrap-github
```

**Nuovo** (`presentation/cli.py`):
```bash
# Identici comandi, migliore output formatting
# Handlers delegate to application/ orchestrators
```

**Migration Path**:
```bash
# Vecchio
taskboard import-roadmap --input docs/my-roadmap.md --dry-run

# Nuovo
taskboard import-roadmap --project ./projects/my-project --dry-run

# Entrambi supportano --dry-run, --dedupe-policy, --previous-manifest
```

## Composizione Moduli per Custom Use Cases

### Case 1: Parsing Custom Markdown

```python
from taskboard_importer.parsing import markdown_reader, roadmap_parser

# Read file
content = markdown_reader.read_markdown_file("my-roadmap.md")
file_hash = markdown_reader.compute_file_hash(content)

# Parse with custom regex
project = roadmap_parser.parse_markdown("my-roadmap.md")

# Extract tasks
tasks = [t for p in project.phases for t in p.tasks]
```

### Case 2: Custom Classification Logic

```python
from taskboard_importer.parsing import parse_markdown
from taskboard_importer.policies import classification
from taskboard_importer.domain import Task

project = parse_markdown("roadmap.md")

# Override classification for specific task types
for phase in project.phases:
    for task in phase.tasks:
        if task.title.startswith("URGENT"):
            task.task_type = "operational_task"
            task.publish_policy = "publish_as_issue"
        else:
            # Use default classification
            classification.classify_task(task, phase.title)
```

### Case 3: Publish to Custom Backend

```python
from taskboard_importer.parsing import parse_markdown
from taskboard_importer.policies import normalize_project
from taskboard_importer.sync import compute_task_hash

project = parse_markdown("roadmap.md")
project = normalize_project(project)

# Publish to custom backend
for phase in project.phases:
    for task in phase.tasks:
        task.content_hash = compute_task_hash(task)
        
        payload = task.to_dict()
        response = custom_api.post_task(payload)
        
        # Store manifest locally
        manifest[task.task_id] = {
            "hash": task.content_hash,
            "remote_id": response["id"]
        }
```

### Case 4: Batch Processing Multiple Roadmaps

```python
from pathlib import Path
from taskboard_importer.application import import_roadmap

roadmap_dir = Path("roadmaps/")
for roadmap_file in roadmap_dir.glob("*.md"):
    project_name = roadmap_file.stem
    
    project, results, run = import_roadmap(
        input_path=str(roadmap_file),
        output_json=f"outputs/{project_name}-import.json",
        manifest_json=f"outputs/{project_name}-manifest.json",
        dry_run=False
    )
    
    print(f"{project.title}: {run.tasks_count} tasks processed")
```

## Best Practices Migrazione

### ✅ DO's

1. **Use application orchestrators** per pipeline complete
   ```python
   from taskboard_importer.application import import_roadmap
   project, results, run = import_roadmap(...)
   ```

2. **Compose moduli** per custom pipelines
   ```python
   from taskboard_importer.parsing import parse_markdown
   from taskboard_importer.policies import normalize_project
   from taskboard_importer.sync import compute_task_hash
   ```

3. **Leverage dataclasses** per type safety
   ```python
   from taskboard_importer.domain import Task, Phase
   task: Task = Task(...)  # IDE autocomplete
   ```

4. **Test moduli independently**
   ```bash
   pytest tests/test_parsing.py -v
   pytest tests/test_policies.py -v
   ```

### ❌ DON'Ts

1. **Don't import internal helpers directly**
   ```python
   # BAD
   from taskboard_importer.parsing.roadmap_parser import ParsedTaskBuffer
   
   # GOOD
   from taskboard_importer.parsing import parse_markdown
   ```

2. **Don't mix legacy + new code**
   ```python
   # BAD
   from taskboard_importer import parser_markdown  # old
   from taskboard_importer.parsing import parse_markdown  # new
   
   # GOOD - use only new
   from taskboard_importer.parsing import parse_markdown
   ```

3. **Don't bypass domain validation**
   ```python
   # BAD
   task = Task()
   task.task_id = ""  # Invalid
   
   # GOOD
   from taskboard_importer.domain import validate_project
   task = Task(task_id="1.1", ...)
   validate_project(project)  # Throws ValidationError if invalid
   ```

4. **Don't hardcode GitHub token**
   ```python
   # BAD
   client = IssuesClient(token="ghp_hardcoded")
   
   # GOOD - use env var or pass via CLI
   import os
   token = os.getenv("GITHUB_TOKEN")
   client = IssuesClient(token=token)
   ```

## Deprecati (Non usare)

Questi file **NON devono essere usati** nel nuovo codebase:
- ❌ `schema.py` → Usa `domain/project_spec.py`
- ❌ `parser_markdown.py` → Usa `parsing/roadmap_parser.py`
- ❌ `normalizer.py` → Usa `policies/classification.py`
- ❌ `dedupe.py` → Usa `sync/sync_planner.py`
- ❌ `github_adapter.py` → Usa `infrastructure/github/`
- ❌ `workspace.py` → Usa `infrastructure/workspace/`
- ❌ `run_import.py` direct → Usa `application/import_roadmap.py`

## Troubleshooting Migrazione

### ImportError: cannot import name 'Task'

```python
# WRONG
from taskboard_importer import Task

# RIGHT
from taskboard_importer.domain import Task
```

### AttributeError: 'ProjectImport' object has no attribute 'tasks'

```python
# WRONG
for task in project.tasks:
    ...

# RIGHT
for phase in project.phases:
    for task in phase.tasks:
        ...
```

### Publish policy non assegnato

```python
# WRONG
project = parse_markdown("roadmap.md")
# publish_policy è None

# RIGHT
project = parse_markdown("roadmap.md")
project = normalize_project(project)
# publish_policy è ora assegnato
```

### GitHub client get_issue ritorna None

```python
# Controllare token e repo exist
from taskboard_importer.infrastructure.github import IssuesClient

client = IssuesClient(token="ghp_xxx")

# Verificare token scope: repo:read, issues:read
try:
    issue = client.get_issue("owner", "repo", issue_number=1)
except Exception as e:
    print(f"GitHub error: {e}")
```

## Summary

| Aspetto | Vecchio | Nuovo |
|---------|--------|-------|
| **Structure** | Monolita (5 big files) | Modulare (7 domains) |
| **Riusabilità** | Difficile (coupling alto) | Facile (loose coupling) |
| **Testing** | Fragile | Robust (30+ test cases) |
| **Composizione** | Scritta manualmente | Orchestrator + DI |
| **Maintenance** | Hard (side effects) | Easy (single responsibility) |
| **Custom Logic** | File nuovo + import globale | Custom client/filter in modulo specifico |
| **Documentation** | Docstring generico | Per-module + architecture docs |

Quando migri, **fai piano per step**: 1→2→3→4 usando application orchestrator, poi componi custom se necessario.
