"""Confere os critérios de aceitação dos testes sintéticos (rodar depois do pipeline completo).

uso: uv run python tests/check_synthetic.py                  # clássico: videos/_teste-sintetico (40 critérios)
     uv run python tests/check_synthetic.py --modo monitor   # método ChatGPT-monitor: videos/_teste-monitor
     uv run python tests/check_synthetic.py --modo todos

CLÁSSICO — além das escolhas de take/cortes: formato do projeto (FPS_PROJETO, padrão 25; intermediários 1080x1920
yuv422p10le), câmera em V-Log marcada, orientação vertical, amostra de cor fora do pipeline, cenas extras
(E01 contínuo em 2 linhas e segurando o último quadro, E02 animação registrada, E03 imagem card com crédito,
E04 faltando enquanto não houver arquivo), coluna TELA com vários itens, a LUT de visualização no preview
(se LUT_ENTRADA_CAMERA / 00-marca/cor/luts/entrada-camera.cube existir) e 1 locutor só (sem IA). Vale antes e
depois do `--so-e04`.

MONITOR — duas vozes na mesma gravação (IA pelo "celular" + Carlos seco; ver make_synthetic.py --modo monitor):
locutores.json acerta ≥ 95 % das palavras contra verdade.json, todo take escolhido é do Carlos, nenhuma palavra
da IA no corte (palavras_saida) nem nenhum trecho de áudio da IA (com cauda) dentro das peças da EDL, voz da IA
residual no corte ≈ 0 (verify), take com a IA sobreposta sinalizado e preterido, frases de monitor em `fala_ia`,
L07 (só a IA leu) `faltando`, e a camada A (diarização do Scribe) simulada com ids da verdade + 3 % de ruído.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VD = ROOT / "videos" / "_teste-sintetico"
VD_MONITOR = ROOT / "videos" / "_teste-monitor"
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "corte-por-roteiro" / "scripts"))
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "legendas-animadas" / "scripts"))
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "audio-polish" / "scripts"))
from common import (FFMPEG, FFPROBE, FPS, energia_bandas, fps_de_stream, janela_zoom, ler_audio,  # noqa: E402
                    limites_energia, lut_entrada_camera, norm_palavra, pecas_da_edl, pecas_do_segmento, wav16k_path)
import audio as AUD  # noqa: E402
import edl as E  # noqa: E402
import gerar_props as GP  # noqa: E402
import locutores as LOC  # noqa: E402

FPS_ESPERADO = float(os.environ.get("FPS_PROJETO") or 25)
PIX = "yuv422p10le"
INTER = (1440, 2560)    # intermediário supersampled do principal
ROTEIRO_REAL = ROOT / "videos" / "2026-09-16-chatgpt-contexto" / "roteiro.json"
ACERTO_MIN = 0.95
ALCA = 0.015            # = render_corte.ALCA
AGUDOS = ("2000-5000", "5000-10000", "10000-16000")
TOL_AGUDOS = 1.5        # dB — nenhum tilt de EQ vs o bruto da câmera


def astream(p: Path) -> dict:
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "a:0", "-show_streams", "-show_format",
                        "-of", "json", str(p)], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    s = (d.get("streams") or [{}])[0]
    s["_dur"] = float(d.get("format", {}).get("duration") or 0)
    return s


def bordas_na_energia(vd: Path, edl: dict, tr: dict) -> tuple[list, list, list]:
    """Bordas de peça (in/out e cortes internos, já na grade de frames) DENTRO da energia de uma palavra do Carlos
    (ataque suave/cauda incluídos) + margens reais antes da 1.ª / depois da última palavra de cada segmento."""
    por = {}
    for w in tr["palavras"]:
        if w.get("locutor") != "ia":
            por.setdefault(w["fonte"], []).append(w)
    ruins, pre, pos = [], [], []
    for s in edl["segmentos"]:
        cortes = s.get("cortes_internos") or []
        # palavras removidas de propósito (muleta dentro de um corte interno) não contam
        ws = sorted((w for w in por.get(s["fonte"], [])
                     if not any(c0 <= (w["inicio"] + w["fim"]) / 2 <= c1 for c0, c1 in cortes)),
                    key=lambda w: w["inicio"])
        wav = str(wav16k_path(vd, s["fonte"]))
        spans = [limites_energia(wav, w["inicio"], w["fim"], ws[k - 1]["fim"] if k else 0.0,
                                 ws[k + 1]["inicio"] if k + 1 < len(ws) else w["fim"] + 1.0) for k, w in enumerate(ws)]
        for a, b in pecas_do_segmento(s):
            for e in (a, b):
                for (on, off), w in zip(spans, ws):
                    if on + 0.01 < e < off - 0.01:
                        ruins.append((s["linha"], round(e, 3), w["texto"], round(on, 3), round(off, 3)))
        dentro = [w for w in ws if s["in"] <= (w["inicio"] + w["fim"]) / 2 <= s["out"]]
        if dentro:
            pre.append(round(dentro[0]["inicio"] - s["in"], 3))
            pos.append(round(s["out"] - dentro[-1]["fim"], 3))
    return ruins, pre, pos


def _quadro(path: Path, n: int, w: int | None = None, h: int | None = None) -> bytes:
    vf = f"scale={w}:{h}:flags=area,format=gray" if w else "format=gray"
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{(n + 0.5) / FPS_ESPERADO:.4f}", "-i", str(path),
                        "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-"], capture_output=True, check=True)
    return r.stdout


def escala_no_video(video: Path, src: Path, p, dims_src: tuple[int, int], cands: list[float]) -> tuple[float, dict]:
    """Qual punch-in está REALMENTE no vídeo: o quadro do meio da peça no corte/preview comparado ao mesmo quadro do
    intermediário recortado para cada escala candidata (z-score + MSE). -> (escala mais parecida, erros)."""
    from PIL import Image
    ws, hs = 270, 480
    d = int(round(p.dur * FPS_ESPERADO)) // 2
    c = np.frombuffer(_quadro(video, int(round(p.saida * FPS_ESPERADO)) + d, ws, hs), np.uint8)[:ws * hs]
    c = c.reshape(hs, ws).astype(float)
    W, H = dims_src
    im = Image.frombytes("L", (W, H), _quadro(src, int(round(p.a * FPS_ESPERADO)) + d)[:W * H])

    def z(a):
        return (a - a.mean()) / (a.std() + 1e-6)
    erros = {}
    for e in cands:
        cw, ch, x, y = janela_zoom(W, H, e, p.origem)
        r = np.asarray(im.crop((x, y, x + cw, y + ch)).resize((ws, hs), Image.BOX), float)
        erros[e] = round(float(((z(r) - z(c)) ** 2).mean()), 4)
    return min(erros, key=erros.get), erros


def checar_zoom_e_audio(vd: Path, edl: dict, fontes: dict, ok, pixels: bool) -> None:
    """Critérios novos (revisão do Carlos): enquadramento alternado a cada corte, zoom aplicado UMA vez (no corte,
    nunca no Remotion) e caminho de áudio sem perdas (agudos do bruto preservados no corte e no master)."""
    pecas = pecas_da_edl(edl)
    esc = [p.escala for p in pecas]
    iguais = [(pecas[k - 1].linha, pecas[k].linha, esc[k]) for k in range(1, len(pecas)) if abs(esc[k] - esc[k - 1]) < 0.04]
    ok("zoom alterna a cada corte (plano: nenhuma peça seguida com o mesmo enquadramento, 1.00 ↔ 1.12)",
       len(pecas) > 3 and not iguais and all(1.0 <= e <= 1.33 for e in esc), {"escalas": esc, "iguais": iguais})
    props = GP.segmentos_props(edl)
    reel = (ROOT / "remotion/src/compositions/Reel.tsx").read_text(encoding="utf-8")
    ok("zoom aplicado UMA vez: edl.zoom_no_corte, props do Reel sem zoom e Reel.tsx respeita zoomNoCorte",
       edl.get("zoom_no_corte") is True and all(s["zoom"] is None for s in props) and "!zoomNoCorte" in reel,
       {"zoom_no_corte": edl.get("zoom_no_corte"), "zoom_props": [s["zoom"] for s in props][:4]})
    if pixels:
        src = vd / fontes[pecas[0].fonte]["arquivo"]
        sv = vstream(src)
        dims = (int(sv["width"]), int(sv["height"]))
        det, det_p = [], []
        for p in pecas:
            cands = sorted({1.0, 1.06, 1.12, round(p.escala, 3)})
            det.append(escala_no_video(vd / "edicao/corte.mp4", src, p, dims, cands)[0])
            det_p.append(escala_no_video(vd / "edicao/preview.mp4", src, p, dims, cands)[0])
        ok("zoom no corte.mp4 E no preview.mp4 (medido nos pixels vs intermediário) = plano, alternando",
           det == [round(e, 3) for e in esc] and det_p == det and all(abs(a - b) >= 0.04 for a, b in zip(det, det[1:])),
           {"plano": esc, "corte": det, "preview": det_p})
    # ---- áudio sem perdas: agudos do bruto preservados
    wav = vd / "edicao/corte-audio.wav"
    sw, sc = (astream(wav) if wav.exists() else {}), astream(vd / "edicao/corte.mp4")
    ok("edicao/corte-audio.wav 48 kHz 24-bit mono com a duração do corte (±1 frame)",
       sw.get("codec_name") == "pcm_s24le" and sw.get("sample_rate") == "48000" and sw.get("channels") == 1
       and abs(sw.get("_dur", 0) - sc["_dur"]) <= 1 / FPS_ESPERADO + 1e-3,
       f"{sw.get('codec_name')} {sw.get('sample_rate')} {sw.get('channels')}ch {sw.get('_dur', 0):.3f}s vs {sc['_dur']:.3f}s")
    p = max(pecas, key=lambda x: x.dur)
    bruto = vd / fontes[p.fonte]["bruto"]
    a0, a1 = p.a + 0.03, p.b - 0.03
    s0, s1 = p.saida + 0.03, p.saida + p.dur - 0.03
    b_raw = energia_bandas(ler_audio(bruto, a0, a1))
    b_cut = energia_bandas(ler_audio(wav, s0, s1))
    d_cut = {b: round(b_cut[b] - b_raw[b], 2) for b in AGUDOS}
    ok(f"agudos preservados no corte (corte-audio.wav vs bruto, {p.linha}: 2–5k/5–10k/10–16k ±{TOL_AGUDOS:g} dB)",
       all(abs(v) <= TOL_AGUDOS for v in d_cut.values()), {"delta_db": d_cut, "bruto": b_raw, "corte": b_cut})
    tmp = vd / "edicao" / "_teste-master.mp4"
    r = AUD.normalizar(vd / "edicao/corte.mp4", tmp)
    b_m = energia_bandas(ler_audio(tmp, s0, s1))
    d_m = {b: round(b_m[b] - b_raw[b], 2) for b in AGUDOS}
    i_f, tp_f = float(r["final"]["input_i"]), float(r["final"]["input_tp"])
    # crest: alvo ≥ 13 dB na fala; a voz TTS clássica já tem só 10,9 dB no bruto -> aí "não esmagar" = perder no máx.
    # 1 dB vs o corte. (Com −14 LUFS e TP −1,5 o limitador sempre tira os picos de uma voz com crest alto.)
    ok(f"master (audio.py): do corte-audio.wav, −14 ±0,5 LUFS, TP ≤ −1,5 dBTP, crest ≥ min(13, corte − 1) dB "
       f"(sem esmagar), agudos ±{TOL_AGUDOS:g} dB do bruto (sem tilt)",
       r["master"] and r["master"].endswith("corte-audio.wav") and abs(i_f + 14) <= 0.5 and tp_f <= -1.5
       and b_m["crest"] >= min(13.0, b_cut["crest"] - 1.0) and all(abs(v) <= TOL_AGUDOS for v in d_m.values()),
       {"lufs": i_f, "tp": tp_f, "crest": (b_raw["crest"], b_cut["crest"], b_m["crest"]), "delta_db": d_m})
    tmp.unlink(missing_ok=True)


def j(p, vd=None):
    return json.loads(((vd or VD) / p).read_text(encoding="utf-8"))


def vstream(p: Path) -> dict:
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_streams", "-show_format",
                        "-of", "json", str(p)], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    s = d["streams"][0]
    s["_dur"] = float(d["format"].get("duration") or 0)
    return s


def frame_cinza(p: Path, t: float, w: int, h: int) -> np.ndarray:
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t:.3f}", "-i", str(p), "-frames:v", "1",
                        "-vf", f"scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(h, w).astype(float) / 255


def formato_ok(s: dict, w=None, h=None, pix=PIX) -> bool:
    return (abs(fps_de_stream(s) - FPS_ESPERADO) <= 0.01 and s.get("pix_fmt") == pix
            and (w is None or (s["width"], s["height"]) == (w, h)))


# ==================================================================== clássico (1 voz + extras)
def checar_classico() -> list:
    al, edl, qa = j("edicao/alinhamento.json"), j("edicao/edl.json"), j("qa/verificacao.json")
    fj = j("edicao/fontes.json")
    fontes, extras = fj["fontes"], fj.get("extras", {})
    tr = j("edicao/transcricao.json")
    L = {l["id"]: l for l in al["linhas"]}
    ps = edl["palavras_saida"]
    txt = [w["texto"].lower().strip(".,!?") for w in ps]
    res = []

    def ok(nome, cond, det=""):
        res.append((nome, bool(cond), det))

    # ---------------------------------------------------------------- escolhas / cortes
    ok("L03 escolhe T3", L["L03"]["escolhido"] == "L03-T3", L["L03"]["escolhido"])
    t1 = L["L03"]["takes"][0] if L["L03"]["takes"] else {}
    ok("L03-T1 marcado como tropeço", {"false_start", "final_cortado"} & set(t1.get("flags", [])), t1.get("flags"))
    ok("L05 tem take false_start", any("false_start" in t["flags"] for t in L["L05"]["takes"]),
       [t["flags"] for t in L["L05"]["takes"]])
    ok("L05 escolhe o take completo", L["L05"]["escolhido"] == "L05-T2", L["L05"]["escolhido"])
    ok("separador 'de novo' descartado", any("novo" in s["texto"].lower() for s in al["separadores"])
       and "novo" not in txt, [s["texto"] for s in al["separadores"]])
    ok("improviso em nao_mapeado", any("esqueci" in g["texto"] for g in al["nao_mapeado"]))
    ok("improviso fora do corte", "esqueci" not in txt)
    ok("L07 faltando no alinhamento", L["L07"]["status"] == "faltando")
    ok("L01B fora da EDL principal", all(s["linha"] != "L01B" for s in edl["segmentos"])
       and any(v["linha"] == "L01B" for v in edl.get("variantes", [])))

    def gap(depois_de, antes_de):
        a = next(w for w in ps if w["texto"].lower().strip(".,") == depois_de)
        b = next(w for w in ps if w["texto"].lower().strip(".,") == antes_de and w["inicio"] >= a["fim"])
        return b["inicio"] - a["fim"]
    g56 = gap("palavras", "com")
    ok("silêncio de 3 s encurtado (L05→L06)", g56 < 0.8, f"{g56:.2f}s")
    g4 = gap("exemplos", "e")
    ok("pausa interna de L04 encurtada", g4 <= 0.45, f"{g4:.2f}s")
    ok("grafia do roteiro (ChatGPT)", "chatgpt" in txt, [w["texto"] for w in ps[:8]])
    q = {r["id"]: r for r in qa["linhas"]}
    ok("diff.md: L07 faltando", q["L07"]["status"].startswith("faltando"), q["L07"]["status"])
    ruins = {k: v["wer"] for k, v in q.items() if k != "L07" and (v["wer"] is None or v["wer"] > 0.08)}
    ok("demais linhas WER <= 8%", not ruins, ruins or {k: v["wer"] for k, v in q.items()})
    ok("WER geral <= 8%", qa["wer_geral"] <= 0.08, qa["wer_geral"])
    d = qa["duracao"]
    ok(f"A/V dentro de 1 frame a {FPS_ESPERADO:g} fps", abs(d["video"] - d["audio"]) <= 1 / FPS_ESPERADO + 1e-3
       and qa.get("fps", {}).get("ok"), f"Δ {abs(d['video'] - d['audio']) * 1000:.1f} ms · {qa.get('fps')}")
    ok("duração = soma das peças", qa["duracao_ok"], d)
    ok("filmstrips gerados", (VD / "edicao/frames/contato.png").exists()
       and list((VD / "edicao/frames").glob("corte-*.png")))

    # ---------------------------------------------------------------- formato do projeto (25 fps, 10-bit)
    ok(f"projeto em {FPS_ESPERADO:g} fps (common.FPS)", abs(FPS - FPS_ESPERADO) < 1e-9, FPS)
    ok(f"EDL fps = {FPS_ESPERADO:g}", abs(float(edl["fps"]) - FPS_ESPERADO) < 1e-9, edl["fps"])
    det, bons = {}, True
    for k, v in fontes.items():
        if v["tipo"] == "amostra_cor":
            continue
        s = vstream(VD / v["arquivo"])
        w48 = VD / (v.get("wav48k") or f"edicao/audio48k/{k}.wav")
        a48 = astream(w48) if w48.exists() else {}
        bons &= (formato_ok(s, *INTER) and a48.get("codec_name") == "pcm_s24le" and a48.get("channels") == 1
                 and a48.get("sample_rate") == "48000" and (v.get("audio") or {}).get("limpar_ruido") is False
                 and "afftdn" not in ((v.get("audio") or {}).get("cadeia") or "afftdn"))
        det[k] = (f"{s['width']}x{s['height']} {s['r_frame_rate']} {s['pix_fmt']} {s.get('profile')} · "
                  f"{a48.get('codec_name')} {a48.get('sample_rate')} {a48.get('channels')}ch · "
                  f"{(v.get('audio') or {}).get('cadeia')}")
    ok(f"fontes (principal) {INTER[0]}×{INTER[1]} {FPS_ESPERADO:g} fps {PIX} + master WAV 48 kHz 24-bit mono "
       "(só passa-altas, sem denoise)", bons and det, det)
    ruins, pre, pos = bordas_na_energia(VD, edl, tr)
    ok("margens de corte: nenhuma borda (in/out/corte interno) dentro da energia de uma palavra; "
       "mediana ≥ 0,04 s antes da 1.ª e ≥ 0,06 s depois da última (2026-10-01: ritmo apertado)",
       not ruins and pre and float(np.median(pre)) >= 0.04 and float(np.median(pos)) >= 0.06,
       {"dentro": ruins[:5], "pre": pre, "pos": pos})
    sc = vstream(VD / "edicao/corte.mp4")
    ok(f"corte 1080×1920 {FPS_ESPERADO:g} fps {PIX}", formato_ok(sc, 1080, 1920),
       f"{sc['width']}x{sc['height']} {sc['r_frame_rate']} {sc['pix_fmt']} {sc.get('profile')}")
    sp = vstream(VD / "edicao/preview.mp4")
    ok("preview 540×960 8-bit, mesma duração do corte",
       formato_ok(sp, 540, 960, "yuv420p") and abs(sp["_dur"] - sc["_dur"]) <= 1 / FPS_ESPERADO + 1e-3,
       f"{sp['width']}x{sp['height']} {sp['pix_fmt']} {sp['_dur']:.3f}s vs corte {sc['_dur']:.3f}s")
    cam = fontes.get("camera-01", {})
    ok("câmera marcada V-Log (perfil vlog); extra de tela sdr", cam.get("perfil") == "vlog"
       and extras.get("E01", {}).get("perfil") == "sdr",
       {k: v.get("perfil") for k, v in {**fontes, **extras}.items()})
    # 3840x2160 + rotação -> em pé: quadrado branco no canto sup. esquerdo, pretos nos outros
    g = frame_cinza(VD / cam.get("arquivo", "edicao/fontes/camera-01.mp4"), 1.0, 108, 192)
    cantos = {"se": g[:10, :10].mean(), "sd": g[:10, -10:].mean(), "ie": g[-10:, :10].mean(), "id": g[-10:, -10:].mean()}
    ok(f"orientação vertical correta (4K rot 90 -> {INTER[0]}×{INTER[1]})",
       cam.get("original", "").startswith("2160x3840") and cantos["se"] > max(cantos["sd"], cantos["ie"], cantos["id"]) + 0.3,
       {k: round(v, 2) for k, v in cantos.items()} | {"original": cam.get("original"), "rot": cam.get("rotacao")})
    amostra = fontes.get("camera-00-cor", {})
    ok("amostra de cor fora do pipeline (fontes.json amostra_cor, sem transcrição/EDL)",
       amostra.get("tipo") == "amostra_cor" and "camera-00-cor" not in tr.get("fontes", {})
       and "camera-00-cor" not in edl["fontes"] and all(s["fonte"] != "camera-00-cor" for s in edl["segmentos"])
       and not (VD / "edicao/fontes/camera-00-cor.mp4").exists(), amostra.get("tipo"))

    # ---------------------------------------------------------------- cenas extras (principal x extras)
    ok("só o principal é transcrito / entra no corte", set(tr.get("fontes", {})) == {"camera-01"}
       and set(edl["fontes"]) == {"camera-01"}, {"transcricao": list(tr.get("fontes", {})), "edl": list(edl["fontes"])})
    e1 = extras.get("E01", {})
    s1 = vstream(VD / e1["arquivo"]) if e1.get("arquivo") else {}
    e3 = extras.get("E03", {})
    ok("extras ingeridos: E01 -> extras/E01.mp4 1080 larg. 25 fps 8-bit; E03 -> png ≤ 2160",
       e1.get("tipo") == "tela" and s1.get("width") == 1080 and formato_ok(s1, pix="yuv420p")
       and e3.get("arquivo", "").endswith("E03.png") and max(e3.get("largura", 9e9), e3.get("altura", 9e9)) <= 2160,
       {"E01": f"{s1.get('width')}x{s1.get('height')} {s1.get('r_frame_rate')} {s1.get('pix_fmt')}",
        "E03": f"{e3.get('largura')}x{e3.get('altura')}"})
    ov = [o for o in edl["overlays"] if o["tipo"] == "extra"]
    por = {}
    for o in ov:
        por.setdefault(o["extra"], []).append(o)
    seg = {s["linha"]: s for s in edl["segmentos"]}
    o1 = (por.get("E01") or [{}])
    ok("E01 contínuo: 1 overlay para L03+L04 (split), segura o último quadro (extra de 6 s)",
       len(o1) == 1 and o1[0].get("linhas") == ["L03", "L04"] and o1[0].get("modo") == "split"
       and abs(o1[0]["saida_inicio"] - seg["L03"]["saida_inicio"]) < 1e-3
       and abs(o1[0]["saida_fim"] - seg["L04"]["saida_fim"]) < 1e-3
       and o1[0].get("in") == 0.0 and abs(o1[0].get("out", 0) - 6.0) < 0.05
       and (o1[0]["saida_fim"] - o1[0]["saida_inicio"]) > 6.0 and o1[0].get("arquivo") == "edicao/extras/E01.mp4",
       o1)
    o2 = (por.get("E02") or [{}])[0]
    ok("E02 animação: componente registrado, sem arquivo, full, não faltando",
       o2.get("extra_tipo") == "animacao" and o2.get("componente") == "_teste-sintetico/E02"
       and o2.get("modo") == "full" and o2.get("faltando") is False and o2.get("linhas") == ["L05"], o2)
    o3 = (por.get("E03") or [{}])[0]
    ok("E03 imagem: card com crédito, sem in/out (Ken Burns no Remotion)",
       o3.get("arquivo") == "edicao/extras/E03.png" and o3.get("modo") == "card" and o3.get("credito")
       and "in" not in o3 and o3.get("faltando") is False, o3)
    o4 = (por.get("E04") or [{}])[0]
    tem_e04 = any((VD / "brutos/extras").glob("E04*"))
    ok(f"E04 {'entregue -> não faltando' if tem_e04 else 'declarado sem arquivo -> faltando'}",
       o4.get("faltando") is (not tem_e04) and o4.get("credito") == "OpenAI (demo)" and o4.get("modo") == "split"
       and (o4.get("arquivo") == "edicao/extras/E04.mp4") == tem_e04, o4)
    md = (VD / "edicao/edl.md").read_text(encoding="utf-8")
    ok("edl.md: tabela 'Cenas extras' com E01–E04 e status",
       "## Cenas extras" in md and all(f"| {e} |" in md for e in ("E01", "E02", "E03", "E04"))
       and ("**FALTANDO**" in md) == (not tem_e04))
    grafo = (VD / "edicao/.grafo-preview.txt").read_text(encoding="utf-8")
    ok("preview com rótulo 'EXTRA Exx · modo' (vermelho se faltando)",
       "EXTRA E01 · split" in grafo and "EXTRA E03 · card" in grafo and ("FALTANDO" in grafo) == (not tem_e04))

    # ---------------------------------------------------------------- coluna TELA com vários itens
    l4t = [o for o in edl["overlays"] if o["tipo"] == "texto" and o.get("linha") == "L04"]
    ok("TELA 'EXTRA: E01 split · TEXTO · GESTO' -> extra + texto (L04), GESTO ignorado",
       [o["texto"] for o in l4t] == ["PEÇA EXEMPLOS"] and "L04" in o1[0].get("linhas", [])
       and seg.get("L04", {}).get("layout") == "split", l4t)
    ok("ZOOM como item -> punch-in no segmento (L01 começa fechado: zoom_pecas[0] = 1.12)",
       (seg.get("L01", {}).get("zoom") or {}).get("tipo") == "punch" and seg.get("L03", {}).get("zoom") is None
       and (seg.get("L01", {}).get("zoom_pecas") or [0])[0] == 1.12,
       {k: (s.get("zoom"), s.get("zoom_pecas")) for k, s in seg.items()})
    tx, rf, zm = E.analisar_tela({"id": "L09", "tela": 'tela-01 00:04-00:11 split · TEXTO: "A · B" · '
                                  "ANIMACAO[card]: checklist de revisão · GESTO: aponta"})
    ok("legado: 'tela-01 a–b modo' e 'ANIMACAO[modo]: desc · …' viram refs de extra",
       [(r["id"], r["modo"], r["in"], r["out"]) for r in rf] == [("tela-01", "split", 4.0, 11.0), ("L09", "card", None, None)]
       and rf[1].get("descricao") == "checklist de revisão" and [t["texto"] for t in tx] == ["A · B"] and zm is None,
       (tx, rf))
    if ROTEIRO_REAL.exists():
        rj = json.loads(ROTEIRO_REAL.read_text(encoding="utf-8"))
        decl = {e["id"]: e for e in rj.get("extras") or []}
        rr = {l["id"]: l for l in rj["linhas"]}
        an = {lid: E.analisar_tela(l, decl) for lid, l in rr.items()}
        # roteiro atual: E02 = 1 animação SPLIT de L03 a L12 (animação deitada 16:9 divide a tela — regra do
        # Carlos, 2026-09-17). L13 sem extra: o E03 (cartão do CTA) foi dispensado por ele no mesmo dia
        # ("esse vídeo é de teste"). (+ GESTO na coluna TELA continua sendo ignorado)
        e02 = {lid: [(r["id"], r["modo"]) for r in an[lid][1]] for lid in rr if lid in an and an[lid][1]}
        corpo = [f"L{k:02d}" for k in range(3, 13)]
        notas = [t for a in an.values() for t in a[0] if "GESTO" in t["texto"]]
        ok("roteiro real (chatgpt-contexto): TEXTO+ZOOM em L01, TEXTO em L02, E02 animação split em L03–L12, "
           "L13 sem extra (E03 dispensado), GESTO ignorado",
           an["L01"][0] and an["L01"][2] and an["L02"][0] and not an["L02"][2]
           and all(e02.get(lid) == [("E02", "split")] for lid in corpo) and not e02.get("L13")
           and (decl.get("E02") or {}).get("tipo") == "animacao" and not notas,
           {"refs": e02, "L01": an["L01"][2], "extras": list(decl)})
    else:
        ok("roteiro real (chatgpt-contexto): pulado — roteiro.json não existe", True)

    # ---------------------------------------------------------------- LUT de visualização no preview
    if lut_entrada_camera():
        s0 = next(s for s in edl["segmentos"] if s["linha"] == "L01")
        t = (s0["saida_inicio"] + s0["saida_fim"]) / 2
        a, b = frame_cinza(VD / "edicao/corte.mp4", t, 108, 192), frame_cinza(VD / "edicao/preview.mp4", t, 108, 192)
        ra, rb = np.percentile(a, 98) - np.percentile(a, 2), np.percentile(b, 98) - np.percentile(b, 2)
        ok("preview com LUT de visualização (contraste > corte em log)", rb > ra + 0.1,
           f"faixa luma corte {ra:.2f} -> preview {rb:.2f}")
    else:
        ok("preview com LUT de visualização: pulado — sem entrada-camera.cube", True)

    # ---------------------------------------------------------------- zoom por peça + áudio sem perdas
    checar_zoom_e_audio(VD, edl, fontes, ok, pixels=True)

    # ---------------------------------------------------------------- locutores (gravação de 1 voz)
    loc = j("edicao/locutores.json")
    ok("1 locutor só (gravação clássica): locutores.json n_locutores=1, todas as palavras `carlos`, sem voz de IA",
       loc.get("n_locutores") == 1 and all(w.get("locutor") == "carlos" for w in tr["palavras"])
       and not qa.get("voz_ia", {}).get("aplicavel", False) and not al.get("fala_ia"),
       {"n_locutores": loc.get("n_locutores"), "separacao": loc.get("separacao", {}).get("distancia"),
        "voz_ia": qa.get("voz_ia", {}).get("motivo")})
    return res


# ==================================================================== monitor (IA pelo celular + Carlos)
def locutor_verdade(w: dict, pedacos: list[dict]) -> set[str]:
    """Locutor(es) reais do meio da palavra (intervalos reais, com cauda); fora de tudo: o pedaço mais perto."""
    m = (w["inicio"] + w["fim"]) / 2
    c = {p["locutor"] for p in pedacos if p["inicio_real"] - 0.05 <= m <= p["fim_real"] + 0.05}
    if not c:
        p = min(pedacos, key=lambda p: min(abs(m - p["inicio_real"]), abs(m - p["fim_real"])))
        c = {p["locutor"]}
    return c


def acerto(palavras: list[dict], pedacos: list[dict]) -> tuple[float, list]:
    erros = [(w["texto"], round(w["inicio"], 2), w.get("locutor"), sorted(locutor_verdade(w, pedacos)))
             for w in palavras if w.get("locutor") not in locutor_verdade(w, pedacos)]
    return 1 - len(erros) / max(1, len(palavras)), erros


def checar_monitor() -> list:
    vd = VD_MONITOR
    al, edl, qa = j("edicao/alinhamento.json", vd), j("edicao/edl.json", vd), j("qa/verificacao.json", vd)
    tr, loc, gt = j("edicao/transcricao.json", vd), j("edicao/locutores.json", vd), j("verdade.json", vd)
    rot = j("roteiro.json", vd)
    pedacos = gt["pedacos"]
    pal = {w["i"]: w for w in tr["palavras"]}
    L = {l["id"]: l for l in al["linhas"]}
    principais = [l["id"] for l in rot["linhas"] if not l.get("alternativa_de")]
    res = []

    def ok(nome, cond, det=""):
        res.append((nome, bool(cond), det))

    # ---------------------------------------------------------------- rótulos
    pp = loc.get("papel") or {}
    ok("locutores.json: 2 vozes, IA identificada (confiança ≥ 0,5), evidências sem conflito",
       loc.get("n_locutores") == 2 and (pp.get("confianca") or 0) >= 0.5 and not pp.get("conflito")
       and len(pp.get("evidencias") or []) >= 3,
       {"metodo": loc.get("metodo"), "separacao": loc.get("separacao", {}).get("distancia"),
        "confianca": pp.get("confianca"), "evidencias": [(e["nome"], e["valor"]) for e in pp.get("evidencias") or []]})
    ac, erros = acerto(tr["palavras"], pedacos)
    ok(f"acerto de locutor por palavra ≥ {ACERTO_MIN:.0%} (verdade.json)", ac >= ACERTO_MIN,
       f"{ac:.1%} de {len(tr['palavras'])} palavras; erros {erros[:6]}")
    st = loc.get("estatisticas") or {}
    ok("locutores.json: segundos IA/Carlos, sobreposições e segmentos por decisão",
       st.get("segundos_ia", 0) > 10 and st.get("segundos_carlos", 0) > 10 and "sobreposicoes" in st
       and loc.get("segmentos") and all("locutor" in s and "conf" in s for s in loc["segmentos"]), st)
    zonas = (loc.get("zonas_ia") or {}).get("camera-01", [])
    cob = []
    for p in pedacos:
        if p["locutor"] != "ia":
            continue
        a, b = p["inicio"], p["fim"]
        dentro = sum(max(0.0, min(b, zb) - max(a, za)) for za, zb in zonas)
        cob.append(dentro / (b - a))
    ok("zonas_ia cobrem ≥ 90 % de cada fala real da IA", cob and min(cob) >= 0.9, [round(c, 2) for c in cob])

    # ---------------------------------------------------------------- takes = só o Carlos
    def palavras_take(t):
        return [pal[i] for i in range(t["i_ini"], t["i_fim"] + 1) if pal[i]["fonte"] == t["fonte"]]
    ruins = []
    for l in al["linhas"]:
        for t in l["takes"]:
            ws = palavras_take(t)
            if any(w.get("locutor") != "carlos" or locutor_verdade(w, pedacos) != {"carlos"} for w in ws):
                ruins.append((t["take_id"], t["texto"][:40]))
    ok("nenhum take contém palavra da IA (rótulo e verdade)", not ruins, ruins)
    esc = {l["id"]: next((t for t in l["takes"] if t["take_id"] == l["escolhido"]), None) for l in al["linhas"]}
    ok("todo take escolhido é do Carlos", all(t is None or all(locutor_verdade(w, pedacos) == {"carlos"}
                                                              for w in palavras_take(t)) for t in esc.values())
       and sum(1 for lid in principais if esc.get(lid)) >= 6,
       {k: (v or {}).get("take_id") for k, v in esc.items()})
    leit = {lid: len(L[lid].get("leituras_ia") or []) for lid in principais}
    ok("leituras da IA registradas por linha (leituras_ia; L03 lida 2×), nunca como take",
       all(n >= 1 for n in leit.values()) and leit.get("L03", 0) >= 2
       and all("inicio" in x and "fim" in x for lid in principais for x in L[lid].get("leituras_ia") or []), leit)
    ok("L01/L02: repetição do Carlos transcrita e escolhida (Whisper não 'engoliu' a repetição)",
       L["L01"]["escolhido"] and L["L02"]["escolhido"], {k: L[k]["escolhido"] for k in ("L01", "L02")})
    ok("L03: erro do Carlos + 'de novo' da IA -> escolhe o retake limpo (T2)", L["L03"]["escolhido"] == "L03-T2",
       [(t["take_id"], t["sim"], t["flags"]) for t in L["L03"]["takes"]])
    t4 = {t["take_id"]: t for t in L["L04"]["takes"]}
    ok("L04: T2 com a IA falando por cima -> `sobreposicao_ia`, escolhido o T1 limpo",
       "sobreposicao_ia" in t4.get("L04-T2", {}).get("flags", []) and L["L04"]["escolhido"] == "L04-T1"
       and any(s["tipo"] == "ia_depois_do_carlos" for s in loc.get("sobreposicoes") or []),
       {"takes": [(k, t["flags"]) for k, t in t4.items()], "motivo": L["L04"]["motivo"]})
    ok("L05: falso começo + 'de novo' do próprio Carlos (separador) -> T2",
       L["L05"]["escolhido"] == "L05-T2" and any("novo" in s["texto"].lower() for s in al["separadores"]),
       {"escolhido": L["L05"]["escolhido"], "separadores": [s["texto"] for s in al["separadores"]]})
    ok("L07 só lida pela IA -> `faltando` (não preenchida com a leitura da IA)",
       L["L07"]["status"] == "faltando" and not L["L07"]["takes"] and leit.get("L07", 0) >= 1
       and "IA" in L["L07"]["motivo"] and all(s["linha"] != "L07" for s in edl["segmentos"]), L["L07"]["motivo"])

    # ---------------------------------------------------------------- fala da IA (monitor)
    fia = " | ".join(g["texto"] for g in al.get("fala_ia") or []).lower()
    ok("frases de monitor da IA em `fala_ia` (de novo, próxima, perfeito, mais uma vez, ótimo)",
       all(x in fia for x in ("novo", "próxima", "perfeito", "mais uma vez", "ótimo")), fia)
    ok("'de novo' da IA fora dos separadores; nada da IA em nao_mapeado",
       all(pal[i].get("locutor") != "ia" for g in al["nao_mapeado"] for i in range(g["i_ini"], g["i_fim"] + 1))
       and len([s for s in al["separadores"] if "novo" in s["texto"].lower()]) == 1,
       {"separadores": al["separadores"], "nao_mapeado": [g["texto"] for g in al["nao_mapeado"]]})

    # ---------------------------------------------------------------- corte sem IA
    monitor = {"proxima", "perfeito", "novo", "repete", "faltou", "boa", "otimo", "terminamos", "pular", "energia"}
    toks_saida = {t for w in edl["palavras_saida"] for t in norm_palavra(w["texto"])}
    ok("palavras_saida sem palavras da IA (nenhuma frase de monitor; L07 ausente)",
       not (toks_saida & monitor) and all(w["linha"] != "L07" for w in edl["palavras_saida"]),
       sorted(toks_saida & monitor))
    ia_real = [(p["inicio_real"], p["fim_real"]) for p in pedacos if p["locutor"] == "ia"]
    toque = []
    for p in pecas_da_edl(edl):
        for a, b in ia_real:
            x = min(p.b + ALCA, b) - max(p.a - ALCA, a)
            if x > 0:
                toque.append((p.linha, round(p.a, 2), round(p.b, 2), round(x, 3)))
    ok("nenhuma peça da EDL (com a alça de áudio) toca a voz real da IA, nem a cauda da reverb", not toque, toque)
    ok("segmentos da EDL com voz_ia = 0", all(s.get("voz_ia", 1) == 0 for s in edl["segmentos"]),
       {s["linha"]: s.get("voz_ia") for s in edl["segmentos"]})
    vz = qa.get("voz_ia") or {}
    diff = (vd / "qa/diff.md").read_text(encoding="utf-8")
    ok("verify: voz da IA residual no corte ≈ 0 s (≤ 0,1 s; reprova > 0,2 s) e reportada no qa/diff.md",
       vz.get("aplicavel") and vz.get("segundos", 9) <= 0.1 and vz.get("segundos_edl", 9) == 0
       and qa.get("voz_ia_ok") and "Voz da IA no corte: OK" in diff,
       {k: vz.get(k) for k in ("segundos", "segundos_edl", "trechos", "palavras_ia")})
    q = {r["id"]: r for r in qa["linhas"]}
    ruins = {k: v["wer"] for k, v in q.items() if k != "L07" and (v["wer"] is None or v["wer"] > 0.08)}
    ok("verify: L07 faltando (não gravada), demais linhas WER ≤ 8 %",
       q["L07"]["status"] == "faltando (não gravada)" and not ruins, ruins or {k: v["wer"] for k, v in q.items()})
    md = (vd / "edicao/edl.md").read_text(encoding="utf-8")
    ok("edl.md: coluna 'IA · Carlos' por linha + resumo de locutores + fala da IA fora do corte",
       "IA · Carlos" in md and "**Locutores (método ChatGPT-monitor):**" in md and "Fala da IA — monitor" in md
       and any(r.startswith("| – | L07 |") and r.rstrip().endswith("| 1 · 0 |") for r in md.splitlines()))
    ok("filmstrips gerados", (vd / "edicao/frames/contato.png").exists() and list((vd / "edicao/frames").glob("corte-*.png")))
    ruins_b, pre, pos = bordas_na_energia(vd, edl, tr)
    ok("margens de corte (2 vozes): nenhuma borda dentro da energia de uma palavra do Carlos",
       not ruins_b, {"dentro": ruins_b[:5], "pre": pre, "pos": pos})
    checar_zoom_e_audio(vd, edl, j("edicao/fontes.json", vd)["fontes"], ok, pixels=False)

    # ---------------------------------------------------------------- camada A: diarização do Scribe (simulada)
    rng = np.random.default_rng(3)
    ids = {"ia": "speaker_1", "carlos": "speaker_0"}
    base = []
    for w in tr["palavras"]:
        v = next(iter(sorted(locutor_verdade(w, pedacos))))
        if rng.random() < 0.03:
            v = "carlos" if v == "ia" else "ia"
        base.append({**{k: x for k, x in w.items() if k not in ("locutor", "locutor_conf")}, "locutor_bruto": ids[v]})
    wavs = {"camera-01": str(vd / "edicao/audio16k/camera-01.wav")}
    ps, dados = LOC.rotular({**tr, "palavras": base}, wavs, rot, forcar_metodo="scribe", verbose=False)
    ac_s, erros_s = acerto(ps, pedacos)
    ok("camada A (Scribe diarize simulado, 3 % dos ids trocados): método scribe, IA = speaker_1, acerto ≥ 95 %",
       dados["metodo"] == "scribe" and ac_s >= ACERTO_MIN
       and dados["classes"][dados["papel"]["ia"]].get("id_scribe") == "speaker_1",
       f"{ac_s:.1%}; nulls {sum(1 for w in ps if w['locutor'] is None)}; erros {erros_s[:5]}")
    return res


def imprimir(titulo: str, res: list) -> int:
    print(f"\n== {titulo}")
    falhas = 0
    for nome, c, det in res:
        print(f"[{'PASS' if c else 'FALHA'}] {nome}" + (f"  ({det})" if det != "" else ""))
        falhas += not c
    print(f"{len(res) - falhas}/{len(res)} critérios ok")
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modo", choices=["classico", "monitor", "todos"], default="classico")
    args = ap.parse_args()
    falhas = 0
    if args.modo in ("classico", "todos"):
        falhas += imprimir("clássico (videos/_teste-sintetico)", checar_classico())
    if args.modo in ("monitor", "todos"):
        falhas += imprimir("método ChatGPT-monitor (videos/_teste-monitor)", checar_monitor())
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
