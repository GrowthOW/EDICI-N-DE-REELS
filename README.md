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
