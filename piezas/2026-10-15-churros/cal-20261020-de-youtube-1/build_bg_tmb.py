# Fondo 9:16 a 25 fps con clips reales del TMB (sources_raw): cortes secos con empuje lento.
# Variante de piezas/2026-10-14/build_bg.py con rutas relativas a sources_raw/.
# Uso: python3 build_bg_tmb.py <shots.json> <salida.mp4> [congelado_final_s]
import json, subprocess, sys
R = '/home/user/EDICI-N-DE-REELS/sources_raw/'
FPS, W, H = 25, 1080, 1920
SHOTS = json.load(open(sys.argv[1])); out = sys.argv[2]
extra = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
inputs, f, labels = [], [], []
for i, (src, ss, d, cx, z, sp) in enumerate(SHOTS):
    inputs += ['-ss', str(ss), '-t', str(d * sp + 0.3), '-i', R + src]
    n = round(d * FPS)
    hold = f',tpad=stop_mode=clone:stop_duration={extra}' if (extra and i == len(SHOTS) - 1) else ''
    nz = n + (round(extra * FPS) if hold else 0)
    f.append(
      f"[{i}:v]setpts=PTS/{sp},fps={FPS},scale=-2:{H}:flags=lanczos,crop={W}:{H}:'min(max(0,iw*{cx}-{W}/2),iw-{W})':0,setsar=1,"
      f"tpad=stop_mode=clone:stop_duration=1{hold},"
      f"zoompan=z='1+({z}-1)*min(on,{n})/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
      f"trim=end_frame={nz},setpts=PTS-STARTPTS,unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.06,format=yuv420p[v{i}]")
    labels.append(f'[v{i}]')
f.append(''.join(labels) + f'concat=n={len(SHOTS)}:v=1:a=0[v]')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-stats', *inputs, '-filter_complex', ';'.join(f),
                '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-r', str(FPS), out], check=True)
