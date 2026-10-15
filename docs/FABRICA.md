# Fábrica de contenidos de Orbis Ways (24/7)

Orden de Iván (15 oct 2026): «Quiero que esto sea una fábrica de contenidos que funcione 24/7 sin necesidad de aprobación ni rondas dos veces al día; que vaya trabajando continuamente y yo ya iré dando feedback sobre las piezas finales, pudiendo ajustar o descartar lo que considere». También: «ve generando las propuestas finales sin que te tenga que confirmar… piezas que funcionen, que se hagan virales, algunas más comerciales y otras más puramente informacionales, para convertir nuestros canales en la referencia del sector, ganando comunidad y engagement».

Este documento es el manual de cada ciclo. Manda junto con `docs/PIEZAS_FEEDBACK.md` (reglas del feedback de Iván); si chocan, manda PIEZAS_FEEDBACK.

## Qué cambia respecto a las rondas de antes

- **No hay aprobación previa.** Toda pieza del calendario (salvo `descartada` y `publicada`) se lleva hasta el final: archivos terminados adjuntos en su entrada del calendario, reproducibles y descargables en la sala de Diseño del centro. Iván revisa las piezas finales y pide cambios o las descarta allí.
- **No hay rondas fijas.** Un ciclo por hora, todos los días. Cada ciclo termina una o dos piezas y deja la cola lista para el siguiente.
- La ronda «Indicaciones al momento» sigue aparte: aplica en el acto lo que Iván escribe en una pieza.

## Centro de control

- URL: https://claude.ai/artifact/SYE8rodqybJ3uKwcXw2PBX. Se lee y escribe solo con la herramienta ArtifactData (cada llamada con esa `url`). Assets (vídeos, PNG) con la herramienta Artifact (`asset: true`).
- Calendario: colección `calendar` (esquema completo en el prompt de la ronda de calendario, copia en `centro-control/rondas/calendario.txt` del repo de control). Campos clave: lang, channel, date, time, market, format, title (en español), hook, keyword, seo, why, justification, ready_material, design, version, feedback, files, status.
- Estado de la fábrica: documento `fabrica/estado` {lastRun, cola, hechasHoy, ultimaPieza, aviso}. Cada ciclo escribe `cycles/<STAMP>-fabrica` {ts, pata: "calendario", findings: 0, actions: 0, entries, updated, summary}.

## Mezcla editorial (para ser la referencia del sector)

Por idioma (EN para UK y EE. UU., ES para España y Latinoamérica, DE para Alemania, Austria y Suiza):
- **60 % informacional y útil:** guías de etapa, datos verificados, cómo prepararse, qué llevar, cuándo ir, comparativas de rutas, errores típicos, mapas y desniveles. Son las que se guardan y se comparten.
- **25 % virales y emocionales:** formatos que están funcionando ahora en ese idioma (tendencia con 2+ ejemplos públicos de los últimos 90 días con métricas), POV, «nadie te cuenta», antes y después, retos, preguntas que abren comentarios.
- **15 % comerciales suaves:** el servicio de Orbis (traslado de equipaje, hoteles con encanto, dossier, asistencia 24/7) contado con hechos, sin urgencias falsas ni «plazas limitadas».
- Toda pieza nace de una búsqueda real en su idioma y de una tendencia que funcione en su idioma (ver la justificación en el prompt de calendario). Cada pieza busca una acción de comunidad: guardar, compartir o comentar.

## Ciclo (una vez por hora)

0. **Ahorro y avisos.** Si aparece cualquier aviso de uso o de límite, escribe `fabrica/estado.aviso` con el texto y la hora, termina la pieza en curso y para el ciclo. Sin subagentes salvo para investigar tendencias (máximo 3 a la vez). Renders cortos, sin repetir renders.
1. **Indicaciones primero.** Entradas con `status: "cambios"` y feedback con `done: false`: aplícalas (rehaz archivos si la pieza ya tenía), marca cada indicación con done, doneTs, version y reply, sube version y deja `status: "lista"`.
2. **Cola.** Entradas de `calendar` desde hoy hasta +14 días, sin `files` y con status distinto de `descartada` o `publicada`. Orden: primero las que Iván aprobó, después por fecha. Si en los próximos 7 días quedan menos de 10 piezas por producir, **planifica** nuevas entradas (con la mezcla editorial, la cadencia por canal e idioma del calendario y justificación completa con búsqueda y tendencia) y déjalas `lista` con su design.
3. **Producción.** Termina 1 pieza (2 si son estáticas) de principio a fin:
   - Vídeo 9:16 con material real (versión TikTok sin logo, cierre ni música; versión Reel/Short con cierre `scripts/piezas/endcard_9x16*.png` y música a −14 LUFS) y su portada con texto nativo.
   - Carrusel 4:5 (máx. 8 láminas) o post: PNG renderizados de su design.
   - LinkedIn: imagen y texto con estilo de marca.
   - Blog: borrador completo, brief, metas e imagen destacada.
   Material: Drive MULTIMEDIA (inventario `media/drive-multimedia`; el conector baja archivos de menos de 6 MB) y `sources_raw/`. Solo material de la ruta de la pieza. Si falta, la pieza queda con `ready_material` y una línea «FALTA: …» y la cola pasa a la siguiente.
4. **Revisión.** Hoja de fotogramas o láminas, contra la lista de control (búsqueda, tendencia, look nativo, idioma, cifras con fuente, marca y negocio, indicaciones). Corrige antes de entregar.
5. **Entrega.** Sube los archivos como assets del centro, adjúntalos en `files` de su entrada (con if_version), `version + 1`, `status: "lista"` y `pieceAction: "a-social-AAAAMMDD-fabrica"`. Escribe `PUBLICAR.md` en `piezas/AAAA-MM-DD/<id>/` (descripción, hashtags, comentario fijado, título de Short, texto alternativo y fuentes).
6. **Registro.** Commit y push de textos y código (no vídeos) a la rama `claude/gifted-babbage-7h92wu`. Actualiza `fabrica/estado` y escribe el ciclo.
7. **Aprendizaje.** El feedback de Iván en piezas finales se convierte en reglas en `docs/PIEZAS_FEEDBACK.md`.

## Normas fijas

- Modo informativo: nada se publica ni se envía fuera del centro de control y del repo.
- Nada inventado: toda cifra con su URL en sources; si no se verifica, no sale.
- Marca: Brandbook OW 2027 V1. Eslogan «Walk it, Ride it, Live it» (nunca todo en mayúsculas). Look nativo en redes (ver PIEZAS_FEEDBACK). Nota real de Trustpilot: 4,5.
- Gente de 50-65 bien equipada, sin mochilas de trekking grandes. Nunca hoteles, habitaciones ni desayunos de bancos de imágenes. Sin logos ajenos en la imagen.
- Orbis no contrata cupos por adelantado: nada de «últimas plazas».
- Campos para el equipo, en español; piezas en el idioma de su público, escritas de forma nativa.
