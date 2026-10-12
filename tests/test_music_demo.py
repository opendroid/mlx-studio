import pytest

from demos.web.music_demo import (
    SongRequest,
    build_lyrics_instruction,
    build_music_prompt,
    lyrics_only,
    markdown_runner_log,
    music_environment,
    parse_song_request,
    require_duration,
    require_lyrics,
)


def test_parse_song_request_normalizes_user_text() -> None:
    request = parse_song_request(
        {"theme": "  city   lights ", "mood": " dreamy ", "genre": " synth-pop "}
    )

    assert request == SongRequest(theme="city lights", mood="dreamy", genre="synth-pop")


def test_build_music_prompt_keeps_the_song_direction() -> None:
    prompt = build_music_prompt(SongRequest("city lights", "dreamy", "synth-pop"))

    assert "dreamy synth-pop" in prompt
    assert "city lights" in prompt
    assert "clear lead singer" in prompt


def test_require_lyrics_preserves_section_newlines() -> None:
    lyrics = require_lyrics("[Verse 1]\nLine one\n\n[Chorus]\nLine two")

    assert lyrics == "[Verse 1]\nLine one\n\n[Chorus]\nLine two"


def test_require_duration_accepts_up_to_five_minutes() -> None:
    assert require_duration(300) == 300


def test_require_duration_rejects_a_duration_outside_the_ui_limit() -> None:
    with pytest.raises(ValueError, match="Song duration"):
        require_duration(360)


def test_markdown_runner_log_displays_generator_output() -> None:
    log = markdown_runner_log("Created song.wav", "")

    assert "# MiniMax Music 3 output" in log
    assert "Created song.wav" in log


def test_lyrics_instruction_requests_final_lyrics_without_reasoning() -> None:
    instruction = build_lyrics_instruction(SongRequest("city lights", "dreamy", "synth-pop"))

    assert instruction.startswith("/no_think")
    assert "city lights" in instruction
    assert "reasoning" in instruction


def test_lyrics_only_removes_thinking_and_terminal_control_codes() -> None:
    raw_output = "Thinking...\n\x1b[4D\x1b[KPlanning lyrics\nTitle: Moonlight\n[Verse 1]\nA line"

    assert lyrics_only(raw_output) == "Title: Moonlight\n[Verse 1]\nA line"


def test_music_environment_uses_the_local_hugging_face_cache() -> None:
    environment = music_environment()

    assert environment["HF_HUB_DISABLE_XET"] == "1"
    assert environment["HF_HOME"].endswith(".local/models/huggingface")
