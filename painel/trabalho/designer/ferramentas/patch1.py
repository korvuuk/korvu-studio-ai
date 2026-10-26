import pathlib
p = pathlib.Path('painel/trabalho/designer/gerar_telas.py')
s = p.read_text(encoding='utf-8')
def troca(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)
troca('SYNC = lon(B["ultima_sincronizacao"][0]["em"])', 'SYNC = lon(B["telas_sincronizacao"][0]["em"])')
troca('assert len(B["telas_retratos"]) == len(RETRATO) == 10', 'assert {r["agente"] for r in B["telas_retratos"]} == set(RETRATO), "retratos mudaram: atualize RETRATO"')
troca('''    return f"""<div class="k-grid k-grid--tiles">
<div class="k-card k-kpi k-span-3"><span class="k-cap">Seguidores no Instagram</span>''', '''    return f"""<section class="k-section" aria-label="Números do perfil"><div class="k-grid k-grid--tiles">
<div class="k-card k-kpi k-span-3"><span class="k-cap">Seguidores no Instagram</span>''')
troca('''<span class="k-kpi-aside">{capa(melhor['slug'], 'k-capa--lg')}</span></a>
</div>"""''', '''<span class="k-kpi-aside">{capa(melhor['slug'], 'k-capa--lg')}</span></a>
</div></section>"""''')
troca('''    c += f"""<div class="k-section-head" style="margin-top:-8px"><div class="k-filtros" role="group" aria-label="Filtrar agentes">{fb}</div>''', '''    c += f"""<section class="k-section" aria-label="Filtros e números da equipe"><div class="k-section-head" style="margin-top:-8px"><div class="k-filtros" role="group" aria-label="Filtrar agentes">{fb}</div>''')
troca('''<span class="k-kpi-note">{usd(TOK['total_us'], 0)} equivalente na API · {trab} trabalharam</span></div></a>
</div>"""''', '''<span class="k-kpi-note">{usd(TOK['total_us'], 0)} equivalente na API</span></div></a>
</div></section>"""''')
troca('''    c += f"""<div class="k-grid k-grid--tiles">
{kpi(''', '''    c += f"""<section class="k-section" aria-label="Números do perfil"><div class="k-grid k-grid--tiles">
{kpi(''')
troca('''toques no link')}
</div>"""''', '''toques no link')}
</div></section>"""''')
troca('''    c += f"""<div class="k-grid k-grid--tiles">
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Tokens utilizados</span>''', '''    c += f"""<section class="k-section" aria-label="Números do consumo"><div class="k-grid k-grid--tiles">
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Tokens utilizados</span>''')
troca('''<span class="k-kpi-note">entre os {trab} que trabalharam</span></div></div>
</div>"""''', '''<span class="k-kpi-note">entre os {trab} que trabalharam</span></div></div>
</div></section>"""''')
troca('''    c += f"""<div class="k-row" style="gap:12px;flex-wrap:wrap;margin-bottom:16px"><label class="k-search k-busca-grande"''', '''    c += f"""<section class="k-section" aria-label="Busca e filtros"><div class="k-row" style="gap:12px;flex-wrap:wrap;margin-bottom:16px"><label class="k-search k-busca-grande"''')
troca('''<div class="k-filtros" role="group" aria-label="Filtrar por tipo">{fb}</div>"""''', '''<div class="k-filtros" role="group" aria-label="Filtrar por tipo">{fb}</div></section>"""''')
troca('''{"<span class=" + chr(34) + "k-chip k-chip--portao is-sm" + chr(34) + ">" + ic("lock", 12) + "Portão</span>" if port else ""}''', '')
troca('''{'<span class="k-pessoa-portao">' + portao_de(a) + '</span>' if port else ''}''', '''{'<span class="k-pessoa-portao">' + ic('lock', 12) + ' ' + portao_de(a) + '</span>' if port else ''}''')
troca('''<section class="k-card k-span-6 k-xl-5" aria-labelledby="t-quem"''', '''<section class="k-card k-span-12 k-xl-5 k-fim-ate-xl" aria-labelledby="t-quem"''')
troca('''<div class="k-span-12 k-xl-3 k-lado" style="align-items:stretch">''', '''<div class="k-span-6 k-xl-3 k-pilha">''')
p.write_text(s, encoding='utf-8')
print('ok')
