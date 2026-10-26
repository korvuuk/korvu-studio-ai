#!/usr/bin/env python3
"""Livro-ChatGPT — camada de extras do par A/B (card do campo -> resultado em full), a partir da EDL atual.

Layout decidido pelo Carlos (21/10, decisões §3): clipe do campo de digitação = `card` (Carlos em tela cheia atrás,
escurecido); logo depois, na MESMA linha, o RESULTADO entra inteiro em `full`. E03/E07 (deitadas) e E09 (quase
quadrada) em `full` + `enquadrar` (pan que revela o detalhe); E05/E11 (em pé) `full` normal (cobre a tela, Ken Burns).
Troca card -> resultado: no silêncio logo depois da palavra do comando ("barra sketchnote:" | "o resumo…"), ou seja,
o comando é ouvido enquanto é digitado e o resultado aparece quando ele descreve o resultado.
O clipe do card entra com `in` tal que o ENVIO (tela.json) caia ~0,1–0,4 s antes do fim do card (a miniatura da capa
já está no campo).

A = Carlos desde o quadro 0 (L01 "Joga o livro no ChatGPT" com ele em tela cheia), E02 card em "e escreve barra
mindmap", E03 full na L02.  B = E01 (capa + logo, full, pan capa -> logo) do quadro 0; E02 card POR CIMA do E01;
E03 full até o fim da L02 — o Carlos só aparece na L03 (atrás do card E04).

Saída: overlays-A.json / overlays-B.json  (gerar_props.py <slug> --overlays edicao/overlays-ab/overlays-X.json)
Uso:   uv run python videos/2026-10-23-livro-chatgpt/edicao/overlays-ab/montar_overlays.py
"""
from __future__ import annotations

import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ED = AQUI.parent
edl = json.loads((ED / "edl.json").read_text())
seg = {s["linha"]: s for s in edl["segmentos"]}
pal = edl["palavras_saida"]

# instante do ENVIO e duração de cada clipe do campo (tela.json: trecho 1 = capa aparece 1,1 s; trecho 2 = digita)
ENVIO = {"E02": 3.30, "E04": 4.35, "E06": 3.80, "E08": 4.10, "E10": 3.05}
DUR = {"E02": 3.72, "E04": 4.44, "E06": 3.92, "E08": 4.24, "E10": 3.24}
DESC = {e["id"]: e for e in json.loads((ED.parent / "roteiro.json").read_text())["extras"]}

# linha, card, resultado, palavra depois da qual troca (índice na linha), enquadrar do resultado
PLANO = [
    ("L03", "E04", "E05", "sketchnote:", None),
    ("L04", "E06", "E07", "entrega", {"x": 0.12, "y": 0.5, "xFim": 0.55, "yFim": 0.5}),
    ("L05", "E08", "E09", "fluxograma:", {"x": 0.25, "y": 0.3, "xFim": 0.72, "yFim": 0.45}),
    ("L06", "E10", "E11", "quadrinhos:", None),
]
ENQ_E03 = {"x": 0.5, "y": 0.45, "xFim": 0.3, "yFim": 0.3}
ENQ_E01 = {"x": 0.24, "y": 0.5, "xFim": 0.71, "yFim": 0.5}


def cortes_saida(linha: str) -> list[float]:
    """Tempos de saída dos cortes internos da linha (troca de enquadramento da câmera)."""
    s, out, t = seg[linha], [], seg[linha]["saida_inicio"]
    ini = s["in"]
    for a, b in sorted(s.get("cortes_internos") or []):
        t += a - ini
        out.append(round(round(t * 25) / 25, 2))
        ini = b
    return out


def troca_depois(linha: str, palavra: str) -> float:
    """Meio do silêncio depois da palavra; se um corte interno da câmera cai a <= 0,12 s, usa o corte (a troca
    card -> resultado e a troca de enquadramento acontecem no mesmo quadro)."""
    t = _troca(linha, palavra)
    perto = [c for c in cortes_saida(linha) if abs(c - t) <= 0.12]
    return perto[0] if perto else t


def _troca(linha: str, palavra: str) -> float:
    ws = [p for p in pal if p["linha"] == linha]
    for i, p in enumerate(ws):
        if p["texto"].lower().startswith(palavra.lower().rstrip(":")):
            prox = ws[i + 1]["inicio"] if i + 1 < len(ws) else seg[linha]["saida_fim"]
            return round(round(((p["fim"] + prox) / 2) * 25) / 25, 2)   # meio do silêncio, grade de 25 fps
    raise SystemExit(f"palavra {palavra} não achada na {linha}")


def ov(eid, linhas, modo, a, b, **kw):
    tipo = DESC[eid]["tipo"]
    arq = f"edicao/extras/{eid}.mp4" if tipo == "tela" else f"edicao/extras/{eid}.png"
    o = {"linhas": linhas, "tipo": "extra", "extra": eid, "extra_tipo": tipo, "arquivo": arq, "modo": modo,
         "som": False, "credito": None, "faltando": False, "saida_inicio": round(a, 2), "saida_fim": round(b, 2),
         "descricao": DESC[eid]["descricao"]}
    o.update(kw)
    return o


def card(eid, linhas, a, b):
    d = b - a
    ini = max(0.0, round(min(DUR[eid] - d, ENVIO[eid] + 0.35 - d), 2))
    return ov(eid, linhas, "card", a, b, **{"in": ini, "out": round(min(DUR[eid], ini + d), 2)})


def miolo() -> list[dict]:
    out = []
    for lid, c, r, palavra, enq in PLANO:
        s = seg[lid]
        t = troca_depois(lid, palavra)
        out.append(card(c, [lid], s["saida_inicio"], t))
        kw = {"enquadrar": enq} if enq else {}
        out.append(ov(r, [lid], "full", t, s["saida_fim"], **kw))
    return out


t_e = troca_depois("L01", "ChatGPT")            # "Joga o livro no ChatGPT | e escreve barra mindmap"
fim_l01, fim_l02 = seg["L01"]["saida_fim"], seg["L02"]["saida_fim"]
A = [card("E02", ["L01"], t_e, fim_l01),
     ov("E03", ["L02"], "full", fim_l01, fim_l02, enquadrar=ENQ_E03)] + miolo()
B = [ov("E01", ["L01"], "full", 0.0, fim_l01, enquadrar=ENQ_E01),
     card("E02", ["L01"], t_e, fim_l01),
     ov("E03", ["L02"], "full", fim_l01, fim_l02, enquadrar=ENQ_E03)] + miolo()
for nome, lst in (("A", A), ("B", B)):
    (AQUI / f"overlays-{nome}.json").write_text(json.dumps({"variante": nome, "overlays": lst},
                                                           ensure_ascii=False, indent=1))
    print(f"overlays-{nome}.json")
    for o in lst:
        x = f" in {o['in']:.2f}–{o['out']:.2f}" if "in" in o else ""
        print(f"   {o['extra']} {o['modo']:<5} {o['saida_inicio']:6.2f}–{o['saida_fim']:6.2f}{x}"
              + (" enquadrar" if o.get("enquadrar") else ""))
print(f"B: o Carlos entra (sem extra por cima) em {fim_l02:.2f} s — atrás do card E04 (L03)")
