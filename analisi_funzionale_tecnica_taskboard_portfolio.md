# Analisi funzionale e tecnica
## Sistema portfolio-friendly per segmentazione roadmap in task e pubblicazione su board Kanban GitHub

### Executive summary
Il progetto prevede la realizzazione di un sistema che acquisisce un documento markdown strutturato, ne segmenta il contenuto in task, checklist, criteri di done e metadati, mostra una preview modificabile e, dopo approvazione, popola una board Kanban GitHub con Issues e Project items.

La soluzione è stata definita per massimizzare il rapporto tra zero costo, rapidità di implementazione, qualità del risultato e valore di portfolio. La destinazione primaria è GitHub Free, perché unisce repository pubblico, documentazione, issue tracking e board di progetto in un unico ecosistema.

### Obiettivi
- Ridurre il tempo necessario per trasformare una roadmap strutturata in backlog operativo.
- Evitare la creazione manuale ripetitiva di card, issue, checklist e descrizioni.
- Mantenere coerenza tra documento sorgente, task pubblicati e stato di avanzamento.
- Costruire un progetto dimostrabile come case study portfolio-friendly.

### Non obiettivi MVP
- Nessuna sincronizzazione bidirezionale completa.
- Nessun supporto iniziale a suite multiple.
- Nessuna creazione completamente automatica senza preview.
- Nessun supporto in v1 a documenti destrutturati o transcript meeting.

### Perimetro funzionale
- Input primario: file markdown strutturato.
- Output: JSON normalizzato, preview, publish su GitHub Project board, log di import.

### Mapping
- Titolo documento -> nome progetto/import
- Macrofase H1 -> phase/label
- Sotto-sezione H2 -> task principale
- Attività -> checklist
- Verifica -> acceptance checks
- Output atteso -> expected outcome
- Done quando -> definition of done
- Tracking -> metadata template
- Tabella avanzamento -> dipendenze e stato sintetico

### Requisiti funzionali
- FR-01 Upload o lettura file markdown
- FR-02 Parsing strutturale con validazione
- FR-03 Normalizzazione in JSON
- FR-04 Preview leggibile
- FR-05 Editing pre-publish di campi chiave
- FR-06 Publish su GitHub Issues e Projects
- FR-07 Mapping stato iniziale
- FR-08 Logging import
- FR-09 Deduplica e re-run controllato
- FR-10 Export JSON tecnico

### Requisiti non funzionali
- Robustezza
- Tracciabilità
- Idempotenza operativa
- Portabilità locale
- Estendibilità a connettori futuri
- Qualità portfolio

### Architettura proposta
- ingestion layer
- parser layer
- normalization layer
- review layer
- publishing layer
- persistence layer

### Componenti
- parser_markdown.py
- schema.py
- normalizer.py
- review_cli.py / review_ui.py
- github_adapter.py
- dedupe.py
- run_import.py
- tests/

### Modello dati
- ProjectImport
- Phase
- Task
- PublishResult
- ImportRun

### Specifica GitHub
- una sezione H2 = una issue
- macrofase = label / campo phase
- stato iniziale = status del Project
- section_ref conservato nel body o metadata per deduplica

### Test strategy
- unit test parser
- validazione schema
- mapping tests
- deduplica/idempotenza
- integration test mockati
- smoke test reale

### Struttura repo consigliata
```text
project-root/
  README.md
  pyproject.toml
  src/taskboard_importer/
  tests/
  outputs/
  docs/
```

### Piano di rilascio
1. Core parser
2. Review e dry-run
3. Publish GitHub
4. Hardening
5. Portfolio packaging

### Rischi
- scope creep
- over-reliance su LLM
- duplicazione task
- dipendenza da UI target
- portfolio debole

### Criterio di completamento
Il progetto è concluso quando il file roadmap di riferimento viene segmentato correttamente, l'utente può validare il dry-run, la board GitHub viene popolata in modo coerente e l'intero sistema è documentato, testato e presentabile come progetto portfolio-friendly.
