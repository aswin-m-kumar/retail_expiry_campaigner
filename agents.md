# Retail Expiry Campaigner — Agent & Developer Guide

## 1. Overview

An intelligent retail campaign agent that scans inventory nearing expiry and decides, per matching customer, whether to send a plain **notification** or a tailored **offer** (discount/perk) — weighing purchase frequency, loyalty, and urgency before acting. Decisions and reasoning are logged and displayed on Owner and Customer dashboards.

**Core Stack:**
- **Backend API**: FastAPI (`backend/`)
- **Agent Engine**: Python deterministic scoring + Claude API (Anthropic / Ollama) for reasoning text generation (`backend/agent.py`)
- **Database**: Supabase / Postgres (`backend/db.py`)
- **Frontend**: Streamlit (`frontend/`)
- **Environment**: Shared Python 3.13 venv at project root (`.venv`)

---

## 2. Current Project Position & Status

### What is Currently Implemented
- [x] **Repository Structure**: Scaffolding complete with separate `backend/` (FastAPI) and `frontend/` (Streamlit).
- [x] **Shared Virtual Environment**: Initialized at `.venv/` (gitignored).
- [x] **Backend Baseline**: `backend/main.py` initialized with FastAPI and `backend/routers/health.py` mounted.
- [x] **Frontend Baseline**: `frontend/app.py` entrypoint with initial metric cards, page skeletons (`1_Inventory.py`, `2_Campaigns.py`), and config (`frontend/src/config.py`).

### Current Position & Next Implementation Steps
1. **Dependencies & Environment Setup**:
   - Add `supabase`, `anthropic`, `python-dotenv` to `backend/requirements.txt` and install into `.venv`.
   - Setup root `.env` (`SUPABASE_URL`, `SUPABASE_KEY`, `ANTHROPIC_API_KEY`).
2. **Database Provisioning (Supabase / Postgres)**:
   - Create tables: `user`, `items`, `inventory`, `purchases`, `notifications`, `offers`.
3. **Seed Data Script (`backend/seed.py`)**:
   - Generate realistic retail mock data (customers, items with perishability tiers, expiring inventory batches, past purchases) and seed Supabase.
4. **Data Access Layer (`backend/db.py`)**:
   - Supabase client initialization, typed CRUD helpers, and computed queries (e.g. `days_to_expiry`).
5. **Configuration & Tunable Parameters (`backend/config.py`)**:
   - Define expiry thresholds, perishability weights, affinity lookback window, and discount bands.
6. **Agent Engine (`backend/agent.py`)**:
   - Implement scoring functions (`urgency`, `affinity`, `would_buy_anyway`), deterministic decision surface, Claude prompt for reasoning copy, and `run_campaign()` orchestrator.
7. **Backend API Endpoints (`backend/routers/`)**:
   - Create routers to trigger campaign runs, query expiring inventory, and fetch notification/offer logs.
8. **Streamlit UI Integration (`frontend/`)**:
   - Implement Owner Dashboard (expiring inventory, run campaign trigger, aggregate metrics).
   - Implement Customer View (user switcher, received notifications & offers).
   - Implement Agent Log View (transparent scoring table, decisions, and Claude reasoning).

---

## 3. Project File Structure

Customized to the current decoupled `backend/` + `frontend/` project layout:

```
retail_expiry_campaigner/
├── .env                     # Supabase & Anthropic credentials (SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY)
├── .venv/                   # Shared Python virtual environment
├── agents.md                # Agent specification and developer guide
├── README.md                # Project documentation and quickstart
│
├── backend/                 # FastAPI service & Agent execution engine
│   ├── main.py              # FastAPI entrypoint (mounts routers, CORS middleware)
│   ├── config.py            # Thresholds, weights, strategy bands (tunable constants)
│   ├── db.py                # Supabase client + typed table read/write helpers
│   ├── agent.py             # Scoring pipeline, decision function, Claude reasoning call, writes result
│   ├── seed.py              # One-off script: generates realistic dataset & seeds Supabase
│   ├── requirements.txt     # fastapi, uvicorn, pydantic, supabase, anthropic, python-dotenv
│   └── routers/             # API routers
│       ├── health.py        # Health check (/health)
│       ├── inventory.py     # Expiring inventory query endpoints
│       ├── campaigns.py     # Campaign run trigger & execution log endpoints
│       ├── notifications.py # Notification retrieval endpoints
│       └── offers.py        # Offer retrieval endpoints
│
└── frontend/                # Streamlit UI
    ├── app.py               # Streamlit entrypoint — Owner / Customer / Agent Log views
    ├── requirements.txt     # streamlit, pandas, numpy, requests
    ├── pages/               # Multipage Streamlit views
    │   ├── 1_Inventory.py   # Expiring inventory monitor
    │   └── 2_Campaigns.py   # Active campaigns & trigger controls
    └── src/
        └── config.py        # Frontend configuration (API_BASE_URL)
```

### Module Responsibilities
- `backend/db.py` — No business or scoring logic; pure CRUD and query wrappers per table.
- `backend/config.py` — Every magic number (thresholds, weights, discount bands) in one auditable location.
- `backend/agent.py` — All agent reasoning: scoring → strategy decision → Claude reasoning copy → write to DB.
- `backend/routers/` — Exposes data and campaign triggers via REST endpoints.
- `frontend/` — Pure presentation layer; reads via API / DB and triggers `agent.run_campaign()`.

---

## 4. Database Tables (Supabase / Postgres)

### `user`
| Column | Type | Notes |
|---|---|---|
| `user_id` | uuid, PK | default `gen_random_uuid()` |
| `name` | text, not null | |
| `role` | text, not null | CHECK IN ('customer','owner') |
| `join_date` | date, not null | |
| `visit_frequency_per_month` | numeric, not null | ≥ 0 |
| `loyalty_tier` | text, not null | CHECK IN ('new','regular','vip') |
| `avg_basket_value` | numeric, not null | ≥ 0 |
| `discount_sensitivity` | text, not null | CHECK IN ('responsive','neutral','insensitive') |

### `items`
| Column | Type | Notes |
|---|---|---|
| `item_id` | uuid, PK | |
| `name` | text, not null | |
| `category` | text, not null | |
| `unit_cost` | numeric, not null | > 0 |
| `mrp` | numeric, not null | > 0, CHECK `mrp >= unit_cost` |
| `perishability_tier` | text, not null | CHECK IN ('high','med','low') |

### `inventory`
| Column | Type | Notes |
|---|---|---|
| `inventory_id` | uuid, PK | |
| `item_id` | uuid, FK → `items.item_id`, not null | ON DELETE CASCADE |
| `batch_no` | text, not null | |
| `stock_qty` | int, not null | ≥ 0 |
| `expiry_date` | date, not null | |

> **Note on `days_to_expiry`:** Not stored as a column — computed at query time as `expiry_date - CURRENT_DATE` to prevent stale values.

### `purchases`
| Column | Type | Notes |
|---|---|---|
| `purchase_id` | uuid, PK | |
| `user_id` | uuid, FK → `user.user_id`, not null | ON DELETE CASCADE |
| `item_id` | uuid, FK → `items.item_id`, not null | ON DELETE CASCADE |
| `purchased_at` | timestamptz, not null | |
| `price_paid` | numeric, not null | ≥ 0 |
| `discount_applied` | numeric, not null default 0 | 0–100 |

### `notifications`
| Column | Type | Notes |
|---|---|---|
| `notification_id` | uuid, PK | |
| `user_id` | uuid, FK → `user.user_id`, not null | ON DELETE CASCADE |
| `inventory_id` | uuid, FK → `inventory.inventory_id`, not null | ON DELETE CASCADE |
| `message` | text, not null | |
| `reasoning_text` | text, not null | Claude-generated |
| `created_at` | timestamptz, not null default now() | |

### `offers`
| Column | Type | Notes |
|---|---|---|
| `offer_id` | uuid, PK | |
| `user_id` | uuid, FK → `user.user_id`, not null | ON DELETE CASCADE |
| `inventory_id` | uuid, FK → `inventory.inventory_id`, not null | ON DELETE CASCADE |
| `strategy_type` | text, not null | CHECK IN ('small_perk','tiered_discount','aggressive_discount') |
| `discount_pct` | numeric, not null | 0–100 |
| `reasoning_text` | text, not null | Claude-generated |
| `urgency_score` | numeric, not null | 0–1 |
| `affinity_score` | numeric, not null | 0–1 |
| `created_at` | timestamptz, not null default now() | |

### Cross-table Constraint (Enforced in `agent.py`)
For a given `(user_id, inventory_id)` pair evaluated during a campaign run, a row is written to **at most one of** `notifications` or `offers` — never both. This either/or outcome is the agent's core decision.

---

## 5. Functions & Interfaces

### `backend/config.py` (Constants, no functions)
- `EXPIRY_WINDOW_DAYS` — inventory scanned if `days_to_expiry <= this`
- `URGENCY_WEIGHTS` — per `perishability_tier` multiplier (high, med, low)
- `AFFINITY_LOOKBACK_DAYS` — purchase history window for affinity calculation
- `DISCOUNT_BANDS` — dict mapping `strategy_type` → `(min_pct, max_pct)`
- `WOULD_BUY_ANYWAY_THRESHOLD` — score above which the agent chooses `notify` only

### `backend/db.py`
- `get_client() -> Client` — cached Supabase client
- `get_expiring_inventory(window_days: int) -> list[dict]` — joins `inventory` + `items`, filters by computed `days_to_expiry`
- `get_users(role: str = None) -> list[dict]` — fetches users, optionally filtered by role
- `get_purchase_history(user_id: str) -> list[dict]` — past purchases within lookback window
- `insert_notification(row: dict) -> None` — records a sent notification
- `insert_offer(row: dict) -> None` — records a sent offer
- `get_notifications(user_id: str = None) -> list[dict]` — query notifications
- `get_offers(user_id: str = None) -> list[dict]` — query offers

### `backend/agent.py`
- `compute_urgency_score(inventory_row: dict) -> float`
  Normalizes `days_to_expiry` against `perishability_tier` weight → `0.0–1.0`.
- `compute_affinity_score(user_id: str, category: str) -> float`
  Purchase frequency in that category within `AFFINITY_LOOKBACK_DAYS`, normalized → `0.0–1.0`.
- `compute_would_buy_anyway_score(user_row: dict) -> float`
  Combines `loyalty_tier`, `visit_frequency_per_month`, and `discount_sensitivity`.
- `decide_strategy(urgency: float, affinity: float, would_buy_anyway: float) -> tuple[str, float]`
  Deterministic decision function → `(strategy_type_or_'notify', discount_pct)`.
  A weighted-score decision surface rather than brittle hardcoded `if/else` checks.
- `generate_reasoning_text(user_row: dict, item_row: dict, scores: dict, strategy: str) -> str`
  Single Claude API call; feeds computed scores + strategy + product/customer details,
  returning 2–3 sentences of customer-facing copy and reasoning rationale. Scores decide *what*;
  Claude writes *why*, in natural language.
- `run_campaign() -> list[dict]`
  Orchestrates: fetch expiring inventory → match users → score → decide →
  generate reasoning copy → write to `notifications` or `offers` → return log of
  all decisions made (for Owner & Agent Log views).

### Frontend Renderers (`frontend/app.py` or pages)
- `render_owner_tab()` — Expiring inventory table, "Run Campaign Agent" button, merged notifications/offers, aggregate metrics (discount spend, notify vs. offer split).
- `render_customer_tab()` — User selector, displaying that user's notifications + offers.
- `render_agent_log_tab()` — Raw scored table: every evaluated `(user, inventory)` pair, scores, decision, and Claude reasoning — full transparency view.

---

## 6. Decision Flow (per expiring inventory × matching user)

```
1. urgency = compute_urgency_score(inventory_row)
2. affinity = compute_affinity_score(user_id, item.category)
3. would_buy_anyway = compute_would_buy_anyway_score(user_row)
4. strategy, discount_pct = decide_strategy(urgency, affinity, would_buy_anyway)
5. if strategy == 'notify':
       text = generate_reasoning_text(...)
       insert_notification(...)
   else:
       text = generate_reasoning_text(...)
       insert_offer(...)  # strategy in {small_perk, tiered_discount, aggressive_discount}
```

---

## 7. Developer Commands & Conventions

### Shared Virtual Environment
- Path: `.venv/` at project root
- Activation (PowerShell / Windows): `.venv\Scripts\Activate.ps1`
- Activation (Bash / POSIX): `source .venv/bin/activate`

### Backend (from `backend/`)
- Run server: `..\.venv\Scripts\uvicorn main:app --reload` (Windows) or `../.venv/bin/uvicorn main:app --reload` (POSIX)
- Install deps: `..\.venv\Scripts\pip install -r requirements.txt`
- Interactive API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Frontend (from `frontend/`)
- Run Streamlit: `..\.venv\Scripts\streamlit run app.py` (Windows) or `../.venv/bin/streamlit run app.py` (POSIX)
- Install deps: `..\.venv\Scripts\pip install -r requirements.txt`
- Dashboard URL: http://localhost:8501

### Core Conventions
- Shared venv at project root (`.venv/`) — already gitignored.
- Backend routers live in `backend/routers/` and are registered in `backend/main.py`.
- Scoring logic is strictly deterministic and auditable; Claude/LLM is used solely for natural-language reasoning text and campaign copy generation.
- Clear separation of concerns: `db.py` handles database queries, `config.py` holds tunable parameters, `agent.py` contains decision logic, and `frontend/` handles rendering and user interaction.