# Tokens e custos — `/tokens`

> **O Carlos abre isto para** ver quanto a operação de IA consome, onde consome, quem consome e quanto isso custa em
> dólar (preço de tabela da API).

- Maquete: `tokens-e-custos.html`. Fonte do desenho: `painel/referencias/claude-design/telas-2026-10-23/Tokens.dc.html`
  (e a conta em `tokens-custos.py`, na mesma pasta).
- Decisões do Carlos: **tokens em destaque laranja** (`accent-ink` pequeno, `accent` ≥ 24 px) e **modelo sempre com a
  versão** (23/10); **custo em US$, a moeda da tabela da Anthropic, sem câmbio** e **projeção pelos últimos 30 dias**
  (24/10, substituem a decisão de 23/10 em £ e a projeção de 7 dias); **sem título de página** (24/10).
- Componentes: livro §15.2 (KPI em linha, segmentado, barras finas larga, ranking, capa, destaque, tokens) e §11.18.

## Fonte e conta — tudo real, retrato com hora de corte
- Registros das sessões do Claude Code deste projeto: `~/.claude/projects/-Users-teste-Documents-CONTENT-AI/**/*.jsonl`
  (`message.usage` + `message.model` por resposta; subagentes: `subagents/agent-*.meta.json → agentType`).
- Cada resposta conta pela **última linha** do seu `message.id` (as primeiras são provisórias) e cai no dia da **1.ª
  linha**, como o banco (PD21).
- Tokens = entrada + cache gravado + saída. Custo = preço de tabela da API em US$ (Opus 5.5 4/20 por milhão, Sonnet 5.5
  2/10, Fable 5.1 10/50; cache gravado 1,25× a entrada por 5 min e **2× por 1 h**; cache lido 0,20/0,25). Sem câmbio.
- Tarefa = uma sessão (execução) com consumo. O **Atlas** soma a sessão principal e os ajudantes (`general-purpose`,
  `workflow-subagent`, `claude`, `Explore`, `Plan`). Vídeo = subagente cujo 1.º pedido cita `videos/<slug>` (só os slugs
  que existem em `videos/`; o Atlas não entra).
- **Corte: 23/10 às 16:02:49 (Londres)**, o mesmo do banco: **37,9 M tokens (37.909.543), US$ 539,06**; + 1,1 bilhão de
  tokens lidos do cache (fora do total, com custo baixo).
- Refeita só lendo em `painel/trabalho/designer/tokens/ler_tokens.py`; o bloco é `dados-2026-10-23.json → telas_tokens`
  (o `telas_cambio` saiu em 24/10).
- **No painel o número vem do banco** (`handoff.md` §8). ElevenLabs (transcrição e música) fica de fora: sem medição.

## Hierarquia e dados
1. Sem título (o `h1` "Tokens e custos" só para leitor de tela). No alto, à direita, o período e a hora da leitura: "24 set –
   23 out · registros das sessões do Claude Code · leitura de 23 out, 16:02 · custo em US$, preço de tabela da API".
2. Números: **Tokens utilizados 37,9 M** (`accent`) "+ 1,1 bilhão lidos do cache" · **Custo estimado US$ 539** "equivalente
   na API, preço de tabela" · **Agentes 26** "21 trabalharam nos 30 dias" · **Custo médio por agente US$ 25,67** "entre os
   21 que trabalharam".
3. **consumo.** (8 colunas): por dia, Tokens | Custo (segmentado). Dia sem sessão = 0. Pico marcado: "23 out · 8,7M" /
   "23 out · US$ 119,90" (eixo do custo 0–120). Nota: a conta e "com assinatura, a fatura é outra".
4. **por modelo.** (4 colunas): rosca de 3 fatias (Opus 5.5 83 % · Sonnet 5.5 12 % · Fable 5.1 5 % dos tokens), cada uma com
   o custo em US$ (435,21 · 23,57 · 80,28) e o % do custo (81 %, 4 %, 15 %); "O Fable 5.1 é 5 % dos tokens e 15 % do custo."
5. **por departamento.**: 7 linhas (Direção (Atlas) 23,7M · US$ 401,81 · 62,4 % … Distribuição e dados 311,7K · US$ 1,84 ·
   0,8 %) + o destaque "A direção … responde por 62 % dos tokens e 75 % do custo. O roteiro fica com 6 %."
6. **custo por vídeo.**: Geoffrey Hinton US$ 32,26 · Livro ChatGPT US$ 6,53 · Demis Hassabis US$ 3,77 · Golpes com IA
   US$ 2,40 · Fei-Fei Li US$ 2,12 (com a capa; "só o trabalho dos especialistas…").
7. **Projeção mensal**: **US$ 539** = média dos **últimos 30 dias** (US$ 17,97 por dia; dia sem sessão conta como zero) × 30.
   "É estimativa: a mensalidade já está paga." Sem delta (a conta de 30 dias contra os mesmos 30 dias não compara nada).
8. **quem mais consome.** (Gerentes | Ranking geral): #, Agente (foto/iniciais, departamento · portão), **Rodou em** (o
   modelo dos registros; o Atlas rodou em Opus 5.5 e Fable 5.1), Tokens (`accent-ink`), Custo (US$), Tarefas, Por tarefa.
   Quem não rodou: "—" e "não rodou" (Vera, Íris e Henrique: os portões começaram em 22 out).

A 1440, "quem mais consome" vai para o fim, na largura toda; a partir de 1600, departamento 4 + quem consome 5 + vídeo e
projeção 3, como o artboard (livro §15.4).

## Interações
Tokens | Custo troca a série e a frase; Gerentes | Ranking geral troca a tabela; hover e foco por dia com a dica; "Ver os
números" em todo gráfico (custo em US$); o nome do agente leva à ficha; o vídeo leva à publicação.

## Estados
| Bloco | Vazio | Carregando | Erro |
|---|---|---|---|
| Números | "Nenhuma sessão nos últimos 30 dias" | esqueleto de KPIs | `k-note--alert` + "Tentar de novo" |
| consumo. | "Nenhum dia com consumo" | esqueleto de gráfico | idem |
| por modelo / por departamento | "Sem consumo para dividir" | esqueleto de gráfico | idem |
| quem mais consome | "Ninguém rodou ainda" | esqueleto de tabela | idem |
| custo por vídeo | "Nenhum pedido citou um vídeo" | esqueleto de lista | idem |

## 375 px
KPIs em uma coluna; gráficos na largura do card; departamentos em duas linhas cada (nome e números; a barra embaixo);
as tabelas rolam dentro do card. `scrollWidth` 375 conferido.

## Do artboard para a maquete
| No artboard | Na maquete | Motivo |
|---|---|---|
| Coluna "Modelo" (o configurado) | "Rodou em" (o dos registros) | o custo é do modelo que rodou; para Otávio e Clara eles diferem |
| "37,7 M · US$ 482" (1.ª versão) | "37,9 M · US$ 539" | cache de 1 h a 2× (23/10), última linha de cada resposta e o corte do banco (PD21), custo em US$ (24/10) |
| Seletor "Últimos 30 dias" | o período escrito | só existe a janela calculada |
| Três blocos lado a lado a 1440 | quem consome no fim, na largura toda | a tabela tem 7 colunas (livro §15.4) |
| "Custo subindo" só na cor | a seta e a palavra na dica ("o custo está subindo") | nada só por cor |

## Dúvidas para o Carlos
- Respondidas em 24/10: custo em US$ sem câmbio; projeção pelos últimos 30 dias. Nenhuma aberta.
