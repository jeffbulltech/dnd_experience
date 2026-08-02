# Dungeons & Dragons AI Game Master

An immersive single-player Dungeons & Dragons experience powered by a FastAPI backend, a React + Tailwind frontend, and local large language models running through Ollama. The system combines AI-driven storytelling with rule enforcement and stateful campaign management.

## Features

- **Adventure Selection**: Choose from pre-made adventures (Lost Mine of Phandelver, Dragon of Icespire Peak, Curse of Strahd) or create custom adventures
- **AI Game Master**: Powered by Ollama with a built-in "GM Screen" that keeps hidden information (monster stats, secrets, loot locations) private
- **Character Management**: Create characters using the guided builder or select existing characters for campaigns
- **Campaign Management**: Create and manage multiple campaigns with persistent game state
- **Interactive Chat**: Real-time conversation with the AI GM with auto-scrolling chat interface
- **Combat Tracker**: Manage encounters, initiative, and combat participants
- **Dice Rolling**: Integrated dice roller with history tracking
- **Inventory Management**: Track character items and equipment
- **RAG-Enhanced**: Uses Retrieval-Augmented Generation with 5e SRD rules for accurate rule enforcement

## Project Structure

```
backend/
├── app/                # FastAPI application modules
│   ├── api/           # API route handlers
│   ├── models/        # SQLAlchemy database models
│   ├── services/      # Business logic (AI GM, RAG, combat, etc.)
│   └── schemas/       # Pydantic validation schemas
├── data/
│   ├── adventures/    # Pre-made adventure templates (JSON)
│   ├── srd/           # SRD reference documents
│   └── vectors/       # Chroma vector database storage
├── migrations/        # Alembic database migrations
└── requirements.txt   # Python dependencies
frontend/
├── src/
│   ├── components/    # React components (Chat, CharacterSheet, etc.)
│   ├── hooks/         # Custom React hooks
│   ├── pages/         # Page components
│   └── services/      # API client
├── package.json       # Frontend dependencies & scripts
└── tailwind.config.js # UI configuration
```

## Getting Started

### Prerequisites

- Python 3.10+ 
- Node.js 18+ and npm
- PostgreSQL (running locally or remote)
- Ollama (for local LLM inference)

### Setup Steps

1. **Clone the repository and create a Python virtual environment:**
   ```bash
   python -m venv dnd  # or .venv
   source dnd/bin/activate  # On Windows: dnd\Scripts\activate
   ```

2. **Set up environment variables:**
   Create a `.env` file in the project root (or export variables manually):
   ```bash
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/dnd_ai
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=mistral
   SECRET_KEY=change-me-to-a-secure-random-string
   ```

3. **Install backend dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Set up the database:**
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Install and start Ollama:**
   - Install Ollama from https://ollama.ai
   - Start Ollama service
   - Pull the required model:
     ```bash
     ollama pull mistral
     ```

6. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

7. **Start the backend server** (from project root):
   ```bash
   source dnd/bin/activate  # if not already activated
   uvicorn backend.app.main:app --reload
   ```

8. **Start the frontend server** (in a separate terminal):
   ```bash
   cd frontend
   npm run dev
   ```

9. **Access the app:**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

### Development

For convenience, you can run both the frontend and backend concurrently from the project root. This script automatically uses the `uvicorn` inside your `.venv`.

1. Install root dependencies (once):
   ```bash
   npm install
   ```
2. Start both servers:
   ```bash
   npm run dev
   ```
   This will show interleaved logs from both services with different colors.

### Authentication

- Register a new account via the UI (or `POST /api/auth/register`) to create a user.
- Login with your username and password to obtain an access token.
- All protected requests require `Authorization: Bearer <token>`. The frontend stores the token client-side and automatically attaches it to requests.

### Creating Your First Campaign

1. **Register/Login** to your account
2. **Create a Campaign:**
   - Click "New Campaign" button
   - Choose an adventure:
     - Select a pre-made adventure (Lost Mine of Phandelver, Dragon of Icespire Peak, or Curse of Strahd)
     - Or choose "Create Custom Adventure" for an AI-generated story
   - Enter a campaign name and optional premise
   - Click "Create Campaign"
3. **Select a Character:**
   - When you enter the campaign, you'll see a welcome message from the AI Game Master
   - Select one of your existing characters or create a new one using the Character Builder
4. **Start Playing:**
   - Chat with the AI Game Master to begin your adventure
   - Use the dice roller, combat tracker, and inventory as needed

## Key Features Explained

### The Game Master Screen

The AI Game Master maintains a figurative "GM Screen" that keeps hidden information private from players:

- **Monster Stats**: Never reveals exact HP, AC, or special abilities until discovered
- **Maps & Secrets**: Only describes what characters can observe, not hidden doors or traps
- **NPC Secrets**: Hidden agendas and motivations stay hidden until discovered
- **Treasure Locations**: Loot is described dramatically as found, not in advance
- **Encounter Details**: Planned encounters and difficulty remain hidden
- **Hidden Rolls**: Perception, Deception, and trap saves are kept private

This preserves mystery, tension, and the sense of discovery that makes D&D engaging.

### Adventure Templates

Pre-made adventures include seed content that guides the AI GM:
- **Lost Mine of Phandelver**: Classic starter adventure (Levels 1-5)
- **Dragon of Icespire Peak**: Frontier adventure (Levels 1-6)
- **Curse of Strahd**: Gothic horror campaign (Levels 1-10)

Custom adventures let the AI GM create unique stories tailored to your campaign premise.

### Character Selection

Before the story begins, you can select which character to use for the campaign. Once you send your first message, the character is locked to that campaign. This ensures continuity and prevents character swapping mid-adventure.

## Next Steps / Roadmap

- Support shared campaigns and multiple players
- Extend combat tooling with turn advancement, area effects, and monster presets
- Add character sheet editing (stats, skills, spell slots) with auto-sync
- Implement automated testing/CI covering API auth flows and frontend integration
- Add more pre-made adventure templates
- Support for custom adventure templates

## Preparing the RAG Knowledge Base

The system uses Retrieval-Augmented Generation (RAG) to provide accurate D&D 5e rule references. To set up the knowledge base:

1. **Place SRD documents** in `backend/data/srd/`:
   - Use only SRD-licensed content (System Reference Document)
   - Supported formats: Markdown, plain text
   - Organize by topic (combat, spells, equipment, etc.)

2. **Ensure Ollama is running** with the configured model:
   ```bash
   ollama pull mistral
   ```

3. **Run the ingestion utility** to embed the corpus:
   ```bash
   cd backend
   source ../dnd/bin/activate  # if not already activated
   python -m app.cli.rag_ingest --source-dir data/srd --recreate
   ```

4. **Verify the vector store**:
   - The Chroma vector database will be created at `backend/data/vectors/`
   - This is used automatically by the backend for rule lookups during gameplay

The RAG system helps the AI GM provide accurate rule references and maintain consistency with official 5e rules.

## License & Attributions

Use only SRD-compatible content and follow the Open Game License when adding rule text or mechanics. Provide attribution to Wizards of the Coast where required.
