"""Renderiza o corte a partir da EDL -> edicao/corte.mp4 (ou edicao/preview.mp4)

uso: uv run python render_corte.py <video_dir> [--preview] [--force|--auto]

- Recusa se edl.json não estiver com "aprovado": true (a menos que --preview ou --force/--auto).
- Vídeo: trim por frame de cada peça (segmentos menos cortes internos) + ENQUADRAMENTO da peça (punch-in do plano
  `zoom_pecas`/`zoom_origem` do edl.py: crop no intermediário 1440x2560 + scale lanczos em 10 bits -> 1080x1920;
  escala 1.00 = só reduz) + concat. O zoom é aplicado UMA vez, aqui (edl.json "zoom_no_corte": true; o Remotion
  não aplica de novo). EDL antiga sem "zoom_no_corte": nenhum zoom aqui (fica para o Remotion, como antes).
- Áudio SEM PERDAS: cada peça sai do master edicao/audio48k/<fonte>.wav (48 kHz 24-bit, do ingest) com "alças" de
  15 ms dos dois lados, cruzadas em 30 ms (linear, em float; montado em numpy, ver montar_audio) -> duração = soma das peças (±1 frame).
  Grava também edicao/corte-audio.wav (24-bit mono) = o áudio do corte sem perdas, que o audio.py (master) usa.
  Sem o master (ingest antigo): usa o AAC do intermediário (AVISO).
- Corte: 1080x1920, FPS_PROJETO (padrão 25) CFR, H.264 High 4:2:2 10-bit (yuv422p10le) CRF 12, tags bt709,
  AAC 48 kHz 256k (voz mono nos 2 canais). A câmera continua em V-Log: a cor (entrada + look) é a etapa seguinte.
- Preview: 540x960, 8-bit yuv420p, CRF 23, mesma timeline e MESMO plano de zoom. Trechos de câmera em log recebem
  a LUT de visualização 00-marca/cor/luts/entrada-camera.cube (lut3d tetraédrica); tela nunca.
- Exige fontes no FPS do projeto (trim por frame); senão pede ingest.py --force.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ALTURA, CORTE_AUDIO, ENC_INTERMEDIARIO, FFMPEG, FPS, FRAME, LARGURA, PIX_FMT_INTER,  # noqa: E402
                    SR, TAGS_709, avisar_uma_vez, duracao, duracao_pecas, duracoes_streams, edicao, esc_filtro,
                    ffprobe_json, filtro_vista_log, fmt_t, fonte_path, fps_de_stream, janela_zoom, ler_json, log,
                    pecas_da_edl, rel, resolver_video_dir, run, tipo_da_fonte, verificar_decodificavel,
                    wav48k_path)

ALCA = 0.015      # s de cada lado
XFADE = 0.03      # = 2 * ALCA
SETPARAMS_709 = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"
SCALE_CORTE = "lanczos+accurate_rnd+full_chroma_int"


def conferir_fontes(caminhos: dict) -> dict[str, tuple[int, int]]:
    """O trim é por número de frame: fonte fora do FPS do projeto = A/V e duração errados. -> {fonte: (w, h)}"""
    erros, dims = [], {}
    for f, c in caminhos.items():
        vs = next((s for s in ffprobe_json(c)["streams"] if s.get("codec_type") == "video"), {})
        dims[f] = (int(vs.get("width") or LARGURA), int(vs.get("height") or ALTURA))
        fps = fps_de_stream(vs)
        if abs(fps - FPS) > 0.01:
            erros.append(f"{f} está a {fps:g} fps")
        elif vs.get("pix_fmt") != PIX_FMT_INTER:
            log(f"   [AVISO] {f} em {vs.get('pix_fmt')} (esperado {PIX_FMT_INTER}) — ingest antigo? "
                "rode ingest.py --force")
    if erros:
        sys.exit(f"[ERRO] {'; '.join(erros)} — o projeto é {FPS} fps (FPS_PROJETO). Rode ingest.py --force.")
    return dims


FONTES_ROTULO = ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
                 "/Library/Fonts/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def rotulos_extras(edl: dict) -> str:
    """Preview: 'EXTRA E01 · split' queimado durante cada cena extra (fundo vermelho se FALTANDO).
    A composição de verdade (split/full/card) só acontece no Remotion."""
    ex = [o for o in edl.get("overlays", []) if o.get("tipo") == "extra"]
    fonte = next((f for f in FONTES_ROTULO if Path(f).exists()), None)
    if not ex or not fonte:
        if ex:
            log("   [AVISO] sem fonte TTF para os rótulos EXTRA do preview")
        return ""
    h = 0.5 / FPS
    fs = []
    for o in ex:
        txt = f"EXTRA {o['extra']} · {o.get('modo') or 'split'}" + (" · FALTANDO" if o.get("faltando") else "")
        txt = "".join(c for c in txt if c not in "'\\:%")
        box = "red@0.9" if o.get("faltando") else "black@0.65"
        fs.append(f"drawtext=fontfile={esc_filtro(fonte)}:text='{txt}':fontsize=26:fontcolor=white:box=1:"
                  f"boxcolor={box}:boxborderw=10:x=(w-tw)/2:y=96:"
                  f"enable='between(t,{max(0.0, o['saida_inicio'] - h):.4f},{o['saida_fim'] - h:.4f})'")
    return ",".join(fs)


def enquadramento(p, dims: tuple[int, int], tipo: str, com_zoom: bool, W: int, H: int, flags: str) -> str:
    """Filtro de uma peça -> W x H: câmera/celular = crop do punch-in (ponto fixo na origem/rosto) + scale;
    tela = cabe inteira (pad)."""
    sw, sh = dims
    if tipo == "tela":
        return (f"scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags={flags},"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black")
    e = p.escala if com_zoom else 1.0
    cw, ch, x, y = janela_zoom(sw, sh, e, p.origem, W, H)
    if cw < W and W == LARGURA:
        avisar_uma_vez(f"{p.fonte}: zoom {e:.2f} AMPLIA o intermediário {sw}x{sh} (recorte {cw}x{ch} < {W}) — "
                       "rode ingest.py --force (intermediário 1440x2560)")
    return (f"crop={cw}:{ch}:{x}:{y}," if (cw, ch) != (sw, sh) else "") + f"scale={W}:{H}:flags={flags}"


def _ler_audio(src: Path, mono_do_canal0: bool) -> np.ndarray:
    cmd = [FFMPEG, "-v", "error", "-nostdin", "-i", str(src)]
    cmd += ["-af", "pan=mono|c0=c0"] if mono_do_canal0 else ["-ac", "1"]
    cmd += ["-ar", str(SR), "-f", "f32le", "-"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"não consegui ler o áudio de {src}: {r.stderr.decode(errors='replace')[-300:]}")
    return np.frombuffer(r.stdout, np.float32)


def montar_audio(pecas, src_a: dict, dur_a: dict, master: dict, destino: Path) -> None:
    """Peças com alças de ALCA s, encadeadas por cruzamento linear de XFADE s (= acrossfade c1=tri:c2=tri)."""
    cache: dict[str, np.ndarray] = {}
    K, n_x = len(pecas), int(round(XFADE * SR))
    rampa = np.linspace(0.0, 1.0, n_x, endpoint=False, dtype=np.float32) if n_x else None
    saida = np.zeros(0, np.float32)
    for k, p in enumerate(pecas):
        if p.fonte not in cache:
            cache[p.fonte] = _ler_audio(src_a[p.fonte], not master[p.fonte])
        x = cache[p.fonte]
        pre = ALCA if k > 0 else 0.0
        pos = ALCA if k < K - 1 else 0.0
        a0, a1 = p.a - pre, p.b + pos
        falta_pre, falta_pos = max(0.0, -a0), max(0.0, a1 - dur_a[p.fonte])
        a0, a1 = max(0.0, a0), min(a1, dur_a[p.fonte])
        s0, s1 = int(round(a0 * SR)), int(round(a1 * SR))
        trecho = np.concatenate([np.zeros(int(round(falta_pre * SR)), np.float32), x[s0:s1],
                                 np.zeros(int(round(falta_pos * SR)), np.float32)])
        if k == 0 or not n_x or len(saida) < n_x or len(trecho) < n_x:
            saida = np.concatenate([saida, trecho])
            continue
        cauda = saida[-n_x:] * (1.0 - rampa) + trecho[:n_x] * rampa
        saida = np.concatenate([saida[:-n_x], cauda, trecho[n_x:]])
    r = subprocess.run([FFMPEG, "-v", "error", "-nostdin", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-c:a", "pcm_f32le", str(destino)], input=saida.astype(np.float32).tobytes(),
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"não consegui gravar {destino}: {r.stderr.decode(errors='replace')[-300:]}")


def montar_grafo(vd: Path, edl: dict, preview: bool):
    pecas = pecas_da_edl(edl)
    if not pecas:
        sys.exit("[ERRO] a EDL não tem segmentos/peças para renderizar")
    com_zoom = bool(edl.get("zoom_no_corte"))
    if not com_zoom and any(p.escala > 1.0 for p in pecas):
        log("   [AVISO] EDL sem plano de zoom (\"zoom_no_corte\") — zoom fica para o Remotion; rode edl.py --recalcular")
    usadas: list[str] = []
    for p in pecas:
        if p.fonte not in usadas:
            usadas.append(p.fonte)
    vidx = {f: k for k, f in enumerate(usadas)}
    caminhos = {f: fonte_path(vd, edl, f) for f in usadas}
    dims = conferir_fontes(caminhos)
    info_f = ler_json(vd / "edicao" / "fontes.json", padrao={"fontes": {}}).get("fontes", {})
    entradas = [caminhos[f] for f in usadas]
    # Áudio: master WAV sem perdas, UMA ENTRADA POR PEÇA (-ss/-t), não uma por fonte.
    # 2026-09-18: com uma entrada por fonte, reusar o mesmo pad para peças fora de ordem no tempo (o take da
    # L11 vinha ANTES do take da L10 no mesmo arquivo) fazia o ffmpeg perder o trecho — 9,7 s sumiram sem um
    # único aviso. Só aparece com gravação em várias partes e linhas repetidas fora de ordem.
    src_a, dur_a, master = {}, {}, {}
    for f in usadas:
        w = wav48k_path(vd, f)
        master[f] = w.exists()
        if not master[f]:
            log(f"   [AVISO] {f}: sem master {rel(vd, w)} — áudio do AAC do intermediário (rode ingest.py --force)")
        src_a[f] = w if master[f] else caminhos[f]
        dur_a[f] = duracao(src_a[f])
    W, H = (540, 960) if preview else (LARGURA, ALTURA)
    flags = "bicubic" if preview else SCALE_CORTE
    g, K = [], len(pecas)
    for k, p in enumerate(pecas):
        i = vidx[p.fonte]
        f0, f1 = int(round(p.a * FPS)), int(round(p.b * FPS))
        tipo = (info_f.get(p.fonte) or {}).get("tipo") or tipo_da_fonte(p.fonte)
        enq = enquadramento(p, dims[p.fonte], tipo, com_zoom, W, H, flags)
        g.append(f"[{i}:v:0]trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS,{enq},"
                 f"format={PIX_FMT_INTER},setsar=1[v{k}]")
    # Áudio montado FORA do ffmpeg (2026-10-01). Com uma entrada -ss/-t por peça + cadeia de acrossfade, o ffmpeg 7.1
    # falhava de forma INTERMITENTE ("Could not open encoder before EOF", nada escrito) — o mesmo trecho passava
    # numa tentativa e falhava na seguinte; com 43 entradas falhava sempre. Aqui é a mesma conta (alças de 15 ms,
    # cruzamento linear de 30 ms = acrossfade c1=tri:c2=tri, em float), e o ffmpeg recebe UM arquivo pronto.
    montado = vd / "edicao" / (".audio-montado-preview.wav" if preview else ".audio-montado.wav")
    montar_audio(pecas, src_a, dur_a, master, montado)
    ia = len(entradas)
    entradas.append(montado)
    vin = "".join(f"[v{k}]" for k in range(K))
    if preview:
        # a timeline do concat = timeline da EDL, então os trechos de log (saida_*) valem direto no `t`
        vista = filtro_vista_log(vd, edl)
        cadeia = f"{vista},scale=out_color_matrix=bt709:out_range=tv," if vista else ""
        cadeia += "format=yuv420p"
        rotulos = rotulos_extras(edl)
        if rotulos:
            cadeia += f",{rotulos}"
    else:
        cadeia = f"format={PIX_FMT_INTER}"
    g.append(f"{vin}concat=n={K}:v=1:a=0,{cadeia},{SETPARAMS_709}[vout]")
    g.append(f"[{ia}:a:0]aformat=sample_fmts=flt:sample_rates={SR}:channel_layouts=mono[amix]")
    if preview:
        g.append("[amix]pan=stereo|c0=c0|c1=c0[aenc]")
    else:                                   # AAC (mono nos 2 canais, p/ tocar) + WAV 24-bit sem perdas p/ o master
        g.append("[amix]asplit=2[a1][awav];[a1]pan=stereo|c0=c0|c1=c0[aenc]")
    info = {"zoom": com_zoom, "master": all(master.values()),
            "escalas": [p.escala if com_zoom else 1.0 for p in pecas]}
    return entradas, ";\n".join(g), duracao_pecas(pecas), K, info


def renderizar(vd: Path, preview: bool = False, saida: Path | None = None) -> dict:
    ed = edicao(vd)
    edl = ler_json(ed / "edl.json")
    fps_edl = float(edl.get("fps") or FPS)
    if abs(fps_edl - FPS) > 0.01:
        sys.exit(f"[ERRO] edl.json está a {edl.get('fps')} fps e o projeto a {FPS} (FPS_PROJETO) — "
                 "rode ingest.py --force e edl.py --recalcular")
    saida = saida or (ed / ("preview.mp4" if preview else "corte.mp4"))
    wav_saida = saida.with_name(CORTE_AUDIO) if not preview else None
    entradas, grafo, esperado, K, info = montar_grafo(vd, edl, preview)
    script = ed / (".grafo-preview.txt" if preview else ".grafo-corte.txt")
    script.write_text(grafo, encoding="utf-8")
    if preview:
        venc = ["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-profile:v", "high", "-pix_fmt", "yuv420p"]
        aenc = ["-c:a", "aac", "-b:a", "128k", "-ar", str(SR)]
    else:
        venc = list(ENC_INTERMEDIARIO)
        aenc = ["-c:a", "aac", "-b:a", "256k", "-ar", str(SR)]
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y"]
    for e in entradas:                      # caminho simples, ou lista de argumentos (-ss/-t/-i) de uma peça
        cmd += [str(x) for x in e] if isinstance(e, (list, tuple)) else ["-i", str(e)]
    cmd += ["-filter_complex_script", str(script), "-map", "[vout]", "-map", "[aenc]", *venc,
            "-r", str(FPS), "-fps_mode", "cfr", *TAGS_709, *aenc, "-ac", "2", "-movflags", "+faststart", str(saida)]
    if wav_saida:
        cmd += ["-map", "[awav]", "-c:a", "pcm_s24le", "-ar", str(SR), "-ac", "1", str(wav_saida)]
    t0 = time.time()
    esc = info["escalas"]
    n_punch = sum(1 for e in esc if e > 1.0)
    log(f"[render] {'preview' if preview else 'corte'}: {K} peças, {esperado:.3f}s esperados, {FPS} fps, "
        f"{'yuv420p 540x960' if preview else PIX_FMT_INTER + ' 1080x1920'} -> {rel(vd, saida)}"
        + (f"{' + ' + rel(vd, wav_saida) if wav_saida else ''}"))
    log(f"   zoom: " + (f"{n_punch} peça(s) fechada(s) · {K - n_punch} aberta(s) · "
                         f"{sum(1 for a, b in zip(esc, esc[1:]) if abs(a - b) >= 0.04)}/{max(0, K - 1)} cortes com troca"
                         if info["zoom"] else "nenhum (EDL sem plano)")
        + f" · áudio {'master WAV 24-bit (sem perdas)' if info['master'] else 'AAC do intermediário'}")
    run(cmd)
    verificar_decodificavel(saida)
    ds = duracoes_streams(saida)
    dv, da = ds.get("video") or 0.0, ds.get("audio") or 0.0
    dw = duracao(wav_saida) if wav_saida else da
    ok = (abs(dv - esperado) <= FRAME + 1e-3 and abs(da - esperado) <= FRAME + 1e-3 and abs(dv - da) <= FRAME + 1e-3
          and abs(dw - esperado) <= FRAME + 1e-3)
    log(f"[render] pronto em {time.time() - t0:.1f}s · vídeo {dv:.3f}s · áudio {da:.3f}s"
        + (f" · wav {dw:.3f}s" if wav_saida else "")
        + f" · esperado {esperado:.3f}s · {'OK (±1 frame)' if ok else 'ATENÇÃO: diferença > 1 frame'}")
    if not ok:
        log("   [AVISO] durações fora da tolerância — ver troubleshooting no SKILL.md")
    return {"arquivo": str(saida), "video": dv, "audio": da, "wav": str(wav_saida) if wav_saida else None,
            "esperado": esperado, "ok": ok, "pecas": K, "duracao_fmt": fmt_t(esperado), "zoom": info["zoom"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    ap.add_argument("--preview", action="store_true", help="540x960 rápido em edicao/preview.mp4 (não exige aprovação)")
    ap.add_argument("--force", "--auto", dest="force", action="store_true",
                    help="renderiza mesmo sem aprovado=true (só se o Carlos pedir --auto)")
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    edl = ler_json(edicao(vd) / "edl.json")
    if not args.preview and edl.get("aprovado") is not True and not args.force:
        sys.exit("[BLOQUEADO] edl.json ainda não está aprovado (\"aprovado\": true). Peça a aprovação do Carlos "
                 "ou use --preview. (--force/--auto só se o Carlos pedir explicitamente.)")
    r = renderizar(vd, preview=args.preview)
    sys.exit(0 if r["ok"] else 2)


if __name__ == "__main__":
    main()
