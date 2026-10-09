# Fondo del TikTok del TMB: cortes secos con empuje lento, 9:16 a 25 fps.
import subprocess, sys
R = '/home/user/EDICI-N-DE-REELS/sources_raw/'
FPS, W, H = 25, 1080, 1920
# (archivo, inicio, duración, centro del recorte en fracción del ancho, zoom final)
SHOTS = [
  ('montblanc_massif_drone.mp4', 0.4, 2.8, 0.55, 1.07),
  ('tmb/tmb02_montblanc_cresta_timelapse.mp4', 0.5, 2.8, 0.52, 1.06),
  ('tmb/tmb03_pareja_senderistas.mp4', 14.0, 2.8, 0.62, 1.05),
  ('tmb/tmb04_vaca_pradera.mp4', 1.5, 2.8, 0.42, 1.06),
  ('tmb/tmb03_pareja_senderistas.mp4', 2.0, 2.8, 0.36, 1.05),
  ('montblanc_massif_drone.mp4', 4.6, 2.8, 0.66, 1.07),
]
extra = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0   # congelado final (cierre de Reel/Short)
out = sys.argv[1]
inputs, f, labels = [], [], []
for i, (src, ss, d, cx, z) in enumerate(SHOTS):
    inputs += ['-ss', str(ss), '-t', str(d + 0.2), '-i', R + src]
    n = round(d * FPS)
    hold = f',tpad=stop_mode=clone:stop_duration={extra}' if (extra and i == len(SHOTS) - 1) else ''
    nz = n + (round(extra * FPS) if hold else 0)
    f.append(
      f"[{i}:v]fps={FPS},scale=-2:{H},crop={W}:{H}:'min(max(0,iw*{cx}-{W}/2),iw-{W})':0,setsar=1{hold},"
      f"zoompan=z='1+({z}-1)*min(on,{n})/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
      f"trim=end_frame={nz},setpts=PTS-STARTPTS,eq=contrast=1.06:saturation=1.08,format=yuv420p[v{i}]")
    labels.append(f'[v{i}]')
f.append(''.join(labels) + f'concat=n={len(SHOTS)}:v=1:a=0[v]')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-stats', *inputs, '-filter_complex', ';'.join(f),
                '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-r', str(FPS), out], check=True)
