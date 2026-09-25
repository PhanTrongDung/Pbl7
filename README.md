# PBL7 - Legal AI Platform

A legal AI platform built to support retrieval, management, and analysis of Vietnamese legal documents using a Retrieval-Augmented Generation (RAG) approach.

## Overview
This project aims to help users search legal documents, ask questions in natural language, summarize legal texts, compare regulatory sources, and obtain answers grounded in authoritative legal references.

The system combines:
- FastAPI backend
- SQLAlchemy ORM
- MySQL database
- React frontend
- RAG-based retrieval pipeline
- LLM-powered answer generation
- Legal document collection and processing workflow

## Project goals
- Search legal documents using natural language
- Return answers with citations to relevant provisions
- Summarize and compare legal documents
- Collect and manage law-related data from official sources
- Reduce hallucination by grounding responses in retrieved actual legal text

## Main architecture

```text
Frontend (React/Vite)
        ↓
Backend (FastAPI)
        ↓
Database (MySQL)
        ↓
Vector Database (Qdrant)
        ↓
LLM / Gemini / Embedding models
        ↓
Legal data collection and document processing
```

## Repository structure

```text
Pbl7/
├── README.md
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── config/
│   │   ├── core/
│   │   ├── crawler/
│   │   ├── database/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── docs/
├── data/
└── .gitignore
```

## Tech stack
- Python 3.11
- FastAPI
- SQLAlchemy
- MySQL
- Pydantic
- React + Vite
- Qdrant (planned)
- Gemini / LLM integration (planned)
- RAG workflow (planned)

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/PhanTrongDung/Pbl7.git
cd Pbl7
```

### 2. Create a virtual environment

```bash
cd backend
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the example file and update values if needed:

```bash
copy .env.example .env
```

### 5. Run backend

```bash
python main.py
```

Then open:
- Backend docs: http://localhost:8000/docs
- API root: http://localhost:8000

### 6. Run frontend

```bash
cd ../frontend
npm install
npm run dev
```

Then open:
- Frontend: http://localhost:5173

## API modules
Current starter endpoints include:
- /api/v1/health
- /api/v1/register
- /api/v1/login
- /api/v1/chat
- /api/v1/search
- /api/v1/summary
- /api/v1/compare
- /api/v1/sync-laws

## Development roadmap

### Phase 1: foundation
- Project structure setup
- Backend skeleton
- API routing
- Database configuration

### Phase 2: legal data pipeline
- Data collection crawler
- PDF processing
- Document chunking
- Metadata extraction

### Phase 3: retrieval layer
- Embedding generation
- Vector storage
- Semantic document retrieval

### Phase 4: RAG engine
- Prompt engineering
- Answer generation
- Citation extraction
- Response validation

### Phase 5: product features
- Dashboard
- Document library
- Legal chat
- Search and comparison tools
- Admin panel

## Notes
This repository is currently in an early-stage starter structure and is intended to be extended into a complete legal AI application.

## License
This project is for academic and learning purposes as part of the PBL7 project.
