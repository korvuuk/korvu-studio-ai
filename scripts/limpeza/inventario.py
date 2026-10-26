"""Classifica o projeto CONTENT AI em grupos de limpeza. Só lê; escreve o manifesto JSON no argv[2]."""
import hashlib, json, os, re, sys
from pathlib import Path

R = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
PUBLICADOS = ["2026-09-17-demis-hassabis", "2026-10-20-fei-fei-li", "2026-10-20-geoffrey-hinton"]
FILA_VIVA = ["2026-10-23-livro-chatgpt"]          # posts até 01/11 → reavaliar depois de 06/11
TESTE = "2026-09-16-chatgpt-contexto"

def h(p, n=8 << 20):
    s = p.stat().st_size; m = hashlib.sha256()
    with open(p, "rb") as f:
        m.update(f.read(n)); f.seek(max(0, s - n)); m.update(f.read(n))
    return (s, m.hexdigest())

def files(base):
    base = R / base
    if base.is_file(): return [base]
    return [f for f in base.rglob("*") if f.is_file() and not f.is_symlink() and not any(x.is_symlink() for x in f.parents if x != R and R in x.parents)] if base.is_dir() and not base.is_symlink() else []

pacotes = {}
for p in R.glob("0[67]-*/*/video/*.mp4"):
    pacotes[h(p)] = p.relative_to(R).as_posix()

G = {k: [] for k in ("G1", "G2", "G3", "G4", "G5")}
motivo = {}
def add(g, f, why):
    rel = f.relative_to(R).as_posix()
    if rel not in motivo:
        G[g].append(rel); motivo[rel] = why

# G1 — lixo seguro (recriável ou cópia idêntica), só nos publicados
for v in PUBLICADOS:
    e = R / "videos" / v / "edicao"
    for f in e.glob("render-remotion*.mp4"): add("G1", f, "render intermediário (antes do áudio); o final está no pacote")
    for f in e.glob("preview*.mp4"): add("G1", f, "prévia")
    for f in e.glob(".audio-montado.wav"): add("G1", f, "áudio temporário do render_corte")
    for f in e.glob("*-leve.mp4"):
        if v != "2026-09-17-demis-hassabis": add("G1", f, "versão leve para mandar ao Carlos")
    for f in e.glob("final*.mp4"):
        k = h(f)
        if k in pacotes: add("G1", f, f"cópia idêntica de {pacotes[k]}")
for d in ("remotion/out/cta-teste",):
    for f in files(d): add("G1", f, "render de teste do CTA")
# G2 — testes e versões descartadas
for f in files(f"videos/{TESTE}"): add("G2", f, "vídeo-teste de cor — 'não publicar' (CONTINUAR §2)")
for f in files(f"05-render-pronto/{TESTE}"): add("G2", f, "pacote do vídeo-teste (o painel mostra como 'Pronto')")
for t in ("_teste-monitor", "_teste-sintetico"):
    for f in files(f"videos/{t}"): add("G2", f, "fixture de teste; recriável: tests/make_synthetic.py")
hz = R / "videos/2026-09-17-demis-hassabis"
for f in (hz / "edicao").glob("final-*.mp4"): add("G2", f, "versão A–E do Hassabis (publicado com o final.mp4)")
for f in (hz / "edicao").glob("render-remotion*.mp4"): pass
for f in files("videos/2026-09-17-demis-hassabis/brutos/_nao-usar"): add("G2", f, "marcado _nao-usar")

# G3 — original de câmera dos publicados
for v in PUBLICADOS:
    for f in files(f"videos/{v}/brutos/principal"):
        add("G3", f, "original 4K da câmera; o vídeo já saiu; edicao/fontes (1440×2560 10-bit V-Log) continua para refazer")

# G4 — material de estudo dos publicados (downloads inteiros; os cortes usados ficam)
for v in PUBLICADOS:
    for f in files(f"videos/{v}/material/obra"):
        if f.suffix.lower() in (".mp4", ".mov", ".webm", ".mkv"): add("G4", f, "obra inteira (cópia de estudo, nunca publicada)")
    yt = R / "videos" / v / "material/youtube"
    for f in yt.glob("*"):
        if f.is_file() and f.suffix.lower() in (".mp4", ".webm", ".mkv"): add("G4", f, "vídeo do YouTube inteiro baixado (os cortes ficam)")
    for f in files(f"videos/{v}/material/youtube/podcast"):
        if f.suffix.lower() in (".mp4", ".webm", ".mkv", ".m4a", ".wav"): add("G4", f, "podcast inteiro baixado (os cortes ficam)")

# G5 — fila viva (só informativo)
for v in FILA_VIVA:
    for f in files(f"videos/{v}/brutos/principal"): add("G5", f, "original de câmera — posts na fila até 01/11")

tam = lambda rel: (R / rel).stat().st_size
res = {g: {"arquivos": len(l), "bytes": sum(tam(x) for x in l), "lista": [{"caminho": x, "bytes": tam(x), "motivo": motivo[x]} for x in sorted(l)]} for g, l in G.items()}
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))
for g, d in res.items():
    print(f"{g}: {d['arquivos']:5d} arquivos · {d['bytes']/2**30:7.2f} GB")
    por = {}
    for it in d["lista"]:
        parts = it["caminho"].split("/")
        k = "/".join(parts[:2]) if parts[0] != "videos" else "/".join(parts[:3]) if len(parts) > 3 else "/".join(parts[:2])
        por[k] = por.get(k, 0) + it["bytes"]
    for k, b in sorted(por.items(), key=lambda x: -x[1])[:14]:
        print(f"      {b/2**30:7.2f} GB  {k}")
