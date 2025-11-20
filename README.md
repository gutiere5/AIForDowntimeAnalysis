# AIForDowntimeAnalysis

A web application for analyzing downtime using AI.

## Project Structure

- `backend/`: Python FastAPI backend for AI analysis.
- `frontend/`: React-based frontend interface.

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.10 or higher)

## Getting Started

### Backend

1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --reload`

### Frontend

1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

## Seeding the Database

To seed the ChromaDB database with sample log data, run the following command from the `backend/` directory:

```bash
python -m vector_chroma_db.seed_database
```

## Features

- AI-powered downtime analysis
- Interactive chat interface

## License

MIT