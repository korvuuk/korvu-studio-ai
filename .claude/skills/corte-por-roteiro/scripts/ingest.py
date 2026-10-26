"""Ingestão dos brutos -> edicao/fontes/*.mp4 (principal) + edicao/extras/* (cenas extras) + edicao/fontes.json

uso: uv run python ingest.py <video_dir> [--force] [--faixa-audio N] [--limpar-ruido]

Estrutura (docs/contratos.md §0): brutos/principal/ = o Carlos falando (A-roll: camera-01.mov, celular-01.mov…);
brutos/extras/ = cenas extras nomeadas pelo ID (E01-chatgpt.mov, E02.png, E03-noticia.mp4…). Legado: arquivos
soltos em brutos/ (camera-*/celular-* = principal; tela-*, E01-* e imagens = extras).

PRINCIPAL — todas as fontes no MESMO formato: 1440x2560 (SUPERSAMPLED: o punch-in do corte recorta daqui e
reduz para 1080x1920 sem ampliar), FPS_PROJETO (padrão 25) CFR, H.264 High 4:2:2 10-bit (yuv422p10le, CRF 12),
tags bt709. O arquivo inteiro é decodificado para conferir (libx264 4:2:2 10-bit multithread do ffmpeg 7.1 tem
bug em larguras 1920/3840); se falhar, recodifica em HEVC main422-10.
ÁUDIO (sem perdas): edicao/audio48k/<stem>.wav = 48 kHz 24-bit mono da faixa a:0 da câmera (--faixa-audio N;
se a:0 estiver muda, a faixa com melhor nível/SNR), só com passa-altas suave 60 Hz 12 dB/oit. — SEM redução de
ruído por padrão (--limpar-ruido = afftdn suave com o piso medido). O render_corte monta o áudio do corte a partir
deste WAV; o AAC dentro do fontes/<stem>.mp4 é só para tocar o arquivo. edicao/audio16k/<stem>.wav (análise e
transcrição) sai do mesmo WAV.
- camera-* (padrão; Lumix S5IIX 4K V-Log/V-Gamut 4:2:2 10-bit): fica em LOG — nenhuma LUT/conversão aqui
  (a transformação de entrada é do colorista, /cor). "perfil": CAMERA_PERFIL (padrão "vlog").
  4K/C4K -> 1440x2560 com lanczos, saída em 10 bits (V-Log full range -> limitado, out_range=tv).
- celular-*: HDR (HLG/PQ) -> tone-map para SDR bt709 (zscale + tonemap=hable); "perfil": "sdr".
- *-cor.* (ex.: camera-00-cor.mov): amostra de cor para o colorista — não convertida, transcrita nem usada na
  EDL; só listada no fontes.json com "tipo": "amostra_cor".
EXTRAS (nunca transcritos) -> fontes.json["extras"][ID]; tipo de roteiro.json.extras[].tipo (senão pelo nome):
- vídeo: edicao/extras/<ID>.mp4, 1080 de largura (mantém proporção), FPS_PROJETO CFR. tipo camera = V-Log
  10-bit 4:2:2 (para o colorista, que gera <ID>-cor.mp4); tela/video/print = SDR 8-bit yuv420p (HDR -> tone-map).
- imagem: edicao/extras/<ID>.png (lado maior ≤ 2160 px).
- extra declarado no roteiro sem arquivo -> listado com "faltando": true (a EDL entra com placeholder).
fps: igual ao projeto -> só CFR; múltiplo (50 -> 25) -> 1 de cada 2; outro (30/60) -> filtro fps + [AVISO].
Rotação (displaymatrix / "vertical position info") respeitada pelo autorotate do ffmpeg: 3840x2160 (ou C4K
4096x2160) com rotação -> 1440x2560 (crop central 9:16); principal horizontal sem rotação -> crop central (AVISO).
Pula arquivos sem mudança (mtime + tamanho + mesma configuração) a menos que --force.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ALTURA_INTER, CAMERA_PERFIL, ENC_INTERMEDIARIO, EXT_IMAGEM, FPS, GOP, LARGURA,  # noqa: E402
                    LARGURA_INTER, PCM_MASTER, PIX_FMT_INTER, SR, TAGS_709, TIPO_AMOSTRA_COR, cadeia_audio_ingest,
                    duracao, edicao, eh_log, escrever_json, ffmpeg, ffprobe_json, fps_de_stream, id_do_extra,
                    ler_json, listar_brutos, log, normalizar_id_extra, rel, resolver_video_dir, stem_limpo,
                    tipo_da_fonte, tipo_extra_por_nome, verificar_decodificavel, wav48k_path)

HDR_TRC = {"arib-std-b67": "arib-std-b67", "smpte2084": "smpte2084"}
# o ffmpeg 7 usa as propriedades do frame para marcar o stream: força bt709 explicitamente
SETPARAMS_709 = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"
SCALE_FLAGS = "lanczos+accurate_rnd+full_chroma_int"
# mudou -> reingere (v2: intermediário 1440x2560 + master WAV 24-bit sem denoise)
CFG_INGEST = f"{FPS}|{PIX_FMT_INTER}|{CAMERA_PERFIL}|{LARGURA_INTER}x{ALTURA_INTER}|audio-v2"
# fallback se o H.264 4:2:2 10-bit sair ilegível: HEVC 4:2:2 10-bit (o render_corte decodifica; o colorista lê o corte)
ENC_INTER_HEVC = ["-c:v", "libx265", "-preset", "fast", "-crf", "14", "-profile:v", "main422-10",
                  "-pix_fmt", PIX_FMT_INTER, "-x265-params", "log-level=error"]
FAIXA_MUDA_DB = -60.0      # p95 (quadros de 10 ms) abaixo disto = faixa sem fala
CFG_EXTRA = f"{FPS}|extra-v1|{CAMERA_PERFIL}"
LADO_MAX_IMAGEM = 2160
ZSCALE_HDR = ("zscale=tin={tin}:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,"
              "zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv")


def rotacao(vs: dict) -> int:
    for sd in vs.get("side_data_list", []) or []:
        if "rotation" in sd:
            try:
                return int(round(float(sd["rotation"])))
            except (TypeError, ValueError):
                pass
    try:
        return int(vs.get("tags", {}).get("rotate", 0))
    except (TypeError, ValueError):
        return 0


def analisar(path: Path) -> dict:
    info = ffprobe_json(path)
    vs = next((s for s in info["streams"] if s.get("codec_type") == "video"
               and not s.get("disposition", {}).get("attached_pic")), None)
    if vs is None:
        raise RuntimeError(f"{path.name}: sem stream de vídeo")
    aus = [s for s in info["streams"] if s.get("codec_type") == "audio"]
    au = aus[0] if aus else None
    w, h = int(vs["width"]), int(vs["height"])
    rot = rotacao(vs)
    if abs(rot) % 180 == 90:          # displaymatrix de 90°: o autorotate entrega o quadro em pé
        w, h = h, w
    trc = (vs.get("color_transfer") or "").lower()
    prim = (vs.get("color_primaries") or "").lower()
    mat = (vs.get("color_space") or "").lower()
    hdr = trc in HDR_TRC or prim == "bt2020" and trc not in ("bt709", "", "unknown")
    return {"w": w, "h": h, "rot": rot, "trc": trc, "prim": prim, "mat": mat, "hdr": bool(hdr),
            "pix_fmt": vs.get("pix_fmt"), "codec": f"{vs.get('codec_name')} {vs.get('profile') or ''}".strip(),
            "fps": fps_de_stream(vs), "fps_str": vs.get("avg_frame_rate") or vs.get("r_frame_rate"),
            "tem_audio": au is not None, "n_audio": len(aus),
            "duracao": float(info["format"].get("duration") or 0)}


def decidir_perfil(tipo: str, a: dict, avisos: list) -> tuple[str, bool]:
    """-> (perfil de saída, converter HDR->SDR?). Câmera em log fica em log (sem conversão)."""
    if tipo == "camera" and eh_log(CAMERA_PERFIL):
        if a["trc"] in HDR_TRC:
            avisos.append(f"câmera marcada como HDR ({a['trc']}), não {CAMERA_PERFIL}: tone-map para SDR bt709 "
                          f"(se gravou em HLG, ajuste CAMERA_PERFIL)")
            return "sdr", True
        return CAMERA_PERFIL, False
    if a["hdr"]:
        avisos.append(f"HDR detectado ({a['trc'] or a['prim']}): tone-map para SDR bt709")
        return "sdr", True
    return "sdr", False


def nota_fps(a: dict, avisos: list) -> str:
    src = a["fps"]
    if src <= 0:
        avisos.append(f"fps da fonte desconhecido: forçado a {FPS} fps CFR")
        return f"?->{FPS}"
    if abs(src - FPS) <= 0.01:
        return f"{FPS}"
    razao = src / FPS
    if round(razao) >= 2 and abs(razao - round(razao)) <= 0.001:
        return f"{src:g}->{FPS} (1 de cada {round(razao)})"
    avisos.append(f"{src:.3f}".rstrip("0").rstrip(".") + f" fps -> {FPS} fps com o filtro fps (quadros descartados/"
                  f"duplicados; movimento pode 'pular'). Grave a {FPS} ou {2 * FPS} fps quando der.")
    return f"{src:g}->{FPS} (filtro fps)"


# ---------------------------------------------------------------- principal
def filtro_video(tipo: str, a: dict, converter_hdr: bool, avisos: list) -> str:
    f = [f"fps={FPS}"]
    W, H = LARGURA_INTER, ALTURA_INTER
    if tipo in ("camera", "celular"):
        if a["w"] > a["h"]:
            avisos.append("vídeo horizontal (sem rotação de vertical): crop central para 9:16 (confira o enquadramento)")
        # 4K -> 1440x2560 (supersampled p/ o punch-in do corte): lanczos com saída direta em 10 bits
        # out_range=tv: a Lumix grava V-Log em full range (0–1023, preto em ~128 = 0,125 da curva). Converter
        # para limitado aqui torna a tag "tv" verdadeira e o colorista (in_range=tv) recupera os códigos V-Log certos.
        f.append(f"scale={W}:{H}:force_original_aspect_ratio=increase:out_range=tv:flags={SCALE_FLAGS}")
        f.append(f"format={PIX_FMT_INTER}")
        f.append(f"crop={W}:{H}")
    else:  # tela no principal (raro): inteira dentro de 1440x2560 (pad preto); nunca recebe zoom
        f.append(f"scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2:out_range=tv:"
                 f"flags={SCALE_FLAGS}")
        f.append(f"format={PIX_FMT_INTER}")
        f.append(f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black")
    if converter_hdr:
        f.append(ZSCALE_HDR.format(tin=HDR_TRC.get(a["trc"], "arib-std-b67")))
    f.append(f"setsar=1,format={PIX_FMT_INTER}")
    f.append(SETPARAMS_709)
    return ",".join(f)


def medir_faixas(src: Path, n: int) -> list[dict]:
    """Nível de cada faixa de áudio (8 kHz mono, quadros de 10 ms): piso (p10), fala (p95), pico e SNR — 1 leitura."""
    import tempfile

    import numpy as np
    import soundfile as sf
    out = []
    with tempfile.TemporaryDirectory() as td:
        args = ["-i", str(src)]
        for k in range(n):
            args += ["-map", f"0:a:{k}", "-ac", "1", "-ar", "8000", "-c:a", "pcm_f32le", str(Path(td) / f"a{k}.wav")]
        ffmpeg(args)
        for k in range(n):
            x, _ = sf.read(Path(td) / f"a{k}.wav", dtype="float32")
            m = len(x) // 80 * 80
            fr = x[:m].reshape(-1, 80) if m else np.zeros((1, 80), np.float32)
            db = 10 * np.log10((fr.astype(np.float64) ** 2).mean(axis=1) + 1e-20)
            p10, p95 = np.percentile(db, [10, 95])
            out.append({"faixa": k, "piso_db": round(float(p10), 1), "fala_db": round(float(p95), 1),
                        "pico_db": round(float(20 * np.log10(np.abs(x).max() + 1e-12)) if len(x) else -200.0, 1),
                        "snr_db": round(float(p95 - p10), 1)})
    return out


def escolher_faixa(stats: list[dict], pedida: int | None, avisos: list) -> int:
    """a:0 (ou --faixa-audio N); se a:0 estiver muda, a faixa com fala de melhor SNR/nível."""
    if pedida is not None:
        if not 0 <= pedida < len(stats):
            sys.exit(f"[ERRO] --faixa-audio {pedida}: o arquivo tem {len(stats)} faixa(s) de áudio (0…{len(stats) - 1})")
        if stats[pedida]["fala_db"] < FAIXA_MUDA_DB:
            avisos.append(f"faixa a:{pedida} (pedida) parece muda: fala p95 {stats[pedida]['fala_db']} dB")
        return pedida
    if stats[0]["fala_db"] >= FAIXA_MUDA_DB:
        return 0
    melhor = max(stats, key=lambda s: (s["fala_db"] >= FAIXA_MUDA_DB, s["snr_db"], s["fala_db"]))
    avisos.append(f"faixa a:0 muda (fala p95 {stats[0]['fala_db']} dB): usando a:{melhor['faixa']} "
                  f"(fala {melhor['fala_db']} dB, SNR {melhor['snr_db']} dB)")
    return melhor["faixa"]


def ingerir(src: Path, dst: Path, wav16: Path, wav48: Path, tipo: str, a: dict, converter_hdr: bool, avisos: list,
            faixa_pedida: int | None = None, limpar_ruido: bool = False) -> dict:
    """-> info do áudio {faixa, faixas, cadeia, limpar_ruido, encoder}. Ordem: master WAV (sem perdas) ->
    vídeo 1440x2560 (+ AAC do master, só para tocar) -> decodifica tudo -> audio16k do master."""
    vf = filtro_video(tipo, a, converter_hdr, avisos)
    wav48.parent.mkdir(parents=True, exist_ok=True)
    info = {"faixa": None, "faixas": [], "cadeia": None, "limpar_ruido": bool(limpar_ruido)}
    if not a["tem_audio"]:
        ffmpeg(["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", f"{a['duracao']:.3f}", *PCM_MASTER, str(wav48)])
        avisos.append("sem áudio: trilha silenciosa adicionada")
    else:
        stats = medir_faixas(src, a["n_audio"])
        k = escolher_faixa(stats, faixa_pedida, avisos)
        cad = cadeia_audio_ingest(limpar_ruido, stats[k]["piso_db"])
        ffmpeg(["-i", str(src), "-map", f"0:a:{k}", "-af", f"aresample={SR},{cad}", *PCM_MASTER, str(wav48)])
        info.update(faixa=k, faixas=stats, cadeia=cad)
    dst.parent.mkdir(parents=True, exist_ok=True)

    def codificar(venc: list) -> None:
        ffmpeg(["-i", str(src), "-i", str(wav48), "-map", "0:v:0", "-map", "1:a:0", "-vf", vf,
                *venc, "-g", str(GOP), "-fps_mode", "cfr", "-r", str(FPS), *TAGS_709,
                "-c:a", "aac", "-b:a", "256k", "-ar", str(SR), "-ac", "1",
                "-movflags", "+faststart", "-metadata:s:v:0", "rotate=0", str(dst)])
        verificar_decodificavel(dst, segundos=None)        # o arquivo inteiro (bug do x264 4:2:2 10-bit)

    try:
        codificar(ENC_INTERMEDIARIO)
        info["encoder"] = "libx264 high422"
    except RuntimeError as e:
        avisos.append(f"H.264 4:2:2 10-bit {LARGURA_INTER}x{ALTURA_INTER} ilegível ({str(e).splitlines()[0][:120]}) — "
                      "recodificado em HEVC main422-10")
        codificar(ENC_INTER_HEVC)
        info["encoder"] = "libx265 main422-10"
    wav16.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg(["-i", str(wav48), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav16)])
    return info


def registrar_amostra_cor(vd: Path, src: Path, stem: str, ed: Path) -> dict:
    """camera-00-cor.mov & cia.: só listada (o colorista usa o bruto). Remove restos de ingest antigo."""
    import re
    a = analisar(src)
    for velho in (ed / "fontes" / f"{stem}.mp4", ed / "audio16k" / f"{stem}.wav", wav48k_path(vd, stem)):
        velho.unlink(missing_ok=True)
    base = re.sub(r"[-_]cor$", "", stem) or "camera"          # camera-00-cor -> camera-00
    perfil = CAMERA_PERFIL if tipo_da_fonte(base) == "camera" and a["trc"] not in HDR_TRC else "sdr"
    log(f"[ingest] {src.name}: amostra de cor ({a['w']}x{a['h']}@{a['fps']:g}, {a['duracao']:.1f}s) — "
        "não ingerida/transcrita, fora da EDL (usar no /cor ou /criar-lut)")
    st = src.stat()
    return {"tipo": TIPO_AMOSTRA_COR, "arquivo": None, "bruto": rel(vd, src), "perfil": perfil,
            "duracao": round(a["duracao"], 3), "original": f"{a['w']}x{a['h']}@{a['fps_str']}",
            "codec_original": f"{a['codec']} {a['pix_fmt']}", "rotacao": a["rot"],
            "avisos": ["amostra de cor: fora do corte"], "mtime": st.st_mtime, "tamanho": st.st_size}


def ingerir_principal(vd: Path, ed: Path, arquivos: list[Path], antigo: dict, force: bool,
                      faixa_pedida: int | None = None, limpar_ruido: bool = False) -> dict:
    fontes = {}
    cfg = f"{CFG_INGEST}|faixa={faixa_pedida}|limpar={int(limpar_ruido)}"
    for src in arquivos:
        stem = stem_limpo(src)
        tipo = tipo_da_fonte(stem)
        if tipo == TIPO_AMOSTRA_COR:
            fontes[stem] = registrar_amostra_cor(vd, src, stem, ed)
            continue
        dst = ed / "fontes" / f"{stem}.mp4"
        wav = ed / "audio16k" / f"{stem}.wav"
        wav48 = wav48k_path(vd, stem)
        st = src.stat()
        old = antigo.get(stem)
        if (not force and old and old.get("mtime") == st.st_mtime and old.get("tamanho") == st.st_size
                and old.get("cfg") == cfg and dst.exists() and wav.exists() and wav48.exists()):
            fontes[stem] = old
            log(f"[ingest] {src.name}: sem mudança (pulado)")
            continue
        a = analisar(src)
        avisos: list[str] = []
        perfil, converter_hdr = decidir_perfil(tipo, a, avisos)
        fps_txt = nota_fps(a, avisos)
        log(f"[ingest] {rel(vd, src)} -> fontes/{stem}.mp4  ({tipo}, {a['w']}x{a['h']}, rot {a['rot']}, "
            f"{a['codec']} {a['pix_fmt']}, {fps_txt} fps, "
            f"{'HDR' if a['hdr'] else 'SDR'}{' -> SDR' if converter_hdr else ''}, perfil {perfil}, {a['duracao']:.1f}s)")
        aud = ingerir(src, dst, wav, wav48, tipo, a, converter_hdr, avisos, faixa_pedida, limpar_ruido)
        for av in avisos:
            log(f"   [AVISO] {av}")
        if aud.get("faixa") is not None:
            fx = aud["faixas"][aud["faixa"]]
            log(f"   áudio: faixa a:{aud['faixa']} (fala {fx['fala_db']} dB, piso {fx['piso_db']} dB, SNR {fx['snr_db']} dB)"
                f" -> {rel(vd, wav48)} 48 kHz 24-bit · {aud['cadeia']}"
                + ("" if limpar_ruido else " (sem redução de ruído)"))
        vs = next(s for s in ffprobe_json(dst)["streams"] if s["codec_type"] == "video")
        fontes[stem] = {
            "arquivo": rel(vd, dst), "wav16k": rel(vd, wav), "wav48k": rel(vd, wav48), "bruto": rel(vd, src),
            "tipo": tipo, "perfil": perfil, "duracao": round(duracao(dst), 3), "largura": int(vs["width"]),
            "altura": int(vs["height"]), "fps": FPS, "pix_fmt": vs.get("pix_fmt"), "codec": aud.get("encoder"),
            "hdr": a["hdr"], "rotacao": a["rot"], "original": f"{a['w']}x{a['h']}@{a['fps_str']}",
            "codec_original": f"{a['codec']} {a['pix_fmt']}",
            "cor_original": f"{a['prim'] or '?'}/{a['trc'] or '?'}/{a['mat'] or '?'}",
            "audio": {k: aud[k] for k in ("faixa", "cadeia", "limpar_ruido", "faixas")},
            "avisos": avisos, "cfg": cfg, "mtime": st.st_mtime, "tamanho": st.st_size,
        }
    return fontes


# ---------------------------------------------------------------- cenas extras
def ingerir_video_extra(src: Path, dst: Path, a: dict, log_10bit: bool, converter_hdr: bool) -> None:
    f = [f"fps={FPS}", f"scale={LARGURA}:-2:out_range=tv:flags={SCALE_FLAGS}"]
    if log_10bit or converter_hdr:
        f.append(f"format={PIX_FMT_INTER}")
    if converter_hdr:
        f.append(ZSCALE_HDR.format(tin=HDR_TRC.get(a["trc"], "arib-std-b67")))
    f += ["setsar=1", f"format={PIX_FMT_INTER if log_10bit else 'yuv420p'}", SETPARAMS_709]
    if log_10bit:
        venc = [*ENC_INTERMEDIARIO]
    else:   # 8-bit 4:2:0: o Remotion lê direto
        venc = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p"]
    aud = (["-map", "0:a:0", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"] if a["tem_audio"] else ["-an"])
    dst.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg(["-i", str(src), "-map", "0:v:0", *aud, "-vf", ",".join(f), *venc, "-g", str(GOP),
            "-fps_mode", "cfr", "-r", str(FPS), *TAGS_709, "-movflags", "+faststart",
            "-metadata:s:v:0", "rotate=0", str(dst)])
    verificar_decodificavel(dst)


def ingerir_imagem(src: Path, dst: Path, avisos: list) -> tuple[int, int]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image, ImageOps
        with Image.open(src) as im0:
            im = ImageOps.exif_transpose(im0)
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if im.mode in ("P", "LA", "PA") or "transparency" in im.info else "RGB")
            w0, h0 = im.size
            im.thumbnail((LADO_MAX_IMAGEM, LADO_MAX_IMAGEM), Image.Resampling.LANCZOS)
            im.save(dst, "PNG")
            if max(w0, h0) > LADO_MAX_IMAGEM:
                avisos.append(f"imagem {w0}x{h0} reduzida para {im.size[0]}x{im.size[1]}")
            return im.size
    except Exception:   # HEIC etc.: ffmpeg
        L = LADO_MAX_IMAGEM
        ffmpeg(["-i", str(src), "-frames:v", "1", "-vf",
                f"scale='if(gte(iw,ih),min({L},iw),-2)':'if(gte(iw,ih),-2,min({L},ih))':flags=lanczos", str(dst)])
        vs = ffprobe_json(dst)["streams"][0]
        return int(vs["width"]), int(vs["height"])


def ingerir_extras(vd: Path, ed: Path, arquivos: list[Path], antigo: dict, force: bool) -> dict:
    rot = ler_json(vd / "roteiro.json", padrao={})
    declarados = {normalizar_id_extra(e["id"]): e for e in (rot.get("extras") or []) if e.get("id")}
    por_id: dict[str, Path] = {}
    for src in arquivos:
        eid = normalizar_id_extra(id_do_extra(stem_limpo(src)))
        if eid in por_id:
            log(f"   [AVISO] extra {eid}: mais de um arquivo ({por_id[eid].name}, {src.name}) — usando o primeiro")
            continue
        por_id[eid] = src
    extras = {}
    for eid, src in sorted(por_id.items()):
        decl = declarados.get(eid) or {}
        eh_img = src.suffix.lower() in EXT_IMAGEM
        tipo = decl.get("tipo") or tipo_extra_por_nome(stem_limpo(src), eh_img)
        dst = ed / "extras" / (f"{eid}.png" if eh_img else f"{eid}.mp4")
        st = src.stat()
        old = antigo.get(eid)
        if (not force and old and old.get("mtime") == st.st_mtime and old.get("tamanho") == st.st_size
                and old.get("cfg") == CFG_EXTRA and old.get("tipo") == tipo and old.get("arquivo") == rel(vd, dst)
                and dst.exists()):
            extras[eid] = old
            log(f"[ingest] extra {eid} ({src.name}): sem mudança (pulado)")
            continue
        avisos: list[str] = []
        if not decl:
            avisos.append(f"{eid} não está na tabela 'Cenas extras' do roteiro (tipo '{tipo}' deduzido do nome)")
        if eh_img:
            w, h = ingerir_imagem(src, dst, avisos)
            info = {"perfil": "sdr", "duracao": None, "largura": w, "altura": h, "fps": None, "pix_fmt": "png",
                    "tem_audio": False}
            log(f"[ingest] extra {eid} ({rel(vd, src)}) -> extras/{dst.name}  ({tipo}, imagem {w}x{h})")
        else:
            a = analisar(src)
            if tipo == "camera":
                perfil, conv = decidir_perfil("camera", a, avisos)
            else:
                perfil, conv = decidir_perfil("tela", a, avisos)
            log_10bit = eh_log(perfil)
            fps_txt = nota_fps(a, avisos)
            log(f"[ingest] extra {eid} ({rel(vd, src)}) -> extras/{dst.name}  ({tipo}, {a['w']}x{a['h']}, rot {a['rot']}, "
                f"{fps_txt} fps, perfil {perfil}{', 10-bit log' if log_10bit else ', 8-bit'}, {a['duracao']:.1f}s)")
            ingerir_video_extra(src, dst, a, log_10bit, conv)
            vs = next(s for s in ffprobe_json(dst)["streams"] if s["codec_type"] == "video")
            info = {"perfil": perfil, "duracao": round(duracao(dst), 3), "largura": int(vs["width"]),
                    "altura": int(vs["height"]), "fps": FPS, "pix_fmt": vs.get("pix_fmt"), "tem_audio": a["tem_audio"],
                    "original": f"{a['w']}x{a['h']}@{a['fps_str']}"}
        for av in avisos:
            log(f"   [AVISO] {av}")
        extras[eid] = {"arquivo_bruto": rel(vd, src), "arquivo": rel(vd, dst), "tipo": tipo, **info,
                       "declarado": bool(decl), "avisos": avisos, "cfg": CFG_EXTRA,
                       "mtime": st.st_mtime, "tamanho": st.st_size}
    for eid, decl in sorted(declarados.items()):
        if eid in extras:
            continue
        tipo = decl.get("tipo") or "video"
        extras[eid] = {"arquivo_bruto": None, "arquivo": None, "tipo": tipo, "perfil": None, "duracao": None,
                       "declarado": True, "faltando": tipo != "animacao"}
        if tipo == "animacao":
            log(f"[ingest] extra {eid}: animação (componente Remotion; sem arquivo em brutos/extras/)")
        else:
            log(f"   [AVISO] extra {eid} ({tipo}) está no roteiro mas não há arquivo em brutos/extras/{eid}-* "
                "— entra como placeholder FALTANDO (o QA reprova até chegar)")
    return extras


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    ap.add_argument("--force", action="store_true", help="reprocessa mesmo sem mudança")
    ap.add_argument("--faixa-audio", type=int, default=None, metavar="N",
                    help="faixa de áudio da câmera para o master (padrão: a:0; se muda, a de melhor SNR)")
    ap.add_argument("--limpar-ruido", action="store_true",
                    help="redução de ruído suave (afftdn, piso medido) no master — padrão: só passa-altas 60 Hz")
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    if not (vd / "brutos").is_dir():
        sys.exit(f"[ERRO] {vd / 'brutos'} não existe")
    ed = edicao(vd)
    fj = ed / "fontes.json"
    antigo = ler_json(fj, padrao={"fontes": {}})
    principal, arquivos_extras = listar_brutos(vd)
    # original 4K num HD externo (docs/contratos.md §0, ARQUIVADO.json): as fontes desses arquivos ficam como estão
    arquivado = ler_json(vd / "brutos" / "principal" / "ARQUIVADO.json", padrao={"arquivos": []})
    no_hd = {stem_limpo(Path(a["nome"])) for a in arquivado["arquivos"]}
    if not principal and not arquivos_extras and not no_hd:
        sys.exit(f"[ERRO] nenhum vídeo em {vd / 'brutos'}/principal/ (nem extras)")
    if no_hd:
        log(f"   [AVISO] {len(no_hd)} original(is) arquivado(s) fora do Mac (brutos/principal/ARQUIVADO.json): "
            "não são reingeridos; as fontes deles no fontes.json ficam como estão")
    elif not principal:
        log("   [AVISO] nenhum vídeo principal em brutos/principal/ — só extras")
    log(f"[ingest] projeto: {FPS} fps · {PIX_FMT_INTER} · câmera {CAMERA_PERFIL} · "
        f"{len(principal)} principal, {len(arquivos_extras)} extra(s)")
    fontes = ingerir_principal(vd, ed, principal, antigo.get("fontes", {}), args.force, args.faixa_audio,
                               args.limpar_ruido)
    for k, v in antigo.get("fontes", {}).items():
        if k in no_hd and k not in fontes:
            fontes[k] = v
    extras = ingerir_extras(vd, ed, arquivos_extras, antigo.get("extras", {}) or {}, args.force)
    escrever_json(fj, {"fontes": fontes, "extras": extras,
                       "atualizado": dt.datetime.now().astimezone().isoformat(timespec="seconds")})
    log(f"[ingest] {len(fontes)} fonte(s) principal + {len(extras)} extra(s) -> {rel(vd, fj)}")
    for k, v in fontes.items():
        if v["tipo"] == TIPO_AMOSTRA_COR:
            log(f"   {k:<14} {v['tipo']:<11} {v['duracao']:>8.2f}s  (bruto, fora do corte)")
        else:
            log(f"   {k:<14} {v['tipo']:<11} {v['duracao']:>8.2f}s  {v['largura']}x{v['altura']} "
                f"{v.get('fps')} fps {v.get('pix_fmt')} perfil {v.get('perfil')}")
    for k, v in extras.items():
        est = "FALTANDO" if v.get("faltando") else (v.get("arquivo") or "componente Remotion")
        log(f"   {k:<14} extra/{v['tipo']:<9} {est}"
            + (f"  {v.get('largura')}x{v.get('altura')} {v.get('pix_fmt')}" if v.get("arquivo") else ""))


if __name__ == "__main__":
    main()
