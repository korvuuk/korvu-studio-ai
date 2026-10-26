# Look de referência — "Tenet" (referência 1 do Carlos, 2026-09-15)

> **Arquivos (2026-09-15):** mosaico original em `_mosaicos/ref-tenet-01.webp` (4 frames do filme *Tenet*), dividido em:
> - `ref-tenet-01a.jpg` — mesa com relógio amarelo, ambiente nublado (paleta geral, neutros frios, amarelo contido)
> - `ref-tenet-01b.jpg` — rosto em plano médio, trilhos e vagões (pele + fundo teal/oliva)
> - `ref-tenet-01d.jpg` — rosto em close, deitado, luz branca suave (pele + altas macias)
> - `_fora-do-lut/ref-tenet-01c.jpg` — close escuro e desfocado com o título "TENET": **fora do cálculo** do LUT (puxaria as sombras e o texto branco distorceria a análise); só referência visual.
> É referência **privada de cor** — imagem com direitos da Warner Bros. Nunca publicar, nunca usar em capa/post.

## O que o Carlos quer (leitura visual da referência)

| Aspecto | Referência | Alvo para os Reels |
|---|---|---|
| **Saturação geral** | baixa, "lavada", nada de cor viva | −25 a −35% vs. câmera; cores fortes (roupa, telas de fundo) contidas |
| **Temperatura/tinta** | fria nas sombras e no ambiente (verde-azulado / teal), céu nublado cinza-ciano | sombras puxando para teal (matiz ~185–200°), meios-tons levemente frios, altas neutras |
| **Pele** | marrom natural, quente mas dessaturada, sem laranja | preservar a linha de pele; saturação da pele −10 a −15%, nunca alaranjada nem esverdeada |
| **Verdes/vegetação** | oliva/musgo, apagados | verdes deslocados para oliva e dessaturados (−40%) |
| **Laranjas/amarelos** | sobrevivem, mas contidos (relógio amarelo) | amarelo/laranja com −15%, levemente puxados para âmbar |
| **Contraste** | médio, curva S suave de filme, altas com roll-off macio | pretos ~3–5 IRE (profundos mas não esmagados), brancos ≤ 90 IRE, meios-tons do rosto ~45–55 IRE |
| **Luz** | difusa, nublada, "moody" | exposição média um pouco abaixo do "YouTube claro"; nada de brilho estourado |
| **Textura** | grão fino de película | opcional: grão sutil na etapa de cor (`--grao 0.3`), desligado por padrão |

**Em uma frase:** cinematográfico, frio e contido — sombras teal, pele natural dessaturada, verdes oliva, contraste de filme suave, nada de cor "Instagram saturada".

## Cuidados para o conteúdo da Korvu
- Os Reels têm **legendas brancas/cinzas e acento laranja** (`estilo-selecao.md`): o look frio ajuda o laranja a destacar — manter.
- Rosto é o protagonista: se o LUT deixar a pele cinzenta ou sem vida, reduzir a intensidade (0.7–0.85) em vez de mexer na pele.
- Gravações de ecrã **não** recebem o look.

## Parâmetros iniciais sugeridos para o `/criar-lut`
- método `mkl` (transferência global, mais estável que histograma para um look de filme)
- `--intensidade 0.8`, `--proteger-pele 0.7`
- comparar com uma amostra real do Carlos gravada na luz do dia a dia (ver roteiro de teste)
