---
description: Edita o vídeo bruto seguindo o roteiro — transcreve, alinha, escolhe takes e gera a EDL para aprovação
argument-hint: <slug> [--engine scribe|mlx] [--auto]
---

Vídeo: **$ARGUMENTS**

Usar o subagente **editor-de-video** no fluxo "/editar" (ver `.claude/skills/corte-por-roteiro/SKILL.md`):
ingest → transcribe → **locutores** (Carlos × ChatGPT: só a voz do Carlos entra no corte) → align → edl (+ `preview.mp4`)
→ filmstrips → análise.

Depois **parar** e mostrar ao Carlos:
- locutores: IA identificada? confiança, evidências em conflito, palavras incertas, sobreposições (ChatGPT falando por cima);
- resumo por linha: `[OK]` / `[REVISAR]` / `[FALTANDO]`, take escolhido e motivo, **IA · Carlos** (linha que só a IA leu = regravar);
- duração final estimada vs 60 s; trechos não mapeados (improvisos) que ficaram de fora;
- caminhos de `videos/<slug>/edicao/edl.md` e `preview.mp4`.

Aguardar "aprovado" ou pedidos de troca ("L05 usa T1"). Com aprovação: `aprovado: true` no `edl.json`, estado `edl_aprovada`, e sugerir `/renderizar <slug>`.
Com `--auto`: aprovar sozinho **apenas** se todas as linhas estiverem `[OK]`.
