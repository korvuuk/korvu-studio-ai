"""Conta as competências pedidas em vagas reais de IA (remotas), por família de cargo.

Uso: python3 -I analisar_vagas.py <pasta-dados> <saida.json>
Fontes na pasta: hima-*.json (Himalayas search), rok-*.json (RemoteOK), wwr-*.rss (We Work Remotely),
hn-oct2026.json (HN "Who is hiring", out/2026).
"""
import glob
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone

D, SAIDA = sys.argv[1], sys.argv[2]


def limpar(t):
    t = html.unescape(t or "")
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


vagas = []
for f in sorted(glob.glob(D + "/hima-*.json")):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    for j in d.get("jobs", []):
        vagas.append(dict(fonte="himalayas", titulo=j.get("title", ""), empresa=j.get("companyName", ""),
                          local=",".join(j.get("locationRestrictions") or []) or "Worldwide",
                          data=datetime.fromtimestamp(int(j.get("pubDate") or 0), timezone.utc).date().isoformat(),
                          texto=limpar(j.get("description", "")), url=j.get("guid", "")))
for f in sorted(glob.glob(D + "/rok-*.json")):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    for j in d:
        if "position" not in j:
            continue
        vagas.append(dict(fonte="remoteok", titulo=j["position"], empresa=j.get("company", ""),
                          local=j.get("location") or "Worldwide", data=j.get("date", "")[:10],
                          texto=limpar(j.get("description", "")) + " " + " ".join(j.get("tags") or []),
                          url=j.get("url", "")))
for f in sorted(glob.glob(D + "/wwr-*.rss")):
    try:
        raiz = ET.parse(f).getroot()
    except Exception:
        continue
    for it in raiz.iter("item"):
        tit = it.findtext("title") or ""
        emp, _, cargo = tit.partition(":")
        vagas.append(dict(fonte="weworkremotely", titulo=cargo.strip() or tit, empresa=emp.strip(),
                          local=it.findtext("region") or "", data=(it.findtext("pubDate") or "")[:16],
                          texto=limpar(it.findtext("description")), url=it.findtext("link") or ""))
try:
    hn = json.load(open(D + "/hn-oct2026.json"))
    for c in hn.get("children", []):
        txt = limpar(c.get("text"))
        if not txt:
            continue
        primeira = txt.split(" ", 40)
        vagas.append(dict(fonte="hn-out2026", titulo=" ".join(primeira[:40]), empresa="", local="",
                          data=(c.get("created_at") or "")[:10], texto=txt,
                          url=f"https://news.ycombinator.com/item?id={c.get('id')}"))
except Exception:
    pass

# ---- famílias de cargo (pelo título) ----
LIXO = re.compile(r"\b(expert|tutor|trainer|annotat|rater|labell?ing|evaluator|contributor|writer|"
                  r"phd|msc|translator|linguist|reviewer)\b", re.I)
IA = re.compile(r"\b(ai|a\.i\.|llm|llms|genai|gen ai|generative|agentic|agents?|ml|machine learning|"
                r"applied ai|nlp|prompt)\b", re.I)
F_ML = re.compile(r"machine learning|\bml engineer|\bmlops|data scien|research scien|computer vision|"
                  r"\bnlp engineer|deep learning", re.I)
F_AUTO = re.compile(r"automation|\bn8n\b|workflow|implementation|solutions? (engineer|architect|consultant)|"
                    r"forward.deployed|integration|\bai (specialist|consultant|strategist|operations)|"
                    r"prompt engineer|customer engineer|deployment strategist", re.I)
F_ENG = re.compile(r"engineer|developer|architect|programmer|builder", re.I)


def familia(v):
    t = v["titulo"]
    if v["fonte"] == "hn-out2026":
        # HN: a 1.ª linha traz empresa | cargo | local; só conta se a vaga for de IA
        if not IA.search(t):
            return None
    elif LIXO.search(t):
        return None
    if F_AUTO.search(t) and (IA.search(t) or IA.search(v["texto"][:600]) or "automation" in t.lower()):
        return "B. Automação / implementação / solutions"
    if F_ML.search(t):
        return "C. ML engineer / data science"
    if IA.search(t) and F_ENG.search(t):
        return "A. AI / LLM engineer"
    return None


# ---- dicionário de competências ----
S = {
    "Python": r"\bpython\b", "TypeScript": r"\btypescript\b", "JavaScript / Node.js": r"\bjavascript\b|\bnode(\.js|js)?\b",
    "SQL": r"\bsql\b", "Go": r"\bgolang\b|\bgo\b(?= ?(,|/|and|or)\b)", "Java": r"\bjava\b(?!script)", "Rust": r"\brust\b",
    "OpenAI / GPT": r"\bopenai\b|\bgpt-?\d|\bchatgpt\b", "Anthropic / Claude": r"\banthropic\b|\bclaude\b",
    "Gemini / Vertex AI": r"\bgemini\b|\bvertex\b", "Open-source LLMs (Llama, Mistral, HF)": r"\bllama\b|\bmistral\b|hugging ?face",
    "LLMs (termo)": r"\bllms?\b|large language model", "Generative AI (termo)": r"\bgen(erative)? ?ai\b",
    "RAG / retrieval": r"\brag\b|retrieval.augmented|\bretrieval\b", "Embeddings": r"\bembeddings?\b",
    "Vector DB (pgvector, Pinecone…)": r"vector (db|database|store|search)|\bpgvector\b|\bpinecone\b|\bweaviate\b|\bqdrant\b|\bchroma\b|\bmilvus\b",
    "Prompt engineering": r"prompt(ing| engineering| design)", "Fine-tuning": r"fine.?tun",
    "Evals / avaliação de LLM": r"\bevals?\b|evaluation (framework|pipeline|harness)|llm evaluation|model evaluation",
    "AI agents / agentic": r"\bagentic\b|\bai agents?\b|\bllm agents?\b|\bautonomous agents?\b|\bagents? (framework|workflow|orchestration|system|platform)|build(ing)? (ai )?agents\b", "Multi-agent": r"multi.agent",
    "Tool / function calling": r"tool (use|calling)|function calling", "MCP": r"\bmcp\b|model context protocol",
    "Guardrails / AI safety": r"guardrails?|ai safety|responsible ai", "LLM observability (LangSmith, Langfuse…)": r"langsmith|langfuse|observability",
    "LangChain": r"langchain", "LangGraph": r"langgraph", "LlamaIndex": r"llama.?index", "CrewAI / AutoGen": r"crewai|autogen",
    "PyTorch": r"pytorch", "TensorFlow": r"tensorflow", "scikit-learn": r"scikit|sklearn", "MLOps": r"\bmlops\b",
    "NLP": r"\bnlp\b|natural language processing", "Deep learning": r"deep learning", "Statistics": r"\bstatistic",
    "FastAPI": r"fastapi", "Django / Flask": r"\bdjango\b|\bflask\b", "REST APIs": r"\brest(ful)?\b|\bapis?\b",
    "GraphQL": r"graphql", "Webhooks": r"webhook", "Microservices": r"microservice",
    "React": r"\breact\b", "Next.js": r"next\.?js", "React Native": r"react native",
    "PostgreSQL": r"postgres", "MongoDB": r"mongo", "Redis": r"\bredis\b", "Supabase": r"supabase",
    "Data pipelines / ETL": r"\betl\b|data pipelines?|airflow|\bdbt\b", "Spark / Kafka": r"\bspark\b|\bkafka\b",
    "AWS": r"\baws\b|amazon web services", "AWS Bedrock": r"bedrock", "GCP": r"\bgcp\b|google cloud", "Azure": r"\bazure\b",
    "Docker": r"docker", "Kubernetes": r"kubernetes|\bk8s\b", "Terraform / IaC": r"terraform|infrastructure as code",
    "CI/CD": r"ci/cd|\bci\b|continuous integration|github actions", "Serverless / Lambda": r"serverless|\blambda\b",
    "Git": r"\bgit\b|github|gitlab", "Testing": r"\btest(s|ing)\b|pytest|vitest|jest",
    "n8n": r"\bn8n\b", "Zapier": r"zapier", "Make.com": r"make\.com|\bmake \(integromat\)|integromat",
    "Workflow automation": r"workflow automation|automat(e|ing|ion) workflows?", "RPA / UiPath / Power Automate": r"\brpa\b|uipath|power automate",
    "CRM (HubSpot, Salesforce)": r"hubspot|salesforce|\bcrm\b", "Integrations (APIs de terceiros)": r"integrations?\b",
    "Production / shipping": r"\bproduction\b|\bship(ped|ping)?\b", "Full-stack": r"full.?stack",
    "Customer-facing / clientes": r"customer.facing|client.facing|stakeholders?|work(ing)? (directly )?with (customers|clients)",
    "Comunicação": r"communication skills|communicat(e|ion)", "Startup / ownership": r"startup|ownership|autonom",
    "System design / arquitetura": r"system design|architect(ure|ing)", "Security": r"security (best practices|reviews?|controls)|secure (coding|systems)|\bsoc ?2\b|\bgdpr\b",
    "Cost / latency optimisation": r"\blatency\b|token (usage|costs?)|cost.(efficien|optimi|aware)|inference costs?",
}
RX = {k: re.compile(v, re.I) for k, v in S.items()}

por_fam = defaultdict(list)
vistos = set()
for v in vagas:
    fam = familia(v)
    if not fam:
        continue
    chave = (v["empresa"].lower(), v["titulo"].lower()[:80], v["fonte"] == "hn-out2026" and v["url"])
    if chave in vistos:
        continue
    vistos.add(chave)
    por_fam[fam].append(v)

saida = {"total_bruto": len(vagas), "familias": {}}
for fam, lst in sorted(por_fam.items()):
    c = Counter()
    for v in lst:
        for k, rx in RX.items():
            if rx.search(v["titulo"] + " " + v["texto"]):
                c[k] += 1
    fontes = Counter(v["fonte"] for v in lst)
    mundo = sum(1 for v in lst if re.search(r"worldwide|anywhere|europe|emea|united kingdom|\buk\b|remote", v["local"] + " " + v["texto"][:300], re.I))
    saida["familias"][fam] = {
        "n": len(lst), "fontes": dict(fontes),
        "skills_pct": {k: round(100 * n / len(lst)) for k, n in c.most_common()},
        "exemplos": [f'{v["titulo"][:70]} — {v["empresa"]} ({v["fonte"]})' for v in lst[:25]],
    }
json.dump(saida, open(SAIDA, "w"), ensure_ascii=False, indent=1)
print("bruto:", len(vagas))
for fam, x in saida["familias"].items():
    print(f"\n== {fam}: n={x['n']} {x['fontes']}")
    for k, p in list(x["skills_pct"].items())[:45]:
        print(f"  {p:3d}%  {k}")
