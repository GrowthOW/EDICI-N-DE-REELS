# Orbis Ways — estilo de cartelas (para reutilizar en próximos videos)

Este es el "design system" de motion graphics extraído de las láminas de
"Top destinos 2027", guardado para reusarlo en los próximos videos que se
pidan en este proyecto — sin depender de que el texto venga horneado en un
PNG como la primera vez.

- `tokens.json` — colores exactos, tipografía y proporciones de layout.
- `components.css` — clases CSS listas para montar las mismas piezas
  (`.ow-country-label`, `.ow-badges-row` / `.ow-badge`, `.ow-pill`,
  `.ow-headline`) con texto nuevo cada vez, en vez de recortar imágenes.

## Piezas del sistema

1. **Country label** — país(es) en mayúsculas, blanco, sin fondo, con
   letter-spacing amplio. Esquina superior izquierda.
2. **Badges (KM · DÍAS · NIVEL)** — 3 cajas en fila, fondo azul-marino
   translúcido (`rgba(10,30,45,.45)`), valor grande blanco + caption
   amarillo (`#F0D723`) en mayúsculas.
3. **Pill de ubicación** — chip azul sólido (`#1474A4`), texto blanco en
   mayúsculas. Va justo encima del titular.
4. **Titular** — 2-3 líneas, blanco, Poppins ExtraBold/Black, interlineado
   muy apretado (1.05-1.1), tono editorial/inspiracional.
5. **Grading de foto** — degradado oscuro en el tercio inferior + leve
   viraje frío/teal para que el texto blanco siempre tenga contraste.

Tipografía: Poppins ExtraBold/Black (alternativas cercanas: Baloo 2 Bold,
Fredoka SemiBold, Nunito ExtraBold).

## Cómo se usa de ahora en adelante

En vez del truco de "desenfoque→foco" sobre un PNG ya renderizado (usado en
el primer intento, que no convenció), los próximos videos deberían montar
estas cartelas como **elementos de texto reales** (HTML/CSS o el motor que
se use) sobre las fotos, para poder animarlas con más libertad: entradas,
salidas, texto dinámico por slide, etc., manteniendo siempre estos mismos
colores, tipografía y proporciones de layout.
