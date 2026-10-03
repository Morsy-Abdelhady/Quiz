#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build pipeline for the 60-second "خمن الفيلم" video.

  python3 build.py plan        -> SHOTLIST.md (per-clip plan + ready-to-paste generation prompts)
  python3 build.py assets      -> out/overlay.ass, out/music.wav, out/sfx.wav
  python3 build.py animatic    -> out/animatic.mp4 (timing preview built from refs/ photos)
  python3 build.py final       -> out/final.mp4 (from generated clips in clips/C01.mp4 … C12.mp4)

Only needs Python 3 (stdlib) and ffmpeg built with libass.
"""
import array
import json
import math
import os
import random
import subprocess
import sys
import wave

import timeline as T

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
REFS = os.path.join(HERE, "refs")
CLIPS_DIR = os.path.join(HERE, "clips")
VOICE_DIR = os.path.join(HERE, "voice")
FONTS = os.path.join(HERE, "fonts")
SR = 44100


def run(cmd):
    print("+", " ".join(cmd[:6]), "…" if len(cmd) > 6 else "")
    subprocess.run(cmd, check=True)


# ───────────────────────────── overlay (ASS) ─────────────────────────────

def ts(t):
    t = max(0.0, t)
    cs = int(round(t * 100))
    return "%d:%02d:%02d.%02d" % (cs // 360000, cs // 6000 % 60, cs // 100 % 60, cs % 100)


def rrect(w, h, r):
    """ASS vector path for a w×h rounded rectangle with its top-left at 0,0."""
    k = r * 0.45
    return (f"m {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} "
            f"b {w} {h - k} {w - k} {h} {w - r} {h} l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} "
            f"l 0 {r} b 0 {k} {k} 0 {r} 0")


def circle(r):
    k = r * 0.5523
    return (f"m 0 {-r} b {k} {-r} {r} {-k} {r} 0 b {r} {k} {k} {r} 0 {r} "
            f"b {-k} {r} {-r} {k} {-r} 0 b {-r} {-k} {-k} {-r} 0 {-r}")


def ass_overlay(draft=False):
    # Colours are &HAABBGGRR.
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {T.W}
PlayResY: {T.H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Me,Cairo,66,&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,0,0,1,5,3,2,90,90,330,-1
Style: AI,Cairo,66,&H00F5E65A,&H00FFFFFF,&H00261A08,&H96000000,-1,0,0,0,100,100,0,0,1,5,3,2,90,90,330,-1
Style: UI,Cairo,44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,-1
Style: Shape,Cairo,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,-1
Style: Title,Cairo,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,0,6,5,0,0,0,-1
Style: Reveal,Cairo,250,&H0046C8FF,&H00FFFFFF,&H00002850,&H78000000,-1,0,0,0,100,100,0,0,1,6,8,5,0,0,0,-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []

    def add(layer, a, b, style, text, name=""):
        ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},{name},0,0,0,,{text}")

    cx = T.W // 2

    # Subtitles (speaker-coloured, quick fade, never over the mouth: bottom safe area).
    for a, b, who, text in T.LINES:
        style = "AI" if who == T.AI else "Me"
        add(10, a, b + 0.08, style, r"{\fad(80,60)\blur0.6}" + text)

    # AI host: a glass panel with a breathing orb and a live waveform, only while the AI talks.
    pw, ph, py = 620, 150, 1290
    px = cx - pw // 2
    for a, b, who, _ in T.LINES:
        if who != T.AI:
            continue
        a0, b1 = a - 0.15, b + 0.15
        add(1, a0, b1, "Shape", r"{\pos(%d,%d)\1c&H1A1410&\1a&H38&\3c&HF5E65A&\bord3\shad0\fad(120,120)\p1}%s"
            % (px, py, rrect(pw, ph, 40)))
        # Orb glow + core, pulsing.
        ox, oy = px + 95, py + ph // 2
        pulses = "".join(r"\t(%d,%d,\fscx%d\fscy%d)" % (int(i * 260), int(i * 260 + 260), s, s)
                         for i, s in enumerate([118, 96] * int((b1 - a0) / 0.52 + 1)))
        add(2, a0, b1, "Shape", r"{\pos(%d,%d)\an7\1c&HF5E65A&\1a&H70&\bord0\blur14\fad(120,120)%s\p1}%s"
            % (ox, oy, pulses, circle(48)))
        add(3, a0, b1, "Shape", r"{\pos(%d,%d)\an7\1c&HFFF8D8&\bord0\blur2\fad(120,120)%s\p1}%s"
            % (ox, oy, pulses, circle(26)))
        add(4, a0, b1, "UI", r"{\pos(%d,%d)\fs30\1c&H261A08&\fad(120,120)}AI" % (ox, oy + 2))
        add(4, a0, b1, "UI", r"{\pos(%d,%d)\an4\fs34\1c&HF5E65A&\fad(120,120)}مساعد التحدي" % (px + 170, py + 44))
        # Waveform: 13 bars that jump to new heights every 90 ms.
        rnd = random.Random(int(a * 100))
        for i in range(13):
            bx = px + 190 + i * 30
            steps = "".join(r"\t(%d,%d,\fscy%d)" % (k * 90, k * 90 + 80, rnd.choice([25, 40, 60, 85, 100, 130]))
                            for k in range(int((b1 - a0) / 0.09)))
            add(4, a0, b1, "Shape", r"{\pos(%d,%d)\an5\1c&HF5E65A&\bord0\fscy30\fad(120,120)%s\p1}%s"
                % (bx, py + 104, steps, rrect(12, 56, 6)))

    # Question counter pill (top-left), slides in per question.
    for a, b, n in T.COUNTER:
        add(5, a, b, "Shape", r"{\move(-340,236,60,236,0,180)\1c&H101010&\1a&H30&\3c&HF5E65A&\bord2\p1}%s"
            % rrect(330, 84, 42))
        add(6, a, b, "UI", r"{\move(-175,278,225,278,0,180)\fs42}السؤال %d / 9" % n)

    # Countdown timer (top-right). Turns red under 15 s, pulses during the guess.
    t0, t1 = T.TIMER
    for s in range(int(t0), int(t1)):
        a, b = max(t0, s), min(t1, s + 1)
        left = int(round(T.DURATION - s))
        red = left <= 15
        col = r"\1c&H3C3CFF&" if red else r"\1c&HFFFFFF&"
        pop = r"\t(0,120,\fscx112\fscy112)\t(120,300,\fscx100\fscy100)" if red else ""
        add(5, a, b, "Shape", r"{\pos(%d,236)\1c&H101010&\1a&H30&\3c&H%s&\bord2\p1}%s"
            % (T.W - 60 - 230, "3C3CFF" if red else "FFFFFF", rrect(230, 84, 42)))
        add(6, a, b, "UI", r"{\pos(%d,278)%s%s\fs46}0:%02d" % (T.W - 60 - 115, col, pop, left))

    # Title card.
    a, b = T.TITLE_CARD
    add(7, a, b, "Shape", r"{\pos(0,0)\1c&H000000&\1a&H60&\fad(150,200)\p1}m 0 0 l %d 0 l %d %d l 0 %d" % (T.W, T.W, T.H, T.H))
    add(8, a, b, "Title", r"{\pos(%d,880)\fad(80,200)\fscx160\fscy160\t(0,220,\fscx100\fscy100)}خمن الفيلم" % cx)
    add(8, a + 0.25, b, "UI", r"{\pos(%d,1030)\fs64\1c&HF5E65A&\fad(150,200)}60 ثانية" % cx)
    add(8, a, b, "Shape", r"{\pos(%d,965)\an5\1c&HF5E65A&\fscx0\t(0,300,\fscx100)\fad(0,200)\p1}%s" % (cx, rrect(420, 6, 3)))

    # Guess: letterbox bars slide in, then out at the reveal.
    a, b = T.GUESS
    for y0, y1 in ((-170, 0), (T.H, T.H - 170)):
        add(7, a, b, "Shape", r"{\move(0,%d,0,%d,0,700)\1c&H000000&\p1}m 0 0 l %d 0 l %d 170 l 0 170" % (y0, y1, T.W, T.W))

    # Reveal: white flash, huge gold title with glow, then a badge to the end.
    r = T.REVEAL
    add(9, r, r + 0.35, "Shape", r"{\pos(0,0)\1c&HFFFFFF&\fad(0,300)\p1}m 0 0 l %d 0 l %d %d l 0 %d" % (T.W, T.W, T.H, T.H))
    add(8, r + 0.35, r + 3.2, "UI", r"{\pos(%d,700)\fs52\1c&HF5E65A&\fad(150,200)}الإجابة الصحيحة" % cx)
    add(8, r + 0.25, r + 3.2, "Reveal", r"{\pos(%d,880)\blur18\1a&H60&\3a&HFF&\fscx170\fscy170\t(0,260,\fscx100\fscy100)\fad(0,200)}الكيف" % cx)
    add(9, r + 0.25, r + 3.2, "Reveal", r"{\pos(%d,880)\fscx170\fscy170\t(0,260,\fscx100\fscy100)\fad(0,200)}الكيف" % cx)
    add(8, r + 3.2, T.DURATION, "Shape", r"{\pos(%d,236)\1c&H101010&\1a&H30&\3c&H46C8FF&\bord3\fad(200,0)\p1}%s" % (cx - 200, rrect(400, 96, 48)))
    add(9, r + 3.2, T.DURATION, "UI", r"{\pos(%d,284)\fs56\1c&H46C8FF&\fad(200,0)}الكيف" % cx)

    # Quick fade to black at the very end.
    add(20, T.DURATION - 0.3, T.DURATION, "Shape", r"{\pos(0,0)\1c&H000000&\fad(300,0)\p1}m 0 0 l %d 0 l %d %d l 0 %d" % (T.W, T.W, T.H, T.H))

    if draft:
        add(30, 0, T.DURATION, "UI", r"{\pos(%d,140)\fs30\1a&H50&}ANIMATIC — مسودة توقيت بدون صوت حوار" % cx)

    return head + "\n".join(ev) + "\n"


# ───────────────────────────── audio (stdlib synth) ─────────────────────────────

class Track:
    def __init__(self, seconds):
        self.buf = array.array("f", bytes(4 * int(seconds * SR)))

    def add(self, t0, samples, gain=1.0):
        i0 = int(t0 * SR)
        buf = self.buf
        for j, v in enumerate(samples):
            k = i0 + j
            if 0 <= k < len(buf):
                buf[k] += v * gain

    def write(self, path, peak=0.89):
        m = max(1e-9, max(abs(v) for v in self.buf))
        g = peak / m if m > peak else 1.0
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(array.array("h", (int(max(-1, min(1, v * g)) * 32767) for v in self.buf)).tobytes())


rng = random.Random(7)


def env_ad(n, attack, sr=SR):
    a = max(1, int(attack * sr))
    return [min(1.0, i / a) for i in range(n)]


def kick(dur=0.32):
    n = int(dur * SR)
    out, ph = [], 0.0
    for i in range(n):
        t = i / SR
        f = 45 + 95 * math.exp(-t * 28)
        ph += 2 * math.pi * f / SR
        out.append(math.sin(ph) * math.exp(-t * 9))
    return out


def hat(dur=0.05):
    n, prev, out = int(dur * SR), 0.0, []
    for i in range(n):
        x = rng.uniform(-1, 1)
        out.append((x - prev) * math.exp(-i / SR * 70))
        prev = x
    return out


def tone(freqs, dur, decay, attack=0.004, vib=0.0):
    n = int(dur * SR)
    a = env_ad(n, attack)
    return [a[i] * math.exp(-i / SR * decay) *
            sum(math.sin(2 * math.pi * f * i / SR * (1 + vib * math.sin(i / SR * 30))) for f in freqs) / len(freqs)
            for i in range(n)]


def pad(freqs, dur, attack=0.6, release=0.8, trem=0.0):
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        e = min(1.0, t / attack, (dur - t) / release) if dur > 0 else 0
        tr = 1 - trem * (0.5 + 0.5 * math.sin(2 * math.pi * 5 * t))
        s = sum(math.sin(2 * math.pi * f * t) + 0.3 * math.sin(4 * math.pi * f * t) for f in freqs) / len(freqs)
        out.append(max(0.0, e) * tr * s)
    return out


def noise_sweep(dur, f0, f1, shape="mid"):
    """Low-passed noise whose cutoff sweeps f0→f1; loudest in the middle (whoosh) or at the end (riser)."""
    n, y, out = int(dur * SR), 0.0, []
    for i in range(n):
        p = i / n
        fc = f0 * (f1 / f0) ** p
        alpha = 1 - math.exp(-2 * math.pi * fc / SR)
        y += alpha * (rng.uniform(-1, 1) - y)
        e = math.sin(math.pi * p) ** 2 if shape == "mid" else p ** 2.2 * (1 - max(0, p - 0.96) * 25)
        out.append(y * e * 2.2)
    return out


def impact(dur=1.6):
    n, out, ph = int(dur * SR), [], 0.0
    for i in range(n):
        t = i / SR
        ph += 2 * math.pi * (38 + 60 * math.exp(-t * 6)) / SR
        out.append(math.sin(ph) * math.exp(-t * 2.6) + rng.uniform(-1, 1) * 0.25 * math.exp(-t * 18))
    return out


def build_audio():
    os.makedirs(OUT, exist_ok=True)
    music, sfx = Track(T.DURATION), Track(T.DURATION)
    D2, A2, D3, F3, A3, C4, Fs3 = 73.42, 110.0, 146.83, 174.61, 220.0, 261.63, 185.0
    beat = 60 / 100
    g0, g1 = T.GUESS

    # Pulse bed 0 → guess: kick on beats, hats on off-beats, minor pad; suspense layer from Q5.
    t = 0.0
    while t < g0 - 0.05:
        music.add(t, kick(), 0.55)
        music.add(t + beat / 2, hat(), 0.12)
        t += beat
    for a, b, freqs, g, trem in [(0.0, 16.8, (D3, F3, A3), 0.10, 0.0),
                                 (16.8, 32.2, (D3, F3, A3, C4), 0.11, 0.0),
                                 (32.2, g0 + 0.4, (D3, F3, A3, C4), 0.12, 0.6)]:
        music.add(a, pad(freqs, b - a, attack=0.4, release=0.4, trem=trem), g)
    # Bass notes on the bar.
    t = 0.0
    while t < g0 - 0.3:
        music.add(t, tone([D2, A2], beat * 1.8, 2.5, attack=0.01), 0.18)
        t += beat * 4
    # Build-up riser into the music drop.
    music.add(38.2, noise_sweep(g0 - 38.2, 200, 5000, "rise"), 0.10)

    # Guess: near silence — a low drone and two heartbeats, then nothing for the final beat.
    music.add(g0, pad((D2, A2), 51.0 - g0, attack=0.3, release=0.6), 0.06)
    for hb in (47.1, 48.0):
        music.add(hb, kick(0.25), 0.35)
        music.add(hb + 0.22, kick(0.22), 0.25)

    # Reveal: bright major return.
    r = T.REVEAL
    t = r + 0.6
    while t < T.DURATION - 0.6:
        music.add(t, kick(), 0.5)
        music.add(t + beat / 2, hat(), 0.12)
        t += beat
    music.add(r + 0.3, pad((D3, Fs3, A3), T.DURATION - r - 0.3, attack=0.2, release=0.6), 0.12)

    # SFX: whoosh centred on every clip cut, ding on every AI answer, impacts, celebration.
    for c in T.CLIPS[1:]:
        if abs(c["start"] - r) > 0.1:
            sfx.add(c["start"] - 0.22, noise_sweep(0.44, 400, 6000), 0.35)
    sfx.add(T.TITLE_CARD[0] - 0.8, noise_sweep(0.8, 300, 4000, "rise"), 0.25)
    sfx.add(T.TITLE_CARD[0] + 0.05, impact(1.0), 0.45)
    for a, b, who, _ in T.LINES:
        if who == T.AI and a < r:
            sfx.add(a - 0.12, tone([1567.98, 2349.32], 0.7, 7), 0.22)
    sfx.add(32.0, impact(1.2), 0.3)          # "إحنا بنقرب"
    sfx.add(g0, impact(1.8), 0.6)            # the drop
    for k, f in enumerate([587.33, 739.99, 880.0, 1174.66, 1479.98]):
        sfx.add(r + k * 0.06, tone([f, f * 2], 0.9, 4), 0.22)
    sfx.add(r, impact(1.2), 0.5)
    sfx.add(r, [v * math.exp(-i / SR * 3) for i, v in enumerate(hat(1.2))], 0.25)

    music.write(os.path.join(OUT, "music.wav"))
    sfx.write(os.path.join(OUT, "sfx.wav"))


def build_assets(draft=False):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "overlay.ass"), "w", encoding="utf-8") as f:
        f.write(ass_overlay(draft=draft))
    build_audio()


# ───────────────────────────── video ─────────────────────────────

def probe_size(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                   "-show_entries", "stream=width,height", "-of", "json", path])
    s = json.loads(out)["streams"][0]
    return s["width"], s["height"]


def find_ref(prefix):
    for name in sorted(os.listdir(REFS)):
        if name.startswith(prefix):
            return os.path.join(REFS, name)
    raise SystemExit(f"refs/: no photo starting with {prefix!r}")


def ass_filter():
    return "ass=%s:fontsdir=%s" % (os.path.join(OUT, "overlay.ass"), FONTS)


def build_animatic():
    """Timing/edit preview: each clip is a Ken-Burns move on one of the reference photos."""
    build_assets(draft=True)
    seg_dir = os.path.join(OUT, "segments")
    os.makedirs(seg_dir, exist_ok=True)
    segs = []
    for c in T.CLIPS:
        prefix, fx, fy, frac, z0, z1 = c["ref"]
        src = find_ref(prefix)
        iw, ih = probe_size(src)
        ch = frac * ih
        cw = ch * T.W / T.H
        if cw > iw:
            cw, ch = iw, iw * T.H / T.W
        x = min(max(0, fx * iw - cw / 2), iw - cw)
        y = min(max(0, fy * ih - 0.40 * ch), ih - ch)
        n = int(round((c["end"] - c["start"]) * T.FPS))
        vf = (f"crop={int(cw)}:{int(ch)}:{int(x)}:{int(y)},scale={T.W * 2}:{T.H * 2},"
              f"zoompan=z='{z0}+({z1}-{z0})*on/{max(1, n - 1)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':"
              f"d={n}:s={T.W}x{T.H}:fps={T.FPS},"
              "eq=contrast=1.06:saturation=0.92:brightness=-0.02,vignette=angle=PI/4.5,format=yuv420p")
        seg = os.path.join(seg_dir, c["id"] + ".mp4")
        run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vf", vf, "-frames:v", str(n),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", seg])
        segs.append(seg)
    finish(segs, dialogue=None, out_name="animatic.mp4")


def build_final():
    """Assemble the generated clips: conform, cut to plan, add AI voice, music, SFX and overlays."""
    build_assets(draft=False)
    seg_dir = os.path.join(OUT, "conformed")
    os.makedirs(seg_dir, exist_ok=True)
    segs = []
    for c in T.CLIPS:
        src = os.path.join(CLIPS_DIR, c["id"] + ".mp4")
        if not os.path.exists(src):
            raise SystemExit(f"missing {src} — generate it from SHOTLIST.md first")
        d = c["end"] - c["start"]
        vf = (f"scale={T.W}:{T.H}:force_original_aspect_ratio=increase,crop={T.W}:{T.H},fps={T.FPS},"
              f"tpad=stop_mode=clone:stop_duration={d},trim=duration={d},setpts=PTS-STARTPTS,format=yuv420p")
        af = f"aresample={SR},aformat=channel_layouts=mono,apad,atrim=duration={d},asetpts=PTS-STARTPTS"
        seg = os.path.join(seg_dir, c["id"] + ".mp4")
        has_audio = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a",
                                             "-show_entries", "stream=index", "-of", "csv=p=0", src]).strip()
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", src]
        if not has_audio:
            cmd += ["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono"]
        cmd += ["-vf", vf, "-af", af, "-map", "0:v", "-map", "0:a" if has_audio else "1:a",
                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-c:a", "pcm_s16le", "-t", str(d),
                seg.replace(".mp4", ".mov")]
        run(cmd)
        segs.append(seg.replace(".mp4", ".mov"))
    finish(segs, dialogue=True, out_name="final.mp4")


def ai_voice_inputs():
    """AI voice: either one full-length voice/ai_track.wav, or per-line voice/ai_NN.wav (NN = line number in timeline.LINES)."""
    full = os.path.join(VOICE_DIR, "ai_track.wav")
    if os.path.exists(full):
        return [(full, 0.0)]
    items = []
    for idx, (a, _, who, _) in enumerate(T.LINES, 1):
        p = os.path.join(VOICE_DIR, "ai_%02d.wav" % idx)
        if who == T.AI and os.path.exists(p):
            items.append((p, a))
    return items


def finish(segs, dialogue, out_name):
    lst = os.path.join(OUT, "concat.txt")
    with open(lst, "w") as f:
        f.writelines("file '%s'\n" % s for s in segs)
    inputs = ["-f", "concat", "-safe", "0", "-i", lst,
              "-i", os.path.join(OUT, "music.wav"), "-i", os.path.join(OUT, "sfx.wav")]
    fc = [f"[0:v]{ass_filter()}[v]"]
    if dialogue:
        voices = ai_voice_inputs()
        for p, _ in voices:
            inputs += ["-i", p]
        parts = ["[0:a]aresample=%d[d0]" % SR]
        names = ["[d0]"]
        for k, (_, at) in enumerate(voices):
            parts.append("[%d:a]aresample=%d,aformat=channel_layouts=mono,adelay=%d:all=1[ai%d]" % (3 + k, SR, int(at * 1000), k))
            names.append("[ai%d]" % k)
        parts.append("%samix=inputs=%d:normalize=0:duration=first,asplit=2[dlg][key]" % ("".join(names), len(names)))
        parts.append("[1:a]volume=0.55[m]")
        parts.append("[m][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[mduck]")
        parts.append("[dlg][mduck][2:a]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[a]")
        fc += parts
    else:
        fc.append("[1:a]volume=0.8[m];[m][2:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
    out = os.path.join(OUT, out_name)
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
         "-map", "[v]", "-map", "[a]", "-t", str(T.DURATION),
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(T.FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-movflags", "+faststart", out])
    print("wrote", out)


# ───────────────────────────── shot list ─────────────────────────────

def clip_lines(c):
    return [(a, b, who, text) for a, b, who, text in T.LINES if c["start"] <= a < c["end"]]


def clip_prompt(c):
    d = c["end"] - c["start"]
    beats = []
    for a, b, who, text in clip_lines(c):
        rel = "%.1f–%.1fs" % (a - c["start"], b - c["start"])
        if who == T.ME:
            beats.append(f'{rel}: he says in Egyptian Arabic: "{text}"')
        else:
            beats.append(f"{rel}: he is silent, listening to an off-screen voice to camera-right, reacting naturally")
    if not beats:
        beats.append("no dialogue")
    return (
        f"{d:.1f}-second vertical 9:16 photoreal clip. {T.IDENTITY} {T.WARDROBE} {T.SET}\n"
        f"Shot: {c['shot']}. Camera: {c['camera']}.\n"
        f"Performance: {c['face']}. Body: {c['body']}. He mostly looks into the lens; when listening he glances to camera-right.\n"
        f"Timing: " + "; ".join(beats) + ".\n"
        f"{T.AUDIO_RULE}"
    )


def build_plan():
    out = ["# خمن الفيلم — Shot list (generated from `timeline.py`)\n",
           "Generate each clip with the **same reference photos attached every time**. "
           "Paste the prompt as-is; paste the negative prompt in the tool's negative field "
           "(or append `Avoid: …` if it has none). Save the result as `clips/<ID>.mp4`.\n",
           "**Negative prompt (all clips):** " + T.NEGATIVE + "\n"]
    for c in T.CLIPS:
        d = c["end"] - c["start"]
        out.append(f"\n## {c['id']} · {c['start']:.1f}s → {c['end']:.1f}s ({d:.1f}s)\n")
        out.append("| | |\n|---|---|")
        out.append(f"| الكادر | {c['shot']} |")
        out.append(f"| حركة الكاميرا | {c['camera']} |")
        out.append(f"| تعبير الوجه | {c['face']} |")
        out.append(f"| حركة الجسم | {c['body']} |")
        out.append(f"| المؤثرات الصوتية | {c['sfx']} |")
        out.append(f"| الموسيقى | {c['music']} |")
        out.append(f"| على الشاشة | {c['onscreen']} |")
        out.append("")
        out.append("**الحوار:**\n")
        for a, b, who, text in clip_lines(c) or [(0, 0, "", "—")]:
            label = "أنا" if who == T.ME else ("AI" if who == T.AI else "")
            out.append(f"- `{a:05.2f}–{b:05.2f}` **{label}**: {text}" if label else "- —")
        out.append("\n**Prompt:**\n\n```text\n" + clip_prompt(c) + "\n```")
    path = os.path.join(HERE, "SHOTLIST.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    {"plan": build_plan, "assets": build_assets, "animatic": build_animatic, "final": build_final}[cmd]()
