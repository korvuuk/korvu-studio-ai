# Métricas dos Reels

Gerado por `scripts/metricas.py` (launchd 1×/dia, 09:30) — **não editar à mão**: é reescrito a cada leitura.
Uma linha por vídeo, com a leitura mais recente (histórico em `07-publicados/<slug>/metricas.json`).
Quem interpreta: agente `analista-de-metricas` → `_controle/aprendizados.md` → roteirista/estrategista.

> A API da Meta não dá a curva de retenção segundo a segundo — só o tempo MÉDIO assistido. '% médio assistido' = tempo médio / duração do vídeo. A curva (em que segundo as pessoas saem) só aparece no app do Instagram, em Insights do Reel.
> Taxas = métrica ÷ alcance do Instagram. "Palavra" = comentários com a palavra-chave / directs enviados (do `responder_comentarios.py`).

| Slug | Publicado | Lido em (dias) | Duração | Views IG | Alcance IG | Tempo médio IG | % assistido IG | Curtidas | Coment. | Salv. | Compart. | Salv./alcance | Coment./alcance | Compart./alcance | Palavra (coment./directs) | Plays FB | Tempo médio FB | Obs. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-17-demis-hassabis | 2026-10-13 | 2026-10-22 (8.87) | 57.84 s | 450 | 338 | 11.88 s | 20.5% | 16 | 2 | 1 | 1 | 0.3% | 0.59% | 0.3% | DOCUMENTARIO (1/1) | 30 | 10.91 s | ok |
| 2026-10-20-fei-fei-li | 2026-10-18 | 2026-10-24 (5.59) | 168.44 s | 45 | 40 | 9.05 s | 5.4% | 1 | 0 | 0 | 0 | 0% | 0% | 0% | AULA (0/0) | 196 | 2.37 s | trial reel |
| 2026-10-20-fei-fei-li-a | 2026-10-20 | 2026-10-22 (1.7) | 168.49 s | 8 | 4 | 2.6 s | 1.5% | 0 | 0 | 0 | 0 | 0% | 0% | 0% | AULA (0/0) | — | — | trial reel |
| 2026-10-20-geoffrey-hinton | 2026-10-15 | 2026-10-22 (7.09) | 158.68 s | 11 | 11 | 1512.69 s | 953.3% | 1 | 0 | 0 | 0 | 0% | 0% | 0% | NOBEL (0/0) | 4 | 1.73 s | trial reel |
