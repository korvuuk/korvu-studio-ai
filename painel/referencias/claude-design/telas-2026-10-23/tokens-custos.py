"""Tokens e custo (preço de tabela da API) das sessões do Claude Code do CONTENT AI, 30 dias.

Fonte: ~/.claude/projects/-Users-teste-Documents-CONTENT-AI/**/*.jsonl (só leitura).
- Cada resposta aparece em várias linhas com o mesmo message.id; o usage das primeiras é provisório,
  então vale a ÚLTIMA linha de cada (message.id, arquivo).
- tokens = entrada + cache gravado + saída (cache lido à parte).
- custo em US$: entrada, cache gravado por 5 min a 1,25× a entrada e por 1 h a 2×, cache lido, saída.
- em £ pelo câmbio de 23/10 (XE): £ 0,7465 por US$.
"""
import collections
import datetime as dt
import glob
import json
import os
import re

P = os.path.expanduser('~/.claude/projects/-Users-teste-Documents-CONTENT-AI')
CORTE = '2026-10-23T15:02:49Z'
FIM = dt.date(2026, 10, 23)
INI = FIM - dt.timedelta(days=29)
CAMBIO = 0.7465
# US$ por milhão: entrada, leitura de cache, saída
PRECO = {'claude-opus-5-5': (4, 0.20, 20), 'claude-sonnet-5-5': (2, 0.20, 10), 'claude-fable-5-1': (10, 0.25, 50),
         'claude-opus-5': (5, 0.50, 25)}
DEPTO = {'principal': 'direcao', 'general-purpose': 'direcao', 'workflow-subagent': 'direcao', 'claude': 'direcao',
         'Explore': 'direcao', 'Plan': 'direcao',
         'pesquisador-de-material': 'pesquisa', 'buscador-de-videos': 'pesquisa', 'estrategista': 'pesquisa',
         'curador-de-obra': 'pesquisa', 'portao-pauta': 'pesquisa',
         'roteirista': 'roteiro', 'revisor-de-roteiro': 'roteiro', 'produtor-de-material': 'roteiro',
         'designer-de-capas': 'arte', 'colorista': 'arte', 'animador': 'arte', 'produtor-de-extras': 'arte',
         'portao-imagem': 'arte',
         'editor-de-video': 'pos', 'revisor-de-video': 'pos', 'produtor-musical': 'pos',
         'auditor-de-perfil': 'distribuicao', 'publicador': 'distribuicao', 'analista-de-metricas': 'distribuicao',
         'portao-publicacao': 'distribuicao',
         'designer-de-produto': 'tecnologia', 'portao-interface': 'tecnologia', 'engenheiro-frontend': 'tecnologia',
         'portao-dados': 'tecnologia', 'engenheiro-backend': 'tecnologia'}
SLUG = re.compile(r'videos/(20\d\d-\d\d-\d\d-[a-z0-9]+(?:-[a-z0-9]+)*)')


def tipo_e_slug(path):
    if '/subagents/' not in path:
        return 'principal', None
    try:
        ag = json.load(open(path[:-6] + '.meta.json')).get('agentType') or 'subagente'
    except Exception:
        ag = 'subagente'
    slug = None
    try:
        primeira = json.loads(open(path, errors='ignore').readline())
        c = primeira.get('message', {}).get('content')
        txt = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
        m = SLUG.search(txt or '')
        slug = m.group(1) if m else None
    except Exception:
        pass
    return ag, slug


ultima = {}
for f in glob.glob(P + '/**/*.jsonl', recursive=True):
    ag, slug = tipo_e_slug(f)
    for line in open(f, errors='ignore'):
        if '"usage"' not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        m = o.get('message') or {}
        if not m.get('usage') or m.get('model') not in PRECO:
            continue
        ts = o.get('timestamp', '')
        if ts > CORTE:
            continue
        ultima[(m.get('id') or o.get('uuid'), f)] = (ts, m['model'], m['usage'], ag, slug)

C = collections.Counter
dia_tk, dia_us, mod_tk, mod_us, ag_tk, ag_us, dep_tk, dep_us, vid_us = (C() for _ in range(9))
runs = collections.defaultdict(set)
cache_lido = 0
for (mid, f), (ts, mod, u, ag, slug) in ultima.items():
    try:
        d = dt.date.fromisoformat(ts[:10])
    except Exception:
        continue
    if not INI <= d <= FIM:
        continue
    pin, pcr, pout = PRECO[mod]
    inp, cw, cr, out = (u.get(k, 0) or 0 for k in
                        ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'))
    cc = u.get('cache_creation') or {}
    w1h = cc.get('ephemeral_1h_input_tokens', 0) or 0
    w5 = cc.get('ephemeral_5m_input_tokens', 0) or 0
    if w1h + w5 == 0:
        w5 = cw
    us = (inp * pin + w5 * pin * 1.25 + w1h * pin * 2 + cr * pcr + out * pout) / 1e6
    tk = inp + cw + out
    cache_lido += cr
    dp = DEPTO.get(ag, 'direcao')
    for cont, chave, val in ((dia_tk, d, tk), (dia_us, d, us), (mod_tk, mod, tk), (mod_us, mod, us), (ag_tk, ag, tk),
                             (ag_us, ag, us), (dep_tk, dp, tk), (dep_us, dp, us)):
        cont[chave] += val
    if slug:
        vid_us[slug] += us
    runs[ag].add(f)

T, U = sum(mod_tk.values()), sum(mod_us.values())
print(f'TOTAL {T} tokens · US$ {U:.2f} · £ {U * CAMBIO:.2f} · cache lido {cache_lido}')
print('MODELO'); [print(f'  {k} {v} {100 * v / T:.1f}% tk · US$ {mod_us[k]:.2f} {100 * mod_us[k] / U:.1f}%') for k, v in mod_tk.most_common()]
print('DEPTO'); [print(f'  {k} {v} US$ {dep_us[k]:.2f} {100 * v / T:.1f}%') for k, v in dep_tk.most_common()]
print('AGENTE'); [print(f'  {k} {v} US$ {ag_us[k]:.2f} execucoes {len(runs[k])}') for k, v in ag_tk.most_common()]
print('VIDEO'); [print(f'  {k} US$ {v:.2f}') for k, v in vid_us.most_common(8)]
print('DIA'); [print(f'  {d} {dia_tk[d]} US$ {dia_us[d]:.2f}') for d in sorted(dia_tk)]
