import type { NomeIcone } from "@/components/Icone";

/**
 * O menu do painel, na ordem decidida pelo Carlos em 23/10 (docs/decisoes.md §5): "Vídeos e portões" virou "Produção de
 * conteúdo" (/videos redireciona para /producao). Calendário, Biblioteca e Tokens e custos já têm rota, com o estado
 * vazio "Esta tela chega em breve" até o desenho de cada uma ser aprovado.
 */
export const PAGINAS: readonly { href: string; nome: string; icone: NomeIcone }[] = [
  { href: "/", nome: "Visão geral", icone: "visao-geral" },
  { href: "/equipe", nome: "Equipe", icone: "equipe" },
  { href: "/producao", nome: "Produção de conteúdo", icone: "videos-portoes" },
  { href: "/calendario", nome: "Calendário", icone: "calendario" },
  { href: "/desempenho", nome: "Desempenho", icone: "desempenho" },
  { href: "/biblioteca", nome: "Biblioteca", icone: "biblioteca" },
  { href: "/tokens", nome: "Tokens e custos", icone: "tokens-custos" },
];

/** Item aceso: "/equipe/marina" e "/equipe/contratar" acendem "Equipe"; "/" só na própria visão geral. */
export const estaAtivo = (href: string, caminho: string) =>
  href === "/" ? caminho === "/" : caminho === href || caminho.startsWith(`${href}/`);
