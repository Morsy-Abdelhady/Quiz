# خمن الفيلم 🎬 — 60s "guess the movie" challenge video

Default layout is **16:9 studio game-show** (`show`), matching the Gemini reference clip: seated in a dark studio, black shirt, HUD bar. Add `--reels` to any command for the 9:16 version.

All timing lives in `timeline.py`. Everything else is generated from it: subtitles, counter, timer, AI-host panel, title and reveal cards, music, SFX, shot list and the final edit.

## Workflow

1. `python3 build.py plan` writes **SHOTLIST.md**: 12 clips (each ≤ 8 s), with framing, camera, performance, SFX, music, on-screen text and a ready-to-paste prompt for each.
2. Generate each clip in Gemini (Veo), attaching **the same reference photos every time**, and save them as `clips/C01.mp4 … clips/C12.mp4`.
   - Only you appear on screen. The AI host is an off-screen voice that Gemini generates in the same clip, plus an "AI Host" HUD tag added in the edit.
   - The prompts forbid on-screen text, because Gemini garbles Arabic. All text is burned in by `final`.
   - Gemini returns 8 s clips. `final` finds the first spoken word in each clip and trims it to line up with the subtitles. Override per clip in `clips/offsets.json`, e.g. `{"C03": 0.6}`.
3. *(Optional, only if a clip lacks the AI voice)* Add the AI host's voice in Egyptian Arabic (any TTS with an `ar-EG` voice, or a voice actor):
   - either one 60 s file `voice/ai_track.wav` aligned to the timeline,
   - or one file per line, `voice/ai_NN.wav`, where NN is the line's number in `timeline.LINES` (1-based). Each file is placed at its line's start time automatically.
4. `python3 build.py final` writes `out/final.mp4` (1920×1080, or 1080×1920 with `--reels`; 30 fps). This step conforms and cuts every clip to the plan, burns in Arabic subtitles and graphics, and mixes dialogue, AI voice, ducked music and SFX.

`python3 build.py animatic` renders a timing preview with no dialogue audio. The `show` layout uses frames from `refs/reference.mp4` (the Gemini clip); `--reels` uses the photos in `refs/`.

`refs/`, `clips/`, `voice/` and `out/` are git-ignored, so personal photos and renders stay out of the repo.

Requires Python 3 (stdlib only) and ffmpeg built with libass. The font is Cairo (SIL OFL), in `fonts/`.
