PORTÃO-INTERFACE: BLOQUEADO — sobre aae5d7867e7f (volta 2)

# PORTÃO-INTERFACE · painel · 22/10/2026 (madrugada de 23/10) · volta 2

- **Alvo:** `painel` · **portão:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão congelada no passo 0:** `aae5d7867e7f` (29 arquivos: `capturar.sh`, configs do `web/` e 22 arquivos em `web/src/**`).
  Era `4f50595fb2a3` (21 arquivos) na volta 1. Conferi de novo depois dos servidores de teste e depois do build: continua
  `aae5d7867e7f`.
- **Estado antes:** `interface · bloqueado` (volta 1, 23:45, S0 1 · S1 9). Relatório anterior relido item por item (abaixo).
- **Resultado:** S0 = 1 · S1 = 1 · S2 = 8 (7 S2 novos + 1 S1-L) → **BLOQUEADO**.
- **Linha de base aplicada** (`docs/gauntlet.md`): o S1-8 da volta 1 (elementos recriados nas páginas) **não foi corrigido**.
  Como o redesign decidido em 22/10 (`docs/decisoes.md` §5, departamento de tecnologia: design system e maquetes em
  `painel/design/` e depois a implementação) vai substituir títulos, botões, tabelas e gráficos, ele vira **S1-L (PI-L1)**:
  vai para o backlog e conta em `--s2`. Foi o único S1 reclassificado assim.

> **Contra o que a fidelidade foi medida:** `painel/design/` continua **vazia**, então não há design aprovado. Medi de novo
> contra `00-marca/design-system/korvu-editorial.md` e contra as regras da skill `dataviz`, que invoquei. Quando a designer
> entregar, o item "fiel ao design" tem de ser refeito contra a entrega dela.

---

## A volta 1 foi corrigida? (item por item, conferido no ponto do defeito)

| Volta 1 | Estado | Como conferi |
|---|---|---|
| **S0-1** motivo do portão cortado no celular / rolagem lateral | ✅ **corrigido** | Chrome via CDP com toque emulado a 375. Toquei o sinal de `/equipe/portao-interface` com o motivo real e a dica ficou em x 8…360 (`prova-toque-sinal-real-375.png`). Troquei o texto por um motivo de 5 arquivos no formato do `portoes.py`: a dica ficou em x 8…360, quebrando linha, com `scrollWidth` 375 aberta **e** fechada (`prova-toque-sinal-longo-375.png`). Num sinal da última coluna de `/videos`, com a tabela rolada até o fim, a dica ficou em x 15…367 (`prova-toque-sinal-tabela-375.png`). Ela acompanha a rolagem da página e fecha ao tocar fora. A 1440, com o mouse, abre em x 1044…1396 e fecha quando o mouse sai (`prova-mouse-sinal-1440.png`). Pelo teclado, Tab abre a dica com contorno de foco e Esc fecha (`prova-teclado-sinal-1440.png`). |
| **S1-1** `capturar.sh` sem emulação / página cortada em 2400 px | ✅ **corrigido** | Rodei o script atual: `innerWidth` medido = 375 e 1440 nas 9 rotas, PNG da página inteira (`equipe-375.png` tem 4096 px e a última fatia mostra o rodapé). O script **recusa** quando a largura não bate: a 320 px, `/desempenho` abriu com 323 e ele não gravou a foto (ver PI24). |
| **S1-2** estados carregando / erro / vazio / 404 | ✅ **corrigido** | Vistos **rodando** num servidor meu (`PAINEL_DIST=.next-trabalho … next dev -p 3457`) ligado a um Supabase de mentira que eu controlava. **Vazio:** cada seção diz o que falta e o comando (`estado-vazio/`). **Carregando:** proxy com 8 s de atraso, esqueleto e "lendo o banco do painel…" no topo (`estado-carregando/`). **Fora do ar:** com a conexão derrubada e com a porta morta de verdade (ECONNREFUSED), aparece "não consegui ler os dados" com os passos certos, e o topo diz "banco do painel fora do ar" (`estado-fora/`, `estado-porta-morta/`). Uma ficha inexistente com o banco fora cai no **erro**, não no 404. **Erro da API** (tabela em falta) em `estado-erro/` (ver PI19). O botão "tentar de novo", clicado depois de o banco voltar, carrega a página e atualiza o topo. **404** na marca, em PT-BR (`pagina-que-nao-existe-*.png`, `equipe-nao-existe-*.png`), com o detalhe do PI17. |
| **S1-3** leitura `suspeito` no gráfico e nas médias | ✅ **corrigido** | `lib/db.ts` `leiturasConfiaveis`. No banco, a última leitura do Hinton (22/10 13:00) tem `suspeito = true`. A tela usa a de 21/10 (alcance 11, views 11, 43,96 s → "44 s · 28%") e avisa "▲ leitura de 22/10 descartada: tempo médio de 1.512,7 s num vídeo de 158,7 s (impossível). Valem os números de 21/10". Os mesmos números estão no arquivo `07-publicados/2026-10-20-geoffrey-hinton/metricas.json` (reach 11, views 11, avg_watch_time 43960 ms). Médias: trial (3) = (40+11+4)/3 = 18 · perfil (4) = 393/4 = 98. |
| **S1-4** "taxas sobre o alcance" | ✅ **corrigido** | O subtítulo agora diz o que o "assistido" é e que "não é uma taxa sobre o alcance" (`desempenho-1440.png`). |
| **S1-5** contraste abaixo de AA | ✅ **corrigido** | Varri **todo nó de texto** das 7 rotas a 1440, com a cor efetiva sobre o fundo efetivo. O único par abaixo do mínimo é o acento em texto grande (o "." dos títulos e os números de seção, 2,96:1), que já é o PI4 (decisão da marca). `tinta-3 #67635a` sobre o papel = 4,70:1. "60%" agora em tinta sobre o acento, e passa. Etiqueta "portão" agora em tinta com fio no acento. |
| **S1-6** fonte mono | ✅ **corrigido** | Estilo calculado: `pre` e `code` em "Inter, Inter Fallback" 500. `CSS.getPlatformFontsForNode` do `pre`: Inter em 596 glifos (Arial só em 2, as setas). O bloco de copiar vem de `components/CopieECole.tsx`. |
| **S1-7** rótulos cortados com reticências | ✅ **corrigido** | `formato.cidade`: "Juiz de Fora · MG", "London · England", "Cintra · Lisbon". `Barras` quebra a linha em vez de cortar. O nome inteiro aparece na dica. Visto a 1440 e a 375. |
| **S1-8** elementos recriados nas páginas | ❌ **não corrigido** → **S1-L (PI-L1)** | `TituloPagina` existe, mas só os estados (erro, erro geral, 404) o usam. As 6 páginas continuam a recriar o h1. O botão agora está copiado em **4** lugares (eram 2). `Etapas`, os cabeçalhos de tabela, a barra empilhada com a legenda e a barra da tabela continuam montados dentro das páginas. Detalhe em PI-L1. |
| **S1-9** postcss vulnerável | ✅ **corrigido** | `overrides.postcss = 8.5.31`. `npm ls postcss` → 8.5.31 em todos os lugares. `npm audit --omit=dev` → **0 vulnerabilidades**. O build passou. |

---

## Achados que bloqueiam

### S0-1 · "4 de 4 vídeos publicados" — são 5, e o mais novo some da tabela sem aviso
- **Onde:** `web/src/app/desempenho/page.tsx` 188–190, subtítulo de "4. o que funciona":
  `` `${comLeitura} de ${linhas.length} vídeos publicados têm leitura válida` ``. `linhas` = tabela `publicacoes`.
  Também o subtítulo de "3. os vídeos" (127, "Última leitura válida de cada Reel publicado") e o vazio da linha 130
  ("Nenhum Reel publicado em 07-publicados ainda").
- **Medido:** na tela (`desempenho-1440.png`) aparece "4 de 4 vídeos publicados têm leitura válida". Em `07-publicados/` há
  **5** pastas, e `07-publicados/2026-10-23-livro-chatgpt-a/post.json` tem `estado: publicado` e `publicado_em:
  2026-10-22T21:19:22+01:00`. O banco tem 4 linhas em `publicacoes`, porque o sincronizador só cria a linha depois do 1.º
  `metricas.json` (PD7, do PORTÃO-DADOS). A tabela "os vídeos" lista 4 Reels e não diz que falta o livro A.
- **Regra:** `portao-interface.md` §2: "número … trocado de rótulo … ou calculado errado = S0". Contar "publicações com leitura"
  e chamar de "vídeos publicados" é trocar o rótulo. O PD7 tinha como gatilho "antes de o painel ter um número
  'publicados'", e esta volta criou exatamente esse número.
- **Cenário concreto:** o Carlos publicou o livro A ontem às 21:00. Abre o desempenho e lê que todos os 4 vídeos publicados já
  têm leitura, e a tabela de "cada Reel publicado" não tem o livro. Ele conclui que o livro não saiu ou que não está a ser
  medido. Daqui a 5 dias o denominador "salta" para 5 sem explicação. Se um dia só houver Reels publicados há menos de
  5 dias, a seção diz "Nenhum Reel publicado em 07-publicados ainda", o que é falso.
- **O que precisa mudar:** **engenheiro-frontend**: o texto não afirma total de publicados a partir de `publicacoes`
  (ex.: "4 vídeos com leitura válida; Reels publicados há menos de 5 dias ainda não têm leitura"), e o vazio da seção diz a
  mesma coisa. Para a tabela listar o livro A como "aguardando a 1.ª leitura" é preciso fechar o **PD7**
  (**engenheiro-backend**, auditado pelo PORTÃO-DADOS). Na volta 3, confiro na tela o número contra `ls 07-publicados/`.

### S1-1 · O painel lê as tabelas inteiras sem paginar e o banco corta em 1.000 linhas: na 6.ª foto do perfil, o desempenho passa a mentir
- **Onde:** `web/src/lib/db.ts` 65–74 (`todos()` faz `select("*")` sem `.range()` nem `count`) e 85
  (`demografia = () => todos("perfil_demografia")`, sem filtro e sem ordem). O limite está em `painel/supabase/config.toml:18`
  (`max_rows = 1000`) e no contêiner que roda (`supabase_rest_content-ai-painel`: `PGRST_DB_MAX_ROWS=1000`, conferido
  com `docker inspect`, filtrando só essa variável).
- **Medido:** `perfil_demografia` já tem **330** linhas com 2 fotos do perfil (148 na de 16/10, 182 na de 22/10). O PostgREST
  devolve no máximo 1.000 linhas, **com HTTP 200 e sem erro**. O sincronizador grava as fotos em ordem de data
  (`sync/sincronizar.py:259`, `sorted(...glob("*.json"))`) e, dentro de cada foto, primeiro "seguidores" e depois "alcançados"
  (país 27 → cidade 45 → idade 7 → gênero 3). Na 6.ª foto (148 + 5×182 = 1.058 linhas), as 58 que somem são as últimas
  gravadas, ou seja, as da foto mais nova: todas as **cidades alcançadas**, a idade e o gênero dos alcançados e 3 países.
  Na 7.ª foto some também parte de "quem segue". `metricas` (10 linhas, ordem crescente) e `veredictos` têm o mesmo
  defeito, mais longe do limite, e o que cortariam seriam as leituras **mais novas**.
- **Regra:** `portao-interface.md` §2 (o número tem de ser o que o banco tem). É S1 e não S0 porque hoje nenhum número está
  errado: todos os países, cidades e idades batem um a um com o banco (ver abaixo). O defeito está no código desta área e
  o próximo passo já decidido o dispara: `perfil.py` diário (`_controle/CONTINUAR.md` 0j, "Próximo"). Não é S1-L: o redesign
  muda a tela, não a leitura do banco.
- **Cenário concreto:** o `perfil.py` passa a rodar todo dia. Quatro dias depois o Carlos abre `/desempenho` e lê "A última
  foto do perfil (dd/mm) não trouxe as cidades alcançadas". É falso: a foto trouxe 45 cidades, e o banco as tem. A
  frase vem do vazio de `desempenho/page.tsx:38`. No dia seguinte "quem os vídeos alcançam" perde países e a idade de
  quem segue some, sem nenhum aviso.
- **O que precisa mudar (engenheiro-frontend):** nenhuma leitura de tabela inteira sem limite. `perfil_demografia` filtrada no
  servidor pela foto mais nova (`.eq("lido_em", ultima)`, a única que a tela usa). As outras tabelas são lidas paginando com
  `.range()` até acabar, ou com `count: "exact"`, e a tela de erro aparece se vierem menos linhas do que o banco tem.
  Junto com o **engenheiro-backend**: um teste no `painel_teste` com mais de 1.000 linhas que prove isso. O PORTÃO-DADOS
  fica avisado do `max_rows`.
- **Não reproduzido com mais de 1.000 linhas:** não escrevo no banco do Carlos. A prova é o limite configurado e ativo no
  contêiner, o código sem paginação e a ordem de gravação do sincronizador.

---

## O que verifiquei e como

1. **Telas olhadas de verdade.** `bash painel/capturar.sh painel/portoes/capturas-aae5d7867e7f` no preview do Carlos (:3456,
   só leitura), com 9 rotas × 1440/375 e fatias: `/`, `/equipe`, `/equipe/portao-imagem`, `/equipe/portao-interface`,
   `/equipe/contratar`, `/videos`, `/desempenho`, `/equipe/nao-existe` e `/pagina-que-nao-existe`. Abri as 18 páginas
   inteiras e as fatias de que precisei. Medido: `innerWidth` = largura pedida e `scrollWidth` = janela em todas, nenhum
   elemento além da borda fora de tabela com rolagem própria, nenhum texto cortado ou sobreposto, sem erro na tela (o
   indicador do Next não acusou nada no :3456). A 320 px (reflow, `reflow-320/`), 5 rotas passam e `/desempenho` passa 3 px
   da borda (PI24).
2. **Estados rodando** num servidor meu na :3457 (`PAINEL_DIST=.next-trabalho`, nunca a `.next` do Carlos) contra um Supabase
   de mentira com os modos vazio, lento, erro, conexão derrubada e porta morta. Detalhe na tabela da volta 1. Desliguei o
   servidor e apaguei a `.next-trabalho` no fim. O preview do Carlos respondeu 200 antes, durante e depois.
3. **Dados honestos, da tela até a fonte** (Postgres 127.0.0.1:55322, conexão `read_only`, só `select`, e arquivos só lidos):
   - Seguidores 3.631 e "−3 desde 16/10" (3631 − 3634). Visualizações 2.448 → "2,4 mil". Contas alcançadas 529.
     Visitas 56. FB 0, igual ao banco e ao `CONTINUAR.md` ("Página FB com 0 seguidores"). Fora da bolha 307/(307+206) =
     59,8% → "60%", e 40%.
   - Tabela "os vídeos", número a número com a última leitura **não suspeita** de cada slug: Demis 338 · 450 · 11,88 s →
     "11,9 s · 21%" · 1 · 1 · 2 · 1/1 · FB 30. Fei-Fei 40 · 45 · "9,1 s · 5%" · FB 196. Hinton (21/10) 11 · 11 · "44 s · 28%"
     · FB 4. Fei-Fei A 4 · 8 · "2,6 s · 2%" · FB "—". Datas de publicação em Europe/London corretas (13/10, 18/10, 15/10,
     20/10). "Melhor vídeo 338 · demis hassabis · leitura de 22/10" ✓.
   - "O que funciona": normal (1) 338 · trial (3) 18 · perfil (4) 98 · até 90 s (1) 338 · mais de 90 s (3) 18 ✓. O
     denominador "de 4 publicados" ✗ (S0-1).
   - Países, cidades e idades da foto de 22/10, um a um: GW 1.741 → "1,7 mil", BR 504, PT 230 … FR 29 · BR 197, GB 58, PT 52,
     GW 22, FR 8, AO 6, DE 5, US 4, CH 3, LU 2 (empate, PI18) · Juiz de Fora 29 … Belo Horizonte 7 · 13-17 15 … 65+ 52 ✓.
   - Fila: os 5 `post.json` de `06-publicar/`, só lidos. Horário com fuso (24/10 19:00 BST e 25/10 em diante GMT), só
     Instagram, trial MANUAL × normal, palavra e "legado": tudo bate com o início e com `/videos`.
   - Portões: 56 linhas em `portoes_estado`. "0 de 12" no roteiro, "0 de 10" na pauta e na imagem, "0 de 5" no corte e na
     publicação, "0 de 1" para Camila e Sérgio (na hora das fotos). Equipe: 26 agentes (25 arquivos + Atlas) em
     6 departamentos fora a direção ✓. Topo "sincronizado sex., 23/10, 00:11" = `sincronizacoes` 23:11:52 UTC (BST) ✓.
4. **Gráficos (skill `dataviz`, invocada).** Rodei o validador `node validate_palette.js "#e85002,#5a5852" --mode light
   --surface "#e7e4d9"`. Resultado: lightness PASS · CVD PASS (ΔE 12,8) · normal-vision PASS (ΔE 26) · **chroma FAIL** no
   `#5a5852` · **contraste WARN** no acento (2,96:1). Leio como na volta 1: o cinza é o "de-ênfase" da forma "1 hue + gray"
   (laranja = alcance/fora da bolha, cinza = quem já segue), não um slot categórico, e o WARN está aliviado porque todo valor
   está escrito ao lado da barra. Um eixo ✓. Legenda na barra de 2 séries ✓. Série única sem legenda, com título ✓. Texto em
   tinta, nunca na cor da série ✓. Vão de 2 px ✓. Dica ao passar o mouse, ao tocar e ao focar ✓. Rótulo inteiro ✓. Leitura
   suspeita fora ✓. Proporção da barra empilhada em casos extremos: PI23.
5. **Fiel ao design** (marca + dataviz, ver o aviso no topo). Nenhuma cor em hexa ou `rgba(` fora de `globals.css`
   (`grep` vazio) ✓. Fonte mono eliminada ✓. Tokens, Bricolage 800 em minúsculas com ponto, Inter ✓. Componentes recriados ✗
   → PI-L1 (S1-L).
6. **Acessibilidade** (skill `design:accessibility-review`, invocada, como checklist). Contraste de todo o texto por varredura
   (item 1.4.3, acima). Teclado em `/equipe/contratar`: a ordem é logo → menu → voltar → campos → selects → botão. Links,
   selects, botão e sinais mostram o contorno de foco. **Os campos de texto não mostram foco** (outline none, borda
   continua no `fio`): é o PI1, ainda aberto. Esc fecha a dica (1.4.13) ✓. Os landmarks `header`/`nav`/`main`/`footer`
   existem. Estado nunca só na cor: ícone diferente + palavra ✓. `lang="pt-BR"` ✓. Reflow a 320: PI24.
7. **Segurança e código.** `npx tsc --noEmit` exit 0 · `npx eslint src` exit 0 · `PAINEL_DIST=.next-verificacao npm run build`
   exit 0 (BUILD_ID 00:29, 7 rotas dinâmicas, 103 kB de JS comum). `grep -rlE "service_role|SERVICE_ROLE|eyJhbGci|sb_secret_"
   .next-verificacao/static` **vazio**. `sb_publishable_` também ausente. "supabase" aparece no cliente só no texto
   "cd painel && supabase start" das telas de erro. `src/lib/db.ts` começa com `import "server-only"`. Nenhum `NEXT_PUBLIC_`
   no código. Os 4 `"use client"` (`error`, `global-error`, `Formulario`, `Dicas`) não importam o banco.
   `npm audit --omit=dev`: 0 vulnerabilidades.

## O que NÃO verifiquei (declarado)

- **Fidelidade a um design aprovado:** não existe (`painel/design/` vazia).
- **Corte por `max_rows` com mais de 1.000 linhas de verdade:** não escrevo no banco do Carlos (S1-1 provado pela configuração
  ativa e pelo código).
- **Build de produção servido (`next start`):** o build passou, mas as telas foram vistas no `next dev`. Em produção o Next
  esconde a mensagem do erro, e o `error.tsx` cai sempre no texto genérico, que traz os mesmos passos. Isso foi só lido no
  código.
- **Safari/iOS real e leitor de tela real (VoiceOver):** toque e teclado emulados no Chrome. Os nomes acessíveis foram lidos
  no DOM, não ouvidos.
- **`.env.local`:** não li nem contei as linhas. A ausência de `NEXT_PUBLIC_` foi conferida no código e no bundle.
- **Banco × arquivos em geral:** é o eixo do PORTÃO-DADOS. Só conferi por amostra: os 5 `post.json`, o `metricas.json` do
  Hinton, o perfil de 22/10 via banco e as pastas de `07-publicados/`.
- **Efeito colateral do build:** o `npm run build` reescreveu `painel/web/next-env.d.ts` (gerado, fora da impressão, no
  `.gitignore`) para apontar para `.next-verificacao/types`. O `next dev` do Carlos volta a gravá-lo quando reiniciar. Não
  mexi nele.
- Desempenho (tempo de carregamento), modo escuro (o painel não tem e a marca não prevê).

## S2 e S1-L (não bloqueiam) → `_controle/backlog-portoes.md`

| Nº | Classe | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|---|
| PI-L1 | **S1-L** (linha de base) | `app/page.tsx:29`, `desempenho/page.tsx:55`, `videos/page.tsx:25`, `equipe/page.tsx:28`, `equipe/[id]/page.tsx:40`, `contratar/page.tsx:14` (h1) · `equipe/page.tsx:31`, `Formulario.tsx:71`, `error.tsx:37`, `global-error.tsx:21` (botão) · `equipe/[id]/page.tsx:35`, `contratar/page.tsx:13` (voltar) · `videos/page.tsx:5–15` (`Etapas`) · `videos/page.tsx:41–43,77`, `desempenho/page.tsx:139` (cabeçalho de tabela) · `desempenho/page.tsx:81–97,167` (barra empilhada, legenda, barra na tabela) | S1-8 da volta 1 não corrigido: `TituloPagina` existe e as páginas não o usam; o botão passou de 2 para 4 cópias | engenheiro-frontend (+ designer-de-produto define os componentes) | implementação do redesign aprovado (`painel/design/`) — antes de ele chegar ao Carlos |
| PI17 | S2 | `app/equipe/[id]/page.tsx:17` + `app/loading.tsx` | Ficha inexistente mostra "não achei esta página" mas responde **HTTP 200** (o `loading.tsx` abre o streaming antes do `notFound()`). Rota fora do app responde 404 | engenheiro-frontend | antes de subir o painel para um domínio |
| PI18 | S2 | `desempenho/page.tsx:7–14` (`top`) | Empate no corte do top 10: "Luxemburgo 2" foi escolhido entre 6 países com 2 (CV, IT, MZ, ES, NL), sem aviso | engenheiro-frontend + designer-de-produto | redesign de `/desempenho` |
| PI19 | S2 | `app/error.tsx:16–34`, `layout.tsx:34–35` | Banco que responde com erro (tabela em falta = migração não aplicada): os passos mandam ligar o banco e sincronizar, o que não resolve, e o topo mostra a mensagem da API em inglês (`estado-erro/`) | engenheiro-frontend | próxima mudança nos estados |
| PI20 | S2 | `equipe/contratar/page.tsx`, `Formulario.tsx:51–54` | Com o banco vazio, o select de departamento fica vazio e o pedido sai com "Departamento: ? — … portão ?", sem estado vazio (`estado-vazio/equipe-contratar-1440.png`) | engenheiro-frontend | próxima mudança no contratar |
| PI21 | S2 | `Formulario.tsx:35–39` | Placeholder (50% da tinta, padrão do Tailwind) com 3,4:1 sobre `papel-3`. Os rótulos existem | designer-de-produto + engenheiro-frontend | componente de campo (com PI1/PI5) |
| PI22 | S2 | `equipe/[id]/page.tsx:51` | "o que faz" mostra as crases do markdown dos agentes cruas ("\`design\`", "\`interface\`") | engenheiro-frontend | próxima mudança nas fichas |
| PI23 | S2 | `desempenho/page.tsx:81–93` | Barra empilhada: os segmentos são flex com `min-width` automático. Quando um lado ficar abaixo de ~10% (rótulo + padding ≈ 34 px a 375), a barra deixa de ser proporcional. Há focáveis (`tabIndex`) dentro de `role="img"` | engenheiro-frontend | redesign de `/desempenho` |
| PI24 | S2 | `desempenho/page.tsx:55` (h1 `text-5xl`) | A 320 px, "desempenho." passa 3 px da janela (o ponto no acento) e o celular afasta o zoom (`capturar.sh` recusou a foto: `innerWidth` 323) | designer-de-produto + engenheiro-frontend | redesign (tipografia dos títulos) |

**Da volta 1, conferidos agora:** PI9 (nulo como "0") **fechado**: os cartões mostram "—" (visto no estado vazio). PI15 está
**parcial**: o subtítulo ficou genérico, mas o "0 de 1 aprovados" continua. PI6 está **parcial**: o número exato vai para a
dica, mas a barra ainda mostra "1,7 mil" ao lado de "504". Continuam abertos, como estavam: PI1, PI2, PI3, PI4, PI5, PI7,
PI8, PI10, PI11, PI12, PI13, PI14 e PI16.

## S0-L abertos (lista inteira do backlog)

Nenhum. A tabela "BLOQUEIOS DE PUBLICAÇÃO (S0-L)" de `_controle/backlog-portoes.md` está vazia, e este portão não abriu nenhum.

## Provas

`painel/portoes/capturas-aae5d7867e7f/`:
- `*-1440.png`, `*-375.png` (+ fatias `-pN`) e `medidas.txt`: o `capturar.sh` atual sobre o preview do Carlos.
- `prova-toque-sinal-real-375.png`, `prova-toque-sinal-longo-375.png`, `prova-toque-sinal-tabela-375.png`, `prova-mouse-sinal-1440.png`,
  `prova-teclado-sinal-1440.png`: dica do portão (S0-1 da volta 1).
- `estado-vazio/`, `estado-carregando/`, `estado-fora/`, `estado-porta-morta/`, `estado-erro/`: os estados no meu servidor de teste.
- `reflow-320/`: 320 px.
