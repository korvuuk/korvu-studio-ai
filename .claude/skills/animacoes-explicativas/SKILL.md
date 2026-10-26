---
name: animacoes-explicativas
description: Animações explicativas dentro dos Reels — gerar brief para o Claude Design (claude.ai), importar o export HTML/código e portar para Remotion sincronizado com as palavras faladas. Usar quando o roteiro tiver ANIMACAO na coluna TELA ou em /animar.
---

# Animações explicativas (Claude Design → Remotion)

## Quando
Linha do roteiro com `ANIMACAO[full|split|card]: descrição` → overlay `tipo: animacao` na EDL (`id` = ID da linha).

| Modo | Área útil | Uso |
|---|---|---|
| `full` | 1080×1920 (respeitar topo 270 / base 670) | conceito inteiro, voz do Carlos por baixo |
| `split` | metade de **cima** 1080×608, 16:9 (o Carlos fica embaixo) — animação em formato YouTube | passo a passo enquanto ele fala |
| `card` | caixa central ~900×700 sobre o vídeo | um número, uma comparação rápida |

## 0. Regra de ouro (feedback do Carlos, 2026-09-15)
**A animação acompanha o roteiro do início ao fim — uma cena para cada linha — nunca um trecho isolado e genérico.**
- Quando a fala **descreve uma ação no ecrã** ("você pede pro ChatGPT…", "abre o app", "cola o prompt"), a animação **simula essa ação**: interface de chat abrindo, cursor piscando, **digitação letra a letra** do texto exato que ele diz, botão de enviar, "IA digitando…", resposta aparecendo palavra a palavra.
- Quando a fala é um **conceito** ("o problema não é a IA", "recado pra funcionário novo"), a cena ilustra o conceito com metáfora visual concreta (bilhete/recado, loja com "?", comparação antes/depois) — nada de cartão com texto repetindo a fala.
- Cada elemento entra **na palavra que o nomeia**; cenas encadeadas (a mesma interface continua de uma cena para outra), sem cortes secos sem motivo.
- Interfaces: **a ferramenta do vídeo aparece como ela é** — o Carlos decidiu (2026-09-17) que a animação leva a cara do ChatGPT (interface, nome, logo) para o público reconhecer na hora. Nunca sugerindo parceria ou aval. Ferramentas que **não** são o assunto do vídeo continuam genéricas no estilo Korvu. Respostas de IA mostradas na animação têm de ser **reais** (o Carlos roda o prompt e cola a resposta) — texto provisório só para desenhar, trocado antes do render.
- O brief lista **todas as linhas** do roteiro com a cena correspondente (o Carlos em tela cheia só onde a TELA indicar: hook, CTA…).

## 1. Brief para o Claude Design
Criar `videos/<slug>/animacoes/<ID>/brief.md` com o template abaixo (preencher tudo; tempos a partir de `edl.json` → `palavras_saida` da linha, relativos ao início da animação).

```markdown
# Animação <ID> — <título curto>

Crie uma animação explicativa em HTML/CSS/JS (um único arquivo, sem dependências externas), <LARGURA>×<ALTURA> px, fundo #111111 com linhas verticais finas de grade (branco 5%).
Duração total: <X,X> s. Deve rodar sozinha do início ao fim, sem interação, e expor uma função global `seek(tempoEmSegundos)` que desenha o estado exato daquele instante (sem depender de relógio real).

Estilo (Korvu): tipografia sans grotesca bold (Geist/Inter Tight), texto branco #F2F2F2 e cinza #9B9B9B, destaque em laranja #FF7A35 com moderação, realce de "seleção de texto" (caixa #2E3033 com alças de cursor) e rabisco à mão sob palavras-chave. Movimentos suaves (ease-out), nada de efeitos exagerados. Sem pessoas reais, sem logos de terceiros.

O que explicar: <descrição da ANIMACAO>
Fala do Carlos durante a animação: "<FALA da linha>"

Cenas (sincronizadas com a fala):
| tempo (s) | palavra falada | o que aparece |
|---|---|---|
| 0,0 | — | fundo + grade |
| 0,4 | "prompt" | caixa "Prompt" entra da esquerda |
| … | … | … |

Área segura: nada importante a menos de <margens> px das bordas.
Entregue o código completo.
```
O Carlos cola no Claude Design, ajusta visualmente e exporta o código para `videos/<slug>/animacoes/<ID>/export/`.

## 2. Importar para o Remotion (preferido)
1. Ler o export. Recriar em `remotion/src/animacoes/<NomePascal>.tsx` usando `useCurrentFrame()`, `interpolate`, `spring`, `Easing` — **proibido** CSS `animation`/`transition`, `setTimeout`, `requestAnimationFrame` (não são determinísticos no render).
2. Props: `{ palavras: {texto, inicio, fim}[], duracaoSeg: number }` — cada elemento entra no frame da palavra correspondente (`Math.round(inicio * fps)`), com fallback para os tempos do brief.
3. Tokens de `remotion/src/brand.ts`; fontes via `@remotion/google-fonts`.
4. Registrar em `remotion/src/animacoes/registry.ts` com a chave **`<slug>/Exx`** (= `componente` do overlay na EDL).
5. Prévia: `cd remotion && npx remotion still Reel --frame=<frame> --props=<reel-props.json> <saida.png>` e ver a imagem; render curto do trecho se precisar.

## 3. Capturar o HTML (caminho usado quando o export é grande demais para portar)
O export do Claude Design compila JSX no browser (150 KB+ numa linha só): reescrever à mão é trabalho perdido.
Como ele expõe `window.seek(t)`, a captura é **determinística** — o mesmo `t` desenha sempre o mesmo quadro.

```bash
node scripts/capturar_animacao.mjs "videos/<slug>/animacoes/E02/<export>.html" \
     "videos/<slug>/brutos/extras/E02.mp4" --dur 39.56 --fps 25 [--warp mapa.json] [--clip x,y,w,h]
```
- Chrome do sistema via CDP (Node ≥ 22 já tem `WebSocket`; **não instala nada**).
- **Recorte automático:** acha o maior elemento 16:9 da página — que é o palco sem a barra de player
  ("▶ 12.3 / 41.8s") que o Claude Design desenha embaixo. `--clip` força outro retângulo.
- **`--warp`**: `[[tExport, tReal], …]` nas bordas das cenas → encaixa a animação na fala (o export quase nunca
  respeita os tempos do brief). Confira o fator de cada cena antes: esticar > 1,25× congela a tela e
  comprimir < 0,8× acelera a digitação. Fator muito fora = melhor regerar com a `TIMELINE` real do brief.
- Depois: `ingest.py` (vira `edicao/extras/<ID>.mp4`) → `edl.py --recalcular` (sai de `faltando`) →
  `gerar_props.py` (mede o arquivo e define o modo pelo formato).

## Checklist
- [ ] Duração = duração da fala da linha (± 2 frames)
- [ ] Cada elemento entra junto da palavra que o nomeia
- [ ] Dentro da área útil do modo + safe zones
- [ ] Estilo igual às referências; legível no celular (texto ≥ 44 px)
- [ ] Prévia vista e aprovada pelo Carlos
