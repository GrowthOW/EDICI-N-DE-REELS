# Guía del equipo — crear y editar reels de Orbis Ways

Todo lo necesario para hacer un reel nuevo o cambiar uno existente: añadir
brutos, cambiar textos o datos, sacar otro idioma y renderizar.

---

## 1. La forma más fácil: pedírselo a Claude

Abre este repo en Claude Code (claude.ai/code) y pídelo en lenguaje normal.
Claude lee `CLAUDE.md` al empezar, así que ya conoce el estilo de marca y
este sistema. Ejemplos:

- *"Te paso un bruto nuevo de la Vía Francígena, añádelo después del
  Cotswold con estos datos: Italia, 120 km, 8 días, nivel moderado."*
- *"Cambia los km del Mont Blanc a 60–170."*
- *"Saca el mismo reel en francés, adaptando las frases, no traducción literal."*
- *"Cambia la música por esta pista y empieza en el segundo 20."*
- *"En el Fisherman's Trail encuadra más a la derecha."*

Los archivos (brutos, música, logos) súbelos directamente al chat: desde el
entorno de Claude no se puede descargar nada de webs como orbisways.com o
Canva.

Consejo: para cambios sencillos (textos, datos, volver a renderizar) usa
**Sonnet** (`/model`), que gasta mucho menos límite que Opus.

---

## 2. Mapa del proyecto

| Carpeta / archivo | Qué es |
|---|---|
| `sources_raw/` | Brutos de video tal cual llegan |
| `sources_audio/` | Pistas de música |
| `scripts/orbisways_style/` | **Design system** de marca: fuentes, logo, colores, tamaños |
| `scripts/v2/segments.json` | **Qué clips salen, en qué orden, qué tramo y con qué encuadre** + la música |
| `scripts/v2/content.json` | **Textos en inglés** de cada cartela |
| `scripts/v2/content_de.json` | Textos en alemán (uno por idioma) |
| `scripts/v2/build_all.sh` | Renderiza el reel completo |
| `scripts/v2/preview.py` | Vista previa rápida de cómo quedan las cartelas |
| `scripts/v2/crop_preview.py` | Compara encuadres verticales de un bruto |
| `output/` | Videos terminados |

Estructura del reel: **intro** → un segmento por ruta → **cierre** (logo +
web). Cada segmento se identifica con una `key` (`intro`, `whw`, `fisherman`,
`cotswold`, `montblanc`, `outro`), que debe ser la misma en
`segments.json` y en `content*.json`. `intro` y `outro` tienen diseño
propio; cualquier otra key usa la cartela de ruta (país + datos + nombre +
frase).

---

## 3. Añadir o cambiar un bruto

1. Copia el clip a `sources_raw/` con un nombre claro
   (p. ej. `francigena_toscana.mp4`).
2. Elige el tramo. Para ver dónde hay cortes de escena:
   ```bash
   ffmpeg -i sources_raw/clip.mp4 -vf "select='gt(scene,0.35)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*"
   ```
3. Elige el encuadre vertical. Los brutos horizontales se recortan a 9:16;
   prueba varias posiciones:
   ```bash
   cd scripts/v2
   python3 crop_preview.py ../../sources_raw/clip.mp4 3 800 1200 1600
   ```
   Abre `crop_preview.jpg` y quédate con el mejor valor. Si el bruto ya es
   vertical, usa `0`.
4. Añade el segmento en `scripts/v2/segments.json`, en el orden en que debe
   salir:
   ```json
   {
     "key": "francigena",
     "src": "sources_raw/francigena_toscana.mp4",
     "src_start": 2.0,
     "src_end": 8.5,
     "crop_x0": 1200,
     "crop_x1": 1200
   }
   ```
   - `src_start` / `src_end`: segundos del bruto que se usan (6–8 s por ruta
     funciona bien; mínimo unos 5 s para que se lean las cartelas).
   - `crop_x0` = `crop_x1` → encuadre fijo. Distintos → paneo suave de uno a
     otro durante el segmento (útil para ir de un paisaje a una persona).
   - `hold_extra` (opcional): congela el último frame N segundos (se usa en
     el cierre).
5. Añade sus textos con la **misma key** en `content.json` (y en cada
   idioma), copiando la estructura de otra ruta:
   ```json
   "francigena": {
     "country": "ITALY",
     "badges": [
       { "value": "120", "cap": "KM" },
       { "value": "8", "cap": "DAYS" },
       { "value": "MODERATE", "cap": "LEVEL" }
     ],
     "pill": "VIA FRANCIGENA",
     "headline": ["Primera línea", "segunda línea", "tercera."]
   }
   ```
6. Vista previa y render (ver §5). **Si has tocado `segments.json`, no uses
   `SKIP_BG=1`**: hay que regenerar el fondo.

---

## 4. Cambiar textos, datos, idioma o música

- **Textos / datos (km, días, nivel, frases):** edita `content.json` (o el
  del idioma). Frases de 2–3 líneas: cada elemento de `headline` es una
  línea.
- **Nuevo idioma:** copia `content.json` a `content_fr.json` (por ejemplo) y
  adapta los textos. Adaptar, no traducir literal: que suene natural para
  ese público. Los nombres de ruta no se traducen.
- **Música:** deja la pista en `sources_audio/` y cambia `music` (ruta) y
  `music_start` (segundo desde el que empieza) en `segments.json`. La
  música se ajusta sola a la duración, con fundido de entrada y salida.
- **Logo del cierre:** `content.json → outro.logo` (logo blanco en
  `scripts/orbisways_style/logo/`).

---

## 5. Previsualizar y renderizar

```bash
cd scripts/v2

# Solo si cambiaste segments.json (clips, tramos, encuadres, orden):
python3 build_background.py

# Vista previa en segundos (un frame por segmento), y avisa si algún texto se sale:
python3 preview.py                    # inglés
python3 preview.py content_de.json    # alemán
# -> preview.jpg

# Render completo (unos 4-5 min):
./build_all.sh ../../output/mi_reel.mp4
# Otro idioma reutilizando el fondo ya generado (unos 4 min):
SKIP_BG=1 ./build_all.sh ../../output/mi_reel_DE.mp4 content_de.json
```

Salida: MP4 1080×1920, 30 fps, H.264 + AAC, unos 20 MB, listo para Instagram.

---

## 6. Reglas de marca (resumen)

Detalle completo en `scripts/orbisways_style/README.md`.

- **Títulos y rótulos** (nombre de ruta, pills, web, datos, país):
  **Manrope ExtraBold**, en mayúsculas.
- **Frases:** **Liberation Sans** engrosada a extra bold.
- El **nombre de la ruta** en la pill azul `#1474A4` es lo más grande.
- País + km/días/nivel **junto al nombre de la ruta**, abajo a la
  izquierda; la parte de arriba del video, limpia.
- Degradado oscuro abajo para que el texto se lea siempre.
- Cierre: logo blanco + frase corta + ORBISWAYS.COM.

---

## 7. Problemas conocidos

- **Renders en el entorno de Claude:** hay que lanzarlos en primer plano
  con un timeout amplio; en segundo plano el entorno los congela y parecen
  colgados.
- **Descargas bloqueadas:** el entorno no puede entrar en orbisways.com,
  Canva ni GitHub para bajar imágenes o fuentes. Los archivos, subidlos al
  chat. Las fuentes se instalan desde npm (`@fontsource/...`), que sí
  funciona.
- **Enviar el video por el chat:** hay un límite de 30 MB; con la
  configuración actual el reel ocupa unos 20 MB.
- **Texto que se sale del cuadro:** `preview.py` lo detecta. Las palabras
  muy largas en los badges (p. ej. ANSPRUCHSVOLL) se reducen solas.
