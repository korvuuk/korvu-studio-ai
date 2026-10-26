# Biblioteca — `/biblioteca` (acervo de estilos, 24/10)

> **O Carlos abre isto para** escolher o estilo do próximo vídeo — o look de cor, a capa, a legenda, a fonte, a animação —
> vendo cada um aplicado a ele, e para saber quanto espaço o estúdio ocupa e o que faz ele rodar.

- Maquete: `biblioteca.html`. **Fonte do desenho (aprovada pelo Carlos em 24/10):**
  `painel/referencias/claude-design/biblioteca-2026-10-24/Biblioteca.dc.html` + `LEIA-ME.md` (origem de cada imagem).
- Decisão de 24/10 (`docs/decisoes.md` §5): a Biblioteca é o **acervo de estilos**, não arquivo de material. **Saem** PDFs,
  vídeos gerados, trechos do YouTube, dossiês, "recentes", "quem adicionou", "mais utilizados", a busca grande e o botão
  "Adicionar material". Sem título de página (o `h1` "Biblioteca" fica só para leitor de tela).
- Componentes: livro §15.2 ("Acervo de estilos": `k-acervo-*`, `k-look`, `k-etiqueta`, `k-estilo-*`, `k-capa-estilo`,
  `k-legenda-estilo`, `k-tipo`, `k-anim`, `k-armazem`, `k-sistema`) + `k-filtro`, `k-empilhada`, `k-kv`, `k-details`.

## Hierarquia
1. Abas (filtros): **Tudo** · Looks de cor 3 · Capas 2 · Legendas 1 · Fontes 4 · Animações 3 · **Sistema 11** (aprovada em
   24/10). Uma aba mostra só o seu bloco; o par que perde a metade ocupa a largura toda. A aba Sistema só aparece quando
   escolhida (não entra em "Tudo"), como no canvas versão 23.
2. Coluna principal (9 de 12 a partir de 1600; largura toda abaixo):
   - **looks de cor.** — 5 cartões com a foto do Carlos no mesmo quadro da gravação de 16 set (4:5): Original da câmera
     (Referência), Só a conversão (Base), Look v4 (Arquivado: "O look “Tenet”, frio e contido; nunca aprovado."), **Look v5 · WAY (Em uso**, contorno laranja), Look v11
     (Alternativa). A contagem da aba (3) conta só os looks, não as duas referências.
   - **capas.** (5 de 9) — Serifa + rabisco (capa do Demis Hassabis, "usado em 17 set") e Grotesca + sublinhado ("Título grotesco, a última palavra sublinhada (cinza ou laranja). Uma capa por variante."; as duas capas
     do Livro ChatGPT, uma por variante, "em uso desde 23 out").
   - **legendas.** (4 de 9) — Texto Selecionado, com a amostra desenhada (não é quadro de vídeo).
   - **fontes.** (5 de 9) — Geist, Bricolage Grotesque, Inter, Playfair Display ("Aa" de cada uma e onde é usada).
   - **animações.** (4 de 9) — as 3 do Geoffrey Hinton (Ligação de madrugada 6,8 s; Máquina que imita a mente 10,2 s;
     2012: reconhecer imagens 10,7 s), metade de cima, "Roteirizada".
   - **sistema.** (só na aba Sistema; decisão de 24/10: o projeto vai para o GitHub e cada peça diz o que é) — "o que cada
     peça é e o que faz neste estúdio · para quem chegar pelo GitHub". Três cartões de modelo (nome, etiqueta "Modelo de
     IA", % dos tokens em `accent-ink` 24 px, a frase): Opus 5.5 82,7 %, Sonnet 5.5 12,4 %, Fable 5.1 4,8 %. Frases (canvas v26): Opus 5.5 "O padrão do dia a dia. A maior parte do trabalho; desde 24 out, o
     padrão de todos os agentes, portões incluídos."; Fable 5.1 "O mais capaz da Anthropic, e o mais caro. Usado pelo
     Atlas (a direção) em parte das sessões." Embaixo, um
     cartão com as 11 ferramentas em 3 colunas: **nome · etiqueta do tipo · o que faz aqui** (Claude Code, Python 3.12 · uv,
     ffmpeg, Remotion 4, ElevenLabs, Meta Graph API, Cloudflare R2, launchd, Next.js 15 · TypeScript, Supabase · Postgres,
     Claude Design). Claude Code: "Onde a equipe trabalha: o Atlas (a direção) e os 25 agentes rodam aqui, leem e
     escrevem os arquivos do projeto e chamam os scripts." Cloudflare R2: "Guarda o vídeo e a capa que a Meta baixa para publicar, e o PDF da palavra-chave,
     com o link que vai no direct." (frases do canvas v26). Visual simples por agora (o Carlos quer a informação primeiro, o acabamento depois).
3. Lateral (3 de 12 a partir de 1600; abaixo de 1600 os dois cartões descem, lado a lado):
   - **Armazenamento** — só o que está no Mac (decisão de 25/10: o painel não mostra o HD externo, que foi só a cópia de
     segurança): "123,8 GB no Mac"; barra empilhada de 2 partes (Gravações da câmera 117,0 GB · Material e cenas extras
     6,7 GB), legenda com o número de cada uma e "Ver os números".
   - **Sistema** — Modelos · tokens dos últimos 30 dias (Opus 5.5 82,7 % em `accent-ink`, Sonnet 5.5 12,4 %, Fable 5.1
     4,8 %) com o subtítulo "Modelos de IA · tokens dos últimos 30 dias"; "Ferramentas · a aba Sistema explica cada uma"
     (11 linhas: nome + a etiqueta do tipo); "25 agentes (mais o Atlas) · 24 habilidades · 19 comandos".

## Dados — de onde vem cada bloco (lista para o `engenheiro-backend`)
Bloco em `dados-2026-10-23.json → telas_acervo` (gerado só lendo por `painel/trabalho/designer/exportar_acervo_24out.py`).

| Bloco | Dado | Hoje vem de | Tipo |
|---|---|---|---|
| Looks de cor | nome, versão, data, aprovado, qual está em uso | `00-marca/cor/luts/*.json` + `00-marca/cor/cor.md` (`versao_ativa: v5`, `alternativa_medida: v11`, `arquivados: [v4]`); rosto em IRE da tabela do `cor.md`, medido em 18 set nos dois ("rosto 23,2 IRE · medido em 18 set" no v5, "rosto 40,9 IRE · medido em 18 set" no v11; o 17 set é a criação do v11) | **configuração** (arquivo; o banco não tem) |
| Looks de cor | a foto de cada look | o quadro `00-marca/cor/amostras/praq0967/…121.00s` com `entrada-camera.cube` e cada `korvu-look-vN.cube` (gerado pelo canvas; cópias em `telas/img/biblioteca/look-*.jpg`) | **arquivo fixo** (refazer quando entrar um look novo) |
| Capas | os 2 estilos e as 3 capas | as capas de `07-publicados/2026-09-17-demis-hassabis` e `06-publicar/2026-10-23-livro-chatgpt` (+ `-l01c`); o nome e a descrição do estilo são do canvas | **configuração** (o estilo não está registrado em lugar nenhum; proposta: uma linha por estilo de capa com o pacote de exemplo) |
| Legendas | Texto Selecionado | `00-marca/referencias/legendas/estilo-selecao.md`; a amostra é desenhada (`img/biblioteca/legenda-texto-selecionado.png`) | **configuração** |
| Fontes | as 4 famílias e o uso | `remotion/src/brand.ts` + o painel (Geist) | **configuração** |
| Animações | nome, duração, vídeo, estado | `videos/*/animacoes/*/brief.md` (título e "duração"); "Roteirizada" = tem brief e não tem `.mp4` na pasta | **arquivos** (o sincronizador não lê; proposta: tabela `animacoes` com slug, código Exx, título, duração, renderizada) |
| Armazenamento | gravações no Mac, material | `videos.gravacao_bytes_no_mac` (117,0 GB) e `sum(biblioteca_arquivos.bytes)` (6,7 GB, 639 arquivos); total 123,8 GB | **banco** (já existe) |
| Sistema · Modelos | % dos tokens nos 30 dias | o mesmo consumo de Tokens e custos (37,9 M, corte 23/10 16:02:49) | **banco** (já existe) |
| Sistema · Ferramentas (cartão e aba) | nome, `tipo`, `desc`, na ordem da tela | **`painel/biblioteca.yaml` → `ferramentas`** (o engenheiro-backend está criando; textos à letra do canvas) | **configuração** (arquivo do Carlos que o sincronizador lê) |
| Sistema · frase de cada modelo (aba) | `desc` por `modelo` | **`painel/biblioteca.yaml` → `modelos`** | **configuração** |
| Sistema · contagens | 25 agentes · 24 habilidades · 19 comandos | `.claude/agents/*.md`, `.claude/skills/*/`, `.claude/commands/*.md` | **arquivos** (o banco tem `agentes`; habilidades e comandos não) |

GB em unidades decimais (1 GB = 10⁹, como o Finder).

## Interações
- Abas: `aria-pressed`; trocam o que aparece, sem recarregar. "Tudo" volta a mostrar todos.
- Cartões de estilo **não são links nem botões** (o painel só informa). Nenhuma ação de escolher look ou capa no painel.
- "Ver os números" do Armazenamento abre a tabela (onde · GB · % do total).

## Estados (cada bloco)
| Bloco | Vazio | Carregando | Erro |
|---|---|---|---|
| Looks de cor | "Nenhum look registrado" | esqueleto de cartões | `k-note--alert` "Não deu para carregar esta parte" + "Tentar de novo" |
| Capas | "Nenhum estilo de capa" | esqueleto de cartões | idem |
| Legendas | "Nenhum estilo de legenda" | esqueleto de cartões | idem |
| Fontes | "Nenhuma fonte registrada" | esqueleto de cartões | idem |
| Animações | "Nenhuma animação ainda" | esqueleto de lista | idem |
| Armazenamento | "Sem leitura do disco" | esqueleto de lista | idem |
| Sistema (cartão da lateral) | "Sem consumo para mostrar" | esqueleto de lista | idem |
| Aba Sistema · modelos | "Nenhum modelo rodou nos 30 dias" | esqueleto de cartões | idem |
| Aba Sistema · ferramentas | "Nenhuma ferramenta descrita" (o `biblioteca.yaml` sem `ferramentas`) | esqueleto de lista | idem |
| Aba sem nada | "Nada aqui ainda." + "Quando a equipe criar um estilo novo, ele aparece nesta lista." | — | — |

## 375 px
Abas quebram em duas linhas; looks 2 por linha (3 entre 640 e 1279; 5 a partir de 1280); capas em pilha (cada estilo numa
linha); legenda com a amostra de 112 px ao lado; fontes 2 × 2; animações em lista; Armazenamento e Sistema em uma coluna. Aba
  Sistema: os 3 modelos em uma coluna; cada ferramenta em duas linhas (nome + etiqueta; embaixo, o que faz) — abaixo de 1024
  px as 3 colunas viram assim.
Sem rolagem lateral (`scrollWidth` 375 conferido) e nenhum texto cortado a 375, 1440, 1600 e 1920.

## Do canvas para a maquete
| No canvas | Na maquete | Motivo |
|---|---|---|
| Etiquetas a 10 px; `.tag` do Sistema a 10,5 px | 11 px (`.k-etiqueta--tipo`, a variante em frase normal da etiqueta do livro) | nenhum texto abaixo de 11 px (livro §15.2); sem estilo novo |
| Etiqueta "Arquivado" (Look v4) em `ink-3` sobre `surface-sunken` | `ink-2` | `ink-3` sobre `surface-sunken` dá 4,36:1 (T12, abaixo de 4,5) |
| Etiqueta "Referência" com fundo translúcido | `surface` sólido | sem vidro nem transparência sobre foto |
| Nomes com reticências (`mat-n`) | quebram em 2 linhas | nada cortado |
| "Aa" das fontes desenhado com Google Fonts | imagem (`img/biblioteca/fonte-*.png`, 2×) | o painel só carrega a Geist; as outras três seriam fontes novas só para mostrar a letra |
| Amostra de legenda em HTML com cores próprias (#3a6fd8, #9b9b9b) | imagem (`legenda-texto-selecionado.png`) | o CSS do painel só usa tokens; as cores são da legenda dos Reels, não do painel |
| Armazenamento "hoje" | sem data no card; o rodapé da página diz "sincronizado em 24 out, 22:40" | uma data de leitura só por tela (PI70); período sempre escrito |
| "25 agentes" | "25 agentes (mais o Atlas)" | a Equipe mostra 26 |
| Altura fixa de 1080 px | a página rola | o conteúdo real é mais alto que a prancha |

## Dúvidas para o Carlos
- Nenhuma aberta. (24/10: o Look v4 fica "Arquivado", como no canvas; `cor.md` → `arquivados: [v4]`.)
