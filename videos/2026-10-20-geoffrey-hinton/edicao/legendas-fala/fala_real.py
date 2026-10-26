import json,sys
V=sys.argv[1]
e=json.load(open(f'{V}/edicao/edl.json'));t=json.load(open(f'{V}/edicao/transcricao.json'))
ps=e['palavras_saida']
out=[]
for s in e['segmentos']:
    cuts=sorted(s.get('cortes_internos') or [])
    def mapt(x):
        off=0
        for a,b in cuts:
            if x>=b: off+=b-a
            elif x>a: return None
        return s['saida_inicio']+(x-s['in'])-off
    ws=[]
    for w in t['palavras']:
        if w['fonte']!=s['fonte']: continue
        m=(w['inicio']+w['fim'])/2
        if not (s['in']<=m<=s['out']): continue
        a=mapt(w['inicio']); b=mapt(w['fim'])
        if a is None or b is None: continue
        ws.append(dict(texto=w['texto'],inicio=round(a,2),fim=round(b,2),loc=w.get('locutor')))
    rot=[p for p in ps if p['linha']==s['linha'] and s['saida_inicio']-0.05<=p['inicio']<s['saida_fim']]
    print(f"== {s['linha']} {s['fonte']} out {s['saida_inicio']:.2f}-{s['saida_fim']:.2f}")
    print('  FALA:', ' '.join(f"{w['texto']}" + ('' if w['loc']=='carlos' else f"[{w['loc']}]") for w in ws))
    print('  LEG :', ' '.join(p['texto'] for p in rot))
    print('  t fala %.2f-%.2f | leg %.2f-%.2f'%((ws[0]['inicio'],ws[-1]['fim']) if ws else (0,0))+'' if False else '', end='')
    if ws and rot: print('  t fala %.2f-%.2f | leg %.2f-%.2f'%(ws[0]['inicio'],ws[-1]['fim'],rot[0]['inicio'],rot[-1]['fim']))
    else: print()
    out.append(dict(linha=s['linha'],n=s['n'],palavras=ws))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
