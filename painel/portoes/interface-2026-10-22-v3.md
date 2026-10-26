PORTÃO-INTERFACE: APROVADO — sobre 061a9d1253af (volta 3)

# PORTÃO-INTERFACE · painel · 22/10/2026 (madrugada de 23/10) · volta 3

- **Alvo:** `painel` · **portão:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão congelada no passo 0:** `061a9d1253af` (29 arquivos). Conferi de novo no fim, depois do build e dos servidores de
  teste, e continua `061a9d1253af`.
- **O que mudou desde a volta 2** (`aae5d7867e7f`): comparei o sha256 de cada arquivo com os gravados no livro
  (`painel/portoes.json`, veredicto da volta 2). Mudaram **só dois**: `web/src/lib/db.ts` e `web/src/app/desempenho/page.tsx`.
  Nenhum arquivo foi criado nem apagado.
- **Estado antes:** `interface · bloqueado` (volta 2, 00:37, S0 1 · S1 1). Reli o relatório anterior item por item (abaixo).
- **Resultado:** S0 = 0 · S1 = 0 · S2 = 4 (3 S2 novos + o S1-L PI-L1, que continua aberto) → **APROVADO**.
- **Linha de base:** continua valendo o **PI-L1 (S1-L)** da volta 2 (elementos recriados nas páginas). O redesign decidido em
  22/10 vai substituí-los, por isso conta em `--s2` e não segura o veredicto. Nesta volta nenhum S1 novo foi reclassificado
  como S1-L. O agente principal precisa avisar o Carlos no cartão de que o PI-L1 fica para o redesign.

> **Contra o que a fidelidade foi medida:** `painel/design/` continua **vazia**, e não há design aprovado. Medi de novo contra
> `00-marca/design-system/korvu-editorial.md` e contra a skill `dataviz` (invocada). Quando a designer entregar, o item "fiel ao
> design" tem de ser refeito contra o que ela entregar. Este APROVADO **não** cobre fidelidade a um design que ainda não existe.

---

## A volta 2 foi corrigida? (conferi no ponto do defeito)

| Volta 2 | Estado | Como conferi |
|---|---|---|
| **S0-1** "4 de 4 vídeos publicados", quando são 5 | ✅ **corrigido** | Em `07-publicados/` há **5** pastas e 4 têm `metricas.json`. `2026-10-23-livro-chatgpt-a` não tem, e o banco tem 4 linhas em `publicacoes`. Na tela (`desempenho-1440.png`, `desempenho-375.png`) já não existe número de "publicados". A seção 3 diz "Só entram os Reels que já têm leitura de métricas: o scripts/metricas.py lê cada um sozinho 5 dias depois de publicar (antes disso, só rodado à mão). Um Reel publicado há pouco pode ainda não estar aqui." A seção 4 diz "4 vídeos com leitura válida. Reel ainda sem leitura de métricas não entra." Os dois textos estão certos: 4 = as 4 linhas de `publicacoes`, todas com leitura não suspeita. O vazio da seção 3 virou "Nenhum Reel com leitura de métricas ainda.", com o comando certo. Vi esse vazio rodando (`teste-max-rows/vazio/desempenho-1440.png`). O `--slug <slug> --forcar` do vazio bate com o `scripts/metricas.py` (linhas 12 e 435–436), e "5 dias" bate com `DIAS_PADRAO = 5`. `grep "publicad"` em `web/src`: nenhum texto conta publicados a partir de `publicacoes`. O PD7 continua aberto no backlog: o livro A ainda não aparece na tabela como "aguardando a 1.ª leitura". A tela, porém, já não afirma nada falso sobre ele. |
| **S1-1** leitura sem paginar, cortada em 1.000 linhas (`max_rows`) | ✅ **corrigido**, provado rodando | `lib/db.ts` `todos()`: pede `count: "exact"`, lê página por página com `.range()` em ordem que termina na chave primária (conferi as 9 ordens contra `migrations/20261022190000_inicial.sql`), relê uma vez se o total muda no meio e **lança** quando vêm menos linhas do que o banco diz ter. `demografia(lido_em)` filtra no banco pela foto mais nova (182 linhas, e não as 330). **Teste:** subi um `next dev` meu na :3457 (`PAINEL_DIST=.next-trabalho`, nunca a `.next` do Carlos) ligado a um proxy só de leitura (GET/HEAD) em frente ao Supabase do painel. O proxy imita `max_rows` = **7**, o que obriga a ler as 182 linhas da demografia em 26 páginas, `portoes_estado` em 8 e `agentes` em 4. Comparei o texto inteiro de 7 rotas (`/`, `/equipe`, `/equipe/portao-imagem`, `/equipe/portao-interface`, `/equipe/contratar`, `/videos`, `/desempenho`) com o do preview do Carlos: **0 linhas diferentes** em todas. Fotos em `teste-max-rows/clamp-7/`. **Banco que esconde linhas** (2.ª página vazia com o total verdadeiro): cai na tela de erro "o banco tem 10 linhas e devolveu 7 — a página não mostra dados pela metade" (`teste-max-rows/trunca/`). **Total que muda uma vez** (sincronização no meio): relê e mostra os números certos, também com 0 linhas diferentes. O proxy registrou a 2.ª leitura indo ao banco, então a memória de pedidos do Next não a serviu. **Total que muda sempre:** a tela de erro diz "a tabela mudou duas vezes durante a leitura (o sincronizador estava rodando) — tente de novo" (`teste-max-rows/muda/`). **Vazio** e **fora do ar** continuam certos depois da mudança no `db.ts` (`teste-max-rows/vazio/`, `teste-max-rows/fora/`). |
| **S1-8 → PI-L1 (S1-L)** elementos recriados | ⏸ continua **S1-L** | Nenhum arquivo de página ou componente mudou além dos dois acima. Segue no backlog, com o gatilho = implementação do redesign. |

---

## Achados que bloqueiam

Nenhum. Zero S0 e zero S1.

---

## O que verifiquei e como

1. **Telas olhadas de verdade.** Rodei `bash painel/capturar.sh painel/portoes/capturas-061a9d1253af … --fatias` no preview do
   Carlos (:3456, só leitura), com 9 rotas a 1440 e a 375. Medido: `innerWidth` = largura pedida e `scrollWidth` = janela em
   todas as 18 fotos (`medidas.txt`), sem elemento além da borda. Abri `desempenho-1440`, `desempenho-375` (inteira + fatia 4),
   `inicio-375`, `videos-1440` e as fatias finais de `equipe-375` (o rodapé aparece, então a página não foi cortada nos 4.096 px).
   Não há texto cortado ou sobreposto, nem erro na tela: o indicador do Next no :3456 está limpo. A tabela "os vídeos" a 375
   rola dentro da própria caixa (`overflow-x-auto`), como antes (PI14).
2. **Estados rodando** no meu servidor de teste: vazio, erro (banco que esconde linhas, tabela que muda) e fora do ar (conexão
   derrubada), a 1440 e a 375. O 404 e a ficha inexistente foram fotografados no preview. Desliguei o servidor da :3457 e o
   proxy no fim. O preview do Carlos respondeu 200 antes, durante e depois.
3. **Dados honestos, da tela até a fonte** (banco via `docker exec … psql` com `default_transaction_read_only=on`; arquivos só
   lidos):
   - Seguidores 3.631, "−3 desde 16/10" (3631 − 3634), visualizações 2.448 → "2,4 mil", contas alcançadas 529, visitas 56,
     fora da bolha 307/(307+206) → 60% / 40%. Batem com `perfil_snapshots` de 22/10 13:00:32.
   - Demografia da foto de 22/10, um a um: quem segue GW 1.741 → "1,7 mil", BR 504, PT 230, AO 185, GB 127, MZ 88, SN 44,
     CV 37, US 34, FR 29 · alcançados BR 197, GB 58, PT 52, GW 22, FR 8, AO 6, DE 5, US 4, CH 3, e um país com 2 (empate,
     PI18) · cidades Juiz de Fora 29, London 27, São Paulo 23, Bissau 22, Rio 11, Lisbon 9, Cintra 8, Belo Horizonte 7 · idade
     de quem segue 13-17 15 … 65+ 52 ✓.
   - Tabela "os vídeos", com a última leitura não suspeita: Demis 338 · 450 · "11,9 s · 21%" · 1 · 1 · 2 · documentario 1/1 ·
     FB 30. Fei-Fei 40 · 45 · "9,1 s · 5%" · FB 196. Hinton (leitura de 21/10, porque a de 22/10 tem `suspeito = t`, 1.512,69 s)
     11 · 11 · "44 s · 28%" · FB 4, com o aviso da leitura descartada. Fei-Fei A 4 · 8 · "2,6 s · 2%" · FB "—" ✓.
   - "O que funciona": normal (1) 338 · trial (3) (40+11+4)/3 = 18 · perfil (4) 393/4 = 98 · até 90 s (1) 338 · mais de 90 s
     (3) 18 ✓. Visão geral: "melhor vídeo 338 · demis hassabis · leitura de 22/10" ✓.
   - Fila: os 5 `post.json` de `06-publicar/`, só lidos. 24/10 19:00 (BST), 25/10, 27/10, 28/10 e 01/11 (GMT), só Instagram,
     e os 5 na lista congelada de `_controle/gauntlet-legado.json` → "legado" ✓.
   - Topo "sincronizado sex., 23/10, 00:41" = `sincronizacoes` 23:41:57 UTC ✓. Às 00:57 houve nova passagem do
     sincronizador, e o texto do `/desempenho` continuou igual.
4. **Gráficos (skill `dataviz`, invocada).** Rodei `validate_palette.js "#e85002,#5a5852" --mode light --surface "#e7e4d9"`.
   Deu lightness PASS · CVD PASS (ΔE 12,8) · normal-vision PASS (ΔE 26) · chroma FAIL no `#5a5852` · contraste WARN do acento
   (2,96:1). Leio como nas voltas 1 e 2: o cinza é a des-ênfase da forma "1 hue + gray", não um slot categórico, e o WARN tem
   o alívio que a regra exige, porque cada barra tem o valor escrito ao lado. A paleta não mudou (`globals.css` é o mesmo da
   volta 2). Um eixo ✓, legenda na barra de 2 séries ✓, texto em tinta ✓, dica ao passar o mouse, tocar e focar ✓, rótulo
   inteiro ✓, leitura suspeita fora das médias ✓.
5. **Fiel ao design** (marca + dataviz). `grep -rnE '#[0-9a-fA-F]{3,6}\b|rgba\('` em `web/src` fora do `globals.css` deu
   vazio ✓. Componentes recriados → PI-L1 (S1-L).
6. **Acessibilidade** (skill `design:accessibility-review`, invocada como checklist). Varri o contraste de **todo nó de
   texto** com um script CDP meu, usando a cor efetiva sobre o fundo efetivo: `/desempenho` 233 nós e `/` 126 nós a 1440, e a
   tela de erro a 375. O único par abaixo do mínimo é o acento em texto grande (o "." dos títulos e os números de seção,
   2,96:1), que já é o PI4. Teclado: em `/desempenho` a ordem é logo → menu → barra empilhada → barras. Na tela de erro é
   menu → "tentar de novo". Todo foco mostrou contorno visível. `scrollWidth` = janela.
7. **Segurança e código.** `npx tsc --noEmit` exit 0 · `npx eslint src` exit 0 · `PAINEL_DIST=.next-verificacao npm run
   build` exit 0 (BUILD_ID 00:55:23, gerado agora, 7 rotas dinâmicas, 103 kB de JS comum).
   `grep -rlE "service_role|SERVICE_ROLE|eyJhbGci|sb_secret_" .next-verificacao/static` deu **vazio**, e `sb_publishable_`
   também. No cliente, "supabase" só aparece no texto "cd painel && supabase start" das telas de erro. `src/lib/db.ts` começa
   com `import "server-only"`. Não há nenhum `NEXT_PUBLIC_` no código. Os 4 `"use client"` não importam o banco.
   `npm audit --omit=dev`: 0 vulnerabilidades (`postcss` 8.5.31 por override).

## O que NÃO verifiquei (declarado)

- **Fidelidade a um design aprovado:** não existe (`painel/design/` vazia).
- **Corte com mais de 1.000 linhas reais:** não escrevo no banco do Carlos. Provei a paginação com o `max_rows` imitado a 7
  por um proxy só de leitura, em frente ao banco real (item S1-1 acima). Com o limite real de 1.000 o caminho do código é o mesmo.
- **Build de produção servido (`next start`):** o build passou, mas as telas foram vistas no `next dev`. Em produção o Next
  esconde a mensagem do erro, então os textos "o banco tem N linhas e devolveu M" e "a tabela mudou duas vezes" **não
  aparecem**: aparece o código do erro (`error.tsx:43`). Isso só li no código.
- **Safari/iOS real e leitor de tela real (VoiceOver):** toque, teclado e árvore de acessibilidade foram emulados ou lidos no
  Chrome.
- **`.env.local`:** não li nem contei as linhas. O servidor de teste pegou a chave dele sozinho, e o proxy só a repassou, sem
  imprimir.
- **Banco × arquivos em geral:** é o eixo do PORTÃO-DADOS. Conferi só por amostra (perfil de 22/10, `metricas` e
  `publicacoes` inteiras, os 5 `post.json`, as pastas de `07-publicados/`).
- **Efeito colateral dos meus servidores:** o `next dev` da :3457 reescreveu `painel/web/next-env.d.ts` (gerado, fora da
  impressão, no `.gitignore`), que agora aponta para `.next-trabalho/types/routes.d.ts`. Por isso **deixei a pasta
  `.next-trabalho`** no lugar (50 MB): sem ela o `tsc` acharia a referência quebrada. Com ela, `tsc --noEmit` passa (conferido
  depois). O `next dev` do Carlos volta a gravar esse arquivo quando reiniciar. A `.next-verificacao` (105 MB) também ficou.
- Tempo de carregamento e modo escuro (o painel não tem, e a marca não prevê).

## S2 e S1-L (não bloqueiam) → `_controle/backlog-portoes.md`

| Nº | Classe | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|---|
| PI-L1 | **S1-L** (linha de base, da volta 2) | h1 em 6 páginas, botão em 4, `Etapas`, cabeçalhos de tabela, barra empilhada e barra na tabela (detalhe no backlog) | Elementos recriados dentro das páginas em vez de virem de `src/components/` | engenheiro-frontend (+ designer-de-produto) | implementação do redesign aprovado, antes de chegar ao Carlos |
| PI25 | S2 | `web/src/lib/db.ts:87–120` (`todos`) | A paginação que fecha o S1-1 não tem teste automático. Eu a provei com um proxy, mas nada no repositório pegaria a regressão: `painel/web` não tem teste nenhum e `painel/tests/` só testa o sincronizador. O teste pedido na volta 2 (`painel_teste` com mais de 1.000 linhas) não foi feito | engenheiro-frontend + engenheiro-backend | próxima mudança em `lib/db.ts` ou no `max_rows` |
| PI26 | S2 | `web/src/app/error.tsx:16–30` × `lib/db.ts:115,119` | Os dois erros novos do `todos()` ("a tabela mudou duas vezes… tente de novo" e "o banco tem N linhas e devolveu M") caem nos passos genéricos: "Abra o Docker e ligue o banco" e "Sincronize". O certo é esperar a passagem do sincronizador e tentar de novo. Em produção o detalhe nem aparece. É da mesma família do PI19 | engenheiro-frontend | junto com o PI19 (próxima mudança nos estados) |
| PI27 | S2 | `web/src/components/ui.tsx:45` (dica do `Sinal`, motivo vindo de `scripts/portoes.py`) | O motivo aparece com a data crua: "interface: bloqueado — BLOQUEADO em 2026-10-23T00:37:57+01:00 (S0 1 · S1 1)" (visão geral, fichas, `/videos`). O resto do painel formata as datas ("sex., 23/10, 00:41") | engenheiro-frontend | redesign da visão geral / dos sinais |

**Gatilho já atingido, e ainda abertos:** PI6, PI7 e PI8 têm o gatilho "próxima mudança em `/desempenho`", e esta volta (como
a 2) mudou `desempenho/page.tsx` sem fechá-los. Continuam S2, porque nenhum dá número falso: PI7 é a base de "60%" (513) ao
lado de "529 contas", PI8 é o "· 28 dias" que falta em "visitas ao perfil", e PI6 é a precisão misturada "1,7 mil" ao lado de
"504". O agente principal deve tratá-los como **vencidos**. Recomendo fechá-los antes de o redesign de `/desempenho` chegar ao
Carlos, e não empurrar o gatilho de novo.

**Da volta 2, sem mudança:** PI1, PI2, PI3, PI4, PI5, PI10, PI11, PI12, PI13, PI14, PI15 (parcial), PI16, PI17, PI18 (o empate
agora resolve por ordem alfabética do código do país: "Cabo Verde 2"; continua sem aviso), PI19, PI20, PI21, PI22, PI23, PI24
e PD7 (do PORTÃO-DADOS).

## S0-L abertos (lista inteira do backlog)

Nenhum. A tabela "BLOQUEIOS DE PUBLICAÇÃO (S0-L)" de `_controle/backlog-portoes.md` está vazia, e este portão não abriu nenhum.

## Provas

`painel/portoes/capturas-061a9d1253af/`:
- `*-1440.png`, `*-375.png` (+ fatias `-pN`) e `medidas.txt`: o `capturar.sh` atual sobre o preview do Carlos (9 rotas).
- `teste-max-rows/clamp-7/`: `/desempenho`, `/videos` e `/equipe` com o `max_rows` imitado a 7. O texto é idêntico ao do
  preview.
- `teste-max-rows/trunca/`: o banco devolve menos linhas do que diz ter, e a página cai na tela de erro.
- `teste-max-rows/muda/`: a tabela muda a cada pedido, e aparece "mudou duas vezes… tente de novo".
- `teste-max-rows/vazio/` e `teste-max-rows/fora/`: os estados vazio e fora do ar depois da mudança no `db.ts`.
