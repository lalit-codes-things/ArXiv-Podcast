# ArXiv Podcast

ArXiv Podcast turns eligible arXiv papers into pure conversational podcast episodes. It downloads a paper, checks that the license allows derivative works, extracts core text, asks OpenAI to summarize and write a 10+ minute Host/Expert discussion, synthesizes speech with free TTS, and produces an MP3 plus a waveform image.

## Features

- Consistent ArXiv Podcast frontend branding with a fixed Galaxy background and glass panels.
# Paper to Podcast

Paper to Podcast turns an arXiv paper into a pure conversational podcast episode. It downloads a paper, checks that the license allows derivative works, extracts the core text, asks OpenAI to summarize and script a 10+ minute Host/Expert discussion, synthesizes speech with free TTS, and produces an MP3 plus a waveform image.

## Features

- No ElevenLabs dependency.
- No intro, outro, citation sounds, beeps, or bundled audio assets.
- Free Edge TTS by default with a configurable male voice (`en-GB-RyanNeural`).
- Optional Kokoro TTS fallback via `TTS_ENGINE=kokoro` if you install the optional dependencies.
- Generated audio and waveform files are written to `output/`.
- FastAPI backend with a React web UI.
- FastAPI backend with a single-page web UI.
- Unit tests with mocks for external APIs.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`.

## Frontend development

The ArXiv Podcast frontend is a Vite React app in `frontend/`.

```bash
npm install
npm run dev
```

For backend-served production assets, build the frontend first:

```bash
npm run build
```

The FastAPI app serves `frontend/dist` when that build output exists.

## Run locally

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Open <http://localhost:8000>, enter an arXiv ID, and wait for generation to complete. If you are changing the React UI, run the Vite dev server separately or build the frontend before starting FastAPI.
Open <http://localhost:8000>, enter an arXiv ID, and wait for generation to complete.

## Docker

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
docker-compose up --build
```

The app will be available at <http://localhost:8000>. The `output/` directory is mounted so generated MP3 and PNG files persist on the host.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | empty | Required for summary and script generation. |
| `TTS_ENGINE` | `edge` | `edge` or `kokoro`. |
| `TTS_VOICE` | `en-GB-RyanNeural` | Voice ID for the chosen TTS engine. |
| `TARGET_DURATION_SECONDS` | `600` | Prompt-level target for the episode length. |
| `MAX_SCRIPT_DURATION_SECONDS` | `1200` | Safety configuration for downstream customization. |
| `OUTPUT_DIR` | `output` | Directory for generated files. |

## Tests

```bash
pytest tests/ -v
```

## License

MIT. See [LICENSE](LICENSE).
