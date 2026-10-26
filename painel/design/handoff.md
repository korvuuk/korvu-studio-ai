# Handoff — design system "korvu. painel" → engenheiro-frontend

> De: designer-de-produto · 24/10/2026 · **versão 3** (as decisões de 24/10; §00) sobre a **versão 2** (as 7 telas; §0). A versão 1 foi a importação do sistema (antes dela
> `painel/design/` estava vazio e o painel usava o `korvu-editorial`).
> Para: engenheiro-frontend (`painel/web`, Next.js 15 + React 19 + Tailwind v4).
> Autoridade: `painel/design/` depois do APROVADO do PORTÃO-INTERFACE (área `design`). O código volta ao mesmo portão,
> área `interface`, e é comparado com as prévias daqui.

## 00. O que mudou na versão 3 (24/10) — as respostas do Carlos (`docs/decisoes.md` §5)

| Mudança | Onde | O que fazer no código |
|---|---|---|
| **Sem título de página** | as 7 telas | tire o `h1` visível e o subtítulo (`k-page-head`, `k-page-lead`). Cada página fica com `<h1 class="k-sr-only">` com o nome do item do menu e, se tiver busca, data ou período, `<div class="k-page-barra">` no alto (16 px abaixo). Sem barra, o conteúdo começa nos 24 px da área |
| **O painel só informa** | Visão geral, Equipe, Produção, Calendário, Biblioteca | saem "Novo vídeo", "Novo conteúdo", "Agendar" (por pronto), "Agendar publicação", "Adicionar material", "Adicionar pessoa", "Adicionar agente" e o popover "Copiar o pedido" (`Pedido`, `.k-pedido`); a rota `/equipe/contratar` sai do menu da Equipe. Os estados vazios perdem a ação "Adicionar…". Ficam os links para outra tela e os controles de vista |
| **Custo em US$, sem câmbio** | Visão geral, Equipe, Tokens e custos | mostre o custo em US$ (`US$\u00a0{valor}`); tire a linha da taxa e a tabela `cambio` do uso. "Ver os números" com uma coluna só de custo (US$) |
| **Projeção pelos últimos 30 dias** | Tokens e custos | `média diária dos 30 dias × 30` (dia sem sessão = 0), com o texto "média dos últimos 30 dias (US$ X por dia…) × 30. É estimativa: a mensalidade já está paga." Sem delta |
| **Modelo que rodou** | Equipe (linha, filtros, KPI "Agentes"), Visão geral (cartão de agente), Direção | o modelo vem dos registros (`message.model`), não de `agentes.modelo`: principal pelos tokens; com mais de um, `.k-modelo-mix` (chip + "92 % · +1", lista no `title` e em `k-sr-only`); sem registro, `.k-modelo-nada` "ainda não rodou". Filtro novo "Ainda não rodou" |
| **Atraso de gravação só na Produção** | Calendário | já é assim: o calendário só marca gravação com data de hoje em diante |
| **Biblioteca refeita** (acervo de estilos, canvas aprovado em 24/10) | `/biblioteca` | implemente pela maquete nova (`telas/biblioteca.*`): abas, looks (5, foto do Carlos), capas, legenda, fontes, animações, Armazenamento (só o que está no Mac: gravações + material) e Sistema, mais a **aba Sistema** (aprovada em 24/10: 3 cartões de modelo e as 11 ferramentas com nome · tipo · o que faz, de `painel/biblioteca.yaml` → `ferramentas` e `modelos`). Componentes novos no livro §15.2 ("Acervo de estilos"); saem `Material`/`Uso` (`.k-material*`, `.k-uso*`, `.k-busca-grande`) e as miniaturas de material (o PI66 deixa de existir). Imagens prontas em `telas/img/biblioteca/` |
| **Números de tokens = os do banco** (PD21) | maquetes | última linha de cada resposta, dia da 1.ª, corte 23/10 16:02:49: 37,9 M, US$ 539,06 |

## 0. O que mudou na versão 2 (23/10, tarde) — as 7 telas

O Carlos desenhou as telas no Claude Design. Elas estão em `telas/`: para cada uma, a especificação (`<tela>.md`: objetivo,
hierarquia, dados de cada bloco com a tabela/coluna ou o arquivo, interações, os três estados, 375 px, o que é exemplo e o
que não segui do artboard) e a maquete (`<tela>.html`, dados reais, 1440 fluido e 375). **Implemente pelas maquetes e
pelos `.md`; o artboard (`painel/referencias/claude-design/telas-2026-10-23/*.dc.html`) é só a origem.**

| Tela | Rota | Arquivos |
|---|---|---|
| Visão geral | `/` | `telas/visao-geral.*` |
| Equipe | `/equipe` | `telas/equipe.*` |
| Produção de conteúdo | `/producao` (substitui `/videos`; redirecione o antigo) | `telas/producao.*` |
| Calendário | `/calendario` | `telas/calendario.*` |
| Desempenho | `/desempenho` | `telas/desempenho.*` |
| Biblioteca | `/biblioteca` | `telas/biblioteca.*` |
| Tokens e custos | `/tokens` | `telas/tokens-e-custos.*` |

**Cores que mudaram (decisão do Carlos, 23/10 — copie `tokens.css`, `acrescimos.css` e `tokens.json` de novo):**
- `--line-strong` agora é **`#928874`** (era `#a8a090`): borda de campos, busca, dropdown, botão secundário e caixa do
  critério passa a 3,13:1 sobre `bg` e 3,33:1 sobre `surface`. **Não ponha controle com essa borda sobre
  `surface-sunken`** (2,94:1).
- `--focus` agora é **`var(--accent-ink)`** (`#b33600`): o anel de foco global (`:focus-visible` de `componentes.css`)
  fica 5,1–5,8:1 nos fundos claros. **Novo `--focus-on-dark`** = `var(--accent)` (o nome é o da versão 6 do artefato do
  Claude Design): o `componentes.css` ganhou a regra dele, `.k-sidebar :focus-visible{outline-color:var(--focus-on-dark)}`,
  logo abaixo do `:focus-visible`, e o `acrescimos.css` faz o mesmo na `.k-topbar` (5,68:1). No Tailwind,
  `--color-focus-on-dark` (§3).
- Nada mais muda de cor; o `fidelidade.py` registra só essas três divergências como aprovadas.

**Componente por componente** (regras no livro §15.2; CSS em `acrescimos.css`, só `var(--…)`):
- **Casca**: a área principal ganha a **barra do app** (`.k-area` > `.k-appbar` + `.k-main`): busca global, sino de avisos,
  "Carlos · Proprietário" sem menu. Abaixo de 1024 px ela some (sino na barra de topo escura, busca no alto do menu).
  O rodapé da barra lateral passa a ser **"@korvu_oficial · Instagram · Facebook"**. Página: `.k-main.is-painel`,
  `h1` + `.k-page-lead`, `.k-page-meta`.
- **Navegação**: o 3.º item agora é **"Produção de conteúdo"** (ícone `videos-portoes`, rota `/producao`); **todos os 7 itens
  têm página** — sai o `aria-disabled` de Calendário, Biblioteca e Tokens e custos. O item ativo de duas linhas tem
  `line-height` 15 px (já no CSS).
- **Novos**: `Filtro` (`.k-filtro`), `Segmentado` (`.k-seg`), `Fases` (`.k-fase`, `.k-fase-elo`), `Canal` (`.k-canal`),
  `Palavra` (`.k-palavra`), `ChipPequeno`/`Modo` (`.k-chip.is-sm`, `.k-chip--modo`), `Capa` (`.k-capa--xs…lg/doc`),
  `CartaoPublicacao` (`.k-post`), `CartaoAgente` (`.k-agente`), `LinhaPessoa` + `Departamento` (`.k-pessoa-linha`,
  `.k-depto`), `Direcao` (`.k-direcao`), `Numeros` (`.k-stats`), `Tokens` (`.k-tokens`), `KpiLinha` / `KpiComPeca`
  (`.k-kpi--linha`, `.has-aside`, `.k-anel`), `BarrasFinas` (`.k-bar-row--fino/--larga`), `Colunas` (`.k-colunas`),
  `Ranking` (`.k-rank-pos`, `.k-table--denso`), `Medidor` (`.k-medidor`), `Mes` / `Semana` (`.k-mes*`, `.k-semana*`,
  `.k-event--mes`, `.k-event--semana`), `Vaga` (`.k-vaga`; `Gravacao`/`.k-gravar` saiu em 24/10), `ChaveValor` (`.k-kv`), `Atalho`,
  `Destaque` (`.k-destaque`), `Fonte` (`.k-fonte`), `Material` / `Uso` (`.k-material`, `.k-uso`), `Pedido`
  (`.k-pedido`). Grade: `.k-span-5/7/9`, `.k-xl-*`, `.k-xxl-3/9`, `.k-lado` (+`--xxl`), `.k-pilha`, `.k-fim-ate-xl` (livro §15.4).
- **4 ícones novos** em `icones/telas/` (`documento`, `seta-direita`, `link-externo`, `camera`) + `icones-telas.json`:
  entram no seu `<Icone>` ao lado dos 31.
- **Retrato = foto** (decisão de 23/10): `<img>` dentro do `k-avatar`/`.k-agente-foto` a partir de
  `public/equipe/<id>.jpg`; sem foto, iniciais no mesmo quadro. **Pode apagar o `Retrato.tsx`** (o retrato editorial gerado
  saiu).
- **Modelo com versão** em todo chip ("Opus 5.5", "Sonnet 5.5", "Fable 5.1"): o rótulo sai de uma tabela apelido → modelo
  (hoje `opus → claude-opus-5-5 → "Opus 5.5"`), num lugar só.
- ~~Custo em libras~~ — **vencido em 24/10**: custo em US$, sem câmbio (§00).
- **Mapa de estados × fases** (livro §15.1): a fase substitui o chip da família 3; cada fase mostra os portões que importam
  nela; Agendados usa a linha "Portões:" do calendário; Publicados nunca perde o "publicado" (PI40); trava manual
  ("Teste de cor · não sai") não é "Bloqueado".
- **Correções de base** (já no CSS): `[hidden]{display:none !important}`; `a.k-btn` sem sublinhado; `.k-delta` sem
  quebra; `.k-grid > *{min-width:0}`; **`.k-table-wrap{position:relative}`** — sem isso, o texto `.k-sr-only` (absoluto)
  de uma célula escapa da rolagem e alarga a página no celular (achado ao fotografar a 375). PI38: `.k-event .k-segura`.
- **Nome de pessoa nunca corta a 1440, 1600 ou 1920** (volta do portão, S1-4; o título do `CartaoPublicacao` ainda corta com `title` a 1440, PI41): `LinhaPessoa` com colunas `32 · nome · 76 · 86 · 64 · 54 ·
  14` px e `Departamento` com `minmax(510px, 1fr)` — 3 por linha só a partir de 1834 px, coluna do nome ≥ 106 px (o nome
  mais longo mede 104). `CartaoAgente`: o nome quebra em 2 linhas, nunca reticências (a 1600 cortava "Vera Ca…").
  `Direcao`: `.k-direcao-quem` com `flex: 0 1 auto` (a 375 o chip "Claude principal" passava 8 px da borda). Moeda e
  número nunca se separam: espaço inseparável entre `US$` e o valor (no React, `US$\u00a0{valor}`).
- **Calendário: limite em 1920 px** (pedido do agente principal, 23/10). Até 1919 px o mês ocupa a largura toda e Fila +
  Melhores horários ficam lado a lado embaixo (`.k-lado.k-lado--xxl`); a partir de 1920 px, 9 + 3 como no artboard
  (`.k-xxl-9` / `.k-xxl-3`). Em `Mes`, horário · estado, título e canais do evento quebram em até 2 linhas — **nenhuma
  reticência** (o `title` fica como apoio). **Sem gravação no calendário** (24/10). Conferido: 0 eventos cortados a 1024, 1280, 1440, 1600,
  1919, 1920 e 2200.
- **O painel só informa** (24/10, §00): sem botões que criam coisas e sem "Copiar o pedido".

## 1. O que você recebe

| Arquivo | Use para |
|---|---|
| `design-system.md` | as regras (cor, tipo, grade, cada componente, 375 px, estados) |
| `tokens.css` | as variáveis com os nomes que os componentes usam (`--bg`, `--ink-2`, `--space-24`, `--radius-card`…) + `@font-face` |
| `tokens.json` | os mesmos valores para código (cada token: `valor`, `css`, `uso`; `chart-1` e `focus-on-dark` com `alias: "accent"`, `focus` com `alias: "accent-ink"`; as cores decididas pelo Carlos trazem `fonte_era` e `decisao`) |
| `componentes.css` | as 19 famílias de classe `k-*` — **cópia do `bundle.css` do Claude Design, regra por regra** |
| `acrescimos.css` | transcrições do que estava inline nas prévias + propostas (casca, 375 px, estados, item sem página…) |
| `fontes/` | Geist e Geist Mono variáveis (OFL 1.1, `OFL.txt`) |
| `icones/` | 31 SVG `currentColor` (traço 1,5) + `icones.json` (nome → conteúdo do `<svg>`, rótulos PT-BR) |
| `marca/` | logotipo `ink` e `ivory` em contornos |
| `previas/*.html` | **a referência visual dos componentes**: abra `previas/index.html`; cada uma abre sem rede, em 1440 e 375 |
| `telas/*.html` + `telas/*.md` | **as 7 telas** (§0): maquete com dados reais + especificação; `telas.css`/`telas.js` são só da maquete |
| `dados-2026-10-23.json` | os números reais das prévias, com a consulta SQL de cada bloco |
| `contraste.md` | pares medidos; o que falha não foi trocado (vai ao Carlos) |
| `verificacao/fidelidade.py` | confere que nada divergiu da fonte |

Não precisa do `korvu.js` no app (ele só alimenta as prévias): faça um componente `<Icone nome tamanho />` a partir de
`icones/icones.json` (ou importe os SVG) e use os SVG de `marca/` para o logotipo.

## 2. Ordem sugerida

1. **Tokens e fontes** (§3) — sem isto nada fica igual.
2. **Casca** (§4): barra lateral 208px + área principal; abaixo de 1024px barra de topo + menu; "Pular para o conteúdo".
3. **Componentes** em `src/components/` (§5), um por família `k-*`, cada um conferido contra a sua prévia.
4. **Estados** `loading.tsx` / `error.tsx` / `not-found.tsx` (§6).
5. **Telas**: as 7 de `telas/` (§0), na ordem que o agente principal pedir. Não redesenhe por conta.

## 3. Tokens e fontes

**Copie sem mudar** `tokens.css`, `componentes.css`, `acrescimos.css` e a pasta `fontes/` para dentro do app (ex.:
`painel/web/src/app/design/`), mantendo `fontes/` ao lado do `tokens.css` — o `@font-face` usa `url("fontes/…")`
relativo e o Next empacota os `.woff2`. (Importar direto de `../../design` exige `externalDir`; copiar é mais simples.
Se copiar, rode o `fidelidade.py` apontando para a cópia ou compare com `cmp`.)

`globals.css` passa a ser:

```css
@import "tailwindcss";
/* Ordem das camadas do Tailwind v4: theme < base < components < utilities.
   Tokens em base vencem os padrões do Tailwind (ex.: o --radius-sm dele); componentes em components deixam as
   utilidades do Tailwind ajustarem um caso pontual sem !important. */
@import "./design/tokens.css" layer(base);
@import "./design/componentes.css" layer(components);
@import "./design/acrescimos.css" layer(components);

@theme inline {
  /* cores com prefixo --color-*: bg-surface, text-ink-2, border-line-strong, fill-chart-1… */
  --color-bg: var(--bg);
  --color-surface: var(--surface);
  --color-surface-sunken: var(--surface-sunken);
  --color-surface-hover: var(--surface-hover);
  --color-line: var(--line);
  --color-line-strong: var(--line-strong);
  --color-ink: var(--ink);
  --color-ink-2: var(--ink-2);
  --color-ink-3: var(--ink-3);
  --color-sidebar: var(--sidebar);
  --color-sidebar-raised: var(--sidebar-raised);
  --color-sidebar-line: var(--sidebar-line);
  --color-sidebar-ink: var(--sidebar-ink);
  --color-sidebar-ink-2: var(--sidebar-ink-2);
  --color-accent: var(--accent);
  --color-accent-hover: var(--accent-hover);
  --color-accent-soft: var(--accent-soft);
  --color-accent-ink: var(--accent-ink);
  --color-on-accent: var(--on-accent);
  --color-positive: var(--positive);
  --color-positive-soft: var(--positive-soft);
  --color-danger: var(--danger);
  --color-danger-soft: var(--danger-soft);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --color-chart-grid: var(--chart-grid);
  --color-focus: var(--focus);
  --color-focus-on-dark: var(--focus-on-dark);
}
```

- **Fontes, raios e sombras não precisam de @theme**: `--font-sans`/`--font-mono` e `--radius-sm` já têm o mesmo nome dos
  do Tailwind e os nossos (camada base) vencem; para os demais use as classes `k-*` ou `rounded-[var(--radius-card)]`,
  `shadow-[var(--shadow-card)]`. **Não** escreva `--radius-card: var(--radius-card)` no `@theme` (nome igual = referência
  circular).
- **Espaçamento**: o `--spacing` padrão do Tailwind v4 (0,25rem = 4px) já dá a escala: `1`=4 · `2`=8 · `3`=12 · `4`=16 ·
  `6`=24 · `8`=32 · `12`=48 · `16`=64. **Só esses oito** entre blocos (`p-6`, `gap-6`, `mt-12`…).
- **Pontos de quebra**: os padrões do Tailwind v4 são exatamente os do §4.1 do livro — `sm` 640 · `md` 768 · `lg` 1024 ·
  `xl` 1280. Mobile-first: `lg:` = a casca de desktop.
- **Sai do `globals.css`**: `--papel*`, `--tinta*`, `--acento`, `--fio`, `--ok`, `--alerta`, `--erro`, `.titulo`,
  `.rotulo`, `.num-tabela` (vira `.k-num`), `.fio`, a regra "código em Inter 500" (agora `code` = Geist Mono via `.k-code`)
  e o bloco `.dica` (vira `.k-tooltip.is-floating`, §5).
- **`layout.tsx`**: sai `next/font/google` (Bricolage_Grotesque, Inter) e as variáveis `--font-bricolage`/`--font-inter`;
  as fontes agora vêm do `@font-face` local do `tokens.css`. Opcional: `<link rel="preload" as="font" type="font/woff2"
  crossorigin>` para `Geist-Variable.woff2`. `lang="pt-BR"` continua.
- **Grep de saída** (o portão roda): nenhuma cor `#hex`/`rgba(` fora de `design/tokens.css`; nada de `bg-[#…]`.

## 4. Casca (substitui o `<header>` + `<main>` + `<footer>` do `layout.tsx`)

Estrutura (prévias `casca.html`, `casca-menu.html`, `barra-lateral.html`):

```html
<a class="k-skip" href="#conteudo">Pular para o conteúdo</a>
<div class="k-shell">                        <!-- + is-menu-open quando o menu está aberto (< 1024px) -->
  <header class="k-topbar">                  <!-- só aparece < 1024px -->
    <a href="/" aria-label="korvu. painel — início"><!-- logotipo ivory 19px --></a>
    <button class="k-menu-btn" aria-expanded="false" aria-controls="menu">Menu <!-- chevron-down 16 --></button>
  </header>
  <nav class="k-sidebar" id="menu" aria-label="Menu principal">
    <a class="k-sidebar-logo" href="/"><!-- logotipo ivory 19px --></a>
    <a class="k-nav-item is-active" aria-current="page" href="/"><!-- visao-geral 18 -->Visão geral</a>
    <a class="k-nav-item" href="/equipe"><!-- equipe 18 -->Equipe<span class="k-nav-count">26<span class="k-sr-only"> pessoas</span></span></a>
    <a class="k-nav-item" href="/producao"><!-- videos-portoes 18 --><span>Produção de conteúdo</span></a>
    <a class="k-nav-item" href="/calendario"><!-- calendario 18 -->Calendário</a>
    <a class="k-nav-item" href="/desempenho"><!-- desempenho 18 -->Desempenho</a>
    <a class="k-nav-item" href="/biblioteca"><!-- biblioteca 18 -->Biblioteca</a>
    <a class="k-nav-item" href="/tokens"><!-- tokens-custos 18 -->Tokens e custos</a>
    <div class="k-sidebar-foot"><div class="k-sidebar-owner">@korvu_oficial<small>Instagram · Facebook</small></div></div>
  </nav>
  <div class="k-area">
    <header class="k-appbar"><!-- busca global · sino de avisos · Carlos · Proprietário (sem menu) --></header>
    <main class="k-main is-painel" id="conteudo">…</main>
  </div>
</div>
```

- **Item ativo** pelo `usePathname()` (`/equipe/[id]` e `/equipe/contratar` acendem "Equipe"). Contagens = `agentes` e
  `videos` do banco (as mesmas consultas do `dados-*.json`); sem dado, sem contagem.
- **Itens sem página**: desde a v2 nenhum — os 7 têm tela. A regra (`<span aria-disabled>`) fica para um item futuro.
- **Menu (< 1024px)**: componente cliente pequeno — alterna `is-menu-open` no `.k-shell`, troca o rótulo para "Fechar" + `x`,
  atualiza `aria-expanded`; fecha com Esc (devolvendo o foco ao botão), ao clicar num item e na troca de rota; enquanto
  aberto, `overflow:hidden` no `<body>` para a página de trás não rolar.
- **Topo de página**: `<header class="k-page-head"><div><h1 class="k-h1">…</h1><p class="k-page-lead">…</p></div><div class="k-page-tools">…</div></header>` —
  um `h1` por página. **v3 (24/10): sem título visível** — `h1.k-sr-only` + `.k-page-barra` (§00).
- **Estado do banco e rodapé**: livro §12.5 — linha discreta no rodapé da `k-main` quando está tudo certo; `k-note--alert`
  antes do `h1` quando fora do ar / nunca sincronizado (a lógica do `Sincronia()` de hoje continua, só muda o lugar e a roupa).

## 5. Componentes — de hoje para o sistema

| Hoje (`src/components`, `src/app`) | Passa a ser | Observação |
|---|---|---|
| `TituloPagina` (Bricolage, minúsculas, ponto laranja) | `h1.k-sr-only` + `.k-page-barra` | **v3 (24/10):** sem título de página visível; o menu diz onde se está |
| `Secao` (número laranja + título com ponto + fio em cima) | `section.k-section` + `.k-section-head` com `h2.k-h2` | sem numeração; 48px entre seções |
| `Numero` (fio de 2px em cima) | `k-card k-kpi` (+ `k-delta`, `k-kpi-note`, sparkline) | delta com seta `aria-hidden` + palavra; cor pelo significado |
| `Sinal` (ícone + palavra do portão, dica com motivo) | `k-chip` (`.is-sm` nas tabelas) pelo **mapa único** do livro §11.3 (família 1) + dica `.k-tooltip.is-floating` com o motivo; **em Produção de conteúdo, a coluna de portão de cada fase segue o livro §15.1** | 7 estados: os 6 do banco + **legado** (`fila.legado = true` vence o `pendente` do banco; hoje é o texto "legado (sem portão)" em `page.tsx` e `videos/page.tsx`). Um desenho por estado, em toda tela. O chip do **vídeo** segue a família 3, **em ordem**: Bloqueado (algum portão do vídeo bloqueado, escalado ou vencido) → Publicado → Agendado → Portão → Em produção — um vídeo agendado com portão vencido é Bloqueado |
| (não existe hoje) | `Portao` = `k-gate` em **dois modos** (livro §11.11) | **Decisão**: só com todos os portões do vídeo aprovados e o vídeo ainda não agendado nem publicado; chip da decisão do Carlos — só **Aguarda** ou **Ajustes** (aprovar = agendar, e o vídeo vira "Agendado": "Aprovado" fica só no verde) — e a frase "falta a sua decisão — agendar ou pedir ajustes é no Claude Code", **sem botões** (24/10). **Portões do vídeo**: qualquer outro caso; só leitura, chip do estado do vídeo (família 3), "N de 4" = os 4 portões do vídeo com o chip do mapa único; abaixo, "Posts na fila" fora da conta, com a mesma regra da linha "Portões:" do calendário. Vídeo agendado ou publicado nunca fica no modo Decisão |
| `Vazio` (fio à esquerda) | `k-empty` | frase "o que vai aparecer aqui"; ação `k-btn-secondary k-btn-sm` |
| `Barras` (uma cor, acento) | `k-bar-row` (destaque `chart-1`, demais `chart-2`) + tabela gêmea | rótulo quebra em 2 linhas, nunca reticências |
| `Etiqueta` (modelo, portão) | `k-chip--model` ("Sonnet 5.5"), `k-chip--opus` ("Opus 5.5"), `k-chip--portao` | **modelo sempre com a versão** (decisão de 23/10): o rótulo sai da tabela apelido → modelo, nunca "Opus" sozinho |
| `Retrato` (retrato editorial gerado) | `k-avatar` / `.k-agente-foto` com a **foto** (`public/equipe/<id>.jpg`); sem foto, **iniciais** | **v2: decidido em 23/10 — retrato = foto realista.** O `Retrato.tsx` pode sair |
| `Esqueleto` | `.k-skel` dentro da casca (prévia `carregando.html`) | respiração só sem `prefers-reduced-motion` |
| `CopieECole` (Inter 500, "nunca mono") | bloco: `k-card k-pad` + `<pre class="k-mono">` (quebra de linha ligada); inline: `.k-code` | a mono agora é permitida para comando/ID |
| `Dicas.tsx` (posiciona a dica presa à janela) | **mantenha a lógica**, troque a roupa: `.k-tooltip.is-floating`, seta por `--seta-x`, abre após 300ms de hover/foco | já resolve o S0 de 22/10 (dica saindo da tela) |
| Menu do cabeçalho (minúsculas) | `.k-sidebar` / `.k-topbar` (§4) | |
| Etapas em quadradinhos (`videos/page.tsx`) | `k-steps` (5 etapas) + `k-steps-labels` opcional | mapa 12 estados → 5 etapas: livro §11.10 (proposta); `aria-label="Etapa 4 de 5: Revisão"` |
| Tabelas com `overflow-x-auto` | `k-card` > `.k-table-wrap` (`role="region"`, `aria-label`, `tabIndex={0}`, `--table-min`) > `table.k-table` | linha 56px, cabeçalho em caption |
| `formato.compacto` ("2,4 mil", "1,2 mi") | "482,6K", "12,8M"; até 9.999 inteiro com ponto (proposta, livro §1) | dica e tabela: número exato |
| Fila no calendário | `k-event` + linha **"Portões:"** (`.k-event-portao`) em **todos** os posts, respondendo se o post sai | O que o `publicar.py` confere na hora de publicar (`portoes.conferir_pacote`): **legado vence** ("Legado · sem selo", nenhuma exigência); senão o portão da publicação **e** a origem (`exigir`: roteiro, imagem, corte; pauta se aplicar). Mostra o **pior** estado (Escalado > Bloqueado > Vencido > Ainda não rodou > Não se aplica) com o chip do mapa único + "&lt;portão&gt; · não sai" (`.k-segura`, em `danger`); tudo aprovado = "Aprovado". Precisa dos portões da **origem** de cada post (hoje o banco tem `portoes_estado` por `videos/<slug>`). Arquivo trocado depois do selo o banco não sabe: só o log do `publicar.py`. `k-event--gate` = portão marcado num dia |
| Gráficos | `Linha`, `Barras`, `Rosca`, `Sparkline` com `k-chart` + legenda `k-legend` + tabela gêmea `.k-details` | desenhe na largura medida (sem `preserveAspectRatio="none"`); valor na dica por hover **e** foco; `suspeito` fora |

Componentes novos para `src/components/` (um por família): `Icone`, `Logo`, `Botao` (variantes + `sm` + `icone` com
`aria-label` obrigatório), `Chip`, `Card`, `Kpi`, `BarraLateral`/`BarraTopo`, `Avatar`, `CardPessoa`, `TabelaVideos`,
`Etapas`, `Progresso`, `Portao`, `Evento`, `Nota`, `Busca`, `Periodo` (dropdown), `Dica`, `Vazio`, `Esqueleto`,
`EstadoPagina` (erro / não encontrado), `Grafico*`. Nada recriado dentro de página (o portão marca S1).

**Acessibilidade que vem junto** (detalhe em `contraste.md`): `aria-current` no item ativo; `.k-skip`; foco visível em
tudo (o anel 2px+2px já está no CSS); chips sempre com palavra; presença e "não lida" com texto `.k-sr-only`; critérios do
portão como lista com o estado escrito no chip do mapa único; dica por foco e Esc; gráfico com `aria-label` + tabela; botão só-ícone com `aria-label`.

## 6. Estados (prévias `carregando.html`, `erro.html`, `nao-encontrado.html`, `vazio.html`)

- `loading.tsx`: esqueleto da página **dentro da casca** (a barra lateral não pisca) — `role="status"` + "Carregando os
  dados do painel…" em `.k-sr-only`; em recarga com dados na tela, `.is-atualizando` em vez de esqueleto.
- `error.tsx`: `.k-state.k-state--erro` com `h1` "Não deu para ler os dados", o porquê, "Como resolver" (`.k-passos`, comandos
  `COMO_LIGAR` e `COMO_SINCRONIZAR` em `.k-code`), "Tentar de novo" (`router.refresh()` + `reset()`, como hoje) e o código
  do erro (`digest`) em `k-mono k-muted`. `global-error.tsx` no mesmo estilo, sem casca.
- `not-found.tsx`: `.k-state` com `search`, "Página não encontrada", "Ir para a visão geral" + "Ver a equipe".
- Bloco que falha dentro de uma página: `k-note k-note--alert` + "Tentar de novo" (`k-btn-secondary k-btn-sm`).

## 7. O que NÃO implementar agora

- **Telas redesenhadas por conta própria**: implemente as 7 de `telas/`, sem inventar outras.
- **Ações de escrita**: o painel **só lê** (decisão de 22/10). O portão mostra o estado; aprovar, agendar e pedir ajustes
  ficam no Claude Code; desde 24/10 também nenhum botão que cria coisa nem o pedido para copiar (§00).
- **O que está marcado `exemplo` nas maquetes** (presença "Ativo agora", filtro "Ativos", "Tarefas atuais", a curva diária do
  Instagram, "não lida"): no app, faça como o `.md` da tela manda (esconder a coluna/filtro, ou o vazio com a frase) —
  **nunca** o número do exemplo.
- **Tokens e custos lidos ao vivo dos `.jsonl`** no servidor do painel: o número tem de vir do **banco** (§8); o painel não lê
  `~/.claude`.
- **Coluna "Responsável"** (Gravados): sem fonte. ("Quem adicionou" saiu com a Biblioteca antiga.)
- **Filtro de período** com uma opção só: mostre o período escrito (Desempenho: 28 dias; Tokens: 30 dias).
- **Modo escuro** (o sistema não tem), `k-sidebar-label` (4,37:1), miniaturas `is-dark`/`is-accent` (sem regra).
- **Trocar valor de cor** para "consertar" contraste: as propostas de `contraste.md` esperam o Carlos.

## 8. Dados que as telas pedem e o banco não tem (para o engenheiro-backend; o designer só registra)

| Peça | Falta | De onde vem / proposta |
|---|---|---|
| **Tokens e custos** (Visão geral, Equipe, Tokens e custos) — **dado novo** | nada no banco | os registros das sessões do Claude Code: `~/.claude/projects/-Users-teste-Documents-CONTENT-AI/**/*.jsonl` (`message.usage`, `message.model`, `timestamp`) e `subagents/agent-*.meta.json` (`agentType`); a conta está em `painel/referencias/claude-design/telas-2026-10-23/tokens-custos.py` (cache gravado 1,25× por 5 min e 2× por 1 h). Proposta: uma tabela com uma linha por resposta ou por (dia, agente, modelo, sessão, slug citado) com tokens de entrada, cache gravado 5 min/1 h, cache lido, saída e o custo em US$ calculado na sincronização; o painel soma por 30 dias |
| **Modelo que rodou** (24/10) | o banco de tokens precisa guardar o modelo por agente | `message.model` dos registros, somado por agente nos 30 dias (tokens por modelo); a Equipe mostra o principal e a fatia; o configurado (`agentes.modelo`) não aparece |
| **Origem e selo da fila (PI39)** | `fila` só tem slug e `legado` | `fila.origem` (o `videos/<slug>` de onde o post veio: `pacote.json → gauntlet.origem` quando houver) e `fila.selado` (o pacote tem `gauntlet`); sem isso a linha "Portões" de Agendados não acompanha o `publicar.py` para posts não legados |
| **Publicados pelo `post.json`** | `publicacoes` só ganha linha com o `metricas.json` | ler `07-publicados/*/post.json` (`publicado_em`, `plataformas`, permalinks): o Livro ChatGPT A (22/10 21:19) não está no banco |
| **Fase de produção** | se o vídeo tem gravação e se tem pacote | `brutos/principal/` com arquivo; pacote em `05-render-pronto/`, `06-publicar/`, `07-publicados/` |
| **Trava "não publicar"** | só existe como texto no `_controle/CONTINUAR.md` | campo `nao_publicar` (+ motivo) no `status.json` ou `pacote.json` (hoje: ChatGPT contexto, "teste de cor") |
| **Canais por post** | LinkedIn não existe | `post.json → linkedin.permalink` quando o LinkedIn publicar; Instagram e Facebook já existem |
| **Nome curto e formato** | só `videos.tema` (com notas) e o slug | campo de título curto e de formato (Reels/Stories/Carrossel) no `status.json`/roteiro |
| **Roteiros** | versão, palavra, PDF, extras | `roteiro.json` (`versao`, `cta_palavra`, `extras`), `material/*.pdf`, `brutos/extras/` |
| **Biblioteca (acervo de estilos, 24/10)** | os estilos | **banco já tem**: armazenamento (`videos.gravacao_bytes_no_mac`, `biblioteca_arquivos.bytes`) e os modelos (consumo). **Falta (configuração, hoje em arquivo)**: looks (`00-marca/cor/luts/*.json` + `cor.md` → versão ativa/alternativas), estilos de capa (com o pacote de exemplo), estilo de legenda (`00-marca/referencias/legendas/`), fontes (`remotion/src/brand.ts`), animações (`videos/*/animacoes/*/brief.md`: título, duração, se tem `.mp4`), contagens de habilidades e comandos (`.claude/skills`, `.claude/commands`). Lista bloco a bloco em `telas/biblioteca.md` |
| **Melhores horários** | nada (só um print) | a API não dá; o print é lido à mão (`dados-2026-10-23.json → telas_melhores_horarios`) |
| **Curva diária do Instagram** | só 2 snapshots de 28 dias | `perfil.py` diário (`period=day`) → uma linha por dia |
| **Presença** ("ativo agora") | nada | sessão do Claude Code com resposta nos últimos minutos |
| Responsável por vídeo · critérios por portão | — | como na v1 |

## 9. Como conferir antes de mandar ao portão

1. `bash painel/capturar.sh painel/trabalho/frontend <rotas>` e compare cada captura com a maquete da tela em
   `painel/design/telas/` e com a prévia do componente em `painel/design/previas/` (mesma largura: 1440 e 375).
   `scrollWidth` = largura da janela em todas.
2. Os três estados vistos num servidor seu (o `portao-interface.md` diz como).
3. `uv run python -I painel/design/verificacao/fidelidade.py` (e `cmp` das cópias em `painel/web`).
4. `npx tsc --noEmit`, `npx eslint src`, build em `.next-verificacao`.
