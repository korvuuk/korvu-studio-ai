# CONTENT AI — Estúdio de Reels da Korvu

> **Começando uma sessão nova? Leia três arquivos antes de qualquer coisa:**
> 1. **`HANDOFF.md`** — diário das sessões: o que cada chat fez, arquivos, branch/commit, pendências (as 3 entradas do topo).
> 2. **`docs/decisoes.md`** — todas as decisões do Carlos, o que fazer e **o que não fazer**, com o motivo de cada uma.
> 3. **`_controle/CONTINUAR.md`** — estado atual de cada vídeo, próximo passo e armadilhas já mapeadas.
>
> **O que mais mudou em 13–14/10** (detalhe em `docs/decisoes.md`): roteiro **narrativo** (`00-marca/modelo-roteiro-narrativo.md`); o **vídeo é o carro-chefe** (material do YouTube pronto antes da gravação, sem teto de trecho, sem licença quando ele narra por cima); palavra-chave curta → PDF; cartão grande do CTA; publicar **sempre IG + FB** com Trial Reel; público = **qualquer pessoa; o conteúdo é em português e o objetivo é ser conhecido mundialmente falando de IA** (decisão de 21/10: **nada amarrado à Inglaterra e nada de "lusófono"** — não definir público por país nem por língua; formato das referências replicado inteiro, mudando só a imagem). **Não perguntar o que já está decidido.**
>
> Decisão nova dele = linha nova em `docs/decisoes.md` **no mesmo dia**. **Toda atualização / fim de sessão = entrada nova no topo do `HANDOFF.md`** (modelo no próprio arquivo) **e** `_controle/CONTINUAR.md` atualizado.

Produção de Reels sobre Inteligência Artificial para **@korvu_oficial** (Instagram + Facebook), do tema até à publicação. Autor e apresentador: **Carlos Mendes Pereira**.

## Áreas do projeto (26/10)
Quatro áreas trabalham nesta mesma raiz. Cada uma tem o seu próprio `CLAUDE.md`, que **também** carrega as
regras daqui — o Claude Code sobe os `CLAUDE.md` da pasta onde a sessão abre até a raiz. Por isso regras
transversais (identidade, legal, segredos) ficam só aqui, nunca duplicadas lá.

| Área | Pasta | Instruções |
|---|---|---|
| **Estúdio de conteúdo** (roteiro → gravação → edição → publicação) | raiz (`videos/`, `00-marca/`, `remotion/`, `docs/`…) | este arquivo |
| **Painel web** (tecnologia) | `painel/` | `painel/CLAUDE.md` |
| **LinkedIn pessoal do Carlos** | `linkedin/` | `linkedin/CLAUDE.md` |
| **Automação Meta** (comentário→direct, publicação e métricas IG/FB) | `automacao-meta/` (scripts em `scripts/`) | `automacao-meta/CLAUDE.md` |

Cada área só deve mexer na própria pasta (a automação Meta é a exceção: lê/escreve em `06-publicar/`,
`07-publicados/` e `_controle/` porque é o fim do pipeline — está documentado lá). Cruzar pra outra área sem
avisar o Carlos = não fazer. **Pra falar só com uma área, abra a sessão já com essa pasta como diretório de
trabalho** — ela carrega o `CLAUDE.md` dali + o da raiz, sem o detalhe das outras três.

## Identidade (sempre)
- Todo conteúdo em **Português do Brasil**: "você", "a gente", "tá", "pra". Nunca "tu"/"teu".
- Público: **iniciantes absolutos em IA + donos de pequenos negócios/empreendedores**, em qualquer lugar do mundo. **Nunca** definir ou pesquisar o público como "lusófono", "imigrante" ou "quem vive em Londres/Europa" (decisão de 21/10).
- Reel padrão: **60 s**, ~130–150 palavras faladas (usar `wps_roteiro` de `00-marca/voz-carlos.md`). **Roteiro NARRATIVO** (padrão desde 14/10: `00-marca/modelo-roteiro-narrativo.md`) — perfis/histórias **até 90 s, nunca mais** (decisão de 16/10: um vídeo só, igual no IG e no FB, que só aceita Reel até 90 s). CTA de palavra-chave sempre FALADO no vídeo, palavra curta (até ~6 letras). **Regras de alcance (16/10): `_controle/estrategia-de-alcance.md`** — virada até ~20 s, palavra-chave 2×, pedido de salvar, vídeo ≤ 90 s.
- Antes de escrever qualquer coisa falada, ler `00-marca/tom-de-voz.md` e `00-marca/voz-carlos.md` (este tem prioridade quando calibrado).

## Captação
- Câmera: **Panasonic Lumix S5IIX em V-Log (V-Gamut)**, 4K, **25 fps**, 4:2:2 **10-bit** (MOV LongGOP ou ProRes 422 HQ), vertical. Celular e gravações de ecrã também entram.
- Todo o projeto roda a **25 fps** (`FPS_PROJETO`) — nunca converter para 30 (causa judder). Celular/ecrã a 30/60 são convertidos para 25 na ingestão.
- Intermediários (`fontes/` 1440×2560 supersampled, `corte.mp4` 1080×1920 já com o zoom alternado por corte) ficam em **10-bit 4:2:2 e ainda em V-Log**; a conversão V-Log → Rec.709 (`00-marca/cor/luts/entrada-camera.cube`) e o look são aplicados só pelo colorista. Pré-visualizações e filmstrips usam o LUT de entrada só para visualização.
- Áudio sem perdas até o master: `edicao/audio48k/*.wav` (24-bit, só passa-altas, sem redução de ruído) → `edicao/corte-audio.wav` → `audio.py` (compressão suave, −14 LUFS, TP −1,5) → AAC só no final.
- Saída final: 1080×1920, 25 fps, H.264 8-bit 4:2:0 bt709 (Instagram/Facebook).

## Pipeline
```
tema → /novo-video (roteirista [formato NARRATIVO] → revisor-de-roteiro → produtor-de-material: PDF do CTA → buscador-de-videos: vídeos do YouTube baixados e cortados [automático] → leitura: teleprompter + monitor + historia-completa.txt) → /extras (produtor-de-extras + animador)
     → Carlos grava o PRINCIPAL (brutos/principal/) e as CENAS EXTRAS que faltam (brutos/extras/)
     → /editar (editor-de-video: alinhamento ao roteiro + EDL)  ⟶ PARA: Carlos aprova a EDL
     (GAUNTLET: depois de cada etapa, o PORTÃO da área — pauta · roteiro · imagem · corte · publicação — aprova ANTES de chegar ao Carlos; docs/gauntlet.md)
     → /renderizar: corte → revisor-de-video (corte + legendas) → colorista (/cor)
                    → Remotion (legendas, títulos, animações, zooms) → /musica (produtor-musical) → áudio → QA final
     → pacote em 05-render-pronto/<slug>/  (vídeo, capa, legendas, material = SÓ o PDF, relatório)
     → /publicar (move p/ 06-publicar/) → publicador escreve legendas/hooks e agenda
     → scripts/publicar.py (launchd) publica IG + FB na hora → 07-publicados/
     → (5 dias) scripts/metricas.py (launchd 09:30) → analista-de-metricas → _controle/aprendizados.md → estrategista + roteirista
```

## Onde fica cada coisa
| Pasta | Conteúdo |
|---|---|
| `00-marca/` | voz, hooks, estruturas, pilares, público, CTA, identidade visual, regras legais, referências, design system, cor/LUT |
| `01-ideias/` | banco de ideias e pesquisas |
| `02-calibracao/` | amostras de voz do Carlos e análises |
| `videos/<slug>/` | área de trabalho de um vídeo: roteiro, **`brutos/principal/`** (Carlos falando), **`brutos/extras/`** (cenas extras `Exx-*`), `animacoes/Exx/`, edicao, capa, material, qa. **`material/obra/`** = obra comentada, cópia de estudo que nunca é publicada |
| `05-render-pronto/<slug>/` | **pacote final montado** (video/, capa/, legendas/, material/, roteiro.md, qa-relatorio.md, pacote.json) |
| `06-publicar/<slug>/` | fila de publicação — **mover para cá = autorização para publicar** |
| `07-publicados/<slug>/` | arquivo com permalinks |
| `_controle/` | tracker, calendário, métricas (`metricas.md`) + `aprendizados.md` (o que as métricas ensinam ao roteirista), temas já feitos |
| `remotion/` | composições Remotion (Reel, Capa, Legendas, Títulos, Animações) |
| `painel/` | **painel web** (tecnologia) — equipe, vídeos + portões, fila, desempenho IG/FB. Instruções em `painel/CLAUDE.md`, detalhe técnico em `painel/README.md` |
| `linkedin/` | **LinkedIn pessoal do Carlos** — portfólio para vaga de engenheiro de IA em 2027. Instruções em `linkedin/CLAUDE.md`, detalhe em `linkedin/README.md` |
| `automacao-meta/` | **Automação Meta** — comentário→direct, publicação e métricas automáticas no IG/FB (scripts em `scripts/`). Instruções em `automacao-meta/CLAUDE.md` |
| `.claude/skills/*/scripts/` | scripts Python (rodar sempre com `uv run`) |

## Convenções
- **Slug:** `AAAA-MM-DD-palavra-chave` (data prevista de gravação).
- **Linhas do roteiro:** `L01`, `L02`… (hooks alternativos `L01B`, `L01C`). **Takes:** `L03-T2`.
- **Coluna FALA = exatamente o que será dito.** Tudo o que não é fala vai na coluna TELA.
- **Pausa da capa** (pedido do Carlos, 2026-09-18): toda gravação começa com ele **parado 3 s olhando para a câmera, em silêncio**, antes da L01. Esse trecho fica fora do corte mas continua no intermediário — é de lá que o `frame_candidates.py` tira o frame da capa, em vez de varrer o vídeo quadro a quadro. A instrução aparece no topo do roteiro, do roteiro limpo, do teleprompter e do monitor; **nunca** dentro da coluna FALA.
- **Todo roteiro sai em formato de leitura**: `teleprompter.txt` (respiros `/`, pausas `//` `///`, ênfase em MAIÚSCULAS, cenas extras e gestos como indicação não lida) + `monitor-chatgpt.txt` (texto para o ChatGPT Voz ler linha a linha e corrigir o Carlos). O roteirista marca os respiros com ` / ` na FALA.
- **Gravação com monitor ChatGPT Voz:** o áudio da câmera tem DUAS vozes — a IA (lê primeiro, sai do altifalante do telemóvel) e o Carlos (repete). O editor identifica os locutores e corta **só a voz do Carlos**; nenhuma leitura ou correção da IA pode ficar no corte.
- `status.json` em cada vídeo + linha no `_controle/tracker.md` — todo comando atualiza os dois.
- **Uma revisão por vez** (pedido do Carlos, 2026-09-16: "manter só a atual"): a pasta do vídeo guarda só o que é preciso para o arquivo final. Cada render novo apaga o anterior — `uv run python scripts/limpar_video.py videos/<slug> --apagar` (sem `--apagar` só lista). Ficam a revisão mais nova (`revisao-vN.mp4` + `-leve`), o corte, o áudio, a cor, as fontes e os JSON; saem rascunhos, `render-remotion.mp4`, `preview.mp4` e as capas não escolhidas.
- Estados: `roteiro → gravacao → edicao → edl_aprovada → revisao → cor → legendas → capa → qa → pronto → agendado → publicado`.

## Regras rígidas
1. **Nunca renderizar o vídeo final sem `edl.json.aprovado = true`** (exceto se o Carlos pedir `--auto`).
2. **Nunca publicar fora do fluxo**: só publica o que estiver em `06-publicar/` com `pacote.json` QA PASS. Os primeiros posts (ver `_controle/calendario.md`) pedem confirmação.
3. Nenhuma imagem realista de pessoas reais além do Carlos. Nada de logos de terceiros **como se fossem parceria**. **Mostrar a ferramenta de que o vídeo fala é permitido e desejado** (decisão do Carlos, 2026-09-17): a animação pode ter a cara do ChatGPT — interface, nome e logo — para o público reconhecer na hora do que se trata. O limite é não sugerir parceria, patrocínio ou aval: nada de "em parceria com", logo de terceiro junto ao da Korvu, nem usar a marca deles como se fosse nossa.
4. **Material de terceiros tem dois caminhos, e não se misturam** (decisão do Carlos, 2026-09-18):
   - **B-roll** (o trecho ilustra outra coisa, sem narração sobre a pessoa/obra) → precisa de **licença de reuso**: `/material`, `scripts/buscar_video.py`.
   - **Decisão de 14/10:** vídeo em que o Carlos **narra por cima** da pessoa/obra (perfis, destaque, comentário) **não precisa de licença**; baixar do YouTube é liberado. Licença nunca é motivo para descartar esse tema ou trecho.
   - **Comentário/reação** (o Reel fala **sobre** a obra/pessoa; o trecho é o objeto da crítica) → `/obra`, `scripts/baixar_obra.py`, e `/buscar-videos`, `scripts/buscar_youtube.py` (qualquer vídeo do YouTube, decisão de 01/10), com crédito na tela. **Desde 14/10 sem teto de tempo**, com o áudio original baixo ou mudo sob a narração (antes: 12 s por trecho / 30 s no total). A cópia inteira fica em `material/obra/` só para estudo e **nunca é publicada**.
5. Máximo **5 hashtags**; palavra-chave principal na 1.ª linha da legenda do post.
6. CTA sempre de `00-marca/cta.md`. **Nunca prometer material que não exista** em `videos/<slug>/material/`.
   **Palavra-chave = sempre um PDF** (decisão do Carlos, 13/10), feito pelo `produtor-de-material` a partir do roteiro
   (`scripts/gerar_material_pdf.py`). Só esse PDF vai para o pacote e para o R2 público — dossiê, `fontes.json` e obra nunca.
   **No CTA nunca entra cena extra**: o Carlos em tela cheia (decisão dele, 19/09) — o `parse_roteiro.py` recusa.
7. Afirmações de notícias precisam de fonte (link no roteiro).
8. Gravações de ecrã **não** recebem LUT. Cor só na imagem da câmera/celular, antes dos gráficos.
9. Não ler nem imprimir `.env`. Segredos só via variáveis de ambiente.
10. **Conferir o resultado no ponto do defeito, e pelo meio certo.** Compilar não prova que roda; `cmd | tail`
    esconde o erro (use `test ${PIPESTATUS[0]} -eq 0`); conferir "perto" do problema não conta. Antes de dizer
    que está corrigido, **olhe o quadro ou o número onde ele reclamou**. Em 19/09 mandei dois vídeos ao Carlos
    dizendo que estavam corrigidos — o render tinha falhado e os arquivos eram de 4 h antes.
11. **Gravação em várias partes** (a câmera divide em N arquivos): cor, preto e nível de voz variam ENTRE
    arquivos. Toda correção tem de ser **por fonte**, nunca global — e **corrigir o mínimo**, com alvo na
    mediana dos arquivos que já estão bons (`scripts/cor_pele_casada.py`). Buscar o número ideal para todos
    criou um degrau no meio do vídeo em 19/09.
12. Antes de um tema novo, checar `_controle/tracker.md` e `_controle/temas-ja-feitos.md` (anti-repetição).
13. **GAUNTLET — quem faz não aprova** (modelo aprovado pelo Carlos em 22/10; detalhe em **`docs/gauntlet.md`**).
    Cada departamento tem um **portão** (o gerente) que audita e não constrói: **PAUTA** `portao-pauta` · **ROTEIRO**
    `revisor-de-roteiro` · **IMAGEM** `portao-imagem` · **CORTE** `revisor-de-video` (passagem 2) · **PUBLICACAO**
    `portao-publicacao`. Quando um construtor termina, o portão da área **roda sozinho, sem perguntar ao Carlos**;
    BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão (até 3 voltas; na 3.ª, ESCALADO = decisão dele).
    **Nada chega ao Carlos antes do APROVADO** — roteiro, PDF, capa, cor, corte, post. O veredicto fica preso aos
    arquivos (`scripts/portoes.py` → `portoes.json`): arquivo mudado depois do APROVADO **vence** o veredicto.
    O `montar_pacote.py` recusa sem os portões e sela o pacote; o `publicar.py` recusa pacote sem selo, arquivo que os
    portões não aprovam e post sem o PORTÃO-PUBLICACAO. Sinais: `uv run python scripts/portoes.py estado`.
    **O painel web tem o seu próprio GAUNTLET de tecnologia** (`portao-interface` + `portao-dados`, alvo
    `painel`) — detalhe em `painel/CLAUDE.md`.

## Contratos de dados
Formatos de `roteiro.json`, `transcricao.json`, `alinhamento.json`, `edl.json`, legendas, `reel-props.json`, `status.json`, `pacote.json` e `post.json`: **`docs/contratos.md`** (fonte única — não inventar campos).

Arquivos de vídeo por etapa: `edicao/corte.mp4` (corte) → `edicao/cor/corte-cor.mp4` (cor) → `edicao/render-remotion.mp4` (gráficos) → `edicao/final.mp4` (áudio −14 LUFS) → `05-render-pronto/<slug>/video/video-final.mp4`.

## Agentes, skills e comandos
- **Portões GAUNTLET** (gerentes, opus, auditam e não constroem — `docs/gauntlet.md`): portao-pauta · revisor-de-roteiro (PORTÃO-ROTEIRO) · portao-imagem · revisor-de-video (PORTÃO-CORTE) · portao-publicacao · **sistema:** portao-interface · portao-dados.
- **Tecnologia (painel web):** agentes, skills e o GAUNTLET da área em `painel/CLAUDE.md`.
- Agentes (`.claude/agents/`): estrategista · pesquisador-de-material · curador-de-obra · buscador-de-videos · produtor-musical · roteirista · revisor-de-roteiro · produtor-de-material · produtor-de-extras · editor-de-video · revisor-de-video · colorista · designer-de-capas · animador · publicador · analista-de-metricas · auditor-de-perfil (perfil/bio/público da conta: `scripts/perfil.py` → `_controle/auditoria-perfil.md`).
- **Estrutura de todo vídeo:** vídeo principal (Carlos falando, a voz) + cenas extras por cima em `split` / `full` / `card` (`docs/contratos.md` §0, medidas em `00-marca/layouts.md`).
- **A cena extra liga-se à linha pela coluna "Linhas"** da tabela `## Cenas extras` do roteiro (o roteiro enxuto não tem coluna TELA). Uma cena pode cobrir **várias linhas seguidas** — é assim que a metade de cima fica ocupada sem piscar. Extras encostados = **faixa contínua com corte seco** entre eles; o Carlos reprovou o "sobe e desce" (19/09).
- Skills próprias: roteiro-reels · **tela-de-computador** (gravação de tela do Mac → cenas extras em `brutos/extras/`, ANTES do /editar; decisão de 21/10) · corte-por-roteiro · audio-polish · color-grading · legendas-animadas · capa-reels · animacoes-explicativas · qa-video.
- Skills externas: `remotion-*` (oficiais do Remotion) · `watch` (claude-video — "olhos" para vídeo).
- Comandos: /ideias · /material · /obra · /buscar-videos · /musica · /novo-video · /roteiro · /extras · /editar · /renderizar · /cor · /criar-lut · /capa · /animar · /pacote · /publicar · /fila · /calibrar-voz · /status.

## Ferramentas
- `FFMPEG_BIN` / `FFPROBE_BIN` vêm do `.env` (ffmpeg estático em `/Users/teste/bin/ffmpeg`, ffprobe do Homebrew).
- Python: `uv run python <script>` (Python 3.12, `pyproject.toml` na raiz).
- Transcrição: ElevenLabs Scribe (`ELEVENLABS_API_KEY`); alternativa local `--engine mlx` (mlx-whisper).
- Remotion: `cd remotion && npx remotion studio` / `npx remotion render`.
- **Ver vídeos**: skill `watch` (`/watch <arquivo|link> <pergunta>` — frames + transcrição) para assistir renders e referências; `filmstrip.py` para inspecionar cortes quadro a quadro.
