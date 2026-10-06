"""Renderiza el banner de YouTube (2560×1440) y una hoja de prueba por dispositivo.

Uso: python3 render.py [cresta panoramica mosaico blanco]
Salida: salida/banner_<variante>.jpg (para subir a YouTube, < 6 MB)
        salida/prueba_<variante>.jpg (lienzo TV con la zona segura marcada,
        franja de escritorio 2560×423 y recorte de móvil 1546×423)
"""
import glob, os, subprocess, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "salida")
VARIANTES = sys.argv[1:] or ["cresta", "panoramica", "mosaico", "blanco"]


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    kw = {}
    exes = sorted(glob.glob(os.path.join(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), "chromium-*", "chrome-linux", "chrome")))
    if exes:
        kw["executable_path"] = exes[-1]
    b = p.chromium.launch(**kw)
    pg = b.new_page(viewport={"width": 2560, "height": 1440})
    for v in VARIANTES:
        pg.goto(f"file://{HERE}/banner.html?v={v}")
        pg.wait_for_function("window.__READY__ === true")
        png = os.path.join(OUT, f"banner_{v}.png")
        pg.screenshot(path=png)
        jpg = os.path.join(OUT, f"banner_{v}.jpg")
        ff("-i", png, "-q:v", "2", jpg)
        os.remove(png)
        # hoja de prueba: TV (con zona segura en amarillo) / escritorio / móvil
        ff("-i", jpg, "-filter_complex",
           "[0]split=3[a][b][c];"
           "[a]drawbox=x=507:y=508:w=1546:h=423:color=yellow@0.9:t=6,"
           "drawbox=x=0:y=508:w=2560:h=423:color=white@0.5:t=3,scale=1280:-2,"
           "drawtext=text='TV (lienzo entero) - amarillo zona segura / blanco escritorio':x=16:y=16:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6[tv];"
           "[b]crop=2560:423:0:508,scale=1280:-2,"
           "drawtext=text='Escritorio':x=16:y=12:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6[pc];"
           "[c]crop=1546:423:507:508,scale=773:-2,pad=1280:ih:(ow-iw)/2:0:color=0x111111,"
           "drawtext=text='Movil':x=16:y=12:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6[mv];"
           "[tv][pc][mv]vstack=3", "-q:v", "3", os.path.join(OUT, f"prueba_{v}.jpg"))
        print("->", jpg)
    b.close()
