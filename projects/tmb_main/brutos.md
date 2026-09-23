# TMB video principal — inventario de brutos

Cada clip llega por el chat, se guarda en `sources_raw/tmb/` y se anota aquí:
qué muestra, calidad y en qué bloque del guion encaja.

| # | Archivo | Dur. | Formato | Audio | Contenido | Encaja en | Notas |
|---|---|---|---|---|---|---|---|
| 01 | `tmb01_collado_refugio_dron.mp4` | 11.5 s | 1280×720 30 fps, horizontal | no | Dron sobre un collado alto con un pequeño refugio de techo metálico, muchos senderistas descansando; el sendero baja al valle con picos nevados al fondo. Plano único, movimiento suave. | **Special** ("Crossing high mountain passes"); recurso para What is / Journey | Collado sin identificar (¿Col du Bonhomme? ¿Col de la Seigne?): confirmar para el mapa. 720p: bien para 16:9, justo para 9:16. |
| 02 | `tmb02_montblanc_cresta_timelapse.mp4` | 7.6 s | 1920×1080 25 fps, horizontal | no | Timelapse del macizo del Mont Blanc nevado detrás de una cresta verde, nubes moviéndose a la derecha. Plano fijo. | **Hook** (gran angular del macizo); también recurso para What is / Closing | Llegó con marca de agua de clideo.com (abajo dcha.): quitada con zoom ×1.25 + reencuadre (recorte 1536×864 desde x132 y74 → 1920×1080). El archivo tal cual llegó se guarda como `..._ORIGINAL_clideo.mp4`. Si existe la descarga original de Artlist sin pasar por Clideo, mejor usar esa (sin zoom, más nitidez). Para 9:16 se queda justo de resolución. |
| 03 | `tmb03_pareja_senderistas.mp4` | 22.3 s | 1920×1080 25 fps, horizontal | no | Pareja mayor (60+) caminando con bastones, sonriendo, travelling lateral; pared de roca y alerces otoñales detrás. | **A day** (caminando), **Special** (gente disfrutando), **Orbis idea** ("Walking.") | **Es Eslovenia**, no el TMB: usar solo como plano genérico de personas. Perfil de edad ideal para el público. Marca clideo quitada (encuadre x40 y74). |
| 04 | `tmb04_vaca_pradera.mp4` | 9.2 s | 1920×1080 25 fps, horizontal | no | Vaca Abondance tumbada en pradera alpina con flores, bosque de abetos detrás. | **Special** ("alpine meadow" / cultura alpina); respiro entre bloques | Abondance = raza típica de Saboya y Aosta: muy TMB. Marca clideo quitada (x160 y74; fuera la otra vaca cortada abajo a la derecha). |
| ~~05~~ | `_descartados/tmb05_tienda_saco.mp4` | 19.6 s | 1920×1080 23.98 fps, horizontal | sí | Interior de tienda glamping: mochila de trekking grande sobre la cama, farol, alguien se la carga y sale. Primeros planos, sin caras. | **A day** ("a new stage ahead"), solo los primeros ~5 s | **Choca con el mensaje** (hoteles + mochila pequeña + equipaje trasladado): evitar la tienda y la mochila grande en pantalla. Mejor sustituir por habitación de hotel. Marca clideo quitada (centrado). |
| ~~06~~ | `_descartados/tmb06_picnic.mp4` | 12.9 s | 1920×1080 25 fps, horizontal | no | Tres personas jóvenes (~30) comiendo en mesa de picnic en un glamping; tiendas campana a los lados, helechos arborescentes y palmeras detrás. | **A day** ("lunch stop") como mucho, y recortado | **Encaja poco**: vegetación no alpina, camping (el mensaje es de hoteles) y público más joven que el vuestro. Mejor sustituir por comida en la terraza de un refugio o un restaurante de pueblo alpino. Marca clideo quitada (x0 y74). |
| ~~07~~ | `_descartados/tmb07_mochilero_puente.mp4` | 10.1 s | 1920×1080 25 fps, horizontal | no | Mochilero de espaldas cruzando un puente colgante metálico hacia un valle con picos nevados; más senderistas al fondo. | **Special** / **A day** ("a new stage ahead"), recurso de sendero | **Es Nueva Zelanda** (Hooker Valley Track, Mount Cook): el puente y la vegetación de matorral son reconocibles. El TMB tiene su propio puente colgante (Passerelle de Bionnassay, en la variante): si hay metraje de ese, mejor. Marca clideo quitada (centrado). |
| 08 | `tmb08_salon_rustico.mp4` | 1.0 s | 1280×720, horizontal | no | Salón rústico de piedra y madera con maletas junto a la entrada. | **Orbis service** (alojamiento, equipaje) | Muy corto: en el montaje va a cámara lenta ×0.36 con interpolación. Sin marca de agua. |
| 09 | `tmb09_habitacion_piedra.mp4` | 1.7 s | 1280×720, horizontal | no | Habitación de hotel con pared de piedra, ventana verde y lámparas encendidas. | **A day** (por la mañana), **Orbis service** | Cámara lenta ×0.55 con interpolación. |
| 10 | `tmb10_habitacion_buhardilla.mp4` | 1.63 s | 1280×720, horizontal | no | Habitación abuhardillada de madera. | **Orbis service** | Cámara lenta ×0.5. |
| 11 | `tmb11_techo_vigas.mp4` | 2.03 s | 1280×720, horizontal | no | Detalle de techo con vigas de madera. | **Orbis service** (apertura del bloque) | Cámara lenta ×0.65. |
| 12 | `tmb12_pasos_bosque_pinos.mp4` | 7.8 s | 1920×1080 25 fps, horizontal | no | Cámara baja siguiendo los pies de un senderista por un sendero de raíces y roca en bosque de pinos/alerces; al final se abre al valle. | **A day** (caminando), **Special** | Encaja muy bien (bosque alpino). Marca clideo quitada (x192 y74). |

**Descartados** (en `sources_raw/tmb/_descartados/`): 05 tienda glamping, 06 picnic con vegetación tropical y 07 puente de Nueva Zelanda. No pueden pasar por el TMB y chocan con el mensaje (hoteles, mochila pequeña).

## Primer corte (16:9, sin locución)

`edit/edl.json` → `python3 edit/build_edit.py bg | overlay [ini fin] | compose <salida>` → `output/tmb_primer_corte_16x9.mp4` (72 s, música provisional). Mapa animado en `edit/overlay_template.html` con los datos de `map/map_data.json`.

## Cobertura del guion

| Bloque | Necesita | Tenemos |
|---|---|---|
| Hook | macizo en gran angular, glaciares, senderistas en el paisaje | **02 (macizo timelapse)** |
| What is TMB | mapa animado + paisajes variados | **mapa animado hecho** (sobre el dron del macizo), 01 |
| The Journey | Les Houches, Les Contamines, Les Chapieux, Courmayeur, Val Ferret, La Fouly, Champex, Trient, Chamonix | — |
| Special | glaciar, pradera, **collado**, pueblo, café de montaña, botas, gente mirando el paisaje | **01 (collado)**, **04 (pradera/vaca)**, 03 (gente) |
| A day | hotel por la mañana, desayuno, mochila, salida, sendero, parada de comida, llegada | 09 (habitación), **12 (pasos en el sendero)**, 03 (caminando) |
| No rush | Courmayeur, terraza/café, teleférico, Chamonix | — |
| Orbis service | hotel, recepción, habitación, desayuno, maleta etiquetada, maleta a la furgoneta, mapas, equipo Orbis, salida con mochila | 08, 10, 11 (interiores rústicos). Falta desayuno, maletas/furgoneta, mapas |
| Orbis idea | maleta entrando en la furgoneta → mismos viajeros se ponen la mochila y echan a andar → gran angular | 03 ("Walking.") |
| Closing | hora dorada, dos senderistas de espaldas, macizo al fondo | — |

## Audio

| Tipo | Archivo | Estado |
|---|---|---|
| Locución | — | pendiente |
| Música | `sources_audio/background_music.mp3` | provisional (la del reel) |
| Sonido ambiente (hook) | — | los brutos recibidos no traen audio |
