# Patch local (Korvu) — reaplicar após `npx skills update`

Skill externa: https://github.com/bradautomates/claude-video (MIT), instalada com
`npx skills add bradautomates/claude-video -a claude-code -s '*' -y --copy`.

## 1. Compatibilidade com ffmpeg ≥ 8 (Homebrew instala o 9.x)
`scripts/frames.py` usava `-vsync vfr`, opção removida no ffmpeg novo. Trocado por `-fps_mode vfr` (equivalente, existe desde o ffmpeg 5.1):

```bash
sed -i '' 's/"-vsync", "vfr",/"-fps_mode", "vfr",/' .claude/skills/watch/scripts/frames.py
```

## Configuração
`~/.config/watch/.env`: `WATCH_DETAIL=balanced`, `SETUP_COMPLETE=true`, sem chave Whisper
(os vídeos do projeto já têm transcrição própria; para links sem legenda, adicionar `GROQ_API_KEY`).
