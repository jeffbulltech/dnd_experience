# Backend - D&D AI Game Master

## Overview

This FastAPI backend powers the single-player Dungeons & Dragons experience. It exposes REST and WebSocket endpoints for character management, campaign orchestration, dice rolling, combat resolution, and AI-driven storytelling. Core services integrate with Ollama for on-device large language models and with a vector database for retrieval-augmented generation (RAG) using the 5e SRD.

## Key Components

- `app/main.py`: FastAPI application entrypoint with CORS configuration.
- `app/api/`: Route handlers grouped by domain (characters, campaigns, chat, dice, combat, game state).
- `app/services/`: Business logic for AI GM, combat, rules, RAG, and integrations.
- `app/models/`: SQLAlchemy models (to be implemented).
- `app/schemas/`: Pydantic models used by the API.
- `app/utils/`: Cross-cutting utilities such as dice rolling.
- `data/`: SRD source material and persisted vector index storage.

## Getting Started

1. Create and activate a Python 3.10+ virtual environment at the repository root:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Set environment variables (see `.env.example`, coming soon) or export them directly:
   ```bash
   export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/dnd_ai
   export OLLAMA_BASE_URL=http://localhost:11434
   export SECRET_KEY=change-me
   ```
4. Run the development server:
   ```bash
   uvicorn app.main:app --reload --factory
   ```
5. Access interactive docs at `http://localhost:8000/docs`.

### Database Migrations

1. Generate a new migration after editing models:
   ```bash
   alembic revision --autogenerate -m "describe change"
   ```
2. Apply migrations:
   ```bash
   alembic upgrade head
   ```
3. Downgrade (if necessary):
   ```bash
   alembic downgrade -1
   ```

## RAG Ingestion Workflow

1. Populate `backend/data/srd/` with SRD-compliant markdown or text files.
2. Ensure Ollama is running and the configured model is available:
   ```bash
   ollama pull mistral
   ```
3. Embed the corpus into Chroma:
   ```bash
   python -m app.cli.rag_ingest --source-dir backend/data/srd --recreate
   ```
4. Confirm the persisted vector store exists at `backend/data/vectors/`.

## Authentication

- Register users via `POST /api/auth/register` (email, username, display_name, password).
- Obtain tokens with `POST /api/auth/token` (form fields `username` and `password`).
- Include `Authorization: Bearer <token>` on protected requests. The `/api/auth/me` endpoint returns the current user.

## Next Steps

- Support shared campaigns and player roles.
- Auto-sync character sheet updates with encounter participants.
- Add automated test coverage for auth flows and client integrations.

### Running Tests

1. Install development dependencies (see `requirements.txt`).
2. Execute the unit test suite:
   ```bash
   pytest
   ```
