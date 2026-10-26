---
name: roteiro-reels
description: Escrever e validar roteiros de Reels de 60 s sobre IA para a Korvu (PT-BR), com 3 hooks, estrutura de retenção, CTA e tabela FALA/TELA com IDs de linha que o editor usa para cortar. Usar sempre que for criar, revisar ou ajustar um roteiro, ou calibrar a voz do Carlos.
---

# Roteiro de Reels (Korvu)

## Padrão NARRATIVO (decisão do Carlos, 14/10 — todo roteiro)
Ler **`00-marca/modelo-roteiro-narrativo.md`** antes de tudo. O roteiro é **uma história com começo, meio e fim**, em blocos: **gancho → contexto → desafio → virada → clímax → reflexão → CTA**. Frases completas e ligadas por conectores, emoção antes de dado, poucos números, **lição no fim**. Picado/telegráfico = o revisor reprova. Tema que não é perfil: mesmo arco, com o problema do espectador no lugar da pessoa.

## Antes de escrever — carregar contexto
0. `00-marca/modelo-roteiro-narrativo.md` (o padrão — exemplo do Hinton escrito pelo Carlos)
1. `00-marca/voz-carlos.md` (ritmo `wps_roteiro`, muletas, expressões — **prioridade** se calibrado)
2. `00-marca/tom-de-voz.md`, `00-marca/hooks.md`, `00-marca/estruturas-psicologicas.md`
3. `00-marca/publico.md`, `00-marca/pilares.md`, `00-marca/cta.md`, `00-marca/regras-legais.md`
4. `_controle/tracker.md` + `_controle/temas-ja-feitos.md` (não repetir ângulo; não repetir a mesma estrutura 2× seguidas na semana)

## Processo
1. **Ângulo**: transformar o tema numa história (pessoa) ou num problema concreto do público (iniciante ou dono de negócio). Uma ideia por vídeo, contada do começo ao fim.
2. **Pilar + estrutura**: escolher pela tabela de `estruturas-psicologicas.md` e pela regra de rotação.
3. **3 hooks (A/B/C)** de templates diferentes de `hooks.md`. Cada um com:
   - FALA ≤ 12 palavras · TEXTO NA TELA 4–7 palavras · VISUAL (interrupção de padrão).
   Escolher o melhor como `hook_escolhido`; os outros viram `L01B`/`L01C` (Trial Reels).
4. **Arco narrativo (60 s; perfis/histórias até 90 s)** — o nome do bloco vai na coluna Seção (não é falado):
   | Bloco (Seção) | Vira `secao` | O que faz | Conectores típicos |
   |---|---|---|---|
   | `gancho` (0–10 s) | hook | emoção + promessa em frase completa; termina dizendo de quem/do quê é a história | "Imagina você…" · "Pois é. Essa é a história de…" |
   | `contexto` / `historia` | corpo | de onde a pessoa (ou o problema) veio, com um detalhe que surpreende | "Mas, diferente do que muita gente imagina…" |
   | `desafio` | corpo | o obstáculo, quem duvidou, o que estava em jogo | "O problema é que…" · "Até o próprio…" |
   | `virada` / `revolucao` | corpo | o que mudou — 1 número no máximo, em palavras simples | "Pouco depois…" · "Aquilo mudou…" |
   | `climax` | payoff | o momento mais forte, contado como cena | "Mas olha que interessante…" |
   | `reflexao` | payoff | a frase-lição que fica, ligada ao público | "E o mais curioso é que…" · "A história dele mostra uma coisa:" |
   | `cta` | cta | UM CTA falado de `cta.md` (+ o pedido curto de enviar/salvar) | "Comenta [PALAVRA] que eu te mando…" |
   | `gancho-alt` | hook-alt | L01B / L01C (Trial Reels) | — |
   O `parse_roteiro.py` aceita esses nomes (com ou sem acento) e os antigos (`hook · promessa · corpo · payoff · cta · hook-alt`), grava a seção técnica em `secao` e o nome do bloco em `bloco` (`docs/contratos.md` §1), e avisa se o roteiro narrativo não tiver `reflexao`. **Interrupção visual a cada 5–8 s** continua (cenas extras ao longo do corpo).
5. **Tamanho**: `palavras_alvo = wps_roteiro × duracao_alvo` (calibrado 17/10 em `voz-carlos.md`: **2,1** → 60 s ≈ 125; perfis/histórias 90 s ≈ **185, máx. 190** — a conta antiga "190–210" era com 2,3 e estoura; dica rápida pode usar 2,3). Aceitável ±10%, sem passar de 190 em 90 s.
6. **Cenas extras** (todo vídeo tem): o que a fala mostra ou cita vira um extra na tabela `## Cenas extras` (E01, E02…) — gravação de ecrã do passo a passo, print da notícia/anúncio (com crédito), imagem gerada, trecho curto de vídeo oficial (com crédito), plano de apoio com a Lumix, ou **animação no Claude Design** para explicação abstrata. Na TELA: `EXTRA: E01 split|full|card [mm:ss–mm:ss]`. Um extra a cada 1–3 linhas do corpo mantém a retenção; o Carlos na tela cheia no hook e no CTA.
7. **CTA com material** (decisão do Carlos, 13/10: *palavra-chave = SEMPRE um link para um PDF*): se `cta_tipo: palavra-material`, preencher no frontmatter `cta_palavra` (MAIÚSCULAS, sem acento, nunca KORVU/CORVO — `cta.md`), `material` (o que o PDF entrega, em uma frase) e `material_titulo` (com artigo, como o direct o chama: "Aqui está **o guia do prompt** que você pediu"), e detalhar na seção "Material do CTA". **O roteirista não escreve o PDF**: depois do roteiro aprovado, o agente **produtor-de-material** gera `videos/<slug>/material/<arquivo>.pdf` sozinho (`scripts/gerar_material_pdf.py`). A fala só promete o que dá para entregar num PDF de 1–3 páginas com fontes (prompt, passo a passo, lista, link oficial) — nunca resultado, nunca algo que a gente não tem.
8. Preencher `titulo` (contexto + impacto + nº de palavras em cinza + palavra do rabisco) para o título animado do hook — ver `00-marca/referencias/legendas/estilo-selecao.md`.
9. Legenda do post (rascunho) + máx. 5 hashtags + fontes.

## Formato
Usar **exatamente** `references/template-roteiro.md`. Regras da coluna FALA:
- É o texto **literal** falado — o editor compara palavra por palavra com a gravação.
- Uma frase **completa** por linha (L01, L02…), idealmente ≤ 18 palavras, e cada linha continua a anterior (conectores do modelo) — nunca frases soltas ou telegráficas.
- `**destaque**` para palavras-chave; `[pausa]`/`[pausa longa]` só no fim da linha.
- PT-BR falado: "tá", "pra", "a gente", números em ALGARISMO (anos e números grandes: "2024", "30 segundos", "15%"; decisão de 14/10).

## Validar (obrigatório)
```bash
uv run python .claude/skills/roteiro-reels/scripts/parse_roteiro.py videos/<slug>
```
Gera `roteiro.json` (contrato em `docs/contratos.md`) e aponta erros (IDs, pausas fora do lugar, hook longo, tamanho fora do alvo). Corrigir até passar sem erros.

## Formato de leitura — teleprompter e narrador (OBRIGATÓRIO em todo roteiro)
O Carlos grava lendo no **teleprompter** ou ouvindo o **narrador**. Por isso o roteirista escreve a FALA já pensando na leitura:
- **Respiros:** ` / ` onde ele deve respirar ou dar uma micro-pausa (troca de ideia, antes de uma revelação, depois de vírgula forte). Linhas de ≥ 12 palavras precisam de pelo menos um ` / `.
- **Pausas:** `[pausa]` (~1 s) e `[pausa longa]` (~2 s) no fim da linha, onde a pausa é dramática/intencional.
- **Ênfase:** `**palavra**` (vira MAIÚSCULAS no teleprompter).
- **Cenas extras NÃO entram aqui**: vivem só na tabela `## Cenas extras`. Nada de gesto, olhar, postura ou cenário — nem no roteiro, nem no teleprompter (Carlos, 2026-09-17: "você não precisa me orientar como eu vou me posicionar").

### Uma fonte, duas saídas
| Arquivo | Para quem | O que tem |
|---|---|---|
| `roteiro.md` | **o editor / a máquina** | IDs `L01…` (alinham a fala linha a linha, escolhem take, cortam erro, montam EDL e legendas), `seção` (frame da capa), `[pausa]` (silêncio real), `**negrito**` (palavra grande na legenda), tabela de cenas extras |
| `roteiro-limpo.txt` | **o Carlos** | só as frases, na ordem. É o que se entrega a ele para ler e aprovar |

Depois de validar, gerar SEMPRE os três:
```bash
uv run python .claude/skills/roteiro-reels/scripts/roteiro_limpo.py videos/<slug>   # → roteiro-limpo.txt (entregar ESTE)
uv run python .claude/skills/roteiro-reels/scripts/teleprompter.py videos/<slug>    # → teleprompter.txt
uv run python .claude/skills/roteiro-reels/scripts/monitor_chatgpt.py videos/<slug> # → monitor-chatgpt.txt
```
Teleprompter: ID de cada linha (para ele saber onde está e dizer "de novo"), frases em linhas curtas (~34 caracteres) e `/` `//` `///` + MAIÚSCULAS. **Sem** divisórias de seção, `(respira)` ou indicação de cena. Se o roteirista não marcar respiros, o script põe `/` nas vírgulas e dois-pontos.

## Monitor ChatGPT Voz (como o Carlos grava)
O Carlos grava com o **ChatGPT Voz** no altifalante do telemóvel (sem fones): a IA lê cada linha, ele repete para a câmera, e a IA pede "de novo" quando ele erra. As duas vozes ficam gravadas — o editor separa-as e corta a voz da IA (`corte-por-roteiro/locutores.py`). Depois de validar o roteiro, gerar:
```bash
uv run python .claude/skills/roteiro-reels/scripts/monitor_chatgpt.py videos/<slug>   # → monitor-chatgpt.txt
```
O `monitor-chatgpt.txt` tem as regras para o ChatGPT (ler só a linha, sem mudar palavras, esperar, "de novo" se errar, nunca falar por cima) + as linhas L01… e os hooks alternativos. O Carlos cola no ChatGPT, ativa o modo voz e diz "começar".

## Checklist final
- [ ] Hook prende em 1 s sem preâmbulo ("Olá pessoal", "Hoje vou falar…" são proibidos)
- [ ] Arco narrativo completo (gancho → contexto → desafio → virada → clímax → reflexão → CTA), frases inteiras e ligadas, emoção antes de dado, lição no fim
- [ ] Soa falado, não lido; frases curtas intercaladas com médias
- [ ] ≥ 1 exemplo concreto ou número específico (real e com fonte)
- [ ] Interrupção visual a cada 5–8 s na coluna TELA
- [ ] Zero palavras banidas; sempre "você"
- [ ] CTA único, vindo de `cta.md`, sem prometer material inexistente
- [ ] `parse_roteiro.py` sem erros

## Calibração de voz
Ver comando `/calibrar-voz`. Script: `scripts/voice_stats.py` (lê `transcricao.json` das amostras e mede ritmo, pausas, muletas, expressões).
