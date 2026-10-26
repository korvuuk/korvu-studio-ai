"""Volta de 24/10: troca SÓ o bloco telas_tokens (PD21: última linha de cada resposta, corte do banco 15:02:49Z) e tira o
telas_cambio (custo volta a US$ sem câmbio, decisão de 24/10). Os outros blocos ficam como estavam em 23/10 — a Biblioteca
não entra nesta volta, e as telas continuam sendo o retrato de 23/10."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import exportar_dados_telas as X
doc = json.loads(X.SAIDA.read_text(encoding="utf-8"))
doc["blocos"]["telas_tokens"] = X.bloco_tokens()
doc["blocos"].pop("telas_cambio", None)
doc["telas_24out"] = ("24/10: telas_tokens refeito (PD21: última linha de cada message.id, dia da 1.ª, corte 2026-10-23T15:02:49Z "
                      "= o banco: 37.909.543 tokens, US$ 539,06); telas_cambio retirado (custo em US$, sem câmbio). Gerado por "
                      "painel/trabalho/designer/atualizar_tokens_24out.py.")
X.SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
t = doc["blocos"]["telas_tokens"]["linhas"][0]
print("ok", t["total_tokens"], t["total_us"])
