---
description: Mostra a fila de publicação e permite confirmar, reagendar ou retirar posts
argument-hint: [confirmar|reagendar|retirar <slug> …]
---

1. Ler todos os `06-publicar/*/post.json` e os sinais dos portões (`uv run python scripts/portoes.py estado`) e a Agenda de `_controle/calendario.md`. Mostrar tabela: data/hora · slug · plataformas · estado (agendado / aguardando_confirmacao / erro).
2. Ação pedida: "$ARGUMENTS"
   - `confirmar <slug>` → só com OK explícito do Carlos nesta conversa: `uv run python scripts/publicar.py publicar <slug> --sim`, e mostrar os permalinks.
   - `reagendar <slug> <data hora>` → atualizar `post.json` e a Agenda (a data não vence o portão; Trial × normal, plataformas, capa e legenda vencem → **portao-publicacao** de novo).
   - `retirar <slug>` → mover de volta para `05-render-pronto/` e limpar a Agenda.
3. Erros: explicar em linguagem simples e propor correção (ex.: `uv run python scripts/publicar.py verificar-tokens`).
