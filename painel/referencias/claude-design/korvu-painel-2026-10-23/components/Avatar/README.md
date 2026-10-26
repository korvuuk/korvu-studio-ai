# Avatar

Avatares de agentes: **retratos fotográficos realistas** de pessoas fictícias, quadrados 1:1.

Regras de imagem (para gerar as fotos):
- Headshot profissional, ombros visíveis, olhar para a câmara, expressão neutra-simpática.
- Mesmo enquadramento em todos: topo da cabeça a ~18% da altura, olhos a ~40%, ombros a cortar a base.
- Fundo neutro liso, tom quente próximo de `surface-sunken` (#EFEBE0); luz suave lateral; sem objetos.
- Diversidade realista de género, idade (25–60) e etnia em toda a equipa.
- Exportar 512×512 px, JPG/WebP.

Uso:
- `k-avatar` com `--s` (tamanho). Cards de equipa 56px raio 10px; listas 40px raio 8px; pilhas 28px redondas (`is-round`).
- Sem foto: iniciais (2 letras) em `ink-2` sobre `surface-sunken` — é o estado mostrado aqui.
- Presença: `k-presence` (verde) só para agentes a trabalhar agora.
