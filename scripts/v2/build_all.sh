#!/usr/bin/env bash
# Reconstruye el reel a partir de los brutos/música definidos en segments.json.
# Uso: ./build_all.sh <salida.mp4> [content.json]
#   SKIP_BG=1 reutiliza background.mp4 (p. ej. al renderizar otro idioma).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
OUT="${1:?uso: build_all.sh <salida.mp4> [content.json]}"
CONTENT="$(cd "$(dirname "${2:-$HERE/content.json}")" && pwd)/$(basename "${2:-$HERE/content.json}")"
BG="$HERE/background.mp4"

echo "== 1/3 fondo (recorte 9:16 + grading + transiciones) =="
if [[ "${SKIP_BG:-0}" == "1" && -f "$BG" ]]; then echo "(reutilizando $BG)"; else python3 "$HERE/build_background.py" "$BG"; fi

echo "== 2/3 cartelas (texto real, capa transparente) =="
python3 - "$HERE" "$CONTENT" << 'PYEOF'
import json, os, sys
here, content_path = sys.argv[1], sys.argv[2]
tl = json.load(open(os.path.join(here, "timeline.json")))
content = json.load(open(content_path))
html = open(os.path.join(here, "overlay_template.html")).read()
html = html.replace("__TIMELINE_JSON__", json.dumps(tl)).replace("__CONTENT_JSON__", json.dumps(content))
open(os.path.join(here, "overlay.html"), "w").write(html)
PYEOF
python3 "$HERE/overlay_capture.py"

echo "== 3/3 composicion final + musica =="
read -r DUR MUSIC MUSIC_START < <(python3 -c "
import json
t=json.load(open('$HERE/timeline.json')); s=json.load(open('$HERE/segments.json'))
print(t['total_duration'], '$REPO/'+s['music'], s.get('music_start',0))")
VFADE=$(python3 -c "print(round($DUR-0.5,3))")
AFADE=$(python3 -c "print(round($DUR-1.5,3))")
ffmpeg -y -v error -stats \
  -i "$BG" \
  -framerate 30 -i "$HERE/overlay_frames/ov_%05d.png" \
  -ss "$MUSIC_START" -t "$DUR" -i "$MUSIC" \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,fade=t=out:st=${VFADE}:d=0.5[v];[2:a]afade=t=in:d=0.4,afade=t=out:st=${AFADE}:d=1.5[a]" \
  -map "[v]" -map "[a]" -t "$DUR" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 20 -preset medium \
  -c:a aac -b:a 192k -movflags +faststart \
  "$OUT"

echo "DONE -> $OUT"
