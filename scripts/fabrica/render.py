"""Motor de la Fábrica: reels (también multipantalla), stories, estáticos, carruseles y comparativas.

Uso:
  python3 render.py reel spec.json
  python3 render.py static spec.json

Textos siempre como HTML real (Nunito en titulares y chips, Mulish en el texto; sustitutos
de Caros Soft y Museo Sans del brandbook, Iván 20 oct), con el azul de marca #1376A4 en los chips,
capturados con Playwright y comprobados con QA (no se pisan, zona segura).

Redes orgánicas (Iván, 18 oct): sin web, sin logo y sin cartela final de marca.
La ruta va como etiqueta de ubicación discreta, como las de la propia red.
"""
import atexit, html, json, os, shutil, subprocess, sys, tempfile


def workdir(prefix):
    """Carpeta temporal de montaje que se borra al terminar (dejaba GB de restos en /tmp)."""
    d = tempfile.mkdtemp(prefix=prefix)
    atexit.register(shutil.rmtree, d, True)
    return d

ENGINE = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.join(ENGINE, "..", "orbisways_style")
W, H = 1080, 1920
BRAND = "#1376A4"  # azul oscuro del brandbook: chips de ruta y rótulos de pantalla
# zona segura de Instagram sobre 1080x1920 (Ana, 19 oct; fabrica/zona-segura): top 210, laterales 48/52, bottom 370;
# desde y=1118 el borde derecho baja a x=921 (botones de la app). cap.js lo comprueba con notchX/notchY.
REEL_SAFE = {"top": 210, "bottom": 370, "right": 52, "left": 48, "notchX": 921, "notchY": 1118}
STORY_SAFE = dict(REEL_SAFE)
NOTCH_RIGHT = W - 921  # margen derecho de todo bloque que baje de y=1118
GAP = 6  # separación blanca entre pantallas

FONTS = f"""
@font-face{{font-family:Head;font-weight:800;src:url({STYLE}/fonts/nunito-latin-800-normal.woff2)}}
@font-face{{font-family:Head;font-weight:700;src:url({STYLE}/fonts/nunito-latin-700-normal.woff2)}}
@font-face{{font-family:Body;font-weight:700;src:url({STYLE}/fonts/mulish-latin-700-normal.woff2)}}
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
    """Etiqueta de ubicación: chip azul de marca con chincheta, en Nunito Bold (brandbook: chip azul con la ruta)."""
    if not text:
        return ""
    return (f'<div class="{cls}" id="{ident}" style="display:inline-flex;align-items:center;gap:{int(size * .35)}px;'
            f'background:{BRAND};padding:{int(size * .32)}px {int(size * .62)}px;border-radius:999px;'
            f'font:800 {size}px/1.15 Head;max-width:100%;box-sizing:border-box">{PIN.format(s=int(size * 1.05))}<span style="text-wrap:balance">{esc(text)}</span></div>')


def badge_html(text, size, ident="badge"):
    """Etiqueta de evento (Iván, 19 oct: el Año Santo 2027 tiene que verse). En azul de marca con texto blanco,
    como el resto de chips (Iván, 20 oct: «limpio y sobrio», solo texto blanco y azul Orbis)."""
    if not text:
        return ""
    return (f'<div class="t badge" id="{ident}" style="display:inline-block;background:{BRAND};color:#fff;'
            f'padding:{int(size * .34)}px {int(size * .62)}px {int(size * .3)}px;border-radius:{int(size * .3)}px;'
            f'font:800 {size}px/1 Head;letter-spacing:.04em;text-transform:uppercase;white-space:nowrap;'
            f'box-shadow:0 4px 18px rgba(34,34,34,.28)">{esc(text)}</div>')


# ---------- reels y stories en vídeo ----------

def text_html(text, tag=None, labels=None, layout="full", top=330, badge=None):
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
            yb = min(y + ph - 60, H - REEL_SAFE["bottom"] - 30)
            mw = min(W - NOTCH_RIGHT - x, W // 2 - 90) if layout == "grid4" else 760
            fs = 34 if layout == "grid4" else 44
            lab += (f'<div class="t lab" id="lab{i}" style="position:absolute;left:{x}px;top:{yb}px;transform:translateY(-100%);'
                    f'background:{BRAND};color:#fff;padding:10px 20px 12px;border-radius:12px;font:700 {fs}px/1.05 Head;'
                    f'box-sizing:border-box;max-width:{mw}px">{esc(lt)}</div>')
    txt = f'<div class="t" id="txt">{esc(text)}</div>' if text else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{W}px;height:{H}px;background:transparent;overflow:hidden}}
.box{{position:absolute;left:80px;right:{NOTCH_RIGHT + 40}px;top:{top}px;display:flex;flex-direction:column;align-items:flex-start;gap:28px}}
.t{{color:#fff}}
#txt{{font:800 70px/1.08 Head;text-shadow:0 3px 3px rgba(34,34,34,.55),0 0 26px rgba(34,34,34,.45)}}
.grad{{position:absolute;left:0;right:0;top:0;height:1000px;background:linear-gradient(180deg,rgba(34,34,34,.40),rgba(34,34,34,.14) 55%,rgba(34,34,34,0))}}
</style></head><body>{'<div class="grad"></div>' if text else ''}<div class="box">{badge_html(badge, 46) if badge and text else ''}{txt}{tag_html(tag, 58) if tag else ''}</div>{lab}</body></html>"""


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


# Sin cámara lenta (Iván, 19 oct: «queda muy de banco de imagen»): los planos de dron, travelling
# o paneo de stock vienen ralentizados y se aceleran; la gente andando va a velocidad real.
AERIAL_SPEED = 1.6
_CATALOG = None


def clip_speed(p):
    """Velocidad del plano: `speed` del brief si la trae; si no, 1.6 para dron/paneo y 1 para el resto."""
    if p.get("speed"):
        return float(p["speed"])
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = {}
        for name in ("catalog.json", "nuevos_18oct.json"):
            try:
                for c in json.load(open(os.path.join(ENGINE, "biblioteca", name))):
                    _CATALOG[str(c.get("id"))] = c
            except (OSError, ValueError):
                pass
    c = _CATALOG.get(os.path.splitext(os.path.basename(p["file"]))[0], {})
    scene = (c.get("scene") or "").lower()
    if c.get("aerial") or any(w in scene for w in ("dron", "travelling", "paneo", "aérea", "aerea")):
        return AERIAL_SPEED
    return 1.0


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
        sp = clip_speed(p)
        if clip_dur and shot["dur"] * sp > clip_dur - 0.1:  # el clip no da para acelerar tanto
            sp = max(1.0, (clip_dur - 0.1) / shot["dur"])
        src = shot["dur"] * sp
        ss = max(0.0, min(float(p.get("ss", 0)), clip_dur - src - 0.1))
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.2f}", "-t", f"{src:.3f}", "-i", p["file"],
             "-vf", f"setpts=PTS/{sp:.3f}," + vf, "-t", str(shot["dur"]), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", po])
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
    work = workdir("reel_")
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
        open(p, "w").write(text_html(tb["text"], spec.get("tag") if i == 0 else None, seg[3], seg[2], top=300 if story else (232 if seg[2] == 'triple' else 330),
                                     badge=tb.get("badge", spec.get("badge"))))
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
    # solo móvil (stories de Instagram; Iván, 20 oct: «Instagram y TikTok se ven en el móvil, baja la calidad si se ve
    # igual»): crf 24 deja el archivo a la mitad con SSIM 0,987. Los reels comparten archivo con YouTube y Facebook,
    # que también se ven en ordenador, y mantienen la calidad alta.
    q = ["-crf", "24", "-maxrate", "4M", "-bufsize", "8M"] if story else ["-crf", "21", "-maxrate", "5M", "-bufsize", "10M"]
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
            *q, "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
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
               f'font:700 {int(30 * k)}px/1 Head;background:rgba(34,34,34,.38);padding:{int(10 * k)}px {int(18 * k)}px;'
               f'border-radius:999px">{esc(sp["counter"])}</div>') if sp.get("counter") else ""
    # en stories el texto va arriba-centro (lo de abajo lo tapan la respuesta y los stickers)
    # stories: texto arriba dentro de la zona segura; carruseles de Instagram: lejos de los iconos de la app (Ana, 19 oct)
    bot = 150 if sp.get("ig") else 90
    box = (f"left:{int(80 * k)}px;right:{int((NOTCH_RIGHT + 30) * k)}px;top:{int(330 * k)}px" if story
           else f"left:{int(70 * k)}px;right:{int((100 if sp.get('ig') else 70) * k)}px;bottom:{int(bot * k)}px")
    grad = ("top:0;height:{0}px;background:linear-gradient(180deg,rgba(34,34,34,.62),rgba(34,34,34,.38) 45%,rgba(34,34,34,0))".format(int(h * .6)) if story
            else "bottom:0;height:{0}px;background:linear-gradient(180deg,rgba(34,34,34,0),rgba(34,34,34,.30) 35%,rgba(34,34,34,.72))".format(int(h * .62)))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#0b2230}}
#bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{pos}}}
.grad{{position:absolute;left:0;right:0;{grad}}}
.box{{position:absolute;{box};display:flex;flex-direction:column;align-items:flex-start;gap:{int(24 * k)}px}}
.t{{color:#fff}}
#head{{font:800 {int(sp.get("headSize", 78) * k)}px/1.06 Head;text-shadow:0 2px 18px rgba(34,34,34,.35)}}
#sub{{font:700 {int(40 * k)}px/1.22 Body;text-shadow:0 2px 12px rgba(34,34,34,.55)}}
</style></head><body><img id="bg" src="{sp["image"]}"><div class="grad"></div>
<div class="box">{badge_html(sp.get("badge"), int(44 * k))}{tag_html(sp.get("tag"), int(34 * k))}<div class="t" id="head">{esc(sp["headline"])}</div>{sub}</div>{counter}</body></html>"""


def render_static(sp):
    work = workdir("st_")
    p = f"{work}/s.html"
    open(p, "w").write(static_html(sp))
    png = f"{work}/s.png"
    m = int(40 * sp["w"] / 1080)
    safe = STORY_SAFE if sp.get("story") else ({"top": 120, "bottom": 130, "right": 90, "left": 60} if sp.get("ig") else {"top": m, "bottom": m // 2, "right": m, "left": m})
    capture([{"html": p, "out": png, "w": sp["w"], "h": sp["h"], "safe": safe}])
    run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", sp["out"]])
    return {"out": sp["out"]}


def render_carousel(sp):
    """Carrusel de Instagram (1080x1350): portada con la ubicación, una idea por lámina y cierre suave."""
    n, outs = len(sp["slides"]), []
    for i, sl in enumerate(sp["slides"]):
        out = f'{sp["out_prefix"]}_{i + 1}.jpg'
        render_static({"w": 1080, "h": 1350, "image": sl["image"], "headline": sl.get("headline", ""), "sub": sl.get("sub", ""),
                       "tag": sp.get("tag") if i == 0 else None, "badge": sp.get("badge") if i == 0 else None,
                       "objectPosition": sl.get("objectPosition", "50% 50%"),
                       "headSize": 84 if i == 0 else 72, "ig": True, "out": out})
        outs.append(out)
    return {"out": outs}


def compare_html(sp):
    """Comparativa de dos rutas parecidas: dos fotos (arriba/abajo), su nombre y 2-3 datos cada una."""
    w, h = sp["w"], sp["h"]
    k = w / 1080
    hh = (h - GAP) // 2
    sp_ig = bool(sp.get("ig"))

    def half(i, side):
        y = 0 if i == 0 else hh + GAP
        facts = "".join(f'<div class="t f" id="f{i}{j}">{esc(x)}</div>' for j, x in enumerate(side.get("facts", [])[:3]))
        return (f'<div style="position:absolute;left:0;top:{y}px;width:{w}px;height:{hh}px;overflow:hidden">'
                f'<img src="{side["image"]}" style="width:100%;height:100%;object-fit:cover;object-position:{side.get("objectPosition", "50% 50%")}">'
                f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(34,34,34,.62),rgba(34,34,34,.1) 70%)"></div>'
                f'<div style="position:absolute;left:{int(60 * k)}px;bottom:{int((120 if (sp_ig and i == 1) else 44) * k)}px;display:flex;flex-direction:column;gap:{int(10 * k)}px">'
                f'<div class="t n" id="n{i}">{esc(side["name"])}</div>{facts}</div></div>')
    cnt = sp.get("counter")
    head = (f'<div class="t" id="head" style="position:absolute;left:{int(60 * k)}px;right:{int((170 if cnt else (100 if sp_ig else 60)) * k)}px;top:{int((120 if sp_ig else 46) * k)}px;'
            f'font:800 {int(54 * k)}px/1.08 Head;text-shadow:0 2px 14px rgba(34,34,34,.6)">{esc(sp.get("headline"))}</div>') if sp.get("headline") else ""
    counter = (f'<div class="t" id="cnt" style="position:absolute;right:{int(56 * k)}px;top:{int(52 * k)}px;'
               f'font:700 {int(30 * k)}px/1 Head;background:rgba(34,34,34,.38);padding:{int(10 * k)}px {int(18 * k)}px;'
               f'border-radius:999px">{esc(cnt)}</div>') if cnt else ""
    # el «vs» va a la derecha de la línea de corte para no pisar los datos de la foto de arriba
    vs = (f'<div class="t" id="vs" style="position:absolute;right:{int(70 * k)}px;top:{hh + GAP // 2}px;transform:translateY(-50%);'
          f'width:{int(96 * k)}px;height:{int(96 * k)}px;border-radius:50%;background:{BRAND};color:#fff;display:grid;place-items:center;'
          f'font:800 {int((36 if len(sp.get("vs", "vs")) <= 2 else 26) * k)}px/1 Head">{esc(sp.get("vs", "vs"))}</div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#fff}}
.t{{color:#fff}} .n{{font:800 {int(sp.get("nameSize", 60) * k)}px/1.05 Head;text-shadow:0 2px 14px rgba(34,34,34,.5)}}
.f{{font:700 {int(34 * k)}px/1.2 Body;text-shadow:0 2px 10px rgba(34,34,34,.5)}}
</style></head><body>{half(0, sp["a"])}{half(1, sp["b"])}{head}{vs}{counter}</body></html>"""


def render_compare(sp):
    work = workdir("cmp_")
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
                        "a": sl["a"], "b": sl["b"], "ig": True, "nameSize": 60 if i == 0 else 46, "out": out})
        outs.append(out)
    return {"out": outs}


if __name__ == "__main__":
    kind, path = sys.argv[1], sys.argv[2]
    spec = json.load(open(path))
    print(json.dumps(render_reel(spec) if kind == "reel" else render_static(spec)))
