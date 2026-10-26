"""Utilitários compartilhados da skill corte-por-roteiro.

Caminhos, ffmpeg/ffprobe, JSON, normalização de texto (PT-BR), RMS de áudio
e o cálculo de "peças" (sub-intervalos de um segmento da EDL) usado por
edl.py, render_corte.py, filmstrip.py e verify.py.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from unidecode import unidecode

# ---------------------------------------------------------------- caminhos
ROOT = Path(__file__).resolve().parents[4]          # .../CONTENT AI
SKILL_DIR = Path(__file__).resolve().parents[1]
if (ROOT / ".env").exists():                         # nunca imprimir o .env
    load_dotenv(ROOT / ".env", override=False)

FFMPEG = os.environ.get("FFMPEG_BIN") or "/Users/teste/bin/ffmpeg"
FFPROBE = os.environ.get("FFPROBE_BIN") or "/opt/homebrew/bin/ffprobe"


def _fps_projeto() -> int | float:
    """Frame rate do projeto: env FPS_PROJETO (padrão 25 — Lumix S5IIX grava 25p)."""
    v = (os.environ.get("FPS_PROJETO") or "").strip()
    try:
        f = float(v) if v else 25.0
    except ValueError:
        print(f"[AVISO] FPS_PROJETO inválido ({v!r}) — usando 25", file=sys.stderr)
        f = 25.0
    if f <= 0:
        f = 25.0
    return int(round(f)) if abs(f - round(f)) < 1e-9 else f


FPS = _fps_projeto()
SR = 48000
LARGURA, ALTURA = 1080, 1920          # corte.mp4 / saída
# Intermediário do PRINCIPAL (edicao/fontes/*.mp4): supersampled 1440x2560 — o punch-in do corte (1.12–1.33)
# recorta daqui e ainda REDUZ para 1080x1920 (nunca amplia). Largura 1440: fora do bug do libx264 4:2:2 10-bit
# multithread (larguras 1920/3840); o ingest decodifica o arquivo inteiro para conferir.
LARGURA_INTER, ALTURA_INTER = 1440, 2560
FRAME = 1.0 / FPS
# 2026-09-18 (Carlos): peça de corte mais curta que isto não se lê — vira um relance e faz o enquadramento
# "dar um zoom e voltar de novo". É absorvida pelo corte à volta (ver pecas_do_segmento).
MIN_PECA_S = 0.8
GOP = max(1, int(round(FPS)))

# Perfil de cor da câmera (env CAMERA_PERFIL): "vlog" = V-Log/V-Gamut (Lumix S5IIX). Fontes camera-* em log
# NÃO são convertidas na ingestão — a transformação de entrada é trabalho do colorista (/cor).
CAMERA_PERFIL = (os.environ.get("CAMERA_PERFIL") or "vlog").strip().lower() or "vlog"

# Intermediários (edicao/fontes/*.mp4 e edicao/corte.mp4): H.264 High 4:2:2 10-bit, para o log não ser
# quantizado a 8 bits antes da cor. A saída final (Remotion/Instagram) continua 8-bit yuv420p bt709.
PIX_FMT_INTER = "yuv422p10le"
ENC_INTERMEDIARIO = ["-c:v", "libx264", "-preset", "medium", "-crf", "12", "-profile:v", "high422",
                     "-pix_fmt", PIX_FMT_INTER]
TAGS_709 = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]

# LUT de VISUALIZAÇÃO do log (V-Log -> Rec.709) usada só no que é mostrado antes da cor (preview, filmstrip,
# candidatos de capa). É a mesma entrada-camera.cube que o colorista usa como transformação de entrada.
LUT_ENTRADA_CAMERA = Path(os.environ.get("LUT_ENTRADA_CAMERA")
                          or ROOT / "00-marca" / "cor" / "luts" / "entrada-camera.cube")

TIPOS_FONTE = ("camera", "celular", "tela")
TIPO_AMOSTRA_COR = "amostra_cor"          # brutos/*-cor.* (ex.: camera-00-cor.mov): só para o colorista
EXT_VIDEO = {".mov", ".mp4", ".m4v"}
_RE_AMOSTRA_COR = re.compile(r"[-_]cor$")


def resolver_video_dir(arg: str) -> Path:
    """Aceita caminho (absoluto/relativo) ou só o slug (videos/<slug>)."""
    p = Path(arg).expanduser()
    if p.is_dir():
        return p.resolve()
    q = ROOT / "videos" / arg
    if q.is_dir():
        return q.resolve()
    sys.exit(f"[ERRO] pasta do vídeo não encontrada: {arg}")


def edicao(vd: Path) -> Path:
    d = vd / "edicao"
    d.mkdir(parents=True, exist_ok=True)
    return d


def rel(vd: Path, p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(vd.resolve()))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------- JSON
def ler_json(p: Path, padrao=None):
    p = Path(p)
    if not p.exists():
        if padrao is not None:
            return padrao
        sys.exit(f"[ERRO] arquivo não encontrado: {p}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def escrever_json(p: Path, dados) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tmp-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, p)


# ---------------------------------------------------------------- ffmpeg
def run(cmd: list, *, capturar: bool = True, check: bool = True, entrada: bytes | None = None):
    cmd = [str(c) for c in cmd]
    r = subprocess.run(cmd, input=entrada, capture_output=capturar)
    if check and r.returncode != 0:
        err = (r.stderr or b"").decode("utf-8", "replace")[-3000:]
        raise RuntimeError(f"comando falhou ({r.returncode}): {' '.join(cmd[:6])} ...\n{err}")
    return r


def ffmpeg(args: list, **kw):
    return run([FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", *args], **kw)


def ffprobe_json(path: Path) -> dict:
    r = run([FFPROBE, "-v", "error", "-print_format", "json", "-show_format",
             "-show_streams", str(path)])
    return json.loads(r.stdout.decode("utf-8", "replace"))


def verificar_decodificavel(path: Path, segundos: float | None = 2.0) -> None:
    """Falha alto se um intermediário recém-codificado não decodifica (ex.: o libx264 4:2:2 10-bit do ffmpeg 7.1
    estático gera stream ilegível em larguras 1920/3840 com várias threads — por isso os 10-bit são 1080 ou 1440
    de largura). Confere o pix_fmt no ffprobe e decodifica os primeiros `segundos` (None = o arquivo inteiro)."""
    info = ffprobe_json(path)
    vs = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    if vs is None or vs.get("pix_fmt") in (None, "", "unknown"):
        raise RuntimeError(f"{Path(path).name}: o ffprobe não reconhece o vídeo gerado "
                           f"(pix_fmt {vs.get('pix_fmt') if vs else '—'}) — arquivo inválido")
    lim = ["-t", f"{segundos:g}"] if segundos else []
    r = run([FFMPEG, "-hide_banner", "-nostdin", "-v", "error", "-xerror", *lim, "-i", str(path),
             "-map", "0:v:0", "-f", "null", "-"], check=False)
    err = (r.stderr or b"").decode("utf-8", "replace").strip()
    if r.returncode != 0 or err:
        raise RuntimeError(f"{Path(path).name}: não decodifica — arquivo inválido\n{err[-800:]}")


def duracao(path: Path) -> float:
    info = ffprobe_json(path)
    return float(info.get("format", {}).get("duration") or 0.0)


def duracoes_streams(path: Path) -> dict:
    """{'video': s, 'audio': s} — duração de cada stream (ffprobe)."""
    info = ffprobe_json(path)
    out = {}
    for s in info.get("streams", []):
        t = s.get("codec_type")
        if t in ("video", "audio") and t not in out:
            d = s.get("duration")
            if d is None and s.get("tags", {}).get("DURATION"):
                h, m, sec = s["tags"]["DURATION"].split(":")
                d = int(h) * 3600 + int(m) * 60 + float(sec)
            if d is None and t == "video" and s.get("nb_frames"):
                d = int(s["nb_frames"]) / FPS
            out[t] = float(d) if d is not None else None
    return out


# ---------------------------------------------------------------- áudio da voz
# Caminho SEM PERDAS: ingest -> edicao/audio48k/<fonte>.wav (48 kHz 24-bit mono, faixa da câmera) -> render_corte
# (peças + alças + crossfades) -> edicao/corte-audio.wav (24-bit) -> audio.py (master) -> AAC 256k só no final.
# Na ingestão, SÓ um passa-altas suave (60 Hz, 12 dB/oitava = 2 polos): o afftdn=nf=-25 antigo tirava ~10 dB de
# 5–16 kHz (voz "abafada"). Redução de ruído só com --limpar-ruido (afftdn suave, piso medido).
HIGHPASS_VOZ = "highpass=f=60:poles=2"
CORTE_AUDIO = "corte-audio.wav"
PCM_MASTER = ["-c:a", "pcm_s24le", "-ar", str(SR), "-ac", "1"]


def cadeia_denoise(piso_db: float = -60.0) -> str:
    """Redução de ruído SUAVE (opt-in): 8 dB no máximo, piso de ruído medido (afftdn aceita −80…−20), com rastreio."""
    nf = max(-80.0, min(-20.0, float(piso_db)))
    return f"afftdn=nr=8:nf={nf:.0f}:tn=1"


def cadeia_audio_ingest(limpar_ruido: bool = False, piso_db: float = -60.0) -> str:
    return HIGHPASS_VOZ + (f",{cadeia_denoise(piso_db)}" if limpar_ruido else "")


def cadeia_limpeza_audio(piso_db: float = -60.0) -> str:
    """Limpeza opcional de voz (audio.py --limpar): passa-altas 60 Hz + afftdn suave. Não é mais o padrão."""
    return cadeia_audio_ingest(True, piso_db)


def wav48k_path(vd: Path, fonte: str) -> Path:
    """Master de áudio sem perdas da fonte principal (48 kHz 24-bit mono)."""
    return Path(vd) / "edicao" / "audio48k" / f"{fonte}.wav"


def ler_audio(path, t0: float = 0.0, t1: float | None = None, faixa: str = "0:a:0", sr: int = SR):
    """Trecho de áudio em float32 mono — SÓ o 1.º canal (downmix de estéreo idêntico somaria +3 dB)."""
    import numpy as np
    lim = ["-t", f"{t1 - t0:.4f}"] if t1 is not None else []
    r = run([FFMPEG, "-hide_banner", "-nostdin", "-v", "error", "-ss", f"{t0:.4f}", *lim, "-i", str(path),
             "-map", faixa, "-af", "pan=mono|c0=c0", "-ar", str(sr), "-f", "f32le", "-"])
    return np.frombuffer(r.stdout, np.float32)


BANDAS_REF = ((60, 250), (250, 2000), (2000, 5000), (5000, 10000), (10000, 16000))


def energia_bandas(x, sr: int = SR) -> dict:
    """Energia relativa por banda (dB em relação a 60 Hz–16 kHz; Welch, Hann 8192, 50 %) + crest factor (pico/RMS
    em dB) e RMS (dBFS). Mede tilt de EQ (voz abafada = 2–16 kHz caindo) e esmagamento (crest baixo)."""
    import numpy as np
    x = np.asarray(x, dtype=np.float64)
    n = 8192
    if len(x) < n:
        x = np.pad(x, (0, n - len(x)))
    hop = n // 2
    win = np.hanning(n)
    k = 1 + (len(x) - n) // hop
    idx = np.arange(n)[None, :] + hop * np.arange(k)[:, None]
    fr = x[idx]
    fr = (fr - fr.mean(axis=1, keepdims=True)) * win
    p = (np.abs(np.fft.rfft(fr, axis=1)) ** 2).mean(axis=0)
    f = np.fft.rfftfreq(n, 1 / sr)
    tot = p[(f >= 60) & (f < 16000)].sum() + 1e-30
    out = {f"{a}-{b}": round(float(10 * np.log10(p[(f >= a) & (f < b)].sum() / tot + 1e-30)), 1) for a, b in BANDAS_REF}
    rms = float(np.sqrt((x ** 2).mean()) + 1e-12)
    out["crest"] = round(float(20 * np.log10((np.abs(x).max() + 1e-12) / rms)), 1)
    out["rms_db"] = round(float(20 * np.log10(rms)), 1)
    return out


# ---------------------------------------------------------------- enquadramento (punch-in no corte)
# Técnica padrão de talking head: a cada corte entre peças da mesma câmera o enquadramento ALTERNA (1.00 ↔ 1.12),
# origem no rosto. Aplicado UMA vez, no render_corte (recorte do intermediário 1440x2560 -> 1080x1920, lanczos,
# 10 bits); edl.json.zoom_no_corte = true faz o Remotion ignorar o zoom dos segmentos.
ZOOM_ESCALA = 1.12
ZOOM_ORIGEM = "50% 38%"            # sem rosto detectado (= ZOOM.origem do remotion/src/brand.ts)
ZOOM_MAX = 1.33                    # 1440/1080: acima disso o corte ampliaria o intermediário


def parse_origem(origem) -> tuple[float, float]:
    """'43% 36%' | [0.43, 0.36] -> (0.43, 0.36). Inválido -> ZOOM_ORIGEM."""
    try:
        if isinstance(origem, (list, tuple)) and len(origem) == 2:
            x, y = float(origem[0]), float(origem[1])
        else:
            a, b = str(origem).replace("%", " ").split()[:2]
            x, y = float(a) / 100, float(b) / 100
        return min(1.0, max(0.0, x)), min(1.0, max(0.0, y))
    except (TypeError, ValueError):
        return parse_origem(ZOOM_ORIGEM) if origem != ZOOM_ORIGEM else (0.5, 0.38)


def fmt_origem(x: float, y: float) -> str:
    return f"{100 * x:.1f}% {100 * y:.1f}%"


def zoom_das_pecas(seg: dict, n: int) -> list[float]:
    """Escala de cada uma das `n` peças do segmento: `zoom_pecas` (plano do edl.py / editado à mão) se tiver o
    tamanho certo; senão (EDL antiga) o `zoom` punch do segmento inteiro, ou 1.0."""
    zp = seg.get("zoom_pecas")
    if isinstance(zp, list) and len(zp) == n:
        try:
            return [min(ZOOM_MAX, max(1.0, float(z))) for z in zp]
        except (TypeError, ValueError):
            pass
    z = seg.get("zoom") or {}
    e = float(z.get("escala") or 1.0) if z.get("tipo") == "punch" else 1.0
    return [min(ZOOM_MAX, max(1.0, e))] * n


def janela_zoom(w: int, h: int, escala: float, origem, w_out: int = LARGURA, h_out: int = ALTURA):
    """Recorte (cw, ch, x, y) em px da fonte w x h para o punch-in `escala` com ponto fixo `origem` (semântica do
    CSS transform-origin: o ponto da origem fica parado na tela; o recorte nunca sai do quadro). Proporção de saída."""
    ox, oy = parse_origem(origem)
    cw = min(w, w / max(1.0, escala))
    ch = cw * h_out / w_out
    if ch > h:
        ch = h
        cw = ch * w_out / h_out
    cw, ch = int(round(cw / 2)) * 2, int(round(ch / 2)) * 2
    x = int(round(ox * (w - cw) / 2)) * 2
    y = int(round(oy * (h - ch) / 2)) * 2
    return cw, ch, max(0, min(x, w - cw)), max(0, min(y, h - ch))


def fps_de_stream(vs: dict) -> float:
    """fps do stream: avg_frame_rate (r_frame_rate se o avg for inválido). 0.0 se desconhecido."""
    for k in ("avg_frame_rate", "r_frame_rate"):
        s = str(vs.get(k) or "")
        if "/" in s:
            n, d = s.split("/", 1)
            try:
                if float(n) and float(d):
                    return float(n) / float(d)
            except ValueError:
                pass
    return 0.0


# ---------------------------------------------------------------- tipos / perfis de fonte
def tipo_da_fonte(nome: str) -> str:
    """camera | celular | tela | amostra_cor. Sem prefixo = camera. `*-cor` (ex.: camera-00-cor.mov) = amostra
    de cor para o colorista: nunca ingerida, transcrita nem usada na EDL."""
    p = Path(nome)
    n = (p.stem if p.suffix.lower() in EXT_VIDEO else nome).strip().lower()
    if _RE_AMOSTRA_COR.search(n):
        return TIPO_AMOSTRA_COR
    for t in TIPOS_FONTE:
        if n.startswith(t + "-") or n.startswith(t + "_") or n == t:
            return t
    return "camera"


def fontes_de_edicao(fontes: dict) -> dict:
    """fontes.json['fontes'] sem as amostras de cor."""
    return {k: v for k, v in fontes.items() if (v or {}).get("tipo") != TIPO_AMOSTRA_COR}


def eh_log(perfil: str | None) -> bool:
    p = (perfil or "").lower()
    return p == "vlog" or "log" in p


def perfil_da_fonte(nome: str, info: dict | None = None) -> str:
    """Perfil gravado no fontes.json; sem ele (ingest antigo): camera -> CAMERA_PERFIL, resto -> sdr."""
    if info and info.get("perfil"):
        return str(info["perfil"])
    tipo = (info or {}).get("tipo") or tipo_da_fonte(nome)
    return CAMERA_PERFIL if tipo in ("camera", TIPO_AMOSTRA_COR) else "sdr"


def perfis_das_fontes(vd: Path) -> dict[str, str]:
    fontes = ler_json(Path(vd) / "edicao" / "fontes.json", padrao={"fontes": {}}).get("fontes", {})
    return {k: perfil_da_fonte(k, v) for k, v in fontes.items()}


# ---------------------------------------------------------------- LUT de visualização (log -> Rec.709)
_avisos_emitidos: set[str] = set()


def avisar_uma_vez(msg: str) -> None:
    if msg not in _avisos_emitidos:
        _avisos_emitidos.add(msg)
        print(f"[AVISO] {msg}", flush=True)


def lut_entrada_camera() -> Path | None:
    return LUT_ENTRADA_CAMERA if LUT_ENTRADA_CAMERA.is_file() else None


def esc_filtro(caminho) -> str:
    """Caminho dentro de uma opção de filtro ffmpeg (aspas simples; a pasta do projeto tem espaço)."""
    s = str(caminho).replace("\\", "/").replace("'", r"'\''")
    return f"'{s}'"


def filtro_lut_camera(enable: str | None = None) -> str:
    """YUV bt709 (tv) -> RGB 16-bit -> lut3d tetraédrica com a entrada-camera.cube.
    `enable` = expressão de timeline (a LUT só age nesses tempos). '' + aviso se a LUT não existir."""
    lut = lut_entrada_camera()
    if lut is None:
        avisar_uma_vez(f"sem LUT de entrada V-Log — imagem vai parecer lavada (falta {rel(ROOT, LUT_ENTRADA_CAMERA)})")
        return ""
    f = (f"scale=in_color_matrix=bt709:in_range=tv,format=gbrp16le,"
         f"lut3d=file={esc_filtro(lut)}:interp=tetrahedral")
    if enable:
        f += f":enable='{enable}'"
    return f


def intervalos_log(vd: Path, edl: dict) -> list[tuple[float, float]]:
    """Trechos da timeline de saída (s) cujos segmentos vêm de fontes em log (câmera V-Log). Tela nunca."""
    perfis = perfis_das_fontes(vd)
    iv: list[list[float]] = []
    for s in edl.get("segmentos", []):
        f = s.get("fonte", "")
        if tipo_da_fonte(f) == "tela" or not eh_log(perfis.get(f) or perfil_da_fonte(f)):
            continue
        a, b = float(s["saida_inicio"]), float(s["saida_fim"])
        if b <= a:
            continue
        if iv and abs(a - iv[-1][1]) < 1e-3:
            iv[-1][1] = b
        else:
            iv.append([a, b])
    return [(a, b) for a, b in iv]


def expr_intervalos(iv: list[tuple[float, float]]) -> str:
    """between(t,..) com meia-frame de folga: o frame k (t = k/FPS) cai no trecho [a, b)."""
    h = 0.5 / FPS
    return "+".join(f"between(t,{max(0.0, a - h):.4f},{b - h:.4f})" for a, b in iv)


def filtro_vista_log(vd: Path, edl: dict) -> str:
    """Filtro (sobre a timeline do corte) que aplica a LUT de visualização só nos trechos de câmera em log.
    '' se não houver log ou se a LUT não existir (com aviso)."""
    iv = intervalos_log(vd, edl)
    return filtro_lut_camera(expr_intervalos(iv)) if iv else ""


# ---------------------------------------------------------------- brutos: principal + cenas extras
EXT_IMAGEM = {".png", ".jpg", ".jpeg", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp"}
TIPOS_EXTRA = ("tela", "print", "imagem", "video", "animacao", "camera")
_RE_ID_EXTRA = re.compile(r"^(e\d{2,3})(?=$|[-_ .])", re.I)


def stem_limpo(p: Path) -> str:
    s = Path(p).stem.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9_.-]", "", s)
    return s or "fonte"


def normalizar_id_extra(eid: str) -> str:
    eid = str(eid).strip()
    return eid.upper() if re.fullmatch(r"e\d{2,3}", eid, re.I) else eid.lower()


def id_do_extra(stem: str) -> str:
    """'e01-chatgpt' -> 'E01'; legado 'tela-01' -> 'tela-01'."""
    m = _RE_ID_EXTRA.match(stem)
    return m.group(1).upper() if m else stem.lower()


def tipo_extra_por_nome(stem: str, eh_imagem: bool) -> str:
    toks = set(re.split(r"[-_. ]+", stem.lower()))
    for t in ("camera", "tela", "print", "imagem", "video", "animacao"):
        if t in toks:
            return t
    if toks & {"screenshot", "captura"}:
        return "print"
    return "imagem" if eh_imagem else "video"


def _arquivos(d: Path, exts: set) -> list[Path]:
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if p.is_file() and p.suffix.lower() in exts and not p.name.startswith("."))


def listar_brutos(vd: Path) -> tuple[list[Path], list[Path]]:
    """-> (principal, extras). brutos/principal/* e brutos/extras/*; legado (arquivos soltos em brutos/):
    camera-*/celular-*/sem prefixo = principal; tela-*, E01-* e imagens = extras."""
    b = Path(vd) / "brutos"
    principal = _arquivos(b / "principal", EXT_VIDEO)
    extras = _arquivos(b / "extras", EXT_VIDEO | EXT_IMAGEM)
    for p in _arquivos(b, EXT_VIDEO | EXT_IMAGEM):
        if p.suffix.lower() in EXT_IMAGEM or tipo_da_fonte(p.name) == "tela" or _RE_ID_EXTRA.match(p.stem):
            extras.append(p)
        else:
            principal.append(p)
    return principal, extras


# ---------------------------------------------------------------- animações registradas no Remotion
REGISTRY_TS = ROOT / "remotion" / "src" / "animacoes" / "registry.ts"


def componentes_registrados() -> set[str]:
    """Chaves do objeto ANIMACOES em remotion/src/animacoes/registry.ts ("<slug>/E02", "E02", "Nome")."""
    try:
        s = REGISTRY_TS.read_text(encoding="utf-8")
    except OSError:
        return set()
    m = re.search(r"ANIMACOES[^=]*=\s*\{(.*?)\n\s*\};", s, re.S)
    corpo = re.sub(r"//[^\n]*|/\*.*?\*/", "", m.group(1) if m else "", flags=re.S)
    chaves = set(re.findall(r"""["']([^"']+)["']\s*:""", corpo))
    chaves |= set(re.findall(r"^\s*([A-Za-z_$][\w$]*)\s*[,:]", corpo, re.M))
    return chaves


def resolver_componente(slug: str, eid: str, registrados: set[str] | None = None) -> str | None:
    reg = componentes_registrados() if registrados is None else registrados
    for k in (f"{slug}/{eid}", eid):
        if k in reg:
            return k
    return None


# ---------------------------------------------------------------- tempo
def fmt_t(t: float | None) -> str:
    if t is None:
        return "--:--.--"
    t = max(0.0, float(t))
    m = int(t // 60)
    return f"{m:02d}:{t - 60 * m:05.2f}"


def q(t: float) -> float:
    """Quantiza para a grade de frames (FPS do projeto — env FPS_PROJETO, padrão 25)."""
    return round(round(t * FPS) / FPS, 6)


# ---------------------------------------------------------------- texto
CONTRACOES = {
    "pra": ["para"], "pras": ["para", "as"], "pro": ["para", "o"], "pros": ["para", "os"],
    "pr'": ["para"], "ta": ["esta"], "tah": ["esta"], "to": ["estou"], "tou": ["estou"],
    "ce": ["voce"], "cês": ["voces"], "ces": ["voces"], "vc": ["voce"], "vcs": ["voces"],
    "tava": ["estava"], "tavam": ["estavam"], "tamo": ["estamos"], "tamos": ["estamos"],
    "num": ["nao"], "neh": ["ne"], "q": ["que"], "tb": ["tambem"], "tbm": ["tambem"],
}
# muletas (forma normalizada, sem acento, letras repetidas colapsadas)
MULETAS = {"e", "eh", "a", "ah", "ahn", "an", "hum", "hm", "um", "uh", "ha", "han",
           "tipo", "ne", "entao", "assim", "bom", "enfim", "sabe", "ai", "hein", "ue"}
# separadores falados entre takes
SEPARADORES = [["vou", "de", "novo"], ["de", "novo", "de", "novo"], ["de", "novo"],
               ["corta"], ["repete"], ["repetindo"]]

_RE_PONT = re.compile(r"[^\w%\s-]", re.UNICODE)
_RE_NUM = re.compile(r"^(\d+(?:[.,]\d+)?)(%|º|ª|o|a)?$")


def _num_por_extenso(tok: str) -> list[str] | None:
    from num2words import num2words
    m = _RE_NUM.match(tok)
    if not m:
        return None
    num, suf = m.group(1), m.group(2)
    try:
        if "," in num or ("." in num and len(num.split(".")[-1]) != 3):
            val = float(num.replace(",", "."))
            txt = num2words(val, lang="pt_BR")
        else:
            val = int(num.replace(".", ""))
            if suf in ("º", "ª", "o", "a"):
                txt = num2words(val, lang="pt_BR", to="ordinal")
                if suf in ("ª", "a"):
                    txt = " ".join(w[:-1] + "a" if w.endswith("o") else w for w in txt.split())
            else:
                txt = num2words(val, lang="pt_BR")
    except Exception:
        return None
    toks = unidecode(txt.lower()).replace("-", " ").split()
    if suf == "%":
        toks += ["por", "cento"]
    return toks


def norm_palavra(texto: str) -> list[str]:
    """Uma palavra (do roteiro ou da transcrição) -> lista de tokens de *matching*.

    minúsculas, sem acento (unidecode só para comparar), sem pontuação,
    números por extenso (num2words pt_BR), contrações expandidas.
    """
    t = texto.strip().lower()
    t = t.replace("’", "'").replace("`", "'")
    t = _RE_PONT.sub("", t).strip("-").strip()
    if not t:
        return []
    out: list[str] = []
    for parte in t.split():
        n = _num_por_extenso(parte)
        if n is not None:
            out += n
            continue
        parte = unidecode(parte).replace("'", "")
        parte = parte.replace("-", "")          # e-mail -> email, fazê-lo -> fazelo
        if not parte:
            continue
        if parte in CONTRACOES:
            out += CONTRACOES[parte]
        else:
            out.append(parte)
    return out


def colapsar(tok: str) -> str:
    return re.sub(r"(.)\1+", r"\1", tok)


def eh_muleta(tok: str) -> bool:
    return tok in MULETAS or colapsar(tok) in MULETAS or bool(re.fullmatch(r"(e+h*|a+h*n*|h+m+|hu+m+|u+m+)", tok))


def palavras_da_fala(fala: str) -> list[str]:
    """Palavras 'visuais' da fala do roteiro (com a grafia/pontuação do roteiro)."""
    fala = re.sub(r"\[pausa( longa)?\]", " ", fala, flags=re.I)
    fala = fala.replace("**", "")
    return [w for w in fala.split() if _RE_PONT.sub("", w).strip("-")]


def destaques_por_posicao(linha: dict) -> list[bool]:
    """Marca quais palavras de `fala` estavam entre ** ** no fala_original."""
    palavras = palavras_da_fala(linha.get("fala", ""))
    orig = linha.get("fala_original") or ""
    marcas: list[bool] = []
    if orig:
        o = re.sub(r"\[pausa( longa)?\]", " ", orig, flags=re.I)
        dentro = False
        for w in o.split():
            n_ast = w.count("**")
            limpo = w.replace("**", "")
            comeca = w.startswith("**")
            if not _RE_PONT.sub("", limpo).strip("-"):
                if n_ast % 2:
                    dentro = not dentro
                continue
            ativo = dentro or comeca
            marcas.append(ativo)
            if n_ast % 2:
                dentro = not dentro
    if len(marcas) != len(palavras):
        alvo = set()
        for d in linha.get("destaques") or []:
            for w in d.split():
                alvo.update(norm_palavra(w))
        marcas = [bool(set(norm_palavra(w)) & alvo) for w in palavras]
    return marcas


# ---------------------------------------------------------------- áudio (RMS)
@lru_cache(maxsize=8)
def rms_wav(path: str, hop: float = 0.010, win: float = 0.020):
    """Retorna (tempos, rms_db) do wav mono 16k (hop 10 ms)."""
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    h = int(sr * hop)
    w = int(sr * win)
    n = max(1, 1 + (len(x) - w) // h)
    if len(x) < w:
        x = np.pad(x, (0, w - len(x)))
    idx = np.arange(w)[None, :] + h * np.arange(n)[:, None]
    fr = x[idx]
    rms = np.sqrt((fr ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    t = (np.arange(n) * h + w / 2) / sr
    return t, db


def ponto_mais_silencioso(wav: str, t: float, lo: float, hi: float) -> float:
    """Ponto de menor RMS em [lo, hi] (limites já restritos pelo chamador)."""
    import numpy as np
    if hi <= lo:
        return t
    tt, db = rms_wav(wav)
    m = (tt >= lo) & (tt <= hi)
    if not m.any():
        return t
    cand = np.where(m)[0]
    best = cand[np.argmin(db[cand] + 0.001 * np.abs(tt[cand] - t))]
    return float(tt[best])


def limiar_fala(wav: str) -> float:
    """Limiar (dB) acima do qual um frame de 10 ms conta como fala."""
    import numpy as np
    _, db = rms_wav(wav)
    p10, p99 = np.percentile(db, [10, 99])
    return float(max(p10 + 12.0, p99 - 40.0))


def refinar_palavras(palavras: list[dict], wav: str) -> list[dict]:
    """Aperta início/fim de cada palavra à energia real do áudio (ASR costuma 'esticar' a palavra
    sobre o silêncio anterior/posterior). Só encolhe dentro do próprio intervalo da palavra."""
    import numpy as np
    tt, db = rms_wav(wav)
    ativo = db > limiar_fala(wav)
    out = []
    for w in palavras:
        w2 = dict(w)
        i0, i1 = np.searchsorted(tt, w["inicio"]), np.searchsorted(tt, w["fim"])
        seg = ativo[i0:i1]
        if seg.any():
            a = float(tt[i0 + int(np.argmax(seg))]) - 0.015
            b = float(tt[i0 + len(seg) - 1 - int(np.argmax(seg[::-1]))]) + 0.015
            ini, fim = max(w["inicio"], a), min(w["fim"], b)
            if fim - ini >= 0.05:
                w2["inicio"], w2["fim"] = round(ini, 3), round(fim, 3)
        else:
            # nenhuma energia de fala na palavra nem a ±0,15 s: provável alucinação do ASR no silêncio
            j0, j1 = np.searchsorted(tt, w["inicio"] - 0.15), np.searchsorted(tt, w["fim"] + 0.15)
            if not ativo[j0:j1].any():
                w2["silencio"] = True
        out.append(w2)
    return out


def nivel_ruido(wav: str) -> float:
    """Estimativa do piso de ruído (percentil 10 do RMS em dB)."""
    import numpy as np
    _, db = rms_wav(wav)
    return float(np.percentile(db, 10))


ENERGIA_ACIMA_PISO = 8.0      # dB acima do piso = ainda é som da palavra (consoante suave, cauda da vogal)...
ENERGIA_ABAIXO_PICO = 30.0    # ...e no máx. 30 dB abaixo do pico da palavra (o tom da sala / respiração a −55 dB
                              #    entre palavras fica de fora; o ataque de 's'/'f' a −20…−30 dB do pico, dentro)
ENERGIA_MAX_EXT = 0.25        # s — no máx. isto além da borda do ASR/refino


def _limiar_energia(tt, db, a: float, b: float, piso: float) -> float:
    m = (tt >= a) & (tt <= b)
    pico = float(db[m].max()) if m.any() else piso + ENERGIA_ABAIXO_PICO
    return max(piso + ENERGIA_ACIMA_PISO, pico - ENERGIA_ABAIXO_PICO)


def limites_energia(wav: str, inicio: float, fim: float, lo: float, hi: float) -> tuple[float, float]:
    """Onde a energia da palavra REALMENTE começa/termina: a borda refinada usa o limiar de fala (p10 + 12 dB),
    que deixa de fora o ataque suave ('s', 'f', 'p' soprado) e a cauda. Estende para trás/para frente enquanto o
    RMS (10 ms) está > max(piso + 8 dB, pico da palavra − 30 dB), até ENERGIA_MAX_EXT e dentro de [lo, hi]."""
    import numpy as np
    tt, db = rms_wav(wav)
    lim = _limiar_energia(tt, db, inicio, fim, nivel_ruido(wav))
    i = int(np.searchsorted(tt, inicio)) - 1
    a = inicio
    while i >= 0 and tt[i] >= max(lo, inicio - ENERGIA_MAX_EXT) and db[i] > lim:
        a = float(tt[i]) - 0.005
        i -= 1
    j = int(np.searchsorted(tt, fim))
    b = fim
    while j < len(tt) and tt[j] <= min(hi, fim + ENERGIA_MAX_EXT) and db[j] > lim:
        b = float(tt[j]) + 0.005
        j += 1
    return max(lo, min(a, inicio)), min(hi, max(b, fim))


def folga_silencio(wav: str, t: float, lo: float, hi: float, guarda: float = 0.04, passo: float = 0.01) -> float:
    """Ponto de corte em silêncio DE VERDADE: nenhum quadro de 10 ms com som (> max(piso + 8 dB, pico em ±0,5 s
    − 30 dB)) a menos de `guarda` de t. Independe das bordas do ASR (uma palavra mal delimitada — ex.: a energia
    da próxima começa dentro do intervalo de uma muleta — não engana). Devolve o t' mais perto de t em [lo, hi]
    que cumpre isso; se não houver (fala colada), devolve t."""
    import numpy as np
    if hi < lo:
        return t
    tt, db = rms_wav(wav)
    alto = db > _limiar_energia(tt, db, t - 0.5, t + 0.5, nivel_ruido(wav))

    def livre(x: float) -> bool:
        return not alto[int(np.searchsorted(tt, x - guarda)):int(np.searchsorted(tt, x + guarda))].any()

    if lo <= t <= hi and livre(t):
        return t
    n = int((hi - lo) / passo) + 1
    for x in sorted((lo + k * passo for k in range(n)), key=lambda x: abs(x - t)):
        if livre(x):
            return round(x, 3)
    return t


# ---------------------------------------------------------------- peças da EDL
@dataclass
class Peca:
    seg: int          # n do segmento
    linha: str
    fonte: str
    a: float          # tempo na fonte (quantizado)
    b: float
    saida: float = 0.0  # início na timeline de saída
    escala: float = 1.0           # punch-in da peça (zoom_pecas do segmento)
    origem: str = ZOOM_ORIGEM     # ponto fixo do zoom (rosto)

    @property
    def dur(self) -> float:
        return self.b - self.a


def pecas_do_segmento(seg: dict) -> list[tuple[float, float]]:
    """[in, out] menos cortes_internos -> sub-intervalos quantizados em frames."""
    a0, b0 = float(seg["in"]), float(seg["out"])
    cortes = sorted((max(a0, float(c[0])), min(b0, float(c[1])))
                    for c in (seg.get("cortes_internos") or []))
    partes, cur = [], a0
    for c0, c1 in cortes:
        if c1 <= c0:
            continue
        if c0 > cur:
            partes.append((cur, c0))
        cur = max(cur, c1)
    if b0 > cur:
        partes.append((cur, b0))
    # 2026-09-18 (Carlos): um caco de 0,37 s entre dois cortes não se lê — ele vê um relance dele a olhar
    # para o lado, ouve a IA "entrar e voltar" e o enquadramento abre e fecha num piscar. Peça curta demais
    # é absorvida pelo corte à volta (nunca a primeira nem a última, que carregam o começo/fim da frase).
    if len(partes) > 2:
        partes = [p for k, p in enumerate(partes)
                  if k in (0, len(partes) - 1) or (p[1] - p[0]) >= MIN_PECA_S]
    out = []
    for a, b in partes:
        qa, qb = q(a), q(b)
        if qb - qa >= 2 * FRAME - 1e-6:      # descarta peças < 2 frames
            out.append((qa, qb))
    return out


def pecas_da_edl(edl: dict) -> list[Peca]:
    pecas, t = [], 0.0
    for seg in edl.get("segmentos", []):
        ps = pecas_do_segmento(seg)
        escalas = zoom_das_pecas(seg, len(ps))
        origem = seg.get("zoom_origem") or (seg.get("zoom") or {}).get("origem") or ZOOM_ORIGEM
        for (a, b), e in zip(ps, escalas):
            p = Peca(seg["n"], seg["linha"], seg["fonte"], a, b, round(t, 6), e, origem)
            pecas.append(p)
            t += b - a
    return pecas


def duracao_pecas(pecas: list[Peca]) -> float:
    return round(sum(p.dur for p in pecas), 6)


def fonte_path(vd: Path, edl_ou_fontes: dict, fonte: str) -> Path:
    f = edl_ou_fontes.get("fontes", edl_ou_fontes).get(fonte)
    if isinstance(f, dict):
        f = f.get("arquivo")
    if not f:
        sys.exit(f"[ERRO] fonte '{fonte}' não encontrada (rode ingest.py)")
    return vd / f


def wav16k_path(vd: Path, fonte: str) -> Path:
    return vd / "edicao" / "audio16k" / f"{fonte}.wav"


def carregar_roteiro(vd: Path) -> dict:
    r = ler_json(vd / "roteiro.json", padrao={})
    if not r:
        sys.exit(f"[ERRO] {vd/'roteiro.json'} não existe — rode parse_roteiro.py (skill roteiro-reels) antes.")
    return r


def linhas_principais(roteiro: dict) -> list[dict]:
    return [l for l in roteiro.get("linhas", []) if not l.get("alternativa_de")]


def ordem_fontes(fontes: dict) -> list[str]:
    return sorted(fontes.keys())


def log(msg: str) -> None:
    print(msg, flush=True)


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def isnan(x) -> bool:
    return isinstance(x, float) and math.isnan(x)
