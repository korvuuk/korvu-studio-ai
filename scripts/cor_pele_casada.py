"""Cor com a PELE casada entre arquivos, numa passagem só (sem recomprimir duas vezes).

1) roda o aplicar_cor normal -> cor/filtro.txt + corte-cor.mp4
2) mede a pele (máscara YCrCb) por fonte no resultado
3) injeta um ganho por fonte no MESMO grafo, logo antes do LUT do look, e re-renderiza do corte 10-bit
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np, cv2

V=Path("videos/2026-09-17-demis-hassabis"); E=V/"edicao"; COR=E/"cor"
FF="/Users/teste/bin/ffmpeg"
XS=[i/16 for i in range(17)]
def curva(k):
    k=min(1.3,max(0.7,k))
    n=4.0 if k<=4/3 else 1.0+1.0/(k-1.0)
    return " ".join(f"{x:.4f}/{min(1.0,max(0.0,x*k/(1+(k-1)*x**n))):.4f}" for x in XS)

def pele(arq, tempos, larg=360):
    out=[]
    for t in tempos:
        r=subprocess.run(["/opt/homebrew/bin/ffmpeg","-v","error","-ss",f"{t:.3f}","-i",str(arq),"-frames:v","1",
                          "-vf",f"scale={larg}:-1","-pix_fmt","rgb24","-f","rawvideo","-"],capture_output=True)
        if not r.stdout: continue
        a=np.frombuffer(r.stdout,np.uint8); alt=len(a)//(larg*3)
        rgb=a[:larg*alt*3].reshape(alt,larg,3)
        y=cv2.cvtColor(rgb[...,::-1].copy(),cv2.COLOR_BGR2YCrCb)
        m=cv2.inRange(y,(40,135,85),(255,180,135)); m[int(0.62*alt):]=0; m[:int(0.10*alt)]=0
        if m.sum()<3000: continue
        out.append(np.median(rgb[m>0].astype(np.float32),axis=0))
    return np.median(np.array(out),axis=0) if out else None

edl=json.load(open(E/"edl.json")); segs=edl["segmentos"]
por={}
for s in segs:
    ts=np.linspace(s["saida_inicio"]+0.4,s["saida_fim"]-0.4,4)
    v=pele(COR/"corte-cor.mp4",[float(x) for x in ts])
    if v is not None: por.setdefault(s["fonte"],[]).append(v)
med={f:np.median(np.array(v),axis=0) for f,v in por.items()}
dur={}
for s in segs: dur[s["fonte"]]=dur.get(s["fonte"],0)+(s["saida_fim"]-s["saida_inicio"])
ref=np.average(np.array([med[f] for f in med]),axis=0,weights=[dur[f] for f in med])
print(f"referência da pele: R {ref[0]:.1f} G {ref[1]:.1f} B {ref[2]:.1f}")
ganhos={}
LUMA=np.array([0.2126,0.7152,0.0722])
for f,m in sorted(med.items()):
    g=np.clip(ref/np.maximum(m,1e-3),0.85,1.20)
    ganhos[f]=[float(x) for x in g]
    print(f"  {f}: pele R {m[0]:5.1f} G {m[1]:5.1f} B {m[2]:5.1f} -> ganho {g[0]:.3f} {g[1]:.3f} {g[2]:.3f}")
# o casamento tira DIFERENÇA, não muda o brilho: normaliza para ganho de luma médio 1,0
w=np.array([dur[f] for f in sorted(med)]); lg=np.array([np.array(ganhos[f])@LUMA for f in sorted(med)])
k=float(np.exp((w*np.log(lg)).sum()/w.sum()))
for f in ganhos: ganhos[f]=[float(x/k) for x in ganhos[f]]
print(f"  (normalizado: ganho de luma médio era {k:.3f}, agora 1.000)")

# PRETO: o Carlos viu a imagem "estourada" — o preto ficou em 7,9 IRE contra 4,5 do vídeo que ele aprovou.
# Gravação mais clara => nada chega ao preto. Fecha o ponto de preto medido para o alvo.
def preto_por_fonte(arq, segs):
    """Preto (p0.5) medido POR FONTE: no Hassabis o praq0969 já tinha 2,8 IRE e o praq0976 tinha 12,3.
    Uma curva só, na mediana, corrigia pouco onde era muito e demais onde já estava bom (2026-09-19)."""
    por={}
    for s in segs:
        for t in np.linspace(s["saida_inicio"]+0.3, s["saida_fim"]-0.3, 4):
            r=subprocess.run(["/opt/homebrew/bin/ffmpeg","-v","error","-ss",f"{t:.2f}","-i",str(arq),"-frames:v","1",
                              "-vf","scale=270:-1","-pix_fmt","rgb24","-f","rawvideo","-"],capture_output=True)
            if not r.stdout: continue
            a=np.frombuffer(r.stdout,np.uint8); alt=len(a)//810
            fr=a[:270*alt*3].reshape(alt,270,3).astype(np.float32)
            I=(0.2126*fr[...,0]+0.7152*fr[...,1]+0.0722*fr[...,2])/255
            por.setdefault(s["fonte"],[]).append(float(np.percentile(I,0.5)))
    return {f:float(np.median(v)) for f,v in por.items()}


def preto_medido(arq, tempos):
    vs=[]
    for t in tempos:
        r=subprocess.run(["/opt/homebrew/bin/ffmpeg","-v","error","-ss",f"{t:.2f}","-i",str(arq),"-frames:v","1",
                          "-vf","scale=270:-1","-pix_fmt","rgb24","-f","rawvideo","-"],capture_output=True)
        if not r.stdout: continue
        a=np.frombuffer(r.stdout,np.uint8); alt=len(a)//810
        fr=a[:270*alt*3].reshape(alt,270,3).astype(np.float32)
        I=(0.2126*fr[...,0]+0.7152*fr[...,1]+0.0722*fr[...,2])/255
        vs.append(np.percentile(I,0.5))
    return float(np.median(vs)) if vs else 0.0
pretos=preto_por_fonte(COR/"corte-cor.mp4", segs)
# 2026-09-19: fechar TODOS para um alvo ideal (3,5 IRE) escureceu os três arquivos que destoavam e criou um
# degrau no meio do vídeo (L08 com rosto 23,9 e L09 com 17,5). O Carlos: "piorou, piorou quase na metade do
# vídeo, era só para trocar o CTA". Agora: alvo = a MEDIANA dos arquivos que já estão bons, e só se corrige
# quem estiver MUITO acima. Mexer no mínimo, não no ideal.
vs=sorted(pretos.values()); mediana=vs[len(vs)//2]
bons=[v for v in vs if v<=mediana]
ALVO_PRETO=float(np.median(bons)) if bons else mediana
MARGEM=0.03          # só corrige quem passa 3 IRE do alvo
print(f"  alvo = mediana dos arquivos bons: {ALVO_PRETO*100:.1f} IRE (corrige só acima de {(ALVO_PRETO+MARGEM)*100:.1f})")
print("  preto por fonte (alvo 3,5 IRE):")
for f,v in sorted(pretos.items()): print(f"    {f}: {v*100:5.1f} IRE")
def curva_preto(b,alvo,meio,margem=0.0):
    """Fecha o preto SEM escurecer os meios-tons. Âncoras: preto medido -> alvo, e o nível da PELE fica onde
    está. Sem a âncora do meio, fechar um preto de 15 IRE puxava o rosto de 22 para 14 IRE (2026-09-19)."""
    if b<=alvo+max(0.002,margem): return None
    meio=min(max(meio, b+0.06), 0.85)
    pts=[(0.0,0.0),(b,alvo),(meio,meio),(1.0,1.0)]
    return "curves=all='"+" ".join(f"{x:.4f}/{y:.4f}" for x,y in pts)+"':interp=pchip"
LUMA709=np.array([0.2126,0.7152,0.0722])
meios={f:float((np.array(med[f])/255.0)@LUMA709) for f in med}
CPRETO={f:curva_preto(v,ALVO_PRETO,meios.get(f,0.35),MARGEM) for f,v in pretos.items()}
for f in sorted(pretos): print(f"    {f}: preto {pretos[f]*100:4.1f} -> 3.5 IRE, pele ancorada em {meios.get(f,0):.3f}")
print("  curvas de preto:", ", ".join(f for f,c in CPRETO.items() if c) or "nenhuma necessária")

# injeta no grafo: o look é o ÚLTIMO lut3d de cada linha [iN]...[vN]
grafo=(COR/"filtro.txt").read_text(encoding="utf-8")
linhas=grafo.split(";\n")
n=0
for i,ln in enumerate(linhas):
    m=re.match(r"\[i(\d+)\]", ln.strip())
    if not m: continue
    k=int(m.group(1))
    if k>=len(segs): continue
    kr,kg,kb=ganhos.get(segs[k]["fonte"],[1,1,1])
    cp=CPRETO.get(segs[k]["fonte"])
    if abs(kr-1)<0.004 and abs(kg-1)<0.004 and abs(kb-1)<0.004 and not cp: continue
    j=ln.rfind("lut3d=file=")
    if j<0: continue
    extra=f"curves=r='{curva(kr)}':g='{curva(kg)}':b='{curva(kb)}':interp=pchip,"
    novo=ln[:j]+extra+ln[j:]
    if cp:                                       # depois do look: senão a LUT levanta o preto outra vez
        m2=re.search(r"(lut3d=file='[^']*korvu-look[^']*':interp=tetrahedral)", novo)
        if m2: novo=novo[:m2.end()]+","+cp+novo[m2.end():]
    linhas[i]=novo; n+=1
print(f"\nganho de pele injetado em {n} segmento(s) do grafo")
novo=COR/"filtro-pele.txt"; novo.write_text(";\n".join(linhas),encoding="utf-8")
saida=COR/"corte-cor.mp4"
subprocess.run([FF,"-hide_banner","-v","error","-y","-i",str(E/"corte.mp4"),
                "-filter_complex_script",str(novo),"-map","[vout]","-map","0:a","-c:a","copy",
                "-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p",
                "-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-color_range","tv",
                "-movflags","+faststart",str(saida)],check=True)
print("->",saida)
