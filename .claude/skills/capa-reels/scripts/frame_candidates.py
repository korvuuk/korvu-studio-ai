#!/usr/bin/env python3
"""Candidatos de capa: amostra frames do hook e do payoff do corte final, pontua e
gera folha de contato.

Saídas (videos/<slug>/capa/candidatos/): cand-NN.jpg (NN = ranking), contato.jpg, scores.json

Se ainda não existe edicao/cor/corte-cor.mp4 e o fallback é o edicao/corte.mp4 (10-bit, câmera em V-Log), os
frames dos trechos de câmera recebem a LUT de visualização 00-marca/cor/luts/entrada-camera.cube (lut3d
tetraédrica) para não parecerem lavados; sem a LUT, avisa. Refaça os candidatos depois do /cor.

Uso:
  uv run python .claude/skills/capa-reels/scripts/frame_candidates.py videos/<slug> [--n 12] [--video edicao/cor/corte-cor.mp4]

Detector de rosto (o primeiro disponível):
  1. Haar do OpenCV (frontalface + eye) — procura os XML em $HAAR_DIR, na pasta
     assets/haar/ desta skill e em cv2.data.haarcascades (o OpenCV 5.x não traz mais).
  2. YuNet (cv2.FaceDetectorYN) se existir assets/face_detection_yunet_2023mar.onnx ou $YUNET_MODEL.
  3. Heurística de pele (YCrCb) + olhos como manchas escuras — menos confiável.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[4]
SKILL = Path(__file__).resolve().parents[1]
SCRIPTS_CORTE = RAIZ / ".claude" / "skills" / "corte-por-roteiro" / "scripts"


def _carregar_env() -> None:
    env = RAIZ / ".env"
    if not env.exists():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(env, override=False)


_carregar_env()
FFMPEG = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE_BIN", "ffprobe")

RECORTE_3x4 = (240 / 1920, 1680 / 1920)  # faixa vertical visível na grade do perfil
# Pedido do Carlos (2026-09-16): a capa tem que pegar um quadro PARADO — boca fechada, sem gesto de mão
# no meio do movimento. Por isso "boca" e "parado" entram na nota com peso alto.
PESOS = {"nitidez": 0.22, "rosto": 0.16, "centragem": 0.13, "olhos": 0.15, "exposicao": 0.04,
         "boca": 0.18, "parado": 0.12}
DELTA_MOV = 0.12   # segundos antes/depois usados para medir movimento
LARANJA = (255, 122, 53)

Caixa = tuple[int, int, int, int]  # x, y, w, h


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# detectores
# ---------------------------------------------------------------------------
def olhos_por_manchas(cinza_rosto: np.ndarray) -> int:
    """Conta olhos abertos como manchas escuras arredondadas na faixa dos olhos (0–2)."""
    h, w = cinza_rosto.shape[:2]
    if h < 20 or w < 20:
        return 0
    faixa = cinza_rosto[int(h * 0.22): int(h * 0.55), :]
    area_rosto = h * w
    achados = 0
    for metade in (faixa[:, : w // 2], faixa[:, w // 2:]):
        if metade.size == 0:
            continue
        limiar = min(np.percentile(metade, 12), float(metade.mean()) - 35)
        mascara = (metade < limiar).astype(np.uint8)
        n, _, stats, _ = cv2.connectedComponentsWithStats(mascara, 8)
        for i in range(1, n):
            x, y, bw, bh, area = stats[i]
            if 0.0015 * area_rosto <= area <= 0.05 * area_rosto and bw / max(bh, 1) <= 4.0 and bh >= 3:
                achados += 1
                break
    return achados


@dataclass
class Detector:
    nome: str

    def rostos(self, bgr: np.ndarray, cinza: np.ndarray) -> list[Caixa]:
        raise NotImplementedError

    def olhos(self, cinza_rosto: np.ndarray) -> int:
        return olhos_por_manchas(cinza_rosto)


class DetectorHaar(Detector):
    def __init__(self, face: "cv2.CascadeClassifier", eye: "cv2.CascadeClassifier | None") -> None:
        super().__init__("haar")
        self.face, self.eye = face, eye

    def rostos(self, bgr, cinza):
        esc = 0.5
        peq = cv2.resize(cinza, None, fx=esc, fy=esc)
        achados = self.face.detectMultiScale(peq, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        return [tuple(int(v / esc) for v in r) for r in achados]

    def olhos(self, cinza_rosto):
        if self.eye is None:
            return olhos_por_manchas(cinza_rosto)
        h = cinza_rosto.shape[0]
        topo = cinza_rosto[: int(h * 0.6), :]
        achados = self.eye.detectMultiScale(topo, scaleFactor=1.1, minNeighbors=6, minSize=(12, 12))
        return min(2, len(achados))


class DetectorYuNet(Detector):
    def __init__(self, modelo: str) -> None:
        super().__init__("yunet")
        self.det = cv2.FaceDetectorYN.create(modelo, "", (320, 320), 0.75, 0.3, 5000)

    def rostos(self, bgr, cinza):
        h, w = bgr.shape[:2]
        self.det.setInputSize((w, h))
        _, faces = self.det.detect(bgr)
        if faces is None:
            return []
        return [tuple(int(v) for v in f[:4]) for f in faces]


class DetectorPele(Detector):
    def __init__(self) -> None:
        super().__init__("pele-heuristica")

    def rostos(self, bgr, cinza):
        h, w = bgr.shape[:2]
        ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
        mascara = cv2.inRange(ycrcb, (40, 135, 85), (255, 180, 135))
        mascara[int(h * 0.75):] = 0
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        n, _, stats, _ = cv2.connectedComponentsWithStats(mascara, 8)
        melhores: list[Caixa] = []
        for i in range(1, n):
            x, y, bw, bh, area = stats[i]
            if area < 0.01 * w * h:
                continue
            bh = min(bh, int(bw * 1.35))  # corta pescoço
            if 0.8 <= bh / max(bw, 1) <= 2.2:
                melhores.append((int(x), int(y), int(bw), int(bh)))
        melhores.sort(key=lambda c: c[2] * c[3], reverse=True)
        return melhores[:1]


def criar_detector() -> Detector:
    pastas = [os.environ.get("HAAR_DIR"), str(SKILL / "assets" / "haar")]
    dados = getattr(getattr(cv2, "data", None), "haarcascades", None)
    if dados:
        pastas.append(dados)
    if hasattr(cv2, "CascadeClassifier"):
        for p in pastas:
            if p and (Path(p) / "haarcascade_frontalface_default.xml").exists():
                face = cv2.CascadeClassifier(str(Path(p) / "haarcascade_frontalface_default.xml"))
                olho_p = Path(p) / "haarcascade_eye.xml"
                return DetectorHaar(face, cv2.CascadeClassifier(str(olho_p)) if olho_p.exists() else None)
    modelo = os.environ.get("YUNET_MODEL") or str(SKILL / "assets" / "face_detection_yunet_2023mar.onnx")
    if hasattr(cv2, "FaceDetectorYN") and Path(modelo).exists():
        return DetectorYuNet(modelo)
    return DetectorPele()


# ---------------------------------------------------------------------------
# pontuação
# ---------------------------------------------------------------------------
def nota_nitidez(cinza: np.ndarray) -> tuple[float, float]:
    peq = cv2.resize(cinza, (540, int(540 * cinza.shape[0] / cinza.shape[1])))
    v = float(cv2.Laplacian(peq, cv2.CV_64F).var())
    return v, clamp((math.log10(max(v, 1.0)) - 1.0) / 2.0)


def nota_tamanho(h_rosto: int, altura: int) -> float:
    r = h_rosto / altura
    if r < 0.05:
        return 0.0
    if r < 0.18:
        return (r - 0.05) / 0.13
    if r <= 0.40:
        return 1.0
    return max(0.3, 1 - (r - 0.40) / 0.4)


def nota_centragem(c: Caixa, largura: int, altura: int) -> float:
    x, y, w, h = c
    cx, cy = (x + w / 2) / largura, (y + h / 2) / altura
    sx = clamp(1 - abs(cx - 0.5) * 2.5)
    sy = 1.0 if 0.30 <= cy <= 0.50 else clamp(1 - min(abs(cy - 0.30), abs(cy - 0.50)) * 4)
    nota = 0.6 * sx + 0.4 * sy
    dentro = y >= RECORTE_3x4[0] * altura and (y + h) <= RECORTE_3x4[1] * altura
    return nota if dentro else nota * 0.6


def nota_exposicao(cinza_rosto: np.ndarray) -> float:
    m = float(cinza_rosto.mean())
    return 1.0 if 90 <= m <= 190 else clamp(1 - min(abs(m - 90), abs(m - 190)) / 80)


def nota_boca(cinza_rosto: np.ndarray) -> tuple[float, float]:
    """(abertura, nota) — boca FECHADA = 1.0.

    Mede a mancha escura na faixa da boca (58–92 % da altura do rosto, 20–80 % da largura): boca fechada é
    uma linha fina e larga; boca aberta no meio de uma palavra é uma mancha alta. `abertura` = altura da
    mancha ÷ altura do rosto.
    """
    h, w = cinza_rosto.shape[:2]
    if h < 40 or w < 40:
        return 0.0, 0.5
    faixa = cinza_rosto[int(h * 0.58): int(h * 0.92), int(w * 0.20): int(w * 0.80)]
    if faixa.size == 0:
        return 0.0, 0.5
    limiar = min(float(np.percentile(faixa, 15)), float(faixa.mean()) - 18)
    mascara = (faixa < limiar).astype(np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, _, stats, _ = cv2.connectedComponentsWithStats(mascara, 8)
    maior = 0
    for i in range(1, n):
        bw, bh, area = int(stats[i][2]), int(stats[i][3]), int(stats[i][4])
        if area < 0.002 * faixa.size or bw < bh:      # sombra vertical (nariz/barba) não é boca
            continue
        maior = max(maior, bh)
    abertura = maior / h
    return round(abertura, 4), round(clamp(1 - (abertura - 0.05) / 0.10), 3)


def nota_parado(cinza: np.ndarray, vizinhos: list[np.ndarray]) -> tuple[float, float]:
    """(movimento, nota) — quadro PARADO = 1.0.

    Compara o quadro com os vizinhos ±DELTA_MOV s: mão em movimento, cabeça virando ou borrão de
    deslocamento aparecem como diferença média alta.
    """
    if not vizinhos:
        return 0.0, 1.0
    peq = cv2.resize(cinza, (270, 480))
    mov = max(float(cv2.absdiff(peq, cv2.resize(v, (270, 480))).mean()) for v in vizinhos)
    return round(mov, 2), round(clamp(1 - (mov - 1.2) / 5.0), 3)


def pontuar(arq: Path, det: Detector, vizinhos: list[np.ndarray] | None = None) -> dict:
    bgr = cv2.imread(str(arq))
    altura, largura = bgr.shape[:2]
    cinza = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    lap, nit = nota_nitidez(cinza)
    mov, n_parado = nota_parado(cinza, vizinhos or [])
    rostos = det.rostos(bgr, cinza)
    notas = {"nitidez": round(nit, 3), "rosto": 0.0, "centragem": 0.0, "olhos": 0.0, "exposicao": 0.0,
             "boca": 0.0, "parado": n_parado}
    rosto = None
    n_olhos = 0
    abertura = 0.0
    if rostos:
        rosto = max(rostos, key=lambda c: c[2] * c[3])
        x, y, w, h = rosto
        recorte = cinza[max(0, y): y + h, max(0, x): x + w]
        n_olhos = det.olhos(recorte)
        abertura, n_boca = nota_boca(recorte)
        notas.update({
            "rosto": round(nota_tamanho(h, altura), 3),
            "centragem": round(nota_centragem(rosto, largura, altura), 3),
            "olhos": round(n_olhos / 2, 3),
            "exposicao": round(nota_exposicao(recorte), 3),
            "boca": n_boca,
        })
        total = sum(PESOS[k] * notas[k] for k in PESOS)
    else:
        total = PESOS["nitidez"] * nit * 0.5  # sem rosto: penaliza
    return {
        "notas": notas,
        "total": round(total, 4),
        "laplaciano": round(lap, 1),
        "olhos_detectados": n_olhos,
        "abertura_boca": abertura,
        "movimento": mov,
        "rosto": dict(zip(("x", "y", "w", "h"), rosto)) if rosto else None,
    }


# ---------------------------------------------------------------------------
# tempos de amostragem
# ---------------------------------------------------------------------------
def ler_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def janelas(video_dir: Path) -> tuple[list[tuple[float, float, str]], list[tuple[float, float, str]]]:
    edl = ler_json(video_dir / "edicao" / "edl.json")
    rot = ler_json(video_dir / "roteiro.json")
    hook_ids: set[str] = set()
    payoff_ids: set[str] = set()
    for l in (rot or {}).get("linhas", []):
        if l.get("alternativa_de"):
            continue
        if l.get("secao") == "hook":
            hook_ids.add(l["id"])
        elif l.get("secao") == "payoff":
            payoff_ids.add(l["id"])
    hook, payoff = [], []
    segs = (edl or {}).get("segmentos", [])
    if segs and not hook_ids:
        hook_ids = {segs[0]["linha"]}
    for s in segs:
        w = (float(s["saida_inicio"]), float(s["saida_fim"]), s.get("linha", ""))
        if s.get("linha") in hook_ids:
            hook.append(w)
        elif s.get("linha") in payoff_ids:
            payoff.append(w)
    return hook, payoff


def distribuir(ws: list[tuple[float, float, str]], n: int, margem: float = 0.15) -> list[tuple[float, str]]:
    ws = [(a + margem, b - margem, l) for a, b, l in ws if b - a > 2 * margem]
    total = sum(b - a for a, b, _ in ws)
    if n <= 0 or total <= 0:
        return []
    passo = total / n
    tempos = []
    for k in range(n):
        alvo = passo * (k + 0.5)
        for a, b, l in ws:
            if alvo <= b - a:
                tempos.append((round(a + alvo, 3), l))
                break
            alvo -= b - a
    return tempos


def secao_de(linha: str, video_dir: Path) -> str | None:
    rot = ler_json(video_dir / "roteiro.json")
    for l in (rot or {}).get("linhas", []):
        if l.get("id") == linha:
            return l.get("secao")
    return None


# ---------------------------------------------------------------------------
# principal
# ---------------------------------------------------------------------------
def duracao(video: Path) -> float:
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def lut_visualizacao(video_dir: Path, video: Path) -> tuple[list[tuple[float, float]], str]:
    """(trechos de câmera em log, filtro da LUT) — só para o corte sem cor (edicao/corte.mp4)."""
    if video.resolve() != (video_dir / "edicao" / "corte.mp4").resolve():
        return [], ""
    edl = ler_json(video_dir / "edicao" / "edl.json")
    if not edl:
        return [], ""
    if str(SCRIPTS_CORTE) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_CORTE))
    import common as C  # noqa: PLC0415
    iv = C.intervalos_log(video_dir, edl)
    if not iv:
        return [], ""
    print("AVISO: candidatos do corte SEM cor (edicao/corte.mp4) — refaça depois do /cor para a capa final.")
    return iv, C.filtro_lut_camera()


def extrair(video: Path, t: float, saida: Path, vf: str = "") -> bool:
    r = subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video),
                        *(["-vf", vf] if vf else []), "-frames:v", "1", "-q:v", "2", str(saida)],
                       capture_output=True, text=True)
    return r.returncode == 0 and saida.exists()


def folha_de_contato(cands: list[dict], pasta: Path, slug: str, pose: str | None = None) -> Path:
    tw, th, rot, margem, colunas = 270, 480, 72, 12, 4
    linhas = math.ceil(len(cands) / colunas)
    topo = 56 if not pose else 86
    W = colunas * tw + (colunas + 1) * margem
    H = topo + linhas * (th + rot + margem) + margem
    folha = Image.new("RGB", (W, H), (17, 17, 17))
    d = ImageDraw.Draw(folha)
    try:
        # fonte do sistema COM acentos: a padrão do PIL desenha caixinhas em "mão", "não", "→"…
        # (visto em 2026-09-18 no cabeçalho da pose, que é justamente onde o texto é em português)
        tipo = next((p for p in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                                 "/System/Library/Fonts/Supplemental/Arial.ttf",
                                 "/System/Library/Fonts/HelveticaNeue.ttc") if Path(p).exists()), None)
        if tipo:
            fonte = ImageFont.truetype(tipo, 17)
            fonte_titulo = ImageFont.truetype(tipo, 22)
        else:
            fonte = ImageFont.load_default(size=17)
            fonte_titulo = ImageFont.load_default(size=22)
    except (TypeError, OSError):
        fonte = fonte_titulo = ImageFont.load_default()
    d.text((margem, 16), f"Candidatos de capa - {slug}  (linhas tracejadas = recorte 3:4 da grade)",
           fill=(242, 242, 242), font=fonte_titulo)
    if pose:
        # O roteiro diz QUAL pose ele fez nos 3 s antes da 1.ª fala. Quem escolhe a capa procura ISTO,
        # em vez de "o quadro mais parado" (pedido do Carlos, 2026-09-18).
        d.text((margem, 46), f"POSE DESTE ROTEIRO → {pose}", fill=LARANJA, font=fonte_titulo)
    for i, c in enumerate(cands):
        col, lin = i % colunas, i // colunas
        x0 = margem + col * (tw + margem)
        y0 = topo + lin * (th + rot + margem)
        img = Image.open(pasta / c["arquivo"]).convert("RGB")
        ex, ey = tw / img.width, th / img.height
        folha.paste(img.resize((tw, th)), (x0, y0))
        for yy in (RECORTE_3x4[0] * th, RECORTE_3x4[1] * th):
            for xx in range(0, tw, 12):
                d.line((x0 + xx, y0 + yy, x0 + min(xx + 6, tw), y0 + yy), fill=(242, 242, 242), width=1)
        if c["rosto"]:
            r = c["rosto"]
            d.rectangle((x0 + r["x"] * ex, y0 + r["y"] * ey, x0 + (r["x"] + r["w"]) * ex, y0 + (r["y"] + r["h"]) * ey),
                        outline=LARANJA, width=2)
        n = c["notas"]
        d.text((x0, y0 + th + 5), f"{c['arquivo'][:-4]}  {c['tempo']:.1f}s  {c.get('linha') or ''}",
               fill=(242, 242, 242), font=fonte)
        d.text((x0, y0 + th + 26), f"total {c['total']:.2f} · nit {n['nitidez']:.2f} · olhos {c['olhos_detectados']}",
               fill=(155, 155, 155), font=fonte)
        d.text((x0, y0 + th + 47), f"boca {n['boca']:.2f} · parado {n['parado']:.2f} (mov {c.get('movimento', 0):.1f})",
               fill=(155, 155, 155), font=fonte)
    saida = pasta / "contato.jpg"
    folha.save(saida, quality=90)
    return saida


def look_ativo() -> Path | None:
    """Maior LUT criativo aprovado (o mesmo critério do aplicar_cor.py)."""
    melhor, nmax = None, -1
    for j in sorted((RAIZ / "00-marca" / "cor" / "luts").glob("korvu-look-*.json")):
        try:
            if not json.loads(j.read_text(encoding="utf-8")).get("aprovada"):
                continue
        except Exception:                                     # noqa: BLE001
            continue
        m = re.search(r"v(\d+)", j.stem)
        n = int(m.group(1)) if m else 0
        if n > nmax and j.with_suffix(".cube").exists():
            melhor, nmax = j.with_suffix(".cube"), n
    return melhor


def _procurar_pose(arq: Path, t0: float, t1: float, segundos: float,
                   fps: int = 4, larg: int = 160) -> tuple[float, float] | None:
    """A janela de `segundos` mais PARADA e em SILÊNCIO entre t0 e t1 — é a pose da capa.

    Ele segura a pose logo depois de a IA ler a instrução, e depois ainda grava vários takes; procurar
    "os segundos antes da 1.ª fala do corte" apanhava um trecho qualquer no meio da gravação.
    Critério: diferença média entre quadros vizinhos (do MESMO arquivo) + nenhum som acima de -45 dBFS.
    """
    if t1 - t0 < segundos + 1:
        return None
    pr = subprocess.run([FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error", "-select_streams", "v:0",
                         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(arq)],
                        capture_output=True, text=True)
    try:
        w0, h0 = (int(x) for x in pr.stdout.strip().split(",")[:2])
        alt = int(round(larg * h0 / w0 / 2)) * 2
    except Exception:
        alt = 284
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(arq),
                        "-vf", f"fps={fps},scale={larg}:{alt},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    a = np.frombuffer(r.stdout, np.uint8)
    nf = len(a) // (larg * alt)
    if nf < segundos * fps + 2:
        return None
    f = a[:nf * larg * alt].reshape(nf, alt, larg).astype(np.float32)
    mov = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    wav = arq.parent.parent / "audio48k" / f"{arq.stem}.wav"
    adb = None
    if wav.exists():
        raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(wav),
                              "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32)
        h = 16000 // fps
        na = len(x) // h
        if na:
            adb = 20 * np.log10(np.sqrt((x[:na * h].reshape(na, h) ** 2).mean(1)) + 1e-12)
    w = max(2, int(segundos * fps))
    melhor = None
    # a folha branca do balanço de branco também é parada e silenciosa: rejeitar quadro quase uniforme
    centro = f[:, int(0.25 * alt):int(0.75 * alt), int(0.15 * larg):int(0.85 * larg)]
    plano = centro.reshape(len(f), -1).std(axis=1)
    for k in range(len(mov) - w):
        if adb is not None and k + w < len(adb) and adb[k:k + w].max() > -45.0:
            continue                                            # tem fala/ruído: não é a pose
        if plano[k:k + w].mean() < 22.0:
            continue                                            # imagem chapada = folha de balanço de branco
        pontos = float(mov[k:k + w].mean())
        if melhor is None or pontos < melhor[0]:
            melhor = (pontos, t0 + k / fps)
    if melhor is None or melhor[0] > 0.5 * float(mov.mean()):
        return None                                             # nada notavelmente parado: não achou a pose
    print(f"[capa] pose encontrada: {melhor[1]:.2f}–{melhor[1] + segundos:.2f}s "
          f"(movimento {melhor[0]:.2f} vs {mov.mean():.2f} de média da gravação)")
    return melhor[1], melhor[1] + segundos


def janela_pausa_capa(video_dir: Path, segundos: float) -> tuple[Path, float, float, str] | None:
    """(intermediário, início, fim, filtro) da PAUSA DA CAPA — os segundos parados logo ANTES da 1.ª fala.

    Pedido do Carlos (2026-09-18): o roteiro manda ele olhar para a câmera e ficar parado 3 s antes de começar.
    Esse trecho fica FORA do corte (o corte começa na 1.ª palavra da L01), mas continua no intermediário
    `edicao/fontes/<fonte>.mp4` — que guarda a gravação inteira. É de lá que sai o frame da capa, em vez de
    varrer o vídeo quadro a quadro.
    """
    edl = ler_json(video_dir / "edicao" / "edl.json")
    segs = (edl or {}).get("segmentos") or []
    if not segs:
        return None
    # Com gravação em VÁRIAS partes a pose está na PRIMEIRA (ele bate o branco, faz a pose e só depois grava
    # as linhas) — mas o take escolhido para a L01 pode estar noutro arquivo. Procurar sempre na 1.ª fonte
    # cronológica (ordem alfabética, como o ingest), não na fonte do 1.º segmento (2026-09-18).
    fontes = sorted({s.get("fonte") for s in segs if s.get("fonte")})
    todas = (ler_json(video_dir / "edicao" / "fontes.json") or {}).get("fontes") or {}
    principais = sorted(k for k, v in todas.items() if v.get("tipo") != "amostra_cor") or fontes
    fonte = principais[0]
    seus = [float(s["in"]) for s in segs if s.get("fonte") == fonte]
    arq = video_dir / "edicao" / "fontes" / f"{fonte}.mp4"
    if not arq.exists():
        return None
    ini_fala = min(seus) if seus else float(todas.get(fonte, {}).get("duracao") or 0.0)
    if ini_fala < 1.5:
        return None
    # 2026-09-18: com o método ChatGPT-monitor a pose NÃO fica colada à 1.ª palavra do corte — a IA lê a
    # instrução da pose, ele segura a pose, e só muitos takes depois vem o take que a EDL escolheu (neste
    # vídeo: pose aos 98 s, take escolhido aos 164 s). Procurar a pose pelo movimento, não pela posição.
    fim = max(0.3, ini_fala - 0.4)
    achada = _procurar_pose(arq, max(0.0, fim - 180.0), fim, segundos)
    if achada:
        ini, fim = achada
    else:
        ini = max(0.0, fim - (segundos + 2.0))
    # o intermediário está em V-Log: conversão de entrada + look ativo, para o frame sair na cor do vídeo
    if str(SCRIPTS_CORTE) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_CORTE))
    import common as C                                        # noqa: PLC0415
    filtros = [C.filtro_lut_camera()]
    # 2026-09-18: a MESMA cadeia do vídeo, incluindo a correção primária por take. Sem ela o frame da capa sai
    # ~0,5 diafragma mais claro que o corte com cor — o Carlos viu a diferença e achou que era outro LUT.
    prim = _curvas_primaria(video_dir)
    if prim:
        filtros.append(prim)
    look = look_ativo()
    if look:
        filtros.append(f"lut3d=file='{look.as_posix()}':interp=tetrahedral")
    return arq, ini, fim, ",".join(f for f in filtros if f)


def _curvas_primaria(video_dir: Path) -> str | None:
    """Reaproveita a curva da primária já calculada pelo /cor (edicao/cor/filtro.txt) — a do 1.º segmento,
    que nesta câmera é praticamente igual em todos (mesma luz)."""
    ftxt = Path(video_dir) / "edicao" / "cor" / "filtro.txt"
    if not ftxt.exists():
        return None
    m = re.search(r"(curves=r='[^']*':g='[^']*':b='[^']*':interp=pchip)", ftxt.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def main() -> None:
    ap = argparse.ArgumentParser(description="Candidatos de capa (frames + notas + folha de contato)")
    ap.add_argument("video_dir", type=Path)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--video", help="relativo à pasta do vídeo (padrão: edicao/cor/corte-cor.mp4 → edicao/corte.mp4)")
    ap.add_argument("--min-intervalo", type=float, default=0.4, help="distância mínima entre candidatos (s)")
    ap.add_argument("--todo-o-video", action="store_true",
                    help="amostra o corte inteiro, não só hook e payoff (útil quando ele gesticula muito nessas linhas)")
    ap.add_argument("--pausa-capa", type=float, default=3.0,
                    help="segundos da pausa parada antes da 1.ª fala, de onde sai o frame da capa (padrão 3)")
    ap.add_argument("--sem-pausa-capa", action="store_true",
                    help="ignora a pausa e varre o vídeo (gravações antigas, sem a pausa)")
    a = ap.parse_args()

    video_dir = a.video_dir.resolve()
    edicao = video_dir / "edicao"
    if a.video:
        video = video_dir / a.video
    else:
        video = next((edicao / c for c in ("cor/corte-cor.mp4", "corte.mp4") if (edicao / c).exists()), None)
    if not video or not video.exists():
        raise SystemExit("Vídeo do corte final não encontrado (edicao/cor/corte-cor.mp4 ou edicao/corte.mp4).")
    slug = video_dir.name

    dur = duracao(video)
    hook, payoff = ([], []) if a.todo_o_video else janelas(video_dir)
    total = max(a.n * (6 if a.todo_o_video else 3), 12)
    if hook and payoff:
        tempos = distribuir(hook, total // 2) + distribuir(payoff, total - total // 2)
        origem = "hook+payoff"
    elif hook or payoff:
        tempos = distribuir(hook or payoff, total)
        origem = "hook" if hook else "payoff"
    else:
        tempos = []
    if not tempos:
        tempos = [(round(dur * (0.05 + 0.9 * (k + 0.5) / total), 3), "") for k in range(total)]
        origem = "uniforme"

    pasta = video_dir / "capa" / "candidatos"
    todos = pasta / "_todos"
    if todos.exists():
        shutil.rmtree(todos)
    todos.mkdir(parents=True)
    for antigo in pasta.glob("cand-*.jpg"):
        antigo.unlink()

    det = criar_detector()
    trechos_log, lut = lut_visualizacao(video_dir, video)

    # amostra = (tempo, linha, arquivo, filtro, origem). Por padrão, tudo vem do corte.
    amostras = [(t, linha, video, (lut if lut and any(a <= t < b for a, b in trechos_log) else ""), "corte")
                for t, linha in tempos]
    # PAUSA DA CAPA primeiro: os segundos parados antes da 1.ª fala (ficam fora do corte, mas estão no
    # intermediário). É o que evita varrer o vídeo quadro a quadro atrás de um quadro bom.
    pausa = None if a.sem_pausa_capa else janela_pausa_capa(video_dir, a.pausa_capa)
    if pausa:
        arq_p, ini_p, fim_p, vf_p = pausa
        n_p = max(4, a.n // 2)
        passo = (fim_p - ini_p) / n_p
        amostras = [(ini_p + passo * (i + 0.5), "pausa-capa", arq_p, vf_p, "pausa") for i in range(n_p)] + amostras
        print(f"pausa da capa: {ini_p:.1f}–{fim_p:.1f}s de {arq_p.name} ({n_p} quadros, com a cor do vídeo)")
    else:
        print("pausa da capa: não encontrada (gravação sem a pausa, ou sem intermediário) — varrendo o vídeo")

    avaliados = []
    for k, (t, linha, arq_fonte, vf, origem) in enumerate(amostras):
        arq = todos / f"t{k:03d}.jpg"
        tt = t if origem == "pausa" else min(t, dur - 0.05)
        if not extrair(arq_fonte, tt, arq, vf):
            continue
        viz: list[np.ndarray] = []                    # vizinhos ±DELTA_MOV s: medem o movimento
        # do MESMO arquivo e com o MESMO filtro da amostra: buscar no corte um tempo que só existe no
        # intermediário (a pausa está aos ~96 s, o corte tem 49 s) dava "movimento" enorme e zerava a nota.
        dur_fonte = duracao(arq_fonte) if origem == "pausa" else dur
        for dt in (-DELTA_MOV, DELTA_MOV):
            tv = min(max(tt + dt, 0.0), dur_fonte - 0.05)
            vaq = todos / f"t{k:03d}{'a' if dt < 0 else 'b'}.jpg"
            if extrair(arq_fonte, tv, vaq, vf):
                img = cv2.imread(str(vaq), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    viz.append(img)
                vaq.unlink(missing_ok=True)
        r = pontuar(arq, det, viz)
        avaliados.append({"tempo": t, "linha": linha or None, "origem": origem, "tmp": arq, **r})

    # Óculos escuros (o Carlos usa em muitos vídeos): o detector não acha olho nenhum e o critério viraria um
    # castigo igual para todos. Se NENHUM quadro tem olhos, neutraliza (0,5) e avisa.
    if avaliados and all(c["olhos_detectados"] == 0 for c in avaliados):
        print("AVISO: nenhum olho detectado em nenhum quadro (óculos escuros?) — critério 'olhos' neutralizado.")
        for c in avaliados:
            c["notas"]["olhos"] = 0.5
            c["olhos_neutralizado"] = True
            if c["rosto"]:
                c["total"] = round(sum(PESOS[k] * c["notas"][k] for k in PESOS), 4)

    avaliados.sort(key=lambda c: c["total"], reverse=True)
    escolhidos: list[dict] = []
    for c in avaliados:
        if all(abs(c["tempo"] - e["tempo"]) >= a.min_intervalo for e in escolhidos):
            escolhidos.append(c)
        if len(escolhidos) == a.n:
            break

    for i, c in enumerate(escolhidos, 1):
        nome = f"cand-{i:02d}.jpg"
        shutil.move(str(c.pop("tmp")), pasta / nome)
        c["arquivo"] = nome
        c["secao"] = secao_de(c["linha"], video_dir) if c["linha"] else None
    shutil.rmtree(todos)

    # A pose que o roteiro pediu para estes 3 s iniciais: quem escolhe a capa procura ISTO na folha
    # de contato, em vez do "quadro mais parado" (pedido do Carlos, 2026-09-18).
    pose = ((ler_json(video_dir / "roteiro.json") or {}).get("pose_capa") or "").strip() or None
    if pose:
        print(f"pose deste roteiro: {pose}")
    contato = folha_de_contato(escolhidos, pasta, slug, pose)
    relatorio = {
        "pose_capa": pose,
        "video": str(video.relative_to(video_dir)),
        "detector": det.nome,
        "amostragem": origem,
        "lut_visualizacao": bool(lut),
        "pesos": PESOS,
        "criado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "candidatos": escolhidos,
    }
    (pasta / "scores.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"detector: {det.nome}  amostragem: {origem}  avaliados: {len(avaliados)}  escolhidos: {len(escolhidos)}")
    if det.nome == "pele-heuristica":
        print("AVISO: sem Haar/YuNet — notas de rosto/olhos são aproximadas (ver SKILL.md).")
    for c in escolhidos[:5]:
        print(f"  {c['arquivo']}  {c['tempo']:6.2f}s  total {c['total']:.3f}  {c['notas']}")
    print(f"contato: {contato}")


if __name__ == "__main__":
    main()
