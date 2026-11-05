#!/usr/bin/env python3
"""Make side-by-side comparison pairs: reference frame left, our render right, both 960x540.

    pairs.py <round-dir>        reads <round-dir>/pairs.json and <round-dir>/renders/<scene>.mp4 + .timing.json

pairs.json: [{"id": "V1-labels-lens", "ref": "0904s-15-schematic-lens.jpg", "scene": "u2-cell-switch", "line": 0, "f": 0.95}, ...]
The frame time is the moment fraction f of narration line `line` is spoken (same as T(line, f) in the scene).
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    rd = Path(sys.argv[1]).resolve()
    for p in json.loads((rd / "pairs.json").read_text()):
        tm = json.loads((rd / "renders" / f"{p['scene']}.timing.json").read_text())
        t = round(tm["starts"][p["line"]] + p["f"] * tm["durs"][p["line"]], 2)
        ours = rd / "renders" / f"{p['id']}-ours.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(rd / "renders" / f"{p['scene']}.mp4"),
                        "-frames:v", "1", str(ours)], check=True)
        out = rd / f"{p['id']}-pair.jpg"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(ROOT / "frames" / p["ref"]), "-i", str(ours),
                        "-filter_complex", "[0]scale=960:540[a];[1]scale=960:540[b];[a][b]hstack", "-q:v", "3", str(out)], check=True)
        print(f"{out.name}: {p['scene']} at {t}s (line {p['line']} + {p['f']})")


if __name__ == "__main__":
    main()
