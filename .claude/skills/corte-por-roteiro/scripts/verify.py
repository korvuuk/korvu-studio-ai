"""Verificação do corte: re-transcreve o vídeo de saída e compara com o roteiro -> qa/diff.md

uso: uv run python verify.py <video_dir> [--video edicao/corte.mp4] [--engine scribe|mlx|whisperx]

- Por linha: presente / faltando (não gravada | perdida no corte) / duplicada + WER da linha.
- Trechos extras (fala fora do roteiro que sobrou no corte).
- WER geral, duração (vs soma das peças da EDL, vs duracao_alvo), sincronia A/V (±1 frame no FPS do projeto),
  fps do vídeo = FPS_PROJETO (padrão 25).
- Voz da IA residual (método ChatGPT-monitor): o modelo por quadro do edicao/locutores.json (gravação original)
  classifica o áudio do corte -> segundos de voz de IA (tem que ser 0; reprova se > 0,2 s). Também informa quanto
  das peças da EDL toca as `zonas_ia` (conta determinística).
- Exit 1 se alguma linha faltar, WER geral > 8%, A/V fora de 1 frame, fps diferente do projeto ou voz de IA > 0,2 s.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from rapidfuzz.distance import Levenshtein

sys.path.insert(0, str(Path(__file__).resolve().parent))
import align as A  # noqa: E402
import locutores as LOC  # noqa: E402
from common import (FPS, FRAME, carregar_roteiro, duracao, duracao_pecas, duracoes_streams, edicao,  # noqa: E402
                    escrever_json, ffmpeg, ffprobe_json, fmt_t, fps_de_stream, ler_json, log, pecas_da_edl, rel,
                    resolver_video_dir)
from transcribe import PROMPT_VERBATIM, engine_padrao, transcrever_wav, vocabulario_roteiro  # noqa: E402

WER_MAX = 0.08
EXTRA_MIN = 3        # tokens seguidos fora do roteiro entre linhas = "trecho extra"
VOZ_IA_MAX = 0.2     # s de voz de IA detectada no corte que reprova (o esperado é 0)
ALCA = 0.015         # = render_corte.ALCA


def alinhar_global(toks: list, esperadas: list):
    """Alinhamento Levenshtein de todo o corte contra a sequência de linhas esperadas."""
    st, sl = [], []
    for li, l in enumerate(esperadas):
        st += l.toks
        sl += [li] * l.n
    voc = A.Vocab()
    a, b = voc.ids([t.t for t in toks]), voc.ids(st)
    est = [{"S": 0, "D": 0, "I": 0, "C": 0, "n": l.n, "toks": []} for l in esperadas]
    dono = [None] * len(a)
    for op in Levenshtein.opcodes(a, b):
        la, lb = op.src_end - op.src_start, op.dest_end - op.dest_start
        if op.tag == "equal":
            for k in range(la):
                li = sl[op.dest_start + k]
                est[li]["C"] += 1
                dono[op.src_start + k] = li
        elif op.tag == "replace":
            m = min(la, lb)
            for k in range(m):
                li = sl[op.dest_start + k]
                est[li]["S"] += 1
                dono[op.src_start + k] = li
            for k in range(m, lb):
                est[sl[op.dest_start + k]]["D"] += 1
        elif op.tag == "insert":
            for k in range(lb):
                est[sl[op.dest_start + k]]["D"] += 1
    extras, k = [], 0
    while k < len(a):
        if dono[k] is not None:
            k += 1
            continue
        k2 = k
        while k2 + 1 < len(a) and dono[k2 + 1] is None:
            k2 += 1
        antes = dono[k - 1] if k > 0 else None
        depois = dono[k2 + 1] if k2 + 1 < len(a) else None
        n = k2 - k + 1
        if n >= EXTRA_MIN and (antes != depois or antes is None):
            extras.append((k, k2))
        else:
            alvo = antes if antes is not None else depois
            if alvo is not None:
                est[alvo]["I"] += n
                for j in range(k, k2 + 1):
                    dono[j] = alvo
        k = k2 + 1
    for j, li in enumerate(dono):
        if li is not None:
            est[li]["toks"].append(j)
    return est, extras


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    ap.add_argument("--video", default="edicao/corte.mp4")
    ap.add_argument("--engine", choices=["scribe", "mlx", "whisperx"], default=None)
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    ed = edicao(vd)
    video = (vd / args.video) if not Path(args.video).is_absolute() else Path(args.video)
    if not video.exists():
        sys.exit(f"[ERRO] {video} não existe")
    roteiro = carregar_roteiro(vd)
    edl = ler_json(ed / "edl.json")
    al = ler_json(ed / "alinhamento.json", padrao={"linhas": []})
    engine = args.engine or engine_padrao()

    wav = ed / "audio16k" / "_verificacao.wav"
    wav.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg(["-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])
    log(f"[verify] transcrevendo {rel(vd, video)} com {engine}...")
    vocab = vocabulario_roteiro(vd)
    palavras, _ = transcrever_wav(wav, engine, ed / "raw" / f"_verificacao.{engine}.json", force=True,
                                  prompt=PROMPT_VERBATIM + (" " + ", ".join(vocab[:20]) + "." if vocab else ""))
    tr_saida = {"engine": engine, "idioma": "pt", "fontes": {"saida": {"arquivo": rel(vd, video), "duracao": duracao(video)}},
                "palavras": [dict(w, i=i, fonte="saida") for i, w in enumerate(palavras)], "eventos": []}
    (vd / "qa").mkdir(exist_ok=True)
    escrever_json(vd / "qa" / "transcricao-corte.json", tr_saida)

    linhas = {l.id: l for l in A.preparar_roteiro(roteiro)}
    principais = [l["id"] for l in roteiro["linhas"] if not l.get("alternativa_de")]
    na_edl = []
    for s in edl["segmentos"]:
        if s["linha"] not in na_edl:
            na_edl.append(s["linha"])
    esperadas = [linhas[i] for i in na_edl if i in linhas]
    toks = A.tokens_por_fonte(tr_saida["palavras"], list(linhas.values()), aproximar=False).get("saida", [])
    est, extras = alinhar_global(toks, esperadas)
    al_saida = A.alinhar(tr_saida, roteiro)
    takes_saida = {l["id"]: [t for t in l["takes"] if t["sim"] >= A.SIM_OK] for l in al_saida["linhas"]}
    status_al = {l["id"]: l["status"] for l in al.get("linhas", [])}
    pal = tr_saida["palavras"]

    linhas_rel, faltando, tot_err, tot_n = [], [], 0, 0
    for lid in principais:
        l = linhas[lid]
        if lid not in na_edl:
            motivo = "faltando (não gravada)" if status_al.get(lid) == "faltando" else "faltando (fora da EDL)"
            faltando.append(lid)
            linhas_rel.append({"id": lid, "status": motivo, "wer": None, "esperado": l.fala, "ouvido": ""})
            continue
        e = est[na_edl.index(lid)]
        err = e["S"] + e["D"] + e["I"]
        wer = err / max(1, e["n"])
        tot_err += err
        tot_n += e["n"]
        ws = sorted({toks[j].wi for j in e["toks"]} | {toks[j].wf for j in e["toks"]})
        ouvido = " ".join(pal[i]["texto"] for i in ws)
        if (e["C"] + e["S"]) < 0.5 * e["n"]:
            st = "faltando (perdida no corte)"
            faltando.append(lid)
        elif len(takes_saida.get(lid, [])) > 1:
            st = "duplicada"
        else:
            st = "presente"
        linhas_rel.append({"id": lid, "status": st, "wer": round(wer, 4), "esperado": l.fala, "ouvido": ouvido,
                           "S": e["S"], "D": e["D"], "I": e["I"]})
    extras_rel = []
    for k0, k1 in extras:
        w0, w1 = pal[toks[k0].wi], pal[toks[k1].wf]
        extras_rel.append({"inicio": w0["inicio"], "fim": w1["fim"],
                           "texto": " ".join(p["texto"] for p in pal[toks[k0].wi:toks[k1].wf + 1])})
        tot_err += k1 - k0 + 1
    wer_geral = tot_err / max(1, tot_n)

    ds = duracoes_streams(video)
    dv, da = ds.get("video") or 0.0, ds.get("audio") or 0.0
    esperado = float(edl.get("duracao_saida") or 0)
    soma = duracao_pecas(pecas_da_edl(edl))
    alvo = roteiro.get("duracao_alvo")
    av_ok = abs(dv - da) <= FRAME + 1e-3
    dur_ok = abs(dv - soma) <= FRAME + 1e-3
    vs = next((s for s in ffprobe_json(video)["streams"] if s.get("codec_type") == "video"), {})
    fps_v = fps_de_stream(vs)
    fps_ok = abs(fps_v - FPS) <= 0.01
    duplicadas = [r["id"] for r in linhas_rel if r["status"] == "duplicada"]
    # voz da IA: acústica (modelo do locutores.json aplicado ao áudio do corte) + conta pela EDL (zonas_ia)
    loc = LOC.carregar(vd)
    voz_ia = LOC.residuo_ia(str(wav), loc, palavras)
    zonas = (loc or {}).get("zonas_ia") or {}
    voz_ia["segundos_edl"] = round(sum(max(0.0, min(p.b + ALCA, zb) - max(p.a - ALCA, za))
                                       for p in pecas_da_edl(edl) for za, zb in zonas.get(p.fonte, [])), 3)
    voz_ia["limite"] = VOZ_IA_MAX
    # a acústica só pega vazamento ≳ 0,5 s (e conta ~metade); o curto (fim sibilante, cauda) sai da conta pela EDL
    ia_ok = voz_ia["segundos"] <= VOZ_IA_MAX and voz_ia["segundos_edl"] <= VOZ_IA_MAX
    falhou = bool(faltando) or wer_geral > WER_MAX or not av_ok or not dur_ok or not fps_ok or not ia_ok
    motivos = []
    if voz_ia["segundos"] > VOZ_IA_MAX:
        motivos.append(f"{voz_ia['segundos']:.2f}s de voz da IA detectados no áudio do corte (limite {VOZ_IA_MAX:g}s)")
    if voz_ia["segundos_edl"] > VOZ_IA_MAX:
        motivos.append(f"{voz_ia['segundos_edl']:.2f}s das peças da EDL dentro das zonas da IA (limite {VOZ_IA_MAX:g}s)")
    if not fps_ok:
        motivos.append(f"vídeo a {fps_v:g} fps ≠ projeto {FPS} fps")
    if faltando:
        motivos.append(f"{len(faltando)} linha(s) faltando: {', '.join(faltando)}")
    if wer_geral > WER_MAX:
        motivos.append(f"WER geral {wer_geral:.1%} > {WER_MAX:.0%}")
    if not av_ok:
        motivos.append(f"A/V fora de sincronia (Δ {abs(dv - da):.3f}s)")
    if not dur_ok:
        motivos.append(f"duração do vídeo ≠ soma das peças (Δ {abs(dv - soma):.3f}s)")

    L = [f"# QA do corte — {roteiro.get('slug') or vd.name}", "",
         f"Vídeo: `{rel(vd, video)}` · engine {engine} · {dt.datetime.now().astimezone().isoformat(timespec='seconds')}", "",
         f"**Resultado: {'FALHOU' if falhou else 'PASSOU'}**" + (f" — {'; '.join(motivos)}" if motivos else ""), "",
         f"- WER geral: **{wer_geral:.1%}** (limite {WER_MAX:.0%}; {tot_err} erros / {tot_n} palavras esperadas)",
         f"- Duração: vídeo {dv:.3f}s · áudio {da:.3f}s · soma das peças {soma:.3f}s · EDL {esperado:.3f}s"
         + (f" · alvo {alvo}s ({(dv - alvo) / alvo:+.0%})" if alvo else ""),
         f"- Sincronia A/V: {'OK' if av_ok else 'FALHOU'} (Δ {abs(dv - da) * 1000:.1f} ms; tolerância 1 frame = {FRAME * 1000:.1f} ms)",
         f"- Duração vs peças: {'OK' if dur_ok else 'FALHOU'} (Δ {abs(dv - soma) * 1000:.1f} ms)",
         f"- FPS: {'OK' if fps_ok else 'FALHOU'} ({fps_v:g} fps; projeto {FPS}) · {vs.get('width')}x{vs.get('height')} "
         f"{vs.get('pix_fmt')}",
         (f"- Voz da IA no corte: {'OK' if ia_ok else 'FALHOU'} — **{voz_ia['segundos']:.2f} s** detectados "
          f"(limite {VOZ_IA_MAX:g} s; modelo por quadro do `edicao/locutores.json`) · peças da EDL dentro das zonas "
          f"da IA: {voz_ia['segundos_edl']:.2f} s"
          + (" · trechos: " + ", ".join(f"{fmt_t(a)}–{fmt_t(b)}" for a, b in voz_ia["trechos"]) if voz_ia["trechos"] else "")
          if voz_ia["aplicavel"] else f"- Voz da IA no corte: não se aplica ({voz_ia.get('motivo')})"),
         "", "| Linha | Status | WER | Esperado (roteiro) | Ouvido no corte |", "|---|---|---|---|---|"]
    for r in linhas_rel:
        w = "—" if r["wer"] is None else f"{r['wer']:.1%}"
        L.append(f"| {r['id']} | {r['status']} | {w} | {r['esperado']} | {r['ouvido'] or '—'} |")
    L += ["", "## Trechos extras (fala fora do roteiro no corte)", ""]
    L += [f"- {fmt_t(x['inicio'])}–{fmt_t(x['fim'])}: \"{x['texto']}\"" for x in extras_rel] or ["- nenhum"]
    if duplicadas:
        L += ["", f"**Duplicadas:** {', '.join(duplicadas)} (a mesma linha aparece mais de uma vez no corte)"]
    if alvo and abs(dv - alvo) / alvo > 0.15:
        L += ["", f"> Aviso: duração {dv:.1f}s está {(dv - alvo) / alvo:+.0%} do alvo de {alvo}s (não reprova)."]
    (vd / "qa" / "diff.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    escrever_json(vd / "qa" / "verificacao.json", {
        "resultado": "FALHOU" if falhou else "PASSOU", "motivos": motivos, "wer_geral": round(wer_geral, 4),
        "linhas": linhas_rel, "extras": extras_rel, "duracao": {"video": dv, "audio": da, "pecas": soma,
                                                                 "edl": esperado, "alvo": alvo},
        "av_ok": av_ok, "duracao_ok": dur_ok, "engine": engine, "voz_ia": voz_ia, "voz_ia_ok": ia_ok,
        "fps": {"video": round(fps_v, 3), "projeto": FPS, "ok": fps_ok, "frame_s": round(FRAME, 6)},
        "formato": {"largura": vs.get("width"), "altura": vs.get("height"), "pix_fmt": vs.get("pix_fmt")}})
    for r in linhas_rel:
        log(f"   {r['id']:<5} {r['status']:<28} " + ("" if r["wer"] is None else f"WER {r['wer']:.1%}"))
    log(f"[verify] {'FALHOU' if falhou else 'PASSOU'} · WER geral {wer_geral:.1%} · vídeo {dv:.3f}s / áudio {da:.3f}s "
        f"(Δ {abs(dv - da) * 1000:.1f} ms) · extras {len(extras_rel)} · voz da IA "
        + (f"{voz_ia['segundos']:.2f}s (EDL {voz_ia['segundos_edl']:.2f}s)" if voz_ia["aplicavel"] else "n/a")
        + f" -> {rel(vd, vd / 'qa' / 'diff.md')}")
    for m in motivos:
        log(f"   motivo: {m}")
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
