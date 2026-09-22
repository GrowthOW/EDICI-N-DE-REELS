import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
with open(os.path.join(HERE, "segments.json")) as f:
    CFG = json.load(f)

TRANS = CFG["trans"]
FPS = CFG["fps"]
W, H = CFG["canvas"]["w"], CFG["canvas"]["h"]
SEGMENTS = CFG["segments"]
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "background.mp4")

inputs, filters, labels = [], [], []
durations = [s["src_end"] - s["src_start"] for s in SEGMENTS]

# One input per segment: sharing a single decoded input across out-of-order
# trims makes the filter graph buffer frames until it stalls.
for i, seg in enumerate(SEGMENTS):
    dur = durations[i]
    inputs += ["-ss", f"{seg['src_start']}", "-t", f"{dur}", "-i", os.path.join(REPO, seg["src"])]
    x0, x1 = seg["crop_x0"], seg["crop_x1"]
    crop_x = f"{x0}" if x0 == x1 else f"{x0}+({x1}-{x0})*(t/{dur:.4f})"
    filters.append(
        f"[{i}:v]fps={FPS},setpts=PTS-STARTPTS,scale=-2:{H},"
        f"crop={W}:{H}:'{crop_x}':0,setsar=1,format=yuv420p,"
        f"eq=contrast=1.08:brightness=-0.02:saturation=0.92,hue=h=-2[v{i}]"
    )
    labels.append(f"v{i}")

running_total = durations[0]
prev = labels[0]
for i in range(1, len(SEGMENTS)):
    offset = running_total - TRANS
    out = f"vx{i}"
    filters.append(f"[{prev}][{labels[i]}]xfade=transition=fade:duration={TRANS}:offset={offset:.4f}[{out}]")
    running_total += durations[i] - TRANS
    prev = out

total_duration = running_total

tl = []
n = len(SEGMENTS)
mount_start = 0.0
for i in range(n):
    full_start = mount_start if i == 0 else mount_start + TRANS
    trans_in = 0 if i == 0 else TRANS
    trans_out = 0 if i == n - 1 else TRANS
    full_end = full_start + durations[i] - trans_in - trans_out
    mount_end = full_end if i == n - 1 else full_end + TRANS
    tl.append({
        "key": SEGMENTS[i]["key"],
        "mountStart": round(mount_start, 4),
        "fullStart": round(full_start, 4),
        "fullEnd": round(full_end, 4),
        "mountEnd": round(mount_end, 4),
    })
    mount_start = full_end

with open(os.path.join(HERE, "timeline.json"), "w") as f:
    json.dump({"trans": TRANS, "total_duration": round(total_duration, 4), "timeline": tl}, f, indent=2)
print(json.dumps(tl, indent=2))

cmd = ["ffmpeg", "-y", "-v", "error", "-stats", *inputs,
       "-filter_complex", ";".join(filters), "-map", f"[{prev}]", "-an",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium",
       OUT]
subprocess.run(cmd, check=True)
print("DONE background", total_duration)
