PORTÃO-INTERFACE: BLOQUEADO — sobre 591f80519753 (volta 1)

# PORTÃO-INTERFACE · painel · 23/10/2026 · as 6 telas novas · ciclo novo, volta 1

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão congelada no passo 0:** `591f80519753` (126 arquivos). Conferida de novo antes do registro: continua a mesma.
- **Ciclo novo:** o APROVADO de 20:44 (`e0add25326be`, volta 2) venceu. Em relação a ele, 44 arquivos são novos, 32 mudaram e
  nenhum foi apagado.
- **Entrega:** 6 das 7 telas do design aprovado às 21:04 (`9893c23bf5db`): Visão geral, Equipe, Produção de conteúdo,
  Calendário, Desempenho e Tokens e custos. A Biblioteca continua como espaço reservado.
- **Placar:** S0 0 · S1 2 · S2 7 (6 novos + o S1-L PI-L1, que continua só nas páginas sem desenho aprovado). Nenhum S0-L.
- **Capturas:** `painel/portoes/capturas-591f80519753/`
  - as 12 rotas a 1440 e 375, com fatias;
  - `interacao/`;
  - `estado-fora/`, `estado-carregando/` e `estado-vazio/`.

> **Resumo:** as 6 telas estão certas onde mais importa. Todo número que conferi bate com o banco: perfil, fila, publicações,
> tokens, libras, departamentos, pessoas, tarefas, projeção e custo por vídeo. Os três estados aparecem nas 6 telas, a
> segurança está limpa e o teclado funciona. Os dois S1 são pequenos e rápidos:
> - duas peças do sistema montadas à mão nas páginas;
> - um nome próprio escrito errado em 4 lugares.

---

## Achados que bloqueiam

### S1-1 · Peças do sistema montadas à mão dentro das telas (componente recriado)
**Onde:**
- `painel/web/src/app/tokens/_componentes/Projecao.tsx:29–35` e `:37–57`: o KPI "Projeção mensal" é montado à mão duas
  vezes (`k-card k-kpi`, `k-cap`, `k-kpi-value`, `k-prefixo`, `k-kpi-note`). Deveria vir de `src/components/Kpi.tsx`.
  - Nem o `Kpi` nem o `KpiLinha` têm a variante "delta ao lado do valor + nota embaixo".
  - A variante entra no componente, não na página.
- `painel/web/src/app/producao/page.tsx:98`: `<Link className="k-btn k-btn-secondary k-btn-sm">` nas ações de "Precisam de
  atenção". O `BotaoLink` já existe (`src/components/Botao.tsx:38`).

**Regra:** elemento recriado na página em vez de vir de `src/components/` é S1. Era o PI-L1, segurado como S1-L até a
implementação do redesign. O redesign chegou, e estas são as duas peças que sobraram nas 6 telas.

**Cenário:** quando o sistema mudar o botão ou o KPI (o anel de foco já mudou hoje com a decisão de contraste), estas
duas cópias ficam para trás. Tokens e custos e Produção passam a ter um KPI e um botão diferentes do resto do painel, e
ninguém percebe, porque a cópia não é o componente.

**Quem corrige:** engenheiro-frontend.
- Variante no `Kpi` (ou no `KpiLinha`) para a Projeção.
- `BotaoLink variante="secundario" pequeno` na linha 98.

### S1-2 · "Jacob coxon": nome de pessoa escrito errado, diferente da maquete aprovada
**Onde:** `painel/web/src/lib/producao.ts:28–55` (`nomeCurto`).
- Fora do pilar "perfil", só a 1.ª palavra do slug ganha maiúscula.
- O tema do vídeo `2026-09-17-jacob-coxon` (pilar `noticia-explicada`) não traz o nome, então a grafia do tema não socorre.

**O que a tela mostra:** "Jacob coxon" em 4 lugares:
- a tabela Roteiros de `/producao`;
- "Precisam de atenção" ("O mais antigo, Jacob coxon, espera desde 17 set");
- o sino;
- a busca ("roteiro" → "Jacob coxon · Roteiros").

**O que a maquete aprovada diz:** `telas/producao.html` (2×) e `telas/visao-geral.html` escrevem "Jacob Coxon". Os outros
6 nomes curtos batem com a maquete.

**Cenário:** o Carlos abre a Produção e vê o sobrenome de uma pessoa real em minúscula, no primeiro roteiro da lista e no
primeiro aviso. É exatamente o "cru" que a cara premium não aceita.

**Quem corrige:** engenheiro-frontend. Por exemplo:
- nome próprio no `GRAFIA`;
- ou slug de pessoa → cada palavra com maiúscula;
- o título curto de verdade é dado do backend (`handoff.md` §8), quando existir.

---

## O que verifiquei e como

### 1. A base copiada é a aprovada (byte a byte, contra o livro)
- O sha256 de cada cópia em `painel/web` é **igual** ao do APROVADO de design de 21:04 (`9893c23bf5db`):
  - `tokens.css`, `tokens.json`, `componentes.css` e `acrescimos.css`;
  - `icones.json`, `icones-telas.json` e as 4 fontes;
  - os 2 logotipos em `public/marca/`.
- O contraste novo do Carlos está no app e foi medido pelo Tab:
  - anel `rgb(179,54,0)` (`accent-ink`) nos fundos claros: pular, sino, Novo vídeo, cartões;
  - anel `rgb(255,77,0)` (`accent`) na barra lateral escura.
- O `casca.css` não repete mais o livro:
  - saíram os blocos `[ARTBOARD]` e o PI38 (fecha o PI53 da interface v2);
  - as 13 regras que citam classes `k-*` só compõem peças `kx-*` do app.

### 2. Código e segurança (em `painel/web`)
- `npx tsc --noEmit` exit 0 · `npx eslint src` exit 0.
- `PAINEL_DIST=.next-verificacao npm run build` exit 0 (BUILD_ID `YOE4O972vgV2K_hS2KZL5`, 12 rotas, 103 kB comuns).
- `grep` de chaves no `static`: vazio (`sb_publishable_` incluído). O HTML das 7 rotas no build não tem chave, nem o
  endereço do banco, nem caminho `/Users/…`.
- Nenhum `NEXT_PUBLIC_`; `server-only` em `db.ts`, `casca.ts`, `capas.ts`, `leituras.ts`, `producao.ts`, `tokens.ts` e
  `retratos.ts`.
- `npm audit --omit=dev`: 0. As dependências não mudaram.
- Nenhuma cor crua fora de `src/app/design/`. Os `style=` são só larguras, `--table-min` e `var(--chart-N)`/`var(--accent)`.
- **Rota nova `/capa/[pasta]/[slug]`** (lê `capa/capa.png` do projeto), testada com 13 endereços no build:
  - as capas reais respondem 200;
  - `..%2F`, `%00`, maiúscula e `.env` respondem 404: não sai da pasta do projeto;
  - `constructor`, `__proto__`, `toString` e `hasOwnProperty` respondem **500** (`pasta in PASTAS` olha o protótipo). Não
    lê arquivo nenhum, porque o `join` recusa uma função. → **S2 PI58**.

### 3. A tela de verdade
- `capturar.sh` no meu `next dev` (`127.0.0.1:3457`), 12 rotas a 1440 e 375, com fatias. `scrollWidth` igual à janela nas 24.
- **Detector de texto cortado:** escrevi um, no Chrome sem janela, que mede todo texto com reticências ou passando da
  própria caixa.
  - Rodei as 7 telas a 375, 768, 1024, 1440, 1600, 1834 e 1920 px.
  - Achou só os dois casos já conhecidos do design, agora com `title`: o PI41 ("Livro ChatGPT L01C A", Visão geral a 1440)
    e o PI53 (design) (departamentos de Tokens a 1024).
  - O PI41 serve de controle: prova que o detector pega um corte.
  - Equipe: 0 cortes em todas as larguras, inclusive a 1834 e a 1920 (3 departamentos por linha).
- **Console:** limpo nas 8 rotas, no dev e no build.

### 4. Cada tela contra a sua `telas/*.md` e contra o banco (consultas só de leitura, `default_transaction_read_only=on`)
Os números de consumo andam com a sincronização (21:56 → 22:11). Conferi tela e banco na mesma leitura.

**Visão geral**
- Perfil: 3.631 (−0,1 %, −3 vs. 16 out); 529 contas (+11,1 %); 2.448 visualizações; 60 % fora da bolha (307 de 513,
  +3,4 p.p.).
- Melhor vídeo: 338 (Demis, 13 out, 450 views, com a capa do `07-publicados`).
- 5 próximas publicações: dia, hora de Londres, "amanhã/em N dias", canal e modo.
- Desempenho 28 dias: 2.448 · 529 · 56.
- Top 10 países nas duas abas: "3.202 contas" / "379 contas", Brasil 52,0 %.
- Tokens: 52.653.092 → "52,7M"; US$ 784,50 × 0,7465 = £ 585,63 → "£ 586"; 88/9/3 %.
- Equipe: Atlas + 4 gerentes; o filtro Tecnologia mostra os 5.
- Como o `.md` manda no app: a curva por dia virou a frase "A curva por dia aparece quando o perfil for lido todo dia." e a
  linha de status sumiu.

**Equipe**
- KPIs: 26 (15 Opus 5.5 · 11 Sonnet 5.5, igual a `agentes.modelo` e aos `.claude/agents`) · 6 · 7 portões · 52,7M.
- Atlas: 46 tarefas · 25,9M · £ 334,72 · Rodou em Opus 5.5 + Fable 5.1.
- As 7 somas de departamento, e as **21 pessoas que rodaram, uma por uma** (tokens, £ e tarefas, pela `consumo_diario` e
  pela `execucoes_custo`). As 5 que não rodaram aparecem "não rodou".
- Sem "Ativos" e sem status, como o `.md` manda.
- Filtros:
  - Portões, Opus 5.5, Sonnet 5.5 e Todos dão 7, 14 (+ o Atlas), 11 e 25 linhas;
  - a busca "lia" dá Júlia Ramos e Lia Monteiro;
  - "zzz" dá "Ninguém com esse filtro" e o "Limpar filtros" funciona.

**Produção de conteúdo**
- Fases: Roteiros 7 · Gravados 0 · Prontos 1 (ChatGPT contexto, "teste de cor, não sai" = `nao_publicar`) · Agendados 5
  (3 vídeos, próxima sáb 24 out 19:00) · Publicados 5 (4 vídeos, melhor Demis).
- Cada fase clicada, com a âncora (`#prontos` abre Prontos):
  - Gravados mostra "Nada em edição agora";
  - Agendados mostra "Legado · sem selo" nos 5, que bate com `fila.legado = t` e `selado = f`;
  - Publicados mostra o alcance, as views, as curtidas e "lê em 27 out" no Livro ChatGPT A.
- Os **links de cada canal** são iguais aos `permalink` dos 5 `post.json`, com `noopener`.
- Portões por área: 10·2 / 12 / 10·2 / 5·7 / 5 legado. "Nenhum veredicto nos vídeos" é verdade: 0 veredictos com
  `alvo like 'videos/%'`.
- Stories e Carrossel mostram o vazio; a busca "hinton" funciona.

**Calendário**
- Os 5 publicados e os 5 agendados no dia e na hora de Londres certos, incluindo a virada para GMT em 25/10.
- Barra por canal (Instagram = `accent`; Instagram + Facebook = `ink`); "Gravar · Comando secreto" no dia 24; hoje em pílula.
- Mês, Semana, ‹ › e Hoje funcionam: "18 – 24 out", "25 – 31 out", Novembro com o L01C A.
- A 375 vira agenda.
- Fila: 5 · 0 · 0, com as frases certas.

**Desempenho**
- KPIs com o valor anterior: 2.448 (−8,6 %, eram 2.677), 529 (+11,1 %, eram 476), 56 (+3,7 %, eram 54).
- Anel 60 % (307/206).
- Países: as 10 de cada lista; o pé "Guiné-Bissau 54,4 % … 4.º, 5,8 %" confere (22/379).
- Ranking:
  - Demis 450 · 338 · 20,5 % · **5,9 % (20 interações)**. O banco tem 16 + 2 + 1 + 1 = 20; a maquete dizia 21 e 6,2 %, e o
    app segue o banco;
  - Fei-Fei 2,5 %; Hinton 27,7 % "leitura de 21 out"; Fei-Fei A 0 %;
  - durações 0:58 / 2:48 / 2:39 / 2:48.
- Destaque: 338 contra 40 + 11 + 4 = 55.

**Tokens e custos**
- KPIs: 52,7M "+ 1,8 bilhão lidos do cache" (1.781.358.309) · £ 586 · 26/21 · £ 27,89 (585,63/21).
- Pico: 23 out 23,4M.
- Por modelo: £ 508,11 / 17,60 / 59,93 e 87/3/10 % do custo.
- Os 7 departamentos (tokens, £ e %); destaque 49 % / 57 %.
- Custo por vídeo: Hinton 24,08 · Livro 4,98 · Demis 4,26 · Golpes 1,79 · Fei-Fei 1,59 (1,5861 contra 1,5852 do Comando
  secreto).
- Projeção: £ 435,79 em 7 dias → £ 1.868, 3,2× em vermelho com a seta e a palavra.
- Quem mais consome:
  - Gerentes, 8 linhas, e Ranking geral, 21 linhas: tudo bate;
  - "Por tarefa" = custo ÷ tarefas.
- Tokens/Custo troca a série: "23 out · £ 283,47".
- "Ver os números" tem as duas colunas, £ e US$.
- A taxa está à vista no topo, no KPI e na nota: "£ 0,7465 por US$ (XE, média de mercado, 23 out)", igual à tabela `cambio`.

### 5. Decisões do Carlos de 23/10
- Menu de 7 itens, e `/videos` responde 307 para `/producao` (no build).
- Topo com busca (agora com grupos Páginas/Pessoas/Vídeos/Portões e "Nada com '…' no painel."), sino e "Carlos ·
  Proprietário".
- Modelo **sempre com a versão** (Opus 5.5, Sonnet 5.5 e Fable 5.1).
- Tokens em laranja (`accent` grande, `accent-ink` pequeno).
- **Custo em libras com a taxa, a fonte e a data à vista** (Visão geral, Equipe e Tokens). Sem taxa: "custo em US$: taxa de
  câmbio não registrada", visto no estado vazio.
- Foto realista com iniciais para quem não tem; 5 fases com Instagram, Facebook e LinkedIn e o link de cada post.
- Contraste novo (`line-strong` #928874, foco `accent-ink`).
- Todas cumpridas.

### 6. Estados, vistos rodando no meu servidor, nas 6 telas, a 1440 e 375
- **Erro** (banco em `127.0.0.1:59999`): nota de banco fora do ar no topo, e **cada bloco** com "Não deu para carregar esta
  parte" + "Tentar de novo"; a casca fica de pé.
- **Carregando** (servidor de mentira que segura o banco por 30 s): esqueleto por bloco, `role=status` com o nome do bloco
  ("Carregando o consumo por dia…"), 8 a 70 blocos de esqueleto por tela.
- **Vazio** (servidor de mentira que responde `[]` com `Content-Range: */0`):
  - "O banco do painel nunca foi sincronizado" no topo;
  - o vazio de cada bloco com a frase do `.md`: "Ainda não há leitura do perfil", "Nada agendado", "Equipe ainda não
    sincronizada", "Nenhuma sessão nos últimos 30 dias", "Nada programado neste mês", "Fila vazia", "Sem print de
    horários", "Nada em produção", "Ninguém rodou ainda" etc.;
  - custo em US$ com "taxa de câmbio não registrada".

### 7. Acessibilidade
- **Auditoria pelo DOM nas 8 rotas (build):**
  - 1 `h1` por página e nenhum pulo de nível;
  - 0 botões ou links sem nome, 0 imagens sem `alt`, 0 ids repetidos, 0 `aria-controls` sem alvo;
  - todo gráfico com `role="img"` + nome. A exceção é um ícone de 12 px sem `aria-hidden` em Tokens, que fica decorativo.
- **Teclado:**
  - Tab e anel em todos os focáveis;
  - fases, filtros e segmentados com `aria-pressed`;
  - "Novo vídeo" abre o pedido e o Esc fecha e devolve o foco;
  - sino e busca como na volta anterior.
- **Pontos do gráfico de consumo:**
  - o Chrome os expõe ao leitor de tela como `graphics-symbol` com nome ("24 set: Tokens 0"), e a dica abre no foco;
  - são **30 paradas de Tab**, o PI48, herdado da maquete aprovada (`telas.js:91`).
- **Contraste:** os tokens são os do design aprovado (`contraste.py` da v5). Os pares de texto novos do `casca.css` foram
  medidos na volta 1, acima de 4,5:1.

### 8. Gráficos (skill `dataviz`)
- `validate_palette.js "#ff4d00,#111111,#a39b8b"` (a rosca dos modelos):
  - CVD PASS (39,5), visão normal PASS (51,5);
  - o preto e o taupe FAIL em faixa e croma, por serem neutros decididos pelo Carlos;
  - taupe 2,62:1 WARN, com o alívio exigido: % na legenda e "Ver os números".
- Um eixo só; uma série sem legenda; texto nunca na cor da série; dica no hover e no foco; tabela gêmea em todo gráfico;
  leitura suspeita fora (Hinton pela de 21 out).

### 9. Os desvios declarados pelo front-end (julgados contra o design e o banco)

| Desvio | Veredicto |
|---|---|
| Calendário sem **vagas** e com **Melhores horários** em vazio | **aceito**. As vagas vêm de `_controle/calendario.md` e os horários de um print medido à mão, e nenhum dos dois está no banco. O vazio é o do próprio `.md` ("Sem print de horários") e diz por quê. Dado novo → S2 PI63 (backend) |
| Produção sem **versão, PDF e cenas extras** do roteiro e sem **duração e data do pacote** | **aceito**. O `handoff.md` §8 lista esses dados como faltando no banco. A coluna sai em vez de inventar, e a meta "6 com PDF" saiu junto → PI63 |
| Equipe sem **presença/status** e sem o filtro **Ativos** | **aceito**. É o que o `equipe.md` manda no app |
| Desempenho sem **curva diária**, "**0 toques no link**", **não seguidores por Reel** e o "~208" | **aceito**. Curva: o `.md` manda a frase no lugar. Toques: só no JSON do perfil. Não seguidores por Reel e ~208: vêm de uma análise em `.md`, não do banco |
| Destaque trocado por um calculado (338 × 55 de alcance) | **aceito**: é verdade e diz que o alcance foi somado Reel a Reel. Ressalva: compara Reels de idades diferentes (Demis lido a 8,9 dias; os Trials a 1,7–6). Continua o PI31 |
| Hinton com 27,7 % assistido (leitura confiável de 21 out) | **aceito**. É a regra do sistema (leitura suspeita fora, vale a anterior, com a data escrita: "leitura de 21 out"), a mesma do S0-1 corrigido na interface v2. O "—" do `desempenho.md` fica para a designer atualizar (PI62) |
| Tokens ao vivo (52,7 M / £ 586) e não o retrato de 16:02 (37,9 M / £ 402) | **aceito**. O `.md` diz "No painel o número vem do banco"; o PD21 cuida da maquete |
| Gerentes com 8 linhas (entrou o Sérgio Lemos) | **aceito**. São o Atlas e os 7 portões, como os KPIs "Portões 7" da Equipe |

---

## O que NÃO verifiquei (declarado)
- **Leitor de tela de verdade** (VoiceOver): conferi papéis, nomes e foco pela árvore de acessibilidade do Chrome, sem ouvir.
- **Safari, 320 px e a janela de preview do app Claude.** O preview do Carlos (:3456) não estava no ar e eu não o liguei.
- **O vazio num Postgres vazio de verdade:** usei um servidor de mentira que imita o PostgREST vazio. O "erro do banco
  com tabela em falta" não foi montado.
- **Gravados com conteúdo** (a fase está vazia hoje) e o Prontos com "Agendar" (o único pronto tem trava): só li o código.
- **"Copiar o pedido":** não cliquei (não mexo na área de transferência do Mac).
- **Preços de tabela e conta dos tokens a partir dos `.jsonl`:** é do PORTÃO-DADOS, cuja área está ⛔ BLOQUEADA desde 22:15.
  Conferi a tela contra o banco, não o banco contra os registros.
- **As capturas do front-end** (`painel/trabalho/frontend/telas/` e `estados-23out/`): não usei como prova; refiz as minhas.
- **A vitrine `/sistema`:** só conferi que abre com `PAINEL_VITRINE=1` (dev) e mostra "Página não encontrada" sem a variável
  (build). Não revi o conteúdo de novo.
- **Efeitos colaterais meus:**
  - refiz a `.next-verificacao`;
  - o `next dev` da :3457 regravou o `next-env.d.ts` (gerado, fora da impressão);
  - derrubei os meus servidores (:3457, :3458) e os servidores de mentira (:59997, :59998).

## Backlog (`_controle/backlog-portoes.md`, só acrescentado)

**Atenção, número repetido:** o PI52, o PI53 e o PI54 foram usados duas vezes: na interface v2 (17:35) e no design v5
(21:04). Daqui para frente os novos começam no PI58. Os antigos ficam referidos como "PI52 (interface v2)" e "PI52
(design v5)".

| Nº | Classe | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|---|
| PI58 | S2 | `src/app/capa/[pasta]/[slug]/route.ts:8`, `lib/capas.ts:25` | `pasta in PASTAS` aceita nomes do protótipo: `/capa/constructor/…` e `__proto__`, `toString`, `hasOwnProperty` dão 500 (TypeError no `join`). Não lê arquivo, mas responde erro de servidor a um endereço inválido. `Object.hasOwn(PASTAS, pasta)` resolve | engenheiro-frontend | antes de subir o painel para um domínio |
| PI59 | S2 | `lib/producao.ts:120–136` (`portoesDoPost`) × `fila.erros_gauntlet` | A linha "Portões:" refaz a conta a partir dos `portoes_estado` e ignora o `erros_gauntlet`, que o sincronizador grava com o próprio `conferir_pacote` do `publicar.py`. Post **não legado sem selo** e arquivo trocado depois do selo: o `publicar.py` recusa, e a tela pode dizer "Aprovado". Hoje os 5 são legado sem selo e a tela está certa | engenheiro-frontend (+ designer: o §11.12 ainda diz que o banco não sabe) | **antes de o 1.º post não legado entrar na fila** |
| PI60 | S2 | `components/ErroBloco.tsx:20` | "Os números do perfil **não veio** do banco": 7 sujeitos no plural (os números, as fases, os avisos, os portões…) com o verbo no singular | engenheiro-frontend | próxima mudança nos estados |
| PI61 | S2 | `src/app/biblioteca/page.tsx` | O h1 "Biblioteca" ficou no estilo antigo; as 6 telas usam "… ." em minúsculas | engenheiro-frontend | implementação da Biblioteca |
| PI62 | S2 | `painel/design/telas/desempenho.md` (Dados) e a maquete | Demis "6,2 % (21 interações)": o banco e o `metricas.json` dão 16 + 2 + 1 + 1 = 20 → 5,9 % (o app está certo). Hinton "—" no % assistido × a regra do sistema (vale a leitura confiável de 21 out, 27,7 %, que o app mostra) | designer-de-produto | próxima volta de design |
| PI63 | S2 | `painel/sync/sincronizar.py` (banco) | Faltam para as telas: vagas semanais (`_controle/calendario.md`); versão, PDF e cenas extras do roteiro; duração e data do pacote pronto. Hoje as colunas e as vagas ficam fora (aceito) | engenheiro-backend | próxima volta do backend |
| PI-L1 | S1-L (continua, menor) | `src/app/equipe/[id]/page.tsx`, `equipe/contratar/*` | Fechou nas 6 telas. As 2 sobras viraram o S1-1 desta volta. Continua só na ficha e no Contratar, que não têm desenho aprovado | engenheiro-frontend | quando a ficha e o Contratar tiverem desenho aprovado |
| PI6 · PI7 · PI8 (fecho) | — | `/desempenho` | Números exatos (1.741), a base escrita ("307 de 513") e a janela no topo ("Últimos 28 dias · 25 set – 22 out") | — | ✅ fechado em 23/10 |
| PI23 (fecho) | — | `/desempenho` | A barra empilhada saiu e entrou o anel-medidor | — | ✅ fechado em 23/10 |
| PI27 · PI52 (interface v2) (fecho) | — | `lib/estados.ts:70–71` | A data ISO do motivo do portão sai formatada ("BLOQUEADO em 23 out, 20:44") no sino, nas dicas e nos avisos | — | ✅ fechado em 23/10 |
| PI53 (interface v2) (fecho) | — | `src/app/casca.css` | Os blocos `[ARTBOARD]` e o PI38 saíram; vêm do `acrescimos.css` aprovado | — | ✅ fechado em 23/10 |
| PI54 (interface v2) (fecho) | — | `lib/formato.ts:46–48`, `Kpi.tsx` | Taxa no formato do livro ("£ 0,7465 por US$ (XE, …, 23 out)"); nenhum "€" no app | — | ✅ fechado em 23/10 |
| PI57 (fecho) | — | Desempenho, Produção | O pilar cru saiu e o modo é o mesmo chip ("Normal"/"Trial Reel") em todo lugar | — | ✅ fechado em 23/10 |

**Continuam abertos, sem mudança:**
- PI18 (empate no 10.º país: "Cabo Verde 2" entre os que têm 2, sem aviso; o `.md` não define regra. Dono passa a ser a
  designer, para escrever a regra).
- PI29 e PI31 (destaque Normal × Trials sem a idade).
- PI41 e PI53 (design): já com `title` no app.
- PI45 ("+44 não seguidores" agora no app).
- PI48: 30 paradas de Tab no gráfico de consumo. O app seguiu a maquete aprovada; a mudança é da designer, depois do front.
- PI55 e PI56 (vitrine e modo Decisão).
- PD24 (dados; o gatilho é a próxima mudança do `db.ts` **depois** das 22:15).

## S0-L abertos (lista inteira do backlog)
Nenhum. A tabela "BLOQUEIOS DE PUBLICAÇÃO (S0-L)" de `_controle/backlog-portoes.md` está vazia.

## Para o engenheiro-frontend (volta 2)
1. **S1-1:**
   - KPI da Projeção pelo componente (variante no `Kpi`/`KpiLinha`), em `tokens/_componentes/Projecao.tsx:29–57`;
   - `BotaoLink` em `producao/page.tsx:98`.
2. **S1-2:** "Jacob Coxon" com a grafia da maquete (`lib/producao.ts`, `nomeCurto`). Conferir na Produção, nos avisos, no
   sino e na busca.

Aproveite a volta para o PI60 (concordância), que é de uma linha. O resto das 6 telas está certo, número por número. Não
mexa nos dados.

## Para o agente principal (fora da área desta auditoria)
- O painel não está limpo para o Carlos: a área **dados está ⛔ BLOQUEADA** (22:15, volta 1).
- **Observação de processo que o painel revela:** em "quem mais consome", o **Otávio Reis (portão do roteiro)** e a **Clara
  Duarte (portão do corte)** rodaram em **Sonnet 5.5** nos 30 dias, embora configurados como Opus 5.5. O
  `docs/gauntlet.md` diz que os portões "nunca rodam num modelo mais fraco do que quem construiu".
  - Não é defeito da tela: a tela mostra isso honestamente, e o `.md` já registra.
  - Vale você conferir como esses portões estão sendo chamados.
