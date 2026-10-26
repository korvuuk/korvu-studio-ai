"""Versão B: metade de cima SEMPRE ocupada. Preenche os buracos com o material que sobra,
respeitando o conteúdo de cada linha."""
import json
from pathlib import Path
V=Path("videos/2026-09-17-demis-hassabis")
edl=json.load(open(V/"edicao/edl.json"))
fontes=json.load(open(V/"edicao/fontes.json"))["extras"]
ovs=[o for o in edl["overlays"] if o.get("tipo")=="extra"]
base={o["extra"]:o for o in ovs}
def novo(eid,ini,fim,linhas):
    inf=fontes[eid]
    return {"linhas":linhas,"tipo":"extra","extra":eid,"extra_tipo":inf["tipo"],
            "arquivo":inf["arquivo"],"modo":"split","in":0.0,"out":round(min(fim-ini,inf["duracao"]),3),
            "som":False,"credito":"The Thinking Game (Google DeepMind / Greg Kohs)",
            "descricao":inf.get("descricao",""),"faltando":False,
            "saida_inicio":round(ini,3),"saida_fim":round(fim,3)}
# E05 (videogame) recua para a 2.ª metade da L03; o E02 (xadrez) cobre a 1.ª — a ordem da própria frase
e05=base["E05"]; e05["saida_inicio"]=9.68; e05["saida_fim"]=12.68; e05["out"]=3.0
extras_novos=[
    novo("E02", 7.44,  9.68, ["L03"]),     # "aos treze já era mestre de xadrez"
    novo("E13",26.20, 28.72, ["L06"]),     # depois da compra: Hassabis hoje
    novo("E08",36.72, 38.76, ["L08"]),     # continua a sequência do Go
    novo("E04",50.12, 53.12, ["L12"]),     # Hassabis falando — payoff
    novo("E09",53.12, 57.12, ["L12"]),     # a proteína, o feito maior
    novo("E10",57.12, 61.20, ["L13"]),     # gráfico no CTA
]
edl["overlays"]=[o for o in edl["overlays"] if o.get("tipo")!="extra"]+sorted(ovs+extras_novos,key=lambda o:o["saida_inicio"])
tot=sum(o["saida_fim"]-o["saida_inicio"] for o in edl["overlays"] if o.get("tipo")=="extra")
json.dump(edl,open(V/"edicao/edl-continuo.json","w"),ensure_ascii=False,indent=1)
print(f"{len([o for o in edl['overlays'] if o.get('tipo')=='extra'])} overlays · cobertura {tot:.1f}s de {edl['duracao_saida']}s = {tot/edl['duracao_saida']*100:.0f}%")
t=0.0
for o in sorted([o for o in edl["overlays"] if o.get("tipo")=="extra"],key=lambda x:x["saida_inicio"]):
    if o["saida_inicio"]-t>0.15: print(f"   buraco {t:.2f}-{o['saida_inicio']:.2f}s")
    t=o["saida_fim"]
if edl["duracao_saida"]-t>0.15: print(f"   buraco {t:.2f}-{edl['duracao_saida']:.2f}s")
print("-> edl-continuo.json")
