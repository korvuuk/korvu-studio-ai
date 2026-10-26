---
description: Lê o roteiro, procura no YouTube os vídeos sobre o assunto, baixa, anota os momentos e entrega a página de material
argument-hint: <slug> [o que procurar]
---

Chame o agente **`buscador-de-videos`** para o vídeo `$ARGUMENTS`.

1. Sem slug, pegue o vídeo mais recente em estado `roteiro`/`gravacao` no `_controle/tracker.md` e confirme com o Carlos.
2. O agente lê o `roteiro.md`, busca, baixa para `material/youtube/`, assiste, anota momentos por linha e corta os trechos que vão para a tela (`scripts/buscar_youtube.py`).
2b. **PORTÃO-PAUTA** — subagente **portao-pauta** sobre o catálogo (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO).
3. Com o PORTÃO-PAUTA APROVADO, entregue o link para `videos/<slug>/material/youtube/catalogo.md` e a tabela de cenas extras pronta para o roteiro.

Baixar: qualquer vídeo (decisão de 2026-10-01). Na tela: trechos narrados pelo Carlos, **sem teto de tempo**, com áudio original baixo/mudo e crédito (decisão de 14/10). Roda **automaticamente** no `/novo-video` (passo 4b), logo depois do roteiro aprovado — o material tem de estar pronto antes da gravação.
