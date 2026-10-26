VEREDICTO: APROVADO (rodada 2; a rodada 1, abaixo, foi REVISAR)

Rodada 1. `parse_roteiro.py`: sem erros (22 linhas, 147 palavras, ~68,7 s; alvo 150 ±10% e 45–75 s: OK).
Estrutura, IDs, mapeamento item→linha (L03…L17 = itens 1…15), E01 cobrindo L01–L20 sem o CTA, pausa da capa no topo (fora da FALA): tudo OK.
Bloqueios: 2 correções de segurança de fato/privacidade (L19, L20) e a decisão do CTA duplo (L22). O resto é ajuste fino.

## Notas dos hooks (rubrica de hooks.md; pesos 20/20/20/15/15/10)

| Hook | Clareza | Curiosidade | Autorrelev. | Especific. | Interrup. visual | Envio | Final |
|---|---|---|---|---|---|---|---|
| A (escolhido) "Quinze coisas que a IA já faz no seu negócio." (9 palavras; tela 6) | 9 | 5 | 8 | 6 | 8 | 7 | **7,2** |
| B "Tem negócio? Salva essa lista de quinze coisas pra IA." (10; tela 4) | 8 | 4 | 9 | 6 | 8 | 8 | **7,1** |
| C "Quinze tarefas do seu negócio que a IA já faz com você." (10; tela 4) | 7 | 5 | 8 | 6 | 8 | 6 | **6,7** |

Limites de palavras (fala ≤12, tela 4–7) e visual definido: OK nos três. A é a maior nota: escolha justificada. Ponto forte: número + lista vazia enchendo é compreensível em 1 s sem som. Nota 7,2 = "aprovado com ajuste": a curiosidade é baixa (promete uma lista, não abre pergunta). Sugestão: usar L02 para abrir a lacuna do item 15, que já é o payoff:
- L02 → "Anota aí, / ou melhor, não anota. / A quinze é a que mais surpreende, e no final eu te mando tudo." (cabe em ~4 s; mantém a promessa até 8 s). Se preferir manter L02 como está, aceitável.
Hook B não deve ser o escolhido: pede "salva" no 1.º segundo (pedido antes de entregar valor) e soma um segundo CTA.

## Problemas por linha

1. **L19 → "Tudo ... até na versão grátis" é impreciso → REESCREVER.** Texto básico (itens 1–5, 7, 9–14), edição de foto enviada (item 6) e leitura de foto de carta (item 15) funcionam em ChatGPT e Gemini sem pagar, mas com limite diário de uso, que varia por conta, país e demanda (busca de hoje: fontes divergem de ~10–20 a ~100 edições de imagem/dia no Gemini grátis; as próprias fontes do roteiro dizem "com limite"). Dizer "até na grátis" sem ressalva pode frustrar quem bater no limite; e a regra de hooks.md (#2) exige "grátis" verdadeiro no dia. Sugestão literal: **"Tudo no ChatGPT ou no Gemini, / até na versão grátis, / com limite por dia."** (11 palavras; some "grátis" do selo da E01 → "grátis (com limite)"). Antes de gravar, o Carlos deve testar ele mesmo os itens 6 e 15 nas contas grátis e conferir a página oficial do Google (blog.google), como o próprio roteiro já anota em Fontes.
2. **L20 → falta o aviso de privacidade da carta (item 15) → REESCREVER.** A fala manda fotografar uma carta oficial (nome, morada, NI/NIF, conta) e enviar à IA, e o aviso de "tapar dados" só estaria no PDF, que quase ninguém lê antes de testar. Regra do próprio CLAUDE.md/hooks (#18 alerta) e público de imigrantes (cartas de impostos, imigração) pedem o aviso no vídeo. Sugestão literal: **"Ela ainda erra, tá? / Confere antes de mandar. / E tapa seus dados na carta."** (+5 palavras, ~2 s; total ~152, dentro do alvo). Selo da E01 em L20: "confira / tape seus dados".
3. **L22 "E salva, pra testar uma por dia." → decidir (ver pontos para o Carlos).** Recomendação padrão: tirar da fala e deixar na legenda; se mantiver, é exceção a uma regra explícita.
4. L02 → "ou melhor, não anota" funciona (hesitação natural, boa), manter. Sem promessa excedida: "no final eu te mando tudo" é paga em L21 + PDF.
5. L04 → "sem travar": ok, não promete resultado mensurável. L12/L13: ok.
6. Legenda do post: acrescentar "grátis, com limite diário" onde diz "Tudo no ChatGPT ou no Gemini" e "tape seus dados antes de enviar a carta". Legenda tem 1 CTA principal (LISTA) + 1 secundário diferente (manda pra quem...): correto conforme cta.md. Se L22 sair do vídeo, pode virar o secundário "Salva pra testar uma por dia" (e "manda pra quem..." fica como alternativa).

## Pontos a registrar para o Carlos (não reprovam sozinhos)

**A. "Salva" como fecho (L22) vs `cta.md`.** `cta.md` é explícito em dois lugares: regra 1 ("um CTA principal por Reel... opcional: um CTA secundário diferente, **só na legenda**") e "Nunca fazer: dois CTAs falados no mesmo vídeo". O pedido de salvar vem da pesquisa (MESA §1 regra 5), não de uma decisão do Carlos; `docs/decisoes.md` 13/10 pede "fazer salvar e comentar", o que a legenda e o PDF já cumprem. Conta como segundo CTA falado, ou seja, contraria a regra escrita, e L21+L22 somam 18 palavras (regra 5: CTA falado ≤12). Não reprovei só por isso. Opções: (a) tirar L22 e pôr "Salva pra testar uma por dia" na legenda (conforme a regra; recomendo); (b) o Carlos autoriza a exceção para a linha 2 e registra em `docs/decisoes.md` + `cta.md`. Se (b), fundir numa linha ≤12 palavras: "Comenta LISTA que eu mando os quinze pedidos, e salva pra testar." (11).
**B. Lista na tela já no hook (E01 split em L01) vs `layouts.md`.** layouts.md manda abrir e fechar com o Carlos em tela cheia (hook e CTA). Aqui o CTA está correto (tela cheia, sem extra: o parse aceita). O hook em split foge do padrão, mas é a própria mecânica do molde (lista vazia que enche = contador de retenção) e hooks.md proíbe começar com rosto parado. Parece aceitável como exceção deliberada; o Carlos deve confirmar e, se aprovar, registrar em `docs/decisoes.md`.
**C. "te mando" / "direct".** PT-BR coloquial aceito: `tom-de-voz.md` lista "te mandar" como o uso correto e `cta.md` usa "que eu te mando... no direct" no modelo oficial. Nada de "tu/teu", "ecrã" etc. no roteiro. Nenhuma palavra banida encontrada ("mindset", "bora", "cara" etc.).

## Demais checagens

- **Voz / "soa a IA?"**: passa (0–1 sinal). Cadência de lista é intencional do molde; compensada por "Anota aí, ou melhor, não anota", "Aí a parte chata", "Ela ainda erra, tá?", frases começando com "E"/"Aí", contrações (pra, tá) e exemplos concretos (carta oficial, cardápio, WhatsApp). Sem pares simétricos nem expressões de manual.
- **Retenção**: promessa em L02 (≤8 s); troca visual a cada item (~1,5–3 s) via E01; payoff (item 15) antes do CTA; loop final fraco: nada reabre depois de L22. Opcional (não bloqueia): fechar com "amanhã tem mais" não, evitar prometer série sem frequência real.
- **Fatos**: itens 1–5, 7, 9–14 = uso básico de chat (verdadeiro nos dois, grátis). Itens 6 e 15 verdadeiros com limites (ver L19); item 15: IA pode errar prazos/valores de carta oficial, o "confere" cobre, e o PDF já traz "não substitui contador/advogado". Nenhuma promessa de renda ou tempo economizado. Sem número que precise de fonte.
- **CTA / material**: palavra LISTA permitida e sem acento; tipo A. `videos/2026-10-22-15-coisas-ia-negocio/material/` está **vazia** (PDF `15-coisas-ia-negocio.pdf` ainda não existe). Pelo fluxo de `cta.md`, o `produtor-de-material` gera o PDF logo após o roteiro aprovado; **não publicar nem agendar antes do PDF existir**, com os 15 itens na ordem do vídeo + prompt de cada um + aviso de tapar dados + "a IA ainda erra". Verificar que LISTA não repete na mesma semana.
- **Formato**: FALA sem indicações; `[pausa]` só no fim da L18 (aceitável como beat do payoff); IDs corretos; hooks B/C com visual definido; E01 liga L01–L20 e deixa L21–L22 em tela cheia.
- **Público**: iniciante entende sem pesquisar (sem jargão); dono de negócio vê aplicação prática em cada linha; "pra quem mora fora" casa com o público lusófono na Europa/UK. Legenda só em PT, Trial Reel: coerente com decisoes 13–14/10.

## Correções pedidas (resumo)

1. L19 → "Tudo no ChatGPT ou no Gemini, / até na versão grátis, / com limite por dia." (e ajustar selo/legenda).
2. L20 → acrescentar "E tapa seus dados na carta."
3. L22 → decisão do Carlos (A): recomendo mover para a legenda.
4. (Opcional) L02 → abrir a lacuna do item 15 para subir a curiosidade do hook A.
5. PDF do material: criar antes de publicar.

---

# Rodada 2 (final)

VEREDICTO: APROVADO

`parse_roteiro.py`: sem erros (21 linhas, 155 palavras, ~72 s; alvo 161 ±10% e 45–75 s: OK, perto do teto).

## Pedidos da rodada 1
1. L19 "Tudo no ChatGPT ou no Gemini, / até na versão grátis, / com limite por dia." aplicado. Selo da E01 e legenda do post também dizem "com limite por dia". OK.
2. L20 "...e tapa seus dados na carta." aplicado; selo da E01 em L20 e legenda avisam. OK.
3. L22 fundida na L21: "Comenta LISTA pros quinze pedidos, e salva pra fazer um por dia." (12 palavras, dentro do teto de 12). Exceção a `cta.md` (dois CTAs falados), pendente do Carlos; não bloqueia. Se negar, fallback já previsto no roteiro (só "Comenta LISTA...").
4. L02 (opcional) mantida como estava; aceitável. Hook A segue 7,2 (B 7,1; C 6,7), acima de 6.
5. PDF: `material/` continua vazia. Não bloqueia o roteiro (o `produtor-de-material` gera após aprovação), mas NÃO empacotar/publicar/agendar sem `15-coisas-ia-negocio.pdf` (15 itens na ordem, prompt de cada, aviso de tapar dados, "a IA ainda erra").

## Fatos e decisões
- 15 itens: nenhuma promessa de renda, tempo ou dinheiro; "sem travar" e "ela ainda erra" ok. Itens 6 e 15 corretos com limite diário no plano grátis. Antes de publicar: Carlos testar 6 e 15 em conta grátis e conferir a página oficial do Google (blog.google), como já consta em Fontes.
- Mapeamento item→linha L03–L17 = 1–15 bate com a E01; E01 cobre L01–L20, CTA em tela cheia (regra 6 ok).
- Decisões 13–14/10: público lusófono na Europa/RU ("pra quem mora fora"), legenda só em PT, formato rápido de salvar/comentar, CTA falado com palavra-chave e material em PDF, Trial Reel: coerentes. Duração de 72 s cabe nos 90 s permitidos.

## Anotado para o Carlos (não bloqueia)
- A. "Comenta LISTA... e salva" na mesma fala contraria `cta.md`; se aceitar, registrar em `docs/decisoes.md` e `cta.md`.
- B. Lista animada já no hook (split) contraria `layouts.md` (hook em tela cheia); se aceitar, registrar em `docs/decisoes.md`.
