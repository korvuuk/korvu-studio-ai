#!/usr/bin/env python3
"""Fei-Fei Li — monta a camada de extras em TELA CHEIA (especificação: edicao/sequencia-extras.md, padrão Hinton v3).

- Vídeos (Y = material/youtube/cortes, E = brutos/extras) → edicao/extras-v2/Vnn-<id>.mp4 (cópia sem áudio).
- Fotos (material/fotos; stills de material/youtube/cortes/stills; quadro parado tirado de um corte) → edicao/extras-v2/<id>.jpg|.png.
- Escreve edicao/extras-v2/overlays.json, lido por
  gerar_props.py videos/<slug> --sem-titulo --overlays edicao/extras-v2/overlays.json
  (substitui os extras da EDL; edl.json/corte/legendas não mudam).

Tempos = saída da EDL v13 (segmentos saida_inicio/saida_fim). Uma troca NO MEIO de uma linha ("~t") é encaixada no
silêncio entre duas palavras mais perto do tempo pedido (edl.json.palavras_saida), nunca no meio de uma palavra.
`enquadrar` = foco x/y (fração da área útil), zoom inicial, pan (xFim/yFim) e `area` (px da fonte: tira legenda
queimada, logo de canto e barras pretas).

Uso: uv run python videos/2026-10-20-fei-fei-li/edicao/extras-v2/montar.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VIDEO = AQUI.parents[1]
FFMPEG = "/Users/teste/bin/ffmpeg"
Y = VIDEO / "material/youtube/cortes"
ST = Y / "stills"
E = VIDEO / "brutos/extras"
F = VIDEO / "material/fotos"
BB = "Bloomberg Originals — The Circuit"
TED15 = "TED2015 / Fei-Fei Li"
TED24 = "TED2024 / Fei-Fei Li"
SFPL = "San Francisco Public Library"
NATGEO = "National Geographic"

edl = json.loads((VIDEO / "edicao/edl.json").read_text())
LIN: dict[str, list[float]] = {}
for s in edl["segmentos"]:
    LIN.setdefault(s["linha"], [s["saida_inicio"], s["saida_fim"]])
    LIN[s["linha"]][1] = max(LIN[s["linha"]][1], s["saida_fim"])
PAL = edl["palavras_saida"]


def ini(l: str) -> float:
    return LIN[l][0]


def fim(l: str) -> float:
    return LIN[l][1]


def gap(t: float, linha: str) -> float:
    """Silêncio entre duas palavras da linha mais perto de t (meio do vão)."""
    ps = [p for p in PAL if p["linha"] == linha]
    melhor, dist = None, 1e9
    for a, b in zip(ps, ps[1:]):
        if b["inicio"] - a["fim"] < 0.06:
            continue
        m = (a["fim"] + b["inicio"]) / 2
        if abs(m - t) < dist:
            melhor, dist = m, abs(m - t)
    assert melhor is not None, (t, linha)
    return round(melhor, 2)


def foto(nome: str, pasta: Path = F) -> tuple:
    return ("foto", next(pasta.glob(nome + "*")))


def vid(nome: str, pasta: Path = Y) -> tuple:
    return ("video", next(pasta.glob(nome + "*")))


def still(nome: str, ss: float) -> tuple:
    """Quadro parado tirado de um corte (vídeo curto demais para a linha)."""
    return ("still", next(Y.glob(nome + "*")), ss)


def area16(w: int, h: int, topo: int = 0, base: int = 0, esq: int = 0, dir_: int = 0) -> dict:
    return {"x": esq, "y": topo, "largura": w - esq - dir_, "altura": h - topo - base}


A_BB = area16(1920, 1080, topo=70)          # sem a legenda "Fei-Fei Li" e o logo da Bloomberg no topo
A_TED24 = area16(1920, 1080, base=100)      # sem a linha de referências no rodapé do slide
A_NATGEO = {"x": 557, "y": 0, "largura": 806, "altura": 1080}   # só a foto, sem as barras pretas

# (n, início, fim, linhas, id, fonte, in, out, enquadrar, crédito)
#   início/fim: número = segundos de saída; ("~", t, linha) = encaixar no silêncio mais perto de t dentro da linha
SEQ = [
    (1, ini("L03"), fim("L03"), ["L03"], "CAPA-01", foto("CAPA-01"), None, None,
     {"x": 0.5, "y": 0.3, "zoom": 1.04}, "Stanford HAI / Queen Elizabeth Prize for Engineering"),
    (2, ini("L04"), ("~", 13.9, "L04"), ["L04"], "Y01", foto("Y01", ST), None, None,
     {"x": 0.5, "y": 0.5, "area": {"x": 538, "y": 108, "largura": 882, "altura": 950}}, BB),
    (3, ("~", 13.9, "L04"), fim("L04"), ["L04"], "Y03", foto("Y03", ST), None, None,
     {"x": 0.32, "xFim": 0.6, "y": 0.35, "area": A_BB}, BB + " / Daily Record"),
    (4, ini("L05"), fim("L05"), ["L05"], "E02", vid("E02", E), 0.0, None, {"x": 0.25, "y": 0.45}, SFPL),
    (5, ini("L06"), ("~", 24.3, "L06"), ["L06"], "Y04", foto("Y04", ST), None, None,
     {"x": 0.72, "y": 0.5, "area": A_BB}, BB),
    (6, ("~", 24.3, "L06"), fim("L06"), ["L06"], "E04", vid("E04", E), 5.0, None, {"x": 0.5, "y": 0.5}, TED15),   # in 5,0: a foto da lavanderia no telão (antes é o slide "Go do something more useful")
    (7, ini("L07"), ("~", 30.8, "L08"), ["L07", "L08"], "CAPA-03", foto("CAPA-03"), None, None,
     {"x": 0.5, "y": 0.42}, "PD Soros Fellowship (divulgação)"),
    (8, ("~", 30.8, "L08"), fim("L08"), ["L08"], "F03", foto("F03"), None, None,
     {"x": 0.33, "y": 0.5, "xFim": 0.4}, "Fei-Fei Li / Princeton (1999)"),
    (9, ini("L09"), ("~", 37.0, "L09"), ["L09"], "F04", foto("F04"), None, None,
     {"x": 0.5, "y": 0.5}, "Nassau Hall, Princeton — Wikimedia Commons (CC BY-SA)"),
    (10, ("~", 37.0, "L09"), fim("L09"), ["L09"], "Y09", foto("Y09", ST), None, None,
     {"x": 0.33, "y": 0.45, "area": A_BB}, BB),
    (11, ini("L10"), fim("L10"), ["L10"], "Y14", vid("Y14"), 0.0, None, {"x": 0.5, "y": 0.45}, TED15),
    (12, ini("L11"), ("~", 49.6, "L11"), ["L11"], "Y12", vid("Y12"), 0.0, None, {"x": 0.5, "y": 0.55}, TED15),
    (13, ("~", 49.6, "L11"), fim("L11"), ["L11"], "Y20", vid("Y20"), 0.0, None, {"x": 0.5, "y": 0.5}, TED15),
    (14, ini("L12"), fim("L12"), ["L12"], "Y13", still("Y13", 3.4), None, None, {"x": 0.45, "xFim": 0.55, "y": 0.5}, TED15),   # quadro parado com os 3 gatos (o clipe dá zoom no olho do gato laranja)   # o gato do meio (pan largo virava close no olho do gato laranja)
    (15, ini("L13"), ("~", 58.6, "L13"), ["L13"], "CAPA-04", foto("CAPA-04"), None, None,
     {"x": 0.5, "y": 0.4}, "Frank Wojciechowski / Princeton (2007)"),
    (16, ("~", 58.6, "L13"), fim("L13"), ["L13"], "F07", foto("F07"), None, None,
     {"x": 0.3, "y": 0.2, "xFim": 0.45, "yFim": 0.5}, "ImageNet (2011)"),
    (17, ini("L14"), ("~", 65.4, "L14"), ["L14"], "Y15", vid("Y15"), 0.0, None, {"x": 0.5, "y": 0.5}, TED15),
    (18, ("~", 65.4, "L14"), fim("L14"), ["L14"], "Y59", vid("Y59"), 0.0, None,
     {"x": 0.42, "y": 0.45, "area": A_TED24}, TED24),
    (19, ini("L15"), ("~", 74.0, "L15"), ["L15"], "Y23", still("Y23", 2.0), None, None,
     {"x": 0.3, "xFim": 0.7, "y": 0.5}, TED15),   # o clipe tem 3,88 s, a linha pede 3,93: quadro parado + pan
    (20, ("~", 74.0, "L15"), fim("L15"), ["L15"], "Y19", still("Y19", 2.5), None, None, {"x": 0.42, "y": 0.55}, TED15),   # urso com as etiquetas (o E05 em 9:16 só mostrava texto cortado)
    # L16 "E sabe o mais curioso?" — Carlos em tela cheia
    (21, ini("L17"), fim("L17"), ["L17"], "E09", vid("E09", E), 0.0, None, {"x": 0.6, "y": 0.45}, TED15),
    (22, ini("L18"), fim("L18"), ["L18"], "Y25", still("Y25", 1.3), None, None,
     {"x": 0.5, "y": 0.45, "zoom": 1.02, "area": A_BB}, BB + " / Krizhevsky, Sutskever, Hinton (2012)"),
    (23, ini("L19"), ("~", 95.3, "L19"), ["L19"], "F21", foto("F21"), None, None,
     {"x": 0.5, "y": 0.5}, "University of Toronto / Computer History Museum"),
    (24, ("~", 95.3, "L19"), fim("L19"), ["L19"], "Y17", vid("Y17"), 0.0, None, {"x": 0.5, "y": 0.5}, TED15),
    (25, ini("L20"), fim("L21"), ["L20", "L21"], "Y24", still("Y24", 5.0), None, None,
     {"x": 0.3, "xFim": 0.5, "y": 0.45, "area": {"x": 0, "y": 70, "largura": 1920, "altura": 750}}, BB + " / Johnny Guatto, University of Toronto"),   # sem as etiquetas de nome no rodapé
    (26, ini("L22"), fim("L22"), ["L22"], "Y60", vid("Y60"), 0.0, None,
     {"x": 0.22, "xFim": 0.5, "y": 0.5, "area": A_TED24}, TED24),
    # L23 "Mas olha só que interessante" — Carlos em tela cheia
    (27, ini("L24"), fim("L24"), ["L24"], "F20", foto("F20"), None, None,
     {"x": 0.3, "xFim": 0.75, "y": 0.5}, "Johnny Guatto / University of Toronto"),
    (28, ini("L25"), fim("L25"), ["L25"], "Y16", vid("Y16"), 0.0, None, {"x": 0.5, "y": 0.5}, TED15),
    (29, ini("L26"), ("~", 126.2, "L26"), ["L26"], "N14", foto("N14"), None, None,
     {"x": 0.5, "y": 0.45}, "Stanford HAI / QEPrize (2025)"),
    (30, ("~", 126.2, "L26"), fim("L26"), ["L26"], "Y66", vid("Y66"), 0.0, None,
     {"x": 0.5, "y": 0.4, "area": A_NATGEO}, NATGEO),
]


def rodar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"falhou: {' '.join(cmd[:6])}…\n{r.stderr[-1500:]}")


def tempo(t, linha_padrao: str) -> float:
    if isinstance(t, tuple):
        return gap(t[1], t[2])
    return round(float(t), 2)


def dur_video(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def main() -> None:
    overlays = []
    for n, t0, t1, linhas, mid, fonte, tin, tout, enq, cred in SEQ:
        a, b = tempo(t0, linhas[0]), tempo(t1, linhas[-1])
        kind, src = fonte[0], fonte[1]
        if kind == "foto":
            arq = AQUI / f"{mid}{src.suffix.lower()}"
            shutil.copyfile(src, arq)
            tipo = "imagem"
        elif kind == "still":
            arq = AQUI / f"{mid}.png"
            rodar([FFMPEG, "-hide_banner", "-y", "-ss", str(fonte[2]), "-i", str(src), "-frames:v", "1", str(arq)])
            tipo = "imagem"
        else:
            arq = AQUI / f"V{n:02d}-{mid}.mp4"
            rodar([FFMPEG, "-hide_banner", "-y", "-i", str(src), "-an", "-c:v", "copy", "-movflags", "+faststart", str(arq)])
            tipo = "video"
            d = dur_video(arq)
            if (tin or 0.0) + (b - a) > d + 0.02:
                raise SystemExit(f"#{n} {mid}: precisa de {b - a:.2f}s a partir de {tin or 0}, o clipe tem {d:.2f}s")
        o = {"linhas": linhas, "tipo": "extra", "extra": f"V{n:02d}", "extra_tipo": tipo,
             "arquivo": str(arq.relative_to(VIDEO)), "modo": "full", "som": False, "credito": cred,
             "faltando": False, "saida_inicio": a, "saida_fim": b, "enquadrar": enq,
             "descricao": f"v1 #{n} {mid}"}
        if tipo == "video":
            o["in"] = tin or 0.0
            if tout is not None:
                o["out"] = tout
        overlays.append(o)
    # faixas: encostados dentro de cada faixa; buracos só onde o Carlos volta (L16, L23)
    for x, y in zip(overlays, overlays[1:]):
        if y["saida_inicio"] - x["saida_fim"] > 1e-6:
            print(f"   Carlos em tela cheia: {x['saida_fim']:.2f} → {y['saida_inicio']:.2f}")
        assert y["saida_inicio"] >= x["saida_fim"] - 1e-6, (x["extra"], y["extra"])
    (AQUI / "overlays.json").write_text(json.dumps({"origem": "edicao/sequencia-extras.md", "overlays": overlays},
                                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for o in overlays:
        print(f"{o['extra']} {o['saida_inicio']:7.2f}–{o['saida_fim']:7.2f} {','.join(o['linhas']):8} {o['descricao']}")
    print(f"{len(overlays)} overlays → {AQUI / 'overlays.json'}")


if __name__ == "__main__":
    main()
