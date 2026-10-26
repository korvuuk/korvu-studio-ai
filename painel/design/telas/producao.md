# Produção de conteúdo — `/producao` (era `/videos`)

> **O Carlos abre isto para** ver em que fase está cada conteúdo — roteiro, gravado, pronto, agendado ou publicado — e o
> que precisa da atenção dele.

- Maquete: `producao.html`. Fonte do desenho: `painel/referencias/claude-design/telas-2026-10-23/Producao.dc.html`.
- Decisão do Carlos (23/10, `docs/decisoes.md` §5): o menu "Vídeos e portões" vira **Produção de conteúdo**, com 5 fases
  separadas; roteiro só vira vídeo depois de gravado; portão é detalhe da fase; vale para Reels, Stories e Carrossel; em
  cada publicação aparece **onde saiu ou vai sair (Instagram · Facebook · LinkedIn)**, com link para o post.
- Componentes: livro §15.2 (fases, canal, palavra, capa, filtro, chip pequeno) e §11.3/§11.12 (mapa de estados).
- **Mapa de estados × fases: livro §15.1** — é a regra desta tela. Resumo abaixo.

## Hierarquia
1. **sem título de página** (decisão de 24/10: o item do menu já diz onde se está; o `h1` "Produção de conteúdo" fica só para leitor de tela); só "Buscar conteúdo…" numa barra fina. Sem "Novo conteúdo" (24/10).
2. Formato (Todos · Reels · Stories · Carrossel) e a fonte ("Lido de `videos/`, `05-render-pronto/`, `06-publicar/` e
   `07-publicados/` · sincronizado em …").
3. As 5 fases com os elos ("você grava", "pós e QA", "você agenda", "publica no horário"). A fase escolhida abre a tabela.
4. Tabela da fase (à largura toda a 1440; 9 colunas a partir de 1600).
5. Precisam de atenção · Portões (lado a lado a 1440; à direita da tabela a partir de 1600).

## As fases (contagem de 23/10)
| Fase | Hoje | Meta do cartão | Está aqui quando |
|---|---|---|---|
| Roteiros | 7 | "6 com PDF · o mais antigo espera desde 17 set" | `videos/<slug>` com `roteiro.json` e `brutos/principal/` vazio |
| Gravados | 0 | "Nenhum em edição agora" | tem gravação e ainda não tem pacote |
| Prontos | 1 | "ChatGPT contexto · teste, não sai" | `05-render-pronto/<slug>` (QA PASS) fora da fila |
| Agendados | 5 | "3 vídeos · próxima sáb 24 out, 19:00" | `06-publicar/<slug>` |
| Publicados | 5 | "4 vídeos · melhor: Demis Hassabis" | `07-publicados/<slug>` |
Roteiros, Gravados e Prontos contam **vídeos**; Agendados e Publicados contam **posts** (o Livro ChatGPT tem 1 publicado e
3 na fila).

## Tabelas — colunas, dados e a coluna de portão de cada fase
**Roteiros** — Roteiro (ícone `documento`, nome curto, slug) · Formato (Reels) · Versão (`roteiro.json.versao`) ·
Palavra-chave (`cta_palavra`; sem palavra "—", ex.: Jacob Coxon tem CTA de seguir) · PDF ("Pronto" se há
`material/*.pdf`) · Cenas extras ("5 de 20" = arquivos em `brutos/extras/` de `len(roteiro.extras)`) · **Portão do
roteiro** (chip do mapa único: hoje "Ainda não rodou" nos 7; a dica mostra também a pauta) · Gravação prevista (data do
slug + "há 36 dias"/"amanhã") · Atualizado (`status.json.atualizado`). Ordem: gravação prevista.

**Gravados** — Vídeo (capa) · Gravado em · Pós-produção (`k-steps` Corte → Cor → Gráficos → Áudio → Capa → QA, pelo
`status.json.estado`) · **Portão da imagem** · **Portão do corte** (um chip do mapa único cada) · Responsável (sem fonte:
fica fora até existir) · Atualizado. **Hoje vazio** → `k-empty` "Nada em edição agora" + "Os próximos a entrar aqui são os
7 roteiros…".

**Prontos** — Vídeo · Duração (`pacote.duracao`) · Palavra-chave · QA ("QA aprovado": o pacote só existe com QA PASS) ·
Pacote criado · **Portões do vídeo** (o pior dos 4 portões do vídeo, com o nome: hoje "Ainda não rodou · roteiro e mais
2"; a pauta do ChatGPT contexto é "não se aplica") · Observação · ação. O ChatGPT contexto: **"Teste de cor · não sai"**
("não sai" em `danger`) e **sem** a ação de agendar — trava escrita à mão (`_controle/CONTINUAR.md`), não portão; por isso
não é "Bloqueado". Sem coluna de ação: agendar é `/publicar` no Claude Code (24/10). Nota no pé da tabela.

**Agendados** — Publicação (capa, nome, slug) · Data e hora ("Sáb 24 out · 19:00" + "amanhã") · **Onde vai sair**
(Instagram · Facebook · LinkedIn: hoje só Instagram nos 5; os outros tracejados, "não vai sair" para leitor de tela) ·
Modo (Normal / Trial Reel) · Palavra-chave · **Portões** (a linha "Portões:" do livro §11.12: hoje "Legado · sem selo" nos 5)
· **Estado** (família 3: Agendado; "Bloqueado" se um portão do vídeo de origem estiver bloqueado, escalado ou vencido —
vem antes de Agendado). Ordem: data.

**Publicados** — Publicação · Publicado em · Modo · Duração · Alcance (o maior em `accent-ink`) · Visualizações ·
Curtidas · Salvos (`metricas.json → ultima.resumo.instagram`) · **Onde foi publicado** (cada canal é link para o post:
`post.json → instagram.permalink`, `facebook.permalink`; LinkedIn tracejado — os Reels não vão para lá hoje). O Livro
ChatGPT A (22 out) ainda não tem leitura: "lê em 27 out". Pé: "última leitura em 22 out, 14:00; a leitura completa sai 5
dias depois de cada post". Ordem: mais recente primeiro. Se um portão do vídeo vencer depois de publicado, o chip vai ao
lado do nome (PI40) — o "publicado" nunca some.

## Lado
- **Precisam de atenção** (contagem em chip): os avisos do livro §15.1 — "7 roteiros esperando gravação" (o mais antigo e o
  próximo), "Pronto, mas não vai ao ar" (`k-note--alert`), "Portão do roteiro ainda não rodou". Cada um com uma ação de
  navegar ("Ver roteiros", "Ver prontos"). É a mesma lista do sino.
- **Portões** (5 áreas): contagem por estado, com as palavras do mapa único — Pauta "10 ainda não rodaram · 2 não se
  aplicam" · Roteiro "12 ainda não rodaram" · Imagem "10 · 2" · Corte "5 · 7" · Publicação "5 legado · sem selo". Fonte:
  `portoes_estado` (`alvo` `videos/%` e `06-publicar/%`), com o legado vindo de `fila.legado`.

## O que o banco ainda não dá (engenheiro-backend; só registrado)
- **PI39**: a linha "Portões" de Agendados precisa da **origem** de cada post e do **selo** (`fila.origem`, `fila.selado`).
- A fase precisa de "tem gravação" (`brutos/principal/`) e "tem pacote" (05/06/07) por vídeo.
- Publicados entram no banco só com o `metricas.json`: o Livro ChatGPT A não está em `publicacoes` — ler o `post.json`.
- A trava "não publicar" precisa de campo (`status.json`/`pacote.json`: `nao_publicar` + motivo).
- Nome curto do conteúdo (hoje sai do slug) e o formato (Reels/Stories/Carrossel) por conteúdo.
- Link do LinkedIn por post (`post.json → linkedin.permalink`), quando o LinkedIn publicar.

## Interações
- Fase: os cartões são botões (`aria-pressed`, `aria-controls` na tabela). Formato Stories/Carrossel: `k-empty` "Nenhum
  story ainda. Hoje a operação produz Reels…". Busca: filtra as linhas pelo nome e slug; sem resultado: "Nada encontrado
  nesta fase. Limpe a busca ou escolha outra fase."
- Sem botões que criam coisas (24/10): vídeo novo e agendar são pedidos no Claude Code.

## Estados
| Bloco | Vazio | Carregando | Erro |
|---|---|---|---|
| Fases | "Nada em produção" | esqueleto dos 5 cartões | `k-note--alert` + "Tentar de novo" |
| Tabela da fase | frase da fase (Gravados: "Nada em edição agora"…; Prontos: "Pacote pronto espera aqui até você agendar") | esqueleto de linhas com capa | idem |
| Precisam de atenção | "Nada pede atenção agora" | esqueleto de lista | idem |
| Portões | "Nenhum portão no banco" | esqueleto de lista | idem |

## 375 px
Fases em lista vertical (número à direita, elo com seta para baixo); a tabela rola **dentro** do card (região com nome,
`tabindex=0`); avisos e portões em uma coluna. `scrollWidth` 375 conferido.

## Do artboard para a maquete
| No artboard | Na maquete | Motivo |
|---|---|---|
| "Pendente" com círculo cinza | chip "Ainda não rodou" (mapa único) | um desenho por estado (livro §11.3) |
| "Legado" | "Legado · sem selo" | palavra do mapa único |
| Observação em chip vermelho "Teste de cor · não publicar" | "Teste de cor · não sai" com "não sai" em `danger` | vermelho em chip = Bloqueado (portão); trava manual usa o "não sai" do calendário |
| Botão "Agendar" desativado | sem ação nessa linha | o pacote não sai; botão desativado sem explicação não ajuda |
| "2 prontas" | "2 de 2" | mostra o que falta (extras planejadas no roteiro) |
| Caixa tracejada explicando Prontos | nota no pé da tabela | caixa tracejada é o estado vazio no sistema |
| "Pedir revisão" | "Ver roteiros" | o painel só lê |
| Tabela 9 colunas ao lado dos avisos a 1440 | largura toda a 1440 | a tabela de roteiros não cabia (livro §15.4) |
| Meta dos cartões cortada (altura fixa) | altura livre | o texto sumia |

## Dúvidas para o Carlos
- "Teste de cor · não sai" no ChatGPT contexto: quer que esse pacote saia de `05-render-pronto/` (vá para um arquivo
  morto), ou que fique em Prontos com a trava?
