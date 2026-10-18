"""Motor de la Fábrica: reels verticales y estáticos con el estilo Orbis Ways.

Uso:
  python3 render.py reel spec.json
  python3 render.py static spec.json

Textos siempre como HTML real (Manrope 800 / Liberation Sans engrosada),
capturados con Playwright y comprobados con QA (no se pisan, zona segura).
"""
import html, json, os, subprocess, sys, tempfile

ENGINE = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.join(ENGINE, "..", "orbisways_style")
W, H = 1080, 1920
REEL_SAFE = {"top": 260, "bottom": 420, "right": 200, "left": 60}

FONTS = f"""
@font-face{{font-family:Manrope;font-weight:800;src:url({STYLE}/fonts/manrope-latin-800-normal.woff2)}}
@font-face{{font-family:LS;font-weight:700;src:url({STYLE}/fonts/LiberationSans-Bold.ttf)}}
"""

END_LINES = {
    "ES": "Tú caminas. Nosotros llevamos tu equipaje.",
    "EN": "You walk. We carry your luggage.",
    "DE": "Du wanderst. Wir tragen dein Gepäck.",
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(cmd[:6]) + "\n" + r.stderr[-2000:])
    return r.stdout


def capture(jobs):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(jobs, f)
    res = json.loads(run(["node", f"{ENGINE}/cap.js", f.name]))
    bad = [r for r in res if not r["ok"]]
    if bad:
        raise RuntimeError("QA de textos falla: " + json.dumps(bad, ensure_ascii=False))
    return res


def esc(s):
    return html.escape(s or "")


# ---------- reels ----------

def text_html(text, pill=None):
    pill_html = f'<div class="t pill" id="pill">{esc(pill)}</div>' if pill else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{W}px;height:{H}px;background:transparent;overflow:hidden}}
.box{{position:absolute;left:90px;right:230px;top:330px;display:flex;flex-direction:column;align-items:flex-start;gap:34px}}
.t{{color:#fff}}
#txt{{font:800 72px/1.08 Manrope;text-shadow:0 3px 3px rgba(0,0,0,.55),0 0 26px rgba(0,0,0,.45)}}
.pill{{background:#1474A4;padding:16px 34px 18px;border-radius:999px;font:800 46px/1 Manrope;white-space:nowrap;box-shadow:0 6px 24px rgba(0,0,0,.35)}}
.grad{{position:absolute;left:0;right:0;top:0;height:1100px;background:linear-gradient(180deg,rgba(0,0,0,.42),rgba(0,0,0,.18) 55%,rgba(0,0,0,0))}}
</style></head><body><div class="grad"></div><div class="box"><div class="t" id="txt">{esc(text)}</div>{pill_html}</div></body></html>"""


def end_html(lang, line=None, web="orbisways.com"):
    line = line or END_LINES.get(lang, END_LINES["EN"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{W}px;height:{H}px;background:#1474A4;overflow:hidden}}
.t{{position:absolute;left:120px;right:120px;text-align:center;color:#fff}}
#logo{{position:absolute;left:50%;top:700px;transform:translateX(-50%);width:560px}}
#f{{top:930px;font:700 48px/1.22 LS;-webkit-text-stroke:2px #fff;paint-order:stroke}}
#w{{top:1100px;font:800 46px/1 Manrope;letter-spacing:.02em}}
</style></head><body><img id="logo" src="{STYLE}/logo/orbisways_logo_white.png">
<div class="t" id="f">{esc(line)}</div><div class="t" id="w">{esc(web)}</div></body></html>"""


def render_reel(spec):
    work = tempfile.mkdtemp(prefix="reel_")
    jobs = []
    for i, tb in enumerate(spec["texts"]):
        p = f"{work}/t{i}.html"
        open(p, "w").write(text_html(tb["text"], spec.get("pill") if i == 0 else None))
        jobs.append({"html": p, "out": f"{work}/t{i}.png", "w": W, "h": H, "safe": REEL_SAFE})
    pe = f"{work}/end.html"
    open(pe, "w").write(end_html(spec["lang"], spec.get("endLine"), spec.get("web", "orbisways.com")))
    jobs.append({"html": pe, "out": f"{work}/end.png", "w": W, "h": H, "safe": {"top": 0, "bottom": 0, "right": 0, "left": 0}})
    capture(jobs)

    # 1) planos normalizados a 1080x1920, 30 fps, sin audio
    parts = []
    for i, s in enumerate(spec["shots"]):
        out = f"{work}/s{i}.mp4"
        cx = s.get("cropx", 0.5)
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H}:(iw-{W})*{cx}:(ih-{H})/2,fps=30,setsar=1,format=yuv420p")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(s.get("ss", 0)), "-t", str(s["dur"]), "-i", s["file"],
             "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
        parts.append(out)
    # tarjeta final 2.6 s
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", "2.6", "-i", f"{work}/end.png",
         "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", f"{work}/end.mp4"])

    # 2) concatenación con corte seco entre planos y fundido corto a la tarjeta final
    lst = f"{work}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{work}/body.mp4"])
    body_dur = sum(s["dur"] for s in spec["shots"])

    # 3) textos encima del cuerpo
    inputs = ["-i", f"{work}/body.mp4"]
    chain, last = [], "0:v"
    for i, tb in enumerate(spec["texts"]):
        inputs += ["-i", f"{work}/t{i}.png"]
        chain.append(f"[{last}][{i + 1}:v]overlay=0:0:enable='between(t,{tb['start']},{tb['end']})'[v{i}]")
        last = f"v{i}"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{last}]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", f"{work}/bodyt.mp4"])

    # 4) fundido a la tarjeta final + audio
    total = body_dur + 2.6 - 0.4
    fc = f"[0:v][1:v]xfade=transition=fade:duration=0.4:offset={body_dur - 0.4:.3f},format=yuv420p[v]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", f"{work}/bodyt.mp4", "-i", f"{work}/end.mp4"]
    if spec.get("music"):
        cmd += ["-i", spec["music"]]
        fc += (f";[2:a]atrim=0:{total:.3f},afade=t=in:d=0.6,afade=t=out:st={total - 1.2:.3f}:d=1.2,"
               f"volume={spec.get('musicVol', 0.8)},loudnorm=I=-14:TP=-1[a]")
    else:
        cmd += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        fc += ";[2:a]anull[a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
            "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", f"{total:.3f}", spec["out"]]
    run(cmd)
    # hoja de fotogramas para QA visual
    sheet = spec["out"].rsplit(".", 1)[0] + "_sheet.jpg"
    run(["ffmpeg", "-v", "error", "-y", "-i", spec["out"], "-vf",
         f"fps={6 / total:.4f},scale=270:-1,tile=6x1", "-frames:v", "1", sheet])
    # portada (primer bloque de texto sobre el primer plano)
    cover = spec["out"].rsplit(".", 1)[0] + "_cover.jpg"
    t0 = (spec["texts"][0]["start"] + spec["texts"][0]["end"]) / 2 if spec["texts"] else 0.5
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.2f}", "-i", spec["out"], "-frames:v", "1", "-q:v", "3", cover])
    return {"out": spec["out"], "sheet": sheet, "cover": cover, "dur": round(total, 2)}


# ---------- estáticos ----------

def static_html(sp):
    w, h = sp["w"], sp["h"]
    k = w / 1080
    pill = f'<div class="t pill" id="pill">{esc(sp["pill"])}</div>' if sp.get("pill") else ""
    sub = f'<div class="t" id="sub">{esc(sp["sub"])}</div>' if sp.get("sub") else ""
    pos = sp.get("objectPosition", "50% 50%")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#0b2230}}
#bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{pos}}}
.grad{{position:absolute;left:0;right:0;bottom:0;height:{int(h * .62)}px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.30) 35%,rgba(0,0,0,.72))}}
.box{{position:absolute;left:{int(70 * k)}px;right:{int(70 * k)}px;bottom:{int(120 * k)}px;display:flex;flex-direction:column;align-items:flex-start;gap:{int(26 * k)}px}}
.t{{color:#fff}}
.pill{{background:#1474A4;padding:{int(14 * k)}px {int(30 * k)}px {int(16 * k)}px;border-radius:999px;font:800 {int(40 * k)}px/1 Manrope;white-space:nowrap}}
#head{{font:800 {int(sp.get("headSize", 78) * k)}px/1.06 Manrope;text-shadow:0 2px 18px rgba(0,0,0,.35)}}
#sub{{font:700 {int(40 * k)}px/1.22 LS;-webkit-text-stroke:{max(1, int(2 * k))}px #fff;paint-order:stroke}}
#web{{position:absolute;right:{int(70 * k)}px;bottom:{int(48 * k)}px;font:800 {int(30 * k)}px/1 Manrope;letter-spacing:.03em;opacity:.95}}
</style></head><body><img id="bg" src="{sp["image"]}"><div class="grad"></div>
<div class="box">{pill}<div class="t" id="head">{esc(sp["headline"])}</div>{sub}</div>
<div class="t" id="web">{esc(sp.get("web", "orbisways.com"))}</div></body></html>"""


def render_static(sp):
    work = tempfile.mkdtemp(prefix="st_")
    p = f"{work}/s.html"
    open(p, "w").write(static_html(sp))
    png = f"{work}/s.png"
    m = int(40 * sp["w"] / 1080)
    capture([{"html": p, "out": png, "w": sp["w"], "h": sp["h"], "safe": {"top": m, "bottom": m // 2, "right": m, "left": m}}])
    run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", sp["out"]])
    return {"out": sp["out"]}


if __name__ == "__main__":
    kind, path = sys.argv[1], sys.argv[2]
    spec = json.load(open(path))
    print(json.dumps(render_reel(spec) if kind == "reel" else render_static(spec)))
