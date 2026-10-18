"""Shutterstock para la Fábrica: licencia y descarga con tope diario.

Uso:
  python3 sst.py preview video <id> <url_preview> <dir>  # vista previa (gratis) + hoja de fotogramas
  python3 sst.py video <id> <dir>           # licencia HD (gasta 1 del cupo de vídeo) y descarga
  python3 sst.py image <id> <dir>           # licencia imagen (cupo de imagen) y descarga
  python3 sst.py status                     # cuántas licencias van hoy

El token va como secreto de red (cabecera Bearer de api.shutterstock.com):
nunca se lee ni se escribe aquí. Tope: 90 al día por tipo (autorizado por
Iván el 18 oct). Un clip ya licenciado se vuelve a descargar sin gastar cupo.
"""
import datetime, json, os, subprocess, sys

API = "https://api.shutterstock.com/v2"
SUB = os.environ.get("SST_SUBSCRIPTION", "4e29a81e85cd4d67a88bb7fb13cf48de")
CAP = 90
LEDGER = os.path.expanduser("~/.sst_ledger.json")


def curl(*args):
    r = subprocess.run(["curl", "-sS", *args], capture_output=True, text=True)
    return r.stdout


def api(method, path, body=None):
    args = ["-X", method, API + path]
    if body is not None:
        args += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = curl(*args)
    try:
        return json.loads(out)
    except Exception:
        return {"error": out[:300]}


def ledger():
    try:
        return json.load(open(LEDGER))
    except Exception:
        return {}


def today():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")


def count(kind):
    return len(ledger().get(today(), {}).get(kind, []))


def note(kind, item):
    lg = ledger()
    lg.setdefault(today(), {}).setdefault(kind, []).append(item)
    json.dump(lg, open(LEDGER, "w"), indent=1)


def already_licensed(kind, media_id):
    path = "/videos/licenses" if kind == "video" else "/images/licenses"
    key = "video_id" if kind == "video" else "image_id"
    d = api("GET", f"{path}?{key}={media_id}&per_page=5")
    for l in d.get("data", []):
        if str((l.get("video") or l.get("image") or {}).get("id")) == str(media_id):
            return l["id"]
    return None


def download(url, out):
    curl("-o", out, url)
    return os.path.exists(out) and os.path.getsize(out) > 10000


def license_video(vid, outdir):
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/{vid}.mp4"
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        return {"file": out, "cached": True}
    lic = already_licensed("video", vid)
    if lic:
        d = api("POST", f"/videos/licenses/{lic}/downloads", {"size": "hd"})
        if d.get("url") and download(d["url"], out):
            return {"file": out, "relicensed": False, "license": lic}
    if count("video") >= CAP:
        return {"error": f"tope diario de {CAP} licencias de vídeo alcanzado"}
    d = api("POST", f"/videos/licenses?subscription_id={SUB}", {"videos": [{"video_id": str(vid), "size": "hd"}]})
    row = (d.get("data") or [{}])[0]
    url = (row.get("download") or {}).get("url")
    if not url:
        return {"error": json.dumps(d)[:400]}
    note("video", vid)
    ok = download(url, out)
    return {"file": out if ok else None, "license": row.get("license_id"), "new": True}


def license_image(iid, outdir):
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/{iid}.jpg"
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        return {"file": out, "cached": True}
    lic = already_licensed("image", iid)
    if lic:
        d = api("POST", f"/images/licenses/{lic}/downloads", {"size": "huge"})
        if d.get("url") and download(d["url"], out):
            return {"file": out, "relicensed": False, "license": lic}
    if count("image") >= CAP:
        return {"error": f"tope diario de {CAP} licencias de imagen alcanzado"}
    d = api("POST", f"/images/licenses?subscription_id={SUB}", {"images": [{"image_id": str(iid), "size": "huge"}]})
    row = (d.get("data") or [{}])[0]
    url = (row.get("download") or {}).get("url")
    if not url:
        return {"error": json.dumps(d)[:400]}
    note("image", iid)
    ok = download(url, out)
    return {"file": out if ok else None, "license": row.get("license_id"), "new": True}


def preview_video(vid, preview_url, outdir):
    """Vista previa con marca de agua (gratis) + hoja de 6 fotogramas y fps, para revisar antes de licenciar."""
    os.makedirs(outdir, exist_ok=True)
    mp4, sheet = f"{outdir}/{vid}_prev.mp4", f"{outdir}/{vid}_prev.jpg"
    curl("-o", mp4, preview_url)
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=r_frame_rate,width,height",
                        "-of", "json", mp4], capture_output=True, text=True)
    info = json.loads(p.stdout or "{}")
    dur = float(info.get("format", {}).get("duration", 10))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vf", f"fps={6 / max(dur, 1):.4f},scale=320:-1,tile=6x1",
                    "-frames:v", "1", sheet])
    return {"sheet": sheet, "duration": dur, "streams": info.get("streams")}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "status":
        print(json.dumps({"video": count("video"), "image": count("image"), "cap": CAP}))
    elif a[0] == "preview":
        print(json.dumps(preview_video(a[2], a[3], a[4])))
    elif a[0] == "video":
        print(json.dumps(license_video(a[1], a[2])))
    elif a[0] == "image":
        print(json.dumps(license_image(a[1], a[2])))
