---
description: Traz a obra de que o Reel vai falar (documentário, palestra, demo), assiste e recorta os trechos a citar
argument-hint: <url> [slug] | trechos <slug> | estado <slug>
---

Vídeo de **comentário/reação**: o Carlos fala **sobre** uma obra e cita trechos dela como prova.

Chame o agente **`curador-de-obra`** com o pedido do Carlos: `$ARGUMENTS`

## Antes de mais nada — confirme que é caso de comentário

O tema do Reel é a própria obra?

- **Sim** → segue aqui.
- **Não** (o trecho seria só imagem de fundo enquanto ele fala de outra coisa) → **pare**. Isso é B-roll, precisa de licença de reuso: use `/material` (agente `pesquisador-de-material`, `scripts/buscar_video.py`). Diga isso ao Carlos em vez de baixar.

## Passos

1. **Slug.** Se não vier no comando, procure em `_controle/tracker.md` um vídeo cujo tema seja essa obra — pode já existir. Só crie um novo (`/novo-video`) se não houver.

2. **Ficha antes do download:**
   ```bash
   uv run python scripts/baixar_obra.py baixar <url> <slug> --so-metadados
   ```
   Confira autor e título em `material/obra.json`. **Sem autor não há crédito, e sem crédito o trecho não entra.**

3. **Baixar** (mesmo comando sem `--so-metadados`). Vai para `material/obra/` — cópia de estudo, nunca publicada. O script pede H.264/AAC e, se mesmo assim vier VP9/Opus, gera sozinho uma cópia `-VER.mp4` que o QuickTime toca.

4. **Assistir** com a skill `watch`, em partes se for longa:
   ```
   /watch videos/<slug>/material/obra/<arquivo> o que esta obra mostra sobre <tema>, com marcas de tempo
   ```

5. **Escolher e recortar** os trechos — curtos, cada um sustentando uma frase do roteiro:
   ```bash
   uv run python scripts/baixar_obra.py trecho <slug> E02 12:30 12:38 \
       --o-que "..." --nome hassabis-alphafold
   ```
   Tetos: 12 s por trecho, 30 s no total (`docs/decisoes.md`, `CLAUDE.md` regra 4). Se o script recusar, **aperte o trecho** — não passe `--forcar` por conta própria.

6. **Entregar**: tabela de cenas extras pronta para o roteiro (ID · tipo · o que mostra · crédito · som · linhas) + marca de tempo de cada trecho, e o crédito que tem de aparecer na tela.

6b. **PORTÃO-PAUTA** — subagente **portao-pauta** sobre a ficha e os trechos (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO). Só depois do APROVADO a tabela vai ao roteiro e ao Carlos.
7. Atualizar `status.json` e a linha do `_controle/tracker.md`.

## Ver o que já está citado
```bash
uv run python scripts/baixar_obra.py estado <slug>
```

Regras completas em `.claude/agents/curador-de-obra.md` e `docs/decisoes.md` §5.
