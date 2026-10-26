"""Teste do painel/sync/sincronizar.py: arquivo de exemplo → linha esperada no banco.

Roda numa RAIZ TEMPORÁRIA (PAINEL_PROJETO) e num BANCO DESCARTÁVEL (`painel_teste_<pid>`, criado e apagado no mesmo
Postgres do painel, 127.0.0.1:55322). Nada do projeto real é lido como dado nem escrito. O banco do Carlos (`postgres`)
só é LIDO, numa transação só-leitura, para o teste de permissões.
Tokens e custos: registros SINTÉTICOS do Claude Code numa HOME temporária (<home>/.claude/projects/
-Users-teste-Documents-CONTENT-AI, o caminho que o tokens-custos.py de referência lê), para rodar o próprio script sobre
os mesmos arquivos e comparar (reconciliação). Os ~/.claude reais nunca são lidos.

Uso (da raiz do projeto):  uv run python painel/tests/test_sincronizar.py [--manter]
  --manter   não apaga a raiz temporária nem o banco de teste (para investigar uma falha).
Precisa do Supabase do painel ligado (bash painel/iniciar.sh — passa pela rede só-no-Mac).
"""
from __future__ import annotations

import ast
import datetime as dt
import unicodedata
import random
import time
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import importlib.util
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True  # nem __pycache__ no projeto real

CODIGO = Path(__file__).resolve().parents[2]
# PAINEL_TESTE_SYNC: rodar a suíte contra uma cópia de trabalho (o launchd só roda o sincronizar.py)
SYNC = Path(os.environ.get("PAINEL_TESTE_SYNC") or CODIGO / "painel" / "sync" / "sincronizar.py").resolve()
REFERENCIA = CODIGO / "painel" / "referencias" / "claude-design" / "telas-2026-10-23" / "tokens-custos.py"
MIGRACOES = sorted((CODIGO / "painel" / "supabase" / "migrations").glob("*.sql"))
ROOT = Path(tempfile.mkdtemp(prefix="korvu-painel-")).resolve()
OUTRA = Path(tempfile.mkdtemp(prefix="korvu-painel-outra-")).resolve()  # raiz "errada" para o teste da raiz única
HOME = Path(tempfile.mkdtemp(prefix="korvu-painel-home-")).resolve()  # HOME dos subprocessos: nunca o ~/.claude real
REG = HOME / ".claude" / "projects" / "-Users-teste-Documents-CONTENT-AI"  # onde o tokens-custos.py procura
os.environ["CONTENT_AI_ROOT"] = str(ROOT)  # o portoes.py deste processo monta os veredictos na raiz temporária
sys.path.insert(0, str(CODIGO / "scripts"))
import portoes  # noqa: E402

import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

SERVIDOR = "postgresql://postgres:postgres@127.0.0.1:55322"
BANCO_REAL = f"{SERVIDOR}/postgres"
NOME_TESTE = f"painel_teste_{os.getpid()}"
BANCO_TESTE = f"{SERVIDOR}/{NOME_TESTE}"
NOME_SCRIPT = f"painel_teste_{os.getpid()}_script"  # a regra do script (1.ª linha), só para a reconciliação (a)
BANCO_SCRIPT = f"{SERVIDOR}/{NOME_SCRIPT}"
PORTA_MORTA = "postgresql://postgres:senha-que-nao-pode-vazar@127.0.0.1:59999/postgres"
TABELAS = ["departamentos", "agentes", "videos", "portoes_estado", "veredictos", "fila", "publicacoes", "metricas",
           "perfil_snapshots", "perfil_demografia", "sincronizacoes", "precos_modelo", "cambio", "execucoes",
           "uso_execucao", "nao_publicar", "biblioteca_materiais", "biblioteca_arquivos", "biblioteca_referencias",
           "biblioteca_mais_utilizados", "prontos", "calendario_vagas", "perfil_diario", "looks", "capa_estilos",
           "capa_estilos_exemplos", "legenda_estilos", "fontes", "sistema_ferramentas", "modelos_descricao", "animacoes",
           "sistema_contagens"]
PRIVILEGIOS = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]

RES: list[tuple[str, bool, str]] = []


def ok(nome: str, cond, detalhe="") -> None:
    RES.append((nome, bool(cond), str(detalhe)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {nome}" + (f" — {detalhe}" if detalhe and not cond else ""))


def igual(nome: str, obtido, esperado) -> None:
    ok(nome, obtido == esperado, f"obtido {obtido!r} · esperado {esperado!r}")


# ───────────────────────── a raiz de exemplo ─────────────────────────

def escrever(rel: str, conteudo, raiz: Path = ROOT) -> Path:
    p = raiz / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(conteudo, (dict, list)):
        p.write_text(json.dumps(conteudo, ensure_ascii=False, indent=1), encoding="utf-8")
    elif isinstance(conteudo, bytes):
        p.write_bytes(conteudo)
    else:
        p.write_text(conteudo, encoding="utf-8")
    return p


HISTORICO = [{"estado": "roteiro", "em": "2026-10-28T10:00:00+00:00", "nota": "rascunho"},
             {"estado": "edicao", "em": "2026-10-29T18:00:00+00:00", "nota": "EDL v1"}]
HINTON_L1, HINTON_L3 = "2026-10-16T11:11:43+01:00", "2026-10-22T14:00:07+01:00"
PERFIL_LIDO = "2026-10-22T14:00:32+01:00"


def montar_projeto() -> None:
    # equipe: skills locais (remotion-* fica de fora), comandos e fichas dos agentes
    for s in ("supabase", "legendas-animadas", "capa-reels", "remotion-render"):
        (ROOT / ".claude" / "skills" / s).mkdir(parents=True)
    escrever(".claude/commands/status.md", "Mostra o estado; chama o portao-dados e o engenheiro-backend-x.\n")
    escrever(".claude/commands/fila.md", "Fila de publicação. Quem mexe no banco é o engenheiro-backend.\n")
    escrever(".claude/agents/engenheiro-backend.md",
             "---\nname: engenheiro-backend\ndescription: Engenheiro do banco do painel.\n"
             "tools: Read, Write, Bash\nmodel: opus\n---\n\n"
             "Use a skill supabase. Leia skills/capa-reels/SKILL.md. Rode `design:design-critique` e `watch`.\n"
             "Nunca `remotion-render`.\n")
    escrever(".claude/agents/portao-dados.md",
             "---\nname: portao-dados\ndescription: Portão dos dados: audita o banco.\ntools: Read, Grep\n"
             "model: opus\n---\n\nConfira painel/supabase/migrations e o arquivo legendas-animadas-velho.txt.\n"
             "`dataviz-extra` não é skill.\n")
    escrever("painel/equipe.yaml", """\
departamentos:
  - id: direcao
    nome: direção
    descricao: Organiza o pipeline.
    gerente: diretor
  - id: tecnologia
    nome: tecnologia
    descricao: Constrói o painel.
    gerente: portao-dados
agentes:
  - id: diretor
    nome: Atlas
    cargo: diretor de operações
    departamento: direcao
    papel: diretor
    resumo: O Claude principal.
    personalidade: Calmo.
  - id: portao-dados
    nome: Sérgio Lemos
    cargo: gerente · portão dos dados
    departamento: tecnologia
    papel: portao
    resumo: Audita o banco.
    personalidade: Desconfiado.
  - id: engenheiro-backend
    nome: Mateus Pacheco
    cargo: engenheiro back-end
    departamento: tecnologia
    papel: construtor
    resumo: Banco e sincronizador.
""")
    escrever("painel/web/public/equipe/portao-dados.png", b"\x89PNG retrato")
    escrever("painel/web/public/equipe/portao-dados.jpg", b"\xff\xd8 foto")  # .jpg vence .png
    escrever("painel/web/public/equipe/diretor.png", b"\x89PNG diretor")    # só .png: vale o .png

    # vídeos: tracker (colunas por posição) + status.json, que vence o tracker
    escrever("_controle/tracker.md", """\
# Tracker de vídeos

| Slug | Tema | Pilar | Estrutura | Hook | CTA | Estado | Atualizado |
|---|---|---|---|---|---|---|---|
| 2026-10-30-com-status | Contexto antes de pedir | tutoriais-rapidos | narrativo | A | PROMPT | roteiro | 2026-10-28 10:00 |
| 2026-10-31-sem-status | Quem é Ana—Lu - a pesquisadora — notas internas (v2) | perfil | narrativo (v2) | B | AULA | gravacao | 2026-10-20 10:00 |
| linha sem slug | x | x | x | x | x | x | x |
""")
    escrever("videos/2026-10-30-com-status/status.json",
             {"slug": "2026-10-30-com-status", "estado": "edicao", "atualizado": "2026-10-29T18:00:00+00:00",
              "historico": HISTORICO})
    escrever("videos/2026-10-30-com-status/roteiro.md", "# roteiro de teste\n\n| L01 | Oi. |\n")
    escrever("videos/2026-10-30-com-status/roteiro.json", {"slug": "2026-10-30-com-status", "versao": 3,
                                                           "cta_tipo": "palavra-material", "cta_palavra": "PROMPT",
                                                           "extras": [{"id": "E01"}, {"id": "E02"}], "linhas": []})
    escrever("videos/2026-10-30-com-status/capa/capa.png", b"capa v1")
    (ROOT / "videos" / "2026-10-31-sem-status").mkdir(parents=True)
    escrever("videos/2026-11-01-fora-do-tracker/status.json",
             {"slug": "2026-11-01-fora-do-tracker", "estado": "roteiro", "atualizado": "2026-11-01T09:00:00+00:00",
              "historico": []})
    escrever("videos/2026-11-04-sem-roteiro/status.json",  # vídeo SEM roteiro.md (os outros 3 têm): mais utilizados
             {"slug": "2026-11-04-sem-roteiro", "estado": "roteiro", "atualizado": "2026-11-04T09:00:00+00:00",
              "historico": []})
    escrever("videos/_modelo/status.json", {"estado": "roteiro"})  # pasta com "_" não é vídeo

    # fila: uma pasta com post.json (trial), uma legada sem trial, uma sem post.json (só portão)
    escrever("06-publicar/2026-10-30-com-status/post.json", {
        "slug": "2026-10-30-com-status", "publicar_em": "2026-10-30T21:00:00+00:00",
        "plataformas": ["instagram", "facebook"], "estado": "agendado", "confirmar": True,
        "instagram": {"legenda_arquivo": "legenda-instagram.txt", "capa": "capa/capa.png", "share_to_feed": True,
                      "trial": {"graduation_strategy": "MANUAL"}},
        "facebook": {"legenda_arquivo": "legenda-facebook.txt"},
        "material": {"palavra": "PROMPT", "arquivo": "material/guia.pdf", "titulo": "o guia"}})
    escrever("06-publicar/2026-10-28-legado/post.json", {
        "slug": "2026-10-28-legado", "publicar_em": "2026-10-28T20:00:00+01:00", "plataformas": ["instagram"],
        "estado": "agendado", "confirmar": False, "instagram": {"capa": "capa/capa.png"},
        "material": {"palavra": "LIVRO"}})
    escrever("06-publicar/2026-10-29-sem-post/video/video.mp4", b"video sem post")
    escrever("_controle/gauntlet-legado.json", {"slugs": ["2026-10-28-legado", "2026-11-03-legado-selado"]})

    # desempenho: trial nas duas formas (objeto e texto), o caso Hinton (tempo médio > duração) e leitura sem resumo
    leitura = lambda lido, dias, tm, pct, views, plays, tmfb: {  # noqa: E731
        "lido_em": lido, "dias_desde_publicacao": dias,
        "resumo": {"instagram": {"views": views, "alcance": views + 1, "curtidas": 1, "comentarios": 2,
                                 "salvamentos": 3, "compartilhamentos": 4, "tempo_medio_s": tm,
                                 "pct_medio_assistido": pct},
                   "facebook": {"plays": plays, "tempo_medio_s": tmfb},
                   "palavra": {"comentarios": 5, "directs": 6}}}
    escrever("07-publicados/2026-10-20-hinton/metricas.json", {
        "slug": "2026-10-20-hinton", "publicado_em": "2026-10-15T11:44:34+01:00", "duracao_s": 158.68,
        "palavra": "NOBEL", "trial": {"graduation_strategy": "SS_PERFORMANCE"}, "tema": "Hinton", "pilar": "perfil",
        "permalink_instagram": "https://www.instagram.com/reel/X/", "permalink_facebook": "https://fb/reel/1/",
        "leituras": [leitura(HINTON_L1, 0.98, 22.79, 14.4, 8, 2, 2.5),
                     leitura(HINTON_L3, 7.09, 1512.69, 953.3, 11, 4, 1.73)]})
    escrever("07-publicados/2026-09-17-demis/metricas.json", {
        "slug": "2026-09-17-demis", "publicado_em": "2026-09-17T20:00:00+01:00", "duracao_s": 57.84,
        "palavra": None, "trial": "MANUAL", "tema": "Demis", "pilar": "perfil",
        "leituras": [{"lido_em": "2026-10-13T18:22:21+01:00", "dias_desde_publicacao": 26.0},
                     leitura("2026-10-16T11:11:53+01:00", 28.6, 11.66, 20.2, 50, 3, 4.0)]})
    escrever("07-publicados/2026-10-20-fei-fei/metricas.json", {
        "slug": "2026-10-20-fei-fei", "publicado_em": "2026-10-20T21:14:22+01:00", "duracao_s": 168.44,
        "trial": {"graduation_strategy": "SS_PERFORMANCE"},  # objeto, só no metricas.json
        "tema": "Fei-Fei", "pilar": "perfil", "leituras": [leitura("2026-10-22T13:59:51+01:00", 1.7, 9.05, 5.4, 9, 1, 3.0)]})
    (ROOT / "07-publicados" / "2026-10-23-sem-metricas").mkdir(parents=True)  # publicado, ainda sem leitura

    # perfil: quebra por tipo de seguidor (pela chave, não pela posição) e demografia
    escrever("_controle/perfil/2026-10-22.json", {
        "lido_em": PERFIL_LIDO,
        "instagram": {
            "conta": {"followers_count": 3631, "follows_count": 7505, "media_count": 5},
            "janela": {"dias": 28},
            "metricas_conta": {
                "reach": {"valor": 529}, "views": {"valor": 2448}, "accounts_engaged": {"valor": 34},
                "total_interactions": {"valor": 99}, "profile_views": {"valor": 56},
                "profile_links_taps": {"valor": 7},
                "reach_por_follow_type": {"valor": 529, "quebras": [{"dimensao": ["follow_type"], "resultados": [
                    {"chave": ["NON_FOLLOWER"], "valor": 307}, {"chave": ["FOLLOWER"], "valor": 206}]}]}},
            "demografia": {
                "follower_demographics": {
                    "country": [{"chave": ["GW"], "valor": 1741}, {"chave": ["BR"], "valor": 504}],
                    "city": [{"chave": ["Bissau, Bissau"], "valor": 1717}],
                    "age": [{"chave": ["25-34"], "valor": 1218}],
                    "gender": [{"chave": ["M"], "valor": 1624}]},
                "reached_audience_demographics": {
                    "country": [{"chave": ["BR"], "valor": 197}],
                    "gender": [{"chave": ["F", "25-34"], "valor": 81}]}}},
        "facebook": {"pagina": {"followers_count": 0}}})
    escrever("_controle/perfil/2026-10-16.json", {
        "lido_em": "2026-10-16T10:00:00+01:00",
        "instagram": {"conta": {"followers_count": 3600}, "metricas_conta": {"reach": {"valor": 400}}}})

    # portões: vídeo com imagem BLOQUEADA; painel com interface APROVADA, dados APROVADO e depois mudado (vencido)
    escrever("painel/web/src/app/page.tsx", "export default function P() { return null }\n")
    escrever("painel/supabase/migrations/0001_x.sql", "create table x (id int);\n")
    escrever("painel/portoes/interface-v1.md", "relatório\n")
    escrever("painel/portoes/dados-v1.md", "relatório\n")
    escrever("videos/2026-10-30-com-status/qa/portoes/imagem-v1.md", "relatório\n")
    v = ROOT / "videos" / "2026-10-30-com-status"
    painel = ROOT / "painel"

    def registrar(alvo, portao, resultado, relatorio, s0=0):
        imp = portoes.impressao(portoes.arquivos_da_area(alvo, portao))
        return portoes.registrar(alvo, portao, resultado, imp, relatorio, s0, 0, 0)

    registrar(v, "imagem", "BLOQUEADO", "videos/2026-10-30-com-status/qa/portoes/imagem-v1.md", s0=1)
    registrar(painel, "interface", "APROVADO", "painel/portoes/interface-v1.md")
    registrar(painel, "dados", "APROVADO", "painel/portoes/dados-v1.md")
    escrever("painel/supabase/migrations/0001_x.sql", "create table x (id bigint);\n")  # mudou depois do APROVADO

    # câmbio do custo de IA: várias datas e duas moedas (a tela usa a mais recente)
    escrever("painel/cambio.yaml", CAMBIO_YAML)

    # fila (PI39): os quatro casos do portoes.conferir_pacote, como o publicar.py chama na hora de publicar
    escrever("06-publicar/2026-10-28-legado/pacote.json", {"slug": "2026-10-28-legado", "qa": "PASS", "arquivos": {}})
    escrever("06-publicar/2026-10-30-com-status/pacote.json",  # sem selo e FORA da lista: recusado
             {"slug": "2026-10-30-com-status", "qa": "PASS", "arquivos": {}})
    # origem com roteiro, imagem e corte APROVADOS (pauta sem arquivos = não se aplica)
    o = ROOT / "videos" / "2026-11-01-fora-do-tracker"
    escrever("videos/2026-11-01-fora-do-tracker/roteiro.md", "# roteiro aprovado\n\n| L01 | Oi. |\n")
    escrever("videos/2026-11-01-fora-do-tracker/capa/capa.png", CAPA)
    escrever("videos/2026-11-01-fora-do-tracker/edicao/final.mp4", FINAL)
    for portao in ("roteiro", "imagem", "corte"):
        escrever(f"videos/2026-11-01-fora-do-tracker/qa/portoes/{portao}-v1.md", "relatório\n")
        registrar(o, portao, "APROVADO", f"videos/2026-11-01-fora-do-tracker/qa/portoes/{portao}-v1.md")
    selo = {"versao": 1, "origem": "videos/2026-11-01-fora-do-tracker", "selado_em": "2026-11-01T10:00:00+00:00",
            "veredictos": {}, "arquivos": {"video/video-final.mp4": hashlib.sha256(FINAL).hexdigest(),
                                           "capa/capa.png": hashlib.sha256(CAPA).hexdigest()}}
    for slug, s in (("2026-11-02-selado", selo),  # selado normal, tudo aprovado: pode sair
                    ("2026-11-03-legado-selado", {**selo, "origem": "videos/2026-10-30-com-status"})):  # regra normal
        escrever(f"06-publicar/{slug}/video/video-final.mp4", FINAL)
        escrever(f"06-publicar/{slug}/capa/capa.png", CAPA)
        escrever(f"06-publicar/{slug}/legenda-instagram.txt", "PROMPT legenda\n")
        escrever(f"06-publicar/{slug}/legenda-facebook.txt", "legenda\n")
        escrever(f"06-publicar/{slug}/post.json", {
            "slug": slug, "publicar_em": "2026-11-02T20:00:00+00:00", "plataformas": ["instagram"],
            "estado": "agendado", "confirmar": False, "instagram": {"capa": "capa/capa.png"}})
        escrever(f"06-publicar/{slug}/pacote.json", {"slug": slug, "qa": "PASS", "cta_palavra": "PROMPT",
                                                    "arquivos": {"video": "video/video-final.mp4",
                                                                 "capa": "capa/capa.png"}, "gauntlet": s})
    escrever("painel/portoes/publicacao-selado-v1.md", "relatório\n")
    ss = ROOT / "videos" / "2026-10-31-sem-status"
    escrever("videos/2026-10-31-sem-status/roteiro.md", "# roteiro\n\n| L01 | Olá. |\n")
    escrever("videos/2026-10-31-sem-status/roteiro.json", {"slug": "2026-10-31-sem-status", "versao": 1,
                                                           "cta_tipo": "seguir", "cta_palavra": "  ", "extras": [],
                                                           "linhas": []})
    escrever("videos/2026-10-31-sem-status/qa/portoes/roteiro.md", "relatório\n")
    rel = "videos/2026-10-31-sem-status/qa/portoes/roteiro.md"
    for _ in range(3):
        registrar(ss, "roteiro", "BLOQUEADO", rel, s0=1)  # a 3.ª volta vira ESCALADO
    portoes.registrar(ss, "roteiro", "APROVADO", portoes.impressao(portoes.arquivos_da_area(ss, "roteiro")), rel,
                      0, 0, 2, nota=NOTA, decisao=DECISAO)
    # PD20: o portoes.py grava `em` com resolução de segundo — os 4 no MESMO segundo, como acontece de verdade
    livro = json.loads((ss / "portoes.json").read_text(encoding="utf-8"))
    for v in livro["veredictos"]:
        v["em"] = "2026-10-31T10:00:00+00:00"
    (ss / "portoes.json").write_text(json.dumps(livro, ensure_ascii=False, indent=2), encoding="utf-8")
    registrar(ROOT / "06-publicar" / "2026-11-02-selado", "publicacao", "APROVADO",
              "painel/portoes/publicacao-selado-v1.md")
    # regra do vídeo: pasta de pacote sem selo cujo slug começa por um vídeo (→ o vídeo); publicada sem metricas.json
    escrever("07-publicados/2026-10-30-com-status-a/pacote.json", {
        "slug": "2026-10-30-com-status-a", "qa": "PASS", "duracao": 34.44, "tema": "Tema do pacote",
        "pilar": "tutoriais-rapidos", "cta_palavra": "LIVRO"})
    escrever("07-publicados/2026-10-30-com-status-a/post.json", {
        "slug": "2026-10-30-com-status-a", "publicar_em": "2026-10-22T21:00:00+01:00",
        "publicado_em": "2026-10-22T21:19:22+01:00", "plataformas": ["instagram", "facebook"], "estado": "publicado",
        "instagram": {"permalink": "https://www.instagram.com/reel/A/",
                      "trial": {"graduation_strategy": "SS_PERFORMANCE"}},  # trial com valor, só no post.json
        "facebook": {"permalink": "https://www.facebook.com/reel/2/", "tipo": "reel"}, "material": {"palavra": "LIVRO"}})
    escrever("07-publicados/2026-10-31-sem-status-b/post.json", {  # só post.json, sem trial nenhum
        "slug": "2026-10-31-sem-status-b", "publicado_em": "2026-10-31T19:00:00+00:00", "plataformas": ["instagram"],
        "estado": "publicado", "instagram": {"permalink": "https://www.instagram.com/reel/B/"}})
    # o Hinton tem post.json, metricas.json E pacote.json, com valores DIFERENTES: o post.json vence o metricas.json em
    # publicado_em, palavra, trial e permalinks; o pacote.json vence em duração, tema e pilar
    escrever("07-publicados/2026-10-20-hinton/post.json", {
        "slug": "2026-10-20-hinton", "publicado_em": "2026-10-15T11:50:00+01:00", "plataformas": ["instagram", "facebook"],
        "estado": "publicado", "instagram": {"permalink": "https://www.instagram.com/reel/X/",
                                             "trial": {"graduation_strategy": "MANUAL"}},
        "facebook": {"permalink": "https://fb/reel/POST/"}, "material": {"palavra": "NOBELPOST"}})
    escrever("07-publicados/2026-10-20-hinton/pacote.json", {
        "slug": "2026-10-20-hinton", "qa": "PASS", "duracao": 158.7, "tema": "Tema do pacote Hinton",
        "pilar": "perfil-pacote"})

    # fases: gravação em brutos/principal/ (só listagem e tamanho), prontos em 05-render-pronto/ e a trava
    g = "videos/2026-10-30-com-status/brutos/principal/"
    for nome, conteudo, mtime in (("camera-01.MOV", b"x" * 100, 1_792_000_000), ("camera-02.mp4", b"y" * 50, 1_792_500_000),
                                  ("sub/camera-03.mov", b"z" * 7, 1_791_000_000), (".DS_Store", b"ds", 1_793_000_000),
                                  ("._camera-01.MOV", b"apple", 1_793_000_000), ("vazio.mov", b"", 1_793_000_000),
                                  ("notas.txt", b"texto", 1_793_000_000)):
        os.utime(escrever(g + nome, conteudo), (mtime, mtime))
    escrever("videos/2026-10-31-sem-status/brutos/principal/.DS_Store", b"ds")  # pasta só com lixo: não gravado
    # o relógio da câmera em 2024 (como os PRAQ*.MOV reais): gravado, com a data do arquivo marcada como suspeita
    os.utime(escrever("videos/2026-11-01-fora-do-tracker/brutos/principal/PRAQ0001.MOV", b"w" * 9),
             (1_721_000_000, 1_721_000_000))
    escrever("05-render-pronto/2026-10-30-com-status/pacote.json", {
        "slug": "2026-10-30-com-status", "qa": "PASS", "duracao": 58.7, "criado_em": "2026-10-30T18:00:00+01:00",
        "cta_palavra": "PROMPT"})
    escrever("05-render-pronto/2026-10-31-sem-status/pacote.json",  # sem criado_em nem cta_palavra
             {"slug": "2026-10-31-sem-status", "qa": "FAIL", "duracao": 12, "cta_palavra": ""})
    escrever("05-render-pronto/2026-11-01-fora-do-tracker-v2/pacote.json",  # sem duracao
             {"slug": "x", "qa": "pass", "criado_em": "2026-11-01T10:00:00Z", "cta_palavra": "X"})
    escrever("_controle/calendario.md", CALENDARIO_MD)
    for nome, conteudo in PERFIL_DIARIO.items():
        escrever(f"_controle/perfil/diario/{nome}", conteudo)
    escrever("_controle/nao-publicar.json", NAO_PUBLICAR)

    # biblioteca: material/ e brutos/extras/ da sem-status (os outros vídeos não têm material)
    for rel_, conteudo in BIBLIOTECA.items():
        escrever(f"videos/2026-10-31-sem-status/{rel_}", conteudo)
    os.utime(ROOT / "videos/2026-10-31-sem-status/material/fotos/velha.jpg", (1_721_000_000, 1_721_000_000))
    for lixo in ("material/.DS_Store", "material/youtube/._t1.mp4", "material/vazio.png", "material/.oculta/y.mp4"):
        escrever(f"videos/2026-10-31-sem-status/{lixo}", b"" if lixo.endswith("vazio.png") else b"lixo")
    escrever("videos/_teste-x/material/a.mp4", b"teste")  # pasta _teste-*: fora (PI43)
    escrever("00-marca/referencias/capas/a.jpg", b"xxx")
    escrever("00-marca/referencias/legendas/.gitkeep", b"")
    escrever("painel/referencias/BRIEF.md", b"bbbb")
    escrever("painel/referencias/.DS_Store", b"ds")
    escrever("painel/referencias/sub/.oculta/z.png", b"zz")
    escrever("00-marca/voz-carlos.md", "voz\n")
    montar_acervo()


CAPA, FINAL = b"\x89PNG capa aprovada", b"mp4 final aprovado"
NOTA, DECISAO = "nota do portão: S2 no backlog", "opção B do Carlos: segue assim"
# calendário: fuso fora do padrão, dia com acento e com "-feira", lista de horas, hora sem aspas (YAML 1.1 = 1260)
CALENDARIO_MD = """# Calendário

```yaml
fuso: Europe/Lisbon
vagas_semanais:        # dia: hora (24h)
  domingo: "19:00"
  terça: ["21:00", "08:30"]
  quarta: 21:00
  Sexta-feira: "7:05"
plataformas_padrao: [instagram]
```

## Agenda
| Data/hora | Slug | Plataformas | Estado |
|---|---|---|---|
"""
PERFIL_DIARIO = {  # a proposta para o perfil.py: um arquivo por dia (UTC)
    "2026-10-23.json": {"dia": "2026-10-23", "lido_em": "2026-10-24T09:30:00+01:00",
                        "metricas": {"reach": 41, "views": 230, "follows_and_unfollows": None}},
    "2026-10-24.json": {"dia": "2026-10-24", "lido_em": "2026-10-25T09:30:00Z",
                        "metricas": {"reach": 50, "seguidores": 3640}}}
BIBLIOTECA = {  # caminho (relativo ao vídeo) → conteúdo; o tamanho é o que o teste confere
    "material/guia-a.pdf": b"%PDF-a", "material/guia-b.pdf": b"%PDF-bb",
    "material/_fonte/guia-b-previa.png": b"p" * 10, "material/_fonte/guia-b-previa-p2.png": b"p" * 11,
    "material/_fonte/material.md": b"m" * 5, "material/dossie.md": b"d" * 8, "material/fontes.json": b"[1,2,3,4]",
    "material/solto.md": b"s" * 4, "material/youtube/cortes/contato.jpg": b"j" * 12, "material/youtube/t1.mp4": b"v" * 20,
    "material/screnn record/tela.mov": b"t" * 30, "material/obra/filme.mp4": b"o" * 40, "material/obra/legenda.vtt": b"lll",
    "material/estranha/nota.txt": b"n" * 6, "material/fotos/velha.jpg": b"f" * 13,
    "brutos/extras/E01.png": b"e" * 15, "brutos/extras/E02.mp4": b"e" * 25, "brutos/extras/_alternativas/E09.mp4": b"e" * 35}
NAO_PUBLICAR = {"descricao": "travas de teste", "travas": [
    {"slug": "2026-10-30-com-status", "motivo": "teste de cor, não publicar", "desde": "2026-09-19"},
    {"slug": "2026-11-01-fora-do-tracker-v2", "motivo": "variante de teste", "desde": "2026-10-23"}]}


CAMBIO_YAML = """\
# câmbio de teste
taxas:
  - data: 2026-10-01
    moeda: GBP
    valor: 0.75
    fonte: teste antigo
  - data: 2026-10-23
    moeda: GBP
    valor: 0.7465
    fonte: XE, média de mercado
  - data: "2026-10-23"
    moeda: EUR
    valor: 0.86125
    fonte: teste euro
"""


# ───────────────────────── registros sintéticos do Claude Code ─────────────────────────

PEDIDO_SECRETO, RESPOSTA_SECRETA = "PEDIDO-QUE-NAO-PODE-IR-PARA-O-BANCO", "RESPOSTA-QUE-NAO-PODE-IR-PARA-O-BANCO"
OPUS, SONNET, FABLE, OPUS5 = "claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1", "claude-opus-5"
SEM_PRECO = "claude-sem-preco-1"  # fictício: modelo que não está em PRECOS
M = 1_000_000


def resp(mid, ts, modelo=OPUS, e=0, c5=0, c1=0, cl=0, s=0, uuid=None, ttl=True, gravado=None,
         provisorio=False) -> dict:
    """Uma linha de resposta como o Claude Code grava (message.usage + model + id, timestamp ISO UTC). provisorio=True =
    a 1.ª linha das versões 2.1.270–2.1.304: o usage do message_start, sem iterations nem output_tokens_details."""
    u = {"input_tokens": e, "cache_creation_input_tokens": c5 + c1 if gravado is None else gravado,
         "cache_read_input_tokens": cl, "output_tokens": s, "service_tier": "standard"}
    if ttl:
        u["cache_creation"] = {"ephemeral_5m_input_tokens": c5, "ephemeral_1h_input_tokens": c1}
    if not provisorio:
        u["iterations"] = [{"input_tokens": e, "output_tokens": s}]
        u["output_tokens_details"] = {"thinking_tokens": 0}
    msg = {"model": modelo, "role": "assistant", "usage": u, "content": [{"type": "text", "text": RESPOSTA_SECRETA}]}
    if mid:
        msg["id"] = mid
    return {"type": "assistant", "uuid": uuid or f"u-{mid}-{ts}", "timestamp": ts, "message": msg}


def pedido(conteudo) -> dict:
    return {"type": "user", "uuid": "u-pedido", "timestamp": "2026-10-01T09:59:00.000Z",
            "message": {"role": "user", "content": conteudo}}


def jsonl(rel: str, linhas: list, cauda: str = "", meta: dict | None = None) -> None:
    escrever(rel, "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas) + cauda, raiz=REG)
    if meta is not None:
        escrever(rel[: -len(".jsonl")] + ".meta.json", meta, raiz=REG)


def montar_registros() -> None:
    """14 execuções (13 tarefas: sess-b só tem modelo sem preço; 12 na janela do script, sem a sess-e de 16/09). Datas
    entre 24/09 e 23/10/2026 (a janela do script), mais 16/09, 20/09 e 24/10 para a janela."""
    a1 = resp("m-a1", "2026-10-01T10:00:02.000Z", e=1000, c5=2000, cl=100000, s=500)  # a linha final
    jsonl("sess-a.jsonl", [
        {"type": "queue-operation", "operation": "enqueue"},
        {"type": "user", "toolUseResult": {"usage": {"input_tokens": 999}}, "message": {"role": "user", "content": "x"}},
        # o formato real (agent-ae5773a0d0643ee67, msg_011CgFohH232CdGk3KXuDG3Z: 3 / 3 / 629): um bloco por linha, as
        # duas primeiras com o usage provisório (saída 3), a última com o final — vale a última
        resp("m-a1", "2026-10-01T10:00:00.000Z", e=1000, c5=2000, cl=100000, s=3, provisorio=True),
        resp("m-a1", "2026-10-01T10:00:01.000Z", e=1000, c5=2000, cl=100000, s=3, provisorio=True),
        a1,
        resp("m-a2", "2026-10-13T23:30:00.000Z", e=10, s=10),  # 14/10 00:30 em Londres: o dia é o UTC (13/10)
        resp("m-a3", "2026-09-20T12:00:00.000Z", e=5000),      # antes da janela do script
        resp("m-a4", "2026-10-24T00:00:00.000Z", e=7000),      # depois da janela do script
        resp("m-a5", "2026-10-02T08:00:00.000Z", modelo=SEM_PRECO, e=777),
        resp("m-a6", "2026-10-02T08:00:01.000Z", modelo="<synthetic>"),
        resp(None, "2026-10-03T08:00:00.000Z", e=300, uuid="u-sem-id"),  # sem message.id: deduplica pelo uuid
        resp(None, "2026-10-03T08:00:05.000Z", e=300, uuid="u-sem-id"),  # a mesma, repetida: conta 1 vez
        {"type": "assistant", "message": None, "usage": "solto"},
        ], cauda='isto não é JSON mas cita "usage"\n'
                 '{"type":"assistant","timestamp":"2026-10-04T00:00:00.000Z","message":{"id":"m-cortada",'
                 '"model":"claude-opus-5-5","usage":{"input_tokens":123')  # a sessão ativa: última linha cortada
    jsonl("sess-a/subagents/agent-a01.jsonl",
          [pedido(f"{PEDIDO_SECRETO} Audite videos/2026-10-30-com-status/roteiro.md."),
           {**a1, "timestamp": "2026-10-01T10:00:05.000Z"}],  # a mesma mensagem noutro arquivo conta de novo
          meta={"agentType": "portao-dados", "description": "auditoria v1", "spawnDepth": 1, "finished": True})
    jsonl("sess-a/subagents/agent-a02.jsonl",  # os 5 "vídeos" que o script inventava
          [pedido("Leia painel/portoes/dados-2026-10-23-v1.md, o 2026-10-22-v, videos/2026-10-22-v1/x.md, "
                  "videos/2026-10-22-v2 e ebook/output/2026-05-08-201030/."),
           resp("m-c1", "2026-10-05T12:00:00.000Z", modelo=SONNET, e=M, c5=M, c1=M, cl=M, s=M)],
          meta={"agentType": "general-purpose"})
    jsonl("sess-a/subagents/agent-a03.jsonl",
          [pedido("Slug: `2026-10-30-com-status` (sem pasta não conta). Veja videos/2026-10-22-nao-existe/, publique "
                  "07-publicados/2026-10-30-com-status-a/ e 07-publicados/2026-10-30-com-status-a/capa; depois "
                  "06-publicar/2026-10-28-legado/."),
           resp("m-d1", "2026-10-06T12:00:00.000Z", modelo=FABLE, e=M, c5=M, c1=M, cl=M, s=M)],
          meta={"agentType": "Explore"})
    jsonl("sess-a/subagents/agent-a04.jsonl",
          [pedido("Construa em videos/2026-10-30-com-status/ o que falta (tecnologia: sem vídeo)."),
           resp("m-e1", "2026-10-07T12:00:00.000Z", e=M, c5=M, c1=M, cl=M, s=M)],
          meta={"agentType": "engenheiro-backend", "description": "backend"})
    jsonl("sess-a/subagents/agent-a05.jsonl",  # sem .meta.json; pedido em blocos (lista)
          [pedido([{"type": "text", "text": "Corte videos/2026-10-30-com-status agora."}]),
           resp("m-f1", "2026-10-08T12:00:00.000Z", e=100)])
    jsonl("sess-a/subagents/workflows/wf_teste-1/agent-a06.jsonl",
          [pedido("sem vídeo"), resp("m-g1", "2026-10-09T12:00:00.000Z", e=50, c5=1000, s=50, ttl=False)],
          meta={"agentType": "workflow-subagent", "description": "x" * 300, "spawnDepth": 2})
    jsonl("sess-a/subagents/workflows/wf_teste-1/journal.jsonl", [{"type": "launched"}])
    for n, tipo, txt in (("07", "claude", "Publique 06-publicar/2026-10-28-legado/."),
                         ("08", "Plan", "Veja 06-publicar/2026-11-02-selado/ e videos/2026-10-31-sem-status/."),
                         ("09", "agente-novo-xyz", "videos/2026-10-30-com-status/a, videos/2026-10-31-sem-status/b e "
                                               "videos/2026-10-31-sem-status/c")):
        jsonl(f"sess-a/subagents/agent-a{n}.jsonl", [pedido(txt), resp(f"m-{n}", "2026-10-10T12:00:00.000Z", e=10)],
              meta={"agentType": tipo})
    jsonl("sess-b.jsonl", [resp("m-k1", "2026-10-11T12:00:00.000Z", modelo=SEM_PRECO, e=4000)])  # não é tarefa
    jsonl("sess-c.jsonl", [resp("m-l1", "2026-10-12T12:00:00.000Z", e=2000, s=100)])
    jsonl("sess-e.jsonl", [resp("m-o1", "2026-09-16T12:00:00.000Z", modelo=OPUS5, e=M, c5=M, c1=M, cl=M, s=M)])
    jsonl(".oculto.jsonl", [resp("m-m1", "2026-10-12T12:00:00.000Z", e=99999)])  # o glob pula nomes com "."
    jsonl("sess-d/subagents/agent-dup.jsonl",
          [pedido("x"),
           resp("m-n1", "2026-10-13T23:59:59.000Z", e=10, c5=100, c1=300, gravado=500),  # detalhe ≠ total
           resp("m-n2", "2026-10-14T00:00:01.000Z", e=20)],
          meta={"agentType": "portao-dados"})
    escrever("sess-a/tool-results/x.txt", "não é jsonl\n", raiz=REG)


ESPERADO = {"departamentos": 2, "agentes": 3, "videos": 4, "portoes_estado": 4 * 4 + 5 + 3, "veredictos": 11,
            "fila": 4, "publicacoes": 5, "metricas": 5, "perfil_snapshots": 2, "perfil_demografia": 7,
            "precos_modelo": 4, "cambio": 3, "nao_publicar": 2, "biblioteca_materiais": 10, "biblioteca_arquivos": 18,
            "biblioteca_referencias": 2, "biblioteca_mais_utilizados": 4, "prontos": 3, "calendario_vagas": 5,
            "perfil_diario": 4, "looks": 5, "capa_estilos": 2, "capa_estilos_exemplos": 3, "legenda_estilos": 1,
            "fontes": 4, "sistema_ferramentas": 5, "modelos_descricao": 2, "animacoes": 3, "sistema_contagens": 1,
            "execucoes": 14,
            "uso_execucao": 21}


# ───────────────────────── utilidades ─────────────────────────

def foto(raiz: Path) -> dict[str, tuple]:
    """Tudo o que existe na raiz (inclusive ocultos): pastas e, de cada arquivo, tamanho, mtime e sha256."""
    out = {}
    for p in sorted(raiz.rglob("*")):
        rel = p.relative_to(raiz).as_posix()
        if p.is_dir():
            out[rel + "/"] = ("pasta",)
        else:
            out[rel] = (p.stat().st_size, p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
    return out


def sincronizar(*args: str, db: str, projeto: Path | None = ROOT, outra_raiz: Path | None = None,
                registros: Path | None = REG, home: Path = HOME, env_extra: dict | None = None):
    """O sincronizador num subprocesso, com HOME temporária (o ~/.claude real nunca entra) e PAINEL_REGISTROS nos
    registros sintéticos (registros=None: o padrão, derivado da raiz)."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("PAINEL_DB_URL", "PAINEL_PROJETO", "CONTENT_AI_ROOT", "PAINEL_REGISTROS", "TZ_PUBLICACAO")}
    env.update({"PAINEL_DB_URL": db, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "HOME": str(home)})
    if projeto is not None:
        env["PAINEL_PROJETO"] = str(projeto)
    if outra_raiz is not None:
        env["CONTENT_AI_ROOT"] = str(outra_raiz)
    if registros is not None:
        env["PAINEL_REGISTROS"] = str(registros)
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, str(SYNC), *args], env=env, cwd=str(OUTRA), capture_output=True,
                       text=True, encoding="utf-8", timeout=120)
    return r.returncode, r.stdout.strip().splitlines(), r.stderr.strip()


def contagens(linha: str) -> dict[str, int]:
    partes = linha.split()
    return {t: int(partes[partes.index(t) + 1]) for t in ESPERADO if t in partes}


def campo(linha: str, nome: str) -> str | None:
    """O valor depois de `nome` na linha do sincronizador (ex.: tokens, usd, usd_cache_1.25x)."""
    partes = linha.split()
    return partes[partes.index(nome) + 1] if nome in partes else None


def violacoes_de_permissao(con) -> list[str]:
    """O que anon/authenticated/service_role podem e não deviam (ou o service_role não pode e devia) no schema public.
    Só lê o catálogo (has_*_privilege)."""
    privs = PRIVILEGIOS + (["MAINTAIN"] if con.info.server_version >= 170000 else [])
    erros = []
    tabelas = con.execute("select c.oid, c.relname from pg_class c where c.relnamespace = 'public'::regnamespace "
                          "and c.relkind in ('r','p','v','m','f') order by 2").fetchall()
    for oid, nome in tabelas:
        for papel in ("anon", "authenticated", "service_role"):
            for pv in privs:
                tem = con.execute("select has_table_privilege(%s, %s::oid, %s)", [papel, oid, pv]).fetchone()[0]
                deve = papel == "service_role" and pv == "SELECT"
                if tem != deve:
                    erros.append(f"{nome}: {papel} {'TEM' if tem else 'NÃO tem'} {pv}")
            if papel != "service_role":
                for pv in ("SELECT", "INSERT", "UPDATE", "REFERENCES"):
                    if con.execute("select has_any_column_privilege(%s, %s::oid, %s)", [papel, oid, pv]).fetchone()[0]:
                        erros.append(f"{nome}: {papel} tem {pv} em coluna")
    for oid, nome in con.execute("select oid, relname from pg_class where relnamespace = 'public'::regnamespace "
                                 "and relkind = 'S'").fetchall():
        for papel in ("anon", "authenticated", "service_role"):
            for pv in ("USAGE", "SELECT", "UPDATE"):
                if con.execute("select has_sequence_privilege(%s, %s::oid, %s)", [papel, oid, pv]).fetchone()[0]:
                    erros.append(f"sequência {nome}: {papel} tem {pv}")
    for oid, nome in con.execute("select oid, proname from pg_proc where pronamespace = 'public'::regnamespace"
                                 ).fetchall():
        for papel in ("anon", "authenticated", "service_role"):
            if con.execute("select has_function_privilege(%s, %s::oid, 'EXECUTE')", [papel, oid]).fetchone()[0]:
                erros.append(f"função {nome}: {papel} executa")
    return erros


def violacoes_de_default(con) -> list[str]:
    """Default privileges do papel postgres (quem roda as migrações): o que a PRÓXIMA tabela, sequência ou função vai
    herdar. As entradas do schema public SOMAM às globais; a global de funções tem de existir, senão vale o padrão
    do Postgres (EXECUTE para PUBLIC, logo para anon)."""
    linhas = con.execute("""
        select case when d.defaclnamespace = 0 then 'global' else d.defaclnamespace::regnamespace::text end,
               d.defaclobjtype::text, case when a.grantee = 0 then 'PUBLIC' else a.grantee::regrole::text end,
               a.privilege_type
        from pg_default_acl d, aclexplode(d.defaclacl) a
        where d.defaclrole = 'postgres'::regrole and d.defaclnamespace in (0, 'public'::regnamespace)""").fetchall()
    erros = [f"default {onde}/{tipo}: {quem} {pv}" for onde, tipo, quem, pv in linhas
             if quem in ("anon", "authenticated", "PUBLIC")
             or (quem == "service_role" and (onde, tipo, pv) != ("public", "r", "SELECT"))]
    if not any(onde == "global" and tipo == "f" for onde, tipo, _, _ in linhas):
        erros.append("default global/f: sem entrada — função nova seria executável por PUBLIC (anon)")
    if ("public", "r", "service_role", "SELECT") not in linhas:
        erros.append("default public/r: service_role não lê as próximas tabelas")
    return erros


def tabelas_sem_rls(con) -> list[str]:
    return [r[0] for r in con.execute("select relname from pg_class where relnamespace = 'public'::regnamespace "
                                      "and relkind in ('r','p') and not relrowsecurity").fetchall()]


def somas(con, tabelas=TABELAS) -> dict[str, str]:
    return {t: con.execute(f"select count(*) || ':' || coalesce(md5(string_agg(x::text, '|' order by x::text)), '') "
                           f"from {t} x").fetchone()[0] for t in tabelas}


def linhas(con, sql: str, args=()) -> list[dict]:
    with con.cursor(row_factory=dict_row) as cur:
        return cur.execute(sql, args).fetchall()


def ts(txt: str) -> dt.datetime:
    return dt.datetime.fromisoformat(txt)


# ───────────────────────── casos ─────────────────────────

def casos_sem_banco() -> None:
    print("\n== --seco: lê tudo, não toca no banco nem no projeto ==")
    antes = foto(ROOT)
    rc, out, err = sincronizar("--seco", db=PORTA_MORTA, outra_raiz=OUTRA)
    ok("--seco sai 0 mesmo com o banco fora do ar (não conecta)", rc == 0 and not err, f"rc={rc} err={err[-300:]}")
    ok("--seco imprime uma linha só", len(out) == 1 and "(seco)" in out[0], out)
    igual("--seco: contagens = arquivos de exemplo", contagens(out[-1]) if out else {}, ESPERADO)
    ok("--seco não cria, muda nem apaga nada na raiz (nem o cache dos portões)", foto(ROOT) == antes)
    ok("raiz 'errada' (CONTENT_AI_ROOT) continua vazia", not any(OUTRA.iterdir()), list(OUTRA.iterdir()))

    print("\n== raiz configurável ==")
    rc, out, _ = sincronizar("--seco", db=PORTA_MORTA, projeto=None, outra_raiz=ROOT)
    igual("sem PAINEL_PROJETO, CONTENT_AI_ROOT vale para os dois", contagens(out[-1]) if out else {}, ESPERADO)

    print("\n== porta morta: uma linha ✗ e exit 1 ==")
    antes = foto(ROOT)
    rc, out, err = sincronizar(db=PORTA_MORTA)
    ok("exit 1", rc == 1, f"rc={rc}")
    ok("uma linha só, com ✗ e 'fora do ar'", len(out) == 1 and "✗" in out[0] and "fora do ar" in out[0], out)
    ok("a dica manda ligar pelo iniciar.sh (rede só-no-Mac), não por um `supabase start` solto (PD12)",
       out and "bash painel/iniciar.sh" in out[0] and "supabase start" not in out[0], out)
    ok("sem traceback no stderr", err == "", err[-300:])
    ok("a senha da URL não aparece na mensagem", "senha-que-nao-pode-vazar" not in " ".join(out) + err)
    ok("nada escrito na raiz", foto(ROOT) == antes)

    print("\n== arquivo ilegível: uma linha ✗, exit 1, nada gravado ==")
    quebrada = Path(tempfile.mkdtemp(prefix="korvu-painel-quebrada-")) / "raiz"
    shutil.copytree(ROOT, quebrada)
    mj = quebrada / "07-publicados" / "2026-10-20-hinton" / "metricas.json"
    mj.write_text(mj.read_text(encoding="utf-8")[:200], encoding="utf-8")  # escrita do metricas.py pela metade
    rc, out, err = sincronizar("--seco", db=PORTA_MORTA, projeto=quebrada)
    ok("JSON truncado → exit 1", rc == 1, f"rc={rc}")
    ok("uma linha ✗ que diz qual arquivo",
       len(out) == 1 and "✗" in out[0] and "07-publicados/2026-10-20-hinton/metricas.json" in out[0], out)
    ok("sem traceback", err == "", err[-300:])
    shutil.rmtree(quebrada.parent, ignore_errors=True)


# Chaves que o sincronizador lê, por arquivo → quem escreve esse arquivo. Se o produtor renomear uma chave (ex.: o
# metricas.py trocar pct_medio_assistido), o painel passaria a mostrar NULL sem erro: este caso pega antes.
CONTRATO = {
    "scripts/metricas.py": ["slug", "publicado_em", "tema", "pilar", "palavra", "duracao_s", "trial",
                            "permalink_instagram", "permalink_facebook", "leituras", "lido_em",
                            "dias_desde_publicacao", "resumo", "instagram", "facebook", "views", "alcance",
                            "tempo_medio_s", "pct_medio_assistido", "curtidas", "comentarios", "salvamentos",
                            "compartilhamentos", "plays", "directs"],
    "scripts/perfil.py": ["lido_em", "instagram", "facebook", "conta", "metricas_conta", "janela", "dias", "quebras",
                          "resultados", "chave", "valor", "demografia", "follower_demographics",
                          "reached_audience_demographics", "pagina", "reach", "views", "accounts_engaged",
                          "total_interactions", "profile_views", "follow_type"],
    "scripts/portoes.py": ["portao", "agente", "resultado", "impressao", "em", "volta", "achados", "S0", "S1", "S2",
                           "relatorio", "nota", "decisao_carlos", "veredictos", "slugs"],
    "docs/contratos.md": ["publicar_em", "plataformas", "estado", "confirmar", "trial", "graduation_strategy",
                          "material", "palavra", "historico", "atualizado"],
}


def casos_contrato() -> None:
    print("\n== contrato: cada chave que o sincronizador lê ainda é escrita pelo produtor ==")
    for fonte, chaves in CONTRATO.items():
        src = (CODIGO / fonte).read_text(encoding="utf-8")
        faltam = [k for k in chaves if f'"{k}"' not in src]
        ok(f"{fonte}: {len(chaves)} chaves", not faltam, f"sumiram: {faltam}")
    src = (CODIGO / "scripts" / "perfil.py").read_text(encoding="utf-8")
    ok("scripts/perfil.py: reach_por_follow_type (montada como reach_por_<quebra>)",
       'f"reach_por_{' in src and '"follow_type"' in src)
    # campos da conta e da página vêm da API Graph com o nome que o perfil.py pede na lista de campos
    campos = re.findall(r'(?:IG_CAMPOS_CONTA|FB_CAMPOS_PAGINA) = \(?"([^"]+)"', src)
    pedidos = {c for lista in campos for c in lista.split(",")}
    faltam = [c for c in ("followers_count", "follows_count", "media_count") if c not in pedidos]
    ok("scripts/perfil.py pede à API followers_count, follows_count e media_count", campos and not faltam,
       f"campos {campos} · faltam {faltam}")


# Totais dos registros sintéticos (montar_registros), contados à mão. Modelo com preço, todos os dias:
TOKENS_TUDO = 15820 + 3500 + 3 * 4 * M + 100 + 1100 + 30 + 2100 + 530 + 4 * M   # + sess-e (claude-opus-5, 16/09)
USD_TUDO = Decimal("148.80768") + Decimal("46.75")      # cache gravado pelo TTL (5 min 1,25 ×, 1 h 2 ×)
USD_125_TUDO = Decimal("136.80678") + Decimal("43")     # todo cache gravado a 1,25 × (a 1.ª versão do tokens-custos.py)
JANELA = (dt.date(2026, 9, 24), dt.date(2026, 10, 23))  # a do script: 30 dias até 23/10
# fora da janela: m-a3 (20/09), m-a4 (24/10) e a sess-e (16/09)
TOKENS_JANELA, USD_JANELA = TOKENS_TUDO - 5000 - 7000 - 4 * M, USD_TUDO - Decimal("0.048") - Decimal("46.75")


def casos_registros_sem_banco() -> None:
    print("\n== registros do Claude Code: --seco (tokens, custo pelo TTL e com o cache todo a 1,25 ×) ==")
    antes_home = foto(HOME)
    rc, out, err = sincronizar("--seco", db=PORTA_MORTA)
    linha = out[-1] if out else ""
    igual("tokens = entrada + cache gravado (5 min + 1 h) + saída, modelo com preço, todos os dias",
          campo(linha, "tokens"), str(TOKENS_TUDO))
    igual("US$ pelo TTL e US$ com todo cache gravado a 1,25 ×, das mesmas colunas",
          (campo(linha, "usd"), campo(linha, "usd_cache_1.25x")), (str(round(USD_TUDO, 2)), str(round(USD_125_TUDO, 2))))
    igual("modelo sem preço: guardado e contado à parte (respostas por modelo)", campo(linha, "sem_preco"),
          f"<synthetic>:1,{SEM_PRECO}:2")
    igual("cache sem detalhe de TTL (tratado como 5 min) e detalhe que não fecha com o total: contados",
          (campo(linha, "cache_sem_ttl"), campo(linha, "cache_ttl_divergente")), ("1", "1"))
    ok("linha cortada e linha que não é JSON não são erro (exit 0, sem stderr)", rc == 0 and not err, err[-300:])

    print("\n== --ate: o corte é inclusivo e só conta respostas até o instante ==")
    rc, out, _ = sincronizar("--seco", "--ate", "2026-10-05T12:00:00Z", db=PORTA_MORTA)
    igual("--ate no instante exato da resposta m-c1 (Sonnet 4 M) a inclui",
          campo(out[-1], "tokens") if out else None, str(3500 + 5000 + 300 + 3500 + 4 * M + 4 * M))
    rc, out, _ = sincronizar("--seco", "--ate", "2026-10-05T11:59:59.999Z", db=PORTA_MORTA)
    igual("um milissegundo antes, não", campo(out[-1], "tokens") if out else None,
          str(3500 + 5000 + 300 + 3500 + 4 * M))
    rc, out, err = sincronizar("--ate", "ontem", "--seco", db=PORTA_MORTA)
    ok("--ate inválido: exit 2 do argparse, sem traceback", rc == 2 and "Traceback" not in err, f"rc={rc} {err[-200:]}")
    # banco do Carlos com senha errada: se a guarda falhasse, a conexão seria recusada — nada pode ser gravado lá
    rc, out, err = sincronizar("--ate", "2026-10-05T12:00:00Z",
                               db="postgresql://postgres:senha-errada@127.0.0.1:55322/postgres")
    ok("--ate sem --seco no banco do painel (127.0.0.1:55322/postgres): recusado antes de conectar, exit 2",
       rc == 2 and len(out) == 1 and "✗" in out[0] and "--ate" in out[0] and "fora do ar" not in out[0], f"rc={rc} {out}")

    print("\n== pasta dos registros ==")
    rc, out, err = sincronizar("--seco", db=PORTA_MORTA, registros=HOME / "nao-existe")
    ok("pasta inexistente: exit 0, uma linha ⚠ e o resumo, sem ✗",
       rc == 0 and len(out) == 2 and "⚠" in out[0] and "registros" in out[0] and not any("✗" in x for x in out),
       f"rc={rc} {out} {err[-200:]}")
    igual("pasta inexistente: 0 execuções lidas", contagens(out[-1]).get("execucoes") if out else None, 0)
    home2 = Path(tempfile.mkdtemp(prefix="korvu-painel-home2-")).resolve()
    padrao = home2 / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))
    padrao.mkdir(parents=True)
    shutil.copy(REG / "sess-c.jsonl", padrao / "sess-c.jsonl")
    rc, out, _ = sincronizar("--seco", db=PORTA_MORTA, registros=None, home=home2)
    igual("sem PAINEL_REGISTROS: ~/.claude/projects/<raiz com / e espaço → -> (1 execução lá)",
          (contagens(out[-1]).get("execucoes") if out else None, campo(out[-1], "tokens") if out else None), (1, "2100"))
    shutil.rmtree(home2, ignore_errors=True)
    ok("nada escrito na HOME temporária nem na pasta dos registros", foto(HOME) == antes_home)

    print("\n== câmbio: painel/cambio.yaml inválido = ✗ e exit 1; ausente = vazio com ⚠ (PD28) ==")
    raiz = Path(tempfile.mkdtemp(prefix="korvu-painel-cambio-")) / "raiz"
    shutil.copytree(ROOT, raiz)
    (raiz / "painel" / "cambio.yaml").unlink()
    rc, out, err = sincronizar("--seco", db=PORTA_MORTA, projeto=raiz)
    ok("câmbio ausente: exit 0, um ⚠ que cita painel/cambio.yaml e a tabela cambio vazia (o painel não congela)",
       rc == 0 and any("⚠" in ln and "painel/cambio.yaml não encontrado" in ln for ln in out)
       and contagens(out[-1]).get("cambio") == 0 and not err, f"rc={rc} {out} {err[-200:]}")
    shutil.rmtree(raiz.parent, ignore_errors=True)
    for nome, conteudo in (("valor com vírgula", CAMBIO_YAML.replace("valor: 0.7465", 'valor: "0,7465"')),
                           ("valor negativo", CAMBIO_YAML.replace("valor: 0.7465", "valor: -0.7465")),
                           ("valor zero", CAMBIO_YAML.replace("valor: 0.7465", "valor: 0")),
                           ("valor texto", CAMBIO_YAML.replace("valor: 0.7465", "valor: libra")),
                           ("mais de 6 casas", CAMBIO_YAML.replace("valor: 0.7465", "valor: 0.74650001")),
                           ("data repetida", CAMBIO_YAML.replace('data: "2026-10-23"\n    moeda: EUR',
                                                                 'data: "2026-10-23"\n    moeda: GBP')),
                           ("data inválida", CAMBIO_YAML.replace("data: 2026-10-01", "data: 2026-13-01")),
                           ("moeda USD", CAMBIO_YAML.replace("moeda: EUR", "moeda: USD")),
                           ("sem fonte", CAMBIO_YAML.replace("fonte: teste euro", 'fonte: " "')),
                           ("sem taxas", "taxas: []\n")):
        raiz = Path(tempfile.mkdtemp(prefix="korvu-painel-cambio-")) / "raiz"
        shutil.copytree(ROOT, raiz)
        (raiz / "painel" / "cambio.yaml").write_text(conteudo, encoding="utf-8")
        rc, out, err = sincronizar("--seco", db=PORTA_MORTA, projeto=raiz)
        ok(f"câmbio {nome}: exit 1, uma linha ✗ que cita painel/cambio.yaml",
           rc == 1 and len(out) == 1 and "✗" in out[0] and "painel/cambio.yaml" in out[0] and not err,
           f"rc={rc} {out} {err[-200:]}")
        shutil.rmtree(raiz.parent, ignore_errors=True)


def casos_nao_publicar_sem_banco() -> None:
    print("\n== trava 'não publicar': _controle/nao-publicar.json opcional; inválido = ✗ ==")
    for nome, conteudo, esperado in (
            ("ausente (o projeto real hoje)", None, 0),
            ("lista vazia", {"travas": []}, 0),
            ("desde inválido", {"travas": [{"slug": "a-b", "motivo": "x", "desde": "19/09/2026"}]}, None),
            ("sem motivo", {"travas": [{"slug": "a-b", "motivo": " ", "desde": "2026-09-19"}]}, None),
            ("slug repetido", {"travas": [{"slug": "a-b", "motivo": "x", "desde": "2026-09-19"},
                                          {"slug": "a-b", "motivo": "y", "desde": "2026-09-20"}]}, None),
            ("JSON quebrado", '{"travas": [', None)):
        raiz = Path(tempfile.mkdtemp(prefix="korvu-painel-trava-")) / "raiz"
        shutil.copytree(ROOT, raiz)
        arq = raiz / "_controle" / "nao-publicar.json"
        if conteudo is None:
            arq.unlink()
        else:
            arq.write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo), encoding="utf-8")
        rc, out, err = sincronizar("--seco", db=PORTA_MORTA, projeto=raiz)
        if esperado is None:
            ok(f"trava {nome}: exit 1, uma linha ✗ que cita _controle/nao-publicar.json",
               rc == 1 and len(out) == 1 and "✗" in out[0] and "_controle/nao-publicar.json" in out[0] and not err,
               f"rc={rc} {out} {err[-200:]}")
        else:
            igual(f"trava {nome}: exit 0, nao_publicar {esperado}",
                  (rc, contagens(out[-1]).get("nao_publicar") if out else None), (0, esperado))
        shutil.rmtree(raiz.parent, ignore_errors=True)


def casos_propriedade_ultima_linha() -> None:
    """Propriedade da regra da última linha, com respostas geradas ao acaso (semente fixa): várias linhas por resposta,
    cada campo do usage nunca diminui de uma linha para a seguinte (o que se observa nos registros reais: só a saída
    cresce). O sincronizador tem de somar a ÚLTIMA linha de cada uma; a regra do script, a 1.ª; e a diferença é a das
    linhas provisórias."""
    print("\n== propriedade: vale a última linha de cada resposta (respostas ao acaso, semente 23) ==")
    pasta = Path(tempfile.mkdtemp(prefix="korvu-painel-prop-")).resolve()
    rnd = random.Random(23)
    ultima_tk, primeira_tk, ultima_usd, primeira_usd, afetadas = 0, 0, Decimal(0), Decimal(0), 0
    for n in range(6):
        linhas_ = []
        for i in range(40):
            modelo = rnd.choice([OPUS, SONNET, FABLE, OPUS5])
            e, c5, c1, cl = (rnd.randint(0, 5000) for _ in range(4))
            s0 = rnd.randint(1, 3)
            dia = dt.date(2026, 9, 24) + dt.timedelta(days=rnd.randint(0, 29))
            k = rnd.randint(1, 4)  # linhas desta resposta
            saidas = sorted([s0] + [rnd.randint(s0, 2000) for _ in range(k - 1)])
            us = []
            for j, s_ in enumerate(saidas):
                us.append(resp(f"p{n}-{i}", f"{dia.isoformat()}T12:00:{j:02d}.000Z", modelo=modelo, e=e, c5=c5, c1=c1,
                               cl=cl, s=s_, provisorio=j < k - 1))
            linhas_ += us
            a, b = us[0]["message"]["usage"], us[-1]["message"]["usage"]
            primeira_tk += a["input_tokens"] + a["cache_creation_input_tokens"] + a["output_tokens"]
            ultima_tk += b["input_tokens"] + b["cache_creation_input_tokens"] + b["output_tokens"]
            primeira_usd += custo_teste(modelo, a)
            ultima_usd += custo_teste(modelo, b)
            afetadas += a["output_tokens"] != b["output_tokens"]
        rnd.shuffle(linhas_)  # respostas intercaladas no arquivo, como blocos de várias respostas…
        linhas_.sort(key=lambda o: o["timestamp"])  # …mas cada uma na ordem em que foi escrita (sort estável por hora)
        escrever(f"s{n}.jsonl", "".join(json.dumps(x) + "\n" for x in linhas_), raiz=pasta)
    rc, out, err = sincronizar("--seco", db=PORTA_MORTA, registros=pasta)
    linha = out[-1] if out else ""
    igual("a regra do painel soma a ÚLTIMA linha: tokens e US$ (à mão, com o preço escrito à parte)",
          (campo(linha, "tokens"), campo(linha, "usd")), (str(ultima_tk), str(round(ultima_usd, 2))))
    igual("respostas com usage provisório contadas", campo(linha, "usage_provisorio"), str(afetadas))
    rc, out, err = sincronizar("--seco", "--regra-do-script", db=PORTA_MORTA, registros=pasta)
    igual("--regra-do-script soma a 1.ª linha", campo(out[-1], "tokens") if out else None, str(primeira_tk))
    ok("e a última nunca é menor que a 1.ª (propriedade observada nos registros reais)",
       ultima_tk >= primeira_tk and ultima_usd >= primeira_usd and afetadas > 0)
    shutil.rmtree(pasta, ignore_errors=True)


def casos_bytecode() -> None:
    print("\n== a passagem como o launchd roda (sem PYTHONDONTWRITEBYTECODE) não grava bytecode no projeto (PD11) ==")
    for trava in (True, False):
        arvore = Path(tempfile.mkdtemp(prefix="korvu-painel-codigo-")).resolve()  # cópia da árvore de código
        (arvore / "painel" / "sync").mkdir(parents=True)
        (arvore / "scripts").mkdir()
        fonte = SYNC.read_text(encoding="utf-8")
        if not trava:  # controle: sem a linha da trava, o teste tem de ver o .pyc nascer
            fonte = fonte.replace("sys.dont_write_bytecode = True\n", "", 1)
        (arvore / "painel" / "sync" / "sincronizar.py").write_text(fonte, encoding="utf-8")
        shutil.copy(SYNC.parent / "previas_looks.py", arvore / "painel" / "sync" / "previas_looks.py")
        shutil.copy(CODIGO / "scripts" / "portoes.py", arvore / "scripts" / "portoes.py")
        env = {k: v for k, v in os.environ.items()
               if k not in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX", "PAINEL_DB_URL", "PAINEL_PROJETO",
                            "CONTENT_AI_ROOT", "PAINEL_REGISTROS")}
        env.update({"PAINEL_DB_URL": PORTA_MORTA, "PAINEL_PROJETO": str(ROOT), "PAINEL_REGISTROS": str(REG),
                    "HOME": str(HOME), "PYTHONIOENCODING": "utf-8"})
        r = subprocess.run([sys.executable, str(arvore / "painel" / "sync" / "sincronizar.py"), "--seco"], env=env,
                           cwd=str(OUTRA), capture_output=True, text=True, encoding="utf-8", timeout=120)
        pycs = sorted(x.relative_to(arvore).as_posix() for x in arvore.rglob("*.pyc"))
        if trava:
            ok("com sys.dont_write_bytecode antes do import: exit 0 e nenhum .pyc na árvore do código",
               r.returncode == 0 and not pycs, f"rc={r.returncode} {pycs} {r.stderr[-200:]}")
        else:
            ok("controle: sem a trava, o import grava scripts/__pycache__/portoes.*.pyc e painel/sync/__pycache__/"
               "previas_looks.*.pyc (o teste enxerga o defeito)",
               any(x.startswith("scripts/__pycache__/portoes") for x in pycs)
               and any(x.startswith("painel/sync/__pycache__/previas_looks") for x in pycs), pycs)
        shutil.rmtree(arvore, ignore_errors=True)


def casos_guarda_do_corte() -> None:
    print("\n== --ate e --regra-do-script não gravam no banco do painel, por nenhum endereço deste Mac (PD18) ==")
    # senha errada de propósito: se a guarda falhasse, a conexão seria recusada — nada pode ser gravado no banco real
    for url in ("postgresql://postgres:senha-errada@0.0.0.0:55322/postgres",
                "postgresql://postgres:senha-errada@localhost.:55322/postgres",
                "postgresql://postgres:senha-errada@[::1]:55322/postgres",
                "host=127.0.0.2 port=55322 user=postgres password=senha-errada dbname=postgres",
                "host=/tmp port=55322 user=postgres password=senha-errada dbname=postgres",           # socket
                # hostaddr: o libpq conecta no hostaddr (127.0.0.1); o host só dá o nome — a guarda tem de olhar o hostaddr
                "host=painel.exemplo hostaddr=127.0.0.1 port=55322 user=postgres password=senha-errada dbname=postgres",
                "postgresql://postgres:senha-errada@[127.0.0.1:55322/postgres",                       # URL ilegível
                "postgresql://postgres:senha-errada@127.0.0.1:55322/postgres"):
        for flag in (["--ate", "2026-10-05T12:00:00Z"], ["--regra-do-script"]):
            rc, out, err = sincronizar(*flag, db=url)
            ok(f"{flag[0]} → {url.split('@')[-1] if '@' in url else url.split()[0]}: recusado antes de conectar (exit 2)",
               rc == 2 and len(out) == 1 and "✗" in out[0] and "--ate/--regra-do-script" in out[0]
               and "fora do ar" not in out[0], f"rc={rc} {out}")
    print("\n== --regra-do-script com --ate: o corte vale pela 1.ª linha de cada resposta, como no script (PD22) ==")
    tk = {}
    for script in (False, True):
        for ate in ("2026-10-05T11:59:59.999Z", "2026-10-05T12:00:00Z"):
            rc, out, _ = sincronizar("--seco", *(["--regra-do-script"] if script else []), "--ate", ate, db=PORTA_MORTA)
            tk[(script, ate)] = int(campo(out[-1], "tokens") or 0) if out else 0
    antes, no_instante = "2026-10-05T11:59:59.999Z", "2026-10-05T12:00:00Z"
    igual("o corte inclui a resposta m-c1 (Sonnet, 4 M) só a partir de 12:00:00, nas duas regras",
          (tk[(True, no_instante)] - tk[(True, antes)], tk[(False, no_instante)] - tk[(False, antes)]), (4 * M, 4 * M))
    igual("no mesmo corte, a regra do painel tem a mais só o que a 1.ª linha provisória escondia (m-a1: 500 − 3)",
          tk[(False, no_instante)] - tk[(True, no_instante)], 497)
    rc, out, _ = sincronizar("--ate", "2026-10-05T12:00:00Z", db=PORTA_MORTA)
    ok("outro banco (porta 59999) não é recusado pela guarda: tenta conectar e cai no 'fora do ar'",
       rc == 1 and out and "fora do ar" in out[-1], f"rc={rc} {out}")


def casos_contrato_referencia() -> None:
    print("\n== contrato com o tokens-custos.py de referência e o equipe.yaml real ==")
    ok("o script de referência existe (a reconciliação depende dele)", REFERENCIA.exists(), str(REFERENCIA))
    if not REFERENCIA.exists():
        return
    arvore = ast.parse(REFERENCIA.read_text(encoding="utf-8"))
    lit = {n.targets[0].id: ast.literal_eval(n.value) for n in arvore.body
           if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("PRECO", "DEPTO")}
    # o PRECOS do sincronizador, lido do código-fonte (importar o módulo conectaria o portoes.py à raiz real)
    fonte = SYNC.read_text(encoding="utf-8")
    bloco = re.search(r"^PRECOS = \{(.*?)^\}", fonte, re.S | re.M).group(1)
    nossos = {m: tuple(Decimal(x) for x in v) for m, _, *v in re.findall(
        r'"([^"]+)": \("([^"]+)", "([\d.]+)", "([\d.]+)", "([\d.]+)", "([\d.]+)", "([\d.]+)"\)', bloco)}
    ok("nenhum modelo do script sem preço aqui; a mais aqui, no máximo o claude-opus-5",
       set(lit.get("PRECO", {})) <= set(nossos) and set(nossos) - set(lit.get("PRECO", {})) <= {OPUS5},
       (sorted(nossos), sorted(lit.get("PRECO", {}))))
    igual("claude-opus-5: 5 / 6,25 / 10 / 0,50 / 25 (documentação da API; cache lido 0,1 × a entrada)",
          nossos.get(OPUS5), tuple(Decimal(x) for x in ("5", "6.25", "10", "0.50", "25")))
    for m, t in lit.get("PRECO", {}).items():
        e, c5, cl, s = t if len(t) == 4 else (t[0], Decimal(str(t[0])) * Decimal("1.25"), t[1], t[2])
        n = nossos.get(m, (None,) * 5)
        igual(f"{m}: entrada, cache 5 min, cache lido e saída = os do script",
              (n[0], n[1], n[3], n[4]), tuple(Decimal(str(x)) for x in (e, c5, cl, s)))
    for m, n in nossos.items():
        igual(f"{m}: cache 5 min = 1,25 × entrada · cache 1 h = 2 × entrada (documentação de prompt caching)",
              (n[1], n[2]), (n[0] * Decimal("1.25"), n[0] * 2))
    import yaml
    real = yaml.safe_load((CODIGO / "painel" / "equipe.yaml").read_text(encoding="utf-8"))
    dep = {a["id"]: a["departamento"] for a in real["agentes"]}
    ajudantes = {"principal", "general-purpose", "workflow-subagent", "claude", "Explore", "Plan"}
    diverge = {a: (d, dep.get(a, "direcao")) for a, d in lit.get("DEPTO", {}).items()
               if a not in ajudantes and dep.get(a, "direcao") != d}
    ok("o departamento de cada agente do script = o do painel/equipe.yaml (a soma por departamento bate)", not diverge,
       diverge)
    ok("os ajudantes do script contam como direção", all(lit.get("DEPTO", {}).get(a) == "direcao" for a in ajudantes))


def rodar_referencia() -> tuple[dict, str]:
    """O próprio tokens-custos.py sobre os registros sintéticos (HOME temporária) → os números que ele imprime."""
    env = {**os.environ, "HOME": str(HOME), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(REFERENCIA)], env=env, cwd=str(OUTRA), capture_output=True, text=True,
                       encoding="utf-8", timeout=120)
    # dois formatos: o de 23/10 16:41 ("TOTAL tokens N US$ X", "  chave tokens US$ … tarefas N") e o de 23/10 21:32
    # ("TOTAL N tokens · US$ X · £ …", "  chave tokens … US$ X …", "… execucoes N", VIDEO só com "US$ X")
    def usd(ln, p):
        m = re.search(r"US\$ ([\d.]+)", ln)
        return Decimal(m.group(1)) if m else Decimal(p[2])
    out, sec = {"total": None, "modelo": {}, "depto": {}, "agente": {}, "video": {}, "dia": {}}, None
    for ln in r.stdout.splitlines():
        p = ln.split()
        if ln.startswith("TOTAL"):
            out["total"] = (int(re.search(r"\d+", ln).group(0)), usd(ln, p))
        elif ln.strip() in ("MODELO", "DEPTO", "AGENTE", "VIDEO", "DIA"):
            sec = ln.strip().lower()
        elif sec == "video":
            out[sec][p[0]] = usd(ln, p)
        elif sec in ("modelo", "depto", "dia"):
            out[sec][p[0]] = (int(p[1]), usd(ln, p))
        elif sec == "agente":
            out[sec][p[0]] = (int(p[1]), usd(ln, p), int(re.search(r"(?:tarefas|execucoes) (\d+)", ln).group(1)))
    return out, (r.stderr or "")[-300:]


CONFERENCIA = """
select {chave} as k, sum(c.tokens)::bigint as tokens, sum(c.usd) as usd,
       sum((c.entrada * p.entrada + (c.cache_gravado_5m + c.cache_gravado_1h) * p.cache_gravado_5m
            + c.cache_lido * p.cache_lido + c.saida * p.saida) / 1000000) as usd_125,
       count(distinct c.arquivo)::int as tarefas
from consumo c join precos_modelo p on p.modelo = c.modelo
where c.dia between %s and %s group by 1"""
CHAVE_AGENTE = "case when c.tipo = 'principal' then 'principal' else coalesce(c.agente_tipo, 'subagente') end"


def conferencia(con, chave: str, janela=JANELA) -> dict:
    """A conta do banco por chave, na janela: tokens, US$ pelo TTL, US$ com todo cache gravado a 1,25 × (a 1.ª versão
    do script, das mesmas colunas) e tarefas (count distinct de execuções com resposta de modelo com preço)."""
    return {r["k"]: r for r in linhas(con, CONFERENCIA.format(chave=chave), janela)}


PRECO_TESTE = {OPUS: ("4", "5", "8", "0.20", "20"), SONNET: ("2", "2.5", "4", "0.20", "10"),
               FABLE: ("10", "12.5", "20", "0.25", "50"), OPUS5: ("5", "6.25", "10", "0.50", "25")}


def custo_teste(modelo: str, u: dict) -> Decimal:
    """O preço da tabela da API, escrito à parte do sincronizador (entrada, 5 min, 1 h, lido, saída por milhão)."""
    e, c5, c1, cl, s_ = (Decimal(x) for x in PRECO_TESTE[modelo])
    cc = u.get("cache_creation") or {}
    um_h = cc.get("ephemeral_1h_input_tokens") or 0
    return (u["input_tokens"] * e + (u["cache_creation_input_tokens"] - um_h) * c5 + um_h * c1
            + u["cache_read_input_tokens"] * cl + u["output_tokens"] * s_) / 1_000_000


def provisorias(janela, pasta: Path = REG) -> list[dict]:
    """Lido direto dos .jsonl (não do sincronizador): as respostas de modelo com preço, na janela, cuja 1.ª linha tem
    usage diferente da última — e quanto a última acrescenta."""
    out = []
    for f in sorted(pasta.rglob("*.jsonl")):
        if any(x.startswith(".") for x in f.relative_to(pasta).parts):
            continue
        por = {}
        for ln in f.read_text(encoding="utf-8").splitlines():
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            m = o.get("message") if isinstance(o, dict) else None
            if isinstance(m, dict) and isinstance(m.get("usage"), dict) and m["usage"]:
                por.setdefault(m.get("id") or o.get("uuid"), []).append(o)
        for ls in por.values():
            a, b = ls[0]["message"], ls[-1]["message"]
            dia = dt.date.fromisoformat(ls[0]["timestamp"][:10])
            if a["usage"] == b["usage"] or b.get("model") not in PRECO_TESTE or not janela[0] <= dia <= janela[1]:
                continue
            ua, ub = a["usage"], b["usage"]
            campos = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
            out.append({"arquivo": f.relative_to(pasta).as_posix(),
                        "tokens": sum(ub[k] - ua[k] for k in campos if k != "cache_read_input_tokens"),
                        "usd": custo_teste(b["model"], ub) - custo_teste(a["model"], ua),
                        "delta_saida": ub["output_tokens"] - ua["output_tokens"],
                        "so_saida": all(ua[k] == ub[k] for k in campos if k != "output_tokens")})
    return out


def perto(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) <= Decimal("0.005")  # o script imprime round(x, 2)


def casos_registros_banco() -> None:
    with psycopg.connect(BANCO_TESTE) as con:
        print("\n== registros → execucoes (uma linha por .jsonl com resposta) ==")
        ex = {r["arquivo"]: r for r in linhas(con, "select * from execucoes")}
        sub = "sess-a/subagents/"
        igual("os .jsonl com resposta (sem o oculto, sem o journal do workflow)", sorted(ex), sorted([
            "sess-a.jsonl", "sess-b.jsonl", "sess-c.jsonl", "sess-e.jsonl", "sess-d/subagents/agent-dup.jsonl",
            *[f"{sub}agent-a0{n}.jsonl" for n in (1, 2, 3, 4, 5, 7, 8, 9)],
            f"{sub}workflows/wf_teste-1/agent-a06.jsonl"]))
        a = ex.get("sess-a.jsonl", {})
        igual("principal: tipo, sessão, sem agente, Atlas/direção, sem vídeo; início/fim = 1.ª e última resposta",
              tuple(a.get(k) for k in ("tipo", "sessao", "agente_id", "agente_tipo", "membro_id", "departamento_id",
                                       "video_slug", "inicio", "fim", "registro_presente")),
              ("principal", "sess-a", None, None, "diretor", "direcao", None, ts("2026-09-20T12:00:00+00:00"),
               ts("2026-10-24T00:00:00+00:00"), True))
        b = ex.get(f"{sub}agent-a01.jsonl", {})
        igual("subagente: sessão-mãe, id, agentType cru, membro e departamento do equipe.yaml, meta, vídeo",
              tuple(b.get(k) for k in ("tipo", "sessao", "agente_id", "agente_tipo", "membro_id", "departamento_id",
                                       "descricao", "profundidade", "terminou", "video_slug")),
              ("subagente", "sess-a", "a01", "portao-dados", "portao-dados", "tecnologia", "auditoria v1", 1, True,
               None))
        igual("ajudantes (general-purpose, Explore, workflow-subagent, claude, Plan), agentType fora do yaml e sem meta "
              "→ Atlas (diretor, direcao), com o agentType cru guardado",
              {k: (ex.get(k, {}).get("agente_tipo"), ex.get(k, {}).get("membro_id"), ex.get(k, {}).get("departamento_id"))
               for k in (f"{sub}agent-a02.jsonl", f"{sub}agent-a03.jsonl", f"{sub}workflows/wf_teste-1/agent-a06.jsonl",
                         f"{sub}agent-a07.jsonl", f"{sub}agent-a08.jsonl", f"{sub}agent-a09.jsonl",
                         f"{sub}agent-a05.jsonl")},
              {f"{sub}agent-a02.jsonl": ("general-purpose", "diretor", "direcao"),
               f"{sub}agent-a03.jsonl": ("Explore", "diretor", "direcao"),
               f"{sub}workflows/wf_teste-1/agent-a06.jsonl": ("workflow-subagent", "diretor", "direcao"),
               f"{sub}agent-a07.jsonl": ("claude", "diretor", "direcao"),
               f"{sub}agent-a08.jsonl": ("Plan", "diretor", "direcao"),
               f"{sub}agent-a09.jsonl": ("agente-novo-xyz", "diretor", "direcao"),
               f"{sub}agent-a05.jsonl": (None, "diretor", "direcao")})
        igual("engenheiro-backend → tecnologia", (ex.get(f"{sub}agent-a04.jsonl", {}).get("membro_id"),
                                                  ex.get(f"{sub}agent-a04.jsonl", {}).get("departamento_id")),
              ("engenheiro-backend", "tecnologia"))
        g = ex.get(f"{sub}workflows/wf_teste-1/agent-a06.jsonl", {})
        igual("workflow: id do wf, description cortada em 200, spawnDepth, finished ausente = NULL",
              (g.get("workflow"), len(g.get("descricao") or ""), g.get("profundidade"), g.get("terminou")),
              ("wf_teste-1", 200, 2, None))
        igual("vídeo: <pasta>/<slug> que existe → vídeo de origem (07-publicados/…-a → o vídeo; 06-publicar com selo "
              "→ gauntlet.origem; sem vídeo-prefixo → o próprio slug); o mais citado, empate = o primeiro; os 5 falsos "
              "do script, o slug sem pasta e a tecnologia (a01, a04) ficam sem vídeo; pedido em blocos também",
              {k.removeprefix(sub): ex.get(k, {}).get("video_slug") for k in sorted(ex) if k.startswith(sub)},
              {"agent-a01.jsonl": None, "agent-a02.jsonl": None,
               "agent-a03.jsonl": "2026-10-30-com-status", "agent-a04.jsonl": None,
               "agent-a05.jsonl": "2026-10-30-com-status", "agent-a07.jsonl": "2026-10-28-legado",
               "agent-a08.jsonl": "2026-11-01-fora-do-tracker", "agent-a09.jsonl": "2026-10-31-sem-status",
               "workflows/wf_teste-1/agent-a06.jsonl": None})

        print("\n== registros → uso_execucao (execução × dia UTC × modelo) ==")
        us = {(r["arquivo"], r["dia"].isoformat(), r["modelo"]): r for r in linhas(con, "select * from uso_execucao")}
        col = ("respostas", "entrada", "cache_gravado_5m", "cache_gravado_1h", "cache_gravado_sem_ttl", "cache_lido",
               "saida", "tokens")
        v = lambda k: tuple(us.get(k, {}).get(c) for c in col)  # noqa: E731
        igual("dedup: a mesma resposta em 3 linhas (formato real: saída 3 / 3 / 500) conta 1 vez, com o usage da ÚLTIMA",
              v(("sess-a.jsonl", "2026-10-01", OPUS)), (1, 1000, 2000, 0, 0, 100000, 500, 3500))
        igual("a mesma message.id noutro arquivo conta de novo", v((f"{sub}agent-a01.jsonl", "2026-10-01", OPUS)),
              (1, 1000, 2000, 0, 0, 100000, 500, 3500))
        igual("sem message.id: deduplica pelo uuid (2 linhas iguais = 1 resposta)", v(("sess-a.jsonl", "2026-10-03", OPUS)),
              (1, 300, 0, 0, 0, 0, 0, 300))
        igual("dia = data UTC (23:30Z de 13/10 é 13/10, não o 14/10 de Londres)", v(("sess-a.jsonl", "2026-10-13", OPUS)),
              (1, 10, 0, 0, 0, 0, 10, 20))
        ok("linha cortada (m-cortada, 04/10) não entra", not any(k[1] == "2026-10-04" for k in us), sorted(us))
        igual("fora da janela do script (20/09 e 24/10): guardado", (v(("sess-a.jsonl", "2026-09-20", OPUS))[1],
                                                                    v(("sess-a.jsonl", "2026-10-24", OPUS))[1]),
              (5000, 7000))
        igual("modelo sem preço guardado (não se perde no arquivo)",
              (v(("sess-a.jsonl", "2026-10-02", SEM_PRECO))[1], v(("sess-b.jsonl", "2026-10-11", SEM_PRECO))[1],
               v(("sess-a.jsonl", "2026-10-02", "<synthetic>"))[0]), (777, 4000, 1))
        igual("cache por TTL: 5 min + 1 h; sem o detalhe = tudo 5 min, marcado em cache_gravado_sem_ttl",
              v((f"{sub}workflows/wf_teste-1/agent-a06.jsonl", "2026-10-09", OPUS)), (1, 50, 1000, 0, 1000, 0, 50, 1100))
        igual("detalhe que não fecha com o total (100 + 300 ≠ 500): 1 h pelo detalhe, 5 min o resto, total mantido",
              v(("sess-d/subagents/agent-dup.jsonl", "2026-10-13", OPUS)), (1, 10, 200, 300, 0, 0, 0, 510))

        print("\n== preços e custo (view consumo): os três modelos, cache lido do Fable a 0,25 ==")
        igual("precos_modelo = PRECOS (entrada, 5 min, 1 h, lido, saída)",
              {r["modelo"]: (r["nome"], r["entrada"], r["cache_gravado_5m"], r["cache_gravado_1h"], r["cache_lido"],
                             r["saida"]) for r in linhas(con, "select * from precos_modelo")},
              {OPUS: ("Opus 5.5", Decimal(4), Decimal(5), Decimal(8), Decimal("0.2"), Decimal(20)),
               SONNET: ("Sonnet 5.5", Decimal(2), Decimal("2.5"), Decimal(4), Decimal("0.2"), Decimal(10)),
               FABLE: ("Fable 5.1", Decimal(10), Decimal("12.5"), Decimal(20), Decimal("0.25"), Decimal(50)),
               OPUS5: ("Opus 5", Decimal(5), Decimal("6.25"), Decimal(10), Decimal("0.5"), Decimal(25))})
        cu = {r["arquivo"].removeprefix(sub): r["usd"] for r in linhas(
            con, "select arquivo, sum(usd) as usd from consumo group by arquivo")}
        igual("1 M de cada (entrada, 5 min, 1 h, lido, saída): Sonnet 18,70 · Fable 92,75 · Opus 5.5 37,20 · Opus 5 46,75",
              (cu.get("agent-a02.jsonl"), cu.get("agent-a03.jsonl"), cu.get("agent-a04.jsonl"), cu.get("sess-e.jsonl")),
              (Decimal("18.7"), Decimal("92.75"), Decimal("37.2"), Decimal("46.75")))
        # diferença de propósito com o script: detalhe do TTL que não fecha (100 + 300 de 500) → o banco cobra o resto
        # (100) a 5 min; o script só cobra o detalhe (0,00294). Nos registros reais de 23/10: 0 casos.
        igual("detalhe que não fecha: o banco cobra os 500 tokens (10×4 + 200×5 + 300×8 + 20×4 = US$ 0,00352)",
              linhas(con, "select sum(usd) as u from consumo where arquivo = 'sess-d/subagents/agent-dup.jsonl'")[0]["u"],
              Decimal("0.00352"))
        ok("consumo não tem modelo sem preço", not linhas(con, "select 1 from consumo where modelo in (%s, %s)",
                                                         (SEM_PRECO, "<synthetic>")))
        t = linhas(con, "select sum(tokens) as tk, sum(usd) as usd from consumo")[0]
        igual("total do banco (todos os dias) = a conta à mão", (t["tk"], t["usd"]), (TOKENS_TUDO, USD_TUDO))
        ec = {r["arquivo"]: r for r in linhas(con, "select * from execucoes_custo")}
        igual("execucoes_custo: sess-b só sem preço = não é tarefa; sess-a tem 2 respostas sem preço",
              ((ec.get("sess-b.jsonl", {}).get("tarefa"), ec.get("sess-b.jsonl", {}).get("respostas"),
                ec.get("sess-b.jsonl", {}).get("respostas_sem_preco")),
               (ec.get("sess-a.jsonl", {}).get("tarefa"), ec.get("sess-a.jsonl", {}).get("respostas_sem_preco"))),
              ((False, 0, 1), (True, 2)))
        igual("as duas visões fecham: Σ execucoes_custo = Σ consumo = Σ consumo_diario",
              (linhas(con, "select sum(tokens) as t, sum(usd) as u from execucoes_custo")[0]["u"],
               linhas(con, "select sum(usd) as u from consumo_diario")[0]["u"]), (USD_TUDO, USD_TUDO))
        dd = {(r["dia"].isoformat()): r["execucoes"] for r in linhas(
            con, "select dia, execucoes from consumo_diario where agente_tipo = 'portao-dados'")}
        igual("consumo_diario: execução que passa da meia-noite UTC aparece nos dois dias (1 por dia)",
              dd, {"2026-10-01": 1, "2026-10-13": 1, "2026-10-14": 1})

        print("\n== câmbio: painel/cambio.yaml → cambio ==")
        igual("uma linha por moeda × data, valor exato", sorted((r["moeda"], r["data"].isoformat(), r["valor"], r["fonte"])
                                                              for r in linhas(con, "select * from cambio")),
              [("EUR", "2026-10-23", Decimal("0.86125"), "teste euro"),
               ("GBP", "2026-10-01", Decimal("0.75"), "teste antigo"),
               ("GBP", "2026-10-23", Decimal("0.7465"), "XE, média de mercado")])

        print("\n== nada de texto de conversa no banco ==")
        tudo = " ".join(str(r) for t in ("execucoes", "uso_execucao", "consumo", "consumo_diario", "execucoes_custo")
                        for r in linhas(con, f"select * from {t}"))
        ok("nem o pedido nem a resposta", PEDIDO_SECRETO not in tudo and RESPOSTA_SECRETA not in tudo
           and "Audite" not in tudo)

        print("\n== reconciliação: o próprio tokens-custos.py sobre os mesmos registros (janela 24/09–23/10) ==")
        if not REFERENCIA.exists():
            ok("tokens-custos.py presente", False, str(REFERENCIA))
            return
        ref, err = rodar_referencia()
        ok("o script roda sobre a HOME temporária", ref["total"] is not None, err)
        if ref["total"] is None:
            return
        fonte_ref = REFERENCIA.read_text(encoding="utf-8")
        ttl = "ephemeral_1h_input_tokens" in fonte_ref
        ultima = "ultima[" in fonte_ref  # a versão de 23/10 21:32 já fica com a ÚLTIMA linha de cada resposta
        col = "usd" if ttl else "usd_125"
        regra = "pelo TTL" if ttl else "com o cache todo a 1,25 ×"
        print(f"     (o tokens-custos.py de hoje cobra o cache gravado {regra} e fica com a "
              f"{'ÚLTIMA' if ultima else '1.ª'} linha de cada resposta)")
        # (a) a regra do script (1.ª linha), num 2.º banco de teste
        rc, out, err = sincronizar("--regra-do-script", db=BANCO_SCRIPT)
        ok("(a) --regra-do-script num banco de teste: exit 0", rc == 0, f"rc={rc} {out} {err[-300:]}")
        # o script se compara com o banco que usa a regra dele: o do painel (última linha) ou o (a) (1.ª linha)
        with psycopg.connect(BANCO_TESTE if ultima else BANCO_SCRIPT) as cr_:
            qual = "banco do painel (última linha)" if ultima else "(a) regra do script (1.ª linha)"
            tot_r = linhas(cr_, CONFERENCIA.format(chave="'total'"), JANELA)[0]
            igual(f"{qual} = o script: total de tokens", tot_r["tokens"], ref["total"][0])
            ok(f"{qual} = o script: US$ {regra}", perto(tot_r[col], ref["total"][1]),
               f"banco {tot_r[col]} · script {ref['total'][1]}")
            for nome, chave, ref_k in (("modelo", "c.modelo", "modelo"), ("departamento", "c.departamento_id", "depto"),
                                       ("dia", "c.dia::text", "dia")):
                db = conferencia(cr_, chave)
                igual(f"{qual} = o script, por {nome}: as mesmas chaves e os mesmos tokens", {k: db[k]["tokens"] for k in db},
                      {k: v[0] for k, v in ref[ref_k].items()})
                ruins = {k: (db[k][col], ref[ref_k][k][1]) for k in db
                         if k in ref[ref_k] and not perto(db[k][col], ref[ref_k][k][1])}
                ok(f"{qual} = o script, por {nome}: US$ {regra}", not ruins, ruins)
            db = conferencia(cr_, CHAVE_AGENTE)
            igual(f"{qual} = o script, por agente: tokens e tarefas", {k: (db[k]["tokens"], db[k]["tarefas"]) for k in db},
                  {k: (v[0], v[2]) for k, v in ref["agente"].items()})
            ruins = {k: (db[k][col], ref["agente"][k][1]) for k in db
                     if k in ref["agente"] and not perto(db[k][col], ref["agente"][k][1])}
            ok(f"{qual} = o script, por agente: US$ {regra}", not ruins, ruins)
        with psycopg.connect(BANCO_SCRIPT) as cs_:
            tot_s = linhas(cs_, CONFERENCIA.format(chave="'total'"), JANELA)[0]
        # (b) o banco do painel (última linha) e (c) a diferença, explicada pelas linhas provisórias dos arquivos
        tot = linhas(con, CONFERENCIA.format(chave="'total'"), JANELA)[0]
        igual("(b) banco do painel (última linha), na janela, à mão: tokens e US$ pelo TTL", (tot["tokens"], tot["usd"]),
              (TOKENS_JANELA, USD_JANELA))
        prov = provisorias(JANELA)
        igual("(c) banco − script = Σ (última − 1.ª linha) das respostas provisórias, em tokens e US$; quantas respostas",
              (tot["tokens"] - tot_s["tokens"], tot["usd"] - tot_s["usd"], len(prov)),
              (sum(d["tokens"] for d in prov), sum(d["usd"] for d in prov), 1))
        ok("(c) só a saída muda entre a 1.ª e a última linha, e nunca diminui", prov
           and all(d["so_saida"] and d["delta_saida"] > 0 for d in prov), prov)
        extra = linhas(con, "select sum(c.cache_gravado_1h * (p.cache_gravado_1h - p.cache_gravado_5m)) / 1000000 as x "
                            "from consumo c join precos_modelo p on p.modelo = c.modelo "
                            "where c.dia between %s and %s", JANELA)[0]["x"]
        igual("US$ pelo TTL − US$ a 1,25 × = só o cache de 1 h a 2 × (e não 1,25 ×)", tot["usd"] - tot["usd_125"], extra)
        db = conferencia(con, CHAVE_AGENTE)
        igual("tarefas: 12 (sess-b só tem modelo sem preço; o oculto e o journal não contam)",
              sum(r["tarefas"] for r in db.values()), 12)
        sem_pasta = [k for k in ref["video"] if not any((ROOT / d / k).is_dir() for d in
                                                         ("videos", "05-render-pronto", "06-publicar", "07-publicados"))]
        ok("vídeo: o script dá custo a um slug sem pasta (ex.: 2026-10-23-v1, 2026-10-22-v1); o banco não (de propósito)",
           sem_pasta and not linhas(con, "select 1 from execucoes where video_slug = any(%s)", (sem_pasta,)),
           (sorted(ref["video"]), sem_pasta))
        igual("vídeo: o total não muda, só a atribuição",
              sorted(r["k"] for r in linhas(con, CONFERENCIA.format(chave="c.video_slug"), JANELA) if r["k"]),
              ["2026-10-28-legado", "2026-10-30-com-status", "2026-10-31-sem-status", "2026-11-01-fora-do-tracker"])


def casos_biblioteca() -> None:
    print("\n== biblioteca: videos/*/material/** e brutos/extras/** → arquivos, materiais lógicos e totais ==")
    v = "videos/2026-10-31-sem-status/"
    with psycopg.connect(BANCO_TESTE) as con:
        arq = {r["caminho"].removeprefix(v): r for r in linhas(con, "select * from biblioteca_arquivos")}
        igual("uma linha por arquivo (recursivo, também brutos/extras/_alternativas); fora .DS_Store, ._*, 0 byte, pasta "
              "oculta e videos/_teste-x", sorted(arq), sorted(BIBLIOTECA))
        igual("tamanho em bytes = o do arquivo", {k: r["bytes"] for k, r in arq.items()},
              {k: len(c) for k, c in BIBLIOTECA.items()})
        tipo = {".pdf": "documento", ".md": "documento", ".txt": "documento", ".png": "imagem", ".jpg": "imagem",
                ".json": "pesquisa", ".mp4": "video", ".mov": "video", ".vtt": "outros"}
        igual("extensão (minúscula, com ponto) e tipo pela extensão (.vtt = outros)",
              {k: (r["extensao"], r["tipo"]) for k, r in arq.items()},
              {k: (Path(k).suffix, tipo[Path(k).suffix]) for k in BIBLIOTECA})
        igual("área e vídeo", {(r["area"], r["video_slug"]) for r in arq.values()},
              {("material", "2026-10-31-sem-status"), ("brutos/extras", "2026-10-31-sem-status")})
        igual("cada arquivo aponta para o seu material (_fonte: o PDF do mesmo nome; sem par, o 1.º PDF)",
              {k: arq[k]["material_id"].split(":", 1)[1] for k in ("material/_fonte/guia-b-previa.png",
                                                                  "material/_fonte/guia-b-previa-p2.png",
                                                                  "material/_fonte/material.md", "material/fontes.json",
                                                                  "material/youtube/cortes/contato.jpg",
                                                                  "brutos/extras/_alternativas/E09.mp4")},
              {"material/_fonte/guia-b-previa.png": "pdf:guia-b.pdf", "material/_fonte/guia-b-previa-p2.png": "pdf:guia-b.pdf",
               "material/_fonte/material.md": "pdf:guia-a.pdf", "material/fontes.json": "dossie",
               "material/youtube/cortes/contato.jpg": "pasta:youtube", "brutos/extras/_alternativas/E09.mp4": "extras"})
        igual("material/obra/ marcado (cópia de estudo, nunca publicada)", sorted(k for k, r in arq.items() if r["obra_estudo"]),
              ["material/obra/filme.mp4", "material/obra/legenda.vtt"])
        igual("data = mtime; mais de 30 dias antes da data do slug = suspeita",
              (arq["material/fotos/velha.jpg"]["modificado_em"], [k for k, r in arq.items() if r["data_suspeita"]]),
              (dt.datetime.fromtimestamp(1_721_000_000, dt.timezone.utc), ["material/fotos/velha.jpg"]))
        res = {r["id"].split(":", 1)[1]: r for r in linhas(con, "select * from biblioteca_materiais_resumo")}
        mini = lambda x: v + x if x else None  # noqa: E731
        igual("materiais lógicos: grupo, nome, arquivos, bytes (no PDF só o .pdf), quem adicionou INFERIDO, miniatura, obra",
              {k: (r["grupo"], r["nome"], r["arquivos"], r["bytes"], r["quem_adicionou_inferido"], r["miniatura"],
                   r["obra_estudo"]) for k, r in res.items()},
              {"pdf:guia-a.pdf": ("pdf", "Guia a", 2, 6, "produtor-de-material", None, False),
               "pdf:guia-b.pdf": ("pdf", "Guia b", 3, 7, "produtor-de-material", mini("material/_fonte/guia-b-previa.png"),
                                  False),
               "dossie": ("dossie", "dossiê de pesquisa", 2, 17, "pesquisador-de-material", None, False),
               "soltos": ("soltos", "outros arquivos", 1, 4, None, None, False),
               "pasta:youtube": ("pasta", "trechos do YouTube", 2, 32, "buscador-de-videos",
                                 mini("material/youtube/cortes/contato.jpg"), False),
               "pasta:screnn record": ("pasta", "gravação de tela", 1, 30, "carlos", mini("material/screnn record/tela.mov"),
                                       False),
               "pasta:obra": ("pasta", "obra comentada", 2, 43, "curador-de-obra", mini("material/obra/filme.mp4"), True),
               "pasta:estranha": ("pasta", "estranha", 1, 6, None, None, False),
               "pasta:fotos": ("pasta", "fotos de pesquisa", 1, 13, "pesquisador-de-material", mini("material/fotos/velha.jpg"),
                               False),
               "extras": ("extras", "cenas extras", 3, 75, "produtor-de-extras", mini("brutos/extras/E01.png"), False)})
        igual("caminho do material: o PDF, a pasta ou brutos/extras",
              (res["pdf:guia-b.pdf"]["caminho"], res["pasta:youtube"]["caminho"], res["extras"]["caminho"],
               res["dossie"]["caminho"]),
              (v + "material/guia-b.pdf", v + "material/youtube", v + "brutos/extras", v + "material"))
        ok("data do material = a do arquivo mais novo dele; suspeita se algum arquivo é",
           all(r["modificado_em"] == max(a["modificado_em"] for a in arq.values() if a["material_id"] == r["id"])
               for r in res.values()) and res["pasta:fotos"]["data_suspeita"] and not res["extras"]["data_suspeita"])
        igual("contagem por tipo do material (o cartão: '1 imagem e 2 vídeos')",
              (res["extras"]["n_imagem"], res["extras"]["n_video"], res["pdf:guia-b.pdf"]["n_documento"],
               res["pdf:guia-b.pdf"]["n_imagem"]), (1, 2, 1, 2))
        igual("por tipo: os 6, também o áudio com zero",
              [(r["tipo"], r["arquivos"], r["bytes"]) for r in linhas(con, "select * from biblioteca_por_tipo order by ordem")],
              [("video", 5, 150), ("imagem", 5, 61), ("documento", 6, 36), ("pesquisa", 1, 9), ("audio", 0, 0),
               ("outros", 1, 3)])
        igual("por vídeo: material + cenas extras, e a gravação (brutos/principal/) ao lado; a _teste-x fora",
              {r["video_slug"]: (r["arquivos"], r["bytes"], r["principal_arquivos"], r["principal_bytes"],
                                 r["principal_hd_arquivos"], r["principal_hd_bytes"])
               for r in linhas(con, "select * from biblioteca_por_video")},
              {"2026-10-30-com-status": (0, 0, 3, 157, 0, 0), "2026-10-31-sem-status": (18, 259, 0, 0, 0, 0),
               "2026-11-01-fora-do-tracker": (0, 0, 1, 9, 0, 0), "2026-11-04-sem-roteiro": (0, 0, 0, 0, 0, 0)})
        igual("referências: arquivos não ocultos por pasta (fora do 'Todos')",
              [(r["pasta"], r["arquivos"], r["bytes"]) for r in linhas(con, "select * from biblioteca_referencias order by 1")],
              [("00-marca/referencias", 1, 3), ("painel/referencias", 1, 4)])
        igual("mais utilizados, pela regra do pipeline: roteiros = 2 dos 4 vídeos, os com roteiro.json (a mesma "
              "definição da Produção, PD25: a fora-do-tracker só tem roteiro.md; a sem-roteiro não tem nada), vídeos "
              "gravados, PDFs da palavra; arquivo_existe pelo disco (os .cube estão na raiz de exemplo desde a "
              "Biblioteca nova, o molde do PDF não)",
              {r["arquivo"]: (r["usos"], r["unidade"], r["arquivo_existe"])
               for r in linhas(con, "select * from biblioteca_mais_utilizados")},
              {"00-marca/voz-carlos.md": (2, "roteiros", True),
               "00-marca/cor/luts/korvu-look-v5.cube": (2, "vídeos gravados", True),
               "00-marca/cor/luts/entrada-camera.cube": (2, "vídeos gravados", True),
               "scripts/gerar_material_pdf.py": (2, "PDFs da palavra", False)})


def casos_producao() -> None:
    print("\n== Produção (Roteiros, Prontos), nome curto, calendário e desempenho ==")
    with psycopg.connect(BANCO_TESTE) as con:
        vd = {r["slug"]: r for r in linhas(con, "select * from videos")}
        col = ("tem_roteiro", "roteiro_versao", "cta_palavra", "roteiro_extras", "gravacao_prevista", "nome_curto")
        igual("videos: roteiro.json (versao, cta_palavra, len(extras)) só onde existe — a fora-do-tracker tem roteiro.md "
              "e não tem roteiro.json —, a data do slug e o nome curto (tema antes do ' — '; sem tema, o slug)",
              {k: tuple(r[c] for c in col) for k, r in vd.items()},
              {"2026-10-30-com-status": (True, 3, "PROMPT", 2, dt.date(2026, 10, 30), "Contexto antes de pedir"),
               # cta_palavra "  " no roteiro.json = NULL (PD27)
               "2026-10-31-sem-status": (True, 1, None, 0, dt.date(2026, 10, 31), "Quem é Ana—Lu - a pesquisadora"),
               "2026-11-01-fora-do-tracker": (False, None, None, None, dt.date(2026, 11, 1), "fora do tracker"),
               "2026-11-04-sem-roteiro": (False, None, None, None, dt.date(2026, 11, 4), "sem roteiro")})
        igual("videos_producao: cenas extras em brutos/extras/ (da Biblioteca) e PDF pronto (material/*.pdf, o 1.º)",
              {r["slug"]: (r["roteiro_extras"], r["extras_arquivos"], r["pdf"], r["pdf_caminho"])
               for r in linhas(con, "select * from videos_producao")},
              {"2026-10-30-com-status": (2, 0, False, None),
               "2026-10-31-sem-status": (0, 3, True, "videos/2026-10-31-sem-status/material/guia-a.pdf"),
               "2026-11-01-fora-do-tracker": (None, 0, False, None), "2026-11-04-sem-roteiro": (None, 0, False, None)})
        igual("prontos: 05-render-pronto/*/pacote.json (qa, duracao, criado_em, cta_palavra; ausente = NULL) e o vídeo",
              {r["slug"]: (r["video_slug"], r["qa"], r["duracao"], r["criado_em"], r["cta_palavra"])
               for r in linhas(con, "select * from prontos")},
              {"2026-10-30-com-status": ("2026-10-30-com-status", "PASS", Decimal("58.7"),
                                         ts("2026-10-30T18:00:00+01:00"), "PROMPT"),
               "2026-10-31-sem-status": ("2026-10-31-sem-status", "FAIL", Decimal(12), None, None),  # "" = NULL
               "2026-11-01-fora-do-tracker-v2": ("2026-11-01-fora-do-tracker", "pass", None,
                                                 ts("2026-11-01T10:00:00+00:00"), "X")})
        igual("calendário: vagas_semanais (fuso do bloco, dia com acento e '-feira', lista, hora sem aspas)",
              sorted((r["dia_semana"], r["dia"], r["hora"].strftime("%H:%M"), r["fuso"])
                     for r in linhas(con, "select * from calendario_vagas")),
              [(2, "terca", "08:30", "Europe/Lisbon"), (2, "terca", "21:00", "Europe/Lisbon"),
               (3, "quarta", "21:00", "Europe/Lisbon"), (5, "sexta", "07:05", "Europe/Lisbon"),
               (7, "domingo", "19:00", "Europe/Lisbon")])
        igual("perfil_snapshots.toques_links_perfil = metricas_conta.profile_links_taps (sem o campo = NULL)",
              {r["lido_em"]: r["toques_links_perfil"] for r in linhas(con, "select * from perfil_snapshots")},
              {ts(PERFIL_LIDO): 7, ts("2026-10-16T10:00:00+01:00"): None})
        igual("perfil_diario: um arquivo por dia → dia × métrica (null fica fora)",
              sorted((r["dia"].isoformat(), r["metrica"], r["valor"], r["lido_em"])
                     for r in linhas(con, "select * from perfil_diario")),
              [("2026-10-23", "reach", 41, ts("2026-10-24T09:30:00+01:00")),
               ("2026-10-23", "views", 230, ts("2026-10-24T09:30:00+01:00")),
               ("2026-10-24", "reach", 50, ts("2026-10-25T09:30:00+00:00")),
               ("2026-10-24", "seguidores", 3640, ts("2026-10-25T09:30:00+00:00"))])


def casos_producao_sem_banco() -> None:
    def variante(rel: str, conteudo, nome: str, cita: str, esperado: int | None, chave: str | None = None) -> None:
        raiz = Path(tempfile.mkdtemp(prefix="korvu-painel-var-")) / "raiz"
        shutil.copytree(ROOT, raiz)
        alvo = raiz / rel
        if conteudo is None:
            shutil.rmtree(alvo) if alvo.is_dir() else alvo.unlink()
        else:
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo), encoding="utf-8")
        rc, out, err = sincronizar("--seco", db=PORTA_MORTA, projeto=raiz)
        if esperado is None:
            ok(f"{nome}: exit 1, uma linha ✗ que cita {cita}",
               rc == 1 and len(out) == 1 and "✗" in out[0] and cita in out[0] and not err, f"rc={rc} {out} {err[-200:]}")
        else:
            igual(f"{nome}: exit 0 e {chave} {esperado}", (rc, contagens(out[-1]).get(chave) if out else None),
                  (0, esperado))
        shutil.rmtree(raiz.parent, ignore_errors=True)

    print("\n== calendário: bloco vagas_semanais ausente = 0 vagas com ⚠; quebrado = ✗ ==")
    cal = "_controle/calendario.md"
    for nome, conteudo in (("arquivo ausente", None), ("sem bloco yaml", "# Calendário\n\nsó texto\n"),
                           ("bloco sem vagas_semanais", "```yaml\nfuso: Europe/London\n```\n")):
        raiz = Path(tempfile.mkdtemp(prefix="korvu-painel-cal-")) / "raiz"
        shutil.copytree(ROOT, raiz)
        (raiz / cal).unlink() if conteudo is None else (raiz / cal).write_text(conteudo, encoding="utf-8")
        rc, out, err = sincronizar("--seco", db=PORTA_MORTA, projeto=raiz)
        ok(f"calendário {nome}: exit 0, uma linha ⚠ e calendario_vagas 0",
           rc == 0 and len(out) == 2 and "⚠" in out[0] and "vagas_semanais" in out[0]
           and contagens(out[-1]).get("calendario_vagas") == 0 and not err, f"rc={rc} {out} {err[-200:]}")
        shutil.rmtree(raiz.parent, ignore_errors=True)
    bloco = lambda corpo: f"# Calendário\n\n```yaml\nfuso: Europe/London\n{corpo}```\n"  # noqa: E731
    for nome, corpo in (("YAML inválido", "vagas_semanais: [domingo: \n"),
                        ("dia que não existe", 'vagas_semanais:\n  feriado: "19:00"\n'),
                        ("hora 25:00", 'vagas_semanais:\n  domingo: "25:00"\n'),
                        ("hora '19h'", 'vagas_semanais:\n  domingo: "19h"\n'),
                        ("vaga repetida", 'vagas_semanais:\n  domingo: ["19:00", "19:00"]\n'),
                        ("vagas_semanais vazio", "vagas_semanais:\n"),
                        ("vagas_semanais em lista", 'vagas_semanais: ["domingo 19:00"]\n')):
        variante(cal, bloco(corpo), f"calendário {nome}", cal, None)
    variante(cal, '# C\n\n```yaml\nfuso: Lua/Crateras\nvagas_semanais:\n  domingo: "19:00"\n```\n',
             "calendário fuso desconhecido", cal, None)
    print("\n== calendário sem fuso: no bloco: a ordem do publicar.py (TZ_PUBLICACAO, depois Europe/London), com ⚠ (PD26) ==")
    for env_extra, fuso in (({}, "Europe/London"), ({"TZ_PUBLICACAO": "America/Sao_Paulo"}, "America/Sao_Paulo")):
        raiz = Path(tempfile.mkdtemp(prefix="korvu-painel-fuso-")) / "raiz"
        shutil.copytree(ROOT, raiz)
        (raiz / cal).write_text('# C\n\n```yaml\nvagas_semanais:\n  domingo: "19:00"\n```\n', encoding="utf-8")
        rc, out, err = sincronizar("--seco", db=PORTA_MORTA, projeto=raiz, env_extra=env_extra)
        ok(f"sem fuso: e {'com TZ_PUBLICACAO=' + fuso if env_extra else 'sem TZ_PUBLICACAO'}: exit 0, ⚠ que diz {fuso}, "
           "1 vaga", rc == 0 and len(out) == 2 and "⚠" in out[0] and "não diz o fuso" in out[0] and f"usa {fuso} " in out[0]
           and contagens(out[-1]).get("calendario_vagas") == 1 and not err, f"rc={rc} {out} {err[-200:]}")
        shutil.rmtree(raiz.parent, ignore_errors=True)
    rc, out, _ = sincronizar("--seco", db=PORTA_MORTA, env_extra={"TZ_PUBLICACAO": "America/Sao_Paulo"})
    ok("com fuso: no bloco, o TZ_PUBLICACAO não manda e não há aviso", rc == 0 and len(out) == 1, out)

    print("\n== prontos, roteiro.json e perfil diário fora do formato = ✗; perfil diário ausente = vazio ==")
    pac = "05-render-pronto/2026-10-30-com-status/pacote.json"
    base = {"slug": "x", "qa": "PASS", "duracao": 58.7, "criado_em": "2026-10-30T18:00:00+01:00", "cta_palavra": "P"}
    for nome, conteudo in (("duracao em texto", {**base, "duracao": "58.7"}), ("duracao zero", {**base, "duracao": 0}),
                           ("criado_em sem fuso", {**base, "criado_em": "2026-10-30T18:00:00"}),
                           ("cta_palavra número", {**base, "cta_palavra": 7}), ("não é objeto", [base])):
        variante(pac, conteudo, f"pacote.json {nome}", pac, None)
    variante("videos/2026-10-30-com-status/roteiro.json", '{"versao": 3', "roteiro.json truncado",
             "videos/2026-10-30-com-status/roteiro.json", None)
    dia = "_controle/perfil/diario/2026-10-23.json"
    bom = PERFIL_DIARIO["2026-10-23.json"]
    for nome, conteudo in (("dia ≠ nome do arquivo", {**bom, "dia": "2026-10-22"}),
                           ("valor negativo", {**bom, "metricas": {"reach": -1}}),
                           ("valor em texto", {**bom, "metricas": {"reach": "41"}}),
                           ("metricas em lista", {**bom, "metricas": [41]}),
                           ("lido_em sem fuso", {**bom, "lido_em": "2026-10-24T09:30:00"})):
        variante(dia, conteudo, f"perfil diário {nome}", dia, None)
    variante("_controle/perfil/diario", None, "perfil diário: pasta ausente", "", 0, "perfil_diario")


def modelo_por_agente(hoje: str) -> dict[tuple, dict]:
    """A view com o "hoje" fixo (set painel.hoje: o teste não depende do dia em que roda)."""
    with psycopg.connect(BANCO_TESTE) as con:
        con.execute("select set_config('painel.hoje', %s, false)", [hoje])
        return {(r["agente_id"], r["modelo"]): r for r in linhas(con, "select * from modelo_por_agente")}


def casos_modelo_por_agente() -> None:
    print("\n== modelo_por_agente: o modelo que RODOU, por agente, nos 30 dias UTC até hoje (decisão de 24/10) ==")
    utc = lambda t: ts(t).astimezone(dt.timezone.utc)  # noqa: E731
    v = modelo_por_agente("2026-10-24")  # janela 25/09–24/10
    igual("uma linha por agente × modelo na janela; o Atlas (diretor) soma a sessão principal e os ajudantes; o "
          "claude-opus-5 de 16/09 (fora) e o modelo sem preço não entram",
          sorted(k for k in v), sorted([("diretor", OPUS), ("diretor", SONNET), ("diretor", FABLE),
                                        ("portao-dados", OPUS), ("engenheiro-backend", OPUS)]))
    col = ("modelo_declarado", "modelo_nome", "tokens", "usd", "execucoes", "ultima_execucao", "ultima_execucao_geral",
           "nunca_rodou")
    igual("tokens, US$, execuções e a última execução de cada agente × modelo (a de 24/10 00:00 entra: o hoje é inclusivo)",
          {k: tuple(r[c] for c in col) for k, r in v.items()},
          {("diretor", OPUS): ("opus", "Opus 5.5", 14150, Decimal("0.09016"), 7, utc("2026-10-24T00:00:00+00:00"),
                               utc("2026-10-24T00:00:00+00:00"), False),
           ("diretor", SONNET): ("opus", "Sonnet 5.5", 4 * M, Decimal("18.7"), 1, utc("2026-10-05T12:00:00+00:00"),
                                 utc("2026-10-24T00:00:00+00:00"), False),
           ("diretor", FABLE): ("opus", "Fable 5.1", 4 * M, Decimal("92.75"), 1, utc("2026-10-06T12:00:00+00:00"),
                                utc("2026-10-24T00:00:00+00:00"), False),
           ("portao-dados", OPUS): ("opus", "Opus 5.5", 4030, Decimal("0.04752"), 2, utc("2026-10-14T00:00:01+00:00"),
                                    utc("2026-10-14T00:00:01+00:00"), False),
           ("engenheiro-backend", OPUS): ("opus", "Opus 5.5", 4 * M, Decimal("37.2"), 1, utc("2026-10-07T12:00:00+00:00"),
                                          utc("2026-10-07T12:00:00+00:00"), False)})
    total = 14150 + 8 * M
    ok("pct_tokens: o % de cada modelo nos tokens DO AGENTE (o Atlas: 14.150 / 8.014.150 no Opus); somam 100 por agente",
       abs(v[("diretor", OPUS)]["pct_tokens"] - Decimal(100 * 14150) / total) < Decimal("1e-12")
       and abs(v[("diretor", SONNET)]["pct_tokens"] - Decimal(100 * 4 * M) / total) < Decimal("1e-12")
       and all(abs(sum(r["pct_tokens"] for k, r in v.items() if k[0] == a) - 100) < Decimal("1e-12")
               for a in ("diretor", "portao-dados", "engenheiro-backend")),
       {k: r["pct_tokens"] for k, r in v.items()})

    v = modelo_por_agente("2026-11-10")  # janela 12/10–10/11: a sessão de 12/10 (sess-c) entra — o início é inclusivo
    igual("início da janela inclusivo (hoje − 29): o Opus do Atlas = 20 (13/10) + 7.000 (24/10) + 2.100 (12/10)",
          (v.get(("diretor", OPUS), {}).get("tokens"), v.get(("diretor", OPUS), {}).get("execucoes")), (9120, 2))
    v = modelo_por_agente("2026-11-11")  # janela 13/10–11/11
    igual("um dia depois, a de 12/10 sai (são 30 dias, não 31)", v.get(("diretor", OPUS), {}).get("tokens"), 7020)
    e = v.get(("engenheiro-backend", None), {})
    igual("rodou só fora da janela: uma linha com modelo NULL, 0 tokens, a última de sempre e nunca_rodou = false",
          (sorted(k for k in v if k[0] == "engenheiro-backend"), e.get("tokens"), e.get("pct_tokens"), e.get("usd"),
           e.get("execucoes"), e.get("ultima_execucao"), e.get("ultima_execucao_geral"), e.get("nunca_rodou"),
           e.get("modelo_declarado")),
          ([("engenheiro-backend", None)], 0, None, Decimal(0), 0, None, utc("2026-10-07T12:00:00+00:00"), False, "opus"))

    eq = ROOT / "painel" / "equipe.yaml"
    original = eq.read_text(encoding="utf-8")
    eq.write_text(original + "  - id: novato-x\n    nome: Novato\n    cargo: novo\n    departamento: tecnologia\n"
                             "    papel: construtor\n    resumo: Ainda não rodou.\n", encoding="utf-8")
    rc, out, err = sincronizar(db=BANCO_TESTE)
    n = modelo_por_agente("2026-10-24").get(("novato-x", None), {})
    igual("nunca rodou: aparece mesmo assim, uma linha com modelo NULL, sem última execução e nunca_rodou = true",
          (rc, n.get("tokens"), n.get("execucoes"), n.get("ultima_execucao_geral"), n.get("nunca_rodou"),
           n.get("modelo_declarado")), (0, 0, 0, None, True, None))
    eq.write_text(original, encoding="utf-8")

    guarda = Path(tempfile.mkdtemp(prefix="korvu-painel-mpa-"))
    sumidos = ["sess-a/subagents/agent-a04.jsonl", "sess-a/subagents/agent-a04.meta.json"]
    for rel in sumidos:
        (guarda / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(REG / rel, guarda / rel)
    rc, out, err = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        presente = linhas(con, "select registro_presente from execucoes where arquivo = %s",
                          ("sess-a/subagents/agent-a04.jsonl",))[0]["registro_presente"]
    a = modelo_por_agente("2026-10-24").get(("engenheiro-backend", OPUS), {})
    igual("arquivada dentro da janela (o .jsonl sumiu, registro_presente = false): continua contando, também na última",
          (rc, presente, a.get("tokens"), a.get("execucoes"), a.get("ultima_execucao"), a.get("ultima_execucao_geral")),
          (0, False, 4 * M, 1, utc("2026-10-07T12:00:00+00:00"), utc("2026-10-07T12:00:00+00:00")))
    for rel in sumidos:
        shutil.move(guarda / rel, REG / rel)
    shutil.rmtree(guarda, ignore_errors=True)
    rc, out, err = sincronizar(db=BANCO_TESTE)
    ok("de volta ao estado da raiz de exemplo", rc == 0 and out and contagens(out[-1]) == ESPERADO, f"rc={rc} {out}")


def casos_fila_troca() -> None:
    print("\n== fila: arquivo trocado depois do selo → não sai (o banco sabe pela conferência) ==")
    capa = ROOT / "06-publicar" / "2026-11-02-selado" / "capa" / "capa.png"
    antes = foto(ROOT)
    capa.write_bytes(b"\x89PNG outra capa")
    rc, out, err = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        erros = linhas(con, "select erros_gauntlet from fila where slug = '2026-11-02-selado'")[0]["erros_gauntlet"]
    ok("exit 0; erros: a capa trocada depois do selo e o portão da publicação vencido",
       rc == 0 and any(e.startswith("capa/capa.png: trocado depois do selo") for e in erros)
       and any(e.startswith("portão publicacao (portao-publicacao) VENCIDO") for e in erros), f"rc={rc} {erros} {err[-200:]}")
    capa.write_bytes(CAPA)
    rc, out, _ = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        erros = linhas(con, "select erros_gauntlet from fila where slug = '2026-11-02-selado'")[0]["erros_gauntlet"]
    igual("a capa aprovada de volta: pode sair de novo", (rc, erros), (0, []))
    ok("a conferência não grava nada na raiz (nem o cache dos portões)",
       {k: v for k, v in foto(ROOT).items() if "capa/capa.png" not in k}
       == {k: v for k, v in antes.items() if "capa/capa.png" not in k})


def casos_arquivo() -> None:
    print("\n== arquivo: o .jsonl some → a execução fica (registro_presente = false) ==")
    guarda = Path(tempfile.mkdtemp(prefix="korvu-painel-sumidos-"))
    sumidos = ["sess-c.jsonl", "sess-a/subagents/agent-a04.jsonl", "sess-a/subagents/agent-a04.meta.json",
               "sess-a/subagents/agent-a09.jsonl", "sess-a/subagents/agent-a09.meta.json"]
    with psycopg.connect(BANCO_TESTE) as con:
        antes = {r["arquivo"]: r for r in linhas(con, "select * from execucoes")}
        uso_antes = somas(con, ["uso_execucao"])
        usd_antes = linhas(con, "select sum(usd) as u, sum(tokens) as t from consumo")[0]
    for rel in sumidos:
        (guarda / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(REG / rel, guarda / rel)
    yaml_eq = ROOT / "painel" / "equipe.yaml"
    yaml_orig = yaml_eq.read_text(encoding="utf-8")
    yaml_eq.write_text(yaml_orig.replace(
        "  - id: engenheiro-backend\n    nome: Mateus Pacheco\n    cargo: engenheiro back-end\n    departamento: tecnologia",
        "  - id: engenheiro-backend\n    nome: Mateus Pacheco\n    cargo: engenheiro back-end\n    departamento: direcao")
        + "  - id: agente-novo-xyz\n    nome: Novo\n    cargo: novo\n    departamento: tecnologia\n    papel: construtor\n"
          "    resumo: Entrou na tecnologia.\n", encoding="utf-8")
    rc, out, err = sincronizar(db=BANCO_TESTE)
    ok("passagem com 3 .jsonl a menos: exit 0, 'arquivadas 3'", rc == 0 and out and campo(out[-1], "arquivadas") == "3",
       f"rc={rc} {out} {err[-300:]}")
    with psycopg.connect(BANCO_TESTE) as con:
        ex = {r["arquivo"]: r for r in linhas(con, "select * from execucoes")}
        c, e4 = ex.get("sess-c.jsonl", {}), ex.get("sess-a/subagents/agent-a04.jsonl", {})
        igual("as duas continuam no banco, marcadas, com o visto_em da última vez que existiram",
              ((c.get("registro_presente"), c.get("visto_em")), (e4.get("registro_presente"), e4.get("visto_em"))),
              ((False, antes["sess-c.jsonl"]["visto_em"]),
               (False, antes["sess-a/subagents/agent-a04.jsonl"]["visto_em"])))
        igual("a que sumiu segue o equipe.yaml de hoje (engenheiro-backend passou para direcao)",
              (e4.get("membro_id"), e4.get("departamento_id")), ("engenheiro-backend", "direcao"))
        e9 = ex.get("sess-a/subagents/agent-a09.jsonl", {})
        igual("arquivada cujo agentType entrou na tecnologia: membro, departamento e perde o vídeo",
              (e9.get("membro_id"), e9.get("departamento_id"), e9.get("video_slug"), e9.get("registro_presente")),
              ("agente-novo-xyz", "tecnologia", None, False))
        ok("as presentes: registro_presente = true e visto_em novo",
           all(r["registro_presente"] and r["visto_em"] > antes[k]["visto_em"] for k, r in ex.items()
               if k not in ("sess-c.jsonl", "sess-a/subagents/agent-a04.jsonl", "sess-a/subagents/agent-a09.jsonl")))
        igual("uso_execucao intacto e o total (tokens, US$) igual", (somas(con, ["uso_execucao"]),
                                                                    linhas(con, "select sum(usd) as u, sum(tokens) as t "
                                                                                "from consumo")[0]),
              (uso_antes, usd_antes))
    yaml_eq.write_text(yaml_orig, encoding="utf-8")

    print("\n== pasta dos registros some inteira: ⚠, exit 0, nada apagado ==")
    fora = REG.with_name("fora-do-lugar")
    REG.rename(fora)
    rc, out, err = sincronizar(db=BANCO_TESTE)
    ok("exit 0, linha ⚠ + linha ✓, sem ✗", rc == 0 and len(out) == 2 and "⚠" in out[0] and "✓" in out[1]
       and not any("✗" in x for x in out), f"rc={rc} {out} {err[-300:]}")
    with psycopg.connect(BANCO_TESTE) as con:
        n = linhas(con, "select count(*) as n, count(*) filter (where registro_presente) as p from execucoes")[0]
        igual("as 14 execuções ficam, todas como arquivo", (n["n"], n["p"]), (14, 0))
        igual("o total não muda", linhas(con, "select sum(usd) as u, sum(tokens) as t from consumo")[0], usd_antes)
        igual("o departamento volta com o equipe.yaml restaurado (também no arquivo)",
              linhas(con, "select departamento_id from execucoes where arquivo = %s",
                     ("sess-a/subagents/agent-a04.jsonl",))[0]["departamento_id"], "tecnologia")
    fora.rename(REG)
    for rel in sumidos:
        shutil.move(guarda / rel, REG / rel)
    shutil.rmtree(guarda, ignore_errors=True)
    rc, out, _ = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        n = linhas(con, "select count(*) as n, count(*) filter (where registro_presente) as p from execucoes")[0]
        igual("os .jsonl voltam: regravados e presentes de novo", (rc, n["n"], n["p"], campo(out[-1], "arquivadas")),
              (0, 14, 14, "0"))
        igual("a09 relida do arquivo: o vídeo volta (direção, não tecnologia)",
              linhas(con, "select video_slug from execucoes where arquivo = 'sess-a/subagents/agent-a09.jsonl'")[0]
              ["video_slug"], "2026-10-31-sem-status")

    print("\n== câmbio com o banco no ar: inválido = ✗, exit 1, nada apagado; ausente = vazio com ⚠ (PD28) ==")
    cam = ROOT / "painel" / "cambio.yaml"
    with psycopg.connect(BANCO_TESTE) as con:
        antes_db = somas(con)
    cam.write_text(CAMBIO_YAML.replace("valor: 0.7465", "valor: -1"), encoding="utf-8")
    rc, out, err = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        ok("câmbio inválido: exit 1, ✗, nenhuma tabela muda (nem sincronizacoes)",
           rc == 1 and len(out) == 1 and "✗" in out[0] and somas(con) == antes_db, f"rc={rc} {out} {err[-200:]}")
    cam.write_text(CAMBIO_YAML, encoding="utf-8")
    sincronizar(db=BANCO_TESTE)  # a base desta comparação: a mesma raiz, com o câmbio
    with psycopg.connect(BANCO_TESTE) as con:
        antes_db = somas(con)
    cam.unlink()
    rc, out, err = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        # execucoes: visto_em novo; portoes_estado: o cambio.yaml é arquivo da área dados (*.yaml no portoes.py) e sumir
        # com ele muda a impressão do alvo painel — é o portão enxergando a mudança, como deve
        outras = [t for t in TABELAS if t not in ("cambio", "sincronizacoes", "execucoes", "portoes_estado")]
        ok("câmbio ausente: exit 0, ⚠ + ✓, a tabela cambio vazia e as outras iguais",
           rc == 0 and any("⚠" in ln and "painel/cambio.yaml não encontrado" in ln for ln in out)
           and "✓" in out[-1] and con.execute("select count(*) from cambio").fetchone()[0] == 0
           and somas(con, outras) == {t: antes_db[t] for t in outras},
           f"rc={rc} {out[:1]} difere: {[t for t, v in somas(con, outras).items() if v != antes_db[t]]}")
    cam.write_text(CAMBIO_YAML, encoding="utf-8")
    rc, out, err = sincronizar(db=BANCO_TESTE)
    ok("câmbio de volta: a raiz de exemplo de novo", rc == 0 and out and contagens(out[-1]) == ESPERADO,
       f"rc={rc} {out}")


# ───────────────────────── Biblioteca nova: o acervo de estilos (24/10) ─────────────────────────

_spec = importlib.util.spec_from_file_location("previas_looks", SYNC.parent / "previas_looks.py")
PL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PL)  # o nome esperado de cada prévia (o mesmo módulo que o sincronizador importa)

CUBE_ENTRADA, CUBE_V4, CUBE_V5, CUBE_V11 = (f"LUT_3D_SIZE 2\n# {n}\n".encode() for n in ("entrada", "v4", "v5", "v11"))
AMOSTRA_FALSA = b"quadro de amostra (o sincronizador so faz o hash, nunca decodifica)"
JSON_V5 = {"nome": "WAY v5", "versao": "v5", "aprovada": True, "aprovada_em": "2026-09-18",
           "criado_em": "2026-09-15T23:03:13+01:00", "grao_recomendado": 0.3}
COR_MD_TESTE = """# Cor da marca — ficha do look

```yaml
status: ativo
versao_ativa: v5                # comentário com v11 no meio não conta
alternativa_medida: v11         # a medida
arquivados: [v4]                # look "Tenet" (24/10: arquivado; antes era alternativa: v4)
intensidade_lut: 0.8
```

## Look desejado
Texto com rosto 99,9 IRE fora da tabela: não conta.

## Histórico
| Data | Versão | Referências | Amostra | Parâmetros | Decisão |
|---|---|---|---|---|---|
| 2026-09-18 | **v5 ✅ ATIVO** | — | `chatgpt02.MOV` (regravação) | mkl | ESCOLHIDO. Medido: rosto 23,2 IRE, fundo 32,7. O v11 media rosto 40,9 / branco 93,3 |
| 2026-09-15 | **v4** | a, b | PRAQ0967.MOV | rosto 12,0 IRE (coluna errada) | alternativa Tenet |
| 2026-09-17 | **v11 ✅** | — | PRAQ0967.MOV | x | APROVADA: Rosto 16,5 → **22,8 IRE** |
| 2026-09-16 | v4, v11 | — | idem | — | comparação: rosto 30,0 IRE |
| set/2026 | v11 | — | idem | — | data fora do padrão: rosto 31,0 IRE |
| 2026-09-15 | v5 ✅ | — | PRAQ0967.MOV | mkl | APROVADA, sem medida de rosto |

## Depois
| v4 | rosto 50,0 IRE |
"""
ACERVO_YAML_TESTE = """\
capas:
  - id: serifa-e-rabisco
    nome: Serifa + rabisco
    descricao: "  Palavra em serifa.  "
    ficha: 00-marca/fichas/capa-serifa.md
    em_uso: false
    exemplos: [2026-09-17-demis]
  - id: sublinhado
    nome: Sublinhado
    descricao: Rabisco na última palavra.
    ficha: null
    em_uso: true
    exemplos:
      - 2026-11-02-selado
      - 2026-10-30-com-status
legendas:
  - id: texto-selecionado
    nome: Texto Selecionado
    descricao: Seleção arrastada.
    ficha: 00-marca/fichas/legenda.md
    em_uso: true
fontes:
  - familia: Geist
    remotion: Geist
    estilo: normal
    pesos: [700, 400]
    uso: Legendas.
  - familia: Playfair Display
    remotion: PlayfairDisplay
    estilo: italico
    pesos: [400]
    uso: Capa.
    reserva: false
  - familia: Inter Tight
    remotion: InterTight
    estilo: normal
    pesos: [800]
    uso: Reserva.
    reserva: true
  - familia: Fonte do painel
    remotion: null
    estilo: normal
    pesos: [500]
    uso: Só o painel.
ferramentas:
  - nome: Remotion
    tipo: Biblioteca de vídeo
    desc: "Monta o vídeo: legendas, títulos."
    versao: {arquivo: remotion/package.json, pacote: remotion}
  - nome: TypeScript
    tipo: Linguagem
    desc: Tipos.
    versao: {arquivo: remotion/package.json, pacote: typescript}
  - nome: Python
    tipo: Linguagem
    desc: "  Os scripts.  "
    versao: {arquivo: .python-version}
  - nome: Postgres
    tipo: Banco de dados
    desc: Guarda os números.
    versao: {arquivo: painel/supabase/config.toml, chave: db.major_version}
  - nome: Claude Code
    tipo: Agente de IA
    desc: Onde a equipe trabalha.
modelos:
  - modelo: claude-opus-5-5
    desc: O mais forte.
  - modelo: claude-fable-5-1
    desc: "Usado pelo Atlas: parte das sessões."
looks:
  - id: vlog
    nome: Original da câmera
    desc: "Como a câmera grava: plano."
  - id: rec709
    desc: Só a conversão.
  - id: v4
    nome: Look v4
    desc: "O look “Tenet”, frio."
  - id: v5
    nome: Look v5 · WAY
    desc: "O escolhido: “a pele”."
    rosto_ire: 23.2
    medido_em: 2026-09-18
    amostra: "chatgpt02.MOV (regravação)"
    fonte: 00-marca/cor/cor.md:41
  - id: v11
    rosto_ire: 40.9
    medido_em: "2026-09-18"
    fonte: 00-marca/cor/cor.md:7,41
"""
BRAND_TS_TESTE = """\
import { loadFont as loadGeist } from "@remotion/google-fonts/Geist";
import { loadFont as loadInterTight } from "@remotion/google-fonts/InterTight";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";

const geist = loadGeist("normal", {
  weights: ["400", "700"],
  subsets: ["latin", "latin-ext"],
});
const interTight = loadInterTight("normal", { weights: ["800"], subsets: ["latin"] });
// Serifa itálica: só para UMA palavra da capa.
const playfair = loadPlayfair("italic", {
  weights: ["400"],
  subsets: ["latin"],
});
"""
ANIM = "videos/2026-10-30-com-status/animacoes"
BRIEF_E01 = """# E01 — A ligação de madrugada (L20)

- **Vídeo:** 2026-10-30-com-status · EDL v24 (aprovada)
- **Modo:** `split` — animação deitada 16:9 na **metade de cima** do Reel
- **Linha:** L20 inteira · saída **107,16 → 113,92 s** · **duração 6,76 s** (169 frames a 25 fps)

> nota: Duração total: 9,99 s no prompt não conta.

---

## PROMPT
- **Modo:** `full`
- **Linha:** L99 · **duração 99,9 s**
"""
BRIEF_E04 = """# E04 — "Uma máquina que imita a mente" (L08 + L09)

- **Vídeo:** 2026-10-30-com-status · EDL v24
- **Modo:** `full` — tela cheia
- **Linhas:** L08 + L09 · saída **38,68 → 48,92 s** · **duração 10,24 s** (256 frames a 25 fps)
"""
BRIEF_E06 = """# E06 — 2012: o sistema que reconheceu imagens

- **Vídeo:** 2026-10-30-com-status
- **Modo:** `card`
- **Linha:** L12 · **duração 3 s**
"""


def montar_acervo() -> None:
    luts = "00-marca/cor/luts"
    escrever(f"{luts}/entrada-camera.cube", CUBE_ENTRADA)
    escrever(f"{luts}/entrada-camera.json", {"nome": "entrada-camera", "provisorio": True,
                                             "criado_em": "2026-09-15T18:28:00+01:00"})
    # criado_em 00:30 +01:00 = 23:30 UTC do dia ANTERIOR: a data vem como está escrita (15/09), não convertida
    escrever(f"{luts}/korvu-look-v4.json", {"nome": "korvu-look-v4", "versao": "v4", "aprovada": False,
                                            "aprovada_em": None, "criado_em": "2026-09-15T00:30:00+01:00"})
    escrever(f"{luts}/korvu-look-v4.cube", CUBE_V4)
    escrever(f"{luts}/korvu-look-v5.json", JSON_V5)
    escrever(f"{luts}/korvu-look-v5.cube", CUBE_V5)
    escrever(f"{luts}/korvu-look-v11.json", {"versao": "v11", "tipo": "parametrico", "nome": "v5 + pele",
                                             "aprovada": False, "aprovada_em": "2026-09-17", "criado_em": "2026-09-17"})
    escrever(f"{luts}/korvu-look-v11.cube", CUBE_V11)
    escrever(f"{luts}/_descartadas/korvu-look-v9.json", {"versao": "v9", "aprovada": True})
    escrever(f"{luts}/_descartadas/korvu-look-v9.cube", b"descartada")
    escrever(f"{luts}/korvu-look-v9.cube", b"orfao")  # .cube no topo sem o .json (que está em _descartadas/): não é look
    escrever(f"{luts}/korvu-look-v5-copia.json", {"versao": "v5"})  # fora do padrão do nome: não é look
    escrever(PL.AMOSTRA, AMOSTRA_FALSA)
    escrever("00-marca/cor/cor.md", COR_MD_TESTE)
    esp = PL.esperadas(ROOT)
    escrever(f"{PL.SAIDA}/{esp['v5']['nome']}", b"jpeg do v5")  # só o v5 tem prévia gerada
    escrever(f"{PL.SAIDA}/v4-0000000000000000.jpg", b"jpeg de um v4 antigo")  # nome que não é o esperado
    # biblioteca.yaml e o que ele cita
    escrever("painel/biblioteca.yaml", ACERVO_YAML_TESTE)
    escrever("00-marca/fichas/capa-serifa.md", "ficha\n")
    escrever("00-marca/fichas/legenda.md", "ficha\n")
    escrever("07-publicados/2026-09-17-demis/capa/capa.png", b"capa do demis")
    escrever("05-render-pronto/2026-10-30-com-status/capa/capa.png", b"capa do pronto")  # 06-publicar dele não tem capa
    escrever("remotion/src/brand.ts", BRAND_TS_TESTE)
    escrever("remotion/package.json", {"dependencies": {"remotion": "4.0.1"}, "devDependencies": {"typescript": "5.9.3"}})
    escrever(".python-version", "\n3.12\n")
    escrever("painel/supabase/config.toml", "[db]\nport = 1\nmajor_version = 17\n")
    # animações: E01 roteirizada; E04 com o .mp4 do ingest; E06 com o .mp4 dentro da pasta dela
    escrever(f"{ANIM}/E01/brief.md", BRIEF_E01)
    escrever(f"{ANIM}/E04/brief.md", BRIEF_E04)
    escrever("videos/2026-10-30-com-status/edicao/extras/E04.mp4", b"mp4 do ingest")
    escrever(f"{ANIM}/E06/brief.md", BRIEF_E06)
    escrever(f"{ANIM}/E06/export/E06.mp4", b"mp4 capturado")
    escrever(f"{ANIM}/E06/export/.E06-oculto.mp4", b"oculto")
    escrever("videos/_teste-x/animacoes/E01/brief.md", BRIEF_E01)  # pasta _teste-*: fora
    # contagens: SKILL.md em 3 das 4 skills; pasta _ e oculta com SKILL.md ficam fora; .txt em agents não conta
    for sk in ("supabase", "legendas-animadas", "remotion-render", "_velha", ".oculta"):
        escrever(f".claude/skills/{sk}/SKILL.md", "# skill\n")
    escrever(".claude/agents/notas.txt", "não é agente\n")
    escrever(".claude/commands/notas.txt", "não é comando\n")  # S1-1: o filtro .md dos comandos
    for nome in ("_rascunho.md", ".oculto.md"):  # PD30: nem a Equipe nem o Sistema contam (e citam agentes de propósito)
        escrever(f".claude/commands/{nome}", "Rascunho: chama o engenheiro-backend e o portao-dados.\n")


@contextmanager
def trocado(*pares):
    """Troca arquivos da raiz de exemplo (conteúdo; None = apaga) e devolve como estavam no fim — também apaga as
    pastas que a troca criou."""
    guardados, criadas = [], []
    for rel, conteudo in pares:
        p = ROOT / rel
        topo, nova = p.parent, None
        while not topo.exists():
            nova, topo = topo, topo.parent
        if nova is not None:
            criadas.append(nova)
        guardados.append((p, p.read_bytes() if p.is_file() else None))
        if conteudo is None:
            p.unlink(missing_ok=True)
        else:
            escrever(rel, conteudo)
    try:
        yield
    finally:
        for p, antes in reversed(guardados):
            if antes is None:
                p.unlink(missing_ok=True)
            else:
                p.write_bytes(antes)
        for d in criadas:
            shutil.rmtree(d, ignore_errors=True)


def _seco(*pares) -> tuple[int, list[str], str]:
    with trocado(*pares):
        return sincronizar("--seco", db=PORTA_MORTA)


def casos_acervo_sem_banco() -> None:
    print("\n== Biblioteca nova (--seco): biblioteca.yaml estrito, cor.md, .json das LUTs e briefs ==")
    rc, out, err = sincronizar("--seco", db=PORTA_MORTA)
    ok("raiz de exemplo: nenhum aviso ⚠ (todo aviso abaixo vem do caso)", rc == 0 and len(out) == 1, out)

    y = "painel/biblioteca.yaml"
    rc, out, _ = _seco((y, None))
    c = contagens(out[-1]) if out else {}
    ok("biblioteca.yaml ausente: exit 0, um ⚠ e capas, legendas, fontes e ferramentas vazias",
       rc == 0 and any("⚠" in ln and "painel/biblioteca.yaml não encontrado" in ln for ln in out)
       and [c.get(t) for t in ("capa_estilos", "capa_estilos_exemplos", "legenda_estilos", "fontes",
                               "sistema_ferramentas", "modelos_descricao")] == [0] * 6 and c.get("looks") == 5, out)
    rc, out, _ = _seco((y, ACERVO_YAML_TESTE.split("ferramentas:")[0]))
    ok("seção ausente (ferramentas): ⚠ e 0 ferramentas", rc == 0 and any("sem a seção ferramentas" in ln for ln in out)
       and contagens(out[-1]).get("sistema_ferramentas") == 0, out)
    quebrados = [
        ("YAML inválido", "capas: [\n", "painel/biblioteca.yaml"),
        ("não é um mapa", "- capas\n", "não é um mapa"),
        ("seção desconhecida", ACERVO_YAML_TESTE + "estilos: []\n", "seção desconhecida estilos"),
        ("seção que não é lista", ACERVO_YAML_TESTE.split("legendas:")[0] + "legendas: x\nfontes:"
         + ACERVO_YAML_TESTE.split("fontes:")[1], "legendas: não é uma lista"),
        ("chave desconhecida", ACERVO_YAML_TESTE.replace("    em_uso: false\n", "    em_uso: false\n    cor: azul\n", 1),
         "capas[0]: chave desconhecida cor"),
        ("falta campo", ACERVO_YAML_TESTE.replace("    em_uso: true\n    exemplos:", "    exemplos:", 1),
         "capas[1]: falta em_uso"),
        ("bool como texto", ACERVO_YAML_TESTE.replace("em_uso: false", "em_uso: \"false\"", 1), "capas[0].em_uso"),
        ("id fora do padrão", ACERVO_YAML_TESTE.replace("id: sublinhado", "id: Sublinhado Laranja", 1), "capas[1].id"),
        ("id repetido", ACERVO_YAML_TESTE.replace("id: sublinhado", "id: serifa-e-rabisco", 1),
         "capas[1]: id 'serifa-e-rabisco' repetido"),
        ("slug de exemplo fora do padrão", ACERVO_YAML_TESTE.replace("[2026-09-17-demis]", "[demis]", 1),
         "capas[0].exemplos"),
        ("exemplos vazio", ACERVO_YAML_TESTE.replace("[2026-09-17-demis]", "[]", 1), "capas[0].exemplos"),
        ("ficha absoluta", ACERVO_YAML_TESTE.replace("ficha: 00-marca/fichas/legenda.md", "ficha: /etc/passwd", 1),
         "legendas[0].ficha"),
        ("ficha com ..", ACERVO_YAML_TESTE.replace("ficha: 00-marca/fichas/legenda.md", "ficha: ../fora.md", 1),
         "legendas[0].ficha"),
        ("peso como texto", ACERVO_YAML_TESTE.replace("pesos: [700, 400]", "pesos: [700, \"400\"]", 1),
         "fontes[0].pesos"),
        ("estilo fora da lista", ACERVO_YAML_TESTE.replace("estilo: italico", "estilo: italic", 1), "fontes[1].estilo"),
        ("família repetida", ACERVO_YAML_TESTE.replace("familia: Inter Tight", "familia: Geist", 1),
         "fontes[2]: familia 'Geist' repetido"),
        ("versão de .json sem pacote", ACERVO_YAML_TESTE.replace(
            "{arquivo: remotion/package.json, pacote: remotion}", "{arquivo: remotion/package.json}", 1),
         "ferramentas[0].versao"),
        ("versão de .toml com pacote", ACERVO_YAML_TESTE.replace("chave: db.major_version", "pacote: db", 1),
         "ferramentas[3].versao"),
        ("ferramenta sem tipo", ACERVO_YAML_TESTE.replace("    tipo: Biblioteca de vídeo\n", "", 1),
         "ferramentas[0]: falta tipo"),
        ("ferramenta sem desc", ACERVO_YAML_TESTE.replace("    desc: Tipos.\n", "", 1), "ferramentas[1]: falta desc"),
        ("ferramenta com desc vazio", ACERVO_YAML_TESTE.replace("    desc: Tipos.\n", "    desc: \"  \"\n", 1),
         "ferramentas[1].desc"),
        ("ferramenta com o campo antigo uso", ACERVO_YAML_TESTE.replace("    tipo: Linguagem\n", "    tipo: Linguagem\n"
                                                                        "    uso: tipos\n", 1),
         "ferramentas[1]: chave desconhecida uso"),
        ("modelo sem desc", ACERVO_YAML_TESTE.replace("    desc: O mais forte.\n", "", 1), "modelos[0]: falta desc"),
        ("modelo repetido", ACERVO_YAML_TESTE.replace("modelo: claude-fable-5-1", "modelo: claude-opus-5-5", 1),
         "modelos[1]: modelo 'claude-opus-5-5' repetido"),
        ("modelo fora do padrão de id", ACERVO_YAML_TESTE.replace("modelo: claude-fable-5-1", "modelo: Fable 5.1", 1),
         "modelos[1].modelo"),
        ("modelos que não é lista", ACERVO_YAML_TESTE.split("modelos:")[0] + "modelos: claude-opus-5-5\n",
         "modelos: não é uma lista"),
        ("rosto como texto", ACERVO_YAML_TESTE.replace("rosto_ire: 23.2", 'rosto_ire: "23,2"', 1), "looks[3].rosto_ire"),
        ("rosto fora de 0–110", ACERVO_YAML_TESTE.replace("rosto_ire: 23.2", "rosto_ire: 150", 1), "looks[3].rosto_ire"),
        ("rosto true", ACERVO_YAML_TESTE.replace("rosto_ire: 23.2", "rosto_ire: true", 1), "looks[3].rosto_ire"),
        ("id de look fora do padrão (vlog, rec709 ou vN)", ACERVO_YAML_TESTE.replace("  - id: v5\n", "  - id: V5\n", 1),
         "looks[3].id"),
        ("rosto na referência (vlog não é look)", ACERVO_YAML_TESTE.replace(
            '    desc: "Como a câmera grava: plano."\n',
            '    desc: "Como a câmera grava: plano."\n    rosto_ire: 10\n    medido_em: 2026-09-18\n    fonte: x.md:1\n', 1),
         "looks[0]: rosto_ire só em look vN"),
        ("medida sem rosto_ire", ACERVO_YAML_TESTE.replace('    desc: "O look “Tenet”, frio."\n',
                                                           '    desc: "O look “Tenet”, frio."\n    fonte: x.md:1\n', 1),
         "looks[2]: fonte sem rosto_ire"),
        ("nome de look vazio", ACERVO_YAML_TESTE.replace("    nome: Look v4\n", '    nome: " "\n', 1), "looks[2].nome"),
        ("id de look repetido", ACERVO_YAML_TESTE.replace("  - id: v11\n", "  - id: v5\n", 1),
         "looks[4]: id 'v5' repetido"),
        ("rosto sem medido_em", ACERVO_YAML_TESTE.replace("    medido_em: 2026-09-18\n", "", 1),
         "looks[3]: falta medido_em (obrigatório com rosto_ire)"),
        ("medido_em fora do padrão", ACERVO_YAML_TESTE.replace("medido_em: 2026-09-18", "medido_em: 18/09/2026", 1),
         "looks[3].medido_em"),
        ("rosto sem fonte", ACERVO_YAML_TESTE.replace("    fonte: 00-marca/cor/cor.md:41\n", "", 1),
         "looks[3]: falta fonte (obrigatório com rosto_ire)"),
        ("look com chave desconhecida", ACERVO_YAML_TESTE.replace("    fonte: 00-marca/cor/cor.md:41\n",
                                                                  "    fonte: 00-marca/cor/cor.md:41\n    nota: x\n", 1),
         "looks[3]: chave desconhecida nota"),
    ]
    for nome, txt, trecho in quebrados:
        rc, out, err = _seco((y, txt))
        ok(f"biblioteca.yaml {nome}: exit 1, uma linha ✗ que diz onde ({trecho})",
           rc == 1 and len(out) == 1 and "✗" in out[0] and "painel/biblioteca.yaml" in out[0] and trecho in out[0]
           and not err, f"rc={rc} {out} {err[-200:]}")

    cor = "00-marca/cor/cor.md"
    for nome, txt, trecho in (
            ("YAML inválido no trecho", COR_MD_TESTE.replace("status: ativo\n", "status: [ativo\n", 1), cor),
            ("chave repetida", COR_MD_TESTE.replace("arquivados: [v4] ", "arquivados: [v4]\narquivados: [v11] ", 1),
             "arquivados repetida"),
            ("trecho que não é mapa", re.sub(r"```yaml\n.*?```", "```yaml\n- a\n- b\n```", COR_MD_TESTE, count=1,
                                              flags=re.S), "não é um mapa")):
        rc, out, _ = _seco((cor, txt))
        ok(f"cor.md {nome}: exit 1, ✗ com o caminho", rc == 1 and len(out) == 1 and "✗" in out[0] and trecho in out[0],
           out)
    lut = "00-marca/cor/luts/korvu-look-v5.json"
    for nome, conteudo, trecho in (("JSON quebrado", "{", lut), ("não é objeto", "[]", "não é um objeto JSON"),
                                   ("versao ≠ nome do arquivo", {**JSON_V5, "versao": "v6"}, "versao 'v6'"),
                                   ("aprovada como texto", {**JSON_V5, "aprovada": "sim"}, "aprovada 'sim'"),
                                   ("data que não é ISO", {**JSON_V5, "criado_em": "ontem"}, "criado_em 'ontem'")):
        rc, out, _ = _seco((lut, conteudo))
        ok(f"korvu-look-v5.json {nome}: exit 1, ✗ com o caminho e o campo",
           rc == 1 and len(out) == 1 and "✗" in out[0] and lut in out[0] and trecho in out[0], out)
    arq_hd = "videos/2026-10-31-sem-status/brutos/principal/ARQUIVADO.json"
    um = [{"nome": "PRAQ0001.MOV", "bytes": 1000, "sha256": "0" * 64, "mtime": "2026-10-20T10:00:00+00:00",
           "ctime": "2026-10-21T10:00:00+00:00"}]
    # 25/10 (Carlos): o HD externo não aparece no painel — arquivado_em e destino não são lidos (o resto do manifesto e o
    # sha256 de cada arquivo continuam obrigatórios: casos_arquivado_sem_banco)
    rc, out, _ = _seco((arq_hd, {"arquivado_em": "2026-10-24T22:00:00", "destino": "KORVU V01", "arquivos": um}))
    ok("ARQUIVADO.json com arquivado_em sem fuso e destino em texto: aceito (o painel não lê esses campos desde 25/10)",
       rc == 0 and len(out) == 1, out)
    rc, out, _ = _seco((arq_hd, {"arquivado_em": "2026-10-24T22:00:00+01:00",
                                 "arquivos": [{k: v for k, v in um[0].items() if k != "sha256"}]}))
    ok("ARQUIVADO.json sem o sha256 de um arquivo: continua ✗ (a prova da cópia)",
       rc == 1 and len(out) == 1 and "✗" in out[0] and arq_hd in out[0] and "sha256" in out[0], out)
    ok("o .json de _descartadas/ não é lido (quebrado não para nada)",
       _seco(("00-marca/cor/luts/_descartadas/korvu-look-v9.json", "{"))[0] == 0)

    avisos = [
        ("cor.md sem versao_ativa", (cor, COR_MD_TESTE.replace("versao_ativa: v5 ", "outra: v5 ", 1)),
         "não diz versao_ativa"),
        ("alternativa_medida que não é só vN",
         (cor, COR_MD_TESTE.replace("alternativa_medida: v11 ", "alternativa_medida: v11 (WAY) ", 1)),
         "linha 6: alternativa_medida = 'v11 (WAY)' não é uma versão vN"),
        ("a chave alternativa de volta (aposentada em 24/10)",
         (cor, COR_MD_TESTE.replace("intensidade_lut: 0.8\n", "alternativa: v4\nintensidade_lut: 0.8\n", 1)),
         "linha 8: a chave alternativa não é mais lida"),
        ("arquivados que não é lista", (cor, COR_MD_TESTE.replace("arquivados: [v4] ", "arquivados: v4 ", 1)),
         "linha 7: arquivados = 'v4' não é uma lista"),
        ("item de arquivados fora do padrão",
         (cor, COR_MD_TESTE.replace("arquivados: [v4] ", 'arquivados: [v4, "v11 (WAY)"] ', 1)),
         "linha 7: item de arquivados 'v11 (WAY)' não é uma versão vN"),
        ("o mesmo look ativo e arquivado", (cor, COR_MD_TESTE.replace("arquivados: [v4] ", "arquivados: [v4, v5] ", 1)),
         "o v5 está ao mesmo tempo em versao_ativa (linha 5) e arquivados (linha 7)"),
        ("versao_ativa sem .json", (cor, COR_MD_TESTE.replace("versao_ativa: v5 ", "versao_ativa: v7 ", 1)),
         "linha 5: versao_ativa = v7, mas não há korvu-look-v7.json"),
        ("cor.md sem trecho yaml", (cor, COR_MD_TESTE.replace("```yaml", "```", 1)), "sem o trecho ```yaml"),
        ("rosto de um id que não é look de luts/ (ex.: foi para _descartadas/)",
         (y, ACERVO_YAML_TESTE + "  - id: v7\n    rosto_ire: 30\n    medido_em: 2026-09-20\n    fonte: x.md:1\n"),
         "looks[5] v7 não é um cartão desta passagem"),
        ("cor.md ausente", (cor, None), "cor.md não encontrado"),
        ("look sem .cube", ("00-marca/cor/luts/korvu-look-v11.cube", None), "korvu-look-v11.json sem o "
                                                                             "korvu-look-v11.cube ao lado"),
        ("capa de exemplo que não existe", (y, ACERVO_YAML_TESTE.replace("2026-09-17-demis]", "2026-09-17-outro]")),
         "capa de exemplo 2026-09-17-outro (serifa-e-rabisco) não encontrada"),
        ("ficha que não existe", (y, ACERVO_YAML_TESTE.replace("fichas/legenda.md", "fichas/sumiu.md")),
         "a ficha 00-marca/fichas/sumiu.md não existe"),
        ("fonte com outros pesos", (y, ACERVO_YAML_TESTE.replace("pesos: [800]", "pesos: [500, 800]")),
         "fonte Inter Tight não bate com o remotion/src/brand.ts"),
        ("fonte de pacote não importado", (y, ACERVO_YAML_TESTE.replace("remotion: Geist", "remotion: Inter")),
         "fonte Geist não bate"),
        ("versão não encontrada", (y, ACERVO_YAML_TESTE.replace("pacote: typescript", "pacote: vite")),
         "versão de TypeScript não encontrada em remotion/package.json#vite"),
        ("modelo fora da tabela de preços", (y, ACERVO_YAML_TESTE.replace("looks:\n", "  - modelo: claude-novo-9\n    desc: Novo.\nlooks:\n", 1)),
         "modelos[2] claude-novo-9 não está na tabela de preços"),
        ("seção modelos ausente", (y, ACERVO_YAML_TESTE.split("modelos:")[0]), "sem a seção modelos"),
        ("pasta de animação fora do padrão", (f"{ANIM}/notas/brief.md", BRIEF_E06), "notas: pasta de animação fora do "
                                                                                    "padrão Exx"),
        ("pasta de animação sem brief", (f"{ANIM}/E10/export/E10.html", "<html>"), "E10: sem brief.md"),
        ("brief com o Exx de outra pasta", (f"{ANIM}/E06/brief.md", BRIEF_E06.replace("# E06", "# E07")),
         "o título diz E07, a pasta é E06"),
        ("brief sem modo no cabeçalho (o do corpo, depois do ---, não conta)",
         (f"{ANIM}/E01/brief.md", BRIEF_E01.replace("- **Modo:** `split` — animação deitada 16:9 na **metade de cima** do "
                                                    "Reel\n", "")), "E01/brief.md: sem modo no cabeçalho"),
        ("brief de outro vídeo", (f"{ANIM}/E04/brief.md", BRIEF_E04.replace("**Vídeo:** 2026-10-30-com-status",
                                                                            "**Vídeo:** 2026-10-31-sem-status")),
         "o brief diz Vídeo 2026-10-31-sem-status, a pasta é 2026-10-30-com-status"),
    ]
    for nome, par, trecho in avisos:
        rc, out, _ = _seco(par)
        ok(f"{nome}: exit 0 e um ⚠ que diz o quê", rc == 0 and any("⚠" in ln and trecho in ln for ln in out), out)
    rc, out, _ = sincronizar("--seco", db=PORTA_MORTA)
    ok("de volta à raiz de exemplo: nenhum aviso", rc == 0 and len(out) == 1 and contagens(out[-1]) == ESPERADO, out)


def _acervo(con) -> dict[str, list[dict]]:
    return {t: linhas(con, f"select * from {t} order by 1, 2") for t in
            ("looks", "capa_estilos", "capa_estilos_exemplos", "legenda_estilos", "fontes", "sistema_ferramentas",
             "modelos_descricao", "animacoes", "sistema_contagens")}


def _passar(*pares) -> dict[str, list[dict]]:
    with trocado(*pares):
        rc, out, err = sincronizar(db=BANCO_TESTE)
    if rc != 0:
        ok("passagem do caso", False, f"rc={rc} {out} {err[-300:]}")
    with psycopg.connect(BANCO_TESTE) as con:
        return _acervo(con)


def _por(ls: list[dict], chave: str = "id") -> dict:
    return {r[chave]: r for r in ls}


def casos_acervo() -> None:
    print("\n== Biblioteca nova: looks (luts/*.json + cor.md) ==")
    sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    esp = PL.esperadas(ROOT)
    a = _passar()
    lk = _por(a["looks"])
    col = ("ordem", "tipo", "nome", "papel", "chaves_cor_md", "linhas_cor_md", "aprovada", "aprovada_em", "criado_em",
           "arquivo_json", "cube", "cube_sha256")
    L = "00-marca/cor/luts/"
    igual("um cartão por vlog (a amostra), rec709 (entrada-camera) e korvu-look-vN.json do topo, pela versão; "
          "_descartadas/ e korvu-look-v5-copia.json fora; papel (versao_ativa → em_uso, alternativa_medida → alternativa, "
          "arquivados: [v4] → arquivado) e nº da linha das chaves do cor.md, cada uma exatamente "
          "\"vN\"; data como está escrita",
          {k: tuple(r[c] for c in col) for k, r in lk.items()},
          {"vlog": (0, "referencia", "Original da câmera", None, [], [], None, None, None, None, None, None),
           "rec709": (1, "base", "entrada-camera", None, [], [], None, None, dt.date(2026, 9, 15),
                      L + "entrada-camera.json", L + "entrada-camera.cube", sha(CUBE_ENTRADA)),
           "v4": (2, "look", "Look v4", "arquivado", ["arquivados"], [7], False, None, dt.date(2026, 9, 15),
                  L + "korvu-look-v4.json", L + "korvu-look-v4.cube", sha(CUBE_V4)),
           "v5": (3, "look", "Look v5 · WAY", "em_uso", ["versao_ativa"], [5], True, dt.date(2026, 9, 18),
                  dt.date(2026, 9, 15),
                  L + "korvu-look-v5.json", L + "korvu-look-v5.cube", sha(CUBE_V5)),
           "v11": (4, "look", "v5 + pele", "alternativa", ["alternativa_medida"], [6], False, dt.date(2026, 9, 17),
                   dt.date(2026, 9, 17), L + "korvu-look-v11.json", L + "korvu-look-v11.cube", sha(CUBE_V11))})
    igual("ficha = o .json inteiro (com o nome dele, \"WAY v5\": o nome: do yaml vence só na coluna nome)",
          lk.get("v5", {}).get("ficha"), JSON_V5)
    igual("nome: o do yaml quando existe (vlog, v4, v5); sem ele, o do .json (rec709 = entrada-camera, v11 = v5 + pele); "
          "descricao = o desc: do yaml, à letra (aspas curvas inclusive); sem desc = NULL",
          {k: (r["nome"], r["descricao"]) for k, r in lk.items()},
          {"vlog": ("Original da câmera", "Como a câmera grava: plano."), "rec709": ("entrada-camera", "Só a conversão."),
           "v4": ("Look v4", "O look “Tenet”, frio."), "v5": ("Look v5 · WAY", "O escolhido: “a pele”."),
           "v11": ("v5 + pele", None)})
    igual("rosto em IRE = o item do look na seção looks do biblioteca.yaml (o número exato, 23.2 e 40.9; medido_em "
          "sem aspas = date, com aspas = texto ISO; sem amostra = NULL); o v4 não tem item: NULL",
          {k: (r["rosto_ire"], r["rosto_ire_em"], r["rosto_ire_amostra"]) for k, r in lk.items()},
          {"vlog": (None, None, None), "rec709": (None, None, None),
           "v4": (None, None, None), "v5": (Decimal("23.2"), dt.date(2026, 9, 18), "chatgpt02.MOV (regravação)"),
           "v11": (Decimal("40.9"), dt.date(2026, 9, 18), None)})
    igual("prévia: o caminho só quando o arquivo com o nome ESPERADO existe (o v4-0000….jpg antigo não conta)",
          {k: (r["previa"], r["previa_esperada"]) for k, r in lk.items()},
          {k: (f"{PL.SAIDA}/{esp[k]['nome']}" if k == "v5" else None, f"{PL.SAIDA}/{esp[k]['nome']}")
           for k in ("vlog", "rec709", "v4", "v5", "v11")})

    nome_v4 = f"{PL.SAIDA}/{esp['v4']['nome']}"
    lk = _por(_passar((nome_v4, b"jpeg do v4"))["looks"])
    igual("o gerador fez a prévia do v4: na passagem seguinte, previa = o caminho", lk["v4"]["previa"], nome_v4)
    lk = _por(_passar(("painel/biblioteca.yaml", ACERVO_YAML_TESTE.replace('  - id: v5\n    nome: Look v5 · WAY\n    desc: "O escolhido: “a pele”."\n    rosto_ire: 23.2\n    medido_em: 2026-09-18\n    amostra: "chatgpt02.MOV (regravação)"\n    fonte: 00-marca/cor/cor.md:41\n', "", 1)))["looks"])
    igual("sem o item do v5 no yaml: nome = o do .json, sem frase e sem rosto — a tabela do cor.md (que diz \"rosto "
          "23,2 IRE\") não é mais lida",
          (lk["v5"]["nome"], lk["v5"]["descricao"], lk["v5"]["rosto_ire"], lk["v5"]["rosto_ire_em"], lk["v11"]["rosto_ire"]),
          ("WAY v5", None, None, None, Decimal("40.9")))
    lk = _por(_passar(("painel/biblioteca.yaml", None))["looks"])
    igual("sem o biblioteca.yaml: os looks ficam (vêm de luts/ e do cor.md), sem rosto",
          sorted((k, r["papel"], r["rosto_ire"]) for k, r in lk.items()),
          [("rec709", None, None), ("v11", "alternativa", None), ("v4", "arquivado", None), ("v5", "em_uso", None),
           ("vlog", None, None)])
    lk = _por(_passar(("00-marca/cor/cor.md", COR_MD_TESTE.replace("alternativa_medida: v11 ",
                                                                   "alternativa_medida: v11 (WAY) ", 1)))["looks"])
    igual("\"alternativa_medida: v11 (WAY)\" não é exatamente vN: o v11 fica sem papel; o v4 continua arquivado",
          (lk["v11"]["papel"], lk["v11"]["chaves_cor_md"], lk["v4"]["papel"]), (None, [], "arquivado"))
    lk = _por(_passar(("00-marca/cor/cor.md", COR_MD_TESTE.replace("alternativa_medida: v11 ", "alternativa_medida: v4 ",
                                                                   1)))["looks"])
    igual("o v4 em alternativa_medida E em arquivados: conflito — as duas chaves, as duas linhas e papel NULL",
          (lk["v4"]["chaves_cor_md"], lk["v4"]["linhas_cor_md"], lk["v4"]["papel"]),
          (["alternativa_medida", "arquivados"], [6, 7], None))
    lk = _por(_passar(("00-marca/cor/cor.md", COR_MD_TESTE.replace("arquivados: [v4] ", "arquivados: [v4, v5] ", 1)))
              ["looks"])
    igual("o v5 ativo E arquivado: papel NULL, nenhum look em uso (a tela não mostra estado inventado)",
          (lk["v5"]["papel"], lk["v5"]["chaves_cor_md"], lk["v5"]["linhas_cor_md"],
           [k for k, r in lk.items() if r["papel"] == "em_uso"]), (None, ["versao_ativa", "arquivados"], [5, 7], []))
    lk = _por(_passar(("00-marca/cor/cor.md", COR_MD_TESTE.replace("arquivados: [v4] ", "alternativa: v4 ", 1)))
              ["looks"])
    igual("só a chave aposentada (alternativa: v4, sem arquivados): não é lida — o v4 fica sem papel",
          (lk["v4"]["papel"], lk["v4"]["chaves_cor_md"]), (None, []))
    lk = _por(_passar(("00-marca/cor/cor.md", COR_MD_TESTE.replace(
        'arquivados: [v4]                # look "Tenet" (24/10: arquivado; antes era alternativa: v4)',
        'arquivados:                     # look "Tenet"\n  - v4\n  - v4',
        1)))["looks"])
    igual("arquivados em lista de linhas: a linha do item; repetido conta uma vez",
          (lk["v4"]["papel"], lk["v4"]["chaves_cor_md"], lk["v4"]["linhas_cor_md"]), ("arquivado", ["arquivados"], [8]))
    lk = _por(_passar(("00-marca/cor/cor.md", None))["looks"])
    igual("cor.md ausente: os 5 cartões, sem papel; o rosto continua (vem do yaml)",
          sorted((k, r["papel"], r["rosto_ire"]) for k, r in lk.items()),
          sorted([("vlog", None, None), ("rec709", None, None), ("v4", None, None), ("v5", None, Decimal("23.2")),
                  ("v11", None, Decimal("40.9"))]))
    lk = _por(_passar(("00-marca/cor/luts/korvu-look-v11.cube", None))["looks"])
    igual("look sem .cube: cube, hash e prévia NULL", (lk["v11"]["cube"], lk["v11"]["cube_sha256"],
                                                       lk["v11"]["previa_esperada"]), (None, None, None))
    lk = _por(_passar((PL.AMOSTRA, None))["looks"])
    igual("sem a amostra: sem o cartão vlog e nenhuma prévia esperada",
          sorted((k, r["previa_esperada"]) for k, r in lk.items()),
          [("rec709", None), ("v11", None), ("v4", None), ("v5", None)])
    lk = _por(_passar(("00-marca/cor/luts/entrada-camera.cube", None))["looks"])
    igual("sem entrada-camera.cube: sem o cartão rec709; os looks ficam, sem prévia (a receita aplica a entrada antes)",
          sorted((k, r["previa_esperada"] is None) for k, r in lk.items()),
          [("v11", True), ("v4", True), ("v5", True), ("vlog", False)])

    print("\n== Biblioteca nova: capas, legendas, fontes e ferramentas (painel/biblioteca.yaml) ==")
    a = _passar()
    igual("capa_estilos: um por item de capas:, na ordem; texto sem espaços nas pontas; ficha_existe pelo disco",
          [tuple(r[c] for c in ("id", "ordem", "nome", "descricao", "ficha", "ficha_existe", "em_uso"))
           for r in a["capa_estilos"]],
          [("serifa-e-rabisco", 0, "Serifa + rabisco", "Palavra em serifa.", "00-marca/fichas/capa-serifa.md", True,
            False), ("sublinhado", 1, "Sublinhado", "Rabisco na última palavra.", None, None, True)])
    igual("exemplos: <pasta>/<slug>/capa/capa.png na 1.ª de 07-publicados, 06-publicar, 05-render-pronto que a tem "
          "(o com-status não tem capa no 06: vale o 05); video_slug = o vídeo de origem do pacote (o selado → o selo)",
          [tuple(r[c] for c in ("estilo_id", "ordem", "slug", "pasta", "caminho", "video_slug"))
           for r in a["capa_estilos_exemplos"]],
          [("serifa-e-rabisco", 0, "2026-09-17-demis", "07-publicados", "07-publicados/2026-09-17-demis/capa/capa.png",
            "2026-09-17-demis"),
           ("sublinhado", 0, "2026-11-02-selado", "06-publicar", "06-publicar/2026-11-02-selado/capa/capa.png",
            "2026-11-01-fora-do-tracker"),
           ("sublinhado", 1, "2026-10-30-com-status", "05-render-pronto",
            "05-render-pronto/2026-10-30-com-status/capa/capa.png", "2026-10-30-com-status")])
    ex = _passar(("07-publicados/2026-11-02-selado/capa/capa.png", b"publicada"))["capa_estilos_exemplos"]
    igual("o mesmo slug em 07-publicados e 06-publicar: vale o 07 (publicado)",
          [(r["slug"], r["pasta"]) for r in ex if r["estilo_id"] == "sublinhado"],
          [("2026-11-02-selado", "07-publicados"), ("2026-10-30-com-status", "05-render-pronto")])
    shutil.rmtree(ROOT / "07-publicados" / "2026-11-02-selado", ignore_errors=True)
    ex = _passar(("06-publicar/2026-10-30-com-status/capa/capa.png", b"na fila"))["capa_estilos_exemplos"]
    igual("o mesmo slug em 06-publicar e 05-render-pronto: vale o 06", [r["pasta"] for r in ex if r["ordem"] == 1],
          ["06-publicar"])
    shutil.rmtree(ROOT / "06-publicar" / "2026-10-30-com-status" / "capa", ignore_errors=True)
    ex = _passar(("07-publicados/2026-09-17-demis/capa/capa.png", None))["capa_estilos_exemplos"]
    igual("capa de exemplo que sumiu: pasta, caminho e vídeo NULL (a linha fica)",
          [(r["slug"], r["pasta"], r["caminho"], r["video_slug"]) for r in ex if r["estilo_id"] == "serifa-e-rabisco"],
          [("2026-09-17-demis", None, None, None)])
    igual("legenda_estilos", [tuple(r[c] for c in ("id", "ordem", "nome", "descricao", "ficha", "ficha_existe", "em_uso"))
                              for r in a["legenda_estilos"]],
          [("texto-selecionado", 0, "Texto Selecionado", "Seleção arrastada.", "00-marca/fichas/legenda.md", True, True)])
    igual("fontes: pesos em ordem; reserva ausente = false; confere_brand_ts = o brand.ts importa o pacote e chama o "
          "loadFont dele com o mesmo estilo (italico → \"italic\") e os mesmos pesos; sem pacote = NULL",
          sorted(tuple(r[c] for c in ("familia", "ordem", "remotion", "estilo", "pesos", "uso", "reserva",
                                      "confere_brand_ts")) for r in a["fontes"]),
          sorted([("Geist", 0, "Geist", "normal", [400, 700], "Legendas.", False, True),
                  ("Playfair Display", 1, "PlayfairDisplay", "italico", [400], "Capa.", False, True),
                  ("Inter Tight", 2, "InterTight", "normal", [800], "Reserva.", True, True),
                  ("Fonte do painel", 3, None, "normal", [500], "Só o painel.", False, None)]))
    f = _por(_passar(("painel/biblioteca.yaml", ACERVO_YAML_TESTE.replace("pesos: [800]", "pesos: [500, 800]")))
             ["fontes"], "familia")
    igual("pesos diferentes dos do brand.ts: confere_brand_ts = false", f["Inter Tight"]["confere_brand_ts"], False)
    f = _por(_passar(("painel/biblioteca.yaml", ACERVO_YAML_TESTE.replace("estilo: italico", "estilo: normal")))
             ["fontes"], "familia")
    igual("estilo diferente do brand.ts (normal × italic): false", f["Playfair Display"]["confere_brand_ts"], False)
    f = _por(_passar(("remotion/src/brand.ts", None))["fontes"], "familia")
    igual("sem brand.ts: não deu para conferir = NULL", f["Geist"]["confere_brand_ts"], None)
    igual("ferramentas: tipo e desc do yaml (desc → descricao, sem espaços nas pontas); a versão lida do arquivo "
          "(dependencies/devDependencies do package.json, a chave do .toml, a 1.ª linha não vazia); sem fonte = NULL",
          [tuple(r[c] for c in ("nome", "ordem", "tipo", "descricao", "versao", "versao_de")) for r in
           sorted(a["sistema_ferramentas"], key=lambda r: r["ordem"])],
          [("Remotion", 0, "Biblioteca de vídeo", "Monta o vídeo: legendas, títulos.", "4.0.1",
            "remotion/package.json#remotion"),
           ("TypeScript", 1, "Linguagem", "Tipos.", "5.9.3", "remotion/package.json#typescript"),
           ("Python", 2, "Linguagem", "Os scripts.", "3.12", ".python-version"),
           ("Postgres", 3, "Banco de dados", "Guarda os números.", "17", "painel/supabase/config.toml#db.major_version"),
           ("Claude Code", 4, "Agente de IA", "Onde a equipe trabalha.", None, None)])
    igual("modelos_descricao: a frase de cada modelo (desc → descricao), na ordem; com_preco = está na tabela de preços",
          [tuple(r[c] for c in ("modelo", "ordem", "descricao", "com_preco")) for r in
           sorted(a["modelos_descricao"], key=lambda r: r["ordem"])],
          [(OPUS, 0, "O mais forte.", True), (FABLE, 1, "Usado pelo Atlas: parte das sessões.", True)])
    md = _por(_passar(("painel/biblioteca.yaml", ACERVO_YAML_TESTE.replace("looks:\n", "  - modelo: claude-novo-9\n    desc: Novo.\nlooks:\n", 1)))
              ["modelos_descricao"], "modelo")
    igual("modelo fora da tabela de preços: a linha fica, com_preco = false", md["claude-novo-9"]["com_preco"], False)
    fr = _por(_passar(("remotion/package.json", "{"))["sistema_ferramentas"], "nome")
    igual("package.json quebrado: a versão fica NULL (o arquivo não é do Carlos: o painel não para)",
          (fr["Remotion"]["versao"], fr["Remotion"]["versao_de"]), (None, "remotion/package.json#remotion"))
    a0 = _passar(("painel/biblioteca.yaml", None))
    igual("biblioteca.yaml ausente: as tabelas dele vazias no banco (e os looks sem rosto, acima)",
          [len(a0[t]) for t in ("capa_estilos", "capa_estilos_exemplos", "legenda_estilos", "fontes",
                                "sistema_ferramentas", "modelos_descricao")], [0] * 6)

    print("\n== Biblioteca nova: animações e contagens ==")
    a = _passar()
    igual("animacoes: título e linhas do \"# Exx — título (L08 + L09)\" (aspas saem), vídeo, modo e duração do "
          "cabeçalho (antes do 1.º ---); renderizada = há .mp4 (edicao/extras/<Exx>.mp4, ou dentro de "
          "animacoes/<Exx>/; oculto não conta); a pasta _teste-x fica fora",
          [tuple(r[c] for c in ("id", "video_slug", "codigo", "titulo", "linhas", "modo", "duracao_s", "video_do_brief",
                                "renderizada", "mp4", "brief")) for r in a["animacoes"]],
          [("2026-10-30-com-status/E01", "2026-10-30-com-status", "E01", "A ligação de madrugada", ["L20"], "split",
            Decimal("6.76"), "2026-10-30-com-status", False, None, f"{ANIM}/E01/brief.md"),
           ("2026-10-30-com-status/E04", "2026-10-30-com-status", "E04", "Uma máquina que imita a mente",
            ["L08", "L09"], "full", Decimal("10.24"), "2026-10-30-com-status", True,
            "videos/2026-10-30-com-status/edicao/extras/E04.mp4", f"{ANIM}/E04/brief.md"),
           ("2026-10-30-com-status/E06", "2026-10-30-com-status", "E06", "2012: o sistema que reconheceu imagens", [],
            "card", Decimal("3"), "2026-10-30-com-status", True, f"{ANIM}/E06/export/E06.mp4", f"{ANIM}/E06/brief.md")])
    an = _por(_passar(("videos/2026-10-30-com-status/brutos/extras/E01-captura.mp4", b"captura"),
                      ("videos/2026-10-30-com-status/brutos/extras/E010-outra.mp4", b"outra"),
                      ("videos/2026-10-30-com-status/brutos/extras/E04.mp4", b"bruto do E04"))["animacoes"])
    igual("captura em brutos/extras/<Exx>-*.mp4 = renderizada (E010-… não é do E01); edicao/extras vem antes de "
          "brutos/extras", (an["2026-10-30-com-status/E01"]["mp4"], an["2026-10-30-com-status/E04"]["mp4"]),
          ("videos/2026-10-30-com-status/brutos/extras/E01-captura.mp4",
           "videos/2026-10-30-com-status/edicao/extras/E04.mp4"))
    with trocado((f"{ANIM}/E04/brief.md", BRIEF_E04.replace("**Vídeo:** 2026-10-30-com-status",
                                                            "**Vídeo:** 2026-10-31-sem-status"))):
        rc, out, err = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        an = _por(_acervo(con)["animacoes"]).get("2026-10-30-com-status/E04", {})
    igual("brief com outro Vídeo (copiado de outro vídeo): video_do_brief = o que o brief diz, video_slug = a pasta, e "
          "um ⚠ no log — a divergência fica na tabela",
          (rc, an.get("video_do_brief"), an.get("video_slug"),
           any("⚠" in ln and "o brief diz Vídeo 2026-10-31-sem-status, a pasta é 2026-10-30-com-status" in ln
               for ln in out)), (0, "2026-10-31-sem-status", "2026-10-30-com-status", True))
    an = _por(_passar(("videos/2026-10-30-com-status/brutos/extras/E010-outra.mp4", b"outra"))["animacoes"])
    igual("só um E010-….mp4 em brutos/extras: o E01 continua roteirizado", an["2026-10-30-com-status/E01"]["mp4"], None)
    an = _por(_passar(("videos/2026-10-30-com-status/edicao/extras/E04.mp4", b""))["animacoes"])
    igual(".mp4 vazio não conta", an["2026-10-30-com-status/E04"]["renderizada"], False)
    an = _por(_passar((f"{ANIM}/E01/brief.md", BRIEF_E01.replace("# E01 — A ligação de madrugada (L20)",
                                                                 "# E01 — Ligação (versão 2)")))["animacoes"])
    igual("parênteses que não são linhas (Lxx + Lyy) ficam no título; linhas vazias",
          (an["2026-10-30-com-status/E01"]["titulo"], an["2026-10-30-com-status/E01"]["linhas"]),
          ("Ligação (versão 2)", []))
    an = _por(_passar((f"{ANIM}/E01/brief.md", BRIEF_E01.replace("- **Modo:** `split` — animação deitada 16:9 na "
                                                                 "**metade de cima** do Reel\n", "")
                       .replace("· **duração 6,76 s**", "· duração 6,76 s")))["animacoes"])
    igual("modo e duração fora do cabeçalho ou do padrão: NULL (o \"- **Modo:** `full`\" e a \"duração 99,9 s\" depois "
          "do --- não contam)", (an["2026-10-30-com-status/E01"]["modo"], an["2026-10-30-com-status/E01"]["duracao_s"]),
          (None, None))
    igual("sistema_contagens: agentes = .md no topo de .claude/agents (o .txt não); habilidades = pastas com SKILL.md "
          "(capa-reels não tem; _velha e .oculta ficam fora); comandos = .md de .claude/commands (o notas.txt não)",
          [(r["agentes"], r["habilidades"], r["comandos"]) for r in a["sistema_contagens"]],
          [(len(list((ROOT / ".claude/agents").glob("[!._]*.md"))), 3, 2)])
    with psycopg.connect(BANCO_TESTE) as con:
        eq = {r["id"]: r["comandos"] for r in linhas(con, "select id, comandos from agentes")}
    igual("PD30: a Equipe segue a regra do Sistema — o diretor tem todos os comandos, sem _rascunho.md e .oculto.md "
          "(que citam o engenheiro-backend e o portao-dados e não entram na lista deles); o número é o do Sistema",
          (eq.get("diretor"), len(eq.get("diretor") or []), eq.get("engenheiro-backend"), eq.get("portao-dados")),
          (["fila", "status"], a["sistema_contagens"][0]["comandos"], ["fila"], ["status"]))
    ct = _passar((".claude/commands/_rascunho.md", "rascunho\n"), (".claude/agents/_rascunho.md", "rascunho\n"),
                 (".claude/commands/.oculto.md", "oculto\n"), (".claude/skills/sem-ficha/LEIA.md", "sem SKILL.md\n"))[
        "sistema_contagens"]
    igual("_rascunho.md em agents e commands, .oculto.md em commands e skill sem SKILL.md não contam",
          [(r["agentes"], r["habilidades"], r["comandos"]) for r in ct],
          [(r["agentes"], r["habilidades"], r["comandos"]) for r in a["sistema_contagens"]])
    shutil.rmtree(ROOT / ".claude/skills/sem-ficha", ignore_errors=True)

    print("\n== Biblioteca nova: armazenamento e sistema_modelos (views sobre o que o banco já tem) ==")
    manifesto = {"arquivado_em": "2026-10-24T22:00:00+01:00", "destino": {"volume": "KORVU V01"}, "arquivos": [
        {"nome": "PRAQ0001.MOV", "bytes": 1000, "sha256": "0" * 64, "mtime": "2026-10-20T10:00:00+00:00",
         "ctime": "2026-10-21T10:00:00+00:00"}]}
    outro = {"arquivado_em": "2026-10-20T08:30:00-03:00", "destino": {"volume": "KORVU V02", "formato": "exFAT"},
             "arquivos": [{"nome": "PRAQ0099.MOV", "bytes": 500, "sha256": "a" * 64,
                           "mtime": "2026-10-19T10:00:00+00:00", "ctime": "2026-10-19T11:00:00+00:00"}]}
    sem_data = {"arquivos": manifesto["arquivos"]}
    # manifesto de um vídeo cujo original está de volta no Mac (o PRAQ0001.MOV está no disco): nota por vídeo, mas fora
    # da data do HD da armazenamento (que é dos vídeos com original no HD)
    de_volta = {"arquivado_em": "2026-10-26T10:00:00+00:00", "destino": {"volume": "KORVU V03"},
                "arquivos": [{"nome": "PRAQ0001.MOV", "bytes": 9, "sha256": "b" * 64,
                              "mtime": "2024-07-15T00:00:00+00:00", "ctime": "2026-10-01T00:00:00+00:00"}]}
    hd_volta = "videos/2026-11-01-fora-do-tracker/brutos/principal/ARQUIVADO.json"
    hd_sem, hd_com = ("videos/2026-10-31-sem-status/brutos/principal/ARQUIVADO.json",
                      "videos/2026-10-30-com-status/brutos/principal/ARQUIVADO.json")
    for caso, pares, hd_esperado in (
            ("sem nada no HD", (), (0, None)),
            ("dois vídeos com o original no HD (e um com o original de volta no Mac)",
             ((hd_sem, manifesto), (hd_com, outro), (hd_volta, de_volta)),
             (1500, ["2026-10-30-com-status", "2026-10-31-sem-status"])),
            ("manifesto sem arquivado_em nem destino", ((hd_sem, sem_data),), (1000, ["2026-10-31-sem-status"]))):
        with trocado(*pares):
            rc, out, err = sincronizar(db=BANCO_TESTE)
        with psycopg.connect(BANCO_TESTE) as con:
            ar = linhas(con, "select * from armazenamento")
            d = linhas(con, "select sum(gravacao_bytes_no_mac)::bigint mac, sum(gravacao_arquivos_no_mac)::int mac_n, "
                            "sum(gravacao_arquivados_bytes)::bigint hd, sum(gravacao_arquivados)::int hd_n, "
                            "array_agg(slug order by slug) filter (where gravacao_arquivados > 0) hd_v from videos")[0]
            m = linhas(con, "select coalesce(sum(bytes), 0)::bigint b, count(*)::int n from biblioteca_arquivos")[0]
            em = con.execute("select max(em) from sincronizacoes").fetchone()[0]
        ok(f"armazenamento ({caso}): uma linha", rc == 0 and len(ar) == 1, f"rc={rc} {ar} {out}")
        r = ar[0] if ar else {}
        igual(f"armazenamento ({caso}) = videos.gravacao_*_no_mac, a soma de biblioteca_arquivos e "
              "videos.gravacao_arquivados_*; mac_bytes = gravações + material; hd_videos = os vídeos com original no "
              "HD; lido_em = a última passagem",
              tuple(r.get(c) for c in ("gravacoes_mac_bytes", "gravacoes_mac_arquivos", "material_mac_bytes",
                                       "material_mac_arquivos", "mac_bytes", "hd_bytes", "hd_arquivos", "hd_videos",
                                       "lido_em")),
              (d["mac"], d["mac_n"], m["b"], m["n"], d["mac"] + m["b"], d["hd"], d["hd_n"], d["hd_v"] or [], em))
        ok(f"armazenamento ({caso}): o caso não passa no vazio", d["mac"] > 0 and m["b"] > 0
           and (d["hd"], d["hd_v"]) == hd_esperado, (d, m))
        igual(f"armazenamento ({caso}): sem as colunas da nota do HD (decisão de 25/10)",
              sorted(c for c in r if c in ("hd_arquivado_em", "hd_todos_conferidos")), [])
    with psycopg.connect(BANCO_TESTE) as con:
        igual("videos sem as colunas da nota do HD (hd_arquivado_em, hd_volume, hd_conferido saíram em 25/10)",
              [r[0] for r in con.execute("select column_name from information_schema.columns where table_schema = "
                                         "'public' and table_name = 'videos' and column_name like 'hd%' order by 1")], [])
    with psycopg.connect(BANCO_TESTE) as con:
        con.execute("select set_config('painel.hoje', '2026-10-24', false)")
        sm = {r["modelo"]: r for r in linhas(con, "select * from sistema_modelos")}
        direto = {r["modelo"]: r for r in linhas(con, """
            select modelo, sum(tokens)::bigint tokens, sum(usd) usd, count(distinct arquivo)::int execucoes,
                   count(distinct membro_id)::int agentes
            from consumo where dia between date '2026-10-24' - 29 and date '2026-10-24' group by modelo""")}
    igual("sistema_modelos (janela até 24/10) = o consumo da janela por modelo (os números de Tokens): tokens, US$, "
          "execuções e agentes",
          {k: (v["tokens"], v["usd"], v["execucoes"], v["agentes"]) for k, v in sm.items()},
          {k: (v["tokens"], v["usd"], v["execucoes"], v["agentes"]) for k, v in direto.items()})
    igual("sistema_modelos.descricao = a frase do biblioteca.yaml (o Sonnet não tem: NULL)",
          {k: v["descricao"] for k, v in sm.items()},
          {OPUS: "O mais forte.", SONNET: None, FABLE: "Usado pelo Atlas: parte das sessões."})
    total = sum(v["tokens"] for v in direto.values())
    ok("pct_tokens = % do total da janela (somam 100), não 100 por modelo",
       total > 0 and all(abs(v["pct_tokens"] - Decimal(100 * v["tokens"]) / total) < Decimal("1e-12")
                         for v in sm.values()) and len(sm) > 1, {k: v["pct_tokens"] for k, v in sm.items()})
    with psycopg.connect(BANCO_TESTE) as con:
        con.execute("select set_config('painel.hoje', '2026-11-11', false)")  # o engenheiro-backend sem consumo
        sm = {r["modelo"]: r["tokens"] for r in linhas(con, "select * from sistema_modelos")}
        direto = {r["modelo"]: r["tokens"] for r in linhas(con, """
            select modelo, sum(tokens)::bigint tokens from consumo
            where dia between date '2026-11-11' - 29 and date '2026-11-11' group by modelo""")}
        sem = linhas(con, "select count(*)::int n from modelo_por_agente where modelo is null")[0]["n"]
    ok("janela com agente sem consumo (linha de modelo NULL na modelo_por_agente): ela não vira modelo",
       sem > 0 and sm == direto and None not in sm, (sem, sm, direto))
    rc, out, err = sincronizar(db=BANCO_TESTE)
    ok("de volta à raiz de exemplo", rc == 0 and out and contagens(out[-1]) == ESPERADO and len(out) == 1,
       f"rc={rc} {out}")


def casos_crescimento() -> None:
    print("\n== a Biblioteca cresce só por arquivo: um look, um estilo de capa e uma animação novos, sem código ==")
    codigo = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (SYNC, SYNC.parent / "previas_looks.py", *MIGRACOES)}
    yaml_novo = ACERVO_YAML_TESTE.replace("legendas:\n", "  - id: letra-gigante\n    nome: Letra gigante\n"
                                                         "    descricao: Uma palavra só, enorme.\n    ficha: null\n"
                                                         "    em_uso: false\n    exemplos: [2026-09-17-demis]\n"
                                                         "legendas:\n", 1)
    brief = ("# E07 — A cena nova (L30)\n\n- **Vídeo:** 2026-10-30-com-status\n- **Modo:** `full`\n"
             "- **Linha:** L30 · **duração 4,5 s**\n")
    with trocado(("00-marca/cor/luts/korvu-look-v13.json", {"nome": "Look novo", "versao": "v13", "aprovada": False,
                                                            "criado_em": "2026-10-25"}),
                 ("00-marca/cor/luts/korvu-look-v13.cube", b"LUT_3D_SIZE 2\n# v13\n"),
                 ("painel/biblioteca.yaml", yaml_novo), (f"{ANIM}/E07/brief.md", brief)):
        esperada = f"{PL.SAIDA}/{PL.esperadas(ROOT)['v13']['nome']}"
        rc, out, err = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        a = _acervo(con)
    lk = _por(a["looks"])
    n = lk.get("v13", {})
    igual("look novo (.cube + .json): uma linha a mais, no fim pela versão, sem papel (o cor.md não o cita) e com a "
          "prévia esperada (o gerador a faz sozinho; até lá, previa NULL)",
          (rc, len(lk), n.get("ordem"), n.get("nome"), n.get("papel"), n.get("cube"), n.get("previa"),
           n.get("previa_esperada")),
          (0, 6, 5, "Look novo", None, "00-marca/cor/luts/korvu-look-v13.cube", None, esperada))
    ce, ex = _por(a["capa_estilos"]), [r for r in a["capa_estilos_exemplos"] if r["estilo_id"] == "letra-gigante"]
    igual("estilo de capa novo (uma entrada no yaml): uma linha a mais, com a capa de exemplo",
          (len(ce), ce.get("letra-gigante", {}).get("ordem"), [(r["slug"], r["pasta"]) for r in ex]),
          (3, 2, [("2026-09-17-demis", "07-publicados")]))
    an = _por(a["animacoes"]).get("2026-10-30-com-status/E07", {})
    igual("animação nova (um brief.md): uma linha a mais",
          (len(a["animacoes"]), an.get("titulo"), an.get("linhas"), an.get("modo"), an.get("duracao_s"),
           an.get("renderizada")), (4, "A cena nova", ["L30"], "full", Decimal("4.5"), False))
    igual("nenhum código nem migração mudou (o sincronizador, o gerador e as migrações são os mesmos)",
          {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
           for p in (SYNC, SYNC.parent / "previas_looks.py",
                     *sorted((CODIGO / "painel" / "supabase" / "migrations").glob("*.sql")))}, codigo)
    rc, out, err = sincronizar(db=BANCO_TESTE)
    ok("tirados os arquivos, as linhas saem (espelho)", rc == 0 and out and contagens(out[-1]) == ESPERADO,
       f"rc={rc} {out}")


def preparar_banco_de_teste() -> None:
    """Banco novo + os default privileges da plataforma no PIOR caso (tudo para os papéis da API, como o Supabase dá
    em alguns schemas) → as migrações, em ordem. O que sobrar de permissão depois disto é culpa das migrações."""
    for nome, url in ((NOME_TESTE, BANCO_TESTE), (NOME_SCRIPT, BANCO_SCRIPT)):
        with psycopg.connect(BANCO_REAL, autocommit=True, connect_timeout=5) as adm:
            adm.execute(f'create database "{nome}" template template0')
        with psycopg.connect(url, autocommit=True) as con:
            con.execute("""
                grant usage on schema public to anon, authenticated, service_role;
                alter default privileges for role postgres in schema public
                  grant all on tables to anon, authenticated, service_role;
                alter default privileges for role postgres in schema public
                  grant all on sequences to anon, authenticated, service_role;
                alter default privileges for role postgres in schema public
                  grant all on functions to anon, authenticated, service_role, public;""")
            for m in MIGRACOES:
                with con.transaction():
                    con.execute(m.read_text(encoding="utf-8"))


def casos_permissoes_do_zero() -> None:
    print("\n== permissões do zero (banco de teste, migrações sobre o pior caso da plataforma) ==")
    with psycopg.connect(BANCO_TESTE) as con:
        n = con.execute("select count(*) from pg_class where relnamespace = 'public'::regnamespace "
                        "and relkind = 'r'").fetchone()[0]
        igual("as migrações criam as 32 tabelas", n, 32)
        igual("todas com RLS", tabelas_sem_rls(con), [])
        vs = con.execute("select relname, coalesce(reloptions @> '{security_invoker=true}', false) from pg_class "
                         "where relnamespace = 'public'::regnamespace and relkind = 'v' order by 1").fetchall()
        igual("as 10 views, todas com security_invoker", vs,
              [("armazenamento", True), ("biblioteca_materiais_resumo", True), ("biblioteca_por_tipo", True),
               ("biblioteca_por_video", True), ("consumo", True), ("consumo_diario", True), ("execucoes_custo", True),
               ("modelo_por_agente", True), ("sistema_modelos", True), ("videos_producao", True)])
        v = violacoes_de_permissao(con)
        ok("anon/authenticated sem nenhum privilégio; service_role só SELECT (tabelas e views)", not v, v[:8])
        v = violacoes_de_default(con)
        ok("default privileges fechados (próximas tabelas/sequências/funções)", not v, v[:8])
        # uma "próxima migração" de mentira, desfeita no fim: o que ela criar herda só o que deve
        with con.transaction(force_rollback=True):
            con.execute("create table proxima (id bigint generated always as identity primary key);"
                        "create sequence proxima_seq;"
                        "create function proxima_fn() returns int language sql as 'select 1';")
            v = violacoes_de_permissao(con)
            ok("tabela, sequência e função criadas DEPOIS herdam nada (service_role só lê a tabela)", not v, v[:8])


def casos_mapeamento() -> None:
    print("\n== passagem real no banco de teste ==")
    antes, antes_home = foto(ROOT), foto(HOME)
    rc, out, err = sincronizar(db=BANCO_TESTE, outra_raiz=OUTRA)
    ok("exit 0, uma linha ✓", rc == 0 and len(out) == 1 and "✓ painel sincronizado" in out[0], f"{out} {err[-300:]}")
    igual("contagens da linha = arquivos de exemplo", contagens(out[-1]) if out else {}, ESPERADO)
    ok("a passagem real não escreve na raiz (nem o cache dos portões)", foto(ROOT) == antes)
    ok("a passagem real não escreve na pasta dos registros (nem na HOME)", foto(HOME) == antes_home)

    with psycopg.connect(BANCO_TESTE) as con:
        for t, n in ESPERADO.items():
            igual(f"banco: {t} = {n}", con.execute(f"select count(*) from {t}").fetchone()[0], n)

        print("\n== equipe: equipe.yaml + .claude/agents → departamentos/agentes ==")
        igual("departamentos na ordem do YAML, com nome, descrição e gerente (cada campo com valor próprio)",
              [tuple(r.values()) for r in linhas(con, "select id, nome, ordem, descricao, gerente_id from departamentos "
                                                      "order by ordem")],
              [("direcao", "direção", 0, "Organiza o pipeline.", "diretor"),
               ("tecnologia", "tecnologia", 1, "Constrói o painel.", "portao-dados")])
        ag = {r["id"]: r for r in linhas(con, "select * from agentes")}
        eb, pd, di = ag.get("engenheiro-backend", {}), ag.get("portao-dados", {}), ag.get("diretor", {})
        igual("agentes: nome, cargo, departamento, papel, resumo e personalidade do equipe.yaml (valores distintos)",
              {k: (r["nome"], r["cargo"], r["departamento_id"], r["papel"], r["resumo"], r["personalidade"])
               for k, r in ag.items()},
              {"diretor": ("Atlas", "diretor de operações", "direcao", "diretor", "O Claude principal.", "Calmo."),
               "portao-dados": ("Sérgio Lemos", "gerente · portão dos dados", "tecnologia", "portao", "Audita o banco.",
                                "Desconfiado."),
               "engenheiro-backend": ("Mateus Pacheco", "engenheiro back-end", "tecnologia", "construtor",
                                      "Banco e sincronizador.", None)})
        igual("skills_citadas: nome solto, skills/<nome>, plugin e global entre crases; remotion-* fora",
              eb.get("skills"), ["capa-reels", "design:design-critique", "supabase", "watch"])
        igual("skills_citadas: pedaço de caminho (painel/supabase/) e nome-com-sufixo não contam", pd.get("skills"), [])
        igual("comandos: o id do agente citado no comando (engenheiro-backend-x não conta)",
              (eb.get("comandos"), pd.get("comandos")), (["fila"], ["status"]))
        igual("diretor: todos os comandos, descrição e modelo padrão, sem arquivo",
              (di.get("comandos"), di.get("descricao"), di.get("modelo"), di.get("arquivo"), di.get("skills")),
              (["fila", "status"], "O Claude principal (esta conversa).", "opus", None, []))
        igual("frontmatter: descrição com ': ' no meio, ferramentas e modelo",
              (pd.get("descricao"), eb.get("ferramentas"), eb.get("modelo")),
              ("Portão dos dados: audita o banco.", ["Read", "Write", "Bash"], "opus"))
        igual("quem fiscaliza quem vem do portoes.PORTOES",
              (eb.get("fiscalizado_por"), pd.get("fiscaliza"), pd.get("fiscalizado_por")),
              ("portao-dados", ["engenheiro-backend"], None))
        igual("retrato: .jpg vence .png, só .png vale o .png, sem arquivo = NULL (iniciais); personalidade ausente = "
              "NULL; arquivo relativo",
              (pd.get("retrato"), di.get("retrato"), eb.get("retrato"), eb.get("personalidade"), eb.get("arquivo")),
              ("/equipe/portao-dados.jpg", "/equipe/diretor.png", None, None, ".claude/agents/engenheiro-backend.md"))

        print("\n== vídeos: tracker.md (por posição) + status.json ==")
        vd = {r["slug"]: r for r in linhas(con, "select * from videos")}
        cs, ss, ft = (vd.get("2026-10-30-com-status", {}), vd.get("2026-10-31-sem-status", {}),
                      vd.get("2026-11-01-fora-do-tracker", {}))
        igual("tracker: tema, pilar, estrutura e CTA (6.ª coluna, não o Hook)",
              (cs.get("tema"), cs.get("pilar"), cs.get("estrutura"), cs.get("cta")),
              ("Contexto antes de pedir", "tutoriais-rapidos", "narrativo", "PROMPT"))
        igual("status.json vence o tracker no estado e na data; histórico vira jsonb",
              (cs.get("estado"), cs.get("atualizado"), cs.get("historico")),
              ("edicao", "2026-10-29T18:00:00+00:00", HISTORICO))
        igual("sem status.json: estado (7.ª coluna) e atualizado (8.ª) do tracker",
              (ss.get("estado"), ss.get("atualizado"), ss.get("cta"), ss.get("historico")),
              ("gravacao", "2026-10-20 10:00", "AULA", []))
        igual("fora do tracker: tema NULL, estado do status.json", (ft.get("tema"), ft.get("estado")), (None, "roteiro"))
        ok("pasta com '_' (videos/_modelo) não entra", "_modelo" not in vd, sorted(vd))
        sr = vd.get("2026-11-04-sem-roteiro", {})
        igual("vídeo sem roteiro.md: entra, com o estado do status.json, sem gravação nem pacote",
              (sr.get("estado"), sr.get("tema"), sr.get("gravado"), sr.get("pronto")), ("roteiro", None, False, False))

        print("\n== fases: gravação (brutos/principal/), pronto (05-render-pronto/), trava e vídeo de origem ==")
        igual("gravado: 3 vídeos (.MOV, .mp4, subpasta); fora .DS_Store, ._, 0 byte e .txt; bytes e data mais recente",
              tuple(cs.get(k) for k in ("gravado", "gravacao_arquivos", "gravacao_bytes", "gravacao_ultima",
                                        "gravacao_data_suspeita")),
              (True, 3, 157, dt.datetime.fromtimestamp(1_792_500_000, dt.timezone.utc), False))
        agora = dt.datetime.now(dt.timezone.utc)
        ok("gravacao_chegou = ctime mais recente (escrito agora pelo teste), não a data do arquivo",
           cs.get("gravacao_chegou") and agora - dt.timedelta(minutes=30) < cs["gravacao_chegou"] <= agora,
           cs.get("gravacao_chegou"))
        igual("pasta brutos/principal/ só com .DS_Store: não gravado, sem datas",
              (ss.get("gravado"), ss.get("gravacao_arquivos"), ss.get("gravacao_ultima"), ss.get("gravacao_chegou"),
               ss.get("gravacao_data_suspeita")), (False, 0, None, None, False))
        igual("arquivo com o relógio da câmera em 2024 num vídeo de 01/11/2026: gravado, data marcada como suspeita",
              (ft.get("gravado"), ft.get("gravacao_ultima"), ft.get("gravacao_data_suspeita")),
              (True, dt.datetime.fromtimestamp(1_721_000_000, dt.timezone.utc), True))
        igual("pronto: 05-render-pronto com qa PASS (também 'pass' numa pasta -v2 do vídeo); qa FAIL não",
              (cs.get("pronto"), ss.get("pronto"), ft.get("pronto")), (True, False, True))
        igual("nao_publicar: _controle/nao-publicar.json, com o vídeo de origem de cada slug",
              sorted((r["slug"], r["video_slug"], r["motivo"], r["desde"].isoformat())
                     for r in linhas(con, "select * from nao_publicar")),
              [("2026-10-30-com-status", "2026-10-30-com-status", "teste de cor, não publicar", "2026-09-19"),
               ("2026-11-01-fora-do-tracker-v2", "2026-11-01-fora-do-tracker", "variante de teste", "2026-10-23")])
        igual("fila e publicações com o vídeo de origem (selo → origem; sem selo → o vídeo-prefixo ou o próprio slug)",
              (dict(con.execute("select slug, video_slug from fila").fetchall()),
               dict(con.execute("select slug, video_slug from publicacoes").fetchall())),
              ({"2026-10-28-legado": "2026-10-28-legado", "2026-10-30-com-status": "2026-10-30-com-status",
                "2026-11-02-selado": "2026-11-01-fora-do-tracker",
                "2026-11-03-legado-selado": "2026-10-30-com-status"},
               {"2026-09-17-demis": "2026-09-17-demis", "2026-10-20-fei-fei": "2026-10-20-fei-fei",
                "2026-10-20-hinton": "2026-10-20-hinton", "2026-10-30-com-status-a": "2026-10-30-com-status",
                "2026-10-31-sem-status-b": "2026-10-31-sem-status"}))

        print("\n== portões: vídeos ×4, pastas da fila ×1, painel ×3 ==")
        pe = {(r["alvo"], r["portao"]): r for r in linhas(con, "select * from portoes_estado")}
        alvos = {}
        for alvo, portao in pe:
            alvos.setdefault(alvo, set()).add(portao)
        quatro = {"pauta", "roteiro", "imagem", "corte"}
        video_alvos = ("videos/2026-10-30-com-status", "videos/2026-10-31-sem-status",
                       "videos/2026-11-01-fora-do-tracker", "videos/2026-11-04-sem-roteiro")
        igual("cada vídeo tem os 4 portões do pacote", {a: alvos.get(a) for a in video_alvos},
              {a: quatro for a in video_alvos})
        igual("vídeo só com status.json: os 4 portões não se aplicam (não há arquivo de área nenhuma)",
              {k[1]: r["status"] for k, r in pe.items() if k[0] == "videos/2026-11-04-sem-roteiro"},
              {p_: "nao_se_aplica" for p_ in quatro})
        fila_alvos = ("06-publicar/2026-10-28-legado", "06-publicar/2026-10-29-sem-post",
                      "06-publicar/2026-10-30-com-status", "06-publicar/2026-11-02-selado",
                      "06-publicar/2026-11-03-legado-selado")
        igual("cada PASTA de 06-publicar/ tem o portão da publicação (também a sem post.json)",
              {a: alvos.get(a) for a in fila_alvos}, {a: {"publicacao"} for a in fila_alvos})
        igual("o painel tem os 3 portões do sistema", alvos.get("painel"), {"design", "interface", "dados"})
        ok("nenhum alvo a mais", set(alvos) == {*video_alvos, *fila_alvos, "painel"}, sorted(alvos))
        p = {k[1]: pe.get(("painel", k[1]), {}) for k in pe if k[0] == "painel"}
        igual("painel: design sem arquivos = nao_se_aplica · interface aprovado · dados vencido",
              {k: (v.get("status"), v.get("agente"), v.get("slug")) for k, v in p.items()},
              {"design": ("nao_se_aplica", "portao-interface", "painel"),
               "interface": ("aprovado", "portao-interface", "painel"),
               "dados": ("vencido", "portao-dados", "painel")})
        ok("painel/dados vencido diz qual arquivo mudou (motivos jsonb)",
           any("supabase/migrations/0001_x.sql" in m for m in (p.get("dados", {}).get("motivos") or [])),
           p.get("dados", {}).get("motivos"))
        im = pe.get(("videos/2026-10-30-com-status", "imagem"), {})
        igual("vídeo: imagem BLOQUEADA, volta 1, agente portao-imagem",
              (im.get("status"), im.get("volta"), im.get("agente")), ("bloqueado", 1, "portao-imagem"))
        igual("vídeo: roteiro com arquivo e sem veredicto = pendente; pauta sem arquivo = nao_se_aplica",
              (pe.get(("videos/2026-10-30-com-status", "roteiro"), {}).get("status"),
               pe.get(("videos/2026-10-30-com-status", "pauta"), {}).get("status")), ("pendente", "nao_se_aplica"))
        livro = json.loads((ROOT / "videos" / "2026-10-30-com-status" / "portoes.json").read_text(encoding="utf-8"))
        vi = livro["veredictos"][0]
        vr = linhas(con, "select * from veredictos where alvo = 'videos/2026-10-30-com-status'")
        igual("veredicto: portoes.json → linha (resultado, S0/S1/S2, impressão, em, relatório)",
              [(r["portao"], r["resultado"], r["s0"], r["s1"], r["s2"], r["impressao"], r["em"], r["relatorio"],
                r["volta"]) for r in vr],
              [("imagem", "BLOQUEADO", 1, 0, 0, vi["impressao"], ts(vi["em"]), vi["relatorio"], 1)])
        igual("veredicto com nota e decisão do Carlos: portão, agente (≠ portão), resultado, volta, nota, decisão",
              [(r["portao"], r["agente"], r["resultado"], r["volta"], r["s0"], r["s2"], r["nota"], r["decisao_carlos"])
               for r in linhas(con, "select * from veredictos where alvo = 'videos/2026-10-31-sem-status' order by ordem")],
              [("roteiro", "revisor-de-roteiro", "BLOQUEADO", 1, 1, 0, None, None),
               ("roteiro", "revisor-de-roteiro", "BLOQUEADO", 2, 1, 0, None, None),
               ("roteiro", "revisor-de-roteiro", "ESCALADO", 3, 1, 0, None, None),
               ("roteiro", "revisor-de-roteiro", "APROVADO", 1, 0, 2, NOTA, DECISAO)])
        igual("PD20: 4 veredictos do mesmo portão no MESMO segundo entram, com a ordem do livro (0–3)",
              [(r["ordem"], r["em"]) for r in linhas(
                  con, "select ordem, em from veredictos where alvo = 'videos/2026-10-31-sem-status' order by ordem")],
              [(i, ts("2026-10-31T10:00:00+00:00")) for i in range(4)])
        igual("veredictos do painel (interface e dados)",
              sorted(r["portao"] for r in linhas(con, "select portao from veredictos where alvo = 'painel'")),
              ["dados", "interface"])

        print("\n== fila: 06-publicar/*/post.json + legado ==")
        fl = {r["slug"]: r for r in linhas(con, "select * from fila")}
        a, b = fl.get("2026-10-30-com-status", {}), fl.get("2026-10-28-legado", {})
        igual("post.json → linha (publicar_em com fuso, plataformas, estado, palavra, confirmar)",
              (a.get("publicar_em"), a.get("plataformas"), a.get("estado"), a.get("palavra"), a.get("confirmar")),
              (ts("2026-10-30T21:00:00+00:00"), ["instagram", "facebook"], "agendado", "PROMPT", True))
        igual("trial: instagram.trial.graduation_strategy; sem trial = NULL", (a.get("trial"), b.get("trial")),
              ("MANUAL", None))
        igual("legado: slug em _controle/gauntlet-legado.json (lido na MESMA raiz, apesar do CONTENT_AI_ROOT)",
              (a.get("legado"), b.get("legado")), (False, True))
        ok("pasta sem post.json fica fora da fila", "2026-10-29-sem-post" not in fl, sorted(fl))

        print("\n== fila: origem, selo e a conferência do GAUNTLET (PI39; o que o publicar.py confere) ==")
        def caso(slug):
            r = fl.get(slug, {})
            return r.get("legado"), r.get("selado"), r.get("origem"), r.get("erros_gauntlet")
        igual("legado SEM selo: dispensado — nada exigido (erros [])", caso("2026-10-28-legado"),
              (True, False, None, []))
        igual("selado normal, origem e publicação aprovadas, arquivos os que os portões viram: pode sair (erros [])",
              caso("2026-11-02-selado"), (False, True, "videos/2026-11-01-fora-do-tracker", []))
        leg, selado, origem, erros = caso("2026-10-30-com-status")
        ok("SEM selo e FORA da lista: recusado (não vira legado)",
           (leg, selado, origem) == (False, False, None) and len(erros or []) == 1
           and "pacote sem selo GAUNTLET" in erros[0], (leg, selado, origem, erros))
        leg, selado, origem, erros = caso("2026-11-03-legado-selado")
        ok("legado COM selo: regra normal — os portões da origem e o da publicação aparecem nos erros",
           (leg, selado, origem) == (True, True, "videos/2026-10-30-com-status")
           and any(e.startswith("origem videos/2026-10-30-com-status: portão imagem (portao-imagem) BLOQUEADO")
                   for e in erros or [])
           and any(e.startswith("portão publicacao (portao-publicacao) PENDENTE") for e in erros or []), erros)
        po = {r["alvo"] for r in linhas(con, "select alvo from portoes_estado")}
        ok("portoes_estado tem o alvo da origem e o 06-publicar/<slug> de cada post selado",
           all(fl[s]["origem"] in po and f"06-publicar/{s}" in po for s in fl if fl[s].get("selado")), sorted(po))

        print("\n== desempenho: 07-publicados/*/metricas.json ==")
        pb = {r["slug"]: r for r in linhas(con, "select * from publicacoes")}
        igual("trial: post.json vence o metricas.json (Hinton MANUAL × SS_PERFORMANCE) · só metricas, texto e objeto · "
              "só post.json, com valor e sem trial",
              tuple(pb.get(k, {}).get("trial") for k in ("2026-10-20-hinton", "2026-09-17-demis", "2026-10-20-fei-fei",
                                                        "2026-10-30-com-status-a", "2026-10-31-sem-status-b")),
              ("MANUAL", "MANUAL", "SS_PERFORMANCE", "SS_PERFORMANCE", None))
        h = pb.get("2026-10-20-hinton", {})
        igual("publicação com post.json, metricas.json e pacote.json DIFERENTES: o post.json vence o metricas.json "
              "(publicado_em, palavra, permalinks, plataformas, estado); o pacote.json vence em duração, tema e pilar",
              (h.get("publicado_em"), h.get("palavra"), h.get("permalink_instagram"), h.get("permalink_facebook"),
               h.get("plataformas"), h.get("estado"), h.get("duracao_s"), h.get("tema"), h.get("pilar")),
              (ts("2026-10-15T11:50:00+01:00"), "NOBELPOST", "https://www.instagram.com/reel/X/", "https://fb/reel/POST/",
               ["instagram", "facebook"], "publicado", Decimal("158.7"), "Tema do pacote Hinton", "perfil-pacote"))
        a = pb.get("2026-10-30-com-status-a", {})
        igual("publicada SEM metricas.json entra pelo post.json (+ tema, pilar e duração do pacote.json, vídeo de origem)",
              tuple(a.get(k) for k in ("publicado_em", "plataformas", "estado", "permalink_instagram",
                                       "permalink_facebook", "palavra", "trial", "duracao_s", "tema", "pilar",
                                       "video_slug")),
              (ts("2026-10-22T21:19:22+01:00"), ["instagram", "facebook"], "publicado", "https://www.instagram.com/reel/A/",
               "https://www.facebook.com/reel/2/", "LIVRO", "SS_PERFORMANCE", Decimal("34.44"), "Tema do pacote",
               "tutoriais-rapidos", "2026-10-30-com-status"))
        igual("só metricas.json (leitura antiga, sem post.json): plataformas e estado NULL",
              (pb.get("2026-09-17-demis", {}).get("plataformas"), pb.get("2026-09-17-demis", {}).get("estado")),
              (None, None))
        ok("pasta sem post.json nem metricas.json não entra", "2026-10-23-sem-metricas" not in pb, sorted(pb))
        ok("publicada sem metricas.json: nenhuma linha de métricas (chegam depois)",
           not linhas(con, "select 1 from metricas where slug = '2026-10-30-com-status-a'"))
        mt = {(r["slug"], r["lido_em"]): r for r in linhas(con, "select * from metricas")}
        h3 = mt.get(("2026-10-20-hinton", ts(HINTON_L3)), {})
        h1 = mt.get(("2026-10-20-hinton", ts(HINTON_L1)), {})
        igual("Hinton: 1512,69 s de tempo médio num vídeo de 158,68 s → suspeito = true",
              (h3.get("tempo_medio_s"), h3.get("pct_assistido"), h3.get("suspeito")),
              (Decimal("1512.69"), Decimal("953.3"), True))
        igual("leitura possível (22,79 s < 158,68 s) → suspeito = false", (h1.get("tempo_medio_s"), h1.get("suspeito")),
              (Decimal("22.79"), False))
        igual("resumo → colunas (IG, FB e palavra-chave)",
              tuple(h3.get(c) for c in ("dias", "views", "alcance", "curtidas", "comentarios", "salvamentos",
                                        "compartilhamentos", "plays_fb", "tempo_medio_fb_s", "palavra_comentarios",
                                        "palavra_directs")),
              (Decimal("7.09"), 11, 12, 1, 2, 3, 4, 4, Decimal("1.73"), 5, 6))
        d0 = mt.get(("2026-09-17-demis", ts("2026-10-13T18:22:21+01:00")), {})
        igual("leitura sem resumo: tudo NULL e não suspeita",
              (d0.get("views"), d0.get("tempo_medio_s"), d0.get("suspeito")), (None, None, False))

        print("\n== perfil: _controle/perfil/*.json ==")
        sn = {r["lido_em"]: r for r in linhas(con, "select * from perfil_snapshots")}
        s = sn.get(ts(PERFIL_LIDO), {})
        igual("follower/non_follower pela chave (não pela posição na lista)",
              (s.get("alcance_seguidores"), s.get("alcance_nao_seguidores")), (206, 307))
        igual("conta e métricas da conta; seguidores do FB = 0 continua 0",
              tuple(s.get(c) for c in ("seguidores", "seguindo", "posts", "janela_dias", "alcance", "views",
                                       "contas_engajadas", "interacoes", "visitas_perfil", "fb_seguidores")),
              (3631, 7505, 5, 28, 529, 2448, 34, 99, 56, 0))
        s16 = sn.get(ts("2026-10-16T10:00:00+01:00"), {})
        igual("foto sem quebra por seguidor: NULL (não zero)",
              (s16.get("seguidores"), s16.get("alcance"), s16.get("alcance_seguidores"), s16.get("fb_seguidores")),
              (3600, 400, None, None))
        dm = {(r["publico"], r["dimensao"], r["chave"]): r["valor"] for r in linhas(con, "select * from perfil_demografia")}
        igual("demografia: follower_demographics → seguidores · reached_audience → alcancados · chave com ' · '", dm, {
            ("seguidores", "country", "GW"): 1741, ("seguidores", "country", "BR"): 504,
            ("seguidores", "city", "Bissau, Bissau"): 1717, ("seguidores", "age", "25-34"): 1218,
            ("seguidores", "gender", "M"): 1624, ("alcancados", "country", "BR"): 197,
            ("alcancados", "gender", "F · 25-34"): 81})



# ───────────────────────── original arquivado fora do Mac (brutos/principal/ARQUIVADO.json) ─────────────────────────
# docs/contratos.md §0, "Original arquivado fora do Mac": vídeo publicado cujo original 4K foi para o HD externo. O vídeo
# continua "gravado" e com os MESMOS números de antes de os .MOV saírem (o critério de aceite de 23/10).

GRAV_COLS = ("gravado", "gravacao_arquivos", "gravacao_bytes", "gravacao_ultima", "gravacao_chegou",
             "gravacao_data_suspeita")
# Os dois primeiros a sair, com o desenho dos reais: o do Hassabis tem os PRAQ com o relógio da câmera em 2024 e o
# camera-00-cor.mov feito no Mac (data com fração de segundo, a mais nova — por isso não é suspeito); o do Hinton só os
# PRAQ de 2024 (suspeito). Fora da conta, no disco e no manifesto: .txt, 0 byte e "._" do macOS. Todos na raiz de
# brutos/principal/, como o escritor real lista (finalizar_g3.py: pr.iterdir(), o nome sem pasta).
ARQ_HASSABIS, ARQ_HINTON = "2026-09-17-arquivado-cor", "2026-10-20-arquivado"
ARQ_FIXTURE = {
    ARQ_HASSABIS: {"PRAQ0969.MOV": (b"a" * 40, 1_721_389_790_000_000_000),
                   "PRAQ0970.MOV": (b"b" * 30, 1_721_389_872_000_000_000),
                   "camera-00-cor.mov": (b"c" * 5, 1_789_769_673_303_067_891),
                   "notas.txt": (b"texto", 1_789_800_000_000_000_000),
                   "vazio.mov": (b"", 1_789_800_000_000_000_000),
                   "._PRAQ0969.MOV": (b"apple", 1_789_800_000_000_000_000)},
    ARQ_HINTON: {"PRAQ0978.MOV": (b"d" * 21, 1_723_637_106_000_000_000),
                 "PRAQ0986.MOV": (b"e" * 60, 1_723_641_652_000_000_000),   # o mais novo dos PRAQ (cai no caso união)
                 "PRAQ0980.MOV": (b"f" * 9, 1_723_637_268_123_456_789)},
}


def _stat_utc(p: Path) -> tuple[int, dt.datetime, dt.datetime]:
    st = p.stat()  # a regra do painel, escrita à parte: float do stat → UTC → até o segundo
    return (st.st_size, dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc).replace(microsecond=0),
            dt.datetime.fromtimestamp(st.st_ctime, dt.timezone.utc).replace(microsecond=0))


def _iso_finalizar_g3(t: float) -> str:
    """O formato EXATO do escritor real, scripts/limpeza/finalizar_g3.py:8 — replicado (o script não se importa sem
    efeito colateral: lê sys.argv, confere o HD e apaga os originais): UTC, isoformat(timespec="seconds")."""
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="seconds")


def _manifesto(principal: Path, escritor: str) -> dict:
    """O ARQUIVADO.json de brutos/principal/. escritor="finalizar_g3": exatamente como o finalizar_g3.py monta
    (linhas 16 e 24–25): os arquivos não ocultos da RAIZ da pasta (pr.iterdir(), inclusive o .txt e o de 0 byte, que o
    painel não conta), o nome SEM pasta e as datas em segundos UTC. escritor="outro": um escritor hipotético que grava a
    fração de segundo, em "Z" — o painel trunca para o segundo e fica igual."""
    arqs = []
    for f in sorted(principal.iterdir()):
        if not f.is_file() or f.name.startswith(".") or f.name == "ARQUIVADO.json":
            continue
        st = f.stat()
        if escritor == "finalizar_g3":
            iso = [_iso_finalizar_g3(st.st_mtime), _iso_finalizar_g3(st.st_ctime)]
        else:
            iso = [dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat().replace("+00:00", "Z")
                   for t in (st.st_mtime, st.st_ctime)]
        arqs.append({"nome": f.name, "bytes": st.st_size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                     "mtime": iso[0], "ctime": iso[1]})
    return {"arquivado_em": "2026-10-23T23:10:00+01:00",
            "motivo": "vídeo publicado; original 4K fora do Mac (limpeza 23/10)",
            "destino": {"volume": "KORVU V01", "volume_uuid": "D4CCA486-0000", "formato": "exFAT",
                        "pasta": "CONTENT AI - originais 4K/x/brutos/principal"},
            "conferencia": "sha256 da origem = sha256 relido do HD", "intermediarios": "edicao/fontes/",
            "arquivos": arqs}


def _gravacao_esperada(itens: list[tuple[int, dt.datetime, dt.datetime]], slug: str) -> tuple:
    """A regra escrita à parte: conta, soma, maior mtime, maior ctime, suspeita = mtime > 30 dias antes do slug."""
    ultima = max(m for _, m, _ in itens)
    return (True, len(itens), sum(b for b, _, _ in itens), ultima, max(c for _, _, c in itens),
            ultima.date() < dt.date.fromisoformat(slug[:10]) - dt.timedelta(days=30))


def casos_arquivado_sem_banco() -> None:
    print("\n== ARQUIVADO.json fora do formato: uma linha ✗ que cita o arquivo, exit 1, sem traceback ==")
    bom = {"nome": "PRAQ0978.MOV", "bytes": 10, "sha256": "0" * 64, "mtime": "2024-08-14T12:05:00+00:00",
           "ctime": "2026-10-14T22:48:00+00:00"}
    rel = "videos/2026-10-30-com-status/brutos/principal/ARQUIVADO.json"
    for nome, conteudo, motivo in (
            ("JSON truncado (escrita pela metade)", '{"arquivos": [{"nome": "PRAQ', "JSONDecodeError"),
            ("não é um objeto", [bom], "não é um objeto JSON"),
            ("sem a lista arquivos", {"motivo": "x"}, "KeyError: 'arquivos'"),
            ("lista arquivos vazia", {"arquivos": []}, "pelo menos um arquivo"),
            ("item que não é objeto", {"arquivos": ["PRAQ0978.MOV"]}, "arquivo 1: não é um objeto"),
            ("item sem bytes", {"arquivos": [{k: v for k, v in bom.items() if k != "bytes"}]}, "KeyError: 'bytes'"),
            ("bytes em texto", {"arquivos": [{**bom, "bytes": "10"}]}, "arquivo 1: bytes '10'"),
            ("bytes negativo", {"arquivos": [{**bom, "bytes": -1}]}, "arquivo 1: bytes -1"),
            ("bytes booleano", {"arquivos": [{**bom, "bytes": True}]}, "arquivo 1: bytes True"),
            ("bytes fracionário", {"arquivos": [{**bom, "bytes": 1.5}]}, "arquivo 1: bytes 1.5"),
            ("item sem ctime", {"arquivos": [{k: v for k, v in bom.items() if k != "ctime"}]}, "KeyError: 'ctime'"),
            ("mtime sem fuso", {"arquivos": [{**bom, "mtime": "2024-08-14T12:05:00"}]}, "mtime '2024-08-14T12:05:00'"),
            ("ctime fora do ISO 8601", {"arquivos": [{**bom, "ctime": "14/10/2026 22:48"}]}, "ctime '14/10/2026 22:48'"),
            ("ctime em número (epoch)", {"arquivos": [{**bom, "ctime": 1792015495}]}, "ctime 1792015495"),
            ("nome vazio", {"arquivos": [{**bom, "nome": ""}]}, "arquivo 1: nome ''"),
            ("nome absoluto", {"arquivos": [{**bom, "nome": "/Volumes/KORVU V01/PRAQ0978.MOV"}]}, "arquivo 1: nome"),
            ("nome que sai da pasta", {"arquivos": [{**bom, "nome": "../PRAQ0978.MOV"}]}, "arquivo 1: nome"),
            ("nome repetido com outra caixa", {"arquivos": [bom, {**bom, "nome": "praq0978.mov"}]},
             "arquivo 2: praq0978.mov repetido"),
            ("nome repetido em NFD", {"arquivos": [{**bom, "nome": "Câmera.MOV"},
                                                   {**bom, "nome": unicodedata.normalize("NFD", "Câmera.MOV")}]},
             "arquivo 2:"),
            ("item sem sha256", {"arquivos": [{k: v for k, v in bom.items() if k != "sha256"}]}, "KeyError: 'sha256'"),
            ("sha256 curto (a prova da cópia)", {"arquivos": [{**bom, "sha256": "abc"}]}, "arquivo 1: sha256 'abc'"),
            ("sha256 que não é hexadecimal", {"arquivos": [{**bom, "sha256": "z" * 64}]}, "arquivo 1: sha256")):
        raiz = Path(tempfile.mkdtemp(prefix="korvu-painel-arquivado-")) / "raiz"
        shutil.copytree(ROOT, raiz)
        escrever(rel, conteudo, raiz=raiz)
        rc, out, err = sincronizar("--seco", db=PORTA_MORTA, projeto=raiz)
        ok(f"ARQUIVADO.json {nome}: exit 1, uma linha ✗ com o arquivo e o motivo",
           rc == 1 and len(out) == 1 and "✗" in out[0] and rel in out[0] and motivo in out[0] and not err,
           f"rc={rc} {out} {err[-200:]}")
        shutil.rmtree(raiz.parent, ignore_errors=True)


def casos_arquivado() -> None:
    print("\n== ARQUIVADO.json: o original fora do Mac continua contando como gravação, com os mesmos números ==")
    pastas = {s: ROOT / "videos" / s / "brutos" / "principal" for s in ARQ_FIXTURE}
    com_status = "2026-10-30-com-status"  # sem manifesto em nenhum momento: a linha não pode mudar
    sql = f"select slug, {', '.join(GRAV_COLS)} from videos where slug = any(%s)"
    sql_arq = "select slug, gravacao_arquivados from videos where slug = any(%s)"

    def arquivados_() -> dict[str, int]:
        with psycopg.connect(BANCO_TESTE) as con:
            return dict(con.execute(sql_arq, [[*ARQ_FIXTURE, com_status]]).fetchall())

    def mac_hd() -> dict[str, tuple]:
        """(no Mac: arquivos, bytes · no HD: arquivos, bytes) na tabela videos — e a view da Biblioteca tem de dizer o
        mesmo nas colunas principal_* (no Mac) e principal_hd_* (no HD)."""
        with psycopg.connect(BANCO_TESTE) as con:
            t = {r["slug"]: (r["gravacao_arquivos_no_mac"], r["gravacao_bytes_no_mac"], r["gravacao_arquivados"],
                             r["gravacao_arquivados_bytes"]) for r in linhas(con, "select * from videos where slug = any(%s)",
                                                                            [[*ARQ_FIXTURE, com_status]])}
            vw = {r["video_slug"]: (r["principal_arquivos"], r["principal_bytes"], r["principal_hd_arquivos"],
                                    r["principal_hd_bytes"]) for r in linhas(
                con, "select * from biblioteca_por_video where video_slug = any(%s)", [[*ARQ_FIXTURE, com_status]])}
        ok("biblioteca_por_video: principal_* = no Mac e principal_hd_* = no HD, os mesmos da tabela videos", t == vw,
           (t, vw))
        return t

    def biblioteca_() -> dict[str, str]:
        with psycopg.connect(BANCO_TESTE) as con:
            return somas(con, ["biblioteca_arquivos", "biblioteca_materiais"])

    def grav() -> dict[str, tuple]:
        with psycopg.connect(BANCO_TESTE) as con:
            return {r["slug"]: tuple(r[k] for k in GRAV_COLS)
                    for r in linhas(con, sql, [[*ARQ_FIXTURE, com_status]])}

    try:
        for slug, arqs in ARQ_FIXTURE.items():
            for rel, (conteudo, mtime_ns) in arqs.items():
                os.utime(escrever(f"videos/{slug}/brutos/principal/{rel}", conteudo), ns=(mtime_ns, mtime_ns))
            escrever(f"videos/{slug}/brutos/principal/.DS_Store", b"ds")
        contados = {s: [_stat_utc(p / r) for r, (c, _) in ARQ_FIXTURE[s].items()
                        if c and r.lower().endswith(".mov") and not Path(r).name.startswith(".")]
                    for s, p in pastas.items()}

        print("   sem manifesto (como hoje)")
        rc, out, err = sincronizar(db=BANCO_TESTE)
        antes, bib_antes = grav(), biblioteca_()
        ok("passagem com os .MOV no disco: exit 0", rc == 0 and out and "✓" in out[-1], f"rc={rc} {out} {err[-300:]}")
        igual("sem manifesto: nenhum arquivo vem do ARQUIVADO.json", arquivados_(), {s_: 0 for s_ in (*ARQ_FIXTURE, com_status)})
        igual("sem manifesto: tudo no Mac (3 vídeos, 75 bytes · 3, 90 bytes), nada no HD",
              {k: v for k, v in mac_hd().items() if k in ARQ_FIXTURE},
              {ARQ_HASSABIS: (3, 75, 0, 0), ARQ_HINTON: (3, 90, 0, 0)})
        for slug in ARQ_FIXTURE:
            igual(f"{slug}: sem ARQUIVADO.json, só o disco — regra de hoje (vídeo, não oculto, > 0 byte)",
                  antes.get(slug), _gravacao_esperada(contados[slug], slug))
        igual("o desenho dos reais: o do Hassabis não é suspeito (camera-00-cor.mov é a data mais nova), o do Hinton é",
              (antes.get(ARQ_HASSABIS, ())[-1:], antes.get(ARQ_HINTON, ())[-1:]), ((False,), (True,)))

        print("   só o manifesto (os .MOV saíram do Mac)")
        for slug, p in pastas.items():
            man = _manifesto(p, "finalizar_g3" if slug == ARQ_HASSABIS else "outro")
            if slug == ARQ_HINTON:  # (fora do escritor real) nome oculto COM extensão de vídeo no manifesto: fora da conta
                man["arquivos"].append({**man["arquivos"][0], "nome": "._PRAQ0978.MOV", "bytes": 4096})
            if slug == ARQ_HASSABIS:
                ok("Hassabis: o manifesto é o do finalizar_g3.py — nome sem pasta, datas em segundos UTC (+00:00)",
                   all("/" not in a["nome"] and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", a["mtime"])
                       and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", a["ctime"]) for a in man["arquivos"]),
                   man["arquivos"][:2])
            for f in sorted(p.rglob("*"), reverse=True):
                if f.name != ".DS_Store":
                    f.rmdir() if f.is_dir() else f.unlink()
            escrever(f"videos/{slug}/brutos/principal/ARQUIVADO.json", man)
        igual("no disco ficou só o ARQUIVADO.json (e o .DS_Store)",
              {s: sorted(f.name for f in p.iterdir()) for s, p in pastas.items()},
              {s: [".DS_Store", "ARQUIVADO.json"] for s in pastas})
        rc, out, err = sincronizar(db=BANCO_TESTE)
        depois = grav()
        ok("passagem só com o manifesto: exit 0", rc == 0 and out and "✓" in out[-1], f"rc={rc} {out} {err[-300:]}")
        for slug in ARQ_FIXTURE:
            igual(f"{slug}: só ARQUIVADO.json → gravado, arquivos, bytes, última, chegou e suspeita IDÊNTICOS aos de "
                  f"antes ({'formato do finalizar_g3.py: segundos UTC' if slug == ARQ_HASSABIS else 'outro escritor: fração e Z'})",
                  depois.get(slug), antes.get(slug))
        ok("continua 'gravado' (o painel não o devolve a Roteiros: producao.ts põe !gravado em Roteiros)",
           all(depois.get(s, (False,))[0] for s in ARQ_FIXTURE), depois)
        igual("gravacao_arquivados: os que vieram do manifesto (3 e 3; fora .txt, 0 byte e o ._ oculto)",
              arquivados_(), {ARQ_HASSABIS: 3, ARQ_HINTON: 3, com_status: 0})
        igual("só o manifesto: nada no Mac, tudo no HD (a Biblioteca não conta o que saiu como se ocupasse o Mac)",
              {k: v for k, v in mac_hd().items() if k in ARQ_FIXTURE},
              {ARQ_HASSABIS: (0, 0, 3, 75), ARQ_HINTON: (0, 0, 3, 90)})
        with psycopg.connect(BANCO_TESTE) as con:
            ok("a Biblioteca não conta o ARQUIVADO.json (está em brutos/principal/, fora de material/ e brutos/extras/)",
               not linhas(con, "select 1 from biblioteca_arquivos where caminho like '%%ARQUIVADO.json'"))
        igual("e a Biblioteca não muda entre antes e depois de os .MOV saírem", biblioteca_(), bib_antes)
        igual("vídeo sem manifesto (com-status) não muda", depois.get(com_status), antes.get(com_status))

        print("   manifesto + arquivo de volta no disco (união, sem contar duas vezes)")
        man = json.loads((pastas[ARQ_HINTON] / "ARQUIVADO.json").read_text(encoding="utf-8"))
        # o PRAQ0986 volta com outra caixa e outro tamanho (o disco vence) e com a data de 2024-01-01: se o item do
        # manifesto ainda contasse, a última seria a dele; e chega um PRAQ0990 que o manifesto não tem
        # e um nome com acento: no disco em NFC, no manifesto em NFD (como o macOS pode guardar) — conta uma vez só
        man["arquivos"].append({**man["arquivos"][0], "nome": unicodedata.normalize("NFD", "Câmera-02.MOV"),
                                "bytes": 999})
        (pastas[ARQ_HINTON] / "ARQUIVADO.json").write_text(json.dumps(man, ensure_ascii=False), encoding="utf-8")
        for nome, conteudo in (("praq0986.mov", b"E" * 7), ("PRAQ0990.MOV", b"g" * 3),
                               (unicodedata.normalize("NFC", "Câmera-02.MOV"), b"h" * 11)):
            os.utime(escrever(f"videos/{ARQ_HINTON}/brutos/principal/{nome}", conteudo),
                     ns=(1_704_067_200_000_000_000,) * 2)
        do_manifesto = [(a["bytes"], ts(a["mtime"]).astimezone(dt.timezone.utc).replace(microsecond=0),
                         ts(a["ctime"]).astimezone(dt.timezone.utc).replace(microsecond=0))
                        for a in man["arquivos"] if a["nome"] in ("PRAQ0978.MOV", "PRAQ0980.MOV")]
        do_disco = [_stat_utc(pastas[ARQ_HINTON] / n) for n in ("praq0986.mov", "PRAQ0990.MOV",
                                                                  unicodedata.normalize("NFC", "Câmera-02.MOV"))]
        rc, out, err = sincronizar(db=BANCO_TESTE)
        uniao = grav()
        ok("passagem com manifesto + disco: exit 0", rc == 0 and out and "✓" in out[-1], f"rc={rc} {out} {err[-300:]}")
        igual("união: 2 do manifesto + praq0986.mov (= PRAQ0986.MOV do manifesto, pelo disco) + PRAQ0990.MOV + "
              "Câmera-02.MOV (NFC no disco = NFD no manifesto) = 5; bytes do disco para os repetidos; última do "
              "manifesto, chegou do disco",
              uniao.get(ARQ_HINTON), _gravacao_esperada(do_manifesto + do_disco, ARQ_HINTON))
        ok("os repetidos contam uma vez só (5 arquivos, não 7) e com os bytes do disco (7 e 11), não os do manifesto "
           "(60 e 999)", uniao.get(ARQ_HINTON, (0, 0, 0))[1:3] == (5, 21 + 9 + 7 + 3 + 11), uniao.get(ARQ_HINTON))
        igual("gravacao_arquivados na união: só os 2 que não estão no disco", arquivados_().get(ARQ_HINTON), 2)
        igual("meio arquivado: no Mac os 3 do disco (7 + 3 + 11 bytes), no HD os 2 que só o manifesto tem (21 + 9); a "
              "soma = o total da gravação", mac_hd().get(ARQ_HINTON), (3, 21, 2, 30))
        igual("o vídeo do Hassabis (só manifesto) não muda", uniao.get(ARQ_HASSABIS), antes.get(ARQ_HASSABIS))
    finally:
        for slug in ARQ_FIXTURE:
            shutil.rmtree(ROOT / "videos" / slug, ignore_errors=True)
    rc, out, err = sincronizar(db=BANCO_TESTE)
    ok("sem os dois vídeos de teste: o banco volta às contagens da raiz de exemplo",
       rc == 0 and out and contagens(out[-1]) == ESPERADO, f"rc={rc} {out} {err[-300:]}")


def casos_fk_da_equipe() -> None:
    print("\n== FK: gerente do departamento e portão que fiscaliza têm de ser agentes (PD5) ==")
    eq = ROOT / "painel" / "equipe.yaml"
    original = eq.read_text(encoding="utf-8")
    with psycopg.connect(BANCO_TESTE) as con:
        antes_db = somas(con)
    for nome, valor, texto in (
            ("gerente com erro de digitação", "(gerente_id)=(portao-dadoz)",
             original.replace("gerente: portao-dados", "gerente: portao-dadoz")),
            ("agente cujo portão (revisor-de-roteiro) não está no equipe.yaml", "(fiscalizado_por)=(revisor-de-roteiro)",
             original + "  - id: roteirista\n    nome: Marina\n    cargo: roteirista\n    departamento: tecnologia\n"
                        "    papel: construtor\n    resumo: Escreve.\n")):
        eq.write_text(texto, encoding="utf-8")
        rc, out, err = sincronizar(db=BANCO_TESTE)
        with psycopg.connect(BANCO_TESTE) as con:
            ok(f"{nome}: exit 1, uma linha ✗ 'recusou' (ForeignKeyViolation no commit) e nada muda no banco",
               rc == 1 and len(out) == 1 and "recusou" in out[0] and "ForeignKey" in out[0] and somas(con) == antes_db,
               f"rc={rc} {out} {err[-200:]}")
            ok(f"{nome}: a linha ✗ diz o valor que falta (o DETAIL do Postgres, PD23)",
               out and valor in out[0], out)
    eq.write_text(original, encoding="utf-8")
    with psycopg.connect(BANCO_TESTE) as con:
        fks = {r["conname"]: r["condeferrable"] and r["condeferred"] for r in linhas(
            con, "select conname, condeferrable, condeferred from pg_constraint where conname in "
                 "('departamentos_gerente_id_fkey', 'agentes_fiscalizado_por_fkey')")}
    igual("as duas FKs existem e são deferrable initially deferred",
          fks, {"departamentos_gerente_id_fkey": True, "agentes_fiscalizado_por_fkey": True})


def casos_fim() -> None:
    with psycopg.connect(BANCO_TESTE) as con:
        print("\n== --seco depois da passagem: o banco não muda ==")
        antes_db = somas(con)
    rc, out, _ = sincronizar("--seco", db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        ok("--seco com o banco no ar: nenhuma tabela muda (nem sincronizacoes)", rc == 0 and somas(con) == antes_db)

        print("\n== banco que recusa a passagem: uma linha ✗, exit 1, nada perdido ==")
        outras = [t for t in TABELAS if t != "fila"]
        antes_db = somas(con, outras)
        n_fila = con.execute("select count(*) from fila").fetchone()[0]
        con.execute("alter table fila drop column confirmar")  # deriva de schema, só no banco de teste
        con.commit()
    rc, out, err = sincronizar(db=BANCO_TESTE)
    with psycopg.connect(BANCO_TESTE) as con:
        ok("exit 1 e uma linha ✗ 'recusou'", rc == 1 and len(out) == 1 and "✗" in out[0] and "recusou" in out[0],
           f"rc={rc} {out} {err[-300:]}")
        ok("sem traceback", err == "", err[-300:])
        ok("rollback: as outras tabelas ficam como estavam e a fila não perde linhas",
           somas(con, outras) == antes_db and con.execute("select count(*) from fila").fetchone()[0] == n_fila)


def casos_banco_real() -> None:
    print("\n== banco do Carlos (só leitura): permissões ==")
    with psycopg.connect(BANCO_REAL, connect_timeout=5) as con:
        con.read_only = True  # transação só-leitura: este teste não escreve no banco do Carlos
        n = con.execute("select count(*) from pg_class where relnamespace = 'public'::regnamespace "
                        "and relkind = 'r'").fetchone()[0]
        ok("há tabelas no public (o teste não passa no vazio)", n >= 23, n)
        vs = [r[0] for r in con.execute("select relname from pg_class where relnamespace = 'public'::regnamespace "
                                        "and relkind = 'v' and not coalesce(reloptions @> '{security_invoker=true}', "
                                        "false)").fetchall()]
        igual("toda view com security_invoker", vs, [])
        igual("todas com RLS", tabelas_sem_rls(con), [])
        v = violacoes_de_permissao(con)
        ok("anon/authenticated sem nenhum privilégio; service_role só SELECT", not v, v[:8])
        v = violacoes_de_default(con)
        ok("default privileges do postgres no public fechados", not v, v[:8])
        con.rollback()


def main() -> int:
    manter = "--manter" in sys.argv
    print(f"raiz temporária: {ROOT}\nregistros:       {REG}\nbanco de teste:  {NOME_TESTE}")
    criado = False
    try:
        montar_projeto()
        montar_registros()
        casos_sem_banco()
        casos_registros_sem_banco()
        casos_propriedade_ultima_linha()
        casos_bytecode()
        casos_guarda_do_corte()
        casos_nao_publicar_sem_banco()
        casos_arquivado_sem_banco()
        casos_producao_sem_banco()
        casos_acervo_sem_banco()
        casos_contrato()
        casos_contrato_referencia()
        try:
            preparar_banco_de_teste()
            criado = True
        except psycopg.OperationalError as e:
            ok("Postgres do painel no ar (127.0.0.1:55322) — ligar com: bash painel/iniciar.sh", False,
               str(e).splitlines()[0])
        if criado:
            casos_permissoes_do_zero()
            casos_mapeamento()
            casos_registros_banco()
            casos_modelo_por_agente()
            casos_biblioteca()
            casos_acervo()
            casos_crescimento()
            casos_producao()
            casos_fila_troca()
            antes_reg = foto(HOME)
            casos_arquivo()
            ok("arquivo: nada escrito na pasta dos registros (só os movimentos do próprio teste)",
               foto(HOME) == antes_reg)
            casos_arquivado()
            casos_fk_da_equipe()
            casos_fim()
            casos_banco_real()
    finally:
        if criado and not manter:
            with psycopg.connect(BANCO_REAL, autocommit=True) as adm:
                for nome in (NOME_TESTE, NOME_SCRIPT):
                    adm.execute(f'drop database if exists "{nome}" with (force)')
                sobrou = adm.execute("select datname from pg_database where datname = any(%s)",
                                     [[NOME_TESTE, NOME_SCRIPT]]).fetchall()
            ok("bancos de teste apagados no fim", not sobrou, sobrou)
        if not manter:
            shutil.rmtree(ROOT, ignore_errors=True)
            shutil.rmtree(OUTRA, ignore_errors=True)
            shutil.rmtree(HOME, ignore_errors=True)
    falhas = [r for r in RES if not r[1]]
    print(f"\n{len(RES) - len(falhas)}/{len(RES)} PASS" + (f" · {len(falhas)} FAIL" if falhas else ""))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
