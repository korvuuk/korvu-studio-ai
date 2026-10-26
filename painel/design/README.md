# painel/design — design system "korvu. painel"

O sistema que o Carlos fez no Claude Design (23/10/2026), importado em PT-BR, com os valores exatos da fonte
(`painel/referencias/claude-design/korvu-painel-2026-10-23/`). Substitui o korvu-editorial **só dentro do painel**.

Por onde começar:
0. `telas/` — **as 7 telas** que o Carlos desenhou em 23/10 (Visão geral, Equipe, Produção de conteúdo, Calendário,
   Desempenho, Biblioteca, Tokens e custos): `<tela>.html` (maquete com dados reais, 1440 e 375) + `<tela>.md` (especificação).
1. `previas/index.html` — ver tudo (abre sem internet; 1440 e 375 px).
2. `design-system.md` — as regras: cor, tipografia, grade, 375 px, cada componente, estados, pendências.
3. `handoff.md` — o que o engenheiro-frontend faz com isto.
4. `contraste.md` — cada par medido; o que falha não foi trocado (vai ao Carlos).

Conferir que nada saiu da fonte: `uv run python -I painel/design/verificacao/fidelidade.py`.
Medir o contraste de novo: `uv run python -I painel/design/verificacao/contraste.py`.
Capturas e rascunhos da designer ficam em `painel/trabalho/designer/` (nunca aqui). As maquetes das telas são geradas por
`painel/trabalho/designer/gerar_telas.py` a partir do `dados-2026-10-23.json` (que `exportar_dados_telas.py` acrescenta,
só lendo).
