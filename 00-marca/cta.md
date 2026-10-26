# CTA — fonte única

> **Este é o único arquivo que define CTAs.** Qualquer outro arquivo que fale de CTA aponta pra cá.
> CTAs antigos com palavra fixa ("corvo", "KORVU"), secretária ou agendamento de reunião estão **descontinuados**. Não usar.

---

## Regras gerais

1. **Um CTA principal por Reel** — falado nos 55–60s e escrito na tela. Opcional: **um CTA secundário diferente, só na legenda**.
2. **Nunca pedir like.** Nunca "segue pra mais conteúdo" genérico.
3. **Sem engagement bait puro** ("comenta SIM", "marca três amigos", "comenta se concorda"). Todo pedido está ligado a um valor real.
4. **Nunca prometer material que não existe.**
5. CTA falado com **≤12 palavras**. Pode vir seguido de UM pedido curto de enviar/salvar com destinatário concreto ("e manda pra quem…") — exceção de 14/10, ver `docs/decisoes.md`. A palavra-chave aparece na tela em caixa alta, no laranja da marca.
6. O CTA combina com o pilar (tabela de rotação abaixo).

---

## Tipo A — Palavra-chave → material no direct (principal)

**Fala padrão:**
> "Comenta **[PALAVRA]** que eu te mando **[o prompt / o guia]** no direct."

**Variações:**
> "Quer o prompt completo? Comenta PROMPT que chega no seu direct."
> "Comenta GUIA aqui embaixo que eu te mando o passo a passo."

### Regras da palavra-chave
- Definida **por vídeo** no campo `cta_palavra` do frontmatter do roteiro.
- **Uma palavra, CAIXA ALTA, sem acento, sem cedilha**, fácil de digitar no celular: **até ~6 letras**, grafia óbvia em português (evitar PROMPT, ENTREVISTA, palavras em inglês com consoantes difíceis). A facilidade vem antes da ligação com o tema (decisão de 14/10).
- Ligada ao material: `PROMPT`, `GUIA`, `IA`, `AGENTE`, `LISTA`, `PASSOS`, `MODELO`, `PLANILHA`.
- **Variar.** Não repetir a mesma palavra em Reels da mesma semana.
- **Proibidas:** `CORVO` e `KORVU` (fluxo descontinuado); palavras com acento (`AUTOMAÇÃO`, `DIAGNÓSTICO`); palavras que as pessoas digitam por acaso (`OI`, `SIM`, `EU`, `TOP`).

### Regras do material
- **Sempre um PDF** (decisão do Carlos, 13/10: "é link, sempre vai ser o link com o material em PDF"). Quem faz é o agente **`produtor-de-material`**, a partir do roteiro, logo depois do roteiro aprovado — sem o Carlos pedir. O roteiro marca a necessidade com `cta_palavra` + `material` + `material_titulo`.
- O material **TEM que existir em `videos/<slug>/material/<arquivo>.pdf` antes de publicar** — arquivo final, não rascunho. Dossiê, fontes e estudo nunca são o material (o PDF vai para um link público).
- O que a fala promete é exatamente o que o arquivo entrega ("prompt" = o prompt; "guia com cinco passos" = cinco passos).
- Formato leve, que abre no celular: texto do prompt, PDF curto ou link.
- Sem material pronto → trocar pra CTA tipo B, C ou D. Sem exceção.

### Entrega
- Feita pelo **`scripts/responder_comentarios.py`** (sem ManyChat, sem CRM, **sem conversa** — decisão de 09/10). Textos em `automacao-meta/respostas.yaml`; funcionamento em `automacao-meta/ARQUITETURA.md`.
- A automação identifica o comentário pela palavra + o post, manda **um direct com o LINK do material** (PDF no R2) e depois responde em público no comentário ("já te mandei no direct").
- A Meta só deixa UM direct por comentário (até 7 dias): tudo o que a pessoa precisa vai nessa mensagem.
- O material precisa estar em **PDF** (ou link) e ter `material.titulo` no `post.json` ("o guia do prompt").

### Aviso na DM (envio automático)
A mensagem **sempre** diz que é envio automático, e **pode pedir like e follow** — exceção à regra 2, decidida pelo Carlos em 09/10, que vale **só no direct**, depois de entregar o material (no vídeo e na legenda a regra 2 continua). Modelo em `automacao-meta/respostas.yaml`:
> "Oi, @ana! 👋 Aqui é o envio automático da Korvu. Aqui está [o material] que você pediu no vídeo: [link]. Se o conteúdo te ajudou, deixa seu like no Reel e segue a @korvu_oficial — toda semana tem IA nova explicada do jeito simples 🚀"

Regras do bot:
- Nunca se passar pelo Carlos.
- Nunca pedir dado sensível (documento, senha, dados bancários).
- Se pedir e-mail: dizer pra quê e como sair da lista (`regras-legais.md`).
- Respeitar "parar"/"sair" imediatamente.

---

## Tipo B — Envio (compartilhamento)

> "Manda esse vídeo pra alguém que ainda faz [X] na mão."

Variações:
> "Manda pro seu contador."
> "Conhece um dono de restaurante? Manda pra ele."
> "Manda pra aquele amigo que ainda tem medo de IA."

**Por quê:** envios por DM são o sinal mais forte pra o Reel chegar em quem ainda não te segue.
**Usar em:** casos de uso por profissão, mitos e erros, notícia explicada.

## Tipo C — Salvar

> "Salva pra não perder."
> "Salva esse vídeo — você vai precisar quando for [fazer X]."

**Usar em:** prompts, listas, tutoriais (conteúdo de consulta).

## Tipo D — Seguir (sempre específico)

> "Sigo postando uma ferramenta de IA por dia."

**Regra:** só prometa a frequência que a gente cumpre de verdade. Com 3 Reels/semana, por exemplo:
> "Toda semana eu mostro uma IA nova que você usa no celular. Me segue."

**Usar em:** notícia explicada, opinião/bastidores, Reels com cara de alcance alto.

---

## Rotação por pilar

| Pilar (`pilares.md`) | CTA principal (vídeo) | CTA secundário (legenda) |
|---|---|---|
| Tutoriais rápidos | C Salvar (ou A com `GUIA`, se houver passo a passo) | A ou D |
| Prompts prontos | A (`PROMPT`) | C Salvar |
| Mitos e erros | B Envio | D Seguir |
| Casos de uso por profissão | B Envio ("manda pro seu [profissão]") | A |
| Antes/depois | A (o prompt usado) | C Salvar |
| Notícia explicada | D Seguir | B Envio |
| Opinião/bastidores | D Seguir | Pergunta real na legenda |

## Rotação por objetivo

| Objetivo do Reel | CTA |
|---|---|
| Alcançar gente nova | B Envio |
| Gerar contatos (leads) | A Palavra-chave |
| Valor de consulta | C Salvar |
| Crescer a base | D Seguir |

**Equilíbrio semanal:** no máximo 3 de cada 5 Reels com CTA tipo A (evita cansar o público e os comentários virarem só palavra-chave).

---

## Padrão de legenda

```
[Linha 1 — gancho da legenda, ≤125 caracteres, completa o vídeo (não copia a fala)]

[2 a 4 linhas curtas: resumo, passo a passo ou "o que muda pra você"]

→ [CTA principal — o mesmo do vídeo]
→ [CTA secundário — ação diferente]

[Fonte: veículo, data — obrigatório em notícia ou dado]
[Aviso de IA, se houver visual realista gerado por IA]

#tag1 #tag2 #tag3   (máximo 5)
```

**Exemplo (pilar Prompts prontos):**
```
Esse prompt responde cliente irritado sem você perder a paciência.

Você cola a mensagem do cliente, ele devolve uma resposta educada e firme.
Funciona no ChatGPT, no Gemini e no Claude.

→ Comenta PROMPT que eu te mando ele completo no direct.
→ Salva pra usar na próxima reclamação.

#inteligenciaartificial #chatgpt #pequenosnegocios #atendimento #prompts
```

---

## Nunca fazer

- "Deixa seu like" / "curte o vídeo"
- "Segue a conta pra mais conteúdo"
- "Comenta SIM se você concorda" (bait sem valor)
- Dois CTAs falados no mesmo vídeo
- Prometer "guia", "checklist" ou "modelo" que ainda não existe
- Palavra-chave com acento ou repetida na mesma semana
- Reel sem CTA

## Checklist antes de publicar

- [ ] Um CTA principal, coerente com o pilar
- [ ] Se tipo A: `cta_palavra` preenchida, material final em `videos/<slug>/material/`, palavra cadastrada na automação
- [ ] Palavra na tela, legível, dentro da zona segura
- [ ] Legenda com CTA principal + secundário diferente, fonte (se notícia), máximo 5 hashtags
