---
name: mlx-local-workflows
description: Build or maintain MLX Studio's local text, audio, image, and video workflows. Use when adding a reusable local inference workflow, preset, or browser demo to this project.
---

# MLX local workflows

Keep changes reproducible, local-first, and suited to Apple Silicon.

## Before changing a workflow

- Read `configs/models.yaml` to choose an installed model or identify a planned
  download.
- Read `docs/python.md` for dependency, quality, and demo conventions.
- Reuse the appropriate example from the unmodified upstream checkout at
  `~/Developer/build/py3-code/mlx-examples`; do not patch that checkout from
  this workflow.

## Runtime selection

- Prefer a maintained MLX workflow for batch or reproducible text, audio,
  image, and video jobs.
- Use Ollama for its installed interactive language, vision, and image models
  when that is the more direct local path.
- Treat new model downloads as an explicit operation: state the model, source,
  expected purpose, and local destination before downloading.

## Deliverables

- Put reusable configuration in `configs/` and documented usage in `docs/`.
- Keep generated media, models, caches, and logs in their ignored local
  directories.
- Provide a browser-visible demo under `demos/web/` when a workflow benefits
  from human interaction or review.
- Run `make format` and `make check` before committing code changes. These use
  isolated tools and must not modify the protected `mlx` environment.
