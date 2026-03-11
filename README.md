# Taskboard Importer

Sistema deterministico per trasformare roadmap Markdown strutturate in task normalizzati e pubblicarli su GitHub Issues + Projects, con classificazione e pubblicazione selettiva.

## Funzionalita
- Parsing robusto di file Markdown strutturati
- Normalizzazione in JSON con schema stabile
- Project summary e phase summary
- Classificazione deterministica dei task
- Dedupe `skip/create/update`
- Preview CLI con tipo e policy
- Dry-run con output JSON e manifest
- Publish selettivo (lane issue operativa)
- Inizializzazione workspace di progetto (project initializer)

## Comandi principali (initializer)
```bash
python -m taskboard_importer.cli init-project \
  --slug databricks-setup \
  --title "Setup Environment Databricks" \
  --path ./projects/databricks-setup \
  --template standard

python -m taskboard_importer.cli import-roadmap \
  --project ./projects/databricks-setup \
  --dry-run

python -m taskboard_importer.cli bootstrap-github \
  --project ./projects/databricks-setup \
  --repo-owner <owner> --repo-name <repo>
```

## Modello dati (sintesi)
- `ProjectImport.summary`: contesto globale del documento
- `Phase.summary`: contesto locale di fase
- `Task.task_type`: `operational_task`, `checklist`, `documentation`, `status_register`
- `Task.publish_policy`: `publish_as_issue`, `publish_as_doc_issue`, `publish_as_note`, `skip`
- `Task.content_kind`: `list`, `table`, `mixed`

## Politiche di publish
- `publish_as_issue` → pubblicato come issue standard
- `publish_as_doc_issue` → tracciato ma **deferito** (lane documentale non ancora pubblicata)
- `publish_as_note` / `skip` → non pubblicati, restano nel manifest

## Dedupe policy
- `skip`: salta task invariati rispetto al manifest precedente
- `create`: crea sempre nuove issue
- `update`: aggiorna issue esistenti se il contenuto e' cambiato

Esempio con update:
```bash
python -m taskboard_importer.run_import \
  --input docs/inputs/databricks_setup_environment_roadmap.md \
  --previous-manifest outputs/sample_manifest.json \
  --dedupe-policy update
```

## Telemetria manifest
Il `result_summary` include:
- conteggi per policy: `tasks_publishable_issue`, `tasks_doc_issue`, `tasks_note`, `tasks_policy_skip`
- conteggi sync Project: `project_sync_found/recovered/missing/failed/skipped`
- `summary_only_phases`

## Esecuzione rapida
```bash
python -m taskboard_importer.run_import \
  --input docs/inputs/databricks_setup_environment_roadmap.md \
  --dry-run
```

## Pubblicazione su GitHub
Imposta le variabili ambiente o passa i parametri CLI:
- `GITHUB_TOKEN`
- `REPO_OWNER`
- `REPO_NAME`
- `PROJECT_NUMBER` (opzionale)
- `DEFAULT_STATUS` (opzionale)

Esempio:
```bash
python -m taskboard_importer.run_import \
  --input docs/inputs/databricks_setup_environment_roadmap.md \
  --repo-owner <owner> --repo-name <repo> --project-number 1 \
  --default-status "Todo" --yes
```

## Struttura repository
- `src/taskboard_importer/`: core del sistema
- `tests/`: test e fixture
- `outputs/`: esempi di output
- `docs/`: documentazione
- `docs/inputs/`: input reali e analisi
- `docs/templates/`: template per initializer
