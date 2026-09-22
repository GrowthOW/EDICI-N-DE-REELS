"""Compara varios encuadres verticales 9:16 de un bruto, lado a lado.

Uso:
  python3 crop_preview.py <clip.mp4> <segundo> <crop_x> [<crop_x> ...]

Ejemplo:
  python3 crop_preview.py ../../sources_raw/montblanc_massif_drone.mp4 3 1100 1450 1800

Genera crop_preview.jpg. El valor que elijas va en segments.json como
crop_x0 / crop_x1 (iguales = encuadre fijo; distintos = paneo de uno a otro).
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 4:
    print(__doc__); sys.exit(1)
clip, t, xs = sys.argv[1], sys.argv[2], sys.argv[3:]

probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=p=0", clip], capture_output=True, text=True, check=True)
w, h = map(int, probe.stdout.strip().split(","))
max_x = round(w * 1920 / h) - 1080
print(f"bruto {w}x{h} -> crop_x valido entre 0 y {max_x}")

tmp = tempfile.mkdtemp()
tiles = []
for x in xs:
    x = min(int(x), max_x)
    out = os.path.join(tmp, f"{x}.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", t, "-i", clip, "-vf",
                    f"scale=-2:1920,crop=1080:1920:{x}:0,scale=360:-2,"
                    f"drawtext=text='crop_x {x}':x=12:y=12:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6",
                    "-frames:v", "1", out], check=True)
    tiles.append(out)

dest = os.path.join(HERE, "crop_preview.jpg")
inputs = sum([["-i", p] for p in tiles], [])
stack = f"hstack={len(tiles)}" if len(tiles) > 1 else "null"
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", stack, dest], check=True)
print("->", dest)
