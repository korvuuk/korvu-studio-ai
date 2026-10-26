"""Transformações de entrada por tipo/perfil de fonte (antes da primária e da LUT da marca).

- camera, perfil `vlog` (Panasonic Lumix S5IIX, V-Log/V-Gamut 10-bit): LUT de entrada V-Log → Rec.709.
    Preferência: 1) LUT oficial da Panasonic em `00-marca/cor/luts/panasonic/*V709*.cube`
                    (ex.: `VLog_to_V709_forV35_ver100.cube`, descarregada pelo Carlos do site da Panasonic)
                 2) `00-marca/cor/luts/entrada-camera.cube` (gerada por gerar_entrada_vlog.py, provisória)
    Sem nenhuma → erro (V-Log sem transformação fica lavado/cinzento e a primária mede tudo errado).
    Range: o YUV V-Log é SEMPRE lido como limitado (`in_range=tv`) → RGB 0–1 em gbrp16le antes do lut3d
    (x = (código−64)/876). É a convenção das duas LUTs (ver docstring de gerar_entrada_vlog.py).
- camera, perfil `sdr`, e celular SDR: passthrough.
- HDR (PQ/HLG, iPhone) → SDR bt709 com zscale + tonemap=hable, **só se o stream ainda for HDR**.
- tela: nunca recebe transformação nem LUT.

Perfil de uma fonte: `edicao/fontes.json` (campo "perfil" por fonte: vlog|sdr) → senão, para câmera,
a env `CAMERA_PERFIL` (padrão `vlog`); celular/tela → sdr.

Uso:  uv run python .claude/skills/color-grading/scripts/entrada.py <video> [--tipo ...] [--perfil vlog|sdr]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _comum as C  # noqa: E402

TRC_HDR = {"smpte2084": "smpte2084", "arib-std-b67": "arib-std-b67"}
PERFIS = ("vlog", "sdr")
TIPOS = ("camera", "celular", "tela")
# yuv (V-Log, range limitado) → RGB 0–1 16 bits: o domínio que as LUTs de entrada esperam
CONVERSAO_RGB16 = "scale=in_color_matrix=bt709:in_range=tv,format=gbrp16le"
CONVERSAO_RGB16_PC = "scale=in_color_matrix=bt709:in_range=pc,format=gbrp16le"


def conversao_rgb16(faixa: str | None) -> str:
    """YUV → gbrp16le respeitando o range do arquivo. A Lumix grava V-Log em FULL range (0–1023, preto ≈ 128 =
    0,125 da curva V-Log, medido em 2026-09-15): arquivo "pc" é lido com in_range=pc; os intermediários do
    ingest já vêm convertidos para limitado ("tv")."""
    return CONVERSAO_RGB16_PC if (faixa or "").lower() in ("pc", "full", "jpeg") else CONVERSAO_RGB16


def tipo_por_nome(nome: str) -> str:
    n = Path(nome).stem.lower()
    if n.startswith("tela"):
        return "tela"
    if n.startswith(("celular", "phone", "iphone", "img_")):
        return "celular"
    return "camera"


# ───────────────────────── perfil (fontes.json / env) ─────────────────────────

def perfil_camera_padrao() -> str:
    v = (os.environ.get("CAMERA_PERFIL") or "vlog").strip().lower()
    if v not in PERFIS:
        print(f"⚠ CAMERA_PERFIL={v!r} desconhecido → a usar 'vlog'")
        return "vlog"
    return v


def carregar_fontes(video_dir: Path) -> dict:
    """`fontes` de <video>/edicao/fontes.json ({} se não existir)."""
    p = Path(video_dir) / "edicao" / "fontes.json"
    if not p.exists():
        return {}
    try:
        return C.ler_json(p).get("fontes") or {}
    except ValueError:
        print(f"⚠ {C.rel(p)} inválido — a ignorar")
        return {}


def carregar_extras(video_dir: Path) -> dict:
    """`extras` (cenas extras / B-roll) de <video>/edicao/fontes.json ({} se não houver)."""
    p = Path(video_dir) / "edicao" / "fontes.json"
    if not p.exists():
        return {}
    try:
        return C.ler_json(p).get("extras") or {}
    except ValueError:
        return {}


def fontes_de_arquivo(path: Path) -> dict:
    """Se o arquivo está em <video>/edicao/fontes/ ou <video>/edicao/, lê o fontes.json desse vídeo."""
    for d in (path.parent, path.parent.parent):
        if (d / "fontes.json").exists() and d.name == "edicao":
            return carregar_fontes(d.parent)
    return {}


def tipo_da_fonte(nome: str, fontes: dict | None = None) -> str:
    t = str(((fontes or {}).get(nome) or {}).get("tipo") or "").lower()
    return t if t in TIPOS else tipo_por_nome(nome)


def perfil_da_fonte(nome: str, fontes: dict | None = None, tipo: str | None = None) -> str:
    tipo = tipo or tipo_da_fonte(nome, fontes)
    p = str(((fontes or {}).get(nome) or {}).get("perfil") or "").lower()
    if p in PERFIS:
        return p
    return perfil_camera_padrao() if tipo == "camera" else "sdr"


# ───────────────────────── LUT de entrada ─────────────────────────

def luts_panasonic() -> list[Path]:
    if not C.PANASONIC_DIR.is_dir():
        return []
    return sorted(p for p in C.PANASONIC_DIR.iterdir()
                  if p.suffix.lower() == ".cube" and "v709" in p.name.lower() and not p.name.startswith("."))


def lut_entrada_camera() -> tuple[Path | None, str]:
    """(caminho, descrição) da LUT V-Log→709 a usar: oficial da Panasonic > gerada (provisória)."""
    of = luts_panasonic()
    if of:
        return of[-1], f"LUT oficial Panasonic ({C.rel(of[-1])})"
    if C.ENTRADA_CAMERA_CUBE.exists():
        meta = C.ENTRADA_CAMERA_CUBE.with_suffix(".json")
        prov = C.ler_json(meta).get("provisorio", True) if meta.exists() else True
        return C.ENTRADA_CAMERA_CUBE, f"{C.rel(C.ENTRADA_CAMERA_CUBE)} ({'gerada, provisória' if prov else 'gerada'})"
    return None, "nenhuma"


def exigir_lut_vlog() -> tuple[Path, str]:
    p, d = lut_entrada_camera()
    if p is None:
        raise SystemExit("Fonte de câmera em V-Log mas não há LUT de entrada. Rode\n"
                         "  uv run python .claude/skills/color-grading/scripts/gerar_entrada_vlog.py\n"
                         f"ou coloque a LUT oficial da Panasonic (V-Log→V-709 .cube) em {C.rel(C.PANASONIC_DIR)}/.\n"
                         "Se a fonte NÃO é V-Log: \"perfil\": \"sdr\" no edicao/fontes.json ou CAMERA_PERFIL=sdr.")
    return p, d


def filtro_camera(conversao: bool = False, faixa: str | None = None) -> str:
    """lut3d da LUT de entrada. `conversao=True` prefixa yuv → gbrp16le (para ler direto de um arquivo),
    respeitando o range do arquivo (`faixa` = color_range do stream)."""
    p, _ = lut_entrada_camera()
    if p is None:
        return ""
    f = f"lut3d=file={C.esc_filtro(p)}:interp=tetrahedral"
    return f"{conversao_rgb16(faixa)},{f}" if conversao else f


# ───────────────────────── HDR ─────────────────────────

def detectar_hdr(stream: dict) -> str | None:
    """Devolve o transfer HDR ('smpte2084'/'arib-std-b67') ou None se já é SDR."""
    trc = (stream.get("color_transfer") or "").lower()
    if trc in TRC_HDR:
        return TRC_HDR[trc]
    # Dolby Vision / sem tag mas bt2020 10-bit: tratar como HLG (iPhone) só se houver side data de DV.
    sd = " ".join(str(x) for x in stream.get("side_data_list", []))
    if "DOVI" in sd or "Dolby Vision" in sd:
        return "arib-std-b67"
    return None


def filtro_hdr_para_sdr(trc: str, prim: str = "bt2020", matriz: str = "bt2020nc") -> str:
    return (f"zscale=tin={trc}:pin={prim}:min={matriz}:t=linear:npl=100,format=gbrpf32le,"
            f"zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
            f"zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
            f"setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")


# ───────────────────────── filtro por arquivo ─────────────────────────

def filtro_entrada(path: Path, tipo: str | None = None, info: dict | None = None,
                   com_lut_camera: bool = True, perfil: str | None = None) -> tuple[str, str]:
    """Devolve (filtro_ffmpeg, descricao) para ler um ARQUIVO (amostra do criar_lut, scopes…).
    Filtro vazio = passthrough. Para V-Log o filtro inclui a conversão yuv limitado → gbrp16le."""
    fontes = fontes_de_arquivo(path)
    tipo = tipo or tipo_da_fonte(path.stem, fontes)
    if tipo == "tela":
        return "", "tela: sem transformação (gravação de ecrã nunca é graduada)"
    info = info or C.probe(path)
    s = C.stream_video(info)
    perfil = perfil or perfil_da_fonte(path.stem, fontes, tipo)
    bits = s.get("pix_fmt", "?")
    if tipo == "camera" and perfil == "vlog":
        if not com_lut_camera:
            return "", f"camera V-Log ({bits}): sem LUT de entrada (desligada)"
        _, d = exigir_lut_vlog()
        faixa = (s.get("color_range") or "tv").lower()
        leitura = "full range (Lumix V-Log 0–1023)" if faixa == "pc" else "limitado"
        return filtro_camera(conversao=True, faixa=faixa), (f"camera: V-Log/V-Gamut ({bits}, yuv {leitura} → "
                                                            f"gbrp16le) → Rec.709 via {d}")
    partes, desc = [], []
    trc = detectar_hdr(s)
    if trc:
        prim = s.get("color_primaries") or "bt2020"
        mat = s.get("color_space") or "bt2020nc"
        if mat == "bt2020_ncl":
            mat = "bt2020nc"
        partes.append(filtro_hdr_para_sdr(trc, prim if prim != "unknown" else "bt2020",
                                          mat if mat != "unknown" else "bt2020nc"))
        desc.append(f"HDR ({trc}) → SDR bt709 (zscale+hable)")
    else:
        desc.append(f"SDR ({s.get('color_transfer') or 'sem tag'}) → sem tone-map")
    if tipo == "camera":
        desc.append("perfil sdr → sem LUT de entrada")
    return ",".join(partes), f"{tipo}: " + "; ".join(desc)


def main() -> None:
    ap = argparse.ArgumentParser(description="Mostra a transformação de entrada detectada para uma fonte.")
    ap.add_argument("video")
    ap.add_argument("--tipo", choices=list(TIPOS))
    ap.add_argument("--perfil", choices=list(PERFIS))
    a = ap.parse_args()
    p = C.resolver(a.video)
    lut, d = lut_entrada_camera()
    print(f"LUT de entrada V-Log disponível: {d}")
    f, d = filtro_entrada(p, a.tipo, perfil=a.perfil)
    print(d)
    print("filtro:", f or "(nenhum)")


if __name__ == "__main__":
    main()
