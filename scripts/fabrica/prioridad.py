"""Prioridad de publicación de cada pieza (Iván, 19 oct): volumen de búsqueda, producto, trend y momento.

Uso: python3 prioridad.py <carpeta con las fichas del Centro en JSON> <salida.json>
Cada fila trae {id, priority:{score, driver, why, factors}}: se escribe en la ficha con update + if_version.
El Centro ordena las piezas de cada canal de mayor a menor score y enseña driver y motivo.
"""
import json, glob, re, sys, os
SRC = sys.argv[1]; OUT = sys.argv[2]
MK = {"EN": "Reino Unido y EE. UU.", "DE": "Alemania", "ES": "España"}
PATS = [("holy", ["holy year", "año santo", "heiliges jahr", "xacobeo", "puerta santa", "heilige pforte"]),
        ("dolomitas", ["dolomit", "alta via"]), ("cotswold", ["cotswold"]),
        ("whw", ["west highland", "midges", "highlands", "escocia", "schottland", "scotland"]),
        ("tmb", ["mont blanc", "tmb", "chamonix"]),
        ("rota", ["rota vicentina", "fishermen", "vicentina", "fischerpfad", "alentejo"]),
        ("cornwall", ["cornwall", "cornualles", "cornish", "south west coast", "swcp", "st ives"]),
        ("portugues", ["portugu", "küstenweg", "portugies", "tui", "baiona", "oporto", "porto"]),
        ("sarria", ["sarria", "francés", "frances", "camino de santiago", "jakobsweg", "camino", "fisterra", "finisterre", "santiago"])]


def route_key(x):
    """Ruta de la pieza por título y ruta; si compara dos rutas distintas, «mix»."""
    head = " ".join(str(x.get(k) or "") for k in ("route", "title")).lower()
    hits = [k for k, pats in PATS if any(p in head for p in pats)]
    if "holy" in hits: return "holy"
    strong = any(p in head for p in ("sarria", "francés", "frances", "jakobsweg", "fisterra", "finisterre", "santiago"))
    if "sarria" in hits and len(hits) > 1 and ("portugues" in hits or not strong):
        hits.remove("sarria")  # «Camino Portugués» o «los caminos del Fishermen's» no son Sarria
    if len(hits) >= 2: return "mix"
    return hits[0] if hits else "general"
NAME = {"sarria": "el Camino desde Sarria", "holy": "el Año Santo Xacobeo 2027", "portugues": "el Camino Portugués por la Costa",
        "tmb": "el Tour du Mont Blanc", "cotswold": "el Cotswold Way", "whw": "la West Highland Way", "rota": "la Rota Vicentina",
        "dolomitas": "las Dolomitas (Alta Via 1)", "cornwall": "la costa de Cornualles", "mix": "la comparativa de rutas", "general": "el traslado de equipaje"}
SEARCH = {"sarria": (32, 30, 35), "holy": (22, 20, 28), "portugues": (24, 22, 26), "tmb": (30, 22, 18), "cotswold": (24, 6, 4),
          "whw": (28, 14, 10), "rota": (14, 24, 12), "dolomitas": (26, 28, 18), "cornwall": (18, 16, 6), "mix": (20, 20, 20), "general": (12, 12, 12)}
# peso de producto = facturación últimos 12 meses en Zoho por mercado (CONTEXTO.md); orden (EN, DE, ES)
PROD = {"sarria": (30, 20, 30), "holy": (26, 26, 26), "portugues": (30, 24, 24), "rota": (16, 30, 6), "cotswold": (24, 6, 4),
        "tmb": (20, 8, 6), "whw": (14, 16, 6), "cornwall": (8, 12, 4), "dolomitas": (6, 6, 6), "mix": (16, 16, 16), "general": (14, 14, 14)}
PROD_WHY = {
    "sarria": {"EN": "Sarria 7/8/11 días es de lo que más factura en EN (1,1 M€ en 12 meses)",
               "DE": "Jakobsweg ab Sarria está entre las rutas que más venden en Alemania y es clave del Camino 2027",
               "ES": "Sarria 7/8 días es la ruta que más factura en España (592 k€ en 12 meses)"},
    "holy": "el pipeline 2027 va un 45 % por encima del año pasado",
    "portugues": {"EN": "el Portugués por la Costa es lo que más factura en EN (705 k€ desde Oporto + 586 k€ desde Baiona/Vigo), y su conversión ha bajado del 7,2 % al 4,7 %",
                  "DE": "el Portugués por la Costa desde Oporto factura 246 k€ en Alemania y su conversión ha bajado del 7,2 % al 4,7 %",
                  "ES": "el Portugués por la Costa es la 2.ª línea en España (228 k€ + 139 k€ desde Tui)"},
    "rota": {"DE": "la Rota Vicentina (Fischerpfad) es lo que más factura en Alemania (377 k€ + 150 k€)",
             "EN": "la Rota Vicentina factura 247 k€ en EN"},
    "cotswold": {"EN": "el Cotswold Way factura 239 k€ (12 días) y cerca de 1 M€ en EN con variantes; Macs ocupa la búsqueda sin Orbis"},
    "tmb": {"EN": "el TMB factura 385 k€ en EN y la disponibilidad de 2027 se decide ya"},
    "whw": {"EN": "la West Highland Way factura 165 k€ en EN", "DE": "la West Highland Way factura 129 k€ en Alemania"},
    "cornwall": {"DE": "el South West Coast Path St Ives–Penzance factura 69 k€ en Alemania"},
    "mix": "compara varias rutas de Orbis: llega a más gente, pero con una intención de búsqueda más difusa",
    "general": "el traslado de equipaje es el servicio que nos diferencia en todas las rutas",
}
DRV = {"search": "Volumen de búsqueda", "product": "Tipo de producto (lo que más factura)", "trend": "Trend que ya ha funcionado en otra cuenta", "timing": "Momento (Año Santo Xacobeo 2027)"}
def li(lang): return {"EN": 0, "DE": 1, "ES": 2}.get(lang, 0)
def trend_of(x):
    j = x.get("justification") if isinstance(x.get("justification"), dict) else {}
    t = j.get("trend") if isinstance(j.get("trend"), dict) else {}
    tr = x.get("trendRef")
    name = t.get("name") or (tr.get("trend") if isinstance(tr, dict) else tr) or ""
    ex = t.get("examples") if isinstance(t.get("examples"), list) else []
    exs = [" · ".join(str(e.get(k)) for k in ("account", "metric") if e.get(k)) for e in ex if isinstance(e, dict)]
    exs = [e for e in exs if e]
    acc = j.get("accounts") or ""
    blob = " ".join([name, acc] + exs)
    strong = bool(re.search(r"\d[\d.,]*\s?(k|K|M|mil|millones|views|visualizaciones|Aufrufe|likes|me gusta|%)", blob))
    pts = 16 if strong and (exs or acc) else 10 if name else 4
    det = exs[0] if exs else (acc[:140] if strong else name[:140])
    return pts, det, name
def fmt_pts(x):
    f = (x.get("format") or "").lower(); c = x.get("channel")
    if "reel" in f or "short" in f or c in ("tiktok", "youtube"): return 8, "vídeo corto, el formato con más alcance"
    if "carrusel" in f or "compar" in f: return 6, "carrusel, el formato que más se guarda"
    if "story" in f: return 2, "story"
    return 3, f or c
rows = []
for f in sorted(glob.glob(SRC + "/*.json")):
    d = json.load(open(f)); x = d.get("data", d); did = os.path.basename(f)[:-5]
    if (x.get("date") or "") < "2026-10-19" and x.get("status") != "cambios": continue
    if x.get("status") in ("descartada", "publicada"): continue
    lang = (x.get("lang") or (x.get("design") or {}).get("lang") or "EN").upper()[:2]
    rk = route_key(x); i = li(lang)
    s, p = SEARCH[rk][i], PROD[rk][i]
    tp, tdet, tname = trend_of(x)
    tm = 15 if rk == "holy" or x.get("badge") else 6 if rk == "rota" else 0
    fp, fdet = fmt_pts(x)
    seo = x.get("seo") if isinstance(x.get("seo"), dict) else {}
    kw = seo.get("keyword") or x.get("keyword") or ""
    comp = {"search": s / 35, "product": p / 30, "trend": tp / 20, "timing": tm / 15}
    order = sorted(comp, key=comp.get, reverse=True)
    pw = PROD_WHY.get(rk); pw = pw.get(lang) if isinstance(pw, dict) else pw
    det = {
        "search": (f"«{kw}» es de las búsquedas con más volumen sobre {NAME[rk]} en {MK[lang]}" if kw else f"{NAME[rk][0].upper() + NAME[rk][1:]} es de lo más buscado en {MK[lang]}") if s >= 24 else (f"búsqueda media en {MK[lang]}" + (f" («{kw}»)" if kw else "")),
        "product": pw or f"sin dato de facturación destacado de {NAME[rk]} en {MK[lang]}",
        "trend": (f"{tname[:110]}" + (f" ({tdet[:120]})" if tdet and tdet != tname[:140] else "")) if tname or tdet else "sin trend contrastado",
        "timing": "2027 es Año Santo Xacobeo y la decisión de viaje se toma estos meses" if rk == "holy" or x.get("badge") else "la costa de Portugal se camina bien en otoño e invierno",
    }
    if rk == "dolomitas": det["product"] = "interés por las Dolomitas al alza (+298 %), pero la ficha AV1 de hotel en hotel está sin confirmar"
    main = order[0]; second = order[1]
    if comp[main] < .7:
        main_label = "Sin palanca fuerte (prioridad media)"
        why = f"Ni la búsqueda ni el producto destacan aquí: {det['search']}; {det['product']}. Formato: {fdet}."
    else:
        main_label = DRV[main]
        why = f"{DRV[main]}: {det[main]}. También pesa: {det[second]}. Formato: {fdet}."
    why = why.replace("de el ", "del ").replace("..", ".").replace(".).", ").")
    score = s + p + tp + tm + fp
    rows.append({"id": did, "version": d.get("version"), "lang": lang, "channel": x.get("channel"), "route": rk, "title": x.get("title"),
                 "priority": {"score": score, "driver": main_label, "why": why,
                              "factors": {"busqueda": s, "producto": p, "trend": tp, "momento": tm, "formato": fp}, "ts": "2026-10-19"}})
json.dump(rows, open(OUT, "w"), ensure_ascii=False, indent=1)
print(len(rows))
import collections
for r in sorted(rows, key=lambda r: (r["lang"], r["channel"] or "", -r["priority"]["score"]))[:400]:
    print(r["lang"], (r["channel"] or "")[:9].ljust(9), r["priority"]["score"], r["route"].ljust(9), (r["title"] or "")[:55], "|", r["priority"]["driver"])
