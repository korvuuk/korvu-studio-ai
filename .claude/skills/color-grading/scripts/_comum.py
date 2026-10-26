"""Utilidades partilhadas pelos scripts de cor (caminhos, ffmpeg, LUTs, medições).

Nunca imprime segredos: o .env é carregado só para obter FFMPEG_BIN/FFPROBE_BIN.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parent


def _raiz_projeto() -> Path:
    for d in [SCRIPTS, *SCRIPTS.parents]:
        if (d / "CLAUDE.md").exists() and (d / "pyproject.toml").exists():
            return d
    return Path.cwd()


PROJETO = _raiz_projeto()

if not os.environ.get("CONTENT_AI_NO_DOTENV"):
    try:
        from dotenv import load_dotenv

        if (PROJETO / ".env").exists():
            load_dotenv(PROJETO / ".env", override=False)
    except ImportError:  # pragma: no cover
        pass

# CONTENT_AI_ROOT permite correr testes sem tocar em 00-marca/ real.
ROOT = Path(os.environ.get("CONTENT_AI_ROOT") or PROJETO).resolve()


def _bin(env: str, padrao: str, nome: str) -> str:
    v = os.environ.get(env) or padrao
    if Path(v).exists():
        return v
    return shutil.which(nome) or v


FFMPEG = _bin("FFMPEG_BIN", "/Users/teste/bin/ffmpeg", "ffmpeg")
FFPROBE = _bin("FFPROBE_BIN", "/opt/homebrew/bin/ffprobe", "ffprobe")

LUTS_DIR = ROOT / "00-marca" / "cor" / "luts"
ANALISES_DIR = ROOT / "00-marca" / "cor" / "analises"
ENTRADA_CAMERA_CUBE = LUTS_DIR / "entrada-camera.cube"
PANASONIC_DIR = LUTS_DIR / "panasonic"  # LUT oficial V-Log→V-709 (o Carlos descarrega do site da Panasonic)

EXT_IMG = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp", ".heic", ".heif"}
EXT_VIDEO = {".mp4", ".mov", ".m4v", ".mkv", ".mxf"}

LUMA709 = np.array([0.2126, 0.7152, 0.0722])


def resolver(p: str | Path) -> Path:
    """Absoluto → ele próprio; relativo → cwd se existir, senão relativo à raiz do projeto."""
    p = Path(p).expanduser()
    if p.is_absolute():
        return p
    if (Path.cwd() / p).exists():
        return (Path.cwd() / p).resolve()
    return (ROOT / p).resolve()


def rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


# ───────────────────────── ffmpeg ─────────────────────────

def run(cmd: list[str], entrada: bytes | None = None, capturar: bool = False) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, input=entrada, stdout=subprocess.PIPE if capturar else subprocess.DEVNULL,
                       stderr=subprocess.PIPE)
    if r.returncode != 0:
        cauda = "\n".join(r.stderr.decode(errors="replace").strip().splitlines()[-25:])
        raise RuntimeError(f"Falhou: {Path(cmd[0]).name} {' '.join(cmd[1:6])} …\n{cauda}")
    return r


def probe(path: Path) -> dict:
    r = run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capturar=True)
    return json.loads(r.stdout)


def stream_video(info: dict) -> dict:
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            return s
    raise RuntimeError("Arquivo sem stream de vídeo")


def fps_de(s: dict) -> float:
    num, den = (s.get("avg_frame_rate") or s.get("r_frame_rate") or "30/1").split("/")
    return float(num) / float(den or 1) if float(num) else 30.0


def duracao_de(info: dict) -> float:
    d = info.get("format", {}).get("duration") or stream_video(info).get("duration") or 0
    return float(d)


def esc_filtro(caminho: Path | str) -> str:
    """Caminho seguro dentro de uma opção de filtro ffmpeg (aspas simples)."""
    s = str(caminho).replace("\\", "/").replace("'", r"'\''")
    return f"'{s}'"


def rotacao_de(s: dict) -> int:
    """Rotação de exibição (graus) do stream: display matrix (side data) ou tag antiga `rotate`."""
    for sd in s.get("side_data_list") or []:
        if "rotation" in sd:
            try:
                return int(round(float(sd["rotation"])))
            except (TypeError, ValueError):
                pass
    try:
        return int(float((s.get("tags") or {}).get("rotate", 0)))
    except (TypeError, ValueError):
        return 0


def dims_exibidas(s: dict) -> tuple[int, int]:
    """(largura, altura) depois da auto-rotação do ffmpeg (câmera na vertical grava 3840×2160 + rotação 90°)."""
    w, h = int(s["width"]), int(s["height"])
    return (h, w) if abs(rotacao_de(s)) % 180 == 90 else (w, h)


def ler_frame(path: Path, t: float | None, largura: int, filtro_pre: str = "") -> np.ndarray:
    """Lê 1 frame (vídeo em t, ou imagem) como float32 RGB 0–1, redimensionado para `largura`.

    Respeita a rotação (o ffmpeg auto-roda antes do -vf). Com `filtro_pre` (tone-map HDR ou LUT de
    entrada V-Log), reduz primeiro no domínio YUV original (10-bit preservado) e só depois aplica o
    filtro — um frame 4K da câmera não passa pelo lut3d em resolução total."""
    info = probe(path)
    s = stream_video(info)
    w, h = dims_exibidas(s)
    alt = int(round(largura * h / w / 2) * 2)
    vf = ",".join(x for x in [f"scale={largura}:{alt}:flags=bicubic" if filtro_pre else "", filtro_pre,
                               f"scale={largura}:{alt}:in_color_matrix=bt709:out_range=pc:flags=bicubic",
                               "format=rgb24"] if x)
    cmd = [FFMPEG, "-v", "error"]
    if t is not None:
        cmd += ["-ss", f"{t:.3f}"]
    cmd += ["-i", str(path), "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-"]
    r = run(cmd, capturar=True)
    a = np.frombuffer(r.stdout, np.uint8)
    if a.size != largura * alt * 3:
        raise RuntimeError(f"Frame inesperado de {path.name} em t={t}")
    return a.reshape(alt, largura, 3).astype(np.float32) / 255.0


def ler_imagem(path: Path, max_lado: int = 720) -> np.ndarray:
    """Imagem → float32 RGB 0–1. HEIC é convertido com `sips` (macOS)."""
    from PIL import Image

    src = path
    tmp = None
    if path.suffix.lower() in {".heic", ".heif"}:
        tmp = Path(tempfile.mkdtemp()) / (path.stem + ".jpg")
        run(["sips", "-s", "format", "jpeg", str(path), "--out", str(tmp)])
        src = tmp
    im = Image.open(src).convert("RGB")
    im.thumbnail((max_lado, max_lado))
    a = np.asarray(im).astype(np.float32) / 255.0
    if tmp:
        shutil.rmtree(tmp.parent, ignore_errors=True)
    return a


def salvar_png(a: np.ndarray, path: Path) -> None:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path)


# ───────────────────────── medições ─────────────────────────

def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def ycbcr601(px: np.ndarray):
    y = px @ np.array([0.299, 0.587, 0.114])
    cb = (px[..., 2] - y) * 0.564 + 0.5
    cr = (px[..., 0] - y) * 0.713 + 0.5
    return y, cb, cr


def rgb_de_ycbcr601(y, cb, cr):
    """Inversa exata de ycbcr601 (a luminância Y faz ida-e-volta sem erro)."""
    r = y + (cr - 0.5) / 0.713
    b = y + (cb - 0.5) / 0.564
    g = (y - 0.299 * r - 0.114 * b) / 0.587
    return np.stack([r, g, b], -1)


def peso_pele(px: np.ndarray) -> np.ndarray:
    """Peso 0–1 de 'tom de pele' (faixa YCrCb clássica Cr 133–173, Cb 77–127, bordas suaves)."""
    y, cb, cr = ycbcr601(px)
    f = 0.025
    w = (_smooth(cr, 133 / 255 - f, 133 / 255 + f) * (1 - _smooth(cr, 173 / 255 - f, 173 / 255 + f))
         * _smooth(cb, 77 / 255 - f, 77 / 255 + f) * (1 - _smooth(cb, 127 / 255 - f, 127 / 255 + f))
         * _smooth(y, 0.10, 0.20) * (1 - _smooth(y, 0.92, 0.99)))
    return w


def medir_primaria(frames: list[np.ndarray]) -> dict:
    """Luminância média + balanço gray-world nos meios-tons (sem pele e sem recortados)."""
    px = np.concatenate([f.reshape(-1, 3) for f in frames]).astype(np.float64)
    Y = px @ LUMA709
    mx, mn = px.max(1), px.min(1)
    recortado = (mx > 0.97) | (mx < 0.03)
    pele = peso_pele(px) > 0.5
    meio = (Y > 0.12) & (Y < 0.88) & ~recortado & ~pele
    # gray-world iterativo: estima a dominante, remove-a e só então escolhe os quase-cinzentos
    # (paredes, roupa neutra). Com saturação absoluta, uma dominante de ±7% já "tira" os cinzentos
    # verdadeiros da seleção e a pele fora da máscara (luz fria) entraria como neutra.
    sel = meio
    est = px[meio].mean(0) if meio.any() else px.mean(0)
    for _ in range(3):
        norm = px / np.maximum(est / est.mean(), 1e-4)
        nmx, nmn = norm.max(1), norm.min(1)
        sat_n = (nmx - nmn) / (nmx + 1e-6)
        for limiar in (0.10, 0.20):
            neutro = meio & (sat_n < limiar)
            if neutro.mean() > 0.02:
                sel = neutro
                break
        est = px[sel].mean(0)
    ok = ~recortado
    luma = float(Y[ok].mean()) if ok.any() else float(Y.mean())
    rgb = px[sel].mean(0) if sel.any() else px.mean(0)
    return {
        "luma": round(luma, 5),
        "rgb_neutro": [round(float(v), 5) for v in rgb],
        "frac_meios_tons": round(float(sel.mean()), 4),
        "frac_recortado": round(float(recortado.mean()), 4),
        "frac_pele": round(float(pele.mean()), 4),
        "confiavel": bool(sel.mean() > 0.02),
    }


def estatisticas(frames: list[np.ndarray]) -> dict:
    """Números para comparar com a referência: brilho, contraste, saturação, pretos/brancos."""
    px = np.concatenate([f.reshape(-1, 3) for f in frames]).astype(np.float64)
    Y = px @ LUMA709
    mx, mn = px.max(1), px.min(1)
    sat = (mx - mn) / (mx + 1e-6)
    return {
        "luma_media": round(float(Y.mean()), 4),
        "contraste_std": round(float(Y.std()), 4),
        "p02": round(float(np.quantile(Y, 0.02)), 4),
        "p98": round(float(np.quantile(Y, 0.98)), 4),
        "saturacao_media": round(float(sat.mean()), 4),
        "rgb_medio": [round(float(v), 4) for v in px.mean(0)],
        "pretos_esmagados_pct": round(float((mx < 0.02).mean() * 100), 2),
        "brancos_estourados_pct": round(float((mn > 0.985).mean() * 100), 2),
    }


# ───────────────────────── LUT 3D ─────────────────────────

def lattice(n: int = 33) -> np.ndarray:
    """Grade identidade (n,n,n,3); eixo0 = R, eixo1 = G, eixo2 = B."""
    lin = np.linspace(0.0, 1.0, n)
    r, g, b = np.meshgrid(lin, lin, lin, indexing="ij")
    return np.stack([r, g, b], -1)


def escrever_cube(path: Path, lut: np.ndarray, titulo: str, comentarios: list[str] | None = None) -> None:
    """Escreve .cube (Resolve/ffmpeg): R varia mais rápido."""
    n = lut.shape[0]
    linhas = [f"# {c}" for c in (comentarios or [])]
    linhas += [f'TITLE "{titulo}"', f"LUT_3D_SIZE {n}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    dados = np.clip(lut, 0, 1).transpose(2, 1, 0, 3).reshape(-1, 3)
    linhas += [f"{r:.6f} {g:.6f} {b:.6f}" for r, g, b in dados]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(linhas) + "\n")


def ler_cube(path: Path) -> np.ndarray:
    n = None
    vals = []
    for ln in Path(path).read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if ln.startswith("LUT_3D_SIZE"):
            n = int(ln.split()[1])
            continue
        if ln[0].isalpha():
            continue
        vals.append([float(v) for v in ln.split()[:3]])
    a = np.array(vals, dtype=np.float64)
    if n is None or a.shape[0] != n ** 3:
        raise ValueError(f"{path}: .cube inválido")
    return a.reshape(n, n, n, 3).transpose(2, 1, 0, 3)  # → [r,g,b]


def aplicar_lut_np(img: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Interpolação trilinear (para estatísticas/validação; o ffmpeg usa tetraédrica)."""
    n = lut.shape[0]
    p = np.clip(img.reshape(-1, 3), 0, 1) * (n - 1)
    i0 = np.minimum(np.floor(p).astype(int), n - 2)
    f = p - i0
    out = np.zeros_like(p)
    for dr in (0, 1):
        wr = f[:, 0] if dr else 1 - f[:, 0]
        for dg in (0, 1):
            wg = f[:, 1] if dg else 1 - f[:, 1]
            for db in (0, 1):
                wb = f[:, 2] if db else 1 - f[:, 2]
                out += (wr * wg * wb)[:, None] * lut[i0[:, 0] + dr, i0[:, 1] + dg, i0[:, 2] + db]
    return out.reshape(img.shape).astype(np.float32)


def ler_json(p: Path) -> dict:
    return json.loads(Path(p).read_text())


def escrever_json(p: Path, d: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")


def fonte_png(tamanho: int = 22):
    from PIL import ImageFont

    for f in ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf"]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, tamanho)
            except OSError:
                pass
    return ImageFont.load_default(size=tamanho)
