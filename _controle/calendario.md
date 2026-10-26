# Calendário de publicação

O agente `publicador` usa este arquivo para agendar. Edite as vagas à vontade.

```yaml
fuso: Europe/London
vagas_semanais:        # dia: hora (24h)
  domingo: "19:00"   # janelas de maior atividade no app (prints 17/10): dom 18–21 h,
  terca: "21:00"     # ter 21–24 h, qua à noite — decisão de 17/10 ("basear no gráfico")
  quarta: "21:00"
plataformas_padrao: [instagram, facebook]
trial_padrao:   # vazio = Reel NORMAL — Trial suspenso em 22/10 (decisões §5b: testar a automação com os seguidores); antes: SS_PERFORMANCE
modo_confirmar_restantes: 0   # os primeiros N posts pedem OK antes de publicar
```

> **Pares A/B (17/10):** cada vídeo ocupa DUAS vagas seguidas — a B (conteúdo primeiro, IG + FB) na 1.ª e a A (Carlos desde 0, só IG) na seguinte; as duas com `trial = {"graduation_strategy": "MANUAL"}`.

## Agenda
| Data/hora | Slug | Plataformas | Estado |
|---|---|---|---|
|  | 2026-09-17-demis-hassabis |  | publicado |
| 2026-10-16 19:00 | 2026-10-20-geoffrey-hinton | instagram, facebook | publicado |
| 2026-10-18 19:00 | 2026-10-20-fei-fei-li | instagram, facebook | publicado |
| 2026-10-20 21:00 | 2026-10-20-fei-fei-li-a | instagram | publicado |
| 2026-10-27 21:00 | 2026-10-23-livro-chatgpt | instagram | agendado |
| 2026-10-22 21:00 | 2026-10-23-livro-chatgpt-a | instagram, facebook | publicado |
| 2026-10-28 21:00 | 2026-10-23-livro-chatgpt-l01c | instagram | agendado |
| 2026-11-01 19:00 | 2026-10-23-livro-chatgpt-l01c-a | instagram | agendado |
| 2026-10-24 19:00 | 2026-10-20-fei-fei-li-r2 | instagram | publicado |
| 2026-10-25 19:00 | 2026-10-20-geoffrey-hinton-r2 | instagram | publicado |

> Vaga extra (pedido explícito do Carlos, 17/10): `2026-10-20-fei-fei-li` sai no **domingo 2026-10-18 19:00** (Europe/London), fora das vagas seg/qua/sex. As vagas semanais acima não mudam.

> Par A/B de `2026-10-20-fei-fei-li` (17/10, `_controle/estrategia-de-alcance.md` §2.8): a **B** (conteúdo primeiro, IG + FB) sai dom 18/10 19:00 e a **A** (`2026-10-20-fei-fei-li-a`, Carlos desde 0, **só Instagram**) na vaga seguinte, **ter 20/10 21:00** (50 h depois). As duas com `trial = {"graduation_strategy": "MANUAL"}`; legenda, hashtags e capa idênticas. A A não tem pasta em `videos/` (o vídeo é `videos/2026-10-20-fei-fei-li/edicao/final-A.mp4`).

> Livro-ChatGPT (21/10): 4 publicações, todas com `confirmar: true` e Trial MANUAL — B dom 25/10 19:00 (IG+FB), A ter 27/10 21:00, L01C qua 28/10 21:00, L01C-A dom 01/11 19:00 (só IG). Ordem combinada: depois do Jensen — se o Jensen ficar pronto antes, reordenar no /fila.

> 22/10 (Carlos): Trial suspenso — livro-chatgpt B antecipado para **hoje 22/10 21:00** como Reel normal (IG + FB) e repost da Fei-Fei B (`2026-10-20-fei-fei-li-r2`) **sáb 24/10 19:00**, normal, só IG. As variantes do livro (A, L01C, L01C-A) continuam Trial MANUAL.
> 22/10 (Carlos): repost do Hinton (`2026-10-20-geoffrey-hinton-r2`) **dom 25/10 19:00**, normal, só IG (o FB já tem o vídeo).
> 22/10 (Carlos, regra nova): a versão A (ele desde o 1.º segundo) sai NORMAL na página (IG + FB) e a B vai para o Trial (só IG). Livro: **A hoje 22/10 21:00** (normal, IG + FB) ↔ **B ter 27/10 21:00** (Trial MANUAL, só IG) — trocaram de vaga. Repost da Fei-Fei de sábado = versão A.
