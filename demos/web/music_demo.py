"""Local HTTP API for the lyric-conditioned MiniMax Music 3 browser demo."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import uuid
import wave
from dataclasses import asdict, dataclass
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

WEB_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WEB_DIR.parents[1]
MODEL_CACHE_DIR = PROJECT_DIR / ".local/models/huggingface"
OUTPUT_DIR = WEB_DIR / "generated/music"
PROMPTS_DIR = PROJECT_DIR / "prompts"
OLLAMA_MODEL = "qwen3:32b"
MUSIC_MODEL = "mlx-community/MiniMax-Music3-4bit"
SUPPORTED_DURATIONS = (30, 60, 120, 180, 240, 300)
LYRICS_TEMPLATE = (PROMPTS_DIR / "lyrics.txt").read_text(encoding="utf-8")
MUSIC_TEMPLATE = (PROMPTS_DIR / "minimax_music3.txt").read_text(encoding="utf-8")
ANSI_ESCAPE = re.compile(r"\x1b(?:[@-_][0-?]*[ -/]*[@-~]|\[[0-?]*[ -/]*[@-~])")
TITLE_LINE = re.compile(r"(?im)^(?:\*\*)?title\s*:")
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SongRequest:
    theme: str
    mood: str
    genre: str


def require_text(value: object, field_name: str, maximum: int = 240) -> str:
    """Return a compact user field or raise a request-friendly error."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text.")
    text = " ".join(value.split())
    if not text:
        raise ValueError(f"{field_name} is required.")
    if len(text) > maximum:
        raise ValueError(f"{field_name} must be at most {maximum} characters.")
    return text


def require_lyrics(value: object) -> str:
    """Accept editable structured lyrics while preserving sections and line breaks."""
    if not isinstance(value, str):
        raise ValueError("Lyrics must be text.")
    lyrics = "\n".join(line.strip() for line in value.splitlines()).strip()
    if not lyrics:
        raise ValueError("Lyrics are required.")
    if len(lyrics) > 4_000:
        raise ValueError("Lyrics must be at most 4000 characters.")
    return lyrics


def require_duration(value: object) -> int:
    """Accept only song lengths supported by this compact local demo."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("Song duration must be a whole number of seconds.")
    if value not in SUPPORTED_DURATIONS:
        supported = ", ".join(map(str, SUPPORTED_DURATIONS))
        raise ValueError(f"Song duration must be one of: {supported} seconds.")
    return value


def parse_song_request(data: object) -> SongRequest:
    """Validate browser JSON independently from the HTTP handler."""
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object.")
    return SongRequest(
        theme=require_text(data.get("theme"), "Theme"),
        mood=require_text(data.get("mood"), "Mood"),
        genre=require_text(data.get("genre"), "Genre"),
    )


def build_music_prompt(request: SongRequest) -> str:
    """Create MiniMax Music 3's caption independently from the lyric sheet."""
    return MUSIC_TEMPLATE.format(**asdict(request)).strip()


def build_lyrics_instruction(request: SongRequest) -> str:
    """Keep the LLM task bounded so the result fits the compact demo UI."""
    return LYRICS_TEMPLATE.format(**asdict(request)).strip()


def lyrics_only(raw_output: str) -> str:
    """Remove terminal control codes and any visible Qwen thinking preamble."""
    cleaned = ANSI_ESCAPE.sub("", raw_output).strip()
    title = TITLE_LINE.search(cleaned)
    return cleaned[title.start() :].strip() if title else cleaned


def markdown_runner_log(stdout: str, stderr: str) -> str:
    """Format the generator's terminal output for readable local logs."""
    output = "\n".join(part.strip() for part in (stdout, stderr) if part.strip())
    return "\n".join(("# MiniMax Music 3 output", "```text", output or "(no output)", "```"))


def run_lyrics(request: SongRequest) -> str:
    """Generate lyrics using the local Ollama text model."""
    if shutil.which("ollama") is None:
        raise RuntimeError("Ollama is not installed or is not on PATH.")
    try:
        completed = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL, build_lyrics_instruction(request)],
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except FileNotFoundError as error:
        raise RuntimeError("Ollama is not installed or is not on PATH.") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Lyric generation timed out after three minutes.") from error
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or "Ollama could not generate lyrics."
        raise RuntimeError(message) from error

    lyrics = lyrics_only(completed.stdout)
    if not lyrics:
        raise RuntimeError("Ollama returned no lyrics.")
    return lyrics


def music_readiness() -> list[str]:
    """Check the local MLX Audio runtime without loading the model."""
    issues: list[str] = []
    if shutil.which(sys.executable) is None:
        issues.append("The configured Python executable is unavailable.")
    try:
        __import__("mlx_audio.music.generate")
    except ImportError as error:
        if "No Metal device available" in str(error):
            issues.append("MLX cannot access an Apple Metal device in this session.")
        else:
            issues.append("The protected mlx environment is missing mlx-audio music support.")
    return issues


def music_environment() -> dict[str, str]:
    """Configure local model caching and a stable Hub download path."""
    environment = os.environ.copy()
    environment["HF_HOME"] = str(MODEL_CACHE_DIR)
    environment["HF_HUB_DISABLE_XET"] = "1"
    return environment


def wav_duration_seconds(path: Path) -> float:
    """Read the duration that the browser will actually receive."""
    with wave.open(str(path)) as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def run_music(caption: str, lyrics: str, duration_seconds: int) -> tuple[str, float]:
    """Generate a lyric-conditioned MiniMax song and return its verified duration."""
    if issues := music_readiness():
        raise RuntimeError(" ".join(issues))
    duration_seconds = require_duration(duration_seconds)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.wav"
    output_path = OUTPUT_DIR / filename
    command = [
        sys.executable,
        str(WEB_DIR / "minimax_music_runner.py"),
        "--model",
        MUSIC_MODEL,
        "--caption",
        caption,
        "--lyrics",
        lyrics,
        "--duration-seconds",
        str(duration_seconds),
        "--output-path",
        str(output_path),
    ]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=3_600,
            env=music_environment(),
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Music generation timed out after 60 minutes.") from error
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or "MiniMax Music 3 could not create audio."
        raise RuntimeError(message) from error
    LOGGER.info("\n%s", markdown_runner_log(completed.stdout, completed.stderr))
    if not output_path.is_file():
        raise RuntimeError("MiniMax Music 3 completed without writing an audio file.")
    actual_duration = wav_duration_seconds(output_path)
    if actual_duration < duration_seconds * 0.95:
        raise RuntimeError(
            f"MiniMax Music 3 wrote {actual_duration:.1f} seconds, not the requested "
            f"{duration_seconds} seconds."
        )
    return f"/generated/music/{filename}", actual_duration


class MusicDemoHandler(SimpleHTTPRequestHandler):
    """Serve static demo files plus a small JSON API."""

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/health":
            self.send_json(
                HTTPStatus.OK,
                {
                    "ollama_model": OLLAMA_MODEL,
                    "music_model": MUSIC_MODEL,
                    "music_issues": music_readiness(),
                    "model_cache": str(MODEL_CACHE_DIR),
                },
            )
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = self.read_json()
            if self.path == "/api/lyrics":
                request = parse_song_request(body)
                lyrics = run_lyrics(request)
                caption = build_music_prompt(request)
                LOGGER.info("\n# Generated lyrics\n\n%s", lyrics)
                self.send_json(
                    HTTPStatus.OK,
                    {
                        "lyrics": lyrics,
                        "music_prompt": caption,
                        "request": asdict(request),
                    },
                )
                return
            if self.path == "/api/music":
                if not isinstance(body, dict):
                    raise ValueError("Request body must be a JSON object.")
                caption = require_text(body.get("music_prompt"), "Music prompt", maximum=1_000)
                lyrics = require_lyrics(body.get("lyrics"))
                duration_seconds = require_duration(body.get("duration_seconds", 60))
                audio_url, actual_duration = run_music(caption, lyrics, duration_seconds)
                self.send_json(
                    HTTPStatus.OK,
                    {"audio_url": audio_url, "duration_seconds": round(actual_duration)},
                )
                return
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown API route."})
        except json.JSONDecodeError:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be valid JSON."})
        except (ValueError, RuntimeError) as error:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def read_json(self) -> object:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 20_000:
            raise ValueError("Request body must be between 1 and 20,000 bytes.")
        return json.loads(self.rfile.read(length))

    def send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local lyric-to-song browser demo.")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    handler = partial(MusicDemoHandler, directory=str(WEB_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Music demo: http://127.0.0.1:{args.port}/music.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping music demo.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
