#!/usr/bin/env python3
"""QA técnico de um vídeo final (Reels): specs, loudness, pretos/congelados, grafia das legendas, cenas extras.

FPS esperado = FPS_PROJETO (padrão 25; Lumix S5IIX 25p) ±0,01 — ou --fps. Com --video_dir: FAIL se algum
overlay de cena extra estiver `faltando` (edl.json / reel-props.json).

Uso:
  uv run python .claude/skills/qa-video/scripts/qa_check.py <arquivo.mp4> [--video_dir videos/<slug>] [--frames 12] [--saida <pasta>]

Gera <saida>/qa-tecnico.json e <saida>/qa-tecnico.md (padrão: videos/<slug>/qa/ com --video_dir,
senão ao lado do arquivo como <nome>.qa.json/.md). Sai com código 1 se houver FAIL.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import struct
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]


def _carregar_env() -> None:
    env = RAIZ / ".env"
    if not env.exists():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(env, override=False)


_carregar_env()
FFMPEG = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE_BIN", "ffprobe")
FPS_PROJETO = float(os.environ.get("FPS_PROJETO") or 25)

SPEC = {
    "largura": 1080, "altura": 1920, "fps": FPS_PROJETO, "fps_tol": 0.01,
    "codec": "h264", "perfil": "High", "pix_fmt": "yuv420p",
    "audio_codec": "aac", "audio_sr": 48000,
    "dur_min": 3.0, "dur_max": 180.0,
    "tamanho_max_mb": 300.0, "bitrate_max_mbps": 25.0,
    "lufs": -14.0, "lufs_tol": 1.0, "true_peak_max": -1.5,
}


def check(nome: str, ok: bool | None, valor, esperado: str, nivel: str = "FAIL") -> dict:
    status = "PASS" if ok else (nivel if ok is False else "WARN")
    return {"check": nome, "status": status, "valor": valor, "esperado": esperado}


def ffprobe(arq: Path) -> dict:
    r = subprocess.run([FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(arq)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def fracao(s: str | None) -> float:
    if not s or s == "0/0":
        return 0.0
    n, _, d = s.partition("/")
    return float(n) / float(d or 1)


def ordem_atoms(arq: Path) -> list[str]:
    atoms = []
    tam = arq.stat().st_size
    with arq.open("rb") as f:
        pos = 0
        while pos < tam and len(atoms) < 64:
            f.seek(pos)
            h = f.read(8)
            if len(h) < 8:
                break
            size, tipo = struct.unpack(">I4s", h)
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
            elif size == 0:
                size = tam - pos
            atoms.append(tipo.decode("latin-1"))
            if size < 8:
                break
            pos += size
    return atoms


def analise_ffmpeg(arq: Path, tem_audio: bool) -> dict:
    """Uma passada: blackdetect + freezedetect (vídeo) e ebur128 (áudio)."""
    filtros = "[0:v]blackdetect=d=0.2:pix_th=0.04,freezedetect=n=0.003:d=0.5[v]"
    mapas = ["-map", "[v]"]
    if tem_audio:
        filtros += ";[0:a]ebur128=peak=true[a]"
        mapas += ["-map", "[a]"]
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(arq), "-filter_complex", filtros,
                        *mapas, "-f", "null", "-"], capture_output=True, text=True)
    err = r.stderr
    pretos = [{"inicio": float(a), "fim": float(b), "duracao": float(c)}
              for a, b, c in re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", err)]
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", err)]
    duracoes = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", err)]
    congelados = [{"inicio": s, "duracao": d} for s, d in zip(starts, duracoes)]
    if len(starts) > len(duracoes):  # congelado até o fim
        congelados.append({"inicio": starts[-1], "duracao": None})
    lufs = tp = None
    resumo = err.split("Summary:")[-1] if "Summary:" in err else ""
    m = re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", resumo)
    if m and m.group(1) != "-inf":
        lufs = float(m.group(1))
    m = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", resumo)
    if m and m.group(1) != "-inf":
        tp = float(m.group(1))
    return {"pretos": pretos, "congelados": congelados, "lufs": lufs, "true_peak": tp}


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w]+", "", s.lower())


def grafia_legendas(video_dir: Path) -> list[dict]:
    """Compara legendas.json com a FALA do roteiro, linha a linha."""
    leg_p, rot_p = video_dir / "edicao" / "legendas.json", video_dir / "roteiro.json"
    if not leg_p.exists() or not rot_p.exists():
        return [{"linha": None, "tipo": "sem_dados", "detalhe": "legendas.json ou roteiro.json ausente"}]
    legendas = json.loads(leg_p.read_text(encoding="utf-8"))
    roteiro = json.loads(rot_p.read_text(encoding="utf-8"))
    problemas = []
    for linha in roteiro.get("linhas", []):
        if linha.get("alternativa_de"):
            continue
        leg = [c["text"].strip() for c in legendas if c.get("linha") == linha["id"]]
        if not leg:
            continue
        ref = (linha.get("fala") or "").split()
        a, b = [normalizar(w) for w in ref], [normalizar(w) for w in leg]
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
            if op == "equal":
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    r0, l0 = ref[i].strip(".,;:!?…\"“”"), leg[j].strip(".,;:!?…\"“”")
                    if r0 != l0:  # mesma palavra, grafia diferente (maiúscula/acento)
                        problemas.append({"linha": linha["id"], "tipo": "grafia", "roteiro": r0, "legenda": l0})
            else:
                problemas.append({"linha": linha["id"], "tipo": op,
                                  "roteiro": " ".join(ref[i1:i2]), "legenda": " ".join(leg[j1:j2])})
    return problemas


def extrair_frames(arq: Path, dur: float, n: int, pasta: Path) -> list[str]:
    pasta.mkdir(parents=True, exist_ok=True)
    saidas = []
    for k in range(n):
        t = dur * (k + 0.5) / n
        out = pasta / f"qa-{k + 1:02d}-{t:05.1f}s.jpg"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(arq), "-frames:v", "1",
                        "-vf", "scale=540:-2", "-q:v", "3", str(out)], check=False)
        if out.exists():
            saidas.append(str(out))
    return saidas


def markdown(rel: dict) -> str:
    L = [f"## QA técnico — `{Path(rel['arquivo']).name}`", "",
         f"Resultado: **{rel['resultado']}** · {rel['criado_em']}", "",
         "| Check | Valor | Esperado | Status |", "|---|---|---|---|"]
    for c in rel["checks"]:
        L.append(f"| {c['check']} | {c['valor']} | {c['esperado']} | {c['status']} |")
    L += ["", "### Pretos / congelados"]
    if not rel["pretos"] and not rel["congelados"]:
        L.append("- nenhum trecho detectado")
    for p in rel["pretos"]:
        L.append(f"- preto {p['inicio']:.2f}–{p['fim']:.2f}s ({p['duracao']:.2f}s)")
    for c in rel["congelados"]:
        d = f"{c['duracao']:.2f}s" if c["duracao"] is not None else "até o fim"
        L.append(f"- congelado a partir de {c['inicio']:.2f}s ({d}) — ok se for cartela/animação estática?")
    if rel.get("grafia") is not None:
        L += ["", "### Legendas vs roteiro"]
        if not rel["grafia"]:
            L.append("- sem divergências")
        for g in rel["grafia"][:40]:
            if g["tipo"] == "sem_dados":
                L.append(f"- {g['detalhe']}")
            else:
                L.append(f"- {g['linha']} · {g['tipo']}: roteiro «{g['roteiro']}» → legenda «{g['legenda']}»")
    if rel.get("frames"):
        L += ["", "### Frames para revisão visual", *[f"- `{f}`" for f in rel["frames"]]]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="QA técnico de vídeo para Reels")
    ap.add_argument("arquivo", type=Path)
    ap.add_argument("--video_dir", "--video-dir", dest="video_dir", type=Path)
    ap.add_argument("--frames", type=int, default=0, help="extrai N frames para revisão visual")
    ap.add_argument("--saida", type=Path, help="pasta dos relatórios")
    ap.add_argument("--fps", type=float, default=None, help="fps esperado (padrão: FPS_PROJETO ou 25)")
    a = ap.parse_args()

    arq = a.arquivo.resolve()
    if not arq.exists():
        raise SystemExit(f"Arquivo não encontrado: {arq}")
    info = ffprobe(arq)
    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), {})
    au = next((s for s in info["streams"] if s.get("codec_type") == "audio"), None)
    fmt = info.get("format", {})
    dur = float(fmt.get("duration", 0) or 0)
    fps = fracao(v.get("r_frame_rate"))
    tamanho_mb = arq.stat().st_size / 1_048_576
    bitrate = float(fmt.get("bit_rate", 0) or 0) / 1e6
    atoms = ordem_atoms(arq)
    faststart = "moov" in atoms and "mdat" in atoms and atoms.index("moov") < atoms.index("mdat")

    S = SPEC
    fps_esp = a.fps or S["fps"]
    cor = (v.get("color_space"), v.get("color_transfer"), v.get("color_primaries"))
    checks = [
        check("Resolução", v.get("width") == S["largura"] and v.get("height") == S["altura"],
              f"{v.get('width')}×{v.get('height')}", "1080×1920"),
        check("FPS", abs(fps - fps_esp) <= S["fps_tol"], round(fps, 3), f"{fps_esp:g} ±0,01 (FPS_PROJETO)"),
        check("Codec vídeo", v.get("codec_name") == S["codec"], v.get("codec_name"), "h264"),
        check("Perfil H.264", v.get("profile") == S["perfil"], v.get("profile"), "High"),
        check("Pixel format", v.get("pix_fmt") == S["pix_fmt"], v.get("pix_fmt"), "yuv420p (8-bit)"),
        check("Cor (tags)", cor == ("bt709", "bt709", "bt709") or None, "/".join(str(c) for c in cor),
              "bt709/bt709/bt709"),
        check("Codec áudio", bool(au) and au.get("codec_name") == S["audio_codec"],
              au.get("codec_name") if au else "sem áudio", "aac"),
        check("Sample rate", bool(au) and int(au.get("sample_rate", 0)) == S["audio_sr"],
              au.get("sample_rate") if au else "—", "48000"),
        check("Duração", S["dur_min"] <= dur <= S["dur_max"], f"{dur:.2f}s", "3–180 s"),
        check("Faststart (moov antes do mdat)", faststart, " > ".join(atoms[:6]), "moov antes de mdat"),
        check("Tamanho", tamanho_mb <= S["tamanho_max_mb"], f"{tamanho_mb:.1f} MB", "≤ 300 MB"),
        check("Bitrate", bitrate <= S["bitrate_max_mbps"], f"{bitrate:.2f} Mbps", "≤ 25 Mbps"),
    ]

    ana = analise_ffmpeg(arq, tem_audio=bool(au))
    lufs, tp = ana["lufs"], ana["true_peak"]
    checks.append(check("Loudness integrada", lufs is not None and abs(lufs - S["lufs"]) <= S["lufs_tol"],
                        f"{lufs} LUFS" if lufs is not None else "—", "−14 ±1 LUFS"))
    checks.append(check("True peak", tp is not None and tp <= S["true_peak_max"],
                        f"{tp} dBTP" if tp is not None else "—", "≤ −1,5 dBTP"))
    pretos_longos = [p for p in ana["pretos"] if p["duracao"] >= 0.5]
    checks.append(check("Trechos pretos (≥0,5 s)", None if pretos_longos else True,
                        len(pretos_longos), "0 (revisar se houver)"))
    congel_longos = [c for c in ana["congelados"] if c["duracao"] is None or c["duracao"] >= 2.0]
    checks.append(check("Congelados (≥2 s)", None if congel_longos else True,
                        len(congel_longos), "0 (ok se cartela estática)"))

    grafia = None
    if a.video_dir:
        vd = a.video_dir.resolve()
        grafia = grafia_legendas(vd)
        edl_p = vd / "edicao" / "edl.json"
        edl_d = json.loads(edl_p.read_text(encoding="utf-8")) if edl_p.exists() else {}
        d_edl = edl_d.get("duracao_saida")
        if d_edl:
            checks.append(check("Duração vs EDL", abs(dur - d_edl) <= 0.2 or None,
                                f"{dur:.2f} vs {d_edl:.2f}", "±0,2 s"))
        if edl_d.get("fps") and abs(float(edl_d["fps"]) - fps_esp) > 0.01:
            checks.append(check("FPS da EDL", None, edl_d["fps"], f"{fps_esp:g}"))
        props_p = vd / "edicao" / "reel-props.json"
        props_d = json.loads(props_p.read_text(encoding="utf-8")) if props_p.exists() else {}
        # A camada que foi renderizada é a do reel-props.json — com `gerar_props.py --overlays` ela substitui os extras
        # da EDL (Hinton v3, 15/10: o edl.json ainda marcava E01/E04/E06 `faltando` e o QA dava FAIL falso).
        ov_props = [o for o in (props_d.get("overlays") or []) if o.get("tipo") == "extra"]
        ov_ex = ov_props or [o for o in (edl_d.get("overlays") or []) if o.get("tipo") == "extra"]
        if ov_ex:
            faltam = sorted({o.get("extra") for o in ov_ex if o.get("faltando")})
            # sem mostrarFaltando o placeholder não vai para o vídeo (o Carlos fica em tela cheia): aviso, não FAIL
            visivel = bool(props_d.get("mostrarFaltando")) if props_d else True
            checks.append(check("Cenas extras (nenhuma faltando)", (not faltam) or (None if not visivel else False),
                                (", ".join(faltam) + (" faltando (placeholder no vídeo)" if visivel else
                                                      " ausentes (sem placeholder; Carlos em tela cheia)"))
                                if faltam else f"{len({o.get('extra') for o in ov_ex})} ok",
                                "0 faltando (placeholder no vídeo)"))
        reais = [g for g in grafia if g["tipo"] != "sem_dados"]
        checks.append(check("Legendas vs roteiro", None if reais else True, len(reais), "0 divergências"))

    if a.saida:
        pasta, base = a.saida.resolve(), "qa-tecnico"
    elif a.video_dir:
        pasta, base = a.video_dir.resolve() / "qa", "qa-tecnico"
    else:
        pasta, base = arq.parent, f"{arq.stem}.qa"
    pasta.mkdir(parents=True, exist_ok=True)
    frames = extrair_frames(arq, dur, a.frames, pasta / "frames") if a.frames > 0 else []

    resultado = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    rel = {
        "arquivo": str(arq), "resultado": resultado,
        "criado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checks": checks, "pretos": ana["pretos"], "congelados": ana["congelados"],
        "loudness": {"lufs": lufs, "true_peak": tp}, "grafia": grafia, "frames": frames,
    }
    (pasta / f"{base}.json").write_text(json.dumps(rel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (pasta / f"{base}.md").write_text(markdown(rel), encoding="utf-8")

    for c in checks:
        print(f"[{c['status']:4}] {c['check']}: {c['valor']} (esperado {c['esperado']})")
    print(f"RESULTADO: {resultado} → {pasta / (base + '.md')}")
    sys.exit(1 if resultado == "FAIL" else 0)


if __name__ == "__main__":
    main()
