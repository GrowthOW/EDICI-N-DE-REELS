"""Fábrica: de brief + selección de planos a piezas finales y fichas para la sala.

Uso:
  python3 produce.py <lang> <brief.json> <selection.json> <media_dir> <out_dir> <fecha YYYY-MM-DD>

media_dir contiene video/<id>.mp4 e image/<id>.jpg ya licenciados.
Escribe en out_dir los MP4/JPG finales y manifest.json con, por pieza, los
archivos y los documentos de calendario (uno por canal) para la sala.
"""
import json, os, re, sys, traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402

ROUTES = [  # (patrón en el nombre de la ruta, {idioma: etiqueta corta para la pill})
    (r"finis|fisterra|mux[ií]a", {"ES": "Camino a Fisterra", "EN": "Camino to Finisterre", "DE": "Jakobsweg nach Finisterre"}),
    (r"a[ñn]o santo|holy year|heilig", {"ES": "Año Santo 2027", "EN": "Holy Year 2027", "DE": "Heiliges Jahr 2027"}),
    (r"costa|coast|küste", {"ES": "Camino Portugués por la Costa", "EN": "Portuguese Coastal Camino", "DE": "Portugiesischer Küstenweg"}),
    (r"tui", {"ES": "Camino Portugués desde Tui", "EN": "Camino from Tui", "DE": "Jakobsweg ab Tui"}),
    (r"sarria", {"ES": "Camino desde Sarria", "EN": "Camino from Sarria", "DE": "Jakobsweg ab Sarria"}),
    (r"franc[ée]s|french|französ|saint-jean|st\.? jean", {"ES": "Camino Francés", "EN": "Camino Francés", "DE": "Französischer Jakobsweg"}),
    (r"fisher|fischer|vicentina", {"ES": "Rota Vicentina", "EN": "Rota Vicentina", "DE": "Rota Vicentina"}),
    (r"cotswold", {"*": "Cotswold Way"}),
    (r"mont blanc|tmb", {"*": "Tour du Mont Blanc"}),
    (r"west highland", {"*": "West Highland Way"}),
    (r"south west coast", {"*": "South West Coast Path"}),
    (r"ingl[ée]s|english way|englischer", {"ES": "Camino Inglés", "EN": "English Way", "DE": "Englischer Jakobsweg"}),
    (r"primitivo|primitive", {"ES": "Camino Primitivo", "EN": "Camino Primitivo", "DE": "Camino Primitivo"}),
]
STATIC = {"ig_carousel": ("instagram", "Carrusel", 1080, 1350), "ig_static": ("instagram", "Post", 1080, 1350), "fb": ("facebook", "Post", 1080, 1350), "linkedin": ("linkedin", "Post", 1200, 1200)}
REEL_CHANNELS = [("instagram", "Reel", "instagram"), ("tiktok", "Vídeo", "tiktok"), ("youtube", "Short", "youtube"), ("facebook", "Reel", "facebook")]
TIMES = ["09:00", "13:30", "19:00"]
MARKET = {"ES": "España", "EN": "UK+US", "DE": "DACH"}


def pill_for(piece, lang):
    if piece.get("pill"):
        return piece["pill"]
    name = (piece.get("route") or "").lower()
    for pat, lab in ROUTES:
        if re.search(pat, name):
            return lab.get(lang) or lab.get("*")
    return None


def caption_for(piece, channel):
    c = piece.get("captions") or {}
    if channel == "youtube":
        return c.get("youtube_desc") or c.get("instagram") or ""
    return c.get(channel) or c.get("instagram") or c.get("facebook") or ""


def material_md(piece, channel):
    c = piece.get("captions") or {}
    lines = []
    if channel == "youtube" and c.get("youtube_title"):
        lines += [f"**Título:** {c['youtube_title']}", ""]
    lines += ["**Texto para publicar**", "", caption_for(piece, channel), ""]
    if piece.get("hashtags"):
        lines += ["**Hashtags:** " + " ".join(h if h.startswith("#") else "#" + h for h in piece["hashtags"]), ""]
    if piece.get("cta"):
        lines += ["**Llamada a la acción:** " + piece["cta"], ""]
    if piece.get("textBlocks"):
        lines += ["**Texto en pantalla**", ""] + [f"- {t['start']}–{t['end']} s: {t['text']}" for t in piece["textBlocks"]] + [""]
    if piece.get("slides"):
        lines += ["**Láminas del carrusel**", ""] + [f"{i + 1}. {x.get('headline', '')}" + (f" — {x['sub']}" if x.get("sub") else "") for i, x in enumerate(piece["slides"])] + [""]
    if piece.get("overlay"):
        lines += ["**Texto en la imagen:** " + " · ".join(x for x in [piece["overlay"].get("headline"), piece["overlay"].get("sub")] if x), ""]
    return "\n".join(lines).strip()


def justification(piece):
    j = piece.get("justification") or {}
    return {
        "origin": "Tendencia y búsqueda por mercado",
        "text": " ".join(x for x in [j.get("business")] if x),
        "trend": {"name": j.get("trend", ""), "why_works": piece.get("engagement", "")},
        "search": {"signals": j.get("search", "")},
        "accounts": j.get("competitor", ""),
        "lang": j.get("marketFit", ""),
        "channel": piece.get("concept", ""),
        "evidence": [s.get("url") for s in piece.get("sources", []) if s.get("url")],
    }


def docs_for(piece, lang, date, slot, files, cycle):
    base = {
        "date": date, "lang": lang, "market": MARKET[lang], "title": piece.get("title", ""), "hook": piece.get("hook", ""),
        "status": "propuesta", "version": 1, "route": piece.get("route", ""), "contentType": piece.get("contentType") or piece.get("type", ""),
        "engagement": piece.get("engagement", ""), "justification": justification(piece), "sources": [s.get("url") for s in piece.get("sources", []) if s.get("url")],
        "searchQuery": (piece.get("justification") or {}).get("search", "")[:160], "agent": "fabrica-v2", "cycle": cycle,
        "briefId": piece["id"], "files": files, "time": TIMES[slot % 3],
    }
    out = []
    if piece["format"] == "reel":
        for ch, fmt, cap in REEL_CHANNELS:
            d = dict(base, channel=ch, format=fmt, design={"caption": caption_for(piece, cap)[:220], "route": pill_for(piece, lang) or "", "lang": lang},
                     ready_material=material_md(piece, cap))
            d["id"] = f"fab-{date.replace('-', '')}-{lang.lower()}-{ch}-reel{slot + 1}"
            out.append(d)
    else:
        ch, fmt, _, _ = STATIC[piece["format"]]
        d = dict(base, channel=ch, format=fmt, design={"caption": caption_for(piece, ch)[:220], "route": pill_for(piece, lang) or "", "lang": lang},
                 ready_material=material_md(piece, ch))
        d["id"] = f"fab-{date.replace('-', '')}-{lang.lower()}-{ch}-{slot + 1}"
        out.append(d)
    return out


def main(lang, brief_p, sel_p, media, out_dir, date):
    brief, sel = json.load(open(brief_p)), json.load(open(sel_p))
    selmap = {p["id"]: p for p in sel["pieces"]}
    os.makedirs(out_dir, exist_ok=True)
    cycle = f"fabrica-{date}-{lang.lower()}"
    manifest, slots = [], {}
    for piece in brief["pieces"]:
        s = selmap.get(piece["id"], {})
        key = piece["format"]
        slot = slots.get(key, 0); slots[key] = slot + 1
        try:
            if piece["format"] == "reel":
                shots = []
                for i, sh in enumerate(s.get("shots", [])):
                    if sh.get("missing") or not sh.get("videoId"):
                        raise RuntimeError("falta plano " + str(i + 1))
                    f = f"{media}/video/{sh['videoId']}.mp4"
                    if not os.path.exists(f):
                        raise RuntimeError("sin licenciar " + sh["videoId"])
                    shots.append({"file": f, "ss": sh.get("ss", 0), "dur": sh.get("dur", 3.5), "cropx": sh.get("cropx", 0.5)})
                texts = [dict(t) for t in piece.get("textBlocks", [])[:3]]
                body = sum(x["dur"] for x in shots)
                planned = sum(x.get("dur", 0) for x in piece.get("shots", [])) or body
                k = body / planned  # si cambia el número o la duración de planos, los textos se reparten igual
                for t in texts:
                    t["start"] = round(t["start"] * k, 2)
                    t["end"] = round(min(t["end"] * k, body - 0.45), 2)
                out = f"{out_dir}/{piece['id']}.mp4"
                r = render.render_reel({"lang": lang, "shots": shots, "texts": texts, "pill": pill_for(piece, lang), "out": out})
                files = [{"kind": "video", "label": "Vídeo final", "local": r["out"], "name": f"{piece['id']}.mp4"},
                         {"kind": "image", "label": "Portada", "local": r["cover"], "name": f"{piece['id']}_portada.jpg"}]
                manifest.append({"id": piece["id"], "ok": True, "sheet": r["sheet"], "files": files,
                                 "docs": docs_for(piece, lang, date, slot, files, cycle), "clips": [x["videoId"] for x in s["shots"]]})
            elif piece["format"] == "ig_carousel":
                slides = []
                for i, (txt, im) in enumerate(zip(piece.get("slides", []), s.get("slides", []))):
                    src = f"{media}/video/{im['fromVideo']}.mp4"
                    if not os.path.exists(src):
                        raise RuntimeError("sin licenciar " + str(im["fromVideo"]))
                    fr = f"{out_dir}/{piece['id']}_frame{i + 1}.jpg"
                    render.run(["ffmpeg", "-v", "error", "-y", "-ss", str(im.get("at", 1.0)), "-i", src, "-frames:v", "1", "-q:v", "2", fr])
                    slides.append({"image": fr, "headline": txt.get("headline", ""), "sub": txt.get("sub", ""), "objectPosition": im.get("objectPosition", "50% 50%")})
                if len(slides) < 3:
                    raise RuntimeError("carrusel con menos de 3 láminas")
                r = render.render_carousel({"slides": slides, "pill": pill_for(piece, lang), "out_prefix": f"{out_dir}/{piece['id']}"})
                files = [{"kind": "image", "label": f"Lámina {i + 1}", "local": f, "name": os.path.basename(f)} for i, f in enumerate(r["out"])]
                manifest.append({"id": piece["id"], "ok": True, "files": files, "docs": docs_for(piece, lang, date, slot, files, cycle),
                                 "clips": [str(x["fromVideo"]) for x in s.get("slides", [])]})
            else:
                img = (s.get("image") or {})
                if img.get("fromVideo"):  # fotograma de un clip de la ruta ya licenciado
                    src = f"{media}/video/{img['fromVideo']}.mp4"
                    if not os.path.exists(src):
                        raise RuntimeError("sin licenciar " + img["fromVideo"])
                    f = f"{out_dir}/{piece['id']}_frame.jpg"
                    render.run(["ffmpeg", "-v", "error", "-y", "-ss", str(img.get("at", 1.0)), "-i", src, "-frames:v", "1", "-q:v", "2", f])
                    img["imageId"] = "v" + str(img["fromVideo"])
                elif img.get("missing") or not img.get("imageId"):
                    raise RuntimeError("falta imagen")
                else:
                    f = f"{media}/image/{img['imageId']}.jpg"
                    if not os.path.exists(f):
                        raise RuntimeError("sin licenciar " + img["imageId"])
                ch, fmt, w, h = STATIC[piece["format"]]
                ov = piece.get("overlay") or {}
                out = f"{out_dir}/{piece['id']}.jpg"
                render.render_static({"w": w, "h": h, "image": f, "headline": ov.get("headline", ""), "sub": ov.get("sub", ""),
                                      "pill": pill_for(piece, lang), "objectPosition": img.get("objectPosition", "50% 50%"), "out": out})
                files = [{"kind": "image", "label": "Imagen final", "local": out, "name": f"{piece['id']}.jpg"}]
                manifest.append({"id": piece["id"], "ok": True, "files": files, "docs": docs_for(piece, lang, date, slot, files, cycle), "image": img["imageId"]})
        except Exception as ex:
            manifest.append({"id": piece["id"], "ok": False, "error": str(ex)[:600], "trace": traceback.format_exc()[-400:]})
    json.dump(manifest, open(f"{out_dir}/manifest.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps([{k: m.get(k) for k in ("id", "ok", "error")} for m in manifest], ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:7])
