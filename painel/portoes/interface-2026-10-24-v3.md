PORTÃO-INTERFACE: APROVADO — sobre 1f444d78dc16 (volta 1)

# PORTÃO-INTERFACE · painel · 24/10/2026 · estados preenchidos com os dados novos do banco · ciclo novo, volta 1

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão:** `1f444d78dc16` (150 arquivos), congelada antes de ler e conferida de novo antes do registro.
- **Ciclo novo:** o APROVADO de 06:00 (`f8729aa1ee1a`) venceu. Desde ele mudaram exatamente os 12 arquivos declarados e
  nenhum foi criado ou apagado.
- **Placar:** S0 0 · S1 0 · S2 3 (2 novos + o S1-L PI-L1). Nenhum S0-L.
- **Capturas:** `painel/portoes/capturas-1f444d78dc16/`
  - as 7 telas a 1440 e 375, com fatias;
  - `cal-semana-1nov.png`;
  - `estado-{fora,vazio,lento}-{producao,calendario,biblioteca}-{1440,375}.png`.

## O que verifiquei e como

### Código e segurança
- `tsc` exit 0 · `eslint` exit 0.
- Build em `.next-verificacao` exit 0 (BUILD_ID `ceyl6ckMncDyv_5WmKuXk`).
- `grep` de chaves no `static` vazio; nenhum `NEXT_PUBLIC_`; `npm audit` 0; nenhuma cor crua.
- **`toques_links_perfil` não aparece** em lugar nenhum de `src/`: nem `toques_links`, nem `profile_links`.

### Produção · Roteiros contra o banco
Consultas só de leitura, sincronização das 07:43.

**Colunas novas**
- Versão, palavra, PDF, cenas extras e gravação prevista vêm de `videos.roteiro_versao`, `cta_palavra`, `roteiro_extras` e
  `gravacao_prevista`. Os 8 batem:
  - ChatGPT contexto v4 · 0 de 1;
  - Jacob Coxon v3 · 2 de 2;
  - Jensen v1 · Nenhuma;
  - Foto da loja v1 · 5 de 20;
  - Golpes v2 · 4 de 6;
  - 15 coisas v1 · 5 de 6;
  - Agente v1 · 3 de 9;
  - Comando secreto v2 · 0 de 9.
- Meta da fase: "6 com PDF".

**CTA de seguir**
- O ChatGPT contexto agora sai "sem palavra (CTA seguir)", e na volta anterior saía "PROMPT".
- **O novo é o certo.** O `roteiro.json` v4 tem `cta_tipo: seguir` e `cta_palavra` vazia. O próprio `roteiro.md` diz "Sem
  cta_palavra e sem material: o vídeo não promete mais o guia de prompt". O "PROMPT" vinha do `videos.cta` antigo do
  `status.json`.
- Jacob Coxon também é CTA de seguir.

**Pedidos da coordenação**
- **"Gravado" do Hassabis e do Hinton depois do apagamento:** `videos.gravado = t` nos dois, com 10 e 9 arquivos, todos
  `gravacao_arquivados` no HD e 0 no Mac. Eles continuam fora de Roteiros e Gravados; estão em Publicados e Agendados como
  antes.
- **Nome curto continua pela `GRAFIA`:** sai "Jacob Coxon". A coluna `videos.nome_curto` existe, mas traz o tema ("Pesquisador
  sai da Anthropic…"), e o app não a usa.

**Prontos**
- A tabela `prontos` tem 0 linhas e a tela mostra "Nenhum pacote pronto".
- Com linhas: só li o código (`Tabelas.tsx`). Duração e "pacote criado" vêm de `prontoDe(slug)`; a palavra vem do pacote.

### Calendário · vagas
- `calendario_vagas` = dom 19:00, ter 21:00 e qua 21:00, todas em `Europe/London`.
- **Mês:** "Vaga livre 21:00" em 3/11 e 4/11. 25/10, 27/10, 28/10 e 1/11 já têm post, então não mostram vaga.
- **Semana de 1–7 nov:** Ter 3 e Qua 4 com "Vaga livre 21:00".
- Legenda "Vaga livre" tracejada.
- Na Semana, a capa do L01C A apareceu em branco na primeira foto. Esperei mais: a imagem estava só carregando
  (`complete`, 200 px), não é defeito.

### Biblioteca · "no Mac" e "no HD externo"
- `sum(gravacao_bytes_no_mac)` = 117.045.314.891 → "**117,0 GB** no Mac".
- `sum(gravacao_arquivados_bytes)` = 99.199.256.718 → "**99,20 GB** de originais no HD externo".
- Os dois números estão certos. As casas decimais diferentes vêm de uma regra só do `bytesPartes`: 2 casas abaixo de 100 GB,
  1 casa acima. Na mesma frase, porém, o Carlos lê precisões diferentes (S2 PI67).
- Soma: 216,2 GB, igual à volta anterior.

### PI65 (fechado)
- **(a)** A frase do vazio agora é por tipo: Áudio fala das músicas, e a busca sem resultado tem frase própria.
- **(b)** O vazio de "Por vídeo" diz "as maiores pastas aparecem aqui".
- **(c)** O texto de exemplo virou "Buscar materiais, vídeos, imagens…" e cabe a 375 (`biblioteca-375-p1.png`).

### Estados desta rodada (vistos rodando no meu servidor, Produção, Calendário e Biblioteca, a 1440 e 375)
- **Erro:** banco fora do ar; nota no topo e 5, 3 e 6 blocos com "Tentar de novo".
- **Vazio:** servidor que imita o banco vazio; "Nada em produção", "Nenhum roteiro esperando", "Nada programado neste mês",
  "Fila vazia", "Nenhum material ainda", "Pasta vazia".
- **Carregando:** `role=status` por bloco (4, 2 e 4).
- `scrollWidth` igual à janela em todos.

### Regressão nas 7 telas
- 14 capturas sem rolagem lateral.
- Detector de texto cortado em 7 larguras: só os casos conhecidos do design (PI41, PI53 (design) e PI52 (design)), todos com
  `title`.
- Auditoria de acessibilidade pelo DOM e console: iguais às voltas anteriores. A Biblioteca não tem nada sem nome, sem `alt`
  ou com id repetido.

## O que NÃO verifiquei (declarado)
- **Prontos com linhas:** a tabela está vazia hoje; só li o código.
- **Vaga em outro fuso:** as 3 vagas são de Londres.
  - Pelo código (`calendario/page.tsx:35–38`), a vaga de outro fuso aparece no dia da semana dela, com o fuso escrito ao
    lado, sem converter para a hora de Londres.
  - Não testei com uma vaga de verdade.
- **Leitor de tela de verdade, Safari, 320 px e a janela de preview do app Claude.**
- **Banco × disco:** é do PORTÃO-DADOS, aprovado às 07:41.
- **As capturas do front-end:** não usei como prova.
- **Efeitos colaterais meus:**
  - refiz a `.next-verificacao`;
  - o `next dev` regravou o `next-env.d.ts`;
  - derrubei os meus servidores.

## Backlog (só acrescentado)
| Nº | Classe | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|---|
| PI67 | S2 | `src/lib/formato.ts:245–253` (`bytesPartes`) + `biblioteca/_componentes/Lado.tsx:65–66` | "117,0 GB no Mac, e mais 99,20 GB… no HD externo": duas precisões na mesma frase. A regra está certa e os números também. Basta mostrar os dois com o mesmo número de casas nessa frase | engenheiro-frontend | próxima mudança na Biblioteca |
| PI68 | S2 | `producao/_componentes/Tabelas.tsx` (Prontos) e `calendario/page.tsx:41,95,133` | Três casos de borda. (a) O chip "QA aprovado" é fixo, embora a tabela `prontos` tenha `qa`. (b) `lerVagas` engole o erro do banco e devolve `[]`: as vagas somem sem aviso. (c) A vaga de outro fuso não é convertida para a hora de Londres (só ganha o fuso escrito). Hoje nada disso acontece: 0 prontos, 3 vagas de Londres | engenheiro-frontend | antes do 1.º pronto novo ou de uma vaga fora de Londres |
| PI65 (fecho) | — | Biblioteca | Frase do vazio por tipo, texto de "Por vídeo" e o exemplo da busca a 375 | — | ✅ 24/10 |
| PI-L1 | S1-L (continua) | ficha e Contratar | Sem desenho aprovado | engenheiro-frontend | quando houver desenho |

## S0-L abertos
Nenhum.

## Para o agente principal
- As três áreas agora estão aprovadas: **design ✅, interface ✅ (esta) e dados ✅ (07:41)**.
- Pela regra 13 do `CLAUDE.md`, rode `uv run python scripts/portoes.py exigir painel` antes de mostrar ao Carlos.
