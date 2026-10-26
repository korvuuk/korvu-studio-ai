// Os comandos que o painel manda o Carlos rodar quando o banco não responde. Ficam aqui (e não só no db.ts) porque
// as telas de erro são componentes do navegador e não podem importar o db.ts (server-only). O db.ts reexporta os dois:
// é a mesma constante nas duas pontas, nunca reescrita à mão (design-system.md §12.2).
export const COMO_LIGAR = "cd painel && supabase start";
export const COMO_SINCRONIZAR = "uv run python painel/sync/sincronizar.py";
