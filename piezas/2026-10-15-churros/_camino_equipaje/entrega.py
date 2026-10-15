# Prepara el update de calendar/<id> para el centro de control.
# Uso: python3 entrega.py <entrada_actual.json> <carpeta_pieza> <salida.json> <files.json> [fuente_extra ...]
# Quita del ready_material la propuesta antigua de clips/montaje y añade PUBLICAR.md (## Publicar + ## Montaje final).
import json, re, sys
cur = json.load(open(sys.argv[1]))
pub = open(sys.argv[2] + '/PUBLICAR.md').read().strip()
rm = cur.get('ready_material', '') or ''
parts = re.split(r'(?m)^(?=## )', rm)
keep = [p for p in parts if not re.match(r'## (Clips propuestos|Montaje final|Publicar)', p)]
new_rm = (''.join(keep).rstrip() + '\n\n' + pub + '\n').lstrip()
sources = list(cur.get('sources', []))
for s in sys.argv[5:]:
    if s not in sources:
        sources.append(s)
data = {'ready_material': new_rm, 'files': json.load(open(sys.argv[4])), 'version': (cur.get('version') or 1) + 1,
        'pieceAction': 'a-social-20261015-churros', 'working': None, 'sources': sources}
json.dump(data, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1)
print('version', data['version'], 'len rm', len(new_rm), 'secciones', [p.split('\n')[0] for p in keep])
