VEREDICTO: APROVADO COM AJUSTES

# Revisão do roteiro — Jensen Huang (v1, 17/10/2026) — revisor-de-roteiro, 1.ª rodada

> Pode gravar amanhã. Os ajustes pequenos (fonte, pausa, metadado de abertura) já estão aplicados no `roteiro.md` e o
> `parse_roteiro.py` roda sem erros nem avisos (19 linhas, 182 palavras). Nenhuma palavra da FALA foi trocada.
> Fatos conferidos de novo na web (AFP, AP, QEPrize, Royal Academy of Engineering, UKTech, Nvidia, Wikipedia, Fortune) e
> nas **legendas automáticas do discurso da CMU** (baixadas hoje com yt-dlp): 2:32 a 5:45 bate com o roteiro.

## 1. Critério eliminatório (roteiro narrativo)
**Passa.** Tem o arco inteiro (gancho L01–L03 → história L04–L09 → desafio L10 → virada L11–L12 → clímax L13–L14 → reflexão
L15–L16 → CTA L17–L19), frases completas com sujeito e verbo, só 2 números (5 trilhões, 1993), emoção antes de dado e a
frase-lição antes do CTA. Não é telegráfico. O ponto mais fraco é o **desafio + virada (L10–L12)**: "quase quebrou" vem sem
causa e a ponte "quase quebrou → IA" é um salto (ver §6, sugestão opcional).

## 2. Os 7 pontos pedidos
| # | Ponto | Resultado |
|---|---|---|
| 1 | "a primeira empresa de 5 trilhões" | **OK.** AP (via Yahoo Finance): "Nvidia on Wednesday became the first public company to reach a market capitalization of $5 trillion", quarta 29/10/2025. Dawn: "became the world's first $5 trillion company". **Erro de fonte achado:** o texto do Dawn é da **AFP**, não da Reuters (a Reuters só assina a foto). Corrigido na seção Fontes e na legenda do post ("AFP e AP"). A fala não cita valor de hoje nem ranking (§9 do dossiê respeitado). |
| 2 | "Se o ChatGPT é o carro, a Nvidia faz o motor" | **OK.** Metáfora do próprio dossiê (§1/§4); a Royal Academy of Engineering premiou Huang e Dally pelas GPUs que sustentam o aprendizado de máquina. Não diz que o ChatGPT roda só em Nvidia nem fala de cliente (§9). Se improvisar: nada de "a OpenAI compra da Nvidia", valor de mercado ou China. |
| 3 | "Aqui em Londres… Rei Charles… mesmo prêmio do Hinton e da Fei-Fei Li" | **OK.** QEPrize 2025 (aprendizado de máquina moderno): sete laureados — Bengio, Dally, Hinton, Hopfield, **Huang**, LeCun, **Fei-Fei Li**; entregue por Charles III no **St James's Palace, em 5/11/2025** (QEPrize + UKTech). "Aqui" é verdadeiro. A fala não conta laureados nem data. **Dependência:** "de quem eu já falei aqui" só é verdade se este vídeo sair **depois** da Fei-Fei (agendada 18/10 19:00; Hinton já saiu em 16/10). |
| 4 | "comenta PRATO" na L05 (seção `virada`) | **OK, verificado no código.** `gerar_props.derivar_cta` pega a 1.ª linha de seção `cta` que contém a palavra: L17 não tem, L18 tem → o cartão grande cai na L18. A L05 é `corpo` e não gera cartão. Parser: 0 erros, 0 avisos. |
| 5 | `pose_capa` com prato | **OK.** Diferente das duas anteriores (braços cruzados / mão no ouvido), combina com o título e com a palavra. Cuidados: prato **à altura do ombro, ao lado do rosto, sem cobrir nada** e dentro do recorte 3:4 (1080×1440); apoiar o cotovelo ou a outra mão para não tremer nos 3 s; o branco é o ponto mais claro do quadro, então conferir a exposição do rosto no primeiro take. |
| 6 | Ritmo / ≤ 90 s | **No teto, risco médio.** Ver §5. |
| 7 | Promessa do CTA × material | **Bate.** A fala diz "o discurso dele" e "ver ele contando"; **não promete legenda em português** (confirmado nas 19 linhas). O discurso da CMU (18 min 22 s, canal oficial) conta de 2:32 a 5:45 o internato em Oneida/Kentucky, o Denny's ("major career advancement"), a fundação com Malachowsky e Priem, "primeiro chip nem funcionou", "quase ficamos sem dinheiro" e o pedido à Sega. **Não conta** a mesa do Denny's de San Jose nem os banheiros: o PDF não deve prometer isso (ver §7). |

## 3. Hooks (rubrica de `hooks.md`)
| Hook | Fala (palavras) | Tela (palavras) | Clar. 20% | Lacuna 20% | Autorrel. 20% | Espec. 15% | Visual 15% | Envio 10% | **Nota** |
|---|---|---|---|---|---|---|---|---|---|
| **A** (escolhido) | L01 = 6 (com L02 = 18) | "DO PRATO SUJO AOS 5 TRILHÕES" = 6 | 9 | 7 | 8 | 8 | 7 | 7 | **7,8** |
| B | 10 | "LIMPAVA BANHEIRO AINDA CRIANÇA" = 4 | 6 | 8 | 8 | 7 | 7 | 6 | 7,1 |
| C | 9 | "O MELHOR LAVADOR DE PRATOS" = 5 | 8 | 7 | 6 | 7 | 7 | 7 | 7,0 |

O de maior nota é o escolhido; nenhum abaixo de 6. A é emoção em frase completa e termina dizendo de quem é a história (L03).
B puxa mais emoção (criança longe de casa, que pega o público imigrante), mas repete o que L06–L07 contam; C é a frase
dele em Stanford, mas "o melhor lavador" soa a brincadeira antes de soar a história. Nota do visual: como estava escrito
("Carlos em tela cheia") valia 5–6; com a abertura corrigida (§4) vale 7.

## 4. Estratégia de alcance (`estrategia-de-alcance.md` §2)
| Regra | Situação | Tempo estimado |
|---|---|---|
| 1. Promessa completa + 1.ª virada em ~20 s | **OK, no limite.** Promessa inteira (lavar prato → 5 trilhões) em L01–L02; a virada "ela nasceu numa mesa de lanchonete" é a L04. Ficha técnica (Taiwan) só na L06, depois dos 20 s. | promessa ~9 s · L04 de ~15 a ~21 s (a ênfase lenta empurra ~1,5 s) |
| 2. Palavra-chave 2× | **OK.** L05 (antes de 30 % do vídeo) e L18 (cartão grande, Carlos em tela cheia). | PRATO #1 ~24 s · #2 ~85 s |
| 3. Pedido de salvar com motivo concreto | **OK.** L17 "Salva pra rever quando achar que começou pequeno demais." | ~80 s |
| 4. ≤ 90 s | **No teto** (§5). | |
| 5. Londres / Europa | **OK.** "Aqui em Londres" (L13) e "recomeçando aqui na Europa" (L19), natural. | |
| 8. Abertura com o CONTEÚDO | **A fala funciona** como narração por cima de imagem: L01–L02 se entendem sem ver o rosto e o nome entra na L03. **O metadado estava errado:** hooks A/B/C e a nota de Cenas extras diziam "Carlos em tela cheia" nas L01–L02, que é o controle, não o teste. Corrigido (§6). Variante do rodízio: Fei-Fei = C5, então este = **C10**; o Carlos entra por volta dos 10 s, exatamente na L03 ("Pois é. Essa é a história…"). | |

Material de abertura que já existe em `material/youtube/`: o vídeo do Denny's de San Jose (`KpD_XKxJwcU`) e a notícia dos 5
trilhões (`XxKcKQlVTjY`). Quem escolhe é o produtor-de-extras/editor.

## 5. Duração
- 182 palavras, dentro de `palavras_alvo` (185 ±10 %) e do teto de `voz-carlos.md` §10 (185, nunca mais de 190).
- **Estimativa calibrada: ~88 s** (182 ÷ 2,06 p/s, o ritmo do Hinton medido no corte final, que já inclui pausas).
  O parser dá 92,8 s porque soma 0,2 s por linha e 0,6–0,9 s por pausa em cima de 2,1 p/s: é pessimista.
- **Risco real:** se ele ler como na Fei-Fei (1,97 p/s com improviso), dá ~92 s. Para ≤ 90 s ele precisa de ≥ 2,02 p/s no corte.
- **Gordura:** de conteúdo, quase nenhuma (cada linha faz um trabalho). De ar, havia 7 marcas de pausa (1 a cada 26 palavras;
  o Hinton tem 1 a cada 41). **Tirei o `[pausa]` da L12 e da L14**, que ele faz sozinho (0,5–1,0 s); sobram 5 (≈ −1 a −2 s).
- **Plano de contingência se o 1.º corte passar de 90 s**, nesta ordem: (1) o editor comprime pausas > 0,6 s e escolhe o
  take mais curto de cada linha (−2 a −3 s); (2) derrubar a L11 inteira no corte (−3 s; o salto fica seco, mas se entende);
  (3) pedir ao Carlos um take de L04 só com "E olha só:" (−3 palavras, −2,5 s, porque essa frase ele fala a ~1,3 p/s).
  Não apliquei o (3) no roteiro porque "olha só que interessante" é expressão dele (`voz-carlos.md` §3).
- Dica para a gravação: as 3 frases de ênfase (L04, L10, L15) podem ser lentas; o resto do corpo (L06–L14) em ritmo de conversa.

## 6. Ajustes aplicados no `roteiro.md` (antes → depois)
| # | Onde | Antes | Depois |
|---|---|---|---|
| 1 | frontmatter `hooks.A/B/C.visual` | "Carlos em tela cheia; o Jensen Huang só aparece na L03" | A: "abertura com o CONTEÚDO em tela cheia (extra `full`: vídeo do Denny's e dos 5 trilhões), voz do Carlos por cima; o Carlos entra na L03 (~10 s, variante C10)". B e C: a mesma ideia, com "extra `full` do assunto" / "vídeo do Denny's" |
| 2 | Cenas extras (nota) | "L01–L02 (gancho) com ele em tela cheia." | "Abertura (§2.8, 17/10): L01–L02 cobertos por um extra em `full`… sem o rosto dele; variante C10 (o Carlos entra na L03); o editor anota em `_controle/testes-abertura.md`." |
| 3 | L12 (FALA) | `…a Nvidia faz o **motor**. [pausa]` | `…a Nvidia faz o **motor**.` |
| 4 | L14 (FALA) | `…de quem eu já falei aqui. [pausa]` | `…de quem eu já falei aqui.` |
| 5 | Fontes L02 | "Dawn, citando Reuters" | "Dawn, texto da AFP" |
| 6 | Legenda do post, linha "Fontes:" | "Reuters e AP (29/10/2025)" | "AFP e AP (29/10/2025)" |
| 7 | Fontes L06–L07 | (sem origem para "a família achava que era escola boa") | Nota: a ideia vem da Wikipedia (tios o matricularam por engano numa "prestigious boarding school") e da Bloomberg Billionaires (citando a Wired, 2002), **não** das páginas da Fortune citadas; a fala diz "a família" e não atribui a ele. Também: nascimento em Taiwan = Wikipedia (Taipei); a fala diz só "Taiwan" |
| 8 | Fontes L13–L14 | "em novembro de 2025" | "em 5 de novembro de 2025" |
| 9 | Topo do roteiro | — | Linha de revisão apontando para este arquivo |

## 7. Pendências e decisões
1. **PDF PRATO ainda não existe** (`material/` só tem dossiê, fontes e vídeos). Não bloqueia gravar; **bloqueia publicar**
   (`cta.md`: sem PDF final, troca o CTA). Pedir ao `produtor-de-material`: link `https://www.youtube.com/watch?v=FZh_0uRgrg4&t=152s`
   (2:32); "legenda em inglês, tradução automática para português pelo YouTube" (nunca "com legenda em português"); dizer o que o
   trecho de 2:32 a 5:45 cobre (**sem** a mesa do Denny's de San Jose e **sem** os banheiros, que vêm do blog da Nvidia e da
   Fortune); bônus: Stanford GSB (`lXLBTBBil2U`, 56 min), para o caso de ele dizer "entrevista" na L18; cadastrar **PRATO** na automação
   (`automacao-meta`). PRATO não repete NOBEL (16/10) nem AULA (18/10).
2. **Ordem de publicação:** só depois da Fei-Fei (domingo 18/10 19:00), por causa da L14 ("de quem eu já falei aqui").
3. **Variante C10 da abertura** foi assumida pelo rodízio; o Carlos/editor confirmam. Se preferirem repetir o controle, voltar o metadado.
4. **Dossiê com o mesmo erro da AFP/Reuters** (`material/dossie.md` §0 e a cópia em `01-ideias/pesquisas/perfis/jensen-huang`): não editei,
   é arquivo do pesquisador. Também: o dossiê marca como "confirmado" a crença da família sobre a escola com base na Fortune, que não a traz (§6.7).
5. **Pronúncia:** o roteiro não lista "Charles" (inglês "Chárls") nem "Hinton"; a legenda segue o roteiro, então se ele disser "Carlos" não quebra nada, só avisar.
6. Cena de abertura (L01–L02) e fotos: **nenhuma imagem de pessoa gerada por IA** (regra rígida 3); só vídeo/foto licenciada ou trecho com crédito.

## 8. Sugestões NÃO aplicadas (a decisão é do Carlos ou do roteirista; todas custam palavras)
- **Mais carne no desafio** (L10): "Só que o primeiro chip não funcionou, / e a empresa quase quebrou." (+6 palavras, ≈ +3 s;
  vem da CMU 5:00 e é a causa real). Só cabe se cair outra coisa (ex.: a L11 inteira, mas aí o salto para a IA fica seco). Ele pode
  fazer isso sozinho no improviso, que costuma acertar ("Só que aí que tá o problema").
- **Idade concreta** (L06): "ainda criança" → "aos 9 anos" (a CMU confirma 9; +1 palavra, a linha vai a 14). Mais emoção, um número a mais.
- **Lição mais clara** (L16): "o seu Denny's pode ser onde você está agora" → "o seu Denny's pode ser o lugar onde você está agora"
  (+2 palavras). O call-back com o Denny's é bom; o risco é um iniciante não decodificar "o seu Denny's". Sem promessa de renda, dentro de `regras-legais.md` §5.
- "anos depois" aparece na L02 e na L11. Ele varia sozinho; se quiser, L02 pode virar "e, décadas depois," (verdadeiro: 1978 → 2025).
- Clímax em pergunta-resposta (`voz-carlos.md` §10.5), p.ex. "E onde ele recebeu o prêmio? Aqui em Londres…". Não cabe nos 90 s sem cortar outra coisa.

## 9. Voz e "soa a IA?"
- **Soa como ele.** Usa os conectores dele ("Pois é.", "E olha só que interessante:", "Só que", "Depois,"), frases com sujeito, sem
  subjuntivo encadeado, sem "é que", "pra"/"tá", números em algarismo, sem lista de 3 itens, sem linha de uma palavra, CTA no formato
  exato que ele diz ("Comenta a palavra PRATO que eu vou te enviar…"). Pontos que ele deve reescrever sozinho e não é problema: L05
  "Se quiser" (vira "Se você quiser"), L17 "quando achar" (vira "quando você achar"), L06 com 13 palavras (1 acima do ideal; ele respira em "Taiwan /").
- **Teste de IA:** 0–1 sinal (só o "A história dele mostra uma coisa:", que é do modelo dele). Tamanhos de frase variam (6 a 13), há
  exemplo concreto em tudo, sem par simétrico "não é X, é Y". Passa.
- **Banidas:** nenhuma. "tu/teu": nenhum. Abertura proibida: nenhuma ("Imagina você…" é o modelo dele).
- **Legal:** nada de valor de hoje, patrimônio, "mesmo Denny's", "30 dias", Sega, China. L16 é opinião com "pode ser", sem promessa.
- **Público:** um iniciante entende sem pesquisar (Denny's é explicado por "lanchonete"; Nvidia vira "o motor"; Hinton e Fei-Fei têm a ponte "de quem eu já falei").
  O dono de negócio e quem recomeça na Europa se veem na L16–L19.

## 10. Formato
FALA literal e sem indicações; `[pausa]` só no fim das linhas (5 restantes); IDs L01–L19, L01B, L01C; L05 em `virada` de propósito
(cartão do CTA só na L18); `pose_capa` presente; `cta_palavra` PRATO, `material` e `material_titulo` preenchidos; 5 hashtags; palavra
"PRATO" na legenda do Instagram; `parse_roteiro.py` sem erros nem avisos.
