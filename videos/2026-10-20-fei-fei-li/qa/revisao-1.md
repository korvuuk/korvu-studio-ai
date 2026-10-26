RESULTADO: FAIL

# Revisão 1 (corte + legendas) — 2026-10-20-fei-fei-li

Revisado em 2026-10-17 · `edicao/corte.mp4` (168,44 s, EDL aprovada em 17/10, `edl.json` versao 14) · `edicao/legendas.json` + `legendas.srt` · `roteiro.json` v4.

**Veredicto em duas partes**
- **Corte (vídeo + áudio): PASS.** Nada a refazer no `corte.mp4`; as 34 linhas estão presentes com o conteúdo, sem voz da IA, sem palavra cortada, sem clique/emenda audível.
- **Legendas: FAIL.** 12 linhas mostram na tela palavras que ele NÃO disse (ou deixam sem legenda palavras que ele disse), e a L14 está **fora de sincronia em ~2 s** (a legenda "exatamente" aparece 1,95 s antes da fala). Basta corrigir `palavras_saida` (texto + tempos) e regerar `legendas.json/srt`/`reel-props.json`; **não precisa re-renderizar o corte** nem mudar a EDL.

Critério usado (decisões 16–17/09 + 17/10): a legenda segue o roteiro, salvo improviso de verdade, e aí segue a fala. Exijo troca quando a legenda difere da fala em **palavra de conteúdo, ordem ou quantidade de palavras** (o espectador ouve uma coisa e lê outra, ou fica trecho falado sem legenda). **Não** exijo troca em diferença só de flexão/concordância/contração (usa/usaram, neural/neurais, eram/era, estava/tava, "ano" comido pelo "anos") — aí vale a grafia do roteiro (dicionário de fala dele).

## Como foi conferido
- Transcrição do corte: `qa/transcricao-corte.json` (Scribe) **mais uma 2.ª transcrição independente** do `edicao/corte-audio.wav` (mlx-whisper large-v3-turbo, palavra a palavra). As duas coincidem em tudo o que está abaixo (só divergem em "tava/estava", "era/eram", "Fei-Fei", "cinquenta/50", "ImageNet").
- Diff legenda × fala palavra a palavra (difflib sobre os 336 tokens de `legendas.json` × 363 do ASR) + lista de buracos de legenda com fala por dentro.
- Medição de energia/espectro no áudio nos pontos duvidosos (início de palavra, emendas, fala da IA).
- Stills do Reel (composição `Reel`, props do `reel-props.json` sem extras, vídeo = proxy 8-bit com LUT de visualização) em 0,6 · 4,6 · 40,9 · 66,8 · 72,0 · 98,7 · 105,5 · 128,2 · 133,9 · 142,4 · 157,0 s — olhados um a um.
- `edicao/frames/contato.png` (72 cortes) olhado inteiro.

## Tabela de checagens

| # | Checagem | Resultado |
|---|---|---|
| 1 | `qa/diff.md`: 34 linhas "presente", 0 faltando, 0 duplicada | OK (nenhuma frase repetida no corte; ambas as ASR mostram só o roteiro/improviso dele) |
| 2 | WER ≤ 8 % | 27 % — **aceito**: é improviso (decisão 17/10 §2), não defeito do corte |
| 3 | Duração: vídeo 168,40 s · áudio 168,44 s · peças 168,44 s (Δ 40 ms = 1 quadro); 25 fps; 1080×1920 yuv422p10le | OK |
| 4 | "Voz da IA 2,78 s" do verify | **Falso positivo confirmado** (ver abaixo) |
| 5 | Palavra cortada / emenda no meio de palavra | OK — 72 bordas de peça testadas: nenhuma palavra do ASR atravessa uma borda, exceto a emenda deliberada L26→`manual` em 128,40 s ("artificial" 128,04–128,58): áudio contínuo (sem clique, nível −46/−47 dBFS dos dois lados) e imagem contínua (Δ quadro 3,3 vs 2–4 normal) |
| 6 | Entrada de cada segmento limpa (sem sílaba pela metade) | OK — nenhum início/fim de segmento com nível alto |
| 7 | Pausas | OK — maior pausa entre palavras 0,92 s (153,10→154,02, antes do CTA); nenhuma pausa morta |
| 8 | Corte aprovado × roteiro (conteúdo) | OK — ver "Conteúdo" abaixo |
| 9 | Grafia: Fei-Fei Li, ImageNet, Geoffrey Hinton, Princeton, Universidade de Toronto | OK, **exceto L32** ("Fei Fei Li" sem hífen, partido em duas páginas) |
| 10 | Números em algarismo: 2007, 2012, 50 mil, 18 | OK (mas L15 mostra "quase 50 mil", ver C6) |
| 11 | Sem pontuação/caractere especial | OK (só o hífen de Fei-Fei) |
| 12 | Páginas de 2–4 palavras | OK no geral; 3 páginas de 1 palavra: "Ela" (L07, correto — resposta dramática), "E" (L10) e "IA" (L28), as duas últimas são sintoma de palavra faltando (C3, C9) |
| 13 | `destaque` nas palavras do roteiro | **2 faltando**: "fiscais" (L06) e "significa" (L29) (C13) |
| 14 | Sincronia ±1 quadro | OK em 296 de 298 palavras casadas (mediana 0 ms); **L14 fora**: "computador" −340 ms e "exatamente" −1950 ms (C5). Os outros 9 desvios (−60 a −140 ms: sem, e, as, ela, ideia, Segundo, 2012, Geoffrey, história) são jitter do ASR (conferi no áudio: "Geoffrey" 101,48 s e "2012" 88,2 s estão certos na legenda) |
| 15 | Safe zones / legibilidade / estilo (stills) | OK — ver "Stills" abaixo |
| 16 | Cartão do CTA "AULA" 154,02–160,78 s | OK (entra em "Comenta" 154,02; sai quando começa a L33 em 160,78; legendas do trecho somem, sem duplicar) |
| 17 | Extras | **Não avaliado nesta passagem** (camada de extras montada à parte, em tela cheia) |

## CORREÇÕES OBRIGATÓRIAS (legendas) — linha, tempo, antes → depois

Os tempos novos são os do ASR do corte (`qa/transcricao-corte.json`, `inicio`/`fim` em s de saída). Sem pontuação. Onde a palavra "depois" não existia na legenda, use o `inicio`/`fim` do ASR dela.

**C1 · L08 (28,98–33,28 s)** — a legenda encurta o que ele disse e troca o verbo.
- Antes: `E foi assim ela conta que ajudou a pagar a faculdade` (buraco de legenda de 0,7 s em 31,34–32,04 com ele falando)
- Depois: `E foi assim ela contou que foi assim que ela ajudou a pagar as faculdades`
- Tempos: E 28,98 · foi 29,16 · assim 29,38 · ela 30,00 · contou 30,30 · que 31,24 · foi 31,40 · assim 31,54 · que 31,86 · ela 31,92 · ajudou 32,04 · a 32,38 · pagar 32,48 · as 32,70 · faculdades 32,82–33,28 (destaque na palavra "faculdades", era "faculdade").
- Alternativa (decisão do Carlos/editor, exige novo render do corte + nova aprovação): cortar "foi assim que ela" (31,40–32,02 s de saída), que é repetição do "foi assim" de segundos antes; aí a legenda do roteiro já serve (só trocar "conta" por "contou"). Recomendo a opção da legenda, porque a EDL está aprovada.

**C2 · L09 (36,58–37,68 s)**
- Antes: `... Princeton e depois entrou para o mundo ...` ("depois" fica 1,06 s na tela, 36,62–37,68, enquanto ele diz outra coisa)
- Depois: `... Princeton e foi aí que ela entrou para o mundo ...`
- Tempos: e 36,58 · foi 36,74 · aí 36,96 · que 37,38 · ela 37,50 · entrou 37,68 (o resto da linha não muda).

**C3 · L10 (40,62–45,34 s)**
- Antes: `E` (página sozinha, 40,62–41,02) · 1,0 s sem nada · `ela começou a pensar numa coisa muito simples`
- Depois: `E a partir daí ela começou a pensar em uma coisa muito simples`
- Tempos: E 40,62 · a 40,72 · partir 40,82 · daí 41,12 · ela 41,74 · começou 42,08 · a 42,92 · pensar 43,04 · em 43,42 · uma 43,56 · coisa 43,80 · muito 44,20 · simples 44,82–45,30 (destaque em "simples").

**C4 · L12 (52,48–56,08 s)**
- Antes: `Então por que um computador seria diferente`
- Depois: `Então por que que um computador deveria ser diferente`
- Tempos: Então 52,48 · por 53,34 · que 53,56 · que 53,88 · um 54,00 · computador 54,14 (destaque) · deveria 55,00 · ser 55,40 · diferente 55,54–56,08.

**C5 · L14 (61,10–69,92 s) — o pior: 3 s de palavra errada na tela e "exatamente" 1,95 s adiantado**
- Antes: `... imagens e dizer ao computador exatamente o que aparecia em cada uma delas` (confirmado no still de 66,8 s: a tela mostra "aparecia" enquanto ele diz "reconhecer")
- Depois: `... imagens e passar para o computador reconhecer exatamente cada uma delas`
- Tempos: e 65,16 · passar 65,30 · para 65,60 · o 65,72 · computador 65,80 · reconhecer 66,64 · exatamente 67,54–68,36 · cada 68,62 · uma 69,18 · delas 69,48–69,92. (As palavras de 61,10 a 64,62 estão certas.)

**C6 · L15 (70,28–78,78 s) — duas coisas**
- (a) **"quase" não foi dito** (ele diz "cinquenta mil"; o "mais de" foi cortado e a emenda em 71,28 s está limpa). Antes: `Segundo ela quase 50 mil pessoas...` → Depois: `Segundo ela 50 mil pessoas...` ("50" em 71,28 — hoje entra às 71,51, 0,23 s atrasado — mil 71,86 · pessoas 72,08; destaque em "50 mil pessoas" mantido).
- (b) **ordem das palavras trocada e 2 palavras sem legenda.** Antes: `... pessoas ajudaram pela internet a organizar e identificar essas imagens` ("ajudaram" 72,63 mas ele diz 73,64; buraco 73,39–74,63 e 76,73–77,87 com fala por dentro). Depois: `... pessoas pela internet ajudaram a organizar e identificar cada uma dessas imagens`.
- Tempos: pela 72,72 · internet 72,92 · ajudaram 73,64 · a 74,64 · organizar 74,88 · e 75,84 · identificar 75,94 · cada 77,08 · uma 77,62 · dessas 77,88 · imagens 78,20–78,78.

**C7 · L21 (101,47–105,82 s)** — falta "no meu canal" (falado, 0,56 s, sem legenda; o verify o listou como "fala extra")
- Antes: `... de quem eu já falei aqui` (a legenda some em 104,89; a tela fica vazia até 106,41)
- Depois: `... de quem eu já falei aqui no meu canal`
- Tempos: no 105,26 · meu 105,36 · canal 105,54–105,82.

**C8 · L22 (108,74–111,70 s)** — verbo diferente do que ele disse
- Antes: `... superior aos concorrentes que aquele momento ajudou a mudar o rumo ...`
- Depois: `... superior ao concorrente e naquele momento começou a mudar o rumo ...`
- Tempos: ao 108,74 · concorrente 108,92 · e 109,76 · naquele 109,86 · momento 110,34 · começou 111,08–111,70 · a 112,08 (o resto não muda; destaque em "inteligência artificial" mantido).

**C9 · L28 (133,16–136,36 s)** — a legenda mostra "IA" 0,4 s e depois fica 1,48 s vazia enquanto ele diz "a inteligência artificial"
- Antes: `IA` · (vazio 133,56–134,72) · `não aprende por mágica`
- Depois: `A inteligência artificial não aprende por mágica`
- Tempos: A 133,18 · inteligência 133,28 · artificial 133,80–134,46 · não 134,72 · aprende 134,90 · por 135,68 · mágica 135,92 (destaque só em "mágica", como está).

**C10 · L32 (160,04–160,63 s)** — grafia do nome
- Antes: `... sobre a Fei Fei Li` (dois tokens "Fei" "Fei", e a quebra de página cai no meio: "…sobre a Fei" / "Fei Li")
- Depois: um token só, `Fei-Fei`, com 160,04–160,38, seguido de `Li` 160,42–160,63. (Na prática as legendas dessa janela ficam atrás do cartão AULA, mas o `legendas.srt` e o `.json` levam o erro; se o cartão sair um dia, aparece.)

**C11 · L33 (160,78–163,94 s)** — falta "somente"
- Antes: `São 18 minutos com legenda em português`
- Depois: `São somente 18 minutos com a legenda em português`
- Tempos: São 160,78 · somente 160,96 · 18 161,42 (hoje 161,32; o "dezoito" dele começa em 161,42) · minutos 161,88 · com 162,42 · a 162,50 · legenda 162,58 · em 163,28 · português 163,44–163,94 (destaque mantido).

**C12 · L23 (115,71–117,55 s)** — falta "só" (palavra de conteúdo, 0,14 s)
- Antes: `Mas olha que interessante` → Depois: `Mas olha só que interessante` (só 116,20–116,34; que 116,60 · interessante 116,74).

**C13 · destaque faltando**
- L06: "fiscais" (27,40–27,90) deve ter `destaque: true` (o roteiro marca "fiscal"; o casamento falhou pelo plural).
- L29: "significa" (143,34–143,94) deve ter `destaque: true` (o roteiro marca "significa"; a palavra está na legenda mas sem destaque).

## Correções opcionais (baixa prioridade — pode ficar como está)
- L06: "telefone" (23,52) → "telefones". As duas ASR do corte ouvem "telefones" (a do bruto ouviu "telefone"); com "os" antes, a legenda no singular parece erro de digitação. O /s/ final dele é fraco, então é decisão sua.
- L04: "aos Estados Unidos" (13,72) → "nos Estados Unidos" e há um "e" falado (14,82–14,92) sem legenda ("...Unidos e ainda adolescente"). Além disso a página quebra "Estados | Unidos" (14,22/14,26).
- L26: "chama Fei-Fei Li de madrinha" → "chama a Fei-Fei Li da madrinha" (a 125,36 · da 126,46) e estender o `fim` de "artificial" de 128,37 para 128,58 (hoje a página some 0,2 s antes de ele terminar a palavra).
- L31: "para a própria família" → "para sua própria família" (sua 152,16).
- L19: a legenda segue o roteiro ("usa o ImageNet… rede neural numa competição de reconhecimento de imagens") e ele disse "usaram a ImageNet… rede neurais em uma competição de reconhecimento das imagens". Só flexão: manter o roteiro.
- L01/L17/L18/L05: "e ... o inglês", "os pesquisadores", "o 2012", "E os pais": funcionais, não precisa legenda.
- CTA (cartão): o rodapé diz "que eu te mando no direct", ele diz "eu te envio no seu direct". Se quiser casar: `edicao/cta.json` com `{"rodape": "que eu te envio no direct"}`.
- Página "Universidade | de Toronto" (quebra entre 30,71 e 30,73 s) e "Estados | Unidos": cosmético da paginação automática.

## Observações (não bloqueiam)
1. **Zoom segurando menos de 1,0 s** (regra de 18/09, `ZOOM_SEGURA_MIN`): 5 trechos de 0,84–0,96 s — 28,04 (L07 "Ela", 0,88 s em 1,12), 28,92 (L08, 0,96 s em 1,0), 49,72 (L11, 0,96 s), 60,96 (L14, 0,92 s) e **150,20 (L31, 0,84 s em 1,0 entre dois 1,12)**. Entre 27 e 30 s são três trocas de enquadramento em ~2 s. A EDL já está aprovada pelo Carlos, então só registro: se o corte for re-renderizado por outro motivo, vale segurar esses trechos.
2. **L32 diz "uma entrevista completa"; o material (AULA) é o PDF com o link da palestra TED2015** (`material/palestra-fei-fei-li-ted2015.pdf`, ~18 min). A L33 ("São somente dezoito minutos com a legenda em português") bate com a palestra, a palavra "entrevista" não. É improviso dele no CTA; fica a critério dele (regra 6: não prometer material que não exista — o PDF existe, só o nome do formato difere).
3. **L29**: o roteiro pedia "mostrar exemplos, organizar informação e ensinar…"; ele nunca disse "mostrar exemplos" no take (T3: "organizar informações, ensinar o que cada coisa significa", sem "e"). O corte não perdeu nada (conferi no bruto); só registro que o conteúdo "mostrar exemplos" não está no vídeo.
4. **L08** fica com "foi assim" duas vezes na frase falada ("e foi assim, ela contou, que foi assim que ela ajudou…"). Está aprovado na EDL; ver alternativa em C1.
5. `reel-props.json` tem `titulo: null`: o hook sai só com a legenda "Imagina…" (começa em 0,14 s, bom). Confirmar que é intencional.
6. `edl.json` está em `versao: 14` (o pedido falava de v13); o corte foi renderizado 05:25, depois da EDL de 05:20, ou seja, corresponde a esta.

## Voz da IA — falso positivo confirmado por amostragem
Dos 33 trechos (2,78 s) do `verify.py`, 32 caem em cima de palavra do Carlos no ASR do corte (Scribe), em nível de −25 a −35 dBFS (o dele). Os que ficam em −45 a −65 dBFS são caudas de palavra (mais baixos que a própria IA, ~−42). O único sem palavra (34,80–34,87 s, −48,6 dBFS) é o vão entre "estudou" e "física". As duas transcrições do corte não têm nenhuma palavra fora do roteiro/improviso dele, exceto o "no meu canal" (que é dele: está no bruto, `praq0987` a partir de 1055,29 s, mesma frase da L21). As duas maiores: 79,24–79,64 ("sabe", −32,1 dBFS) e 115,90–116,14 ("Mas olha", −32,7 dBFS) — voz dele.

## Conteúdo do corte × roteiro
Todas as informações das 34 linhas estão no corte. Improvisos que mudam só a forma (L04, L06, L08, L09, L10, L12, L14, L19, L22, L25, L28, L33) mantêm a mesma informação. L15 fala "50 mil" (a fonte diz "quase 50 mil"; o "mais de" foi cortado limpo em 71,28 s). L32 diz "uma entrevista completa" no lugar de "a palestra dela" (obs. 2).

## Stills (composição Reel, sem extras)
- Legenda centrada em y≈1150 (1 a 2 linhas, destaque 132 px cabe até y≈1215), abaixo do queixo, sempre sobre o peito/mão — **nunca no rosto**; laterais livres (maior página medida: "da inteligência / artificial" ≈ 530 px de largura); base ≤ 1250 (limite 670 px).
- Estilo igual a `estilo-selecao.md`: cinza→branco, destaque em branco bold grande, sombra suave, sem caixa.
- Mão passa por trás da legenda em alguns quadros (4,6 s, 133,9 s) e a leitura continua boa (branco com sombra).
- Cartão AULA (157,0 s): "comenta" + "AULA" laranja com contorno + rodapé, abaixo da boca (boca ≈ y 750, "comenta" ≈ y 960, rodapé ≈ y 1216), dentro da zona segura; legendas da janela ocultas.
- Evidências dos defeitos: 66,8 s ("aparecia" na tela com ele dizendo "reconhecer"), 72,0 s ("quase 50 mil" na tela, ele diz "cinquenta mil"), 40,9 s ("E" sozinho com ele dizendo "a partir daí"), 105,5 s (tela vazia com ele dizendo "no meu canal"), 133,9 s ("IA" com ele dizendo "inteligência artificial").

## Depois das correções
Regerar `legendas.json/srt` e `reel-props.json` (`gerar_props.py`), conferir o still de 66,8 s ("reconhecer"), 72,0 s ("50 mil"), 105,5 s ("no meu canal"), 133,9 s ("inteligência"), e rodar uma nova diff legenda × `qa/transcricao-corte.json` (zero troca de palavra de conteúdo, zero buraco de legenda > 0,45 s com fala por dentro). Com isso a Passagem 1 vira PASS.
