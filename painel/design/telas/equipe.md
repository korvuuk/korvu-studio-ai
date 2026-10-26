# Equipe — `/equipe`

> **O Carlos abre isto para** ver quem é quem por departamento, quem é portão, com que modelo cada um trabalha e quanto
> cada um consumiu nos últimos 30 dias.

- Maquete: `equipe.html`. Fonte do desenho: `painel/referencias/claude-design/telas-2026-10-23/Equipe.dc.html`.
- Componentes: livro §11.6–11.8, §15.2 (filtro, KPI em linha, direção, pessoa do departamento, tokens).

## Hierarquia
1. **Sem título de página** (decisão de 24/10: o menu já diz onde se está; o `h1` "Equipe" fica só para leitor de tela).
   No alto, só "Buscar agente…". **Sem "Adicionar agente"** (decisão de 24/10: o painel só informa; contratar é no Claude
   Code).
2. Filtros (Todos · Ativos · Portões · Opus 5.5 · Sonnet 5.5 · Ainda não rodou, com contagem — pelo **modelo que rodou**) e
   a legenda: status + "modelo, consumo e tarefas: 30 dias, registros do Claude Code (o modelo é o que rodou) · custo em
   US$, preço de tabela da API". Sem câmbio (decisão de 24/10, que substitui a de 23/10 em £).
3. Quatro números: Agentes 26 ("rodaram em Opus 5.5: 10 · Sonnet 5.5: 11 · ainda não: 5") · Departamentos 6 (mais a
   direção) · Portões 7 · Tokens · 30 dias 37,9 M (US$ 539 equivalente na API; leva a Tokens e custos).
4. Direção: o Atlas.
5. Seis departamentos, um cartão cada, gerente primeiro.

## Dados
| O quê | Fonte |
|---|---|
| Nome, função (cargo antes do " · "), departamento, papel, resumo | `agentes` (do `painel/equipe.yaml`) + `departamentos` |
| Modelo **que rodou**, com a versão (decisão de 24/10) | registros do Claude Code, 30 dias: o modelo de cada resposta do agente (`message.model`), o principal pelos tokens; com mais de um, a fatia do principal e "+N"; sem registro, "ainda não rodou". **Não** é o `agentes.modelo` configurado: quem escolhe o modelo são os orquestradores, pela tarefa. Os 11 que rodaram em Sonnet 5.5 passaram a Opus em 24/10 — aparece quando rodarem de novo |
| Portão (chip/linha "Portão da pauta") | `agentes.papel = 'portao'`; o nome do portão é o fim do cargo ("gerente de pesquisa · portão da pauta") |
| Gerente (linha destacada) | `departamentos.gerente_id` |
| Foto | `painel/web/public/equipe/<id>.jpg`; sem foto, iniciais |
| Tokens, custo (US$) e tarefas por pessoa · 30 dias | registros do Claude Code (livro §15.3): por `agentType`; o Atlas soma a sessão principal e os ajudantes. Ex.: Atlas 23,7 M · US$ 401,81 · 45 tarefas. Corte 23/10 16:02:49, o mesmo do banco (PD21) |
| Soma por departamento ("1,8M tokens · US$ 11,33") | soma das pessoas do departamento |
| "Rodou em" (cartão do Atlas) | modelos que aparecem nos registros (Opus 5.5 e Fable 5.1) |
| Status "Ativo agora / Em espera" e o filtro "Ativos 2" | **exemplo** (Atlas e Lia Monteiro no artboard) |

**No app, até existir presença:** sem a coluna Status, sem o filtro "Ativos" e sem a legenda do status. De onde viria:
sessão do Claude Code com resposta nos últimos minutos (engenheiro-backend).

## Direção (cartão do Atlas, `k-direcao`)
Foto 72, "Direção", nome + "Claude principal", "Diretor de operações", o resumo do `equipe.yaml` ("Recebe o
pedido do Carlos, aciona os especialistas e os portões, e só entrega com tudo aprovado.") e os números: Status
(**exemplo**) · Tarefas · 30 dias 45 · Tokens · 30 dias 23,7M (`accent-ink`) · Custo estimado US$ 401,81 · Rodou em
Opus 5.5 92 % e Fable 5.1 8 % (o único agente com mais de um modelo nos 30 dias). O cartão leva à ficha do Atlas.

## Departamento (`k-depto` > `k-pessoa-linha`)
- Cabeçalho: nome, "5 agentes", soma de tokens (`accent-ink`) · custo em US$.
- Colunas: Agente (avatar 32, nome, função, e nos portões o cadeado + "Portão da pauta" em `accent-ink`) · Status
  (**exemplo**) · Modelo **que rodou** (chip com versão; com mais de um, o chip do principal e embaixo "92 % · +1", a lista
  no `title` e no leitor de tela; sem registro, "ainda não rodou" em `ink-2`) · Consumo (tokens + US$) · Tarefas · seta.
- Gerente: fundo `surface-hover` com contorno `line`. Quem não rodou: "ainda não rodou" no Modelo e "—" no Consumo e nas
  Tarefas (Vera Campos, Beatriz Santos, Íris Moura, Caio Martins e Henrique Sales).
- Os três casos do Modelo estão desenhados na maquete, fora da tela ("Modelo que rodou: os três casos"), com dados reais.
- A linha inteira é link para a ficha (`/equipe/<id>`).
- **Largura:** colunas de 32 · nome · 76 · 86 · 64 · 54 · 14 px (o chip "Sonnet 5.5" mede 85 px e o "não rodou", 62).
  **3 departamentos por linha a partir de 1834 px de janela** (cada cartão com ≥ 510 px: `.k-deptos` com
  `minmax(510px, 1fr)`; a garantia é a largura do cartão, não a da janela: com barra de rolagem fixa o limite anda, o
  cartão não); de 1024 a 1833 px, 2 por linha; abaixo de 1024, 1. A coluna do nome fica com 172 px a 1440, 252 a 1600,
  106 a 1834 e 135 a 1920; o nome mais longo ("Mateus Pacheco") mede 104. Só o **nome** pode cortar (com `title`), e
  hoje nenhum corta; a função e a linha do portão quebram em 2 linhas. Conferido no navegador a 375, 768, 1024, 1440,
  1600, 1834 e 1920: nenhum texto com reticências e nenhum conteúdo saindo da própria caixa.
- O modelo da linha é o **configurado** (`.claude/agents/*.md`). O Otávio Reis e a Clara Duarte estão como Opus 5.5, mas
  as execuções dos 30 dias rodaram em Sonnet 5.5 — a tela Tokens e custos mostra "Rodou em".

## Interações
- Filtros (`aria-pressed`) e busca por nome/função: **escondem** as linhas que não passam e o departamento que fica vazio;
  sem resultado, `k-empty` "Ninguém com esse filtro" + "Limpar filtros".
- Linhas e cartões são links com foco visível.

## Estados
| Bloco | Vazio | Carregando | Erro |
|---|---|---|---|
| Números da equipe | "Equipe ainda não sincronizada" | esqueleto de 4 KPIs | `k-note--alert` + "Tentar de novo" |
| Direção | "Sem a ficha do Atlas" | esqueleto de cartão | idem |
| Departamento | "Ninguém neste departamento" + "Adicionar agente" | esqueleto de lista | idem |
| Consumo (por linha) | "—" + "não rodou" (a pessoa não trabalhou nos 30 dias) | — (vem com a linha) | a linha mostra "—" e o bloco Tokens mostra o erro |

## 375 px
Filtros quebram em linhas; KPIs em uma coluna; Atlas com os números embaixo do resumo; departamentos em uma coluna; cada
pessoa em duas linhas (avatar + nome/função/portão; embaixo status, modelo, consumo e tarefas). Sem rolagem lateral.

## Do artboard para a maquete
| No artboard | Na maquete | Motivo |
|---|---|---|
| Contorno laranja na linha do gerente | fundo `surface-hover` + contorno `line` | laranja é ação e foco; o contorno parecia o anel de foco |
| Chip "PORTÃO" de 10 px ao lado do nome | cadeado + "Portão da pauta" na 3.ª linha | a 1440 o chip cortava o nome ("Vera Ca…"); 10 px fica abaixo do caption |
| Botão "…" em cada linha | a linha é o link para a ficha | não havia ação para pôr no menu |
| Filtro apagava (opacidade .3) quem não passava | esconde | texto a 30 % não passa no contraste |
| Contagem do filtro com opacidade .72 | `ink-3` / `sidebar-ink-2` | mantém 4,5:1 |
| "Tarefas atuais 3 · Tela Equipe e mais 2" (exemplo) | "Tarefas · 30 dias 45" (real) + "Rodou em" | o número real existe; tarefa em andamento não tem fonte |
| 3 departamentos por linha a 1440 | 2 por linha até 1833 px; 3 a partir de 1834 px | a 1440 a coluna do nome ficava com 19 px; com 3 por linha antes de 1834 os nomes e portões cortavam (achado do portão, S1-4) |
| Função e portão com reticências | quebram em 2 linhas | "Gerente de pós-produç…", "Portão do rotei…" escondiam o que a linha diz |

## Dúvidas para o Carlos
- Quer foto para as 16 pessoas que ainda estão em iniciais?
- (Respondida em 24/10: o modelo é o que rodou. Fotos: o Carlos gera no ChatGPT Image; nada muda nesta volta.)
