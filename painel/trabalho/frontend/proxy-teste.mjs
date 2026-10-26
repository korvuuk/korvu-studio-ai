// Proxy de TESTE: faz um PostgREST puro (contêiner painel_fe_teste_rest) parecer o Supabase para o supabase-js
// (/rest/v1/<tabela> → /<tabela>) e tira as chaves dos cabeçalhos (o PostgREST de teste usa o papel service_role sem JWT).
// CORTAR=<tabela>: devolve uma linha a menos nas respostas dessa tabela — simula um banco que entrega menos do que diz ter.
import http from "node:http";
const ALVO = { host: "127.0.0.1", port: Number(process.env.REST_PORT || 55991) };
const CORTAR = process.env.CORTAR || "";
// MUDAR=<tabela>: na 1.ª resposta dessa tabela, diz que ela tem uma linha a mais (como se o sincronizador regravasse
// a tabela entre um pedido e outro). Cada pedido sai no terminal, para ver a releitura.
const MUDAR = process.env.MUDAR || "";
let mudou = false;
http.createServer((req, res) => {
  const path = req.url.replace(/^\/rest\/v1/, "") || "/";
  const headers = { ...req.headers, host: `${ALVO.host}:${ALVO.port}` };
  delete headers.authorization; delete headers.apikey;
  const p = http.request({ ...ALVO, path, method: req.method, headers }, (r) => {
    const cortar = CORTAR && path.startsWith(`/${CORTAR}?`) && r.statusCode < 300;
    const tabela = path.split("?")[0].slice(1);
    let faixa = r.headers["content-range"];
    if (MUDAR === tabela && !mudou && faixa) {
      mudou = true;
      faixa = faixa.replace(/\/(\d+)$/, (_, n) => `/${Number(n) + 1}`);
      r.headers["content-range"] = faixa;
    }
    if (MUDAR || CORTAR) console.log(`${tabela} offset=${new URLSearchParams(path.split("?")[1]).get("offset") ?? 0} -> ${r.statusCode} ${faixa ?? ""}`);
    if (!cortar) { res.writeHead(r.statusCode, r.headers); r.pipe(res); return; }
    let corpo = ""; r.setEncoding("utf8"); r.on("data", (c) => (corpo += c));
    r.on("end", () => {
      const linhas = JSON.parse(corpo); linhas.pop();
      const out = JSON.stringify(linhas); const h = { ...r.headers, "content-length": Buffer.byteLength(out) };
      res.writeHead(r.statusCode, h); res.end(out);
    });
  });
  p.on("error", (e) => { res.writeHead(502); res.end(String(e)); });
  req.pipe(p);
}).listen(Number(process.env.PORT || 55992), "127.0.0.1");
