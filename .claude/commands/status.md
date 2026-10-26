---
description: Mostra o estado de todos os vídeos e da fila de publicação
model: haiku
---

Ler `videos/*/status.json`, `05-render-pronto/*/pacote.json`, `06-publicar/*/post.json` e `_controle/tracker.md`.
Ignorar pastas que começam com `_` (testes, ex.: `videos/_teste-sintetico`).
Mostrar uma tabela: slug · tema · estado · portões (`uv run python scripts/portoes.py estado`: ✅ aprovado · ⌛ vencido · ⛔ bloqueado · 🔺 escalado · · pendente · — n/a) · próximo passo (comando sugerido) · atualizado. Depois a fila de publicação (data/hora, plataformas, estado). Sem modificar nada.
Por fim, a última leitura de métricas: de `_controle/metricas.md`, uma linha por vídeo publicado (lido em, views, alcance, % assistido, salv./alcance, coment./alcance, palavra) e a coluna Obs. se houver "permissão em falta"; mais a data do topo de `_controle/aprendizados.md`.
