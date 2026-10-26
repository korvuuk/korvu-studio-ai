"""Acabamento de áudio (master da voz) sem esmagar: compressão suave -> ganho LINEAR até −14 LUFS -> limitador de
true peak com sobreamostragem 4× -> AAC 256k. Nenhum EQ. (O loudnorm "dinâmico" antigo comprimia a voz: crest
17,8 -> 14,8 dB na revisão v2.)

uso:
  uv run python audio.py <entrada.mp4> <saida.mp4> [--audio-master edicao/corte-audio.wav | --sem-master]
                         [--lufs -14 --tp -1.5] [--razao 2 --ataque 10 --release 150] [--limpar]
                         [--musica trilha.mp3 --musica-db -22]
  uv run python audio.py --medir <arquivo> [--json] [--trecho INI FIM]

- VÍDEO: copiado da entrada (-c:v copy). ÁUDIO: do master sem perdas `edicao/corte-audio.wav` (24-bit, gravado pelo
  render_corte) quando existir — procurado na pasta `edicao/` acima da entrada e só se tiver a duração do vídeo —
  senão da própria entrada. Assim o ÚNICO encode com perdas é o AAC final (256k; voz mono nos 2 canais).
  EDL com cena extra `som: true`: o som dela só existe no render do Remotion -> usa o áudio da entrada (AVISO).
- Cadeia: RMS da fala medido -> acompressor leve 1,5:1 (limiar = RMS da fala + 9 dB, ataque 30 ms, release 300 ms,
  joelho suave, detecção RMS — mais forte inclina o timbre, ver RAZAO) -> ganho linear para −14 LUFS integrado ->
  alimiter a 192 kHz (4×, teto = true peak alvo − 0,5 dB,
  lookahead compensado: sem atraso) -> 48 kHz -> AAC. Mede a saída e corrige ganho/teto (até 4 passadas) até
  −14 ±0,3 LUFS e true peak ≤ −1,5 dBTP.
- --musica: trilha em loop, volume --musica-db, ducking (sidechaincompress com a voz), fade-out 1,5 s — somada
  depois da compressão da voz e antes do ganho/limitador.
- --limpar: redução de ruído SUAVE (passa-altas 60 Hz + afftdn com o piso medido) antes de tudo — só se o ruído
  incomodar (tira um pouco de brilho). A ingestão não faz mais redução de ruído.
- --medir: LUFS integrado, true peak e LRA (+ crest e energia por banda do --trecho INI FIM, em segundos).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

SCRIPTS_CORTE = Path(__file__).resolve().parents[2] / "corte-por-roteiro" / "scripts"
sys.path.insert(0, str(SCRIPTS_CORTE))
from common import (CORTE_AUDIO, FFMPEG, cadeia_limpeza_audio, duracao, energia_bandas, ffprobe_json,  # noqa: E402
                    ler_audio, run)

SR = 48000
BITRATE = "256k"
# Compressor = nivelador LEVE. Medido na voz do Carlos (L03/L10 do 2026-09-16): 2:1 com limiar NO RMS da fala
# (10/150 ms) inclinava +2,9 dB em 5–10 kHz (baixa as vogais altas, as sibilantes ficam) sem ganhar crest — quem
# controla os picos é o limitador (crest 17,8 -> ~14,2 dB). 1,5:1 a +9 dB, 30/300 ms: Δ agudos ≤ 1,3 dB.
RAZAO, ATAQUE_MS, RELEASE_MS, JOELHO = 1.5, 30.0, 300.0, 2.82843     # joelho ≈ 9 dB (suave)
LIMIAR_REL = 9.0           # dB acima do RMS da fala (limiar do compressor)
TOL_LUFS = 0.3
MARGEM_TP = 0.3            # teto do limitador abaixo do alvo de true peak (AAC + reamostragem sobem um pouco; a
                           # passada seguinte baixa o teto se o TP medido passar do alvo)


def tags_bt709(entrada: Path) -> list[str]:
    """O Remotion marca só a matriz (bt709/None/None). Sem reencodar, completa primárias/transferência bt709 no
    SPS (h264_metadata) e no contêiner — só para H.264 8-bit que já é bt709 ou sem marcação."""
    vs = next((s for s in ffprobe_json(entrada).get("streams", []) if s.get("codec_type") == "video"), {})
    if vs.get("codec_name") != "h264" or vs.get("color_space") not in (None, "", "unknown", "bt709"):
        return []
    return ["-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]


def _json_loudnorm(stderr: str) -> dict:
    blocos = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", stderr, re.S)
    if not blocos:
        raise RuntimeError("não achei a saída JSON do loudnorm:\n" + stderr[-1500:])
    return json.loads(blocos[-1])


# ---------------------------------------------------------------- medição
def medir(entrada: Path, musica: Path | None = None, musica_db: float = -22, limpar: bool = False,
          lufs: float = -14, tp: float = -1.5, lra: float = 11) -> dict:
    """LUFS integrado / true peak / LRA do áudio do arquivo (loudnorm só como medidor). (musica/limpar: legado.)"""
    dur = duracao(entrada)
    r = run([FFMPEG, "-hide_banner", "-nostdin", "-nostats", "-i", str(entrada), "-map", "0:a:0",
             "-af", f"loudnorm=I={lufs}:TP={tp}:LRA={lra}:print_format=json", "-t", f"{dur:.3f}", "-f", "null", "-"])
    return _json_loudnorm(r.stderr.decode("utf-8", "replace"))


def rms_fala_db(x: np.ndarray, sr: int = SR) -> tuple[float, float]:
    """-> (RMS da fala em dBFS — só quadros de 20 ms com fala —, piso de ruído p10 em dBFS)."""
    h = int(0.02 * sr)
    n = len(x) // h
    if n < 5:
        return -30.0, -70.0
    p = (x[: n * h].astype(np.float64).reshape(n, h) ** 2).mean(axis=1) + 1e-20
    db = 10 * np.log10(p)
    p10, p99 = np.percentile(db, [10, 99])
    ativo = db > max(p10 + 12.0, p99 - 40.0)
    return float(10 * np.log10(p[ativo].mean() if ativo.any() else p.mean())), float(p10)


def crest_fala(x: np.ndarray, sr: int = SR) -> float:
    """Pico / RMS da fala (dB) — o que o esmagamento reduz."""
    rms_db, _ = rms_fala_db(x, sr)
    return round(20 * np.log10(np.abs(x).max() + 1e-12) - rms_db, 1)


# ---------------------------------------------------------------- master de áudio
def achar_master(entrada: Path, dur_video: float) -> Path | None:
    """`edicao/corte-audio.wav` acima da entrada (edicao/cor/corte-cor.mp4, edicao/render-remotion.mp4…), com a
    duração do vídeo (±0,1 s). None se não houver, se a duração não bater ou se a EDL tiver extra com som."""
    for d in [entrada.resolve().parent, *entrada.resolve().parents]:
        if d.name == "edicao":
            m = d / CORTE_AUDIO
            if not m.exists():
                return None
            try:
                edl = json.loads((d / "edl.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                edl = {}
            if any(o.get("tipo") == "extra" and o.get("som") for o in edl.get("overlays", [])):
                print(f"[audio] AVISO: a EDL tem cena extra com som — usando o áudio de {entrada.name}, não o master")
                return None
            dm = duracao(m)
            if abs(dm - dur_video) > 0.1:
                print(f"[audio] AVISO: {m.name} tem {dm:.3f}s e o vídeo {dur_video:.3f}s — corte re-renderizado? "
                      f"usando o áudio de {entrada.name}")
                return None
            return m
    return None


def cadeia_voz(vi: int, limpar: bool, piso_db: float, limiar_db: float, razao: float, ataque: float,
               release: float) -> str:
    """Voz (mono) -> [limpeza opcional] -> compressor suave -> estéreo (mono duplicado)."""
    thr = min(1.0, max(0.000976563, 10 ** (limiar_db / 20)))
    comp = (f"acompressor=threshold={thr:.6f}:ratio={razao:g}:attack={ataque:g}:release={release:g}:"
            f"knee={JOELHO}:makeup=1:detection=rms:link=average")
    return (f"[{vi}:a:0]aformat=sample_fmts=flt:sample_rates={SR},pan=mono|c0=c0"
            + (f",{cadeia_limpeza_audio(piso_db)}" if limpar else "") + f",{comp},pan=stereo|c0=c0|c1=c0")


def grafo(voz: str, mi: int | None, musica_db: float, dur: float, cauda: str) -> str:
    if mi is None:
        return f"{voz},apad=whole_dur={dur:.3f}{cauda}[out]"
    fade = max(0.0, dur - 1.5)
    return (f"{voz},apad=whole_dur={dur:.3f},asplit=2[voz][sc];"
            f"[{mi}:a]aformat=sample_fmts=flt:sample_rates={SR}:channel_layouts=stereo,volume={musica_db}dB,"
            f"atrim=0:{dur:.3f},afade=t=out:st={fade:.3f}:d=1.5[mus];"
            f"[mus][sc]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[musd];"
            f"[voz][musd]amix=inputs=2:duration=first:normalize=0{cauda}[out]")


def limitador(teto_db: float) -> str:
    """True peak ≈ pico a 4× (192 kHz). latency=1 compensa o lookahead (sem atraso = A/V intacto)."""
    return (f"aresample={4 * SR},alimiter=limit={10 ** (teto_db / 20):.5f}:attack=1.5:release=60:level=false:"
            f"latency=1,aresample={SR}")


def normalizar(entrada: Path, saida: Path, musica: Path | None = None, musica_db: float = -22, lufs: float = -14,
               tp: float = -1.5, lra: float = 11, limpar: bool = False, master: Path | None = None,
               usar_master: bool = True, razao: float = RAZAO, ataque: float = ATAQUE_MS,
               release: float = RELEASE_MS, limiar_rel: float = LIMIAR_REL) -> dict:
    dur = duracao(entrada)
    if master is None and usar_master:
        master = achar_master(entrada, dur)
    fonte_voz = master or entrada
    entradas = ["-i", str(entrada)]
    vi = 0
    if master:
        entradas += ["-i", str(master)]
        vi = 1
    mi = None
    if musica:
        entradas += ["-stream_loop", "-1", "-i", str(musica)]
        mi = vi + 1
    x = ler_audio(fonte_voz, 0.0, None, "0:a:0")
    rms_db, piso = rms_fala_db(x)
    limiar = min(-0.5, rms_db + limiar_rel)
    voz = cadeia_voz(vi, limpar, piso, limiar, razao, ataque, release)
    print(f"[audio] voz: {fonte_voz.name}{' (master sem perdas)' if master else ' (áudio da entrada)'} · RMS da fala "
          f"{rms_db:.1f} dBFS · piso {piso:.1f} dBFS · crest {crest_fala(x):.1f} dB")
    print(f"[audio] compressor {razao:g}:1 · limiar {limiar:.1f} dBFS (RMS da fala {limiar_rel:+g} dB) · ataque "
          f"{ataque:g} ms · release {release:g} ms · joelho suave{' · + limpeza suave' if limpar else ''}")
    # passada 1: loudness da voz comprimida (+ música) -> ganho linear
    r = run([FFMPEG, "-hide_banner", "-nostdin", "-nostats", *entradas, "-filter_complex",
             grafo(voz, mi, musica_db, dur, f",loudnorm=I={lufs}:TP={tp}:LRA={lra}:print_format=json"),
             "-map", "[out]", "-t", f"{dur:.3f}", "-f", "null", "-"])
    m = _json_loudnorm(r.stderr.decode("utf-8", "replace"))
    ganho = lufs - float(m["input_i"])
    teto = tp - MARGEM_TP
    print(f"[audio] comprimido: I {m['input_i']} LUFS · TP {m['input_tp']} dBTP -> ganho {ganho:+.2f} dB, teto {teto:.2f} dBTP")
    saida.parent.mkdir(parents=True, exist_ok=True)
    final = {}
    for passada in range(1, 5):
        g = grafo(voz, mi, musica_db, dur, f",volume={ganho:.3f}dB,{limitador(teto)}")
        run([FFMPEG, "-hide_banner", "-nostdin", "-nostats", "-loglevel", "error", "-y", *entradas,
             "-filter_complex", g, "-map", "0:v:0", "-map", "[out]", "-c:v", "copy", *tags_bt709(entrada),
             "-c:a", "aac", "-b:a", BITRATE, "-ar", str(SR), "-ac", "2", "-t", f"{dur:.3f}", "-movflags", "+faststart",
             str(saida)])
        final = medir(saida, lufs=lufs, tp=tp, lra=lra)
        i_f, tp_f = float(final["input_i"]), float(final["input_tp"])
        print(f"[audio] passada {passada}: I {i_f:.2f} LUFS · TP {tp_f:.2f} dBTP · LRA {final['input_lra']} LU")
        if abs(i_f - lufs) <= TOL_LUFS and tp_f <= tp:
            break
        ganho += lufs - i_f
        if tp_f > tp:
            teto -= (tp_f - tp) + 0.1
    y = ler_audio(saida, 0.0, None, "0:a:0")
    res = {"medido": m, "final": final, "master": str(master) if master else None, "ganho_db": round(ganho, 2),
           "teto_db": round(teto, 2), "limiar_db": round(limiar, 1), "crest_entrada": crest_fala(x),
           "crest_saida": crest_fala(y)}
    print(f"[audio] resultado: I {float(final['input_i']):.1f} LUFS · TP {float(final['input_tp']):.1f} dBTP · crest da "
          f"fala {res['crest_entrada']:.1f} -> {res['crest_saida']:.1f} dB · AAC {BITRATE} -> {saida}")
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", nargs="?")
    ap.add_argument("saida", nargs="?")
    ap.add_argument("--medir", metavar="ARQUIVO", help="só mede e imprime LUFS / true peak / LRA")
    ap.add_argument("--json", action="store_true", help="(com --medir) imprime JSON")
    ap.add_argument("--trecho", nargs=2, type=float, metavar=("INI", "FIM"),
                    help="(com --medir) crest e energia por banda (dB rel. 60 Hz–16 kHz) deste trecho")
    ap.add_argument("--audio-master", type=Path, help="WAV sem perdas do corte (padrão: edicao/corte-audio.wav "
                                                      "acima da entrada, se a duração bater)")
    ap.add_argument("--sem-master", action="store_true", help="usa o áudio da própria entrada")
    ap.add_argument("--musica", type=Path)
    ap.add_argument("--musica-db", type=float, default=-22)
    ap.add_argument("--lufs", type=float, default=-14)
    ap.add_argument("--tp", type=float, default=-1.5)
    ap.add_argument("--lra", type=float, default=11, help="(só medição)")
    ap.add_argument("--razao", type=float, default=RAZAO, help=f"razão do compressor (padrão {RAZAO:g}; 1 = sem)")
    ap.add_argument("--ataque", type=float, default=ATAQUE_MS)
    ap.add_argument("--release", type=float, default=RELEASE_MS)
    ap.add_argument("--limiar", type=float, default=LIMIAR_REL,
                    help=f"limiar do compressor em dB acima do RMS da fala (padrão {LIMIAR_REL:+g}; menor = comprime mais)")
    ap.add_argument("--limpar", action="store_true", help="redução de ruído suave antes (tira um pouco de brilho)")
    a = ap.parse_args()
    if a.medir:
        m = medir(Path(a.medir), lufs=a.lufs, tp=a.tp, lra=a.lra)
        res = {"lufs": float(m["input_i"]), "true_peak": float(m["input_tp"]), "lra": float(m["input_lra"])}
        if a.trecho:
            res["trecho"] = energia_bandas(ler_audio(Path(a.medir), a.trecho[0], a.trecho[1], "0:a:0"))
        if a.json:
            print(json.dumps(res))
        else:
            print(f"LUFS integrado: {res['lufs']:.1f} | True peak: {res['true_peak']:.1f} dBTP | LRA: {res['lra']:.1f} LU")
            if a.trecho:
                print("Trecho " + " · ".join(f"{k} {v}" for k, v in res["trecho"].items()))
        return
    if not a.entrada or not a.saida:
        ap.error("informe <entrada> <saida> (ou --medir ARQUIVO)")
    ent, sai = Path(a.entrada), Path(a.saida)
    if ent.resolve() == sai.resolve():
        sys.exit("[ERRO] a saída precisa ser outro arquivo")
    if a.musica and not a.musica.exists():
        sys.exit(f"[ERRO] música não encontrada: {a.musica}")
    if a.audio_master and not a.audio_master.exists():
        sys.exit(f"[ERRO] master não encontrado: {a.audio_master}")
    normalizar(ent, sai, a.musica, a.musica_db, a.lufs, a.tp, a.lra, a.limpar, master=a.audio_master,
               usar_master=not a.sem_master, razao=a.razao, ataque=a.ataque, release=a.release, limiar_rel=a.limiar)


if __name__ == "__main__":
    main()
