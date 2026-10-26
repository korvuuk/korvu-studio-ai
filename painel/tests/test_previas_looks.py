"""Teste do painel/sync/previas_looks.py (as prévias dos looks da Biblioteca), numa RAIZ TEMPORÁRIA.

Amostra SINTÉTICA mínima (FFV1 yuv422p10le full range, 400×200, deitada como a câmera grava: três faixas verticais,
azul | laranja | magenta) e .cube de 2³ escritos aqui (identidade, troca R↔B, tudo vermelho). Nada do projeto real é
lido nem escrito. Precisa de ffmpeg e ffprobe (FFMPEG_BIN/FFPROBE_BIN ou no PATH).

Uso (da raiz do projeto):  uv run python painel/tests/test_previas_looks.py [--manter]
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True

CODIGO = Path(__file__).resolve().parents[2]
GERADOR = Path(os.environ.get("PAINEL_TESTE_GERADOR") or CODIGO / "painel" / "sync" / "previas_looks.py")
ROOT = Path(tempfile.mkdtemp(prefix="korvu-previas-")).resolve()
BIN = Path(tempfile.mkdtemp(prefix="korvu-previas-bin-")).resolve()
FFMPEG, FFPROBE = os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg"), os.environ.get("FFPROBE_BIN") or shutil.which("ffprobe")
AMOSTRA = ROOT / "00-marca/cor/amostras/praq0967/praq0967-121.00s.mkv"
LUTS = ROOT / "00-marca/cor/luts"
SAIDA = ROOT / "painel/previas/looks"
LARANJA, AZUL, MAGENTA = (200, 120, 40), (0, 0, 255), (255, 0, 255)

spec = importlib.util.spec_from_file_location("previas_looks", GERADOR)
PL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PL)

RES: list[tuple[str, bool]] = []


def ok(nome: str, cond, detalhe="") -> None:
    RES.append((nome, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {nome}" + (f" — {detalhe}" if detalhe and not cond else ""))


def igual(nome: str, obtido, esperado) -> None:
    ok(nome, obtido == esperado, f"obtido {obtido!r} · esperado {esperado!r}")


def cube(mapa) -> str:
    """LUT 3D de tamanho 2 (R varia mais rápido); mapa(r, g, b) → (r', g', b')."""
    linhas = ["TITLE \"teste\"", "LUT_3D_SIZE 2"]
    for b in (0, 1):
        for g in (0, 1):
            for r in (0, 1):
                linhas.append(" ".join(f"{x:.1f}" for x in mapa(r, g, b)))
    return "\n".join(linhas) + "\n"


IDENTIDADE = cube(lambda r, g, b: (r, g, b))
TROCA_RB = cube(lambda r, g, b: (b, g, r))
VERMELHO = cube(lambda r, g, b: (1, 0, 0))


def escrever(p: Path, txt: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(txt, encoding="utf-8")
    return p


def amostra(faixa: str = "pc", destino: Path = AMOSTRA) -> None:
    """400×200 deitada: x 0–39 azul, 40–309 laranja, 310–399 magenta. Depois do transpose=1 (90° horário) a faixa da
    esquerda vira o alto: o recorte 4:5 (200×250 a partir de y = 12% de 400 = 48) só pega o laranja."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    cor = lambda c: "0x%02X%02X%02X" % c  # noqa: E731
    filtro = (f"color=c={cor(AZUL)}:s=40x200[a];color=c={cor(LARANJA)}:s=270x200[b];color=c={cor(MAGENTA)}:s=90x200[c];"
              f"[a][b][c]hstack=3,format=gbrp,scale=out_color_matrix=bt709:out_range={faixa},format=yuv422p10le")
    cru = destino.with_name("cru-" + destino.name)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "nullsrc=s=16x16:d=1", "-filter_complex", filtro,
                    "-frames:v", "1", "-c:v", "ffv1", "-color_range", faixa, "-colorspace", "bt709",
                    "-color_primaries", "bt709", "-color_trc", "bt709", str(cru)], check=True)
    # a rotação −90 da Lumix vai como side data, como na amostra real (o ffprobe em CSV a imprime como um campo a mais)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-display_rotation", "-90", "-i", str(cru), "-c", "copy", str(destino)],
                   check=True)
    cru.unlink()


def montar() -> None:
    amostra()
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream_side_data=rotation",
                        "-of", "json", str(AMOSTRA)], capture_output=True, text=True)
    ok("a amostra sintética tem a rotação −90 em side data, como a real", '"rotation": -90' in r.stdout, r.stdout)
    escrever(LUTS / "entrada-camera.cube", TROCA_RB)  # a "conversão" troca R↔B: a rec709 tem de ser a vlog trocada
    escrever(LUTS / "korvu-look-v4.json", '{"versao": "v4"}')
    escrever(LUTS / "korvu-look-v4.cube", IDENTIDADE)
    escrever(LUTS / "korvu-look-v5.json", '{"versao": "v5"}')
    escrever(LUTS / "korvu-look-v5.cube", VERMELHO)
    escrever(LUTS / "korvu-look-v7.json", '{"versao": "v7"}')  # sem .cube: sem prévia
    escrever(LUTS / "korvu-look-v12.json", '{"versao": "v12"}')
    escrever(LUTS / "korvu-look-v12.cube", IDENTIDADE)  # v12 depois do v5 (ordem numérica, não de texto)
    escrever(LUTS / "_descartadas/korvu-look-v9.json", '{"versao": "v9"}')
    escrever(LUTS / "_descartadas/korvu-look-v9.cube", IDENTIDADE)
    escrever(LUTS / "korvu-look-v9.cube", IDENTIDADE)  # .cube órfão no topo: o .json do v9 está em _descartadas/
    escrever(LUTS / "korvu-look-v5-copia.json", "{}")  # fora do padrão do nome
    escrever(SAIDA / "LEIA.txt", "não é prévia: o gerador não apaga\n")


def foto(raiz: Path) -> dict[str, tuple]:
    out = {}
    for p in sorted(raiz.rglob("*")):
        rel = p.relative_to(raiz).as_posix()
        out[rel] = ("pasta",) if p.is_dir() else (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
    return out


def gerar(*args: str, env_extra: dict | None = None, path: str | None = None):
    env = {k: v for k, v in os.environ.items() if k not in ("PAINEL_PROJETO", "CONTENT_AI_ROOT", "FFMPEG_BIN",
                                                             "FFPROBE_BIN")}
    env.update({"PAINEL_PROJETO": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})
    if path is not None:
        env["PATH"] = path
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, str(GERADOR), *args], env=env, capture_output=True, text=True, timeout=120,
                       cwd=str(BIN))
    return r.returncode, r.stdout.strip().splitlines(), r.stderr.strip()


def rgb(p: Path) -> np.ndarray:
    r = subprocess.run([FFMPEG, "-v", "error", "-i", str(p), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(PL.ALTURA, PL.LARGURA, 3).astype(float)


def dimensoes(p: Path) -> str:
    return subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip()


def perto(a, b, tol=8) -> bool:
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def casos() -> None:
    print("\n== nomes esperados (receita + amostra + .cube) ==")
    esp = PL.esperadas(ROOT)
    igual("uma prévia por vlog, rec709 e korvu-look-vN.json do topo COM .cube, pela versão (v12 depois do v5); "
          "_descartadas/, sem .cube e nome fora do padrão ficam fora", list(esp), ["vlog", "rec709", "v4", "v5", "v12"])
    igual("cubes de cada uma: vlog nenhum; rec709 a entrada; look = entrada + o dele",
          [p["cubes"] for p in esp.values()],
          [[], ["entrada-camera.cube"], ["entrada-camera.cube", "korvu-look-v4.cube"],
           ["entrada-camera.cube", "korvu-look-v5.cube"], ["entrada-camera.cube", "korvu-look-v12.cube"]])
    ok("nome = <id>-<16 hex>.jpg", all(PL.NOME.match(p["nome"]) and p["nome"].startswith(i + "-")
                                       for i, p in esp.items()), esp)
    ok("v4 e v12 têm o MESMO .cube: o mesmo hash, nomes diferentes pelo id",
       esp["v4"]["nome"] != esp["v12"]["nome"] and esp["v4"]["nome"][3:] == esp["v12"]["nome"][4:])
    antes = PL.RECEITA
    PL.RECEITA = antes + 1
    outra = PL.esperadas(ROOT)
    PL.RECEITA = antes
    ok("receita nova (RECEITA + 1) = todos os nomes mudam", all(outra[i]["nome"] != esp[i]["nome"] for i in esp))

    print("\n== gerar: só em painel/previas/looks/, uma JPEG 640×800 por look ==")
    antes_foto = foto(ROOT)
    rc, out, err = gerar()
    depois = foto(ROOT)
    ok("exit 0, sem traceback", rc == 0 and err == "", f"rc={rc} {out} {err[-400:]}")
    novos = sorted(set(depois) - set(antes_foto))
    igual("arquivos novos = só as 5 prévias, em painel/previas/looks/",
          novos, sorted(f"painel/previas/looks/{p['nome']}" for p in esp.values()))
    ok("nada do que já existia mudou (amostra, LUTs, .json, o LEIA.txt da pasta)",
       all(depois.get(k) == v for k, v in antes_foto.items()))
    ok("nenhum temporário sobrou", not list(SAIDA.glob(".*")))
    for i, p in esp.items():
        igual(f"{i}: 640×800", dimensoes(SAIDA / p["nome"]), "640,800")
    v = {i: rgb(SAIDA / p["nome"]) for i, p in esp.items()}
    media = {i: tuple(round(x) for x in a.reshape(-1, 3).mean(0)) for i, a in v.items()}
    ok("vlog = o quadro como a câmera grava, girado e recortado em 4:5 no alto: só a faixa laranja (sem o azul do "
       "alto nem o magenta do fim)", perto(media["vlog"], LARANJA) and (v["vlog"][..., 2] > 150).mean() < 0.001,
       media["vlog"])
    ok("rec709 = vlog + entrada-camera.cube (aqui a troca R↔B)", perto(media["rec709"], LARANJA[::-1]), media["rec709"])
    ok("look v4 (identidade) = a rec709: a LUT do look vem DEPOIS da entrada",
       np.abs(v["v4"] - v["rec709"]).mean() < 2, np.abs(v["v4"] - v["rec709"]).mean())
    ok("look v5 (tudo vermelho) = vermelho, sem correção primária", perto(media["v5"], (255, 0, 0), 12), media["v5"])

    print("\n== de novo, nada mudou: não regrava ==")
    antes_foto = foto(ROOT)
    rc, out, _ = gerar()
    ok("exit 0, as 5 iguais, nenhuma gerada nem apagada", rc == 0 and sum(ln.startswith("= ") for ln in out) == 5
       and out[-1].endswith("5 iguais · 0 geradas · 0 antigas apagadas · 0 falhas"), out)
    ok("nenhum arquivo tocado (mtime e conteúdo)", foto(ROOT) == antes_foto)

    print("\n== --seco: diz o que faria, não grava nem apaga ==")
    escrever(LUTS / "korvu-look-v4.cube", TROCA_RB)  # o v4 mudou
    antes_foto = foto(ROOT)
    rc, out, _ = gerar("--seco")
    novo_v4 = PL.esperadas(ROOT)["v4"]["nome"]
    ok("exit 0; anuncia a v4 nova e a antiga a apagar", rc == 0 and any(novo_v4 in ln and "seco" in ln for ln in out)
       and any(esp["v4"]["nome"] in ln and ln.startswith("- ") for ln in out), out)
    ok("nada gravado nem apagado", foto(ROOT) == antes_foto)

    print("\n== .cube mudou: nome novo, gerada; a antiga apagada; as outras intactas ==")
    rc, out, _ = gerar()
    depois = foto(ROOT)
    ok("exit 0", rc == 0, out)
    ok("v4 nova existe e a antiga sumiu", (SAIDA / novo_v4).is_file() and not (SAIDA / esp["v4"]["nome"]).exists())
    ok("vlog, rec709, v5 e v12 não foram regravadas", all(depois[f"painel/previas/looks/{esp[i]['nome']}"]
                                                         == antes_foto[f"painel/previas/looks/{esp[i]['nome']}"]
                                                         for i in ("vlog", "rec709", "v5", "v12")))
    ok("v4 agora = a troca aplicada duas vezes = o laranja de volta",
       perto(tuple(rgb(SAIDA / novo_v4).reshape(-1, 3).mean(0)), LARANJA), novo_v4)
    ok("arquivo fora do padrão de nome (LEIA.txt) não é apagado", (SAIDA / "LEIA.txt").is_file())
    escrever(LUTS / "entrada-camera.cube", IDENTIDADE)
    ok("entrada mudou = rec709 e todos os looks mudam de nome; a vlog não",
       [PL.esperadas(ROOT)[i]["nome"] != v_ for i, v_ in (("rec709", esp["rec709"]["nome"]), ("v5", esp["v5"]["nome"]),
                                                           ("v12", esp["v12"]["nome"]))] == [True] * 3
       and PL.esperadas(ROOT)["vlog"]["nome"] == esp["vlog"]["nome"])
    escrever(LUTS / "entrada-camera.cube", TROCA_RB)

    print("\n== falhas: nada pela metade ==")
    escrever(LUTS / "korvu-look-v12.cube", "isto não é um cube\n")
    rc, out, _ = gerar()
    v12 = PL.esperadas(ROOT)["v12"]["nome"]
    ok("ffmpeg falhou no v12: exit 1, linha ✗ do v12, o resto em ordem",
       rc == 1 and any(ln.startswith("✗ v12") for ln in out) and out[-1].endswith("1 falhas"), out)
    ok("sem arquivo do v12 nem temporário", not (SAIDA / v12).exists() and not list(SAIDA.glob(".*")))
    escrever(LUTS / "korvu-look-v12.cube", IDENTIDADE)
    gerar()

    print("\n== passagem interrompida no meio da escrita: nada pela metade com o nome certo ==")
    escrever(LUTS / "korvu-look-v5.cube", TROCA_RB)  # a v5 precisa ser gerada de novo
    v5 = PL.esperadas(ROOT)["v5"]["nome"]
    morre = BIN / "ffmpeg-que-morre"  # escreve meia imagem no arquivo de saída e mata o gerador (kill -9)
    morre.write_text('#!/bin/sh\nfor a in "$@"; do saida="$a"; done\nprintf "meia imagem" > "$saida"\nkill -9 $PPID\n',
                     encoding="utf-8")
    morre.chmod(morre.stat().st_mode | stat.S_IEXEC)
    rc, out, _ = gerar(env_extra={"FFMPEG_BIN": str(morre), "FFPROBE_BIN": FFPROBE})
    ok("o gerador morreu no meio e não ficou prévia pela metade com o nome final (só o temporário oculto)",
       rc != 0 and not (SAIDA / v5).exists() and len(list(SAIDA.glob(".*.tmp.jpg"))) == 1, f"rc={rc} {out}")
    escrever(LUTS / "korvu-look-v5.cube", VERMELHO)  # e o .cube mudou de novo: o temporário velho não é o da vez
    v5 = PL.esperadas(ROOT)["v5"]["nome"]
    rc, out, _ = gerar()
    ok("a passagem seguinte apaga o temporário velho e gera a v5 inteira", rc == 0 and (SAIDA / v5).is_file()
       and not list(SAIDA.glob(".*")) and dimensoes(SAIDA / v5) == "640,800"
       and any("temporário de uma passagem interrompida" in ln for ln in out), out)

    print("\n== a Biblioteca cresce por arquivo: um look novo (.cube + .json) = só a prévia dele ==")
    escrever(LUTS / "korvu-look-v13.json", '{"versao": "v13"}')
    escrever(LUTS / "korvu-look-v13.cube", VERMELHO)
    antes_foto = foto(ROOT)
    rc, out, _ = gerar()
    v13 = PL.esperadas(ROOT).get("v13", {}).get("nome")
    depois = foto(ROOT)
    ok("exit 0; uma linha + (a do v13) e as outras =", rc == 0 and [ln.split()[1] for ln in out if ln.startswith("+ ")]
       == ["v13"] and sum(ln.startswith("= ") for ln in out) == 5, out)
    igual("o único arquivo novo é a prévia do v13; nenhum outro mudou",
          (sorted(set(depois) - set(antes_foto)), all(depois.get(k) == v for k, v in antes_foto.items())),
          ([f"painel/previas/looks/{v13}"], True))
    ok("a do v13 = o look dela (tudo vermelho)", v13 is not None and (SAIDA / v13).is_file()
       and perto(tuple(rgb(SAIDA / v13).reshape(-1, 3).mean(0)), (255, 0, 0), 12), v13)

    antes_foto = foto(ROOT)
    rc, out, _ = gerar(path=str(BIN))  # PATH sem ffmpeg e sem FFMPEG_BIN
    ok("sem ffmpeg: exit 1, uma linha ✗, nada escrito", rc == 1 and len(out) == 1 and out[0].startswith("✗")
       and foto(ROOT) == antes_foto, out)

    log = BIN / "ffmpeg.log"
    embrulho = BIN / "meu-ffmpeg"
    embrulho.write_text(f"#!/bin/sh\necho chamado >> '{log}'\nexec '{FFMPEG}' \"$@\"\n", encoding="utf-8")
    embrulho.chmod(embrulho.stat().st_mode | stat.S_IEXEC)
    escrever(LUTS / "korvu-look-v5.cube", IDENTIDADE)
    rc, out, _ = gerar(env_extra={"FFMPEG_BIN": str(embrulho), "FFPROBE_BIN": FFPROBE}, path=str(BIN))
    ok("FFMPEG_BIN do ambiente é o ffmpeg usado (PATH sem ffmpeg)", rc == 0 and log.is_file()
       and log.read_text().count("chamado") == 1, f"rc={rc} {out}")

    mkv = AMOSTRA.read_bytes()
    amostra("tv")
    antes_foto = foto(ROOT)
    rc, out, _ = gerar()
    ok("amostra em range limitado (tv): recusa — exit 1, ✗, nada escrito", rc == 1 and out and out[-1].startswith("✗")
       and "full range" in out[-1] and foto(ROOT) == antes_foto, out)
    AMOSTRA.write_bytes(mkv)
    AMOSTRA.rename(AMOSTRA.with_suffix(".fora"))
    antes_foto = foto(ROOT)
    rc, out, _ = gerar()
    ok("sem amostra: exit 1, ✗, nada escrito", rc == 1 and out[-1].startswith("✗") and foto(ROOT) == antes_foto, out)
    igual("sem amostra, esperadas = {} (o sincronizador grava previa NULL)", PL.esperadas(ROOT), {})
    AMOSTRA.with_suffix(".fora").rename(AMOSTRA)
    ok("amostra de volta (os mesmos bytes) = o mesmo nome da vlog", PL.esperadas(ROOT)["vlog"]["nome"]
       == esp["vlog"]["nome"])
    AMOSTRA.write_bytes(mkv + b"\0")
    ok("amostra com outro conteúdo = todos os nomes mudam",
       all(PL.esperadas(ROOT)[i]["nome"] != esp[i]["nome"] for i in esp))
    AMOSTRA.write_bytes(mkv)


def main() -> int:
    manter = "--manter" in sys.argv
    print(f"raiz temporária: {ROOT}\ngerador:         {GERADOR}")
    try:
        if not FFMPEG or not FFPROBE:
            ok("ffmpeg e ffprobe disponíveis", False)
        else:
            montar()
            casos()
            ok("nenhum __pycache__ no painel/sync (o gerador roda sem bytecode)",
               not (GERADOR.parent / "__pycache__").exists())
    finally:
        if not manter:
            shutil.rmtree(ROOT, ignore_errors=True)
            shutil.rmtree(BIN, ignore_errors=True)
    falhas = [r for r in RES if not r[1]]
    print(f"\n{len(RES) - len(falhas)}/{len(RES)} PASS" + (f" · {len(falhas)} FAIL" if falhas else ""))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
