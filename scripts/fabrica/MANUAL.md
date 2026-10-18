# Fábrica de contenidos v2 — manual de las rutinas

Lo que Iván pidió (18 oct 2026): propuestas **finales** (MP4 e imágenes listos para publicar),
nunca a medias, para cada mercado e idioma (EN, ES, DE). Cada día y por idioma: **3 reels**
(se publican en Instagram Reels, TikTok, YouTube Shorts y Facebook Reels), **3 carruseles de
Instagram** (5-7 láminas: portada con gancho, una idea por lámina y cierre suave para
guardar/compartir; formato `ig_carousel`), **3 imágenes de Facebook** y **3 de LinkedIn**. Iván las revisa en la sala de la Fábrica
del Centro de Control, descarga las que le gustan y pide cambios en la propia pieza.

Reglas de contenido: `CONTEXTO.md` (léelo entero; manda sobre cualquier idea propia).

## Herramientas

| Paso | Herramienta |
|---|---|
| Montaje | `render.py` (reel 1080x1920 y estáticos, textos HTML reales con QA de solapes y zona segura) |
| Producción en lote | `produce.py <LANG> <brief.json> <selection.json> <media_dir> <out_dir> <fecha>` |
| Shutterstock | `sst.py` (licencias con tope de 90/día; redescarga gratis de lo ya licenciado, en 4K si existe) |
| Fichas de la sala | `docs_build.py <assets.json> <out_dir> <manifest.json>...` |
| Biblioteca | `biblioteca/catalog.json` y `biblioteca/lib_info.json` (los 112 de partida) + colección `biblioteca` del Centro (los nuevos) |

## Circuito de clips nuevos (Shutterstock, 18 oct 2026)

La API no puede licenciar con el plan de Iván («Unlimited Downloads», que solo incluye la parte
del catálogo marcada «Unlimited»): da «outside of your collection» siempre. Lo que sí funciona:
1. La Fábrica elige candidatos (2-3 por plano que falte, revisados con `sst.py preview`) y los
   añade a la colección de Iván «Orbis · para licenciar» (id 328831218):
   `POST /v2/videos/collections/328831218/items {"items":[{"id":"…"}]}`.
2. Escribe en el Centro `fabrica/descargas` {pending, collection: "Orbis · para licenciar",
   url, ids, note, ts}: el Centro muestra el aviso a Iván.
3. Iván (o Claude en Chrome por él) descarga en la web los que su plan permite.
4. En cada ronda: `GET /v2/videos/licenses?per_page=50&sort=newest` → los clips licenciados que
   no estén en `biblioteca/catalog.json` ni en la colección `biblioteca` del Centro son nuevos:
   bájalos con `sst.py video <id> <dir> <licenseId>`, míralos (hoja de fotogramas) y
   catalógalos en el Centro (colección `biblioteca`, un doc por clip, mismos campos que
   catalog.json + licenseId). Quítalos de la colección 328831218 (DELETE …/items?item_id=…)
   y actualiza `fabrica/descargas.pending` (los que queden en la colección).
5. Los candidatos que sigan en la colección más de 3 días sin descargar no están en su plan:
   quítalos.

## Límites que hay que respetar

- **Shutterstock API**: 100 peticiones por hora. La app solo puede licenciar su colección;
  los clips nuevos del catálogo completo dan «outside of your collection» hasta que
  Shutterstock conecte la suscripción de Iván. Mientras tanto, **solo la biblioteca** (112
  clips ya licenciados). Redescargar uno: `python3 sst.py video <id> <dir> <licenseId>`
  (licenseId en `biblioteca/lib_info.json`): no gasta cupo. Nunca licencies fuera del tope.
- **Assets del Centro**: máximo 15 MB por archivo (los reels salen a ≤5 Mbps, ~10 MB).
- **Uso de Claude**: Iván no quiere llegar al límite. Si ves un aviso de uso, termina la
  pieza en curso, anótalo en `fabrica/estado.aviso` y para.
- **Sin inventar**: toda cifra con URL; sin precios de Orbis; sin plazas reservadas.
- Material solo de la ruta real; nada de cámara lenta, primeros planos, poses ni mochilas
  grandes; vetados 4014828357 y 4014828363 (mochilas) y 3897286255 y 3897285953 (gente
  joven); 3999121987 sale oscuro en vertical.

## Producción diaria (rutina «Fábrica»)

1. Por idioma, un subagente estratega (Agent) con `CONTEXTO.md`, `biblioteca/catalog.json`,
   la facturación por ruta y mercado (council/baseline del Centro) y lo que ya hay en la
   sala de los últimos 14 días (para no repetir idea ni clip). Investiga con WebSearch
   (tendencias del país, búsquedas, competencia; cita URL) y escribe `briefs/<lang>.json`
   y `selection/<lang>.json` con el formato de la última tanda (ver un doc
   `calendar/fab-*`: campos `brief` y `selection`). 12 piezas: 3 reel, 3 ig_static, 3 fb,
   3 linkedin; ~1 de cada 3 de producto.
2. Baja los clips elegidos con `sst.py` (4K) a `media/video/`.
3. `produce.py` por idioma con la fecha del día siguiente.
4. **Revisión obligatoria**: mira con Read la hoja `_sheet.jpg` de cada reel y cada estático
   (encuadre, mochilas, oscuridad, textos). Corrige y vuelve a montar lo que falle.
5. Sube los archivos finales con Artifact (`action: publish`, `url` del Centro,
   `asset: true`, `file_paths` de hasta 25) y guarda `{ruta local: assetId}` en `assets.json`.
6. `docs_build.py` y escribe las fichas con ArtifactData `batch` (lotes de 50). Añade a cada
   ficha `brief` y `selection` (con `licenseId` en cada plano) para poder rehacerla.

## Cambios que pide Iván (rutina «Indicaciones»)

Una ficha con `feedback` pendiente (`done: false`) y `agent: "fabrica-v2"`:
1. Lee la indicación, `brief` y `selection` de la ficha.
2. Aplica el cambio al brief/selección (texto, plano, orden, duración…), baja los clips con
   `sst.py` y monta solo esa pieza con `produce.py` (brief y selección de una sola pieza).
3. Mira la hoja de fotogramas, sube los archivos nuevos y actualiza **todas las fichas de la
   misma pieza** (`briefId` igual en los cuatro canales del reel): `files` nuevos,
   `version` +1, `brief`/`selection` nuevos, `status: "propuesta"`, y en el feedback
   `done: true`, `reply` (qué has cambiado en una frase) y `version` nueva.
