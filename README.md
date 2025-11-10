# Dungeons & Dragons AI Game Master

An immersive single-player Dungeons & Dragons experience powered by a FastAPI backend, a React + Tailwind frontend, and local large language models running through Ollama. The system combines AI-driven storytelling with rule enforcement and stateful campaign management.

## Project Structure

```
backend/
├── app/                # FastAPI application modules
├── data/               # SRD docs and vector database storage
├── requirements.txt    # Python dependencies
└── README.md
frontend/
├── src/                # React application source
├── package.json        # Frontend dependencies & scripts
└── tailwind.config.js  # UI configuration
```

## Getting Started

1. Clone the repository and create a Python virtual environment at the project root:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Copy `.env.example` to `.env` (or export variables manually) and set:
   - `DATABASE_URL`
   - `OLLAMA_BASE_URL`
   - `SECRET_KEY` (used to sign auth tokens)
3. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. Start the backend FastAPI server (from project root):
   ```bash
   uvicorn backend.app.main:app --reload
   ```
6. Access the app at `http://localhost:5173`, with the API served from `http://localhost:8000`.

### Authentication

- Register a new account via the UI (or `POST /api/auth/register`) to create a user.
- Obtain an access token using `POST /api/auth/token` (username + password form fields).
- All protected requests require `Authorization: Bearer <token>`. The frontend stores the token client-side and automatically attaches it to requests.

## Next Steps

- Refine access control (e.g., support shared campaigns and player roles beyond the owner).
- Extend combat tooling with turn advancement, area effects, and presets for common monsters.
- Add character sheet editing (stats, skills, spell slots) with auto-sync to encounter participants.
- Implement automated testing/CI covering API auth flows and frontend integration.

## Preparing the RAG Knowledge Base

1. Place SRD-licensed reference documents inside `backend/data/srd/`.
2. Start Ollama locally and ensure the desired model is pulled:
   ```bash
   ollama pull mistral
   ```
3. Run the ingestion utility to embed the corpus:
   ```bash
   cd backend
   python -m app.cli.rag_ingest --source-dir data/srd --recreate
   ```
4. The resulting Chroma vector store persists in `backend/data/vectors/` and will be used automatically by the backend.

## License & Attributions

Use only SRD-compatible content and follow the Open Game License when adding rule text or mechanics. Provide attribution to Wizards of the Coast where required.
