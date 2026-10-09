# Piezas diarias de redes

Kit para montar las piezas del día con la marca del OW DESIGN SYSTEM. El texto siempre es real (HTML/CSS renderizado con Chromium), nunca una imagen.

| Archivo | Para qué |
|---|---|
| `brand.css` | Tokens de color, sustitutos tipográficos (Nunito y Mulish) y estilos `.k` (palabra en caja azul sobre foto) y `.kl` (palabra en azul claro sobre blanco) |
| `render.js` | `still`: HTML → PNG por estados. `frames`: HTML animado (`window.renderAt(t)`) → secuencia PNG transparente |
| `endcard.html` / `endcard_9x16.png` | Cierre de Reel y Short (logo blanco, claim, web y slogan). En TikTok no hay cierre |

## Plantillas de referencia (`piezas/2026-10-09/`)
- **`tmb_tiktok/`:** vídeo 9:16 a 25 fps.
  - `build_bg.py` hace cortes secos con empuje lento.
  - `overlay.html` anima el texto palabra a palabra, con el gancho visible desde el fotograma 0 y el bloque inferior fijo (país, chip con la ruta y 3 datos).
  - `cover.html` es la portada.
- **`holyyear_carrusel/`:** carrusel 4:5 de 8 láminas, que alterna foto con caja azul, láminas blancas con titular bicolor, cifra grande y CTA con un único amarillo.
- **`linkedin_datos/`:** imagen 4:5 de datos con fuente.

## Flujo
1. Leer `docs/PIEZAS_FEEDBACK.md`. Las reglas que contiene mandan.
2. Elegir los temas con el centro de control (acciones y hallazgos de Redes y SEO) y una búsqueda principal por pieza.
3. Montar en `piezas/AAAA-MM-DD/<pieza>/`, revisar con hojas de fotogramas y corregir.
4. Escribir `PUBLICAR.md`, con los textos con SEO de cada canal.
5. Enviar al chat, subir al centro de control (acción `a-social-AAAAMMDD-piezas` con `files`) y hacer commit.

## Renders
- Lanzarlos en primer plano y con un timeout amplio.
- Las duraciones deben ser múltiplos de 0,04 s (25 fps).
