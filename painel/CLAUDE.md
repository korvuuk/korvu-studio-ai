# Painel web (tecnologia) — instruções desta área

> Esta área é `painel/`. Regras transversais (identidade da marca, legal, segredos, GAUNTLET em geral) estão no
> `CLAUDE.md` da raiz — o Claude Code carrega os dois quando a sessão abre aqui, então não duplicar.
> Detalhe técnico completo (schema, sync, telas, limites de dados): **`painel/README.md`**.

## Escopo
Equipe (quem é quem), vídeos + portões do GAUNTLET, fila de publicação, desempenho IG/FB e tokens/custos.
**O painel só LÊ o projeto** — o sincronizador (`painel/sync/sincronizar.py`) nunca escreve em `videos/`,
`00-marca/`, `_controle/`, `scripts/` nem em `~/.claude`. A única escrita própria é `painel/sync/previas_looks.py`
(gera `painel/previas/looks/*.jpg`).

## Limite da área
Só mexer dentro de `painel/`. Nunca editar `videos/`, `00-marca/`, `scripts/` (fora do que o sync já lê),
`linkedin/` ou `automacao-meta/` a partir de uma sessão desta área sem avisar o Carlos.

## Pilhas
- Banco: Supabase **próprio** em `painel/supabase/` (portas **553xx** — nunca as 543xx do MUNTUZA_CMS), só em
  `127.0.0.1`.
- App: Next.js 15 + TypeScript + Tailwind em `painel/web/` (:3456), design system **"korvu. painel"** em
  `painel/design/`.
- Sincronização automática: launchd `uk.korvu.painel` (15 min). Subir tudo: `bash painel/iniciar.sh`.
- Nomes da equipe: `painel/equipe.yaml`. Câmbio: `painel/cambio.yaml`. Acervo de estilos: `painel/biblioteca.yaml`.

## Quem constrói (departamento de tecnologia)
| Agente | Faz |
|---|---|
| `designer-de-produto` | referências → design system e maquetes em `painel/design/` |
| `engenheiro-frontend` | implementa em `painel/web/` o que foi aprovado |
| `engenheiro-backend` | banco (`painel/supabase/`), sincronizador (`painel/sync/`), testes (`painel/tests/`) |

Skills: `supabase`, `supabase-postgres-best-practices`, `dataviz`, `frontend-design:frontend-design`, `design:*`.

## GAUNTLET desta área
Portões-gerentes: `portao-interface` (áreas **design** e **interface**) e `portao-dados` (área **dados**), alvo
`painel`. **Nada do painel chega ao Carlos sem `uv run python scripts/portoes.py exigir painel` limpo.**
Detalhe: `docs/gauntlet.md`.
