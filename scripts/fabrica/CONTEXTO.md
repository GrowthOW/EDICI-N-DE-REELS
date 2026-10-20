# Contexto Fábrica de contenidos Orbis Ways (leer entero)

Orbis Ways: agencia de viajes de senderismo autoguiado (walking holidays) y Camino de Santiago. Incluye alojamientos rurales de calidad, TRANSPORTE DE EQUIPAJE de etapa a etapa (el cliente camina solo con mochila de día ligera), asistencia 24/7 y documentación/app de ruta. Lema exacto: «Walk it, Ride it, Live it». Web: orbisways.com (NO va en las piezas orgánicas: ver abajo).
REGLA GENERAL: todo busca acelerar el crecimiento de la facturación. Prioriza rutas y mercados que más facturan.

## Público
Personas de 50-65 años, mejor en pareja, activas, que caminan 15-25 km/día con ropa técnica, botas y mochila de día. NUNCA mochilas grandes de trekking (vendemos traslado de equipaje). Nada de ropa de calle.

## Facturación últimos 12 meses (Zoho) — rutas que más venden
- EN (UK+US, 8,3 M€): Camino Portugués de la Costa completo desde Oporto (705k), Camino desde Sarria 7/8/11 días (1,1M), Rota Vicentina Fisherman's Trail (247k), Camino Francés completo desde St-Jean (246k), Cotswold Way 12 días (239k), Portugués Costa desde Vigo/Baiona (586k), Tour du Mont Blanc (385k), West Highland Way 9 días (165k), Portugués desde Tui (154k).
- ES (1,9 M€, 83% Camino): Camino desde Sarria 7/8 días (592k), Portugués Costa desde Baiona/Vigo/Oporto (228k), Portugués desde Tui (139k), Sarria 11 días, Camino Inglés desde Ferrol, Lebaniego, Primitivo desde Oviedo, West Highland Way.
- DE (2,5 M€, el walking pesa más que el Camino): Rota Vicentina Fischerpfad (377k + 150k), Portugiesischer Küstenweg ab Porto (246k) / ab Baiona / Vigo, Jakobsweg ab Sarria, West Highland Way 9-10 Tage (129k), South West Coast Path St Ives–Penzance (69k), Französischer Jakobsweg komplett.
- Año Santo Xacobeo 2027 (en español SIEMPRE «Año Santo Xacobeo 2027», nunca solo «Año Santo 2027»; Iván, 19 oct). Las piezas que tratan de él llevan la etiqueta amarilla de evento encima del titular (produce.py, `badge_for`). Gran oportunidad (pipeline 2027 +45% vs año pasado). Orbis NO compra cupos por adelantado: no prometer "plazas reservadas"; sí avisar de fechas con alta demanda.

## Formatos que hay que entregar (por idioma y día)
- 3 REELS verticales 1080x1920, 12-25 s (se publican en Instagram Reels, TikTok, YouTube Shorts y Facebook Reels con copy adaptado a cada canal). Al menos 1 de cada tanda MULTIPANTALLA sencillo (`split` arriba/abajo, `triple` o `grid4`, con una etiqueta corta por pantalla).
- 3 CARRUSELES de Instagram 1080x1350 (5-7 láminas; las imágenes fijas de Instagram van siempre en carrusel).
- 3 posts Facebook (imagen 1080x1350) — tono más informativo, público algo mayor.
- 3 posts LinkedIn 1200x1200 — tono profesional (datos del sector, sostenibilidad, Año Santo, turismo lento), sin vender.
- STORIES de Instagram 1080x1920: 2 en imagen y 1 en vídeo, cada una con un sticker sugerido (encuesta, quiz, pregunta, deslizador). Texto arriba; abajo queda libre para el sticker y la respuesta.
- 1 post COMPARANDO dos rutas parecidas (TMB vs West Highland Way, Portugués por la Costa vs Rota Vicentina, Cotswold Way vs South West Coast Path, Sarria vs Tui…), SIEMPRE EN CARRUSEL: portada en pantalla partida y una lámina partida por aspecto (distancia, inicio y final, terreno, paisaje, para quién), con fotos distintas y datos verificables.
- Ninguna pieza termina con cartela de logo, lema o web (Iván, 18 oct: «no queda orgánico»).

## Redes orgánicas: nada de anuncio (Iván, 18 oct)
- En las piezas (texto en pantalla, imagen y copy) NO va orbisways.com, ni «link in bio», ni logo, ni cartela final de marca, ni el lema. El reel termina en su último plano con un fundido corto.
- La ruta va como etiqueta de ubicación discreta (chincheta), como las de la propia red, no como pill de marca.
- Nada de llamadas de venta («reserva», «pide fechas», «plazas», «book now»…). CTA solo suave: guardar, compartir, comentar, responder la story.
- Fotos y vídeo de calidad aceptable siempre: solo clips HD/4K de la biblioteca (para fotos fijas, fotogramas de clips de 1920 px o más); nada oscuro, borroso ni con marca de agua.

## SEO social: obligatorio en cada pieza (Iván, 19 oct: «doy por hecho que el texto está todo priorizado por SEO»)
Instagram, TikTok, YouTube, Facebook y LinkedIn son buscadores: leen el texto en pantalla, el copy, el título y el texto alternativo. Cada pieza lleva `seo`:
- `keyword`: UNA palabra clave principal, como la busca la gente en ese país e idioma (transcreación, no traducción: «Camino desde Sarria», «Camino from Sarria», «Jakobsweg ab Sarria»). Sale de los hallazgos de la sala SEO del Centro, de `seo_keywords.json` o de búsquedas reales (autocompletado, «la gente también pregunta», foros), siempre citadas en `seo.source`.
- `secondary`: 2-3 variantes o preguntas relacionadas.
- `altText`: una frase descriptiva por imagen (o lámina), con la palabra clave si encaja de forma natural.
- `ytTitle` en los reels: título de YouTube Shorts de 60 caracteres como máximo, con la palabra clave al principio.
Dónde va la palabra clave: en el rótulo del gancho o el titular de la portada si queda natural; en los primeros 125 caracteres del copy de cada canal; en el título y las dos primeras líneas de la descripción de YouTube; y en 1 de los 3-5 hashtags (1 de ruta, 1 de destino, 1-2 de nicho; nada de hashtags genéricos tipo #travel). Nunca forzada ni repetida: primero que se lea natural.

## Tipografía y azul de marca (Iván, 20 oct: «utiliza Nunito y el azul del manual en todas las creas»)
- Titulares y chips en **Nunito** (800 titulares, 700 chips, etiquetas y contador), el sustituto de Caros Soft Bold del brandbook mientras no haya licencia. El texto secundario va en **Mulish** 700 (sustituto de Museo Sans), sin contorno. Nunca menos de 22 px a 1080.
- La etiqueta de la ruta, los rótulos de cada pantalla y el badge de evento van en chip **azul de marca #1376A4** con texto blanco. Nada más de color.
- Limpio y sobrio (Iván, 20 oct: «no quiero bolds en blanco como hay en unas creas, solo la fuente en blanco y algún fondo azul Orbis en el nombre de los destinos»): texto en blanco sobre la foto, sin cajas blancas detrás del texto, sin contornos, sin amarillo ni más adornos.
- Zona segura de Instagram SIEMPRE (Iván, 20 oct: «nada de la información importante puede quedar tapada por los iconos de la app»): en 9:16, top 210, laterales 48/52, abajo 370 y, desde y=1118, nada a la derecha de x=921 (botones). En carruseles, sin contador propio y lejos de los iconos. cap.js lo comprueba: una pieza con «fuera de zona» o «tapado por los botones de IG» no se sube.
- Lo aplica `render.py` solo; no se cambia a mano en el brief. Si llega la Caros Soft con licencia, se sustituye en `FONTS`.

## Referencia de estilo: @_thru_hiking (Iván, 20 oct)
Cuenta de Instagram que nos gusta como referencia: https://www.instagram.com/_thru_hiking/ (grandes datos de alcance y comunidad).
- Formato favorito de Iván: **entrada por el mapa y paso a imágenes reales**, como https://www.instagram.com/p/DdsyksTt2RW/. El vídeo arranca con un mapa 3D o un vuelo sobre la ruta (dónde está, por dónde va) y enlaza con planos reales del sendero.
- Cómo hacerlo con lo que tenemos: el vuelo 3D de Virtual Routes (https://claude.ai/artifact/4t1wUrkkXdhmvMnGK9Dx4n) o el Configurador de Mapas Animados con el GPX real de la ruta como primer plano (2-4 s), y después los clips reales de la biblioteca. Mismo estilo de siempre: texto blanco en Nunito y el destino en chip azul.
- Proponer al menos un reel así en cada tanda de vídeos, empezando por las rutas que más facturan.

## Orbis habla como fuente autorizada (Iván, 19 oct: «quita referencia de las fuentes, nosotros mismos somos una fuente autorizada»)
En las piezas (texto en pantalla, láminas, copys, títulos y descripciones) NO se citan fuentes: nada de «según la Xunta», «(Oficina del Peregrino)», «Source: …», «according to…», «laut…», «je nach Quelle». Los datos se dan en primera persona de experto («Desde Sarria salen 3 de cada 10 peregrinos», «Unos 10.000 m de desnivel positivo»). Las fuentes siguen siendo obligatorias, pero solo DENTRO de la ficha (justification, sources, explain), para comprobar que el dato es real; nunca en lo que se publica. Si un dato es dudoso o varía según quién lo mida, se redondea («unos», «más de») en lugar de citar.

## Orden de publicación: de más a menos importante (Iván, 19 oct)
En la sala, las piezas de cada canal se ordenan de izquierda a derecha por prioridad, y cada ficha explica por qué en `priority` {score, driver, why, factors}: lo calcula `prioridad.py` con cuatro palancas y lo pinta el Centro («Nº 1 · motivo» y en la Justificación):
- **Volumen de búsqueda** de la palabra clave en ese mercado.
- **Tipo de producto**: lo que más factura en ese mercado (cifras de Zoho de arriba).
- **Trend que ya ha funcionado** en otra cuenta (con métrica en `justification.trend.examples`).
- **Momento**: Año Santo Xacobeo 2027, temporada de la ruta.
El motivo dice cuál pesa más y cuál le sigue, con el dato. Si ninguna palanca destaca, lo dice («Sin palanca fuerte»).

## Alimentarse de las salas
Cada tanda parte de los hallazgos de TODAS las salas del Centro (colección `findings`: social, viral, instagram, tiktok, youtube, facebook, linkedin, community, competencia, seo, product, pr, cro, council). Cada pieza cita en `justification.findings` los ids en que se apoya.

## Estilo de las piezas
- Formatos SENCILLOS que funcionan en búsqueda y en feed: p.ej. pantalla partida arriba/abajo comparando dos cosas, "3 cosas que…", "lo que nadie te cuenta de…", "cuánto cuesta / cuántos km", POV caminando, antes/después, mapa de etapas, pregunta-respuesta de búsqueda real ("¿se puede hacer el Camino sin cargar mochila?").
- Planos reales, que parezcan grabados por un cliente o creador, no anuncio. NADA de cámara lenta ni planos muy producidos/drones cinematográficos en exceso. Prioriza días SOLEADOS.
- Máx. 3 bloques de texto en pantalla por reel, frases cortas, nunca se pisan. Texto real (lo maquetamos nosotros).
- Hoteles, habitaciones y desayunos: NUNCA de banco de imágenes (si una pieza los necesita, descártala).
- Material SOLO de la ruta real que se nombra (nada del Camino en otras rutas, nada de otra costa haciéndose pasar por la Rota Vicentina).
- Textos en cada idioma: transcreación nativa, no traducción literal. Nombres de ruta sin traducir cuando sea nombre propio (West Highland Way, Rota Vicentina, Cotswold Way, Tour du Mont Blanc).
- Sin datos inventados: precios, km o etapas solo si son reales y verificables (km de las rutas oficiales son públicos; precios de Orbis NO los des si no los tienes). La fuente se guarda en la ficha, no se cita en la pieza.

## Regla reforzada por Iván (18 oct)
- PRIORIZAR SIEMPRE REALISMO Y NATURALIDAD: planos que parezcan grabados por un viajero real.
- EVITAR: cámara lenta, planos muy cercanos (primerísimos planos de caras, manos, pies, detalles), planos muy producidos o de anuncio, poses mirando a cámara, drones cinematográficos.
- PREFERIR: planos generales y medios de la ruta y de gente caminando de forma natural, luz de día soleada, sonido ambiente creíble.

## Objetivo de la Fábrica (Iván, 18 oct)
Contenido de calidad y sobre todo ATRACTIVO para redes, para maximizar alcance, engagement, viralidad y crecimiento de la comunidad lo más rápido posible, además de tráfico a la web y ventas orgánicas desde redes. Equilibrio entre contenido de PRODUCTO (rutas Orbis, servicio, por qué con nosotros) y contenido INFORMACIONAL (resolver dudas, consejos, curiosidades, inspiración). Orientativo: ~1 de cada 3 piezas de producto, 2 de cada 3 informacionales/inspiración con CTA suave.
