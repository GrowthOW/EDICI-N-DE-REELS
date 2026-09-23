"""Quita la marca de agua de clideo.com (abajo a la derecha) con un zoom
x1.25 y reencuadre, manteniendo 16:9 y la resolución de salida.

Uso:
  python3 quitar_marca_clideo.py <entrada.mp4> <salida.mp4> [x y]
  python3 quitar_marca_clideo.py <entrada.mp4> --preview [x y]

x, y: esquina superior izquierda del encuadre en coordenadas 1920x1080
(por defecto 192 74 = centrado y lo más abajo posible sin tocar la marca).
El encuadre es 1536x864; x va de 0 a 384, y de 0 a 74.
--preview dibuja el encuadre en 4 momentos del clip -> <entrada>_encuadre.jpg
para elegir x/y antes de exportar.

La marca ocupa x 1385-1855, y 955-1012 (a 1080p). Si en un clip aparece en
otro sitio, este recorte no sirve: revisar a mano.
"""
import os, subprocess, sys

CW, CH = 1536, 864
MAX_Y = 74  # bottom edge 938 < 955, where the watermark starts


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "default=nw=1", path],
                         capture_output=True, text=True, check=True).stdout
    vals = dict(l.split("=") for l in out.split())
    return int(vals["width"]), int(vals["height"]), float(vals["duration"])


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__); sys.exit(1)
    src = args[0]
    preview = args[1] == "--preview"
    rest = args[2:] if preview or len(args) > 2 else []
    if not preview:
        dst = args[1]
    x, y = (int(rest[0]), int(rest[1])) if len(rest) >= 2 else (192, MAX_Y)
    x, y = max(0, min(x, 1920 - CW)), max(0, min(y, MAX_Y))

    w, h, dur = probe(src)
    s = w / 1920  # the watermark scales with the frame
    crop = f"crop={round(CW*s)}:{round(CH*s)}:{round(x*s)}:{round(y*s)}"

    if preview:
        base = os.path.splitext(src)[0]
        tiles = []
        for i, t in enumerate([0.1, 0.35, 0.65, 0.9]):
            p = f"{base}_enc{i}.jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{dur*t:.2f}", "-i", src, "-vf",
                            f"drawbox=x={round(x*s)}:y={round(y*s)}:w={round(CW*s)}:h={round(CH*s)}:c=yellow:t={max(2,round(6*s))},scale=480:-2",
                            "-frames:v", "1", p], check=True)
            tiles.append(p)
        out = f"{base}_encuadre.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", *sum([["-i", p] for p in tiles], []),
                        "-filter_complex", "hstack=4", out], check=True)
        for p in tiles:
            os.remove(p)
        print("->", out)
        return

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vf",
                    f"{crop},scale={w}:{h}:flags=lanczos,unsharp=5:5:0.6:5:5:0.0",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", dst], check=True)
    print(f"-> {dst}  (encuadre x={x} y={y})")


if __name__ == "__main__":
    main()
