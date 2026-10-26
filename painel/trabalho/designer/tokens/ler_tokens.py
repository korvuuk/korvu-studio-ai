"""Lê, SÓ LENDO, os registros das sessões do Claude Code deste projeto e soma tokens e custo — a MESMA conta do
painel/referencias/claude-design/telas-2026-10-23/tokens-custos.py (preços, departamentos, regra de tarefa e de vídeo),
vale a ÚLTIMA linha de cada resposta e o dia da 1.ª (PD21, igual ao banco); com duas diferenças: corta num instante (--ate, ISO UTC) para a leitura não andar enquanto a sessão continua, e devolve
JSON com todos os agentes (não só os 30 primeiros).
Rodar: uv run python -I painel/trabalho/designer/tokens/ler_tokens.py --ate 2026-10-23T15:00:00Z > saida.json
Cache gravado: 1,25× a entrada por 5 min e 2× por 1 h (usage.cache_creation.ephemeral_5m/1h_input_tokens), como o
tokens-custos.py corrigido às 16:41 de 23/10.
"""
import collections, datetime as dt, glob, json, os, re, sys

P = os.path.expanduser('~/.claude/projects/-Users-teste-Documents-CONTENT-AI')
ate_txt = sys.argv[sys.argv.index('--ate') + 1] if '--ate' in sys.argv else None
ate = dt.datetime.fromisoformat(sys.argv[sys.argv.index('--ate') + 1].replace('Z', '+00:00')) if '--ate' in sys.argv else None
fim = dt.date(2026, 10, 23); ini = fim - dt.timedelta(days=29)
PRECO = {'claude-opus-5': (5, 6.25, 0.50, 25), 'claude-opus-5-5': (4, 5, 0.20, 20), 'claude-sonnet-5-5': (2, 2.5, 0.20, 10), 'claude-fable-5-1': (10, 12.5, 0.25, 50)}
DEPTO = {'principal':'direcao','general-purpose':'direcao','workflow-subagent':'direcao','claude':'direcao','Explore':'direcao','Plan':'direcao',
 'pesquisador-de-material':'pesquisa','buscador-de-videos':'pesquisa','estrategista':'pesquisa','curador-de-obra':'pesquisa','portao-pauta':'pesquisa',
 'roteirista':'roteiro','revisor-de-roteiro':'roteiro','produtor-de-material':'roteiro',
 'designer-de-capas':'arte','colorista':'arte','animador':'arte','produtor-de-extras':'arte','portao-imagem':'arte',
 'editor-de-video':'pos','revisor-de-video':'pos','produtor-musical':'pos',
 'auditor-de-perfil':'distribuicao','publicador':'distribuicao','analista-de-metricas':'distribuicao','portao-publicacao':'distribuicao',
 'designer-de-produto':'tecnologia','portao-interface':'tecnologia','engenheiro-frontend':'tecnologia','portao-dados':'tecnologia','engenheiro-backend':'tecnologia'}
C = collections.Counter
seen = set(); dia_tk, dia_us, mod_tk, mod_us, ag_tk, ag_us, runs, dep_tk, dep_us, vid_us, vid_tk, ag_mod = C(), C(), C(), C(), C(), C(), C(), C(), C(), C(), C(), collections.defaultdict(C)
cache_lido = 0
slug_re = re.compile(r'videos/(20\d\d-\d\d-\d\d-[a-z0-9]+(?:-[a-z0-9]+)*)')
ultima, primeira_ts, agslug = {}, {}, {}
for f in glob.glob(P + '/**/*.jsonl', recursive=True):
    sub = '/subagents/' in f; ag = 'principal'; slug = None
    if sub:
        try: ag = json.load(open(f[:-6] + '.meta.json')).get('agentType') or 'subagente'
        except Exception: ag = 'subagente'
        try:
            first = json.loads(open(f, errors='ignore').readline()); c = first.get('message', {}).get('content')
            txt = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
            m = slug_re.search(txt or ''); slug = m.group(1) if m else None
        except Exception: pass
    agslug[f] = (ag, slug, sub)
    for line in open(f, errors='ignore'):
        if '"usage"' not in line: continue
        try: o = json.loads(line)
        except Exception: continue
        m = o.get('message') or {}; u = m.get('usage')
        if not u or m.get('model') not in PRECO: continue
        ts = o.get('timestamp', '')
        if ate_txt and ts > ate_txt: continue  # comparação de texto, como o tokens-custos.py e o banco (o segundo do corte entra inteiro)
        k = (m.get('id') or o.get('uuid'), f)
        primeira_ts.setdefault(k, ts)          # o dia é o da 1.ª linha, como o painel (PD21)
        ultima[k] = (m['model'], u)            # o usage que vale é o da ÚLTIMA linha (as primeiras são provisórias)
contou_em = set()
for k, (mod, u) in ultima.items():
    f = k[1]; ag, slug, sub = agslug[f]
    try: d = dt.date.fromisoformat(primeira_ts[k][:10])
    except Exception: continue
    if not (ini <= d <= fim): continue
    a, b, c_, e = PRECO[mod]
    inp, cw, cr, out = u.get('input_tokens', 0), u.get('cache_creation_input_tokens', 0), u.get('cache_read_input_tokens', 0), u.get('output_tokens', 0)
    cc = u.get('cache_creation') or {}
    w1h = cc.get('ephemeral_1h_input_tokens', 0) or 0; w5 = cc.get('ephemeral_5m_input_tokens', 0) or 0
    if w1h + w5 == 0: w5 = cw
    cw_us = w5 * a * 1.25 + w1h * a * 2.0
    tk = inp + cw + out; us = (inp * a + cw_us + cr * c_ + out * e) / 1e6
    cache_lido += cr
    dia_tk[d] += tk; dia_us[d] += us; mod_tk[mod] += tk; mod_us[mod] += us; ag_tk[ag] += tk; ag_us[ag] += us; ag_mod[ag][mod] += tk
    dp = DEPTO.get(ag, 'direcao'); dep_tk[dp] += tk; dep_us[dp] += us
    if slug: vid_us[slug] += us; vid_tk[slug] += tk
    contou_em.add(f)
for f in contou_em:
    ag, slug, sub = agslug[f]
    runs[ag if sub else 'principal'] += 1
dias = [(ini + dt.timedelta(days=i)) for i in range(30)]
print(json.dumps({
    "janela": [str(ini), str(fim)], "ate": ate.isoformat() if ate else None,
    "total_tokens": sum(mod_tk.values()), "total_us": round(sum(mod_us.values()), 2), "cache_lido": cache_lido,
    "por_modelo": [{"modelo": k, "tokens": v, "us": round(mod_us[k], 2)} for k, v in mod_tk.most_common()],
    "por_departamento": [{"departamento": k, "tokens": v, "us": round(dep_us[k], 2)} for k, v in dep_tk.most_common()],
    "por_agente": [{"agente": k, "tokens": v, "us": round(ag_us[k], 2), "tarefas": runs[k], "modelos": dict(ag_mod[k])} for k, v in ag_tk.most_common()],
    "por_video": [{"slug": k, "tokens": vid_tk[k], "us": round(v, 2)} for k, v in vid_us.most_common()],
    "por_dia": [{"dia": str(d), "tokens": dia_tk[d], "us": round(dia_us[d], 2)} for d in dias],
}, ensure_ascii=False, indent=1))
