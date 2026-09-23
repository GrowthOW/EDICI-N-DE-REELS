"""Monta el video 16:9 del TMB a partir de edl.json.

Uso (desde cualquier carpeta):
  python3 build_edit.py bg                  # fondo (clips + cámaras lentas + transiciones) y timeline.json
  python3 build_edit.py overlay [ini fin]   # capa gráfica (textos, mapa, cierre) -> overlay_frames/
  python3 build_edit.py compose <salida.mp4>
  python3 build_edit.py preview <seg> [<seg> ...]   # hoja con frames de prueba -> preview.jpg

El overlay se puede lanzar por tramos de frames (ini fin) para no pasar del
timeout; los frames que no cambian se enlazan en vez de volver a capturarse.
"""
import glob, json, math, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EDL = json.load(open(os.path.join(HERE, "edl.json")))
FPS, W, H, TRANS = EDL["fps"], EDL["w"], EDL["h"], EDL["trans"]
BG = os.path.join(HERE, "background.mp4")
TL_PATH = os.path.join(HERE, "timeline.json")
FRAMES = os.path.join(HERE, "overlay_frames")
GRADE = "eq=contrast=1.06:brightness=-0.015:saturation=0.95"


def clip_dur(c):
    return (c["out"] - c["in"]) / c.get("speed", 1.0) + c.get("hold", 0.0)


def build_timeline():
    clips = EDL["clips"]; n = len(clips); tl = []; mount = 0.0
    for i, c in enumerate(clips):
        d = clip_dur(c)
        full_start = mount if i == 0 else mount + TRANS
        full_end = mount + d - (0 if i == n - 1 else TRANS)
        tl.append({"key": c["key"], "mountStart": round(mount, 4), "fullStart": round(full_start, 4),
                   "fullEnd": round(full_end, 4), "mountEnd": round(mount + d, 4)})
        mount = full_end
    return tl


def cmd_bg():
    clips = EDL["clips"]; inputs = []; fl = []
    for i, c in enumerate(clips):
        src_d = c["out"] - c["in"]
        inputs += ["-ss", str(c["in"]), "-t", str(src_d), "-i", os.path.join(REPO, c["src"])]
        chain = [f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={W}:{H}", "setsar=1"]
        sp = c.get("speed", 1.0)
        if sp != 1.0:
            chain.append(f"setpts=PTS/{sp}")
            if c.get("interp"):
                chain.append(f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1")
            elif c.get("fx") == "mapbg":
                chain.append(f"minterpolate=fps={FPS}:mi_mode=blend")
        chain += [f"fps={FPS}", "setpts=PTS-STARTPTS", "format=yuv420p", GRADE]
        if c.get("fx") == "mapbg":
            chain += ["gblur=sigma=7", "eq=brightness=-0.16:saturation=0.8"]
        if c.get("hold"):
            chain.append(f"tpad=stop_mode=clone:stop_duration={c['hold']}")
        fl.append(f"[{i}:v]" + ",".join(chain) + f"[v{i}]")
    tl = build_timeline(); prev = "v0"
    for i in range(1, len(clips)):
        off = tl[i]["mountStart"]
        fl.append(f"[{prev}][v{i}]xfade=transition=fade:duration={TRANS}:offset={off:.4f}[x{i}]")
        prev = f"x{i}"
    json.dump({"total": tl[-1]["mountEnd"], "timeline": tl}, open(TL_PATH, "w"), indent=2)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stats", *inputs, "-filter_complex", ";".join(fl),
                    "-map", f"[{prev}]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                    "-pix_fmt", "yuv420p", BG], check=True)
    print("DONE bg", tl[-1]["mountEnd"])


def page_html():
    tl = json.load(open(TL_PATH))["timeline"]
    data = {"timeline": tl, "edl": EDL, "map_data": json.load(open(os.path.join(HERE, "..", "map", "map_data.json")))}
    html = open(os.path.join(HERE, "overlay_template.html")).read().replace("__DATA_JSON__", json.dumps(data))
    path = os.path.join(HERE, "overlay.html"); open(path, "w").write(html)
    return path


def browser(p):
    kw = {}
    exes = sorted(glob.glob(os.path.join(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), "chromium-*", "chrome-linux", "chrome")))
    if exes:
        kw["executable_path"] = exes[-1]
    b = p.chromium.launch(**kw)
    pg = b.new_page(viewport={"width": W, "height": H})
    pg.on("pageerror", lambda e: print("ERROR JS:", e))
    pg.goto("file://" + page_html())
    pg.wait_for_function("window.__READY__ === true")
    return b, pg


def cmd_overlay(start=None, end=None):
    from playwright.sync_api import sync_playwright
    total = json.load(open(TL_PATH))["total"]; n = int(math.ceil(total * FPS))
    start = int(start or 0); end = min(int(end or n), n)
    os.makedirs(FRAMES, exist_ok=True)
    if start == 0:
        for f in glob.glob(os.path.join(FRAMES, "*.png")):
            os.remove(f)
    with sync_playwright() as p:
        b, pg = browser(p)
        stage = pg.locator("#stage"); last_sig = None; last_path = None; shots = 0
        for i in range(start, end):
            sig = pg.evaluate(f"window.renderAtTime({i / FPS})")
            path = os.path.join(FRAMES, f"ov_{i:05d}.png")
            if sig == last_sig and last_path:
                shutil.copyfile(last_path, path)
            else:
                stage.screenshot(path=path, omit_background=True); shots += 1
                last_sig, last_path = sig, path
            if i % 150 == 0:
                print(f"frame {i}/{n}", flush=True)
        b.close()
    print(f"DONE overlay {start}-{end} de {n} ({shots} capturas)")


def cmd_compose(out):
    total = json.load(open(TL_PATH))["total"]
    music = os.path.join(REPO, EDL["music"])
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stats", "-i", BG,
                    "-framerate", str(FPS), "-i", os.path.join(FRAMES, "ov_%05d.png"),
                    "-ss", str(EDL.get("music_start", 0)), "-t", str(total), "-i", music,
                    "-filter_complex",
                    f"[0:v][1:v]overlay=0:0:format=auto,fade=t=out:st={total-0.6:.3f}:d=0.6[v];"
                    f"[2:a]afade=t=in:d=0.5,afade=t=out:st={total-2:.3f}:d=2[a]",
                    "-map", "[v]", "-map", "[a]", "-t", str(total),
                    "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "19",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print("DONE ->", out)


def cmd_preview(times):
    from playwright.sync_api import sync_playwright
    tmp = os.path.join(HERE, "cache"); os.makedirs(tmp, exist_ok=True); tiles = []
    with sync_playwright() as p:
        b, pg = browser(p)
        for t in times:
            pg.evaluate(f"window.renderAtTime({t})")
            png = os.path.join(tmp, f"pv_{t}.png"); pg.locator("#stage").screenshot(path=png, omit_background=True)
            jpg = os.path.join(tmp, f"pv_{t}.jpg")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", BG, "-i", png, "-filter_complex",
                            f"[0:v][1:v]overlay,scale=640:-2,drawtext=text='{t}s':x=10:y=10:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6",
                            "-frames:v", "1", jpg], check=True)
            tiles.append(jpg)
        b.close()
    cols = 3; rows = [tiles[i:i+cols] for i in range(0, len(tiles), cols)]
    row_imgs = []
    for r, row in enumerate(rows):
        while len(row) < cols: row.append(row[-1])
        ri = os.path.join(tmp, f"row{r}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", *sum([["-i", x] for x in row], []), "-filter_complex", f"hstack={cols}", ri], check=True)
        row_imgs.append(ri)
    out = os.path.join(HERE, "preview.jpg")
    if len(row_imgs) == 1: shutil.copyfile(row_imgs[0], out)
    else: subprocess.run(["ffmpeg", "-y", "-v", "error", *sum([["-i", x] for x in row_imgs], []), "-filter_complex", f"vstack={len(row_imgs)}", out], check=True)
    print("->", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(1)
    {"bg": lambda: cmd_bg(),
     "overlay": lambda: cmd_overlay(*a[1:3]),
     "compose": lambda: cmd_compose(a[1]),
     "preview": lambda: cmd_preview([float(x) for x in a[1:]])}[a[0]]()
