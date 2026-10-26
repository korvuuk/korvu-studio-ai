#!/usr/bin/env python3
"""Sincroniza os arquivos do CONTENT AI com o banco do painel (Supabase local do painel).

Os arquivos são a fonte da verdade: este script LÊ o projeto e REGRAVA cada tabela inteira do painel, numa
transação só. Nunca escreve em videos/, 06-publicar/, 07-publicados/ nem _controle/.

Tokens e custos (23/10): lê também os registros das sessões do Claude Code deste projeto (PAINEL_REGISTROS; padrão
~/.claude/projects/<raiz com tudo o que não é letra/dígito trocado por ->) — só lê, nunca escreve lá. Essas tabelas
(execucoes, uso_execucao) são um ARQUIVO: o Claude Code apaga os registros com mais de 30 dias, então cada passagem
regrava as execuções cujo .jsonl ainda existe e MANTÉM as que sumiram (registro_presente = false). Nunca as trunca.

Biblioteca nova (24/10, o acervo de estilos): looks de 00-marca/cor/luts/*.json + 00-marca/cor/cor.md, capas, legendas,
fontes e ferramentas do painel/biblioteca.yaml, animações de videos/*/animacoes/*/brief.md e as contagens de .claude/.
As prévias dos looks são de outro script (painel/sync/previas_looks.py, o único do painel que grava): aqui só o stat().

Uso (da raiz):  uv run python painel/sync/sincronizar.py [--seco] [--ate <ISO>] [--regra-do-script]
  --seco              lê tudo e mostra o resumo, sem tocar no banco.
  --ate <ISO>         conta só as linhas dos registros com timestamp até esse instante, inclusive (reconciliar um corte).
  --regra-do-script   conta como o tokens-custos.py: o usage da 1.ª linha de cada resposta, que nas versões
                      2.1.270–2.1.304 do Claude Code é provisório — só para conferir a leitura contra o script.
  --ate e --regra-do-script gravam um número que não é o do painel: no banco do Carlos, só com --seco (ou num banco de
  teste, por PAINEL_DB_URL).
Automático: launchd `uk.korvu.painel` a cada 15 min (scripts/launchd/instalar.sh uk.korvu.painel) →
_controle/logs/painel.log, uma linha por passagem.
Banco: PAINEL_DB_URL (padrão: o Postgres do painel, 127.0.0.1:55322 — ligado por `bash painel/iniciar.sh`).
Projeto lido: PAINEL_PROJETO (padrão: CONTENT_AI_ROOT, senão a raiz real — a pasta acima de painel/). É a mesma raiz
para tudo, inclusive para o scripts/portoes.py: vídeos de uma raiz nunca se misturam com portões de outra. Os testes
(painel/tests/test_sincronizar.py) apontam para uma raiz temporária.

Saída: uma linha por passagem. Banco fora do ar, banco que recusa a gravação ou arquivo do projeto ilegível dão uma
linha "✗ …" e exit 1, sem apagar nada — a transação é desfeita e o painel continua com a passagem anterior.
Pasta dos registros inexistente: uma linha "⚠", 0 execuções lidas e o arquivo do banco mantido (não é erro).
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
import tomllib
import unicodedata
from zoneinfo import ZoneInfo
from collections import Counter
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path, PurePosixPath

import psycopg
import yaml
from psycopg.conninfo import conninfo_to_dict

CODIGO = Path(__file__).resolve().parents[2]  # onde mora o código (scripts/portoes.py)
PROJETO = Path(os.environ.get("PAINEL_PROJETO") or os.environ.get("CONTENT_AI_ROOT") or CODIGO).resolve()
os.environ["CONTENT_AI_ROOT"] = str(PROJETO)  # o portoes.py lê esta variável no import: a mesma raiz para os dois
sys.path.insert(0, str(CODIGO / "scripts"))
# O painel só lê: nem o cache do interpretador (scripts/__pycache__/portoes.*.pyc) pode nascer no projeto. O launchd roda
# sem PYTHONDONTWRITEBYTECODE, então a trava fica aqui, antes do import (PD11).
sys.dont_write_bytecode = True
import portoes  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import previas_looks  # noqa: E402  (painel/sync/: o nome esperado de cada prévia de look; quem GERA é ele, não este)

portoes.SO_LEITURA = True  # desde o import: o painel só lê; nem o cache de hashes dos portões é gravado por ele
if portoes.ROOT != PROJETO:  # portoes já importado com outra raiz: nunca misturar duas raízes
    raise SystemExit(f"✗ raízes diferentes: sincronizador {PROJETO} · portoes.py {portoes.ROOT}")

DB_URL = os.environ.get("PAINEL_DB_URL") or "postgresql://postgres:postgres@127.0.0.1:55322/postgres"
# Registros do Claude Code: o Claude Code guarda cada projeto em ~/.claude/projects/<cwd com tudo o que não é letra ou
# dígito trocado por "-"> (para esta raiz: "/" e espaço → "-", -Users-teste-Documents-CONTENT-AI).
REGISTROS = Path(os.environ.get("PAINEL_REGISTROS")
                 or Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(PROJETO))).expanduser()
AGENTES_DIR = PROJETO / ".claude" / "agents"
SKILLS_DIR = PROJETO / ".claude" / "skills"
COMANDOS_DIR = PROJETO / ".claude" / "commands"


class ErroArquivo(Exception):
    """Arquivo do projeto ilegível ou fora do formato: a passagem para e o banco fica como estava."""


@contextmanager
def lendo(p: Path):
    """Erro de leitura ou de formato dentro do bloco vira ErroArquivo com o caminho do arquivo (uma linha no log, em
    vez de um traceback)."""
    try:
        yield
    except ErroArquivo:
        raise
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, yaml.YAMLError) as e:
        rel = p.relative_to(PROJETO).as_posix() if p.is_relative_to(PROJETO) else str(p)
        msg = str(e).strip().splitlines()[0] if str(e).strip() else ""
        raise ErroArquivo(f"{rel}: {type(e).__name__}{': ' + msg if msg else ''}") from e


def ler_frontmatter(p: Path) -> tuple[dict, str]:
    txt = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", txt, re.S)
    if not m:
        return {}, txt
    # O frontmatter dos agentes não é YAML estrito (descrições com ": " no meio): uma chave por linha, como o Claude
    # Code lê.
    fm = {}
    for ln in m.group(1).splitlines():
        k, sep, v = ln.partition(":")
        if sep and re.fullmatch(r"[a-z_-]+", k.strip()):
            fm[k.strip()] = v.strip()
    return fm, m.group(2)


# ───────────────────────── equipe ─────────────────────────

def comandos_md() -> list[Path]:
    """Os comandos: arquivos .md no topo de .claude/commands/, sem os que começam por "." ou "_" (rascunho, oculto).
    Uma regra só para a Equipe (comandos de cada agente) e para o Sistema (sistema_contagens.comandos)."""
    with lendo(COMANDOS_DIR):
        return sorted(p for p in (COMANDOS_DIR.iterdir() if COMANDOS_DIR.is_dir() else [])
                      if p.is_file() and p.suffix == ".md" and not p.name.startswith((".", "_")))


# Skills que não moram em .claude/skills/ (vêm de plugin ou do próprio Claude Code) e que os agentes citam pelo nome.
SKILLS_GLOBAIS = {"dataviz", "watch"}


def skills_citadas(texto: str, locais: list[str]) -> list[str]:
    """Skills que o agente manda usar. Skill local conta pelo nome solto ou por `skills/<nome>` — não quando o nome é
    só um pedaço de caminho (`painel/supabase/` é uma pasta, não a skill supabase). Skill de plugin (`design:x`) e as
    globais contam quando aparecem entre crases."""
    achadas = {s for s in locais
               if re.search(rf"(?<![\w/-]){re.escape(s)}(?![\w-])|skills/{re.escape(s)}(?![\w-])", texto)}
    for t in re.findall(r"`([a-z][a-z0-9-]*(?::[a-z0-9-]+)?)`", texto):
        if ":" in t or t in SKILLS_GLOBAIS:
            achadas.add(t)
    return sorted(achadas)


def equipe() -> tuple[list[dict], list[dict]]:
    ficha = PROJETO / "painel" / "equipe.yaml"
    with lendo(ficha):
        cfg = yaml.safe_load(ficha.read_text(encoding="utf-8"))
        deps = [{"id": d["id"], "nome": d["nome"], "ordem": i, "descricao": d["descricao"],
                 "gerente_id": d.get("gerente")} for i, d in enumerate(cfg["departamentos"])]
        fichas = [{"id": a["id"], "nome": a["nome"], "cargo": a["cargo"], "departamento_id": a["departamento"],
                   "papel": a["papel"], "resumo": a["resumo"], "personalidade": a.get("personalidade")}
                  for a in cfg["agentes"]]
    with lendo(SKILLS_DIR):
        skills = sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith("remotion-"))
    comandos = {}
    for c in comandos_md():  # PD30: a mesma regra do rodapé do Sistema (sistema_contagens.comandos)
        with lendo(c):
            comandos[c.stem] = c.read_text(encoding="utf-8")
    fiscal = {a: p["agente"] for p in portoes.PORTOES.values() for a in p["fiscaliza"]}
    fiscaliza = {p["agente"]: p["fiscaliza"] for p in portoes.PORTOES.values()}
    agentes = []
    for a in fichas:
        arq = AGENTES_DIR / f"{a['id']}.md"
        with lendo(arq):
            fm, corpo = ler_frontmatter(arq) if arq.exists() else ({}, "")
        texto = f"{fm.get('description', '')}\n{corpo}"
        ferramentas = [t.strip() for t in str(fm.get("tools") or "").split(",") if t.strip()]
        if a["id"] == "diretor":
            usa_skills, cmds = [], sorted(comandos)
        else:
            usa_skills = skills_citadas(texto, skills)
            cmds = [c for c, t in comandos.items() if re.search(rf"(?<![\w-]){re.escape(a['id'])}(?![\w-])", t)]
        # retrato: .jpg (as fotos de 23/10) vence .png; sem arquivo, o painel mostra as iniciais
        retrato = next((f for f in (PROJETO / "painel" / "web" / "public" / "equipe" / f"{a['id']}{ext}"
                                    for ext in (".jpg", ".png")) if f.is_file()), None)
        agentes.append({
            **a,
            "descricao": fm.get("description") or ("O Claude principal (esta conversa)." if a["id"] == "diretor" else None),
            "modelo": fm.get("model") or ("opus" if a["id"] == "diretor" else None),
            "ferramentas": ferramentas, "skills": usa_skills, "comandos": cmds,
            "fiscalizado_por": fiscal.get(a["id"]), "fiscaliza": fiscaliza.get(a["id"], []),
            "retrato": f"/equipe/{retrato.name}" if retrato else None,
            "arquivo": arq.relative_to(PROJETO).as_posix() if arq.exists() else None,
        })
    faltam = sorted({p.stem for p in AGENTES_DIR.glob("*.md")} - {a["id"] for a in agentes})
    if faltam:
        print(f"⚠ agentes sem ficha em painel/equipe.yaml: {', '.join(faltam)}")
    return deps, agentes


# ───────────────────────── vídeos e portões ─────────────────────────

def tracker() -> dict[str, dict]:
    """Linhas da tabela de _controle/tracker.md, pela posição das colunas:
    Slug | Tema | Pilar | Estrutura | Hook | CTA | Estado | Atualizado."""
    arq = PROJETO / "_controle" / "tracker.md"
    out = {}
    with lendo(arq):
        for ln in arq.read_text(encoding="utf-8").splitlines():
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(c) >= 8 and re.match(r"\d{4}-\d{2}-\d{2}-", c[0]):
                out[c[0]] = {"tema": c[1], "pilar": c[2], "estrutura": c[3], "cta": c[5], "estado": c[6],
                             "atualizado": c[7]}
    return out


# Gravação = arquivo de vídeo de verdade em brutos/principal/ (subpastas incluídas): extensão de vídeo, nome não oculto
# (fora .DS_Store e os "._" do macOS), mais de 0 bytes. Só a listagem e o tamanho — os brutos (centenas de GB) não abrem.
# Mais os originais que saíram do Mac para o HD externo, listados em brutos/principal/ARQUIVADO.json (23/10).
EXT_VIDEO = {".mov", ".mp4", ".m4v", ".mxf", ".mts", ".m2ts", ".avi", ".mkv", ".3gp", ".webm"}
ARQUIVADO = "ARQUIVADO.json"  # docs/contratos.md §0, "Original arquivado fora do Mac"


DIAS_SUSPEITA = 30  # data do arquivo mais de 30 dias antes da data do slug = relógio da câmera errado


def _chave(rel: str) -> str:
    """O mesmo arquivo no disco e no ARQUIVADO.json: caminho relativo a brutos/principal/ sem diferenciar maiúsculas
    (nem a forma Unicode do nome — o macOS pode guardar em NFD)."""
    return unicodedata.normalize("NFC", rel).casefold()


def _video(rel: PurePosixPath) -> bool:
    """O filtro da listagem pelo nome: extensão de vídeo e nenhuma parte do caminho oculta (mais de 0 bytes, à parte)."""
    return rel.suffix.lower() in EXT_VIDEO and not any(x.startswith(".") for x in rel.parts)


def _segundo(t: dt.datetime) -> dt.datetime:
    """A data da gravação vale até o SEGUNDO (S1-1 do PORTÃO-DADOS, 24/10): o escritor real do ARQUIVADO.json
    (scripts/limpeza/finalizar_g3.py:8, isoformat(timespec="seconds")) corta a fração, e o painel não precisa dela.
    Truncar as datas do disco e as do manifesto do mesmo jeito deixa o vídeo com os MESMOS números antes e depois de os
    .MOV saírem, para qualquer escritor (com ou sem fração)."""
    return t.replace(microsecond=0)


def arquivados(principal: Path) -> dict[str, tuple[int, dt.datetime, dt.datetime]]:
    """brutos/principal/ARQUIVADO.json → {chave: (bytes, mtime, ctime)} dos originais que saíram do Mac, com o mesmo
    filtro da listagem do disco — assim o vídeo fica com os mesmos números antes e depois de os .MOV saírem. As datas
    (ISO 8601 com fuso) vão para UTC e para o segundo, como as do stat(). Ausente = {}; fora do formato = ErroArquivo."""
    arq = principal / ARQUIVADO
    if not arq.exists():
        return {}
    out, vistos = {}, set()
    with lendo(arq):
        man = json.loads(arq.read_text(encoding="utf-8"))
        if not isinstance(man, dict):
            raise ValueError("não é um objeto JSON")
        lista = man["arquivos"]
        if not isinstance(lista, list) or not lista:
            raise ValueError("arquivos: tem de ser uma lista com pelo menos um arquivo")
        for i, a in enumerate(lista, 1):
            if not isinstance(a, dict):
                raise ValueError(f"arquivo {i}: não é um objeto")
            nome, tamanho = a["nome"], a["bytes"]
            rel = PurePosixPath(nome) if isinstance(nome, str) else None
            if rel is None or not rel.parts or rel.is_absolute() or ".." in rel.parts:
                raise ValueError(f"arquivo {i}: nome {nome!r} não é um caminho dentro de brutos/principal/")
            if isinstance(tamanho, bool) or not isinstance(tamanho, int) or tamanho < 0:
                raise ValueError(f"arquivo {i}: bytes {tamanho!r} não é um inteiro ≥ 0")
            sha = a["sha256"]  # a prova da cópia (contrato): sem ela, o original não está conferido no HD
            if not (isinstance(sha, str) and re.fullmatch(r"[0-9a-fA-F]{64}", sha)):
                raise ValueError(f"arquivo {i}: sha256 {sha!r} não tem 64 dígitos hexadecimais")
            datas = []
            for campo in ("mtime", "ctime"):
                try:
                    t = dt.datetime.fromisoformat(a[campo])
                except (TypeError, ValueError):
                    t = None
                if t is None or t.utcoffset() is None:
                    raise ValueError(f"arquivo {i}: {campo} {a[campo]!r} não é ISO 8601 com fuso")
                datas.append(_segundo(t.astimezone(dt.timezone.utc)))
            chave = _chave(rel.as_posix())
            if chave in vistos:
                raise ValueError(f"arquivo {i}: {nome} repetido")
            vistos.add(chave)
            if _video(rel) and tamanho > 0:
                out[chave] = (tamanho, datas[0], datas[1])
    return out


def gravacao(d: Path) -> dict:
    """Só stat(): mtime = a data do próprio arquivo (vem do relógio da câmera, que está em 2024); ctime = quando o
    arquivo entrou (ou mudou) no disco do projeto. Data do arquivo muito anterior à do slug é marcada como suspeita.
    Original arquivado fora do Mac (ARQUIVADO.json) conta como gravação, com o tamanho e as datas do manifesto; o nome
    que está no disco E no manifesto conta uma vez só, pelo stat() do disco. As datas valem até o segundo (_segundo).
    Ficam também as duas partes: no Mac (o disco) e no HD (o manifesto, sem o que está no disco)."""
    principal = d / "brutos" / "principal"
    lidos: list[tuple[str, int, dt.datetime, dt.datetime]] = []  # (chave, bytes, mtime, ctime)
    with lendo(principal):
        for f in sorted(principal.rglob("*")) if principal.is_dir() else []:
            rel = PurePosixPath(f.relative_to(principal).as_posix())
            if not _video(rel) or not f.is_file():
                continue
            st = f.stat()
            if st.st_size <= 0:
                continue
            lidos.append((_chave(rel.as_posix()), st.st_size,
                          _segundo(dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc)),
                          _segundo(dt.datetime.fromtimestamp(st.st_ctime, dt.timezone.utc))))
    no_mac = list(lidos)
    no_disco = {c for c, *_ in no_mac}
    fora_do_mac = [(c, *v) for c, v in arquivados(principal).items() if c not in no_disco]
    lidos += fora_do_mac
    ultima = max((m for _, _, m, _ in lidos), default=None)
    chegou = max((c for _, _, _, c in lidos), default=None)
    try:
        previsto = dt.date.fromisoformat(d.name[:10])
    except ValueError:
        previsto = None
    suspeita = bool(ultima and previsto and ultima.date() < previsto - dt.timedelta(days=DIAS_SUSPEITA))
    return {"gravado": bool(lidos), "gravacao_arquivos": len(lidos), "gravacao_bytes": sum(b for _, b, _, _ in lidos),
            "gravacao_ultima": ultima, "gravacao_chegou": chegou, "gravacao_data_suspeita": suspeita,
            "gravacao_arquivados": len(fora_do_mac), "gravacao_arquivados_bytes": sum(b for _, b, _, _ in fora_do_mac),
            "gravacao_arquivos_no_mac": len(no_mac), "gravacao_bytes_no_mac": sum(b for _, b, _, _ in no_mac)}


def _com_fuso(txt, campo: str) -> dt.datetime:
    """ISO 8601 COM fuso (sem fuso a hora é ambígua) → datetime; senão ValueError com o campo."""
    try:
        t = dt.datetime.fromisoformat(txt)
    except (TypeError, ValueError):
        t = None
    if t is None or t.utcoffset() is None:
        raise ValueError(f"{campo} {txt!r} não é ISO 8601 com fuso")
    return t


def prontos(destinos: dict[tuple[str, str], str]) -> list[dict]:
    """05-render-pronto/<slug>/pacote.json → uma linha por pacote (docs/contratos.md §9): qa, duracao, criado_em e
    cta_palavra, e o vídeo de origem da pasta. Campo ausente = NULL; presente e fora do formato = ErroArquivo."""
    out, base = [], PROJETO / "05-render-pronto"
    for d in sorted(base.iterdir()) if base.is_dir() else []:
        pj = d / "pacote.json"
        if not d.is_dir() or d.name.startswith((".", "_")) or not pj.is_file():
            continue
        pac = _json(pj)
        with lendo(pj):
            dur, criado, palavra, qa = (pac.get(k) for k in ("duracao", "criado_em", "cta_palavra", "qa"))
            if dur is not None and (isinstance(dur, bool) or not isinstance(dur, (int, float)) or dur <= 0):
                raise ValueError(f"duracao {dur!r} não é um número de segundos > 0")
            if palavra is not None and not isinstance(palavra, str):
                raise ValueError(f"cta_palavra {palavra!r} não é texto")
            out.append({"slug": d.name, "video_slug": destinos.get(("05-render-pronto", d.name), d.name),
                        "qa": None if qa is None else str(qa), "duracao": dur,
                        "criado_em": None if criado is None else _com_fuso(criado, "criado_em"),
                        "cta_palavra": palavra if isinstance(palavra, str) and palavra.strip() else None})
    return out


def nome_curto(slug: str, tema) -> str:
    """O título curto das telas, num lugar só (era o tituloVideo do front, formato.ts): o tema antes do primeiro " — "
    (depois dele vêm notas internas), sem espaços nas pontas; tema vazio ou ausente = o slug sem a data, com espaço no
    lugar do hífen. Nem o roteiro.json nem o status.json têm um campo de título curto."""
    corte = tema.split(" — ")[0].strip() if isinstance(tema, str) else ""
    return corte or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug).replace("-", " ")


def videos(destinos: dict[tuple[str, str], str], prontos_: list[dict]) -> list[dict]:
    tr = tracker()
    # pronto = QA PASS, a mesma leitura do publicar.py: str(qa).upper() == "PASS"
    pr = {r["video_slug"] for r in prontos_ if str(r["qa"] or "").upper() == "PASS"}
    out = []
    for d in sorted((PROJETO / "videos").iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        sj = d / "status.json"
        with lendo(sj):
            st = json.loads(sj.read_text(encoding="utf-8")) if sj.exists() else {}
            t = tr.get(d.name, {})
        rj = d / "roteiro.json"
        rot = _json(rj)  # docs/contratos.md §1: versao, cta_palavra, extras
        versao, palavra, extras = rot.get("versao"), rot.get("cta_palavra"), rot.get("extras")
        try:
            prevista = dt.date.fromisoformat(d.name[:10])
        except ValueError:
            prevista = None
        out.append({"slug": d.name, "tema": t.get("tema"), "pilar": t.get("pilar"),
                    "estrutura": t.get("estrutura"), "cta": t.get("cta"),
                    "estado": st.get("estado") or t.get("estado"),
                    "atualizado": st.get("atualizado") or t.get("atualizado"),
                    "historico": json.dumps(st.get("historico") or [], ensure_ascii=False),
                    **gravacao(d), "pronto": d.name in pr,
                    "tem_roteiro": rj.is_file(), "roteiro_versao": versao if type(versao) is int else None,
                    "cta_palavra": palavra if isinstance(palavra, str) and palavra.strip() else None,
                    "roteiro_extras": len(extras) if isinstance(extras, list) else None,
                    "gravacao_prevista": prevista, "nome_curto": nome_curto(d.name, t.get("tema"))})
    return out


# ───────────────────────── biblioteca (videos/*/material, videos/*/brutos/extras) ─────────────────────────
# Uma linha por arquivo e uma por "material lógico" (regra da designer, painel/design/telas/biblioteca.md). Só a listagem
# e o stat(): nenhum arquivo é aberto. Fora do índice: pastas de vídeo com "_" ou "." (como em `videos`: _teste-*,
# _modelo), nomes ocultos em qualquer nível (.DS_Store, ._*, .gitkeep) e arquivos de 0 byte.
TIPO_EXT = {**{e: "video" for e in (".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi")},
            **{e: "imagem" for e in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic")},
            **{e: "documento" for e in (".md", ".pdf", ".txt", ".docx")},
            ".json": "pesquisa",
            **{e: "audio" for e in (".wav", ".mp3", ".m4a", ".aac", ".flac")}}  # o resto (.vtt, .srt, .svg…) = outros
# subpasta de material/ → (nome do material, quem adicionou — INFERIDO pela função de quem produz aquilo; o arquivo não
# guarda autor). 'carlos' = o próprio Carlos (não é agente). Outras pastas: o nome da pasta, quem = NULL.
PASTAS_MATERIAL = {"youtube": ("trechos do YouTube", "buscador-de-videos"),
                   "fotos": ("fotos de pesquisa", "pesquisador-de-material"),
                   "img": ("imagens das cenas", "produtor-de-extras"),
                   "capas": ("capas de referência", "pesquisador-de-material"),
                   "screnn record": ("gravação de tela", "carlos"), "screen record": ("gravação de tela", "carlos"),
                   "obra": ("obra comentada", "curador-de-obra"),
                   "podcast": ("trechos de podcast", "buscador-de-videos"),
                   "cortes-podcast": ("cortes de podcast", "buscador-de-videos")}


def _arquivos_de(base: Path) -> list[tuple[Path, tuple[str, ...], os.stat_result]]:
    """Os arquivos que contam sob `base`: não ocultos em nenhum nível, regulares, com mais de 0 byte."""
    out = []
    with lendo(base):
        for f in sorted(base.rglob("*")) if base.is_dir() else []:
            rel = f.relative_to(base).parts
            if any(x.startswith(".") for x in rel) or not f.is_file():
                continue
            st = f.stat()
            if st.st_size > 0:
                out.append((f, rel, st))
    return out


def biblioteca(slugs: list[str]) -> tuple[list[dict], list[dict]]:
    materiais, arquivos, grupos = {}, [], {}
    for slug in slugs:
        v = PROJETO / "videos" / slug
        try:
            previsto = dt.date.fromisoformat(slug[:10])
        except ValueError:
            previsto = None
        mat = _arquivos_de(v / "material")
        pdfs = sorted(f for f, rel, _ in mat if len(rel) == 1 and f.suffix.lower() == ".pdf")
        for area, lista in (("material", mat), ("brutos/extras", _arquivos_de(v / "brutos" / "extras"))):
            for f, rel, st in lista:
                obra = area == "material" and len(rel) > 1 and rel[0] == "obra"
                if area == "brutos/extras":
                    m = {"id": f"{slug}:extras", "grupo": "extras", "nome": "cenas extras",
                         "caminho": f"videos/{slug}/brutos/extras", "quem": "produtor-de-extras"}
                elif len(rel) == 1 and f.suffix.lower() == ".pdf" or (rel[0] == "_fonte" and len(rel) > 1 and pdfs):
                    # o _fonte vai para o PDF cujo nome começa o do arquivo (<pdf>-previa.png); senão, o 1.º PDF
                    pdf = f if len(rel) == 1 else max((p for p in pdfs if f.name.startswith(p.stem)),
                                                      key=lambda p: len(p.stem), default=pdfs[0])
                    nome = pdf.stem.replace("-", " ")
                    m = {"id": f"{slug}:pdf:{pdf.name}", "grupo": "pdf", "nome": nome[:1].upper() + nome[1:],
                         "caminho": pdf.relative_to(PROJETO).as_posix(), "quem": "produtor-de-material"}
                elif len(rel) == 1 and f.name in ("dossie.md", "fontes.json"):
                    m = {"id": f"{slug}:dossie", "grupo": "dossie", "nome": "dossiê de pesquisa",
                         "caminho": f"videos/{slug}/material", "quem": "pesquisador-de-material"}
                elif len(rel) == 1:
                    m = {"id": f"{slug}:soltos", "grupo": "soltos", "nome": "outros arquivos",
                         "caminho": f"videos/{slug}/material", "quem": None}
                else:
                    nome, quem = PASTAS_MATERIAL.get(rel[0], (rel[0], None))
                    m = {"id": f"{slug}:pasta:{rel[0]}", "grupo": "pasta", "nome": nome,
                         "caminho": f"videos/{slug}/material/{rel[0]}", "quem": quem}
                if m["id"] not in materiais:
                    materiais[m["id"]] = {"id": m["id"], "video_slug": slug, "grupo": m["grupo"], "nome": m["nome"],
                                          "caminho": m["caminho"], "quem_adicionou_inferido": m["quem"],
                                          "miniatura": None, "obra_estudo": m["grupo"] == "pasta" and rel[0] == "obra"}
                    grupos[m["id"]] = []
                ext = f.suffix.lower()
                quando = dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc)
                linha = {"caminho": f.relative_to(PROJETO).as_posix(), "material_id": m["id"], "video_slug": slug,
                         "area": area, "extensao": ext, "tipo": TIPO_EXT.get(ext, "outros"), "bytes": st.st_size,
                         "modificado_em": quando,
                         "data_suspeita": bool(previsto and quando.date() < previsto - dt.timedelta(days=DIAS_SUSPEITA)),
                         "obra_estudo": obra}
                arquivos.append(linha)
                grupos[m["id"]].append(linha)
    for mid, ls in grupos.items():  # miniatura: só o CAMINHO do candidato (a imagem não é gerada aqui)
        if materiais[mid]["grupo"] == "pdf":
            pngs = sorted((x for x in ls if "/_fonte/" in x["caminho"] and x["extensao"] == ".png"),
                          key=lambda x: (len(x["caminho"]), x["caminho"]))
            materiais[mid]["miniatura"] = pngs[0]["caminho"] if pngs else None
        elif materiais[mid]["grupo"] in ("pasta", "extras"):
            cand = (sorted(x["caminho"] for x in ls if x["tipo"] == "imagem")
                    or sorted(x["caminho"] for x in ls if x["tipo"] == "video"))
            materiais[mid]["miniatura"] = cand[0] if cand else None
    return list(materiais.values()), arquivos


def referencias() -> list[dict]:
    """Contagem simples por pasta (arquivos não ocultos, em qualquer nível) — fora do "Todos" da biblioteca."""
    out = []
    for pasta in ("00-marca/referencias", "painel/referencias"):
        d = PROJETO / pasta
        n = b = 0
        with lendo(d):
            for f in d.rglob("*") if d.is_dir() else []:
                if not any(x.startswith(".") for x in f.relative_to(d).parts) and f.is_file():
                    n, b = n + 1, b + f.stat().st_size
        out.append({"pasta": pasta, "arquivos": n, "bytes": b})
    return out


def mais_utilizados(vids: list[dict], materiais: list[dict]) -> list[dict]:
    """O uso pela REGRA do pipeline (CLAUDE.md), não um registro de uso: quem usa cada ativo e quantos são."""
    roteiros = sum(1 for v in vids if v["tem_roteiro"])  # roteiro.json, a mesma definição da Produção (PD25)
    gravados = sum(1 for v in vids if v["gravado"])
    pdfs = sum(1 for m in materiais if m["grupo"] == "pdf")
    linhas = [
        ("00-marca/voz-carlos.md", "Voz do Carlos", roteiros, "roteiros",
         "vídeos com videos/<slug>/roteiro.json (videos.tem_roteiro): todo roteiro é escrito a partir da voz do Carlos "
         "(CLAUDE.md)"),
        ("00-marca/cor/luts/korvu-look-v5.cube", "Look da Korvu v5", gravados, "vídeos gravados",
         "vídeos com gravação em brutos/principal/ (videos.gravado): a cor da marca vai em todo vídeo gravado — look "
         "ativo v5 (docs/decisoes.md, 18/09)"),
        ("00-marca/cor/luts/entrada-camera.cube", "LUT de entrada V-Log", gravados, "vídeos gravados",
         "vídeos com gravação em brutos/principal/ (videos.gravado): toda imagem da câmera entra por ela"),
        ("scripts/gerar_material_pdf.py", "Molde do PDF da palavra", pdfs, "PDFs da palavra",
         "PDFs de videos/<slug>/material/ (biblioteca_materiais, grupo pdf): todo PDF da palavra sai do molde")]
    return [{"arquivo": a, "nome": n, "usos": u, "unidade": un, "regra": r, "arquivo_existe": (PROJETO / a).is_file()}
            for a, n, u, un, r in linhas]


# ───────────────────────── Biblioteca nova: o acervo de estilos (24/10) ─────────────────────────
# Tela: painel/design/telas/biblioteca.md (os nomes das tabelas seguem os blocos dela). Leitura estrita: o que não se lê
# sem adivinhar fica NULL (e vira um aviso ⚠ quando é anomalia); arquivo que não se lê — JSON ou YAML quebrado, tipo
# errado no biblioteca.yaml — é ErroArquivo (✗, nada gravado). As tabelas biblioteca_* de 23/10 continuam como estão.
LUTS_DIR = PROJETO / previas_looks.LUTS
COR_MD = PROJETO / "00-marca" / "cor" / "cor.md"
# As chaves do cor.md que dão papel a um look (24/10, decisão do Carlos: o v4 foi arquivado — a antiga
# `alternativa: v4` virou `arquivados: [v4]`). `alternativa` não se lê mais: se voltar, é aviso.
PAPEL_DA_CHAVE = {"versao_ativa": "em_uso", "alternativa_medida": "alternativa", "arquivados": "arquivado"}
CHAVES_APOSENTADAS = ("alternativa",)
VERSAO_LOOK = re.compile(r"v\d+")
IRE_MAX = 110  # rosto em IRE: acima do branco legal (100) ainda é medida; acima disto é erro de digitação


def _rel(p: Path) -> str:
    return p.relative_to(PROJETO).as_posix()


def _vn(no) -> bool:
    """Um escalar de texto que é EXATAMENTE "vN" (o comentário depois do # não faz parte do valor)."""
    return isinstance(no, yaml.ScalarNode) and no.tag == "tag:yaml.org,2002:str" and bool(VERSAO_LOOK.fullmatch(no.value))


def _papeis_cor(linhas: list[str], avisos: list[str]) -> dict[str, list[tuple[str, int]]]:
    """O 1.º trecho ```yaml do cor.md → versão → [(chave, nº da linha no cor.md)], lido EXATAMENTE como está escrito:
    versao_ativa e alternativa_medida = um valor "vN"; arquivados = uma lista de "vN" (cada item com a linha dele).
    Valor ou item fora disso = ignorado, com aviso; a chave aposentada `alternativa` = aviso, não é lida. Chave repetida
    = ValueError (qual valer seria adivinhar). Quem decide o papel (e o conflito) é looks()."""
    ini = next((i for i, ln in enumerate(linhas) if ln.strip() == "```yaml"), None)
    fim = next((j for j in range(ini + 1, len(linhas)) if linhas[j].strip() == "```"), None) if ini is not None else None
    if ini is None or fim is None:
        avisos.append(f"{_rel(COR_MD)} sem o trecho ```yaml — nenhum look em uso nem alternativa na Biblioteca")
        return {}
    no = yaml.compose("\n".join(linhas[ini + 1:fim]))
    if no is not None and not isinstance(no, yaml.MappingNode):
        raise ValueError("o trecho ```yaml não é um mapa")
    out: dict[str, list[tuple[str, int]]] = {}
    vistas: set[str] = set()
    linha = lambda no_: ini + 2 + no_.start_mark.line  # noqa: E731  (1.ª linha do trecho = ini + 2; ini conta do 0)
    for k, v in no.value if no is not None else []:
        if not isinstance(k, yaml.ScalarNode):
            continue
        n = linha(k)
        if k.value in CHAVES_APOSENTADAS:
            avisos.append(f"{_rel(COR_MD)} linha {n}: a chave {k.value} não é mais lida (24/10: o look arquivado vai em "
                          "arquivados: [vN]) — ignorada")
            continue
        if k.value not in PAPEL_DA_CHAVE:
            continue
        if k.value in vistas:
            raise ValueError(f"linha {n}: {k.value} repetida")
        vistas.add(k.value)
        if k.value == "arquivados":
            if not isinstance(v, yaml.SequenceNode):
                avisos.append(f"{_rel(COR_MD)} linha {n}: arquivados = {getattr(v, 'value', None)!r} não é uma lista "
                              "[vN, …] — ignorada")
                continue
            for item in v.value:
                if not _vn(item):
                    avisos.append(f"{_rel(COR_MD)} linha {linha(item)}: item de arquivados "
                                  f"{getattr(item, 'value', None)!r} não é uma versão vN — ignorado")
                elif not any(c == "arquivados" for c, _ in out.get(item.value, [])):  # repetido na lista = um só
                    out.setdefault(item.value, []).append(("arquivados", linha(item)))
        elif _vn(v):
            out.setdefault(v.value, []).append((k.value, n))
        else:
            avisos.append(f"{_rel(COR_MD)} linha {n}: {k.value} = {getattr(v, 'value', None)!r} não é uma versão vN "
                          "— ignorada")
    if "versao_ativa" not in vistas:
        avisos.append(f"{_rel(COR_MD)}: o trecho ```yaml não diz versao_ativa — nenhum look em uso na Biblioteca")
    return out


def _data_iso(v, campo: str) -> dt.date | None:
    """AAAA-MM-DD, ou ISO 8601 com hora → a data como está escrita; ausente/null = None; outro valor = ValueError."""
    if v is None:
        return None
    try:
        if isinstance(v, str):
            return dt.date.fromisoformat(v) if len(v) == 10 else dt.datetime.fromisoformat(v).date()
    except ValueError:
        pass
    raise ValueError(f"{campo} {v!r} não é uma data ISO")


def _ficha_lut(f: Path, versao: str | None) -> dict:
    """O .json de uma LUT, inteiro (vai para looks.ficha), e os campos da tela: nome, aprovada, aprovada_em, criado_em.
    Campo ausente = NULL; presente com tipo errado, ou versao diferente da do nome do arquivo = ValueError."""
    with lendo(f):
        d = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(d, dict):
            raise ValueError("não é um objeto JSON")
        if versao is not None and "versao" in d and d["versao"] != versao:
            raise ValueError(f"versao {d['versao']!r} ≠ {versao} do nome do arquivo")
        if d.get("aprovada") is not None and type(d["aprovada"]) is not bool:
            raise ValueError(f"aprovada {d['aprovada']!r} não é true/false")
        if d.get("nome") is not None and not isinstance(d["nome"], str):
            raise ValueError(f"nome {d['nome']!r} não é texto")
        return {"nome": d.get("nome"), "aprovada": d.get("aprovada"),
                "aprovada_em": _data_iso(d.get("aprovada_em"), "aprovada_em"),
                "criado_em": _data_iso(d.get("criado_em"), "criado_em"), "arquivo_json": _rel(f),
                "ficha": json.dumps(d, ensure_ascii=False)}


def looks(avisos: list[str], do_yaml: dict[str, dict]) -> list[dict]:
    """Os cartões de "looks de cor.", na ordem da tela: vlog (o quadro da amostra como a câmera grava; existe se a
    amostra existe), rec709 (entrada-camera.cube, com o .json dela se houver) e cada korvu-look-vN.json do TOPO de
    luts/ (_descartadas/ fica fora), pela versão. Papel = a chave do cor.md que cita a versão (versao_ativa → em_uso,
    alternativa_medida → alternativa, arquivados → arquivado); citada por duas = conflito: papel NULL e aviso (escolher
    uma seria adivinhar); por nenhuma = NULL. Do item do cartão na seção looks do biblioteca.yaml (25/10): nome (o do
    yaml vence; sem ele, o "nome" do .json — que fica sempre na ficha), descricao (a frase da tela) e o rosto em IRE
    (só vN; a tabela do cor.md não é mais lida). Cartão sem item = esses campos NULL (nome: o do .json), sem aviso;
    item de um id que não é cartão desta passagem = aviso. Prévia = o caminho da imagem esperada
    (previas_looks.esperadas) se ela existe — só o stat()."""
    with lendo(COR_MD):
        texto = COR_MD.read_text(encoding="utf-8") if COR_MD.is_file() else None
        if texto is None:
            avisos.append(f"{_rel(COR_MD)} não encontrado — nenhum look em uso, alternativa nem arquivado")
        papeis = _papeis_cor(texto.splitlines(), avisos) if texto is not None else {}
    with lendo(LUTS_DIR):
        previas = previas_looks.esperadas(PROJETO)
        jsons = sorted(((m.group(1), f) for f in (LUTS_DIR.iterdir() if LUTS_DIR.is_dir() else [])
                        if (m := previas_looks.LOOK_JSON.match(f.name)) and f.is_file()), key=lambda x: int(x[0][1:]))
        entrada = LUTS_DIR / previas_looks.ENTRADA
        out: list[dict] = []

        def linha(ident: str, tipo: str, **campos) -> None:
            p = previas.get(ident)
            esperada = f"{previas_looks.SAIDA}/{p['nome']}" if p else None
            y = do_yaml.get(ident) or {}
            ln = {"id": ident, "ordem": len(out), "tipo": tipo, "nome": None, "descricao": None, "papel": None,
                  "chaves_cor_md": [], "linhas_cor_md": [], "aprovada": None, "aprovada_em": None, "criado_em": None,
                  "arquivo_json": None, "ficha": None, "cube": None, "cube_sha256": None, "rosto_ire": None,
                  "rosto_ire_em": None, "rosto_ire_amostra": None,
                  "previa": esperada if esperada and (PROJETO / esperada).is_file() else None,
                  "previa_esperada": esperada, **campos}
            ln["nome"] = y.get("nome") or ln["nome"]  # o nome da tela vence; o do .json continua na ficha
            ln["descricao"] = y.get("desc")
            if tipo == "look" and y.get("rosto_ire") is not None:
                ln.update(rosto_ire=y["rosto_ire"], rosto_ire_em=y["medido_em"], rosto_ire_amostra=y["amostra"])
            out.append(ln)

        if (PROJETO / previas_looks.AMOSTRA).is_file():
            linha("vlog", "referencia")
        if entrada.is_file():
            ej = entrada.with_suffix(".json")
            linha("rec709", "base", **(_ficha_lut(ej, None) if ej.is_file() else {}), cube=_rel(entrada),
                  cube_sha256=previas_looks.sha256(entrada))
        for versao, f in jsons:
            chaves = papeis.get(versao, [])
            papel = PAPEL_DA_CHAVE[chaves[0][0]] if len(chaves) == 1 else None
            if len(chaves) > 1:
                avisos.append(f"{_rel(COR_MD)}: o {versao} está ao mesmo tempo em "
                              f"{' e '.join(f'{k} (linha {n})' for k, n in chaves)} — sem estado na Biblioteca até o "
                              "cor.md decidir")
            cube = f.with_suffix(".cube")
            if not cube.is_file():
                avisos.append(f"{_rel(f)} sem o {cube.name} ao lado — sem prévia")
            linha(versao, "look", **_ficha_lut(f, versao), papel=papel, chaves_cor_md=[k for k, _ in chaves],
                  linhas_cor_md=[n for _, n in chaves], cube=_rel(cube) if cube.is_file() else None,
                  cube_sha256=previas_looks.sha256(cube) if cube.is_file() else None)
    cartoes = {ln["id"] for ln in out}
    for ident, y in do_yaml.items():
        if ident not in cartoes:  # um look que saiu de luts/ (ex.: para _descartadas/) não para o painel
            avisos.append(f"{_rel(ACERVO_YAML)}: looks[{y['indice']}] {ident} não é um cartão desta passagem (look de "
                          f"{previas_looks.LUTS}/, ou vlog/rec709 sem a amostra/entrada) — item ignorado")
    nas_linhas = {ln["id"] for ln in out if ln["tipo"] == "look"}
    for versao, chaves in papeis.items():
        if versao not in nas_linhas:
            for k, n in chaves:
                avisos.append(f"{_rel(COR_MD)} linha {n}: {k} = {versao}, mas não há korvu-look-{versao}.json no topo "
                              f"de {previas_looks.LUTS}/")
    return out


ACERVO_YAML = PROJETO / "painel" / "biblioteca.yaml"
SECOES_ACERVO = ("capas", "legendas", "fontes", "ferramentas", "modelos", "looks")
PASTAS_CAPA = ("07-publicados", "06-publicar", "05-render-pronto")  # onde procurar <slug>/capa/capa.png, nesta ordem
ID_ESTILO = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SLUG_PACOTE = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*")
BRAND_TS = PROJETO / "remotion" / "src" / "brand.ts"
ESTILO_TS = {"normal": "normal", "italico": "italic"}  # estilo do yaml → o 1.º argumento do loadFont no brand.ts


def _texto(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _caminho(v) -> bool:
    """Caminho relativo dentro do projeto, com /: sem / no começo, sem .. e sem \\."""
    return _texto(v) and not v.startswith("/") and "\\" not in v and ".." not in PurePosixPath(v).parts


def _versao_de(v) -> bool:
    return (isinstance(v, dict) and set(v) <= {"arquivo", "pacote", "chave"} and _caminho(v.get("arquivo"))
            and all(_texto(x) for x in v.values())
            and ("pacote" in v) == v["arquivo"].endswith(".json") and ("chave" in v) == v["arquivo"].endswith(".toml"))


def _data_ok(v) -> bool:
    """Data AAAA-MM-DD: o YAML já entrega um date (sem aspas) ou o texto ISO (com aspas)."""
    if isinstance(v, dt.date) and not isinstance(v, dt.datetime):
        return True
    try:
        return isinstance(v, str) and len(v) == 10 and bool(dt.date.fromisoformat(v))
    except ValueError:
        return False


# campo → (obrigatório, validador, o que tem de ser)
_ID = (True, lambda v: isinstance(v, str) and bool(ID_ESTILO.fullmatch(v)), "um id em minúsculas-com-hífen")
_NOME = (True, _texto, "texto")
_FICHA = (True, lambda v: v is None or _caminho(v), "null ou um caminho relativo no projeto")
_BOOL = (True, lambda v: type(v) is bool, "true/false")
CAMPOS_CAPA = {"id": _ID, "nome": _NOME, "descricao": _NOME, "ficha": _FICHA, "em_uso": _BOOL,
               "exemplos": (True, lambda v: isinstance(v, list) and len(v) > 0 and len(set(map(str, v))) == len(v)
                            and all(isinstance(s, str) and SLUG_PACOTE.fullmatch(s) for s in v),
                            "uma lista de slugs de pacote (AAAA-MM-DD-…), sem repetir")}
CAMPOS_LEGENDA = {"id": _ID, "nome": _NOME, "descricao": _NOME, "ficha": _FICHA, "em_uso": _BOOL}
CAMPOS_FONTE = {"familia": _NOME, "uso": _NOME,
                "remotion": (True, lambda v: v is None or (isinstance(v, str) and bool(re.fullmatch(r"[A-Za-z0-9]+", v))),
                             "null ou o nome do pacote em @remotion/google-fonts/"),
                "estilo": (True, lambda v: v in ESTILO_TS, "normal ou italico"),
                "pesos": (True, lambda v: isinstance(v, list) and len(v) > 0 and len(set(map(str, v))) == len(v)
                          and all(type(p) is int and 100 <= p <= 1000 for p in v), "uma lista de pesos 100–1000"),
                "reserva": (False, lambda v: type(v) is bool, "true/false")}
# a stack ganhou tipo e desc em 24/10 (decisão do Carlos: para quem chegar pelo GitHub); no banco, desc = descricao
CAMPOS_FERRAMENTA = {"nome": _NOME, "tipo": _NOME, "desc": _NOME,
                     "versao": (False, _versao_de, "{arquivo: x.json, pacote: p} · {arquivo: x.toml, chave: a.b} · "
                                                   "{arquivo: outro}")}
CAMPOS_MODELO = {"modelo": (True, lambda v: isinstance(v, str) and bool(re.fullmatch(r"[a-z0-9][a-z0-9._-]*", v)),
                            "o id do modelo nos registros (ex.: claude-opus-5-5)"),
                 "desc": _NOME}
# Por cartão de look: o nome e a frase da tela (25/10, maquete aprovada) e o rosto medido (a tabela do cor.md por regex
# saiu). id = vlog, rec709 ou vN. Com rosto_ire, medido_em e fonte são obrigatórios; sem rosto_ire, os três campos da
# medida (medido_em, amostra, fonte) não entram; rosto só em vN (vlog e rec709 são referência) — senão ValueError.
CAMPOS_LOOK = {"id": (True, lambda v: isinstance(v, str) and (v in ("vlog", "rec709") or bool(VERSAO_LOOK.fullmatch(v))),
                      "vlog, rec709 ou uma versão vN"),
               "nome": (False, _texto, "texto"),
               "desc": (False, _texto, "texto"),
               "rosto_ire": (False, lambda v: type(v) in (int, float) and 0 <= v <= IRE_MAX,
                             f"um número de 0 a {IRE_MAX} (IRE)"),
               "medido_em": (False, lambda v: _data_ok(v), "uma data AAAA-MM-DD"),
               "amostra": (False, _texto, "texto"),
               "fonte": (False, _texto, "texto (arquivo:linhas de onde veio o número)")}
MEDIDA_LOOK = ("medido_em", "amostra", "fonte")  # só com rosto_ire


def _medida_do_look(x: dict, onde: str) -> dict:
    """As regras entre campos de um item de looks (o _item confere cada campo sozinho)."""
    if "rosto_ire" in x:
        if not VERSAO_LOOK.fullmatch(x["id"]):
            raise ValueError(f"{onde}: rosto_ire só em look vN ({x['id']} é referência, não look)")
        for k in ("medido_em", "fonte"):
            if k not in x:
                raise ValueError(f"{onde}: falta {k} (obrigatório com rosto_ire)")
    else:
        sobra = [k for k in MEDIDA_LOOK if k in x]
        if sobra:
            raise ValueError(f"{onde}: {', '.join(sobra)} sem rosto_ire")
    return x


def _item(x, onde: str, campos: dict) -> dict:
    """Um item do biblioteca.yaml: um mapa só com as chaves conhecidas, as obrigatórias presentes e cada valor do tipo
    certo — senão ValueError com o lugar (ex.: capas[1].em_uso)."""
    if not isinstance(x, dict):
        raise ValueError(f"{onde}: não é um mapa")
    fora = sorted(map(str, set(x) - set(campos)))
    if fora:
        raise ValueError(f"{onde}: chave desconhecida {', '.join(fora)}")
    for k, (obrigatorio, valido, tipo) in campos.items():
        if k not in x:
            if obrigatorio:
                raise ValueError(f"{onde}: falta {k}")
        elif not valido(x[k]):
            raise ValueError(f"{onde}.{k}: {x[k]!r} não é {tipo}")
    return x


def _unicos(itens: list[dict], chave: str, secao: str) -> None:
    vistos: set = set()
    for i, x in enumerate(itens):
        if x[chave] in vistos:
            raise ValueError(f"{secao}[{i}]: {chave} {x[chave]!r} repetido")
        vistos.add(x[chave])


def _fontes_do_brand_ts() -> dict[str, tuple[str, list[int]] | None] | None:
    """remotion/src/brand.ts → pacote de @remotion/google-fonts → (estilo, pesos) da chamada do loadFont importado dele;
    pacote importado sem chamada reconhecível = None; sem brand.ts = None. Só CONFERE o biblioteca.yaml (a fonte da
    tela é o yaml)."""
    if not BRAND_TS.is_file():
        return None
    with lendo(BRAND_TS):
        txt = BRAND_TS.read_text(encoding="utf-8")
    alias = dict(re.findall(r'import\s*\{\s*loadFont\s+as\s+(\w+)\s*\}\s*from\s*"@remotion/google-fonts/(\w+)"', txt))
    out: dict[str, tuple[str, list[int]] | None] = {p: None for p in alias.values()}
    for a, estilo, pesos in re.findall(r'\b(\w+)\(\s*"(normal|italic)"\s*,\s*\{\s*weights:\s*\[([^\]]*)\]', txt):
        if a in alias:
            out[alias[a]] = (estilo, sorted(int(p) for p in re.findall(r'"(\d+)"', pesos)))
    return out


def _versao_lida(v: dict, nome: str, avisos: list[str]) -> tuple[str | None, str]:
    """(a versão em uso, de onde) de uma ferramenta: dependencies/devDependencies do package.json, a chave do .toml ou a
    1.ª linha não vazia do arquivo. Não achou = NULL e aviso (o arquivo não é do Carlos: não para o painel)."""
    de = v["arquivo"] + (f"#{v['pacote']}" if "pacote" in v else f"#{v['chave']}" if "chave" in v else "")
    try:
        txt = (PROJETO / v["arquivo"]).read_text(encoding="utf-8")
        if "pacote" in v:
            d = json.loads(txt)
            val = next((d[s][v["pacote"]] for s in ("dependencies", "devDependencies")
                        if isinstance(d, dict) and isinstance(d.get(s), dict) and v["pacote"] in d[s]), None)
        elif "chave" in v:
            val = tomllib.loads(txt)
            for k in v["chave"].split("."):
                val = val.get(k) if isinstance(val, dict) else None
        else:
            val = next((ln.strip() for ln in txt.splitlines() if ln.strip()), None)
    except (OSError, ValueError):  # TOMLDecodeError, JSONDecodeError e UnicodeDecodeError são ValueError
        val = None
    if isinstance(val, bool) or not isinstance(val, (str, int, float)):
        val = None
    if val is None:
        avisos.append(f"{_rel(ACERVO_YAML)}: versão de {nome} não encontrada em {de} — NULL")
    return (None if val is None else str(val)), de


def ler_acervo_yaml(avisos: list[str]) -> dict[str, list[dict]] | None:
    """painel/biblioteca.yaml (fonte do Carlos, como o equipe.yaml; formato em docs/contratos.md §12), leitura estrita:
    cada seção é uma lista de itens validados (_item) e sem repetição. Ausente = None, com aviso; seção ausente = vazia,
    com aviso; quebrado ou fora do formato = ErroArquivo."""
    if not ACERVO_YAML.is_file():
        avisos.append(f"{_rel(ACERVO_YAML)} não encontrado — capas, legendas, fontes, ferramentas, modelos e rostos "
                      "vazios na Biblioteca")
        return None
    with lendo(ACERVO_YAML):
        cfg = yaml.safe_load(ACERVO_YAML.read_text(encoding="utf-8"))
        if not isinstance(cfg, dict):
            raise ValueError(f"não é um mapa com {', '.join(SECOES_ACERVO)}")
        fora = sorted(map(str, set(cfg) - set(SECOES_ACERVO)))
        if fora:
            raise ValueError(f"seção desconhecida {', '.join(fora)}")
        for s in SECOES_ACERVO:
            if s not in cfg:
                avisos.append(f"{_rel(ACERVO_YAML)} sem a seção {s}: — vazia na Biblioteca")
            elif not isinstance(cfg[s], list):
                raise ValueError(f"{s}: não é uma lista")
        campos = {"capas": (CAMPOS_CAPA, "id"), "legendas": (CAMPOS_LEGENDA, "id"), "fontes": (CAMPOS_FONTE, "familia"),
                  "ferramentas": (CAMPOS_FERRAMENTA, "nome"), "modelos": (CAMPOS_MODELO, "modelo"),
                  "looks": (CAMPOS_LOOK, "id")}
        out = {}
        for s, (c, chave) in campos.items():
            out[s] = [_item(x, f"{s}[{i}]", c) for i, x in enumerate(cfg.get(s) or [])]
            _unicos(out[s], chave, s)
        for i, x in enumerate(out["looks"]):
            _medida_do_look(x, f"looks[{i}]")
        return out


def looks_do_yaml(cfg: dict[str, list[dict]] | None) -> dict[str, dict]:
    """id do cartão → o item da seção looks do biblioteca.yaml, já no tipo do banco (o que falta = None)."""
    def data(v):
        return None if v is None else v if isinstance(v, dt.date) else dt.date.fromisoformat(v)
    return {x["id"]: {"indice": i, "nome": x["nome"].strip() if x.get("nome") else None,
                      "desc": x["desc"].strip() if x.get("desc") else None,
                      "rosto_ire": Decimal(str(x["rosto_ire"])) if "rosto_ire" in x else None,
                      "medido_em": data(x.get("medido_em")),
                      "amostra": x["amostra"].strip() if x.get("amostra") else None}
            for i, x in enumerate((cfg or {}).get("looks", []))}


def acervo(destinos: dict[tuple[str, str], str], avisos: list[str], cfg: dict[str, list[dict]] | None
           ) -> dict[str, list[dict]]:
    """O biblioteca.yaml já lido (ler_acervo_yaml) → capa_estilos (+ exemplos), legenda_estilos, fontes,
    sistema_ferramentas e modelos_descricao. A capa de exemplo é <pasta>/<slug>/capa/capa.png na 1.ª de 07-publicados,
    06-publicar, 05-render-pronto que a tiver (o pacote anda entre elas); a ficha e a capa que não existem ficam
    marcadas, com aviso."""
    out: dict[str, list[dict]] = {"capa_estilos": [], "capa_estilos_exemplos": [], "legenda_estilos": [], "fontes": [],
                                  "sistema_ferramentas": [], "modelos_descricao": []}
    if cfg is None:
        return out
    capas, legendas, fontes_, ferramentas, modelos = (cfg[s] for s in ("capas", "legendas", "fontes", "ferramentas",
                                                                       "modelos"))

    def estilo(x: dict, i: int, secao: str) -> dict:
        existe = None if x["ficha"] is None else (PROJETO / x["ficha"]).is_file()
        if existe is False:
            avisos.append(f"{_rel(ACERVO_YAML)}: {secao}[{i}] ({x['id']}): a ficha {x['ficha']} não existe")
        return {"id": x["id"], "ordem": i, "nome": x["nome"].strip(), "descricao": x["descricao"].strip(),
                "ficha": x["ficha"], "ficha_existe": existe, "em_uso": x["em_uso"]}

    for i, x in enumerate(capas):
        out["capa_estilos"].append(estilo(x, i, "capas"))
        for j, slug in enumerate(x["exemplos"]):
            pasta = next((p for p in PASTAS_CAPA if (PROJETO / p / slug / "capa" / "capa.png").is_file()), None)
            if pasta is None:
                avisos.append(f"{_rel(ACERVO_YAML)}: capa de exemplo {slug} ({x['id']}) não encontrada — "
                              f"<slug>/capa/capa.png em {', '.join(PASTAS_CAPA)}")
            out["capa_estilos_exemplos"].append({
                "estilo_id": x["id"], "ordem": j, "slug": slug, "pasta": pasta,
                "caminho": f"{pasta}/{slug}/capa/capa.png" if pasta else None,
                "video_slug": destinos.get((pasta, slug)) if pasta else None})
    out["legenda_estilos"] = [estilo(x, i, "legendas") for i, x in enumerate(legendas)]
    brand = _fontes_do_brand_ts()
    for i, x in enumerate(fontes_):
        pesos = sorted(x["pesos"])
        confere = None
        if x["remotion"] is not None and brand is not None:
            if x["remotion"] not in brand:
                confere = False
            elif brand[x["remotion"]] is not None:
                confere = brand[x["remotion"]] == (ESTILO_TS[x["estilo"]], pesos)
        if confere is False:
            avisos.append(f"{_rel(ACERVO_YAML)}: fonte {x['familia']} não bate com o remotion/src/brand.ts "
                          f"(@remotion/google-fonts/{x['remotion']}: {brand.get(x['remotion'], 'não importado')})")
        elif confere is None and x["remotion"] is not None:
            avisos.append(f"{_rel(ACERVO_YAML)}: fonte {x['familia']}: não deu para conferir no remotion/src/brand.ts")
        out["fontes"].append({"familia": x["familia"].strip(), "ordem": i, "remotion": x["remotion"],
                              "estilo": x["estilo"], "pesos": pesos, "uso": x["uso"].strip(),
                              "reserva": x.get("reserva", False), "confere_brand_ts": confere})
    for i, x in enumerate(ferramentas):
        versao, de = _versao_lida(x["versao"], x["nome"], avisos) if "versao" in x else (None, None)
        out["sistema_ferramentas"].append({"nome": x["nome"].strip(), "ordem": i, "tipo": x["tipo"].strip(),
                                           "descricao": x["desc"].strip(), "versao": versao, "versao_de": de})
    for i, x in enumerate(modelos):
        com_preco = x["modelo"] in PRECOS
        if not com_preco:  # consumo só tem modelo com preço: a frase não teria onde aparecer no Sistema
            avisos.append(f"{_rel(ACERVO_YAML)}: modelos[{i}] {x['modelo']} não está na tabela de preços (PRECOS) — a "
                          "frase não aparece no Sistema")
        out["modelos_descricao"].append({"modelo": x["modelo"], "ordem": i, "descricao": x["desc"].strip(),
                                         "com_preco": com_preco})
    return out


CODIGO_EXTRA = re.compile(r"E\d+")
TITULO_BRIEF = re.compile(r"# (E\d+) — (.+)")
LINHAS_TITULO = re.compile(r"(.+?) \((L\d+[A-Z]?(?: \+ L\d+[A-Z]?)*)\)")
CAMPOS_BRIEF = {"video": re.compile(r"- \*\*Vídeo:\*\* (\S+)"),
                "modo": re.compile(r"- \*\*Modo:\*\* `(full|split|card)`"),
                "duracao": re.compile(r"- \*\*Linhas?:\*\* .*?\*\*duração (\d+(?:,\d+)?) s\*\*")}
ASPAS = (('"', '"'), ("“", "”"))


def _mp4_da_animacao(v: Path, codigo: str) -> Path | None:
    """O .mp4 que faz a animação contar como renderizada, procurado nesta ordem: videos/<slug>/edicao/extras/<Exx>.mp4
    (depois do ingest), videos/<slug>/brutos/extras/<Exx>.mp4 ou <Exx>-*.mp4 (a captura do export, docs/contratos.md
    §0) e qualquer .mp4 dentro de videos/<slug>/animacoes/<Exx>/ (subpastas incluídas). Oculto ou vazio não conta."""
    cands = [v / "edicao" / "extras" / f"{codigo}.mp4"]
    be, pasta = v / "brutos" / "extras", v / "animacoes" / codigo
    cands += sorted(f for f in (be.iterdir() if be.is_dir() else [])
                    if f.suffix.lower() == ".mp4" and (f.stem == codigo or f.name.startswith(f"{codigo}-")))
    cands += sorted(f for f in pasta.rglob("*") if f.suffix.lower() == ".mp4")
    return next((f for f in cands if f.is_file() and f.stat().st_size > 0
                 and not any(x.startswith(".") for x in f.relative_to(v).parts)), None)


def animacoes(slugs: list[str], avisos: list[str]) -> list[dict]:
    """videos/<slug>/animacoes/<Exx>/brief.md (as pastas de vídeo de `videos`) → uma linha por animação. Leitura
    estrita do cabeçalho do brief (as linhas antes do 1.º "---"): título e linhas de "# Exx — título (L08 + L09)" (o Exx
    tem de ser o da pasta; aspas em volta do título saem), "- **Vídeo:** <slug>", "- **Modo:** `split`" e
    "**duração 6,76 s**" na linha "- **Linha(s):**". Campo fora do padrão = NULL, com aviso. renderizada = há o .mp4
    (_mp4_da_animacao); sem ele = roteirizada."""
    out = []
    for slug in slugs:
        v = PROJETO / "videos" / slug
        base = v / "animacoes"
        with lendo(base):
            pastas = sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))) \
                if base.is_dir() else []
        for p in pastas:
            b = p / "brief.md"
            if not CODIGO_EXTRA.fullmatch(p.name):
                avisos.append(f"{_rel(p)}: pasta de animação fora do padrão Exx — ignorada")
                continue
            if not b.is_file():
                avisos.append(f"{_rel(p)}: sem brief.md — ignorada")
                continue
            with lendo(b):
                linhas = b.read_text(encoding="utf-8").splitlines()
                cab = [ln.strip() for ln in linhas[:next((i for i, ln in enumerate(linhas) if ln.strip() == "---"),
                                                        len(linhas))]]
                titulo, lin = None, []
                m = TITULO_BRIEF.fullmatch(cab[0]) if cab else None
                if m and m.group(1) == p.name:
                    resto = m.group(2).strip()
                    m2 = LINHAS_TITULO.fullmatch(resto)
                    titulo, lin = (m2.group(1).strip(), m2.group(2).split(" + ")) if m2 else (resto, [])
                    for a, f in ASPAS:
                        if len(titulo) > 2 and titulo.startswith(a) and titulo.endswith(f):
                            titulo = titulo[1:-1].strip()
                            break
                elif m:
                    avisos.append(f"{_rel(b)}: o título diz {m.group(1)}, a pasta é {p.name} — título NULL")
                campos = {k: next((mm.group(1) for ln in cab if (mm := rx.match(ln))), None)
                          for k, rx in CAMPOS_BRIEF.items()}
                faltam = [n for n, val in (("título", titulo), ("vídeo", campos["video"]), ("modo", campos["modo"]),
                                           ("duração", campos["duracao"])) if val is None]
                if faltam:
                    avisos.append(f"{_rel(b)}: sem {', '.join(faltam)} no cabeçalho — NULL")
                if campos["video"] is not None and campos["video"] != slug:
                    avisos.append(f"{_rel(b)}: o brief diz Vídeo {campos['video']}, a pasta é {slug}")
                mp4 = _mp4_da_animacao(v, p.name)
            out.append({"id": f"{slug}/{p.name}", "video_slug": slug, "codigo": p.name, "titulo": titulo,
                        "linhas": lin, "modo": campos["modo"],
                        "duracao_s": Decimal(campos["duracao"].replace(",", ".")) if campos["duracao"] else None,
                        "video_do_brief": campos["video"], "renderizada": mp4 is not None,
                        "mp4": _rel(mp4) if mp4 else None, "brief": _rel(b)})
    return out


def contagens_do_sistema() -> list[dict]:
    """O rodapé do Sistema: agentes = arquivos .md no topo de .claude/agents/; habilidades = pastas do topo de
    .claude/skills/ com um SKILL.md dentro; comandos = arquivos .md no topo de .claude/commands/. Nome começado por "."
    ou "_" fica fora; pasta ausente = 0. (O Atlas, diretor, não tem .md: a tabela agentes tem um a mais.)"""
    def itens(d: Path) -> list[Path]:
        with lendo(d):
            return [p for p in d.iterdir() if not p.name.startswith((".", "_"))] if d.is_dir() else []
    return [{"agentes": sum(1 for p in itens(AGENTES_DIR) if p.is_file() and p.suffix == ".md"),
             "habilidades": sum(1 for p in itens(SKILLS_DIR) if p.is_dir() and (p / "SKILL.md").is_file()),
             "comandos": len(comandos_md())}]


# ───────────────────────── calendário (_controle/calendario.md, bloco vagas_semanais) ─────────────────────────
# O bloco é o 1.º trecho ```yaml do calendario.md (o mesmo que o publicar.py lê): `fuso:` (padrão Europe/London) e
# `vagas_semanais:` = mapa dia → "HH:MM" ou lista de "HH:MM". Dia em português, com ou sem acento e "-feira".
DIAS_SEMANA = {"segunda": 1, "terca": 2, "quarta": 3, "quinta": 4, "sexta": 5, "sabado": 6, "domingo": 7}


def _dia(nome) -> tuple[int, str]:
    n = "".join(c for c in unicodedata.normalize("NFKD", str(nome).strip().lower()) if not unicodedata.combining(c))
    n = n.removesuffix("-feira")
    if n not in DIAS_SEMANA:
        raise ValueError(f"vagas_semanais: dia {nome!r} não é um dia da semana")
    return DIAS_SEMANA[n], n


def _hora_vaga(h, dia: str) -> dt.time:
    if type(h) is int and 0 <= h < 24 * 60:  # YAML 1.1: 19:00 sem aspas chega como 1140 (sexagesimal)
        return dt.time(h // 60, h % 60)
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", h.strip()) if isinstance(h, str) else None
    if m and int(m[1]) < 24 and int(m[2]) < 60:
        return dt.time(int(m[1]), int(m[2]))
    raise ValueError(f"vagas_semanais: hora {h!r} de {dia} não é HH:MM")


def calendario_vagas() -> tuple[list[dict], bool, bool]:
    """(vagas, achou o bloco, o bloco diz o fuso). Arquivo ou bloco vagas_semanais ausente = (vazio, False, False) — a
    passagem avisa com ⚠; bloco presente e quebrado (YAML inválido, dia ou hora fora do formato, vaga repetida, fuso
    desconhecido) = ErroArquivo. Fuso: o `fuso:` do bloco; sem ele, a ordem do publicar.py (fuso() em scripts/publicar.py:
    TZ_PUBLICACAO e depois Europe/London) — mas o publicar.py lê o TZ_PUBLICACAO do .env, que o painel não lê: a passagem
    avisa (⚠) para pôr o `fuso:` no bloco (PD26)."""
    arq = PROJETO / "_controle" / "calendario.md"
    if not arq.exists():
        return [], False, False
    out, vistas = [], set()
    with lendo(arq):
        m = re.search(r"```ya?ml\n(.*?)```", arq.read_text(encoding="utf-8"), re.S)
        cfg = yaml.safe_load(m.group(1)) if m else None
        if cfg is None or (isinstance(cfg, dict) and "vagas_semanais" not in cfg):
            return [], False, False
        if not isinstance(cfg, dict):
            raise ValueError("o bloco yaml não é um mapa")
        vagas, fuso = cfg["vagas_semanais"], cfg.get("fuso") or os.environ.get("TZ_PUBLICACAO") or "Europe/London"
        if not isinstance(vagas, dict) or not vagas:
            raise ValueError("vagas_semanais: tem de ser um mapa dia → hora com pelo menos uma vaga")
        try:
            ZoneInfo(str(fuso))
        except (ValueError, KeyError):
            raise ValueError(f"fuso {fuso!r} desconhecido") from None
        for nome, horas in vagas.items():
            n, dia = _dia(nome)
            for h in horas if isinstance(horas, list) else [horas]:
                hora = _hora_vaga(h, dia)
                if (n, hora) in vistas:
                    raise ValueError(f"vagas_semanais: {dia} {hora:%H:%M} repetida")
                vistas.add((n, hora))
                out.append({"dia_semana": n, "dia": dia, "hora": hora, "fuso": str(fuso)})
    return out, True, bool(cfg.get("fuso"))


def nao_publicar(destinos: dict[tuple[str, str], str]) -> list[dict]:
    """_controle/nao-publicar.json (opcional: ausente = nenhuma trava) → tabela nao_publicar. Formato, como o
    _controle/gauntlet-legado.json: {"travas": [{"slug", "motivo", "desde": "AAAA-MM-DD"}]}. Inválido = ErroArquivo."""
    arq = PROJETO / "_controle" / "nao-publicar.json"
    if not arq.exists():
        return []
    out, vistos = [], set()
    with lendo(arq):
        travas = json.loads(arq.read_text(encoding="utf-8"))["travas"]
        if not isinstance(travas, list):
            raise ValueError("travas: tem de ser uma lista")
        for i, t in enumerate(travas, 1):
            slug, motivo, desde = t["slug"], t["motivo"], t["desde"]
            if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
                raise ValueError(f"trava {i}: slug {slug!r} inválido")
            if not isinstance(motivo, str) or not motivo.strip():
                raise ValueError(f"trava {i}: sem motivo")
            if not isinstance(desde, str):
                raise ValueError(f"trava {i}: desde {desde!r} não é AAAA-MM-DD")
            desde = dt.date.fromisoformat(desde)
            if slug in vistos:
                raise ValueError(f"trava {i}: {slug} repetido")
            vistos.add(slug)
            video = next((destinos[(p, slug)] for p in PASTAS_DE_VIDEO if (p, slug) in destinos), slug)
            out.append({"slug": slug, "video_slug": video, "motivo": motivo.strip(), "desde": desde})
    return out


def portoes_e_veredictos() -> tuple[list[dict], list[dict]]:
    """Alvos: cada vídeo (pauta, roteiro, imagem, corte), cada PASTA de 06-publicar/ (publicacao) e o painel/
    (design, interface, dados)."""
    estados, vs = [], []
    alvos = [(d, list(portoes.EXIGIDOS_PACOTE)) for d in sorted((PROJETO / "videos").iterdir())
             if d.is_dir() and not d.name.startswith("_")]
    alvos += [(d, ["publicacao"]) for d in sorted((PROJETO / "06-publicar").iterdir()) if d.is_dir()]
    alvos.append((PROJETO / "painel", list(portoes.EXIGIDOS_SISTEMA)))  # o GAUNTLET do próprio painel
    for alvo, nomes in alvos:
        rel = alvo.relative_to(PROJETO).as_posix()
        with lendo(alvo / portoes.LIVRO):
            livro = portoes.ler_livro(alvo)
        with lendo(alvo):
            for p in nomes:
                e = portoes.estado(alvo, p)
                estados.append({"alvo": rel, "slug": alvo.name, "portao": p, "agente": e["agente"],
                                "status": e["status"], "motivos": json.dumps(e["motivos"], ensure_ascii=False),
                                "volta": e["volta"]})
        with lendo(alvo / portoes.LIVRO):
            for ordem, v in enumerate(livro["veredictos"]):  # a posição no livro: a chave com o alvo (PD20)
                vs.append({"alvo": rel, "slug": alvo.name, "ordem": ordem, "portao": v["portao"], "agente": v["agente"],
                           "resultado": v["resultado"], "impressao": v["impressao"], "em": v["em"],
                           "volta": v["volta"], "s0": v["achados"]["S0"], "s1": v["achados"]["S1"],
                           "s2": v["achados"]["S2"], "relatorio": v.get("relatorio"), "nota": v.get("nota"),
                           "decisao_carlos": v.get("decisao_carlos")})
    return estados, vs


def conferencia(d: Path, post: dict) -> tuple[dict, list[str]]:
    """(pacote.json, erros do GAUNTLET) de uma pasta da fila — o que o publicar.py confere na hora de publicar
    (validar_pacote → portoes.conferir_pacote(pasta, pacote, post, publicacao=True)), com as mesmas mensagens. Com
    portoes.SO_LEITURA = True nada é gravado (nem o cache de hashes). [] = o post pode sair."""
    pj = d / "pacote.json"
    if not pj.exists():
        return {}, ["falta pacote.json"]
    with lendo(pj):
        pac = json.loads(pj.read_text(encoding="utf-8"))
        if not isinstance(pac, dict):
            raise ValueError("pacote.json não é um objeto")
    try:
        return pac, portoes.conferir_pacote(d, pac, post, publicacao=True)
    except Exception as e:  # o publicar.py faz o mesmo: livro corrompido ou arquivo sumindo bloqueiam SÓ este post
        return pac, [f"GAUNTLET: não consegui conferir os portões ({type(e).__name__}: {e})"]


def fila(destinos: dict[tuple[str, str], str]) -> list[dict]:
    """06-publicar/<slug>/post.json + o selo do pacote.json. legado = slug na lista congelada; a dispensa de portões é
    legado SEM selo (legado selado segue a regra normal; sem selo fora da lista é recusado — erros_gauntlet diz)."""
    leg = portoes.legado()
    out = []
    for d in sorted((PROJETO / "06-publicar").iterdir()):
        pj = d / "post.json"
        if not pj.exists():
            continue
        with lendo(pj):
            p = json.loads(pj.read_text(encoding="utf-8"))
            trial = ((p.get("instagram") or {}).get("trial") or {}).get("graduation_strategy")
        pac, erros = conferencia(d, p)
        selo = pac.get("gauntlet")
        origem = selo.get("origem") if isinstance(selo, dict) and isinstance(selo.get("origem"), str) else None
        out.append({"slug": d.name, "publicar_em": p.get("publicar_em"), "plataformas": p.get("plataformas") or [],
                    "estado": p.get("estado"), "trial": trial, "palavra": (p.get("material") or {}).get("palavra"),
                    "legado": d.name in leg, "confirmar": p.get("confirmar"),
                    "origem": origem if selo else None, "selado": bool(selo),
                    "erros_gauntlet": json.dumps(erros, ensure_ascii=False),
                    "video_slug": destinos.get(("06-publicar", d.name), d.name)})
    return out


# ───────────────────────── desempenho ─────────────────────────

def _json(p: Path) -> dict:
    """Um JSON do projeto que, se existir, tem de ser um objeto (senão ErroArquivo). Ausente = {}."""
    if not p.exists():
        return {}
    with lendo(p):
        o = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(o, dict):
            raise ValueError("não é um objeto JSON")
    return o


def _trial(t):
    # {"graduation_strategy": …} (post.json e cópias) ou, em leituras antigas do metricas.json, o texto direto
    return t.get("graduation_strategy") if isinstance(t, dict) else t


def publicacoes_e_metricas(destinos: dict[tuple[str, str], str]) -> tuple[list[dict], list[dict]]:
    """Uma publicação por pasta de 07-publicados/ com post.json (o registro do publicar.py: publicado_em, plataformas,
    permalinks) ou com metricas.json (as leituras do metricas.py, 5 dias depois). O post.json vence; o metricas.json
    completa; tema, pilar e duração vêm do pacote.json (senão do metricas.json)."""
    pubs, mets = [], []
    for d in sorted((PROJETO / "07-publicados").iterdir()):
        if not d.is_dir():
            continue
        post, m = _json(d / "post.json"), _json(d / "metricas.json")
        if not post and not m:
            continue
        pac = _json(d / "pacote.json")
        ig, fb = post.get("instagram") or {}, post.get("facebook") or {}
        with lendo(d / ("post.json" if post else "metricas.json")):
            pubs.append({
                "slug": d.name, "publicado_em": post.get("publicado_em") or m.get("publicado_em"),
                "tema": pac.get("tema") or m.get("tema"), "pilar": pac.get("pilar") or m.get("pilar"),
                "palavra": (post.get("material") or {}).get("palavra") or m.get("palavra"),
                "duracao_s": pac.get("duracao") or m.get("duracao_s"),
                "trial": _trial(ig.get("trial")) if post else _trial(m.get("trial")),
                "permalink_instagram": ig.get("permalink") or m.get("permalink_instagram"),
                "permalink_facebook": fb.get("permalink") or m.get("permalink_facebook"),
                "video_slug": destinos.get(("07-publicados", d.name), d.name),
                "plataformas": post.get("plataformas") if post else None,
                "estado": post.get("estado") if post else None})
        if not m:
            continue  # as métricas chegam depois (metricas.py, 5 dias)
        mj = d / "metricas.json"
        with lendo(mj):
            dur = pubs[-1]["duracao_s"] or 0
            for leit in m.get("leituras") or []:
                r = leit.get("resumo") or {}
                ig, fb, pal = r.get("instagram") or {}, r.get("facebook") or {}, r.get("palavra") or {}
                tm = ig.get("tempo_medio_s")
                mets.append({"slug": d.name, "lido_em": leit["lido_em"], "dias": leit.get("dias_desde_publicacao"),
                             "views": ig.get("views"), "alcance": ig.get("alcance"), "tempo_medio_s": tm,
                             "pct_assistido": ig.get("pct_medio_assistido"), "curtidas": ig.get("curtidas"),
                             "comentarios": ig.get("comentarios"), "salvamentos": ig.get("salvamentos"),
                             "compartilhamentos": ig.get("compartilhamentos"), "plays_fb": fb.get("plays"),
                             "tempo_medio_fb_s": fb.get("tempo_medio_s"), "palavra_comentarios": pal.get("comentarios"),
                             "palavra_directs": pal.get("directs"),
                             # a API devolveu 1512 s de tempo médio num vídeo de 158 s (Hinton): impossível → marcado
                             "suspeito": bool(tm and dur and tm > dur)})
    return pubs, mets


def perfil() -> tuple[list[dict], list[dict]]:
    snaps, dem = [], []
    for f in sorted((PROJETO / "_controle" / "perfil").glob("*.json")):
        with lendo(f):
            s, d = _perfil(json.loads(f.read_text(encoding="utf-8")))
        snaps.append(s)
        dem += d
    return snaps, dem


def perfil_diario() -> list[dict]:
    """_controle/perfil/diario/AAAA-MM-DD.json (PROPOSTA para o perfil.py; ainda não existe) → uma linha por dia ×
    métrica. Formato: {"dia": "AAAA-MM-DD", "lido_em": ISO com fuso, "metricas": {"reach": 41, …}} — o dia é o do nome
    do arquivo; métrica null = a Meta não devolveu (fica fora). Pasta ausente = vazio; fora do formato = ErroArquivo."""
    pasta, out = PROJETO / "_controle" / "perfil" / "diario", []
    for f in sorted(pasta.glob("*.json")) if pasta.is_dir() else []:
        if f.name.startswith("."):
            continue
        d = _json(f)
        with lendo(f):
            if d.get("dia") != f.stem:
                raise ValueError(f"dia {d.get('dia')!r} ≠ o nome do arquivo ({f.stem})")
            dia, lido, mets = dt.date.fromisoformat(d["dia"]), _com_fuso(d["lido_em"], "lido_em"), d["metricas"]
            if not isinstance(mets, dict):
                raise ValueError("metricas: tem de ser um mapa métrica → valor")
            for k, v in mets.items():
                if v is None:
                    continue
                if type(v) is not int or v < 0:
                    raise ValueError(f"metricas.{k} {v!r} não é um inteiro ≥ 0")
                out.append({"dia": dia, "metrica": str(k), "valor": v, "lido_em": lido})
    return out


def _perfil(p: dict) -> tuple[dict, list[dict]]:
    ig, fb = p.get("instagram") or {}, p.get("facebook") or {}
    conta, mc = ig.get("conta") or {}, ig.get("metricas_conta") or {}

    def val(k):
        return (mc.get(k) or {}).get("valor")

    seg = nao = None
    for q in (mc.get("reach_por_follow_type") or {}).get("quebras") or []:
        for r in q.get("resultados") or []:
            if r["chave"] == ["FOLLOWER"]:
                seg = r["valor"]
            elif r["chave"] == ["NON_FOLLOWER"]:
                nao = r["valor"]
    lido = p["lido_em"]
    snap = {"lido_em": lido, "seguidores": conta.get("followers_count"), "seguindo": conta.get("follows_count"),
            "posts": conta.get("media_count"), "janela_dias": (ig.get("janela") or {}).get("dias"),
            "alcance": val("reach"), "views": val("views"), "contas_engajadas": val("accounts_engaged"),
            "interacoes": val("total_interactions"), "visitas_perfil": val("profile_views"),
            "alcance_seguidores": seg, "alcance_nao_seguidores": nao,
            "fb_seguidores": (fb.get("pagina") or {}).get("followers_count"),
            "toques_links_perfil": val("profile_links_taps")}
    dem = []
    for publico, chave in (("seguidores", "follower_demographics"), ("alcancados", "reached_audience_demographics")):
        for dim, linhas in ((ig.get("demografia") or {}).get(chave) or {}).items():
            for r in linhas or []:
                dem.append({"lido_em": lido, "publico": publico, "dimensao": dim,
                            "chave": " · ".join(r["chave"]), "valor": r["valor"]})
    return snap, dem


# ───────────────────────── tokens e custos (registros do Claude Code) ─────────────────────────
# A conta das telas (a do tokens-custos.py de referência, painel/referencias/claude-design/telas-2026-10-23/), com UMA
# correção (S1-1 do PORTÃO-DADOS, 23/10): uma resposta = as linhas com message.usage e a mesma chave (message.id, ou uuid
# se não houver id) no mesmo arquivo — a mesma mensagem em dois arquivos conta duas vezes; vale o usage da ÚLTIMA linha
# lida. O Claude Code grava cada bloco da resposta numa linha, e nas versões 2.1.270–2.1.304 a 1.ª traz o usage
# provisório do message_start (output_tokens 1–3); o final só vem na última (nos registros de 23/10: 521 respostas, só a
# saída muda, a linha posterior é sempre ≥ à anterior). O script fica com a 1.ª — `--regra-do-script` refaz a conta dele
# para conferir. Dia e instante = os da 1.ª linha (o começo da resposta, como no script): dia = os 10 primeiros
# caracteres do timestamp (data UTC); tokens = entrada + cache gravado + saída (o cache lido entra só no custo); modelo
# fora de PRECOS não conta (fica guardado em uso_execucao, mas fora de todo custo e de toda contagem de tarefas).
# O cache gravado é cobrado pelo TTL (5 min = 1,25 × a entrada, 1 h = 2 ×, documentação de prompt caching): a 1.ª versão
# do script cobrava tudo a 1,25 × (custo_cache_a_1_25() refaz essa conta das mesmas colunas, para conferir); a de 23/10
# 16:41 já cobra pelo TTL. Diferenças de propósito: (1) o vídeo de um subagente sai das pastas que existem, mapeadas para
# o vídeo de origem, o mais citado (video_do_pedido; o script pegava o 1.º AAAA-MM-DD-palavra e inventava vídeos), e o
# departamento tecnologia nunca recebe vídeo; (2) se o detalhe do TTL não fechar com o cache_creation_input_tokens, o
# resto é cobrado a 5 min (o script não cobra o resto) — nos registros reais de 23/10: 0 casos; (3) o claude-opus-5
# (15–19/09) tem preço aqui e não no script — fica fora da janela de 30 dias até 23/10.

PRECOS = {  # US$ por milhão de tokens, preço de tabela da API (tabela de modelos da documentação da Anthropic):
    #                     nome          entrada  cache 5 min (1,25×)  cache 1 h (2×)  cache lido  saída
    "claude-opus-5-5": ("Opus 5.5", "4", "5", "8", "0.20", "20"),
    "claude-sonnet-5-5": ("Sonnet 5.5", "2", "2.5", "4", "0.20", "10"),
    "claude-fable-5-1": ("Fable 5.1", "10", "12.5", "20", "0.25", "50"),
    # 23/10 (coordenador): o histórico de 15–19/09. Cache lido = 0,1 × a entrada (o desconto maior só vale para o
    # Fable 5.1 e o Opus 5.5). "<synthetic>" continua sem preço: mensagem gerada pelo Claude Code, sem custo de API.
    "claude-opus-5": ("Opus 5", "5", "6.25", "10", "0.50", "25"),
}
# ajudantes do Claude Code (e qualquer agentType fora do equipe.yaml) trabalham para o Claude principal: contam como Atlas
AJUDANTES = {"general-purpose", "workflow-subagent", "claude", "Explore", "Plan"}
PASTAS_DE_VIDEO = ("videos", "05-render-pronto", "06-publicar", "07-publicados")
SLUG_CITADO = re.compile(r"(?<![\w-])(videos|05-render-pronto|06-publicar|07-publicados)/"
                         r"(20\d\d-\d\d-\d\d-[a-z0-9]+(?:-[a-z0-9]+)*)")
SEM_VIDEO = "tecnologia"  # o departamento do painel: as execuções dele nunca recebem vídeo
USO = (("entrada", "input_tokens"), ("cache_gravado", "cache_creation_input_tokens"),
       ("cache_lido", "cache_read_input_tokens"), ("saida", "output_tokens"))
COLUNAS_USO = ("entrada", "cache_gravado_5m", "cache_gravado_1h", "cache_gravado_sem_ttl", "cache_lido", "saida")
DESCRICAO_MAX = 200  # a description do .meta.json é um rótulo curto; nada de texto de conversa no banco


def precos() -> list[dict]:
    return [{"modelo": m, "nome": n, "entrada": Decimal(e), "cache_gravado_5m": Decimal(c5), "cache_gravado_1h": Decimal(c1),
             "cache_lido": Decimal(cl), "saida": Decimal(s)} for m, (n, e, c5, c1, cl, s) in PRECOS.items()]


def custo(modelo: str, t: dict) -> Decimal:
    """US$ equivalente no preço de tabela da API, cache gravado pelo TTL (a mesma conta da view `consumo`)."""
    _, e, c5, c1, cl, s = PRECOS[modelo]
    return (t["entrada"] * Decimal(e) + t["cache_gravado_5m"] * Decimal(c5) + t["cache_gravado_1h"] * Decimal(c1)
            + t["cache_lido"] * Decimal(cl) + t["saida"] * Decimal(s)) / 1_000_000


def custo_cache_a_1_25(modelo: str, t: dict) -> Decimal:
    """A conta da 1.ª versão do tokens-custos.py (todo cache gravado a 1,25 × a entrada), feita das mesmas colunas — só
    para conferir a reconciliação; o custo do painel é o de custo()."""
    _, e, c5, _, cl, s = PRECOS[modelo]
    return (t["entrada"] * Decimal(e) + (t["cache_gravado_5m"] + t["cache_gravado_1h"]) * Decimal(c5)
            + t["cache_lido"] * Decimal(cl) + t["saida"] * Decimal(s)) / 1_000_000


def _instante(ts) -> dt.datetime | None:
    try:
        t = dt.datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def _tokens(u: dict, fora: Counter) -> dict | None:
    """usage → colunas de uso_execucao. O cache gravado se divide pelo TTL (cache_creation.ephemeral_1h_input_tokens /
    ephemeral_5m_input_tokens): a parte de 1 h é a do detalhe e os 5 min são o resto, para o total continuar a ser o
    cache_creation_input_tokens (tokens idênticos aos do script). Sem o detalhe, tudo conta como 5 min (sem_ttl)."""
    v = {}
    for col, chave in USO:
        n = u.get(chave) or 0
        if type(n) is not int or n < 0:
            return None
        v[col] = n
    gravado, det = v.pop("cache_gravado"), u.get("cache_creation")
    h = det.get("ephemeral_1h_input_tokens") if isinstance(det, dict) else None
    c = det.get("ephemeral_5m_input_tokens") if isinstance(det, dict) else None
    tem_ttl = type(h) is int or type(c) is int
    um_h = min(h, gravado) if type(h) is int and h > 0 else 0
    if tem_ttl and (h if type(h) is int else 0) + (c if type(c) is int else 0) != gravado:
        fora["cache_ttl_divergente"] += 1  # o detalhe não fecha com o total: vale o total, 1 h pelo detalhe
    if not tem_ttl and gravado:
        fora["cache_sem_ttl"] += 1
    return {**v, "cache_gravado_5m": gravado - um_h, "cache_gravado_1h": um_h,
            "cache_gravado_sem_ttl": 0 if tem_ttl else gravado}


def _mesmo_uso(a: dict, b: dict) -> bool:
    return all(a.get(c) == b.get(c) for _, c in USO) and a.get("cache_creation") == b.get("cache_creation")


def ler_respostas(arq: Path, ate: dt.datetime | None, fora: Counter, regra_do_script: bool = False
                  ) -> tuple[dict, dt.datetime | None, dt.datetime | None] | None:
    """Um .jsonl → ({(dia, modelo): somas}, primeira resposta, última resposta). None se o arquivo sumiu entre a listagem
    e a leitura (limpeza do Claude Code). Linha que não é JSON (a última da sessão ativa pode vir cortada) é pulada.

    Vale o usage da ÚLTIMA linha lida de cada resposta (com --ate: a última escrita até o corte — as posteriores ainda não
    existiam); dia e instante vêm da 1.ª. regra_do_script=True refaz a conta do tokens-custos.py: o usage da 1.ª linha,
    com o corte aplicado depois da deduplicação, como ele faz — só para conferir."""
    primeira, ultima, uso, ini, fim = {}, {}, {}, None, None
    try:
        fh = open(arq, encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return None
    with fh:
        for linha in fh:
            if '"usage"' not in linha:  # atalho do script: só estas linhas podem ter message.usage
                continue
            try:
                o = json.loads(linha)
            except ValueError:
                continue
            m = o.get("message") if isinstance(o, dict) else None
            u = m.get("usage") if isinstance(m, dict) else None
            if not u or not isinstance(u, dict):
                continue
            chave = m.get("id") or o.get("uuid")
            if not isinstance(chave, (str, int, type(None))):  # id fora do formato não derruba a passagem
                chave = json.dumps(chave, sort_keys=True)
            if ate is not None and not regra_do_script:
                q = _instante(o.get("timestamp"))
                if q is None or q > ate:  # no corte, esta linha ainda não tinha sido escrita
                    continue
            if chave not in primeira:
                primeira[chave] = o
            ultima[chave] = m  # a mesma resposta em várias linhas: vale a última
    for chave, o in primeira.items():
        m = o["message"] if regra_do_script else ultima[chave]
        ts = o.get("timestamp")
        try:
            dia = dt.date.fromisoformat(ts[:10])
        except (TypeError, ValueError):
            fora["sem_data"] += 1
            continue
        quando = _instante(ts)
        if ate is not None and regra_do_script and (quando is None or quando > ate):
            continue
        modelo = m.get("model")
        t = _tokens(m["usage"], fora) if isinstance(modelo, str) and modelo else None
        if t is None:
            fora["sem_modelo_ou_uso"] += 1
            continue
        if not _mesmo_uso(o["message"]["usage"], ultima[chave]["usage"]):
            fora["usage_provisorio"] += 1  # respostas cuja 1.ª linha tinha o usage provisório (o script fica com ele)
        soma = uso.setdefault((dia, modelo), {"respostas": 0, **{c: 0 for c in COLUNAS_USO}})
        soma["respostas"] += 1
        for c in t:
            soma[c] += t[c]
        if quando is not None:
            ini = quando if ini is None or quando < ini else ini
            fim = quando if fim is None or quando > fim else fim
    return uso, ini, fim


def ler_meta(arq: Path) -> dict:
    try:
        meta = json.loads(arq.with_name(arq.name[: -len(".jsonl")] + ".meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return meta if isinstance(meta, dict) else {}


def video_do_pedido(arq: Path, destinos: dict[tuple[str, str], str]) -> str | None:
    """O vídeo de um subagente, pelo 1.º pedido (a 1.ª linha do .jsonl): cada `<pasta>/<slug>` citado cuja pasta existe
    (videos/, 05-render-pronto/, 06-publicar/, 07-publicados/) vira o vídeo de origem (destinos); vale o vídeo mais
    citado e, no empate, o citado primeiro. O texto do pedido só é lido aqui; não vai para o banco."""
    try:
        with open(arq, encoding="utf-8", errors="ignore") as fh:
            c = (json.loads(fh.readline()).get("message") or {}).get("content")
    except (OSError, ValueError, AttributeError):
        return None
    txt = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
    citados = [destinos[m.groups()] for m in SLUG_CITADO.finditer(txt or "") if m.groups() in destinos]
    if not citados:
        return None
    vezes = Counter(citados)
    return next(v for v in citados if vezes[v] == max(vezes.values()))


def destinos_de_video() -> dict[tuple[str, str], str]:
    """(pasta, slug) que existe → slug do vídeo de origem. videos/<slug> é ele mesmo; uma pasta de pacote (05/06/07) é
    o `gauntlet.origem` do pacote.json, senão o slug de videos/ mais longo que é prefixo do slug do pacote (até um
    "-": 2026-10-20-fei-fei-li-r2 → 2026-10-20-fei-fei-li), senão o próprio slug."""
    pastas = {}
    for pasta in PASTAS_DE_VIDEO:
        d = PROJETO / pasta
        with lendo(d):
            pastas[pasta] = sorted(p for p in d.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))) \
                if d.is_dir() else []
    videos_ = {p.name for p in pastas["videos"]}
    out = {("videos", v): v for v in videos_}
    for pasta in PASTAS_DE_VIDEO[1:]:
        for p in pastas[pasta]:
            selo, pj = None, p / "pacote.json"
            if pj.is_file():
                with lendo(pj):
                    pac = json.loads(pj.read_text(encoding="utf-8"))
                    selo = pac.get("gauntlet") if isinstance(pac, dict) else None
            origem = selo.get("origem") if isinstance(selo, dict) else None
            if isinstance(origem, str) and origem.strip("/"):
                out[(pasta, p.name)] = Path(origem).name
            else:
                prefixos = [v for v in videos_ if p.name == v or p.name.startswith(v + "-")]
                out[(pasta, p.name)] = max(prefixos, key=len) if prefixos else p.name
    return out


def membro_de(tipo: str, agente_tipo: str | None, fichas: dict[str, str]) -> str:
    """Sessão principal, ajudantes e agentType fora do equipe.yaml = o Claude principal (diretor, Atlas)."""
    if tipo == "subagente" and agente_tipo and agente_tipo not in AJUDANTES and agente_tipo in fichas:
        return agente_tipo
    return "diretor"


def registros(fichas: dict[str, str], ate: dt.datetime | None, destinos: dict[tuple[str, str], str],
              regra_do_script: bool = False) -> dict:
    """Execuções e consumo lidos de REGISTROS (só leitura). `presentes` = todo .jsonl lido nesta passagem (com ou sem
    resposta): o que estiver no banco e não estiver aqui é arquivo (registro_presente = false)."""
    out = {"execucoes": [], "uso_execucao": [], "presentes": [], "pasta_existe": REGISTROS.is_dir(), "fora": Counter()}
    if not out["pasta_existe"]:
        return out
    if "diretor" not in fichas:
        raise ErroArquivo("painel/equipe.yaml: sem o agente 'diretor' (a quem contam a sessão principal e os ajudantes)")
    agora = dt.datetime.now(dt.timezone.utc)
    # o mesmo glob do script (recursivo; pula nomes que começam com ".")
    for f in sorted(glob.glob(os.path.join(glob.escape(str(REGISTROS)), "**", "*.jsonl"), recursive=True)):
        arq = Path(f)
        rel = arq.relative_to(REGISTROS)
        with lendo(arq):
            lido = ler_respostas(arq, ate, out["fora"], regra_do_script)
        if lido is None:
            continue
        out["presentes"].append(rel.as_posix())
        uso, ini, fim = lido
        if not uso:
            continue
        sub = "subagents" in rel.parts[:-1]
        meta = ler_meta(arq) if sub else {}
        agente_tipo = meta.get("agentType") if isinstance(meta.get("agentType"), str) and meta.get("agentType") else None
        tipo = "subagente" if sub else "principal"
        membro = membro_de(tipo, agente_tipo, fichas)
        desc = meta.get("description")
        wf = rel.parts.index("workflows") + 1 if "workflows" in rel.parts[:-1] else None
        out["execucoes"].append({
            "arquivo": rel.as_posix(), "tipo": tipo,
            "sessao": rel.parts[0][: -len(".jsonl")] if len(rel.parts) == 1 else rel.parts[0],
            "agente_id": arq.stem.removeprefix("agent-") if sub else None,
            "workflow": rel.parts[wf] if wf is not None and wf < len(rel.parts) - 1 else None,
            "agente_tipo": agente_tipo, "membro_id": membro, "departamento_id": fichas[membro],
            "descricao": desc.strip()[:DESCRICAO_MAX] if isinstance(desc, str) and desc.strip() else None,
            "profundidade": meta.get("spawnDepth") if type(meta.get("spawnDepth")) is int else None,
            "terminou": meta.get("finished") if isinstance(meta.get("finished"), bool) else None,
            "video_slug": video_do_pedido(arq, destinos) if sub and fichas[membro] != SEM_VIDEO else None,
            "inicio": ini, "fim": fim, "registro_presente": True, "visto_em": agora})
        for (dia, modelo), s in sorted(uso.items()):
            out["uso_execucao"].append({"arquivo": rel.as_posix(), "dia": dia, "modelo": modelo, **s})
    return out


def totais(uso: list[dict]) -> tuple[int, Decimal, Decimal, Counter]:
    """Tokens, US$ (pelo TTL) e US$ com todo cache gravado a 1,25 × do que conta (modelo com preço), e respostas sem
    preço por modelo — para a linha do log e a conferência."""
    tk, usd, usd_125, sem = 0, Decimal(0), Decimal(0), Counter()
    for u in uso:
        if u["modelo"] in PRECOS:
            tk += u["entrada"] + u["cache_gravado_5m"] + u["cache_gravado_1h"] + u["saida"]
            usd += custo(u["modelo"], u)
            usd_125 += custo_cache_a_1_25(u["modelo"], u)
        else:
            sem[u["modelo"]] += u["respostas"]
    return tk, usd, usd_125, sem


# ───────────────────────── câmbio (painel/cambio.yaml) ─────────────────────────

def cambio(avisos: list[str]) -> list[dict]:
    """painel/cambio.yaml → tabela cambio (uma linha por moeda × data). O custo fica em US$ (decisão de 24/10: nenhuma
    tela converte hoje). Arquivo ausente = tabela vazia, com aviso (PD28: apagar o arquivo não congela o painel); taxa
    inválida = ErroArquivo (a passagem para, nada é gravado)."""
    arq = PROJETO / "painel" / "cambio.yaml"
    out, vistas = [], set()
    if not arq.is_file():
        avisos.append("painel/cambio.yaml não encontrado — tabela cambio vazia (o custo continua em US$)")
        return out
    with lendo(arq):
        taxas = (yaml.safe_load(arq.read_text(encoding="utf-8")) or {})["taxas"]
        if not isinstance(taxas, list) or not taxas:
            raise ValueError("taxas: precisa de pelo menos uma linha")
        for i, t in enumerate(taxas, 1):
            data, moeda, valor, fonte = t["data"], t["moeda"], t["valor"], t["fonte"]
            if isinstance(data, str):
                data = dt.date.fromisoformat(data)
            if type(data) is not dt.date:
                raise ValueError(f"taxa {i}: data {data!r} não é AAAA-MM-DD")
            if not (isinstance(moeda, str) and re.fullmatch(r"[A-Z]{3}", moeda)) or moeda == "USD":
                raise ValueError(f"taxa {i}: moeda {moeda!r} não é um código de 3 letras (ex.: GBP)")
            if isinstance(valor, bool) or not isinstance(valor, (int, float, str)):
                raise ValueError(f"taxa {i}: valor {valor!r} não é um número")
            try:
                v = Decimal(str(valor).strip())
            except ArithmeticError:
                raise ValueError(f"taxa {i}: valor {valor!r} não é um número (use ponto decimal)") from None
            if not v.is_finite() or v <= 0 or v.as_tuple().exponent < -6 or v >= 10 ** 6:
                raise ValueError(f"taxa {i}: valor {valor!r} fora do formato (maior que 0, até 6 casas)")
            if not isinstance(fonte, str) or not fonte.strip():
                raise ValueError(f"taxa {i}: sem fonte")
            if (moeda, data) in vistas:
                raise ValueError(f"taxa {i}: {moeda} de {data} repetida")
            vistas.add((moeda, data))
            out.append({"moeda": moeda, "data": data, "valor": v, "fonte": fonte.strip()})
    return out


def ler_projeto(ate: dt.datetime | None = None, regra_do_script: bool = False) -> tuple[dict[str, list[dict]], dict]:
    """Tudo o que vai para o banco, lido do projeto e dos registros do Claude Code (só leitura). Levanta ErroArquivo se
    um arquivo estiver ilegível."""
    portoes.SO_LEITURA = True  # o painel só lê; nem o cache de hashes dos portões é gravado por ele
    avisos: list[str] = []  # anomalias que não param a passagem: uma linha ⚠ cada (main)
    deps, agentes = equipe()
    estados, vs = portoes_e_veredictos()
    destinos = destinos_de_video()  # (pasta, slug) → vídeo de origem: fila, publicações, prontos, travas e tokens
    pubs, mets = publicacoes_e_metricas(destinos)
    snaps, dem = perfil()
    reg = registros({a["id"]: a["departamento_id"] for a in agentes}, ate, destinos, regra_do_script)
    pron = prontos(destinos)
    vids = videos(destinos, pron)
    mats, arqs = biblioteca([v["slug"] for v in vids])
    vagas, reg["calendario_bloco"], reg["calendario_fuso"] = calendario_vagas()
    cfg = ler_acervo_yaml(avisos)
    lks, acv = looks(avisos, looks_do_yaml(cfg)), acervo(destinos, avisos, cfg)
    anims = animacoes([v["slug"] for v in vids], avisos)
    reg["avisos"] = avisos
    return ({"departamentos": deps, "agentes": agentes, "videos": vids, "portoes_estado": estados,
             "veredictos": vs, "fila": fila(destinos), "publicacoes": pubs, "metricas": mets,
             "perfil_snapshots": snaps, "perfil_demografia": dem, "precos_modelo": precos(), "cambio": cambio(avisos),
             "nao_publicar": nao_publicar(destinos), "biblioteca_materiais": mats, "biblioteca_arquivos": arqs,
             "biblioteca_referencias": referencias(), "biblioteca_mais_utilizados": mais_utilizados(vids, mats),
             "prontos": pron, "calendario_vagas": vagas, "perfil_diario": perfil_diario(),
             "looks": lks, **acv, "animacoes": anims, "sistema_contagens": contagens_do_sistema(),
             "execucoes": reg["execucoes"], "uso_execucao": reg["uso_execucao"]}, reg)


# ───────────────────────── gravar ─────────────────────────

# regravadas inteiras a cada passagem (espelho dos arquivos)
ORDEM = ["departamentos", "agentes", "videos", "portoes_estado", "veredictos", "fila", "publicacoes", "metricas",
         "perfil_snapshots", "perfil_demografia", "precos_modelo", "cambio", "nao_publicar", "biblioteca_materiais",
         "biblioteca_arquivos", "biblioteca_referencias", "biblioteca_mais_utilizados", "prontos", "calendario_vagas",
         "perfil_diario", "looks", "capa_estilos", "capa_estilos_exemplos", "legenda_estilos", "fontes",
         "sistema_ferramentas", "modelos_descricao", "animacoes", "sistema_contagens"]
# ARQUIVO: nunca truncadas — só se regrava o que o .jsonl ainda mostra
ARQUIVO = ["execucoes", "uso_execucao"]


def _inserir(cur, tabela: str, linhas: list[dict]) -> None:
    if linhas:
        cols = list(linhas[0])
        sql = f"insert into {tabela} ({', '.join(cols)}) values ({', '.join(['%s'] * len(cols))})"
        cur.executemany(sql, [[ln[c] for c in cols] for ln in linhas])


def gravar(dados: dict[str, list[dict]], reg: dict, fichas: dict[str, str]) -> int:
    """Uma transação só: se qualquer comando falhar, o `with` desfaz tudo e o banco fica com a passagem anterior.
    Devolve quantas execuções estão no arquivo sem o .jsonl (registro_presente = false)."""
    with psycopg.connect(DB_URL, connect_timeout=5) as con, con.cursor() as cur:
        cur.execute("truncate " + ", ".join(ORDEM))
        for tabela in ORDEM:
            _inserir(cur, tabela, dados[tabela])
        # o arquivo: o .jsonl presente é a verdade (apaga e regrava, uso_execucao vai junto pelo on delete cascade);
        # o que sumiu fica, marcado, com o membro e o departamento do equipe.yaml de hoje
        presentes = reg["presentes"]
        cur.execute("delete from execucoes where arquivo = any(%s)", [presentes])
        for tabela in ARQUIVO:
            _inserir(cur, tabela, dados[tabela])
        sumidas = cur.execute("select arquivo, tipo, agente_tipo from execucoes where not (arquivo = any(%s))",
                              [presentes]).fetchall()
        for arquivo, tipo, agente_tipo in sumidas:
            m = membro_de(tipo, agente_tipo, fichas)
            cur.execute("update execucoes set registro_presente = false, membro_id = %s, departamento_id = %s, "
                        "video_slug = case when %s = %s then null else video_slug end where arquivo = %s",
                        [m, fichas[m], fichas[m], SEM_VIDEO, arquivo])
        tk, usd, _, sem = totais(dados["uso_execucao"])
        resumo = {**{t: len(dados[t]) for t in ORDEM + ARQUIVO}, "arquivadas": len(sumidas), "tokens": tk,
                  "usd": str(round(usd, 4)), "sem_preco": dict(sem), "registros_presentes": reg["pasta_existe"],
                  **{k: n for k, n in reg["fora"].items()}}
        cur.execute("insert into sincronizacoes (resumo) values (%s)", [json.dumps(resumo)])
        # o launchd sincroniza a cada 15 min: guarda só a última semana do histórico de passagens
        cur.execute("delete from sincronizacoes where em < now() - interval '7 days'")
        return len(sumidas)


def _primeira_linha(e: Exception) -> str:
    return str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__


def _local(host: str) -> bool:
    """Host que cai neste Mac: vazio ou socket, localhost (também com "." no fim), 127.0.0.0/8, 0.0.0.0 e ::1/::."""
    h = host.strip().strip("[]").rstrip(".").lower()
    return h in ("", "localhost", "0.0.0.0", "::1", "::", "0:0:0:0:0:0:0:1") or h.startswith(("127.", "/"))


def _banco_do_carlos(url: str) -> bool:
    """A URL aponta para o banco do painel do Carlos (Postgres `postgres` na porta 55322 deste Mac)? Na dúvida (URL que
    não se lê), trata como se fosse — a guarda do --ate/--regra-do-script prefere recusar (PD18)."""
    try:
        d = conninfo_to_dict(url)
    except psycopg.ProgrammingError:
        return True
    hosts = (d.get("host") or "").split(",") + [h for h in (d.get("hostaddr") or "").split(",") if h]
    portas = [p.strip() for p in str(d.get("port") or "5432").split(",")]
    return (any(_local(h) for h in hosts) and "55322" in portas
            and (d.get("dbname") or d.get("user") or "postgres") == "postgres")


def _iso(txt: str) -> dt.datetime:
    t = _instante(txt)
    if t is None:
        raise argparse.ArgumentTypeError(f"instante ISO inválido: {txt!r} (ex.: 2026-10-23T15:02:49.958Z)")
    return t


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seco", action="store_true")
    ap.add_argument("--ate", type=_iso, metavar="ISO")
    ap.add_argument("--regra-do-script", action="store_true")
    a = ap.parse_args()
    agora = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if (a.ate or a.regra_do_script) and not a.seco and _banco_do_carlos(DB_URL):
        # um corte ou a conta do script gravados no banco do Carlos ficariam no arquivo das execuções (se um .jsonl sumir
        # antes da próxima passagem, para sempre)
        print(f"{agora} ✗ --ate/--regra-do-script gravam um número que não é o do painel: no banco do painel só com "
              "--seco (ou PAINEL_DB_URL de um banco de teste)")
        return 2
    try:
        dados, reg = ler_projeto(a.ate, a.regra_do_script)
    except ErroArquivo as e:
        # um arquivo truncado no meio de uma escrita do metricas.py/publicar.py, ou um formato que mudou: não grava
        # nada (melhor o painel da passagem anterior do que um painel pela metade) e tenta de novo na próxima.
        print(f"{agora} ✗ arquivo do projeto ilegível ({e}) — nada gravado; o painel continua com a passagem anterior")
        return 1
    if reg["calendario_bloco"] and not reg["calendario_fuso"]:
        fuso = (dados["calendario_vagas"] or [{}])[0].get("fuso")
        print(f"{agora} ⚠ _controle/calendario.md: o bloco não diz o fuso: — o painel usa {fuso} (TZ_PUBLICACAO do "
              "ambiente ou Europe/London), mas o publicar.py lê o TZ_PUBLICACAO do .env; ponha fuso: no bloco")
    if not reg["calendario_bloco"]:
        print(f"{agora} ⚠ _controle/calendario.md sem o bloco vagas_semanais — 0 vagas no painel (o bloco é o 1.º "
              "trecho ```yaml do arquivo)")
    for aviso in reg["avisos"]:
        print(f"{agora} ⚠ {aviso}")
    if not reg["pasta_existe"]:
        print(f"{agora} ⚠ registros do Claude Code não encontrados ({REGISTROS}) — 0 execuções lidas; as que já estão "
              "no banco ficam (arquivo)")
    tk, usd, usd_125, sem = totais(dados["uso_execucao"])
    resumo = "  ".join(f"{t} {len(v)}" for t, v in dados.items())
    resumo += f"  tokens {tk}  usd {round(usd, 2)}  usd_cache_1.25x {round(usd_125, 2)}"
    if sem:
        resumo += "  sem_preco " + ",".join(f"{m}:{n}" for m, n in sorted(sem.items()))
    for k, n in sorted(reg["fora"].items()):  # respostas sem data, sem modelo/usage, cache sem TTL ou divergente
        resumo += f"  {k} {n}"
    if a.ate:
        resumo += f"  ate {a.ate.isoformat()}"
    if a.regra_do_script:
        resumo += "  regra_do_script 1"
    if a.seco:
        print(f"{agora} (seco) {resumo}")
        return 0
    try:
        sumidas = gravar(dados, reg, {ag["id"]: ag["departamento_id"] for ag in dados["agentes"]})
    except psycopg.OperationalError as e:
        # Docker/Supabase do painel desligado (ex.: depois de reiniciar o Mac): avisa e tenta de novo na próxima passagem.
        # ligar pelo iniciar.sh: ele garante a rede só-no-Mac (garantir_rede) antes do `supabase start` — o comando solto
        # pode recriar a rede Docker aberta para a rede local (PD12)
        print(f"{agora} ✗ banco do painel fora do ar ({_primeira_linha(e)}) — ligar com: bash painel/iniciar.sh")
        return 1
    except psycopg.Error as e:
        # schema diferente do que o sincronizador espera, chave repetida, FK quebrada…: a transação foi desfeita.
        # o DETAIL diz o valor (ex.: Key (gerente_id)=(portao-dadoz) is not present in table "agentes") — PD23
        detalhe = getattr(getattr(e, "diag", None), "message_detail", None)
        print(f"{agora} ✗ o banco recusou a passagem ({type(e).__name__}: {_primeira_linha(e)}"
              f"{' · ' + detalhe.strip() if detalhe else ''}) — desfeita; o painel continua com a passagem anterior")
        return 1
    print(f"{agora} ✓ painel sincronizado  {resumo}  arquivadas {sumidas}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
