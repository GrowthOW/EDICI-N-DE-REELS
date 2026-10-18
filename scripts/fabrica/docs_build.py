"""Fábrica: fichas de calendario listas para la sala a partir de los manifest y de los assets subidos.

Uso:
  python3 docs_build.py <assets.json> <out_dir> <manifest.json> [<manifest.json> ...]

assets.json: {"<ruta local>": "<assetId de 32 hex>"} (resultado de subir los archivos al centro).
Escribe un JSON por ficha en out_dir y batches.json con lotes de hasta 50 escrituras.
"""
import json, os, sys


def main(assets_p, out_dir, *manifests):
    assets = json.load(open(assets_p))
    os.makedirs(out_dir, exist_ok=True)
    writes, missing = [], []
    for mp in manifests:
        for m in json.load(open(mp)):
            if not m.get("ok"):
                continue
            files = []
            for f in m["files"]:
                aid = assets.get(f["local"])
                if not aid:
                    missing.append(f["local"])
                    continue
                files.append({"assetId": aid, "kind": f["kind"], "label": f["label"], "name": f["name"]})
            if not files:
                continue
            for d in m["docs"]:
                doc = dict(d, files=files, ts=d.get("ts") or "2026-10-18T13:30:00Z")
                p = f"{out_dir}/{doc['id']}.json"
                json.dump(doc, open(p, "w"), ensure_ascii=False)
                writes.append({"op": "set", "collection": "calendar", "doc_id": doc["id"], "file_path": p})
    batches = [writes[i:i + 50] for i in range(0, len(writes), 50)]
    json.dump(batches, open(f"{out_dir}/batches.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({"docs": len(writes), "batches": len(batches), "missing_assets": missing[:10]}))


if __name__ == "__main__":
    main(*sys.argv[1:])
