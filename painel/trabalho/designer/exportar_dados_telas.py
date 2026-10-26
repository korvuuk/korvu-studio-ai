"""Acrescenta ao painel/design/dados-2026-10-23.json, SÓ LENDO, os números que as 5 telas de 23/10 usam.

Não troca nenhum bloco que o PORTÃO-INTERFACE aprovou: só cria blocos novos com o prefixo "telas_". Cada bloco diz de
onde veio ("fonte"), como foi lido ("consulta" para o banco, "como" para arquivo) e a hora da leitura ("lido_em").
Banco: transação só de leitura em 127.0.0.1:55322. Arquivos: só abertos para leitura.

Rodar:  uv run python -I painel/trabalho/designer/exportar_dados_telas.py
"""
import datetime as dt
import decimal
import json
import pathlib
import re

import psycopg

RAIZ = pathlib.Path(__file__).resolve().parents[3]
SAIDA = RAIZ / "painel/design/dados-2026-10-23.json"
URL = "postgresql://postgres:postgres@127.0.0.1:55322/postgres"
AGORA = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def normal(v):
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, list):
        return [normal(x) for x in v]
    return v


def ler(p):
    return json.loads((RAIZ / p).read_text(encoding="utf-8"))


def rel(p):
    return str(pathlib.Path(p).relative_to(RAIZ))


CONSULTAS = {
    "telas_perfil": (
        "select lido_em, seguidores, seguindo, janela_dias, alcance, views, contas_engajadas, interacoes, visitas_perfil, "
        "alcance_seguidores, alcance_nao_seguidores from perfil_snapshots order by lido_em"),
    "telas_paises": (
        "select publico, chave, valor from perfil_demografia where dimensao = 'country' "
        "and lido_em = (select max(lido_em) from perfil_snapshots) order by publico, valor desc"),
    "telas_departamentos": "select id, nome, ordem, descricao, gerente_id from departamentos order by ordem",
    "telas_agentes": (
        "select id, nome, cargo, departamento_id, papel, resumo, modelo, fiscalizado_por, fiscaliza from agentes "
        "order by departamento_id, papel desc, nome"),
    "telas_portoes_por_area": (
        "select portao, status, count(*) as n from portoes_estado where alvo like 'videos/%' or alvo like '06-publicar/%' "
        "group by portao, status order by portao, status"),
    "telas_portoes_videos": (
        "select slug, portao, status from portoes_estado where alvo like 'videos/%' order by slug, portao"),
    "telas_fila_legado": "select slug, legado, publicar_em, trial from fila order by publicar_em",
    "telas_sincronizacao": "select em from sincronizacoes order by em desc limit 1",
}


def blocos_banco():
    out = {}
    with psycopg.connect(URL, autocommit=True) as c:
        c.read_only = True
        with c.cursor() as cur:
            for nome, sql in CONSULTAS.items():
                cur.execute(sql)
                cols = [d.name for d in cur.description]
                out[nome] = {"fonte": "banco do painel (Supabase local)", "consulta": sql, "lido_em": AGORA,
                             "linhas": [{k: normal(v) for k, v in zip(cols, r)} for r in cur.fetchall()]}
    return out


def bloco_perfil_arquivo():
    linhas = []
    for f in ("_controle/perfil/2026-10-16.json", "_controle/perfil/2026-10-22.json"):
        p = ler(f)
        ig = p["instagram"]
        m = ig["metricas_conta"]
        q = {r["chave"][0]: r["valor"] for r in m["reach_por_follow_type"]["quebras"][0]["resultados"]}
        linhas.append({"arquivo": f, "lido_em": p["lido_em"], "janela": ig["janela"],
                       "seguidores": ig["conta"]["followers_count"], "alcance": m["reach"]["valor"],
                       "views": m["views"]["valor"], "visitas_perfil": m["profile_views"]["valor"],
                       "toques_no_link": m["profile_links_taps"]["valor"],
                       "alcance_nao_seguidores": q.get("NON_FOLLOWER"), "alcance_seguidores": q.get("FOLLOWER")})
    return {"fonte": "_controle/perfil/2026-10-16.json e 2026-10-22.json (o snapshot da Meta, janela de 28 dias)",
            "como": "instagram.conta.followers_count; instagram.metricas_conta.{reach,views,profile_views,"
                    "profile_links_taps}.valor; reach_por_follow_type (NON_FOLLOWER / FOLLOWER)",
            "lido_em": AGORA, "linhas": linhas}


def capa_de(pasta):
    for c in ("capa/capa.png", "capa/capa.jpg"):
        if (pasta / c).exists():
            return rel(pasta / c)
    return None


def bloco_fila():
    linhas = []
    for d in sorted((RAIZ / "06-publicar").iterdir()):
        if not (d / "post.json").exists():
            continue
        p, k = json.loads((d / "post.json").read_text(encoding="utf-8")), json.loads((d / "pacote.json").read_text(encoding="utf-8"))
        ig = p.get("instagram") or {}
        linhas.append({"slug": d.name, "publicar_em": p.get("publicar_em"), "plataformas": p.get("plataformas"),
                       "estado": p.get("estado"), "trial": (ig.get("trial") or {}).get("graduation_strategy") if ig.get("trial") else None,
                       "palavra": (p.get("material") or {}).get("palavra"), "duracao_s": k.get("duracao"),
                       "qa": k.get("qa"), "selo": "gauntlet" in k, "capa": capa_de(d)})
    return {"fonte": "06-publicar/<slug>/post.json + pacote.json",
            "como": "publicar_em, plataformas, estado, instagram.trial.graduation_strategy, material.palavra; "
                    "pacote.duracao, pacote.qa, 'gauntlet' em pacote.json (selo); capa/capa.png",
            "lido_em": AGORA, "linhas": linhas}


def bloco_publicados():
    linhas = []
    for d in sorted((RAIZ / "07-publicados").iterdir()):
        if not (d / "post.json").exists():
            continue
        p = json.loads((d / "post.json").read_text(encoding="utf-8"))
        k = json.loads((d / "pacote.json").read_text(encoding="utf-8"))
        ig, fb = p.get("instagram") or {}, p.get("facebook") or {}
        lin = {"slug": d.name, "publicado_em": p.get("publicado_em"), "plataformas": p.get("plataformas"),
               "trial": (ig.get("trial") or {}).get("graduation_strategy") if ig.get("trial") else None,
               "permalink_instagram": ig.get("permalink"), "permalink_facebook": fb.get("permalink"),
               "permalink_linkedin": (p.get("linkedin") or {}).get("permalink"),
               "palavra": (p.get("material") or {}).get("palavra"), "duracao_s": k.get("duracao"), "capa": capa_de(d),
               "metricas": None}
        mj = d / "metricas.json"
        if mj.exists():
            m = json.loads(mj.read_text(encoding="utf-8"))
            u = m["ultima"]
            r = u.get("resumo") or {}
            i, f = r.get("instagram") or {}, r.get("facebook") or {}
            tm, dur = i.get("tempo_medio_s"), m.get("duracao_s") or 0
            lin["metricas"] = {
                "lido_em": u.get("lido_em"), "dias": u.get("dias_desde_publicacao"),
                "views": i.get("views"), "alcance": i.get("alcance"), "curtidas": i.get("curtidas"),
                "comentarios": i.get("comentarios"), "salvamentos": i.get("salvamentos"),
                "compartilhamentos": i.get("compartilhamentos"),
                "interacoes": (u.get("instagram") or {}).get("metricas", {}).get("total_interactions"),
                "tempo_medio_s": tm, "pct_assistido": i.get("pct_medio_assistido"),
                "suspeito": bool(tm and dur and tm > dur), "fb_plays": f.get("plays"),
                "fb_tempo_medio_s": f.get("tempo_medio_s")}
        linhas.append(lin)
    return {"fonte": "07-publicados/<slug>/post.json + pacote.json + metricas.json (ultima)",
            "como": "post: publicado_em, plataformas, instagram/facebook.permalink, instagram.trial; pacote.duracao; "
                    "metricas.ultima.resumo.instagram (views, alcance, curtidas, salvamentos, tempo médio, % assistido) "
                    "e ultima.instagram.metricas.total_interactions. 'suspeito' = tempo médio maior que a duração "
                    "(a mesma regra do sincronizar.py). Sem metricas.json = a 1.ª leitura ainda não saiu.",
            "observacao": "o banco (tabela publicacoes) só tem um post depois da 1.ª leitura de métricas: o "
                          "2026-10-23-livro-chatgpt-a (publicado 22/10 21:19) ainda não está nele.",
            "lido_em": AGORA, "linhas": linhas}


def bloco_videos():
    linhas = []
    for d in sorted((RAIZ / "videos").iterdir()):
        if not re.match(r"\d{4}-\d{2}-\d{2}-", d.name):
            continue
        r = json.loads((d / "roteiro.json").read_text(encoding="utf-8"))
        s = json.loads((d / "status.json").read_text(encoding="utf-8"))
        vis = lambda p: [x for x in p.glob("*") if not x.name.startswith(".") and x.is_file()] if p.exists() else []
        ex_planejadas = r.get("extras") or []
        linhas.append({"slug": d.name, "versao": r.get("versao"), "palavra": r.get("cta_palavra"),
                       "pdfs": [x.name for x in (d / "material").glob("*.pdf")],
                       "extras_prontas": len(vis(d / "brutos/extras")),
                       "extras_planejadas": len(ex_planejadas) if isinstance(ex_planejadas, list) else None,
                       "gravado": len(vis(d / "brutos/principal")) > 0, "estado": s.get("estado"),
                       "atualizado": s.get("atualizado"), "gravacao_prevista": d.name[:10]})
    return {"fonte": "videos/<slug>/roteiro.json + status.json + material/*.pdf + brutos/extras/ + brutos/principal/",
            "como": "versao, cta_palavra, len(extras) do roteiro; estado e atualizado do status.json; arquivos em "
                    "brutos/extras/ (prontas) e brutos/principal/ (gravado = tem arquivo); gravação prevista = data do "
                    "slug (CLAUDE.md, convenção do slug)",
            "lido_em": AGORA, "linhas": linhas}


def bloco_prontos():
    linhas = []
    cont = (RAIZ / "_controle/CONTINUAR.md").read_text(encoding="utf-8").splitlines()
    for d in sorted((RAIZ / "05-render-pronto").iterdir()):
        if not (d / "pacote.json").exists():
            continue
        k = json.loads((d / "pacote.json").read_text(encoding="utf-8"))
        nota = next((l.strip() for l in cont if d.name in l and "não publicar" in l), None)
        linhas.append({"slug": d.name, "criado_em": k.get("criado_em"), "duracao_s": k.get("duracao"),
                       "qa": k.get("qa"), "palavra": k.get("cta_palavra"), "selo": "gauntlet" in k,
                       "capa": capa_de(RAIZ / "videos" / d.name), "nota_continuar": nota})
    return {"fonte": "05-render-pronto/<slug>/pacote.json + _controle/CONTINUAR.md (linha do vídeo)",
            "como": "criado_em, duracao, qa, cta_palavra; nota = a linha do CONTINUAR.md que cita o slug e diz "
                    "'não publicar' (texto, não há campo para isso)",
            "lido_em": AGORA, "linhas": linhas}


def bloco_retratos():
    pasta = RAIZ / "painel/web/public/equipe"
    nomes = sorted(p.name for p in pasta.glob("*.jpg"))
    return {"fonte": "painel/web/public/equipe/<id do agente>.jpg (onde o painel serve os retratos; as 10 fotos que o Carlos "
                     "mandou estavam em painel/web/src/app/equipe/img equipe/ e foram para cá com o nome do agente). Cópias "
                     "512×512 para a maquete: painel/design/telas/img/retratos/ (de painel/referencias/claude-design/"
                     "telas-2026-10-23/retratos/)",
            "como": "lista de arquivos; o nome do arquivo é o id do agente (agentes.id)",
            "lido_em": AGORA, "linhas": [{"arquivo": n, "agente": n.rsplit(".", 1)[0]} for n in nomes]}


def bloco_horarios():
    return {
        "fonte": "_controle/perfil/prints-2026-10-17/15.jpg (app do Instagram, 'Horários de atividade dos seguidores', "
                 "fuso GMT+01:00, dia mostrado: quinta-feira) + _controle/calendario.md (vagas_semanais)",
        "como": "altura de cada barra medida em pixels no print (base y=1562, topo de cada barra) ÷ a mais alta; o "
                "app não dá número absoluto. Picos = texto do próprio app no mesmo print ('Terças-feiras 9 PM–12 AM', "
                "'os domingos 6 PM–9 PM', 'Quartas-feiras'…). Vagas = vagas_semanais do calendario.md.",
        "lido_em": AGORA,
        "linhas": [
            {"faixa": "0h", "pixels": 407, "relativo": 72}, {"faixa": "3h", "pixels": 192, "relativo": 34},
            {"faixa": "6h", "pixels": 187, "relativo": 33}, {"faixa": "9h", "pixels": 388, "relativo": 69},
            {"faixa": "12h", "pixels": 518, "relativo": 92}, {"faixa": "15h", "pixels": 559, "relativo": 99},
            {"faixa": "18h", "pixels": 562, "relativo": 100}, {"faixa": "21h", "pixels": 559, "relativo": 99}],
        "picos_no_app": ["Dom 18–21 h", "Ter 21–24 h", "Qua à noite"],
        "vagas_semanais": {"domingo": "19:00", "terca": "21:00", "quarta": "21:00"}}


def bloco_analise():
    return {"fonte": "_controle/analise-trial-vs-normal-2026-10-22.md (§1 e item 4 da recomendação)",
            "como": "copiado do texto da análise (não recalculado)",
            "lido_em": AGORA,
            "linhas": [
                {"slug": "2026-09-17-demis-hassabis", "nao_seguidores": "~208", "pct_nao_seguidores": 62.2,
                 "base": "62,2 % de 334 contas no app, 17/10"},
                {"slug": "2026-10-20-fei-fei-li", "nao_seguidores": "~40", "pct_nao_seguidores": None, "base": "Trial: mostrado primeiro a quem não segue"},
                {"slug": "2026-10-20-geoffrey-hinton", "nao_seguidores": "11", "pct_nao_seguidores": 100, "base": "11 (100 %)"},
                {"slug": "2026-10-20-fei-fei-li-a", "nao_seguidores": "~4", "pct_nao_seguidores": None, "base": "Trial"}],
            "frase": "o único Reel normal (Hassabis) chegou a ~208 NÃO seguidores; os três Trials somados chegaram a 55.",
            "seis_dias": "+44 não seguidores em 6 dias (16 → 22 out), com 3 Trials no ar"}


def bloco_modelos():
    return {"fonte": "model: de .claude/agents/*.md (alias 'opus' / 'sonnet'); versão = o modelo que cada alias usa "
                     "hoje: tabela de modelos da skill claude-api (cache de 06/10/2026: claude-opus-5-5 = Claude Opus 5.5, "
                     "claude-sonnet-5-5 = Claude Sonnet 5.5) e o message.model das sessões do Claude Code deste projeto "
                     "(~/.claude/projects/-Users-teste-Documents-CONTENT-AI/*.jsonl: 346 respostas da sessão mais recente, "
                     "todas claude-opus-5-5)",
            "como": "alias → rótulo com versão. O banco guarda só o alias (agentes.modelo)",
            "lido_em": AGORA,
            "linhas": [{"alias": "opus", "modelo": "claude-opus-5-5", "rotulo": "Opus 5.5"},
                       {"alias": "sonnet", "modelo": "claude-sonnet-5-5", "rotulo": "Sonnet 5.5"}]}


def curva_do_canvas():
    """Pontos da curva de EXEMPLO do canvas (Desempenho.dc.html): âncoras das curvas de Bézier → valor no eixo 0–300."""
    t = (RAIZ / "painel/referencias/claude-design/telas-2026-10-23/Desempenho.dc.html").read_text(encoding="utf-8")
    def pontos(d):
        nums = re.findall(r"-?[\d.]+", d.split(" L")[0])
        xs = [(float(nums[0]), float(nums[1]))]
        resto = list(map(float, nums[2:]))
        for i in range(0, len(resto) - 5, 6):
            xs.append((resto[i + 4], resto[i + 5]))
        return [round((186 - y) / 176 * 300, 1) for x, y in xs if x <= 1034.5]
    vis = re.search(r'<path class="s1" d="([^"]+)"', t).group(1)
    alc = re.search(r'<path d="(M34 [^"]+)" fill="none" stroke-width="1.5"', t).group(1)
    return {"views": pontos(vis), "alcance": pontos(alc)}


def bloco_exemplos():
    return {"fonte": "nenhuma — pedidos do Carlos no canvas de 23/10 (painel/referencias/claude-design/telas-2026-10-23/)",
            "como": "valores copiados do renderVals() dos artboards; aparecem nas maquetes com o selo 'exemplo'",
            "lido_em": AGORA,
            "linhas": [
                {"o_que": "status Ativo agora / Em espera (presença)", "valores": "Atlas e Lia Monteiro 'ativos' no Equipe.dc.html (filtro 'Ativos 2'); Atlas 'Trabalhando agora' no Main.dc.html",
                 "de_onde_viria": "sessão do Claude Code com resposta nos últimos minutos (timestamp do .jsonl) — engenheiro-backend"},
                {"o_que": "tarefas atuais do Atlas", "valores": "3 · 'Tela Equipe e mais 2'",
                 "de_onde_viria": "não há registro de tarefa em andamento; as 'tarefas' reais (execuções em 30 dias) já vêm dos registros"},
                {"o_que": "curva diária de visualizações e alcance do Instagram", "valores": "forma desenhada no canvas (Main.dc.html e Desempenho.dc.html); os pontos marcam as datas reais dos Reels",
                 "de_onde_viria": "perfil.py lendo a Meta todo dia (insights da conta com period=day) → uma linha por dia em perfil_snapshots — engenheiro-backend",
                 "pontos_exemplo": curva_do_canvas(), "dias": "25 set … 22 out (28 dias)"},
                {"o_que": "avisos não lidos", "valores": "o canvas dizia '3 novas'",
                 "de_onde_viria": "o painel não guarda o que você já viu; os 3 avisos em si são calculados dos dados (reais)"}]}



TOKENS_CORTE = "2026-10-23T15:02:49Z"  # o corte do banco do painel e do tokens-custos.py (PD21, 23/10 às 16:02:49 em Londres)


def bloco_tokens():
    import subprocess, sys
    saida = subprocess.run([sys.executable, "-I", str(RAIZ / "painel/trabalho/designer/tokens/ler_tokens.py"), "--ate",
                            TOKENS_CORTE], capture_output=True, text=True, check=True).stdout
    d = json.loads(saida)
    return {"fonte": "registros das sessões do Claude Code deste projeto: ~/.claude/projects/-Users-teste-Documents-CONTENT-AI/"
                     "**/*.jsonl (message.usage + message.model por resposta; subagentes: subagents/agent-*.meta.json → "
                     "agentType)",
            "como": "a mesma conta de painel/referencias/claude-design/telas-2026-10-23/tokens-custos.py (refeita em "
                    "painel/trabalho/designer/tokens/ler_tokens.py, que só lê): 30 dias (24 set – 23 out); tokens = entrada + "
                    "cache gravado + saída; custo = preço de tabela da API em US$ (Opus 5.5 4/20 por milhão, Sonnet 5.5 2/10, "
                    "Fable 5.1 10/50; cache gravado 1,25× a entrada por 5 min e 2× por 1 h; cache lido 0,20 ou 0,25); tarefa = um arquivo de sessão "
                    "(execução) com consumo; vídeo = subagente cujo 1.º pedido cita videos/<slug>. Cada resposta conta pela ÚLTIMA linha "
                    "do seu message.id (as primeiras são provisórias) e cai no dia da 1.ª linha, como o banco (PD21). Cortada no instante "
                    + TOKENS_CORTE + " (23/10 às 16:02:49 em Londres), o mesmo corte do banco, para não andar com a sessão aberta. É um retrato "
                    "com hora de corte: no painel, o número vem do banco.",
            "ressalva": "custo = equivalente na API pelo preço de tabela; com assinatura, a fatura é outra. ElevenLabs "
                        "(transcrição e música) fica de fora: sem medição.",
            "lido_em": AGORA, "linhas": [d]}


def _tam(b):
    return b


REGRA_MATERIAL = (
    "Material lógico = um agrupamento por vídeo: (1) cada PDF de material/ junto com material/_fonte/ = 'PDF da palavra'; "
    "(2) material/dossie.md + fontes.json = 'dossiê de pesquisa'; (3) cada subpasta de material/ é um material "
    "(youtube = trechos do YouTube, fotos = fotos de pesquisa, img = imagens das cenas, capas = capas de referência, "
    "'screnn record' = gravação de tela, obra = obra comentada, as outras pelo nome); (4) brutos/extras/ = cenas extras. "
    "Data do material = a do arquivo mais novo dele; tamanho = a soma (no PDF, só o PDF). Pastas _teste-* ficam fora (não são "
    "vídeos). Miniatura: a prévia do PDF, a 1.ª imagem da pasta ou um quadro do 1.º vídeo.")
PASTA_MATERIAL = {"youtube": ("trechos do YouTube", "YouTube", "Tiago Lopes · vídeos"),
                  "fotos": ("fotos de pesquisa", "Fotos", "Rafael Nunes · pesquisa"),
                  "img": ("imagens das cenas", "Imagens", "Caio Martins · cenas extras"),
                  "capas": ("capas de referência", "Imagens", "Rafael Nunes · pesquisa"),
                  "screnn record": ("gravação de tela", "Vídeo", "Carlos · gravação"),
                  "obra": ("obra comentada", "Vídeo", "Beatriz Santos · obras"),
                  "podcast": ("trechos de podcast", "Áudio", "Tiago Lopes · vídeos"),
                  "cortes-podcast": ("cortes de podcast", "Vídeo", "Tiago Lopes · vídeos")}
TIPO_EXT = {".mp4": "videos", ".mov": "videos", ".jpg": "imagens", ".jpeg": "imagens", ".png": "imagens", ".webp": "imagens",
            ".md": "documentos", ".pdf": "documentos", ".json": "pesquisas", ".wav": "audio", ".mp3": "audio", ".m4a": "audio"}


def materiais_logicos():
    import datetime as _dt
    grupos = {}
    def poe(chave, f, **meta):
        g = grupos.setdefault(chave, {"arquivos": [], **meta})
        g["arquivos"].append(f)
    for v in sorted((RAIZ / "videos").glob("2026-*")):
        mat, ext = v / "material", v / "brutos/extras"
        pdfs = sorted(mat.glob("*.pdf")) if mat.exists() else []
        for f in (sorted(mat.rglob("*")) if mat.exists() else []):
            if not f.is_file() or f.name.startswith("."):
                continue
            partes = f.relative_to(mat).parts
            if len(partes) == 1 and f.suffix.lower() == ".pdf":
                poe((v.name, "pdf", f.name), f, video=v.name, tipo_mat="pdf", nome=f.stem)
            elif partes[0] == "_fonte" and pdfs:
                poe((v.name, "pdf", pdfs[0].name), f, video=v.name, tipo_mat="pdf", nome=pdfs[0].stem)
            elif len(partes) == 1 and f.name in ("dossie.md", "fontes.json"):
                poe((v.name, "dossie"), f, video=v.name, tipo_mat="dossie", nome="dossie")
            elif len(partes) == 1:
                poe((v.name, "outros"), f, video=v.name, tipo_mat="outros", nome="outros")
            else:
                poe((v.name, "pasta", partes[0]), f, video=v.name, tipo_mat="pasta", nome=partes[0])
        for f in (sorted(ext.iterdir()) if ext.exists() else []):
            if f.is_file() and not f.name.startswith("."):
                poe((v.name, "extras"), f, video=v.name, tipo_mat="extras", nome="extras")
    itens = []
    for chave, g in grupos.items():
        fs = g["arquivos"]
        exts = {}
        for f in fs:
            t = TIPO_EXT.get(f.suffix.lower())
            if t:
                exts[t] = exts.get(t, 0) + 1
        n_mp4 = sum(1 for f in fs if f.suffix.lower() in (".mp4", ".mov"))
        n_img = sum(1 for f in fs if f.suffix.lower() in (".jpg", ".jpeg", ".png"))
        if g["tipo_mat"] == "pdf":
            nome = g["nome"].replace("-", " "); nome = nome[:1].upper() + nome[1:]
            rot, quem, tipos, extra = "PDF", "Lívia Rocha · material", ["documentos"], None
            fonte_mini = next((f for f in sorted(fs, key=lambda f: (len(f.name), f.name)) if "_fonte" in f.parts and f.suffix == ".png"), None)
        elif g["tipo_mat"] == "dossie":
            nome, rot, quem, tipos, extra, fonte_mini = "dossiê de pesquisa", "Pesquisa", "Rafael Nunes · pesquisa", ["pesquisas"], "dossiê e fontes", None
        elif g["tipo_mat"] == "extras":
            nome, rot, quem = "cenas extras", "Cenas extras", "Caio Martins · cenas extras"
            tipos = sorted(t for t in exts if t in ("videos", "imagens"))
            extra = " e ".join(x for x in [f"{n_img} imagens" if n_img else "", f"{n_mp4} vídeos" if n_mp4 else ""] if x)
            fonte_mini = next((f for f in sorted(fs) if f.suffix.lower() in (".png", ".jpg")), None) or next((f for f in sorted(fs) if f.suffix.lower() in (".mp4", ".mov")), None)
        elif g["tipo_mat"] == "pasta":
            nome, rot, quem = PASTA_MATERIAL.get(g["nome"], (g["nome"], "Pasta", "—"))
            tipos = {"youtube": ["videos"], "screnn record": ["videos"], "obra": ["videos"], "cortes-podcast": ["videos"],
                     "fotos": ["imagens"], "img": ["imagens"], "capas": ["imagens"], "podcast": ["audio"]}.get(g["nome"], sorted(exts))
            extra = (f"{n_mp4} trechos" if g["nome"] == "youtube" else (f"{n_img} imagens" if n_img and not n_mp4 else None))
            if g["nome"] == "screnn record":
                extra = None
            fonte_mini = (next((f for f in sorted(fs) if f.suffix.lower() in (".png", ".jpg", ".jpeg")), None)
                          or next((f for f in sorted(fs) if f.suffix.lower() in (".mp4", ".mov")), None))
        else:
            nome, rot, quem, tipos, extra, fonte_mini = "outros arquivos", "Outros", "—", sorted(exts), None, None
        mtime = max(f.stat().st_mtime for f in fs)
        gid = "-".join([g["video"][11:]] + [str(c) for c in chave[1:]]).replace(" ", "-").replace(".pdf", "")
        tam = (sum(f.stat().st_size for f in fs if f.suffix.lower() == ".pdf") if g["tipo_mat"] == "pdf"
               else sum(f.stat().st_size for f in fs))
        itens.append({"id": gid, "video": g["video"], "material": nome, "rotulo": rot, "tipos": tipos, "quem_inferido": quem,
                      "n_arquivos": len(fs), "bytes": tam, "extra": extra,
                      "data": _dt.datetime.fromtimestamp(mtime, dt.timezone.utc).isoformat(timespec="seconds"),
                      "miniatura_de": rel(fonte_mini) if fonte_mini else None})
    itens.sort(key=lambda x: x["data"], reverse=True)
    return itens


def bloco_biblioteca():
    import datetime as _dt
    tipos = {"videos": (".mp4", ".mov"), "imagens": (".jpg", ".jpeg", ".png", ".webp"), "documentos": (".md", ".pdf"),
             "pesquisas": (".json",), "audio": (".wav", ".mp3", ".m4a", ".aac")}
    cont, tam, outros, total_n, total_b, por_video = {k: 0 for k in tipos}, {k: 0 for k in tipos}, [], 0, 0, {}
    for v in sorted((RAIZ / "videos").glob("2026-*")):
        for sub in ("material", "brutos/extras"):
            for f in (v / sub).rglob("*") if (v / sub).exists() else []:
                if not f.is_file() or f.name.startswith("."):
                    continue
                e, b = f.suffix.lower(), f.stat().st_size
                total_n += 1; total_b += b; por_video[v.name] = por_video.get(v.name, 0) + b
                k = next((k for k, ex in tipos.items() if e in ex), None)
                if k:
                    cont[k] += 1; tam[k] += b
                else:
                    outros.append(rel(f))
    principal = sum(f.stat().st_size for f in (RAIZ / "videos").glob("*/brutos/principal/**/*") if f.is_file())
    refs = {d: sum(1 for f in (RAIZ / d).rglob("*") if f.is_file() and not f.name.startswith(".")) for d in
            ("00-marca/referencias", "painel/referencias")}
    itens = materiais_logicos()
    gravados = [v.name for v in sorted((RAIZ / "videos").glob("2026-*")) if any(
        f.is_file() and not f.name.startswith(".") for f in (v / "brutos/principal").glob("*"))] if True else []
    pdfs = sorted(rel(f) for f in (RAIZ / "videos").glob("2026-*/material/*.pdf"))
    roteiros = sorted(rel(f) for f in (RAIZ / "videos").glob("2026-*/roteiro.json"))
    return {"fonte": "videos/<slug>/material/ e videos/<slug>/brutos/extras/ (extensão, tamanho e data de cada arquivo); "
                     "brutos/principal/ só somado; 00-marca/referencias/ e painel/referencias/ contados",
            "como": "tipo pela extensão (vídeos .mp4 .mov · imagens .jpg .png · documentos .md .pdf · pesquisas .json · áudio "
                    ".wav .mp3 .m4a); bytes em unidades decimais (1 GB = 10^9, como o Finder). 'quem adicionou' NÃO existe "
                    "no arquivo: é a função do agente que produz aquele tipo (inferido). 'recentes' = os materiais lógicos "
                    "(regra em regra_recentes) ordenados pela data do arquivo mais novo de cada um.",
            "lido_em": AGORA,
            "linhas": [{"total_arquivos": total_n, "total_bytes": total_b, "por_tipo": {k: {"n": cont[k], "bytes": tam[k]} for k in tipos},
                        "outros": outros, "por_video_bytes": dict(sorted(por_video.items(), key=lambda x: -x[1])),
                        "brutos_principal_bytes": principal, "referencias": refs,
                        "regra_recentes": REGRA_MATERIAL,
                        "recentes": itens[:8],
                        "seguintes": itens[8:16],
                        "mais_utilizados": [
                            {"nome": "Voz do Carlos", "arquivo": "00-marca/voz-carlos.md", "tipo": "documento", "uso": f"nos {len(roteiros)} roteiros", "como": "todo roteiro é escrito a partir dele (CLAUDE.md)"},
                            {"nome": "Look da Korvu v5", "arquivo": "00-marca/cor/luts/korvu-look-v5.cube", "tipo": "cor", "uso": f"em {len(gravados)} vídeos gravados", "como": "vídeos com brutos/principal/: " + ", ".join(gravados)},
                            {"nome": "LUT de entrada V-Log", "arquivo": "00-marca/cor/luts/entrada-camera.cube", "tipo": "cor", "uso": f"em {len(gravados)} vídeos gravados", "como": "idem"},
                            {"nome": "Molde do PDF da palavra", "arquivo": "scripts/gerar_material_pdf.py", "tipo": "documento", "uso": f"em {len(pdfs)} PDFs", "como": "PDFs em videos/*/material/"}]}]}



def bloco_cambio():
    return {"fonte": "decisão do Carlos de 23/10 (docs/decisoes.md §5, 'custo de IA sempre em libras'): taxa do XE, média de "
                     "mercado em 23/10/2026",
            "como": "o custo fica guardado em US$ (preço de tabela da API) e aparece em £ = US$ × taxa; a taxa, a fonte e a data "
                    "ficam à vista na tela",
            "lido_em": AGORA, "linhas": [{"moeda": "GBP", "por_usd": 0.7465, "fonte": "XE, média de mercado", "data": "2026-10-23"}]}


def main():
    doc = json.loads(SAIDA.read_text(encoding="utf-8"))
    novos = blocos_banco()
    novos.update({
        "telas_perfil_arquivo": bloco_perfil_arquivo(),
        "telas_fila": bloco_fila(),
        "telas_publicados": bloco_publicados(),
        "telas_videos": bloco_videos(),
        "telas_prontos": bloco_prontos(),
        "telas_retratos": bloco_retratos(),
        "telas_melhores_horarios": bloco_horarios(),
        "telas_analise_trial": bloco_analise(),
        "telas_modelos": bloco_modelos(),
        "telas_exemplos": bloco_exemplos(),
        "telas_tokens": bloco_tokens(),
        "telas_biblioteca": bloco_biblioteca(),
    })
    velhos = [k for k in doc["blocos"] if not k.startswith("telas_")]
    for k in list(doc["blocos"]):
        if k.startswith("telas_"):
            del doc["blocos"][k]
    doc["blocos"].update(novos)
    doc["telas"] = ("Blocos telas_* (23/10, 2.ª rodada): os números das 5 telas em painel/design/telas/. Os blocos sem o "
                    "prefixo são os que o PORTÃO-INTERFACE aprovou na volta 3 e não mudaram: " + ", ".join(velhos))
    SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("ok:", SAIDA, "· blocos novos:", ", ".join(novos))


if __name__ == "__main__":
    main()
