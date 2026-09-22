import os, math, glob
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "overlay_frames")
os.makedirs(FRAMES, exist_ok=True)
for f in os.listdir(FRAMES):
    os.remove(os.path.join(FRAMES, f))

FPS = 30

def find_chromium():
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")
    matches = sorted(glob.glob(os.path.join(base, "chromium-*", "chrome-linux", "chrome")))
    return matches[-1] if matches else None

with sync_playwright() as p:
    launch_kwargs = {"args": ["--force-color-profile=srgb", "--disable-lcd-text"]}
    chromium_path = find_chromium()
    if chromium_path:
        launch_kwargs["executable_path"] = chromium_path
    browser = p.chromium.launch(**launch_kwargs)
    page = browser.new_page(
        viewport={"width": 1080, "height": 1920},
        device_scale_factor=1,
    )
    page.goto("file://" + os.path.join(HERE, "overlay.html"))
    page.wait_for_function("window.__READY__ === true")
    total = page.evaluate("window.TOTAL_DURATION")
    print("TOTAL_DURATION", total)
    total_frames = int(math.ceil(total * FPS))
    print("total_frames", total_frames)
    stage = page.locator("#stage")
    for i in range(total_frames):
        t = i / FPS
        page.evaluate(f"window.renderAtTime({t})")
        stage.screenshot(path=os.path.join(FRAMES, f"ov_{i:05d}.png"), omit_background=True)
        if i % 30 == 0:
            print("frame", i, "/", total_frames)
    browser.close()

print("DONE", total_frames, "overlay frames")
