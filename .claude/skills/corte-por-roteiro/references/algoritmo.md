# Algoritmo do corte por roteiro

Implementação: `scripts/locutores.py` (Carlos × IA), `scripts/align.py` (alinhamento e escolha), `scripts/edl.py`
(pontos de corte), `scripts/render_corte.py` (render), `scripts/verify.py` (QA). Parâmetros no topo de cada arquivo.

## 0. Locutores — Carlos × IA (método ChatGPT-monitor, `locutores.py`)
O ChatGPT Voice lê cada linha pelo alto-falante do celular na sala e o Carlos repete para a câmera: o áudio tem duas
vozes com (quase) o mesmo texto. Resultado: `locutor` ∈ `carlos | ia | null` + `locutor_conf` em cada palavra.

**Transcrição (mlx):** o Whisper não emite a repetição idêntica de uma frase dita logo antes (nem mudando
`compression_ratio_threshold`/`hallucination_silence_threshold`). `transcribe.lacunas_de_fala`: quadros com fala
(energia + vozeamento) sem palavra do ASR (cada palavra "cobre" no máx. 1,2 s), agrupados com buracos < 0,3 s; trecho
≥ 0,5 s com ≥ 0,25 s vozeados é recortado (±0,25 s) e transcrito sozinho; palavras novas entram com o tempo da fonte.

**Quadros** (wav 16 kHz, janela Hann 32 ms, passo 10 ms): nível (dBFS) · **graves** = 10·log10(E[60–250 Hz] /
E[250–4000 Hz]) — o alto-falante de celular quase não reproduz < 300 Hz · centróide e rolloff 85 % (em oitavas) ·
pitch por autocorrelação normalizada pela da janela (Boersma; 75–400 Hz; menor lag com pico ≥ 0,9·máximo; vozeado se
pico > 0,45). Ativo = nível > max(p10 + 12 dB, p99 − 40 dB).

**Camada A (Scribe):** `diarize=True`, `num_speakers=2` → `locutor_bruto`. Os 2 ids com mais tempo viram as classes
(Scribe com 1 id e acústica com 2 vozes → usa a local). A diarização entra como observação (confiança 0,92) somada à
verossimilhança acústica no HMM abaixo — discordância forte da acústica derruba a palavra para `null`.

**Camada B (local):**
1. Enunciados = palavras com intervalo ≤ 0,35 s. Vetor por enunciado (graves e centróide/rolloff = mediana; nível =
   p75; pitch = mediana dos vozeados) dividido por escalas fixas "dentro do mesmo locutor"
   (graves 3 dB, nível 3 dB, centróide 0,25 oct, rolloff 0,3 oct, pitch 2 semitons).
2. k-means ponderado (k = 2, 17 inícios). **2 vozes** se a distância entre os centros ≥ 3,0, a classe menor tem ≥ 5 % da
   fala e ≥ 2 enunciados. 2,0–3,0 = zona cinzenta (1 voz, com aviso). 1 voz → tudo `carlos` (com `--ia-primeiro`, as
   1.ªs leituras de pares leitura→repetição ficam `null`).
3. HMM de 2 estados por palavra: emissão = gaussiana diagonal por classe (média/desvio no espaço escalado, desvio
   ≥ 0,35; peso ∝ nº de quadros ativos, temperatura 0,7); troca de locutor custa p = 0,02 (intervalo < 0,15 s), 0,10
   (< 0,4 s), 0,35 (< 1 s), 0,5 (≥ 1 s). Forward-backward → posterior; 3 iterações reestimando as classes.
4. **Bordas esticadas:** numa troca de locutor o Whisper estica a 1.ª palavra do novo locutor para trás, por cima da
   cauda da voz anterior. Palavra entre vizinhos de locutores diferentes com 2+ trechos de energia separados por
   silêncio ≥ 0,15 s fica só com o último trecho (ou o 1.º, se encosta na anterior e a próxima está ≥ 0,3 s longe);
   original em `borda_asr`. Depois, 2.ª passada completa.

**Qual classe é a IA** — S = Σ peso·evidência / Σ pesos (só as disponíveis; evidência ∈ [−1, 1]):
| Evidência | Peso | Regra |
|---|---|---|
| `assinatura` | 2,0 | 0,7·tanh(Δgraves/6 dB) + 0,3·tanh(Δnível/6 dB): menos graves e menos nível = celular |
| `ordem` | 1,5 (3,0 com `--ia-primeiro`) | segmentos seguidos de locutores diferentes, ≤ 4 s, lendo a mesma linha (cobertura LCS ≥ 0,6): voto para quem leu primeiro; × min(1, pares/3) |
| `monitor` | 1,0 | segmentos com "de novo", "repete", "próxima", "faltou", "ótimo", "perfeito", "mais uma vez"… (fora do texto da linha); × min(1, n/2) |
| `inscricao` | 1,5 | distância (pitch, centróide[, graves]) de cada classe ao perfil do Carlos (`00-marca/voz-carlos.json` → `perfil_locutor`, ou 1.º áudio de `02-calibracao/amostras/`) |
Confiança do papel = |S|. `locutor_conf` = min(posterior da palavra, 0,5 + |S|/2); < 0,75 → `locutor: null`
(ou seja, com |S| < 0,5 todas as palavras ficam `null` e as linhas vão para [REVISAR]). Evidências com sinal contrário
e |valor| > 0,2 aparecem como `conflito`.

**Zonas da IA** (`zonas_ia`): cada sequência de palavras da IA (intervalo ≤ 0,6 s) + **cauda**: segue quadro a quadro
enquanto o nível > piso + 6 dB, sem entrar num quadro vozeado "do Carlos" nem na próxima palavra dele, até 0,5 s
(e até 0,2 s para trás); + voz de IA sem palavra transcrita (quadros com LLR suavizada > 3 por ≥ 0,15 s, fora das
palavras). **Sobreposição**: palavras vizinhas de locutores diferentes a < 0,10 s ou sem ≥ 30 ms de silêncio entre si.

**Modelo por quadro** (para o verify): gaussianas diagonais IA/Carlos sobre quadros vozeados de palavras com conf ≥ 0,9,
em (graves, centróide, pitch) — sem nível, para valer depois de mudança de ganho. LLR = log p(IA) − log p(Carlos),
mediana móvel de 9 quadros; voz de IA no verify = LLR > 1,5 por ≥ 2 quadros, ou palavra da re-transcrição com LLR
mediana > 1,5 (zonas sem palavra e parada da cauda usam LLR > 3).
**Limite medido** (teste sintético, varredura janela 1–9 × run 2–5 × limiar 1,5–3): nenhuma combinação pega um
vazamento de 0,1–0,3 s do fim de uma leitura da IA sem dar falso positivo na voz do Carlos — o fim de frase é sibilante/
pouco vozeado. A escolhida tem 0 s de falso positivo (gravação e corte) e mede 0–0,13 s para 0,3 s vazados,
0,23–0,30 s para 0,6 s e 0,55–0,60 s para 1,0 s (conta ~metade; confiável a partir de ~0,5 s). Por isso o verify também reprova pela conta determinística **peças da EDL ×
`zonas_ia`** (que incluem a cauda da reverb): pega vazamento curto, desde que as zonas estejam certas.

## 1. Normalização (só para comparar; a grafia original é preservada)
`common.norm_palavra()` aplicada às palavras do roteiro e da transcrição:
1. minúsculas, remove pontuação (`e-mail` → `email`);
2. números por extenso com `num2words(lang="pt_BR")`: `3` → `tres`, `10%` → `dez por cento`, `1º` → `primeiro`;
3. `unidecode` (sem acento) — **só** para o matching;
4. contrações expandidas para uma forma canônica: `pra→para`, `pro→para o`, `tá→esta` (= `está`),
   `tô→estou`, `cê/vc→voce`, `né→ne` (também é muleta), `tava→estava`…

Na transcrição, antes de alinhar (`align.tokens_por_fonte`):
- **compostos quebrados** pela transcrição são juntados quando a concatenação casa (ratio ≥ 85) com uma palavra
  do roteiro e as partes sozinhas não casam (`chat IGPT` → `chatgpt`);
- **grafia aproximada** (token ≥ 5 letras, ratio ≥ 88 com uma palavra do roteiro) é trocada pela do roteiro
  (desligado no `verify.py`, que é mais estrito);
- **separadores** falados `de novo`, `de novo de novo`, `vou de novo`, `corta`, `repete`, `repetindo` são marcados e
  descartados. Se a expressão existir no próprio roteiro, só conta como separador se estiver isolada por
  silêncio ≥ 0,3 s dos dois lados.

As bordas de cada palavra são antes "apertadas" pela energia do áudio (`common.refinar_palavras`: RMS em janelas
de 20 ms / passo 10 ms; limiar = max(p10 + 12 dB, p99 − 40 dB)), porque o ASR costuma esticar a palavra sobre o
silêncio anterior — isso afeta pausas, blocos e pontos de corte. Palavras sem nenhuma energia de fala no próprio
intervalo nem a ±0,15 s são descartadas como alucinação do ASR (o Whisper às vezes "ouve" um "E aí" no silêncio
do fim). `transcribe.py --sem-refino` desliga os dois ajustes.

## 2. Blocos e âncoras
- A transcrição de cada fonte é dividida em **blocos** por separadores, por **palavras da IA** (`locutor: ia` —
  nunca entram num take) e por silêncio > **1,5 s**. Um take nunca atravessa blocos. Palavras `null` entram, mas o take
  ganha `locutor_incerto`. Separador só conta se dito pelo Carlos; "de novo" da IA vai para `fala_ia`.
- **Leituras da IA:** as palavras da IA passam, sozinhas, pelo mesmo alinhamento (âncoras → janelas → PD entre linhas);
  janelas com sim ≥ 0,60 viram `leituras_ia` da linha (só registro). O resto da fala da IA (índices consecutivos,
  intervalo ≤ 1 s) vira `fala_ia`.
- Para cada linha (n tokens), **âncora** = posição em que as primeiras k palavras (k = 3 se n ≥ 5, senão 2)
  casam com `rapidfuzz.fuzz.ratio ≥ 80` (strings unidas). Âncora secundária (1ª palavra perdida pela
  transcrição): palavras 2..k+1 com ratio ≥ 85.
- **Recomeço sem separador**: se outra âncora da mesma linha aparece ≥ 2 tokens depois, a janela anterior termina
  ali (exceto se a repetição existir no próprio roteiro).

## 3. Janelas e similaridade
Para cada âncora p, testa fins e ∈ [p + ⌈0,6n⌉, p + ⌊1,4n⌋] (limitado ao fim do bloco / próximo recomeço) e
fica com o maior
`sim = rapidfuzz.distance.Levenshtein.normalized_similarity(tokens_take, tokens_roteiro)` (listas de palavras
mapeadas para inteiros; desempate: maior LCS, depois janela menor).
`cobertura = LCS(tokens_take, tokens_roteiro) / n`. `prefixo = sim(take, roteiro[:len(take)])`.
Candidatos com sim < 0,50 são descartados, a não ser que pareçam falso começo (prefixo ≥ 0,85).
Candidatos da mesma linha sobrepostos > 50 % → fica o de maior sim.

## 4. Flags
Alinhamento fino por `Levenshtein.opcodes` entre take e roteiro (substituição com ratio ≥ 60 = mesma palavra).

| Flag | Regra |
|---|---|
| `false_start` | prefixo ≥ 0,85 **e** cobertura < 0,60 |
| `recomeco` | o bigrama das 2 primeiras palavras aparece mais vezes dentro do take (posição ≥ 1) do que no roteiro |
| `muleta` | token inserido (não casado com o roteiro) do conjunto {é, e alongado, ã, hum, hã, tipo, né, então, assim, bom, enfim, sabe, aí…}; letras repetidas colapsadas (`ééé`, `hummm`). Palavra do conjunto que **está** no roteiro naquela posição não conta |
| `pausa_interna` | intervalo entre palavras consecutivas do take > **0,35 s** (era 0,7 s: no 1.º vídeo real ficavam buracos de 0,4–1,3 s no corte) |
| `final_cortado` | nenhuma das 2 últimas palavras do roteiro foi casada (não marcado junto com `false_start`) |
| `baixa_confianca` | confiança média das palavras < 0,6 (Scribe: exp(logprob); Whisper: probability) |
| `sobreposicao_ia` | uma palavra do take está em `locutores.json.sobreposicoes` (`carlos_i`), ou uma zona da IA cruza o take fora de um silêncio entre duas palavras dele |
| `fala_ia_interna` | zona da IA inteira dentro de um silêncio entre duas palavras do take (folga 0,04 s) |
| `locutor_incerto` | alguma palavra do take com `locutor: null` |

Tropeços (impedem "take limpo"): `false_start`, `recomeco`, `final_cortado`, `sobreposicao_ia`. `muleta`,
`pausa_interna` e `fala_ia_interna` viram cortes internos na EDL, então não desqualificam.

## 5. Linhas parecidas — programação dinâmica monotônica
Candidatos de linhas **diferentes** sobrepostos > 50 % formam um grupo (região disputada). Os grupos, em ordem
de tempo, passam por uma PD (Viterbi): estado = última linha principal atribuída; ganho = sim do candidato;
penalidade **0,10** quando a linha atribuída vem *antes* da anterior no roteiro (voltar é possível — regravação
tardia — mas menos provável). Hooks alternativos não mudam o estado. Cada região fica com um único dono;
sobreposição residual (< 50 %) entre linhas vizinhas apara o fim do take anterior. A saída é sempre na ordem
do roteiro, independentemente da ordem de gravação.

## 6. Escolha do take e status
Takes de cada linha numerados por ordem de gravação (T1, T2…; fontes em ordem alfabética).
1. **Limpos** = sim ≥ 0,80 e sem tropeço → escolhe o **último** → `ok` (`revisar` se `baixa_confianca` ou
   `locutor_incerto`). Takes depois dele preteridos por `sobreposicao_ia` aparecem no motivo.
2. Senão, entre takes com sim ≥ **0,45** e sem `false_start`, maior
   `score = 0,55·sim + 0,15·cobertura + 0,10·fluência + 0,10·recência + 0,10·confiança`
   - fluência = max(0, 1 − **0,12**·nº tropeços − **0,04**·nº muletas − **0,06**·nº pausas)
   - recência = posição do take / (nº takes − 1) (último = 1)
   → `revisar` se sim ≥ 0,80, `parafrase` se 0,45–0,80.
3. Nada ≥ **0,45** → `faltando` (os takes fracos continuam listados).

**Por que estes números (2026-09-17).** O Carlos come o fim das palavras, troca palavra, improvisa a frase e é
gago. Antes, `parafrase` começava em 0,60 e abaixo disso a linha virava `faltando` — improvisar fazia a frase
**sumir do vídeo**; e a fluência tirava 0,34 por tropeço, o que fazia o sistema preferir sempre o take mais
mecânico, justamente o que soa lido. A pergunta é "ele disse a ideia?", não "ele disse igualzinho?".

**Dicionário da fala** — `00-marca/fala-carlos.json` → `pronuncia`: o que o ASR ouve → palavra do roteiro
("pronto"→"prompt", "antropica"→"anthropic"). Aplicado em `tokens_por_fonte()` **antes** da aproximação por
grafia (que só aceita ratio ≥ 88 e nunca casaria "pronto"/"prompt", ratio 60). A troca só vale se a palavra
existir no roteiro — o dicionário nunca inventa texto. A lista cresce a cada vídeo. Com `leituras_ia`: "a IA leu a linha (N×), mas não
   há take do Carlos" — a leitura da IA nunca preenche a linha.

`nao_mapeado` = palavras fora de qualquer take de qualquer linha e fora dos separadores, agrupadas (mesma fonte,
índices consecutivos, intervalo ≤ 1 s); `so_muletas: true` quando o trecho só tem muletas.

## 7. Pontos de corte (edl.py)
- **Energia da palavra** (`common.limites_energia`): a borda refinada usa o limiar de fala (p10 + 12 dB), que deixa
  de fora o ataque suave (s, f, p soprado) e a cauda. Estende-se a borda enquanto o RMS de 10 ms > max(piso p10 + 8 dB,
  pico da palavra − 30 dB) — o tom da sala/respiração entre palavras (−55 dB no bruto real, 20 dB acima do piso) fica
  de fora —, até 0,25 s e sem passar dos vizinhos. Nenhum ponto de corte entra nessa faixa (+ `GUARDA_ENERGIA` 0,04 s).
- **Silêncio de verdade** (`common.folga_silencio`), aplicado por último a TODO ponto de corte (in, out, bordas dos
  cortes internos): nenhum quadro de 10 ms com som (> max(piso + 8, pico em ±0,5 s − 30 dB)) a menos de 0,04 s do
  ponto; senão, o ponto livre mais próximo dentro dos limites (vizinhos, zonas da IA, 2 frames de peça). Independe
  das bordas do ASR: no bruto real a energia da palavra seguinte começava dentro do intervalo que o ASR deu a uma
  muleta ("bairro | e | o poste", L09) e o corte caía 10 ms antes do ataque.
- `in` = início da 1ª palavra − **0,15 s** (e ≤ ataque − 0,04 s), nunca antes do fim da palavra anterior + 0,02 s
  nem da cauda dela (até o meio do silêncio).
- `out` = fim da última palavra + max(**0,18 s**, pausa do roteiro: normal 0,20 / pausa 0,60 / pausa_longa 0,90;
  e ≥ cauda + 0,04 s), limitado a 0,05 s antes da próxima palavra falada e do ataque dela (se não há silêncio
  suficiente, a pausa encolhe).
- Cada borda vai para o ponto de menor RMS em ±60 ms (wav 16 kHz, passo 10 ms), dentro desses limites, e depois para
  a grade de frames **para fora** (`in` para baixo, `out` para cima; se não couber entre vizinhos/zonas da IA, o
  outro lado) — o render arredonda para o frame mais próximo e podia comer até 20 ms do ataque.
- **Zonas da IA** (`locutores.json.zonas_ia`): `in` ≥ fim da última zona que começa antes da 1.ª palavra + 0,08 s;
  `out` ≤ início da 1.ª zona que termina depois da última palavra − 0,08 s (a pausa do roteiro encolhe; com a IA colada,
  o `out` fica no fim da palavra). 0,08 s = meia frame de quantização (20 ms) + alça de áudio (15 ms) + folga.
  Zona dentro de um silêncio entre duas palavras do take → corte interno [max(A.fim + 0,03; zona − 0,06),
  min(B.início − 0,03; zona + 0,06)]. `voz_ia` do segmento = Σ interseção (peças ± 15 ms) × zonas (tem que ser 0).
- `palavras_saida`, muletas e cortes internos só olham palavras que não são da IA.
- **Muleta que é fala do roteiro** (`edl.muleta_e_fala_do_roteiro`): antes de virar corte interno, um token de muleta
  é comparado com as palavras do roteiro que ficaram SEM par entre as vizinhas casadas; ratio ≥ 66 → é o ASR
  escrevendo errado o roteiro, não muleta (no bruto real, "não é **a IA**" saiu "não é **AI**" e o corte apagava
  "a IA"). Na dúvida, fica a palavra.
- Cortes internos: muleta(s) entre as palavras A e B → remove [A.fim + 0,075, B.início − 0,075]; pausa > **0,35 s** →
  remove [A.fim + 0,09, B.início − 0,09] (sobram **0,18 s**); bordas também vão para o ponto mais silencioso, ficam fora
  da energia de A e de B (+ 0,04 s) e vão para a grade **para dentro** do trecho removido (tira menos). Fala da IA:
  grade **para fora** (tira mais; `voz_ia` continua 0).
- **Enquadramento** (`planejar_zoom`): peças de câmera/celular em ordem de saída alternam 1.00 ↔ E (E = 1.12 ou a
  escala do `zoom` do segmento); a 1.ª peça de um segmento com `zoom` (TELA `ZOOM`) é fixa em E; `zoom_pecas`
  editado à mão é fixo; peças livres entre fixas alternam, e se a última livre bate numa fixa igual fica em
  (1 + E)/2. Tela: sempre 1.00 e quebra a sequência. Origem = rosto: Haar frontal (OpenCV,
  `haarcascade_frontalface_default`, 360×640 em cinza equalizado, scaleFactor 1,1, minNeighbors 5, rosto ≥ 12 % da
  largura) no meio de cada peça (+ 25/75 % da maior, 3–5 quadros); maior rosto por quadro; mediana se ≥ metade dos
  quadros tem rosto; limitado a x 30–70 %, y 25–55 %; senão `50% 38%`. `zoom_no_corte: true` na raiz.
- Peças = [in, out] − cortes internos, quantizadas para a grade de frames do projeto (`FPS_PROJETO`, padrão 25 fps = 40 ms) (peças < 2 frames são descartadas).
  `saida_inicio/fim`, `palavras_saida` e `duracao_saida` são calculados sobre essas peças.
- **Silêncio dentro de uma palavra** (varredura de energia do take, `rms_wav` + `_limiar_energia`): o ASR às vezes
  estica uma palavra por cima do silêncio (no 1.º vídeo real, o "e" do CTA durava 1,52 s com 1,3 s de silêncio
  dentro). Trechos sem energia > 0,35 s + 2×0,04 s viram corte interno, mesmo sem intervalo entre palavras.
- `palavras_saida` = **as palavras do roteiro**, não as da transcrição (pedido do Carlos, 2026-09-16: ele come o fim
  das palavras e o ASR escreveu "pronto" onde o roteiro diz "PROMPT"). Por linha: cada palavra do roteiro fica com o
  tempo das palavras do ASR casadas com ela (união de início/fim); as que ele comeu recebem tempo **interpolado**
  entre as vizinhas casadas (passo mínimo 0,06 s, dentro do segmento); o que o ASR ouviu a mais é descartado. Só se
  **nada** da linha casar (improviso) é que sai o texto do ASR.
  `destaque` vem das palavras entre `**` no `fala_original`, por posição no roteiro. Palavra que **atravessa** um corte
  interno não é descartada (só se sumir inteira): fica com a parte que sobrou; e se a mesma palavra do roteiro
  reaparecer na unidade seguinte a < 0,35 s (as duas metades de um corte), as entradas são fundidas — senão a
  legenda repetia ("pros pros").
- Overlays da coluna TELA: `TEXTO: "…"` → texto; `tela-01 00:04–00:11 split` → tela (duração limitada à linha);
  `ANIMACAO[modo]` / `animacao` → animação; `ZOOM` → `zoom: punch 1.12`. Tela/animação `split` → `layout: split`.

## 8. Render (render_corte.py)
Vídeo: `trim=start_frame:end_frame` + `setpts` por peça → enquadramento da peça: recorte `janela_zoom` do
intermediário 1440×2560 (largura = 1440/escala, proporção 9:16, `x = ox·(W − w)`, `y = oy·(H − h)` = ponto fixo na
origem, como o `transform-origin` do CSS) + `scale` lanczos (accurate_rnd, full_chroma_int) para 1080×1920 em
`yuv422p10le` + `setsar=1` → `concat`. Escala 1.00 = só a redução 1440 → 1080 (1.33 é o limite sem ampliar). EDL
sem `zoom_no_corte` (antiga): nenhum zoom aqui. Áudio: cada peça extraída do **master WAV 24-bit**
(`audio48k/<fonte>.wav`) com alças de 15 ms (sem alça antes da 1ª e depois da última), em float, encadeada com
`acrossfade=d=0.03`: duração = Σpeças + 0,03·(K−1) − 0,03·(K−1) = Σpeças. Saídas: AAC 256k no `corte.mp4` (mono nos
2 canais) e `corte-audio.wav` (pcm_s24le mono). O script confere vídeo, áudio e WAV contra Σpeças (±1 frame).

## 9. Verificação (verify.py)
Re-transcreve o corte, alinha globalmente (Levenshtein) com a sequência de linhas da EDL e atribui S/D/I a cada
linha → WER por linha; sequências ≥ 3 palavras fora do roteiro entre linhas = "extra". Linha com < 50 % das
palavras casadas = faltando (perdida no corte); linha fora da EDL = faltando (não gravada / fora da EDL);
mais de um take com sim ≥ 0,80 no corte = duplicada. **Voz da IA residual**: o modelo por quadro do
`locutores.json` (§0) classifica o áudio do corte (quadros + palavras da re-transcrição) → segundos de voz de IA;
também soma quanto das peças da EDL (± alça) toca as `zonas_ia`. Falha (exit 1): linha faltando, WER geral > 8 %,
A/V ou duração vs peças fora de 1 frame, voz da IA > 0,2 s (acústica **ou** pela EDL). Duração vs `duracao_alvo` só
gera aviso (> 15 %).
