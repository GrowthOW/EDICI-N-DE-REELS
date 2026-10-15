#!/bin/bash
# Uso: preview.sh <carpeta_pieza> "t1 t2 ..." -> <carpeta>/pv/preview.jpg
D=$1; TS="$2"; node "$(dirname $0)/preview.js" $D "$(echo $TS | tr ' ' ',')"
args=(); n=0; for t in $TS; do ffmpeg -v error -y -ss $t -i $D/bg.mp4 -i $D/pv/ov_$t.png -filter_complex "[0:v][1:v]overlay,scale=360:640,drawbox=y=86:h=2:w=iw:c=red,drawbox=y=500:h=2:w=iw:c=red" -frames:v 1 $D/pv/f_$t.jpg; args+=(-i $D/pv/f_$t.jpg); n=$((n+1)); done
ffmpeg -v error -y "${args[@]}" -filter_complex "hstack=inputs=$n" $D/pv/preview.jpg
