#!/usr/bin/env python3
"""Hinton v2 — monta a camada de extras em TELA CHEIA (especificação: edicao/sequencia-extras-v2.md).

- Vídeos (P = material/youtube/cortes-podcast, E = brutos/extras) → edicao/extras-v2/Vnn-<id>.mp4 (cópia sem áudio;
  E09 recortado de novo do original com 11 s, porque a entrada 24 dura 10,72 s e o E09 tinha 8 s).
- Fotos (material/fotos) → edicao/extras-v2/<id>.jpg com a rotação EXIF aplicada (feito antes, ver HANDOFF 15/10).
- Escreve edicao/extras-v2/overlays.json, lido por
  gerar_props.py videos/<slug> --sem-titulo --overlays edicao/extras-v2/overlays.json
  (substitui os extras da EDL; edl.json/corte/legendas não mudam).

Tempos = saída da EDL v24; as trocas no meio de uma linha caem no silêncio entre palavras mais perto do tempo da
especificação. `enquadrar` = foco x/y (fração da área útil), zoom inicial, pan (xFim/yFim) e `area` (px da fonte:
tira barras pretas, legenda queimada em inglês, tarja de TV e logos de canto).

Uso: uv run python videos/2026-10-20-geoffrey-hinton/edicao/extras-v2/montar_v2.py
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VIDEO = AQUI.parents[1]
FFMPEG = "/Users/teste/bin/ffmpeg"
P = VIDEO / "material/youtube/cortes-podcast"
E = VIDEO / "brutos/extras"
YT = VIDEO / "material/youtube"
DOAC = "The Diary of a CEO"
CBS = "60 Minutes / CBS News"
NOBEL = "NobelPrize.org"

# (n, inicio, fim, linhas, id, fonte, in, out, enquadrar, credito)
#   fonte: Path de vídeo a copiar | "foto" (já em extras-v2/<id>.jpg) | ("corte", arquivo, ss, t)
SEQ = [
    (1, 12.48, 16.48, ["L03"], "CAPA-02", "foto", None, None,
     {"x": 0.54, "y": 0.27, "zoom": 1.08}, "John Sears / Wikimedia Commons (CC BY-SA 4.0)"),
    # P02: abre no rosto (direita) e o pan revela o quadro com as redes à esquerda; área sem o canto do logo DOAC
    (2, 16.48, 18.52, ["L04"], "P02", P / "P02-hinton-jovem-quadro-redes.mp4", 0.0, None,
     {"x": 0.58, "xFim": 0.36, "y": 0.45, "area": {"x": 0, "y": 0, "largura": 1920, "altura": 1000}}, DOAC),
    (3, 18.52, 20.44, ["L04"], "P11", P / "P11-familia-george-boole.mp4", 0.5, None,
     {"x": 0.48, "y": 0.5, "area": {"x": 0, "y": 0, "largura": 1920, "altura": 900}}, DOAC),
    (4, 20.44, 22.40, ["L04"], "P14", P / "P14-familia-joan-hinton.mp4", 0.5, None,
     {"x": 0.52, "y": 0.45, "area": {"x": 576, "y": 44, "largura": 768, "altura": 992}}, DOAC),
    (5, 22.40, 25.84, ["L05"], "F02", "foto", None, None, {"x": 0.5, "y": 0.45}, CBS),
    (6, 25.84, 28.88, ["L05"], "F01", "foto", None, None, {"x": 0.47, "y": 0.4}, CBS),
    (7, 28.88, 33.16, ["L06"], "P04", P / "P04-cerebro-neuronios-animacao.mp4", 0.8, None, {"x": 0.5, "y": 0.5}, DOAC),
    (8, 33.16, 38.68, ["L07"], "E03", E / "E03-edimburgo-jovem.mp4", 0.0, None,
     {"x": 0.5, "y": 0.4, "area": {"x": 560, "y": 0, "largura": 790, "altura": 1080}}, CBS),
    # P06: dentro da imagem 4:3 (sem barras) e acima da legenda queimada; cartões MAN/WOMAN → foto da mulher
    # (1,12 s: o quadro 1,08 ainda é o dissolve do plano anterior; o quadro 6,20 já é o dissolve para o plano seguinte → out 6,00 e segura a foto)
    (9, 38.68, 44.36, ["L08"], "P06", P / "P06-perceptron-rosenblatt-arquivo.mp4", 1.12, 6.00,
     {"x": 0.36, "xFim": 0.50, "y": 0.6, "area": {"x": 340, "y": 84, "largura": 1236, "altura": 796}}, DOAC),
    (10, 44.36, 48.92, ["L09"], "P03", P / "P03-hinton-jovem-estante.mp4", 0.0, None,
     {"x": 0.48, "y": 0.5}, DOAC),
    (11, 48.92, 56.48, ["L10"], "E05", E / "E05-orientador.mp4", 0.0, 5.60,
     {"x": 0.5, "y": 0.45, "area": {"x": 500, "y": 0, "largura": 920, "altura": 1080}}, CBS),
    # fim do P03 com recorte fechado no rosto (não repete a foto F01 da entrada 6)
    (12, 56.48, 59.04, ["L10"], "P03", P / "P03-hinton-jovem-estante.mp4", 3.64, None,
     {"x": 0.48, "y": 0.42, "zoom": 1.6}, DOAC),
    (13, 59.04, 63.60, ["L11"], "P01", P / "P01-hinton-jovem-computador.mp4", 0.0, None,
     {"x": 0.34, "y": 0.5}, DOAC),
    (14, 63.60, 67.04, ["L12"], "F10", "foto", None, None, {"x": 0.22, "xFim": 0.80, "y": 0.5},
     "Johnny Guatto / University of Toronto"),
    (15, 67.04, 70.84, ["L13"], "F12", "foto", None, None, {"x": 0.55, "y": 0.5},
     "University of Toronto / Computer History Museum"),
    (16, 70.84, 74.28, ["L13"], "F14", "foto", None, None, {"x": 0.74, "y": 0.55},
     "ImageNet / Computer History Museum"),
    (17, 74.28, 80.64, ["L14"], "P05", P / "P05-chip-conexoes-animacao.mp4", 0.4, None, {"x": 0.5, "y": 0.5}, DOAC),
    (18, 80.64, 85.84, ["L15"], "E07", E / "E07-google-toronto.mp4", 2.80, None, {"x": 0.5, "y": 0.5}, CBS),
    (19, 85.84, 87.68, ["L15"], "F18", "foto", None, None, {"x": 0.42, "y": 0.3},
     "Eviatar Bach / Wikimedia Commons (CC BY-SA 3.0)"),
    (20, 87.68, 91.32, ["L16"], "F19", "foto", None, None, {"x": 0.47, "y": 0.5},
     "Steve Jurvetson / Wikimedia Commons (CC BY 2.0)"),
    (21, 91.32, 94.84, ["L16"], "F20", "foto", None, None, {"x": 0.26, "y": 0.5}, "Computer History Museum"),
    (22, 94.84, 101.32, ["L17", "L18"], "CAPA-08", "foto", None, None, {"x": 0.48, "y": 0.3, "zoom": 1.05},
     "Ramsey Cardy / Collision via Sportsfile (CC BY 2.0)"),
    # E08: sem a tarja da BBC (área acima de y 790)
    (23, 101.32, 107.16, ["L19"], "E08", E / "E08-riscos-bbc.mp4", 0.0, None,
     {"x": 0.56, "y": 0.62, "area": {"x": 0, "y": 0, "largura": 1920, "altura": 790}}, "BBC News"),
    (24, 107.16, 117.88, ["L20", "L21"], "E09", ("corte", "66WiF8fXL0k-Geoffrey_Hinton_Nobel_Prize_in_Physics_2024_-_Official_interview.mp4", 57.5, 11.0), 0.0, None,
     {"x": 0.37, "y": 0.4}, NOBEL),
    # P10: x 18–50 % (Hinton + o Rei), acima da legenda queimada
    (25, 117.88, 121.52, ["L22"], "P10", P / "P10-nobel-recebendo-do-rei.mp4", 0.0, None,
     {"x": 0.34, "y": 0.4, "area": {"x": 0, "y": 0, "largura": 1920, "altura": 915}},
     "The Nobel Prize / The Diary of a CEO"),
    (26, 121.52, 125.20, ["L23"], "N03", "foto", None, None, {"x": 0.5, "y": 0.35},
     "Nobel Prize Outreach / Nanaka Adachi"),
    (27, 125.20, 128.72, ["L23"], "N18", "foto", None, None, {"x": 0.5, "y": 0.3, "zoom": 1.05},
     "Jennifer 8. Lee / Wikimedia Commons (CC BY-SA 4.0)"),
    (28, 128.72, 133.28, ["L24"], "E10", E / "E10-banquete-produtividade.mp4", 0.0, None,
     {"x": 0.49, "y": 0.4, "area": {"x": 0, "y": 0, "largura": 1700, "altura": 1080}}, NOBEL),
    (29, 133.28, 139.12, ["L25"], "E11", E / "E11-banquete-golpes.mp4", 0.0, None,
     {"x": 0.49, "y": 0.4, "area": {"x": 0, "y": 0, "largura": 1700, "altura": 1080}}, NOBEL),
]


def rodar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"falhou: {' '.join(cmd[:6])}…\n{r.stderr[-1500:]}")


def main() -> None:
    overlays = []
    for n, ini, fim, linhas, mid, fonte, tin, tout, enq, cred in SEQ:
        if fonte == "foto":
            arq = AQUI / f"{mid}.jpg"
            tipo = "imagem"
        else:
            arq = AQUI / f"V{n:02d}-{mid}.mp4"
            tipo = "video"
            if isinstance(fonte, tuple):
                _, nome, ss, t = fonte
                rodar([FFMPEG, "-hide_banner", "-y", "-ss", str(ss), "-t", str(t), "-i", str(YT / nome), "-an",
                       "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                       "-profile:v", "high", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                       "-movflags", "+faststart", str(arq)])
            else:
                rodar([FFMPEG, "-hide_banner", "-y", "-i", str(fonte), "-an", "-c:v", "copy", "-movflags", "+faststart",
                       str(arq)])
        if not arq.exists():
            raise SystemExit(f"falta {arq}")
        o = {"linhas": linhas, "tipo": "extra", "extra": f"V{n:02d}", "extra_tipo": tipo,
             "arquivo": str(arq.relative_to(VIDEO)), "modo": "full", "som": False, "credito": cred,
             "faltando": False, "saida_inicio": ini, "saida_fim": fim, "enquadrar": enq,
             "descricao": f"v2 #{n} {mid}"}
        if tipo == "video":
            o["in"] = tin or 0.0
            if tout is not None:
                o["out"] = tout
        overlays.append(o)
    # encostados, em ordem, sem buraco: 12,48 → 139,12
    for a, b in zip(overlays, overlays[1:]):
        assert abs(a["saida_fim"] - b["saida_inicio"]) < 1e-6, (a["extra"], b["extra"])
    (AQUI / "overlays.json").write_text(json.dumps({"origem": "edicao/sequencia-extras-v2.md", "overlays": overlays},
                                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(overlays)} overlays → {AQUI / 'overlays.json'}")


if __name__ == "__main__":
    main()
