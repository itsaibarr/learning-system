#!/usr/bin/env python3
"""Render a scene through the real engine pipeline (voice -> hf_prepare -> hyperframes check -> render) for the visual
comparison rounds, without a learn session: nothing is written to the vault or state/learner.json.

    render.py <scene.html | dram scene name> <out-dir> [--fake-voice]

Writes <out-dir>/<name>.mp4 and <name>.timing.json (line starts/durations, so frames can be taken at narrated beats).
"""
import json, shutil, subprocess, sys, tempfile, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
import learn  # noqa: E402


def load(arg):
    p = Path(arg)
    if p.suffix == ".html" and p.exists():
        return p.stem, p.read_text()
    subprocess.run([sys.executable, str(REPO / "dram-memory/kit/build.py"), arg], check=True, capture_output=True)
    return arg, (REPO / "dram-memory/build" / f"{arg}.html").read_text()


def main():
    name, html = load(sys.argv[1])
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    lines = learn.hf_narration(html)
    learn.validate_narration(lines)
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        clips = None if "--fake-voice" in sys.argv else learn.tts_lines(lines, learn.DEFAULT_VOICE, tmp)
        t1 = time.time()
        mp4 = learn.render_hyperframes(html, lines, clips, tmp)
        t2 = time.time()
        shutil.copy(mp4, out / f"{name}.mp4")
        durs = [d for _, d in clips] if clips else [max(1.0, len(x.split()) / 2.6) for x in lines]
        starts, total = learn.hf_timing(durs, learn.hf_pauses(html, len(durs)))
    words = sum(len(x.split()) for x in lines)
    info = {"name": name, "starts": starts, "durs": [round(d, 2) for d in durs], "total": total, "words": words,
            "words_per_s": round(words / sum(durs), 2), "tts_s": round(t1 - t0, 1), "render_s": round(t2 - t1, 1)}
    (out / f"{name}.timing.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info))


if __name__ == "__main__":
    main()
