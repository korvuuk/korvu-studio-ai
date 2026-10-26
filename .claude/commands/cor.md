---
description: Aplica a cor da marca (correção primária + LUT fixo) ao corte aprovado
argument-hint: <slug> [--intensidade 0.0-1.0]
---

Usar o subagente **colorista** no fluxo "/cor" para: **$ARGUMENTS**.
Depois: **PORTÃO-IMAGEM** — subagente **portao-imagem** (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO). Se já existem capas, a cor nova vence o veredicto e o portão confere se as capas foram tiradas da cor ATUAL (o erro de 21/10).
Com o APROVADO, mostrar ao Carlos `edicao/cor/antes-depois.png` e o parecer do colorista (consistência entre takes, pele, clipping).
