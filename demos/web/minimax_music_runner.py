"""Run lyric-conditioned MiniMax Music 3 without loading it in the web server."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a lyric-conditioned MLX song.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--caption", required=True)
    parser.add_argument("--lyrics", required=True)
    parser.add_argument("--duration-seconds", required=True, type=int)
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()

    from mlx_audio.music.generate import generate_music

    generate_music(
        caption=args.caption,
        lyrics=args.lyrics,
        model=args.model,
        duration=args.duration_seconds,
        output_path=args.output_path,
        steps=30,
        verbose=True,
    )


if __name__ == "__main__":
    main()
