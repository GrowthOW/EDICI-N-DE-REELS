#!/usr/bin/env bash
# Reconstruye el reel "Top destinos 2027" a partir de un clip bruto.
# Uso: ./build_all.sh /ruta/al/bruto.mp4 /ruta/de/salida.mp4
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${1:?uso: build_all.sh <bruto.mp4> <salida.mp4>}"
OUT="${2:?uso: build_all.sh <bruto.mp4> <salida.mp4>}"

BG="$HERE/background.mp4"

echo "== 1/3 fondo (recorte 9:16 + grading + transiciones + audio) =="
python3 "$HERE/build_background.py" "$SRC" "$BG"

echo "== 2/3 cartelas (texto real, capa transparente) =="
python3 << PYEOF
import json
with open("$HERE/timeline.json") as f: tl = json.load(f)
with open("$HERE/content.json") as f: content = json.load(f)
with open("$HERE/overlay_template.html") as f: html = f.read()
html = html.replace("__TIMELINE_JSON__", json.dumps(tl))
html = html.replace("__CONTENT_JSON__", json.dumps(content))
with open("$HERE/overlay.html", "w") as f:
    f.write(html)
PYEOF
python3 "$HERE/overlay_capture.py"

echo "== 3/3 composicion final =="
DUR=$(python3 -c "import json;print(json.load(open('$HERE/timeline.json'))['total_duration'])")
FADE_ST=$(python3 -c "print($DUR-0.5)")
ffmpeg -y \
  -i "$BG" \
  -framerate 30 -i "$HERE/overlay_frames/ov_%05d.png" \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,fade=t=out:st=${FADE_ST}:d=0.5[v]" \
  -map "[v]" -map 0:a \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 16 -preset slow \
  -c:a aac -b:a 192k -af "afade=t=out:st=${FADE_ST}:d=0.5" \
  -movflags +faststart \
  "$OUT"

echo "DONE -> $OUT"
