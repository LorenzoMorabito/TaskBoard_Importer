# Taskboard Importer

Sistema deterministico per trasformare roadmap Markdown strutturate in task normalizzati e pubblicarli su GitHub Issues + Projects, con **architettura modulare** ben definita e separazione delle responsabilità.

## ✨ Caratteristiche

- ✅ **Parsing robusto** di file Markdown strutturati (H1 titolo, H2 task)
- ✅ **Normalizzazione** in JSON con schema stabile
- ✅ **Classificazione deterministica** dei task (operational, checklist, documentation, status_register)
- ✅ **Deduplicazione** intelligente con politiche skip/create/update
- ✅ **Pubblicazione selettiva** su GitHub (4 livelli di policy)
- ✅ **Architettura modulare** - ogni modulo riusabile in pipeline diverse
- ✅ **Test suite** con regressioni su CLI e application layer
- ✅ **CLI** allineata a config file, env e publish reale
- ✅ **Dry-run** preview-only mode

## 🚀 Quick Start

### Installazione

```bash
# Clone repository
git clone <repo> && cd TaskBoard_Importer

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate      # Windows

# Install
pip install -e .
```

### Inizializzare progetto

```bash
taskboard init-project \
  --path ./projects/my-roadmap \
  --title "My Roadmap" \
  --repo-owner kirey \
  --repo-name my-repo
```

### Importare roadmap

```bash
taskboard import-roadmap \
  --project ./projects/my-roadmap \
  --dry-run
```

### Pubblicare su GitHub

**Nota:** Questo comando richiede un GitHub Personal Access Token (PAT) con permessi `repo` e `project` (se usi GitHub Projects).

```bash
# Pubblicare task su GitHub Issues
export GITHUB_TOKEN="ghp_xxxxx..."

taskboard import-roadmap \
  --project ./projects/my-project \
  --repo-owner kirey \
  --repo-name my-repo \
  --token $GITHUB_TOKEN \
  --project-number 5
```

**Sequenza consigliata:**
1. **Primo**: Esegui con `--dry-run` per preview
2. **Secondo**: Esegui senza `--dry-run` per publish reale
3. **Verifica**: Controlla GitHub Issues per i nuovi task

**Output:**
- I task `publish_as_issue` generano o aggiornano GitHub Issue
- I task `publish_as_doc_issue` restano deferred in manifest
- Se `--project-number` è fornito, le issue create o aggiornate possono essere sincronizzate al Project V2
- `manifest.json` registra fingerprints e publish results

## 🏗️ Architettura Modulare

TaskBoard Importer è organizzato in **7 moduli con responsabilità chiare**:

```
domain/        → Entità, business logic, validazione
parsing/       → Markdown → Dominio
policies/      → Classificazione task e publish rules
sync/          → Deduplicazione, fingerprints, manifest
infrastructure → GitHub API integration, workspace management
application/   → Orchestratori pipeline
presentation/  → CLI, user interfaces
```

Vedi [docs/architecture.md](docs/architecture.md) per dettagli completi.

## 📋 Comandi CLI

### Init Project
```bash
taskboard init-project \
  --path ./projects/my-project \
  --title "Project Title" \
  --repo-owner kirey \
  --repo-name my-repo
```

### Import Roadmap
```bash
taskboard import-roadmap \
  --project ./projects/my-project \
  --dry-run                              # Preview solo, nessun publish
  --dedupe-policy update                 # skip, create, o update
  --repo-owner kirey \
  --repo-name my-repo \
  --token $GITHUB_TOKEN \
  --previous-manifest outputs/manifest.json
```

### Bootstrap GitHub
```bash
taskboard bootstrap-github \
  --project ./projects/my-project \
  --token $GITHUB_TOKEN \
  --labels "Phase 1" "Phase 2" "Documentation"
```

## 📊 Modello Dati

### Task
```python
Task(
    task_id="1.1",
    phase_id="1",
    section_ref="1.1",
    title="Implement feature",
    activities=["Do X", "Do Y"],
    verification=["Check A", "Check B"],
    expected_output="Feature working",
    done_when="Tests pass",
    task_type="operational_task",           # auto-classified
    publish_policy="publish_as_issue",      # auto-assigned
    content_hash="abc123..."                # SHA256
)
```

### Politiche di Classificazione

| Task Type | Detect | Policy | Output |
|-----------|--------|--------|--------|
| **operational_task** | verification/output/done_when | publish_as_issue | GitHub Issue |
| **checklist** | [x] items o keyword "checklist" | publish_as_doc_issue | Deferred in manifest |
| **documentation** | No verification + doc hints | publish_as_note | Manifest only |
| **status_register** | Markdown tables | publish_as_note | Manifest only |

### Dedupe Policies

- **skip** (default): Salta task invariati, crea nuovi
- **create**: Crea sempre nuove issue
- **update**: Crea nuove, aggiorna cambiate, salta uguali

## 📂 Struttura Progetto

```
projects/my-project/
├── project.yaml              # Configurazione
├── roadmap/
│   └── roadmap.md           # Input Markdown
├── outputs/
│   ├── import.json          # Task normalizzati
│   └── manifest.json        # Fingerprints + publish results
├── rules/
│   └── publish_rules.yml    # (opzionale) Custom policy
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   └── glossary.md
└── state/
    ├── backlog_notes.md
    ├── current_status.md
    └── risks.md
```

## 🔧 Usare Moduli Indipendentemente

### Parsing only
```python
from taskboard_importer import parse_markdown

project = parse_markdown("roadmap.md")
# ProjectImport with phases and tasks
```

### Parsing + Classification
```python
from taskboard_importer import parse_markdown, normalize_project

project = parse_markdown("roadmap.md")
project = normalize_project(project)
# Task sono classificati e hanno publish_policy
```

### Deduplicazione custom
```python
from taskboard_importer import (
    parse_markdown,
    normalize_project,
    plan_dedupe,
    compute_task_hash,
    load_manifest
)

project = parse_markdown("roadmap.md")
project = normalize_project(project)

tasks = [t for p in project.phases for t in p.tasks]
for task in tasks:
    task.content_hash = compute_task_hash(task)

previous = load_manifest("outputs/manifest.json")
decisions = plan_dedupe(tasks, previous, policy="update")

for decision in decisions:
    if decision.action == "create":
        print(f"New: {decision.task.title}")
    elif decision.action == "update":
        print(f"Changed: {decision.task.title}")
    else:
        print(f"Skip: {decision.task.title}")
```

### GitHub API directly
```python
from taskboard_importer.infrastructure.github import IssuesClient, LabelsClient

# Create issues
issues_client = IssuesClient(token="ghp_xxx")
issue_num, node_id = issues_client.create_issue(
    "owner", "repo", 
    title="Feature X",
    body="Description"
)

# Manage labels
labels_client = LabelsClient(token="ghp_xxx")
labels_client.ensure_labels("owner", "repo", ["Phase 1", "Phase 2"])
```

## 🧪 Test

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_domain.py -v
pytest tests/test_parsing.py -v
pytest tests/test_policies.py -v
pytest tests/test_sync.py -v

# With coverage
pytest tests/ --cov=taskboard_importer
```

## 📖 Documentazione

- [Architecture](docs/architecture.md) - Dettagli architettura modulare
- [Decisions](docs/decisions.md) - Technology decisions
- Test fixtures: [tests/fixtures/](tests/fixtures/)

## 🔐 Variabili Ambiente

```bash
GITHUB_TOKEN              # Personal access token
REPO_OWNER                # GitHub repo owner
REPO_NAME                 # GitHub repo name
PROJECT_NUMBER            # GitHub project number (opzionale)
DEFAULT_STATUS            # Default task status (default: Backlog)
```

O passare via CLI:
```bash
taskboard import-roadmap \
  --project ./my-project \
  --repo-owner kirey \
  --repo-name task-tracker \
  --token ghp_xxx \
  --project-number 5
```

## 📝 Esempio Completo

### 1. Create Markdown Roadmap
```markdown
# Q1 2024 Roadmap

## 1. Setup Environment
### 1.1 Create Workspace
**Attività**: Create AWS workspace
**Verifica**: Workspace is accessible
**Output atteso**: Workspace ID in system

## 2. Core Features
### 2.1 Implement API
**Attività**:
- Setup routing
- Add authentication
**Verifica**:
- Tests pass
- Coverage > 80%
```

### 2. Initialize Project
```bash
taskboard init-project \
  --path ./projects/q1-roadmap \
  --title "Q1 2024 Roadmap"
```

### 3. Preview
```bash
taskboard import-roadmap \
  --project ./projects/q1-roadmap \
  --dry-run
```

### 4. Publish to GitHub
```bash
taskboard import-roadmap \
  --project ./projects/q1-roadmap \
  --repo-owner myorg \
  --repo-name product-roadmap \
  --token $GITHUB_TOKEN
```

## 🛠️ Development

### Add New Policy
```python
# policies/custom_rules.py
from taskboard_importer.domain import Task

def my_custom_classify(task: Task, phase_title: str):
    if task.title.startswith("URGENT"):
        task.publish_policy = "publish_as_issue"
        return
    # ... more logic
```

### Extend GitHub Integration
```python
# infrastructure/github/custom_client.py
from taskboard_importer.infrastructure.github import GitHubClient

class CustomClient(GitHubClient):
    def my_custom_api_call(self):
        return self.graphql("""
            query { ... }
        """)
```

## 🤝 Contributing

Pull requests welcome! Please:
1. Write tests for new features
2. Update documentation
3. Follow existing code style

## 📄 License

MIT - See LICENSE file

## 🎯 Roadmap

- [ ] Async GitHub API (aiohttp)
- [ ] Jira integration backend
- [ ] Custom policy plugins
- [ ] Performance caching layer
- [ ] Web UI for preview/publish
