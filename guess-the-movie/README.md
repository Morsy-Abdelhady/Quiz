# خمن الفيلم 🎬 — 60s vertical challenge video

All timing lives in `timeline.py`. Everything else is generated from it: subtitles, counter, timer, AI-host panel, title and reveal cards, music, SFX, shot list and the final edit.

## Workflow

1. `python3 build.py plan` writes **SHOTLIST.md**: 12 clips (each ≤ 8 s), with framing, camera, performance, SFX, music, on-screen text and a ready-to-paste prompt for each.
2. Generate each clip in an image-to-video model with native audio and lip-sync, attaching **the same reference photos every time**. Save the results as `clips/C01.mp4 … clips/C12.mp4`.
   - Generated clips contain only you. The AI host is a graphic panel added in the edit, so the model never has to render two characters.
3. Add the AI host's voice in Egyptian Arabic (any TTS with an `ar-EG` voice, or a voice actor):
   - either one 60 s file `voice/ai_track.wav` aligned to the timeline,
   - or one file per line, `voice/ai_NN.wav`, where NN is the line's number in `timeline.LINES` (1-based). Each file is placed at its line's start time automatically.
4. `python3 build.py final` writes `out/final.mp4` (1080×1920, 30 fps). This step conforms and cuts every clip to the plan, burns in Arabic subtitles and graphics, and mixes dialogue, AI voice, ducked music and SFX.

`python3 build.py animatic` renders a timing preview from the photos in `refs/` (no dialogue audio).

`refs/`, `clips/`, `voice/` and `out/` are git-ignored, so personal photos and renders stay out of the repo.

Requires Python 3 (stdlib only) and ffmpeg built with libass. The font is Cairo (SIL OFL), in `fonts/`.
