PORTÃO-INTERFACE: BLOQUEADO — sobre 52f8b6832fcd (volta 1)

# PORTÃO-INTERFACE · painel · 25/10/2026 · decisões de 24/10, Equipe pelo modelo que rodou, Biblioteca nova

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão:** `52f8b6832fcd` (140 arquivos), congelada antes de ler e conferida de novo antes do registro.
- **Placar:** S0 0 · **S1 1** · S2 3. Nenhum S0-L.
- **Base:**
  - design APROVADO a1454ab6f426 (`acrescimos.css` 58bd71d9e817, igual ao do app);
  - dados APROVADO 25/10 02:22.
- **Capturas** (`painel/portoes/capturas-52f8b6832fcd/`):
  - 7 telas + `/equipe/portao-imagem` + 404, a 1440 e a 375 px;
  - `bib-looks-tela-*`, `bib-aba-sistema-*`;
  - `estados-{fora,vazio,lento}/` (Biblioteca, Equipe, Tokens) e `estados-lento/*-carregando-1440.png`.

## O que mudou desde o último APROVADO (1f444d78dc16)
Comparei o hash de cada arquivo da impressão com o veredicto anterior em `portoes.json`.
- **Apagados:**
  - a Biblioteca antiga: `Filtros.tsx`, `Materiais.tsx`, `components/Biblioteca.tsx`, `lib/biblioteca.ts`, `app/miniatura/[id]/route.ts`;
  - as 15 miniaturas de `web/public/biblioteca/`.
- **Novos:**
  - `biblioteca/_componentes/{Abas,Acervo}.tsx`, `components/Acervo.tsx`, `lib/acervo.ts`, `app/look/[id]/route.ts`;
  - 5 amostras em `public/biblioteca/` (4 fontes + legenda).
- **Alterados:** os 47 restantes da lista (Tokens, Equipe, Visão geral, Produção, Calendário, Desempenho, componentes, `db.ts`, `leituras.ts`, `consumo.ts`, `tokens.ts`, `formato.ts` e os 3 arquivos de design copiados).

Bate com o que a coordenação declarou.

## O que verifiquei e como

### Código e segurança
- `npx tsc --noEmit` exit 0 · `npx eslint src` exit 0.
- Build em `.next-verificacao` exit 0 (13 rotas, entre elas `/look/[id]` e `/capa/[pasta]/[slug]`; `/miniatura` saiu).
- `grep` de `service_role|SERVICE_ROLE|eyJhbGci|sb_secret_` no `static`: vazio.
- `npm audit --omit=dev`: 0 vulnerabilidades.
- Cores cruas (`#hex`, `rgba(`) só em `app/design/componentes.css`, que é a cópia do design aprovado.
- **`/look/[id]`, contenção de caminho:**
  - o id passa por `^(vlog|rec709|v[0-9]{1,3})$`;
  - o caminho vem do banco (`looks.previa`) e passa por `^painel/previas/looks/[a-z0-9-]+\.jpg$` e por `startsWith(PASTA + sep)`.
  - Medi:
    - os 5 ids reais: 200 `image/jpeg`;
    - `v99`, `..%2F..%2Fx` e `v5.jpg`: 404;
    - banco fora: 503;
    - banco vazio: 404.
- **Rota de capas:** não mudou (PI58). A Biblioteca usa `/capa/publicados/2026-09-17-demis-hassabis` (Serifa + rabisco) e `/capa/fila/2026-10-23-livro-chatgpt{,-l01c}` (Grotesca + sublinhado).
- **Limpeza:**
  - nenhuma referência a `lib/biblioteca`, `miniatura`, `Materiais` ou `Filtros`;
  - `/miniatura/x` dá 404;
  - o `FiltroLista` ficou com `FiltroLista`, `BuscaLista` e `FiltrosLista` (opções vindas de quem chama), usados em Produção e Equipe.

### Decisões de 24/10 (`docs/decisoes.md` §5, linhas 159–166)
- **Sem título de página:**
  - `BarraPagina` virou `h1.k-sr-only` (só para o leitor de tela) mais a barra de meta;
  - nas capturas nenhuma tela tem título visível;
  - a varredura confirma um `h1` por página ("Visão geral", "Equipe"…).
- **Sem botões que criam ou agem:**
  - `grep` de `<button>`/`<Botao>`: sobram só "Tentar de novo" (erro), os controles de vista (Mês/Semana, Hoje, setas, abas, filtros, Tokens/Custo), a bandeja de avisos e os `BotaoLink`, que são navegação;
  - `<Pedido>` não é usado em nenhuma tela;
  - "Novo vídeo" e "Aprovar portão" só existem em `/sistema`, a vitrine de componentes, fora do menu;
  - `Portao.tsx` no modo Decisão não tem botão, só a frase "A decisão é sua, dada no Claude Code" (li o código: nenhum vídeo está em `portao` hoje);
  - `/equipe/contratar` continua como rota, mas sem nenhum link para ela (o `handoff.md:14` manda tirá-la do menu, e ela saiu).
- **US$, sem câmbio:**
  - nenhum `£`, `libra` ou `GBP` em código vivo; sobra só um comentário órfão em `db.ts:227` (S2, PI77);
  - Visão geral, Equipe, Tokens e Biblioteca mostram US$ e "preço de tabela".
- **Projeção pelos 30 dias:**
  - `Projecao.tsx`, com `DIAS_RITMO = 30`, faz média diária dos 30 dias (dia sem sessão = 0) × 30;
  - na tela: US$ 40,86 × 30 = US$ 1.226, igual ao custo dos 30 dias, como deve ser.
- **Calendário sem gravação:**
  - mês e semana só com publicados, agendados e vagas;
  - o atalho "A caminho: 8 roteiros ainda sem gravação" na Fila é do desenho aprovado (`calendario.md:47`) e leva à Produção.

### Equipe: o modelo que rodou (`modelo_por_agente`)
- **A view, lida no banco em modo só leitura:**
  - 10 agentes com principal Opus 5.5 (o Atlas incluído, 94,3 % Opus + 5,7 % Fable);
  - 11 com Sonnet 5.5;
  - 5 sem execução (curador-de-obra, portao-imagem, portao-pauta, portao-publicacao, produtor-de-extras).
  - A tela diz "rodaram em Opus 5.5: 10 · Sonnet 5.5: 11 · ainda não: 5". Confere.
- **Filtros no navegador:**
  - Portões 7, Opus 5.5 10 (com a Direção), Sonnet 5.5 11, Ainda não rodou 5 e Todos 26: a contagem do chip é igual às linhas visíveis em cada um;
  - a busca "lia" deixa Júlia e Lia.
- **Tokens e custo, no mesmo instante que o banco:**
  - total 98,7M (banco 98.690.819);
  - Atlas: 47 tarefas (banco 47) e 32,0M tokens, Opus + Fable (banco 32.022.612).
  - A primeira captura mostrava 31,6M / 96,5M porque o sincronizador gravou às 21:39, depois dela. Conferi as somas por departamento (Tecnologia 57,1M = soma das 5 linhas) e o total de US$ 1.226 (soma dos departamentos).

### Tokens e custos
- **Por modelo:**
  - Opus US$ 1.122 (92 %), Sonnet US$ 23,57 (2 %), Fable US$ 80,28 (7 %), igual a `sistema_modelos.usd`;
  - os preços da nota (4/20, 2/10, 10/50) são os de `precos_modelo`.
- **Médias e participações:**
  - custo médio por agente: 1.225,86 / 21 = US$ 58,37;
  - Tecnologia: 59,2 % dos tokens e 50 % do custo.

### Biblioteca nova
- **Looks:**
  - Referência, Base, Arquivado (v4), Em uso (v5) e Alternativa (v11) vêm de `looks.papel`;
  - v5 "rosto 23,2 IRE · medido em 18 set" e v11 "40,9 · 18 set" vêm de `rosto_ire` e `rosto_ire_em`;
  - v4 "korvu-look-v4 · 15 set" vem de `criado_em`.
  - As 5 fotos carregam (naturalWidth 240 e 187 nas duas larguras).
- **Capas, legendas, fontes, animações, ferramentas e contagens:** vêm das tabelas do banco (25 agentes · 24 habilidades · 19 comandos = `sistema_contagens`).
- **Abas:**
  - cada uma mostra só o seu bloco, com `aria-pressed` certo, nas duas larguras; Armazenamento e Sistema ficam em todas, como manda o `biblioteca.md`.
  - A aba Sistema bate com a maquete: frases dos modelos e das 11 ferramentas, à letra.
- **Armazenamento:** 123,8 GB no Mac e 99,2 GB no HD (`armazenamento`: 123.770.912.649 e 99.199.256.718 bytes).

### As 3 divergências que o front-end declarou
1. **Frases dos looks e o "· WAY" saíram. Aceito.** O banco não tem a frase de cada look; o "WAY" só aparece no meio do nome livre do JSON ("WAY v5 — ATIVO (escolhido…)"). Escrever as frases à mão no código seria pior: o texto deixaria de vir do projeto. A tela fica mais pobre que a maquete, mas não diz nada falso. Fica no backlog como S2 (PI75), com o backend dono do yaml.
2. **Nota do HD sem "4K" e sem a data. Aceito.** `armazenamento` só tem `hd_videos` e `lido_em` (a hora da leitura, não a da cópia); resolução e data da cópia não existem no banco. Também no PI75.
3. **Números dos modelos de hoje. Correto.** A maquete era um retrato (82,7 %); o app lê `sistema_modelos`: 93,2 / 4,9 / 1,9 na captura e 93,4 / 4,8 / 1,9 depois da sincronização seguinte. É o que o banco diz.

### Tela, estados e acessibilidade
- **Capturas:** as 9 rotas a 1440 e 375 px com scrollWidth igual à janela. Abri cada PNG e não há erro na tela nem sobreposição.
- **Detector de texto cortado** (375 a 1920 px, 8 rotas): só os 2 nomes de departamento em Tokens a 1024 px, que já estão no backlog (PI53) e agora têm `title`.
- **Estados num servidor meu (3458):**
  - banco fora: aviso e erro por bloco com "Tentar de novo";
  - banco vazio: vazios com a frase e chips "0";
  - banco lento: esqueletos (76, 22 e 47 elementos);
  - 404 da página que não existe.
- **Varredura de acessibilidade** (9 rotas): um `h1`, sem salto de nível, nenhum botão ou link sem nome, nenhuma imagem sem `alt`, nenhum id repetido, nenhum `aria-controls` órfão. O único SVG apontado em Tokens é falso positivo: o `span` pai tem `role="img"` e `aria-label`.
- **Console:** limpo em 8 rotas; na Biblioteca, 2 avisos de LCP (S2, PI77).

## Achados

### S1-1 · O líder dos modelos sai apagado no card Sistema da Biblioteca
- **Onde:** `painel/web/src/app/biblioteca/_componentes/Lado.tsx:60` e `app/design/acrescimos.css:413` contra `:571`.
- **O defeito:**
  - o Opus (o 1.º) recebe `k-estilo-meta k-tokens` e os outros `k-estilo-meta kx-meta-ink`;
  - `.k-estilo-meta` (ink-3, peso 500) vem depois de `.k-tokens` (accent-ink, peso 600) com a mesma especificidade e vence;
  - medido: Opus `rgb(115,108,96)` peso 500, contraste 4,94; Sonnet e Fable `rgb(17,17,17)`, contraste 17,95.
- **O desenho:** a maquete aprovada (`biblioteca.html:68`) põe o líder em `accent-ink` 600.
- **Cenário:** o Carlos abre a Biblioteca e o "93,2 %" do Opus, o número principal do bloco, sai cinza claro, enquanto 4,9 % e 1,9 % saem em preto. A ênfase fica ao contrário do desenho e lê como se o Opus fosse o menos importante. Não é ilegível (passa AA), mas é desvio do design aprovado.
- **Correção:** o destaque tem de vencer a meta (ex.: `.k-estilo-meta.k-tokens` ou a mesma regra que a lateral usa em `.k-armazem-leg`). Conferir no quadro: Opus em accent-ink 600 nas duas larguras.
- **Quem corrige:** engenheiro-frontend.

### S2 (no `_controle/backlog-portoes.md`)
- **PI75:** as frases dos looks, o "WAY" e o "4K"/data do HD esperam o dado no yaml e no banco (backend → front-end).
- **PI76:** os rótulos de modelo do KPI e dos filtros da Equipe são fixos por família (`MODELOS`), e não o `modelo_nome` da view. Hoje estão certos.
- **PI77:**
  - as fotos dos looks sem `priority`: avisos de LCP e cartões cinza no 1.º carregamento frio;
  - o comentário órfão do câmbio em `db.ts:227`.

## O que NÃO verifiquei
- **Leitor de tela de verdade (VoiceOver).** Só a varredura automática de nomes, papéis e níveis.
- **Navegação inteira por teclado e foco visível nas abas novas da Biblioteca.** Só confirmei que são `<button>` com `aria-pressed` e `aria-controls` válidos.
- **O modo Decisão do `Portao` na tela.** Nenhum vídeo está em `portao` hoje, então só li o código.
- **A Semana do Calendário.** Abri só o Mês; o código da semana não tem mais gravação.
- **O banco contra os arquivos.** É do PORTÃO-DADOS, APROVADO às 02:22.
- **As capturas do front-end** em `painel/trabalho/frontend/telas-v4/` e `estados-25out/`: fiz as minhas.
- **O preview do Carlos (3456):** não estava no ar e não o liguei.

## S0-L abertos
Nenhum nesta área (lista completa em `_controle/backlog-portoes.md`).

## Incidente do portão (causado por mim, já desfeito)
- **O que aconteceu:** o meu servidor de auditoria (`PAINEL_DIST=.next-portao npm run dev -- -p 3457`) fez o Next reescrever `painel/web/tsconfig.json` às 21:36: acrescentou `.next-portao/types/**/*.ts`, expandiu os arrays e reordenou o `include`. A impressão foi para 07e789e8ea42 e o `registrar` recusou.
- **O que fiz:**
  - parei o servidor;
  - recompus o arquivo original byte a byte, achado pelo hash: `include` na ordem de antes e `lib`, `paths` e `exclude` compactos;
  - confirmei `tsconfig.json` = 8e511b97b9c9 e a impressão de volta a 52f8b6832fcd;
  - apaguei a `.next-portao`.
- **Nenhum arquivo do painel ficou diferente do que foi auditado.**
- **Lição para o processo:** servidor de auditoria só com um `PAINEL_DIST` que já esteja no `include` (`.next-trabalho`); nome novo faz o Next editar o `tsconfig.json`.
