# Lyric-to-synth-music demo

Run the browser demo from the repository root:

```bash
make music-demo
```

Open `http://127.0.0.1:8080/music.html`. The demo first asks the installed
local Ollama model `qwen3:32b` for full original lyrics. It then sends a style
caption and the complete lyric sheet separately to MiniMax Music 3, a local
lyric-conditioned song model. The browser keeps both fields editable so you
can review or change them before generation.

## Local prerequisites

- Ollama must be running and have `qwen3:32b` available.
- The protected `mlx` Conda environment must already contain `mlx-audio` with
  its `music` module. The demo checks this without changing the environment.

## Model download

The first successful music run downloads
`mlx-community/MiniMax-Music3-4bit` from Hugging Face. It is a deliberate
model download; the server directs the Hugging Face cache to
`.local/models/huggingface`, which is ignored by Git. Generated WAV files are
saved under `demos/web/generated/music/`, also ignored by Git.

Choose a duration from 30 seconds to 5 minutes; the initial choice is a
one-minute song. The installed MiniMax implementation allows up to six
minutes, and this demo deliberately caps requests at five. It receives the
structured lyric sheet directly and uses 30 generation steps. Generation can
take many minutes, especially while the model downloads on the first run. To
use your own Hugging Face account's rate limits, configure `HF_TOKEN` in your
local shell; never save it in this repository.

## Prompt files

The demo loads its model-facing templates from the tracked top-level
`prompts/` directory: `lyrics.txt` asks Qwen for final lyric text only,
and `minimax_music3.txt` creates the song-style caption. Keep prompt text in
that directory rather than embedding it in the Python or browser code. Both
the lyric sheet and music prompt remain editable in the browser as a human
review step.
