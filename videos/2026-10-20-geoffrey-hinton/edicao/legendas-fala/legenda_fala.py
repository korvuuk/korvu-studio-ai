"""Gera palavras_saida a partir da FALA REAL (tempos do ASR mapeados para a saída), com grafia corrigida à mão."""
import json,sys,re
fr=json.load(open(sys.argv[1]))
# texto por segmento (n), mesma contagem de palavras do ASR salvo ajustes especiais
TXT={
1:"Imagina você passar 50 anos acreditando numa ideia que ninguém levava a sério",
2:"E no final essa ideia mudar o mundo e ainda te dar um Prêmio Nobel",
3:"Pois é essa é a história do Geoffrey Hinton",
4:"Hinton nasceu em Londres em 1947",          # '194' + '47' (2 fontes) viram 1947
5:"é uma família de cientistas",
6:"Mas diferente que muitas pessoas imaginavam ele não começou a estudar os computadores",
7:"Ele queria entender como funcionava a mente humana",
8:"Nos anos 70 ele começou a defender uma ideia que parecia impossível",
9:"E se a gente criasse uma máquina que consegue imitar a mente humana",
10:"Só que o problema quase ninguém acreditava nessa ideia",
11:"O mais curioso o próprio orientador dele aconselhou ele a abandonar essa pesquisa porque essa pesquisa pode comprometer a carreira dele",
12:"Como o cara é fera ele simplesmente não desistiu",
13:"Em 2012 ele juntou com dois alunos",
14:"Ele desenvolveu um sistema capaz de reconhecer imagem de forma precisa e impecável",
15:"Foi aí que ele acabou de mudar o rumo da inteligência artificial",
16:"Pouco depois o Google acabou de comprar a empresa que eles acabaram de criar",
17:"E o Hinton passou mais de 10 anos trabalhando junto com gigantes da tecnologia",
18:"Agora olha só que interessante",
19:"Em 2023 ele acabou deixando o Google",
20:"Para poder falar livremente sobre os riscos da inteligência artificial",
21:"E um ano e meio depois ele recebeu uma ligação às duas e meia da manhã",  # '2:30' vira 3 palavras
22:"E a ligação era a comitê do Nobel",
23:"Ele tinha acabado de ganhado um Nobel",
24:"E hoje o Geoffrey Hinton é conhecido como o padrinho da inteligência artificial",
25:"E o mais curioso o homem que ajudou a desenvolver essa tecnologia",
26:"É também o que mais alerta sobre os riscos da inteligência artificial",
27:"A história dele mostra uma coisa",
28:"Às vezes uma ideia que ninguém acredita pode mudar o mundo",
29:"Comenta a palavra NOBEL que eu vou te enviar a entrevista completa",
30:"E também não esquece de mandar pra alguém que tá querendo desistir duma grande ideia",
}
DEST={"L01":["sério"],"L02":["Prêmio","Nobel"],"L03":["Geoffrey","Hinton"],"L04":["cientistas"],"L05":["computadores"],
"L06":["mente","humana"],"L07":["impossível"],"L08":["mente","humana"],"L09":["ninguém"],"L11":["não","desistiu"],
"L13":["reconhecer","imagem"],"L14":["inteligência","artificial"],"L15":["Google"],"L16":["10","anos"],"L18":["deixando","o","Google"],
"L19":["riscos"],"L20":["duas","e","meia","da","manhã"],"L21":["Nobel"],"L22":["Nobel"],"L23":["padrinho","da","inteligência","artificial"],
"L25":["alerta"],"L27":["mudar","o","mundo"],"L28":["NOBEL"]}
out=[]
for seg in fr:
    n=seg['n'];L=seg['linha'];asr=[w for w in seg['palavras']]
    tok=TXT[n].split()
    if n==4:   # L04 parte 1 termina em '194'; junta com o '47' do segmento 5
        asr=asr[:]; nxt=fr[n]['palavras'][0]; assert nxt['texto'].startswith('47'),nxt
        asr[-1]=dict(asr[-1],fim=nxt['fim'])
    if n==5: asr=asr[1:]
    if n==21:
        i=[k for k,w in enumerate(asr) if '2:30' in w['texto']][0]; w=asr[i]; d=(w['fim']-w['inicio'])/3
        asr=asr[:i]+[dict(w,inicio=round(w['inicio']+j*d,2),fim=round(w['inicio']+(j+1)*d,2)) for j in range(3)]+asr[i+1:]
    assert len(tok)==len(asr),(n,L,len(tok),len(asr),tok,[w['texto'] for w in asr])
    ds=DEST.get(L,[])
    for t,w in zip(tok,asr):
        out.append(dict(texto=t,inicio=w['inicio'],fim=w['fim'],linha=L,destaque=t in ds))
# destaques só em sequência contígua do bloco (evita 'o'/'e'/'da' soltos)
for i,p in enumerate(out):
    if p['destaque'] and p['texto'].lower() in ('o','e','da','de'):
        viz=[out[j]['destaque'] for j in (i-1,i+1) if 0<=j<len(out) and out[j]['linha']==p['linha']]
        if not all(viz): p['destaque']=False
for a,b in zip(out,out[1:]): assert a['inicio']<=b['inicio'],(a,b)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print(len(out),'palavras');
from itertools import groupby
for L,g in groupby(out,key=lambda p:p['linha']): print(L,' '.join(('*'+p['texto']) if p['destaque'] else p['texto'] for p in g))
