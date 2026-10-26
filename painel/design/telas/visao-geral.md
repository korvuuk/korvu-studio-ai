# Visão geral — `/`

> **O Carlos abre isto para** saber, numa olhada, como está o estúdio hoje: o perfil, o que sai nos próximos dias, como
> foram os últimos 28 dias, quanto a IA consumiu e quem está na equipe.

- Maquete: `visao-geral.html` (1440 fluido e 375 px; dados de `../dados-2026-10-23.json`).
- Fonte do desenho: `painel/referencias/claude-design/telas-2026-10-23/Main.dc.html` (artboard 1920×1080, aprovado pelo
  Carlos em palavras: "Approved. Take the Visão geral mockup into painel/design/").
- Componentes: livro §11 e §15.2. Nada desenhado solto.

## Hierarquia
1. Barra do app (busca global, avisos, dono) — §15.2.
2. Topo: **sem título de página** (decisão de 24/10: o item do menu já diz onde se está; o `h1` "Visão geral" fica só para leitor de tela); só a data de hoje, à direita, numa barra fina. **Sem "Novo vídeo"** (24/10: o painel só informa).
3. Quatro números do perfil (KPIs).
4. Próximas publicações (5 cartões).
5. Desempenho · 28 dias | Público · Top 10 países | Tokens e custos · 30 dias.
6. Equipe: filtros por departamento e 5 cartões com foto.
7. Rodapé: "@korvu_oficial · sincronizado em … · o painel só lê os arquivos do projeto" (§12.5).

## Blocos

### Números do perfil (4 × `k-kpi`)
| KPI | Valor (23/10) | Fonte | Rodapé |
|---|---|---|---|
| Seguidores no Instagram | 3.631 | `perfil_snapshots.seguidores` (última leitura) | `k-delta--flat` "−0,1%" + "−3 vs. leitura de 16 out" (leitura anterior) |
| Alcance · 28 dias | 529 contas | `perfil_snapshots.alcance` | `k-delta--up` "11,1%" (476 → 529) + "2.448 visualizações" (`views`) |
| Alcance fora da bolha | 60 % | `alcance_nao_seguidores / (alcance_nao_seguidores + alcance_seguidores)` = 307 / 513 | `k-delta--up` "3,4 p.p." (56,4 % → 59,8 %) + "307 de 513 não seguem"; anel `k-anel` ao lado (`role="img"` com a frase) |
| Melhor vídeo até agora | 338 alcance | maior `metricas.alcance` da última leitura confiável (`suspeito = false`) = Demis Hassabis | nome + "13 out · 450 visualizações" + capa (`k-capa--lg`, `capa/capa.png` do post). O cartão inteiro leva a Desempenho |
- Delta com seta `aria-hidden` e a palavra para leitor de tela ("a mais que em 16 out"). Cor pelo significado.
- Números ≤ 9.999 inteiros com ponto (livro §1).

### Próximas publicações (`k-posts` > `k-post`)
- Fonte: `fila` (`publicar_em`, `plataformas`, `trial`) ordenada por data; capa do pacote em `06-publicar/<slug>/capa/`.
- Cada cartão: dia em caption + hora (horário de Londres, o mesmo do `publicar.py`), "amanhã/em N dias" (`accent-ink`
  quando é hoje ou amanhã), nome curto, canais por extenso (só os que vão sair) e o modo (Normal / Trial Reel).
- Cabeçalho: "5 agendadas · horário de Londres" (é o fuso em que os posts são agendados; não é definição de público) e
  "Ver calendário". O cartão leva ao Calendário.
- Nome curto: hoje sai do slug sem a data (não existe campo de título curto — `handoff.md` §8).

### Desempenho · 28 dias
- Totais reais: 2.448 visualizações · 529 contas alcançadas · 56 visitas ao perfil (`perfil_snapshots.views`, `alcance`,
  `visitas_perfil`), em `k-stats`.
- Curva "Visualizações por dia": **exemplo**. A Meta só devolve o total de 28 dias; a forma vem do artboard
  (`telas_exemplos` no JSON) e os pontos marcam as datas reais dos Reels (13, 15, 18, 20 e 22 out). Uma série: sem legenda
  (o título diz o que é). Hover/foco por dia com a dica; "Ver os números" mostra o que existe de verdade.
- **No app, até a fonte existir:** mostrar só os três totais e, no lugar da curva, a frase "A curva por dia aparece quando
  o perfil for lido todo dia." (sem desenhar curva). De onde viria: `perfil.py` pedindo os insights da conta com
  `period=day` e o sincronizador gravando uma linha por dia (engenheiro-backend).

### Público · Top 10 países
- Fonte: `perfil_demografia` (última leitura, `dimensao = 'country'`), `publico = 'seguidores'` (3.202 contas com país) e
  `'alcancados'` (379). Barra = % do total do público; a 1.ª em `chart-1`, as demais `chart-2` (destaque).
- Controle segmentado "Quem segue | Quem os vídeos alcançam" troca a lista e a base ("3.202 contas" / "379 contas").
- Nomes de país em PT-BR a partir do código ISO (tabela no gerador). É **dado**, não definição de público (decisão de 21/10).
- "Ver os números": as contas de cada país nas duas listas.

### Tokens e custos · 30 dias
- Fonte: registros do Claude Code (livro §15.3), corte em 23/10 16:02:49 (o mesmo do banco, PD21): 37,9 M tokens; Opus 5.5 83 %, Sonnet 5.5 12 %,
  Fable 5.1 5 % (rosca de 3 fatias, total no centro em `accent`, %s em `accent-ink`).
- Custo estimado **US$ 539** ("equivalente na API · 30 dias · preço de tabela"), sem câmbio (decisão de 24/10). O "›" leva
  a Tokens e custos.
- **No app**: o número vem do banco (tabela nova, `handoff.md` §8) — não dos `.jsonl` lidos ao vivo.

### Equipe
- Fonte: `agentes` (nome, cargo, departamento, papel, modelo) + `departamentos`; retrato em
  `painel/web/public/equipe/<id>.jpg` (10 com foto; o resto, iniciais no mesmo quadro).
- "Todos" mostra o Atlas e os 4 primeiros gerentes (como o artboard); cada departamento mostra até 5 pessoas, o gerente
  primeiro. Cartão: foto, status, nome, função, departamento, chip **Portão** (papel `portao`) e o modelo com a versão.
- Status "Trabalhando agora / Em espera": **exemplo** (não existe dado de presença). **No app, até existir:** a linha de
  status não aparece. De onde viria: sessão do Claude Code com resposta nos últimos minutos (timestamp do `.jsonl`).
- "Ver equipe completa" → Equipe. **Sem "Adicionar pessoa"** (24/10).

## Interações
- Busca global (⌘K): procura vídeos (nome curto e slug), pessoas (nome e função) e portões; resultado num `k-menu` em
  grupos; Esc fecha. Sem nada para achar: "Nada com '…' no painel."
- Sino: abre os avisos (§15.1) num `k-menu`; o ponto laranja aparece quando há aviso.
- Pedidos (vídeo novo, agendar, contratar) são feitos no Claude Code; o painel não tem botão nem "Copiar o pedido" (24/10).
- Filtros de departamento (`aria-pressed`), abas do Público, cartões clicáveis (foco visível em todos).

## Estados (cada bloco; desenhados na faixa "fora da tela" da maquete)
| Bloco | Vazio | Carregando | Erro |
|---|---|---|---|
| Números do perfil | "Ainda não há leitura do perfil" — quando o perfil.py ler a conta pela 1.ª vez, os números aparecem aqui | esqueleto de 4 KPIs | `k-note--alert` "Não deu para carregar esta parte" + "Tentar de novo" |
| Próximas publicações | "Nada agendado" — quando um pacote entrar na fila, aparece aqui com dia, hora e canal; ação "Ver produção" | esqueleto de linhas com capa | idem |
| Desempenho · 28 dias | "Sem números de 28 dias" | esqueleto de gráfico | idem |
| Público | "Sem dados de país" — a Meta só mostra a partir de 100 contas | esqueleto de lista | idem |
| Tokens e custos | "Nenhuma sessão nos últimos 30 dias" | esqueleto de gráfico | idem |
| Equipe (filtro) | "Ninguém neste departamento" (sem ação) | esqueleto de cartões | idem |
Banco fora do ar: `k-note--alert` no alto da página com os comandos (§12.5). Recarga com dados na tela: `.is-atualizando`.

## 375 px
- Barra de topo escura com o sino e "Menu"; a busca global fica no alto do menu aberto; a barra do app some.
- Sem título; a data numa linha própria; KPIs, publicações, blocos e cartões em uma coluna; cartão de
  agente com a foto de 96 px à esquerda. Sem rolagem lateral (conferido: `scrollWidth` 375).

## Do artboard para a maquete (o que não segui, e por quê)
| No artboard | Na maquete | Motivo |
|---|---|---|
| Tokens repetidos em `:root`, estilos inline | `tokens.css` + classes `k-*` | regra do sistema |
| "Carlos ▾" com seta de menu | identidade sem menu | não há conta, login nem menu para abrir |
| Sino "3 novas" | sino com os avisos calculados, sem "não lida" | o painel não guarda o que você viu; os avisos em si são reais |
| "2,4 mil" | "2.448" | livro §1: até 9.999, número inteiro |
| Legenda com uma série no gráfico | sem legenda | dataviz: uma série não pede legenda, o título diz |
| Linha de 6 + 3 + 3 colunas a 1440 | a 1440: desempenho na largura toda, público e tokens lado a lado; ≥ 1600 como o artboard | a 1440 a aba "Quem os vídeos alcançam" não cabia em 3 colunas (livro §15.4) |
| Cartão de agente horizontal | foto 4:3 em cima a 1440; horizontal ≥ 1600 e < 640 | a 1440 o cartão tem 220 px e o texto ficava com 66 px |
| Texto de 10–10,5 px | mínimo 11 px | caption do sistema |

## Dúvidas para o Carlos (pelo agente principal)
- Respondidas em 24/10: sem título de página e sem botões que criam coisas (`docs/decisoes.md` §5). Nenhuma aberta.
