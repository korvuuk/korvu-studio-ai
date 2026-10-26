import type { NextConfig } from "next";

// Pasta de saída escolhida por variável. O preview do Carlos (next dev :3456) usa ".next"; o build de verificação e
// os servidores de trabalho usam outra pasta e nunca tocam na dele:
//   PAINEL_DIST=.next-verificacao npm run build      PAINEL_DIST=.next-trabalho npm run dev -- -p 3457
// Os scripts "dev" e "start" do package.json escutam só em 127.0.0.1 (o site só abre no próprio Mac, 23/10); o
// "npm run dev -- -p 3457" herda o -H. Um "npx next dev" solto, sem -H 127.0.0.1, abriria a porta para a rede local.
// Só nomes que começam com ".next": ficam fora do git e fora da impressão dos portões (scripts/portoes.py).
const distDir = process.env.PAINEL_DIST || ".next";
if (!/^\.next[\w-]*$/.test(distDir)) {
  throw new Error(`PAINEL_DIST="${distDir}" não serve: use um nome que comece com .next (ex.: .next-verificacao)`);
}

const nextConfig: NextConfig = {
  distDir,
  // O selo "N" do next dev ficava em cima do rodapé da barra lateral (só aparece em desenvolvimento).
  devIndicators: false,
  // "Vídeos e portões" virou "Produção de conteúdo" (decisão do Carlos, 23/10): o endereço antigo continua valendo.
  // Redirecionamento HTTP (307), antes de qualquer página — um redirect() dentro da página chegaria tarde, com a casca
  // já transmitida, e viraria um "refresh" no navegador.
  async redirects() {
    return [{ source: "/videos", destination: "/producao", permanent: false }];
  },
};

export default nextConfig;
