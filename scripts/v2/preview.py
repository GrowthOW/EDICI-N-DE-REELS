"""Vista previa rápida del reel: compone cartelas + video en unos segundos
y los monta en una hoja, sin hacer el render completo.

Uso:
  python3 preview.py [content.json] [segundo ...]

Ejemplos:
  python3 preview.py                          # inglés, un frame por segmento
  python3 preview.py content_de.json 8 14.5   # alemán, segundos concretos

Necesita background.mp4 (lo genera build_all.sh o build_background.py).
Genera preview.jpg y avisa si algún texto se sale del cuadro.
"""
import glob, json, os, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
content_path = os.path.join(HERE, "content.json")
if args and args[0].endswith(".json"):
    content_path = os.path.abspath(args.pop(0))
tl = json.load(open(os.path.join(HERE, "timeline.json")))
bg = os.path.join(HERE, "background.mp4")
if not os.path.exists(bg):
    sys.exit("Falta background.mp4: ejecuta antes  python3 build_background.py")

# por defecto: un momento de cada segmento, con las cartelas ya reveladas
times = [float(a) for a in args] or [
    round(min(s["fullStart"] + 1.8, s["mountEnd"] - 0.3), 2) for s in tl["timeline"]]

html = open(os.path.join(HERE, "overlay_template.html")).read()
html = html.replace("__TIMELINE_JSON__", json.dumps(tl)).replace(
    "__CONTENT_JSON__", json.dumps(json.load(open(content_path))))
page_path = os.path.join(HERE, "_preview.html")
open(page_path, "w").write(html)

tmp = tempfile.mkdtemp()
launch = {}
exes = sorted(glob.glob(os.path.join(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), "chromium-*", "chrome-linux", "chrome")))
if exes:
    launch["executable_path"] = exes[-1]
try:
    with sync_playwright() as p:
        b = p.chromium.launch(**launch)
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("ERROR JS:", e))
        pg.goto("file://" + page_path)
        pg.wait_for_function("window.__READY__ === true")
        for t in times:
            pg.evaluate(f"window.renderAtTime({t})")
            pg.locator("#stage").screenshot(path=os.path.join(tmp, f"ov_{t}.png"), omit_background=True)
        overflow = pg.evaluate("""() => { const out=[]; document.querySelectorAll('.seg').forEach(s=>{s.style.display='block';
            s.querySelectorAll('.badges,.pill,.hline,.country,.o-hline,.o-cta').forEach(e=>{
              if (e.getBoundingClientRect().right > 1010) out.push(s.dataset.key+': "'+e.textContent.trim()+'"');});}); return out; }""")
        b.close()
finally:
    os.remove(page_path)

tiles = []
for t in times:
    out = os.path.join(tmp, f"c_{t}.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", bg, "-i", os.path.join(tmp, f"ov_{t}.png"),
                    "-filter_complex", f"[0:v][1:v]overlay,scale=360:-2,drawtext=text='{t}s':x=10:y=10:fontsize=24:"
                    "fontcolor=white:box=1:boxcolor=black@0.6", "-frames:v", "1", out], check=True)
    tiles.append(out)
dest = os.path.join(HERE, "preview.jpg")
inputs = sum([["-i", p] for p in tiles], [])
stack = f"hstack={len(tiles)}" if len(tiles) > 1 else "null"
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", stack, dest], check=True)
print("->", dest)
print("OK: ningún texto se sale del cuadro" if not overflow else "OJO, texto que se sale del cuadro:\n  " + "\n  ".join(overflow))
