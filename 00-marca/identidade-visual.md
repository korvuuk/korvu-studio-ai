# Identidade Visual — Korvu (cores, fontes, logo, zonas seguras)

## Status: provisório

> **21/10:** o PDF do material e o cartão do CTA seguem o design system editorial — `00-marca/design-system/korvu-editorial.md` (papel + tinta + laranja `#E85002`, Bricolage Grotesque). As cores laranja `#FF7A35`/rosa e a Barlow Condensed abaixo **não valem mais** para esses dois.

Este arquivo reúne só o essencial da identidade aprovada nos carrosséis (abril/2026).
**Será substituído/complementado pelo design system em `00-marca/design-system/` e pela referência de legenda em `00-marca/referencias/legendas/estilo-selecao.md`.** Quando esses existirem, eles prevalecem.

---

## Paleta

| Uso | Valor |
|---|---|
| **Laranja accent (principal)** — destaques, palavra-chave, subtítulos | `#FF7A35` |
| Laranja variante (legado, borda de avatar) — preferir `#FF7A35` | `#FF6B35` |
| **Rosa accent** — botões, segundo destaque | `#E8317B` |
| **Fundo escuro** | `#080808` |
| Título em fundo escuro | `#FFFFFF` |
| Texto corrido em fundo escuro | `rgba(255,255,255,0.80)` |
| Texto secundário / handle | `rgba(255,255,255,0.50)` |
| **Fundo claro** | `linear-gradient(160deg, #FAFAF8, #F0EFE9)` |
| **Fundo accent roxo** | `linear-gradient(145deg, #1a0533, #2d1058, #0d1a40)` |
| Gradiente de destaque (barra, palavra-chave grande) | `#FF7A35 → #E8317B` |
| Etiqueta (tag) em fundo escuro | borda `rgba(180,100,240,0.70)` · fundo `rgba(160,80,220,0.10)` |
| Etiqueta em fundo claro | borda `rgba(0,0,0,0.25)` · fundo `rgba(0,0,0,0.06)` · texto `#222` |

---

## Tipografia

| Elemento | Fonte | Peso | Extras |
|---|---|---|---|
| Título / gancho na tela | **Barlow Condensed** | 900 | CAIXA ALTA, line-height 0.92–0.93 |
| Subtítulo acima do título | Inter | 700 | CAIXA ALTA, letter-spacing 3px, `#FF7A35` |
| Etiquetas | Inter | 600 | CAIXA ALTA, letter-spacing 2.5px |
| Texto corrido | Inter | 400 | line-height 1.4–1.55 |
| Nome do autor / handle | Inter | 700 / 400 | — |

Google Fonts: `Barlow+Condensed:wght@700;800;900` + `Inter:wght@400;500;600;700;800;900`

### Aplicação no Reel (1080×1920)
- Gancho na tela: Barlow Condensed 900, CAIXA ALTA, **4–7 palavras, máx. 2 linhas**, ~88–120px.
- Contraste alto: branco sobre fundo escuro/vídeo com sombra ou contorno; palavra-chave em `#FF7A35`.
- Nunca texto fino sobre vídeo claro sem contraste.

---

## Logo e marca

- Avatar Korvu circular, borda 2px laranja; no bloco de autor pode aparecer com opacidade 60%.
- Bloco de autor: nome **Korvu Oficial** + handle **@korvu_oficial**.
- Arquivos oficiais do logo: `00-marca/assets/logo/` *(pendente — pasta ainda vazia)*.
- Não distorcer, não recolorir fora da paleta, não aplicar sobre fundo que tire o contraste.
- Logo nunca compete com o gancho no frame 1 e nunca fica fora da zona segura.

---

## Zonas seguras do Reel (1080×1920)

A interface do Instagram cobre partes do vídeo. Texto e rosto importantes ficam **dentro** da área segura.

| Margem | Reservar | Motivo |
|---|---|---|
| Topo | ~270px | nome da conta, "Reels", status do celular |
| Base | ~670px | legenda, nome, música, botões |
| Esquerda | ~65px | borda |
| Direita | ~120px | curtir, comentar, enviar, salvar |

**Área segura resultante:** x 65 → 960 · y 270 → 1250 (≈ 895 × 980px).

```
┌──────────────────────── 1080 ────────────────────────┐
│ ░░░░░░░░░░░░░░░ topo 270px (UI) ░░░░░░░░░░░░░░░░░░░ │
│░│                                              │░░░░░│
│░│        ÁREA SEGURA                            │░░░░░│
│░│        gancho na tela, rosto, legenda         │ 120 │
│65        (y 270 → 1250)                         │ px  │
│░│                                              │░░░░░│
│ ░░░░░░░░░░░░░ base 670px (legenda/botões) ░░░░░░░░░ │
└──────────────────────────────────────────────────────┘ 1920
```

### Legendas queimadas (texto falado na tela)
Referência definitiva: `00-marca/referencias/legendas/estilo-selecao.md` *(pendente)*. Até lá:
- Inter 700 ou Barlow Condensed 800, branco com sombra/contorno; destaque em `#FF7A35`.
- Máx. 2 linhas, dentro da área segura, acima de y = 1250.

---

## Capa do Reel

- **Título + rosto dentro do centro 1080×1440** (y 240 → 1680) — é o recorte 3:4 que aparece na grade do perfil.
- Título com **3–6 palavras**, Barlow Condensed 900, CAIXA ALTA, destaque em laranja.
- Rosto do Carlos ou a tela/resultado — nunca pessoa real que não seja o Carlos.
- O título também respeita a área segura do Reel (a capa aparece no próprio vídeo).

---

## Proibido

- Foto ou imagem realista (inclusive gerada por IA) de pessoa real que não seja o Carlos. A antiga rotação de fotos de celebridades de tecnologia foi **removida**.
- Texto gerado por IA dentro de imagens (sai corrompido) — texto é sempre colocado na edição.
- Mais de 5 cores fora da paleta num mesmo vídeo.
- Print de tela com dado pessoal visível (contatos, e-mails, telefones) — borrar antes.
