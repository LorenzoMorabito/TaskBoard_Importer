# Decisions

- Parsing deterministico con regex, LLM opzionale e non necessario.
- `ProjectImport` e' schema stabile, indipendente dal target.
- Hash contenuti per deduplica minima (section_ref + payload).
- GitHub Project V2 gestito via GraphQL con fallback: se non configurato, crea solo Issues.
- CLI unica per dry-run e publish.
