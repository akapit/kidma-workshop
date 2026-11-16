#!/usr/bin/env python3
"""Burn house-style captions into a video and write a matching .srt.

House look: white Assistant 800, black
3px stroke, soft drop shadow, NO background box, 75px on a 1080x1920 frame, top edge at
1358px. Scales with the frame. Each cue is rendered as a transparent PNG by headless
Chrome (real browser text shaping = correct Hebrew/RTL), then composited with ffmpeg
overlay + enable=between(t,...). Audio is copied untouched.

Usage:
  burn_captions.py VIDEO CUES.json [--out OUT.mp4] [--srt OUT.srt] [--work DIR]
                   [--size PX] [--top PX] [--bottom PX] [--color #fff]
"""
import argparse, html, json, os, pathlib, shutil, subprocess, sys, tempfile

# Google Chrome: set CHROME_PATH to override; otherwise the usual Mac, Windows and Linux spots.
_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    shutil.which("google-chrome") or "", shutil.which("chromium") or "",
]
CHROME = next((c for c in _CANDIDATES if c and pathlib.Path(c).exists()), _CANDIDATES[1])


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", video],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    return int(s["width"]), int(s["height"]), float(d["format"]["duration"])


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("cues")
    ap.add_argument("--out"); ap.add_argument("--srt"); ap.add_argument("--work")
    ap.add_argument("--size", type=float, help="font px (default 75 per 1080px of the short side)")
    ap.add_argument("--top", type=float, help="caption top edge px (portrait default 0.7073*H)")
    ap.add_argument("--bottom", type=float, help="caption bottom offset px (landscape default 110*H/1080)")
    ap.add_argument("--color", default="#fff")
    a = ap.parse_args()

    video = pathlib.Path(a.video).resolve()
    cues = json.load(open(a.cues, encoding="utf-8"))
    out = pathlib.Path(a.out) if a.out else video.with_name(video.stem + "_subtitled.mp4")
    srt = pathlib.Path(a.srt) if a.srt else video.with_suffix(".srt")
    work = pathlib.Path(a.work or tempfile.mkdtemp(prefix="caps-")); png = work / "png"; png.mkdir(parents=True, exist_ok=True)
    if not pathlib.Path(CHROME).exists():
        sys.exit("Google Chrome not found at " + CHROME)

    W, H, dur = probe(str(video))
    k = min(W, H) / 1080
    size = a.size or 75 * k
    stroke, blur, dy, side = 3 * k, 15 * k, 4 * k, 60 * k
    if H >= W:  # portrait / square: house position
        pos = f"top:{a.top if a.top is not None else round(0.7073 * H)}px"
    else:       # landscape: low third
        pos = f"bottom:{a.bottom if a.bottom is not None else round(110 * k)}px"
    head = f"""<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@800&display=block" rel="stylesheet">
<style>html,body{{margin:0;width:{W}px;height:{H}px;background:transparent;overflow:hidden;font-family:'Assistant','Rubik',sans-serif}}
.cap{{position:absolute;left:{side}px;right:{side}px;{pos};text-align:center;color:{a.color};font-weight:800;font-size:{size}px;line-height:1.18;
-webkit-text-stroke:{stroke}px #000;paint-order:stroke fill;text-shadow:0 {dy}px {blur}px rgba(0,0,0,.75)}}</style></head><body>"""

    inputs, chain, prev = [], [], "0:v"
    for i, c in enumerate(cues):
        h = work / f"cap-{i}.html"
        h.write_text(head + f'<div class="cap">{html.escape(c["text"])}</div></body></html>', encoding="utf-8")
        p = png / f"cap-{i}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--default-background-color=00000000", f"--window-size={W},{H}", "--virtual-time-budget=5000",
                        f"--screenshot={p}", h.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        inputs += ["-i", str(p)]
        lbl = f"v{i}"
        chain.append(f"[{prev}][{i + 1}:v]overlay=0:0:enable='between(t,{c['start']},{c['end']})'[{lbl}]")
        prev = lbl
    (work / "filter.txt").write_text(";".join(chain), encoding="utf-8")

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(video), *inputs, "-filter_complex_script", str(work / "filter.txt"),
           "-map", f"[{prev}]", "-map", "0:a?", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)

    srt.write_text("".join(f"{i + 1}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n\n"
                           for i, c in enumerate(cues)), encoding="utf-8")

    # contact strip: one frame from the middle of each cue, for visual QA
    frames = work / "frames"; frames.mkdir(exist_ok=True)
    for f in frames.glob("*.png"):
        f.unlink()
    for i, c in enumerate(cues):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{(c['start'] + c['end']) / 2:.2f}", "-i", str(out),
                        "-frames:v", "1", "-vf", "scale=300:-1", str(frames / f"f{i:03}.png")])
    cols = min(len(cues), 6); rows = -(-len(cues) // cols)
    strip = work / "check.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(frames / "f%03d.png"), "-vf", f"tile={cols}x{rows}",
                    "-frames:v", "1", str(strip)])
    print(f"video: {out}\nsrt:   {srt}\ncheck: {strip}\ncues:  {len(cues)}  ({W}x{H}, {dur:.2f}s, font {size:.0f}px)")


if __name__ == "__main__":
    main()
