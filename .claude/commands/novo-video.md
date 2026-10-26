---
description: Cria um vídeo novo a partir de um tema — pasta, roteiro (roteirista) e revisão (revisor-de-roteiro)
argument-hint: <tema do vídeo>
---

Tema: **$ARGUMENTS**

1. Criar o slug `AAAA-MM-DD-palavra-chave` (data de hoje ou a próxima gravação prevista; 2–4 palavras-chave sem acento). Criar `videos/<slug>/` com `brutos/`, `material/`, `capa/`, `qa/`, `edicao/` e `status.json` (estado `roteiro`). Checar `_controle/tracker.md` e `_controle/temas-ja-feitos.md` — se o ângulo já foi feito, avisar e propor um ângulo novo antes de continuar.
2. Usar o subagente **roteirista** para escrever `videos/<slug>/roteiro.md` (com `cta_palavra`, `material` e `material_titulo` se o CTA for de palavra-chave).
3. **Material do CTA** — se o roteiro tiver `cta_tipo: palavra-material`, usar o subagente **produtor-de-material** (sem o Carlos pedir — decisão de 13/10): escreve `material/_fonte/material.md` e gera `material/<arquivo>.pdf` + prévia PNG.
4. **PORTÃO-ROTEIRO** — subagente **revisor-de-roteiro** sobre o roteiro E o PDF (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO). Roteiro → roteirista; PDF → produtor-de-material.
4b. **Material em VÍDEO (sem o Carlos pedir — decisão de 14/10, o vídeo é o carro-chefe)** — usar o subagente **buscador-de-videos** (`/buscar-videos <slug>`): busca no YouTube, baixa para `material/youtube/`, assiste, anota os momentos por linha, **corta os trechos que vão para a tela** e preenche a tabela de cenas extras do roteiro. Prioridade: vídeo da própria pessoa/assunto (entrevistas, palestras, demos, reportagens) > animação > foto (fotos só quando não houver vídeo — dão menos credibilidade). Sem teto de tempo para trecho narrado por cima, com áudio original baixo/mudo e crédito (decisão de 14/10). O roteiro só segue para a gravação com o catálogo pronto. Depois do buscador: **PORTÃO-PAUTA** — subagente **portao-pauta** sobre o catálogo/dossiê (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO).
5. Adicionar a linha no `_controle/tracker.md`.
6. Gerar os dois formatos de leitura:
   - **roteiro limpo (o que se entrega ao Carlos)**: `uv run python .claude/skills/roteiro-reels/scripts/roteiro_limpo.py videos/<slug>` → `videos/<slug>/roteiro-limpo.txt` — só as frases; o `roteiro.md` técnico é para o editor
   - **teleprompter**: `uv run python .claude/skills/roteiro-reels/scripts/teleprompter.py videos/<slug>` → `videos/<slug>/teleprompter.txt`
   - **monitor ChatGPT Voz**: `uv run python .claude/skills/roteiro-reels/scripts/monitor_chatgpt.py videos/<slug>` → `videos/<slug>/monitor-chatgpt.txt` (o Carlos cola no ChatGPT Voz; a IA lê cada linha, ele repete, a IA pede "de novo" se ele errar — o editor remove a voz da IA)
6b. **História completa (decisão de 14/10)** — `videos/<slug>/historia-completa.txt`: o contexto INTEIRO do vídeo, sem resumir, em texto puro para uma IA ler em voz alta (perfil: 1.800–2.500 palavras, cronológico; tema: 1.000–1.800). Só fatos verificados do dossiê/fontes. No fim, "Os momentos que estão no vídeo": a ideia de cada fala com 1–2 formas diferentes de dizê-la (para o improviso), e o que não pode mudar (números, nomes, palavra-chave, pedido final). Depois, "Fontes (não precisa ler em voz alta)". Serve para o Carlos entender tudo e improvisar do jeito dele na gravação.
7. Só com os portões roteiro (e pauta, se houve pesquisa) APROVADOS — `uv run python scripts/portoes.py estado videos/<slug>` — mostrar ao Carlos:
   - **o roteiro limpo** (só as frases) — nunca a tabela técnica; hooks A/B/C, duração estimada, CTA/material (caminho do PDF e a prévia);
   - **checklist de gravação**: Lumix S5IIX vertical em V-Log, 4K 25p 4:2:2 10-bit, 1/50, WB fixo; `camera-00-cor.mov` (folha branca + rosto parado) na primeira tomada do dia; repetir a linha inteira quando errar (pode dizer "de novo"); gravar também L01B/L01C; gravações de ecrã como `tela-01.mov`; soltar tudo em `videos/<slug>/brutos/` e depois rodar `/editar <slug>`.
