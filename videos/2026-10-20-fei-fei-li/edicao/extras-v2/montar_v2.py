#!/usr/bin/env python3
"""Fei-Fei Li — camada de extras v2 (17/10): tela cheia + PILHAS de 3 faixas, sincronia fala ↔ imagem.

Pedido do Carlos depois de ver a v1 (docs/decisoes.md 17/10): imagens deitadas/de grupo em PILHA (topo / meio / base)
em vez de um zoom que corta ("não consegue ver a imagem por completo"); a imagem do que ele cita entra quando ele cita
(o ImageNet aparecia só depois); sai a imagem de hardware vazia da L19. Mais as correções do QA (qa/relatorio.md):
E02 x 0.49 · Y04 x 0.58 · E09 in 2.3 · Y59 área sem a faixa vinho · E04 sem barras · Y01 sem a faixa azul · créditos curtos.

Saída: edicao/extras-v2/overlays-v2.json (lido por gerar_props.py --overlays). Mídias copiadas para edicao/extras-v2/.
Uso: uv run python videos/2026-10-20-fei-fei-li/edicao/extras-v2/montar_v2.py
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
E = VIDEO / "brutos/extras"
F = VIDEO / "material/fotos"
BB = "Bloomberg Originals"
TED15 = "TED2015 / Fei-Fei Li"
TED24 = "TED2024 / Fei-Fei Li"
CBS = "CBS Mornings"
SFPL = "San Francisco Public Library"
NATGEO = "National Geographic"
HAI = "Stanford HAI"

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


def palavra(txt: str, linha: str) -> float:
    """Início da palavra `txt` na linha (para a imagem entrar quando ele a diz)."""
    for p in PAL:
        if p["linha"] == linha and p["texto"].lower().strip('",.?:') == txt.lower():
            return round(p["inicio"], 2)
    raise SystemExit(f"palavra {txt!r} não está na {linha}")


# fontes: ("foto", Path) · ("video", Path) · ("still", Path, ss)
def foto(nome: str, pasta: Path = F) -> tuple:
    return ("foto", next(pasta.glob(nome + "*")))


def vid(nome: str, pasta: Path = Y) -> tuple:
    return ("video", next(pasta.glob(nome + "*.mp4")))


def still(nome: str, ss: float, pasta: Path = Y) -> tuple:
    return ("still", next(pasta.glob(nome + "*.mp4")), ss)


A_BB = {"x": 0, "y": 70, "largura": 1920, "altura": 1010}       # sem a legenda "Fei-Fei Li" e o logo da Bloomberg
A_BB_SEM_TAGS = {"x": 0, "y": 70, "largura": 1920, "altura": 750}  # Y24: sem as etiquetas de nome no rodapé
A_CBS = {"x": 0, "y": 70, "largura": 1920, "altura": 840}       # sem a data no topo e a barra "GODMOTHER OF A.I."
A_TED24 = {"x": 0, "y": 115, "largura": 1920, "altura": 855}    # sem a faixa vinho do topo e as referências do rodapé
A_TED24_GRAF = {"x": 0, "y": 200, "largura": 1920, "altura": 770}  # Y60: sem o título do slide (o crédito ficava em cima)
A_E04 = {"x": 0, "y": 58, "largura": 1280, "altura": 597}       # E04: sem as barras pretas do vídeo da TED
A_Y21 = {"x": 0, "y": 110, "largura": 1280, "altura": 610}      # Y21: sem o título "Ladles are hard"
A_NATGEO = {"x": 557, "y": 0, "largura": 806, "altura": 1080}   # só a foto, sem as barras pretas
A_Y01 = {"x": 538, "y": 108, "largura": 882, "altura": 870}     # só a foto da família (sem a faixa azul da base)

# item de pilha: (id, fonte, in, enquadrar, crédito)
def F_(id_, fonte, enq, cred, tin=0.0):
    return (id_, fonte, tin, enq, cred)


# (n, início, fim, linhas, id, fonte | ("pilha", [itens]), in, out, enquadrar, crédito)
SEQ = [
    (1, ini("L03"), fim("L03"), ["L03"], "CAPA-01", foto("CAPA-01"), None, None,
     {"x": 0.5, "y": 0.3, "zoom": 1.04}, "Stanford HAI / QEPrize"),
    (2, ini("L04"), palavra("e", "L04"), ["L04"], "Y01", foto("Y01", Y / "stills"), None, None,
     {"x": 0.5, "y": 0.45, "area": A_Y01}, BB),
    (3, palavra("e", "L04"), fim("L04"), ["L04"], "Y03", foto("Y03", Y / "stills"), None, None,
     {"x": 0.32, "xFim": 0.45, "y": 0.35, "area": A_BB}, BB + " / Daily Record"),
    (4, ini("L05"), fim("L05"), ["L05"], "E02", vid("E02", E), 0.0, None, {"x": 0.49, "y": 0.45}, SFPL),
    (5, ini("L06"), ("~", 24.3, "L06"), ["L06"], "Y04", foto("Y04", Y / "stills"), None, None,
     {"x": 0.58, "y": 0.5, "area": A_BB}, BB),
    (6, ("~", 24.3, "L06"), fim("L06"), ["L06"], "E04", vid("E04", E), 5.0, None,
     {"x": 0.5, "y": 0.5, "area": A_E04}, TED15),
    (7, ini("L07"), ("~", 30.8, "L08"), ["L07", "L08"], "CAPA-03", foto("CAPA-03"), None, None,
     {"x": 0.5, "y": 0.42}, "PD Soros Fellowship"),
    (8, ("~", 30.8, "L08"), fim("L08"), ["L08"], "F03", foto("F03"), None, None,
     {"x": 0.47, "y": 0.5, "xFim": 0.48}, "Princeton (1999)"),
    # L09 inteira em pilha: Princeton (prédio) · ela com a rede na tela · ela no escritório de Stanford
    (9, ini("L09"), fim("L09"), ["L09"], "P-L09", ("pilha", [
        F_("F04", foto("F04"), {"x": 0.5, "y": 0.55}, "Nassau Hall, Princeton — Wikimedia Commons"),
        F_("Y09", foto("Y09", Y / "stills"), {"x": 0.4, "y": 0.45, "area": A_BB}, BB),
        F_("Y08", still("Y08", 1.2), {"x": 0.5, "y": 0.5, "area": A_CBS}, CBS),
    ]), None, None, None, None),
    # L10: três crianças (pedido do Carlos)
    (10, ini("L10"), fim("L10"), ["L10"], "P-L10", ("pilha", [
        F_("Y14", vid("Y14"), {"x": 0.5, "y": 0.45}, TED15),
        F_("Y10", still("Y10", 1.7), {"x": 0.42, "y": 0.45}, TED15),
        F_("Y11", still("Y11", 1.5), {"x": 0.5, "y": 0.5}, TED15),
    ]), None, None, None, None),
    (11, ini("L11"), ("~", 49.6, "L11"), ["L11"], "P-L11", ("pilha", [
        F_("Y12", vid("Y12"), {"x": 0.5, "y": 0.5}, TED15),
        F_("Y13", still("Y13", 3.4), {"x": 0.5, "y": 0.5}, TED15),
        F_("Y19", still("Y19", 2.5), {"x": 0.45, "y": 0.55}, TED15),
    ]), None, None, None, None),
    (12, ("~", 49.6, "L11"), fim("L11"), ["L11"], "Y20", vid("Y20"), 0.0, None, {"x": 0.5, "y": 0.5}, TED15),
    # L12 "por que um computador seria diferente?": ela com a tecnologia (laboratório, quadro, robôs)
    (13, ini("L12"), fim("L12"), ["L12"], "P-L12", ("pilha", [
        F_("Y40", vid("Y40"), {"x": 0.45, "y": 0.5, "area": A_CBS}, CBS),
        F_("Y37", still("Y37", 1.5), {"x": 0.5, "y": 0.5, "area": A_CBS}, CBS),   # clipe de 3,3 s < linha
        F_("Y38", vid("Y38"), {"x": 0.5, "y": 0.5, "area": A_CBS}, CBS),
    ]), None, None, None, None),
    (14, ini("L13"), ("~", 58.6, "L13"), ["L13"], "CAPA-04", foto("CAPA-04"), None, None,
     {"x": 0.5, "y": 0.5}, "Princeton (2007)"),
    # "chamado ImageNet": o logo do ImageNet na tela quando ele diz o nome
    (15, ("~", 58.6, "L13"), fim("L13"), ["L13"], "P-L13", ("pilha", [
        F_("Y22", vid("Y22"), {"x": 0.5, "y": 0.5}, TED15),
        F_("F07", foto("F07"), {"x": 0.3, "y": 0.2, "xFim": 0.45, "yFim": 0.4}, "ImageNet (2011)"),
        F_("Y17", vid("Y17"), {"x": 0.5, "y": 0.5}, TED15),
    ]), None, None, None, None),
    (16, ini("L14"), ("~", 65.4, "L14"), ["L14"], "Y15", vid("Y15"), 0.0, None, {"x": 0.5, "y": 0.5}, TED15),
    (17, ("~", 65.4, "L14"), fim("L14"), ["L14"], "Y59", vid("Y59"), 0.0, None,
     {"x": 0.42, "y": 0.45, "area": A_TED24}, TED24),
    # "50 mil pessoas pela internet": mapa · o número no telão da TED · gente trabalhando
    (18, ini("L15"), ("~", 74.0, "L15"), ["L15"], "P-L15", ("pilha", [
        F_("Y23", still("Y23", 2.0), {"x": 0.5, "y": 0.5}, TED15),
        F_("E05", vid("E05", E), {"x": 0.5, "y": 0.4}, TED15),
        F_("Y36", vid("Y36"), {"x": 0.5, "y": 0.5, "area": A_CBS}, CBS),
    ]), None, None, None, None),
    (19, ("~", 74.0, "L15"), fim("L15"), ["L15"], "Y16", vid("Y16"), 0.0, None, {"x": 0.5, "y": 0.5}, TED15),
    # L16 "E sabe o mais curioso?" — Carlos em tela cheia
    (20, ini("L17"), fim("L17"), ["L17"], "E09", vid("E09", E), 2.3, None, {"x": 0.42, "y": 0.45}, TED15),
    (21, ini("L18"), fim("L18"), ["L18"], "Y25", still("Y25", 1.3), None, None,
     {"x": 0.5, "y": 0.45, "zoom": 1.02, "area": A_BB}, BB),
    (22, ini("L19"), palavra("usa", "L19"), ["L19"], "Y24", still("Y24", 5.0), None, None,
     {"x": 0.22, "xFim": 0.5, "y": 0.45, "area": A_BB_SEM_TAGS}, BB + " / U of Toronto"),
    # "usaram a ImageNet para treinar uma rede neural": fotos do banco · o diagrama dados/rede/GPU · o computador
    (23, palavra("usa", "L19"), palavra("numa", "L19"), ["L19"], "P-L19", ("pilha", [
        F_("Y20b", still("Y20", 2.0), {"x": 0.5, "y": 0.5}, TED15),
        F_("Y26", vid("Y26"), {"x": 0.5, "y": 0.5, "area": A_BB}, BB),
        F_("F21", foto("F21"), {"x": 0.5, "y": 0.5}, "University of Toronto / CHM"),
    ]), None, None, None, None),
    (24, palavra("numa", "L19"), fim("L19"), ["L19"], "Y21", vid("Y21"), 0.0, None,
     {"x": 0.5, "y": 0.5, "area": A_Y21}, TED15),
    (25, ini("L20"), fim("L21"), ["L20", "L21"], "F20", foto("F20"), None, None,
     {"x": 0.25, "xFim": 0.78, "y": 0.5}, "Johnny Guatto / University of Toronto"),
    (26, ini("L22"), fim("L22"), ["L22"], "Y60", vid("Y60"), 0.0, None,
     {"x": 0.22, "xFim": 0.5, "y": 0.5, "area": A_TED24_GRAF}, TED24),
    # L23 "Mas olha só que interessante" — Carlos em tela cheia
    (27, ini("L24"), fim("L24"), ["L24"], "N12", foto("N12"), None, None,
     {"x": 0.45, "xFim": 0.6, "y": 0.45}, HAI + " / QEPrize"),
    # "Os exemplos eram dela": três imagens com etiqueta
    (28, ini("L25"), fim("L25"), ["L25"], "P-L25", ("pilha", [
        F_("Y59b", still("Y59", 3.0), {"x": 0.42, "y": 0.45, "area": A_TED24}, TED24),
        F_("Y19b", still("Y19", 2.5), {"x": 0.45, "y": 0.55}, TED15),
        F_("Y12b", still("Y12", 6.0), {"x": 0.5, "y": 0.5}, TED15),
    ]), None, None, None, None),
    (29, ini("L26"), ("~", 125.4, "L26"), ["L26"], "N14", foto("N14"), None, None,
     {"x": 0.55, "y": 0.45}, HAI + " / QEPrize (2025)"),
    (30, ("~", 125.4, "L26"), fim("L26"), ["L26"], "Y66", vid("Y66"), 0.0, None,
     {"x": 0.5, "y": 0.4, "area": A_NATGEO}, NATGEO),
]


def rodar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"falhou: {' '.join(cmd[:6])}…\n{r.stderr[-1500:]}")


def tempo(t) -> float:
    if isinstance(t, tuple):
        return gap(t[1], t[2])
    return round(float(t), 2)


def dur_video(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def preparar(mid: str, fonte: tuple, n: int, tin: float | None, dur: float) -> tuple[Path, str]:
    """Copia/recorta a mídia para extras-v2/ e devolve (arquivo, tipo)."""
    kind, src = fonte[0], fonte[1]
    if kind == "foto":
        arq = AQUI / f"{mid}{src.suffix.lower()}"
        shutil.copyfile(src, arq)
        return arq, "imagem"
    if kind == "still":
        arq = AQUI / f"{mid}.png"
        rodar([FFMPEG, "-hide_banner", "-y", "-ss", str(fonte[2]), "-i", str(src), "-frames:v", "1", str(arq)])
        return arq, "imagem"
    arq = AQUI / f"V{n:02d}-{mid}.mp4"
    rodar([FFMPEG, "-hide_banner", "-y", "-i", str(src), "-an", "-c:v", "copy", "-movflags", "+faststart", str(arq)])
    d = dur_video(arq)
    if (tin or 0.0) + dur > d + 0.02:
        raise SystemExit(f"#{n} {mid}: precisa de {dur:.2f}s a partir de {tin or 0}, o clipe tem {d:.2f}s")
    return arq, "video"


def main() -> None:
    overlays = []
    for n, t0, t1, linhas, mid, fonte, tin, tout, enq, cred in SEQ:
        a, b = tempo(t0), tempo(t1)
        if fonte[0] == "pilha":
            faixas = []
            for (fid, f_src, f_in, f_enq, f_cred) in fonte[1]:
                arq, tipo = preparar(fid, f_src, n, f_in, b - a)
                item = {"id": fid, "arquivo": str(arq.relative_to(VIDEO)), "extra_tipo": tipo, "som": False,
                        "enquadrar": f_enq, "credito": f_cred}
                if tipo == "video":
                    item["in"] = f_in or 0.0
                faixas.append(item)
            o = {"linhas": linhas, "tipo": "extra", "extra": f"V{n:02d}", "extra_tipo": faixas[0]["extra_tipo"],
                 "arquivo": faixas[0]["arquivo"], "modo": "pilha", "som": False, "credito": None,
                 "faltando": False, "saida_inicio": a, "saida_fim": b, "pilha": faixas,
                 "descricao": f"v2 #{n} pilha " + "+".join(f["id"] for f in faixas)}
        else:
            arq, tipo = preparar(mid, fonte, n, tin, b - a)
            o = {"linhas": linhas, "tipo": "extra", "extra": f"V{n:02d}", "extra_tipo": tipo,
                 "arquivo": str(arq.relative_to(VIDEO)), "modo": "full", "som": False, "credito": cred,
                 "faltando": False, "saida_inicio": a, "saida_fim": b, "enquadrar": enq,
                 "descricao": f"v2 #{n} {mid}"}
            if tipo == "video":
                o["in"] = tin or 0.0
                if tout is not None:
                    o["out"] = tout
        overlays.append(o)
    for x, y in zip(overlays, overlays[1:]):
        if y["saida_inicio"] - x["saida_fim"] > 1e-6:
            print(f"   Carlos em tela cheia: {x['saida_fim']:.2f} → {y['saida_inicio']:.2f}")
        assert y["saida_inicio"] >= x["saida_fim"] - 1e-6, (x["extra"], y["extra"])
    (AQUI / "overlays-v2.json").write_text(
        json.dumps({"origem": "edicao/sequencia-extras.md (v2, 17/10)", "overlays": overlays},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for o in overlays:
        print(f"{o['extra']} {o['saida_inicio']:7.2f}–{o['saida_fim']:7.2f} {','.join(o['linhas']):8} "
              f"{o['modo']:5} {o['descricao']}")
    print(f"{len(overlays)} overlays → {AQUI / 'overlays-v2.json'}")


if __name__ == "__main__":
    main()
