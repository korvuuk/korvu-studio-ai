"""Copia os originais 4K para o HD externo com SHA-256 na leitura, depois relê a cópia do HD sem cache e compara.
Nunca sobrescreve: destino existente = para. Escreve o resultado em JSON (argv[3])."""
import fcntl, hashlib, json, os, sys, time
from pathlib import Path

R = Path(sys.argv[1]); DEST = Path(sys.argv[2]); OUT = Path(sys.argv[3]); SLUGS = sys.argv[4:]
F_NOCACHE = getattr(fcntl, "F_NOCACHE", 48)
BUF = 16 << 20

def abrir(p, modo):
    f = open(p, modo, buffering=0)
    fcntl.fcntl(f.fileno(), F_NOCACHE, 1)   # lê/escreve sem o cache do macOS: a conferência lê do disco de verdade
    return f

def hash_de(p):
    h = hashlib.sha256()
    with abrir(p, "rb") as f:
        while b := f.read(BUF): h.update(b)
    return h.hexdigest()

res = {"destino": str(DEST), "inicio": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "arquivos": []}
itens = []
for slug in SLUGS:
    for src in sorted((R / "videos" / slug / "brutos" / "principal").iterdir()):
        if src.name.startswith(".") or not src.is_file() or src.is_symlink(): continue
        itens.append((slug, src, DEST / slug / "brutos" / "principal" / src.name))
total = sum(s.stat().st_size for _, s, _ in itens); feito = 0
livre = os.statvfs(DEST.parent if not DEST.exists() else DEST)
livre = livre.f_bavail * livre.f_frsize
print(f"{len(itens)} arquivos · {total/2**30:.2f} GiB · livre no HD {livre/2**30:.2f} GiB", flush=True)
pular = set()
for slug, src, dst in itens:
    if dst.with_name(dst.name + ".parcial").exists(): sys.exit(f"sobrou um .parcial, conferir antes: {dst}")
    if dst.exists():
        if dst.stat().st_size != src.stat().st_size: sys.exit(f"destino existe com outro tamanho, não sobrescrevo: {dst}")
        pular.add(dst)   # copiado numa passada anterior: não recopia, mas a conferência lê os dois lados
total -= sum(s.stat().st_size for _, s, d in itens if d in pular)
print(f"falta copiar {total/2**30:.2f} GiB", flush=True)
if total > livre - (5 << 30): sys.exit("não cabe com 5 GiB de folga — parei antes de copiar")
for slug, src, dst in itens:
    if dst in pular:
        res["arquivos"].append({"slug": slug, "nome": src.name, "bytes": src.stat().st_size, "sha256_origem": hash_de(src),
                                "mtime": src.stat().st_mtime, "destino": str(dst), "passada_anterior": True})
        print(f"já estava {slug}/{src.name} (hash da origem calculado agora)", flush=True); continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".parcial"); h = hashlib.sha256(); t0 = time.time()
    with abrir(src, "rb") as fi, open(tmp, "wb", buffering=0) as fo:
        while b := fi.read(BUF):
            h.update(b); fo.write(b); feito += len(b)
        os.fsync(fo.fileno())
    st = src.stat(); os.utime(tmp, (st.st_atime, st.st_mtime)); tmp.rename(dst)
    mb = st.st_size / 2**20 / max(time.time() - t0, 1e-3)
    print(f"copiado {slug}/{src.name} {st.st_size/2**30:.2f} GiB {mb:.0f} MB/s · {feito/total*100:.0f}%", flush=True)
    res["arquivos"].append({"slug": slug, "nome": src.name, "bytes": st.st_size, "sha256_origem": h.hexdigest(),
                            "mtime": st.st_mtime, "destino": str(dst)})
print("conferindo a cópia (relendo do HD, sem cache)…", flush=True)
ok = True
for a in res["arquivos"]:
    d = Path(a["destino"]); a["bytes_destino"] = d.stat().st_size; a["sha256_destino"] = hash_de(d)
    a["confere"] = a["bytes_destino"] == a["bytes"] and a["sha256_destino"] == a["sha256_origem"]
    ok &= a["confere"]
    print(f"{'OK ' if a['confere'] else 'ERRO'} {a['slug']}/{a['nome']} {a['sha256_destino'][:16]}", flush=True)
res["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S%z"); res["tudo_confere"] = ok
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))
print("TUDO CONFERE" if ok else "HÁ DIFERENÇAS — não apagar nada", flush=True)
sys.exit(0 if ok else 1)
