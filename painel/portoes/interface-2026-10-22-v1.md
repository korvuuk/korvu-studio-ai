PORTÃO-INTERFACE: BLOQUEADO — sobre 4f50595fb2a3 (volta 1)

# PORTÃO-INTERFACE · painel · 22/10/2026 · volta 1

- **Alvo:** `painel` · **portão:** `interface` · **auditor:** portao-interface (opus) · **fiscalizados:** designer-de-produto, engenheiro-frontend
- **Impressão congelada no passo 0:** `4f50595fb2a3` (21 arquivos: `capturar.sh`, `web/eslint.config.mjs`, `web/next.config.ts`,
  `web/package-lock.json`, `web/package.json`, `web/postcss.config.mjs`, `web/tsconfig.json`, `web/src/**` — 14 arquivos).
  Conferida de novo antes e **depois** do `npm run build`: continua `4f50595fb2a3`. O build não mexeu em nenhum arquivo da área
  (`tsconfig.json` com o mesmo sha antes e depois).
- **Estado antes:** `interface · pendente` (1.ª volta, sem relatório anterior). `dados` já rodou (BLOQUEADO, `dados-2026-10-22-v1.md`).
- **Resultado:** S0 = 1 · S1 = 9 · S2 = 16 → **BLOQUEADO**.

> **Contra o que a fidelidade foi medida.** `painel/design/` está **vazia**: a designer ainda não trabalhou e as referências
> do Carlos (`painel/referencias/`) só têm o LEIA-ME. Não há design aprovado. Nesta volta o item "fiel ao design" foi
> auditado contra **`00-marca/design-system/korvu-editorial.md`** (a marca que o próprio `globals.css` e o README do
> painel dizem seguir) e contra as **regras da skill `dataviz`** (invocada). Quando a designer entregar `painel/design/`,
> a fidelidade tem de ser auditada de novo contra ela.

---

## Achados que bloqueiam

### S0-1 · No celular, o motivo do portão sai cortado — e um motivo real empurra a página para o lado
- **Onde:** `web/src/app/globals.css` linhas 67–89 (`.dica-texto`: `position:absolute; left:50%; transform:translateX(-50%);
  white-space:nowrap`) usado pelo `Sinal` (`web/src/components/ui.tsx` 41–55) — o único lugar onde o painel mostra **por que**
  um portão bloqueou/venceu ("Passe o mouse no sinal para ver o motivo", `/videos`).
- **Medido (Chrome sem janela, CDP, 375 px com toque emulado):**
  - `/equipe/portao-imagem`, toque no 1.º sinal: a dica abre (opacidade 1) mas ocupa **x = −65 … 256**. Os primeiros 65 px ficam
    fora da tela, que não rola para a esquerda. Prova: `painel/portoes/capturas-v1/prova-toque-sinal-375.png` — lê-se
    "inda não rodou — o portão ainda não rodou" (falta "imagem: a").
  - Mesma tela, com um motivo no formato que o `scripts/portoes.py` escreve (linha 295: "mudou depois do APROVADO: capa/capa-A.png,
    capa/capa-B.png, edicao/cor/corte-cor.mp4"): a dica vai de **x = −237 a 428** e a página passa de `scrollWidth` **375 → 428**
    — rolagem lateral, **mesmo com a dica escondida** (elemento com opacidade 0 conta para a rolagem).
- **Regra:** `portao-interface.md` §1 — "texto cortado ou sobreposto = S0"; "375 px sem rolagem lateral fora de tabela larga".
- **Cenário concreto:** este veredicto BLOQUEADO entra no banco na próxima passagem do sincronizador (≤ 15 min) e aparece na
  visão geral, em "precisa de atenção", como `interface: bloqueado — BLOQUEADO em <data> (S0 1 · S1 9)` (`portoes.py` linha 284).
  O Carlos abre no celular, toca no sinal e lê o motivo pela metade. Quando um portão **vencer** com lista de arquivos, a
  página ainda ganha rolagem lateral.
- **O que precisa mudar:** **designer-de-produto** define como o motivo aparece no celular (texto visível abaixo do sinal,
  folha ao tocar, ou dica que quebra linha). **engenheiro-frontend** implementa: a dica nunca sai da janela (largura máxima,
  quebra de linha, presa à borda), e nada escondido aumenta a largura da página. Repetir as duas medições acima com um motivo
  longo.

### S1-1 · `capturar.sh` não fotografa um celular: o "375" é uma tela de 500 px recortada, e a página é cortada em 2400 px
- **Onde:** `capturar.sh` linhas 17–19 (`--window-size="$largura,2400"`).
- **Medido:** com `--window-size=375,2400` o Chrome sem janela abre a página com `innerWidth` = **500** (mínimo da janela). A
  imagem tem 375 px, mas a página foi montada a 500 px e recortada. Por isso `inicio-375.png` mostra o menu "desempenh" cortado,
  "sincronizad", parágrafos cortados no meio da palavra e os cartões com rolagem. **Nada disso existe num celular de verdade.**
  Com emulação de dispositivo a 375 px (`Emulation.setDeviceMetricsOverride`, `mobile:true`) as 6 rotas medem
  `scrollWidth = 375`, o menu quebra linha e não há texto cortado (`capturas-v1/*-375-real.png`). Além disso, a altura fixa de
  2400 px corta as páginas longas: a 375, `/equipe` tem mais de 4096 px e `/desempenho` 3292 px. Em `equipe-375.png` os
  departamentos pós-produção, distribuição e tecnologia **nunca aparecem**.
- **Regra:** `portao-interface.md` §1 (abrir a tela de verdade a 1440 e 375) e `CLAUDE.md` regra 10 (conferir pelo meio certo).
  O script é a ferramenta que o GAUNTLET usa para "olhar a tela" (`docs/gauntlet.md`, seção do painel).
- **Cenário concreto:** o construtor e o portão olham um celular que não existe. Aparece defeito falso (texto cortado). Some
  defeito real que só acontece entre 375 e 500 px. E metade da equipe e o fim do desempenho a 375 nunca são vistos. Um
  "APROVADO" dado sobre essas fotos não prova nada.
- **O que precisa mudar (engenheiro-frontend):** capturar com emulação de dispositivo (CDP `Emulation.setDeviceMetricsOverride`
  com largura 375 e `mobile:true`, como em `scripts/capturar_animacao.mjs`) e com a altura da página inteira. Escrever no topo
  do PNG ou no nome a largura **medida** (`innerWidth`). Falhar se `innerWidth` ≠ largura pedida.

### S1-2 · Faltam os estados carregando, erro, vazio e não encontrado
- **Onde:** não existe `loading.tsx`, `error.tsx`, `global-error.tsx` nem `not-found.tsx` em `web/src/app/` (procurei em todas
  as rotas). Vazios: "próximas publicações" vira lista vazia sem texto (`app/page.tsx` 65–79). "Fora da bolha" some
  (`desempenho/page.tsx` 68, `tot > 0 &&`). `Barras` sem itens desenha uma lista vazia (`components/ui.tsx` 58–80). As tabelas
  de `/videos` ficam só com o cabeçalho (`videos/page.tsx` 44, 74). Erro: `lib/db.ts` 59 lança e nenhuma fronteira o pega.
  `ultimaSincronizacao` (`db.ts` 74–77) ignora o erro, e o cabeçalho (`layout.tsx` 22, 41) diz "sem sincronização — rode
  painel/sync/sincronizar.py", que é o diagnóstico errado quando o banco está fora. Id inexistente (`/equipe/nao-existe`) cai
  no 404 padrão do Next: "This page could not be found.", **em inglês, fundo branco** (conferido por `curl`, HTTP 404).
- **Regra:** `portao-interface.md` §1 ("os três estados existem e foram vistos") e §Classes (S1 = estado faltando).
- **Cenário concreto:** o README do painel já prevê o caso: o Supabase do painel desligado depois de reiniciar o Mac (o Docker
  ainda não subiu). O Carlos abre o painel e, em vez de "o banco do painel está fora do ar — `cd painel && supabase start`",
  vê a tela técnica do Next ("Application error: a server-side exception has occurred…"). O cabeçalho ainda manda rodar o
  sincronizador, que também vai falhar.
- **O que precisa mudar:** **designer-de-produto** desenha os estados (vazio com a frase do que falta, carregando,
  erro com a ação certa, 404 na marca). **engenheiro-frontend** implementa `loading.tsx`, `error.tsx`, `not-found.tsx` e os
  vazios por seção, e faz `ultimaSincronizacao` distinguir "banco fora" de "nunca sincronizou".
- **Como verifiquei:** pelo código e pelo `curl` do 404. **Não** derrubei o banco num servidor de teste (ver "o que não verifiquei").

### S1-3 · Uma leitura `suspeito` entra no gráfico e nas médias de "o que funciona"
- **Onde:** `web/src/app/desempenho/page.tsx` 22 (`ultimaPorVideo` pega a última leitura, suspeita ou não), 27–41 (`grupo` faz a
  média com `m.alcance` sem olhar `m.suspeito`) e 136–141 (barra de alcance da tabela).
- **Medido no banco:** a última leitura do Geoffrey Hinton (`2026-10-22 13:00:07+00`) tem `tempo_medio_s = 1512,69` num vídeo de
  158,68 s, com `suspeito = true`. Mesmo assim é ela que alimenta a barra "11" e as médias "trial (3) 18", "perfil (4) 98" e
  "mais de 90 s (3) 18". A coluna "assistido" mostra "?", o que está certo. **Hoje o número não está errado por coincidência:**
  o alcance dessa leitura (11) é igual ao da leitura boa de 21/10.
- **Regra:** `portao-interface.md` §2 — "leitura `suspeito` não entra em média nem gráfico".
- **Cenário concreto:** a próxima leitura impossível que vier com um alcance também errado muda as médias de "trial × normal",
  que é a seção onde o Carlos decide se publica como trial, sem nada na tela avisar.
- **O que precisa mudar (engenheiro-frontend):** gráfico e médias usam a última leitura **não suspeita** (dizendo a data) ou
  deixam o vídeo de fora e mostram o "n" certo. A linha da tabela diz que a leitura mais recente foi descartada.

### S1-4 · O texto da seção diz "taxas sobre o alcance", e a tabela não tem taxa nenhuma sobre o alcance
- **Onde:** `web/src/app/desempenho/page.tsx` 115, subtítulo de "3. os vídeos": "Taxas sobre o alcance do Instagram."
- **Medido:** a única porcentagem da tabela é o "% assistido" (`pct_medio_assistido` = tempo médio ÷ duração: Demis 11,88 s ÷
  57,84 s = 20,5% → "21%"). Não é taxa sobre o alcance. Salvamentos, compartilhamentos e comentários aparecem como
  **contagens**.
- **Regra:** `portao-interface.md` §2 (número trocado de rótulo). Classifiquei como S1 e não S0 porque o cabeçalho da coluna
  ("assistido") está certo. O erro está no texto de apoio.
- **Cenário concreto:** o Carlos lê "21%" do Demis como "21% de quem foi alcançado" e tira a conclusão errada sobre retenção.
- **O que precisa mudar (engenheiro-frontend):** o subtítulo diz o que a porcentagem é ("% médio do vídeo assistido"). Ou, se a
  designer quiser, a tabela passa a mostrar as taxas de verdade, com a base escrita.

### S1-5 · Texto abaixo do contraste AA, justo no estado dos portões
- **Medido** (fórmula WCAG sobre os tokens de `globals.css`):
  - `tinta-3 #8c887c` sobre `papel #e7e4d9` = **2,78:1**. É a cor do texto dos sinais "ainda não rodou" e "não se aplica"
    (`ui.tsx` 36–37, 49), em 12 px. Hoje isso vale para **55 de 55 sinais** (44 pendentes + 11 não se aplica no banco).
  - `acento #e85002` sobre `papel` = **2,96:1** na etiqueta "portão" de 11 px (`ui.tsx` 84, `/equipe`).
  - `papel` sobre `acento` = **2,96:1** no "60%" de 12 px dentro da barra (`desempenho/page.tsx` 71–73).
  - Para comparar: `tinta-2` sobre `papel` = 5,59:1 (passa).
- **Regra:** `portao-interface.md` §4 — contraste AA no texto (4,5:1 para texto pequeno).
- **Cenário concreto:** no celular, ao sol, o estado dos portões é o texto mais apagado da tela, e é a informação principal
  de `/videos` e das fichas dos gerentes.
- **O que precisa mudar:** **designer-de-produto** escolhe um tom de texto apagado que passe 4,5:1 sobre o papel e decide
  a etiqueta e o rótulo dentro da barra. **engenheiro-frontend** aplica.

### S1-6 · Fonte mono, que a marca proíbe, no bloco que o Carlos copia
- **Onde:** `web/src/app/equipe/contratar/Formulario.tsx` 70: o `<pre>` do "pedido de contratação" aparece na monoespaçada do
  navegador (ver `equipe-contratar-1440.png`). Também os `<code>` em `desempenho/page.tsx` 50–51, `videos/page.tsx` 30 e
  `equipe/[id]/page.tsx` 63.
- **Regra:** `korvu-editorial.md` §3 ("Comando para copiar · Inter 500 · **sem fonte mono** (mono = cara de terminal, o que ele
  não quer)") e §6 ("Proibido: … fonte mono").
- **Cenário concreto:** o bloco que o Carlos copia e cola tem exatamente a "cara de terminal" que ele recusou.
- **O que precisa mudar (engenheiro-frontend):** `pre`/`code` em Inter 500 (o "copie e cole" da marca: fundo `papel-2`, sem
  canto).

### S1-7 · Rótulos de gráfico cortados com reticências
- **Onde:** "cidades alcançadas" (`desempenho/page.tsx` 102 → `ui.tsx` 67, `truncate`). Na tela: "Juiz de Fora, Minas G…",
  "São Paulo, São Paulo …", "Rio de Janeiro, Rio de …", "Belo Horizonte, Minas…" (`desempenho-1440.png`, `desempenho-375-real.png`).
- **Regra:** `portao-interface.md` §2 / `dataviz` — "rótulo nunca cortado".
- **Cenário concreto:** a 375 não há mouse para o `title`, e o nome da cidade fica pela metade no gráfico que mostra para onde
  o conteúdo está indo.
- **O que precisa mudar (engenheiro-frontend):** encurtar o rótulo na tela ("Juiz de Fora · MG"), quebrar linha, ou dar a
  largura que o rótulo precisa.

### S1-8 · Elementos recriados dentro das páginas em vez de virem de `src/components/`
- **Onde:**
  - título de página (h1 `titulo … text-5xl sm:text-6xl` + ponto no acento) copiado em 6 páginas: `app/page.tsx` 25,
    `desempenho/page.tsx` 46, `videos/page.tsx` 25, `equipe/page.tsx` 28, `equipe/[id]/page.tsx` 39, `contratar/page.tsx` 14;
  - botão copiado: `equipe/page.tsx` 31 e `Formulario.tsx` 71 (mesmas classes);
  - gráfico montado dentro da página: barra empilhada + legenda em `desempenho/page.tsx` 70–85 e a barra de alcance da tabela
    em 138 (o `Barras` existe em `ui.tsx`, mas estes não usam nada de lá);
  - `Etapas` definido dentro de `videos/page.tsx` 5–15; cabeçalho de tabela copiado (`videos/page.tsx` 38–40 e 70,
    `desempenho/page.tsx` 121); "← equipe" copiado (`equipe/[id]/page.tsx` 34, `contratar/page.tsx` 13).
- **Regra:** `portao-interface.md` §3 — "Elemento recriado dentro de página em vez de vir de `src/components/` = S1".
- **Cenário concreto:** quando a designer entregar o design, cada mudança de título, botão ou gráfico terá de ser feita em até
  6 lugares, e as telas vão sair diferentes umas das outras.
- **O que precisa mudar (engenheiro-frontend):** `TituloPagina`, `Botao`, `Voltar`, `Tabela`/`Cabecalho`, `BarraEmpilhada` +
  `Legenda`, `BarraNaTabela` e `Etapas` em `src/components/`, e as páginas passam a usá-los.

### S1-9 · `npm audit --omit=dev`: vulnerabilidade **alta** no `postcss` que vem com o Next
- **Medido:** `postcss <= 8.5.22`, severidade **high** (GHSA-qx2v-qp2m-jg93, GHSA-6g55-p6wh-862q, GHSA-fxqj-rqcc-2cmp,
  GHSA-r28c-9q8g-f849), em `node_modules/next/node_modules/postcss`, puxado por `next@15.5.28`. Total: 2 vulnerabilidades
  (1 moderada, 1 alta). O `npm audit fix --force` sobe para `next@16.4.2` (quebra).
- **Por que S1 e não S0-L:** a dependência entrou com o próprio painel (`package-lock.json` de 22/10, 19:12), que esta 1.ª
  auditoria cobre por inteiro. Não é anterior à área nem independente dela. Na prática a exposição é baixa: o postcss roda no
  build e só processa o CSS do próprio painel. Mesmo assim a regra é objetiva.
- **Regra:** `portao-interface.md` §5 — "vulnerabilidade alta/crítica nova trazida por esta tarefa = S1".
- **Cenário concreto:** o painel sobe um dia para um domínio (o README já prevê) com uma dependência conhecida como vulnerável
  e sem nenhum registro de que alguém a viu.
- **O que precisa mudar (engenheiro-frontend):** `overrides` do `postcss` ≥ 8.5.23 no `package.json` (sem trocar o Next),
  rodar `npm audit --omit=dev` limpo e repetir o build. Se isso quebrar o build, a escolha entre o Next 16 e aceitar o risco
  com motivo escrito vira decisão (ESCALADO), e não um aprovado com ressalva.

---

## O que verifiquei e como

1. **Telas olhadas de verdade.** Rodei `bash painel/capturar.sh painel/portoes/capturas-v1` no servidor do Carlos (:3456, antes do
   build) e abri os 12 PNG, 6 rotas × 1440 e 375. Como o "375" do script se mostrou falso (S1-1), medi as 6 rotas com o meu
   próprio Chrome sem janela via CDP, com emulação de dispositivo a 375 e a 1440: `innerWidth`, `scrollWidth` e os elementos
   além da borda (fora de contêiner com rolagem própria). Resultado: **375/375 e 1440/1440 em todas, nenhum elemento além da
   borda**. Abri as 6 capturas reais a 375 (`capturas-v1/*-375-real.png`). Testei as 26 fichas `/equipe/<id>`: todas HTTP 200.
   `/equipe/nao-existe`: 404 do Next.
2. **Dados honestos, da tela até a fonte.** Conferi cada número visível contra o banco (Postgres 127.0.0.1:55322, só `select`) e,
   por amostra, contra o arquivo:
   - Seguidores 3.631 e "−3 desde 16/10" = `perfil_snapshots` 3631 (22/10) − 3634 (16/10). Alcance 529, visualizações 2.448
     ("2,4 mil") e visitas 56 = `_controle/perfil/2026-10-22.json` (janela de 28 dias, 24/09–22/10). "60%" = 307 ÷ (307+206).
   - "Melhor vídeo 338 · demis hassabis" = última leitura do Demis (22/10 13:00:16).
   - Tabela "os vídeos": as 4 linhas batem com a última leitura de cada slug (alcance, views, tempo médio, % assistido, salv.,
     compart., coment., palavra 1/1 e 0/0, FB plays 30/196/4/—). Ordem por alcance correta. Datas no fuso Europe/London (o
     Mac está em BST) corretas: 13/10, 18/10, 15/10, 20/10.
   - "O que funciona": trial (3) = (40+11+4)/3 = 18,3 → 18 · normal (1) = 338 · perfil (4) = 393/4 = 98,25 → 98 ·
     até 90 s (1) = 338 · mais de 90 s (3) = 18. Amostra pequena declarada ("Com 4 vídeos…"), com o "n" de cada grupo.
   - Países, cidades e idade: os 10, 8 e 7 primeiros de `perfil_demografia` (22/10) batem um a um (GW 1741 → "1,7 mil",
     BR 504… · BR 197, GB 58… · 25-34 1218 → "1,2 mil").
   - Fila (início e `/videos`): os 5 `post.json` de `06-publicar/` (só leitura): `publicar_em` com fuso
     (`2026-10-24T19:00:00+01:00` → "sáb., 24/10, 19:00"; 25/10 já em GMT → 19:00), `plataformas: ["instagram"]`, trial
     `MANUAL`, palavra. Tudo bate com a tela, e os 5 aparecem como "legado".
   - Portões: 55 linhas em `portoes_estado` (44 pendentes + 11 não se aplica) = o que `/videos` e as fichas mostram.
     "0 de 10 aprovados" (pauta) = 12 vídeos − 2 "não se aplica".
   - Equipe: "26 pessoas em 6 departamentos" = 26 agentes, 7 departamentos − direção.
3. **Gráficos (skill `dataviz`, invocada).** Validador rodado:
   `node validate_palette.js "#e85002,#5a5852" --mode light --surface "#e7e4d9"` → lightness PASS, CVD PASS (ΔE 12,8), normal-vision
   PASS (ΔE 26), **chroma FAIL** no `#5a5852` e **contraste WARN** do acento (2,96:1). O FAIL é o cinza de des-ênfase da forma
   "emphasis" (choosing-a-form.md: "1 hue + gray"), que é o uso daqui: laranja = alcance/fora da bolha, cinza = quem já segue. Não
   é slot categórico. O WARN está aliviado porque todo valor aparece escrito ao lado da barra. Um eixo só ✓. Legenda na barra de 2
   séries ✓. Gráficos de uma série sem legenda e com título ✓. Texto em tinta, nunca na cor da série ✓. Vão de 2 px entre
   segmentos ✓. Dica ao passar o mouse em toda barra ✓ (no "?" do Hinton a dica abre dentro da caixa da tabela, medido a 1440).
   Rótulo cortado ✗ (S1-7). Leitura suspeita fora de média ✗ (S1-3).
4. **Fiel ao design** (contra `korvu-editorial.md` + dataviz, ver o aviso no topo). Papel, tinta e acento nos tokens ✓. Bricolage
   800 nos títulos em minúsculas com ponto ✓. Inter 400/500/600 ✓. Número de seção no acento ✓. Retrato em P&B ✓. Nenhuma cor
   em hexa ou `rgba(` fora de `globals.css` (`grep` vazio) ✓. Fonte mono ✗ (S1-6). Componentes recriados ✗ (S1-8). Cantos
   arredondados e as cores de estado ficam para decisão da designer (S2).
5. **Acessibilidade.** Contraste calculado para todos os pares de tokens usados em texto (S1-5). Teclado: 14 Tabs em `/videos` e
   `/equipe/contratar` (CDP). Os links, sinais, `select` e botão recebem o contorno de foco do navegador e a dica abre no foco.
   Os campos de texto **não** mostram foco além do cursor (S2, prova em `prova-foco-campo-1440.png`). Árvore de acessibilidade do
   Chrome: a célula do sinal recebe o nome completo ("pauta: ainda não rodou — o portão ainda não rodou"). O estado nunca está
   só na cor: ícone diferente por estado (✓ ✕ ▲ ⌛ ○ —) e palavra. `lang="pt-BR"` ✓.
6. **Segurança e código.** `src/lib/db.ts` começa com `import "server-only"` ✓. Nenhum `NEXT_PUBLIC_` no código, e
   `grep -c "^NEXT_PUBLIC_" web/.env.local` = 0 (só a contagem, sem ler valores) ✓. O único `"use client"` é o
   `Formulario.tsx`, que não importa o banco ✓. **Depois do build:**
   `grep -rl "service_role\|SERVICE_ROLE\|eyJhbGci" painel/web/.next/static` = vazio, e nem "supabase" aparece no bundle do
   cliente ✓. `npx tsc --noEmit` exit 0 ✓. `npx eslint src` exit 0 ✓. `npm run build` exit 0 ✓ (7 rotas dinâmicas, 103 kB de
   JS comum). `npm audit --omit=dev` ✗ (S1-9).

## O que NÃO verifiquei (declarado)

- **Fidelidade ao design aprovado:** não existe (`painel/design/` vazia). Auditei contra a marca e a dataviz. Com o design
  entregue, este item tem de ser refeito.
- **Estados de erro, carregando e vazio em execução:** não derrubei o banco num servidor de teste. Um segundo `next dev` na mesma
  pasta disputaria o `.next/` com o servidor do Carlos. Concluí pela leitura do código (os arquivos não existem) e pelo `curl` do
  404.
- **Navegação no build de produção (`next start`):** o build passou, mas as capturas e as medições foram feitas no servidor de
  desenvolvimento, antes do build.
- **Safari/iOS e leitor de tela real (VoiceOver):** o toque foi emulado no Chrome (CDP `setTouchEmulationEnabled`). O iOS pode
  tratar o `:hover`/`:focus` do toque de outro jeito. A acessibilidade foi lida na árvore do Chrome, não ouvida.
- **Console do navegador:** não li os logs. O indicador do Next ("N") não mostrou nenhum erro em nenhuma das 12 capturas.
- **Desempenho (tempo de carregamento), modo escuro** (o painel não tem e a marca não prevê) e **rotas fora do menu**, além das
  26 fichas e do 404.
- **Banco × arquivos em geral:** é o eixo do PORTÃO-DADOS. Só conferi por amostra (perfil de 22/10, os 5 `post.json`, as
  leituras do banco).
- **O servidor de desenvolvimento em :3456 está fora depois do build** (o `curl` devolve 500). O agente principal precisa
  reiniciá-lo. Não tentei.

## S2 (não bloqueiam) → `_controle/backlog-portoes.md` (PI1–PI16)

| Nº | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|
| PI1 | `web/src/app/globals.css` 63–65 × `Formulario.tsx` 35, 38 | `.fio` fica fora das camadas do Tailwind e por isso vence o `focus:border-tinta` (que está em `@layer utilities`): campo de texto focado fica só com o cursor, sem borda nem contorno (`prova-foco-campo-1440.png`) | engenheiro-frontend | junto com o S1-8 (componente de campo) |
| PI2 | `ui.tsx` 71, `desempenho/page.tsx` 138 | Pontas arredondadas de 4 px nas barras (pedido da dataviz) × marca "nada de canto arredondado" (`korvu-editorial.md` §1, o próprio `globals.css` 4) — decidir e escrever o motivo | designer-de-produto | 1.ª entrega de `painel/design/` |
| PI3 | `globals.css` 15–17 | Cores de estado ok/alerta/erro além de "três cores e só" (com ícone + palavra, como a dataviz manda) — escrever a exceção à marca com motivo | designer-de-produto | 1.ª entrega de `painel/design/` |
| PI4 | `ui.tsx` 9 | Número de seção "1." no acento a 30 px: 2,96:1 (texto grande pede 3:1). É a cor aprovada da marca, por isso fica como decisão | designer-de-produto | 1.ª entrega de `painel/design/` |
| PI5 | `Formulario.tsx` 35, 38, 51, 61 | Contorno dos campos (`fio`) com 1,37:1 sobre o papel e 1,52:1 sobre `papel-3` (WCAG 1.4.11 pede 3:1) | designer-de-produto + engenheiro-frontend | componente de campo |
| PI6 | `desempenho/page.tsx` 94, 106 (`compacto`) | Precisão misturada no mesmo gráfico: "1,7 mil" (1.741) e "1,2 mil" (1.218) ao lado de 504 e 925. O número exato não aparece nem na dica | engenheiro-frontend | próxima mudança em `/desempenho` |
| PI7 | `app/page.tsx` 14–15, 38 · `desempenho/page.tsx` 23–25 | "60% fora da bolha" é sobre 513 (307+206, a quebra da Meta), enquanto o cartão ao lado diz 529 contas. A base não é dita | engenheiro-frontend | próxima mudança em `/desempenho` |
| PI8 | `desempenho/page.tsx` 64 | "visitas ao perfil" sem a janela; os outros cartões dizem "· 28 dias" e o dado é da mesma janela | engenheiro-frontend | próxima mudança em `/desempenho` |
| PI9 | `app/page.tsx` 35 · `desempenho/page.tsx` 62–63 | `compacto(x ?? 0)`: alcance/visualizações nulos aparecem como "0" em vez de "—" | engenheiro-frontend | próxima mudança nos cartões |
| PI10 | `videos/page.tsx` 33, 51 · `lib/formato.ts` 35 | "em produção" lista os 3 publicados; a etapa aparece crua ("edl_aprovada"); títulos tirados do slug sem acento ("15 coisas ia negocio") | designer-de-produto + engenheiro-frontend | 1.ª entrega do design de `/videos` |
| PI11 | `layout.tsx` 30–36 | Menu sem página atual (sem destaque nem `aria-current`) | engenheiro-frontend | componente de menu |
| PI12 | `ui.tsx` 66 | Cada linha de barra é uma parada de Tab (~45 em `/desempenho`) | engenheiro-frontend | próxima mudança no `Barras` |
| PI13 | `Formulario.tsx` 72 | "copiar pedido" usa `navigator.clipboard` sem tratar erro: fora de origem segura (ex.: `http://<IP da rede>:3456` no celular) o botão não faz nada e não avisa | engenheiro-frontend | antes de abrir o painel fora do `localhost` |
| PI14 | `videos/page.tsx` 34–35 (`min-w-[720px]`) | A 375, os sinais dos portões, que são a razão da página, só aparecem rolando a tabela de lado, sem nenhuma indicação | designer-de-produto | 1.ª entrega do design de `/videos` |
| PI15 | `equipe/[id]/page.tsx` 67 · `app/page.tsx` 95 | Ficha dos portões do painel diz "os vídeos que passam por aqui" (o alvo é o painel); "0 de 1 aprovados" | engenheiro-frontend | próxima mudança nas fichas |
| PI16 | `ui.tsx` 47 · `videos/page.tsx` 8 | `aria-label` em `span` sem papel (não é garantido pelo ARIA). Hoje o nome chega pela célula da tabela | engenheiro-frontend | junto com o S1-8 |

## S0-L abertos (lista inteira do backlog)

Nenhum. A tabela "BLOQUEIOS DE PUBLICAÇÃO (S0-L)" de `_controle/backlog-portoes.md` está vazia. Este portão não abriu
nenhum: o S1-9 (postcss) não é S0-L porque a dependência entrou com o próprio painel (ver o achado).

## Provas

`painel/portoes/capturas-v1/`:
- `*-1440.png` e `*-375.png`: saída do `capturar.sh` (o 375 é falso, S1-1).
- `*-375-real.png`: emulação de dispositivo a 375.
- `prova-toque-sinal-375.png` (S0-1) e `prova-foco-campo-1440.png` (PI1).
