---
slug: 2026-10-22-15-coisas-ia-negocio
tema: "15 coisas que a IA já faz no seu negócio — lista que enche na tela (linha 2, engajamento)"
pilar: casos-de-uso-negocio
# Molde: oluizsampaio DchGxWDxR6O (MESA §1 e §3) — lista 1→15 vazia na tela que vai enchendo item a item,
# sem introdução. O "15" é a âncora numérica da estrutura 2 (número sozinho → o que ele representa → itens → CTA).
estrutura: "2-numero-que-choca"
hook_template: lista
publico: negocios
duracao_alvo: 70                 # alvo do pedido: 45–75 s; estimativa do parse_roteiro: ~72 s (155 palavras, rodada 1 do revisor)
palavras_alvo: 161              # wps_roteiro 2,3 × 70 (00-marca/voz-carlos.md, não calibrado)
wps_ref: 2.3
hooks:
  A: {fala: "Quinze coisas que a IA já faz no seu negócio.", tela: "15 COISAS QUE A IA JÁ FAZ", visual: "lista 1–15 vazia em cima, Carlos embaixo"}
  B: {fala: "Tem negócio? Salva essa lista de quinze coisas pra IA.", tela: "DONO DE NEGÓCIO, SALVA", visual: "lista 1–15 vazia em cima, Carlos embaixo"}
  C: {fala: "Quinze tarefas do seu negócio que a IA já faz com você.", tela: "15 TAREFAS PRA IA", visual: "lista 1–15 vazia em cima, Carlos embaixo"}
hook_escolhido: A
titulo: {contexto: "15 coisas que a IA", impacto: "já faz no seu negócio", cinza: 2, rabisco: "negócio"}
pose_capa: "mão aberta mostrando os cinco dedos, sobrancelha erguida"
cta_tipo: palavra-material
cta_palavra: LISTA
material: "PDF com as 15 coisas que a IA já faz num pequeno negócio e, para cada uma, o pedido (prompt) pronto para copiar no ChatGPT ou no Gemini"
material_titulo: "a lista com os 15 pedidos prontos"
status: rascunho
versao: 1
---

# 15 coisas que a IA já faz no seu negócio

## Roteiro

> **POSE DA CAPA (antes de falar qualquer coisa).** Mão aberta mostrando os cinco dedos, sobrancelha erguida —
> **segure 3 segundos**, em silêncio. É desse trecho que sai o frame da capa do feed. O ChatGPT Voz lê essa
> linha em voz alta antes da L01.

<!-- Linha 2 (rápidos de engajamento). Ritmo de metralhadora nos itens (L03–L17): uma linha por item, para a
lista da E01 escrever o nome do item no momento em que ele é falado. Os números (1…15) ficam só na tela;
na fala, só "a quinze" no último, para fechar a contagem. -->

| ID | Seção | FALA |
|---|---|---|
| L01 | hook | **Quinze** coisas que a IA / já faz no **seu** negócio. |
| L02 | promessa | Espera a quinze, / que é pra quem mora fora, / e no final eu te mando tudo. |
| L03 | corpo | Responder cliente no **WhatsApp**. |
| L04 | corpo | Responder em **inglês**, / sem travar. |
| L05 | corpo | O cardápio, / já traduzido. |
| L06 | corpo | Legenda de post. |
| L07 | corpo | Descrição de produto. |
| L08 | corpo | Trocar o fundo da **foto** do produto. |
| L09 | corpo | Orçamento bem organizado. |
| L10 | corpo | Aí a parte chata: / **cobrança** educada. |
| L11 | corpo | Escala da equipe. |
| L12 | corpo | Fórmula de planilha / que você nunca lembra. |
| L13 | corpo | Ideia de promoção / pra semana fraca. |
| L14 | corpo | Roteiro de vídeo. |
| L15 | corpo | Resposta pras perguntas / que todo cliente repete. |
| L16 | corpo | Anúncio de vaga. |
| L17 | payoff | E a quinze, / pra quem mora fora: / a **carta oficial** em inglês que chegou em casa. |
| L18 | payoff | Tira uma foto, / e ela te explica em **português**. [pausa] |
| L19 | payoff | Tudo no **ChatGPT** ou no **Gemini**, / até na versão grátis, / com limite por dia. |
| L20 | payoff | Ela ainda erra, tá? / Confere antes de mandar, / e tapa seus dados na carta. |
| L21 | cta | Comenta **LISTA** pros quinze pedidos, / e **salva** pra fazer um por dia. |
| L01B | hook-alt | Tem negócio? / Salva essa lista de **quinze** coisas pra IA. |
| L01C | hook-alt | Quinze tarefas do seu negócio / que a IA já faz **com** você. |

## Cenas extras

| ID | Tipo | O que mostrar | Como obter / fonte | Crédito | Som | Linhas |
|---|---|---|---|---|---|---|
| E01 | animacao | LISTA ANIMADA, faixa contínua de L01 a L20 (deitada 16:9 → split: lista em cima, Carlos embaixo). Título fixo "15 COISAS QUE A IA JÁ FAZ NO SEU NEGÓCIO"; números 1–15 visíveis e **vazios desde o 1.º quadro** (o tema e o contador aparecem antes de 2 s). De L03 a L17 cada item é escrito na sua linha **no momento em que é falado**, com efeito de digitação curta: 1 Responder cliente no WhatsApp · 2 Resposta em inglês · 3 Cardápio traduzido · 4 Legenda de post · 5 Descrição de produto · 6 Fundo da foto do produto · 7 Orçamento organizado · 8 Cobrança educada · 9 Escala da equipe · 10 Fórmula da planilha · 11 Ideias de promoção · 12 Roteiro de vídeo · 13 Respostas pras perguntas repetidas · 14 Anúncio de vaga · 15 Explicar carta oficial. Ao lado de cada item, mini-ícone da ferramenta (texto: ChatGPT/Gemini; item 6: ChatGPT/Gemini com ícone de imagem; item 15: ícone de câmera). Em L18 o item 15 ganha destaque laranja (simula foto da carta → explicação em português num balão de chat). Em L19 a lista inteira fica cheia, 15/15, e entram os selos "ChatGPT" e "Gemini" (nome/ícone da ferramenta, sem nada da Korvu ao lado — regra 3) + "grátis, com limite por dia". Em L20, selo discreto "confira antes de mandar · tape seus dados". Lista com 15 linhas tem de caber legível na metade de cima: duas colunas (1–8 / 9–15) se precisar | Claude Design (brief do animador, design system `00-marca/design-system/korvu-video.md`); capturar com `scripts/capturar_animacao.mjs --warp` nos tempos da gravação | — | não | L01–L20 |
| E02 | video | INSERÇÃO OPCIONAL dentro da faixa da E01 (YouTube, mudo, ~2,2 s): mão segura o celular com o ChatGPT Voz aberto | `brutos/extras/E02-mao-chatgpt-voz.mp4` (OpenAI, "This is the new ChatGPT Voice", 0:37–0:39) | This is the new ChatGPT Voice, powered by GPT-Live (OpenAI) | não | L04 |
| E03 | video | INSERÇÃO OPCIONAL (YouTube, mudo, ~1,4 s): foto do prato no celular vira item do cardápio | `brutos/extras/E03-gemini-cardapio.mp4` (Google, "Help Wanted, Help Found", 0:23–0:24) | Help Wanted, Help Found: See How Holly is Using Gemini (Google) | não | L05 |
| E06 | video | INSERÇÃO OPCIONAL (YouTube, mudo, ~5,8 s; usar só ~2 s): mãos anexam a foto no celular, pedem, e a imagem pronta aparece | `brutos/extras/E06-anexa-foto-flores.mp4` (OpenAI, "Introducing ChatGPT Images 2.5", 0:38–0:44) | Introducing ChatGPT Images 2.5 (OpenAI) | não | L08 |
| E04 | video | INSERÇÃO OPCIONAL (YouTube, mudo, ~0,9 s): cartaz de promoção "lunch specials" no notebook | `brutos/extras/E04-gemini-cartaz-promocao.mp4` (Google, mesmo vídeo, 0:25–0:25) | Help Wanted, Help Found: See How Holly is Using Gemini (Google) | não | L13 |
| E05 | video | INSERÇÃO OPCIONAL (YouTube, mudo, ~3,3 s): anúncio de vaga pronto, em inglês e depois em espanhol | `brutos/extras/E05-gemini-anuncio-vaga.mp4` (Google, mesmo vídeo, 1:03–1:06) | Help Wanted, Help Found: See How Holly is Using Gemini (Google) | não | L16 |

<!-- CTA EXCEÇÃO A CONFIRMAR PELO CARLOS: a L21 junta palavra-chave + salvar com momento ("um por dia")
num só fecho de 12 palavras (MESA §1 regras 4 e 5; revisor, rodada 1). O 00-marca/cta.md proíbe dois CTAs
falados — se o Carlos não aceitar, a L21 vira só "Comenta LISTA que eu te mando os quinze pedidos no direct."
"Manda pra quem tem negócio" fica só na legenda. -->

<!-- E02–E06: complementos de vídeo oficial (OpenAI/Google) para quebrar a lista só onde fizer sentido; a E01 (lista animada) continua a base L01–L20 e cada inserção é corte seco curto dentro dela. Itens de ~1,5 s: usar no máximo 2–3 inserções para não competir com a digitação da lista. Catálogo: material/youtube/catalogo.md -->

<!-- O CTA (L21) é o Carlos em tela cheia (regra 6 do CLAUDE.md). A E01 abre já no hook (pedido do
orquestrador, molde oluizsampaio: a lista vazia é o contador que segura) — isso foge do padrão "hook em tela
cheia" de 00-marca/layouts.md; ver dúvida para o Carlos. -->

## Checklist de gravação
- [ ] Lumix S5IIX vertical: V-Log, 4K 25p, 4:2:2 10-bit, 1/50, ISO base, WB fixo, "Vertical Position Info" ligado (`00-marca/captura.md`)
- [ ] Primeira tomada do dia: `camera-00-cor.mov` (5 s folha branca perto do rosto + 5 s rosto parado)
- [ ] Pose da capa: mão aberta mostrando os cinco dedos, sobrancelha erguida — 3 s parado
- [ ] Ritmo rápido nos itens (L03–L16), sem pausa entre eles; se errar, **repetir a linha inteira**
- [ ] Gravar também L01B e L01C
- [ ] Vídeo principal → `videos/2026-10-22-15-coisas-ia-negocio/brutos/principal/` (`camera-01.mov`…)
- [ ] A E01 é animação — nada para gravar de ecrã (`/extras 2026-10-22-15-coisas-ia-negocio` confirma)

## Legenda do post (rascunho)
15 coisas que a IA já faz no seu negócio — e dá pra começar hoje, em português.

Responder cliente, traduzir pro inglês, cardápio, orçamento, cobrança, escala, planilha… e a carta oficial que chegou em casa.
Tudo no ChatGPT ou no Gemini — dá pra começar na versão grátis, com limite por dia. Ela ainda erra: confira antes de mandar e tape seus dados pessoais.

→ Comenta LISTA que eu te mando os 15 pedidos prontos no direct.
→ Manda pra quem tem negócio e ainda faz tudo isso sozinho.

## Hashtags (máx. 5)
#inteligenciaartificial #chatgpt #pequenosnegocios #empreendedorismo #iaparanegocios

## Material do CTA
PDF de 1–3 páginas, título "15 coisas que a IA já faz no seu negócio" (arquivo sugerido:
`material/15-coisas-ia-negocio.pdf`). Entrega exatamente o que a fala promete: **os 15 itens, na mesma ordem
do vídeo, cada um com o pedido (prompt) pronto para copiar**, com o espaço entre colchetes para a pessoa
completar ([seu negócio], [mensagem do cliente]…). Indicar em cada item onde funciona (ChatGPT, Gemini; os de
texto também no Claude). Item 6 (fundo da foto): ChatGPT ou Gemini, enviando a foto. Item 15 (carta oficial):
enviar foto ou PDF e pedir explicação simples em português + o que precisa ser feito e até quando — com o aviso
de **tapar números de documento, conta e dados pessoais antes de enviar** e de que a IA não substitui contador
nem advogado. Rodapé: "a IA ainda erra — confira antes de mandar". Nada de prometer resultado, economia de
tempo ou dinheiro.

## Fontes
- Edição de foto enviada pelo usuário no ChatGPT, inclusive no plano grátis (com limite de uso): OpenAI Help Center, "Images in ChatGPT" — https://help.openai.com/en/articles/11084440
- Envio de arquivos/fotos para o ChatGPT ler (carta, planilha): OpenAI Help Center, "File Uploads FAQ" — https://help.openai.com/en/articles/8555545-file-uploads-faq
- Edição de imagem no app Gemini para todos os usuários (modelo Gemini 2.5 Flash Image, "nano-banana"), cobertura de 2025: https://www.digit.in/news/general/gemini-app-can-now-blend-restyle-and-edit-photos-with-a-single-text-prompt-heres-how.html/amp/ e https://www.neowin.net/news/the-gemini-app-now-lets-you-edit-images-directly/ — **conferir no blog oficial do Google (blog.google) antes de publicar** e anotar a página no PDF
- Os demais itens (texto, tradução, planilha, ideias) são uso básico de chat, disponível na versão grátis dos três.
- Molde: `01-ideias/pesquisas/referencias-instagram/MESA.md` §1 e §3; `oluizsampaio.md` (Reel DchGxWDxR6O)
