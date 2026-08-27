#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
SHEET = ASSETS / "poolcat-spritesheet.png"
FRAMES = ASSETS / "frames"

CELL_W = 192
CELL_H = 208
STATES = {
    "idle": (0, 6),
    "walk_right": (1, 8),
    "walk_left": (2, 8),
    "happy": (3, 4),
    "jump": (4, 5),
    "sad": (5, 8),
    "sleepy": (6, 6),
    "eat": (8, 6),
}


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    if not SHEET.exists():
        raise SystemExit(f"Missing spritesheet: {SHEET}")
    FRAMES.mkdir(parents=True, exist_ok=True)
    for state, (row, count) in STATES.items():
        target_dir = FRAMES / state
        target_dir.mkdir(parents=True, exist_ok=True)
        for col in range(count):
            out = target_dir / f"{col:02d}.png"
            offset_y = row * CELL_H
            offset_x = col * CELL_W
            run([
                "sips",
                "-c", str(CELL_H), str(CELL_W),
                "--cropOffset", str(offset_y), str(offset_x),
                str(SHEET),
                "--out", str(out),
            ])
    print(f"Sliced frames into {FRAMES}")


if __name__ == "__main__":
    main()
