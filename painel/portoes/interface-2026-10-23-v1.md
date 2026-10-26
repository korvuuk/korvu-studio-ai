PORTÃO-INTERFACE: APROVADO — sobre dd0011568610 (volta 1)

# PORTÃO-INTERFACE · painel · 23/10/2026 · volta 1 (ciclo novo)

- **Alvo:** `painel` · **portão:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão congelada no passo 0:** `dd0011568610` (29 arquivos). Conferi de novo no fim, depois do build e dos três servidores
  de teste, e continua `dd0011568610`.
- **Por que há ciclo novo:** o APROVADO da volta 3 (`061a9d1253af`, 23/10 01:03) venceu porque mudaram `web/package.json` e
  `web/next.config.ts`. O pedido do Carlos (23/10): "Fecha também o site do painel (:3456) para só abrir no próprio Mac".
- **Resultado:** S0 = 0 · S1 = 0 · S2 = 2 (1 S2 novo, o PI28, mais o S1-L PI-L1, que continua aberto) → **APROVADO**.
- **Linha de base:** continua só o **PI-L1 (S1-L)** da volta 2 (elementos recriados nas páginas, gatilho = redesign). Nada novo
  foi reclassificado como S1-L neste ciclo.

> **Contra o que a fidelidade foi medida:** `painel/design/` continua **vazia** (0 arquivos). Este APROVADO não cobre a
> fidelidade a um design que ainda não existe, como nas voltas anteriores.

---

## O que mudou desde a volta 3 (provado byte a byte)

Comparei o sha256 de cada arquivo com o gravado em `painel/portoes.json` no veredicto da volta 3. A lista de arquivos é a
mesma (29, nenhum criado nem apagado), e só dois mudaram:

| Arquivo | Volta 3 → agora | O que mudou, e como provei |
|---|---|---|
| `web/package.json` | `e7e2c9940d4c` → `525875014122` | Tirei as ocorrências de ` -H 127.0.0.1` do arquivo atual e o sha256 voltou **exatamente** a `e7e2c9940d4c`. A única mudança é, portanto, `"dev": "next dev -p 3456 -H 127.0.0.1"` e `"start": "next start -p 3456 -H 127.0.0.1"`. Dependências, overrides e o `build` estão intactos. |
| `web/next.config.ts` | `241d95c5c50a` → `2d7e5b6c66d4` | Recuperei a versão antiga a partir de uma leitura anterior do arquivo, e o sha256 dela deu `241d95c5c50a`. O `diff` mostra só comentário: a linha 5 trocou `npx next dev -p 3457` por `npm run dev -- -p 3457`, e entraram as linhas 6–7, que explicam o `-H` e avisam que um `npx next dev` solto abre a porta. O código (`distDir`, a validação de `PAINEL_DIST`, o `nextConfig`) é idêntico. |

## O pedido do Carlos foi atendido? (provado por mim, sem confiar no relato)

**Controle primeiro.** Para mostrar que o meu teste pega uma porta aberta, subi um `node` que escuta em todas as interfaces
(`*:3459`, IPv6 de pilha dupla). Ele respondeu **200 por todos os endereços**: localhost, 127.0.0.1, ::1, **192.168.1.74** e
os dois IPv6 públicos (`2a04:…:c53f` e `2a04:…:6d76`). Depois de derrubado, o mesmo teste dá recusa. Usei o mesmo script,
`curl -g --max-time 90`, endereço por endereço, nas quatro portas.

| Servidor | Escuta (`lsof -iTCP -sTCP:LISTEN`) | localhost | 127.0.0.1 | ::1 | 192.168.1.74 | IPv6 públicos (2) |
|---|---|---|---|---|---|---|
| **Preview do Carlos :3456**: `npm run dev` → `next dev -p 3456 -H 127.0.0.1`, processo de 13:03:50 (religado pelo app Claude, que eu não toquei) | `127.0.0.1:3456` (só IPv4, só loopback) | **200** | **200** | recusa | **recusa** | **recusa** |
| Meu `next dev` :3457: `PAINEL_DIST=.next-trabalho npm run dev -- -p 3457` → `next dev -p 3456 -H 127.0.0.1 -p 3457` (vale o último `-p`, e o `-H` é herdado) | `127.0.0.1:3457` | 200 | 200 | recusa | recusa | recusa |
| Meu `next start` :3458: `PAINEL_DIST=.next-verificacao npm start -- -p 3458` (build de produção) | `127.0.0.1:3458` | 200 | 200 | recusa | recusa | recusa |
| Meu `next dev` :3457 com o banco morto (`SUPABASE_URL=http://127.0.0.1:59999`) | `127.0.0.1:3457` | — | 200 | — | — | — |

- **Em qualquer rede.** O endereço preso é `127.0.0.1`, e não o IP do Wi-Fi. No coworking o Mac recebe outro IP, que também
  cai fora da escuta. O `localhost` funciona porque o `/etc/hosts` tem `127.0.0.1 localhost` e `::1 localhost`: o cliente tenta
  `::1`, é recusado na hora e cai no `127.0.0.1`. Provei isso com o curl (`ip=127.0.0.1`), com o Node (`fetch` do
  `capturar.sh`) e com o Chrome.
- **As telas continuam funcionando, nas duas origens.** Num script CDP meu (Chrome sem janela, perfil temporário), em
  `http://localhost:3456`, `http://127.0.0.1:3456` e nos dois do meu :3457 e :3458, `/equipe/contratar` hidrata: digitar
  "legendador" no campo cargo muda o pedido para "Cargo: legendador → arquivo .claude/agents/legendador.md". O websocket do
  HMR (`/_next/webpack-hmr`) abre com **101** nas duas origens do `next dev`. Não houve erro nem aviso no console, e o log do meu
  :3457 não tem nenhum "Blocked cross-origin" nem `allowedDevOrigins`. Em produção (:3458) aparecem 4 `ERR_ABORTED` com
  `canceled=true`: são os prefetch RSC dos links do menu (`/?_rsc=…`, `/equipe?_rsc=…`), que o próprio roteador do Next cancela.
  É comportamento normal, da mesma origem, e não tem relação com o `-H`.
- **`capturar.sh` padrão** (sem `PAINEL_URL`, portanto `http://localhost:3456`): exit 0, 12 fotos (6 rotas × 1440/375), HTTP
  200, `innerWidth` = largura pedida e `scrollWidth` = janela em todas (`capturas-dd0011568610/medidas.txt`). Abri
  `inicio-1440`, `desempenho-375` (inteira e fatia 1), `videos-1440`, `equipe-contratar-375`, a última fatia de `equipe-375` (o
  rodapé está lá) e a ficha inexistente a 375. Não há texto cortado ou sobreposto, nem erro na tela.
- **Os caminhos que sobem o app herdam o `-H`:** `.claude/launch.json` (`npm --prefix painel/web run dev`) e
  `painel/iniciar.sh` (`cd web && npm run dev`). `grep` por `next dev|next start|npx next` em `.claude/agents`, `docs`,
  `painel/*.sh`, `painel/README.md`, `CLAUDE.md` e `_controle`: nenhuma instrução sobe o app sem o `-H`. O `engenheiro-frontend.md`
  e o meu `portao-interface.md` já mandam usar `npm run dev -- -p 3457`.

---

## Achados que bloqueiam

Nenhum. Zero S0 e zero S1.

---

## O que verifiquei e como (a área inteira)

1. **Rede**: a tabela acima, com o controle. Prova bruta em `capturas-dd0011568610/rede.txt`.
2. **Telas**: o `capturar.sh` padrão no preview do Carlos (só leitura) e mais 5 rotas a 375 com `--fatias`
   (`capturas-dd0011568610/fatias/`), entre elas `/equipe/portao-interface`, `/equipe/nao-existe` (a tela "não achei esta
   página", HTTP 200, que é o PI17 já conhecido) e `/rota-inexistente` (HTTP 404).
3. **Estados**: vi rodando o **fora do ar**, no meu servidor com o banco morto, a 1440 e a 375, em `/` e `/desempenho`
   (`capturas-dd0011568610/estado-fora/`). Aparece "não consegui ler os dados", com os passos e o "tentar de novo". O
   **carregando**, o **vazio** e o **erro da API** não foram refeitos neste ciclo: `loading.tsx`, `error.tsx`, `db.ts` e as
   páginas têm o mesmo sha256 da volta 3, onde os vi rodando.
4. **Dados honestos (amostra)**: o topo "sincronizado sex., 23/10, 13:07" bate com `sincronizacoes.em` = 12:07:09 UTC. Seguidores
   3.631 e "−3 desde 16/10" batem com `perfil_snapshots` (3631 em 22/10 e 3634 em 16/10). Li o banco com `docker exec … psql` e
   `default_transaction_read_only=on`. "precisa de atenção: interface · vencido" bate com `portoes.py estado painel`. O resto das
   cifras vem de código idêntico ao da volta 3, onde segui uma por uma até a fonte.
5. **Gráficos (skill `dataviz`, invocada)**: rodei de novo `validate_palette.js "#e85002,#5a5852" --mode light --surface
   "#e7e4d9"`, e o resultado é o mesmo da volta 3 (lightness PASS · CVD PASS ΔE 12,8 · normal PASS ΔE 26 · chroma FAIL no
   cinza de des-ênfase · contraste WARN do acento 2,96:1 com o valor escrito ao lado). Leio como antes: a forma é "1 hue +
   gray". Os tokens em `globals.css` não mudaram.
6. **Código e segurança** (em `painel/web`): `npx tsc --noEmit` exit 0 (rodei antes e depois de o meu servidor reescrever o
   `next-env.d.ts`) · `npx eslint src` exit 0 · `PAINEL_DIST=.next-verificacao npm run build` exit 0 (BUILD_ID
   `SJKUdqnitntCY1Hekq3vC`, 13:13, 7 rotas dinâmicas, 103 kB comuns) · `grep -rlE
   "service_role|SERVICE_ROLE|eyJhbGci|sb_secret_" .next-verificacao/static` vazio, e `sb_publishable_` também ·
   `src/lib/db.ts` começa com `import "server-only"` · nenhum `NEXT_PUBLIC_` em `src` · `npm audit --omit=dev`: 0 vulnerabilidades.
7. **Fiel ao design / acessibilidade**: nenhum arquivo de tela, componente ou `globals.css` mudou desde a volta 3 (sha256), e
   o resultado de lá continua valendo: grep de cor crua vazio, contraste varrido nó a nó, foco visível. Neste ciclo vi o foco e a
   hidratação só no formulário de contratar.

## O que NÃO verifiquei (declarado)

- **Um segundo aparelho de verdade** (celular no mesmo Wi-Fi ou a rede do coworking): testei do próprio Mac contra o IP da
  rede (192.168.1.74) e os IPv6 públicos dele. A recusa vem do socket, que só existe em `127.0.0.1`, e o firewall do macOS está
  desligado, então um aparelho de fora encontra a mesma porta fechada. Mesmo assim, não houve teste a partir de outra máquina.
- **Safari e o painel de preview do app Claude:** vi com o curl, o Node e o Chrome sem janela. O processo do preview escuta em
  `127.0.0.1:3456` e responde 200 por localhost, mas não olhei a janela do app.
- **Não reiniciei o preview do Carlos.** Ele já tinha sido religado pelo app às 13:03:50, com o `-H`, conforme o `ps`.
- **`painel/iniciar.sh` rodando:** só li o código. Rodá-lo subiria um segundo app na :3456 e mexeria no banco.
- **Clique real em "copiar pedido":** não cliquei, para não gravar na área de transferência do Mac do Carlos. Provei só que a
  origem é segura (`isSecureContext` true) e que `navigator.clipboard.writeText` existe, nas duas origens.
- **Estados carregando, vazio e erro da API** neste ciclo: o código é idêntico ao da volta 3, onde foram vistos rodando.
- **Fidelidade a um design aprovado:** não existe. **`.env.local`:** não li. **Banco × arquivos:** é do PORTÃO-DADOS.
- **Efeitos colaterais meus:** o `next dev` da :3457 reescreveu `painel/web/next-env.d.ts` (gerado, fora da impressão), que
  agora aponta para `.next-trabalho/types/routes.d.ts`. Deixei a `.next-trabalho` (48 MB) e a `.next-verificacao` (106 MB) no
  lugar. O `tsc` passa assim, e o `next dev` do Carlos regrava o arquivo quando reiniciar. Derrubei os meus três servidores e o
  controle da :3459. No fim, a única escuta 345x é a do Carlos, em `127.0.0.1:3456`.

## Backlog (`_controle/backlog-portoes.md`, só acrescentado)

| Nº | Classe | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|---|
| PI28 | S2 | `painel/so-no-mac.sh:55–69` (`conferir_portas`), `painel/iniciar.sh`, `painel/web/package.json` | O "só no Mac" do site depende só do `-H 127.0.0.1` dos scripts npm, e nada confere a escuta do app. O `conferir_portas` olha só as 553xx. Cenário: um `npx next dev` solto (ou um `-H 0.0.0.0` passado à mão) no coworking reabre o painel para a rede sem aviso. A mudança no `package.json` o portão pega, porque está na impressão; o comando solto, ninguém | engenheiro-frontend (+ engenheiro-backend, dono do `so-no-mac.sh`) | junto com o D4 (`entregar.sh`) ou na próxima mudança do `iniciar.sh`/`so-no-mac.sh` |
| PI13 (fecho) | — | `Formulario.tsx:72` | O cenário deixou de existir: o site só escuta em 127.0.0.1 (provado acima), e as duas origens possíveis, `localhost` e `127.0.0.1`, são contexto seguro, com `navigator.clipboard.writeText` presente. Reabrir se o painel for servido por HTTP fora do loopback | — | ✅ fechado em 23/10 |
| PD9 (parte do app verificada) | — | `web/package.json` | O item "app em `*:3456`" do PD9 foi verificado: dev e produção só em `127.0.0.1`, recusa pelo 192.168.1.74 e pelos IPv6 públicos, com o controle. O PD9 continua aberto pelo firewall (Carlos) e pelas chaves de demonstração | — | ✅ parte do app verificada em 23/10 |

**Já no backlog, e tocando nesta mudança:** o **PD12** (portão-dados) cobre a dica "cd painel && supabase start" de
`db.ts:62`/`error.tsx:24`/`global-error.tsx:18`, que contorna o `garantir_rede`. Vi de novo essa dica na tela de banco fora do
ar (`estado-fora/`). Não reabri como achado meu.

**Da volta 3, sem mudança:** PI-L1 (S1-L), PI1–PI8, PI10–PI12, PI14–PI27 e PD7. PI6, PI7 e PI8 continuam com o gatilho
vencido (ver a volta 3).

## S0-L abertos (lista inteira do backlog)

Nenhum. A tabela "BLOQUEIOS DE PUBLICAÇÃO (S0-L)" de `_controle/backlog-portoes.md` está vazia, e este portão não abriu nenhum.

## Provas

`painel/portoes/capturas-dd0011568610/`:
- `rede.txt`: endereços do Mac, controle `*:3459` (200 por todos) e preview :3456 (200 por localhost e 127.0.0.1, recusa pelo
  resto), com `lsof` e `ps`.
- `*-1440.png`, `*-375.png` e `medidas.txt`: o `capturar.sh` padrão (localhost:3456).
- `fatias/`: 5 rotas a 375 em fatias (desempenho, equipe, ficha do portão-interface, ficha inexistente, rota inexistente).
- `estado-fora/`: o banco fora do ar no meu `next dev` preso em 127.0.0.1:3457.
