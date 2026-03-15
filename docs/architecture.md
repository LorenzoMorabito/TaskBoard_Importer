# TaskBoard Importer - Architettura Modulare v2

## 📋 Panoramica

TaskBoard Importer ha subito una rework completa per adottare una **architettura modulare** ben definita con separazione delle responsabilità.

Ogni modulo ha un dominio specifico e può essere riutilizzato in diverse pipeline.

## 🏗️ Struttura Modulare

```
taskboard_importer/
├── domain/                  # Entità di dominio e logica di business
│   ├── project_spec.py      # Modelli Task, Phase, ProjectImport
│   ├── import_run.py        # PublishResult, ImportRun (telemetria)
│   ├── validation.py        # Regole di validazione
│   └── identifiers.py       # Generazione ID
│
├── parsing/                 # Parsing Markdown → Dominio
│   ├── markdown_reader.py   # I/O low-level
│   ├── roadmap_parser.py    # Parser Markdown strutturato
│   └── source_mapping.py    # Traceback source lines
│
├── policies/                # Classificazione e regole di pubblicazione
│   ├── classification.py    # Classificazione task e normalizzazione
│   └── publish_rules.py     # Politiche di pubblicazione
│
├── sync/                    # Deduplicazione e sincronizzazione
│   ├── fingerprints.py      # Hash SHA256 per deduplicazione
│   ├── manifest_store.py    # I/O manifest (JSON)
│   ├── sync_planner.py      # Piano dedupe (skip/create/update)
│   └── drift_report.py      # Rilevamento drift tra versioni
│
├── infrastructure/          # Integrazioni esterne
│   ├── github/
│   │   ├── client.py        # Client HTTP base
│   │   ├── issues.py        # GitHub Issues API
│   │   ├── projects_v2.py   # GitHub Projects V2 GraphQL
│   │   └── labels.py        # GitHub Labels API
│   │
│   └── workspace/
│       ├── scaffold.py      # Creazione struttura progetto
│       ├── project_config.py    # Caricamento config YAML/JSON
│       └── template_loader.py   # Gestione template
│
├── application/             # Orchestratori (pipeline complete)
│   ├── import_roadmap.py    # Main pipeline
│   ├── init_workspace.py    # Inizializzazione workspace
│   └── bootstrap_github.py  # Setup repository GitHub
│
└── presentation/            # CLI e interfaccia utente
    ├── cli.py               # Entry point comandi CLI
    └── preview.py           # Rendering preview terminale
```

## 🔄 Pipeline Principale

```
Markdown File
    ↓
[Parsing] → parse_markdown()
    ├─ read_markdown_file()
    ├─ Extract phases (H2 headers)
    ├─ Parse task fields
    ├─ Compute source_hash
    └─ Output: ProjectImport
    ↓
[Policies] → normalize_project()
    ├─ classify_task() per ogni task
    ├─ Assegna task_type e publish_policy
    ├─ Computa content_hash
    └─ Riempie defaults mancanti
    ↓
[Domain] → validate_project()
    ├─ Verifica struttura
    └─ Solleva ValidationError se invalido
    ↓
[Sync] → plan_dedupe()
    ├─ Carica previous manifest
    ├─ Compara fingerprints
    ├─ Decide: create/update/skip per ogni task
    └─ Output: List[DedupeDecision]
    ↓
[Infrastructure/GitHub] → publish_tasks()
    ├─ Crea issue su GitHub
    ├─ Aggiunge labels phase
    ├─ Sincronizza Projects V2
    └─ Output: List[PublishResult]
    ↓
[Sync] → save_manifest()
    ├─ Salva new task fingerprints
    ├─ Salva publish results
    └─ Crea ImportRun record
    ↓
import.json, manifest.json
```

## 📦 Moduli Dettagliati

### Domain
Definisce le entità di dominio e le regole di business:
- **Task, Phase, ProjectImport**: Modelli principali
- **PublishResult, ImportRun**: Telemetria esecuzione
- **validate_project()**: Validazione struttura
- **ID generators**: generate_task_id(), generate_phase_id(), generate_run_id()

### Parsing
Trasforma Markdown → dominio:
- Estrae H1 (titolo) e H2 (task)
- Supporta alias campo (italiano/inglese)
- Computa file hash e traccia source lines

### Policies
Classifica task e assegna politiche:
- 4 task types: operational_task, checklist, documentation, status_register
- 4 publish policies: publish_as_issue, publish_as_doc_issue, publish_as_note, skip
- Regole deterministiche basate su content

### Sync
Deduplicazione e versionamento:
- SHA256 fingerprint per ogni task
- Manifest store (JSON persistence)
- Drupe planner (skip/create/update decisions)
- Drift detection tra versioni

### Infrastructure
Integrazioni esterne:
- **GitHub**: REST API (issues, labels), GraphQL (Projects V2)
- **Workspace**: Directory scaffold, config loading, templates

### Application
Orchestratori pipeline:
- **import_roadmap**: Main pipeline completa
- **init_workspace**: Setup workspace
- **bootstrap_github**: Setup GitHub

### Presentation
CLI e UI:
- Entry point comandi
- Preview rendering

## 🧪 Test Coverage

```bash
pytest tests/test_domain.py        # Domain models
pytest tests/test_parsing.py       # Markdown parsing
pytest tests/test_policies.py      # Classification
pytest tests/test_sync.py          # Deduplication
pytest tests/ -v                   # Tutti i test
```

## 📈 Vantaggi

✅ Separazione Responsabilità  
✅ Riusabilità moduli  
✅ Testabilità alta  
✅ Scalabilità  
✅ Manutenibilità  
✅ Composabilità

