# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

# Code Architecture

This project ("Downtime Detective") is an AI-powered downtime analysis application consisting of a Python FastAPI backend and a React frontend.

## Backend (`backend/`)

The backend uses a multi-agent architecture to process user queries about manufacturing downtime events.

- **Entry Point:** `backend/main.py` initializes the FastAPI app and includes the API router.
- **Agents (`backend/agents/`):**
  - **`MainAgent` (`main_agent.py`):** The primary controller. It receives a query and coordinates the sub-agents.
  - **`AgentOrchestrator` (`agent_orchestrator.py`):** Uses an LLM to parse natural language queries into a structured JSON execution plan (e.g., "Retrieve logs from last week" -> "Analyze top causes").
  - **`AgentRetrieval` (`agent_retrieval.py`):** Interfaces with ChromaDB to fetch relevant downtime logs or known issues using metadata filters and semantic search.
  - **`AgentAnalysis` (`agent_analysis.py`):** Performs deterministic analysis on retrieved data (e.g., calculating totals, clustering reasons, aggregating by line) using `pandas` and `sklearn`.
  - **`AgentSynthesis` (`agent_synthesis.py`):** Uses an LLM to generate a natural language response based on the analysis results and conversation history.
- **Data Repositories:**
  - **Vector DB (`backend/repositories/vector_chroma_db/`):** ChromaDB stores embeddings of downtime logs for semantic search.
  - **SQL DB (`backend/repositories/sql_databases/`):** SQLite stores conversation history and structured "Known Issues" data.
- **API:**
  - Endpoints are defined in `backend/api/endpoints/`.
  - `agent.py` handles the main streaming chat endpoint (`/agent/query`).

## Frontend (`frontend/`)

The frontend is a React application built with Vite.

- **State Management:** Uses React `useState` and `useImmer` for managing chat history and UI state.
- **Communication:** Uses Server-Sent Events (SSE) to consume the streaming response from the backend agent (handled in `src/assets/utils.js`).
- **Components:**
  - `Chatbot.jsx`: Main chat interface.
  - `SidePanel.jsx`: Manages conversation history and global actions.
  - `KnownIssuesModal.jsx`: Interface for CRUD operations on the "Known Issues" database.

# Development Workflow

## Backend

The backend requires a Python environment (v3.10+).

**Installation:**
```bash
cd backend
pip install -r requirements.txt
```

**Running the Server:**
It is recommended to run the server from the repository root to ensure package imports (`backend.xyz`) resolve correctly.
```bash
# From the repository root
uvicorn backend.main:app --reload --port 8000
```

**Seeding the Database:**
To populate ChromaDB with sample downtime logs:
```bash
# From the repository root
python -m backend.repositories.vector_chroma_db.run_and_seed_db
```

**Injecting Build Info:**
To generate the `.env.build` file with commit hash and build date:
```bash
# From the backend directory
python inject_build_info.py
```

## Frontend

The frontend requires Node.js (v18+).

**Installation:**
```bash
cd frontend
npm install
```

**Running the Development Server:**
```bash
cd frontend
npm run dev
```

**Linting:**
```bash
cd frontend
npm run lint
```

# Architecture Notes for Code Changes

- **Agent Modifications:** When adding capabilities to the AI, you typically need to update:
  1. `AgentOrchestrator` prompt/schema to teach the planner about the new task.
  2. `AgentAnalysis` or `AgentRetrieval` to implement the logic.
  3. `MainAgent` to route the new task type to the correct agent.
- **Data Model:** `downtime_logs` are immutable event logs stored in ChromaDB. `known_issues` are editable solution documents stored in both SQLite (for CRUD) and ChromaDB (for retrieval).
- **Streaming:** The backend streams responses token-by-token. Any new agent response logic must yield chunks compatible with the frontend's SSE parser.
