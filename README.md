# Orbis Ways — Top destinos 2027 (Story animada)

Conversión de las 5 láminas estáticas de "Top destinos 2027" (portada +
4 destinos) en un video animado para Instagram Stories, con textos que
aparecen con animación y transiciones orgánicas entre slides.

- `sources/` — las 5 imágenes originales (1080×1920), tal como se subieron.
- `scripts/` — pipeline de generación del video.
- `output/orbisways_top_destinos_2027_story.mp4` — video final (1080×1920,
  30fps, H.264, ~18s).

## Cómo funciona

Cada lámina ya trae el texto "horneado" en el PNG (no hay capas separadas),
así que el efecto de "las letras aparecen" se logra por bloque de texto
(país, badges de KM/días/nivel, pill de ubicación, líneas del titular):

1. `make_assets.py` detecta con Pillow/NumPy los bloques de texto de cada
   imagen (por color de píxel: blanco/amarillo), genera un fondo con esos
   bloques desenfocados (`*_bg.jpg`) y recorta cada bloque nítido por
   separado (`*_pill.jpg`, `*_h1.jpg`, etc.) en `scripts/assets/`.
2. `index.html` monta esos fondos + recortes en un timeline JS
   (`renderAtTime(t)`) que anima cada bloque de desenfoque→foco + fade +
   slide-up escalonado, con Ken Burns sutil en el fondo y crossfade con
   parallax entre slides (transición orgánica, no corte seco).
3. `capture.py` reproduce la página con Playwright/Chromium en modo
   determinista (avanza el timeline frame a frame, no en tiempo real) y
   exporta 30 fps a `scripts/frames/`.
4. ffmpeg codifica los frames a H.264/yuv420p con `faststart`, listo para
   subir a Instagram.

## Regenerar el video

```bash
cd scripts
python3 make_assets.py      # regenera assets/ a partir de sources/
python3 capture.py          # exporta scripts/frames/*.png (requiere playwright + su navegador)
ffmpeg -y -framerate 30 -i frames/frame_%05d.png \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 17 -preset slow \
  -movflags +faststart -r 30 \
  ../output/orbisways_top_destinos_2027_story.mp4
```

El video no incluye audio; queda listo para añadir música/voz al publicarlo.

## v2 — cartelas sobre video bruto (`scripts/v2/`)

Segunda pieza: mismas cartelas (design system en `scripts/orbisways_style/`),
pero ahora montadas como **texto real** (no imagen) sobre clips de video
brutos, en vez de sobre fotos estáticas.

- `sources_raw/` — clips brutos de producto tal como se recibieron.
- `sources_audio/background_music.mp3` — pista musical de la pieza.
- `scripts/v2/segments.json` — qué clip y qué tramo usa cada
  producto/destino, cómo se recorta a vertical (con paneo cuando hace falta)
  y qué música lleva.
- `scripts/v2/content.json` — texto de cada cartela (país, km/días/nivel,
  nombre, frase) por segmento.
- `scripts/v2/build_background.py` — recorta cada tramo a 9:16, aplica el
  grading de marca, encadena las transiciones (crossfade)
  y calcula el timeline (`timeline.json`) que usa la capa de texto.
- `scripts/v2/overlay_template.html` + `overlay_capture.py` — renderizan las
  cartelas como HTML/CSS real (fuente Poppins, mismos colores/proporciones)
  sobre fondo transparente, con Playwright, frame a frame.
- `scripts/v2/build_all.sh` — encadena los 3 pasos + composición final con
  ffmpeg (`overlay` de la capa de texto sobre el video, fade final y
  música).
- `output/orbisways_top_destinos_2027_reel.mp4` — resultado.

```bash
cd scripts/v2
./build_all.sh ../../output/mi_reel.mp4
```

La cartela de cierre (`outro` en `content.json`) continúa la última toma con
un velo azul y muestra la web. Para añadir el isotipo, poner la ruta del
archivo (PNG/SVG con fondo transparente, relativa a la raíz del repo) en
`content.json → outro.logo` y volver a renderizar.

Para cambiar clips, música o datos: editar `segments.json` y `content.json`
y volver a correr `build_all.sh`. La fuente Poppins va incrustada en
`scripts/orbisways_style/fonts/` (no depende de internet al renderizar).
