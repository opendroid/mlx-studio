# MLX Studio agent guide

This project is a local-first Apple Silicon studio for text, audio, image, and
video workflows. Prefer MLX whenever a maintained MLX implementation exists.
Use the installed Ollama models for interactive tasks and the upstream MLX
examples for direct, reproducible workflows.

## Read first

- Read `configs/models.yaml` for the model registry and local paths.
- Read `docs/python.md` before adding or changing Python code.
- Use `skills/mlx-local-workflows/SKILL.md` for a workflow-level change.

## Runtime policy

- Run ML workflows with the existing Conda environment named `mlx`:
  `conda activate mlx`. It is protected. Never run package installs, upgrades,
  removals, or environment updates against it.
- Run code-quality tools through the Makefile. Its isolated `uvx` tools must
  not add packages to the `mlx` environment.
- Do not edit the upstream checkout at
  `~/Developer/build/py3-code/mlx-examples`. Put studio-specific wrappers,
  presets, and documentation in this repository.

## Repository policy

- Keep models, caches, source media, generated media, logs, secrets, and
  machine-local settings out of Git. `.gitignore` is intentional.
- Put reusable conventions in `docs/`, model choices in `configs/`, and
  narrowly scoped agent guidance in `skills/`.
- Make browser-visible demos under `demos/web/`. Use an HTML interface or a
  local web container rather than a native GUI as the primary demo surface.
