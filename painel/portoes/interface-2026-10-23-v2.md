PORTÃO-INTERFACE: BLOQUEADO — sobre 0f6e64385aae (volta 1)

# PORTÃO-INTERFACE · painel · 23/10/2026 · ciclo novo, volta 1

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão congelada no passo 0:** `0f6e64385aae` (82 arquivos). Conferida de novo antes do registro: continua a mesma.
- **Por que há ciclo novo:** o APROVADO de 13:21 (`dd0011568610`) venceu. Em relação a ele, 58 arquivos são novos, 17
  mudaram e 5 foram apagados (`videos/page.tsx`, `CopieECole.tsx`, `Retrato.tsx`, `TituloPagina.tsx`, `ui.tsx`).
  Ficaram iguais 7: `package.json`, `package-lock.json`, `eslint.config.mjs`, `postcss.config.mjs`, `tsconfig.json`,
  `favicon.ico` e `capturar.sh`.
- **O que foi entregue:** os passos 1 a 4 do `painel/design/handoff.md`: tokens e fontes, casca, componentes e estados.
  As 7 telas novas ainda não estão no app.
- **Placar:** S0 1 · S1 0 · S2 7 (6 novos + o S1-L PI-L1, que continua aberto). Nenhum S0-L.
- **Capturas:** `painel/portoes/capturas-0f6e64385aae/` (30 rotas×larguras com fatias, `interacao/`, `estado-fora/`,
  `estado-carregando/`).

---

## Achado que bloqueia

### S0-1 · Desempenho: o texto diz que um vídeo saiu da conta por "leituras descartadas", e não é verdade

**Onde:** `painel/web/src/app/desempenho/page.tsx`
- linhas 48–53: `semValida` e a frase `entra`;
- linha 167: a frase "Só entram os Reels que já têm leitura de métricas…";
- linha 195: "sem leitura válida";
- linhas 229–231: "(N com só leituras descartadas fica de fora)".

**O que a tela mostra agora** (`capturas-0f6e64385aae/desempenho-1440-p3.png` e `desempenho-375-p5.png`):
- Em "O que funciona": "4 vídeos com leitura válida (**1 com só leituras descartadas fica de fora**)".
- Em "Os vídeos": "Só entram os Reels que já têm leitura de métricas… Um Reel publicado há pouco pode ainda não estar
  aqui". Logo abaixo, a tabela mostra o **Joga o livro no ChatGPT** (22 out) com "—" em tudo e a meta "sem leitura válida".

**O que o banco diz** (consulta só de leitura, `default_transaction_read_only=on`):
- `publicacoes` tem 5 linhas. Uma delas é a `2026-10-23-livro-chatgpt-a`, publicada em 22/10 às 21:19 (Londres).
- `metricas` tem **0 linhas** desse slug. Nenhuma leitura foi descartada: ela simplesmente ainda não foi lida.
- O único vídeo com leitura descartada é o Hinton (22/10, 1.512,7 s). Ele **entra** na conta pela leitura de 21/10.

**Por que apareceu agora:**
- O código assume que `publicacoes` só ganha o Reel depois da 1.ª leitura de métricas (comentário das linhas 50–52, PD7).
- O `sincronizar.py` mudou às 17:14:07 e passou a criar a publicação a partir do `post.json` (`publicacoes_e_metricas`,
  linhas 364–390). É o que o `handoff.md` §8 pedia ("Publicados pelo `post.json`").
- As capturas do front-end são de 17:05 (`painel/trabalho/frontend/v3/desempenho-1440.png`, 2.729 px, 4 linhas). As
  minhas são depois da sincronização (2.785 px, 5 linhas).
- O defeito é do texto da página: ele não distingue "ainda sem leitura" de "só leituras descartadas".

**Cenário:** o Carlos abre o Desempenho e lê que um vídeo ficou de fora porque as leituras foram jogadas fora, como
impossíveis (o caso do Hinton). Ele conclui que a API devolveu número impossível para o Livro ChatGPT, o que é falso.
Pela mesma página, ele também lê que "só entram Reels com leitura" e vê na tabela um Reel sem nenhuma leitura.

**Quem corrige:** engenheiro-frontend, em `desempenho/page.tsx`.
- Separar "sem leitura ainda" (nenhuma linha em `metricas`) de "só leituras descartadas", e contar cada um com o rótulo certo.
- Trocar "sem leitura válida" por "ainda sem leitura de métricas" quando não houver leitura nenhuma.
- Reescrever a frase `entra`: hoje o Reel publicado aparece, e com "—".
- O PORTÃO-DADOS julga a mudança do `sincronizar.py` à parte (área `dados`, vencida). A mudança é legítima; a tela é que
  precisa acompanhar.

---

## O que verifiquei e como

### 1. A base copiada é a aprovada (byte a byte, contra o livro `painel/portoes.json`)
Comparei o sha256 de cada cópia em `painel/web` com o gravado no APROVADO de design de 15:55 (`1bbde9add555`, volta 3).
Todas são **iguais**:

| Cópia | Origem aprovada |
|---|---|
| `src/app/design/tokens.css` | `design/tokens.css` |
| `src/app/design/componentes.css` | `design/componentes.css` |
| `src/app/design/acrescimos.css` | `design/acrescimos.css` = `1237dee36cf32b712be5796a387fdd59158732f7a75b721eec95c00fdce1d1c7` (o hash completo que ele declarou confere com o livro) |
| `src/app/design/fontes/*` (4 arquivos) | `design/fontes/*` |
| `src/app/design/icones.json` | `design/icones/icones.json` |
| `public/marca/*.svg` (2) | `design/marca/*.svg` |

Observação: o `painel/design/acrescimos.css` de hoje (`d8272f43…`) é a versão nova da designer, ainda BLOQUEADA. O
front-end copiou a aprovada, como devia.

### 2. Código e segurança (em `painel/web`)
- `npx tsc --noEmit` deu exit 0 e `npx eslint src` deu exit 0.
- `rm -rf .next-verificacao && PAINEL_DIST=.next-verificacao npm run build` deu exit 0 (BUILD_ID `x3OHZuuf5G2LWnE1j3sUm`,
  17:17). São 11 rotas dinâmicas, 103 kB comuns.
- `grep -rlE "service_role|SERVICE_ROLE|eyJhbGci|sb_secret_" .next-verificacao/static` veio vazio. `sb_publishable_`
  também veio vazio.
- O HTML de 6 rotas, no dev e no build, não tem chave nem o endereço do banco (`55321`).
- `src/lib/db.ts`, `lib/casca.ts` e `lib/retratos.ts` começam com `import "server-only"`.
- Não há nenhum `NEXT_PUBLIC_` em `src` nem no `next.config.ts`.
- `npm audit --omit=dev`: 0 vulnerabilidades. As dependências estão iguais às de 13:21.
- `grep` de `#hex`, `rgba(`, `hsl(` e `oklch(` fora de `src/app/design/` veio vazio. Não há `bg-[#…]`. Os `style=` são
  só larguras, `--table-min`, `--s` do avatar e `var(--chart-N)`.

### 3. A tela de verdade
- `capturar.sh` contra o meu `next dev` em `127.0.0.1:3457` (com `PAINEL_VITRINE=1`), nas 15 rotas, a 1440 e 375 px,
  com fatias. As rotas foram `/`, `/equipe`, as fichas `diretor`, `portao-imagem` e `portao-interface`,
  `/equipe/contratar`, `/producao`, `/videos`, `/calendario`, `/desempenho`, `/biblioteca`, `/tokens`, `/sistema`,
  `/equipe/nao-existe` e `/rota-inexistente`.
- `scrollWidth` igual à janela nas **30** capturas (`medidas.txt`). Abri as páginas inteiras e as fatias de todas as
  telas do Carlos. Não há texto sobreposto nem erro na tela. Os títulos de vídeo cortam com reticências e `title`
  (comportamento do componente aprovado).
- **Console:** limpo, sem erro, aviso ou hidratação, nas 10 rotas principais, no dev (:3457) e no build (:3458).
- **Fontes:** a Geist e a Geist Mono carregam no build e no dev (`document.fonts`: "Geist 100 900", "Geist Mono
  100 900"). O `url("fontes/…")` relativo funciona, o que fecha a parte (a) do PI36 no app.

### 4. Decisões do Carlos de 23/10 que a casca tinha de cumprir

| Decisão | Como conferi | Resultado |
|---|---|---|
| Menu com 7 itens, nesta ordem: Visão geral · Equipe · Produção de conteúdo · Calendário · Desempenho · Biblioteca · Tokens e custos | captura, ordem do Tab e `lib/navegacao.ts` | cumpre (Equipe com "26", que bate com `agentes`) |
| `/videos` → `/producao` | `curl` no dev e no build: **307** para `/producao` (com query preservada) | cumpre (`/videos/` → 308 → `/videos` → 307) |
| Topo com busca, avisos e "Carlos · Proprietário" | captura + CDP | cumpre (detalhe no item 6) |
| Versão do modelo nos chips | Equipe, fichas, gerentes, contratar | cumpre: "Opus 5.5" / "Sonnet 5.5" em todo chip; o pedido do contratar sai "Modelo: sonnet (Sonnet 5.5)". `agentes.modelo` = 15 opus + 11 sonnet = os 25 `.claude/agents/*.md` (14 + 11) mais o Atlas |
| Custo em libras | `grep €`/`US$` em `src` | cumpre: nenhum custo real na tela ainda; o formato `libras()` sai "£ 12,40" / "£ 1.292"; a tela Tokens diz "em libras… com a taxa de câmbio usada". Ressalva no PI54 |
| Retrato = foto realista; iniciais para quem não tem | comparação das 10 cópias com os originais (miniatura 24×24, erro médio) | cumpre (detalhe abaixo) |

Detalhe dos retratos:
- Cada `public/equipe/<id>.jpg` (512×512, RGB) casa com o original certo, com erro 0,2–0,3 contra ≥ 12 do segundo
  candidato. Exemplos: `portao-pauta` → Vera Campos, `revisor-de-roteiro` → Otávio Reis, `roteirista` → Marina Costa.
- Na tela, os 10 aparecem com foto e os outros 16 com iniciais.
- A pasta `src/app/equipe/img equipe/` não existe mais. Os originais estão em `painel/referencias/fotos-equipe-originais/`.
- Não sobrou nenhuma referência a `Retrato`, `TituloPagina`, `CopieECole`, `ui.tsx`, Bricolage ou `next/font`.

### 5. Dados honestos (segui até o banco, só leitura)
Os números da tela batem com o banco nestes pontos:
- **Topo:** "sincronizado em 23 out, 17:14" = `sincronizacoes.em` 16:14:28 UTC.
- **Perfil:**
  - seguidores 3.631, "▼3 desde 16 out" (3634 → 3631);
  - alcance 529;
  - fora da bolha 60 % (307 de 513);
  - visualizações 2.448 e visitas 56.
- **Melhor vídeo:** 338 (Demis, leitura de 22/10).
- **Gerentes:** "0 de N aprovados" = `portoes_estado`. Pauta 0/10, roteiro 0/12, imagem 0/10, corte 0/5, publicação 0/5,
  design+interface 0/2, dados 0/1.
- **Fila:** as 5 horas em Londres, com a virada para GMT em 25/10 (18:00Z → 19:00; 19:00Z → 19:00). "Trial manual" =
  `trial = MANUAL`.
- **Países e cidades:** os 10 países das duas listas, as 8 cidades e as 7 faixas de idade.
- **Rosca:** 307/206.
- **Médias de "O que funciona":** Normal (1) 338, Trial (3) 18, Perfil (4) 98, Até 90 s (1) 338, Mais de 90 s (3) 18. A
  leitura suspeita do Hinton (22/10) fica fora.
- **Veredictos na ficha do portão-interface:** iguais ao `portoes.json`.
- **Avisos do sino:** "8 arquivos" e "80 arquivos" = `portoes.py estado painel`.

A exceção é o **S0-1** acima.

Os estados de portão que a tela mostra seguem o banco, que sincroniza a cada 15 min. Às 17:14 o design ainda aparecia
"Vencido". Na passagem seguinte já aparecia "Bloqueado", igual ao `portoes.py`. Isso é atraso do sincronizador, não
defeito da tela.

### 6. Interação, teclado e acessibilidade (Chrome sem janela via CDP, com o meu script em scratchpad)
- **Tab a 1440:**
  - ordem: "Pular para o conteúdo" → logotipo → os 7 itens → busca → sino → regiões das tabelas → chips com dica;
  - anel de foco de 2 px `#FF4D00` em todos;
  - a busca mostra o foco pela borda escura com halo (`interacao/busca-marina-1440.png`).
- **"Pular para o conteúdo":** Enter leva o foco ao `main#conteudo`, e o Tab seguinte cai na 1.ª região da página.
- **Busca:**
  - ⌘K foca o campo e "marina" → "Marina Costa · Pessoa · Roteirista" (`aria-selected`, "1 resultado" no `aria-live`); Enter → `/equipe/roteirista`;
  - "hinton" → vídeo; seta para baixo + Enter → `/producao#v-2026-10-20-geoffrey-hinton`, e a âncora existe;
  - "zzzqqq" → "Nada encontrado…"; Esc limpa e fecha.
- **Sino:**
  - `aria-label` "Avisos: 3 portões pedindo ação";
  - abre com os 3 avisos e o link de cada um; Esc fecha e devolve o foco ao sino;
  - a 375 o painel fica dentro da janela (x=16, w=343, `scrollWidth` 375).
- **Menu a 375:**
  - Enter no "Menu" → "Fechar" + `x`, `aria-expanded=true`, `body.overflow=hidden`, `.k-area` inerte;
  - o Tab percorre busca → 7 itens → topo;
  - Esc fecha e devolve o foco ao botão; tocar num item navega e fecha;
  - a busca dentro do menu funciona ("desemp" → Desempenho).
- **Dica:**
  - abre por foco (chip "Vencido": "Portão dos dados · 8 arquivos mudaram…") e por mouse (barra "Guiné-Bissau · 1.741 seguidores"), a 1440 e a 375;
  - fica dentro da janela; Esc fecha.
- **Contraste dos pares novos do `casca.css`** (WCAG, calculado):
  - `k-dono-papel` ink-3/bg 4,64;
  - conta na barra lateral 6,19;
  - rodapé 5,22;
  - detalhe da busca 4,91;
  - `kx-etiqueta` 4,91;
  - `k-tokens` 5,79;
  - placeholder 4,94.
  Os pares abaixo do mínimo (foco 2,97 sobre `bg`, borda `line-strong` 2,47) são os 10 já pendentes com o Carlos em
  `contraste.md`.
- **Estado nunca só pela cor:** os chips têm sempre a palavra; as etapas têm o nome do estado ao lado e um `aria-label`;
  o delta tem a seta, o número e a palavra para o leitor de tela.

### 7. Gráficos (skill `dataviz`, invocada)
- `validate_palette.js "#ff4d00,#111111" --mode light --surface "#fbf9f4"`:
  - CVD **PASS** (ΔE 39,5), visão normal **PASS** (53,9), contraste ≥ 3:1 **PASS**;
  - faixa e croma **FAIL** no preto, que é neutro e foi decidido pelo Carlos ("não alterar"); é o mesmo resultado das voltas anteriores.
- Com as 4 cores da rosca da vitrine, taupe e areia dão contraste **WARN**. A legenda tem os valores escritos e há a
  tabela "Ver os números", que é o alívio que a regra pede.
- Um eixo só; texto em ink, nunca na cor da série; legenda com 2+ séries (linha da vitrine); dica no hover e no foco;
  tabela gêmea em todo gráfico; leitura `suspeito` fora.

### 8. Estados (no meu servidor, nunca no do Carlos)
- **Banco fora do ar:** `SUPABASE_URL=http://127.0.0.1:59999`, rotas `/`, `/equipe`, `/desempenho`, a ficha e `/tokens`,
  a 1440 e 375 (`estado-fora/`).
  - Aparece a nota "O banco do painel está fora do ar" antes do h1, e "Não deu para ler os dados" com "Como resolver"
    (os comandos `COMO_LIGAR`/`COMO_SINCRONIZAR`), "Tentar de novo" e o detalhe técnico.
  - A casca fica de pé: o sino aparece sem ponto e sem contagem. É igual à prévia aprovada `erro.html`.
- **Carregando:** servidor de mentira que segura a resposta do banco por 20 s (`estado-carregando/`). Esqueleto dentro da
  casca, `role=status` "Carregando os dados do painel…", 36 blocos, `scrollWidth` igual à janela, a 1440 e 375.
- **Não encontrado:** `/rota-inexistente` responde 404; `/equipe/nao-existe` mostra a mesma tela com HTTP 200 (o PI17 de
  sempre).
- **Vitrine `/sistema`:**
  - no meu dev com `PAINEL_VITRINE=1`, abre (a página inteira foi fotografada);
  - no build em :3458 **sem** a variável, mostra "Página não encontrada" (o payload traz `NEXT_HTTP_ERROR_FALLBACK;404`;
    o HTTP é 200 pelo mesmo motivo do PI17);
  - a variável não está no `.env.local`: o `next start` também carrega esse arquivo e a vitrine não abriu.

### 9. Os desvios das prévias (julgados um por um)
Não recebi o relatório escrito do engenheiro-frontend em arquivo. Julguei os desvios marcados no código (`casca.css`, com
os blocos `[ARTBOARD]`/`[FRONT]`, e os comentários dos componentes) e os que vi na tela.

| Desvio | Base aprovada (15:55) | Veredicto |
|---|---|---|
| Barra do app com busca, sino e "Carlos · Proprietário" (`casca.css:22–41`, `BarraApp.tsx`) | não tinha (busca e período no topo da página, dono no rodapé da lateral) | **aceito**: é a decisão do Carlos de 23/10. Os nomes e valores são os mesmos da proposta da designer (`painel/design/acrescimos.css:250–266`), que o portão de design não bloqueou nesse ponto. Duplicação → PI53 |
| "Produção de conteúdo" em duas linhas (`line-height:15px`), sem `aria-disabled`, contagem só na Equipe | "Vídeos e portões 12", 3 itens desativados | **aceito**: decisão do Carlos; igual à proposta da designer (`acrescimos.css:246`; a `telas/visao-geral.html` só tem o "26") |
| Rodapé da lateral "@korvu_oficial · Instagram · Facebook" | dono no rodapé | **aceito**: artboard e handoff v2 §0 |
| h1 com maiúscula inicial e sem ponto ("Visão geral") | igual (prévia `casca.html` aprovada) | **aceito**: segue o aprovado. O "minúsculas com ponto" é da v2, BLOQUEADA. Rever quando as 7 telas forem aprovadas |
| `.k-event .k-segura` (PI38) e `.k-table-wrap{position:relative}` antecipados no `casca.css` | não tinha | **aceito**: mesma regra da versão nova da designer; sai quando ela for copiada (PI53) |
| Peças `kx-*` (campos, painel de avisos, lista da busca, rótulo→valor, ressalva, etiqueta) | não tinha | **aceito**: só `var(--…)`, contraste medido acima de 4,5:1 e montadas sobre peças do sistema (`k-menu`, `k-card`, `k-note`). Vão à designer para entrar no livro (PI53) |
| Detalhe da busca em ink-2, não ink-3 | ink-3 só sobre bg/surface | **aceito**: ink-3 sobre `surface-sunken` daria 4,36:1 |
| Card de pessoa sem o chip "Portão" na Equipe | o livro põe "Portão" no gerente | **aceito**: o chip cortava o nome, e o cargo diz "portão da pauta". A Equipe será refeita pela tela nova |

### 10. Fidelidade às telas
As 7 telas (`painel/design/telas/`) **não estão aprovadas**: a área design está BLOQUEADA desde 17:14. Também não estão
implementadas. Comparei os componentes com as prévias aprovadas e a casca com as decisões. As telas antigas vestidas com
o sistema continuam cobertas pelo **PI-L1 (S1-L)**, cujo gatilho é a implementação do redesign. Continuam lá, por
exemplo:
- a célula de vídeo montada à mão em `desempenho/page.tsx:186–206` (em vez do `CelulaVideo`);
- o topo da ficha com utilitários Tailwind em `equipe/[id]/page.tsx:84–96`;
- a grade de departamentos em `equipe/page.tsx:62`.

---

## O que NÃO verifiquei (declarado)
- **O relatório escrito do engenheiro-frontend:** não estava em arquivo. Julguei os desvios que achei no código e na tela
  (item 9). Se a lista dele tiver outro desvio, ele não foi julgado.
- **Leitor de tela de verdade** (VoiceOver): conferi papéis, nomes, `aria-*`, ordem do Tab e `inert` pelo DOM, sem ouvir.
- **Safari e a janela de preview do app Claude:** só o Chrome sem janela. O preview do Carlos (:3456) não estava no ar e
  eu não o liguei.
- **320 px e 1920 px:** só capturei 1440 e 375.
- **Estados "nunca sincronizado" e "banco respondeu com erro"** (tabela em falta): só li `layout.tsx:39–54` e
  `error.tsx`. Não montei um banco vazio nem um banco sem migração.
- **Vazio de cada bloco com o banco vazio:** só leitura do código (os `Vazio` de cada seção). Não rodei com um banco vazio
  neste ciclo.
- **"Copiar pedido":** não cliquei, para não mexer na área de transferência do Mac. Vi o formulário hidratar ("legendador"
  → `.claude/agents/legendador.md`).
- **Banco × arquivos:** é do PORTÃO-DADOS, cuja área está vencida (o `sincronizar.py` mudou às 17:14). **`.env.local`:**
  não li.
- **Efeitos colaterais meus:**
  - o `next dev` da :3457 reescreveu `painel/web/next-env.d.ts` (gerado, fora da impressão) para `.next-trabalho/types`;
  - refiz a `.next-verificacao` (build das 17:17) e reaproveitei a `.next-trabalho`;
  - derrubei os meus servidores (:3457, :3458) e o servidor de mentira (:59998).

## Backlog (`_controle/backlog-portoes.md`, só acrescentado)

| Nº | Classe | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|---|
| PI52 | S2 | `components/Avisos.tsx:88` + `lib/estados.ts:66–76` (`resumoMotivos`) | O sino mostra o motivo com a data crua: "o painel · BLOQUEADO em 2026-10-23T17:14:36+01:00 (S0 0 · S1 4)". É o PI27, agora também no topo de toda página | engenheiro-frontend | junto com o PI27 (redesign da Visão geral) |
| PI53 | S2 | `src/app/casca.css:12–45, 84, 175–178` | Os blocos `[ARTBOARD]` (barra do app, avisos, dono, item de 2 linhas, `k-tokens`), o PI38 e o `.k-table-wrap{position:relative}` repetem regras da versão nova da designer. Quando ela for aprovada e copiada, os mesmos seletores existirão duas vezes, e uma mudança da designer pode ser vencida pela cópia velha. As peças `[FRONT]` (`kx-*`) ainda não estão no livro | engenheiro-frontend (+ designer-de-produto, para o livro) | na cópia do próximo `acrescimos.css` aprovado |
| PI54 | S2 | `lib/formato.ts:41–43` (`taxaCambio`), `components/Kpi.tsx:4` | O exemplo do comentário é "US$ 1 = £ 0,79 · Banco da Inglaterra", mas a decisão é £ 0,7465 (XE, 23/10). O formato também difere do livro ("£ 0,7465 por US$ (XE, 23 out)"), e o KPI ainda fala em "€". Hoje não está em uso | engenheiro-frontend | antes de implementar Tokens e custos |
| PI55 | S2 | `app/sistema/page.tsx:171` | Na vitrine, o delta dos seguidores é fixo ("▼", "ruim", "a menos"). Se os seguidores subirem, a vitrine mostra uma queda. Só a vitrine | engenheiro-frontend | próxima mudança na vitrine |
| PI56 | S2 | `components/Portao.tsx:32–43` | O modo Decisão conta "N de 4" incluindo "não se aplica": um vídeo sem pauta, com tudo aprovado, sai "3 de 4 portões aprovados · sua decisão" | engenheiro-frontend | antes de usar o `Portao` na Produção |
| PI57 | S2 | `desempenho/page.tsx:195`, `producao/page.tsx:105` × `page.tsx:145` | (a) O pilar aparece como o slug cru ("Tutoriais-rapidos"). (b) O modo sai "Trial (manual)" na Produção e "Trial manual" na Visão geral | engenheiro-frontend | redesign de `/desempenho` e da Produção |
| PI-L1 | S1-L (continua) | ver acima (item 10) | Elementos ainda montados nas páginas | engenheiro-frontend | implementação das 7 telas aprovadas |
| PI36 (a) (fecho no app) | — | `src/app/design/tokens.css` (`@font-face`) | A Geist e a Geist Mono carregam no build e no dev (`document.fonts`) | — | ✅ fechado em 23/10 |

Continuam abertos, sem mudança:
- PI6–PI8 (gatilho vencido, fecham antes do redesign de `/desempenho`);
- PI14–PI27, PI28;
- PI16, que segue em `producao/page.tsx:68,114` e `Kpi.tsx:44`;
- PI17, que agora também vale para `/sistema` sem a variável.

## S0-L abertos (lista inteira do backlog)
Nenhum. A tabela "BLOQUEIOS DE PUBLICAÇÃO (S0-L)" de `_controle/backlog-portoes.md` está vazia, e este portão não abriu
nenhum.

## Para o engenheiro-frontend (volta 2)
1. **S0-1:** em `desempenho/page.tsx`, separar "ainda sem leitura" de "só leituras descartadas" nas linhas 48–53, 167,
   195 e 229–231. Conferir com o Livro ChatGPT A (0 leituras) e com o Hinton (1 leitura descartada, entra pela de 21/10).

O resto da base está certo: tokens, casca, componentes, estados, decisões de 23/10, segurança e acessibilidade. Não
mexa nisso.
