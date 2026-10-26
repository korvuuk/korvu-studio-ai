#!/usr/bin/env python3
"""Prévias dos looks de cor da Biblioteca: o mesmo quadro do Carlos com cada LUT (decisão de 24/10, docs/decisoes.md §5).

O sincronizador do painel SÓ LÊ o projeto; este gerador é separado e é o único passo do painel que grava — e só em
painel/previas/looks/ (fora de painel/web/, que é da interface). O sincronizador não chama este script: confere (stat)
se a prévia esperada existe e guarda o caminho em looks.previa, ou NULL.

Uma prévia por look, com a receita do LEIA-ME da maquete (painel/referencias/claude-design/biblioteca-2026-10-24/):
  vlog     o quadro como a câmera grava: -noautorotate, transpose=1 (vertical), recorte 4:5
  rec709   o mesmo + lut3d=entrada-camera.cube (V-Log → Rec.709, sem look)
  vN       o mesmo + entrada-camera.cube + korvu-look-vN.cube, sem correção primária, LUT inteira
  (vN = cada 00-marca/cor/luts/korvu-look-vN.json do topo de luts/ que tem o .cube ao lado; _descartadas/ fica fora)
Amostra: 00-marca/cor/amostras/praq0967/praq0967-121.00s.mkv (quadro sem perdas, V-Log em full range — LEIA.md da pasta).
O yuv vira RGB como o pipeline de cor lê a câmera (entrada.py: in_range=pc para a Lumix em full range); o gerador
recusa uma amostra que não seja full range (a receita não serviria).

Nome = <id>-<16 hex>.jpg, o hash (sha256) da receita + da amostra + de cada .cube aplicado. Prévia com o nome esperado
já no disco = nada a fazer (não regrava); .cube, amostra ou receita mudou = nome novo, gerado, e o antigo (do mesmo
padrão de nome) é apagado — uma revisão por vez. A imagem é escrita num temporário oculto e só ganha o nome final
inteira: uma passagem interrompida nunca deixa uma prévia pela metade com o nome certo (o temporário é apagado na próxima). JPEG 640×800 (4:5), YCbCr full range com a matriz do JFIF (BT.601).

ffmpeg/ffprobe: FFMPEG_BIN / FFPROBE_BIN do ambiente, senão os do PATH (este script não lê o .env).
Uso (da raiz):  uv run python painel/sync/previas_looks.py [--seco]
  --seco   só diz o que faria; não grava nem apaga nada.
Saída: uma linha por prévia (= igual · + gerada · - apagada · ✗ falhou) e um resumo; exit 1 se alguma falhou.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

AMOSTRA = "00-marca/cor/amostras/praq0967/praq0967-121.00s.mkv"
LUTS = "00-marca/cor/luts"
ENTRADA = "entrada-camera.cube"
SAIDA = "painel/previas/looks"
RECEITA = 1  # versão da receita: mudar qualquer filtro abaixo = subir este número (e o hash muda de qualquer jeito)
LARGURA, ALTURA = 640, 800
# deitado como a câmera grava, girado para a vertical e recortado em 4:5 a 12% do alto (o enquadramento da maquete
# aprovada: o rosto no terço de cima)
GIRO_E_RECORTE = "transpose=1,crop=iw:iw*5/4:0:ih*12/100"
PARA_RGB = "scale=in_color_matrix=bt709:in_range=pc,format=gbrp16le"  # V-Log da Lumix em full range → RGB 0–1
LUT = "lut3d=file={}:interp=tetrahedral"
PARA_JPEG = f"scale={LARGURA}:{ALTURA}:flags=lanczos:out_color_matrix=bt470bg:out_range=pc,format=yuv420p"
LOOK_JSON = re.compile(r"^korvu-look-(v\d+)\.json$")
NOME = re.compile(r"^(vlog|rec709|v\d+)-[0-9a-f]{16}\.jpg$")
TEMPORARIO = re.compile(r"^\.(vlog|rec709|v\d+)-[0-9a-f]{16}\.jpg\.tmp\.jpg$")  # de uma passagem interrompida


def raiz_padrao() -> Path:
    """A mesma raiz do sincronizador: PAINEL_PROJETO, senão CONTENT_AI_ROOT, senão a pasta acima de painel/."""
    return Path(os.environ.get("PAINEL_PROJETO") or os.environ.get("CONTENT_AI_ROOT")
                or Path(__file__).resolve().parents[2]).resolve()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _versao(v: str) -> int:
    return int(v[1:])


def filtro(cubes: list[str]) -> str:
    """O filtergraph do ffmpeg, com os .cube pelo nome (o ffmpeg roda dentro de luts/)."""
    return ",".join([GIRO_E_RECORTE, PARA_RGB, *(LUT.format(c) for c in cubes), PARA_JPEG])


def esperadas(raiz: Path) -> dict[str, dict]:
    """id → {"cubes": [nomes em luts/], "nome": <id>-<hash>.jpg} das prévias que a receita pede hoje, na ordem da tela
    (vlog, rec709, looks pela versão). Sem amostra = {} (nenhuma prévia possível). Look sem .cube ao lado fica de fora;
    sem entrada-camera.cube, só a vlog."""
    luts, amostra = raiz / LUTS, raiz / AMOSTRA
    if not amostra.is_file():
        return {}
    pedidos: list[tuple[str, list[str]]] = [("vlog", [])]
    if (luts / ENTRADA).is_file():
        pedidos.append(("rec709", [ENTRADA]))
        versoes = sorted((m.group(1) for f in luts.iterdir() if (m := LOOK_JSON.match(f.name))
                          and f.is_file() and (luts / f"korvu-look-{m.group(1)}.cube").is_file()), key=_versao)
        pedidos += [(v, [ENTRADA, f"korvu-look-{v}.cube"]) for v in versoes]
    h_amostra = sha256(amostra)
    h_cube: dict[str, str] = {}
    out = {}
    for ident, cubes in pedidos:
        for c in cubes:
            h_cube.setdefault(c, sha256(luts / c))
        chave = json.dumps({"receita": RECEITA, "filtro": filtro(["{lut}"] * len(cubes)), "amostra": h_amostra,
                            "luts": [h_cube[c] for c in cubes]}, sort_keys=True)
        out[ident] = {"cubes": cubes, "nome": f"{ident}-{hashlib.sha256(chave.encode()).hexdigest()[:16]}.jpg"}
    return out


def _ferramenta(var: str, nome: str) -> str | None:
    return os.environ.get(var) or shutil.which(nome)


def faixa_da_amostra(ffprobe: str, amostra: Path) -> str:
    """O color_range do 1.º stream de vídeo, pelo JSON do ffprobe (o CSV ganha um campo vazio a mais quando o stream tem
    side data — a rotação da Lumix: "pc," em vez de "pc")."""
    r = subprocess.run([ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_range",
                        "-of", "json", str(amostra)], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe falhou na amostra: {r.stderr.strip().splitlines()[-1:] or r.returncode}")
    try:
        streams = json.loads(r.stdout).get("streams") or [{}]
    except ValueError as e:
        raise RuntimeError(f"ffprobe devolveu algo que não é JSON: {e}") from None
    return str(streams[0].get("color_range") or "")


def gerar(raiz: Path, seco: bool = False) -> int:
    saida, luts, amostra = raiz / SAIDA, raiz / LUTS, raiz / AMOSTRA
    if not amostra.is_file():
        print(f"✗ amostra não encontrada: {AMOSTRA} — nenhuma prévia")
        return 1
    ffmpeg, ffprobe = _ferramenta("FFMPEG_BIN", "ffmpeg"), _ferramenta("FFPROBE_BIN", "ffprobe")
    if not ffmpeg or not ffprobe:
        print("✗ ffmpeg/ffprobe não encontrados (FFMPEG_BIN/FFPROBE_BIN do ambiente ou no PATH) — nenhuma prévia")
        return 1
    faixa = faixa_da_amostra(ffprobe, amostra)
    if faixa != "pc":
        print(f"✗ a amostra não é full range (color_range={faixa or 'vazio'}): a receita lê in_range=pc — nenhuma prévia")
        return 1
    if list((luts / "panasonic").glob("*V709*.cube")):
        print("⚠ há LUT oficial da Panasonic em luts/panasonic/: o pipeline de cor a usa no lugar da entrada-camera.cube,"
              " mas a prévia segue a receita do LEIA-ME (entrada-camera.cube)")
    pedidas = esperadas(raiz)
    nomes = {p["nome"] for p in pedidas.values()}
    for f in sorted(saida.iterdir()) if saida.is_dir() else []:  # temporário de uma passagem interrompida: nunca vale
        if TEMPORARIO.match(f.name):
            if not seco:
                f.unlink()
            print(f"- {f.name} (temporário de uma passagem interrompida{'; seco: não apagado' if seco else ''})")
    falhas = geradas = iguais = 0
    for ident, p in pedidas.items():
        alvo = saida / p["nome"]
        if alvo.is_file():
            iguais += 1
            print(f"= {ident:7s} {SAIDA}/{p['nome']}")
            continue
        if seco:
            geradas += 1
            print(f"+ {ident:7s} {SAIDA}/{p['nome']} (seco: não gerada)")
            continue
        saida.mkdir(parents=True, exist_ok=True)
        tmp = saida / f".{p['nome']}.tmp.jpg"  # o nome final só aparece com a imagem inteira (os.replace)
        r = subprocess.run([ffmpeg, "-v", "error", "-y", "-noautorotate", "-i", str(amostra), "-vf", filtro(p["cubes"]),
                            "-frames:v", "1", "-update", "1", "-q:v", "2", str(tmp)],
                           cwd=str(luts), capture_output=True, text=True)
        if r.returncode != 0 or not tmp.is_file() or tmp.stat().st_size == 0:
            tmp.unlink(missing_ok=True)
            falhas += 1
            print(f"✗ {ident:7s} ffmpeg falhou: {(r.stderr.strip().splitlines() or ['sem saída'])[-1]}")
            continue
        os.replace(tmp, alvo)  # só aparece com o nome final quando está inteira
        geradas += 1
        print(f"+ {ident:7s} {SAIDA}/{p['nome']}")
    apagadas = 0
    for f in sorted(saida.iterdir()) if saida.is_dir() else []:
        if NOME.match(f.name) and f.name not in nomes:
            apagadas += 1
            if not seco:
                f.unlink()
            print(f"- {f.name}" + (" (seco: não apagada)" if seco else ""))
    print(f"{'(seco) ' if seco else ''}prévias: {len(pedidas)} pedidas · {iguais} iguais · {geradas} geradas · "
          f"{apagadas} antigas apagadas · {falhas} falhas")
    return 1 if falhas else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seco", action="store_true")
    a = ap.parse_args()
    try:
        return gerar(raiz_padrao(), a.seco)
    except (OSError, RuntimeError) as e:
        print(f"✗ {type(e).__name__}: {str(e).strip().splitlines()[0] if str(e).strip() else ''}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
