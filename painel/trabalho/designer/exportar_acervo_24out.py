"""24/10 — Biblioteca = acervo de estilos (aprovada pelo Carlos; canvas em painel/referencias/claude-design/biblioteca-2026-10-24/).
Acrescenta, SÓ LENDO, o bloco telas_acervo ao painel/design/dados-2026-10-23.json. Cada parte diz de onde vem e se é BANCO
(o sincronizador já grava) ou CONFIGURAÇÃO (arquivo do projeto que o backend ainda não lê)."""
import json, pathlib, re, datetime as dt
import psycopg
RAIZ = pathlib.Path(__file__).resolve().parents[3]
SAIDA = RAIZ / "painel/design/dados-2026-10-23.json"
DB = "postgresql://postgres:postgres@127.0.0.1:55322/postgres"
CONSULTA_ARMAZEM = ("select sum(gravacao_bytes_no_mac) as gravacao_mac from videos; "
                    "select sum(bytes) as material, count(*) from biblioteca_arquivos")  # 25/10: o HD externo não aparece no painel

cor = (RAIZ / "00-marca/cor/cor.md").read_text()
ativa = re.search(r"^versao_ativa:\s*(\S+)", cor, re.M).group(1)
alt_medida = re.search(r"^alternativa_medida:\s*(\S+)", cor, re.M).group(1)
alt = (re.search(r"^arquivados:\s*(\[[^]]*\])", cor, re.M) or re.search(r"^alternativa:\s*(\S+)", cor, re.M)).group(1)  # 24/10: v4 arquivado
luts = {p.stem: json.loads(p.read_text()) for p in (RAIZ / "00-marca/cor/luts").glob("*.json")}

def briefs():
    out = []
    for b in sorted((RAIZ / "videos").glob("2026-*/animacoes/*/brief.md")):
        t = b.read_text(); tit = t.splitlines()[0].lstrip("# ").strip()
        d = re.search(r"duração\s*([\d,]+)\s*s", t)
        out.append({"arquivo": str(b.relative_to(RAIZ)), "titulo": tit, "duracao_s": d.group(1) if d else None,
                    "video": b.parts[-4], "renderizada": any((b.parent).glob("*.mp4"))})
    return out

with psycopg.connect(DB) as c:
    mac = c.execute("select sum(gravacao_bytes_no_mac) from videos").fetchone()[0]
    mat, n_mat = c.execute("select sum(bytes), count(*) from biblioteca_arquivos").fetchone()
    sinc = c.execute("select max(em) from sincronizacoes").fetchone()[0]

tok = json.loads(SAIDA.read_text())["blocos"]["telas_tokens"]["linhas"][0]
T = tok["total_tokens"]
bloco = {
 "fonte": "canvas aprovado: painel/referencias/claude-design/biblioteca-2026-10-24/ (Biblioteca.dc.html + LEIA-ME.md)",
 "lido_em": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
 "linhas": [{
  "looks": {"origem": "CONFIGURAÇÃO: 00-marca/cor/luts/*.json + 00-marca/cor/cor.md (versao_ativa, alternativa_medida, alternativa); fotos = o mesmo quadro da gravação de 16 set (00-marca/cor/amostras/praq0967) com cada LUT, geradas pelo canvas",
            "versao_ativa": ativa, "alternativa_medida": alt_medida, "alternativa": alt,
            "luts": {k: {c_: v.get(c_) for c_ in ("nome", "versao", "criado_em", "aprovada", "aprovada_em")} for k, v in luts.items()}},
  "capas": {"origem": "CONFIGURAÇÃO/ARQUIVOS: capas de 07-publicados/2026-09-17-demis-hassabis e 06-publicar/2026-10-23-livro-chatgpt (+ -l01c); o estilo é do canvas (Serifa + rabisco; Sublinhado laranja)"},
  "legendas": {"origem": "CONFIGURAÇÃO: 00-marca/referencias/legendas/estilo-selecao.md (Texto Selecionado); a amostra é desenhada, não quadro de vídeo"},
  "fontes": {"origem": "CONFIGURAÇÃO: remotion/src/brand.ts (Geist, Bricolage Grotesque, Inter, Playfair Display) + o painel (Geist)"},
  "animacoes": {"origem": "ARQUIVOS: videos/*/animacoes/*/brief.md", "itens": briefs()},
  "armazenamento": {"origem": "BANCO: videos.gravacao_bytes_no_mac, biblioteca_arquivos.bytes (só o que está no Mac; decisão de 25/10)",
                    "consulta": CONSULTA_ARMAZEM, "gravacao_mac_bytes": int(mac),
                    "material_bytes": int(mat), "material_arquivos": n_mat,
                    "sincronizado_em": sinc.isoformat()},
  "sistema": {"origem": "modelos = BANCO (tokens 30 dias, o mesmo telas_tokens); ferramentas = CONFIGURAÇÃO (lista fixa do canvas); contagens = ARQUIVOS (.claude/agents/*.md, .claude/skills/*/, .claude/commands/*.md)",
              "modelos": [{"modelo": m["modelo"], "tokens": m["tokens"], "pct": round(100 * m["tokens"] / T, 1)} for m in tok["por_modelo"]],
              "agentes": len(list((RAIZ / ".claude/agents").glob("*.md"))), "habilidades": len([p for p in (RAIZ / ".claude/skills").iterdir() if p.is_dir()]),
              "comandos": len(list((RAIZ / ".claude/commands").glob("*.md")))},
 }]}
doc = json.loads(SAIDA.read_text())
doc["blocos"]["telas_acervo"] = bloco
SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
print(json.dumps(bloco["linhas"][0]["armazenamento"], ensure_ascii=False)[:300]); print(bloco["linhas"][0]["sistema"]["agentes"], bloco["linhas"][0]["sistema"]["habilidades"], bloco["linhas"][0]["sistema"]["comandos"], [x["titulo"] for x in bloco["linhas"][0]["animacoes"]["itens"]])
