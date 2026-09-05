# Retail Expiry Campaigner — Agent Guide

## 1. High-Signal Architecture
- **Backend**: FastAPI (`backend/`) + Supabase/Postgres.
- **Frontend**: Streamlit (`frontend/`).
- **Core Logic**: `backend/agent.py` contains the deterministic scoring pipeline (Urgency $\rightarrow$ Affinity $\rightarrow$ Decision) and LLM-based reasoning/chat.
- **Data Flow**: `backend/db.py` (CRUD) $\rightarrow$ `backend/agent.py` (Logic) $\rightarrow$ `backend/routers/` (API) $\rightarrow$ `frontend/` (UI).
- **Config**: Tunable parameters (weights, thresholds) are in `backend/config.py`.
- **Database**: Sequential SQL migrations in `migrations/` (0001-0006). Manual updates should edit these files directly.

## 2. Developer Commands
### Environment
- **Venv**: Shared at root `.venv/`.
- **Activation**: `source .venv/bin/activate` (POSIX) / `.venv\Scripts\activate` (Windows).

### Backend
- **Run**: `uvicorn main:app --reload` (from `backend/`)
- **Deps**: `pip install -r backend/requirements.txt`
- **Docs**: `http://localhost:8000/docs`

### Frontend
- **Run**: `streamlit run app.py` (from `frontend/`)
- **Deps**: `pip install -r frontend/requirements.txt`

## 3. Critical Implementation Details
- **Campaign Logic**: For each `(user, inventory)` pair, the agent writes to **either** `notifications` or `offers`, never both.
- **AI Agents**:
    - **Owner**: Intent parsing $\rightarrow$ Inventory analysis/update $\rightarrow$ Natural language answer.
    - **Customer**: Live re-scoring of offers on-demand (read-only, does not write to DB).
- **Constraints**: 
    - `days_to_expiry` is computed at query time, not stored.
    - No business logic in `backend/db.py`.
    - LLMs are used for **text generation and intent parsing**, not for the core decision scoring.
