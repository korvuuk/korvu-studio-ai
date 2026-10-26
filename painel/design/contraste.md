# Contraste e acessibilidade — korvu. painel

> Medido em 23/10/2026 pela designer-de-produto, **com cálculo** (WCAG 2.1, luminância relativa sRGB), sobre as cores de
> `painel/design/tokens.json`. Reproduzir: `uv run python -I painel/design/verificacao/contraste.py`
> (`--falhas` mostra só o que fica abaixo do mínimo). A tabela completa, no fim, é a saída do script sem edição.
> Paleta de gráficos conferida também pelo validador da skill `dataviz` (`validate_palette.js`).
>
> **"Cor — não alterar" (Carlos).** Só mudam os valores que **ele** aprovou. **Decisão de 23/10** (`docs/decisoes.md` §5):
> "Aceito as duas: borda dos campos em #928874 e anel de foco em laranja escuro (accent-ink) nos fundos claros." —
> `line-strong` passou a **#928874** e `focus` a **`accent-ink`** nos fundos claros (`focus-on-dark` = `accent` na barra
> lateral). As outras propostas continuam com ele; os pares que ainda falham estão registrados com a medida e a mitigação.

## Resumo

- **72 pares medidos**: 35 de texto (3 deles usos que a fonte proíbe), 27 de objeto gráfico/controle (WCAG 1.4.11, 3:1;
  um deles — o contorno do botão primário — só informativo, porque o rótulo identifica o botão; outro — `line-strong` sobre
  `surface-sunken` — medido para proibir o uso) e 10 só informativos (decorativos, logotipo, controle desativado).
- **Desde a decisão de 23/10, a borda dos controles e o anel de foco passam**: `line-strong` 3,13 sobre `bg` e 3,33 sobre
  `surface`; anel `accent-ink` 5,44 · 5,79 · 5,12 · 5,60 sobre `bg`, `surface`, `surface-sunken` e `surface-hover`; na barra
  lateral, `accent` 5,68 (5,12 no item ativo). **Nenhum controle com borda `line-strong` sobre `surface-sunken`** (2,94).
- **6 pares abaixo do mínimo**, como o Carlos desenhou — nenhum é texto de leitura corrente: trilho de progresso, duas
  cores de gráfico, a barra/etapa atual sobre o trilho, laranja como texto grande sobre o fundo e um rótulo de 10px que
  nenhuma prévia usa.
- **3 usos que a própria fonte proíbe** (branco sobre o laranja, laranja como texto pequeno, `ink-3` sobre
  `surface-sunken`) foram medidos e a proibição se confirma.
- Todo o texto que o sistema manda usar passa AA: `ink` 16,86:1 · `ink-2` 5,22:1 · `ink-3` 4,64:1 sobre `bg`;
  `on-accent` 5,68:1 sobre `accent` (4,69:1 no hover); `accent-ink` 5,18:1 sobre `accent-soft`; chips de 4,55:1 a 16,86:1;
  `sidebar-ink-2` 6,19:1.

### O que as notas da fonte dizem × o que mede

| Nota da fonte | Medido | Situação |
|---|---|---|
| `ink` 16.9:1, `ink-2` 5.2:1, `ink-3` 4.6:1 sobre `bg` | 16,86 · 5,22 · 4,64 | confere |
| `on-accent` 5.7:1 sobre `accent` | 5,68 | confere |
| `accent-ink` 4.6:1 sobre `accent-soft` | 5,18 | confere (melhor que o anotado) |
| `sidebar-ink-2` 6:1 sobre `sidebar` | 6,19 | confere |
| branco sobre o laranja 3.3:1 | 3,33 | confere (por isso é proibido) |
| `line-strong` "3:1 sobre `bg` e `surface`" | era 2,32 · 2,47; **com #928874 (23/10): 3,13 · 3,33** | **resolvido pela decisão** |
| `focus` "3:1 sobre `bg`/`surface`" | era 2,97 · 3,16; **com `accent-ink` (23/10): 5,44 · 5,79** | **resolvido pela decisão** |
| **`accent` como texto "em 24px+"** sobre `bg` | **2,97** | **não confere sobre `bg`**; sobre `surface` 3,16 passa |

## Decididos pelo Carlos em 23/10 (deixaram de ser proposta)

| # | Par | Antes | Agora | Onde |
|---|---|---|---|---|
| G01 · G02 | `line-strong` sobre `bg` / `surface` | #a8a090: 2,32 / 2,47 | **#928874: 3,13 / 3,33** | borda da busca, do dropdown, do botão secundário e a caixa do critério. **G25**: sobre `surface-sunken` dá 2,94 — nenhum controle com essa borda sobre esse fundo (medido no navegador, 7 telas a 1440 e 375 e as 26 prévias: 0 casos; o segmentado e o atalho, que ficam sobre `surface-sunken`, não têm borda). O botão secundário em hover pinta o **próprio** miolo de `surface-sunken`, mas o contorno que o separa da página continua sobre `bg`/`surface` (3,13/3,33) |
| G03 · G05 | `focus` sobre `bg` / `surface-sunken` | `accent`: 2,97 / 2,79 | **`accent-ink`: 5,44 / 5,12** (5,79 sobre `surface`, 5,60 sobre `surface-hover`) | anel de foco 2px + 2px; na barra lateral e na de topo, `focus-on-dark` = `accent` (5,68; 5,12 no item ativo) |

## Os 6 pares abaixo do mínimo — medida, mitigação e proposta

| # | Par | Medida | Onde aparece | Mitigação dentro do sistema (vale já) | Proposta ao Carlos |
|---|---|---|---|---|---|
| T20 | `accent` como texto grande sobre `bg` | 2,97 (mín. 3) | regra "laranja como texto só sobre `sidebar` ou em 24px+" | Nenhum componente usa laranja como texto sobre `bg`; texto laranja é sempre `accent-ink`. | Reescrever a regra: laranja como texto **só sobre a barra lateral**; em qualquer fundo claro, `accent-ink`. |
| G08 | `accent` sobre `surface-sunken` | 2,79 | preenchimento da barra de progresso; etapa atual | A barra vem **sempre com o número** ("3 de 12 · 25%", regra da fonte) e a etapa com o nome ("Etapa 5 de 5: Publicar"). | Manter, com a regra do número obrigatória. |
| G12 | `surface-sunken` sobre `surface` | 1,13 | trilho da barra e **etapas futuras** (k-steps) contra o card | Sem o texto, não dá para contar quantas etapas faltam. Por isso: texto da etapa sempre junto (coluna Etapa) + `aria-label` no k-steps. | Etapa futura com contorno interno de 1px em `line-strong` (#928874 desde 23/10) — muda o componente, por isso é decisão dele. |
| G15 | `chart-3` (taupe) sobre `surface` | 2,62 | 3.ª série | Só com legenda + rótulo direto + tabela gêmea ("Ver os números"). | `chart-3` **#968D7B** (3,12 sobre `surface`; validador: ΔE 20,1 contra `chart-4`) |
| G16 | `chart-4` (areia) sobre `surface` | 1,52 | 4.ª série e "Outros" na rosca | Uso só para resto ("Outros") com o valor escrito ao lado. | Manter para "Outros"; escurecer até 3:1 viraria mostarda (#A58E5C) e perderia o papel de "resto". |
| T34 | `sidebar-ink-2` a 80% sobre `sidebar` | 4,37 (mín. 4,5) | `k-sidebar-label` (10px, opacity .8) — existe no CSS, nenhuma prévia usa | Não usar até decidir. | Tirar o `opacity:.8` (fica 6,19:1). |

## Usos proibidos (a medida confirma a proibição)

| # | Par | Medida | Regra |
|---|---|---|---|
| T15 | branco sobre `accent` | 3,33 | Texto sobre o laranja é sempre `on-accent` (#111). |
| T22 | `accent` texto pequeno sobre `bg` | 2,97 | Texto laranja pequeno é `accent-ink`. |
| T12 | `ink-3` sobre `surface-sunken` | 4,36 | `ink-3` só sobre `bg` e `surface` (o ícone neutro do k-thumb, que é gráfico, passa: 4,36 ≥ 3). |

## Paleta de gráficos no validador da skill `dataviz`

```
node validate_palette.js "#FF4D00,#111111,#A39B8B,#D6CCB5,#4F6475" --mode light --surface "#FBF9F4"
  [FAIL] Lightness band         outside band: [["#111111",0.178],["#D6CCB5",0.847]]
  [FAIL] Chroma floor           below floor (reads gray): [["#111111",0],["#A39B8B",0.025],["#D6CCB5",0.033],["#4F6475",0.037]]
  [PASS] CVD separation         worst adjacent #D6CCB5↔#A39B8B ΔE 15.5 (protan) · tritan 15.6
  [PASS] Normal-vision floor    worst adjacent #D6CCB5↔#A39B8B ΔE 15.6 (normal)
  [WARN] Contrast vs surface    below 3:1 — relief required (visible labels or table view): [["#A39B8B",2.62],["#D6CCB5",1.52]]
(com --pairs all: CVD pior par #A39B8B↔#FF4D00 ΔE 11.8 — passa)
só chart-1 + chart-2:  CVD ΔE 39.5 · visão normal ΔE 53.9 · contraste 3.16 e 17.95 — tudo passa (as faixas de
                       luminosidade/croma reprovam o preto por desenho: é neutro)
```

**Leitura.** A paleta do Carlos é de propósito quase neutra: um laranja e quatro neutros (preto, taupe, areia, ardósia).
O validador reprova "faixa de luminosidade" e "croma" porque preto, taupe, areia e ardósia **leem como cinza** — então,
fora o laranja, a identidade da série vem da luminosidade, não do matiz. A separação para daltonismo passa (ΔE ≥ 15,5).
**Mitigação obrigatória** (já nas regras do componente Gráficos): (1) a maioria dos gráficos usa só `chart-1` + `chart-2`,
que passam em tudo; (2) com 2+ séries, legenda sempre e rótulo direto no fim de cada linha; (3) toda série tem a tabela
gêmea; (4) `chart-3`/`chart-4` só com essas três coisas. Com a proposta `chart-3` #968D7B o único aviso restante é
`chart-4` ("Outros", rotulado).

## Além da cor — o que o sistema precisa para não depender só da cor (achados nos componentes)

| Ponto | Critério | Achado | O que fica definido |
|---|---|---|---|
| Etapas (k-steps) | 1.4.1 · 1.1.1 | só cor (feita/atual/bloqueada) | `role="img"` + `aria-label="Etapa 4 de 5: Revisão"` + coluna Etapa em texto |
| Presença (k-presence) | 1.4.1 | ponto verde sem texto | texto para leitor de tela ("trabalhando agora") — e hoje não há dado de presença |
| Não lida (k-unread) | 1.4.1 · 1.3.1 | ponto laranja sem texto | `.k-sr-only` "não lida" |
| Critério do portão (k-check) | 4.1.2 | `<b>` desenhado como caixa | lista; caixa `aria-hidden` e o estado escrito no chip do mapa único (livro §11.3); se um dia for clicável, `<input type="checkbox">` de verdade |
| Delta do KPI | 1.4.1 · 1.1.1 | seta ▲/▼ + cor | seta `aria-hidden` + palavra ("a menos", "de aumento"); a cor segue o significado |
| Item ativo do menu | 4.1.2 | só visual | `aria-current="page"` (o ponto e o fundo também marcam, além da cor) |
| Item de menu sem página | 4.1.2 | — | não é link; `aria-disabled="true"` + "ainda sem página" para leitor de tela; apagado a .45 (isento, 1.4.3) |
| Menu de 7 itens antes do conteúdo | 2.4.1 | — | link "Pular para o conteúdo" (`.k-skip`), primeiro Tab da página |
| Dica (k-tooltip) | 1.4.13 · 2.1.1 | — | abre com hover **e foco**, fecha com Esc e ao sair, nunca sai da janela (8px das bordas) |
| Gráficos | 1.1.1 · 1.4.1 | valor só na dica | `aria-label` no SVG + tabela gêmea + rótulo direto; a dica complementa |
| Tabela larga em 375px | 2.1.1 · 1.4.10 | — | rola **dentro** do card numa região com `tabindex="0"`, `role="region"` e nome |
| Foco | 2.4.7 | anel 2px + 2px em tudo | vale; `accent-ink` nos fundos claros e `accent` na barra lateral (decisão de 23/10, G03–G06, G26, G27) |
| Movimento | 2.3.3 | — | esqueleto só "respira" se a pessoa não pediu menos movimento (`prefers-reduced-motion`) |
| Texto abaixo de 11px | (legibilidade) | rótulo do portão 10px, dia do calendário 10,5px, eixos 10px, `k-sidebar-label` 10px | contrastes passam (ver T06/T32); o tamanho fica como o Carlos desenhou e a proposta de subir para 11px (caption) vai a ele |
| Alvo de toque | 2.5.8 (2.2) | controles 36px, pequeno 28px, item de menu 34px | todos ≥ 24×24 |
| Botão desativado | 1.4.3 | opacity .45 | isento (controle inativo); "Aprovar e agendar" desativado até todos os critérios feitos |

## Tabela completa (saída de `verificacao/contraste.py`)

| # | Frente | Fundo | Hex | Razão | Mínimo | Resultado | Onde |
|---|---|---|---|---|---|---|---|
| T01 | `ink` | `bg` | #111111 / #f5f2e8 | 16.86:1 | 4.5:1 (texto) | passa | corpo, títulos e números sobre o fundo |
| T02 | `ink` | `surface` | #111111 / #fbf9f4 | 17.95:1 | 4.5:1 (texto) | passa | corpo e números dentro de cards e tabelas |
| T03 | `ink` | `surface-sunken` | #111111 / #efebe0 | 15.85:1 | 4.5:1 (texto) | passa | botão secundário em hover, item de menu em hover, ícone de nota neutra |
| T04 | `ink` | `surface-hover` | #111111 / #f8f5ee | 17.34:1 | 4.5:1 (texto) | passa | linha de tabela em hover |
| T05 | `ink-2` | `bg` | #6b6458 / #f5f2e8 | 5.22:1 | 4.5:1 (texto) | passa | texto secundário sobre o fundo; k-kbd |
| T06 | `ink-2` | `surface` | #6b6458 / #fbf9f4 | 5.56:1 | 4.5:1 (texto) | passa | descrições, rótulos k-cap 11px, eixos 10px, cabeçalho de tabela |
| T07 | `ink-2` | `surface-sunken` | #6b6458 / #efebe0 | 4.91:1 | 4.5:1 (texto) | passa | chip Agendado (12px/600), delta neutro |
| T08 | `ink-2` | `surface-hover` | #6b6458 / #f8f5ee | 5.37:1 | 4.5:1 (texto) | passa | células secundárias numa linha em hover |
| T09 | `ink-3` | `bg` | #736c60 / #f5f2e8 | 4.64:1 | 4.5:1 (texto) | passa | meta e horários sobre o fundo |
| T10 | `ink-3` | `surface` | #736c60 / #fbf9f4 | 4.94:1 | 4.5:1 (texto) | passa | meta em cards; placeholder da busca |
| T11 | `ink-3` | `surface-hover` | #736c60 / #f8f5ee | 4.77:1 | 4.5:1 (texto) | passa | meta da VideoRow ("Reel · …") numa linha em hover |
| T12 | `ink-3` | `surface-sunken` | #736c60 / #efebe0 | 4.36:1 | 4.5:1 (texto) | falha esperada — uso proibido | NÃO permitido pelo token ink-3 — medido para mostrar por quê |
| T13 | `on-accent` | `accent` | #111111 / #ff4d00 | 5.68:1 | 4.5:1 (texto) | passa | rótulo do botão primário (13px/600); ícone do k-thumb laranja |
| T14 | `on-accent` | `accent-hover` | #111111 / #e64500 | 4.69:1 | 4.5:1 (texto) | passa | rótulo do botão primário em hover |
| T15 | #ffffff | `accent` | #ffffff / #ff4d00 | 3.33:1 | 4.5:1 (texto) | falha esperada — uso proibido | branco sobre o laranja — proibido pela fonte; conferido |
| T16 | `accent-ink` | `bg` | #b33600 / #f5f2e8 | 5.44:1 | 4.5:1 (texto) | passa | texto laranja sobre o fundo |
| T17 | `accent-ink` | `surface` | #b33600 / #fbf9f4 | 5.79:1 | 4.5:1 (texto) | passa | chip Portão (contorno), marca ✓ do menu |
| T18 | `accent-ink` | `accent-soft` | #b33600 / #ffe8dc | 5.18:1 | 4.5:1 (texto) | passa | chip Em produção, evento de portão no calendário |
| T19 | `accent-ink` | `surface-hover` | #b33600 / #f8f5ee | 5.60:1 | 4.5:1 (texto) | passa | chip Portão numa linha em hover |
| T20 | `accent` | `bg` | #ff4d00 / #f5f2e8 | 2.97:1 | 3.0:1 (texto grande) | **FALHA** | laranja como texto só a partir de 24px (regra da fonte) |
| T21 | `accent` | `surface` | #ff4d00 / #fbf9f4 | 3.16:1 | 3.0:1 (texto grande) | passa | idem, dentro de card |
| T22 | `accent` | `bg` | #ff4d00 / #f5f2e8 | 2.97:1 | 4.5:1 (texto) | falha esperada — uso proibido | laranja como texto PEQUENO sobre o fundo — proibido pela fonte; conferido |
| T23 | `positive` | `bg` | #1e7a45 / #f5f2e8 | 4.78:1 | 4.5:1 (texto) | passa | métrica positiva sobre o fundo |
| T24 | `positive` | `surface` | #1e7a45 / #fbf9f4 | 5.09:1 | 4.5:1 (texto) | passa | métrica positiva em card |
| T25 | `positive` | `positive-soft` | #1e7a45 / #e3f0e4 | 4.55:1 | 4.5:1 (texto) | passa | chip Aprovado, delta ▲ (12px/600) |
| T26 | `danger` | `bg` | #c2271b / #f5f2e8 | 5.21:1 | 4.5:1 (texto) | passa | alerta sobre o fundo |
| T27 | `danger` | `surface` | #c2271b / #fbf9f4 | 5.54:1 | 4.5:1 (texto) | passa | alerta em card |
| T28 | `danger` | `danger-soft` | #c2271b / #fbe3df | 4.77:1 | 4.5:1 (texto) | passa | chip Bloqueado, delta de custo ▲ (12px/600) |
| T29 | `bg` | `ink` | #f5f2e8 / #111111 | 16.86:1 | 4.5:1 (texto) | passa | chip Publicado, chip Opus, botão escuro, ✓ do critério feito |
| T30 | `sidebar-ink` | `sidebar` | #f5f2e8 / #111111 | 16.86:1 | 4.5:1 (texto) | passa | logotipo korvu., texto da dica (tooltip) |
| T31 | `sidebar-ink` | `sidebar-raised` | #f5f2e8 / #1d1c1a | 15.20:1 | 4.5:1 (texto) | passa | item ativo e em hover, avatar do rodapé |
| T32 | `sidebar-ink-2` | `sidebar` | #9a9385 / #111111 | 6.19:1 | 4.5:1 (texto) | passa | itens inativos (13px/500), contagens 11px, 2.ª linha da dica |
| T33 | `sidebar-ink-2` | `sidebar-raised` | #9a9385 / #1d1c1a | 5.58:1 | 4.5:1 (texto) | passa | contagem dentro do item ativo/hover |
| T34 | `sidebar-ink-2` a 80% sobre `sidebar` | `sidebar` | #7f796e / #111111 | 4.37:1 | 4.5:1 (texto) | **FALHA** | k-sidebar-label (10px, opacity .8) — rótulo de grupo da barra lateral |
| T35 | `accent` | `sidebar` | #ff4d00 / #111111 | 5.68:1 | 4.5:1 (texto) | passa | laranja como texto sobre a barra lateral (permitido pela fonte) |
| G01 | `line-strong` | `bg` | #928874 / #f5f2e8 | 3.13:1 | 3.0:1 (controle) | passa | borda de campo, dropdown e botão secundário sobre o fundo (#928874, decisão de 23/10) |
| G02 | `line-strong` | `surface` | #928874 / #fbf9f4 | 3.33:1 | 3.0:1 (controle) | passa | idem dentro de card; caixa do critério (k-check) (decisão de 23/10) |
| G03 | `focus` | `bg` | #b33600 / #f5f2e8 | 5.44:1 | 3.0:1 (foco) | passa | anel de foco 2px (afastamento 2px) sobre o fundo — focus = accent-ink (decisão de 23/10) |
| G04 | `focus` | `surface` | #b33600 / #fbf9f4 | 5.79:1 | 3.0:1 (foco) | passa | anel de foco sobre card |
| G05 | `focus` | `surface-sunken` | #b33600 / #efebe0 | 5.12:1 | 3.0:1 (foco) | passa | anel de foco sobre área rebaixada (segmentado, atalho) |
| G06 | `focus-on-dark` | `sidebar` | #ff4d00 / #111111 | 5.68:1 | 3.0:1 (foco) | passa | anel de foco na barra lateral e na barra de topo (focus-on-dark = accent) |
| G25 | `line-strong` | `surface-sunken` | #928874 / #efebe0 | 2.94:1 | 3.0:1 (controle) | falha esperada — uso proibido | NÃO permitido: nenhum controle com borda line-strong sobre surface-sunken — medido para mostrar por quê |
| G26 | `focus` | `surface-hover` | #b33600 / #f8f5ee | 5.60:1 | 3.0:1 (foco) | passa | anel de foco numa linha ou cartão em hover |
| G27 | `focus-on-dark` | `sidebar-raised` | #ff4d00 / #1d1c1a | 5.12:1 | 3.0:1 (foco) | passa | anel de foco no item ativo da barra lateral |
| G07 | `ink` | `surface` | #111111 / #fbf9f4 | 17.95:1 | 3.0:1 (controle) | passa | borda do campo em foco / dropdown aberto |
| G08 | `accent` | `surface-sunken` | #ff4d00 / #efebe0 | 2.79:1 | 3.0:1 (gráfico) | **FALHA** | preenchimento da barra de progresso; etapa atual (k-steps .now) |
| G09 | `ink` | `surface-sunken` | #111111 / #efebe0 | 15.85:1 | 3.0:1 (gráfico) | passa | etapa concluída (k-steps .on) |
| G10 | `positive` | `surface-sunken` | #1e7a45 / #efebe0 | 4.49:1 | 3.0:1 (gráfico) | passa | barra concluída (k-progress.is-done) |
| G11 | `danger` | `surface-sunken` | #c2271b / #efebe0 | 4.90:1 | 3.0:1 (gráfico) | passa | etapa/barra bloqueada |
| G12 | `surface-sunken` | `surface` | #efebe0 / #fbf9f4 | 1.13:1 | 3.0:1 (gráfico) | **FALHA** | trilho da barra e etapas FUTURAS contra o card |
| G13 | `chart-1` | `surface` | #ff4d00 / #fbf9f4 | 3.16:1 | 3.0:1 (gráfico) | passa | série 1 (laranja) |
| G14 | `chart-2` | `surface` | #111111 / #fbf9f4 | 17.95:1 | 3.0:1 (gráfico) | passa | série 2 (preto) |
| G15 | `chart-3` | `surface` | #a39b8b / #fbf9f4 | 2.62:1 | 3.0:1 (gráfico) | **FALHA** | série 3 (taupe) |
| G16 | `chart-4` | `surface` | #d6ccb5 / #fbf9f4 | 1.52:1 | 3.0:1 (gráfico) | **FALHA** | série 4 / "Outros" (areia) |
| G17 | `chart-5` | `surface` | #4f6475 / #fbf9f4 | 5.85:1 | 3.0:1 (gráfico) | passa | série 5 (ardósia); barra do evento Facebook |
| G18 | `ink-3` | `surface-sunken` | #736c60 / #efebe0 | 4.36:1 | 3.0:1 (gráfico) | passa | ícone play do k-thumb neutro |
| G19 | `accent-ink` | `accent-soft` | #b33600 / #ffe8dc | 5.18:1 | 3.0:1 (gráfico) | passa | cadeado do portão (k-gate-icon), ícone de nota de portão |
| G20 | `accent-ink` | `surface-sunken` | #b33600 / #efebe0 | 5.12:1 | 3.0:1 (gráfico) | passa | ✓ do item selecionado com o item em hover |
| G21 | `positive` | `surface` | #1e7a45 / #fbf9f4 | 5.09:1 | 3.0:1 (gráfico) | passa | ponto de presença (k-presence) |
| G22 | `accent` | `surface` | #ff4d00 / #fbf9f4 | 3.16:1 | 3.0:1 (gráfico) | passa | ponto de não lida (k-unread); contorno do chip Portão |
| G23 | `accent` | `sidebar-raised` | #ff4d00 / #1d1c1a | 5.12:1 | 3.0:1 (gráfico) | passa | ícone e ponto do item ativo na barra lateral |
| G24 | `accent` | `bg` | #ff4d00 / #f5f2e8 | 2.97:1 | — | — (não exigido) | contorno do botão primário contra o fundo — o rótulo identifica o botão (1.4.11 não exige) |
| I01 | `line` | `bg` | #e4dfd2 / #f5f2e8 | 1.19:1 | — | — (decorativo) | borda fina de card (a fonte declara decorativa) |
| I02 | `line` | `surface` | #e4dfd2 / #fbf9f4 | 1.26:1 | — | — (decorativo) | divisórias de tabela |
| I03 | `chart-grid` | `surface` | #e9e4d8 / #fbf9f4 | 1.21:1 | — | — (decorativo) | grade dos gráficos |
| I04 | `sidebar-line` | `sidebar` | #2c2a27 / #111111 | 1.32:1 | — | — (decorativo) | divisória do rodapé da barra lateral |
| I05 | `sidebar-raised` | `sidebar` | #1d1c1a / #111111 | 1.11:1 | — | — (decorativo) | fundo do item ativo (o ponto laranja também marca) |
| I06 | `surface` | `bg` | #fbf9f4 / #f5f2e8 | 1.06:1 | — | — (decorativo) | card contra o fundo (a borda line separa) |
| I07 | `ink-2` | `bg` | #6b6458 / #f5f2e8 | 5.22:1 | — | — (logotipo) | "painel" no logotipo claro — logotipo é isento (1.4.3) |
| I08 | `sidebar-ink-2` | `sidebar` | #9a9385 / #111111 | 6.19:1 | — | — (logotipo) | "painel" no logotipo escuro — isento |
| I09 | `on-accent` a 45% sobre `accent` a 45% sobre `bg` | `accent` a 45% sobre `bg` | #91644e / #faa880 | 2.65:1 | — | — (desativado) | botão primário desativado (opacity .45) — controle inativo é isento (1.4.3) |
| I10 | `sidebar-ink-2` a 45% sobre `sidebar` | `sidebar` | #4f4c45 / #111111 | 2.20:1 | — | — (desativado) | item de menu sem página (proposta: opacity .45, a mesma do botão desativado) — inativo é isento (1.4.3) |

6 par(es) abaixo do mínimo.
