**korvu. painel** é o sistema interno desktop do Carlos para gerir uma operação de criação de conteúdo feita por agentes de IA: equipa e departamentos, vídeos em produção, etapas e portões de aprovação, calendário editorial, publicações no Instagram e Facebook, desempenho, audiência, tokens e custos de IA. Este design system é a **fonte visual de verdade** para todas as telas — qualquer tela nova parte daqui. A prancha completa está em `components/Prancha` (e em PNG 2560×1440 em `assets/Prancha/`).

Premium SaaS desktop com alma editorial: muito espaço negativo, hierarquia tipográfica forte, números grandes, superfícies quentes e um único laranja que aponta para o que importa.

## Conteúdo e tom

- Toda a interface em **português**. Datas `22 out`, horas `18:30`, números com vírgula decimal e ponto de milhar: `482,6K`, `€ 186,40`, `1.284.910 tokens`.
- Rótulos curtos e concretos, em sentence case: "Vídeos e portões", "Aprovar e agendar", "Pedir ajustes". Rótulos de secção e de KPI em MAIÚSCULAS só via estilo `caption`.
- Os agentes são tratados como equipa: nome próprio + função + departamento ("Ana Ribeiro · Roteirista · Roteiro").
- Não existe login nem gestão de utilizadores; o único dono é **Carlos**, que aparece no rodapé da sidebar como "Proprietário" e é quem decide nos portões.
- Sem emoji, sem exclamações, sem jargão de marketing. Estados vazios dizem o que vai aparecer ("Quando um agente parar numa etapa, aparece aqui.").

## Cor — não alterar

- Fundo de todas as telas: `bg` (#F5F2E8, marfim quente). Nunca branco puro.
- Cards, tabelas, inputs e popovers: `surface` (#FBF9F4) com borda 1px `line`. Zonas rebaixadas (trilhos, chips neutros, hover): `surface-sunken`.
- Sidebar e tooltips: `sidebar` (#111111). Texto sobre ela: `sidebar-ink` (ativo) e `sidebar-ink-2` (inativo).
- Texto: `ink` (#111111) para títulos, valores e corpo; `ink-2` para secundário; `ink-3` só para meta/captions sobre `bg` e `surface`.
- Laranja Korvu `accent` (#FF4D00) = ação e foco: botão primário, item ativo (ícone + ponto), anel de foco, série principal de gráficos. **Texto sobre o laranja é sempre `on-accent` (#111111)** — branco falha o contraste. Para texto laranja sobre fundos claros use `accent-ink`.
- Verde `positive` **só** para métricas positivas e o estado Aprovado. Vermelho `danger` **só** para alertas e o estado Bloqueado. A cor do delta segue o significado: custo a subir é vermelho.
- Gráficos: `chart-1` laranja → `chart-2` preto → `chart-3` taupe → `chart-4` areia → `chart-5` ardósia, por esta ordem; outras cores não existem.
- Contraste verificado: `ink` 16.9:1, `ink-2` 5.2:1, `ink-3` 4.6:1 sobre `bg`; `on-accent` 5.7:1 sobre `accent`; `accent-ink` 4.6:1 sobre `accent-soft`. Anel de foco: 2px `focus` com offset 2px.

## Tipografia

- Família única **Geist** (`sans`, ficheiro variável em `fonts/`), com **Geist Mono** (`mono`) para modelos, IDs, HEX e contagens de tokens. Não usar a fonte antiga do projeto.
- Escala: `display` 56/800 · `h1` 44/800 · `h2` 30/700 · `h3` 22/700 · `body` 15/400 · `small` 13/500 · `caption` 11/600 maiúsculas tracking 8% · `metric-xl` 40/700 · `metric-l` 24/700.
- Títulos com tracking negativo (−1.5% a −3.5%). Todos os números com `font-variant-numeric: tabular-nums` (classe `k-num`).
- Uma página = um `h1` no topo (`space-64` acima). `display` só em boas-vindas e capas.

## Layout

- Referência desktop **1440px**. Sidebar fixa `sidebar-width` (208px) à esquerda; área principal fluida com padding `content-padding` (32px).
- Grelha de **12 colunas**, gutter `grid-gutter` 24px (20px abaixo de 1280px). KPIs em 3–4 cards (span 4 ou 3); gráfico principal span 8 + lateral span 4.
- Espaçamento só na escala `space-4 · 8 · 12 · 16 · 24 · 32 · 48 · 64`. Entre secções `space-48`; entre cards `space-24`; dentro de cards `space-16`/`space-24`.
- Topo de cada página: `h1` à esquerda; pesquisa (`Search`), filtro de período (`Dropdown`) e ação primária à direita.

## Formas, bordas e sombras

- Raios: `radius-card` 12px (cards), `radius-panel` 14px (painéis e modais), `radius-btn` 8px (botões, inputs, itens da sidebar), `radius-sm` 6px (tooltips, eventos), `radius-pill` (chips, barras de progresso).
- Bordas fazem o trabalho, sombras quase não existem: `shadow-card` em repouso, `shadow-hover` em hover de card clicável (com borda `line-strong`), `shadow-pop` só em dropdowns e notificações flutuantes.
- Hover discreto: muda borda/sombra ou fundo para `surface-hover`; nunca escala nem cor saturada.
- Proibido: gradientes, glassmorphism, cards com borda colorida à esquerda, cards dentro de cards.

## Componentes

Todos os componentes são classes `k-*` em `components/bundle.css` sobre os tokens; o script `components/bundle.js` expõe `window.Korvu` (`icon()`, `logo()`, `hydrate()`) e preenche `<span data-icon="…">` e `<span data-logo="ink|ivory">` automaticamente. Cada componente tem guia e preview em `components/<Nome>/`: Logo, Button, StatusChip, Card, KPICard, Sidebar, Avatar, TeamMemberCard, VideoRow, ProgressIndicator, ApprovalGate, CalendarEvent, Notification, Search, Dropdown, Tooltip, EmptyState, Charts, Icons.

## Iconografia

- Conjunto próprio de ícones **outline**, grelha 24px, traço 1.5px, pontas arredondadas, `currentColor` (`Korvu.icon(nome, tamanho)`).
- Os 7 ícones de navegação estão em `assets/Icons/` (traço `ink`): Visão geral, Equipe, Vídeos e portões, Calendário, Desempenho, Biblioteca, Tokens e custos.
- O portão é sempre o cadeado (`lock`). Canais (Instagram, Facebook) são escritos por extenso — não desenhar logótipos de terceiros.

## Imagens e avatares

- Avatares de agentes são **retratos fotográficos realistas** de pessoas fictícias: headshot profissional, quadrado 1:1, mesmo enquadramento (cabeça no topo a ~18%, olhos a ~40%, ombros a cortar a base), fundo neutro liso próximo de `surface-sunken`, luz suave, diversidade realista de género, idade e etnia. Exportar 512×512.
- Até haver fotos, o avatar mostra iniciais em `ink-2` sobre `surface-sunken` (ver `Avatar`).
- Thumbnails de vídeo usam o frame real; sem frame, `k-thumb` neutro com ícone `play`.

## Logótipo

`korvu.` (Geist 800) + `painel` (Geist 500, tom apagado). Em fundo claro: `assets/Logos/korvu-painel-ink.svg`; na sidebar/escuro: `assets/Logos/korvu-painel-ivory.svg`. Nunca em laranja, nunca separado, altura mínima 16px.
