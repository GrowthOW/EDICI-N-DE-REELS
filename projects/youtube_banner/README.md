# Banner del canal de YouTube

Lienzo de 2560×1440 según el brandbook 2027 (p. 34). Todo el contenido importante
va en la zona segura central de 1546×423, que es lo único que se ve en el móvil.
El escritorio enseña la franja de 2560×423 y la TV el lienzo entero.

Sin eslogan: solo el logo y la web.

| Variante | Qué es |
|---|---|
| `cresta` **(elegida)** | Panorámica con el timelapse de la cresta nevada del Mont Blanc entre nubes. Logo blanco y web arriba a la izquierda, sobre el cielo y con un degradado azul, para que la cumbre se vea en la franja. Usa el original de 1080p: la marca de Clideo queda por debajo del lienzo. |
| `mosaico` | Cajas redondeadas sobre gris Orbis #222222 (recurso "mosaico" del brandbook) con caja blanca para el logo a color y la web en azul oscuro #1376A4. |
| `blanco` | Las mismas cajas sobre blanco, con la caja de marca en azul oscuro y el logo y la web en blanco. |
| `panoramica` | Foto a sangre del macizo del Mont Blanc (dron 4K), con el logo blanco y la web sobre el cielo y un degradado azul suave. |

## Uso

    python3 projects/youtube_banner/render.py [cresta panoramica mosaico blanco]

- `salida/banner_<variante>.jpg`: el archivo que se sube a YouTube.
- `salida/prueba_<variante>.jpg`: cómo queda en TV, escritorio y móvil.

## Fotos

Las fotos (`fotos/`) son fotogramas de los brutos. Al subir fotos reales de
clientes, se cambian en `banner.html`: lista `cajas`, con `pos` para el encuadre.
