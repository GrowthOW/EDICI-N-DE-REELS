#!/bin/bash
# Uso: compose.sh <carpeta_pieza> <fondo.mp4> <endcard.png> <nombre_base>
# Salidas: <nombre_base>_tiktok.mp4 (21,6 s, sin música, sin cierre) y <nombre_base>_short.mp4 (24 s, cierre + música −14 LUFS)
set -e
P=$1; BG=$2; EC=$3; N=$4
MUS=/home/user/EDICI-N-DE-REELS/sources_audio/background_music.mp3
cd "$P"
ffmpeg -y -v error -stats -i "$BG" -framerate 25 -i ov/f_%05d.png -f lavfi -i anullsrc=r=48000:cl=stereo \
  -filter_complex "[0:v]trim=end=21.6,setpts=PTS-STARTPTS[b];[b][1:v]overlay=0:0:eof_action=pass,format=yuv420p[v]" \
  -map "[v]" -map 2:a -t 21.6 -c:v libx264 -crf 20 -preset slow -profile:v high -r 25 -c:a aac -b:a 128k -movflags +faststart ${N}_tiktok.mp4
# música: medición y normalización en dos pasadas a −14 LUFS / −1,5 dBTP
J=$(ffmpeg -v info -ss 4 -t 24 -i $MUS -af "afade=t=in:d=0.3,afade=t=out:st=22.2:d=1.8,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
mi=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
read II ITP ILRA ITH OFF <<< "$mi"
ffmpeg -y -v error -stats -i "$BG" -framerate 25 -i ov/f_%05d.png -loop 1 -t 24 -framerate 25 -i "$EC" -ss 4 -t 24 -i $MUS \
  -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass[a];[2:v]format=rgba,fade=t=in:st=21.2:d=0.4:alpha=1[e];[a][e]overlay=0:0:eof_action=pass,format=yuv420p[v];[3:a]afade=t=in:d=0.3,afade=t=out:st=22.2:d=1.8,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$II:measured_TP=$ITP:measured_LRA=$ILRA:measured_thresh=$ITH:offset=$OFF:linear=true,aresample=48000[m]" \
  -map "[v]" -map "[m]" -t 24 -c:v libx264 -crf 20 -preset slow -profile:v high -r 25 -c:a aac -b:a 192k -movflags +faststart ${N}_short.mp4
ffmpeg -v info -i ${N}_short.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak:"
