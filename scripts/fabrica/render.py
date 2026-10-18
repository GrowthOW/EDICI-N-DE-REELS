"""Motor de la Fábrica: reels (también multipantalla), stories, estáticos, carruseles y comparativas.

Uso:
  python3 render.py reel spec.json
  python3 render.py static spec.json

Textos siempre como HTML real (Manrope 800 / Liberation Sans engrosada),
capturados con Playwright y comprobados con QA (no se pisan, zona segura).

Redes orgánicas (Iván, 18 oct): sin web, sin logo y sin cartela final de marca.
La ruta va como etiqueta de ubicación discreta, como las de la propia red.
"""
import html, json, os, subprocess, sys, tempfile

ENGINE = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.join(ENGINE, "..", "orbisways_style")
W, H = 1080, 1920
REEL_SAFE = {"top": 260, "bottom": 420, "right": 200, "left": 60}
STORY_SAFE = {"top": 250, "bottom": 340, "right": 60, "left": 60}
GAP = 6  # separación blanca entre pantallas

FONTS = f"""
@font-face{{font-family:Manrope;font-weight:800;src:url({STYLE}/fonts/manrope-latin-800-normal.woff2)}}
@font-face{{font-family:LS;font-weight:700;src:url({STYLE}/fonts/LiberationSans-Bold.ttf)}}
"""
PIN = ('<svg viewBox="0 0 24 24" width="{s}" height="{s}" style="flex:none"><path fill="#fff" '
       'd="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>')


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


def tag_html(text, size, cls="t tag", ident="tag"):
    """Etiqueta de ubicación: chip translúcido con chincheta, sin color de marca."""
    if not text:
        return ""
    return (f'<div class="{cls}" id="{ident}" style="display:inline-flex;align-items:center;gap:{int(size * .35)}px;'
            f'background:rgba(0,0,0,.42);padding:{int(size * .32)}px {int(size * .62)}px;border-radius:999px;'
            f'font:800 {size}px/1 Manrope;white-space:nowrap">{PIN.format(s=int(size * 1.05))}<span>{esc(text)}</span></div>')


# ---------- reels y stories en vídeo ----------

def text_html(text, tag=None, labels=None, layout="full", top=330):
    """Bloque de texto del reel (y etiquetas de cada pantalla en los formatos multipantalla)."""
    lab = ""
    if labels:
        n = len(labels)
        if layout == "grid4":
            pos = [(60, 0), (W // 2 + 30, 0), (60, H // 2), (W // 2 + 30, H // 2)]
            ph = H // 2
        else:
            ph = H // n
            pos = [(60, i * ph) for i in range(n)]
        for i, (lt, (x, y)) in enumerate(zip(labels, pos)):
            if not lt:
                continue
            # la etiqueta de cada pantalla va abajo a la izquierda de su pantalla, dentro de la zona segura
            yb = min(y + ph - 60, H - REEL_SAFE["bottom"] - 10)
            mw = min(W - REEL_SAFE["right"] - x, W // 2 - 90) if layout == "grid4" else 760
            fs = 34 if layout == "grid4" else 44
            lab += (f'<div class="t lab" id="lab{i}" style="position:absolute;left:{x}px;top:{yb}px;transform:translateY(-100%);'
                    f'background:#fff;color:#111;padding:10px 20px 12px;border-radius:12px;font:800 {fs}px/1.05 Manrope;'
                    f'box-sizing:border-box;max-width:{mw}px">{esc(lt)}</div>')
    txt = f'<div class="t" id="txt">{esc(text)}</div>' if text else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{W}px;height:{H}px;background:transparent;overflow:hidden}}
.box{{position:absolute;left:90px;right:230px;top:{top}px;display:flex;flex-direction:column;align-items:flex-start;gap:28px}}
.t{{color:#fff}}
#txt{{font:800 70px/1.08 Manrope;text-shadow:0 3px 3px rgba(0,0,0,.55),0 0 26px rgba(0,0,0,.45)}}
.grad{{position:absolute;left:0;right:0;top:0;height:1000px;background:linear-gradient(180deg,rgba(0,0,0,.40),rgba(0,0,0,.14) 55%,rgba(0,0,0,0))}}
</style></head><body>{'<div class="grad"></div>' if text else ''}<div class="box">{txt}{tag_html(tag, 38) if tag else ''}</div>{lab}</body></html>"""


def panel_geom(layout):
    if layout == "split":
        h = (H - GAP) // 2
        return [(W, h)] * 2
    if layout == "triple":
        h = (H - 2 * GAP) // 3
        return [(W, h)] * 3
    if layout == "grid4":
        w, h = (W - GAP) // 2, (H - GAP) // 2
        return [(w, h)] * 4
    return [(W, H)]


def segment(shot, out, work, idx):
    """Un tramo del reel: una pantalla o varias a la vez (split, triple, grid4)."""
    layout = shot.get("layout", "full")
    panels = shot.get("panels") or [shot]
    geo = panel_geom(layout)
    if len(panels) != len(geo):
        raise RuntimeError(f"el formato {layout} necesita {len(geo)} pantallas")
    parts = []
    for j, (p, (pw, ph)) in enumerate(zip(panels, geo)):
        cx, cy = p.get("cropx", 0.5), p.get("cropy", 0.5)
        po = f"{work}/s{idx}_{j}.mp4"
        vf = (f"scale={pw}:{ph}:force_original_aspect_ratio=increase,"
              f"crop={pw}:{ph}:(iw-{pw})*{cx}:(ih-{ph})*{cy},fps=30,setsar=1,format=yuv420p")
        # si el tramo pedido se sale del clip, se adelanta para que el plano dure lo previsto
        clip_dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p["file"]]).strip() or 0)
        ss = max(0.0, min(float(p.get("ss", 0)), clip_dur - shot["dur"] - 0.1))
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.2f}", "-t", str(shot["dur"]), "-i", p["file"],
             "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", po])
        parts.append(po)
    if layout == "full":
        os.replace(parts[0], out)
        return
    ins = sum((["-i", p] for p in parts), [])
    pad = f"pad=iw:ih+{GAP}:0:0:white"
    if layout in ("split", "triple"):
        n = len(parts)
        fc = ";".join(f"[{k}:v]{pad if k < n - 1 else 'null'}[p{k}]" for k in range(n)) + ";" + "".join(f"[p{k}]" for k in range(n)) + f"vstack={n},scale={W}:{H}[v]"
    else:  # grid4
        padw = f"pad=iw+{GAP}:ih:0:0:white"
        fc = (f"[0:v]{padw}[a];[a][1:v]hstack[top];[2:v]{padw}[b];[b][3:v]hstack[bot];"
              f"[top]{pad}[t2];[t2][bot]vstack,scale={W}:{H}[v]")
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])


def render_reel(spec):
    """Reel o story en vídeo 1080x1920. Sin cartela final: termina en el último plano con un fundido corto."""
    work = tempfile.mkdtemp(prefix="reel_")
    story = spec.get("kind") == "story"
    safe = STORY_SAFE if story else REEL_SAFE
    # etiquetas por pantalla: las del primer tramo multipantalla se mantienen mientras dure ese formato
    jobs, overlays = [], []
    t_acc, seg_times = 0.0, []
    for s in spec["shots"]:
        seg_times.append((t_acc, t_acc + s["dur"], s.get("layout", "full"), s.get("labels")))
        t_acc += s["dur"]
    body_dur = t_acc
    for i, tb in enumerate(spec["texts"]):
        mid = (tb["start"] + tb["end"]) / 2
        seg = next((x for x in seg_times if x[0] <= mid < x[1]), seg_times[-1])
        p = f"{work}/t{i}.html"
        open(p, "w").write(text_html(tb["text"], spec.get("tag") if i == 0 else None, seg[3], seg[2], top=300 if story else 330))
        jobs.append({"html": p, "out": f"{work}/t{i}.png", "w": W, "h": H, "safe": safe})
        overlays.append((f"{work}/t{i}.png", tb["start"], tb["end"]))
    # tramos multipantalla sin texto propio: sus etiquetas también se ven
    for k, (a, b, lay, labels) in enumerate(seg_times):
        covered = any(tb["start"] < b and tb["end"] > a for tb in spec["texts"])
        if labels and not covered:
            p = f"{work}/l{k}.html"
            open(p, "w").write(text_html("", None, labels, lay))
            jobs.append({"html": p, "out": f"{work}/l{k}.png", "w": W, "h": H, "safe": safe})
            overlays.append((f"{work}/l{k}.png", a, b))
    if jobs:
        capture(jobs)

    parts = []
    for i, s in enumerate(spec["shots"]):
        out = f"{work}/s{i}.mp4"
        segment(s, out, work, i)
        parts.append(out)
    lst = f"{work}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{work}/body.mp4"])

    inputs = ["-i", f"{work}/body.mp4"]
    chain, last = [], "0:v"
    for i, (png, a, b) in enumerate(overlays):
        inputs += ["-i", png]
        chain.append(f"[{last}][{i + 1}:v]overlay=0:0:enable='between(t,{a},{b})'[v{i}]")
        last = f"v{i}"
    fade = f"fade=t=out:st={body_dur - 0.35:.3f}:d=0.35"
    fc = (";".join(chain) + f";[{last}]{fade},format=yuv420p[v]") if chain else f"[0:v]{fade},format=yuv420p[v]"
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs]
    na = len(overlays) + 1
    if spec.get("music"):
        cmd += ["-i", spec["music"]]
        fc += (f";[{na}:a]atrim=0:{body_dur:.3f},afade=t=in:d=0.6,afade=t=out:st={body_dur - 1.2:.3f}:d=1.2,"
               f"volume={spec.get('musicVol', 0.8)},loudnorm=I=-14:TP=-1[a]")
    else:
        cmd += ["-f", "lavfi", "-t", f"{body_dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        fc += f";[{na}:a]anull[a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
            "-crf", "21", "-maxrate", "5M", "-bufsize", "10M", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
            "-t", f"{body_dur:.3f}", spec["out"]]
    run(cmd)
    sheet = spec["out"].rsplit(".", 1)[0] + "_sheet.jpg"
    run(["ffmpeg", "-v", "error", "-y", "-i", spec["out"], "-vf", f"fps={6 / body_dur:.4f},scale=270:-1,tile=6x1", "-frames:v", "1", sheet])
    cover = spec["out"].rsplit(".", 1)[0] + "_cover.jpg"
    t0 = (spec["texts"][0]["start"] + spec["texts"][0]["end"]) / 2 if spec["texts"] else 0.5
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.2f}", "-i", spec["out"], "-frames:v", "1", "-q:v", "3", cover])
    return {"out": spec["out"], "sheet": sheet, "cover": cover, "dur": round(body_dur, 2)}


# ---------- estáticos, carruseles, comparativas y stories en imagen ----------

def static_html(sp):
    w, h = sp["w"], sp["h"]
    k = w / 1080
    story = sp.get("story")
    sub = f'<div class="t" id="sub">{esc(sp["sub"])}</div>' if sp.get("sub") else ""
    pos = sp.get("objectPosition", "50% 50%")
    counter = (f'<div class="t" id="cnt" style="position:absolute;right:{int(56 * k)}px;top:{int(52 * k)}px;'
               f'font:800 {int(30 * k)}px/1 Manrope;background:rgba(0,0,0,.38);padding:{int(10 * k)}px {int(18 * k)}px;'
               f'border-radius:999px">{esc(sp["counter"])}</div>') if sp.get("counter") else ""
    # en stories el texto va arriba-centro (lo de abajo lo tapan la respuesta y los stickers)
    box = (f"left:{int(70 * k)}px;right:{int(70 * k)}px;top:{int(330 * k)}px" if story
           else f"left:{int(70 * k)}px;right:{int(70 * k)}px;bottom:{int(90 * k)}px")
    grad = ("top:0;height:{0}px;background:linear-gradient(180deg,rgba(0,0,0,.62),rgba(0,0,0,.38) 45%,rgba(0,0,0,0))".format(int(h * .6)) if story
            else "bottom:0;height:{0}px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.30) 35%,rgba(0,0,0,.72))".format(int(h * .62)))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#0b2230}}
#bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{pos}}}
.grad{{position:absolute;left:0;right:0;{grad}}}
.box{{position:absolute;{box};display:flex;flex-direction:column;align-items:flex-start;gap:{int(24 * k)}px}}
.t{{color:#fff}}
#head{{font:800 {int(sp.get("headSize", 78) * k)}px/1.06 Manrope;text-shadow:0 2px 18px rgba(0,0,0,.35)}}
#sub{{font:700 {int(40 * k)}px/1.22 LS;-webkit-text-stroke:{max(1, int(2 * k))}px #fff;paint-order:stroke;text-shadow:0 2px 12px rgba(0,0,0,.55)}}
</style></head><body><img id="bg" src="{sp["image"]}"><div class="grad"></div>
<div class="box">{tag_html(sp.get("tag"), int(34 * k))}<div class="t" id="head">{esc(sp["headline"])}</div>{sub}</div>{counter}</body></html>"""


def render_static(sp):
    work = tempfile.mkdtemp(prefix="st_")
    p = f"{work}/s.html"
    open(p, "w").write(static_html(sp))
    png = f"{work}/s.png"
    m = int(40 * sp["w"] / 1080)
    safe = STORY_SAFE if sp.get("story") else {"top": m, "bottom": m // 2, "right": m, "left": m}
    capture([{"html": p, "out": png, "w": sp["w"], "h": sp["h"], "safe": safe}])
    run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", sp["out"]])
    return {"out": sp["out"]}


def render_carousel(sp):
    """Carrusel de Instagram (1080x1350): portada con la ubicación, una idea por lámina y cierre suave."""
    n, outs = len(sp["slides"]), []
    for i, sl in enumerate(sp["slides"]):
        out = f'{sp["out_prefix"]}_{i + 1}.jpg'
        render_static({"w": 1080, "h": 1350, "image": sl["image"], "headline": sl.get("headline", ""), "sub": sl.get("sub", ""),
                       "tag": sp.get("tag") if i == 0 else None, "objectPosition": sl.get("objectPosition", "50% 50%"),
                       "headSize": 84 if i == 0 else 72, "counter": f"{i + 1}/{n}", "out": out})
        outs.append(out)
    return {"out": outs}


def compare_html(sp):
    """Comparativa de dos rutas parecidas: dos fotos (arriba/abajo), su nombre y 2-3 datos cada una."""
    w, h = sp["w"], sp["h"]
    k = w / 1080
    hh = (h - GAP) // 2

    def half(i, side):
        y = 0 if i == 0 else hh + GAP
        facts = "".join(f'<div class="t f" id="f{i}{j}">{esc(x)}</div>' for j, x in enumerate(side.get("facts", [])[:3]))
        return (f'<div style="position:absolute;left:0;top:{y}px;width:{w}px;height:{hh}px;overflow:hidden">'
                f'<img src="{side["image"]}" style="width:100%;height:100%;object-fit:cover;object-position:{side.get("objectPosition", "50% 50%")}">'
                f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.62),rgba(0,0,0,.1) 70%)"></div>'
                f'<div style="position:absolute;left:{int(60 * k)}px;bottom:{int(44 * k)}px;display:flex;flex-direction:column;gap:{int(10 * k)}px">'
                f'<div class="t n" id="n{i}">{esc(side["name"])}</div>{facts}</div></div>')
    cnt = sp.get("counter")
    head = (f'<div class="t" id="head" style="position:absolute;left:{int(60 * k)}px;right:{int((170 if cnt else 60) * k)}px;top:{int(46 * k)}px;'
            f'font:800 {int(54 * k)}px/1.08 Manrope;text-shadow:0 2px 14px rgba(0,0,0,.6)">{esc(sp.get("headline"))}</div>') if sp.get("headline") else ""
    counter = (f'<div class="t" id="cnt" style="position:absolute;right:{int(56 * k)}px;top:{int(52 * k)}px;'
               f'font:800 {int(30 * k)}px/1 Manrope;background:rgba(0,0,0,.38);padding:{int(10 * k)}px {int(18 * k)}px;'
               f'border-radius:999px">{esc(cnt)}</div>') if cnt else ""
    # el «vs» va a la derecha de la línea de corte para no pisar los datos de la foto de arriba
    vs = (f'<div class="t" id="vs" style="position:absolute;right:{int(70 * k)}px;top:{hh + GAP // 2}px;transform:translateY(-50%);'
          f'width:{int(96 * k)}px;height:{int(96 * k)}px;border-radius:50%;background:#fff;color:#111;display:grid;place-items:center;'
          f'font:800 {int((36 if len(sp.get("vs", "vs")) <= 2 else 26) * k)}px/1 Manrope">{esc(sp.get("vs", "vs"))}</div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#fff}}
.t{{color:#fff}} .n{{font:800 {int(sp.get("nameSize", 60) * k)}px/1.05 Manrope;text-shadow:0 2px 14px rgba(0,0,0,.5)}}
.f{{font:700 {int(34 * k)}px/1.2 LS;-webkit-text-stroke:{max(1, int(1.5 * k))}px #fff;paint-order:stroke;text-shadow:0 2px 10px rgba(0,0,0,.5)}}
</style></head><body>{half(0, sp["a"])}{half(1, sp["b"])}{head}{vs}{counter}</body></html>"""


def render_compare(sp):
    work = tempfile.mkdtemp(prefix="cmp_")
    p = f"{work}/c.html"
    open(p, "w").write(compare_html(sp))
    png = f"{work}/c.png"
    m = int(30 * sp["w"] / 1080)
    capture([{"html": p, "out": png, "w": sp["w"], "h": sp["h"], "safe": {"top": m, "bottom": m // 2, "right": m, "left": m}}])
    run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", sp["out"]])
    return {"out": sp["out"]}


def render_compare_carousel(sp):
    """Comparativa en carrusel (Iván, 18 oct: «no puede ser solo una foto»): portada partida y una lámina partida por aspecto."""
    n, outs = len(sp["slides"]), []
    for i, sl in enumerate(sp["slides"]):
        out = f'{sp["out_prefix"]}_{i + 1}.jpg'
        render_compare({"w": sp.get("w", 1080), "h": sp.get("h", 1350), "headline": sl.get("headline", ""), "vs": sp.get("vs", "vs"),
                        "a": sl["a"], "b": sl["b"], "counter": f"{i + 1}/{n}", "nameSize": 60 if i == 0 else 46, "out": out})
        outs.append(out)
    return {"out": outs}


if __name__ == "__main__":
    kind, path = sys.argv[1], sys.argv[2]
    spec = json.load(open(path))
    print(json.dumps(render_reel(spec) if kind == "reel" else render_static(spec)))
