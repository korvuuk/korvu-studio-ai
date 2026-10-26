import "server-only";
import { cache } from "react";
import * as db from "./db";

// Biblioteca = acervo de estilos (telas/biblioteca.md, 24/10): as leituras do banco, uma vez por pedido cada (os blocos
// em Suspense separados leem a mesma tabela sem ir ao banco de novo). Uma falha derruba só o bloco que a usa.

export const looks = cache(db.looks);
export const capaEstilos = cache(db.capaEstilos);
export const capaExemplos = cache(db.capaExemplos);
export const legendaEstilos = cache(db.legendaEstilos);
export const fontes = cache(db.fontes);
export const ferramentas = cache(db.ferramentas);
export const sistemaModelos = cache(db.sistemaModelos);
export const animacoes = cache(db.animacoes);
export const sistemaContagens = cache(db.sistemaContagens);
export const armazenamento = cache(db.armazenamento);
