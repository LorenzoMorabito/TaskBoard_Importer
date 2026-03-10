# Architecture

## Overview
Il sistema e' suddiviso in layer:
- Ingestion: lettura file markdown
- Parser: estrazione struttura (fasi, task, campi)
- Normalizer: completamento ID, default, hash
- Review: preview e conferma
- Publishing: adapter GitHub REST/GraphQL
- Persistence: output JSON + manifest

## Data flow
1. `parse_markdown` produce un `ProjectImport` iniziale
2. `normalize_project` completa campi e calcola hash
3. `review_cli` mostra anteprima
4. `GitHubAdapter` pubblica Issues e, se configurato, Project V2
5. `ImportRun` salva manifest
