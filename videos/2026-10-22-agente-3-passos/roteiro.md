---
slug: 2026-10-22-agente-3-passos
tema: "Agente de IA em 3 passos (pra quem nunca fez): um Gem do Gemini que escreve a resposta pro cliente no tom da casa"
pilar: tutoriais-rapidos
estrutura: "6-sistema-vs-vontade"
hook_template: resultado-primeiro
publico: ambos
duracao_alvo: 70
palavras_alvo: 155
wps_ref: 2.3
hooks:
  A: {fala: "Olha isso: / o cliente pergunta, / e a resposta já sai pronta.", tela: "RESPOSTA PRONTA PRO CLIENTE", visual: "abre na tela: mensagem do cliente colada no Gem e a resposta aparecendo (E01)"}
  B: {fala: "Seu primeiro agente de IA. / Grátis, / em três passos.", tela: "SEU 1º AGENTE EM 3 PASSOS", visual: "título gigante + tela do Gem respondendo atrás (E01)"}
  C: {fala: "Você ainda responde cliente na mão? / Olha o que dá pra montar.", tela: "AINDA RESPONDE NA MÃO?", visual: "corte seco para a resposta pronta na tela (E01)"}
hook_escolhido: A
titulo: {contexto: "Seu primeiro agente de IA", impacto: "em três passos", cinza: 2, rabisco: "três"}
pose_capa: "parado olhando para a câmera, expressão leve, boca fechada, sem gesto de mão"
cta_tipo: palavra-material
cta_palavra: AGENTE
material: "material/agente-3-passos.pdf — o passo a passo de criar um Gem no Gemini (com prints e o link oficial da Central de Ajuda) + o texto de instruções do assistente de atendimento pronto pra copiar e adaptar"
material_titulo: "o passo a passo do seu primeiro agente"
fontes:
  - "https://support.google.com/gemini/answer/15146780?hl=pt-BR"
  - "https://www.androidauthority.com/gemini-gems-free-3534726/"
  - "https://chromestory.com/2026/07/create-gem-gemini-app/"
status: rascunho
versao: 1
---

# Agente de IA em 3 passos (pra quem nunca fez)

## Roteiro

> **POSE DA CAPA (antes de falar qualquer coisa).** Parado, olhando para a câmera, expressão leve, boca fechada,
> **sem gesto de mão** — **segure 3 segundos**, em silêncio. É desse trecho que sai o frame da capa do feed.
> O ChatGPT Voz lê esta linha em voz alta antes da L01.

<!-- Molde: Jeff Su ("explicado em 3 passos", mesmo exemplo do começo ao fim) + Allie K. Miller (iniciante absoluto).
Esqueleto da linha 3 (MESA.md §4): resultado no 1.º s → "em 3 passos" numerado → cada passo com a tela real →
AGENTE (PDF) → "salva pra fazer no fim de semana".
Honestidade (ferramenta.md): o Gem NÃO atende sozinho no WhatsApp/Instagram — o dono cola a mensagem e o Gem escreve
a resposta. Isso é dito na L11. O café da tela é um EXEMPLO de demonstração, não um cliente real. -->

| ID | Seção | FALA |
|---|---|---|
| L01 | hook | Olha isso: / o cliente pergunta, / e a resposta já sai **pronta**. |
| L02 | promessa | Eu chamo de **agente** de IA. / Você monta o seu em **três passos**. [pausa] |
| L03 | corpo | Agente aqui é um assistente, / tipo funcionário novo / que já leu as **regras** da sua loja. |
| L04 | corpo | E criar é **grátis**, / só precisa de conta Google. |
| L05 | corpo | **Passo um**: / no computador, / abre o Gemini, / clica em Gems, / Novo Gem. |
| L06 | corpo | **Passo dois**: / um nome / e como ele tem que responder. |
| L07 | corpo | Tipo: / responde curto, simpático / e nunca inventa preço. |
| L08 | corpo | **Passo três**, / o pulo do gato: / em Conhecimento, / você sobe a sua lista de preços. |
| L09 | corpo | Salvar. / Pronto. [pausa] |
<!-- L09: gravar "Salvar. Pronto." de uma vez só, como uma linha. -->
| L10 | payoff | Chegou mensagem? / Você cola ali, até no celular, / e ele escreve a resposta com os **seus** preços. |
| L11 | payoff | Ele não manda sozinho no WhatsApp, tá? / Quem confere e envia é **você**. |
| L12 | cta | Comenta **AGENTE** / que eu te mando o passo a passo no direct. |
| L13 | cta | Com as instruções prontas pra copiar. / Salva pra fazer no **fim de semana**. |
| L01B | hook-alt | Seu primeiro agente de IA. / Grátis, / em três passos. |
| L01C | hook-alt | Você ainda responde cliente na mão? / Olha o que dá pra montar. |

## Cenas extras

> Gravações de tela do Carlos (tela-01…tela-05) no **Gemini em português**, conta Google pessoal, zoom 150 %,
> sem dados pessoais visíveis. Exemplo de demonstração: Gem "Atendente do Café", com um PDF curto de preços e
> horários **feito para o vídeo** (não é cliente real). A mesma demonstração do começo ao fim (molde Jeff Su).
> Os extras encostados formam faixa contínua com corte seco. **L12–L13 (CTA) sem extra**: o Carlos em tela cheia.

| ID | Tipo | O que mostrar | Como obter / fonte | Crédito | Som | Linhas |
|---|---|---|---|---|---|---|
| E01 | tela | tela-01 — RESULTADO: no Gem "Atendente do Café", colar a mensagem "Oi! Vocês abrem domingo? Quanto é o bolo de cenoura inteiro?" e a resposta aparecendo, com horário e preço do arquivo; selo "EXEMPLO" na tela (café fictício) | Carlos grava a tela (gemini.google.com, Gem já criado) | — | não | L01 |
| E02 | animacao | Card numerado "1 · 2 · 3" acendendo um por um (título "SEU 1º AGENTE"), no design system Korvu | Claude Design (brief do animador) | — | não | L02 |
| E11 | video | Google Workspace, pequena equipe usando o Gemini no dia a dia ("é como ter um time de milhões"), mudo, ~6 s | YouTube oficial (Google Workspace): `brutos/extras/E11-pequena-equipe-gemini.mp4` (tem legenda embutida em inglês: cobrir ou aceitar) | Google Workspace (YouTube) | não | L03 |
| E03 | animacao | "AGENTE = assistente + regras do seu negócio" (caderninho com "preços · horários · jeito de falar") some e fica só o selo "GRÁTIS · só conta Google" | Claude Design (brief do animador) | — | não | L04 |
| E04 | tela | tela-02 — PASSO 1 (selo "1" grande no topo): gemini.google.com → abrir barra lateral → Gems → Novo Gem | Carlos grava a tela | — | não | L05 |
| E05 | tela | tela-03 — PASSO 2 (selo "2"): digitar o nome "Atendente do Café" e as instruções ("Você atende o Café… responde curto e simpático… nunca inventa preço…") | Carlos grava a tela | — | não | L06–L07 |
| E06 | tela | tela-04 — PASSO 3 (selo "3"): Conhecimento → Adicionar arquivos → Anexar arquivos (PDF de preços e horários) → Salvar | Carlos grava a tela | — | não | L08–L09 |
| E07 | tela | tela-05 — USO: abrir o Gem salvo, colar outra mensagem de cliente e a resposta pronta com os preços do arquivo; no fim, o mesmo Gem no app do Gemini no celular | Carlos grava a tela do computador + do celular | — | não | L10 |
| E08 | animacao | Card animado em 3 tempos: "você cola" → "ele escreve" → "você confere e envia" (o Gem não envia sozinho) | Claude Design (brief do animador) | — | não | L11 |

> **Alternativas em vídeo (opcionais, cortadas, não ligadas a linha):** E09 `brutos/extras/E09-holly-celular-pergunta.mp4` (3,4 s, celular com Gemini: pergunta e resposta; crédito Google) para L01/L10; E10 `brutos/extras/E10-gmail-sugerir-resposta.mp4` (3,7 s, texto gerado aparecendo no Gmail/Docs; mostra um rosto no começo; crédito Google Workspace). Total citado hoje: 12,9 s a 13,9 s (sem teto desde 14/10).

## Checklist de gravação
- [ ] Lumix S5IIX vertical: V-Log, 4K 25p, 4:2:2 10-bit, 1/50, ISO base, WB fixo, "Vertical Position Info" ligado
- [ ] Primeira tomada do dia: `camera-00-cor.mov` (5 s folha branca perto do rosto + 5 s rosto parado)
- [ ] Pose da capa 3 s antes da L01
- [ ] Gravar cada linha; se errar, **repetir a linha inteira** (pode dizer "de novo" antes)
- [ ] Gravar também L01B e L01C
- [ ] Vídeo principal → `videos/2026-10-22-agente-3-passos/brutos/principal/` (`camera-01.mov`…)
- [ ] Gravações de tela (E01, E04–E07) → `brutos/extras/` com o ID no nome (`E01-resultado.mov`…) — antes, criar o PDF de exemplo do "Café" (preços e horários fictícios) e conferir que a interface está em português
- [ ] Conferir no dia que os botões continuam com os mesmos nomes (Gems, Novo Gem, Conhecimento, Adicionar arquivos, Salvar)

## Legenda do post (rascunho)
Seu primeiro agente de IA, grátis, em 3 passos — mesmo que você nunca tenha mexido com IA.

Um "agente" aqui é um assistente que já conhece as regras do seu negócio: preços, horários, jeito de falar.
Você cola a mensagem do cliente e ele escreve a resposta. Quem envia continua sendo você.
Feito no Gemini (Google), só com uma conta Google.

→ Comenta AGENTE que eu te mando o passo a passo no direct, com as instruções prontas pra copiar.
→ Salva pra fazer no fim de semana.

## Hashtags (máx. 5)
#inteligenciaartificial #agentesdeia #gemini #pequenosnegocios #iaparainiciantes

## Material do CTA
PDF `material/agente-3-passos.pdf` ("o passo a passo do seu primeiro agente"), 1–3 páginas, igual ao que a fala promete:
1. **Os 3 passos** com prints da interface em português: gemini.google.com → barra lateral → Gems → Novo Gem; nome + instruções; Conhecimento → Adicionar arquivos → Salvar (e que depois aparece no app do celular). Link da Central de Ajuda oficial.
2. **O texto de instruções pronto pra copiar** do assistente de atendimento (responde curto e simpático, usa só os preços/horários do arquivo, nunca inventa preço, diz "vou confirmar e te respondo" quando não souber), com os campos para trocar pelo nome do negócio.
3. Avisos honestos:
   - o Gem escreve a resposta, mas **não** responde sozinho no WhatsApp/Instagram — a pessoa cola a mensagem, confere e envia;
   - ele **pode errar preço ou horário**: conferir sempre antes de enviar;
   - o plano gratuito tem **limites de uso** (citar só o que a página oficial do Google disser, com link — sem inventar número);
   - **não colar dados pessoais de clientes** (telefone, morada, dados de pagamento) na conversa;
   - quem tem conta europeia pode ver a interface em **português de Portugal ou em inglês**: indicar o nome dos botões nas duas versões (conferir na interface real, não traduzir de cabeça);
   - não funciona no Gemini Live; idade mínima 13 anos (ou a do país).
Sem citar data, preço ou existência de imersão.

## Fontes
- Central de Ajuda do Gemini (pt-BR), "Criar Gems": https://support.google.com/gemini/answer/15146780?hl=pt-BR — passos e nomes dos botões; Gem criado na web aparece no app do celular; não funciona no Gemini Live (conferido em 14/10/2026).
- Gems grátis em todas as contas Google pessoais (desde mar/2025): https://www.androidauthority.com/gemini-gems-free-3534726/
- Guia de criação de Gem (07/2026): https://chromestory.com/2026/07/create-gem-gemini-app/
- Pesquisa da ferramenta: `material/_fonte/ferramenta.md`
