# EDICIÓN DE REELS — Orbis Ways

Videos de marketing (reels / stories 1080×1920) de Orbis Ways.

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
- Cierre con el logo blanco (`scripts/orbisways_style/logo/`) + web.
- Cartelas siempre como texto real (HTML/CSS), no como imagen.

## Pipeline

`scripts/v2/` (ver README raíz): `segments.json` (clips, tramos, recorte,
música) + `content*.json` (textos por idioma) → `build_all.sh`.
Los renders largos (ffmpeg/Playwright) hay que lanzarlos en primer plano
con timeout amplio: en segundo plano el entorno los congela.
