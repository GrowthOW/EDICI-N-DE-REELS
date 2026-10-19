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
STATIC = {"ig_carousel": ("instagram", "Carrusel", 1080, 1350), "ig_static": ("instagram", "Post", 1080, 1350),
          "fb": ("facebook", "Post", 1080, 1350), "linkedin": ("linkedin", "Post", 1200, 1200),
          "story": ("instagram", "Story", 1080, 1920), "compare": (None, "Comparativa", 1080, 1350)}
REEL_CHANNELS = [("instagram", "Reel", "instagram"), ("tiktok", "Vídeo", "tiktok"), ("youtube", "Short", "youtube"), ("facebook", "Reel", "facebook")]
TIMES = ["09:00", "13:30", "19:00"]
MARKET = {"ES": "España", "EN": "UK+US", "DE": "DACH"}
# id de la ficha por formato (los cuatro primeros mantienen el esquema de la primera tanda)
SUFFIX = {"ig_carousel": "", "ig_static": "", "fb": "", "linkedin": "", "story": "story", "story_video": "story", "compare": "cmp"}


def tag_for(piece, lang):
    """Etiqueta de ubicación de la pieza (nombre corto de la ruta en el idioma del público)."""
    if piece.get("tag") or piece.get("pill"):
        return piece.get("tag") or piece.get("pill")
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
    if piece.get("sticker"):
        st = piece["sticker"]
        lines += [f"**Sticker para añadir en Instagram ({st.get('type', 'encuesta')}):** {st.get('text', '')}" + (" · Opciones: " + " / ".join(st.get("options", [])) if st.get("options") else ""), ""]
    if piece.get("compare"):
        c = piece["compare"]
        if c.get("slides"):
            lines += ["**Láminas de la comparativa**", ""]
            for i, sl in enumerate(c["slides"]):
                lines += [f"{i + 1}. {sl.get('headline', '')} — " + " / ".join(
                    f"{sl[side].get('name', '')}: " + " · ".join(sl[side].get("facts", [])) for side in ("a", "b"))]
        else:
            for side in ("a", "b"):
                x = c.get(side) or {}
                lines += [f"**{x.get('name', '')}:** " + " · ".join(x.get("facts", []))]
        lines += [""]
    if piece.get("overlay"):
        lines += ["**Texto en la imagen:** " + " · ".join(x for x in [piece["overlay"].get("headline"), piece["overlay"].get("sub")] if x), ""]
    seo = piece.get("seo") or {}
    if seo:  # SEO social (Iván, 19 oct): palabra clave por pieza y dónde va
        lines += ["**SEO**", "", f"- Palabra clave: {seo.get('keyword', '')}"]
        if seo.get("secondary"):
            lines += ["- Secundarias: " + ", ".join(seo["secondary"])]
        if seo.get("altText"):
            alts = seo["altText"] if isinstance(seo["altText"], list) else [seo["altText"]]
            lines += [f"- Texto alternativo {i + 1}: {a}" for i, a in enumerate(alts)]
        if seo.get("source"):
            lines += [f"- De dónde sale: {seo['source']}"]
        lines += [""]
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
    if piece.get("seo"):
        base["seo"] = piece["seo"]
    day = date.replace("-", "")
    fmt_key = piece["format"]
    out = []
    if fmt_key == "reel":
        for ch, fmt, cap in REEL_CHANNELS:
            d = dict(base, channel=ch, format=fmt, design={"caption": caption_for(piece, cap)[:220], "route": tag_for(piece, lang) or "", "lang": lang},
                     ready_material=material_md(piece, cap))
            d["id"] = f"fab-{day}-{lang.lower()}-{ch}-reel{slot + 1}"
            out.append(d)
        return out
    if fmt_key == "story_video":
        ch, fmt = "instagram", "Story"
    else:
        ch, fmt, _, _ = STATIC[fmt_key]
        ch = ch or piece.get("channel", "facebook")
    d = dict(base, channel=ch, format=fmt, design={"caption": caption_for(piece, ch)[:220], "route": tag_for(piece, lang) or "", "lang": lang},
             ready_material=material_md(piece, ch))
    d["id"] = f"fab-{day}-{lang.lower()}-{ch}-{SUFFIX.get(fmt_key, '')}{slot + 1}"
    out.append(d)
    return out


def clip(media, vid):
    f = f"{media}/video/{vid}.mp4"
    if not os.path.exists(f):
        raise RuntimeError("sin licenciar " + str(vid))
    return f


def frame(media, im, out):
    """Fotograma de un clip de la ruta ya licenciado (las fotos salen de clips 4K/HD: calidad aceptable siempre)."""
    render.run(["ffmpeg", "-v", "error", "-y", "-ss", str(im.get("at", 1.0)), "-i", clip(media, im["fromVideo"]), "-frames:v", "1", "-q:v", "2", out])
    return out


def build_shots(piece, s, media):
    """Planos del reel. Un plano puede ser multipantalla: layout split/triple/grid4 con panels [{videoId, ss, cropx, cropy}]."""
    shots = []
    for i, sh in enumerate(s.get("shots", [])):
        bs = piece.get("shots") or []
        b = bs[i] if i < len(bs) else {}
        if sh.get("panels"):
            panels = [{"file": clip(media, p["videoId"]), "ss": p.get("ss", 0), "cropx": p.get("cropx", 0.5), "cropy": p.get("cropy", 0.5)}
                      for p in sh["panels"]]
            shots.append({"layout": sh.get("layout", "split"), "panels": panels, "dur": sh.get("dur", 3.5),
                          "labels": sh.get("labels") or b.get("labels")})
            continue
        if sh.get("missing") or not sh.get("videoId"):
            raise RuntimeError("falta plano " + str(i + 1))
        shots.append({"file": clip(media, sh["videoId"]), "ss": sh.get("ss", 0), "dur": sh.get("dur", 3.5), "cropx": sh.get("cropx", 0.5)})
    return shots


def shot_clips(s):
    out = []
    for sh in s.get("shots", []):
        out += [str(p["videoId"]) for p in sh["panels"]] if sh.get("panels") else [str(sh.get("videoId"))]
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
        # reel y story_video comparten numeración con su canal (reelN / storyN)
        sk = "story" if key == "story_video" else key
        slot = slots.get(sk, 0); slots[sk] = slot + 1
        if piece.get("slot"):  # piezas extra del mismo día: número fijo para no pisar las fichas de la tanda principal
            slot = int(piece["slot"]) - 1
        tag = tag_for(piece, lang)
        try:
            if key in ("reel", "story_video"):
                shots = build_shots(piece, s, media)
                texts = [dict(t) for t in piece.get("textBlocks", [])[:3]]
                body = sum(x["dur"] for x in shots)
                planned = sum(x.get("dur", 0) for x in piece.get("shots", [])) or body
                k = body / planned  # si cambia el número o la duración de planos, los textos se reparten igual
                for t in texts:
                    t["start"] = round(t["start"] * k, 2)
                    t["end"] = round(min(t["end"] * k, body - 0.45), 2)
                out = f"{out_dir}/{piece['id']}.mp4"
                r = render.render_reel({"lang": lang, "shots": shots, "texts": texts, "tag": tag, "out": out,
                                        "kind": "story" if key == "story_video" else "reel"})
                files = [{"kind": "video", "label": "Vídeo final", "local": r["out"], "name": f"{piece['id']}.mp4"},
                         {"kind": "image", "label": "Portada", "local": r["cover"], "name": f"{piece['id']}_portada.jpg"}]
                manifest.append({"id": piece["id"], "ok": True, "sheet": r["sheet"], "files": files,
                                 "docs": docs_for(piece, lang, date, slot, files, cycle), "clips": shot_clips(s)})
            elif key == "ig_carousel":
                slides = []
                for i, (txt, im) in enumerate(zip(piece.get("slides", []), s.get("slides", []))):
                    fr = frame(media, im, f"{out_dir}/{piece['id']}_frame{i + 1}.jpg")
                    slides.append({"image": fr, "headline": txt.get("headline", ""), "sub": txt.get("sub", ""), "objectPosition": im.get("objectPosition", "50% 50%")})
                if len(slides) < 3:
                    raise RuntimeError("carrusel con menos de 3 láminas")
                r = render.render_carousel({"slides": slides, "tag": tag, "out_prefix": f"{out_dir}/{piece['id']}"})
                files = [{"kind": "image", "label": f"Lámina {i + 1}", "local": f, "name": os.path.basename(f)} for i, f in enumerate(r["out"])]
                manifest.append({"id": piece["id"], "ok": True, "files": files, "docs": docs_for(piece, lang, date, slot, files, cycle),
                                 "clips": [str(x["fromVideo"]) for x in s.get("slides", [])]})
            elif key == "compare" and (piece.get("compare") or {}).get("slides"):
                # comparativa en carrusel: portada partida + una lámina partida por aspecto
                c, cs = piece["compare"], (s.get("compare") or {}).get("slides", [])
                if len(cs) != len(c["slides"]) or len(cs) < 3:
                    raise RuntimeError("la comparativa en carrusel necesita 3 láminas o más, con imagen para cada una")
                slides = []
                for i, (txt, im) in enumerate(zip(c["slides"], cs)):
                    sl = {"headline": txt.get("headline", "")}
                    for side in ("a", "b"):
                        fr = frame(media, im[side], f"{out_dir}/{piece['id']}_{i + 1}{side}.jpg")
                        sl[side] = {"image": fr, "name": txt[side].get("name", ""), "facts": txt[side].get("facts", []),
                                    "objectPosition": im[side].get("objectPosition", "50% 50%")}
                    slides.append(sl)
                r = render.render_compare_carousel({"slides": slides, "vs": c.get("vs", "vs"), "out_prefix": f"{out_dir}/{piece['id']}"})
                files = [{"kind": "image", "label": f"Lámina {i + 1}", "local": f, "name": os.path.basename(f)} for i, f in enumerate(r["out"])]
                manifest.append({"id": piece["id"], "ok": True, "files": files, "docs": docs_for(piece, lang, date, slot, files, cycle),
                                 "clips": sorted({str(x[side]["fromVideo"]) for x in cs for side in ("a", "b")})})
            elif key == "compare":
                c, cs = piece.get("compare") or {}, s.get("compare") or {}
                sides = {}
                for side in ("a", "b"):
                    im = cs.get(side) or {}
                    if not im.get("fromVideo"):
                        raise RuntimeError("falta imagen " + side)
                    fr = frame(media, im, f"{out_dir}/{piece['id']}_{side}.jpg")
                    sides[side] = {"image": fr, "name": (c.get(side) or {}).get("name", ""), "facts": (c.get(side) or {}).get("facts", []),
                                   "objectPosition": im.get("objectPosition", "50% 50%")}
                out = f"{out_dir}/{piece['id']}.jpg"
                render.render_compare({"w": 1080, "h": 1350, "headline": c.get("headline", ""), "vs": c.get("vs", "vs"), "out": out, **sides})
                files = [{"kind": "image", "label": "Imagen final", "local": out, "name": f"{piece['id']}.jpg"}]
                manifest.append({"id": piece["id"], "ok": True, "files": files, "docs": docs_for(piece, lang, date, slot, files, cycle),
                                 "clips": [str(cs[x]["fromVideo"]) for x in ("a", "b")]})
            else:
                img = (s.get("image") or {})
                if img.get("fromVideo"):
                    f = frame(media, img, f"{out_dir}/{piece['id']}_frame.jpg")
                    img["imageId"] = "v" + str(img["fromVideo"])
                elif img.get("missing") or not img.get("imageId"):
                    raise RuntimeError("falta imagen")
                else:
                    f = f"{media}/image/{img['imageId']}.jpg"
                    if not os.path.exists(f):
                        raise RuntimeError("sin licenciar " + img["imageId"])
                ch, fmt, w, h = STATIC[key]
                ov = piece.get("overlay") or {}
                out = f"{out_dir}/{piece['id']}.jpg"
                render.render_static({"w": w, "h": h, "image": f, "headline": ov.get("headline", ""), "sub": ov.get("sub", ""),
                                      "tag": tag, "objectPosition": img.get("objectPosition", "50% 50%"), "out": out,
                                      "story": key == "story", "headSize": ov.get("headSize", 78)})
                files = [{"kind": "image", "label": "Imagen final", "local": out, "name": f"{piece['id']}.jpg"}]
                manifest.append({"id": piece["id"], "ok": True, "files": files, "docs": docs_for(piece, lang, date, slot, files, cycle), "image": img["imageId"]})
        except Exception as ex:
            manifest.append({"id": piece["id"], "ok": False, "error": str(ex)[:600], "trace": traceback.format_exc()[-400:]})
    json.dump(manifest, open(f"{out_dir}/manifest.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps([{k: m.get(k) for k in ("id", "ok", "error")} for m in manifest], ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:7])
