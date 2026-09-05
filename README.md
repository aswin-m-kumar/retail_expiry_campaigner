# Retail Expiry Campaigner

Track retail products approaching expiry and trigger targeted campaigns.

## Project layout

```
.
├── backend/        FastAPI API (routers/, main.py)
├── frontend/       Streamlit app (app.py, pages/)
├── .venv/          Python virtual environment (shared)
└── agents.md       Developer/agent instructions
```

## Prerequisites

- Python 3.13
- Node not required (Streamlit serves the frontend)

## Setup

1. Create and activate the virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   (Or on Windows: `.venv\Scripts\activate`)

2. Install backend dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

3. Install frontend dependencies:

   ```bash
   pip install -r frontend/requirements.txt
   ```

## Running

### Backend (from `backend/`)

```bash
uvicorn main:app --reload
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Frontend (from `frontend/`)

```bash
streamlit run app.py
```

- App: http://localhost:8501

## Configuration

- Backend: `frontend/src/config.py` holds the `API_BASE_URL` used to reach the API.
- Streamlit options live in `frontend/.streamlit/config.toml`.