import json, os
from PIL import Image, ImageFilter, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "sources")
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920

def pad(box, t, b, l, r, w=W, h=H):
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - l); y0 = max(0, y0 - t)
    x1 = min(w, x1 + r); y1 = min(h, y1 + b)
    return [x0, y0, x1, y1]

SLIDES = {
    "portada": {
        "file": "Portada 2027.png",
        "regions": [
            {"id": "pill", "type": "pill", "box": pad((79, 1243, 570, 1262), 24, 22, 22, 25)},
            {"id": "h1", "type": "headline", "box": pad((80, 1330, 767, 1419), 10, 10, 14, 34)},
            {"id": "h2", "type": "headline", "box": pad((83, 1420, 972, 1533), 8, 12, 14, 34)},
            {"id": "h3", "type": "headline", "box": pad((80, 1564, 370, 1644), 10, 14, 14, 34)},
        ],
    },
    "montblanc": {
        "file": "Mont Blanc.png",
        "regions": [
            {"id": "country", "type": "country", "box": pad((82, 150, 641, 168), 24, 20, 12, 30)},
            {"id": "badge1", "type": "badge", "box": [87, 200, 265, 390]},
            {"id": "badge2", "type": "badge", "box": [301, 200, 509, 390]},
            {"id": "badge3", "type": "badge", "box": [543, 200, 758, 390]},
            {"id": "pill", "type": "pill", "box": pad((112, 1295, 809, 1331), 25, 22, 25, 25)},
            {"id": "h1", "type": "headline", "box": pad((80, 1398, 878, 1467), 10, 10, 14, 34)},
            {"id": "h2", "type": "headline", "box": pad((80, 1487, 824, 1572), 8, 10, 14, 34)},
            {"id": "h3", "type": "headline", "box": pad((80, 1585, 451, 1659), 10, 14, 14, 34)},
        ],
    },
    "whw": {
        "file": "West Highland Way.png",
        "regions": [
            {"id": "country", "type": "country", "box": pad((81, 150, 261, 168), 24, 20, 12, 30)},
            {"id": "badge1", "type": "badge", "box": [87, 200, 265, 390]},
            {"id": "badge2", "type": "badge", "box": [298, 200, 502, 390]},
            {"id": "badge3", "type": "badge", "box": [537, 200, 848, 390]},
            {"id": "pill", "type": "pill", "box": pad((114, 1295, 786, 1331), 25, 22, 25, 25)},
            {"id": "h1", "type": "headline", "box": pad((86, 1398, 887, 1467), 10, 10, 14, 34)},
            {"id": "h2", "type": "headline", "box": pad((80, 1492, 938, 1572), 8, 10, 14, 34)},
            {"id": "h3", "type": "headline", "box": pad((80, 1582, 478, 1662), 10, 14, 14, 34)},
        ],
    },
    "fisherman": {
        "file": "Fisherman's Trail.png",
        "regions": [
            {"id": "country", "type": "country", "box": pad((82, 150, 263, 168), 24, 20, 12, 30)},
            {"id": "badge1", "type": "badge", "box": [87, 200, 276, 390]},
            {"id": "badge2", "type": "badge", "box": [312, 200, 520, 390]},
            {"id": "badge3", "type": "badge", "box": [556, 200, 866, 390]},
            {"id": "pill", "type": "pill", "box": pad((116, 1295, 716, 1331), 25, 22, 25, 25)},
            {"id": "h1", "type": "headline", "box": pad((80, 1403, 815, 1467), 10, 10, 14, 34)},
            {"id": "h2", "type": "headline", "box": pad((85, 1487, 749, 1572), 8, 10, 14, 34)},
            {"id": "h3", "type": "headline", "box": pad((85, 1585, 951, 1662), 10, 14, 14, 34)},
        ],
    },
    "cotswold": {
        "file": "Cotswold Way.png",
        "regions": [
            {"id": "country", "type": "country", "box": pad((82, 151, 243, 168), 24, 20, 12, 30)},
            {"id": "badge1", "type": "badge", "box": [87, 200, 268, 390]},
            {"id": "badge2", "type": "badge", "box": [302, 200, 505, 390]},
            {"id": "badge3", "type": "badge", "box": [540, 200, 767, 390]},
            {"id": "pill", "type": "pill", "box": pad((114, 1295, 619, 1331), 25, 22, 25, 25)},
            {"id": "h1", "type": "headline", "box": pad((82, 1398, 850, 1483), 10, 10, 14, 34)},
            {"id": "h2", "type": "headline", "box": pad((83, 1491, 655, 1593), 8, 10, 14, 34)},
            {"id": "h3", "type": "headline", "box": pad((83, 1599, 445, 1662), 10, 14, 14, 34)},
        ],
    },
}

def feathered_blur_paste(img, box, radius=22, feather=18):
    x0, y0, x1, y1 = [int(v) for v in box]
    ex0, ey0 = max(0, x0 - feather), max(0, y0 - feather)
    ex1, ey1 = min(W, x1 + feather), min(H, y1 + feather)
    crop = img.crop((ex0, ey0, ex1, ey1))
    blurred = crop.filter(ImageFilter.GaussianBlur(radius))
    mask = Image.new("L", blurred.size, 0)
    d = ImageDraw.Draw(mask)
    d.rectangle([x0 - ex0, y0 - ey0, x1 - ex0, y1 - ey0], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    img.paste(blurred, (ex0, ey0), mask)

config = {"slides": [], "canvas": {"w": W, "h": H}}

for key, spec in SLIDES.items():
    im = Image.open(os.path.join(SRC, spec["file"])).convert("RGB")
    bg = im.copy()
    for r in spec["regions"]:
        feathered_blur_paste(bg, r["box"], radius=24, feather=16)
    bg_name = f"{key}_bg.jpg"
    bg.save(os.path.join(OUT, bg_name), quality=92)

    regions_out = []
    for r in spec["regions"]:
        x0, y0, x1, y1 = [int(v) for v in r["box"]]
        crop = im.crop((x0, y0, x1, y1))
        fname = f"{key}_{r['id']}.jpg"
        crop.save(os.path.join(OUT, fname), quality=95)
        regions_out.append({
            "id": r["id"], "type": r["type"], "file": fname,
            "x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0,
        })
    config["slides"].append({"key": key, "bg": bg_name, "regions": regions_out})

with open(os.path.join(OUT, "config.json"), "w") as f:
    json.dump(config, f, indent=2)

print("done", json.dumps(config, indent=2)[:2000])
