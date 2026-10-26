# Trial Reel × Reel normal — análise de 22/10/2026

> Pedido do Carlos (22/10): "os Trials tiveram pouquíssimo alcance — vale colocar no modo normal e mudar a estratégia?"
> Dados: `_controle/metricas.md` e `07-publicados/<slug>/metricas.json` (leitura de 22/10 14:00), `_controle/perfil/2026-10-22.json` × `2026-10-16.json`, prints do app de 17/10 (`_controle/perfil/prints-2026-10-17/`, resumidos em `_controle/aprendizados.md`).
> Só análise: nada foi alterado em `docs/decisoes.md`, `_controle/calendario.md`, `post.json` ou pastas de vídeo. Quem decide é o Carlos.

## Recomendação (curta)
1. **Hinton e Fei-Fei A: deixe como estão.** Não compartilhe e não reposte.
2. **Fei-Fei B: toque em "Compartilhar com todos" no sábado 24/10**, se a A continuar abaixo dela (a regra do par A/B de 17/10 já manda fazer isso com a vencedora). É o mesmo post: vai para a grade e para os seguidores. O teste com não seguidores já acabou (as 72 h passaram), então você não perde nada, e a gente ainda mede o que o modo normal acrescenta ao mesmo vídeo.
3. **Próximos: misto por 2 semanas.** Em cada vídeo, **uma versão sai NORMAL** (grade + seguidores, IG + FB) e as variantes saem como **Trial MANUAL**. A 1.ª é a livro-chatgpt B no domingo 25/10, que hoje está agendada como Trial e precisa do seu ok para mudar. A decisão sai em ~06/11, pela regra numérica da §6.
4. Motivo, em um número: **o único Reel normal (Hassabis) chegou a ~208 NÃO seguidores; os três Trials somados chegaram a 55.** O Trial foi feito para mostrar o vídeo a quem não segue, e nesta conta ele mostrou menos do que o post normal.

---

## 1. Os números lado a lado

| Reel | Modo | Duração | Idade | Alcance IG | Não seguidores (contas) | Tempo médio IG | % assistido | Pulados (app) | FB plays (tempo médio) |
|---|---|---|---|---|---|---|---|---|---|
| Hassabis | **normal** | 57,8 s | 8,9 d | **338** | **~208** (62,2 % de 334 no app, 17/10) | 11,9 s | 20,5 % | 49,4 % | 30 (10,9 s) |
| Hinton | Trial SS_PERFORMANCE, **repostado** 36 min depois do 1.º (apagado) | 158,7 s | 7,1 d | 11 | 11 (100 %) | API inválido (1.512 s); app 34 s com 9 pessoas | — | 55,6 % | 4 (1,7 s) |
| Fei-Fei B | Trial MANUAL | 168,4 s | 3,8 d | 40 | ~40 | 9,1 s | 5,4 % | sem print | **196** (2,4 s) |
| Fei-Fei A | Trial MANUAL, 50 h depois da B, conteúdo igual | 168,5 s | 1,7 d | 4 | ~4 | 2,6 s | 1,5 % | sem print | — |

**Conta (28 dias, API):**

| | 16/10 | 22/10 | Δ |
|---|---|---|---|
| Alcance | 476 | 529 | +53 |
| Não seguidores alcançados | 263 | 307 | **+44 em 6 dias, com 3 Trials no ar** |
| Seguidores alcançados | 203 | 206 | +3 |
| Seguidores / seguindo | 3.634 / 7.495 | 3.631 / 7.505 | −3 / +10 |
| Posts na grade (`media_count`) | 7 | **5** (as fotos de 2018/2023 saíram; sobram Hassabis + 4 Reels de abril) | — |
| Toques no link | 0 | 0 | — |

**Histórico da conta (os 12 Reels que a API devolve):**
- Os **5** que foram para a grade (`is_shared_to_feed = true`: Hassabis + 4 de abril) tiveram alcance de **252 a 417**.
- Os **7** que ficaram fora dela (3 Trials + 4 de maio) tiveram de **0 a 98**.
- Nenhum Reel fora da grade passou de 98, e nenhum da grade ficou abaixo de 252. Se fosse acaso, uma separação tão perfeita teria ~0,13 % de chance (1 em 792).
- Mas abril tinha outro estilo e outra fase da conta, e não se sabe por que os de maio ficaram fora da grade. **Pergunta para você:** os Reels de maio foram publicados como teste, ou com "compartilhar no feed" desligado?

**Quem foi alcançado em outubro (API, 379 contas com país):** Brasil 52,0 %, Reino Unido 15,3 %, Portugal 13,7 %, **Guiné-Bissau 5,8 % (22 contas)**. Quem segue: Guiné-Bissau 54,4 % (1.741).

## 2. Por que os Trials ficaram em 4–40: o que os dados sustentam e o que não dá para separar

**Como o Instagram diz que o Trial funciona (fonte oficial, [creators.instagram.com](https://creators.instagram.com/blog/instagram-trial-reels)):**
- O vídeo é "shown to non-followers first".
- Fica fora da grade e da aba Reels.
- As métricas aparecem ~24 h depois.
- O compartilhamento automático com seguidores é decidido pelas **views das primeiras 72 h**. O limite não é publicado.
- Ao "share with everyone", o Reel "will live on your profile grid" e passa a ser distribuído aos seguidores.
- O Instagram **não diz** se os números do teste continuam no mesmo post. Como o post (permalink e media_id) é o mesmo, a hipótese é que somam. A gente confere pelo `is_shared_to_feed`, que passa a `true`, e pelo alcance, que deve continuar subindo a partir de 40.
- O Mosseri cita tempo assistido, curtidas por alcance e envios por alcance como os sinais principais. Para quem não segue, pesa mais o envio ([resumo em Tubefilter](https://www.tubefilter.com/2025/01/23/instagram-trial-reels-growth-hacking-creator-economy/); fonte secundária).

| Causa possível | O que os dados dizem | Veredicto |
|---|---|---|
| **Modo Trial em conta pequena** | Um Trial só cresce se a 1.ª amostra de não seguidores reagir. Os nossos receberam amostras de 4–40 pessoas, com 0 salvamentos, 0 envios e 0–1 curtida, então não havia sinal para ampliar. O Hinton estava em graduação automática e, 7 dias depois, ainda não foi compartilhado (`is_shared_to_feed = false`): o próprio Instagram julgou que não foi bem. Já o post normal chega a quem não segue **e** a quem segue: o Hassabis teve ~208 não seguidores, contra 40 do melhor Trial. | **Sustentado, mas confundido com a duração** (abaixo) |
| **Duração 158–168 s × 58 s** | Todos os Trials são longos, e o único normal é curto: modo e duração andam juntos nos 4 casos. Em %, o longo perde muito (5,4 % e 1,5 % × 20,5 %). Em segundos, o tempo médio fica parecido (9 s × 12 s). Se o Instagram olha a % concluída, o longo parece pior para ele. | **Não dá para separar com n = 4.** Daqui pra frente a pergunta perde força: todo vídeo novo tem ≤ 90 s (regra de 16/10), e a livro-chatgpt tem 34,5 s, o 1.º Trial curto |
| **Tempo médio / % assistido baixo** | Fei-Fei A: 2,6 s (as pessoas saem quase na hora). Fei-Fei B: 9,1 s. Os pulados do app ficam em ~50–56 % nos dois vídeos com print. O começo continua sendo o gargalo, em qualquer modo. | **Sustentado** como causa comum, não como diferença entre os modos |
| **Abertura (B conteúdo × A Carlos)** | Na Fei-Fei, B teve 40 e A teve 4, mas com idades diferentes (3,8 d × 1,7 d) e a A saiu como cópia da B (próxima linha). No FB, a B teve 196 plays com 2,4 s médios: o FB mostrou, mas quase ninguém ficou. | **Inconclusivo**: o par não está limpo |
| **Cópia / repost** | O Hinton foi repostado 36 min depois do 1.º. A Fei-Fei A é o mesmo vídeo da B, com só ~9 s diferentes. Hipótese: o classificador de originalidade usa sinais como "a pessoa já viu isto" ([Mosseri, 2022, via TechCrunch/AOL](https://www.aol.com/news/instagram-improve-ranking-system-better-191319059.html)) e corta a 2.ª cópia. Contra a hipótese: há criadores crescendo com Trials de vídeos antigos (Tubefilter, acima) e testes com o mesmo vídeo em Trial e normal em que os dois foram distribuídos ([Kapwing](https://kapwing.com/resources/instagram-trial-reels-study-what-we-learned-after-a-trial-reel-hit-1-million-views)). | **Hipótese plausível** para o Hinton (11) e a Fei-Fei A (4); sem fonte oficial |
| **Horário** | Hassabis ter 17:03 · Hinton qui 11:44 · Fei-Fei B dom 19:14 · A ter 21:14. Uma hora diferente por vídeo, sem repetição. | **Não dá para dizer nada** |
| **Seguindo 7.505 × 3.631 seguidores (2,07×)** | Pode pesar na recomendação de toda a conta. Vale para os dois modos e não explica a diferença entre eles. | Fator de fundo (ver `_controle/auditoria-perfil.md`) |

**Em resumo:** o que dá para afirmar é que, **nesta conta e com estes vídeos, o Trial entregou menos a não seguidores do que o post normal**: 40 no melhor caso, contra ~208. Não dá para afirmar que o Trial é o culpado sozinho, porque todos os Trials também eram longos. O teste da §6 separa as duas coisas.

## 3. O medo da bolha, com os números de hoje
A decisão de 17/10 ("não compartilhar com seguidores") partiu de que mostrar aos seguidores alimenta a bolha da Guiné-Bissau. Os dados de hoje enfraquecem esse medo:
- No mês, **a Guiné-Bissau é só 22 das 379 contas alcançadas (5,8 %)**, embora seja 54 % de quem segue. Isso quer dizer que, dos 1.741 seguidores de lá, no máximo ~1,3 % viu alguma coisa. Essa parte da base está **adormecida**: mostrar o Reel a ela não o prende ali, porque ela quase não abre.
- No Hassabis normal, os seguidores foram 37,8 % do alcance (~126 de 3.631, ou 3,5 % da base), e mesmo assim 62,2 % foi para não seguidores, com o Brasil, o Reino Unido e Portugal à frente.
- O risco que sobra é o "flop" com quem segue: o Reel é testado primeiro com eles, eles não reagem e o vídeo nasce frio ([FAQ do Instagram for Creators](https://creators.instagram.com/faq?locale=en_US): "people who follow you are typically the first to see it"). Mesmo assim, o Hassabis, testado assim, ainda bateu os três Trials somados.

## 4. Tensão nas regras (para você decidir)
Três textos de 17/10 dizem coisas diferentes:

| Onde | O que diz |
|---|---|
| `docs/decisoes.md` (linha do Trial SS_PERFORMANCE) | graduação **automática**: "só passa para seguidores/grade se for bem". Ou seja, **o Instagram compartilha com os seguidores por você** |
| `docs/decisoes.md` (linha "canal deixa de ser pessoal") e `estrategia-de-alcance.md` §2.7 | "**não** compartilhar com seguidores" |
| `estrategia-de-alcance.md` §2.8 e `testes-abertura.md` | a **vencedora** do par A/B é compartilhada com os seguidores pelo Carlos, no app |

**Proposta de regra única** (só entra com o seu ok): *"Só vai para os seguidores o que provou com quem não segue: Trial com ≥ 150 contas em 72 h, ou a vencedora do par. Durante o teste da §6, cada vídeo tem uma versão normal."* Assim, "não alimentar a bolha" vira um critério com número, e não mais uma proibição que a graduação automática e a regra do par já contradizem.

## 5. Os 3 Trials já publicados: o que fazer com cada um

O que faz cada caminho:
- **(b) "Compartilhar com todos"** (o nome do botão pode variar na versão do app): é o **mesmo post**. Ele vai para a grade e para o feed dos seguidores e mantém comentários, curtidas e o link. Os números devem continuar somando (hipótese, ver §2).
  - **Só dá para fazer no app.** A API não tem endpoint para graduar um Trial: a graduação é escolhida só na hora de publicar, com `MANUAL` ou `SS_PERFORMANCE` ([Ayrshare](https://www.ayrshare.com/docs/apis/post/social-networks/instagram.md), [Postiz](https://docs.postiz.com/public-api/providers/instagram.md); fontes de terceiros, sem a página da Meta confirmada).
  - A API **confere** depois: o `metricas.py` lê `is_shared_to_feed`.
- **(c) Repostar como Reel normal:** é um post novo, que começa do zero.
  - Pela API dá para fazer: o `publicar.py` com `trial: null`.
  - Quem apaga o antigo é você, no app (a API do Instagram não apaga).
  - Riscos: o sinal de cópia (o Hinton repostado ficou em 11) e os 168 s, acima da regra de 90 s. Para fazer direito, seria preciso um **recorte novo de ≤ 90 s, com gancho novo**, o que é trabalho de edição.

| Reel | Recomendação | Por quê |
|---|---|---|
| **Hinton** ([Degw3KFDvcO](https://www.instagram.com/reel/Degw3KFDvcO/)) | **(a) deixar como está** | 11 contas em 7 dias, e o próprio Instagram não graduou (estava em automático). Tem 158,7 s (acima de 90) e é um repost. Compartilhar levaria aos seguidores um vídeo que já foi reprovado por quem não segue. Repostar repete o erro que deu 11. |
| **Fei-Fei B** ([DepSlbLADfM](https://www.instagram.com/reel/DepSlbLADfM/)) | **(b) "Compartilhar com todos" no sábado 24/10**, depois da leitura das 09:30, se a A continuar abaixo da B | É a vencedora provável do par, e a §2.8 já manda compartilhar a vencedora. As 72 h do teste passaram (40 contas), então compartilhar não tira nada do teste. A grade ganha um 2.º vídeo da linha nova (hoje: Hassabis + 4 de abril). E vira um experimento grátis: alcance antes = 40, depois = ? aos 3 dias. Contra: 168 s, 5,4 % assistido e 45 views à mostra. É um ganho modesto, mas o risco é baixo, porque a parte da Guiné-Bissau da base quase não abre (§3). |
| **Fei-Fei A** ([Deuqi5pDmyf](https://www.instagram.com/reel/Deuqi5pDmyf/)) | **(a) deixar como está** | 4 contas. Compartilhar poria o **mesmo** vídeo duas vezes na grade. É a perdedora do par. |

**(c) Recorte ≤ 90 s da Fei-Fei como Reel normal:** **agora não.**
- Fica como opção para depois do teste da §6, se o normal ganhar. A história é boa e só ~44 pessoas a viram no IG.
- Entra em conflito com "não repostar" (17/10). Precisa do seu ok e de horas do editor.

## 6. Próximos vídeos: teste de 2 semanas (misto, com critério numérico)
**Ideia:** cada vídeo já sai em pares quase idênticos (A/B). Basta publicar **uma versão como normal e outra como Trial** para ter, no mesmo conteúdo, a resposta "o modo muda o alcance a não seguidores?". A duração deixa de confundir, porque tudo agora tem ≤ 90 s.

| Quando | Publicação | Modo proposto | Hoje está |
|---|---|---|---|
| dom 25/10 19:00 | livro-chatgpt **B** (34,5 s), IG + FB | **NORMAL** (`instagram.trial: null`) | Trial MANUAL |
| ter 27/10 21:00 | livro **A**, só IG | Trial MANUAL | igual |
| qua 28/10 21:00 | livro **L01C**, só IG | Trial MANUAL | igual |
| dom 01/11 19:00 | livro **L01C-A**, só IG | Trial MANUAL | igual |
| quando ficar pronto | Jensen (~88 s) | **ordem invertida**: a versão Trial sai primeiro e a normal ≥ 48 h depois | — |

A ordem invertida no Jensen controla o viés de "quem sai primeiro leva vantagem" (cópia). Com isso, o teste de abertura (B × A) e o de gancho (L01 × L01C) continuam:
- **entre os Trials:** A × L01C-A mede o gancho; L01C × L01C-A mede a abertura;
- **entre os modos:** pulados % e tempo médio, lembrando que os públicos diferem.

**O que medir aos 5 dias** (prints do Insights do Reel, porque a API não separa não seguidores por post): contas alcançadas × % de não seguidores = **contas não seguidoras**. Mais pulados %, tempo médio, salvamentos, envios e comentários com a palavra LIVRO.

**Regra de decisão (≈ 06/11, livro completo; o Jensen confirma):**
- **Normal vira o padrão da versão principal** se, no livro, a versão normal tiver **≥ 2× as contas não seguidoras do melhor Trial e ≥ 150 não seguidores** (o Hassabis fez ~208). As variantes continuam como Trial MANUAL e nunca vão para a grade.
- **O Trial volta a ser o padrão** (SS_PERFORMANCE na versão principal) se **o melhor Trial alcançar ≥ as contas não seguidoras da normal**.
- **Entre os dois:** misto por mais 2 vídeos (Jensen + o próximo).
- **Guarda da bolha** (para a versão normal): se a Guiné-Bissau passar de **15 %** das contas alcançadas (Hassabis: 5,7 %) ou os seguidores passarem de **50 %** do alcance (Hassabis: 37,8 %), volta a ser Trial.
- **Compartilhar um Trial:** só com **≥ 150 contas em 72 h** e pulados **≤ 50 %** (Hassabis: 49,4 %).
- **Aviso:** se os 3 Trials do livro caírem para < 20 contas, isso pode ser o efeito cópia (§2) e não o modo. Nesse caso, o Jensen (Trial primeiro) é o desempate.

## 7. Quem faz o quê
| Ação | Quem | Onde / como |
|---|---|---|
| Decidir: (1) compartilhar a Fei-Fei B; (2) livro B como normal; (3) a regra única da §4 | **Carlos** | responde na conversa |
| Compartilhar a Fei-Fei B com todos (sáb 24/10, se a A continuar abaixo) | **Carlos, no app** | Perfil → aba Reels (os de teste só você vê) → Reel da Fei-Fei (abre com a Fei-Fei em tela cheia) → painel do teste / "Ver insights" → **"Compartilhar com todos"**. Se não achar, mande print da tela |
| Conferir se foi compartilhado e medir o "depois" | **pipeline (API)** | `metricas.py` (09:30): `is_shared_to_feed` = `true` e alcance > 40 |
| Trocar a livro B para normal (`06-publicar/2026-10-23-livro-chatgpt/post.json` → `instagram.trial: null`) antes de dom 25/10 19:00 | **sessão principal**, só com o seu ok | `publicar.py` publica normal quando `trial` é `null`; o FB já sai normal |
| Registrar a decisão | **sessão principal** | `docs/decisoes.md` (linha nova), `estrategia-de-alcance.md` §2.7–2.8, `testes-abertura.md` (coluna "modo") e `calendario.md`. Este relatório não mexe em nenhum deles |
| Apagar ou repostar | ninguém, por agora | — |

## 8. Prints que faltam (do app; a API não dá)
1. **Painel do teste da Fei-Fei B e da A**: contas alcançadas, % de não seguidores, pulados %, retenção aos 3 s e a comparação "com seus testes anteriores".
2. **Hassabis hoje**: contas alcançadas e % de não seguidores (o 62,2 % é de 17/10).
3. **A tela em que aparece o botão de compartilhar o teste**, para escrever o caminho exato no `publicador`.
4. Os Reels de **maio**: foram publicados como teste ou com "compartilhar no feed" desligado? (Isso explica o 0–98 deles.)
5. Depois de compartilhar a Fei-Fei B: o Insights dela aos 3 dias (seguidores × não seguidores, país).

## Fontes
- Instagram for Creators: [Trial reels: try content with non-followers first](https://creators.instagram.com/blog/instagram-trial-reels) (oficial).
- Instagram for Creators: [FAQ](https://creators.instagram.com/faq?locale=en_US) (oficial; citado na auditoria de 16/10).
- [Kapwing: Instagram Trial Reels study](https://kapwing.com/resources/instagram-trial-reels-study-what-we-learned-after-a-trial-reel-hit-1-million-views) (terceiros).
- [Tubefilter: creators gaining followers with Trial Reels](https://www.tubefilter.com/2025/01/23/instagram-trial-reels-growth-hacking-creator-economy/) (terceiros).
- [TechCrunch via AOL: Instagram ranking original content](https://www.aol.com/news/instagram-improve-ranking-system-better-191319059.html) (Mosseri, 2022).
- [Ayrshare: Instagram trial params](https://www.ayrshare.com/docs/apis/post/social-networks/instagram.md) e [Postiz](https://docs.postiz.com/public-api/providers/instagram.md): graduação não exposta na API (terceiros).
