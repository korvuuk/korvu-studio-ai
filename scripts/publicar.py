#!/usr/bin/env python3
"""Publicação agendada de Reels no Instagram + Página do Facebook.

Uso (da raiz do projeto, sempre com uv):
  uv run python scripts/publicar.py agendar <slug> [--em "2026-09-21 19:00"] [--reagendar] [--dry-run]
  uv run python scripts/publicar.py --due [--dry-run]            # chamado pelo launchd a cada 15 min
  uv run python scripts/publicar.py publicar <slug> [--dry-run] [--sim] [--plataformas instagram,facebook]
  uv run python scripts/publicar.py verificar-tokens [--dry-run]

Regras:
- Só publica o que está em 06-publicar/<slug>/ com pacote.json QA PASS e arquivos presentes.
- GAUNTLET (22/10, docs/gauntlet.md): o pacote tem de ter o selo dos portões (`pacote.gauntlet`, escrito pelo
  montar_pacote.py), os arquivos têm de ser os que os portões aprovaram, e na hora de publicar o PORTÃO-PUBLICACAO
  tem de estar APROVADO e válido sobre a pasta. Exceção única: `_controle/gauntlet-legado.json` (lista congelada).
- Legendas (legenda-instagram.txt / legenda-facebook.txt) são escritas pelo agente `publicador`.
- Enquanto `modo_confirmar_restantes` > 0 no calendário, o post fica `confirmar: true`: o --due não
  publica; muda para `aguardando_confirmacao` e notifica. O Carlos confirma com `publicar <slug> --sim`.
- Facebook: até 90 s sai como Reel (/video_reels, limite da API 3–90 s); acima de 90 s sai como VÍDEO DA
  PÁGINA (/videos, upload multipart do disco). post.facebook.tipo = "reel" | "video".
- --dry-run percorre o fluxo inteiro e imprime os pedidos exatos (tokens mascarados), sem escrever em
  lado nenhum (nem R2, nem Meta, nem ficheiros locais).
- Variáveis: INSTAGRAM_USER_ID, INSTAGRAM_ACCESS_TOKEN, META_PAGE_ID, META_PAGE_ACCESS_TOKEN,
  META_APP_ID, META_APP_SECRET, R2_*, META_GRAPH_VERSION (padrão v23.0), CONTENT_AI_ROOT (testes).
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import json
import logging
import mimetypes
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
import yaml

PROJETO = Path(__file__).resolve().parent.parent
if not os.environ.get("CONTENT_AI_NO_DOTENV"):
    try:
        from dotenv import load_dotenv

        if (PROJETO / ".env").exists():
            load_dotenv(PROJETO / ".env", override=False)
    except ImportError:  # pragma: no cover
        pass

ROOT = Path(os.environ.get("CONTENT_AI_ROOT") or PROJETO).resolve()
sys.path.insert(0, str(Path(__file__).resolve().parent))
import portoes  # noqa: E402  (GAUNTLET: selo do pacote + portão da publicação — docs/gauntlet.md)

FILA = ROOT / "06-publicar"
PUBLICADOS = ROOT / "07-publicados"
CONTROLE = ROOT / "_controle"
CALENDARIO = CONTROLE / "calendario.md"
TRACKER = CONTROLE / "tracker.md"
LOG_ARQ = CONTROLE / "logs" / "publicar.log"
TRAVA = CONTROLE / ".publicar.lock"

GRAPH_VERSION = os.environ.get("META_GRAPH_VERSION") or "v23.0"
GRAPH = f"https://graph.facebook.com/{GRAPH_VERSION}"
RUPLOAD = f"https://rupload.facebook.com/video-upload/{GRAPH_VERSION}"
GRAPH_VIDEO = f"https://graph-video.facebook.com/{GRAPH_VERSION}"
FFPROBE = os.environ.get("FFPROBE_BIN") or "/opt/homebrew/bin/ffprobe"
# API de Reels da Página só aceita 3–90 s; acima disso o FB recebe o vídeo como VÍDEO DA PÁGINA (14/10).
FB_REEL_MAX_S = 90

SEGREDOS = ("INSTAGRAM_ACCESS_TOKEN", "META_PAGE_ACCESS_TOKEN", "META_APP_SECRET", "R2_SECRET_ACCESS_KEY",
            "R2_ACCESS_KEY_ID")
R2_VARS = ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME", "R2_PUBLIC_URL")
DIAS = {"segunda": 0, "terca": 1, "terça": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5,
        "sábado": 5, "domingo": 6}
IG_MAX_LEGENDA, IG_MAX_HASHTAGS = 2200, 5
POLL_INTERVALO, POLL_MAX_S = 5, 600
ATRASO_MAX_H = float(os.environ.get("PUBLICAR_ATRASO_MAX_H", "6"))
CODIGOS_TRANSITORIOS = {1, 2, 4, 17, 32, 341, 613, 80001, 80002}
ESCOPOS_IG = {"instagram_basic", "instagram_content_publish"}
ESCOPOS_PAGINA = {"pages_manage_posts", "pages_read_engagement", "pages_show_list"}

dormir = time.sleep  # substituível nos testes
log = logging.getLogger("publicar")


# ───────────────────────── erros, máscara, log ─────────────────────────

class ErroPublicacao(Exception):
    transitorio = False


class Ocupado(Exception):
    pass


DICAS = {
    190: "token inválido ou expirado — gere um novo e rode `verificar-tokens`",
    102: "sessão do token expirou — renove o token",
    10: "a app/token não tem a permissão necessária",
    200: "permissão em falta (instagram_content_publish / pages_manage_posts?)",
    4: "limite de chamadas da app — tente mais tarde",
    17: "limite de chamadas do utilizador — tente mais tarde",
    32: "limite de chamadas da Página — tente mais tarde",
    613: "limite de chamadas — tente mais tarde",
    9004: "a Meta não conseguiu baixar a mídia do URL (o R2 está público?)",
    9007: "a mídia ainda não está pronta para publicar",
    2207026: "formato de vídeo não suportado para Reels (H.264/AAC, 9:16, 3 s–15 min)",
    36003: "proporção do vídeo inválida",
    100: "parâmetro inválido ou ID errado (confira INSTAGRAM_USER_ID / META_PAGE_ID)",
}


class ErroMeta(ErroPublicacao):
    def __init__(self, status: int, erro: dict, url: str):
        self.status, self.erro = status, erro
        code, sub = erro.get("code"), erro.get("error_subcode")
        self.transitorio = bool(status >= 500 or status == 429 or erro.get("is_transient")
                                or code in CODIGOS_TRANSITORIOS)
        msg = erro.get("error_user_msg") or erro.get("message") or str(erro)[:300]
        dica = DICAS.get(sub) or DICAS.get(code)
        onde = (url.split("?")[0].replace(GRAPH, "graph").replace(RUPLOAD, "rupload")
                .replace(GRAPH_VIDEO, "graph-video"))
        texto = f"Meta {status} em {onde} (code {code}{'/' + str(sub) if sub else ''}): {msg}"
        if dica:
            texto += f" → {dica}"
        if erro.get("fbtrace_id"):
            texto += f" [fbtrace {erro['fbtrace_id']}]"
        super().__init__(mascarar(texto))


class ErroRede(ErroPublicacao):
    transitorio = True


def mascarar_valor(v: str) -> str:
    v = str(v)
    return f"{v[:4]}…({len(v)} chars)" if len(v) > 10 else "****"


def mascarar(texto) -> str:
    s = str(texto)
    for k in SEGREDOS:
        v = os.environ.get(k)
        if v and len(v) >= 6:
            s = s.replace(v, mascarar_valor(v))
    s = re.sub(r"((?:access_token|input_token)=)[A-Za-z0-9|_\-\.]{12,}", r"\1****", s)
    s = re.sub(r"(OAuth )[A-Za-z0-9|_\-\.]{12,}", r"\1****", s)
    return s


class _FiltroSegredos(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = mascarar(record.getMessage())
        record.args = ()
        return True


def configurar_log() -> None:
    if log.handlers:
        return
    log.setLevel(logging.INFO)
    log.addFilter(_FiltroSegredos())
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", "%Y-%m-%d %H:%M:%S")
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(fmt)
    log.addHandler(h)
    # sob o launchd o stdout já vai para o log; num terminal, gravamos também no arquivo
    if sys.stdout.isatty() and CONTROLE.exists():
        LOG_ARQ.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(LOG_ARQ, encoding="utf-8")
        fh.setFormatter(fmt)
        log.addHandler(fh)


# ───────────────────────── tempo, trava, notificação ─────────────────────────

def agora() -> dt.datetime:
    v = os.environ.get("CONTENT_AI_AGORA")  # só para testes
    return dt.datetime.fromisoformat(v) if v else dt.datetime.now().astimezone()


def iso(t: dt.datetime) -> str:
    return t.isoformat(timespec="seconds")


def ler_iso(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        t = dt.datetime.fromisoformat(s)
        return t if t.tzinfo else t.astimezone()
    except ValueError:
        return None


@contextlib.contextmanager
def trava():
    TRAVA.parent.mkdir(parents=True, exist_ok=True)
    f = open(TRAVA, "a+")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        f.close()
        raise Ocupado("Outra execução do publicar.py está em curso (trava _controle/.publicar.lock).")
    try:
        f.seek(0)
        f.truncate()
        f.write(f"{os.getpid()} {iso(agora())}\n")
        f.flush()
        yield
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def notificar(titulo: str, msg: str, dry: bool = False) -> None:
    if dry or os.environ.get("PUBLICAR_SEM_NOTIFICACAO") or sys.platform != "darwin":
        log.info(f"[notificação{' dry-run' if dry else ''}] {titulo}: {msg}")
        return
    esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')  # noqa: E731
    subprocess.run(["osascript", "-e",
                    f'display notification "{esc(msg)}" with title "{esc(titulo)}" sound name "Glass"'],
                   check=False, timeout=15, capture_output=True)


# ───────────────────────── calendário / tracker / status ─────────────────────────

def ler_calendario() -> tuple[str, dict]:
    if not CALENDARIO.exists():
        raise ErroPublicacao(f"Calendário não encontrado: {CALENDARIO}")
    txt = CALENDARIO.read_text(encoding="utf-8")
    m = re.search(r"```ya?ml\n(.*?)```", txt, re.S)
    cfg = (yaml.safe_load(m.group(1)) if m else None) or {}
    return txt, cfg


def fuso(cfg: dict) -> ZoneInfo:
    return ZoneInfo(cfg.get("fuso") or os.environ.get("TZ_PUBLICACAO") or "Europe/London")


def _celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def _linha(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def ler_agenda(txt: str) -> list[list[str]]:
    linhas, dentro, rows = txt.splitlines(), False, []
    for ln in linhas:
        if ln.strip().lower().startswith("## agenda"):
            dentro = True
            continue
        if dentro and ln.startswith("## "):
            break
        if dentro and ln.strip().startswith("|"):
            c = _celulas(ln)
            if c and c[0] not in ("Data/hora",) and not set(c[0]) <= set("-: "):
                rows.append(c)
    return rows


def atualizar_agenda(slug: str, dry: bool, data_hora: str | None = None, plataformas: str | None = None,
                     estado: str | None = None) -> None:
    if dry:
        log.info(f"[dry-run] calendário/Agenda: {slug} → "
                 + ", ".join(f"{k}={v}" for k, v in [("data", data_hora), ("plataformas", plataformas),
                                                     ("estado", estado)] if v))
        return
    txt, _ = ler_calendario()
    linhas = txt.splitlines()
    try:
        i_ag = next(i for i, ln in enumerate(linhas) if ln.strip().lower().startswith("## agenda"))
    except StopIteration:
        linhas += ["", "## Agenda", "| Data/hora | Slug | Plataformas | Estado |", "|---|---|---|---|"]
        i_ag = len(linhas) - 3
    ult, alvo = i_ag, None
    for i in range(i_ag + 1, len(linhas)):
        if linhas[i].startswith("## "):
            break
        if linhas[i].strip().startswith("|"):
            ult = i
            c = _celulas(linhas[i])
            if len(c) >= 2 and c[1] == slug:
                alvo = i
    if alvo is not None:
        c = (_celulas(linhas[alvo]) + ["", "", "", ""])[:4]
        c = [data_hora or c[0], slug, plataformas or c[2], estado or c[3]]
        linhas[alvo] = _linha(c)
    else:
        linhas.insert(ult + 1, _linha([data_hora or "", slug, plataformas or "", estado or ""]))
    CALENDARIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def definir_confirmar_restantes(n: int, dry: bool) -> None:
    if dry:
        log.info(f"[dry-run] calendário: modo_confirmar_restantes → {n}")
        return
    txt, _ = ler_calendario()
    novo = re.sub(r"(?m)^(modo_confirmar_restantes:\s*)\d+", rf"\g<1>{n}", txt, count=1)
    CALENDARIO.write_text(novo, encoding="utf-8")


def atualizar_tracker(slug: str, estado: str, pac: dict | None, dry: bool) -> None:
    if dry:
        log.info(f"[dry-run] tracker: {slug} → {estado}")
        return
    if not TRACKER.exists():
        return
    linhas = TRACKER.read_text(encoding="utf-8").splitlines()
    try:
        i_cab = next(i for i, ln in enumerate(linhas) if ln.strip().startswith("| Slug"))
    except StopIteration:
        log.warning("tracker.md sem tabela; não atualizado")
        return
    cols = _celulas(linhas[i_cab])
    quando = agora().strftime("%Y-%m-%d %H:%M")
    ult, feito = i_cab + 1, False
    for i in range(i_cab + 2, len(linhas)):
        if not linhas[i].strip().startswith("|"):
            break
        ult = i
        c = _celulas(linhas[i])
        if c and c[0] == slug:
            c = (c + [""] * len(cols))[:len(cols)]
            if "Estado" in cols:
                c[cols.index("Estado")] = estado
            if "Atualizado" in cols:
                c[cols.index("Atualizado")] = quando
            linhas[i], feito = _linha(c), True
    if not feito:
        pac = pac or {}
        valores = {"Slug": slug, "Tema": pac.get("tema", ""), "Pilar": pac.get("pilar", ""),
                   "CTA": pac.get("cta_palavra", ""), "Estado": estado, "Atualizado": quando}
        linhas.insert(ult + 1, _linha([str(valores.get(c, "")) for c in cols]))
    TRACKER.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def atualizar_status_video(slug: str, estado: str, dry: bool) -> None:
    p = ROOT / "videos" / slug / "status.json"
    if dry or not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    d["estado"], d["atualizado"] = estado, iso(agora())
    d.setdefault("historico", []).append({"estado": estado, "em": d["atualizado"]})
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ───────────────────────── vagas ─────────────────────────

def _hora(v) -> tuple[int, int]:
    if isinstance(v, int):  # YAML 1.1 lê 19:00 sem aspas como sexagesimal (1140)
        return v // 60, v % 60
    hh, mm = str(v).strip().split(":")
    return int(hh), int(mm)


def proximas_vagas(cfg: dict, tz: ZoneInfo, depois_de: dt.datetime, semanas: int = 8) -> list[dt.datetime]:
    regras = []
    for nome, horas in (cfg.get("vagas_semanais") or {}).items():
        d = DIAS.get(str(nome).lower().replace("-feira", "").strip())
        if d is None:
            raise ErroPublicacao(f"Dia inválido em vagas_semanais: {nome}")
        for h in horas if isinstance(horas, list) else [horas]:
            regras.append((d, *_hora(h)))
    if not regras:
        raise ErroPublicacao("calendario.md sem vagas_semanais")
    base = depois_de.astimezone(tz).date()
    out = []
    for i in range(semanas * 7 + 1):
        dia = base + dt.timedelta(days=i)
        for d, hh, mm in regras:
            if dia.weekday() == d:
                t = dt.datetime(dia.year, dia.month, dia.day, hh, mm, tzinfo=tz)
                if t > depois_de:
                    out.append(t)
    return sorted(out)


def _chave(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")


def vagas_ocupadas(txt: str, tz: ZoneInfo, exceto: str) -> set[str]:
    usadas = set()
    for c in ler_agenda(txt):
        if len(c) >= 2 and c[1] != exceto and "cancel" not in (c[3] if len(c) > 3 else "").lower():
            with contextlib.suppress(ValueError):
                usadas.add(_chave(dt.datetime.strptime(c[0][:16], "%Y-%m-%d %H:%M").replace(tzinfo=tz)))
    for pj in FILA.glob("*/post.json"):
        if pj.parent.name == exceto:
            continue
        with contextlib.suppress(Exception):
            t = ler_iso(json.loads(pj.read_text(encoding="utf-8")).get("publicar_em"))
            if t:
                usadas.add(_chave(t))
    return usadas


# ───────────────────────── pacote / post ─────────────────────────

def carregar_post(pasta: Path) -> dict | None:
    p = pasta / "post.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def salvar_post(pasta: Path, post: dict, dry: bool) -> None:
    if dry:
        return
    tmp = pasta / "post.json.tmp"
    tmp.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(pasta / "post.json")


def post_padrao(slug: str, pac: dict, cfg: dict) -> dict:
    arq = pac.get("arquivos") or {}
    return {
        "slug": slug,
        "publicar_em": None,
        "plataformas": list(cfg.get("plataformas_padrao") or ["instagram", "facebook"]),
        "estado": "agendado",
        "confirmar": True,
        "instagram": {"legenda_arquivo": "legenda-instagram.txt", "capa": arq.get("capa") or "capa/capa.png",
                      "share_to_feed": True,
                      "trial": ({"graduation_strategy": cfg["trial_padrao"]} if cfg.get("trial_padrao") else None),
                      "container_id": None, "media_id": None,
                      "permalink": None},
        "facebook": {"legenda_arquivo": "legenda-facebook.txt", "tipo": None, "video_id": None, "permalink": None},
        "material": {"palavra": pac.get("cta_palavra"), "arquivo": arq.get("material"),
                     "titulo": pac.get("material_titulo"), "url": None},
        "publicado_em": None,
        "erros": [],
    }


def mesclar(base: dict, existente: dict | None) -> dict:
    if not existente:
        return base
    out = dict(base)
    for k, v in existente.items():
        out[k] = mesclar(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def contar_hashtags(t: str) -> list[str]:
    return re.findall(r"(?:(?<=\s)|^)#\w+", t, re.M)


def validar_pacote(pasta: Path, post: dict | None, publicacao: bool = False) -> dict:
    """`publicacao=True` (hora de publicar) exige também o PORTÃO-PUBLICACAO aprovado sobre esta pasta;
    no `agendar` o portão ainda não rodou — ele audita o post.json que o agendar escreve."""
    erros, avisos = [], []
    pj = pasta / "pacote.json"
    if not pj.exists():
        raise ErroPublicacao(f"{pasta.name}: falta pacote.json")
    pac = json.loads(pj.read_text(encoding="utf-8"))
    if str(pac.get("qa", "")).upper() != "PASS":
        erros.append(f"QA não é PASS (qa = {pac.get('qa')!r})")
    arq = pac.get("arquivos") or {}
    for chave in ("video", "capa"):
        v = arq.get(chave)
        if not v or not (pasta / v).is_file():
            erros.append(f"arquivo em falta: {chave} ({v})")
    mat = arq.get("material")
    if mat and not (pasta / mat).is_file():
        erros.append(f"material prometido mas em falta: {mat}")
    ig_nome = ((post or {}).get("instagram") or {}).get("legenda_arquivo") or "legenda-instagram.txt"
    fb_nome = ((post or {}).get("facebook") or {}).get("legenda_arquivo") or "legenda-facebook.txt"
    ig, fb = pasta / ig_nome, pasta / fb_nome
    if not ig.is_file() or not ig.read_text(encoding="utf-8").strip():
        erros.append(f"falta {ig_nome} (escrita pelo agente publicador)")
    else:
        t = ig.read_text(encoding="utf-8").strip()
        if len(t) > IG_MAX_LEGENDA:
            erros.append(f"legenda do Instagram com {len(t)} caracteres (máx. {IG_MAX_LEGENDA})")
        tags = contar_hashtags(t)
        if len(tags) > IG_MAX_HASHTAGS:
            erros.append(f"legenda do Instagram com {len(tags)} hashtags (máx. {IG_MAX_HASHTAGS}): {' '.join(tags)}")
        palavra = pac.get("cta_palavra")
        if palavra and palavra.lower() not in t.lower():
            avisos.append(f"a palavra do CTA ({palavra}) não aparece na legenda do Instagram")
    if not fb.is_file() or not fb.read_text(encoding="utf-8").strip():
        erros.append(f"falta {fb_nome} (escrita pelo agente publicador)")
    v = arq.get("video")
    if v and (pasta / v).is_file() and Path(FFPROBE).exists():
        r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,codec_name:format=duration,size", "-of", "json", str(pasta / v)],
                           capture_output=True, text=True)
        with contextlib.suppress(Exception):
            info = json.loads(r.stdout)
            s, f = info["streams"][0], info["format"]
            dur, tam = float(f["duration"]), int(f["size"])
            if not 3 <= dur <= 900:
                erros.append(f"duração do vídeo {dur:.1f}s fora do permitido para Reels (3 s–15 min)")
            if abs(s["width"] / s["height"] - 9 / 16) > 0.02:
                avisos.append(f"vídeo {s['width']}×{s['height']} não é 9:16")
            if s["codec_name"] not in ("h264", "hevc"):
                avisos.append(f"codec {s['codec_name']} (recomendado H.264)")
            if tam > 300e6:
                avisos.append(f"vídeo com {tam / 1e6:.0f} MB (limite prático 300 MB)")
    # GAUNTLET (22/10): só sai o que os portões aprovaram — e os arquivos têm de ser OS MESMOS que eles viram.
    try:
        erros += portoes.conferir_pacote(pasta, pac, post, publicacao=publicacao)
    except Exception as e:  # livro corrompido, arquivo sumindo no meio do hash…: bloqueia SÓ este post
        erros.append(f"GAUNTLET: não consegui conferir os portões ({type(e).__name__}: {e})")
    if not pac.get("gauntlet") and pasta.name in portoes.legado():
        avisos.append("pacote LEGADO sem selo GAUNTLET (anterior a 22/10) — publica sem portões")
    for a in avisos:
        log.warning(f"{pasta.name}: {a}")
    if erros:
        raise ErroPublicacao(f"{pasta.name}: pacote inválido:\n  - " + "\n  - ".join(erros))
    return pac


# ───────────────────────── HTTP (Meta) ─────────────────────────

def _mostrar(k: str, v) -> str:
    if k.lower() in ("access_token", "input_token"):
        if "|" in str(v):  # token de app "id|segredo"
            a, b = str(v).split("|", 1)
            return f"{a}|{mascarar_valor(b)}"
        return mascarar_valor(v)
    if k.lower() == "authorization":
        p = str(v).split(" ", 1)
        return f"{p[0]} {mascarar_valor(p[1])}" if len(p) == 2 else "****"
    s = str(v)
    return s if len(s) <= 240 else s[:240].replace("\n", "⏎") + f"… ({len(s)} chars)"


class Http:
    def __init__(self, dry: bool):
        self.dry = dry
        self.s = requests.Session()
        self.n = 0

    def req(self, metodo: str, url: str, *, params=None, data=None, headers=None, fake=None,
            tentativas: int = 5, timeout: int = 60, arquivo: tuple | None = None) -> dict:
        """`arquivo` = (campo, caminho) envia o arquivo do disco em multipart/form-data;
        (campo, caminho, inicio, fim) envia só os bytes [inicio, fim) — pedaço do upload retomável."""
        if self.dry:
            self.n += 1
            linhas = [f"[dry-run #{self.n}] {metodo} {url}"]
            if isinstance(data, bytes):
                linhas.append(f"      corpo  {len(data) / 1e6:.2f} MB (binário)")
            if arquivo:
                tam = (arquivo[3] - arquivo[2]) if len(arquivo) == 4 else arquivo[1].stat().st_size
                linhas.append(f"      multipart {arquivo[0]} = @{arquivo[1].name} ({tam / 1e6:.2f} MB)")
            for nome, d in (("query", params), ("form", data if isinstance(data, dict) else None),
                            ("header", headers)):
                for k, v in (d or {}).items():
                    linhas.append(f"      {nome:<6} {k} = {_mostrar(k, v)}")
            log.info("\n".join(linhas))
            return dict(fake or {})
        for t in range(1, tentativas + 1):
            try:
                if arquivo and len(arquivo) == 4:  # pedaço [inicio, fim) do arquivo
                    with open(arquivo[1], "rb") as fh:
                        fh.seek(arquivo[2])
                        pedaco = fh.read(arquivo[3] - arquivo[2])
                    r = self.s.request(metodo, url, params=params, data=data, headers=headers, timeout=timeout,
                                       files={arquivo[0]: (arquivo[1].name, pedaco, "application/octet-stream")})
                elif arquivo:  # reabre a cada tentativa (o handle anterior já foi consumido)
                    with open(arquivo[1], "rb") as fh:
                        r = self.s.request(metodo, url, params=params, data=data, headers=headers, timeout=timeout,
                                           files={arquivo[0]: (arquivo[1].name, fh, "video/mp4")})
                else:
                    r = self.s.request(metodo, url, params=params, data=data, headers=headers, timeout=timeout)
            except (requests.ConnectionError, requests.Timeout) as e:
                if t == tentativas:
                    raise ErroRede(f"Sem ligação a {url.split('/')[2]} ({e.__class__.__name__}) após {t} tentativas")
                log.warning(f"rede: {e.__class__.__name__} — nova tentativa {t + 1}/{tentativas}")
                dormir(min(60, 2 ** t) + random.random())
                continue
            try:
                corpo = r.json()
            except ValueError:
                corpo = {"_texto": r.text[:400]}
            erro = corpo.get("error") if isinstance(corpo, dict) else None
            if r.ok and not erro:
                return corpo
            e = ErroMeta(r.status_code, erro if isinstance(erro, dict) else {"message": str(corpo)[:300]}, url)
            if e.transitorio and t < tentativas:
                log.warning(f"{e} — nova tentativa {t + 1}/{tentativas}")
                dormir(min(60, 2 ** t) + random.random())
                continue
            raise e
        raise ErroPublicacao("pedido falhou")  # pragma: no cover


# ───────────────────────── R2 ─────────────────────────

class R2:
    def __init__(self, dry: bool):
        self.dry = dry
        cfg = {k: os.environ.get(k) for k in R2_VARS}
        self.faltando = [k for k, v in cfg.items() if not v]
        if self.faltando and not dry:
            raise ErroPublicacao("Faltam variáveis do Cloudflare R2 no .env: " + ", ".join(self.faltando))
        self.bucket = cfg["R2_BUCKET_NAME"] or "<R2_BUCKET_NAME>"
        self.base = (cfg["R2_PUBLIC_URL"] or "https://<R2_PUBLIC_URL>").rstrip("/")
        self.endpoint = f"https://{cfg['R2_ACCOUNT_ID'] or '<R2_ACCOUNT_ID>'}.r2.cloudflarestorage.com"
        self._cli = None

    def cliente(self):
        if self._cli is None:
            import boto3
            from botocore.config import Config

            self._cli = boto3.client("s3", endpoint_url=self.endpoint, region_name="auto",
                                     aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                                     aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                                     config=Config(signature_version="s3v4",
                                                   retries={"max_attempts": 5, "mode": "standard"}))
        return self._cli

    def url(self, chave: str) -> str:
        return f"{self.base}/{quote(chave)}"

    def enviar(self, arquivo: Path, chave: str) -> str:
        ct = mimetypes.guess_type(arquivo.name)[0] or "application/octet-stream"
        mb = arquivo.stat().st_size / 1e6
        if self.dry:
            log.info(f"[dry-run] R2 PUT {self.endpoint}/{self.bucket}/{chave}  ({mb:.2f} MB, {ct})\n"
                     f"      → URL pública {self.url(chave)}")
            return self.url(chave)
        try:
            self.cliente().upload_file(str(arquivo), self.bucket, chave,
                                       ExtraArgs={"ContentType": ct, "CacheControl": "public, max-age=31536000"})
        except Exception as e:  # boto3 levanta vários tipos
            raise ErroPublicacao(f"Falha no upload para o R2 ({arquivo.name}): {mascarar(e)}")
        log.info(f"R2 ✓ {chave} ({mb:.2f} MB)")
        return self.url(chave)

    def conferir_publico(self, http: Http, url: str) -> None:
        if self.dry:
            return
        try:
            r = http.s.request("HEAD", url, timeout=30, allow_redirects=True)
        except requests.RequestException as e:
            raise ErroRede(f"Não consegui aceder ao URL público do R2 ({e.__class__.__name__}): {url}")
        if r.status_code != 200:
            raise ErroPublicacao(f"O R2 não serve o arquivo publicamente (HTTP {r.status_code}): {url} — "
                                 "confira R2_PUBLIC_URL / domínio público do bucket")


# ───────────────────────── Instagram ─────────────────────────

def _cred(nome: str, dry: bool) -> str:
    v = os.environ.get(nome)
    if v:
        return v
    if dry:
        return f"<{nome}>"
    raise ErroPublicacao(f"Variável {nome} não configurada no .env")


def status_container(http: Http, cont: str, tok: str) -> dict:
    return http.req("GET", f"{GRAPH}/{cont}", params={"fields": "status_code,status", "access_token": tok},
                    fake={"status_code": "FINISHED", "status": "Finished: Media has been uploaded"})


def aguardar_container(http: Http, cont: str, tok: str) -> None:
    for _ in range(POLL_MAX_S // POLL_INTERVALO + 1):
        r = status_container(http, cont, tok)
        sc = r.get("status_code")
        if sc in ("FINISHED", "PUBLISHED"):
            return
        if sc in ("ERROR", "EXPIRED"):
            raise ErroPublicacao(f"Instagram recusou o vídeo (container {sc}): {r.get('status')}")
        log.info(f"IG container {sc or '?'} — a aguardar {POLL_INTERVALO}s")
        dormir(POLL_INTERVALO)
    raise ErroPublicacao("Instagram não terminou de processar o vídeo em 10 min (container IN_PROGRESS)")


def recuperar_media(http: Http, uid: str, tok: str, legenda: str) -> str | None:
    r = http.req("GET", f"{GRAPH}/{uid}/media", params={"fields": "id,caption,timestamp", "limit": 5,
                                                         "access_token": tok}, fake={"data": []})
    for m in r.get("data", []):
        if (m.get("caption") or "").strip() == legenda.strip():
            return m.get("id")
    return None


def publicar_container(http: Http, uid: str, cont: str, tok: str, legenda: str) -> str:
    """media_publish NÃO é idempotente: antes de repetir, confirmar que não publicou mesmo assim."""
    for t in range(1, 6):
        try:
            r = http.req("POST", f"{GRAPH}/{uid}/media_publish", data={"creation_id": cont, "access_token": tok},
                         fake={"id": "DRYRUN_IG_MEDIA_ID"}, tentativas=1, timeout=120)
            return r["id"]
        except ErroPublicacao as e:
            nao_pronto = isinstance(e, ErroMeta) and (e.erro.get("code") == 9007)
            if not (e.transitorio or nao_pronto) or t == 5:
                raise
            log.warning(f"media_publish falhou ({e}); a confirmar estado do container…")
            with contextlib.suppress(ErroPublicacao):
                if status_container(http, cont, tok).get("status_code") == "PUBLISHED":
                    mid = recuperar_media(http, uid, tok, legenda)
                    if mid:
                        return mid
                    raise ErroPublicacao("O container já está PUBLISHED mas não encontrei o media_id — "
                                         "confira no Instagram antes de repetir (evitar post duplicado).")
            dormir(min(60, 5 * 2 ** t))
    raise ErroPublicacao("media_publish falhou")  # pragma: no cover


def publicar_instagram(http: Http, pasta: Path, post: dict, video_url: str, capa_url: str | None,
                       legenda: str) -> None:
    uid, tok = _cred("INSTAGRAM_USER_ID", http.dry), _cred("INSTAGRAM_ACCESS_TOKEN", http.dry)
    ig = post["instagram"]
    cont = ig.get("container_id")
    imp = portoes.estado(pasta, "publicacao")["impressao"]
    if cont and ig.get("container_impressao") not in (None, imp):
        # o conteúdo mudou (e o portão reaprovou) depois de o container ser criado: ele leva o vídeo/capa/legenda
        # velhos. Começa outro.
        log.info(f"container {cont} é de antes da última aprovação do portão — criando outro")
        cont = None
    if cont and not http.dry:  # retoma um container de uma tentativa anterior se ainda servir
        with contextlib.suppress(ErroPublicacao):
            sc = status_container(http, cont, tok).get("status_code")
            if sc in ("ERROR", "EXPIRED", None):
                cont = None
            elif sc == "PUBLISHED":
                mid = recuperar_media(http, uid, tok, legenda)
                if not mid:
                    raise ErroPublicacao("Container anterior já PUBLISHED; confira no Instagram (media_id desconhecido).")
                ig["media_id"] = mid
    if not ig.get("media_id"):
        if not cont:
            data = {"media_type": "REELS", "video_url": video_url, "caption": legenda,
                    "share_to_feed": "true" if ig.get("share_to_feed", True) else "false", "access_token": tok}
            if capa_url:
                data["cover_url"] = capa_url
            if ig.get("trial"):
                data["trial_params"] = json.dumps(ig["trial"])
            cont = http.req("POST", f"{GRAPH}/{uid}/media", data=data, fake={"id": "DRYRUN_IG_CONTAINER"},
                            timeout=120)["id"]
            ig["container_id"], ig["container_impressao"] = cont, imp
            salvar_post(pasta, post, http.dry)
            log.info(f"IG container criado: {cont}")
        aguardar_container(http, cont, tok)
        ig["media_id"] = publicar_container(http, uid, cont, tok, legenda)
        salvar_post(pasta, post, http.dry)
    try:
        r = http.req("GET", f"{GRAPH}/{ig['media_id']}", params={"fields": "permalink", "access_token": tok},
                     fake={"permalink": "https://www.instagram.com/reel/DRYRUN/"})
        ig["permalink"] = r.get("permalink")
    except ErroPublicacao as e:
        log.warning(f"IG publicado mas sem permalink: {e}")
    log.info(f"IG ✓ media {ig['media_id']} {ig.get('permalink') or ''}")


# ───────────────────────── Facebook: Reel da Página (≤ 90 s) ou vídeo da Página (> 90 s) ─────────────────────────

def _status_fb(http: Http, vid: str, tok: str, fields: str, fake: dict) -> dict:
    return http.req("GET", f"{GRAPH}/{vid}", params={"fields": fields, "access_token": tok}, fake=fake)


def _erro_fase(st: dict) -> str | None:
    s = st.get("status") or {}
    if s.get("video_status") == "error":
        return "video_status=error"
    for fase in ("uploading_phase", "processing_phase", "publishing_phase"):
        f = s.get(fase) or {}
        if f.get("status") == "error":
            return f"{fase}: {f.get('errors') or f}"
    return None


def duracao_video(pac: dict, video: Path) -> float | None:
    """`pacote.json` `duracao`; se faltar, mede com ffprobe (FFPROBE_BIN ou `ffprobe` do PATH)."""
    with contextlib.suppress(TypeError, ValueError):
        if pac.get("duracao") is not None:
            return float(pac["duracao"])
    exe = FFPROBE if Path(FFPROBE).exists() else shutil.which("ffprobe")
    if not exe or not video.is_file():
        return None
    r = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True)
    with contextlib.suppress(ValueError):
        return float(r.stdout.strip())
    return None


def publicar_facebook(http: Http, pasta: Path, post: dict, video: Path, legenda: str,
                      duracao: float | None = None) -> None:
    """≤ 90 s (ou duração desconhecida) → Reel da Página; > 90 s → vídeo da Página (a API de Reels recusa)."""
    if duracao is not None and duracao > FB_REEL_MAX_S:
        log.info(f"FB: vídeo com {duracao:.1f}s > {FB_REEL_MAX_S}s (limite da API de Reels) → VÍDEO DA PÁGINA "
                 f"(/{{page-id}}/videos)")
        return publicar_facebook_video(http, pasta, post, video, legenda)
    if duracao is None:
        log.warning("FB: duração do vídeo desconhecida — segue como Reel (a API de Reels só aceita 3–90 s)")
    else:
        log.info(f"FB: vídeo com {duracao:.1f}s ≤ {FB_REEL_MAX_S}s → REEL (/{{page-id}}/video_reels)")
    pid, tok = _cred("META_PAGE_ID", http.dry), _cred("META_PAGE_ACCESS_TOKEN", http.dry)
    fb = post["facebook"]
    fb["tipo"] = "reel"
    r = http.req("POST", f"{GRAPH}/{pid}/video_reels", data={"upload_phase": "start", "access_token": tok},
                 fake={"video_id": "DRYRUN_FB_VIDEO_ID", "upload_url": f"{RUPLOAD}/DRYRUN_FB_VIDEO_ID"})
    vid = r["video_id"]
    fb["video_id"], fb["permalink"] = vid, None
    salvar_post(pasta, post, http.dry)
    up = r.get("upload_url") or f"{RUPLOAD}/{vid}"
    # Envia o arquivo do Mac (não por file_url): o robô do Facebook leva 403 da Cloudflare no
    # media.korvuai.com, embora o do Instagram baixe normalmente (13/10).
    corpo = video.read_bytes()
    r = http.req("POST", up, headers={"Authorization": f"OAuth {tok}", "offset": "0",
                                      "file_size": str(len(corpo))},
                 data=corpo, fake={"success": True}, timeout=600)
    if not r.get("success"):
        raise ErroPublicacao(f"Facebook não aceitou o upload do vídeo (rupload): {str(r)[:200]}")
    ok_fake = {"status": {"video_status": "upload_complete", "uploading_phase": {"status": "complete"}}}
    for _ in range(60):  # até ~5 min para a Meta confirmar o recebimento
        st = _status_fb(http, vid, tok, "status", ok_fake)
        if (e := _erro_fase(st)):
            raise ErroPublicacao(f"Facebook falhou a receber o vídeo: {e}")
        if ((st.get("status") or {}).get("uploading_phase") or {}).get("status") == "complete":
            break
        dormir(POLL_INTERVALO)
    else:
        raise ErroPublicacao("Facebook não terminou de receber o vídeo em 5 min")
    r = http.req("POST", f"{GRAPH}/{pid}/video_reels",
                 data={"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                       "description": legenda, "access_token": tok},
                 fake={"success": True}, tentativas=2, timeout=120)
    if not r.get("success"):
        raise ErroPublicacao(f"Facebook não confirmou a publicação (finish): {str(r)[:200]}")
    fb["permalink"] = f"https://www.facebook.com/reel/{vid}"  # provisório até o status confirmar
    salvar_post(pasta, post, http.dry)
    pub_fake = {"status": {"video_status": "ready", "publishing_phase": {"status": "complete"}},
                "permalink_url": "/reel/DRYRUN_FB_VIDEO_ID"}
    for _ in range(POLL_MAX_S // POLL_INTERVALO + 1):
        st = _status_fb(http, vid, tok, "status,permalink_url", pub_fake)
        if (e := _erro_fase(st)):
            raise ErroPublicacao(f"Facebook falhou a processar/publicar o Reel: {e}")
        s = st.get("status") or {}
        if (s.get("publishing_phase") or {}).get("status") == "complete" or s.get("video_status") == "ready":
            if st.get("permalink_url"):
                p = st["permalink_url"]
                fb["permalink"] = p if p.startswith("http") else f"https://www.facebook.com{p}"
            break
        dormir(POLL_INTERVALO)
    else:
        log.warning("Facebook ainda a processar após 10 min; publicado (finish OK), permalink provisório")
    log.info(f"FB ✓ reel {vid} {fb['permalink']}")


def _upload_video_retomavel(http: Http, pid: str, tok: str, video: Path, legenda: str) -> str:
    """Upload retomável do vídeo da Página (start → transfer em pedaços → finish). O envio num pedido só
    (`source` multipart) deu 413 com 171 MB (Hinton, 15/10). Ref.: graph-api/reference/page/videos
    (upload_phase). Devolve o video_id."""
    url = f"{GRAPH_VIDEO}/{pid}/videos"
    tam = video.stat().st_size
    r = http.req("POST", url, data={"upload_phase": "start", "file_size": str(tam), "access_token": tok},
                 fake={"video_id": "DRYRUN_FB_PAGE_VIDEO_ID", "upload_session_id": "DRYRUN_SESSAO",
                       "start_offset": str(tam), "end_offset": str(tam)}, tentativas=3, timeout=120)
    vid, sessao = r.get("video_id"), r.get("upload_session_id")
    if not vid or not sessao:
        raise ErroPublicacao(f"Facebook não abriu a sessão de upload: {str(r)[:200]}")
    ini, fim = int(r.get("start_offset", 0)), int(r.get("end_offset", 0))
    while ini < fim:
        log.info(f"FB upload {ini / 1e6:.1f}–{fim / 1e6:.1f} de {tam / 1e6:.1f} MB")
        r = http.req("POST", url, data={"upload_phase": "transfer", "upload_session_id": sessao,
                                        "start_offset": str(ini), "access_token": tok},
                     arquivo=("video_file_chunk", video, ini, fim), tentativas=4, timeout=600,
                     fake={"start_offset": str(tam), "end_offset": str(tam)})
        ini, fim = int(r.get("start_offset", fim)), int(r.get("end_offset", fim))
    r = http.req("POST", url, data={"upload_phase": "finish", "upload_session_id": sessao,
                                    "description": legenda, "published": "true", "access_token": tok},
                 fake={"success": True}, tentativas=3, timeout=300)
    if not r.get("success"):
        raise ErroPublicacao(f"Facebook não confirmou o fim do upload: {str(r)[:200]}")
    return vid


def publicar_facebook_video(http: Http, pasta: Path, post: dict, video: Path, legenda: str) -> None:
    """Vídeo da Página (> 90 s): POST graph-video.facebook.com/{v}/{page-id}/videos, upload não retomável
    com o arquivo do disco em multipart `source` (até 1 GB / 20 min — limites da Meta), `description`,
    `published=true`. Ref.: https://developers.facebook.com/docs/graph-api/reference/page/videos/#Creating
    e https://developers.facebook.com/docs/video-api/guides/publishing (publicar vídeo na Página).
    Não é idempotente: uma só tentativa; se já há video_id desta via, só confere o estado (evita duplicado)."""
    pid, tok = _cred("META_PAGE_ID", http.dry), _cred("META_PAGE_ACCESS_TOKEN", http.dry)
    fb = post["facebook"]
    vid = fb.get("video_id") if fb.get("tipo") == "video" else None
    if vid:
        log.info(f"FB: vídeo da Página {vid} já enviado numa tentativa anterior — só confiro o estado")
    else:
        vid = _upload_video_retomavel(http, pid, tok, video, legenda)
    fb["tipo"], fb["video_id"] = "video", vid
    fb["permalink"] = fb.get("permalink") or f"https://www.facebook.com/{pid}/videos/{vid}/"  # provisório
    salvar_post(pasta, post, http.dry)
    pub_fake = {"status": {"video_status": "ready"}, "permalink_url": "/korvu/videos/DRYRUN_FB_PAGE_VIDEO_ID/"}
    for _ in range(POLL_MAX_S // POLL_INTERVALO + 1):
        st = _status_fb(http, vid, tok, "status,permalink_url", pub_fake)
        if (e := _erro_fase(st)):
            raise ErroPublicacao(f"Facebook falhou a processar o vídeo da Página: {e}")
        if (st.get("status") or {}).get("video_status") == "ready":
            if st.get("permalink_url"):
                p = st["permalink_url"]
                fb["permalink"] = p if p.startswith("http") else f"https://www.facebook.com{p}"
            break
        dormir(POLL_INTERVALO)
    else:
        log.warning("Facebook ainda a processar o vídeo após 10 min; publicado, permalink provisório")
    log.info(f"FB ✓ vídeo da Página {vid} {fb['permalink']}")


# ───────────────────────── DM bot (futuro) ─────────────────────────

def registrar_material_dm(palavra: str | None, media_id: str | None, material_url: str | None) -> None:
    """TODO(dm-bot): registar {palavra, media_id_instagram, material_url} no Supabase para o bot de DM
    responder a comentários com a palavra do CTA. Por agora só existe o dm-material.json na pasta."""
    return None


# ───────────────────────── fluxo principal ─────────────────────────

def preparar_capa(png: Path, tmp: Path) -> Path:
    """A Meta aceita melhor JPEG na capa (cover_url): converte PNG → JPEG."""
    from PIL import Image

    jpg = tmp / "capa.jpg"
    Image.open(png).convert("RGB").save(jpg, quality=92)
    return jpg


def registrar_erro(post: dict, plataforma: str, e: Exception) -> None:
    msg = mascarar(str(e))
    post.setdefault("erros", []).append({"plataforma": plataforma, "em": iso(agora()), "mensagem": msg})
    log.error(f"✗ {plataforma}: {msg}")


def _feito(post: dict, plat: str) -> bool:
    return bool(post["instagram"].get("media_id")) if plat == "instagram" else bool(post["facebook"].get("permalink"))


def publicar_slug(slug: str, http: Http, r2: R2 | None = None, *, sim: bool = False,
                  plataformas: list[str] | None = None, origem: str = "manual") -> dict:
    dry = http.dry
    pasta = FILA / slug
    if not pasta.is_dir():
        if (PUBLICADOS / slug).is_dir():
            raise ErroPublicacao(f"{slug} já está em 07-publicados/")
        raise ErroPublicacao(f"{slug} não está em 06-publicar/ (mover para lá = autorização para publicar)")
    existente = carregar_post(pasta)
    pac = validar_pacote(pasta, existente, publicacao=True)
    _, cfg = ler_calendario()
    post = mesclar(post_padrao(slug, pac, cfg), existente)
    if existente is None:
        post["publicar_em"], post["confirmar"] = iso(agora()), False
    if plataformas:
        post["plataformas"] = plataformas
    if post["estado"] == "publicado":
        raise ErroPublicacao(f"{slug} já está publicado")
    if post.get("confirmar") and not sim and origem == "manual":
        if not dry:
            raise ErroPublicacao(f"{slug} pede confirmação do Carlos: rode `publicar {slug} --sim` para confirmar.")
        log.info("[dry-run] (este post pede confirmação — na execução real seria preciso --sim)")
    r2 = r2 or R2(dry)
    if dry and r2.faltando:
        log.warning("[dry-run] variáveis do R2 em falta (necessárias na execução real): " + ", ".join(r2.faltando))
    if dry:
        faltam = [k for k in ("INSTAGRAM_USER_ID", "INSTAGRAM_ACCESS_TOKEN", "META_PAGE_ID",
                              "META_PAGE_ACCESS_TOKEN") if not os.environ.get(k)]
        if faltam:
            log.warning("[dry-run] variáveis da Meta em falta: " + ", ".join(faltam))

    log.info(f"▶ publicar {slug} → {', '.join(post['plataformas'])} (Graph {GRAPH_VERSION}){' [DRY-RUN]' if dry else ''}")
    post["estado"] = "publicando"
    salvar_post(pasta, post, dry)
    atualizar_agenda(slug, dry, estado="publicando")
    ig_leg = (pasta / post["instagram"]["legenda_arquivo"]).read_text(encoding="utf-8").strip()
    fb_leg = (pasta / post["facebook"]["legenda_arquivo"]).read_text(encoding="utf-8").strip()

    try:
        with tempfile.TemporaryDirectory() as td:
            base = f"reels/{slug}"
            video = pasta / pac["arquivos"]["video"]
            video_url = r2.enviar(video, f"{base}/{video.name}")
            capa_url = r2.enviar(preparar_capa(pasta / post["instagram"]["capa"], Path(td)), f"{base}/capa.jpg")
            # Só o PDF de post.material.arquivo vai para o R2 (que é PÚBLICO). Nunca a pasta material/ inteira:
            # dossiê, fontes.json e cópia de obra são estudo e não podem sair de casa (contratos §1a, 13/10).
            mat_arq = (post.get("material") or {}).get("arquivo")
            if mat_arq:
                f = (pasta / mat_arq).resolve()
                if not f.is_file() or (pasta / "material").resolve() not in f.parents:
                    raise ErroPublicacao(f"material.arquivo inválido (tem de ser um arquivo em material/): {mat_arq}")
                post["material"]["url"] = r2.enviar(f, f"{base}/material/{f.name}")
            sobras = [f.name for f in (pasta / "material").glob("*")
                      if f.is_file() and not f.name.startswith(".") and (not mat_arq or f.name != Path(mat_arq).name)
                      ] if (pasta / "material").is_dir() else []
            if sobras:
                log.warning(f"material/ tem arquivos que NÃO vão para o R2: {', '.join(sorted(sobras))}")
            r2.conferir_publico(http, video_url)
            salvar_post(pasta, post, dry)
    except ErroPublicacao as e:
        registrar_erro(post, "r2", e)
        post["estado"] = "erro"
        salvar_post(pasta, post, dry)
        atualizar_agenda(slug, dry, estado="erro")
        notificar("Korvu — erro na publicação", f"{slug}: upload R2 falhou", dry)
        return post

    for plat in post["plataformas"]:
        if _feito(post, plat):
            log.info(f"{plat}: já publicado antes — a saltar")
            continue
        try:
            if plat == "instagram":
                publicar_instagram(http, pasta, post, video_url, capa_url, ig_leg)
                m = post.get("material") or {}
                dm = {"palavra": m.get("palavra"), "media_id_instagram": post["instagram"]["media_id"],
                      "material_url": m.get("url")}
                if dry:
                    log.info(f"[dry-run] dm-material.json = {json.dumps(dm, ensure_ascii=False)}")
                else:
                    (pasta / "dm-material.json").write_text(json.dumps(dm, ensure_ascii=False, indent=2) + "\n",
                                                            encoding="utf-8")
                registrar_material_dm(dm["palavra"], dm["media_id_instagram"], dm["material_url"])
            elif plat == "facebook":
                publicar_facebook(http, pasta, post, video, fb_leg, duracao_video(pac, video))
            else:
                raise ErroPublicacao(f"plataforma desconhecida: {plat}")
        except ErroPublicacao as e:
            registrar_erro(post, plat, e)
        salvar_post(pasta, post, dry)

    if all(_feito(post, p) for p in post["plataformas"]):
        post["estado"], post["publicado_em"] = "publicado", iso(agora())
        destino = PUBLICADOS / slug
        if dry:
            log.info(f"[dry-run] mover 06-publicar/{slug} → 07-publicados/{slug}")
            log.info("[dry-run] post.json final:\n" + json.dumps(post, ensure_ascii=False, indent=2))
        else:
            salvar_post(pasta, post, dry)
            PUBLICADOS.mkdir(parents=True, exist_ok=True)
            if destino.exists():
                destino = PUBLICADOS / f"{slug}-{agora().strftime('%Y%m%d%H%M%S')}"
            shutil.move(str(pasta), str(destino))
        if sim:
            _, cfg = ler_calendario()
            definir_confirmar_restantes(max(0, int(cfg.get("modo_confirmar_restantes") or 0) - 1), dry)
        atualizar_agenda(slug, dry, estado="publicado")
        atualizar_tracker(slug, "publicado", pac, dry)
        atualizar_status_video(slug, "publicado", dry)
        links = " ".join(x for x in [post["instagram"].get("permalink"), post["facebook"].get("permalink")] if x)
        notificar("Korvu — Reel publicado", f"{slug} {links}", dry)
        log.info(f"✓ {slug} publicado{' (dry-run)' if dry else ' → ' + str(destino.relative_to(ROOT))}")
    else:
        post["estado"] = "erro"
        salvar_post(pasta, post, dry)
        atualizar_agenda(slug, dry, estado="erro")
        falhou = [p for p in post["plataformas"] if not _feito(post, p)]
        notificar("Korvu — erro na publicação", f"{slug}: falhou {', '.join(falhou)} (rode publicar {slug})", dry)
        log.error(f"✗ {slug}: falhou {', '.join(falhou)}; o que já foi publicado ficou registado. "
                  f"Corrija e rode `publicar {slug}` (só repete o que falta).")
    return post


def cmd_agendar(slug: str, em: str | None, reagendar: bool, dry: bool) -> dict:
    pasta = FILA / slug
    if not pasta.is_dir():
        raise ErroPublicacao(f"{slug} não está em 06-publicar/ (mover para lá = autorização para publicar)")
    existente = carregar_post(pasta)
    pac = validar_pacote(pasta, existente)
    txt, cfg = ler_calendario()
    tz = fuso(cfg)
    post = mesclar(post_padrao(slug, pac, cfg), existente)
    if post["estado"] in ("publicado", "publicando"):
        raise ErroPublicacao(f"{slug} está '{post['estado']}' — não dá para agendar")
    ocupadas = vagas_ocupadas(txt, tz, slug)
    atual = ler_iso(post.get("publicar_em"))
    if em:
        t = ler_iso(em) if "T" in em else None
        if t is None:
            try:
                t = dt.datetime.strptime(em.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=tz)
            except ValueError:
                raise ErroPublicacao('--em deve ser "AAAA-MM-DD HH:MM" (fuso do calendário) ou ISO 8601')
        if _chave(t) in ocupadas:
            raise ErroPublicacao(f"{t.strftime('%Y-%m-%d %H:%M')} já está ocupado por outro post")
    elif atual and atual > agora() and post["estado"] == "agendado" and not reagendar:
        t = atual
        log.info(f"{slug} já estava agendado para {iso(t)} (use --reagendar para mudar)")
    else:
        livres = [v for v in proximas_vagas(cfg, tz, agora()) if _chave(v) not in ocupadas]
        if not livres:
            raise ErroPublicacao("Sem vagas livres nas próximas 8 semanas — acrescente vagas no calendário")
        t = livres[0]
    t = t.astimezone(tz)
    restantes = int(cfg.get("modo_confirmar_restantes") or 0)
    post.update({"publicar_em": iso(t), "estado": "agendado", "confirmar": restantes > 0})
    if dry:
        log.info("[dry-run] post.json:\n" + json.dumps(post, ensure_ascii=False, indent=2))
    salvar_post(pasta, post, dry)
    atualizar_agenda(slug, dry, data_hora=t.strftime("%Y-%m-%d %H:%M"), plataformas=", ".join(post["plataformas"]),
                     estado="agendado (confirmar)" if post["confirmar"] else "agendado")
    atualizar_tracker(slug, "agendado", pac, dry)
    atualizar_status_video(slug, "agendado", dry)
    log.info(f"✓ {slug} agendado para {t.strftime('%a %d/%m %H:%M')} ({tz.key})"
             + (" — vai pedir confirmação" if post["confirmar"] else ""))
    return post


def cmd_due(http: Http) -> int:
    n = agora()
    falhas = 0
    for pj in sorted(FILA.glob("*/post.json")):
        pasta, slug = pj.parent, pj.parent.name
        try:
            post = json.loads(pj.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            log.error(f"{slug}: post.json ilegível ({e})")
            continue
        est = post.get("estado")
        if est == "aguardando_confirmacao":
            log.info(f"{slug}: aguardando confirmação — `publicar {slug} --sim`")
            continue
        if est == "publicando":
            log.warning(f"{slug}: ficou 'publicando' numa execução anterior — confira e rode `publicar {slug}`")
            continue
        if est != "agendado":
            continue
        quando = ler_iso(post.get("publicar_em"))
        if not quando:
            log.warning(f"{slug}: agendado sem publicar_em válido")
            continue
        if quando > n:
            continue
        atraso_h = (n - quando).total_seconds() / 3600
        if post.get("confirmar") or atraso_h > ATRASO_MAX_H:
            motivo = "pede confirmação" if post.get("confirmar") else f"atrasado {atraso_h:.1f} h"
            if http.dry:
                log.info(f"[dry-run] {slug}: {motivo} → ficaria 'aguardando_confirmacao' + notificação")
                continue
            post["estado"] = "aguardando_confirmacao"
            salvar_post(pasta, post, False)
            atualizar_agenda(slug, False, estado="aguardando confirmação")
            notificar("Korvu — Reel pronto a publicar", f"{slug} ({motivo}). Confirme: publicar {slug} --sim")
            log.info(f"{slug}: {motivo} → aguardando_confirmacao (notificado)")
            continue
        try:
            if publicar_slug(slug, http, origem="due")["estado"] != "publicado":
                falhas += 1
        except ErroPublicacao as e:
            falhas += 1
            log.error(f"✗ {slug}: {e}")
            if not http.dry:
                post = carregar_post(pasta) or post
                registrar_erro(post, "validacao", e)
                post["estado"] = "erro"
                salvar_post(pasta, post, False)
                atualizar_agenda(slug, False, estado="erro")
                notificar("Korvu — erro na publicação", f"{slug}: {str(e)[:120]}")
    return 1 if falhas else 0


def cmd_verificar(http: Http) -> int:
    env = {k: os.environ.get(k) for k in ("INSTAGRAM_USER_ID", "INSTAGRAM_ACCESS_TOKEN", "META_PAGE_ID",
                                          "META_PAGE_ACCESS_TOKEN", "META_APP_ID", "META_APP_SECRET", *R2_VARS)}
    log.info(f"Graph API: {GRAPH_VERSION}")
    for k, v in env.items():
        mostra = (mascarar_valor(v) if k in SEGREDOS else v) if v else "— em falta"
        log.info(f"  {k:<24} {mostra}")
    problemas = 0

    def tentar(nome: str, f):
        nonlocal problemas
        try:
            f()
        except ErroPublicacao as e:
            problemas += 1
            log.error(f"✗ {nome}: {e}")

    uid, igt, pid, pgt = (env[k] for k in ("INSTAGRAM_USER_ID", "INSTAGRAM_ACCESS_TOKEN", "META_PAGE_ID",
                                           "META_PAGE_ACCESS_TOKEN"))
    if uid and igt:
        tentar("Instagram (conta)", lambda: log.info("✓ IG conta: " + json.dumps(http.req(
            "GET", f"{GRAPH}/{uid}", params={"fields": "id,username,name", "access_token": igt},
            fake={"id": uid, "username": "korvu_oficial"}), ensure_ascii=False)))
        tentar("Instagram (dono do token)", lambda: log.info("✓ token IG pertence a: " + json.dumps(http.req(
            "GET", f"{GRAPH}/me", params={"fields": "id,name", "access_token": igt}, fake={"id": "0"}),
            ensure_ascii=False)))
    else:
        problemas += 1
        log.error("✗ INSTAGRAM_USER_ID / INSTAGRAM_ACCESS_TOKEN em falta")
    if pid and pgt:
        tentar("Página", lambda: log.info("✓ Página: " + json.dumps(http.req(
            "GET", f"{GRAPH}/{pid}", params={"fields": "id,name", "access_token": pgt},
            fake={"id": pid, "name": "Korvu"}), ensure_ascii=False)))
    else:
        problemas += 1
        log.error("✗ META_PAGE_ID / META_PAGE_ACCESS_TOKEN em falta")
    app, sec = env["META_APP_ID"], env["META_APP_SECRET"]
    if app and sec:
        for nome, tok, precisa in (("token IG", igt, ESCOPOS_IG), ("token Página", pgt, ESCOPOS_PAGINA)):
            if not tok:
                continue

            def dbg(nome=nome, tok=tok, precisa=precisa):
                d = http.req("GET", f"{GRAPH}/debug_token", params={"input_token": tok, "access_token": f"{app}|{sec}"},
                             fake={"data": {"is_valid": True, "type": "PAGE", "expires_at": 0,
                                            "scopes": sorted(precisa)}}).get("data", {})
                exp = d.get("expires_at")
                exp_txt = "nunca" if exp == 0 else (dt.datetime.fromtimestamp(exp).astimezone().strftime("%Y-%m-%d %H:%M")
                                                    if exp else "?")
                falta = sorted(precisa - set(d.get("scopes") or []))
                log.info(f"{'✓' if d.get('is_valid') else '✗'} {nome}: válido={d.get('is_valid')} tipo={d.get('type')} "
                         f"expira={exp_txt} app={d.get('app_id', '?')}"
                         + (f" | escopos em falta: {', '.join(falta)}" if falta else ""))
                if not d.get("is_valid") or falta:
                    raise ErroPublicacao(f"{nome} inválido ou sem permissões")
                if exp and exp - time.time() < 7 * 86400:
                    log.warning(f"⚠ {nome} expira em menos de 7 dias")

            tentar(f"debug {nome}", dbg)
    else:
        log.info("(META_APP_ID/META_APP_SECRET ausentes — sem debug_token)")
    if all(env[k] for k in R2_VARS):
        r2 = R2(http.dry)
        if http.dry:
            log.info(f"[dry-run] R2 HEAD bucket {r2.endpoint}/{r2.bucket}")
        else:
            def head():
                try:
                    r2.cliente().head_bucket(Bucket=r2.bucket)
                except Exception as e:
                    raise ErroPublicacao(f"R2 inacessível: {mascarar(e)}")
                log.info(f"✓ R2 bucket {r2.bucket} acessível")
            tentar("R2", head)
    else:
        problemas += 1
        log.error("✗ variáveis do R2 incompletas")
    return 1 if problemas else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Publicação de Reels (Instagram + Facebook).")
    ap.add_argument("--due", action="store_true", help="publica/processa o que já chegou à hora")
    ap.add_argument("--dry-run", action="store_true", help="não escreve em lado nenhum; imprime os pedidos")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("agendar", help="valida o pacote e reserva a próxima vaga")
    p.add_argument("slug")
    p.add_argument("--em", help='"AAAA-MM-DD HH:MM" no fuso do calendário')
    p.add_argument("--reagendar", action="store_true")
    p.add_argument("--dry-run", dest="dry_sub", action="store_true")
    p = sub.add_parser("publicar", help="publica já")
    p.add_argument("slug")
    p.add_argument("--sim", action="store_true", help="o Carlos confirmou (desconta modo_confirmar_restantes)")
    p.add_argument("--plataformas", help="ex.: instagram ou instagram,facebook")
    p.add_argument("--dry-run", dest="dry_sub", action="store_true")
    p = sub.add_parser("verificar-tokens", help="confere tokens da Meta e acesso ao R2 (só leituras)")
    p.add_argument("--dry-run", dest="dry_sub", action="store_true")
    a = ap.parse_args(argv)
    dry = a.dry_run or getattr(a, "dry_sub", False)
    portoes.SO_LEITURA = dry  # --dry-run não escreve nada local, nem o cache de hashes dos portões
    configurar_log()
    if not a.due and not a.cmd:
        ap.print_help()
        return 2
    try:
        if a.cmd == "verificar-tokens":
            return cmd_verificar(Http(dry))
        ctx = contextlib.nullcontext() if dry else trava()
        with ctx:
            if a.due:
                return cmd_due(Http(dry))
            if a.cmd == "agendar":
                cmd_agendar(a.slug, a.em, a.reagendar, dry)
                return 0
            plats = [x.strip() for x in a.plataformas.split(",")] if a.plataformas else None
            post = publicar_slug(a.slug, Http(dry), sim=a.sim, plataformas=plats)
            return 0 if post["estado"] == "publicado" else 1
    except Ocupado as e:
        log.warning(str(e))
        return 0 if a.due else 1
    except ErroPublicacao as e:
        log.error(f"✗ {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
