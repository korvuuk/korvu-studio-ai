# korvu. painel — design system

> **Fonte:** o design system "korvu. painel" que o Carlos fez no Claude Design em 23/10/2026
> (cópia exata e intocada em `painel/referencias/claude-design/korvu-painel-2026-10-23/`). Importado para cá **em PT-BR**
> pela designer-de-produto, com os **valores exatos** da fonte. Conferir a fidelidade:
> `uv run python -I painel/design/verificacao/fidelidade.py`.
>
> **Como ler as marcas deste livro**
> - sem marca = o que o Carlos desenhou, só traduzido para PT-BR;
> - **[TRANSCRITO]** = estilo que estava escrito à mão (inline) nas prévias do Claude Design e virou classe, com os mesmos valores;
> - **[PROPOSTA]** = acréscimo da designer-de-produto para o que o artefato não cobriu (375 px, carregando, erro, não
>   encontrado, item sem página…) — vai ao Carlos;
> - **[DIVERGÊNCIA]** = a fonte diz duas coisas diferentes; está escrito o que ficou valendo e por quê — vai ao Carlos.
>
> Prévias (abrem sem internet): `previas/index.html`. Contraste: `contraste.md`. Para o front-end: `handoff.md`.
>
> **2.ª rodada (23/10, tarde): as 7 telas.** O Carlos desenhou no Claude Design as telas Visão geral, Equipe, Produção de
> conteúdo, Calendário, Desempenho, Biblioteca e Tokens e custos (fonte exata em
> `painel/referencias/claude-design/telas-2026-10-23/`). Elas estão em `telas/` (uma especificação `.md` e uma maquete
> `.html` por tela, com dados reais). Os componentes que as telas pediram estão na **§15** e em `acrescimos.css`; as
> decisões dele de 23/10 (menu "Produção de conteúdo", canais por publicação, versão do modelo, tokens em destaque, retrato
> por foto) estão aplicadas aqui, com as de **24/10**: sem título de página, o painel só informa (sem botões que criam
> coisas), custo em US$ sem câmbio, projeção pelos últimos 30 dias e o modelo que **rodou** na Equipe.

---

## 0. Decisão, escopo e o que muda em relação à marca editorial

**Decisão do Carlos, 23/10/2026** (`docs/decisoes.md`): o design system do painel passa a ser o "korvu. painel" que ele
mesmo montou no Claude Design. Ele **substitui o `korvu-editorial` dentro do painel**. O `korvu-editorial`
(`00-marca/design-system/korvu-editorial.md`) **continua valendo** para o PDF do CTA, o CTA na tela e o Remotion.
As diferenças abaixo não são desvio da designer: são a decisão dele.

| | korvu-editorial (PDF, CTA, Remotion) | korvu. painel (este sistema) |
|---|---|---|
| Fundo | papel `#E7E4D9` | marfim `#F5F2E8` (`bg`); cards `#FBF9F4` (`surface`) |
| Acento | laranja `#E85002` | laranja `#FF4D00` (`accent`), **com texto preto em cima** (`on-accent` #111); texto laranja = `accent-ink` #B33600 |
| Títulos | Bricolage Grotesque 800, minúsculas com ponto final | **Geist** 800/700, só a primeira letra maiúscula, tracking negativo |
| Texto | Inter | **Geist** |
| Mono | proibida ("cara de terminal") | **Geist Mono permitida** para modelos, IDs, HEX e contagens de tokens |
| Cantos | sem canto arredondado | raios 6 · 8 · 12 · 14 · pill |
| Sombra | nenhuma | três sombras quase invisíveis (a borda faz o trabalho) |
| Navegação | cabeçalho com links | **barra lateral escura fixa de 208px** |
| Continua igual | UM acento laranja · nada de degradê ou vidro · tinta #111 | idem |

**Escopo:** o **sistema** — tokens, fontes, marca, ícones, componentes, regras, estados e o comportamento em 375 px — e,
desde a 2.ª rodada de 23/10, as **7 telas** em `telas/`, desenhadas pelo Carlos no Claude Design a partir daqui (§15).

**Dois entendimentos ajustados para este caso:**
- **"Carlos · Proprietário" no rodapé da barra lateral** fica como ele desenhou. A regra de 21/10 ("o nome pessoal do
  Carlos não aparece") é para o material **público** (vídeos, PDF, posts). O painel é privado: só abre no Mac dele
  (decisão de 23/10, "o painel só abre no próprio Mac") e não tem login nem outros usuários.
- **Avatares**: **retrato = foto realista** (decisão do Carlos de 23/10, `docs/decisoes.md` §5). Quem ainda não tem foto
  mostra as iniciais. Ver §10.

**Exemplos da fonte trocados:** a fonte usava nomes fictícios e conteúdo amarrado a um país — contra a decisão de 21/10
(nada definido por país). Aqui os nomes são os da equipe real (`painel/equipe.yaml`), os títulos são os dos vídeos reais
e todo número vem do banco do painel (`dados-2026-10-23.json`, com a consulta de cada bloco) ou está marcado "exemplo".

---

## 1. Conteúdo e tom

- Toda a interface em **português do Brasil**, tratando por **"você"**. Sem emoji, sem exclamação, sem jargão de marketing.
- Datas `22 out`, horas `18:30`. Números com vírgula decimal e ponto de milhar: `482,6K`, `US$ 539,06`, `1.284.910 tokens`.
  Dinheiro em dólar, com o símbolo antes e um espaço que não quebra (`US$ 25,67`); sem câmbio (decisão de 24/10).
- **[PROPOSTA] Quando compactar:** no KPI, até 9.999 o número inteiro (`3.631`); de 10.000 em diante, compacto com uma
  casa (`482,6K`, `12,8M`). Na dica e na tabela, sempre o número exato. (A fonte mostra os dois formatos sem dizer o limite.)
- Rótulos curtos e concretos, só a primeira letra maiúscula: "Produção de conteúdo", "Ver calendário", "Tentar de novo".
- **Sem título de página** (decisão de 24/10: "é uma duplicidade entre o menu e o título"). O `h1` editorial ("o estúdio
  hoje.", "equipe.") saiu das telas; cada página guarda um `h1` **só para leitor de tela** (`k-sr-only`, com o nome do item
  do menu) e, quando tem busca, data ou período, uma barra fina no alto (`.k-page-barra`, §15.2). Os títulos de bloco em
  minúsculas com ponto ("crescimento.", "por modelo.") continuam como o Carlos desenhou; títulos de card, rótulos e botões
  com a primeira maiúscula. O ponto nunca é laranja.
- **O painel só informa, não age** (decisão de 24/10): nenhuma tela tem botão que cria coisa — "Novo vídeo", "Novo
  conteúdo", "Agendar", "Agendar publicação", "Adicionar material", "Adicionar pessoa/agente", "Contratar" e o "Copiar o
  pedido" saíram. Ficam os que levam a outra tela ou mudam a vista ("Ver calendário", "Ver roteiros", "Hoje", filtros,
  "Tentar de novo"). Pedidos são feitos no Claude Code.
- **Modelo sempre com a versão** (decisão de 23/10): "Opus 5.5", "Sonnet 5.5", "Fable 5.1" — nunca só "opus".
- **O modelo de um agente é o que RODOU** (decisão de 24/10), dos registros do Claude Code (`message.model`), não o
  configurado em `.claude/agents/`: quem escolhe o modelo são os orquestradores, pela tarefa. Com mais de um modelo, o
  chip do principal + "92 % · +1"; sem registro, "ainda não rodou".
- **Tokens em destaque** (decisão de 23/10): contagem de tokens em `accent-ink` no texto pequeno (`.k-tokens`) e em
  `accent` a partir de 24 px (`.k-tokens.is-grande`). Vermelho continua só para alerta.
- **Custo de IA em US$, a moeda da tabela da Anthropic, sem câmbio** (decisão de 24/10, que substitui a de 23/10 em £).
  Exemplo: 30 dias = US$ 539. **Projeção mensal = média dos últimos 30 dias × 30** (não 7). Com assinatura, a fatura é
  outra — a tela diz isso; a projeção é estimativa.
  Rótulos de seção e de KPI em MAIÚSCULAS **só pelo estilo `caption`** (o texto continua escrito normal).
- Os agentes são tratados como equipe: nome próprio + função + departamento ("Marina Costa · Roteirista · Roteiro").
- Não existe login nem gestão de usuários; o único dono é o **Carlos**, que aparece no rodapé da barra lateral como
  "Proprietário" e é quem decide nos portões.
- Estado vazio diz **o que vai aparecer aqui** ("Quando um portão parar um vídeo, ele aparece aqui com o motivo.").
- Erro diz **o que aconteceu + por quê + como resolver**, e oferece "Tentar de novo".
- Público e autoria: "korvu" / "@korvu_oficial"; nada de público definido por país ou por língua nos textos.
- Período sempre escrito: "desde 16 out", "vs. 16 out", "28 dias". As métricas do perfil vêm da Meta em janelas de 28 dias.

---

## 2. Cor — não alterar sem decisão do Carlos

Tema único, claro, chamado "Marfim". **Não existe modo escuro.** As telas de 23/10 não pediram cor nova. Valores em `tokens.json` / `tokens.css`.

**Decisão do Carlos, 23/10** (`docs/decisoes.md` §5): "Aceito as duas: borda dos campos em #928874 e anel de foco em
laranja escuro (accent-ink) nos fundos claros." — `line-strong` passou de `#A8A090` a **`#928874`**; `focus` passou de
alias de `accent` a **alias de `accent-ink`**; e entrou **`focus-on-dark`** (= `accent`) para o anel nos fundos escuros. São
as únicas cores que divergem da fonte; o `verificacao/fidelidade.py` as registra como divergências aprovadas.

| Token | Valor | Uso |
|---|---|---|
| `bg` | `#F5F2E8` | Fundo principal de todas as telas (marfim quente). Nunca branco puro. |
| `surface` | `#FBF9F4` | Fundo de cards, tabelas, popovers e campos — um passo mais claro que `bg`. |
| `surface-sunken` | `#EFEBE0` | Áreas rebaixadas: trilho de progresso, chips neutros, células vazias do calendário, hover de linha. Só `ink` e `ink-2` sobre ele. |
| `surface-hover` | `#F8F5EE` | Hover discreto de card e de linha de tabela. |
| `line` | `#E4DFD2` | Borda fina (1px) de cards, divisórias de tabela e separadores. Decorativa: nunca é a única pista de um controle. |
| `line-strong` | `#928874` (decisão de 23/10; a fonte tinha `#A8A090`) | Borda de controles (campos, dropdown, botão secundário): **3,13:1 sobre `bg` e 3,33:1 sobre `surface`**. Sobre `surface-sunken` dá 2,94: **nenhum controle com esta borda sobre esse fundo**. |
| `ink` | `#111111` | Texto principal, títulos, números de métricas. Sobre `bg`, `surface`, `surface-sunken` e `accent`. |
| `ink-2` | `#6B6458` | Texto secundário (cinza quente): descrições, rótulos, eixos de gráfico. Sobre `bg`, `surface`, `surface-sunken`. |
| `ink-3` | `#736C60` | Meta e legendas pequenas (horários, contagens). Só sobre `bg` e `surface`. |
| `sidebar` | `#111111` | Fundo da barra lateral fixa (quase preto) e das dicas (tooltips). |
| `sidebar-raised` | `#1D1C1A` | Item ativo e hover dentro da barra lateral. |
| `sidebar-line` | `#2C2A27` | Divisórias dentro da barra lateral. |
| `sidebar-ink` | `#F5F2E8` | Texto ativo e o `korvu.` do logotipo sobre `sidebar`. |
| `sidebar-ink-2` | `#9A9385` | Itens inativos e a palavra `painel` sobre `sidebar` (6,19:1). |
| `accent` | `#FF4D00` | Laranja Korvu: botão primário, item ativo, foco, série principal dos gráficos. Como texto, só sobre `sidebar` ou a partir de 24px — sobre `bg` use `accent-ink`. |
| `accent-hover` | `#E64500` | Hover/pressionado do botão primário. |
| `accent-soft` | `#FFE8DC` | Fundo do chip `Em produção` e de destaques laranja suaves. |
| `accent-ink` | `#B33600` | Texto laranja sobre `bg`, `surface` e `accent-soft` (≥ 4,5:1). |
| `on-accent` | `#111111` | Texto e ícones sobre `accent` (5,68:1). Branco sobre o laranja falha (3,33:1). |
| `positive` | `#1E7A45` | Só métricas positivas (▲ +12%) e o chip `Aprovado`. Sobre `bg`, `surface`, `positive-soft`. |
| `positive-soft` | `#E3F0E4` | Fundo do chip `Aprovado` e do delta positivo. |
| `danger` | `#C2271B` | Só alertas: chip `Bloqueado`, custo acima do orçamento, erros. Sobre `bg`, `surface`, `danger-soft`. |
| `danger-soft` | `#FBE3DF` | Fundo do chip `Bloqueado` e das notificações de alerta. |
| `chart-1` | `#FF4D00` (= `accent`) | Série principal de qualquer gráfico (a que está em foco). |
| `chart-2` | `#111111` | Segunda série / comparação (período anterior, Facebook). |
| `chart-3` | `#A39B8B` | Terceira série (taupe). |
| `chart-4` | `#D6CCB5` | Quarta série e restos ("Outros") em gráficos de rosca. |
| `chart-5` | `#4F6475` | Quinta série, só quando funcionalmente necessária (ardósia). |
| `chart-grid` | `#E9E4D8` | Linhas de grade dos gráficos. |
| `focus` | `#B33600` (= `accent-ink`; decisão de 23/10, a fonte tinha `accent`) | Anel de foco 2px + afastamento 2px em todos os controles dos fundos claros: 5,44 sobre `bg`, 5,79 sobre `surface`, 5,12 sobre `surface-sunken`, 5,60 sobre `surface-hover`. |
| `focus-on-dark` | `#FF4D00` (= `accent`; acréscimo da mesma decisão) | Anel de foco na barra lateral e na barra de topo escuras: 5,68 sobre `sidebar`, 5,12 no item ativo (`sidebar-raised`). Nome e regra iguais aos da versão 6 do artefato do Claude Design: `.k-sidebar :focus-visible{outline-color:var(--focus-on-dark)}` no `componentes.css`, logo abaixo do `:focus-visible` (o `fidelidade.py` aceita só esta regra, neste lugar); a barra de topo escura (< 1024 px), que é acréscimo nosso, tem a mesma regra em `acrescimos.css` (`.k-topbar :focus-visible`). |

**Regras**
- Fundo de toda tela: `bg`. Cards, tabelas, campos e popovers: `surface` com borda 1px `line`. Zonas rebaixadas (trilhos,
  chips neutros, hover): `surface-sunken`.
- Barra lateral e dicas: `sidebar`; texto sobre ela `sidebar-ink` (ativo) e `sidebar-ink-2` (inativo).
- Texto: `ink` para títulos, valores e corpo; `ink-2` para secundário; `ink-3` só para meta sobre `bg` e `surface`.
- Laranja = ação e foco: botão primário, item ativo (ícone + ponto), anel de foco, série principal de gráfico.
  **Texto sobre o laranja é sempre `on-accent` (#111).** Texto laranja sobre fundo claro é `accent-ink`.
- Verde **só** para métricas positivas e o estado Aprovado; vermelho **só** para alertas e o estado Bloqueado.
  **A cor do delta segue o significado**: custo subindo é vermelho.
- Gráficos: `chart-1` laranja → `chart-2` preto → `chart-3` taupe → `chart-4` areia → `chart-5` ardósia, **nesta ordem**;
  outras cores não existem. Verde e vermelho nunca como série.
- **Contraste** (medido, `contraste.md`): todo texto que o sistema manda usar passa AA, e desde 23/10 também a borda dos
  controles (`line-strong` 3,13/3,33) e o anel de foco (5,1–5,8 nos fundos claros, 5,68 na barra lateral). Ficam abaixo do
  mínimo — como o Carlos desenhou, com mitigação e proposta — o laranja como texto grande sobre `bg` (2,97), o
  progresso/etapas sobre `surface-sunken`, `chart-3` (2,62) e `chart-4` (1,52) contra o card e o `k-sidebar-label` (4,37).

---

## 3. Tipografia

Família única **Geist** (`--font-sans`: `Geist, Inter, system-ui, sans-serif`), com **Geist Mono** (`--font-mono`:
`"Geist Mono", ui-monospace, monospace`) para modelos, IDs, HEX e contagens de tokens. Arquivos variáveis (peso 100–900)
em `fontes/`, licença **SIL Open Font License 1.1** (`fontes/OFL.txt`). Não usar as fontes antigas do painel
(Bricolage Grotesque / Inter).

| Estilo | Tamanho / linha | Peso | Tracking | Uso | Classe |
|---|---|---|---|---|---|
| `display` | 56 / 60 | 800 | −0,035em | Só em capas e estados de boas-vindas. No máximo uma por tela. | `.k-display` |
| `h1` | 44 / 48 | 800 | −0,03em | Título da página (topo da área principal). | `.k-h1` |
| `h2` | 30 / 36 | 700 | −0,02em | Título de seção dentro da página. | `.k-h2` |
| `h3` | 22 / 28 | 700 | −0,015em | Título de card grande, modal ou painel lateral. | `.k-h3` |
| `body` | 15 / 22 | 400 | — | Texto corrido, células de tabela, descrições. | `.k-body` (é o padrão do `body`) |
| `body-strong` | 15 / 22 | 600 | — | Nomes, títulos de linha e de card pequeno. | `.k-body-strong` |
| `small` | 13 / 18 | 500 | — | Rótulos de botão, chips, barra lateral, texto auxiliar. | `.k-small` |
| `caption` | 11 / 14 | 600 | 0,08em, MAIÚSCULAS | Rótulos de seção e de KPI, sempre em `ink-2` ou `ink-3`. | `.k-cap` |
| `metric-xl` | 40 / 44 | 700 | −0,03em | Valor principal do KPI (tabular). | `.k-metric-xl` / `.k-kpi-value` |
| `metric-l` | 24 / 28 | 700 | −0,02em | Valores secundários e totais em tabelas e cards de equipe. | `.k-metric-l` |
| `mono` | 12 / 16 | 500 | — | Modelos, IDs, contagens de tokens e códigos HEX (Geist Mono). | `.k-mono` |

- Títulos com tracking negativo (−1,5% a −3,5%). Todos os números com algarismos tabulares (`font-variant-numeric:
  tabular-nums`, classe `.k-num`; o `body` já liga `"tnum"`).
- Uma página = **um** `h1` no topo, com `space-64` acima. `display` só em boas-vindas e capas.
- `.k-display` … `.k-metric-l` são **[TOKEN]**: só aplicam a escala de `tokens.json` (a fonte trazia a escala, não as classes).
- **[DIVERGÊNCIA]** a prancha desenha o `display` com −0,04em e o `h1` do cabeçalho dela com linha de 44px; ficou o token
  (−0,035em e 48px). O README do logotipo cita tracking −4% para o "korvu.": o logotipo é contorno vetorial, não texto.
- O símbolo `⌘` não existe na Geist (cai na fonte do sistema). `▲ ▼ … £ €` existem.
- Nota da skill dataviz: ela recomenda algarismos proporcionais em número grande isolado; a fonte manda tabular em todos.
  Ficou a fonte.

---

## 4. Layout e grade

| Token | Valor | Uso |
|---|---|---|
| `viewport-desktop` | 1440px | Largura de referência de todas as telas. |
| `sidebar-width` | 208px | Barra lateral fixa à esquerda. |
| `content-padding` | 32px | Padding lateral da área principal. |
| `grid-columns` | 12 | Colunas da área principal. |
| `grid-gutter` | 24px | Espaço entre colunas (**20px abaixo de 1280px** — `tokens.css` já faz). |
| `row-height` | 56px | Altura de linha de tabela (linha de vídeo). |
| `control-height` | 36px | Altura de botões, busca e dropdown. |

- Referência desktop **1440px**. Barra lateral fixa de 208px; área principal fluida com padding de 32px.
- Grade de **12 colunas**. KPIs em 3–4 cards (span 4 ou 3); gráfico principal span 8 + lateral span 4.
- Espaçamento só na escala `space-4 · 8 · 12 · 16 · 24 · 32 · 48 · 64`. Entre seções `space-48`; entre cards `space-24`;
  dentro de cards `space-16`/`space-24`.
- Topo de cada página (24/10): sem título visível; busca, data ou período numa barra fina (`.k-page-barra`). Sem ação primária.
- Medidas internas de alguns componentes (14, 20, 10, 6, 22…) vêm assim da fonte: a escala vale para o layout entre blocos.

**[PROPOSTA] Classes da casca** (`acrescimos.css`), que aplicam exatamente as regras acima: `.k-shell` (barra lateral +
área), `.k-main` (padding 64 em cima, 32 dos lados), `.k-page-head` (h1 à esquerda, `.k-page-tools` à direita, 32 abaixo — **sem uso nas telas desde 24/10**, ver `.k-page-barra`),
`.k-section` (48 entre seções), `.k-section-head`, `.k-grid` + `.k-span-3/4/6/8/12`, `.k-grid--tiles` (KPIs e cards de
equipe), `.k-skip` ("Pular para o conteúdo"). Prévia: `previas/casca.html`.

### 4.1 Tela estreita — 375 px **[PROPOSTA]**

O sistema veio só para 1440. A regra do painel continua: **375 px sem rolagem lateral**, fora de tabela larga (que rola
dentro do próprio card). Tudo abaixo é acréscimo e não muda nada acima de 1024px.

| Abaixo de | O que muda | Por quê |
|---|---|---|
| **1280px** | gutter 20px | regra da fonte |
| **1024px** | A barra lateral vira **barra de topo** (56px, fundo `sidebar`, logotipo ivory 19px) + botão **"Menu"** (rótulo + `chevron-down`; aberto: "Fechar" + `x`). Menu aberto = a mesma `.k-sidebar` em **tela cheia** abaixo da barra de topo — sem véu, sem vidro; fecha com Esc, ao tocar num item e ao trocar de página. Grade: tudo empilha (span 12); KPIs e cards de equipe em **2 por linha**; gráfico principal e lateral um embaixo do outro. | 208px fixos não cabem com conteúdo legível; não existe ícone de "menu" no conjunto, por isso o rótulo escrito |
| **768px** | Área principal com **16px** de lado (`space-16`); `h1` no **tamanho do h2** (30/36, peso 800 mantido); **24px** acima do h1; busca, período e ação numa linha própria, busca na largura toda; 32px entre seções; gutter 16px; calendário 2 dias por linha | 64px de topo e 44px de título comem metade da tela do celular |
| **640px** | **Uma coluna**: KPIs, cards de equipe e calendário; no card de pessoa as métricas descem para a linha de baixo, alinhadas ao nome; os rótulos das 5 etapas viram só o da etapa atual | 2 colunas de KPI com valor de 40px estouram em 343px úteis |

Sempre, em qualquer largura: **tabela larga** dentro de `.k-table-wrap` (rola dentro do card; região com `tabindex="0"`,
`role="region"` e nome); **dica** presa a 8px das bordas da janela; **menu do dropdown** nunca mais largo que a tela;
títulos longos com reticências onde o componente manda, nunca empurrando a página. Prévias: `casca.html`,
`casca-menu.html` (abra a 375px).

---

## 5. Espaçamento

| Token | Valor | Uso |
|---|---|---|
| `space-4` | 4px | Ícone ↔ texto em chips; ajustes finos. |
| `space-8` | 8px | Ícone ↔ rótulo em botões e itens da barra lateral; espaço entre chips. |
| `space-12` | 12px | Padding vertical de linhas de tabela e itens de lista. |
| `space-16` | 16px | Padding de cards pequenos; espaço entre campos. |
| `space-24` | 24px | Padding de cards e gutter da grade de 12 colunas. |
| `space-32` | 32px | Entre blocos de uma seção; padding lateral da área principal. |
| `space-48` | 48px | Entre seções da página. |
| `space-64` | 64px | Do topo da página até o H1; respiros editoriais. |

---

## 6. Formas, bordas e sombras

| Raio | Valor | Uso |
|---|---|---|
| `radius-sm` | 6px | Checkbox, dica (tooltip), células do calendário. |
| `radius-btn` | 8px | Botões, campos, busca, dropdown, itens da barra lateral. |
| `radius-card` | 12px | Cards, popovers, notificações. |
| `radius-panel` | 14px | Painéis grandes e modais. |
| `radius-pill` | 999px | Chips de estado, avatares redondos em pilhas, barras de progresso. |

| Sombra | Valor | Uso |
|---|---|---|
| `shadow-card` | `0 1px 2px rgba(17,17,17,0.04)` | Cards em repouso — quase invisível; a borda `line` faz o trabalho. |
| `shadow-hover` | `0 6px 20px rgba(17,17,17,0.07)` | Hover de card clicável (com borda `line-strong`). |
| `shadow-pop` | `0 12px 32px rgba(17,17,17,0.12)` | Dropdowns, popovers, notificações flutuantes. |

- **Bordas fazem o trabalho**, sombras quase não existem.
- Hover discreto: muda borda/sombra ou o fundo para `surface-hover`; **nunca escala nem cor saturada**.
- **Proibido:** degradê, vidro (glassmorphism), card com borda colorida à esquerda, card dentro de card.
  (A barra de 3px do evento do calendário é a marca de canal definida pela fonte para aquele componente — não é card.)

---

## 7. Movimento (lido do CSS dos componentes — a fonte não tem token de movimento)

| Nome em `tokens.css` | Valor | Onde |
|---|---|---|
| `--duracao-padrao` | 150ms | borda, sombra, fundo e cor de cards, botões e itens da barra lateral |
| `--duracao-linha` | 120ms | fundo da linha de tabela no hover |
| `--atraso-dica` | 300ms | tempo até a dica aparecer (hover ou foco) |
| `--curva` | `ease` | a fonte não define curva: vale o padrão do CSS |

Sem escala, sem quique, sem brilho correndo. O esqueleto de carregamento só "respira" (opacidade, 1,6s) se a pessoa não
pediu menos movimento.

---

## 8. Iconografia

- Conjunto próprio de ícones **outline**, grade 24px, **traço 1,5px**, pontas e junções arredondadas, `currentColor`.
- **31 ícones**: 7 da navegação (Visão geral · Equipe · Produção de conteúdo — arquivo `videos-portoes` · Calendário ·
  Desempenho · Biblioteca · Tokens e custos) + 24 de interface (`search`, `chevron-down`, `chevron-right`, `bell`, `lock`, `check`, `plus`, `more`,
  `arrow-up`, `arrow-down`, `clock`, `filter`, `x`, `alert`, `info`, `play`, `upload`, `sparkle`, `cpu`, `settings`,
  `inbox`, `eye`, `heart`, `users`).
- Arquivos: `icones/<nome>.svg` (31, `currentColor`), `icones/icones.json` (os mesmos caminhos + rótulos PT-BR) e
  `icones/navegacao/*.svg` (os 7 originais, traço `#111111`, para documentação e exportação).
- Tamanhos: **18px** na barra lateral, **16px** em botões e campos, **14px** em chips e tabelas, **22–24px** em estados vazios.
- **O portão é sempre o cadeado (`lock`).** Canais (Instagram, Facebook, LinkedIn) escritos por extenso — **nada de
  logotipo de terceiros**.
- **[TRANSCRITO] +4 ícones das telas de 23/10** em `icones/telas/` (`documento`, `seta-direita`, `link-externo`,
  `camera`; `icones-telas.json` com os caminhos e rótulos), no mesmo estilo (grade 24, traço 1,5, `currentColor`). Ficam
  fora de `icones/*.svg`, que é a cópia conferida dos 31 da fonte.
- Sem ícones preenchidos, sem emoji. Ícone decorativo: `aria-hidden`; ícone sozinho num botão: `aria-label` no botão.

---

## 9. Logotipo

`korvu.` (Geist 800) + `painel` (Geist 500, tom apagado), em contornos vetoriais.

- Fundo claro (`bg`, `surface`): `marca/korvu-painel-ink.svg` — `korvu.` em `ink`, `painel` em `ink-2`.
- Barra lateral / fundo escuro: `marca/korvu-painel-ivory.svg` — `korvu.` em `sidebar-ink`, `painel` em `sidebar-ink-2`.
- **Nunca em laranja, nunca separado** ("korvu." sem "painel" dentro do produto), **altura mínima 16px**, respiro em volta = a
  altura do "k". Na barra lateral, 19px.
- Logotipo é isento da regra de contraste (mesmo assim o "painel" fica a 5,22:1 e 6,19:1).

---

## 10. Imagens e avatares

- **Retrato = foto realista** (decisão do Carlos de 23/10, `docs/decisoes.md` §5; resolve o pendente de 22/10 — a
  ilustração editorial sai). As 10 fotos que ele mandou estão em `painel/web/public/equipe/<id do agente>.jpg` (eram
  `painel/web/src/app/equipe/img equipe/`); as cópias 512×512 das maquetes ficam em `telas/img/retratos/`. Regras do sistema
  do Claude Design para as próximas: headshot 1:1, cabeça no topo a ~18%, olhos a ~40%, ombros cortando a base, fundo liso
  perto de `surface-sunken`, luz suave, 512×512; recorte na tela com `object-position: 50% 22–24%`.
- **Quem ainda não tem foto: iniciais** (2 letras) em `ink-2` sobre `surface-sunken`, no mesmo quadro e no mesmo tamanho
  da foto — a página nunca muda de forma quando a foto chega. Hoje 16 das 26 pessoas estão em iniciais.
- A foto é sempre de pessoa fictícia; nenhuma foto de pessoa real além do Carlos (CLAUDE.md, regra 3).
- `alt="Retrato de <nome>"`; nas listas em que o nome está ao lado, a foto pode ser `alt=""` (o nome já é lido).
- Miniatura de vídeo: o frame real quando existe; sem frame, `k-thumb` neutro com o ícone `play`.

---

## 11. Componentes

Todos são classes `k-*` de `componentes.css` (cópia do `bundle.css`, mesmas regras) sobre `tokens.css`. Peças que
estavam inline nas prévias e os acréscimos estão em `acrescimos.css`. `korvu.js` (cópia do `bundle.js`) expõe
`window.Korvu` — `icon(nome, tamanho)`, `logo(altura, "ink"|"ivory")`, `hydrate()` — e preenche
`<span data-icon="…">` e `<span data-logo="ink|ivory">` sozinho; no app os ícones vêm de `icones/` (ver `handoff.md`).
Cada componente tem prévia em `previas/`.

### 11.1 Logotipo — `Korvu.logo()` · prévia `logo.html`
Ver §9. Em código: `<span data-logo="ivory" data-h="19"></span>` ou o SVG de `marca/`.

### 11.2 Botão — `k-btn` · prévia `botao.html`
Botões de **36px** (`control-height`), raio `radius-btn` (8px), rótulo 13px/600.

| Variante | Classe | Quando |
|---|---|---|
| Primário | `k-btn k-btn-primary` | **Uma** ação principal por vista. **Hoje nenhuma tela usa** (24/10: o painel só informa). Fundo `accent`, texto `on-accent` (#111). Hover `accent-hover`. |
| Secundário | `k-btn k-btn-secondary` | Ações de apoio (Exportar). `surface` + borda `line-strong`; hover `surface-sunken`. |
| Fantasma | `k-btn k-btn-ghost` | Ações terciárias e cancelar. Texto `ink-2`; hover `surface-sunken` + `ink`. |
| Escuro | `k-btn k-btn-dark` | Confirmação de portão — a decisão do Carlos. Fundo `ink`, texto `bg`. |
| Só ícone | `+ k-btn-icon` | Ícone 16px sem texto; **sempre `aria-label`**. |
| Pequeno | `+ k-btn-sm` | 28px, só em tabelas e barras densas. |

- Estados: repouso, hover, **foco** (anel 2px `focus` + 2px — `accent-ink`; na barra lateral, `focus-on-dark`), desativado (`disabled` → opacity .45, cursor proibido).
- O consumidor fornece o texto e um ícone opcional (`<span data-icon="…" data-size="16">`).
- **Texto branco sobre o laranja não é permitido** (3,33:1); sempre `on-accent`.
- Fazer: verbo no rótulo ("Ver calendário"). Não fazer: dois primários na mesma vista; "OK".

### 11.3 Chip de estado — `k-chip` · prévia `chip.html`
Chips totalmente arredondados (`radius-pill`), **24px**, 12px/600, **sempre com palavra** — a cor nunca é a única pista.

| Estado | Classe | Cor |
|---|---|---|
| Aprovado | `k-chip--aprovado` | `positive` sobre `positive-soft` |
| Em produção | `k-chip--producao` | `accent-ink` sobre `accent-soft` |
| Bloqueado | `k-chip--bloqueado` | `danger` sobre `danger-soft` |
| Agendado | `k-chip--agendado` | `ink-2` sobre `surface-sunken` |
| Publicado | `k-chip--publicado` | `bg` sobre `ink` (estado final) |
| Portão | `k-chip--portao` | contorno `accent`, texto `accent-ink`, ícone `lock`, sem ponto |
| Modelo Sonnet — **sempre com a versão** ("Sonnet 5.5") | `k-chip--model` | mono, contorno `line-strong` |
| Modelo Opus — **sempre com a versão** ("Opus 5.5") | `k-chip--opus` | mono, `ink` sólido (o desenho da fonte) |

- Ponto de 6px na cor do texto antes da palavra (`::before`); `no-dot` tira o ponto.
- Verde e vermelho só aqui e em métricas — nunca como decoração.
- **[PROPOSTA] Três famílias de estado, um mapa para cada — nunca dois desenhos para o mesmo estado:**

  **(1) Estado de cada portão do GAUNTLET** (o veredicto do portão-agente, de `portoes_estado`). É o **mapa único**: vale
  no chip, nos critérios do card do portão (§11.11) e no calendário (§11.12).

  | Estado no banco | Chip | Palavra |
  |---|---|---|
  | `aprovado` | `k-chip--aprovado` | Aprovado |
  | `bloqueado` | `k-chip--bloqueado` | Bloqueado |
  | `escalado` | `k-chip--bloqueado` | Escalado |
  | `vencido` | `k-chip--bloqueado` | Vencido |
  | `pendente` | `k-chip--agendado` | Ainda não rodou |
  | `nao_se_aplica` | `k-chip--agendado no-dot` | Não se aplica |
  | **legado** — `fila.legado = true` | `k-chip--agendado no-dot` | Legado · sem selo |

  - **Legado vence o "pendente" do banco** no portão da publicação: o pacote está na lista congelada de 22/10
    (`_controle/gauntlet-legado.json`) e publica sem selo — não espera portão nenhum.
  - Vermelho só para o que pede ação (bloqueado, escalado, vencido); a palavra diferencia os três.

  **(2) Decisão do Carlos** (só no card do portão, modo Decisão): `k-chip--portao`, como a fonte desenhou. Não é o estado
  de um portão-agente: só existe quando todos os portões do vídeo aprovaram.
  - Das três palavras da fonte (Aguarda · Aprovado · Ajustes), viram chip **"Aguarda"** (esperando a decisão) e
    **"Ajustes"** (ele pediu ajustes).
  - **"Aprovado" não vira chip laranja**: agendar (no Claude Code) leva o vídeo a **Agendado** (família 3) e sai do
    modo Decisão. Assim cada palavra tem um desenho só ("Aprovado" = o verde da família 1).

  **(3) Estado do vídeo** (linha de vídeo, cabeçalho do card do portão). **Lido em ordem — vale a primeira linha verdadeira:**

  | Ordem | Chip | Quando |
  |---|---|---|
  | 1 | **Bloqueado** (`k-chip--bloqueado`) | algum portão do vídeo (pauta, roteiro, imagem, corte) está bloqueado, escalado ou vencido. **Vem antes de Publicado e Agendado.** |
  | 2 | **Publicado** (`k-chip--publicado`) | status `publicado` |
  | 3 | **Agendado** (`k-chip--agendado`) | status `agendado` |
  | 4 | **Portão** (`k-chip--portao` + cadeado) | todos os portões que se aplicam aprovaram e falta a decisão do Carlos |
  | 5 | **Em produção** (`k-chip--producao`) | o resto |

  - Exemplo: vídeo agendado com o portão da imagem vencido (a cor foi refeita com o post na fila) = **Bloqueado**.
  - **[PROPOSTA] Publicado nunca some (PI40, 23/10).** A família 3 descreve o vídeo **enquanto ele anda**. Um post que já
    saiu é um fato: na lista de publicados ele é sempre **Publicado** (com o link do canal). Se um portão do vídeo vencer
    depois (cor ou capa refeita para um repost), a linha ganha, **ao lado** do nome, o chip do mapa único com o portão
    ("Vencido · imagem") — nunca no lugar do Publicado. O "Bloqueado" da ordem 1 vale para o vídeo nas fases em que ele
    ainda não saiu.
  - **[PROPOSTA] Com o menu "Produção de conteúdo" (23/10), a fase substitui o chip da família 3** — o vídeo está numa das
    5 fases, e cada fase mostra os portões que importam nela. Onde cada estado aparece e o que mostra a coluna de portão de
    cada fase: **§15.1**.
  - Se o post sai ou não é uma pergunta **por post**, respondida na linha "Portões:" do calendário (§11.12): o legado
    publica sem selo mesmo com o vídeo Bloqueado, porque o publicar.py não confere portão para ele.

### 11.4 Card — `k-card` · prévia `card.html`
Contêiner base de todo o painel.
- Fundo `surface`, borda **1px `line`**, raio `radius-card` (12px), sombra `shadow-card`.
- Clicável: `is-interactive` — o hover troca a borda para `line-strong` e a sombra para `shadow-hover`. Sem escala, sem
  mudar o fundo. O card clicável inteiro é um link (`<a>`), com foco visível.
- Padding padrão `space-24` (`k-pad`); cards densos 16–20px.
- Cabeçalho: `k-card-head` com `k-card-title` (15px/600) à esquerda e ação ou caption à direita.
- **Nunca:** borda colorida à esquerda, degradê, sombra forte, card dentro de card.

### 11.5 KPI — `k-card k-kpi` · prévia `kpi.html`
Três linhas:
1. Rótulo em `caption` (`k-cap`), `ink-2`.
2. Valor em `metric-xl` (40px/700, tabular) — `k-kpi-value`. Unidades (K, M, US$) em `<small>` a 18px `ink-2`
   (US$ antes do valor: `<small class="k-prefixo">` **[TRANSCRITO]**, 4px de folga). Custo de IA em US$, sem câmbio (24/10).
3. Rodapé `k-kpi-foot`: delta (`k-delta--up` verde, `--down` vermelho, `--flat` neutro) + contexto (`k-kpi-note`, 12px
   `ink-3` **[TRANSCRITO]**) ou sparkline.
- **A cor do delta segue o significado, não a direção**: custo subindo é `k-delta--down` (vermelho) com a seta ▲.
- Delta acessível: seta `aria-hidden` + palavra para leitor de tela ("▼ 3 a menos"). Período sempre escrito.
- Linha de KPIs: 3 ou 4 cards (span 4 ou 3). Tela estreita: §4.1.
- **Atualização (23/10):** tokens e custo de IA **passaram a ter fonte** — os registros das sessões do Claude Code (§15.3).
  O custo aparece em US$ (§1). Variantes das telas (KPI em linha, KPI com anel ou capa ao lado): §15.2.

### 11.6 Barra lateral — `k-sidebar` · prévia `barra-lateral.html`
Barra fixa de **208px** (`sidebar-width`), fundo `sidebar` (#111111), em toda a altura.
- Topo: logotipo `ivory` a 19px (`k-sidebar-logo`).
- Itens (`k-nav-item`): 34px, ícone 18px + rótulo 13px/500, raio `radius-btn`. Inativo `sidebar-ink-2`; hover
  `sidebar-raised` + `sidebar-ink`.
- **Ativo (`is-active`)**: fundo `sidebar-raised`, texto `sidebar-ink`, **ícone em `accent`** e **ponto laranja de 6px** à
  direita; `aria-current="page"`. **Nunca barra lateral colorida.**
- Contagens opcionais em `k-nav-count` (mono 11px) — com a unidade para leitor de tela ("26 pessoas").
- **Ordem fixa:** Visão geral · Equipe · **Produção de conteúdo** (antes "Vídeos e portões", decisão de 23/10; ícone
  `videos-portoes`) · Calendário · Desempenho · Biblioteca · Tokens e custos. Desde 23/10 **todos os 7 têm tela** (§15).
- "Produção de conteúdo" ocupa duas linhas a 208 px: o item tem `line-height` 15 px e, ativo, 24 px de folga à direita para
  o ponto laranja não encostar no texto (`acrescimos.css`).
- Rodapé (`k-sidebar-foot`): **"@korvu_oficial · Instagram · Facebook"** — como o Carlos desenhou nas telas de 23/10. O dono
  ("Carlos · Proprietário") passou para a barra do app, no alto à direita (§15.2). Não há login nem troca de usuário.
- `k-sidebar-label` (rótulo de grupo, 10px a 80%) existe no CSS mas mede 4,37:1 — não usar até o Carlos decidir.
- **[PROPOSTA] Item sem página** (regra que fica para o futuro): continua no lugar desenhado, mas **não é link**
  (`<span class="k-nav-item" aria-disabled="true">`), apagado com a opacidade do botão desativado da fonte (.45), sem
  contagem, sem acender no hover, com "ainda sem página" para leitor de tela. Em 23/10 (tarde) nenhum item está nesse caso.
- O bloco "Orçamento IA" da prancha **não entra**: o custo agora existe (tela Tokens e custos), mas orçamento (um teto
  definido pelo Carlos) não existe em lugar nenhum.
- Tela estreita: barra de topo + menu (§4.1, `.k-topbar`, `.k-menu-btn`).

### 11.7 Avatar — `k-avatar` · prévia `avatar.html`
- Quadrado 1:1 com iniciais (2 letras) em `ink-2` sobre `surface-sunken`, borda 1px `line`; tamanho por `--s`
  (padrão 40px, raio 8). Cards de equipe **56px raio 10**; listas **40px raio 8**; pilhas **28px redondas** (`is-round`,
  `k-avatar-stack`, sobreposição de 8px com anel `surface`).
- **Retrato = foto** (§10): `<img>` dentro do `k-avatar` (object-fit cover); sem foto, as iniciais.
- Presença: `k-presence` (ponto verde de 10px) **só para agentes trabalhando agora** — com texto para leitor de tela.
  Hoje nenhum dado diz quem está trabalhando.

### 11.8 Card de pessoa (TeamMemberCard) — `k-card k-member` **[TRANSCRITO]** · prévia `pessoa.html`
Card de agente da equipe, usado em **Equipe** e em painéis laterais.
- O consumidor fornece: retrato (foto; sem foto, iniciais), nome, função · departamento, o modelo **que rodou**, **com a
  versão** ("Sonnet 5.5"/"Opus 5.5"; "ainda não rodou" sem registro) e três métricas dos últimos 30 dias: **tokens, custo
  (US$) e tarefas** — dos registros do
  Claude Code (§15.3). "Vídeos ativos", do desenho original, saiu: não tem fonte.
- `k-card is-interactive`, padding 16px, gap 14px, avatar 56px raio 10px.
- Nome 15px (`k-member-name`), chip do modelo ao lado; função · departamento em 12px `ink-2` (`k-member-role`); métricas
  em 20px/700 tabular (`k-member-stat-value`) com rótulo `ink-3` (`k-member-stat-label`), gap 22px.
- Em grade: 3 por linha (span 4) na página Equipe. Tela estreita: §4.1.
- **Atualização (23/10):** tokens, custo (US$) e tarefas por pessoa **têm fonte** (registros do Claude Code, §15.3). Quem
  não rodou nos 30 dias mostra "—" e "não rodou". "Vídeos ativos" continua sem fonte. Nas telas de 23/10 o cartão de
  pessoa com foto grande é o `k-agente` e a linha de departamento é o `k-pessoa-linha` (§15.2).
- **[DIVERGÊNCIA]** o README diz "nome em body-strong" (600); a prévia desenha `<b>` (700). Ficou o desenho (700).

### 11.9 Linha de vídeo (VideoRow) — `k-table` · `k-thumb` · `k-video` **[TRANSCRITO]** · prévia `linha-de-video.html`
Linha de vídeo dentro de `k-table` num `k-card`. Altura `row-height` (56px).
- Colunas recomendadas: Vídeo (miniatura 56×36 + título + formato · duração) · Responsável · Etapa · Progresso (`k-steps`)
  · Publicação · Estado (`k-chip` pelo mapa do estado do vídeo, §11.3).
- Cabeçalhos em `caption`; divisórias `line`; hover `surface-hover`.
- Miniatura: frame real do vídeo quando existe; senão `k-thumb` neutro com `play`. As variantes `is-dark` e `is-accent`
  existem no CSS mas a fonte não diz quando usar — usar o neutro até o Carlos dizer.
- **Títulos longos cortam com reticências — nunca quebram em várias linhas** (`k-video-title`).
- **[DIVERGÊNCIA]** o README diz "título body-strong" (15px); a prévia desenha 600 no tamanho da célula (13px). Ficou o desenho.
- Hoje **não há dado de "Responsável"** nem um campo de título limpo (ver `handoff.md`); a prévia mostra Vídeo · Etapa ·
  Progresso · Publicação · Estado.
- Tela estreita: a tabela rola dentro do card (`.k-table-wrap`, §4.1).

### 11.10 Progresso — `k-progress` · `k-steps` · prévia `progresso.html`
- **Barra** (`k-progress`): 6px, trilho `surface-sunken`, preenchimento `accent`; `is-done` → `positive`; `is-blocked` →
  `danger`. **Sempre acompanhada do número** ("3 de 12 · 25%").
- **Etapas** (`k-steps`): um segmento por etapa de produção — Roteiro · Gravação · Edição · Revisão · Publicar. Concluída
  `on` (`ink`), atual `now` (`accent`), bloqueada `blocked` (`danger`), futura vazia. Rótulos opcionais em
  `k-steps-labels` **[TRANSCRITO]** (caption; a atual em `accent-ink`).
- Acessível: `role="img"` + `aria-label="Etapa 4 de 5: Revisão"` — as etapas futuras ficam a 1,13:1 do card.
- **[PROPOSTA] Os 12 estados do projeto nas 5 etapas:** roteiro → Roteiro; gravação → Gravação; edição e EDL aprovada →
  Edição; revisão, cor, legendas, capa e QA → Revisão; pronto e agendado → Publicar (atual); publicado → todas feitas.

### 11.11 Portão de aprovação (ApprovalGate) — `k-gate` · `k-check` · prévia `portao.html`
Ponto onde um vídeo **para** até o Carlos decidir.
- O consumidor fornece: número do portão / total, nome da etapa, título do vídeo, critérios (feitos/pendentes). **Sem ações** (24/10: o painel só informa).
- Cadeado `lock` em `accent-ink` sobre `accent-soft` (`k-gate-icon`); chip `k-chip--portao` com o estado
  (Aguarda · Aprovado · Ajustes) — **[PROPOSTA]** na prática só "Aguarda" ou "Ajustes" (§11.3, família 2).
- Critérios com `k-check`; os feitos ficam **riscados em `ink-2`**.
- ~~Ações "Aprovar e agendar" e "Pedir ajustes"~~ — **saíram em 24/10**: no modo Decisão, a frase "Tudo aprovado: falta a
  sua decisão — agendar ou pedir ajustes é no Claude Code." (`k-fonte`).
- **[PROPOSTA] Dois modos, um componente:**
  - **Decisão** — só quando **todos os portões que se aplicam ao vídeo aprovaram** e o vídeo ainda não está agendado nem
    publicado. Leva o chip da **decisão do Carlos** (§11.3, família 2: Aguarda ou Ajustes) e a frase da decisão, sem botões.
  - **Portões do vídeo** — em qualquer outro caso. **Só leitura, sem ações**, com o chip do **estado do vídeo** (§11.3,
    família 3) no cabeçalho. **Vídeo agendado ou publicado nunca fica no modo Decisão**.
- **[PROPOSTA]** Quando os critérios são os portões, cada um mostra o estado pelo **mapa único** (§11.3, família 1):
  `<small class="k-chip …">` à direita do critério (`.k-check > .k-chip`). Feito = `aprovado`. A conta "N de 4" é só
  dessas quatro linhas (os portões do vídeo).
- **[PROPOSTA]** No modo Portões do vídeo, abaixo, **"Posts na fila"** — um por post do vídeo, fora da conta, sem caixa —
  com a mesma regra da linha "Portões:" do calendário (§11.12): o pior estado do que o publicar.py confere, legado vence.
- Partes **[TRANSCRITO]**: `k-gate-head`, `k-gate-step` (10px), `k-gate-title` (15px/700, reticências), `k-gate-checks`,
  `k-gate-actions`.
- **[DIVERGÊNCIA]** a prévia da fonte mostra o botão ativo com um critério aberto; vale a regra do README (desativado).
- **[DIVERGÊNCIA]** o rótulo "Portão N de M" é 10px na prévia (o caption é 11px). Ficou 10px; proposta: 11px.
- Os critérios são **estado** (quem marca é o portão): lista em que a caixa é `aria-hidden` e o estado vem **escrito no
  chip** do mapa único (o leitor de tela lê "Pauta, Ainda não rodou"). Se um dia o Carlos marcar, vira checkbox de verdade.
  Critérios além dos portões **não estão no banco** (ver `handoff.md`).

### 11.12 Evento do calendário — `k-event` · prévia `calendario.html`
- `k-event`: raio 6px, `surface`, borda `line`, 12px/16px.
- **Marca de canal**: barra de 3px à esquerda — Instagram `k-event--ig` (`accent`), Facebook `k-event--fb` (`chart-5`),
  multicanal sem modificador (`ink`) — **e o nome do canal escrito** na segunda linha.
- Portões no calendário: `k-event--gate` (fundo `accent-soft`, texto `accent-ink`, sem barra).
- Conteúdo: título (12px/600) + hora · canal (12px `ink-2`), **uma linha cada, com reticências**.
- **[PROPOSTA] Linha "Portões:" em todos os posts da fila** (nunca só em alguns), no `.k-event-portao`. Ela responde **se o
  post sai**, com o que o `publicar.py` confere na hora de publicar (`scripts/publicar.py` → `portoes.conferir_pacote`):
  1. **Legado vence.** Pacote da lista congelada sem selo: `conferir_pacote` devolve nenhum erro antes de olhar qualquer
     portão. Mostra **"Legado · sem selo"**.
  2. Senão, o `publicar.py` exige o **portão da publicação** aprovado sobre a pasta da fila **e** a origem válida
     (`exigir(origem)`: roteiro, imagem e corte do vídeo aprovados; pauta aprovada ou "não se aplica").
  3. Mostra o **pior** desses estados, com o chip do mapa único, nesta ordem: Escalado, Bloqueado, Vencido, Ainda não rodou,
     Não se aplica. Tudo aprovado: **"Aprovado"**.
  4. Se algo segura o post, depois do chip: **"&lt;portão&gt; · não sai"**, com "não sai" em `danger`
     (ex.: `Vencido` imagem · não sai). Com mais de um portão no mesmo estado: "imagem e mais 1".
  - O que o banco não sabe (arquivo da fila trocado depois do selo) só aparece no log do `publicar.py`.
  - O `k-event--gate` fica para um portão marcado num dia. A fila de 23/10 tem 5 posts, todos legado: os 5 mostram
    "Legado · sem selo". Os casos "não sai" estão na prévia como exemplo.
  - **PI38 corrigido (23/10):** `.k-event .k-segura` em `acrescimos.css` — o "não sai" é `danger` também dentro do evento.
  - **[TRANSCRITO] Variante do mês** (tela Calendário, §15.2): evento com capa (`k-event--mes`) e linha de portões compacta
    (`.k-event-portao.is-compacto`), em que o cadeado faz o papel da palavra "Portões:" (que fica em `.k-sr-only`).
  - **A marca de canal segue esta regra também nas telas:** o artboard do Calendário pintou todos os eventos de laranja; na
    maquete, Instagram = `accent`, Instagram + Facebook = `ink`, Facebook = `chart-5`, com a legenda.
- Grade de dias `k-cal` / `k-cal-day` **[TRANSCRITO]** (4 colunas, 6px; rótulo do dia 10,5px caps — **[DIVERGÊNCIA]**
  abaixo do caption; proposta 11px).
- A página Calendário não existe ainda; o componente já serve para a fila de publicação (dados reais na prévia).

### 11.13 Notificação — `k-note` · prévia `notificacao.html`
Em lista dentro de `k-card` (divisória `line`) ou flutuante com `shadow-pop`.
- Ícone 32px em quadrado `radius-btn`: alerta `k-note--alert` (danger), portão `k-note--gate` (accent), sucesso
  `k-note--ok` (positive), informação neutra sem modificador.
- Título 13px/600 (`k-note-title`) + corpo 13px `ink-2` (`k-note-body`) com contexto e tempo.
- Não lida: ponto `k-unread` laranja à direita **+ "não lida" para leitor de tela**.

### 11.14 Busca — `k-search` · prévia `busca.html`
Campo de busca global, 36px, raio 8px, borda `line-strong`.
- Placeholder em `ink-3`: **"Buscar vídeos, agentes…"**. Atalho `⌘K` em `k-kbd`.
- Foco: borda `ink` + halo de 3px `accent-soft`.
- Fica no topo da área principal, à direita do h1 (tela estreita: linha própria, largura toda).
- O campo precisa de nome acessível (`aria-label` ou `<label>`).

### 11.15 Dropdown — `k-select` · `k-menu` · prévia `dropdown.html`
Gatilho `k-select` (36px) + menu `k-menu` flutuante (`shadow-pop`, raio 12px), 4px abaixo.
- Itens `k-menu-item` 32px; hover `surface-sunken`; selecionado em 600 com `check` em `accent-ink` (`k-tick`).
- Gatilho aberto: borda `ink`. Separador `k-menu-sep` para opções especiais (Personalizado…).
- Teclado: setas movem, Enter escolhe, Esc fecha e devolve o foco ao gatilho.
- As opções do período têm de bater com as janelas que os dados têm (perfil: 28 dias da Meta).

### 11.16 Dica (tooltip) — `k-tooltip` · prévia `dica.html`
Dica escura: fundo `sidebar`, texto `sidebar-ink`, linha secundária `sidebar-ink-2`, raio 6px, seta de 8px.
- Para valores exatos em gráficos e para explicar ícones. Aparece **após 300ms de hover ou foco**; no máximo 2 linhas.
- **[PROPOSTA] Nunca sai da janela**: aberta, `.k-tooltip.is-floating` (position fixed, presa a 8px das bordas, largura
  máxima `min(22rem, 100vw − 16px)`, seta pelo `--seta-x`); fecha ao sair, ao tocar fora e com Esc.
- Complementa, nunca é o único jeito de ler um valor.

### 11.17 Estado vazio — `k-empty` · prévia `vazio.html`
Contorno tracejado `line-strong`, sem fundo, centrado.
- Ícone 22px num quadrado `surface` de 48px; título 15px/600; **uma frase em `ink-2` que diz o que vai aparecer aqui**.
- Ação opcional `k-btn-secondary k-btn-sm`. **Nunca ilustração nem emoji.**

### 11.18 Gráficos — `k-chart` · prévia `graficos.html`
Gráficos em SVG desenhados com `chart-1`…`chart-5`.

| Forma | Uso no painel |
|---|---|
| Linha / área | Evolução no tempo (visualizações, alcance, seguidores). Série em foco `chart-1` 2px + área a 14%; comparação `chart-2` tracejada 1,5px. |
| Barras horizontais | Ranking por categoria. Barra em destaque `chart-1`, as demais `chart-2`, trilho `surface-sunken`, valor à direita (`k-bar-row` **[TRANSCRITO]**). |
| Rosca (donut) | Partes de um todo com **≤ 4 fatias**. Espessura 14px, total no centro, 2px de folga entre fatias. |
| Sparkline | Tendência dentro de KPI, 120×28, sem eixos, ponto final marcado. |

- Grade `chart-grid` 1px, eixos em 10px `ink-2`, sem bordas de eixo. **Um eixo só** (nunca dois).
- Ordem das cores fixa: laranja → preto → taupe → areia → ardósia. Verde/vermelho nunca como série.
- **Legenda sempre com 2+ séries** (`k-legend`), rótulo direto só no fim da linha, **texto nunca na cor da série**.
- Valor exato no `k-tooltip`, por hover **e** por foco.
- **[PROPOSTA] Tabela gêmea:** `<details class="k-details"><summary class="k-btn k-btn-ghost k-btn-sm">Ver os números</summary>`
  com a `k-table` — todo gráfico tem.
- `chart-3` e `chart-4` ficam abaixo de 3:1 contra o card: só com legenda + rótulo + tabela (`contraste.md`).
- Desenhe na **largura real** do contêiner: `preserveAspectRatio="none"` (usado na prévia da fonte) entorta o texto dos eixos.
- Leitura marcada como `suspeito` no banco nunca entra em gráfico nem média.

### 11.19 Ícones — `Korvu.icon()` · prévia `icones.html`
Ver §8. Em código: `Korvu.icon("lock", 16)` ou `<span data-icon="lock" data-size="16"></span>`.

---

## 12. Acréscimos (o que o artefato não trouxe) — `acrescimos.css`

| Peça | Classes | Prévia | Origem |
|---|---|---|---|
| Escala tipográfica em classes | `.k-display` … `.k-metric-l` | `fundamentos.html` | [TOKEN] |
| Só para leitor de tela | `.k-sr-only` | — | [TOKEN] |
| Casca e grade | `.k-shell`, `.k-topbar`, `.k-menu-btn`, `.k-main`, `.k-page-head`, `.k-page-tools`, `.k-section`, `.k-section-head`, `.k-grid`, `.k-span-*`, `.k-grid--tiles`, `.k-skip` | `casca.html`, `casca-menu.html` | [PROPOSTA] |
| Item de menu sem página | `.k-nav-item[aria-disabled="true"]` | `barra-lateral.html` | [PROPOSTA] |
| Link no meio do texto | `.k-link` (tinta + sublinhado `line-strong`; nunca laranja sobre fundo claro) | `graficos.html` | [PROPOSTA] |
| Comando no texto | `.k-code` (Geist Mono 12px sobre `surface-sunken`) | `erro.html` | [PROPOSTA] |
| Tabela que rola dentro do card | `.k-table-wrap` (`--table-min`) | `linha-de-video.html` | [PROPOSTA] |
| Tabela gêmea do gráfico | `.k-details` | `graficos.html` | [PROPOSTA] |
| Dica presa à janela | `.k-tooltip.is-floating` | `dica.html` | [PROPOSTA] |
| Partes inline da fonte | `.k-video*`, `.k-gate-*`, `.k-member*`, `.k-bar-*`, `.k-cal*`, `.k-kpi-note`, `.k-prefixo`, `.k-steps-labels` | prévias de cada um | [TRANSCRITO] |
| Peças das telas de 23/10 | §15.2 (barra do app, filtro, segmentado, fases, canal, palavra, capa, publicação, agente, pessoa, direção, números lado a lado, KPI em linha/com peça, barras finas, colunas, ranking, medidor, mês, semana, vaga, gravação, chave-valor, atalho, destaque, material, uso, pedido) | `telas/*.html` | [TRANSCRITO] / [PROPOSTA] |
| Correções de base pedidas pelas telas | `[hidden]{display:none !important}`, `a.k-btn` sem sublinhado, `.k-delta` sem quebra, `.k-grid > *{min-width:0}`, `.k-table-wrap{position:relative}` | `telas/*.html` | [PROPOSTA] |

### 12.1 Carregando — `.k-skel` **[PROPOSTA]** · prévia `carregando.html`
- Esqueleto em **`surface-sunken`** no **lugar exato** do conteúdo, dentro da casca (a barra lateral não pisca): blocos
  `k-skel-h1`, `k-skel-cap`, `k-skel-line`, `k-skel-title`, `k-skel-metric`, `k-skel-chip`, `k-skel-avatar`,
  `k-skel-thumb`, dentro dos mesmos `k-card` / `k-kpi` / `k-table` da página.
- **Sem animação chamativa**: nada de brilho correndo; só uma respiração lenta de opacidade (1,6s, até .55), e **nenhuma**
  com `prefers-reduced-motion: reduce`.
- Blocos `aria-hidden`; o contêiner com `role="status"` + `.k-sr-only` "Carregando os dados do painel…".
- Ao recarregar dados que já estão na tela, **não** volte ao esqueleto: mantenha o conteúdo com `.is-atualizando`
  (opacidade .6) até chegar o novo. Nunca um spinner de página inteira.

### 12.2 Erro — `.k-state--erro` e `k-note--alert` **[PROPOSTA]** · prévia `erro.html`
- **Erro de página** (`app/error.tsx`, dentro da casca): `.k-state.k-state--erro` — ícone `alert` no quadrado de 48px em
  `danger` sobre `danger-soft` (o mesmo par do `k-note--alert`), `h1` "Não deu para ler os dados", frase do porquê
  (`.k-state-text`), card "Como resolver" com passos numerados (`.k-passos`) e os comandos em `.k-code`, ação primária
  **"Tentar de novo"** (`.k-state-actions`), e o código técnico em `k-mono k-muted`. `role="alert"`.
- **Erro de bloco** (uma parte da página falhou): `k-card` > `k-note k-note--alert` com título "Não deu para carregar esta
  parte", corpo dizendo que o resto continua valendo, e `k-btn-secondary k-btn-sm` "Tentar de novo" em `.k-note-actions`.
- Os comandos são as constantes `COMO_LIGAR` e `COMO_SINCRONIZAR` de `painel/web/src/lib/db.ts` (não reescrever à mão).

### 12.3 Não encontrado — `.k-state` **[PROPOSTA]** · prévia `nao-encontrado.html`
- `app/not-found.tsx`, dentro da casca: ícone `search` no quadrado de 48px (`.k-state-icon`, como o do estado vazio),
  `h1` "Página não encontrada", "Este endereço não existe no painel. Se era a ficha de alguém da equipe, a pessoa pode ter
  saído ou mudado de nome.", ações **"Ir para a visão geral"** (primário) e "Ver a equipe" (fantasma).

### 12.4 Vazio
Já existe na fonte (`k-empty`, §11.17).

### 12.5 Estado do banco e rodapé **[PROPOSTA]** (só composição de peças que já existem)
O painel de hoje mostra no cabeçalho se o banco está sincronizado, fora do ar ou nunca sincronizado; o sistema não tem
lugar para isso. Proposta:
- **Tudo certo:** uma linha discreta no rodapé da área principal, 12px `ink-2`, separada por 1px `line`:
  "@korvu_oficial · sincronizado em 23 out, 14:22 · o painel só lê os arquivos do projeto".
- **Banco fora do ar ou nunca sincronizado:** `k-card` > `k-note k-note--alert` **no topo da página, antes do h1**, com o
  comando em `.k-code` (as constantes de `db.ts`). Some quando o banco volta.

---

## 13. Pendências — vão ao Carlos (pelo agente principal)

1. ~~**Avatar**~~ — **resolvido em 23/10**: retrato = foto realista; sem foto, iniciais (§10). Fica a pergunta: **quer
   foto para as 16 pessoas que ainda estão em iniciais?**
2. **Contraste** (`contraste.md`): ~~`line-strong` → #928874; anel de foco em `accent-ink` nas superfícies claras~~ —
   **aprovados em 23/10** (§2). Continuam com ele: laranja como texto só na barra lateral; `chart-3` → #968D7B; `chart-4` só para "Outros" rotulado; tirar o `opacity:.8` do
   `k-sidebar-label`; contorno nas etapas futuras do `k-steps`.
3. ~~**Itens de menu sem página**~~ — desde 23/10 os 7 itens têm tela.
4. **375 px** (§4.1), **estados** carregando/erro/não encontrado (§12), **os três mapas de estado** (portão, decisão do Carlos, vídeo — §11.3) e os **dois modos do card do portão** (§11.11),
   **12 estados → 5 etapas** (§11.10) e **quando compactar números** (§1).
5. **Divergências dentro da fonte**: peso do nome no card de pessoa (600 × 700) e do título da linha de vídeo (15 × 13px);
   botão "Aprovar" ativo com critério aberto na prévia; textos de 10–10,5px; variantes `is-dark`/`is-accent` da miniatura
   sem regra; `display` −0,04em na prancha.
6. **Sem fonte de dados hoje** (trabalho do engenheiro-backend, se o Carlos quiser essas partes): presença ("ativo agora"),
   responsável por vídeo, critérios por portão, título curto do vídeo, curva diária do Instagram; na Biblioteca, os estilos (looks, capas,
   legenda, fontes, animações) ainda são arquivos de configuração (`telas/biblioteca.md`). **Tokens e custos passaram a ter fonte** (registros do Claude Code) e precisam ser sincronizados (§15.3).
7. **Das telas de 23/10** (§15): os blocos que a 1440 descem para baixo do
   bloco principal (§15.4); o anel no lugar da rosca de
   2 fatias em "fora da bolha"; a escala de 0–100 % no "% assistido"; contar como "Referências" os 105 arquivos de
   `painel/referencias/` (que são os desenhos do próprio painel) — tudo em `telas/*.md`, "Do artboard para a maquete".

## 14. Arquivos desta pasta

| Arquivo | O que é |
|---|---|
| `design-system.md` | este livro |
| `tokens.json` | os tokens para importar (valor, nome da variável CSS e uso de cada um) |
| `tokens.css` | as variáveis CSS com os nomes que `componentes.css` usa + `@font-face` |
| `componentes.css` | o CSS dos 19 componentes (cópia do `bundle.css`, comentado em PT-BR) |
| `acrescimos.css` | transcrições e propostas (§12) |
| `korvu.js` | `window.Korvu` (cópia do `bundle.js`) — usado pelas prévias |
| `icones/` | 31 SVG `currentColor` + `icones.json`; `navegacao/` = os 7 originais |
| `marca/` | os dois logotipos (cópias exatas) |
| `fontes/` | Geist e Geist Mono variáveis + `OFL.txt` + `LEIA-ME.md` |
| `previas/` | uma prévia por componente e por estado + índice (`index.html`), sem rede |
| `contraste.md` | todos os pares medidos, falhas, mitigação e proposta |
| `dados-2026-10-23.json` | os números reais das prévias e das telas, com a consulta (ou o arquivo) de cada bloco; os blocos `telas_*` são da 2.ª rodada |
| `telas/` | as 7 telas: `<tela>.md` (especificação) + `<tela>.html` (maquete com dados reais), `telas.css` e `telas.js` (só da maquete) e `img/` (cópias de retratos, capas e miniaturas) |
| `icones/telas/` | os 4 ícones que as telas pediram (§8) |
| `verificacao/` | `fidelidade.py` (confere contra a fonte) e `contraste.py` (mede os pares) |
| `handoff.md` | o que o engenheiro-frontend faz com tudo isso |
| `README.md` | por onde começar |

---

## 15. As telas de 23/10 (2.ª rodada)

O Carlos desenhou as 7 telas no Claude Design (artboards de 1920×1080, fonte exata em
`painel/referencias/claude-design/telas-2026-10-23/`). Cada uma está em `telas/` como especificação (`.md`) e maquete
(`.html`, dados reais de `dados-2026-10-23.json`, 1440 fluido e 375 px). Fotografar:
`bash painel/capturar.sh painel/trabalho/designer --arquivo painel/design/telas/<tela>.html`.

| Tela | Arquivos | O Carlos abre para… |
|---|---|---|
| Visão geral | `telas/visao-geral.*` | saber como está o estúdio hoje: perfil, o que sai nos próximos dias, desempenho, consumo de IA e a equipe |
| Equipe | `telas/equipe.*` | ver quem é quem por departamento, com que modelo, quem é portão e quanto cada um consumiu |
| Produção de conteúdo | `telas/producao.*` | ver em que fase está cada conteúdo, do roteiro ao publicado, e o que precisa de atenção |
| Calendário | `telas/calendario.*` | ver o que sai em cada dia, as vagas livres, as gravações previstas e se cada post da fila sai |
| Desempenho | `telas/desempenho.*` | ver o que cresce, quem os vídeos alcançam e qual conteúdo funciona |
| Biblioteca | `telas/biblioteca.*` | escolher o estilo do próximo vídeo (looks, capas, legendas, fontes, animações) e ver o espaço e o sistema — **refeita em 24/10** como acervo de estilos |
| Tokens e custos | `telas/tokens-e-custos.*` | ver quanto a IA consome, onde, quem e quanto custa (US$, preço de tabela) |

Cada maquete tem, depois da tela, uma faixa tracejada "fora da tela" com os **três estados de cada bloco** (vazio,
carregando, erro) e as vistas que só aparecem ao tocar (outras fases, semana, popovers). O que não tem fonte leva o selo
**`exemplo`** (`.tl-ex`, só da maquete); no app, esses blocos seguem o que o `.md` da tela manda (esconder ou vazio).

### 15.1 Produção de conteúdo — as 5 fases e o mapa de estados **[PROPOSTA]**

Decisão do Carlos (23/10): o menu é **Produção de conteúdo**, separado pela fase real; **roteiro só vira vídeo depois de
gravado**; **portão é detalhe da fase, não nome de menu**; vale para Reels, Stories e Carrossel. A fase é decidida pela
**pasta onde o trabalho está** (é o que o pipeline move), lida nesta ordem:

| Fase | Unidade da linha | Está aqui quando | Coluna de portão | Estado do vídeo (família 3) |
|---|---|---|---|---|
| **Roteiros** | vídeo (`videos/<slug>`) | tem `roteiro.json` e **nenhum arquivo** em `brutos/principal/` | **Portão do roteiro**: chip do mapa único (família 1) do portão `roteiro`; a dica mostra também a `pauta` | a fase é o estado ("Em produção"); se um portão do vídeo estiver bloqueado, escalado ou vencido, o chip vermelho aparece na coluna e o aviso entra em "Precisam de atenção" |
| **Gravados** | vídeo | tem arquivo em `brutos/principal/` e **ainda não tem pacote** (`05-render-pronto/`, `06-publicar/`, `07-publicados/`) | **Portão da imagem** e **Portão do corte**: um chip da família 1 cada | idem |
| **Prontos** | pacote (`05-render-pronto/<slug>`) | pacote com QA PASS que **não entrou na fila** | **Portões do vídeo**: o **pior** dos 4 portões do vídeo (pauta só se aplicar), com o chip da família 1 e o nome ("Ainda não rodou · roteiro e mais 2"); tudo aprovado = "Aprovado" (= família 3 "Portão": falta o Carlos agendar) | se um portão segurar, o vídeo não sai daqui; "Bloqueado" só vem de portão |
| **Agendados** | post (`06-publicar/<slug>`) | está na fila com data | **Portões**: a linha "Portões:" do §11.12, igual ao calendário — **legado sem selo vence** ("Legado · sem selo"); senão o portão da publicação **e** `exigir(origem)`, o pior estado e "‹portão› · não sai" em `danger` | coluna **Estado** = família 3 em ordem: **Bloqueado** (algum portão do vídeo de origem bloqueado, escalado ou vencido) vem **antes** de **Agendado** |
| **Publicados** | post (`07-publicados/<slug>`) | saiu | sem coluna; se um portão do vídeo vencer depois, o chip vai **ao lado** do nome (PI40, §11.3) | sempre **Publicado** (é um fato), com o link de cada canal |

**Onde cada estado aparece**

| Estado (família 1) | Roteiros | Gravados | Prontos | Agendados | Publicados |
|---|---|---|---|---|---|
| Aprovado | coluna | colunas | "Portões do vídeo" | "Portões" | — |
| Ainda não rodou | coluna (hoje os 7) | colunas | "Portões do vídeo" (hoje o ChatGPT contexto) | "Portões", seguido de "‹portão› · não sai" | — |
| Bloqueado · Escalado · Vencido | coluna (vermelho) + aviso | colunas + aviso | "Portões do vídeo" + aviso | "Portões" + "· não sai" + Estado **Bloqueado** | ao lado do nome, sem tirar o Publicado |
| Não se aplica | dica (pauta) | coluna | dentro do pior (só se for o pior) | dentro do pior | — |
| **Legado · sem selo** | — | — | — | "Portões" (hoje os 5); o Estado continua "Agendado" | — |

**"Não sai" tem duas origens, e a tela diz qual:**
- **Um portão segura o post** (Agendados, calendário): "‹portão› · não sai", com o chip vermelho do mapa único — é o que o
  `publicar.py` faria na hora de publicar.
- **Uma trava escrita à mão** (Prontos): o **ChatGPT contexto** é um teste de cor ("não publicar", `_controle/CONTINUAR.md`).
  A linha mostra **"Teste de cor · não sai"** na coluna Observação, com "não sai" em `danger`, e **sem** a ação de agendar.
  **Não é "Bloqueado"** (Bloqueado é só de portão). Hoje isso vem de um texto do CONTINUAR.md: o banco precisa de um campo
  (ver `handoff.md` §8, `nao_publicar` no `status.json`/`pacote.json`).
- **Legado nunca é "não sai"**: o post legado sem selo publica sem olhar portão. Ele aparece como "Legado · sem selo", em
  cinza, em Agendados, no calendário e no resumo "Portões" (`Publicação: 5 legado · sem selo`).

**Dependências que são do backend (só registradas aqui):** a linha "Portões" de Agendados precisa da **origem** e do
**selo** de cada post na fila (**PI39**: `fila.origem`, `fila.selado`); a fase precisa saber se há gravação
(`brutos/principal/`) e se há pacote; os publicados precisam entrar no banco pelo `post.json` (hoje só entram com o
`metricas.json`, e o Livro ChatGPT A, publicado em 22/10, ainda não está na tabela `publicacoes`). Ver `handoff.md` §8.

**"Precisam de atenção"** (também é a lista do sino, §15.2): calculada dos dados, um aviso por regra que vale hoje —
roteiros esperando gravação (com o mais antigo e o próximo), pronto que não sai (trava manual), portão do roteiro que ainda
não rodou, e qualquer portão bloqueado, escalado ou vencido (vermelho). Sem "não lida": o painel não guarda o que você viu.

### 15.2 Componentes novos — `acrescimos.css`

Todos com só `var(--…)`. Origem: **[TRANSCRITO]** = estava inline no artboard; **[PROPOSTA]** = acréscimo da designer.

| Peça | Classes | Onde | Regras |
|---|---|---|---|
| Barra do app **[TRANSCRITO]** | `.k-area`, `.k-appbar`, `.k-appbar-fim`, `.k-appbar-sep`, `.k-avisos` (+`.tem-aviso`), `.k-dono` | todas | 64 px, borda `line` embaixo. Busca global (`k-search`, até 440 px, ⌘K), sino de avisos (botão fantasma só-ícone, `aria-label="Avisos: N"`, ponto laranja quando há aviso) e o dono "Carlos · Proprietário" — **sem menu** (não há conta nem login; o artboard tinha uma seta de menu). Abaixo de 1024 px some: o sino vai para a barra de topo escura (`.k-topbar-fim`) e a busca para o alto do menu aberto |
| Avisos (popover do sino) **[PROPOSTA]** | `k-menu` + `k-note` (`--gate`, `--alert`) + `.k-note-actions` | todas | a mesma lista de "Precisam de atenção" (§15.1); fecha com Esc e ao tocar fora |
| Topo de página com subtítulo **[TRANSCRITO]** | `.k-page-lead`, `.k-page-meta`, `.k-main.is-painel` | todas | subtítulo 15/22 `ink-2`; meta 13 px `ink-3` com ícone (data, período, fonte). `is-painel`: 32 px entre seções (artboard 28; o livro dizia 48 — **[PROPOSTA]**, telas de painel) |
| Filtro em pílula **[TRANSCRITO]** | `.k-filtros`, `.k-filtro` (`aria-pressed`), `.k-filtro-n` | Visão geral, Equipe, Produção, Biblioteca | 30 px (36 px abaixo de 768); escolhido = `ink` com texto `bg`; a contagem em mono **sem opacidade** (o artboard usava .72, que derruba o contraste). Quebra de linha, nunca rolagem lateral |
| Controle segmentado **[TRANSCRITO]** | `.k-seg` (+`.is-largo`, `.is-alto`) | Público, Mês/Semana, Tokens/Custo, Gerentes/Ranking | trilho `surface-sunken`; escolhido `surface` + `shadow-card`; botões com `aria-pressed`; troca a vista no mesmo bloco |
| Fases **[TRANSCRITO]** | `.k-fases`, `.k-fase` (`aria-pressed`), `.k-fase-n/-d/-m`, `.k-fase-elo` | Produção | cartão-botão que escolhe a tabela; escolhido = borda `ink` + ponto laranja; elo = seta + o que acontece entre as fases ("você grava"). < 1024: 3 por linha sem elo; < 768: lista vertical, número à direita, elo com a seta para baixo |
| Canal **[TRANSCRITO]** | `.k-canais`, `.k-canal`, `.k-canal.is-off`, `a.k-canal` | Produção, Visão geral | Instagram · Facebook · LinkedIn **sempre os três** (decisão de 23/10). Saiu/vai sair = contorno cheio; publicado = link com `link-externo` ("abrir o post", nova aba); não vai/não saiu = tracejado `ink-3`. O estado também vai por texto para leitor de tela |
| Palavra-chave **[TRANSCRITO]** | `.k-palavra` | Produção | mono 11 px em `surface-sunken`; sem palavra = "—" |
| Chip pequeno e modo **[TRANSCRITO]** | `.k-chip.is-sm`, `.k-chip--modo` | tabelas, cartões | 20 px. Modo de publicação: **Normal** = `k-chip--agendado no-dot`; **Trial Reel** = `k-chip--modo` (contorno, sem mono — o artboard usava o chip de modelo, que é para modelo de IA) |
| Capa 9:16 **[TRANSCRITO]** | `.k-capa` + `--xs` (18×32) `--sm` (24×42) padrão (27×48) `--md` (36×64) `--lg` (58×103) `--doc` (roteiro) | todas | a capa real (`capa/capa.png`); sem capa, `surface-sunken` com `play`; roteiro (ainda sem vídeo) = ícone `documento`. Título + slug: `.k-video-title` + `.k-video-slug` |
| Publicação **[TRANSCRITO]** | `.k-posts`, `.k-post`, `.k-post-quando/-rel/-titulo/-onde` | Visão geral | dia em caption `ink` + hora mono; "amanhã/hoje" em `accent-ink`; canais por extenso + chip de modo. 5 por linha a 1440, 1 coluna a 375 |
| Agente com foto **[TRANSCRITO]** | `.k-agentes`, `.k-agente`, `.k-agente-foto`, `.k-agente-nome/-funcao/-depto/-chips`, `.k-agora` | Visão geral | foto 4:3 em cima (1440); ≥ 1600, foto à esquerda como no artboard; < 640, foto à esquerda de 96 px. Sem foto, iniciais no mesmo quadro. O nome **nunca é cortado**: quebra em até 2 linhas (a 1600 a coluna do texto tem ~100 px; o artboard cortava "Vera Ca…"). `.k-agora` = ponto + palavra (Trabalhando agora / Em espera) — **exemplo** até existir presença |
| Pessoa do departamento **[TRANSCRITO]** | `.k-deptos`, `.k-depto`, `.k-depto-head/-soma`, `.k-pessoas`, `.k-pessoa-linha` (+`.is-gerente`, `.k-pessoa-cab`), `.k-pessoa-id/-nome/-funcao/-portao/-num/-seta` | Equipe | linha inteira é link para a ficha (`/equipe/<id>`) — sai o botão "…" do artboard (não havia ação). Gerente: fundo `surface-hover` com contorno `line` — **o contorno laranja do artboard sai** (laranja = ação e foco; parecia o anel de foco). Portão: cadeado + "Portão da pauta" em `accent-ink` na 3.ª linha (o chip "Portão" ao lado do nome cortava o nome a 1440). < 640: avatar à esquerda, números numa 2.ª linha. **3 departamentos por linha só a partir de 1834 px** (`minmax(510px)`: a coluna do nome fica com ≥ 106 px e o nome mais longo mede 104); colunas 32 · nome · 76 · 86 · 64 · 54 · 14 px; só o nome pode cortar (com `title`), função e portão quebram em 2 linhas |
| Direção **[TRANSCRITO]** | `.k-direcao`, `.k-direcao-quem/-texto`, `.k-stats`, `.k-stat`, `.k-stat-v/-r` | Equipe | o Atlas com foto 72, chips do modelo e "Claude principal", o resumo do `equipe.yaml` e números lado a lado (status, tarefas, tokens, custo, modelos que rodou). `.k-stats` também mostra os totais da Visão geral (`.is-solto`) |
| Tokens em destaque **[TRANSCRITO]** | `.k-tokens`, `.k-tokens.is-grande` | Visão geral, Equipe, Tokens | decisão de 23/10 (§1) |
| KPI em linha e KPI com peça **[TRANSCRITO]** | `.k-kpi--linha`, `.k-kpi-linha`, `.k-kpi-lado`, `.k-kpi.has-aside`, `.k-kpi-aside`, `.k-kpi--capa`, `.k-anel` | Visão geral, Equipe, Desempenho, Tokens | valor 36 px com o contexto ao lado (≥ 1600) ou embaixo (< 1600). Peça ao lado: anel (`trilho` `surface-sunken`, `valor` `chart-1`) ou capa; só o rótulo e o valor dão lugar a ela |
| Barras finas **[TRANSCRITO]** | `.k-barras`, `.k-bar-row--fino`, `.k-bar-row--larga` | Visão geral, Desempenho, Tokens | variante do `k-bar-row`: trilho 6 px, valor mono; `--larga` com 3 valores (tokens, custo, %). 1.º em `chart-1`, os outros `chart-2` (destaque, não categoria) |
| Colunas por faixa **[TRANSCRITO]** | `.k-colunas`, `.k-colunas-rot`, `.is-foco` | Calendário | uma série; as 3 faixas mais altas em `chart-1`, o resto `chart-2`; altura relativa; `role="img"` com a frase + tabela gêmea |
| Ranking **[TRANSCRITO]** | `.k-rank-pos` (`.is-1/2/3`), `tr.is-top`, `.k-valor-foco`, `.k-table--denso`, `.k-sub`, `.k-n` | Desempenho, Tokens | posição escrita no círculo (o 1.º em `accent` com texto `on-accent`): nada só por cor |
| Medidor de % **[TRANSCRITO]** | `.k-medidor`, `.k-medidor-trilho` | Desempenho | escala **0–100 %** (o artboard escalava até 25 %, o que aumentava 4× as barras); valor sempre escrito; dica com "tempo médio ÷ duração"; leitura suspeita = "—" |
| Mês **[TRANSCRITO]** | `.k-cal-topo`, `.k-cal-nav`, `.k-cal-legenda`, `.k-mes-cab`, `.k-mes`, `.k-mes-dia` (`.is-fora/.is-passado/.is-hoje/.is-vazio`), `.k-mes-n`, `.k-mes-dl`, `.k-mes-nada`, `.k-event--mes`, `.k-event-linha`, `.k-event-txt`, `.k-event.is-publicado`, `.k-event-portao.is-compacto` | Calendário | 6 semanas a partir do domingo; hoje = número em pílula `accent`; publicado = fundo `surface-hover`; < 768 vira **agenda**: só os dias com algo (e hoje), com o rótulo "Sáb 24 out" |
| Vaga livre **[TRANSCRITO]** (a gravação saiu em 24/10: o calendário mostra só o que está agendado para publicar) | `.k-vaga` (`.k-gravar` sem uso) | Calendário | vaga = tracejado com a hora, só daqui para frente e só em dia de vaga sem post; gravação = câmera + "Gravar · nome", só a partir de hoje (as atrasadas estão em Produção) |
| Semana **[TRANSCRITO]** | `.k-semana`, `.k-semana-dia`, `.k-semana-cab`, `.k-semana-nota`, `.k-semana-vazio`, `.k-event--semana` | Calendário | 7 colunas com a capa grande; nota "hoje" ou "vaga sem post"; < 768 empilha |
| Chave → valor, atalho, destaque, fonte **[TRANSCRITO]** | `.k-kv` (+`--grande`, `.k-kv-t/-v/-n`), `.k-atalho`, `.k-destaque` (+`-t/-m`), `.k-fonte` | várias | `k-destaque` é o achado da análise em `accent-soft` (texto `ink`, meta `accent-ink`); `k-fonte` diz de onde veio o número |
| ~~Material e uso~~ **saiu em 24/10** | `.k-material*`, `.k-materiais`, `.k-uso*`, `.k-busca-grande` removidos do CSS | — | a Biblioteca deixou de guardar material (fecha o PI66) |
| Acervo de estilos **[TRANSCRITO, 24/10]** | `.k-acervo-sec`, `.k-acervo-head`, `.k-acervo-par` (+`-5/-4`), `.k-looks`, `.k-look` (+`.is-uso`, `-foto`), `.k-etiqueta` (`--uso/--alt/--ref/--arq/--tipo`), `.k-sis-modelos`, `.k-sis-modelo` (+`-topo/-pct`), `.k-sis-lista`, `.k-sis`, `.k-estilo-corpo/-nome/-meta/-desc`, `.k-capas-estilos`, `.k-capa-estilo`, `.k-legenda-estilo`, `.k-tipos`, `.k-tipo`, `.k-anims`, `.k-anim` (+`-i/-nome`), `.k-armazem` (+`-n/-leg`), `.k-sistema`, `.k-sistema-sub`, `.k-empilhada` | Biblioteca | canvas aprovado em 24/10. Look em uso = contorno `accent` de 2 px + etiqueta "Em uso" (`accent`/`on-accent`); etiquetas 11 px, nunca `ink-3` sobre `surface-sunken`; nomes quebram em 2 linhas; "Aa" das fontes e a amostra da legenda são imagens (as fontes e as cores são dos Reels, não do painel). Looks 5 → 3 (< 1280) → 2 (< 640); pares 5 + 4 de 9 viram uma coluna abaixo de 1024 |
| ~~Pedido ao Claude Code~~ **saiu em 24/10** | `.k-pedido` fica no CSS sem uso | — | decisão de 24/10: o painel só informa; nenhuma tela tem botão que cria coisa nem "Copiar o pedido" |
| Barra do topo da página **[PROPOSTA, 24/10]** | `.k-page-barra` (+ `h1.k-sr-only`) | todas | no lugar do `k-page-head`: sem título visível; leva busca, data ou período; 16 px abaixo; sem barra, o conteúdo começa nos 24 px da área |
| Modelo que rodou **[PROPOSTA, 24/10]** | `.k-modelo-mix` (chip + `<small>` "92 % · +1", lista no `title` e em `k-sr-only`), `.k-modelo-nada` ("ainda não rodou", 11 px `ink-2`) | Equipe, Visão geral | o modelo dos registros, não o configurado |
| Grade em largura **[PROPOSTA]** | `.k-span-5/7/9`, `.k-xl-3/4/5/6/7/9`, `.k-xxl-3/9` (≥ 1920, Calendário), `.k-lado` (+`--xxl`), `.k-pilha`, `.k-fim-ate-xl` | todas | §15.4 |
| Correções de base **[PROPOSTA]** | `[hidden]{display:none !important}`; `a.k-btn{text-decoration:none}`; `.k-delta{white-space:nowrap}`; `.k-grid > *{min-width:0}`; `.k-table-wrap{position:relative}` | todas | o último impede que o texto `.k-sr-only` (absoluto) de uma célula escape da rolagem da tabela e alargue a página no celular — achado ao fotografar a 375 |

Contraste: as peças novas só usam pares já medidos em `contraste.md` (T02–T11, T13, T16–T19, T21, T24, T27–T29, G08,
G13, G14, G22). Nenhum texto novo abaixo de 11 px (o artboard tinha 10 e 10,5 px em cabeçalhos e chips).

### 15.3 Dados das telas — de onde vem cada número

- **Tokens e custos** (Visão geral, Equipe, Tokens e custos): registros das sessões do Claude Code deste projeto
  (`~/.claude/projects/-Users-teste-Documents-CONTENT-AI/**/*.jsonl` → `message.usage` + `message.model` por resposta;
  subagentes: `subagents/agent-*.meta.json` → `agentType`). Conta: tokens = entrada + cache gravado + saída; custo = preço
  de tabela da API em US$ (cache gravado 1,25× a entrada por 5 min e 2× por 1 h); tarefa = uma sessão (execução) com
  consumo; vídeo = subagente cujo 1.º pedido cita `videos/<slug>`; o Atlas soma a sessão principal e os ajudantes
  (`general-purpose`, `workflow-subagent`, `claude`, `Explore`, `Plan`). Cada resposta vale pela **última linha** do seu
  `message.id` e cai no dia da 1.ª (PD21). **É um retrato com hora de corte** (23/10, 16:02:49, o mesmo do banco):
  37,9 M tokens, **US$ 539,06**. No painel o número vem do banco — **dado novo para o `engenheiro-backend`
  sincronizar** (`handoff.md` §8). ElevenLabs (transcrição e música) fica de fora: sem medição.
- **Câmbio**: saiu em 24/10 (custo em US$).
- **Modelo**: o que **rodou** (registros, `message.model` → rótulo com versão), na Equipe, na Visão geral e no "Rodou em"
  de Tokens e custos (decisão de 24/10). O configurado (`agentes.modelo`) não aparece na tela.
- **Biblioteca** (24/10, acervo de estilos): looks de `00-marca/cor/luts/*.json` + `cor.md`; capas dos pacotes; legenda
  de `00-marca/referencias/legendas/`; fontes de `remotion/src/brand.ts`; animações de `videos/*/animacoes/*/brief.md`;
  armazenamento do banco (`videos.gravacao_bytes_no_mac`, `biblioteca_arquivos.bytes` — só o que está no Mac);
  modelos do consumo. Banco × configuração bloco a bloco: `telas/biblioteca.md`.
- **Desempenho / Visão geral**: os snapshots do perfil (`_controle/perfil/2026-10-16.json` e `2026-10-22.json`); a curva
  diária é **exemplo** (a Meta só dá o total de 28 dias).
- Cada bloco, com a consulta ou o arquivo: `dados-2026-10-23.json` → `telas_*`.

### 15.4 Larguras — o artboard é 1920, a referência é 1440 **[PROPOSTA]**

Os artboards foram desenhados a 1920 px para caber numa tela. O sistema usa **1440 como referência** e é fluido:
- **A partir de 1600 px**, a grade segue o artboard: Produção com o bloco principal em 9 colunas e os cartões
  laterais em 3; Desempenho com países 5 + ranking 7; Tokens e custos com departamento 4 + quem consome 5 + vídeo 3; Visão
  geral com desempenho 6 + público 3 + tokens 3.
- **Abaixo de 1600 px** (1440 incluído), o bloco largo ganha a largura toda e os laterais descem, lado a lado
  (`k-lado`): a 1440 o mês do calendário teria células de 124 px e a tabela de roteiros não caberia em 9 colunas. Em Tokens
  e custos, "quem mais consome" vai para o fim da grade (`k-fim-ate-xl`).
- **Calendário: o limite é 1920 px**, não 1600. Até 1919 px o mês ocupa a largura toda e Fila + Melhores horários ficam
  lado a lado embaixo (`.k-lado--xxl`); a partir de 1920 px, 9 + 3 como no artboard (`.k-xxl-9`, `.k-xxl-3`). Com o painel
  ao lado a 1600, 22 eventos cortavam. Os textos do evento do mês quebram em até 2 linhas, nunca reticências.
- **375 px**: tudo em uma coluna (§4.1); tabelas largas rolam dentro do card; o mês vira agenda; as fases viram lista.

