PORTÃO-INTERFACE: APROVADO — sobre e0add25326be (volta 2)

# PORTÃO-INTERFACE · painel · 23/10/2026 · volta 2

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão congelada no passo 0:** `e0add25326be` (82 arquivos). Conferida de novo antes do registro: continua a mesma.
- **Volta anterior:** `painel/portoes/interface-2026-10-23-v2.md`, BLOQUEADO sobre `0f6e64385aae` por um S0 (S0-1: o texto
  da Desempenho dizia que um Reel saiu da conta por "leituras descartadas" quando ele ainda não tinha leitura nenhuma).
- **Placar:** S0 0 · S1 0 · S2 7. Os 7 S2 são os mesmos da volta 1 (PI52–PI57 e o S1-L PI-L1): continuam no backlog e
  nenhum é novo. Nenhum S0-L.
- **Capturas:** `painel/portoes/capturas-e0add25326be/` (dev) e `capturas-e0add25326be/build/` (build).

## O que mudou desde a volta 1 (provado)
Comparei a impressão arquivo por arquivo com a gravada no veredicto da volta 1 (`0f6e64385aae`). Nada é novo, nada foi
apagado, e mudou **exatamente um** arquivo:
- `web/src/app/desempenho/page.tsx`: `c61b0a6c13e0` → `1192b671a8fd…cc12`, o sha256 que o front-end declarou.

## Conferência do S0-1, ponto a ponto

**O código** (`desempenho/page.tsx:44–75`):
- Cada Reel cai em um de quatro casos (linha 58): `semLeitura` (nenhuma linha em `metricas`), `soDescartadas` (só leituras
  `suspeito`), `semAlcance` (leitura confiável sem alcance) ou `valida`.
- A frase de "O que funciona" (linhas 65–71, 251–253) conta cada caso com o seu rótulo.
- A meta da linha (linha 217) usa o rótulo do caso.
- A frase "Os vídeos" (linha 75) passou a dizer o que acontece de verdade: "Aparece todo Reel de 07-publicados… até lá, o
  Reel aparece com '—' e 'ainda sem leitura de métricas'".

**Contra o banco** (consulta só de leitura, sincronização das 20:40):

| Reel | Leituras no banco | O que a tela mostra | Confere |
|---|---|---|---|
| Livro ChatGPT A (22/10 21:19) | 0 | "ainda sem leitura de métricas", "—" em tudo, fora das médias | sim |
| Hinton | 3 (1 suspeita, de 22/10) | "leitura de 21 out" + a ressalva "Leitura de 22 out descartada… Valem os números de 21 out"; entra nas médias com 11 | sim |
| Demis · Fei-Fei · Fei-Fei A | 5 · 1 · 1, nenhuma suspeita | "leitura de 22 out", 338 · 40 · 4 | sim |

- A frase final de "O que funciona" ficou: "4 Reels com leitura válida. Fica de fora: 1 ainda sem leitura de métricas (a
  1.ª sai 5 dias depois do post)". Bate com o banco: 4 válidos e 1 sem leitura nenhuma.
- As médias não mudaram e continuam certas: Normal (1) 338, Trial (3) 18, Perfil (4) 98, Até 90 s (1) 338, Mais de 90 s
  (3) 18.

**Os dois casos que o banco não tem hoje** ("só descartadas" e "sem o alcance"):
- Extraí à letra do app a `leiturasConfiaveis` (`lib/db.ts`), a expressão do `caso` e o bloco `fora`/`foraTexto`, e rodei
  com dados sintéticos (`node --experimental-strip-types`, no scratchpad).
- Os cinco casos saíram certos: válido; sem leitura; só descartadas; sem alcance; e o do Hinton (descartada + confiável
  → válido, pela leitura confiável).
- A frase sai: "Ficam de fora: 1 ainda sem leitura de métricas…; 1 só com leituras descartadas (número impossível da
  API); 1 com leitura que não trouxe o alcance."

**Outras telas:** só a Visão geral e a vitrine leem `publicacoes()`. As duas filtram por alcance antes de usar
("Melhor vídeo" e "Alcance por vídeo"), então o Reel sem leitura não entra em número nenhum. Nada mais dependia da regra
antiga.

**S0-1: corrigido.**

## O que verifiquei e como (nesta volta)
- **Código e segurança** (em `painel/web`):
  - `npx tsc --noEmit` exit 0 e `npx eslint src` exit 0;
  - `rm -rf .next-verificacao && PAINEL_DIST=.next-verificacao npm run build` exit 0 (BUILD_ID `Hh2Wj81EerJXvAGf-0FId`);
  - `grep` de chaves no `static` vazio, `sb_publishable_` incluído;
  - `npm audit --omit=dev`: 0 vulnerabilidades.
- **Tela:**
  - `capturar.sh` contra o meu `next dev` (`127.0.0.1:3457`) em `/desempenho`, `/`, `/producao` e `/equipe`, e contra o
    build (`127.0.0.1:3458`) em `/desempenho`, a 1440 e 375, com fatias;
  - `scrollWidth` igual à janela nas 10 capturas;
  - abri as fatias da Desempenho (1440 p2/p3; 375 p5/p6 do build): nada cortado nem sobreposto;
  - console limpo em `/desempenho` e `/`, no dev e no build.
- **Capturas do front-end** (`painel/trabalho/frontend/v4/`): existem. Não usei como prova; refiz as minhas.
- **O resto da área** é idêntico byte a byte ao da volta 1. Valem as conferências de lá: decisões de 23/10, dados das
  outras telas, teclado, estados, vitrine, desvios julgados e contraste.

## O que NÃO verifiquei
- **Os casos "só descartadas" e "sem o alcance" na tela:** provados só pela lógica extraída do app, com dados sintéticos.
  O banco de hoje não tem nenhum Reel nesses casos, e eu não montei um banco de teste.
- **A mudança de contraste do Carlos** (`line-strong` #928874, foco em `accent-ink`): ainda não está no app, de propósito.
  Entra pelo `painel/design` depois do APROVADO da área design. Os pares abaixo do mínimo de hoje são os de `contraste.md`.
- **O mesmo da volta 1** (lista completa em `interface-2026-10-23-v2.md`): leitor de tela de verdade, Safari e a janela do
  app Claude, 320 e 1920 px, estados "nunca sincronizado" e "erro do banco", vazio com o banco vazio, "Copiar pedido",
  fidelidade às 7 telas (não aprovadas e não implementadas) e banco × arquivos (é do PORTÃO-DADOS, área `dados` vencida).
- **Efeitos colaterais meus:**
  - refiz a `.next-verificacao`;
  - o `next dev` da :3457 regravou o `next-env.d.ts` (gerado, fora da impressão);
  - derrubei os meus servidores (:3457 e :3458).

## Backlog
Nada novo. Continuam abertos, sem mudança:
- PI52–PI57;
- o S1-L PI-L1 (gatilho: implementação das 7 telas aprovadas);
- PI6–PI8, PI14–PI28.

## S0-L abertos (lista inteira do backlog)
Nenhum. A tabela "BLOQUEIOS DE PUBLICAÇÃO (S0-L)" de `_controle/backlog-portoes.md` está vazia.

## Para o agente principal
- A área `interface` está aprovada sobre `e0add25326be`.
- **O painel ainda não está limpo para o Carlos:** a área `design` segue BLOQUEADA (17:14) e a `dados` segue vencida.
  Pela regra 13 do `CLAUDE.md`, a tela só chega a ele com `portoes.py exigir painel` limpo.
- A área `dados` está vencida justamente pela mudança do `sincronizar.py` que expôs o S0-1. Quando o PORTÃO-DADOS rodar,
  vale ele conferir que `publicacoes` passou a ter uma linha por pasta de `07-publicados` com `post.json` ou
  `metricas.json`. Esta tela já conta com isso.
