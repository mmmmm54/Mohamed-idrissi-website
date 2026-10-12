"""
Encode Mohamed's videos for the web. Run from the project root:
    python scripts/encode-motion.py
For each entry in src/data/motion.json it reads the original file named in the
"source" field (from the Downloads folders, never committed) and writes into
public/motion/<id>/:
    full.mp4     H.264 720p, AAC, faststart: plays in every browser, loaded on click
    preview.mp4  6 seconds, silent, 360p: the looping card preview
    poster.webp  one frame, 540px wide: shown before anything plays
Existing outputs are skipped, so re-running only encodes new videos.
Then it records duration and sizes back into motion.json.
"""
import json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'src', 'data', 'motion.json')
OUT = os.path.join(ROOT, 'public', 'motion')

def tool(name):
    found = shutil.which(name)
    if found:
        return found
    winget = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages')
    for base, _, files in os.walk(winget):
        if f'{name}.exe' in files:
            return os.path.join(base, f'{name}.exe')
    sys.exit(f'{name} not found')

FFMPEG, FFPROBE = tool('ffmpeg'), tool('ffprobe')

def probe(path):
    out = subprocess.run([FFPROBE, '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height',
                          '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    return float(info['format']['duration']), video

def run(args):
    subprocess.run([FFMPEG, '-v', 'error', '-y', *args], check=True)

items = json.load(open(DATA, encoding='utf-8'))
for item in items:
    src = os.path.expandvars(item['source'])
    folder = os.path.join(OUT, item['id'])
    os.makedirs(folder, exist_ok=True)
    full, preview, poster = (os.path.join(folder, n) for n in ('full.mp4', 'preview.mp4', 'poster.webp'))
    duration, _ = probe(src)
    at = round(duration * item.get('posterAt', 0.15), 2)
    if not os.path.exists(full):
        run(['-i', src, '-vf', 'scale=720:-2:flags=lanczos,fps=30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '26',
             '-maxrate', '1600k', '-bufsize', '3200k', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
             '-c:a', 'aac', '-b:a', '96k', '-ac', '2', '-movflags', '+faststart', full])
    if not os.path.exists(preview):
        run(['-ss', str(at), '-t', '6', '-i', src, '-vf', 'scale=360:-2:flags=lanczos,fps=24', '-an', '-c:v', 'libx264',
             '-preset', 'medium', '-crf', '30', '-maxrate', '450k', '-bufsize', '900k', '-pix_fmt', 'yuv420p',
             '-movflags', '+faststart', preview])
    if not os.path.exists(poster):
        run(['-ss', str(at), '-i', src, '-frames:v', '1', '-vf', 'scale=540:-2:flags=lanczos', '-c:v', 'libwebp',
             '-quality', '78', poster])
    _, video = probe(full)
    item.update(duration=round(duration, 1), width=video['width'], height=video['height'],
                sizeKB={n: os.path.getsize(os.path.join(folder, n)) // 1024 for n in ('full.mp4', 'preview.mp4', 'poster.webp')})
    print(f"{item['id']:28} {item['duration']:6.1f}s  full {item['sizeKB']['full.mp4']:6} KB  preview {item['sizeKB']['preview.mp4']:4} KB", flush=True)

with open(DATA, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
    f.write('\n')
