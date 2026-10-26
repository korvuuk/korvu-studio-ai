---
description: Ajusta o roteiro de um vídeo existente (nova versão) e revisa de novo
argument-hint: <slug> [o que mudar]
---

Pedido: **$ARGUMENTS** (primeira palavra = slug; o resto = ajuste pedido).

1. Ler `videos/<slug>/roteiro.md`, `roteiro-revisao.md` e `status.json`. Se o vídeo já foi gravado (estado ≥ `gravacao`), avisar que mudar a FALA exige regravar as linhas alteradas e listar quais.
2. Usar o **roteirista** para aplicar o ajuste, incrementando `versao` no frontmatter.
3. Se a versão nova mudou o CTA, a palavra ou o que o material promete: usar o **produtor-de-material** para regerar o PDF (mesmo `arquivo`, por cima do antigo).
4. **PORTÃO-ROTEIRO** — **revisor-de-roteiro** sobre o roteiro e o PDF (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO). Mudar a FALA vence o veredicto anterior.
5. Com o PORTÃO-ROTEIRO APROVADO, mostrar o diff das linhas alteradas (ID → antes → depois) e o veredicto.
