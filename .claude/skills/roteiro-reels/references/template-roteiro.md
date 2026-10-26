---
slug: AAAA-MM-DD-palavra-chave
tema: "Tema em uma frase"
pilar: mitos-e-erros            # ver 00-marca/pilares.md
estrutura: "1-ruptura"          # ver 00-marca/estruturas-psicologicas.md
hook_template: jeito-errado     # ver 00-marca/hooks.md
publico: iniciantes             # iniciantes | negocios | ambos
duracao_alvo: 60
palavras_alvo: 138              # = wps_roteiro × 60 (00-marca/voz-carlos.md)
wps_ref: 2.3
hooks:
  A: {fala: "Você tá usando o ChatGPT errado.", tela: "CHATGPT ERRADO?", visual: "snap-zoom no rosto + celular na mão"}
  B: {fala: "", tela: "", visual: ""}
  C: {fala: "", tela: "", visual: ""}
hook_escolhido: A
titulo: {contexto: "Se você usa o ChatGPT assim,", impacto: "tá jogando tempo fora.", cinza: 2, rabisco: "fora"}
cta_tipo: palavra-material      # palavra-material | envio | salvar | seguir (ver 00-marca/cta.md)
cta_palavra: GUIA                # curta e fácil de digitar (14/10): nada de PROMPT/ENTREVISTA
material: "Prompt mestre em PDF (1 página)"   # o que o PDF entrega (o produtor-de-material escreve a partir disto)
material_titulo: "o prompt mestre"   # como o direct chama o PDF: "Aqui está o prompt mestre que você pediu"
status: rascunho
versao: 1
---

# Título do vídeo

## Roteiro

> **POSE DA CAPA (antes de falar qualquer coisa).** Faça a pose escrita em `pose_capa` no frontmatter e
> **segure 3 segundos**, em silêncio. É desse trecho que sai o frame da capa do feed — o editor não precisa
> procurar quadro a quadro. O ChatGPT Voz **lê essa linha em voz alta** antes da L01, para não esquecer.
>
> A pose **muda a cada vídeo** e tem que combinar com o título: mão aberta parando o ar, braços cruzados,
> sobrancelha erguida, cara de espanto, apontando para a câmera. Pose sempre igual deixa o feed monótono —
> mas tem que ser **segurada**, senão o quadro sai tremido.

<!-- Regras (atualizadas em 2026-09-17, a pedido do Carlos):
- **O roteiro tem SÓ o que ele fala.** A tabela é `| ID | Seção | FALA |`.
  PROIBIDO no roteiro: gesto, olhar, postura, respiração, cenário, "segura o celular", "faz zoom",
  descrição do que entra na tela. Ele sabe se posicionar — não o dirija.
- FALA = exatamente o que vai ser dito. Uma frase por linha. Máx. ~18 palavras por linha.
- **negrito** = palavra de destaque (legenda "impacto" / rabisco). [pausa] e [pausa longa] só no FIM da linha.
- " / " dentro da FALA = respiro (vira "/" no teleprompter; não é falado).
- As cenas vivem **só** na tabela "## Cenas extras" (ID, tipo, o que mostrar, como obter, crédito, som, linhas).
  Quem caça o material é o `pesquisador-de-material`; quem monta na tela é o editor.
  O modo (split/full/card) **não se declara**: quem decide é o formato do arquivo (`docs/contratos.md` §0).
- **Não force "o que muda pra você"**: só entra quando o assunto tem mesmo essa consequência prática.
  Vídeo sobre uma pessoa = quem é, de onde veio, o que fez, o que aconteceu.
- **Roteiro NARRATIVO (padrão desde 14/10 — `00-marca/modelo-roteiro-narrativo.md`)**: uma história com
  começo, meio e fim. Na coluna Seção, os blocos do arco, nesta ordem:
  gancho · contexto (ou historia) · desafio · virada (ou revolucao) · climax · reflexao · cta · gancho-alt (L01B, L01C).
  Frases completas, ligadas por conectores ("Pois é", "Mas olha que interessante…", "O problema é que…"),
  emoção antes de dado, poucos números, lição no bloco reflexao. Um bloco pode ter várias linhas.
  (Seções antigas hook · promessa · corpo · payoff · cta · hook-alt continuam aceitas pelo parser.)
-->

| ID | Seção | FALA |
|---|---|---|
| L01 | gancho | Imagina você pedir um post pro ChatGPT / e receber um texto genérico. [pausa] |
| L02 | gancho | Pois é. / Isso acontece com quase todo mundo que começa a usar **IA**. |
| L03 | contexto | Mas, diferente do que muita gente pensa, / a culpa não é da ferramenta. |
| L04 | contexto | O ChatGPT só sabe do seu negócio / aquilo que você conta pra ele. |
| L05 | desafio | O problema é que a gente pede / como se ele já conhecesse a sua loja. |
| L06 | virada | Aí entra o truque: / antes de pedir, você conta quem você é, / pra quem vende e como fala. |
| L07 | climax | E olha que interessante… / a mesma pergunta volta com a **cara do seu negócio**. [pausa] |
| L08 | reflexao | A IA não adivinha. / Quanto melhor você explica, / melhor ela trabalha pra você. [pausa] |
| L09 | cta | Comenta **GUIA** que eu te mando o prompt mestre no direct. |
| L10 | cta | E manda pra quem ainda briga com o ChatGPT. |
| L01B | gancho-alt | Existe um jeito de usar o ChatGPT que quase ninguém conhece. |
| L01C | gancho-alt | Pare de pedir coisas pro ChatGPT desse jeito. |

## Cenas extras

| ID | Tipo | O que mostrar | Como obter / fonte | Crédito | Som | Linhas |
|---|---|---|---|---|---|---|
| E01 | tela | ChatGPT: o pedido fraco e a resposta genérica | Carlos grava o ecrã (Chat temporário, zoom 150%) | — | não | L03–L05 |
| E02 | animacao | 3 caixas: Contexto → IA → Resposta com a cara da loja | Claude Design (brief do animador) | — | não | L06–L08 |

<!-- Tipos: tela · print · imagem · video (terceiros, crédito obrigatório) · animacao · camera (plano de apoio com a Lumix).
Arquivos: brutos/extras/E01-descricao.ext · o /extras gera a lista do que falta e os prints automáticos. -->

## Checklist de gravação
- [ ] Lumix S5IIX vertical: V-Log, 4K 25p, 4:2:2 10-bit, 1/50, ISO base, WB fixo, "Vertical Position Info" ligado
- [ ] (opcional, decisão de 21/10) `camera-00-cor.mov` com folha branca — **não é necessária**: luz e câmera na mesma temperatura, e a cadeia de cor nunca neutraliza o branco (a folha é só conferência, nunca correção)
- [ ] Gravar cada linha; se errar, **repetir a linha inteira** (pode dizer "de novo" antes)
- [ ] Gravar também L01B e L01C
- [ ] Vídeo principal (você falando) → `videos/<slug>/brutos/principal/` (`camera-01.mov`…)
- [ ] Cenas extras → `videos/<slug>/brutos/extras/` com o ID no nome (`E01-chatgpt.mov`, `E03.png`…) — rode `/extras <slug>` para ver o que falta

## Legenda do post (rascunho)
Primeira linha com a palavra-chave de busca…

## Hashtags (máx. 5)
#inteligenciaartificial #chatgpt #iaparanegocios

## Material do CTA
Só quando `cta_tipo: palavra-material`. O que o PDF entrega, em 2–4 linhas, igual ao que a fala promete
("o prompt" = o prompt; "cinco passos" = cinco passos) e com as fontes dos fatos que entram nele.
Quem escreve e gera o PDF é o **produtor-de-material**, logo depois do roteiro aprovado
(`videos/<slug>/material/<arquivo>.pdf`) — o roteirista não escreve o PDF.

## Fontes
- (links de notícias/dados citados)
