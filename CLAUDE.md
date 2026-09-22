# EDICIÓN DE REELS — Orbis Ways

Videos de marketing (reels / stories 1080×1920) de Orbis Ways, una agencia
de viajes de senderismo (walking holidays). Guía paso a paso para el
equipo: `docs/GUIA_EQUIPO.md`.

## Estilo de marca: obligatorio en cualquier pieza nueva

Seguir siempre `scripts/orbisways_style/` (README, `tokens.json`,
`components.css`). En particular:

- **Tipografía**: títulos y rótulos (nombres de ruta, pills, CTA, datos,
  país) en **Manrope ExtraBold 800**; cuerpo / frases en **Liberation Sans
  engrosada a extra bold** (trazo de 3px del mismo color). Fuentes
  incrustadas desde `scripts/orbisways_style/fonts/`. No usar Poppins ni
  otras familias.
- El **nombre de la ruta** en la pill azul `#1474A4` es el elemento más
  grande e importante.
- Datos clave (país + km/días/nivel) en un bloque junto al nombre de la
  ruta, abajo a la izquierda y fuera de la zona de la UI de Instagram; nunca
  arriba del todo.
- Mantener el degradado oscuro inferior para la legibilidad.
- Cierre con el logo blanco (`scripts/orbisways_style/logo/`) + frase corta
  + web; sin etiquetas extra.
- Cartelas siempre como texto real (HTML/CSS), no como imagen.
- Textos en otros idiomas: adaptar (transcreación), no traducir literal.
  Nombres de ruta sin traducir.

## Pipeline

`scripts/v2/`: `segments.json` (clips por segmento, tramo, recorte/paneo,
música) + `content*.json` (textos por idioma, misma `key` que el segmento)
→ `build_all.sh <salida.mp4> [content.json]`.

- `preview.py [content.json]` para validar cartelas en segundos antes del
  render completo, y `crop_preview.py` para elegir encuadres.
- `SKIP_BG=1` solo si `segments.json` no ha cambiado.
- Enseñar al usuario frames de prueba antes de gastar un render completo.

## Lecciones del entorno

- Los renders largos (ffmpeg/Playwright) hay que lanzarlos en **primer
  plano con timeout amplio**: en segundo plano el entorno los congela.
- Cada segmento lleva su propia entrada de ffmpeg; compartir un único
  archivo con tramos fuera de orden bloqueaba el filtro.
- El proxy bloquea orbisways.com, media de Canva y GitHub raw: pedir los
  archivos al usuario por el chat. Las fuentes se bajan con `npm pack
  @fontsource/<familia>`.
- Límite de 30 MB para enviar archivos por el chat (el reel con crf 20
  ocupa unos 20 MB).
- No inventar logos ni material de marca: si falta, pedirlo.
