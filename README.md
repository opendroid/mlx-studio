# MLX Studio

MLX Studio is a local-first workspace for Apple Silicon text processing,
audio, image, and video workflows. It uses MLX wherever a maintained MLX path
exists and retains Ollama as the convenient interactive runtime for installed
models.

## Boundaries

- `mlx` is the project Conda environment and is protected. This project never
  updates it.
- Quality tools run in isolated `uvx` environments through the Makefile, so
  they do not alter the ML runtime.
- `~/Developer/build/py3-code/mlx-examples` remains an unmodified upstream
  reference checkout. Studio-specific work belongs here.
- The Git repository contains code, documentation, configuration, and small
  HTML demos only. Models, caches, media, logs, and secrets stay local.

## Workspace

```text
configs/        Model registry and shareable presets
docs/           Runtime and Python standards
skills/         Reusable guidance for AI coding agents
demos/web/      Browser-first demo source
inputs/         Local source media (ignored)
audio/          Local audio artifacts (ignored)
images/         Local image artifacts (ignored)
video/          Local video artifacts (ignored)
outputs/        Final generated media (ignored)
logs/           Runtime logs (ignored)
```

## Workflow map

| Need | Primary local route | Reference implementation |
| --- | --- | --- |
| Text processing and classification | MLX LLMs; Ollama Qwen for interactive work | `llms/` |
| Transcription and synthetic speech | `mlx-whisper`, `mlx-audio` | `whisper/` |
| Synthetic music | MLX MusicGen | `musicgen/` |
| Image creation and management | Ollama image models; direct MLX FLUX when control matters | `flux/` |
| GIFs and video | FFmpeg plus MLX Wan 2.1 | `video/wan2.1/` |

See [the model registry](configs/models.yaml) before selecting or downloading a
model.

## Common commands

Start each ML workflow with `conda activate mlx`. The Makefile keeps quality
tools isolated and does not modify that environment:

```bash
make format
make check
make demo
```

`make demo` serves the static demo at `http://127.0.0.1:8080`.

## Agent guidance

Coding agents should begin with [AGENTS.md](AGENTS.md). The reusable local MLX
workflow guidance is in
[skills/mlx-local-workflows/SKILL.md](skills/mlx-local-workflows/SKILL.md).
