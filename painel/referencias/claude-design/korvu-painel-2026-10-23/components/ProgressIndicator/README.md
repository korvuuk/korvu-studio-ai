# ProgressIndicator

Dois formatos:

- **Barra** (`k-progress`): 6px, trilho `surface-sunken`, preenchimento `accent`; `is-done` → `positive`; `is-blocked` → `danger`. Sempre acompanhada do número (9/14 · 64%).
- **Etapas** (`k-steps`): um segmento por etapa de produção — Roteiro · Gravação · Edição · Revisão · Publicar. Concluída `on` (`ink`), atual `now` (`accent`), bloqueada `blocked` (`danger`), futura vazia.
