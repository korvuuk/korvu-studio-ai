RESULTADO: PASS (com avisos)

# Revisão 1 — corte + legendas — 2026-10-20-geoffrey-hinton

Método: legendas.json (327 palavras) comparado com Scribe (qa/transcricao-corte.json) e com uma 2.ª transcrição independente (mlx-whisper large-v3-turbo sobre edicao/corte-audio.wav); 6 stills do Reel renderizados (3, 16, 41, 47, 105, 150 s); medição de nível do áudio nas emendas.

## Corte
- 29 linhas presentes e em ordem (diff.md + EDL v24). Duração 158,68 s.
- Voz da IA: nenhuma fala da IA detectada por transcrição; os 18 trechos do verify são <=0,15 s dentro de palavras do Carlos (falsos positivos já analisados). Único a vigiar: 80,85–81,00 s (início de "Pouco", L15) — nível alto (-19 dB) e contínuo, parece ser a voz dele; ouvir uma vez.
- Cauda: 158,3–158,68 s silenciosa (-75 dB); o "E aí" do whisper ali é alucinação.
- Emenda 0980→0981 em 19,76 s: cai DENTRO de "1947" ("em 194|47", fala contínua, ~1 s depois do início do número). Nível sem degrau (-34/-38/-35 dB), espectrograma sem descontinuidade visível, mas é corte no meio de palavra/número por construção. AVISO: ouvir 19,4–20,2 s.
- Emenda 0985→0986 em 80,64 s: entre frases (silêncio -74 dB antes de "Pouco" a 80,78 s). OK.
- Pausas >0,6 s em: 12,92–13,54; 63,04–63,66; 75,02–75,64; 95,36–96,16; 97,34–98,10; 113,46–114,06; 116,44–117,20; 141,60–142,22 (todas em fronteiras de peça/ritmo; nenhuma excessiva).

## Legendas
- Sem pontuação nem caracteres especiais (varredura por regex: 0 ocorrências). "Geoffrey Hinton" correto nas 3 ocorrências (15,22 / 15,94 / 123,14 s e 87,98 "Hinton"). Números: 50, 1947, 70, 2012, 10, 2023.
- Sincronia: 325/327 palavras dentro de 0,15 s do Scribe. Exceções leves: " imitar" (42,09 s) termina 0,23 s antes do áudio; " e" (112,15 s) começa 0,31 s antes do áudio ("duas e meia"). Não reprova.
- CTA L28: legenda "Comenta a palavra NOBEL que eu vou te enviar a entrevista completa", NOBEL destacado (149,02 s). reel-props cta NOBEL 147,92–152,46 s, linha L28, rodapé "que eu vou te enviar a entrevista completa". Nenhum extra sobre L28/L29 (último overlay termina em 139,12 s). Still 150 s: cartão dentro da safe zone, mãos não conflitam.
- Posição: full y≈1100–1150 e split logo abaixo da divisória; sem tapar o rosto nos stills.

## Correções propostas (menores; legenda x fala real, duas transcrições concordam)
1. L02, " dar", startMs 10000 (índice ~16): fala = "dá" ("e ainda te dá um Prêmio Nobel"); Scribe e whisper concordam. Trocar por "dá".
2. L21, " o", startMs 115700: fala = "a" ("era a comitê do Nobel"); ambas as transcrições dizem "a". Legenda corrigiu a gramática; se o critério é fala real, trocar por "a" (aceitável deixar).
3. L13, antes de " Ele" (startMs 67180): falta um "e" curto falado (67,18–67,26 s, "e ele desenvolveu"). Opcional.
4. L19/L16: " da" (startMs 105360) — fala "das inteligência artificial" (Scribe); legenda "da". Opcional.
5. L02, " mudar" (7700): whisper ouviu "mudou"; Scribe "mudar" — ambíguo, não mexer sem ouvir.
- " ganhado" (119860): Scribe "ganhado", whisper "ganhar"; mantido conforme o Carlos.

## Extras / avisos
- E01, E04, E06 (animações) ausentes: Carlos em tela cheia nesses trechos (63,6–74,28 e 107,16–113,92 e 38,68–48,92 s). AVISO, não FAIL nesta passagem; o QA final deve tratar.
- Extras de vídeo presentes: E02, E03, E05, E12, E07, E08, E09, E10, E11 em split, com crédito "Fonte: X" visível nos que vi (E02, E08).
- Still 105 s (E08/BBC): a palavra "os" da legenda encosta na faixa de crédito "Fonte: BBC News" / base do extra. AVISO: legenda no split sobe até o rodapé do painel de cima; baixar alguns px ou deslocar crédito.
- Não há extra nos intervalos 12,48–22,4 s e seguintes além do listado; extras não cobrem rosto no split (Carlos recortado embaixo).

## Não verificado
- Escuta humana do áudio (só transcrição dupla + medidas); IA nos 18 trechos curtos confiada à análise prévia.
- Stills só em 6 instantes; não revisei todas as páginas de legenda quanto a 2–4 palavras nem legibilidade de todos os extras; gravações de ecrã inexistentes aqui (sem dados pessoais a checar).
- Cor: corte em V-Log, stills já saíram com LUT de visualização; não avaliado.
