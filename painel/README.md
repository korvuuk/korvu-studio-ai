# Painel do CONTENT AI

Equipe (quem é quem), vídeos e portões do GAUNTLET, fila de publicação e desempenho do @korvu_oficial.
**Os arquivos do projeto são a fonte da verdade; o painel só lê.**

```
arquivos do projeto ──► painel/sync/sincronizar.py ──► Supabase do painel ──► painel/web (Next.js) :3456
(.claude/agents, videos/*/status.json + portoes.json, 06-publicar, 07-publicados/*/metricas.json, _controle/perfil/*.json,
 painel/cambio.yaml, painel/biblioteca.yaml, 00-marca/cor/luts + cor.md, videos/*/animacoes/*/brief.md)
painel/sync/previas_looks.py ──► painel/previas/looks/*.jpg  (o único passo do painel que grava; o sincronizador só confere)
registros do Claude Code ──┘  (~/.claude/projects/<projeto>/**/*.jsonl — tokens e custos; só leitura, guardados como ARQUIVO)
```

## Rodar
```bash
bash painel/iniciar.sh            # banco + sincronização + app em http://localhost:3456
uv run python painel/sync/sincronizar.py   # só ressincronizar (o app mostra a hora da última)
uv run python painel/sync/previas_looks.py # prévias dos looks da Biblioteca (gera só o que mudou; proposta: no iniciar.sh)
bash painel/studio.sh liga        # Studio em http://127.0.0.1:55323 (reinicia o Supabase do painel, ~30 s)
bash painel/studio.sh desliga     # tira o Studio de novo (idem, ~30 s) — deixe desligado no dia a dia
bash painel/studio.sh             # estado: rede, portas e Studio (o mesmo que bash painel/so-no-mac.sh)
```

## Só no Mac (PD9, 23/10)
O banco e a API do painel **só respondem no próprio Mac**: `127.0.0.1:55321` (API/Kong) e `127.0.0.1:55322`
(Postgres). Do IP da rede local (ex.: 192.168.1.74) a conexão é recusada. O **Studio fica desligado** no dia a dia
(`[studio] enabled = false` no `config.toml`; com ele sai o postgres-meta, que a API servia sem senha em `/pg/*` — agora
`/pg/*` responde 503). Ligado pelo `studio.sh`, ele também só escuta em `127.0.0.1:55323`.

**O site (o app em :3456) também só abre no próprio Mac, em qualquer rede** (casa, coworking): http://localhost:3456 ou
http://127.0.0.1:3456 — `next dev` e `next start` escutam só em `127.0.0.1` (`-H 127.0.0.1` em `web/package.json`;
servidor de trabalho: `PAINEL_DIST=.next-trabalho npm run dev -- -p 3457`, que herda o endereço). Celular e outros
aparelhos não abrem; o acesso de fora virá pelo domínio, com login.

Como funciona: o Docker daqui é o Colima, cujo encaminhador `ssh` repete no Mac o endereço em que o contêiner publica
(0.0.0.0 → `*:porta`, 127.0.0.1 → `127.0.0.1:porta`). O `config.toml` do CLI não tem opção de endereço, então o
`painel/so-no-mac.sh` cria a rede Docker que o CLI usa por padrão, `supabase_network_content-ai-painel`, com
`com.docker.network.bridge.host_binding_ipv4=127.0.0.1` (o caminho da documentação do Supabase para rede não
confiável). Ela vem **sem o rótulo do CLI**, para o `supabase stop` não a apagar — assim todo comando do CLI que cria
contêiner no painel (`supabase start`, `db reset`, `db diff`) já publica só em 127.0.0.1, sem flag. O `iniciar.sh` e
o `studio.sh` garantem a rede antes de subir e **param com erro** se alguma porta do painel ficar aberta para a rede.
Nada disso mexe no Colima, no firewall do macOS nem no MUNTUZA_CMS (543xx, que continua em `*:`).

- **Não usar** `--network-id` nem `SUPABASE_NETWORK_ID` no painel (tiraria os contêineres da rede só-no-Mac), nem
  `docker network prune` com o painel parado (apagaria a rede; o próximo `supabase start` solto a recriaria aberta —
  o `iniciar.sh` conserta e o `bash painel/so-no-mac.sh` acusa).
- O CLI imprime no `start` um aviso fixo "All services bind to 0.0.0.0": é texto genérico dele. Quem diz onde as portas
  escutam é `bash painel/so-no-mac.sh` (ou `lsof -nP -iTCP -sTCP:LISTEN | grep 553`).
- **Fora deste passo:** o firewall do macOS (desligado — decisão do Carlos, "vejo depois"). As chaves de demonstração
  do Supabase continuam (agora só valem neste Mac); trocar antes de qualquer exposição.

**Sincronização automática (instalada em 22/10):** launchd `uk.korvu.painel` roda o sincronizador **a cada 15 min e ao
entrar na sessão do Mac** → `_controle/logs/painel.log` (uma linha por passagem). Se o Supabase do painel estiver
desligado (ex.: o Docker ainda não subiu depois de reiniciar), a linha diz `✗ banco do painel fora do ar — ligar com:
bash painel/iniciar.sh` (nunca um `supabase start` solto: só o `iniciar.sh`/`studio.sh` garantem a rede só-no-Mac — PD12)
e ele tenta de novo na passagem seguinte; os contêineres têm `restart: unless-stopped`, então voltam quando o Docker volta.
O app em si (`npm run dev`, :3456) **não** é automático: `bash painel/iniciar.sh` ou o preview "painel".
```bash
launchctl kickstart -k gui/$(id -u)/uk.korvu.painel   # forçar uma passagem agora
bash scripts/launchd/desinstalar.sh uk.korvu.painel     # desligar
```

| Peça | Onde | Notas |
|---|---|---|
| Banco | `painel/supabase/` | Supabase local **próprio** (`project_id = content-ai-painel`, portas **553xx** — o MUNTUZA_CMS usa as 543xx), **só em 127.0.0.1** (ver "Só no Mac"). Studio desligado; quando
ligado (`bash painel/studio.sh liga`), http://127.0.0.1:55323. Tabelas em `migrations/`; RLS em todas, `anon`/`authenticated` sem privilégio nenhum, `service_role` só SELECT (também nos default privileges: `20261022225715_revogar_privilegios_da_api.sql`). `departamentos.gerente_id` e `agentes.fiscalizado_por` são FK para `agentes(id)`, `deferrable initially deferred` (a relação é circular): gerente ou portão fora do `equipe.yaml` = a passagem falha com `✗`. `veredictos` tem chave (`alvo`, `ordem`): `ordem` = a posição no `portoes.json` (o `em` tem resolução de segundo e repetia — PD20) |
| Sincronizador | `painel/sync/sincronizar.py` | regrava cada tabela inteira numa transação — **menos `execucoes`/`uso_execucao`, que são arquivo** (ver "Tokens e custos"); nunca escreve no projeto (nem o cache dos portões, nem bytecode: `sys.dont_write_bytecode` antes do `import portoes`, porque o launchd roda sem `PYTHONDONTWRITEBYTECODE`) nem em `~/.claude`. Banco fora do ar, banco que recusa ou arquivo ilegível = uma linha `✗`, exit 1, nada apagado; a linha do banco que recusa traz o DETAIL do Postgres (ex.: `Key (gerente_id)=(portao-dadoz) is not present in table "agentes"` — PD23). Raiz lida: `PAINEL_PROJETO` (padrão: `CONTENT_AI_ROOT`, senão a raiz real), a mesma para o `portoes.py`. Registros do Claude Code: `PAINEL_REGISTROS` (padrão `~/.claude/projects/<raiz com tudo o que não é letra/dígito → ->`) |
| Testes | `painel/tests/test_sincronizar.py` | `uv run python painel/tests/test_sincronizar.py`: raiz temporária + banco `painel_teste_<pid>` (criado e apagado no 55322) — um caso por mapeamento, `--seco`, porta morta, contrato com os produtores e permissões (o banco do Carlos só é lido) |
| Equipe | `painel/equipe.yaml` | nome, cargo, departamento, personalidade — o lado técnico vem de `.claude/agents/*.md` |
| Câmbio | `painel/cambio.yaml` | taxa do custo de IA em libras (decisão do Carlos, 23/10): moeda por 1 US$, fonte e data, uma linha por data. Atualizar = acrescentar uma linha (sem mexer em código). Ausente ou inválido = `✗`, nada gravado |
| Retratos | `painel/web/public/equipe/<id>.jpg` | **foto realista 512×512** (decisão do Carlos, 23/10), com o `id` de `painel/equipe.yaml`; o app olha a pasta a cada página (`web/src/lib/retratos.ts`) e, sem foto, mostra as iniciais. Originais em `painel/referencias/fotos-equipe-originais/`. O sincronizador grava `agentes.retrato` = `/equipe/<id>.jpg` (o `.jpg` vence; senão `<id>.png`; sem arquivo, NULL = iniciais) |
| Trava "não publicar" | `_controle/nao-publicar.json` (**proposta**, ainda não existe) | `{"descricao", "travas": [{"slug", "motivo", "desde": "AAAA-MM-DD"}]}`, no formato do `_controle/gauntlet-legado.json`; o sincronizador LÊ para a tabela `nao_publicar` (ausente = nenhuma trava; inválido = `✗`). Quem cria e escreve é a sessão coordenadora |
| App | `painel/web/` | Next.js 15 + TypeScript + Tailwind, design system **"korvu. painel"** (`painel/design/`, copiado sem mudar para `web/src/app/design/`; biblioteca em `web/src/components/`). Chaves só no servidor (`web/.env.local`) |

## Tokens e custos (23/10)
**Fonte:** os registros das sessões do Claude Code deste projeto. Sessão principal = `.jsonl` de primeiro nível;
subagente = `<sessão>/subagents/[workflows/<wf>/]agent-<id>.jsonl`, com o tipo em `agent-<id>.meta.json` (`agentType`;
o painel guarda também `description` (≤ 200 caracteres), `spawnDepth` e `finished`). Cada resposta traz `message.usage`,
`message.model`, `message.id` e `timestamp`. **Nada de texto de conversa vai para o banco** (nem o pedido, nem a resposta).

**A conta** é a do `painel/referencias/claude-design/telas-2026-10-23/tokens-custos.py` (a das telas), com uma correção
(S1-1 do PORTÃO-DADOS, 23/10): uma resposta = as linhas com a mesma chave (`message.id`, ou `uuid`) no mesmo arquivo — a
mesma mensagem em dois arquivos conta duas vezes — e **vale o usage da ÚLTIMA linha lida**. O Claude Code grava cada bloco
da resposta numa linha; nas versões 2.1.270–2.1.304 a 1.ª traz o usage provisório (`output_tokens` 1–3) e o final só vem
na última (521 respostas nos registros de 23/10; só a saída muda e nunca diminui). O script fica com a 1.ª linha:
`--regra-do-script` refaz a conta dele, só para conferir. Dia e instante = os da 1.ª linha (o começo da resposta);
dia = os 10 primeiros caracteres do `timestamp` (**data UTC**); tokens = entrada + cache gravado + saída (o cache lido entra
só no custo); modelo fora de `precos_modelo` **não conta** (fica guardado em `uso_execucao`, sem custo; hoje só 5
`<synthetic>`, mensagens geradas pelo próprio Claude Code, sem custo de API); tarefa = execução com ao menos uma resposta de
modelo com preço. Custo em US$ pelo preço de tabela da API por milhão (entrada/saída): Opus 5.5 4/20, Sonnet 5.5 2/10,
Fable 5.1 10/50 e **Opus 5 5/25** (o histórico de 15–19/09; cache lido 0,50 = 0,1 × a entrada); **cache gravado pelo TTL** —
5 min = 1,25 × a entrada, 1 h = 2 × (`cache_creation.ephemeral_5m/1h_input_tokens`; sem o detalhe, tudo a 5 min, contado
em `cache_gravado_sem_ttl`); cache lido 0,20 (0,25 no Fable, 0,50 no Opus 5). Diferenças de propósito com o script: o
vídeo (abaixo); detalhe de TTL que não fecha com o total cobra o resto a 5 min (0 casos em 23/10); o Opus 5 tem preço aqui
(15–19/09 fica fora da janela de 30 dias até 23/10, que continua 37.699.450 tokens / US$ 536,09 no corte).

**Vídeo de uma execução** (regra do coordenador, 23/10 — a mesma da `fila.video_slug` e da `publicacoes.video_slug`): no 1.º
pedido do subagente, cada `videos/<slug>`, `05-render-pronto/<slug>`, `06-publicar/<slug>` ou `07-publicados/<slug>` **cuja
pasta existe** vira o vídeo de origem — `videos/` é o próprio; uma pasta de pacote é o `gauntlet.origem` do `pacote.json`,
senão o slug de `videos/` mais longo que é prefixo do slug da pasta (até um "-": `…-fei-fei-li-r2` → `…-fei-fei-li`), senão o
próprio slug. Vale o vídeo **mais citado**; no empate, o citado primeiro. O departamento **tecnologia** (o painel) nunca
recebe vídeo; a sessão principal também não. Slug citado sem a pasta na frente ("Slug: `…`", "--slug …") não conta.

| Tabela / view | Grão | O que é |
|---|---|---|
| `precos_modelo` | modelo | preço de tabela (US$/M): entrada, cache 5 min, cache 1 h, cache lido, saída — de `PRECOS` no sincronizador |
| `cambio` | moeda × data | espelho de `painel/cambio.yaml` (GBP 0,7465 por US$, XE, 23/10). Desde 24/10 o custo fica em US$ e nenhuma tela converte; o arquivo é **opcional** (PD28): ausente = tabela vazia + ⚠; inválido = ✗ |
| `execucoes` | um `.jsonl` com resposta | tipo (principal/subagente), sessão(-mãe), id do agente, workflow, `agente_tipo` cru, membro e departamento (equipe.yaml; sessão principal, ajudantes `general-purpose`/`workflow-subagent`/`claude`/`Explore`/`Plan` e agentType fora do yaml = `diretor`/`direcao`), vídeo, início/fim, `registro_presente`, `visto_em` |
| `uso_execucao` | execução × dia × modelo | respostas, entrada, cache 5 min, cache 1 h, sem TTL, cache lido, saída, tokens (gerado) — todos os modelos |
| `consumo` (view) | execução × dia × modelo, só com preço | + modelo_nome, membro, departamento, vídeo e **usd** (calculado de `precos_modelo`) — a base de toda soma das telas; tarefas numa janela = `count(distinct arquivo)` |
| `consumo_diario` (view) | dia × modelo × agente (e departamento) | somas + `execucoes` do dia (não somar entre dias) |
| `execucoes_custo` (view) | execução | totais de sempre (tokens, usd, respostas), `tarefa`, `respostas_sem_preco` |

O custo **não é guardado** nas linhas: as views o calculam de `precos_modelo`, então o número e a sua origem são sempre os
mesmos (e o arquivo antigo segue o preço da tabela). As três views são `security_invoker`; tudo com RLS e só SELECT para o
`service_role` (migrações `20261023153330`, `20261023154146`, `20261023154151`).

## Fila, fases e publicados (23/10)
| Tabela · coluna | De onde vem |
|---|---|
| `fila.origem` · `fila.selado` · `fila.erros_gauntlet` | PI39. `pacote.json → gauntlet.origem` (NULL sem selo); `selado` = o pacote tem o bloco `gauntlet`; `erros_gauntlet` = o que `portoes.conferir_pacote(pasta, pacote, post, publicacao=True)` dá **nesta passagem** — a mesma chamada do `publicar.py` na hora de publicar, com as mesmas mensagens; `[]` = o post sai. Legado (`fila.legado`, slug na lista congelada) **sem** selo: nada exigido; legado **com** selo: regra normal; sem selo fora da lista: recusado (o erro aparece aqui, não vira legado). Pega também arquivo trocado depois do selo. Com `portoes.SO_LEITURA = True`, nada é gravado (nem o cache dos hashes) |
| `fila.video_slug` · `publicacoes.video_slug` | o vídeo de origem da pasta (regra acima) |
| `videos.gravado` · `gravacao_arquivos` · `gravacao_bytes` · `gravacao_ultima` · `gravacao_chegou` · `gravacao_data_suspeita` | arquivos de vídeo (`.mov`, `.mp4`, `.m4v`, `.mxf`, `.mts`, `.m2ts`, `.avi`, `.mkv`, `.3gp`, `.webm`; nome não oculto; > 0 byte) em `videos/<slug>/brutos/principal/`, subpastas incluídas — **só a listagem e o `stat()`**, os brutos não são abertos. `gravacao_ultima` = mtime mais recente (a data do arquivo: a câmera grava com o relógio em 2024); `gravacao_chegou` = ctime mais recente (quando entrou no disco do projeto); `gravacao_data_suspeita` = a data do arquivo é mais de 30 dias anterior à data do slug |
| `videos.pronto` | há `05-render-pronto/<pasta>/pacote.json` com `qa` = `PASS` (a leitura do `publicar.py`: `str(qa).upper()`) cujo vídeo de origem é este |
| `publicacoes` (+ `plataformas`, `estado`) | entra por **`07-publicados/<slug>/post.json`** (o registro do `publicar.py`: `publicado_em`, `plataformas`, `estado`, `instagram.permalink`, `facebook.permalink`, `instagram.trial`, `material.palavra`) **ou** pelo `metricas.json`; o `post.json` vence, o `metricas.json` completa; tema, pilar e duração do `pacote.json`. As métricas chegam depois (5 dias). Sem `post.json`: `plataformas`/`estado` NULL |
| `nao_publicar` | `_controle/nao-publicar.json` (proposta acima): `slug`, `video_slug` (origem), `motivo`, `desde` |

Fases da Produção de conteúdo (decisão de 23/10): **Roteiros** = vídeo sem `gravado` · **Gravados** = `gravado` sem
`pronto` · **Prontos** = `pronto` (e fora de `fila`/`publicacoes`) · **Agendados** = `fila` · **Publicados** =
`publicacoes`, ligados pelo `video_slug`. Migrações `20261023160517`, `20261023160956`, `20261023161339`.

**O arquivo (decisão de 23/10).** O Claude Code apaga os registros com mais de 30 dias (`cleanupPeriodDays` padrão; já não
há nada anterior a 01/10, salvo 18 arquivos de 15–19/09 só com `claude-opus-5`). Por isso `execucoes` e `uso_execucao`
**nunca são truncadas**: cada passagem, na mesma transação das outras tabelas, apaga e regrava as execuções cujo `.jsonl`
ainda existe (o arquivo é a verdade enquanto existe) e **mantém** as que sumiram, com `registro_presente = false` e o
`visto_em` da última vez que existiram; membro e departamento delas seguem o `equipe.yaml` de hoje. Pasta dos registros
inexistente = linha `⚠`, 0 execuções lidas e o arquivo inteiro mantido (não é `✗`). Linha que não é JSON (a última da
sessão ativa pode vir cortada) é pulada. A linha do log traz `tokens`, `usd` (pelo TTL), `usd_cache_1.25x` (a conta antiga,
das mesmas colunas), `sem_preco`, `usage_provisorio` (respostas cuja 1.ª linha era provisória) e `arquivadas`. A
passagem de 23/10 21:01 (a 1.ª com a regra da última linha) regravou as 160 execuções presentes; nenhuma estava arquivada,
então nada ficou congelado com o usage provisório (15/09: saída 2.074.080, era 453.986).

**Reconciliar** (`--ate <ISO>`: só as linhas dos registros até esse instante, inclusive; `--ate` e `--regra-do-script`
gravam só num banco de teste — no banco do painel, por qualquer endereço deste Mac, só com `--seco`):
`uv run python painel/trabalho/engenheiro-backend/reconciliar_tokens.py` monta bancos `painel_teste_rec_<pid>_*` e põe lado
a lado, no corte de 23/10 15:02:49.958Z (janela 24/09–23/10):
- **(a)** a regra do script (1.ª linha) × o `tokens-custos.py` com o mesmo corte: **37.699.450 tokens · US$ 536,09**, igual
  em total, modelo, departamento e nos 25 agentes — a leitura é a mesma;
- **(b)** a regra do painel (última linha), o que o banco guarda: **37.909.543 tokens · US$ 539,06** (£ 402,41 a 0,7465);
- **(c)** (b) − (a) = 210.093 tokens · US$ 2,9705 = a soma, contada direto dos `.jsonl`, das 240 respostas da janela cuja
  1.ª linha era provisória (Claude Code 2.1.284/2.1.295/2.1.304; só a saída muda).

O `tokens-custos.py` de referência foi reescrito em 23/10 21:32 (outra sessão): já fica com a ÚLTIMA linha e tem o corte
`2026-10-23T15:02:49Z` embutido. A suíte segue a regra que ele usar (compara o script com o banco do painel quando ele usa
a última linha, e com o `--regra-do-script` quando usa a 1.ª). Diferença que sobra: ele data a resposta pela última linha
e o painel pela 1.ª (1 resposta nos registros reais atravessa a meia-noite UTC). O rascunho `reconciliar_tokens.py` foi
escrito para a versão de 16:41 e recusa rodar com a nova (confere o corte embutido) até ser ajustado.

## Biblioteca (23/10)
O índice dos materiais dos vídeos para a tela Biblioteca (`painel/design/telas/biblioteca.md`). **Só a listagem e o
`stat()`**: nenhum arquivo é aberto nem copiado (os vídeos somam centenas de GB). A passagem leva ~48 ms a mais nesta
parte (dry-run: 1,43 s → 1,48 s; passagem real: 1,52 s → 1,60 s, com as ~700 linhas a mais).

| Tabela / view | Grão | O que é |
|---|---|---|
| `biblioteca_arquivos` | um arquivo | `caminho` (relativo à raiz, chave), `material_id`, `video_slug`, `area` (`material` · `brutos/extras`), `extensao` (minúscula, com ponto), `tipo` (`video` · `imagem` · `documento` · `pesquisa` · `audio` · `outros`), `bytes`, `modificado_em` (mtime), `data_suspeita`, `obra_estudo` |
| `biblioteca_materiais` | um material lógico | `id` (`<slug>:pdf:<arquivo>` · `<slug>:dossie` · `<slug>:pasta:<nome>` · `<slug>:extras` · `<slug>:soltos`), `video_slug`, `grupo`, `nome`, `caminho` (o PDF ou a pasta), **`quem_adicionou_inferido`**, `miniatura` (só o caminho do candidato), `obra_estudo` |
| `biblioteca_materiais_resumo` (view) | um material lógico | + `arquivos`, `bytes` (no PDF só o `.pdf`), `modificado_em` (o arquivo mais novo), `data_suspeita`, `n_video` … `n_outros` — o cartão; "recentes" = `order by modificado_em desc` |
| `biblioteca_por_tipo` (view) | tipo | os 6 tipos, também com zero (`ordem` 1–6): `arquivos`, `bytes` |
| `biblioteca_por_video` (view) | vídeo | `arquivos`, `bytes` (material + cenas extras) e, ao lado, a gravação da câmera: `principal_arquivos`/`principal_bytes` = **o que está no Mac** (os vídeos de `brutos/principal/` no disco, `videos.gravacao_*_no_mac`) e `principal_hd_arquivos`/`principal_hd_bytes` = o que foi para o HD externo (`ARQUIVADO.json`, `videos.gravacao_arquivados*`). Desde 24/10 (migração `20261024055255`): antes, `principal_*` seria o total |
| `biblioteca_referencias` | pasta | `00-marca/referencias` e `painel/referencias`: `arquivos` (não ocultos, em qualquer nível), `bytes` — fora do "Todos" |
| `biblioteca_mais_utilizados` | ativo | `arquivo`, `nome`, `usos`, `unidade`, `regra`, `arquivo_existe` — o uso pela regra do pipeline, **não** um registro de uso |

- **O que entra:** todo arquivo de `videos/<slug>/material/**` e `videos/<slug>/brutos/extras/**` (subpastas incluídas).
  **Fica fora:** pastas de vídeo que começam com `_` ou `.` (a mesma regra da tabela `videos`: `_teste-*` — PI43 — e
  `_modelo`); qualquer nome oculto em qualquer nível (`.DS_Store`, `._*`, `.gitkeep`, pastas ocultas); arquivos de 0
  byte; o que não é arquivo regular.
- **Tipo pela extensão:** vídeo `.mp4 .mov .m4v .mkv .webm .avi` · imagem `.jpg .jpeg .png .webp .gif .heic` · documento
  `.md .pdf .txt .docx` · pesquisa `.json` · áudio `.wav .mp3 .m4a .aac .flac` · o resto é `outros` (hoje: 2 legendas
  `.vtt` da obra do Demis e 1 gráfico `.svg` do Hinton).
- **Material lógico** (regra da designer): cada PDF da raiz de `material/` com os arquivos de `material/_fonte/` (o do
  mesmo nome — `<pdf>-previa.png`; sem par, o 1.º PDF; sem PDF nenhum, `_fonte` vira uma pasta); `dossie.md` +
  `fontes.json`; cada subpasta de `material/`; os outros arquivos soltos na raiz de `material/` ("outros arquivos");
  `brutos/extras/` inteiro ("cenas extras", também `_alternativas/`).
- **Quem adicionou — INFERIDO pela pasta** (o arquivo não guarda autor; PI44): PDF → `produtor-de-material`; dossiê,
  `fotos`, `capas` → `pesquisador-de-material`; `youtube`, `podcast`, `cortes-podcast` → `buscador-de-videos`; `img` e
  `brutos/extras` → `produtor-de-extras`; `obra` → `curador-de-obra`; gravação de tela (`screnn record`) → `carlos` (o
  próprio Carlos, não é agente: não buscar em `agentes`); outras pastas e os soltos → NULL.
- **`material/obra/`** = a cópia de estudo, nunca publicada (CLAUDE.md regra 4): entra no índice com `obra_estudo = true`.
- **Data:** `modificado_em` = mtime. `data_suspeita` = mtime mais de 30 dias antes da data do slug (a mesma regra da
  gravação). Hoje 0 arquivos: os trechos do YouTube têm a hora do download (o yt-dlp não copia a data do vídeo original) e
  nada tem data anterior a 01/09/2026.
- **Mais utilizados:** Voz do Carlos = vídeos com `roteiro.json` (`videos.tem_roteiro`, a mesma definição da Produção — PD25); Look da Korvu v5 (o look ativo, decisão de 18/09) e LUT de
  entrada = vídeos com `videos.gravado`; molde do PDF (`scripts/gerar_material_pdf.py`) = materiais do grupo `pdf`.

**Contra a maquete** (`dados-2026-10-23.json → telas_biblioteca`, lida às 16:22 UTC): 659 arquivos em 12 vídeos,
13.948.839.987 B, por tipo 353/240/41/22/0/3 com os mesmos bytes, os 5 maiores vídeos, 2 + 116 referências, 12/5/5/9 nos
mais utilizados e os 16 materiais mais novos — **iguais**. Diferenças: `brutos/principal/` = 240,05 GB em 29 gravações (a
maquete somava 243,6 GB com as `_teste-*` e qualquer arquivo — PI43); as cenas extras do Hinton contam também
`brutos/extras/_alternativas/E09-ligacao-nobel.mp4` (a maquete somava esse arquivo no total, mas não no material lógico).

## Produção, calendário, desempenho e o original fora do Mac (24/10)
Migração `20261024042911_producao_calendario_e_desempenho.sql`. Tudo lido de arquivo do projeto, só lendo.

| Tabela · coluna / view | De onde vem |
|---|---|
| `videos.tem_roteiro` · `roteiro_versao` · `cta_palavra` · `roteiro_extras` | `videos/<slug>/roteiro.json` (`docs/contratos.md` §1): existe? · `versao` · `cta_palavra` (NULL = CTA sem palavra, ex.: seguir) · `len(extras)` (as cenas extras planejadas). Sem `roteiro.json`, os três NULL |
| `videos.gravacao_prevista` | a data do slug (`AAAA-MM-DD-…`) |
| `videos.nome_curto` | **regra do corte, num lugar só** (era o `tituloVideo` do `web/src/lib/formato.ts`): `videos.tema` (do tracker) antes do primeiro `" — "`, sem espaços nas pontas; sem tema, o slug sem a data com espaço no lugar do hífen. Nem o `roteiro.json` nem o `status.json` têm um campo de título curto (proposta: um `titulo_curto` no roteiro, decisão do Carlos) |
| `videos.gravacao_arquivados` | quantos dos `gravacao_arquivos` vêm do `brutos/principal/ARQUIVADO.json` (ver abaixo) |
| `videos_producao` (view) | Roteiros numa linha por vídeo: os campos do roteiro + `extras_arquivos` (= `biblioteca_materiais_resumo.arquivos` do grupo `extras`: os arquivos de `brutos/extras/`) + `pdf`/`pdf_caminho` (= o 1.º material do grupo `pdf` da Biblioteca: `material/*.pdf`) — sem contar de novo |
| `prontos` | `05-render-pronto/<slug>/pacote.json` (§9): `qa`, `duracao`, `criado_em`, `cta_palavra` (ausente = NULL; fora do formato = `✗`) e o vídeo de origem. `videos.pronto` sai da mesma leitura (QA PASS). Hoje vazio: a limpeza de 23/10 apagou o pacote do ChatGPT contexto |
| `calendario_vagas` | o bloco `vagas_semanais` do `_controle/calendario.md` — o 1.º trecho ` ```yaml ` do arquivo (o mesmo do `publicar.py`): `fuso:` (sem ele, a ordem do `publicar.py`: `TZ_PUBLICACAO` do ambiente e depois Europe/London — mas o `publicar.py` lê o `TZ_PUBLICACAO` do `.env`, que o painel não lê, então a passagem avisa com `⚠` para pôr o `fuso:` no bloco; hoje ele está lá — PD26) e `vagas_semanais:` = mapa dia → `"HH:MM"` ou lista de `"HH:MM"`; dia em português, com ou sem acento e `-feira`; hora sem aspas (YAML 1.1 lê `21:00` como 1260) aceita. Uma linha por vaga: `dia_semana` (ISO 1 = segunda … 7 = domingo), `dia`, `hora`, `fuso`. **Bloco ausente = 0 vagas com `⚠`; bloco quebrado (YAML, dia, hora, repetida, fuso) = `✗`.** Os "melhores horários" ficam de fora (print do app, sem fonte legível) |
| `perfil_snapshots.toques_links_perfil` | `instagram.metricas_conta.profile_links_taps` do snapshot (janela de 28 dias). **Atenção ao rótulo:** pela Meta são os toques nos botões de endereço, ligação, e-mail e mensagem do perfil, não o link da bio |
| `perfil_diario` | `_controle/perfil/diario/AAAA-MM-DD.json` — **proposta**, o `perfil.py` ainda não grava (formato abaixo). Pasta ausente = vazio |

**Original arquivado fora do Mac — `brutos/principal/ARQUIVADO.json`** (`docs/contratos.md` §0; código trazido pela sessão
da limpeza em 23/10 22:42, revisto e testado aqui). A gravação de um vídeo = os vídeos do disco (`.mov`, `.mp4`…, não
ocultos, > 0 byte) **mais** os itens do manifesto com o mesmo filtro, com o tamanho e as duas datas do manifesto (ISO 8601
com fuso → UTC). O nome que está no disco **e** no manifesto conta uma vez, pelo `stat()` do disco; o "mesmo nome" não
diferencia maiúsculas nem a forma Unicode (NFC × NFD). O manifesto tem de trazer `arquivos` (≥ 1) com `nome` (caminho
dentro de `brutos/principal/`), `bytes` (inteiro ≥ 0), `sha256` (64 hexadecimais — a prova da cópia), `mtime` e `ctime`
com fuso; nome repetido ou qualquer campo fora disso = `✗`. Ausente = só o disco.
- **As datas valem até o SEGUNDO** (24/10, S1-1 do PORTÃO-DADOS): `gravacao_ultima` e `gravacao_chegou` são truncadas para
  o segundo, as do disco e as do manifesto. O escritor real (`scripts/limpeza/finalizar_g3.py:8`) grava
  `isoformat(timespec="seconds")` e o painel não precisa da fração: assim o antes e o depois de os `.MOV` saírem ficam
  iguais para qualquer escritor. Os valores mudaram menos de 1 s, uma vez, na passagem de 24/10.
- **No Mac × no HD** (S1-2): `videos.gravacao_arquivos`/`gravacao_bytes` continuam a ser o total (é o que faz o vídeo
  continuar "gravado" na Produção); `gravacao_arquivos_no_mac`/`gravacao_bytes_no_mac` = o disco; `gravacao_arquivados`/
  `gravacao_arquivados_bytes` = o HD. A Biblioteca (Armazenamento, "como o Finder") usa o que está no Mac.
- **Prova com os vídeos reais** (só `stat`, nenhum `.MOV` aberto; o manifesto no formato exato do `finalizar_g3.py`: o nome
  sem pasta, segundos UTC): o Hassabis (10, com o `camera-00-cor.mov`) e o Hinton (9) ficam idênticos nos 6 campos antes
  (disco), depois (só manifesto) e na transição (manifesto + parte dos `.MOV`, com o nome em minúsculas) —
  `painel/trabalho/engenheiro-backend/prova_arquivado.py`. A Biblioteca não o conta (`brutos/principal/` não é material).

**Proposta para o `scripts/perfil.py`** (não mexido — só o painel está pronto para ler): um modo diário (ex.:
`perfil.py --diario`, no launchd das 09:30) que grava `_controle/perfil/diario/<ontem UTC>.json`:
`{"dia": "AAAA-MM-DD", "lido_em": "<ISO com fuso>", "metricas": {"reach": 41, "views": 230, "accounts_engaged": 5,
"total_interactions": 9, "profile_views": 3, "profile_links_taps": 0, "follows_and_unfollows": null, "seguidores": 3640}}`.
Cada métrica com `period=day`, `metric_type=total_value`, `since`/`until` = o dia UTC inteiro (só o `reach` aceita
`time_series`, o resto só `total_value` — documentação da Graph API, Instagram User Insights); `seguidores` =
`followers_count` da conta na hora da leitura; `null` = a Meta não devolveu (ela manda vazio, não 0). Um arquivo por dia,
nunca reescrito (`--desde AAAA-MM-DD` para preencher os dias para trás, um arquivo por dia; a Meta guarda ~90 dias).

## O modelo que rodou, por agente (24/10)
Decisão do Carlos de 24/10 (`docs/decisoes.md` §5): a Equipe mostra o modelo que **rodou**, não o declarado. View
`modelo_por_agente` (migração `20261024213122`), sobre o `consumo` que já está no banco:

| Coluna | Significado |
|---|---|
| `agente_id` | `agentes.id` (= `execucoes.membro_id`). A sessão principal e os ajudantes (general-purpose, workflow-subagent, claude, Explore, Plan) contam como `diretor`: a mistura do Atlas inclui os ajudantes |
| `modelo_declarado` | `agentes.modelo` — o `model:` de `.claude/agents/*.md` (o diretor = `opus`), para comparar com o que rodou |
| `modelo`, `modelo_nome` | o modelo que rodou na janela (`claude-opus-5-5`, "Opus 5.5"…); **NULL** = o agente não rodou nos 30 dias |
| `tokens`, `usd`, `execucoes` | na janela, daquele agente com aquele modelo (`execucoes` = `.jsonl` distintos) |
| `pct_tokens` | % dos tokens do agente na janela (somam 100 por agente; NULL na linha sem modelo) |
| `ultima_execucao` | o `fim` mais recente das execuções daquele agente com aquele modelo, na janela |
| `ultima_execucao_geral` | o `fim` mais recente de sempre, também das arquivadas (`registro_presente = false`) |
| `nunca_rodou` | nenhuma execução em `execucoes`, nunca — separa "rodou, mas não nos 30 dias" (`modelo` NULL e `nunca_rodou` false) de "nunca rodou" |

**Janela:** os 30 dias UTC até hoje, inclusive (de hoje − 29 a hoje), com hoje = `(now() at time zone 'UTC')::date` — o
banco do painel roda em UTC, então é o `current_date`. Todo agente de `agentes` aparece. Conta o que tem preço
(`consumo`), inclusive as execuções arquivadas. `set painel.hoje = 'AAAA-MM-DD'` na sessão fixa o "hoje" (só testes e
reconciliação). Libras e projeção ficam no app (nenhuma view usa a `cambio`).

## Biblioteca nova: o acervo de estilos (24/10)
Decisão do Carlos de 24/10 (`docs/decisoes.md` §5): a Biblioteca é o **acervo de estilos** (looks, capas, legendas,
fontes, animações, armazenamento, a stack), não arquivo de material. Tela: `painel/design/telas/biblioteca.md` — os nomes
seguem os blocos dela. Migração `20261024215907`. As tabelas `biblioteca_*` de 23/10 ficam (a tela nova usa a
`biblioteca_arquivos` só no armazenamento). Leitura **estrita**: o que não se lê sem adivinhar fica NULL e, quando é
anomalia, vira uma linha ⚠ no log; arquivo que não se lê (JSON/YAML quebrado, tipo errado no `biblioteca.yaml`) = ✗.
Formato do `biblioteca.yaml`: `docs/contratos.md` §12.

| Tabela / view | Fonte | O que é |
|---|---|---|
| `looks` | `00-marca/cor/luts/korvu-look-vN.json` do **topo** (`_descartadas/` fora) + `entrada-camera.*` + `00-marca/cor/cor.md` (+ o rosto do `biblioteca.yaml`) | `id` (`vlog` · `rec709` · `vN`), `ordem`, `tipo` (`referencia` · `base` · `look`), `nome`, `aprovada`, `aprovada_em`, `criado_em` (a data como está escrita), `ficha` (o .json inteiro), `cube` + `cube_sha256`; **`papel`** `em_uso` (= `versao_ativa`), `alternativa` (= `alternativa_medida`) ou `arquivado` (= está em `arquivados: [vN]`; 24/10: o v4) — NULL sem chave ou com duas ao mesmo tempo (conflito: ⚠), com `chaves_cor_md` e `linhas_cor_md` (de onde saiu; a antiga `alternativa:` não é lida, ⚠ se voltar); **`nome`** (o do `biblioteca.yaml` vence o do `.json`), **`descricao`** (a frase do cartão) e **`rosto_ire`** (+ `_em`, `_amostra`), do item do cartão na seção `looks` do `biblioteca.yaml` (a tabela do `cor.md` não é mais lida; sem item = NULL); `previa` / `previa_esperada` |
| `capa_estilos` + `capa_estilos_exemplos` | `painel/biblioteca.yaml` → `capas` | estilo (`id`, `nome`, `descricao`, `ficha`, `ficha_existe`, `em_uso`) e as capas reais: `<pasta>/<slug>/capa/capa.png` na 1.ª de `07-publicados`, `06-publicar`, `05-render-pronto` que a tiver, + o `video_slug` de origem |
| `legenda_estilos` | `biblioteca.yaml` → `legendas` | idem, sem exemplos (a amostra é desenhada pela tela a partir da ficha) |
| `fontes` | `biblioteca.yaml` → `fontes` | `familia`, `estilo`, `pesos`, `uso`, `reserva`, `remotion` (o pacote) e **`confere_brand_ts`** (o `remotion/src/brand.ts` carrega o pacote com o mesmo estilo e pesos) |
| `sistema_ferramentas` | `biblioteca.yaml` → `ferramentas` | `nome`, `tipo`, `descricao` (o `desc:` do yaml; `desc` é palavra reservada no SQL) — textos à letra do canvas —, `versao` **lida** do arquivo de `versao_de` (package.json#pacote, config.toml#chave, 1.ª linha) |
| `modelos_descricao` | `biblioteca.yaml` → `modelos` | `modelo` (o id dos registros), `descricao` (o `desc:`), `com_preco` (está na tabela de preços; sem preço = ⚠, a frase não aparece) |
| `animacoes` | `videos/<slug>/animacoes/<Exx>/brief.md` | `titulo`, `linhas`, `modo`, `duracao_s`, `video_do_brief` do cabeçalho (antes do 1.º `---`); **`renderizada`** = há `.mp4` em `edicao/extras/<Exx>.mp4`, `brutos/extras/<Exx>.mp4` ou `<Exx>-*.mp4`, ou dentro de `animacoes/<Exx>/` (o caminho em `mp4`); sem = roteirizada |
| `sistema_contagens` | `.claude/` | `agentes` (.md no topo de `agents/`), `habilidades` (pastas de `skills/` com `SKILL.md`), `comandos` (.md de `commands/`); nome com `.` ou `_` na frente fica fora |
| `armazenamento` (view) | `biblioteca_por_video` | uma linha: `gravacoes_mac_bytes`, `material_mac_bytes`, `mac_bytes`, `hd_bytes` (+ arquivos), `hd_videos`, `lido_em`. O HD externo não aparece no painel (Carlos, 25/10: foi só a cópia de segurança); as colunas `hd_*` ficam porque a gravação continua contando o original arquivado (`ARQUIVADO.json`, `sha256` obrigatório) |
| `sistema_modelos` (view) | `modelo_por_agente` + `modelos_descricao` | por modelo, 30 dias UTC: `tokens`, `pct_tokens` (do total), `usd`, `execucoes`, `agentes`, `descricao` (a frase; NULL = sem frase) |

**Prévias dos looks** (`painel/sync/previas_looks.py`, separado: o sincronizador só faz o `stat()`). Um JPEG 640×800 por
look em `painel/previas/looks/<id>-<hash>.jpg`, do quadro `00-marca/cor/amostras/praq0967/praq0967-121.00s.mkv`
(`-noautorotate`, `transpose=1`, recorte 4:5 a 12% do alto; yuv → RGB como o pipeline de cor, `in_range=pc`; +
`entrada-camera.cube`; + `korvu-look-vN.cube`, sem primária). O hash = receita + amostra + cada `.cube`: só gera o que
mudou e apaga a versão anterior. `uv run python painel/sync/previas_looks.py [--seco]` (ffmpeg de `FFMPEG_BIN` ou do PATH).
Testes: `uv run python painel/tests/test_previas_looks.py` (amostra sintética e `.cube` de 2³).

**Crescer só por arquivo** (decisão de 24/10): um look novo = `korvu-look-vN.cube` + `.json` no topo de `luts/` (a
prévia: rodar o gerador, que faz só a dele); um estilo de capa ou de legenda, uma fonte, uma ferramenta = uma entrada no
`biblioteca.yaml`; uma animação = um `brief.md` em `videos/<slug>/animacoes/<Exx>/`. Nada de código nem migração (o
`test_sincronizar.py` prova numa raiz temporária). Conferência do yaml REAL contra o canvas, o `brand.ts` e o
sincronizador: `uv run python painel/tests/test_biblioteca_yaml.py` (só leitura).

## Quem constrói o painel (departamento de tecnologia, 22/10)
| Quem | Agente | O que faz |
|---|---|---|
| Lia Monteiro | `designer-de-produto` | referências (`painel/referencias/`) → design system e maquetes em `painel/design/` |
| Gabriel Torres | `engenheiro-frontend` | implementa em `painel/web/` o que foi aprovado |
| Mateus Pacheco | `engenheiro-backend` | banco (`painel/supabase/`), sincronizador (`painel/sync/`), testes (`painel/tests/`) |
| Camila Freitas | `portao-interface` | gerente · portão das áreas **design** e **interface** |
| Sérgio Lemos | `portao-dados` | portão dos dados (banco + sincronizador) |

GAUNTLET (`docs/gauntlet.md`): nada do painel chega ao Carlos sem `uv run python scripts/portoes.py exigir painel` limpo.
Para olhar as telas: `bash painel/capturar.sh <pasta> [rotas]` (1440 e 375 px). Briefing do redesign e referências do
Carlos: `painel/referencias/` (`BRIEF.md`). Capturas e rascunhos de quem constrói: `painel/trabalho/<agente>/`.
Banco de teste: `create database painel_teste` no mesmo Postgres → migrações → sincronizar com `PAINEL_DB_URL` → `drop`.

## Páginas
Menu (decisão de 23/10): Visão geral · Equipe · Produção de conteúdo · Calendário · Desempenho · Biblioteca · Tokens e custos. Topo: busca (⌘K), avisos (portões que pedem ação) e "Carlos · Proprietário".
- **visão geral** — seguidores, alcance, fora da bolha, o que precisa de atenção nos portões, próximas publicações, os gerentes.
- **equipe** — organograma por departamento (gerente = portão), ficha de cada um (função, modelo, skills, comandos, quem fiscaliza quem, veredictos), **contratar** (gera o pedido para o Claude criar o agente já ligado ao portão).
- **produção de conteúdo** (`/producao`; `/videos` redireciona) — etapa de cada vídeo + estado dos 4 portões; fila com o portão da publicação. As 5 fases (Roteiros → Publicados) entram com o desenho aprovado.
- **calendário**, **biblioteca**, **tokens e custos** — rota com o estado vazio "Esta tela chega em breve" até o desenho de cada uma ser aprovado (sem dado inventado).
- **desempenho** — seguidores, alcance fora da bolha, países/cidades/idade, ranking dos Reels, o que funciona (trial × normal, pilar, duração).

## Limites dos dados (hoje)
- Seguidores por país e a evolução dos seguidores dependem das fotos do `scripts/perfil.py` (só 16/10 e 22/10 até agora).
- A API da Meta não dá a curva de retenção, só o tempo médio; leitura impossível (tempo médio > duração) aparece como "?".
- Subir para um domínio: criar um projeto Supabase na nuvem, `supabase db push`, trocar `web/.env.local` e pôr login antes de abrir.
- **Custo de IA = equivalente no preço de tabela da API**, não a fatura da assinatura do Claude. Guardado em US$; a tela
  mostra em £ pela taxa de `painel/cambio.yaml`. Converter o valor exato e arredondar só no fim (a conta antiga:
  US$ 482,1353 × 0,7465 = £ 359,91; arredondar os dólares antes dá £ 359,92).
- **ElevenLabs fora** (transcrição e música não têm medição de tokens/custo no projeto).
- **Dia = data UTC** do `timestamp` da resposta: no horário de verão de Londres, uma resposta à 00:30 conta no dia
  anterior (23:30 UTC).
- Modelo sem preço na tabela não entra em custo nem em tarefa (hoje só `<synthetic>`): pôr o preço em `PRECOS` faz contar,
  inclusive no arquivo. O que o Claude Code apagou antes de 23/10 (setembro, salvo 15–19/09) não volta.
- Vídeo de uma execução: só pelas pastas citadas no 1.º pedido (regra acima); "Slug: `…`" sem pasta fica sem vídeo
  (US$ 11,60 em 23/10 — `painel/trabalho/engenheiro-backend/regra-video-antes-depois-2026-10-23.txt`).
- **Não seguidores por Reel:** a API não dá. Em `GET /{ig-media-id}/insights` o `reach` não tem quebra nenhuma (as únicas
  são `action_type`, só para `profile_activity`, e `story_navigation_action_type`, só para `navigation` — documentação
  da Graph API, Instagram Media Insights); os `07-publicados/*/metricas.json` reais também não trazem. O `follow_type` só
  existe no alcance da CONTA (`perfil_snapshots.alcance_seguidores`/`alcance_nao_seguidores`).
- Data da gravação: a dos arquivos vem do relógio da câmera (2024 nos PRAQ*.MOV) — `gravacao_data_suspeita`; a chegada
  ao projeto (`gravacao_chegou`) é o ctime, que também muda se o arquivo for renomeado ou tiver permissões trocadas.
