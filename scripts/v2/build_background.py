import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "segments.json")) as f:
    CFG = json.load(f)

TRANS = CFG["trans"]
W, H = CFG["canvas"]["w"], CFG["canvas"]["h"]
SEGMENTS = CFG["segments"]
SRC = sys.argv[1] if len(sys.argv) > 1 else "/root/.claude/uploads/e0fd080d-e535-5b69-93b5-485d4695a69d/d9a094cc-Disen_o_sin_ti_tulo_1_1.mp4"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "background.mp4")

filters = []
v_labels = []
a_labels = []
timeline = []  # will hold mountStart/fullStart/fullEnd/mountEnd per segment, in FINAL composited time

durations = [s["src_end"] - s["src_start"] for s in SEGMENTS]

for i, seg in enumerate(SEGMENTS):
    S, E = seg["src_start"], seg["src_end"]
    dur = E - S
    x0, x1 = seg["crop_x0"], seg["crop_x1"]
    if x0 == x1:
        crop_x_expr = f"{x0}"
    else:
        crop_x_expr = f"{x0}+({x1}-{x0})*(t/{dur:.4f})"
    vf = (
        f"[0:v]trim=start={S}:end={E},setpts=PTS-STARTPTS,"
        f"scale=-2:{H},"
        f"crop={W}:{H}:'{crop_x_expr}':0,"
        f"eq=contrast=1.08:brightness=-0.02:saturation=0.92,"
        f"hue=h=-2[v{i}]"
    )
    af = f"[0:a]atrim=start={S}:end={E},asetpts=PTS-STARTPTS[a{i}]"
    filters.append(vf)
    filters.append(af)
    v_labels.append(f"v{i}")
    a_labels.append(f"a{i}")

# xfade / acrossfade chain
n = len(SEGMENTS)
running_total = durations[0]
prev_v, prev_a = v_labels[0], a_labels[0]
for i in range(1, n):
    offset = running_total - TRANS
    out_v = f"vx{i}"
    out_a = f"ax{i}"
    filters.append(
        f"[{prev_v}][{v_labels[i]}]xfade=transition=fade:duration={TRANS}:offset={offset:.4f}[{out_v}]"
    )
    filters.append(f"[{prev_a}][{a_labels[i]}]acrossfade=d={TRANS}[{out_a}]")
    running_total = running_total + durations[i] - TRANS
    prev_v, prev_a = out_v, out_a

total_duration = running_total

filter_complex = ";\n".join(filters)

cmd = [
    "ffmpeg", "-y", "-i", SRC,
    "-filter_complex", filter_complex,
    "-map", f"[{prev_v}]", "-map", f"[{prev_a}]",
    "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
    "-crf", "16", "-preset", "slow",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    OUT,
]

print("TOTAL_DURATION", total_duration)

# also compute and dump the text-overlay timeline (mountStart/fullStart/fullEnd/mountEnd per segment)
tl = []
mount_start = 0.0
for i in range(n):
    full_start = mount_start if i == 0 else mount_start + TRANS
    dur = durations[i]
    trans_in = 0 if i == 0 else TRANS
    trans_out = 0 if i == n - 1 else TRANS
    hold = dur - trans_in - trans_out
    full_end = full_start + hold
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
    json.dump({"trans": TRANS, "total_duration": total_duration, "timeline": tl}, f, indent=2)

print(json.dumps(tl, indent=2))
print(" ".join(f"'{c}'" if " " in c else c for c in cmd))
subprocess.run(cmd, check=True)
print("DONE background.mp4")
