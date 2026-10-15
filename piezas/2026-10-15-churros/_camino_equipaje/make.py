# Camino / traslado de equipaje («churros», 15 oct 2026): fondos base compartidos + textos por idioma.
# Uso:
#   python3 make.py bg <base/base_x.json> <base/bg_x.mp4>   fondo 9:16, cortes secos y empuje lento
#   python3 make.py piece <id>                               pieza en ../<id>/ (beats.json + piece.json)
# piece.json: {"bg": "base/bg_a.mp4", "name": "archivo", "versions": ["tiktok", "reel"],
#              "endcard": "../../../scripts/piezas/endcard_9x16.png" (relativo a esta carpeta), "music_ss": 0, "cover_t": 1.0}
# base_x.json: [[archivo, inicio, duración_salida, centro_del_recorte, zoom_final, velocidad], ...]
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
R = os.path.join(REPO, 'sources_raw', 'camino_drive')
MUSIC = os.path.join(REPO, 'sources_audio', 'background_music.mp3')
RENDER = os.path.join(REPO, 'scripts', 'piezas', 'render.js')
FPS, W, H = 25, 1080, 1920
END_IN, END_D = 19.6, 2.8          # cierre: entra en 19,6 s, total 22,4 s
Q = ['-hide_banner', '-v', 'error', '-nostats']


def run(cmd):
    print('>', ' '.join(os.path.basename(c) if os.sep in c else c for c in cmd[:3]), cmd[-1], flush=True)
    subprocess.run(cmd, check=True)


def build_bg(shots_file, out):
    shots = json.load(open(shots_file))
    inputs, f, labels = [], [], []
    for i, (src, ss, d, cx, z, sp) in enumerate(shots):
        inputs += ['-ss', str(ss), '-t', str(d * sp + 0.3), '-i', os.path.join(R, src)]
        n = round(d * FPS)
        f.append(
            f"[{i}:v]setpts=PTS/{sp},fps={FPS},scale=-2:{H}:flags=lanczos,crop={W}:{H}:'min(max(0,iw*{cx}-{W}/2),iw-{W})':0,setsar=1,"
            f"tpad=stop_mode=clone:stop_duration=1,"
            f"zoompan=z='1+({z}-1)*min(on,{n})/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
            f"trim=end_frame={n},setpts=PTS-STARTPTS,unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.06,format=yuv420p[v{i}]")
        labels.append(f'[v{i}]')
    f.append(''.join(labels) + f'concat=n={len(shots)}:v=1:a=0[v]')
    run(['ffmpeg', '-y', *Q, *inputs, '-filter_complex', ';'.join(f),
         '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-r', str(FPS), out])


def piece(pid):
    d = os.path.abspath(os.path.join(HERE, '..', pid))
    cfg = json.load(open(os.path.join(d, 'piece.json')))
    bj = json.load(open(os.path.join(d, 'beats.json')))
    total, beats = bj['total'], bj['beats']
    bg = os.path.join(HERE, cfg['bg'])
    ov = os.path.join(d, 'ov')
    if not os.path.exists(os.path.join(ov, f'f_{round(total * FPS) - 1:05d}.png')):
        run(['node', RENDER, 'frames', os.path.join(HERE, 'native_overlay.html') + '?p=../' + pid,
             str(W), str(H), ov, str(FPS)])
    seq = ['-framerate', str(FPS), '-i', os.path.join(ov, 'f_%05d.png')]
    name = cfg['name']
    out = {}
    if 'tiktok' in cfg['versions']:      # sin logo, sin cierre, sin música
        out['tiktok'] = os.path.join(d, name + '_tiktok.mp4')
        run(['ffmpeg', '-y', *Q, '-i', bg, *seq, '-filter_complex',
             f'[0:v][1:v]overlay=0:0:format=auto,trim=duration={total},format=yuv420p[v]', '-map', '[v]', '-an',
             '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-r', str(FPS), '-movflags', '+faststart', out['tiktok']])
    if 'reel' in cfg['versions']:        # con cierre y música a −14 LUFS
        end = os.path.join(HERE, cfg['endcard'])
        out['reel'] = os.path.join(d, name + '_reel.mp4')
        tot = END_IN + END_D
        fc = (f"[0:v]tpad=stop_mode=clone:stop_duration={tot - total + 0.2}[b];"
              f"[b][1:v]overlay=0:0:format=auto:eof_action=pass[t];"
              f"[2:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS+{END_IN}/TB[e];"
              f"[t][e]overlay=0:0:format=auto:eof_action=pass,trim=duration={tot},format=yuv420p[v];"
              f"[3:a]atrim=0:{tot},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.5,afade=t=out:st={tot - 1.6}:d=1.6,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
        run(['ffmpeg', '-y', *Q, '-i', bg, *seq,
             '-loop', '1', '-framerate', str(FPS), '-t', str(END_D), '-i', end,
             '-ss', str(cfg.get('music_ss', 0)), '-i', MUSIC, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
             '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-r', str(FPS),
             '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out['reel']])
        r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', out['reel'], '-af', 'ebur128=peak=true',
                            '-f', 'null', '-'], capture_output=True, text=True).stderr
        print('LUFS', [l.strip() for l in r.splitlines()[-12:] if 'I:' in l or 'Peak:' in l])
    # portada: fotograma real del vídeo con el gancho
    run(['ffmpeg', '-y', *Q, '-ss', str(cfg.get('cover_t', 1.0)), '-i', bg, '-i', os.path.join(ov, 'f_00000.png'),
         '-filter_complex', '[0:v][1:v]overlay=0:0', '-frames:v', '1', '-q:v', '2', os.path.join(d, 'portada.jpg')])
    # hoja de fotogramas: uno por plano + cierre
    src = out.get('reel') or out['tiktok']
    ts = [b['t'] + 1.0 for b in beats] + ([END_IN + 1.6] if 'reel' in out else [])
    sel = '+'.join(f"eq(n\\,{round(t * FPS)})" for t in ts)
    run(['ffmpeg', '-y', *Q, '-i', src, '-vf', f"select='{sel}',scale=360:-1,tile={len(ts)}x1",
         '-frames:v', '1', '-fps_mode', 'passthrough', os.path.join(d, 'sheet.jpg')])


if __name__ == '__main__':
    if sys.argv[1] == 'bg':
        build_bg(sys.argv[2], sys.argv[3])
    else:
        piece(sys.argv[2])
