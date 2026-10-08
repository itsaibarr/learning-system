# Voiceover: how narrated lesson videos are made

Every lesson animation is narrated by a local voice. Nothing calls a paid API.

```
learn figure <name>   (agent pipes a Manim scene with a NARRATION list)
  1. old-ManimGL check              learn.py OLD_MANIM_API
  2. NARRATION parsed + checked      narration_of(), validate_narration()
  3. each line spoken FIRST          tts_lines()  -> Voicebox server -> Kokoro-82M -> WAV
       (leading silence trimmed; each line's real length measured)
  4. Manim render, checked           render_manim() + MANIM_HARNESS
       `with self.voice(i):` starts line i there and pads the block to the line's length
       (old scenes without voice blocks: numbered-caption marks, align_narration())
  5. timeline planned                schedule(exact=True)  (lines start at their voice marks)
  7. audio + video mixed             compose()    (ffmpeg: freezes, EBU R128 -16 LUFS, AAC)
  8. saved to the vault              save_figure() -> Attachments/learn/<topic>/<name>.mp4
learn block <concept>                adds a folded "Narration" transcript under each narrated video
```

## Where things live

| What | Where |
| --- | --- |
| All voiceover code | `scripts/learn.py`, section "narration" |
| Voicebox server (v0.5.0, MIT) | `~/.local/share/learning-system/voicebox` (+ `.venv`, Python 3.12) |
| Its data (profiles, generations, log) | `~/.local/share/learning-system/voicebox-data/` (`server.log`) |
| Kokoro-82M weights (~313 MB, Apache-2.0) | Hugging Face cache, `~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M`; downloaded once |
| Slim dependency list | `scripts/voicebox-requirements.txt` (Kokoro only; upstream also ships Qwen/LuxTTS/Chatterbox) |
| Install / repair | `bash scripts/install.sh` (idempotent; ends with a spoken smoke test) |
| Narrator voice | learner state `profile.voice` (default `af_heart`); `learn voice [id]` |
| Narration text per video | learner state `narrations[<vault path>]` |

## The TTS backend

`tts_lines(lines, voice, outdir) -> [(wav_path, seconds)]` is the only function that knows
about the voice engine. It:

1. checks `GET /health` at `LEARN_VOICEBOX_URL` (default `http://127.0.0.1:17493`); if nothing
   answers, starts `python -m backend.main --port 17493 --data-dir ...` from the install dir,
   detached, and waits up to 90 s (cold start ~25 s);
2. finds or creates a preset profile `learn-narrator-<voice>` (`voice_type=preset`,
   `preset_engine=kokoro`);
3. per line: `POST /generate` (engine `kokoro`), reads the `GET /generate/{id}/status` SSE
   stream until `completed`/`failed` (120 s limit), then `GET /audio/{id}` -> WAV (24 kHz mono).

`LEARN_TTS=fake` writes silent WAVs at 2.6 words/s (tests); `LEARN_TTS=none` turns narration
off. `LEARN_VOICEBOX_AUTOSTART=0` never starts the server.

**Replacing the backend:** add a branch in `tts_lines()` that returns `[(wav, seconds)]`
for each line. Nothing else depends on Voicebox.

## Sync

**Audio-first (default).** `learn figure` speaks every NARRATION line before rendering and
passes the measured lengths to the harness. In the scene, `with self.voice(i):` marks where
line i starts; the harness pads the block with a wait so it lasts as long as the line plus a
0.35 s gap. The voice therefore starts exactly at its event and the picture never runs ahead.
One line = one visual event (4-40 words), so a 3-minute scene stays in sync line by line.
Measured with the real voice: speech onset within 0.03 s of each voice mark.

**Fallback (scenes without voice blocks, or TTS off).** The harness records when each
numbered caption first appears; line N starts there, and the picture freezes (`tpad`) while
line N-1 is still being spoken. If speech outlasts the video, the last frame is held.

Scene length: 2-180 s (target 60-120 s); a unit uses one scene per segment.

## Mixing

ffmpeg places each line with `adelay`, mixes, normalises to -16 LUFS (EBU R128, true peak
-1.5 dB), encodes AAC 160 kbit/s at 48 kHz. The video stream is copied when no freeze is
needed; with freezes it is re-encoded once (libx264 veryfast, CRF 20).

## When something fails

| Failure | Result |
| --- | --- |
| Voicebox not installed / won't start / a line fails or times out | silent video saved, `WARNING: narration failed (...)`, lesson continues |
| ffmpeg can't mix | silent video saved, warning |
| NARRATION missing | rejected before rendering (use `--silent` to opt out deliberately) |
| NARRATION has LaTeX, citations, markdown, wrong length | rejected before rendering, with the fix |
| Line count != numbered captions, or a line only reads its caption | rejected after rendering, with the fix |
| Voice blocks used, but not one per NARRATION line | rejected after rendering, with the fix |

Rejections are not counted as failed Manim attempts.

## Measured on this machine (Apple M5, 16 GB)

- Kokoro speaks ~7x faster than real time: 14 s of speech in 2 s; server RSS ~1 GB.
- `learn figure` with narration: ~6-11 s warm (render + voice + mix), ~14 s when the
  server has to start.
- Disk: Voicebox venv 1.1 GB, Kokoro 313 MB.

## Known limits

- English only (Kokoro's English voices). Kokoro also speaks es/fr/hi/it/pt/ja/zh with
  other voices; Russian would need another engine (e.g. Qwen CustomVoice, ~1.2 GB).
- Pronunciation follows misaki G2P: most acronyms and terms are fine, but unusual ones may
  be read oddly. Write them as they should sound ("S Q L" vs "sequel").
- Freezes can be long when a scene is short and its narration long; the visuals guide asks
  for scenes paced at ~2.6 words/s per step.
- matplotlib fallback figures and `--still` pictures have no voice.
