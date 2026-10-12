# Python development standards

## Environment and dependencies

- The `mlx` Conda environment is immutable project baseline. Do not install,
  upgrade, remove, or otherwise update packages in it.
- Run all ML workflows with `conda activate mlx`. Keep runtime dependencies
  minimal and record a dependency before relying on it.
- Use the Makefile's isolated `uvx` invocations for Ruff and pytest. Those
  tools must not be installed into the protected `mlx` environment.
- Do not vendor dependencies or copy package caches into this repository.

## Code quality

- Target Python 3.13. Use type annotations on public functions and explicit
  return types where practical.
- Prefer `pathlib.Path`, small composable functions, dataclasses for structured
  local data, and the standard library before adding a dependency.
- Keep model loading out of module import time. Load heavy models only in an
  explicit command or function so commands remain inspectable and testable.
- Validate paths and media formats at system boundaries. Write generated files
  only to the ignored media/output directories.
- Use `logging` for operational messages; reserve `print` for concise CLI
  output intended for a human.
- Add a focused test for deterministic utilities and configuration parsing.
  Tests must not download a model or require a GPU unless they are explicitly
  marked as an integration test.

## Formatting and review

- Run `make format` before committing and `make check` before pushing.
- Ruff is the formatter, linter, and import sorter. Do not add a second
  formatter without a concrete compatibility reason.
- Keep functions readable and names specific. Favor clear control flow over
  compressed expressions or clever abstractions.

## Demos

- Put browser-facing demos in `demos/web/`. A static HTML shell or local web
  container is the default interface for a workflow demo.
- Keep demo source tracked, but store generated assets in
  `demos/web/generated/`, which remains local.
