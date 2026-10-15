# Monta una pieza 9:16 con look nativo (fábrica «churros», 15 oct 2026).
# Uso: python3 make.py <carpeta_pieza> [pasos]   pasos: bg,ov,clean,reel,cover,sheet (por defecto todos)
# La carpeta lleva piece.json:
#   {"name": "base_del_archivo", "shots": [[archivo, inicio, duración_salida, centro_x, zoom_final, velocidad], ...],
#    "endcard": null | "es" | "en", "music_ss": 0, "cover": {"t": 1.2, "text": "...", "top": 600}}
# y beats.json (textos, ver native_overlay.html). Duración del fondo = suma de los planos = beats.total.
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
d = os.path.abspath(sys.argv[1]); p = os.path.basename(d)
steps = sys.argv[2].split(',') if len(sys.argv) > 2 else ['bg', 'ov', 'clean', 'reel', 'cover', 'sheet']
cfg = json.load(open(os.path.join(d, 'piece.json')))
beats = json.load(open(os.path.join(d, 'beats.json')))
T = beats['total']; name = cfg['name']
assert abs(sum(s[2] for s in cfg['shots']) - T) < 0.02, 'los planos no suman beats.total'
run = lambda *a: subprocess.run(list(a), check=True)
clean = os.path.join(d, name + ('_tiktok.mp4' if not cfg.get('endcard') else '_sin_cierre.mp4'))
reel = os.path.join(d, name + '_con_cierre.mp4')

if 'bg' in steps:
    json.dump(cfg['shots'], open(os.path.join(d, 'shots.json'), 'w'))
    run('python3', os.path.join(HERE, 'build_bg.py'), os.path.join(d, 'shots.json'), os.path.join(d, 'bg.mp4'))
if 'ov' in steps:
    run('rm', '-rf', os.path.join(d, 'ov'))
    run('node', os.path.join(REPO, 'scripts/piezas/render.js'), 'frames', os.path.join(HERE, 'native_overlay.html') + '?p=' + p,
        '1080', '1920', os.path.join(d, 'ov'), '25')
if 'clean' in steps:
    # TikTok / versión sin cierre: sin logo, sin cierre y sin música (como las piezas del 14 y 15 oct)
    run('ffmpeg', '-y', '-v', 'error', '-i', os.path.join(d, 'bg.mp4'), '-framerate', '25', '-i', os.path.join(d, 'ov', 'f_%05d.png'),
        '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]', '-map', '[v]', '-an',
        '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-r', '25', '-movflags', '+faststart', '-t', str(T), clean)
if 'reel' in steps and cfg.get('endcard'):
    ec = os.path.join(REPO, 'scripts/piezas', 'endcard_9x16_es.png' if cfg['endcard'] == 'es' else 'endcard_9x16.png')
    ED, XF = 2.8, 0.4; TT = T + ED - XF
    music = os.path.join(REPO, 'sources_audio/background_music.mp3')
    run('ffmpeg', '-y', '-v', 'error', '-i', clean, '-loop', '1', '-framerate', '25', '-t', str(ED), '-i', ec,
        '-ss', str(cfg.get('music_ss', 0)), '-t', str(TT), '-i', music,
        '-filter_complex',
        f'[1:v]scale=1080:1920,setsar=1,format=yuv420p,fps=25,settb=1/25[e];[0:v]setsar=1,format=yuv420p,fps=25,settb=1/25[c];'
        f'[c][e]xfade=transition=fade:duration={XF}:offset={T - XF:.2f}[v];'
        f'[2:a]afade=t=in:d=0.3,afade=t=out:st={TT - 1.4:.2f}:d=1.4,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]',
        '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-r', '25',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', f'{TT:.2f}', reel)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', reel, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    print('LUFS:', [l.strip() for l in r.splitlines() if l.strip().startswith(('I:', 'Peak:'))][-2:])
if 'cover' in steps:
    c = cfg['cover']
    json.dump({'total': 0.04, 'beats': [{'t': 0, 'text': c['text'], 'top': c.get('top', 560), 'size': 'cover',
                                          **({'sticker': c['sticker']} if c.get('sticker') else {})}]},
              open(os.path.join(d, 'cover.json'), 'w'), ensure_ascii=False)
    run('rm', '-rf', os.path.join(d, 'cov'))
    run('node', os.path.join(REPO, 'scripts/piezas/render.js'), 'frames',
        os.path.join(HERE, 'native_overlay.html') + '?p=' + p + '&f=cover.json', '1080', '1920', os.path.join(d, 'cov'), '25')
    run('ffmpeg', '-y', '-v', 'error', '-ss', str(c['t']), '-i', os.path.join(d, 'bg.mp4'), '-i', os.path.join(d, 'cov', 'f_00000.png'),
        '-filter_complex', '[0:v][1:v]overlay=0:0', '-frames:v', '1', '-q:v', '2', os.path.join(d, 'portada.jpg'))
if 'sheet' in steps:
    src = reel if cfg.get('endcard') else clean
    run('ffmpeg', '-y', '-v', 'error', '-i', src, '-vf', 'fps=1,scale=270:480,tile=8x3', '-frames:v', '1', '-q:v', '3',
        os.path.join(d, 'sheet.jpg'))
print('ok', p)
