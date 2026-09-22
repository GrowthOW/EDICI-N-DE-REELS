# Orbis Ways — design system de cartelas / motion graphics

Estilo fijo para todas las piezas de video de Orbis Ways (reels, stories).
Las cartelas se montan siempre como **texto real** (HTML/CSS) sobre el
video o la foto, nunca como imagen con el texto ya puesto.

- `tokens.json` — colores, tipografía, tamaños y layout en crudo.
- `components.css` — clases listas (`.ow-info`, `.ow-country-label`,
  `.ow-badge`, `.ow-pill`, `.ow-headline`, `.ow-outro*`).
- `fonts/` — Manrope 700/800 y Liberation Sans Bold, incrustadas (no se
  depende de internet ni de las fuentes del sistema).
- `logo/` — logo blanco y a color, fondo transparente.

## Tipografía (regla fija)

| Uso | Fuente | Peso |
|---|---|---|
| **Títulos y rótulos**: nombre de la ruta (pill azul), pill del intro, CTA de la web, datos km/días/nivel, país, captions | **Manrope** | ExtraBold 800, MAYÚSCULAS |
| **Cuerpo**: frases del intro, de cada destino y del cierre | **Liberation Sans** (estilo Arial/Helvetica) | extra bold* |

\* Liberation Sans solo existe en Bold; se lleva a extra bold con un trazo
del mismo color bajo el relleno (`-webkit-text-stroke:3px` +
`paint-order:stroke fill`). Mismas letras, más gruesas.

No usar Poppins ni otras familias.

## Piezas

1. **Bloque de info por ruta** — abajo a la izquierda, anclado a 330px del
   borde inferior (fuera de la zona que tapa Instagram), crece hacia arriba:
   país → 3 badges → pill con el nombre de la ruta → frase. La parte de
   arriba del video queda limpia.
2. **Badges (KM · DÍAS · NIVEL)** — cajas translúcidas azul marino, valor
   blanco + caption amarillo `#F0D723`.
3. **Pill del nombre de la ruta** — azul sólido `#1474A4`, Manrope 800 a
   66px. Es el elemento más importante de cada cartela.
4. **Frase** — 2-3 líneas en blanco, Liberation Sans extra bold, 60px.
5. **Legibilidad** — degradado oscuro en la mitad inferior + grading frío.
6. **Cierre** — la última toma sigue bajo un velo azul marino; centrado:
   logo blanco → frase corta → pill con la web → caption.

## Colores

Azul pill / azul oscuro del logo `#1474A4` · azul claro del logo `#3E9DCA`
· amarillo captions `#F0D723` · blanco `#FFFFFF`.
