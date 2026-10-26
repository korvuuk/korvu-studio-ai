"""Gera a EDL (lista de decisões de edição) -> edicao/edl.json + edicao/edl.md (+ edicao/preview.mp4)

uso: uv run python edl.py <video_dir> [--recalcular] [--sem-preview]

Sem --recalcular: gera do zero a partir de alinhamento.json + roteiro.json (a EDL anterior,
se existir, vai para edicao/edl.anterior.json).
Com --recalcular: lê o edl.json editado (troca de take, in/out, cortes_internos, zoom, layout,
segmentos removidos/adicionados), MANTÉM essas edições e recalcula os campos derivados
(saida_inicio/fim, palavras_saida, overlays, duracao_saida). Mantém o valor de "aprovado".
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import align as A  # noqa: E402
import locutores as LOC  # noqa: E402
from common import (ALTURA, FFMPEG, FPS, FRAME, LARGURA, SR, ZOOM_ESCALA, ZOOM_MAX, ZOOM_ORIGEM,  # noqa: E402
                    avisar_uma_vez, carregar_roteiro, componentes_registrados, destaques_por_posicao, edicao,
                    escrever_json, fmt_origem, fmt_t, folga_silencio, fontes_de_edicao, _limiar_energia, ler_json, limites_energia, log, nivel_ruido, rms_wav,
                    normalizar_id_extra, pecas_do_segmento, ponto_mais_silencioso, rel, resolver_componente,
                    resolver_video_dir, run, tipo_da_fonte, wav16k_path, wav48k_path)

PAUSA_ALVO = {"normal": 0.08, "pausa": 0.45, "pausa_longa": 0.75}   # 2026-10-01: era 0,20/0,60/0,90 — "muita pausa entre uma linha e a outra"
PRE = 0.06            # antes da 1ª palavra (ASR). O ataque suave é protegido por GUARDA_ENERGIA (medido no áudio);
                      # 2026-10-01: era 0,15 e, somado ao POS, deixava ~0,33 s de silêncio entre linhas
POS = 0.08            # depois da última palavra (mínimo; a cauda é protegida por GUARDA_ENERGIA). Era 0,18
SNAP = 0.06           # busca do ponto mais silencioso (±)
GUARDA_ENERGIA = 0.04  # s — o corte fica ≥ isto antes do ataque / depois da cauda da ENERGIA da palavra
PAUSA_INTERNA = 0.25  # (2026-10-01: era 0,35) pausas maiores que isso DENTRO da linha... (2026-09-16: era 0.70 e deixava buracos de
                      # 0,4–1,3 s no corte; as pausas intencionais do roteiro são as de FIM de linha, em PAUSA_ALVO)
PAUSA_RESTA = 0.12    # (2026-10-01: era 0,18) ...ficam com esta duração (respiro natural, sem soar cortado)
GAP_MULETA = 0.15     # silêncio que sobra no lugar de uma muleta cortada
ZOOM_PUNCH = {"tipo": "punch", "escala": ZOOM_ESCALA}
ZOOM_DIF_MIN = 0.04   # enquadramentos com escalas a menos que isto = "o mesmo" (corte não disfarçado)
# 2026-09-18 (Carlos): "o zoom tem que ser proposital… tem um ponto que ele deu um zoom e voltou de novo,
# isso não pode acontecer nunca". Um enquadramento tem de SEGURAR pelo menos este tempo antes de trocar;
# peça curta demais herda o enquadramento da anterior em vez de abrir e fechar num piscar.
ZOOM_SEGURA_MIN = 1.0   # s — abaixo disto o enquadramento SEGURA (o corte fica sem disfarce, mas
                        # é melhor que abrir e fechar num piscar). Com MIN_PECA_S=0,8 o mais rápido possível é 1 s.
MIN_PECA = 0.8          # s — peça menor que isto não se lê: os cortes à volta são fundidos e ela sai
MARGEM_IA = 0.08      # s — distância mínima entre ponto de corte e voz da IA (zonas_ia; cobre quantização + alça)
MARGEM_IA_CORTE = 0.06  # s — folga de um corte interno que remove fala da IA dentro de um silêncio do take
ALCA = 0.015          # = render_corte.ALCA (áudio de cada peça vai 15 ms além das bordas)
CAMPOS_EDITAVEIS = ("fonte", "in", "out", "cortes_internos", "zoom", "layout")
CAMPOS_ZOOM = ("zoom_pecas", "zoom_origem")    # plano de enquadramento (planejar_zoom); editáveis também
MARCA = {"ok": "[OK]", "revisar": "[REVISAR]", "parafrase": "[PARAFRASE]", "faltando": "[FALTANDO]",
         "manual": "[MANUAL]"}


class Ctx:
    def __init__(self, vd: Path):
        self.vd = vd
        ed = edicao(vd)
        self.roteiro = carregar_roteiro(vd)
        self.rot = {l["id"]: l for l in self.roteiro["linhas"]}
        self.lrot = {l.id: l for l in A.preparar_roteiro(self.roteiro)}
        self.ordem = [l["id"] for l in self.roteiro["linhas"]]
        self.tr = ler_json(ed / "transcricao.json")
        self.al = ler_json(ed / "alinhamento.json")
        fj = ler_json(ed / "fontes.json")
        self.fontes = fontes_de_edicao(fj["fontes"])          # só o principal (sem amostras de cor)
        self.extras = fj.get("extras") or {}                   # cenas extras ingeridas (edicao/extras/)
        self.decl_extras = {normalizar_id_extra(e["id"]): e for e in (self.roteiro.get("extras") or [])
                            if e.get("id")}
        self.slug = self.roteiro.get("slug") or vd.name
        self.registrados = componentes_registrados()
        self.avisos_extras: list[tuple[str, float, list[str]]] = []
        self.por_fonte: dict[str, list[dict]] = {}
        for w in self.tr["palavras"]:
            self.por_fonte.setdefault(w["fonte"], []).append(w)
        for ws in self.por_fonte.values():
            ws.sort(key=lambda w: (w["inicio"], w["i"]))
        self.al_linha = {l["id"]: l for l in self.al["linhas"]}
        self.takes = {t["take_id"]: t for l in self.al["linhas"] for t in l["takes"]}
        # método ChatGPT-monitor: zonas com voz da IA (+ cauda da reverb) = proibidas para pontos de corte
        self.loc = LOC.carregar(vd) or {}
        self.zonas: dict[str, list[list[float]]] = self.loc.get("zonas_ia") or {}
        self.rostos: dict[tuple, tuple | None] = {}      # cache da detecção de rosto (fonte, tempos)
        self.info_rosto: dict[int, str] = {}             # n do segmento -> "rosto 3/3" | "padrão (0/3)"

    def wav(self, fonte):
        return str(wav16k_path(self.vd, fonte))

    def dur(self, fonte):
        return float(self.fontes[fonte]["duracao"])


# ---------------------------------------------------------------- pontos de corte
def _snap(ctx, fonte, t, lo, hi):
    return round(ponto_mais_silencioso(ctx.wav(fonte), t, lo, hi), 3)


def _piso_frame(t: float) -> float:
    return round(math.floor(t * FPS + 1e-6) / FPS, 6)


def _teto_frame(t: float) -> float:
    return round(math.ceil(t * FPS - 1e-6) / FPS, 6)


def _ataque(ctx, fonte, w, lo) -> float:
    """Início da ENERGIA da palavra (ataque suave incluído), nunca antes de `lo`."""
    return limites_energia(ctx.wav(fonte), w["inicio"], w["fim"], lo, w["fim"])[0]


def _cauda(ctx, fonte, w, hi) -> float:
    """Fim da ENERGIA da palavra (cauda da vogal / consoante final), nunca depois de `hi`."""
    return limites_energia(ctx.wav(fonte), w["inicio"], w["fim"], w["inicio"], hi)[1]


def pontos_in_out(ctx: Ctx, fonte: str, i_ini: int, i_fim: int, pausa: str) -> tuple[float, float]:
    ws = ctx.por_fonte[fonte]
    pos = {w["i"]: k for k, w in enumerate(ws)}
    k0, k1 = pos[i_ini], pos[i_fim]
    first, last = ws[k0], ws[k1]
    prev = ws[k0 - 1] if k0 > 0 else None
    nxt = ws[k1 + 1] if k1 + 1 < len(ws) else None
    # voz da IA antes/depois do take (zonas_ia, com a cauda da reverb): nem o `in` nem a pausa do `out` entram nela
    lo_ia, hi_ia = 0.0, ctx.dur(fonte)
    for za, zb in ctx.zonas.get(fonte, []):
        if za < first["inicio"]:
            lo_ia = max(lo_ia, zb + MARGEM_IA)
        if zb > last["fim"]:
            hi_ia = min(hi_ia, za - MARGEM_IA)
    lo = max(prev["fim"] + 0.02 if prev else 0.0, lo_ia)
    hi = min((nxt["inicio"] - 0.05) if nxt else ctx.dur(fonte) - 0.01, hi_ia)
    # vizinhos: nem a cauda da palavra anterior nem o ataque da seguinte entram (no máx. até o meio do silêncio)
    if prev:
        lo = max(lo, min(_cauda(ctx, fonte, prev, first["inicio"]) + 0.02, (prev["fim"] + first["inicio"]) / 2))
    if nxt:
        hi = min(hi, max(_ataque(ctx, fonte, nxt, last["fim"]) - 0.02, (last["fim"] + nxt["inicio"]) / 2))
    # o corte nunca entra na ENERGIA da 1.ª/última palavra (a borda do ASR/refino deixa de fora o ataque suave)
    teto_in = _ataque(ctx, fonte, first, lo) - GUARDA_ENERGIA
    piso_out = _cauda(ctx, fonte, last, hi) + GUARDA_ENERGIA
    ini = min(first["inicio"] - PRE, teto_in)
    if ini < lo:
        ini = min(lo, first["inicio"])
    ini = _snap(ctx, fonte, ini, max(ini - SNAP, lo), min(ini + SNAP, teto_in))
    # corte em silêncio de verdade: nenhum som a ±GUARDA do ponto (independe das bordas do ASR)
    ini = folga_silencio(ctx.wav(fonte), ini, lo, min(teto_in, first["inicio"] - 0.01), GUARDA_ENERGIA)
    out = max(last["fim"] + max(POS, PAUSA_ALVO.get(pausa, 0.20)), piso_out)
    if out > hi:                               # não há silêncio suficiente (ou a IA começa a falar): limita a pausa
        out = max(hi, last["fim"] + 0.03)
        if nxt and out > nxt["inicio"] - 0.01:
            out = (last["fim"] + nxt["inicio"]) / 2
    out = _snap(ctx, fonte, out, max(out - SNAP, piso_out, last["fim"] + 0.03), min(out + SNAP, hi))
    out = folga_silencio(ctx.wav(fonte), out, max(piso_out, last["fim"] + 0.03), hi, GUARDA_ENERGIA)
    out = min(out, max(hi_ia, last["fim"]))    # IA colada no fim: corta no fim da palavra, nunca depois
    ini = max(ini, min(lo_ia, first["inicio"]))
    # grade de frames PARA FORA (o render arredonda para o frame mais próximo: o `in` podia andar até 20 ms para
    # dentro do ataque) — só se ainda couber entre os vizinhos e as zonas da IA
    iq = _piso_frame(ini)
    ini = iq if iq >= lo - 1e-6 else _teto_frame(ini)
    oq = _teto_frame(out)
    out = oq if oq <= max(hi, last["fim"]) + 1e-6 and oq <= max(hi_ia, last["fim"]) + 1e-6 else _piso_frame(out)
    return round(max(0.0, ini), 6), round(min(out, ctx.dur(fonte)), 6)


def palavras_no_intervalo(ctx: Ctx, fonte: str, a: float, b: float) -> list[dict]:
    """Palavras do Carlos (e `null`) com o meio em [a, b] — palavras da IA nunca entram na legenda/análise."""
    return [w for w in ctx.por_fonte.get(fonte, [])
            if w.get("locutor") != "ia" and a <= (w["inicio"] + w["fim"]) / 2 <= b]


def voz_ia_nas_pecas(ctx: Ctx, fonte: str, pecas: list[tuple[float, float]]) -> float:
    """Segundos de zona da IA dentro das peças (com a alça de áudio do render). Tem que ser 0."""
    return round(sum(max(0.0, min(b + ALCA, zb) - max(a - ALCA, za))
                     for a, b in pecas for za, zb in ctx.zonas.get(fonte, [])), 3)


def muleta_e_fala_do_roteiro(toks, mapa: dict, lr, k: int) -> bool:
    """Token com cara de muleta ('ai', 'é', 'né'…) que na verdade é o ASR escrevendo errado palavras do roteiro que
    ficaram sem par ali (ex.: roteiro "não é a IA. Ela…", ASR "não é AI. Ela…": 'ai' ≈ 'a'+'ia'). Cortar isso apaga
    fala do roteiro — então NÃO é muleta. Compara o token com as palavras do roteiro não casadas entre as vizinhas
    casadas (ratio ≥ 66)."""
    from rapidfuzz import fuzz
    from common import norm_palavra
    w0 = max((mapa[i] for i in range(k) if mapa.get(i) is not None), default=-1)
    w1 = min((mapa[i] for i in range(k + 1, len(toks)) if mapa.get(i) is not None), default=len(lr.palavras))
    casadas = {v for v in mapa.values() if v is not None}
    falta = [lr.palavras[j] for j in range(w0 + 1, w1) if j not in casadas]
    alvo = "".join(t for p in falta for t in norm_palavra(p))
    return bool(alvo) and fuzz.ratio(toks[k].t, alvo) >= 66


def analisar(ctx: Ctx, linha_id: str, ws: list[dict]):
    """tokens da fala do segmento alinhados ao roteiro -> (unidades p/ legenda, i das muletas)"""
    lr = ctx.lrot[linha_id]
    toks = A.tokens_por_fonte(ws, [lr]).get(ws[0]["fonte"], []) if ws else []
    mapa, mul, _ = A.mapear([t.t for t in toks], lr)
    muletas = set()
    for k in mul:
        if 0 < k < len(toks) - 1 and not muleta_e_fala_do_roteiro(toks, mapa, lr, k):
            muletas.update(range(toks[k].wi, toks[k].wf + 1))
    unidades = []
    for k, tk in enumerate(toks):
        j = mapa.get(k)
        if unidades and unidades[-1]["wi"] == tk.wi and unidades[-1]["wf"] == tk.wf:
            if j is not None:
                unidades[-1]["js"].add(j)
            continue
        unidades.append({"wi": tk.wi, "wf": tk.wf, "js": {j} if j is not None else set()})
    return unidades, muletas


def cortes_auto(ctx: Ctx, fonte: str, ws: list[dict], muletas: set[int]) -> list[list[float]]:
    """Cortes internos. As bordas respeitam a ENERGIA das palavras vizinhas (cauda de A / ataque de B + guarda) e
    são quantizadas para DENTRO do trecho removido (tira menos, nunca come palavra); a fala da IA é o contrário
    (quantizada para FORA: tira mais, nunca vaza)."""
    cortes = []
    wav = ctx.wav(fonte)

    def dentro(c0, c1, lo_c, hi_c):
        # bordas em silêncio de verdade (a energia da palavra seguinte pode começar dentro do intervalo que o ASR
        # deu à muleta); depois a grade de frames para dentro do trecho removido
        c0 = folga_silencio(wav, c0, lo_c, c1 - 2 / FPS, GUARDA_ENERGIA)
        c1 = folga_silencio(wav, c1, c0 + 2 / FPS, hi_c, GUARDA_ENERGIA)
        c0, c1 = _teto_frame(c0), _piso_frame(c1)
        if c1 - c0 >= 2 / FPS - 1e-6:
            cortes.append([c0, c1])

    k = 1
    while k < len(ws) - 1:
        if ws[k]["i"] in muletas:
            k2 = k
            while k2 + 1 < len(ws) - 1 and ws[k2 + 1]["i"] in muletas:
                k2 += 1
            a, b = ws[k - 1], ws[k2 + 1]
            if b["inicio"] - a["fim"] > GAP_MULETA + 0.04:
                lo_c = _cauda(ctx, fonte, a, ws[k]["inicio"]) + GUARDA_ENERGIA
                hi_c = _ataque(ctx, fonte, b, ws[k2]["fim"]) - GUARDA_ENERGIA
                if lo_c > ws[k]["inicio"]:          # A emenda na muleta sem silêncio: volta à regra antiga
                    lo_c = a["fim"] + 0.02
                if hi_c < ws[k2]["fim"]:
                    hi_c = b["inicio"] - 0.02
                c0 = max(a["fim"] + GAP_MULETA / 2, lo_c)
                c1 = min(b["inicio"] - GAP_MULETA / 2, hi_c)
                c0 = _snap(ctx, fonte, c0, lo_c, min(c0 + SNAP, ws[k]["inicio"]))
                c1 = _snap(ctx, fonte, c1, max(c1 - SNAP, ws[k2]["fim"]), hi_c)
                dentro(c0, c1, lo_c, hi_c)
            k = k2 + 1
            continue
        k += 1
    for k in range(1, len(ws)):
        a, b = ws[k - 1], ws[k]
        if a["i"] in muletas or b["i"] in muletas:
            continue
        if b["inicio"] - a["fim"] > PAUSA_INTERNA:
            lo_c = max(a["fim"] + 0.05, _cauda(ctx, fonte, a, b["inicio"]) + GUARDA_ENERGIA)
            hi_c = min(b["inicio"] - 0.05, _ataque(ctx, fonte, b, a["fim"]) - GUARDA_ENERGIA)
            c0 = max(a["fim"] + PAUSA_RESTA / 2, lo_c)
            c1 = min(b["inicio"] - PAUSA_RESTA / 2, hi_c)
            if c1 - c0 < 2 / FPS:
                continue
            c0 = _snap(ctx, fonte, c0, lo_c, min(c0 + SNAP, c1 - 2 / FPS))
            c1 = _snap(ctx, fonte, c1, max(c1 - SNAP, c0 + 2 / FPS), hi_c)
            dentro(c0, c1, lo_c, hi_c)
    # silêncios que o ASR NÃO mostra como intervalo entre palavras (duração esticada: o "e" de 1,5 s da L13 do
    # 2026-09-16 tinha o silêncio DENTRO da palavra). Varre a energia do take e corta o que passar de PAUSA_INTERNA.
    if ws:
        tt, db = rms_wav(wav)
        ini_take, fim_take = ws[0]["inicio"], ws[-1]["fim"]
        alto = db > _limiar_energia(tt, db, ini_take, fim_take, nivel_ruido(wav))
        k0 = None
        for i, t in enumerate(tt):
            if t < ini_take or t > fim_take:
                continue
            if not alto[i]:
                k0 = i if k0 is None else k0
                continue
            if k0 is not None:
                a, b = float(tt[k0]), float(t)
                if b - a > PAUSA_INTERNA + 2 * GUARDA_ENERGIA:
                    dentro(a + PAUSA_RESTA / 2, b - PAUSA_RESTA / 2, a + GUARDA_ENERGIA, b - GUARDA_ENERGIA)
                k0 = None

    # fala da IA dentro de um silêncio entre duas palavras do take (flag `fala_ia_interna`): sai inteira
    for za, zb in ctx.zonas.get(fonte, []):
        for k in range(1, len(ws)):
            a, b = ws[k - 1], ws[k]
            if a["fim"] <= za and zb <= b["inicio"]:
                off_a = _cauda(ctx, fonte, a, za) + GUARDA_ENERGIA
                on_b = _ataque(ctx, fonte, b, zb) - GUARDA_ENERGIA
                c0 = max(a["fim"] + 0.03, min(max(za - MARGEM_IA_CORTE, off_a), za - 0.02))
                c1 = min(b["inicio"] - 0.03, max(min(zb + MARGEM_IA_CORTE, on_b), zb + 0.02))
                c0 = folga_silencio(wav, c0, a["fim"] + 0.03, za - 0.02, GUARDA_ENERGIA)
                c1 = folga_silencio(wav, c1, zb + 0.02, b["inicio"] - 0.03, GUARDA_ENERGIA)
                q0, q1 = _piso_frame(c0), _teto_frame(c1)
                c0 = q0 if q0 >= a["fim"] - 1e-6 else _teto_frame(c0)
                c1 = q1 if q1 <= b["inicio"] + 1e-6 else _piso_frame(c1)
                if c1 - c0 >= 2 / FPS - 1e-6:
                    cortes.append([c0, c1])
    cortes.sort()
    fund = []
    for c in cortes:
        if fund and c[0] <= fund[-1][1]:
            fund[-1][1] = max(fund[-1][1], c[1])
        else:
            fund.append(list(c))
    return [[round(a, 6), round(b, 6)] for a, b in fund]


# ---------------------------------------------------------------- segmentos
def sem_pecas_orfas(ctx: Ctx, fonte: str, a0: float, b0: float, cortes: list[list[float]],
                    ws: list[dict]) -> list[list[float]]:
    """Decisão de 01/10: corte interno NUNCA deixa peça de fala < MIN_PECA_S no meio do segmento — o
    `pecas_do_segmento` descarta essa peça (regra do "caco", 18/09) e a fala some sem aviso. Na Fei-Fei (17/10) os
    cortes automáticos apagavam "sem" (L01), "era" (L14, L25), "por que" (L12), "traduzir tudo" (L31)… Retira o corte
    vizinho que custa menos: primeiro o de PAUSA, depois o de muleta (o menor); o da fala da IA nunca sai."""
    zonas = ctx.zonas.get(fonte, [])
    fala = [(w["inicio"], w["fim"]) for w in ws if w.get("locutor") != "ia"]
    cortes = sorted([list(c) for c in cortes])

    def tipo(c):
        if any(za < c[1] and zb > c[0] for za, zb in zonas):
            return 2                                     # fala da IA: nunca retirar
        return 1 if any(wa < c[1] - 0.01 and wb > c[0] + 0.01 for wa, wb in fala) else 0   # muleta / pausa
    while len(cortes) >= 2:
        bordas = [a0] + [x for c in cortes for x in c] + [b0]
        partes = [(bordas[2 * k], bordas[2 * k + 1]) for k in range(len(cortes) + 1)]
        orfa = None
        for k in range(1, len(partes) - 1):
            pa, pb = partes[k]
            if pb - pa < MIN_PECA and any(wa < pb and wb > pa for wa, wb in fala):
                orfa = k
                break
        if orfa is None:
            break
        viz = [j for j in (orfa - 1, orfa) if tipo(cortes[j]) < 2]
        if not viz:
            break
        j = min(viz, key=lambda j: (tipo(cortes[j]), cortes[j][1] - cortes[j][0]))
        cortes.pop(j)
    return cortes


def segmento_auto(ctx: Ctx, linha_id: str, take_id: str | None, spec: dict | None = None) -> dict | None:
    """Valores automáticos de um segmento para (linha, take). Take fora do alinhamento => manual
    (usa fonte/in/out do spec)."""
    pausa = ctx.rot[linha_id].get("pausa_depois") or "normal"
    t = ctx.takes.get(take_id) if take_id else None
    if t is not None:
        fonte = t["fonte"]
        ini, out = pontos_in_out(ctx, fonte, t["i_ini"], t["i_fim"], pausa)
    elif spec and all(k in spec for k in ("fonte", "in", "out")):
        fonte, ini, out = spec["fonte"], float(spec["in"]), float(spec["out"])
    else:
        return None
    ws = palavras_no_intervalo(ctx, fonte, ini, out)
    _, muletas = analisar(ctx, linha_id, ws)
    _, refs, zoom = analisar_tela(ctx.rot[linha_id], ctx.decl_extras)
    split = any(r.get("modo") == "split" for r in refs)
    return {"linha": linha_id, "take": take_id or "manual", "fonte": fonte, "in": ini, "out": out,
            "cortes_internos": sem_pecas_orfas(ctx, fonte, ini, out, cortes_auto(ctx, fonte, ws, muletas), ws),
            "layout": "split" if split else "full", "zoom": zoom}


# ---------------------------------------------------------------- coluna TELA
# Itens separados por " · " (ou "|"): TEXTO: "..." · ZOOM [1.2] · tela-01 00:04–00:11 split ·
# ANIMACAO[split]: descrição · GESTO: ... · B-ROLL: ...   (cada item é lido independentemente)
RE_TEXTO = re.compile(r'^TEXTO\s*:\s*(?:[“"](.+)[”"]|(.+))$', re.I)
RE_ANIM = re.compile(r"^ANIMA[CÇ][AÃ]O\s*\[\s*(\w+)\s*\]\s*:?\s*(.*)$", re.I)
RE_ZOOM = re.compile(r"^ZOOM\b\s*(?:[x×]?\s*(\d+(?:[.,]\d+)?))?", re.I)
_TC = r"\d{1,2}:\d{2}(?:[.,]\d+)?"
RE_TELA = re.compile(rf"\b(tela-[a-z0-9_]+)\b(?:\s+({_TC})\s*[–—-]\s*({_TC}))?(?:\s+(full|split|card)\b)?", re.I)
RE_NOTA = re.compile(r"^(GESTO|B-?ROLL|VISUAL|NOTA|OBS)\b\s*:?", re.I)       # anotações: ignoradas
SEPARADORES_TELA = "·•|"


def itens_tela(tela: str) -> list[str]:
    """Divide a célula TELA nos separadores " · " / "|" — nunca dentro de aspas (TEXTO: "A · B")."""
    itens, buf, fecha = [], [], None
    for c in tela:
        if fecha:
            buf.append(c)
            if c == fecha:
                fecha = None
        elif c in '"“':
            fecha = '"' if c == '"' else "”"
            buf.append(c)
        elif c in SEPARADORES_TELA:
            itens.append("".join(buf))
            buf = []
        else:
            buf.append(c)
    itens.append("".join(buf))
    if fecha:                                   # aspas sem fechar: divide sem respeitar aspas
        itens = re.split(r"[·•|]", tela)
    return [x.strip() for x in itens if x.strip()]


def _mmss(s: str) -> float:
    m, sec = s.replace(",", ".").split(":")
    return int(m) * 60 + float(sec)


RE_EXTRA = re.compile(r"^EXTRA\s*:\s*([A-Za-z0-9_-]+)(.*)$", re.I)


def analisar_tela(linha: dict, decl: dict | None = None) -> tuple[list[dict], list[dict], dict | None]:
    """-> (textos, refs de cenas extras, zoom do segmento ou None).

    refs = [{"id", "modo", "in", "out", ...}] na ordem: `extras_ref` do roteiro.json, itens `EXTRA: E01 split
    [a–b]` da coluna TELA e os legados `tela-01 a–b modo` (id "tela-01") e `ANIMACAO[modo]: …` / campo
    `animacao` (id = id da linha; ignorado se a linha já usa um extra do tipo animacao). Um id por linha."""
    textos, refs, zoom, vistos, anim_legado = [], [], None, set(), []

    def add(r: dict) -> None:
        if r["id"] not in vistos:
            vistos.add(r["id"])
            refs.append(r)

    for r in linha.get("extras_ref") or []:
        if r.get("id"):
            add({"id": normalizar_id_extra(r["id"]), "modo": (r.get("modo") or "split").lower(),
                 "in": r.get("in"), "out": r.get("out")})
    for item in itens_tela(linha.get("tela") or ""):
        if RE_NOTA.match(item):
            continue
        m = RE_TEXTO.match(item)
        if m:
            texto = (m.group(1) or m.group(2) or "").strip().strip('"“”').strip()
            if texto:
                textos.append({"tipo": "texto", "texto": texto})
            continue
        m = RE_EXTRA.match(item)
        if m:
            modo = re.search(r"\b(split|full|card)\b", m.group(2), re.I)
            tc = re.search(rf"({_TC})\s*[–—-]\s*({_TC})", m.group(2))
            add({"id": normalizar_id_extra(m.group(1)), "modo": modo.group(1).lower() if modo else "split",
                 "in": _mmss(tc.group(1)) if tc else None, "out": _mmss(tc.group(2)) if tc else None})
            continue
        m = RE_ANIM.match(item)
        if m:
            anim_legado.append({"modo": m.group(1).lower(), "descricao": m.group(2).strip()})
            continue
        m = RE_ZOOM.match(item)
        if m:
            esc = float(m.group(1).replace(",", ".")) if m.group(1) else ZOOM_PUNCH["escala"]
            zoom = {"tipo": "punch", "escala": esc if 1.0 < esc <= 2.0 else ZOOM_PUNCH["escala"]}
            continue
        m = RE_TELA.search(item)
        if m:
            add({"id": m.group(1).lower(), "modo": (m.group(4) or "split").lower(), "tipo": "tela",
                 "in": _mmss(m.group(2)) if m.group(2) else None, "out": _mmss(m.group(3)) if m.group(3) else None})
    if linha.get("animacao"):
        a = linha["animacao"]
        anim_legado = [{"modo": a.get("modo") or "full", "descricao": a.get("descricao") or ""}]
    tem_anim = any(((decl or {}).get(r["id"]) or {}).get("tipo") == "animacao" for r in refs)
    if anim_legado and not tem_anim:
        a = anim_legado[0]
        add({"id": linha["id"], "modo": a["modo"], "in": None, "out": None, "tipo": "animacao",
             "descricao": a["descricao"]})
    return textos, refs, zoom


def finalizar_extra(ctx: "Ctx", ov: dict) -> dict:
    """Overlay `tipo: extra` final (contrato §4): arquivo, in/out (segura o último quadro se o extra acabar
    antes), som, crédito, componente (animação) e `faltando`."""
    eid, ref = ov["extra"], ov["_ref"]
    decl = ctx.decl_extras.get(eid) or {}
    info = ctx.extras.get(eid) or {}
    tipo = decl.get("tipo") or info.get("tipo") or ref.get("tipo") or "video"
    span = round(ov["saida_fim"] - ov["saida_inicio"], 3)
    avisos: list[str] = []
    arq = info.get("arquivo")
    if arq and tipo == "camera":
        cor = str(Path(arq).with_name(f"{eid}-cor.mp4"))
        if (ctx.vd / cor).exists():
            arq = cor
        else:
            avisos.append(f"câmera em V-Log ainda sem cor ({eid}-cor.mp4): no Remotion vai com a LUT de visualização")
    existe = bool(arq) and (ctx.vd / arq).exists()
    componente = None
    if tipo == "animacao" and not existe:
        componente = resolver_componente(ctx.slug, eid, ctx.registrados)
        faltando = componente is None
        if faltando:
            avisos.append(f"sem componente no registry do Remotion ('{ctx.slug}/{eid}' ou '{eid}')")
    else:
        faltando = not existe
        if faltando:
            avisos.append(f"sem arquivo: pôr em brutos/extras/{eid}-… e rodar ingest.py + edl.py --recalcular")
    o = {"linhas": list(ov["linhas"]), "tipo": "extra", "extra": eid, "extra_tipo": tipo,
         "arquivo": arq if existe else None, "modo": ov["modo"]}
    eh_imagem = bool(arq) and Path(arq).suffix.lower() == ".png"
    if tipo != "animacao" and not eh_imagem and (existe or tipo in ("tela", "video", "camera")):
        ini = float(ov["_in"] or 0.0)
        fim = ini + span
        oe = ov.get("_out_expl")
        if oe is not None:
            if float(oe) - ini > span + FRAME:
                avisos.append(f"trecho {fmt_t(ini)}–{fmt_t(oe)} maior que a fala ({span:.2f}s): para em {fmt_t(ini + span)}")
            fim = min(float(oe), fim)
        d = info.get("duracao") if existe else None
        if d:
            if ini >= d:
                avisos.append(f"in {ini:.2f}s depois do fim do extra ({d:.2f}s)")
                ini = max(0.0, d - FRAME)
            fim = min(fim, float(d))
        if existe and span - (fim - ini) > FRAME:
            # 2026-09-19: segurar o último quadro é ruim de ver e, num Reel de citação, infla o tempo de
            # material de terceiros na tela (no Hassabis: 29,9 s de clipes ocupavam 51,3 s = 81% do Reel).
            # O extra sai quando o clipe acaba e o Carlos volta a ocupar o quadro inteiro.
            sobra = span - (fim - ini)
            ov["saida_fim"] = round(ov["saida_inicio"] + (fim - ini), 3)
            avisos.append(f"extra ({fim - ini:.2f}s) mais curto que a fala: sai {sobra:.2f}s antes, "
                          f"em vez de segurar o último quadro")
        o["in"], o["out"] = round(ini, 3), round(max(fim, ini + FRAME), 3)
    o["som"] = bool(decl.get("som"))
    o["credito"] = decl.get("credito") or None
    if tipo == "animacao":
        o["componente"] = componente or eid
    desc = decl.get("descricao") or ref.get("descricao")
    if desc:
        o["descricao"] = desc
    o["faltando"] = bool(faltando)
    o["saida_inicio"], o["saida_fim"] = ov["saida_inicio"], ov["saida_fim"]
    ctx.avisos_extras.append((eid, o["saida_inicio"], avisos))
    return o


def montar(ctx: Ctx, specs: list[dict], snapshot: dict | None, recalc: bool):
    """-> (segmentos, novo_snapshot)"""
    ordem = {lid: k for k, lid in enumerate(ctx.ordem)}
    specs = sorted(enumerate(specs), key=lambda kv: (ordem.get(kv[1]["linha"], 999), kv[0]))
    segs, snap_novo = [], {}
    for _, spec in specs:
        lid = spec["linha"]
        if lid not in ctx.rot:
            log(f"   [AVISO] linha {lid} não existe no roteiro — segmento ignorado")
            continue
        take = spec.get("take")
        if take and take != "manual" and not take.startswith(lid + "-") and re.fullmatch(r"T\d+", take):
            take = f"{lid}-{take}"                 # "T1" -> "L05-T1"
        auto = segmento_auto(ctx, lid, take if take in ctx.takes else None, spec)
        if auto is None:
            log(f"   [AVISO] {lid}: take '{take}' não existe no alinhamento e não há fonte/in/out — ignorado")
            continue
        chave = f"{lid}|{auto['take']}"
        if auto["take"] == "manual":
            # 2026-10-15: linha dividida entre dois arquivos da câmera = dois segmentos manuais da MESMA linha;
            # sem a fonte na chave um sobrescrevia o snapshot do outro e o zoom fixado à mão se perdia
            chave += f"|{auto['fonte']}"
        snap_novo[chave] = {k: auto[k] for k in CAMPOS_EDITAVEIS}
        seg = dict(auto)
        seg["_chave"] = chave
        if recalc and snapshot is not None:
            antigo = snapshot.get(chave)
            if antigo is not None:                 # mesmo take: preserva o que foi editado à mão
                for k in CAMPOS_EDITAVEIS:
                    if k in spec and spec[k] != antigo.get(k):
                        seg[k] = spec[k]
                for k in CAMPOS_ZOOM:              # plano de zoom: editado à mão = difere do automático anterior
                    if spec.get(k) is not None and k in antigo and spec[k] != antigo[k]:
                        seg["_manual_" + k] = spec[k]
            elif auto["take"] == "manual":
                for k in CAMPOS_EDITAVEIS:
                    if k in spec:
                        seg[k] = spec[k]
                for k in CAMPOS_ZOOM:
                    if spec.get(k) is not None:
                        seg["_manual_" + k] = spec[k]
            # take trocado: in/out/cortes antigos pertenciam ao take anterior -> recalculados
        segs.append(seg)
    return segs, snap_novo


# ---------------------------------------------------------------- enquadramento (zoom por peça)
def eh_camera(ctx: Ctx, fonte: str) -> bool:
    """Peças que recebem punch-in: câmera/celular (rosto). Gravação de tela no principal nunca."""
    return ((ctx.fontes.get(fonte) or {}).get("tipo") or tipo_da_fonte(fonte)) in ("camera", "celular")


def rosto(ctx: Ctx, fonte: str, tempos: list[float]) -> tuple[float, float, int, int] | None:
    """Centro do rosto (0–1 do quadro) por Haar frontal (OpenCV) em alguns quadros do intermediário -> mediana.
    -> (x, y, quadros com rosto, quadros) ou None (sem OpenCV / sem rosto na maioria dos quadros)."""
    chave = (fonte, tuple(round(t, 2) for t in tempos))
    if chave in ctx.rostos:
        return ctx.rostos[chave]
    try:
        import cv2
        import numpy as np
    except ImportError:
        avisar_uma_vez("OpenCV (opencv-python-headless) não instalado: zoom com origem padrão " + ZOOM_ORIGEM)
        return None
    arq = ctx.vd / ctx.fontes[fonte]["arquivo"]
    if not hasattr(ctx, "_haar"):
        ctx._haar = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    W, H = 360, 640
    achados = []
    for t in tempos:
        r = run([FFMPEG, "-hide_banner", "-nostdin", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", str(arq),
                 "-frames:v", "1", "-vf", f"scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"], check=False)
        if r.returncode or len(r.stdout) < W * H:
            continue
        g = cv2.equalizeHist(np.frombuffer(r.stdout, np.uint8)[:W * H].reshape(H, W))
        fs = ctx._haar.detectMultiScale(g, scaleFactor=1.1, minNeighbors=5, minSize=(int(0.12 * W), int(0.12 * W)))
        if len(fs):
            x, y, w, h = max(fs, key=lambda f: f[2] * f[3])
            achados.append(((x + w / 2) / W, (y + h / 2) / H))
    res = None
    if len(achados) >= max(1, (len(tempos) + 1) // 2):
        res = (statistics.median(a[0] for a in achados), statistics.median(a[1] for a in achados),
               len(achados), len(tempos))
    elif tempos:
        res = (None, None, len(achados), len(tempos))
    ctx.rostos[chave] = res
    return res


def origem_auto(ctx: Ctx, s: dict) -> str:
    """Origem do zoom do segmento = centro do rosto (limitado ao miolo do quadro); sem rosto -> ZOOM_ORIGEM."""
    ps = pecas_do_segmento(s)
    tempos = [(a + b) / 2 for a, b in ps]
    if ps and len(tempos) < 3:
        a, b = max(ps, key=lambda p: p[1] - p[0])
        tempos += [a + 0.25 * (b - a), a + 0.75 * (b - a)]
    r = rosto(ctx, s["fonte"], sorted(tempos)[:5]) if tempos else None
    if r and r[0] is not None:
        ctx.info_rosto[id(s)] = f"rosto {r[2]}/{r[3]}"
        return fmt_origem(min(0.7, max(0.3, r[0])), min(0.55, max(0.25, r[1])))
    ctx.info_rosto[id(s)] = f"padrão (rosto {r[2]}/{r[3]})" if r else "padrão"
    return ZOOM_ORIGEM


def alternar(itens: list[dict]) -> list[float]:
    """Escala de cada peça (ordem de saída). Peças de câmera seguidas ALTERNAM 1.00 ↔ E; peças `fixo` (TELA `ZOOM`
    = começa fechado, ou plano editado à mão) são respeitadas e o resto se adapta em volta. Se a alternância pura
    bate numa peça fixa igual, a última livre antes dela fica no meio-termo ((1 + E)/2)."""
    res: list[float] = [1.0] * len(itens)
    ant: float | None = None
    segurado = 0.0      # há quanto tempo o enquadramento atual está no ar
    for i, it in enumerate(itens):
        if not it["cam"]:
            ant = None
            segurado = 0.0
            continue
        if it.get("continua") and ant is not None:    # divisão do arquivo da câmera: não é corte
            res[i] = ant
            segurado += it.get("dur", 0.0)
            continue
        if it["fixo"] is not None:
            res[i] = float(it["fixo"])
            segurado = it.get("dur", 0.0) if abs(res[i] - (ant if ant is not None else -9)) >= ZOOM_DIF_MIN \
                else segurado + it.get("dur", 0.0)
            ant = res[i]
            continue
        # o enquadramento tem de segurar: trocar antes disso vira o zoom que "vai e volta" (2026-09-18)
        if ant is not None and segurado < ZOOM_SEGURA_MIN:
            res[i] = ant
            segurado += it.get("dur", 0.0)
            continue
        v = 1.0 if (ant is None or ant > 1.0 + ZOOM_DIF_MIN / 2) else it["E"]
        prox = itens[i + 1] if i + 1 < len(itens) else None
        if prox and prox["cam"] and prox["fixo"] is not None and abs(float(prox["fixo"]) - v) < ZOOM_DIF_MIN:
            outros = [x for x in (ant, float(prox["fixo"])) if x is not None]
            v = round((1.0 + it["E"]) / 2, 3)
            if any(abs(v - x) < ZOOM_DIF_MIN for x in outros):
                v = 1.0 if all(abs(1.0 - x) >= ZOOM_DIF_MIN for x in outros) else it["E"]
        res[i] = v
        segurado = it.get("dur", 0.0) if (ant is None or abs(v - ant) >= ZOOM_DIF_MIN) else segurado + it.get("dur", 0.0)
        ant = v
    return res


FALA_DB = -40.0        # acima disto a borda está em cima de fala
SILENCIO_DB = -45.0    # abaixo disto é silêncio seguro para cortar
BUSCA_MAX = 1.5        # s que se anda à procura de silêncio


def _envelope(vd: Path, fonte: str, _cache: dict = {}) -> "list[float] | None":
    """Nível por 10 ms do master de áudio da fonte (dBFS), para achar silêncio."""
    chave = (str(vd), fonte)
    if chave not in _cache:
        wav = wav48k_path(vd, fonte)
        if not wav.exists():
            _cache[chave] = None
        else:
            import numpy as np                                    # noqa: PLC0415
            r = run([FFMPEG, "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000",
                     "-af", "highpass=f=80", "-f", "f32le", "-"])
            x = np.frombuffer(r.stdout, np.float32)
            h = 160
            n = len(x) // h
            e = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-12)
            _cache[chave] = np.convolve(e, np.ones(3) / 3, mode="same")
    return _cache[chave]


def assentar_bordas(vd: Path, segs: list[dict]) -> None:
    """Nenhuma borda de corte em cima de fala — medido no ÁUDIO, não nas marcas do ASR (2026-09-19).

    O ASR erra até 0,18 s: uma entrada caía 0,02 s depois do início de "2016" e cortava o "2", e segmentos
    acabavam colados na última palavra, cortando a cauda ("ele cortou a palavra"). Aqui cada `in`/`out`/corte
    interno é empurrado para o silêncio mais próximo. Roda sempre, inclusive no --recalcular.
    """
    def db(e, t):
        k = int(t / 0.01)
        return float(e[k]) if 0 <= k < len(e) else -99.0

    mudou = 0
    for s in segs:
        e = _envelope(vd, s["fonte"])
        if e is None:
            continue
        if db(e, s["in"]) > FALA_DB:                              # entrada dentro de uma palavra: recua
            t = s["in"]
            while t > 0.05 and db(e, t) > SILENCIO_DB and s["in"] - t < BUSCA_MAX:
                t -= 0.01
            s["in"] = round(max(0.0, t - 0.10), 3)
            mudou += 1
        if db(e, s["out"]) > FALA_DB:                             # saída colada na palavra: alonga a cauda
            t = s["out"]
            while db(e, t) > SILENCIO_DB and t - s["out"] < BUSCA_MAX:
                t += 0.01
            # nunca além do fim da fonte (2026-10-14: gravação dividida pela câmera — a linha atravessa dois
            # arquivos e o `out` cai no último quadro; esticar passava 0,11 s do fim e desalinhava A/V)
            s["out"] = round(min(t + 0.10, len(e) * 0.01), 3)
            mudou += 1
        novos = []
        for a, b in (s.get("cortes_internos") or []):
            while db(e, b) > -35.0 and b > a + 0.05:
                b = round(b - 0.01, 3)
            while db(e, a) > -35.0 and a < b - 0.05:
                a = round(a + 0.01, 3)
            if b - a >= 0.10:
                novos.append([a, b])
        if novos != (s.get("cortes_internos") or []):
            mudou += 1
        s["cortes_internos"] = novos
    if mudou:
        log(f"   bordas assentadas no silêncio: {mudou} ajuste(s) (medido no áudio, não no ASR)")


def continuacao_de_arquivo(ctx: Ctx, a: dict, b: dict) -> bool:
    """2026-10-17 (Fei-Fei L26): a câmera divide a gravação em arquivos de ~82 s e a linha atravessa a divisão
    (`out` = fim do arquivo, o segmento seguinte da MESMA linha começa no 0 do próximo). Isso não é corte: a 2.ª
    parte herda escala e origem da peça anterior — senão o zoom pulava no meio da palavra ("artifici|al")."""
    if a["linha"] != b["linha"] or a["fonte"] == b["fonte"] or not (eh_camera(ctx, a["fonte"]) and eh_camera(ctx, b["fonte"])):
        return False
    if a.get("cortes_internos") and max(c[1] for c in a["cortes_internos"]) >= float(a["out"]) - 1e-6:
        return False
    try:
        dur_a = ctx.dur(a["fonte"])
    except Exception:
        return False
    return abs(float(a["out"]) - dur_a) <= 2 * FRAME and float(b["in"]) <= 2 * FRAME


def planejar_zoom(ctx: Ctx, segs: list[dict], snap: dict) -> None:
    """Plano de enquadramento: `zoom_origem` (rosto) e `zoom_pecas` (escala de cada peça) em cada segmento.
    Respeita o que foi editado à mão (difere do automático anterior, no edl.auto.json)."""
    def continua(si: int) -> bool:
        return si > 0 and continuacao_de_arquivo(ctx, segs[si - 1], segs[si])

    def itens(com_manual: bool) -> tuple[list[dict], list[tuple[int, int]]]:
        its, idx = [], []
        for si, s in enumerate(segs):
            pcs = pecas_do_segmento(s)
            n = len(pcs)
            cam = eh_camera(ctx, s["fonte"])
            z = s.get("zoom") or {}
            punch = z.get("tipo") == "punch"
            E = min(ZOOM_MAX, max(1.0 + 2 * ZOOM_DIF_MIN, float(z.get("escala") or ZOOM_ESCALA))) if punch else ZOOM_ESCALA
            man = s.get("_manual_zoom_pecas") if com_manual else None
            if man is not None and (not isinstance(man, list) or len(man) != n):
                log(f"   [AVISO] {s['linha']}: zoom_pecas editado tem {len(man) if isinstance(man, list) else '?'} "
                    f"valor(es), mas o segmento tem {n} peça(s) — plano automático")
                man = None
            idx.append((len(its), n))
            for k in range(n):
                fixo = float(man[k]) if man is not None else (E if punch and k == 0 else None)
                if fixo is not None:
                    fixo = min(ZOOM_MAX, max(1.0, fixo))
                its.append({"cam": cam, "E": E, "fixo": fixo if cam else None,
                            "continua": k == 0 and man is None and continua(si),
                            "dur": (pcs[k][1] - pcs[k][0]) if k < len(pcs) else 0.0})
        return its, idx

    its_auto, idx = itens(False)
    auto = alternar(its_auto)
    its_final, _ = itens(True)
    final = alternar(its_final)
    for s, (i0, n) in zip(segs, idx):
        cam = eh_camera(ctx, s["fonte"])
        origem = origem_auto(ctx, s) if cam else None
        cand = [round(x, 3) for x in auto[i0:i0 + n]]
        if s.get("_chave") in snap:
            snap[s["_chave"]]["zoom_pecas"] = cand
            snap[s["_chave"]]["zoom_origem"] = origem
        s["zoom_pecas"] = [round(x, 3) for x in final[i0:i0 + n]]
        mo = s.get("_manual_zoom_origem")
        s["zoom_origem"] = mo if (mo and cam) else origem
    for si, s in enumerate(segs):
        if continua(si) and not s.get("_manual_zoom_origem"):
            s["zoom_origem"] = segs[si - 1].get("zoom_origem")
    # consecutivas iguais (só com edição à mão): avisa — a divisão de arquivo da câmera não é corte
    flat = [(s["linha"], e, k == 0 and continua(si)) for si, s in enumerate(segs) if eh_camera(ctx, s["fonte"])
            for k, e in enumerate(s["zoom_pecas"])]
    iguais = [f"{a[0]}→{b[0]}" for a, b in zip(flat, flat[1:]) if abs(a[1] - b[1]) < ZOOM_DIF_MIN and not b[2]]
    if iguais:
        log(f"   [AVISO] corte(s) sem troca de enquadramento (zoom editado à mão): {', '.join(iguais)}")


def derivar(ctx: Ctx, segs: list[dict]):
    """Calcula saida_inicio/fim, palavras_saida, overlays e duração."""
    t = 0.0
    palavras_saida, finais, textos_ov, extras_ov = [], [], [], []
    abertos: dict[str, dict] = {}       # extras presentes no segmento anterior (para juntar linhas seguidas)
    ctx.avisos_extras = []
    for n, s in enumerate(segs, start=1):
        pecas = pecas_do_segmento(s)
        ini_seg = t
        mapa = []                                   # (a, b, saida)
        for a, b in pecas:
            mapa.append((a, b, t))
            t += b - a
        lid = s["linha"]
        seg = {"n": n, "linha": lid, "take": s["take"], "fonte": s["fonte"], "in": s["in"], "out": s["out"],
               "cortes_internos": s.get("cortes_internos") or [], "saida_inicio": round(ini_seg, 3),
               "saida_fim": round(t, 3), "layout": s.get("layout") or "full", "zoom": s.get("zoom"),
               "zoom_origem": s.get("zoom_origem"), "zoom_pecas": s.get("zoom_pecas") or [1.0] * len(pecas),
               "voz_ia": voz_ia_nas_pecas(ctx, s["fonte"], pecas)}
        if s.get("_chave"):
            ctx.info_rosto[n] = ctx.info_rosto.pop(id(s), "")
        if seg["voz_ia"] > 0:
            log(f"   [AVISO] {lid} ({s['take']}): {seg['voz_ia']:.2f}s de voz da IA dentro do segmento "
                "(in/out/cortes editados à mão ou take com sobreposicao_ia) — confira no preview")
        finais.append(seg)

        def para_saida(x):
            for a, b, o in mapa:
                if a - 1e-6 <= x <= b + 1e-6:
                    return o + (x - a)
            return None

        ws = palavras_no_intervalo(ctx, s["fonte"], s["in"], s["out"])
        unidades, _ = analisar(ctx, lid, ws)
        porid = {w["i"]: w for w in ws}
        lr = ctx.lrot[lid]
        dest = destaques_por_posicao(ctx.rot[lid])
        # LEGENDA = O ROTEIRO (pedido do Carlos, 2026-09-16: "a legenda deve ser corrigida pelo roteiro, não pelo
        # que estou falando" — ele come sílabas e o ASR escreve "pronte" em vez de "PROMPT"). Os tempos vêm da
        # fala; as palavras do roteiro que ele comeu recebem tempo interpolado; o que o ASR inventou é descartado.
        #
        # EXCEÇÃO — IMPROVISO DE VERDADE (2026-09-17). Só quando ele REESCREVEU a frase: aí a legenda segue a
        # FALA, porque o texto do roteiro contradiria o que se ouve.
        # NÃO basta o status `parafrase`: ele marca tudo abaixo de sim 0,80, e as linhas dele caem nessa faixa
        # só por comer o fim das palavras (no 1.º vídeo real: L01 sim 0,64, L02 0,78, L06 0,75 — todas ditas
        # como no roteiro). Usar `parafrase` fez a legenda da L01 virar "Para depender post parou", que é
        # exatamente o erro que ele mandou corrigir. Por isso o corte é bem mais baixo: reescrita de verdade.
        SIM_IMPROVISO = 0.55
        _al = ctx.al_linha.get(lid) or {}
        _sim = next((t.get("sim") for t in _al.get("takes", []) if t.get("take_id") == _al.get("escolhido")), None)
        improviso = _al.get("status") == "parafrase" and _sim is not None and _sim < SIM_IMPROVISO
        tempos: dict[int, list[float]] = {}
        asr_solto: list[dict] = []
        for u in unidades:
            w0, w1 = porid.get(u["wi"]), porid.get(u["wf"])
            if not w0 or not w1:
                continue
            # A palavra pode ATRAVESSAR um corte interno (o silêncio dentro de uma palavra esticada pelo ASR: o
            # "e" de 1,5 s do CTA). Só se descarta quando NADA dela sobra; senão usa-se a parte que ficou.
            ini_w, fim_w = max(w0["inicio"], s["in"]), min(w1["fim"], s["out"])
            partes = [(max(a0, ini_w), min(b0, fim_w), o) for a0, b0, o in mapa
                      if min(b0, fim_w) - max(a0, ini_w) > 1e-3]
            if not partes:
                continue                            # inteira dentro de um corte (muleta)
            a = partes[0][2] + (partes[0][0] - [m for m in mapa if m[2] == partes[0][2]][0][0])
            ultima = partes[-1]
            b = ultima[2] + (ultima[1] - [m for m in mapa if m[2] == ultima[2]][0][0])
            if u["js"]:
                for j in u["js"]:
                    tj = tempos.setdefault(j, [a, b])
                    tj[0], tj[1] = min(tj[0], a), max(tj[1], b)
            else:
                asr_solto.append({"texto": " ".join(porid[i]["texto"] for i in range(u["wi"], u["wf"] + 1)
                                                    if i in porid), "inicio": a, "fim": b})

        if tempos and not improviso:                 # a linha foi reconhecida: legenda inteira pelo roteiro
            js = list(range(len(lr.palavras)))
            conhecidos = sorted(tempos)
            ini_l = tempos[conhecidos[0]][0]
            fim_l = tempos[conhecidos[-1]][1]
            for j in js:
                if j in tempos:
                    a, b = tempos[j]
                else:                                # palavra comida/mal dita: tempo entre as vizinhas casadas
                    ant_j = max((k for k in conhecidos if k < j), default=None)
                    prox_j = min((k for k in conhecidos if k > j), default=None)
                    a0 = tempos[ant_j][1] if ant_j is not None else max(ini_seg, ini_l - 0.30)
                    b0 = tempos[prox_j][0] if prox_j is not None else min(seg["saida_fim"], fim_l + 0.30)
                    faltam = [k for k in js if k not in tempos
                              and (ant_j is None or k > ant_j) and (prox_j is None or k < prox_j)]
                    quantas = max(1, len(faltam))
                    pos = faltam.index(j)
                    passo = max(0.06, (b0 - a0) / quantas)
                    a, b = a0 + pos * passo, min(b0, a0 + (pos + 1) * passo)
                palavras_saida.append({"texto": lr.palavras[j], "inicio": round(a, 3),
                                       "fim": round(max(b, a + 0.06), 3), "linha": lid,
                                       "destaque": bool(j < len(dest) and dest[j])})
        elif improviso:                              # ele reescreveu a linha: a legenda acompanha a fala dele
            for i in sorted(porid):
                w = porid[i]
                a, b = para_saida(w["inicio"]), para_saida(w["fim"])
                if a is None or b is None:
                    continue
                palavras_saida.append({"texto": w["texto"], "inicio": round(a, 3),
                                       "fim": round(max(b, a + 0.06), 3), "linha": lid, "destaque": False})
        else:                                        # nada casou: mantém o que foi dito
            for x in asr_solto:
                palavras_saida.append({"texto": x["texto"], "inicio": round(x["inicio"], 3),
                                       "fim": round(max(x["fim"], x["inicio"] + 0.02), 3),
                                       "linha": lid, "destaque": False})
        textos, refs, _ = analisar_tela(ctx.rot[lid], ctx.decl_extras)
        for o in textos:
            textos_ov.append({"linha": lid, "tipo": "texto", "texto": o["texto"],
                              "saida_inicio": seg["saida_inicio"], "saida_fim": seg["saida_fim"]})
        novos = {}
        for r in refs:
            ab = abertos.get(r["id"])
            # mesmo extra, mesmo modo, segmento colado e (se houver trecho explícito) trecho contínuo -> 1 overlay
            continua = (ab is not None and ab["modo"] == r["modo"]
                        and abs(ab["saida_fim"] - seg["saida_inicio"]) < 1e-3
                        and (r.get("in") is None or ab["_out_expl"] is None
                             or abs(float(r["in"]) - float(ab["_out_expl"])) <= 0.05))
            if continua:
                ab["saida_fim"] = seg["saida_fim"]
                if lid not in ab["linhas"]:
                    ab["linhas"].append(lid)
                if r.get("out") is not None:
                    ab["_out_expl"] = r["out"]
            else:
                ab = {"linhas": [lid], "extra": r["id"], "modo": r["modo"], "_in": r.get("in"),
                      "_out_expl": r.get("out"), "_ref": r,
                      "saida_inicio": seg["saida_inicio"], "saida_fim": seg["saida_fim"]}
                extras_ov.append(ab)
            novos[r["id"]] = ab
        abertos = novos
    # extras primeiro, textos por cima (ordem = camadas no Remotion)
    overlays = [finalizar_extra(ctx, ov) for ov in extras_ov] + textos_ov
    return finais, overlays, palavras_saida, round(t, 3)


def variantes(ctx: Ctx) -> list[dict]:
    out = []
    for l in ctx.al["linhas"]:
        if l.get("alternativa_de") and l.get("escolhido"):
            s = segmento_auto(ctx, l["id"], l["escolhido"])
            if s:
                out.append({"linha": l["id"], "alternativa_de": l["alternativa_de"], "take": s["take"],
                            "fonte": s["fonte"], "in": s["in"], "out": s["out"],
                            "cortes_internos": s["cortes_internos"], "status": l["status"]})
    return out


# ---------------------------------------------------------------- edl.md
def escrever_md(ctx: Ctx, edl: dict, path: Path) -> None:
    r = ctx.al["resumo"]
    alvo = ctx.roteiro.get("duracao_alvo")
    L = [f"# EDL — {edl['slug']} (versão {edl['versao']})", "",
         "> **Como aprovar:** assista `edicao/preview.mp4` e revise a tabela. Para aprovar, diga ao agente",
         "> **\"aprovado\"** — ou edite `edicao/edl.json` e troque `\"aprovado\": false` por `\"aprovado\": true`.",
         "> **Trocar take:** diga, por exemplo, \"L05 usa T1\" (o agente muda `segmentos[].take` e roda `edl.py --recalcular`).",
         "> **Ajuste fino:** edite `in` / `out` / `cortes_internos` no `edl.json` e rode `edl.py --recalcular`.",
         "",
         f"**Estado:** {'APROVADA' if edl['aprovado'] else 'NÃO APROVADA'} · **Duração do corte:** "
         f"{edl['duracao_saida']:.1f} s" + (f" (alvo {alvo} s)" if alvo else "") +
         f" · **Linhas:** {r['ok']} ok, {r['revisar']} revisar, {r['parafrase']} paráfrase, {r['faltando']} faltando"]
    loc = ctx.loc or {}
    if loc.get("n_locutores") == 2:
        st, pp = loc.get("estatisticas") or {}, loc.get("papel") or {}
        L.append("")
        L.append(f"**Locutores (método ChatGPT-monitor):** {loc.get('metodo')} · IA = classe {pp.get('ia')} "
                 f"(confiança {pp.get('confianca')}) · IA {st.get('segundos_ia', 0):.1f} s · Carlos "
                 f"{st.get('segundos_carlos', 0):.1f} s · {r.get('leituras_ia', 0)} leitura(s) da IA e "
                 f"{r.get('fala_ia', 0)} fala(s) de monitor fora do corte · sobreposições {st.get('sobreposicoes', 0)}"
                 + (f" · **{st['palavras_incertas']} palavra(s) com locutor incerto**" if st.get("palavras_incertas") else "")
                 + " · a coluna **IA · Carlos** = leituras da IA · takes do Carlos da linha")
    L += ["", "| # | Linha | Status | Take | Fonte · in → out | Saída | Texto no corte | Alternativas | IA · Carlos |",
          "|---|---|---|---|---|---|---|---|---|"]
    segs_por_linha = {}
    for s in edl["segmentos"]:
        segs_por_linha.setdefault(s["linha"], []).append(s)
    for lid in ctx.ordem:
        rl = ctx.rot[lid]
        if rl.get("alternativa_de"):
            continue
        al = ctx.al_linha.get(lid, {"status": "faltando", "takes": [], "escolhido": None, "motivo": ""})
        alts = [f"{t['take_id'].split('-')[-1]} ({t['sim']:.2f}{'; ' + ', '.join(t['flags']) if t['flags'] else ''})"
                for t in al["takes"]]
        segs = segs_por_linha.get(lid, [])
        ic = f"{len(al.get('leituras_ia') or [])} · {len(al['takes'])}"
        if not segs:
            L.append(f"| – | {lid} | {MARCA[al['status']] if al['status'] == 'faltando' else '[FORA]'} | — | — | — | "
                     f"_{rl['fala']}_ | {' · '.join(alts) or '—'} | {ic} |")
            continue
        for s in segs:
            t = ctx.takes.get(s["take"])
            manual = s["take"] != al.get("escolhido")
            status = MARCA["manual"] if manual else MARCA[al["status"]]
            # 2026-10-17: o texto mostrado é o que está NAS PEÇAS (in/out e cortes editados à mão mudam a fala)
            pcs = pecas_do_segmento(s)
            ws_seg = [w for w in palavras_no_intervalo(ctx, s["fonte"], s["in"], s["out"]) if w.get("locutor") != "ia"
                      and sum(max(0.0, min(b, w["fim"]) - max(a, w["inicio"])) for a, b in pcs) >= 0.5 * (w["fim"] - w["inicio"])]
            texto = " ".join(w["texto"] for w in ws_seg) or (t["texto"] if t else "")
            cortes = f" ✂{len(s['cortes_internos'])}" if s["cortes_internos"] else ""
            aviso_ia = f" ⚠ **{s['voz_ia']:.2f} s de voz da IA**" if s.get("voz_ia") else ""
            L.append(f"| {s['n']} | {lid} | {status}{aviso_ia} | {s['take'].split('-')[-1]} | {s['fonte']} · "
                     f"{fmt_t(s['in'])} → {fmt_t(s['out'])}{cortes} | {fmt_t(s['saida_inicio'])}–{fmt_t(s['saida_fim'])}"
                     f" | {texto} | "
                     f"{' · '.join(a for a in alts if not a.startswith(s['take'].split('-')[-1] + ' ')) or '—'} | {ic} |")
    L += ["", "## Motivos e cortes internos", ""]
    for lid in ctx.ordem:
        al = ctx.al_linha.get(lid)
        if not al:
            continue
        extra = ""
        for s in segs_por_linha.get(lid, []):
            if s["cortes_internos"]:
                extra = " · cortes internos: " + ", ".join(f"{fmt_t(a)}–{fmt_t(b)}" for a, b in s["cortes_internos"])
        alt = f" (hook alternativo de {al['alternativa_de']})" if al.get("alternativa_de") else ""
        L.append(f"- **{lid}** {MARCA[al['status']]}{alt}: {al['motivo']}{extra}")
    L += ["", "## Fora do corte", ""]
    # 2026-10-17: trecho não mapeado que um segmento manual / in-out estendido pôs no corte não está "fora do corte"
    no_corte = set()
    for s in edl["segmentos"]:
        pcs = pecas_do_segmento(s)
        for w in palavras_no_intervalo(ctx, s["fonte"], s["in"], s["out"]):
            if sum(max(0.0, min(b, w["fim"]) - max(a, w["inicio"])) for a, b in pcs) >= 0.5 * (w["fim"] - w["inicio"]):
                no_corte.add(w["i"])
    pal = {w["i"]: w for w in ctx.tr["palavras"]} if getattr(ctx, "tr", None) else {}
    nm = [g for g in ctx.al["nao_mapeado"] if not g.get("so_muletas")]
    for g in nm:
        idx = range(g.get("i_ini", -1), g.get("i_fim", -2) + 1)
        fora = [i for i in idx if i not in no_corte]
        if pal and idx and not fora:
            continue
        txt = " ".join(pal[i]["texto"] for i in fora) if (pal and len(fora) < len(idx)) else g["texto"]
        L.append(f"- Não mapeado ({g['fonte']} {fmt_t(g['inicio'])}–{fmt_t(g['fim'])}): \"{txt}\"")
    for sp in ctx.al.get("separadores", []):
        L.append(f"- Separador descartado ({sp['fonte']} {fmt_t(sp['inicio'])}): \"{sp['texto']}\"")
    so_m = [g for g in ctx.al["nao_mapeado"] if g.get("so_muletas")]
    if so_m:
        L.append(f"- {len(so_m)} trecho(s) só de muletas entre takes (descartados)")
    fia = ctx.al.get("fala_ia") or []
    for g in fia:
        L.append(f"- Fala da IA — monitor ({g['fonte']} {fmt_t(g['inicio'])}): \"{g['texto']}\"")
    n_leit = sum(len(l.get("leituras_ia") or []) for l in ctx.al["linhas"])
    if n_leit:
        L.append(f"- {n_leit} leitura(s) das linhas pela IA (nunca entram no corte; ver `leituras_ia` no alinhamento.json)")
    if not nm and not ctx.al.get("separadores") and not so_m and not fia and not n_leit:
        L.append("- nada")
    if edl.get("variantes"):
        L += ["", "## Hooks alternativos (variantes, fora da montagem principal)", ""]
        for v in edl["variantes"]:
            L.append(f"- {v['linha']} (alt. de {v['alternativa_de']}): {v['take']} · {v['fonte']} "
                     f"{fmt_t(v['in'])} → {fmt_t(v['out'])} [{v['status']}]")
    ex = [o for o in edl["overlays"] if o["tipo"] == "extra"]
    if ex or ctx.decl_extras:
        falt = sum(1 for o in ex if o["faltando"])
        L += ["", "## Cenas extras", "",
              f"{len(ex) - falt} ok · **{falt} faltando**" + (" — o vídeo sai com placeholder e o QA reprova até chegar"
                                                             if falt else ""), "",
              "| ID | Tipo | Arquivo | Linhas | Modo | Saída | Status |", "|---|---|---|---|---|---|---|"]
        avs = {(e, t0): a for e, t0, a in ctx.avisos_extras}
        for o in ex:
            if o.get("arquivo"):
                arq = o["arquivo"] + (f" ({fmt_t(o['in'])}–{fmt_t(o['out'])})" if o.get("in") is not None else "")
            elif o.get("componente") and not o["faltando"]:
                arq = f"componente `{o['componente']}`"
            else:
                arq = "—"
            notas = list(avs.get((o["extra"], o["saida_inicio"])) or [])
            if o.get("credito"):
                notas.append(f"crédito: {o['credito']}")
            if o.get("som"):
                notas.append("com som")
            L.append(f"| {o['extra']} | {o['extra_tipo']} | {arq} | {', '.join(o['linhas'])} | {o['modo']} | "
                     f"{fmt_t(o['saida_inicio'])}–{fmt_t(o['saida_fim'])} | "
                     f"{'**FALTANDO**' if o['faltando'] else 'OK'}{' · ' + '; '.join(notas) if notas else ''} |")
        usados = {o["extra"] for o in ex}
        for eid, d in sorted(ctx.decl_extras.items()):
            if eid not in usados:
                L.append(f"| {eid} | {d.get('tipo')} | — | {', '.join(d.get('linhas') or [])} | — | — | "
                         "sem uso no corte (linha fora da EDL?) |")
    L += ["", "## Enquadramento (zoom por peça — aplicado UMA vez, no corte)", "",
          "> Cada corte troca o enquadramento (1.00 ↔ 1.12, origem no rosto) para disfarçar o jump cut. Para mudar: "
          "`zoom_pecas` (uma escala por peça) e/ou `zoom_origem` (\"x% y%\") no segmento + `edl.py --recalcular`; "
          "`\"zoom\": {\"tipo\": \"punch\", \"escala\": 1.2}` muda a escala do punch e faz o segmento começar fechado.", ""]
    ant, trocas, iguais = None, 0, []
    for si, s in enumerate(edl["segmentos"]):
        zp = s.get("zoom_pecas") or []
        if si and zp and continuacao_de_arquivo(ctx, edl["segmentos"][si - 1], s):
            ant = None                      # continuação no arquivo seguinte da câmera: não é corte
        L.append(f"- **{s['linha']}** · origem {s.get('zoom_origem') or '—'} "
                 f"({ctx.info_rosto.get(s['n']) or 'sem zoom (tela)'}) · " + " → ".join(f"{z:.2f}" for z in zp))
        for z in zp:
            if ant is not None:
                if abs(z - ant) >= ZOOM_DIF_MIN:
                    trocas += 1
                else:
                    iguais.append(s["linha"])
            ant = z
    L.append("")
    L.append(f"{trocas} corte(s) com troca de enquadramento" + (f" · **sem troca: {', '.join(iguais)}**" if iguais else
                                                               " · nenhum corte com o mesmo enquadramento"))
    tx = [o for o in edl["overlays"] if o["tipo"] != "extra"]
    if tx:
        L += ["", "## Textos na tela", ""]
        for o in tx:
            L.append(f"- {o.get('linha')} · {o['tipo']} · {fmt_t(o['saida_inicio'])}–{fmt_t(o['saida_fim'])} · "
                     f"{o.get('texto') or o.get('descricao', '')}")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    ap.add_argument("--recalcular", action="store_true", help="mantém edições manuais do edl.json")
    ap.add_argument("--sem-preview", action="store_true", help="não renderiza edicao/preview.mp4")
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    ed = edicao(vd)
    ctx = Ctx(vd)
    ej, snapj = ed / "edl.json", ed / "edl.auto.json"
    anterior = ler_json(ej, padrao={}) if ej.exists() else {}
    if args.recalcular:
        if not anterior:
            sys.exit("[ERRO] --recalcular precisa de um edl.json existente")
        specs = anterior.get("segmentos", [])
        snapshot = ler_json(snapj, padrao={})
    else:
        if anterior:
            escrever_json(ed / "edl.anterior.json", anterior)
        specs = [{"linha": l["id"], "take": l["escolhido"]} for l in ctx.al["linhas"]
                 if not l.get("alternativa_de") and l.get("escolhido")]
        snapshot = None
    segs, snap_novo = montar(ctx, specs, snapshot, args.recalcular)
    assentar_bordas(vd, segs)
    planejar_zoom(ctx, segs, snap_novo)
    finais, overlays, palavras_saida, dur = derivar(ctx, segs)
    edl = {
        "versao": int(anterior.get("versao", 0)) + 1 if anterior else 1,
        "slug": ctx.roteiro.get("slug") or vd.name,
        "fps": FPS, "sr": SR, "largura": LARGURA, "altura": ALTURA,
        "aprovado": bool(anterior.get("aprovado")) if args.recalcular else False,
        "aprovado_em": anterior.get("aprovado_em") if args.recalcular else None,
        "fontes": {f: v["arquivo"] for f, v in sorted(ctx.fontes.items())},
        "segmentos": finais,
        "overlays": overlays,
        "palavras_saida": palavras_saida,
        "duracao_saida": dur,
        # o plano de zoom (segmentos[].zoom_pecas/zoom_origem) é aplicado pelo render_corte -> o Remotion NÃO aplica
        # o zoom dos segmentos de novo (gerar_props.py / Reel.tsx)
        "zoom_no_corte": True,
        "audio": anterior.get("audio") or {"loudnorm_lufs": -14, "true_peak": -1.5, "musica": None, "ducking": True},
        "variantes": variantes(ctx),
        "gerado_em": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if edl["aprovado"] and not edl["aprovado_em"]:
        edl["aprovado_em"] = edl["gerado_em"]
    escrever_json(ej, edl)
    escrever_json(snapj, snap_novo)
    escrever_md(ctx, edl, ed / "edl.md")
    log(f"[edl] {len(finais)} segmentos · {sum(len(s['cortes_internos']) for s in finais)} cortes internos · "
        f"{len(overlays)} overlays · duração {dur:.2f}s -> {rel(vd, ej)}, {rel(vd, ed / 'edl.md')}")
    for s in finais:
        log(f"   {s['n']:>2} {s['linha']:<5} {s['take']:<8} {fmt_t(s['in'])}→{fmt_t(s['out'])}  "
            f"saída {fmt_t(s['saida_inicio'])}–{fmt_t(s['saida_fim'])}  zoom "
            + "→".join(f"{z:.2f}" for z in s["zoom_pecas"]) + f" @ {s.get('zoom_origem') or '—'}"
            + (f"  cortes {s['cortes_internos']}" if s["cortes_internos"] else ""))
    for o in overlays:
        if o["tipo"] == "extra":
            log(f"   extra {o['extra']:<8} {o['extra_tipo']:<9} {o['modo']:<5} {','.join(o['linhas']):<12} "
                f"saída {fmt_t(o['saida_inicio'])}–{fmt_t(o['saida_fim'])}"
                + (f"  in {o['in']:.2f}–{o['out']:.2f}" if o.get("in") is not None else "")
                + ("  FALTANDO" if o["faltando"] else ""))
    if not args.sem_preview:
        import render_corte
        render_corte.renderizar(vd, preview=True)
    log("[edl] PARE: mostre edl.md + preview ao Carlos e aguarde aprovação antes do render final.")


if __name__ == "__main__":
    main()
