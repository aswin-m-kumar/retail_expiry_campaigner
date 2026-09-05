# Retail Expiry Campaigner

## Project layout

- `backend/` — FastAPI app (uvicorn `main:app`, docs at `/docs`), core app files at backend root
- `frontend/` — Streamlit app (`app.py`), multipage under `frontend/pages/`

## Commands

### Backend (from `backend/`)
- Run: `.venv/bin/uvicorn main:app --reload` (venv lives at project root)
- Install deps: `../.venv/bin/pip install -r requirements.txt`

### Frontend (from `frontend/`)
- Run: `../.venv/bin/streamlit run app.py`
- Install deps: `../.venv/bin/pip install -r requirements.txt`

## Conventions

- Shared venv at project root (`.venv/`) — already gitignored
- Backend routers live in `backend/routers/` and are registered in `backend/main.py`