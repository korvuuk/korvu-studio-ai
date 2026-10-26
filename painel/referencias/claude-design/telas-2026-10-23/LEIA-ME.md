# As 5 telas do painel feitas no Claude Design (23/10)

- **Canvas:** "korvu. painel — Visão geral", https://claude.ai/artifact/9vtqDX3tQ4CCwGWYLaQAQ4 (versão 1792767247-1d5d), feito
  sobre o design system "korvu. painel" (o mesmo de `painel/design/`, aprovado pelo PORTÃO-INTERFACE às 15:55).
- **Pedidos do Carlos:** um prompt por tela, nesta sessão. Visão geral aprovada em palavras ("Approved. Take the Visão geral
  mockup into painel/design/ … and run it through the PORTÃO-INTERFACE gate"); depois "vamos prosseguir para implementar a
  segunda tela" e os ajustes listados abaixo.
- Cada `*.dc.html` é a **fonte exata** de um artboard 1920×1080 (formato Design Component: `<x-dc>`, `<sc-for>`, `<sc-if>`,
  `{{ }}`, classe `Component` com os dados em `renderVals()`). Não abre sozinho no navegador. Usa as classes `k-*` do
  `bundle.css` (= `painel/design/componentes.css`) e repete os tokens em `:root`.

| Arquivo | Tela | Menu |
|---|---|---|
| `Main.dc.html` | Visão geral | Visão geral |
| `Equipe.dc.html` | Equipe | Equipe |
| `Producao.dc.html` | Produção de conteúdo (5 fases) | **Produção de conteúdo** (antes "Vídeos e portões") |
| `Calendario.dc.html` | Calendário editorial (mês + semana) | Calendário |
| `Desempenho.dc.html` | Desempenho | Desempenho |
| `Biblioteca.dc.html` | Biblioteca (materiais dos vídeos) | Biblioteca |
| `Tokens.dc.html` | Tokens e custos | Tokens e custos |

> **Atualização 23/10, 16:20:** entraram Biblioteca e Tokens e custos, e os números de tokens/custo de **todas** as telas
> passaram a ser **reais** (Visão geral, Equipe e Tokens). A fonte são os registros das sessões do Claude Code deste projeto
> (`~/.claude/projects/-Users-teste-Documents-CONTENT-AI/**/*.jsonl`: `message.usage` + `model` por resposta; nos subagentes,
> `subagents/agent-*.meta.json` → `agentType`). O script que fez a conta está em `tokens-custos.py` (30 dias até 23/10 às 16:02:49 de Londres, o mesmo corte do banco; vale a ÚLTIMA linha de cada resposta, porque o usage das primeiras é provisório — PD21; tokens
> = entrada + cache gravado + saída; custo = preço de tabela da API em US$, cache gravado = 1,25× a entrada por 5 min e 2× por
> 1 h — correção da sessão de tokens). Total: 37.909.543 tokens, US$ 539,06 = £ 402,41 — bate com o banco do painel (PORTÃO-DADOS v3, APROVADO) (a £ 0,7465 por US$, XE 23/10). Isso é um
> **dado novo para o `engenheiro-backend`** sincronizar.

## Decisões do Carlos aplicadas (todas em `docs/decisoes.md` §5, 23/10)
- Menu **"Produção de conteúdo"** com 5 fases: Roteiros → Gravados → Prontos → Agendados → Publicados; roteiro só vira vídeo
  depois de gravado; portão é detalhe, não nome de menu; formatos Reels / Stories / Carrossel.
- **Onde saiu / vai sair:** Instagram · Facebook · LinkedIn em cada publicação, com link para o post.
- **Versão do modelo** em todo chip ("Opus 5.5", "Sonnet 5.5") e **tokens em destaque laranja** (`accent-ink` em texto
  pequeno, `accent` ≥ 24 px). Vermelho só para alerta.
- **Retratos dos agentes = foto realista** (as fotos estão em `painel/web/src/app/equipe/img equipe/`; cópias 512×512 em
  `retratos/`). Quem ainda não tem foto mostra as iniciais.

## Imagens (no canvas são `/_blob/<id>`)
| id (início) | arquivo aqui | origem |
|---|---|---|
| 4b0d17ca | `retratos/atlas.jpg` | `img equipe/ATLAS · Diretor de Operações.png` |
| 4a6f45d2 | `retratos/vera.jpg` | `VERA CAMPOS · Gerente de Pesquisa.png` |
| e886863b | `retratos/otavio.jpg` | `OTÁVIO REIS · Gerente de Roteiro.png` |
| c4ca776e | `retratos/iris.jpg` | `10 — ÍRIS MOURA · Diretora de Arte.png` |
| c9519730 | `retratos/helena.jpg` | `HELENA PRADO · Estrategista de Conteúdo.png` |
| aed454b5 | `retratos/rafael.jpg` | `RAFAEL NUNES · Pesquisador.png` |
| cc9695d4 | `retratos/tiago.jpg` | `TIAGO LOPES · Caçador de Vídeos.png` |
| 288af123 | `retratos/beatriz.jpg` | `BEATRIZ SANTOS · Curadora de Obras.png` |
| d4266f08 | `retratos/marina.jpg` | `09 — MARINA COSTA · Roteirista.png` |
| 53862d50 | `retratos/livia.jpg` | `08 — LÍVIA ROCHA · Produtora de Material.png` |
| 8737c82b | `capas/capa-demis.jpg` | `07-publicados/2026-09-17-demis-hassabis/capa/capa.png` |
| d740077b | `capas/capa-feifei.jpg` | `06-publicar/2026-10-20-fei-fei-li-r2/capa/capa.png` |
| d701f0c5 | `capas/capa-hinton.jpg` | `06-publicar/2026-10-20-geoffrey-hinton-r2/capa/capa.png` |
| 09186922 | `capas/capa-livro.jpg` | `06-publicar/2026-10-23-livro-chatgpt/capa/capa.png` |
| 976cb8bd | `capas/capa-livro-l01c.jpg` | `06-publicar/2026-10-23-livro-chatgpt-l01c/capa/capa.png` |
| 24151418 | `capas/capa-livro-l01c-a.jpg` | `06-publicar/2026-10-23-livro-chatgpt-l01c-a/capa/capa.png` |
| fc8843a9 | `capas/capa-chatgpt-contexto.jpg` | `videos/2026-09-16-chatgpt-contexto/capa/capa.png` |
| d16607ee | `capas/pub-feifei.jpg` | `07-publicados/2026-10-20-fei-fei-li/capa/capa.png` |
| a316c35b | `capas/pub-feifei-a.jpg` | `07-publicados/2026-10-20-fei-fei-li-a/capa/capa.png` |
| 96cd2592 | `capas/pub-hinton.jpg` | `07-publicados/2026-10-20-geoffrey-hinton/capa/capa.png` |
| 5a862831 | `capas/pub-livro-a.jpg` | `07-publicados/2026-10-23-livro-chatgpt-a/capa/capa.png` |

## De onde vem cada dado — e o que é exemplo
| Tela · bloco | Fonte | Real? |
|---|---|---|
| Visão geral · seguidores, alcance, visualizações, visitas, fora da bolha 307/513, países | `_controle/perfil/2026-10-22.json` | sim |
| Visão geral · deltas (−0,1 %, +11,1 %, +3,4 p.p.) | `2026-10-22.json` × `2026-10-16.json` | sim |
| Visão geral / Desempenho · curva diária | o snapshot só tem totais de 28 dias | **exemplo (forma)**; datas dos Reels reais |
| Próximas publicações / Agendados / Calendário | `06-publicar/*/post.json` (`publicar_em`, `plataformas`, `instagram.trial`) | sim |
| Publicados · métricas e links | `07-publicados/*/metricas.json` (`ultima`), `post.json` (permalinks) | sim |
| Produção · roteiros (versão, palavra, PDF, extras, gravação prevista) | `videos/<slug>/roteiro.json`, `material/*.pdf`, `brutos/extras/`, data do slug, `status.json` | sim |
| Produção · Prontos (ChatGPT contexto, "teste de cor, não publicar") | `05-render-pronto/…/pacote.json` + `_controle/CONTINUAR.md` | sim |
| Portões (pendente/legado, contagens) | `scripts/portoes.py estado` | sim |
| Equipe · nomes, funções, departamentos, portões, modelo | `painel/equipe.yaml` + `model:` de `.claude/agents/*.md` | sim |
| Equipe · tokens, custo e tarefas (execuções) por agente | registros do Claude Code (ver acima) | sim |
| Equipe · status "Ativo/Em espera"; tarefas atuais do Atlas | — | **exemplo** |
| Tokens e custos · 37,9 M tokens, US$ 539 = £ 402, por dia/modelo/departamento/agente, custo por vídeo (subagentes cujo pedido cita `videos/<slug>`) | registros do Claude Code + `tokens-custos.py` | sim (custo = equivalente na API; com assinatura a fatura é outra). Projeção = ritmo dos últimos 7 dias × 30 |
| Tokens e custos · ElevenLabs (transcrição, música) | — | **fora** (sem medição) |
| Biblioteca · contagens por tipo, 13,95 GB, tamanhos e datas, maiores pastas, 227 GB de `brutos/principal/` | `videos/*/material` + `brutos/extras` (extensão, tamanho, data) | sim |
| Biblioteca · "quem adicionou" | a função do agente que produz aquele tipo | **inferido** (o arquivo não guarda autor) |
| Biblioteca · "mais utilizados" | voz-carlos.md (12 roteiros), look v5 e LUT de entrada (5 vídeos gravados), molde do PDF (9 PDFs) | sim |
| Calendário · vagas e "melhores horários" | `_controle/calendario.md`; print 15 de `_controle/perfil/prints-2026-10-17/` (alturas medidas) | sim |
| Desempenho · ranking (views, alcance, não seguidores, % assistido, engajamento) | `metricas.json` + `_controle/analise-trial-vs-normal-2026-10-22.md` | sim; "seguidores ganhos" = n/d (a API não dá por Reel) |
| Notificações (3) | — | **exemplo** |
