# Retail Expiry Campaigner — Agent & Developer Guide

## 1. Overview

An intelligent retail campaign agent that scans inventory nearing expiry and decides, per matching customer, whether to send a plain **notification** or a tailored **offer** (discount/perk) — weighing purchase frequency, loyalty, and urgency before acting. Decisions and reasoning are logged and displayed on Owner and Customer dashboards. In addition, interactive chat-based AI agent tabs provide real-time inventory management for the store owner and on-demand live deal discovery for customers.

**Core Stack:**
- **Backend API**: FastAPI (`backend/`)
- **Agent Engine**: Python deterministic scoring + Claude API (Anthropic / Ollama) for reasoning copy and conversational intent parsing (`backend/agent.py`)
- **Database**: Supabase / Postgres with sequential SQL migrations (`migrations/`, `backend/db.py`)
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
2. **Database Migrations (`migrations/`)**:
   - Create SQL migration files `0001_create_user.sql` through `0006_create_offers.sql` and apply sequentially in Supabase SQL editor or CLI.
3. **Seed Data Script (`backend/seed.py`)**:
   - Generate realistic retail mock data (customers, items with perishability tiers, expiring inventory batches, past purchases) and seed Supabase.
4. **Data Access Layer (`backend/db.py`)**:
   - Supabase client initialization, typed CRUD helpers, computed queries (`days_to_expiry`), and inventory update helpers.
5. **Configuration & Tunable Parameters (`backend/config.py`)**:
   - Define expiry thresholds, perishability weights, affinity lookback window, and discount bands.
6. **Agent Engine (`backend/agent.py`)**:
   - Implement scoring functions (`urgency`, `affinity`, `would_buy_anyway`), deterministic decision surface, Claude prompt for reasoning copy, and `run_campaign()` orchestrator.
   - Implement conversational AI handlers for Owner (`parse_owner_query`, `analyze_inventory_health`, `apply_inventory_update`, `answer_owner_query`) and Customer (`parse_customer_query`, `answer_availability`, `get_live_offers_for_user`, `answer_customer_query`).
7. **Backend API Endpoints (`backend/routers/`)**:
   - Create routers to trigger campaign runs, query expiring inventory, execute chat queries, and fetch notification/offer logs.
8. **Streamlit UI Integration (`frontend/`)**:
   - Implement Owner Dashboard (expiring inventory, run campaign trigger, aggregate metrics).
   - Implement Customer View (user switcher, received notifications & offers).
   - Implement Agent Log View (transparent scoring table, decisions, and Claude reasoning).
   - Implement Owner AI Agent Tab (interactive stock analytics and confirmed inventory updates).
   - Implement Customer AI Agent Tab (conversational availability and on-demand live offers).

---

## 3. Project File Structure

Customized to the current decoupled `backend/` + `frontend/` project layout:

```
retail_expiry_campaigner/
├── .env                     # Supabase & Anthropic credentials (SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY)
├── .venv/                   # Shared Python virtual environment
├── agents.md                # Agent specification and developer guide
├── README.md                # Setup, project documentation, and user-flow Mermaid diagram
│
├── migrations/              # SQL migration files, applied in order (parents before children)
│   ├── 0001_create_user.sql
│   ├── 0002_create_items.sql
│   ├── 0003_create_inventory.sql
│   ├── 0004_create_purchases.sql
│   ├── 0005_create_notifications.sql
│   └── 0006_create_offers.sql
│
├── backend/                 # FastAPI service & Agent execution engine
│   ├── main.py              # FastAPI entrypoint (mounts routers, CORS middleware)
│   ├── config.py            # Thresholds, weights, strategy bands (tunable constants)
│   ├── db.py                # Supabase client + typed table read/write helpers
│   ├── agent.py             # Scoring pipeline, decision function, Claude call, conversational AI
│   ├── seed.py              # One-off script: generates realistic dataset & seeds Supabase
│   ├── requirements.txt     # fastapi, uvicorn, pydantic, supabase, anthropic, python-dotenv
│   └── routers/             # API routers
│       ├── health.py        # Health check (/health)
│       ├── inventory.py     # Expiring inventory query & update endpoints
│       ├── campaigns.py     # Campaign run trigger & execution log endpoints
│       ├── chat.py          # Conversational agent query endpoints (owner/customer)
│       ├── notifications.py # Notification retrieval endpoints
│       └── offers.py        # Offer retrieval endpoints
│
└── frontend/                # Streamlit UI
    ├── app.py               # Streamlit entrypoint — Owner / Customer / Agent Log / AI Agent tabs
    ├── requirements.txt     # streamlit, pandas, numpy, requests
    ├── pages/               # Multipage Streamlit views (or unified tabs in app.py)
    │   ├── 1_Inventory.py   # Expiring inventory monitor
    │   └── 2_Campaigns.py   # Active campaigns & trigger controls
    └── src/
        └── config.py        # Frontend configuration (API_BASE_URL)
```

### Module Responsibilities
- `backend/db.py` — No business logic; pure CRUD and query wrappers per table.
- `backend/agent.py` — All reasoning lives here: deterministic scoring → decision → Claude copy → write, as well as conversational intent parsing and agent dialog.
- `backend/config.py` — Every magic number (thresholds, weights, discount bands) in one auditable place.
- `backend/routers/` — Exposes agent operations and DB data over REST endpoints for frontend consumption.
- `frontend/app.py` (or `frontend/pages/`) — Presentation only; reads from DB/API, displays dashboards, and triggers `agent.run_campaign()`.
- `migrations/` — Hand-authored SQL, one file per table, numbered in dependency order (FK targets before referencers) so they can be applied sequentially via Supabase SQL editor or CLI (`supabase db push`).

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

> **Note on `days_to_expiry`:** Not stored as a column — computed at query time as `expiry_date - CURRENT_DATE` to avoid staleness.

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

### Cross-table Constraint (Enforced in `agent.py`, not DB-level)
For a given `(user_id, inventory_id)` pair produced in one campaign run, a row is written to **at most one of** `notifications` / `offers` — never both. This is the agent's core either/or decision.

---

## 4.1 Migration Files

One SQL file per table, stored in `migrations/`, applied in numbered order (parents before children, so FKs never reference a table that does not exist yet). Each file is idempotent (`CREATE TABLE IF NOT EXISTS`) so re-running the set is safe.

**`migrations/0001_create_user.sql`**
```sql
CREATE TABLE IF NOT EXISTS "user" (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('customer','owner')),
  join_date DATE NOT NULL,
  visit_frequency_per_month NUMERIC NOT NULL CHECK (visit_frequency_per_month >= 0),
  loyalty_tier TEXT NOT NULL CHECK (loyalty_tier IN ('new','regular','vip')),
  avg_basket_value NUMERIC NOT NULL CHECK (avg_basket_value >= 0),
  discount_sensitivity TEXT NOT NULL CHECK (discount_sensitivity IN ('responsive','neutral','insensitive'))
);
```

**`migrations/0002_create_items.sql`**
```sql
CREATE TABLE IF NOT EXISTS items (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  unit_cost NUMERIC NOT NULL CHECK (unit_cost > 0),
  mrp NUMERIC NOT NULL CHECK (mrp > 0),
  perishability_tier TEXT NOT NULL CHECK (perishability_tier IN ('high','med','low')),
  CONSTRAINT mrp_covers_cost CHECK (mrp >= unit_cost)
);
```

**`migrations/0003_create_inventory.sql`**
```sql
CREATE TABLE IF NOT EXISTS inventory (
  inventory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
  batch_no TEXT NOT NULL,
  stock_qty INT NOT NULL CHECK (stock_qty >= 0),
  expiry_date DATE NOT NULL
);
```

**`migrations/0004_create_purchases.sql`**
```sql
CREATE TABLE IF NOT EXISTS purchases (
  purchase_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
  item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
  purchased_at TIMESTAMPTZ NOT NULL,
  price_paid NUMERIC NOT NULL CHECK (price_paid >= 0),
  discount_applied NUMERIC NOT NULL DEFAULT 0 CHECK (discount_applied BETWEEN 0 AND 100)
);
```

**`migrations/0005_create_notifications.sql`**
```sql
CREATE TABLE IF NOT EXISTS notifications (
  notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
  inventory_id UUID NOT NULL REFERENCES inventory(inventory_id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  reasoning_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**`migrations/0006_create_offers.sql`**
```sql
CREATE TABLE IF NOT EXISTS offers (
  offer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
  inventory_id UUID NOT NULL REFERENCES inventory(inventory_id) ON DELETE CASCADE,
  strategy_type TEXT NOT NULL CHECK (strategy_type IN ('small_perk','tiered_discount','aggressive_discount')),
  discount_pct NUMERIC NOT NULL CHECK (discount_pct BETWEEN 0 AND 100),
  reasoning_text TEXT NOT NULL,
  urgency_score NUMERIC NOT NULL CHECK (urgency_score BETWEEN 0 AND 1),
  affinity_score NUMERIC NOT NULL CHECK (affinity_score BETWEEN 0 AND 1),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Generation note:** If the schema changes, update the matching migration file directly rather than adding ad-hoc `ALTER TABLE` files, as there is no automatic migration-diffing tool wired in here.

---

## 5. Functions & Interfaces

### `backend/config.py` (Constants, no functions)
- `EXPIRY_WINDOW_DAYS` — inventory scanned if `days_to_expiry <= this`
- `URGENCY_WEIGHTS` — per `perishability_tier` multiplier (high, med, low)
- `AFFINITY_LOOKBACK_DAYS` — purchase history window for affinity calculation
- `DISCOUNT_BANDS` — dict mapping `strategy_type` → `(min_pct, max_pct)`
- `WOULD_BUY_ANYWAY_THRESHOLD` — score above which → notify only

### `backend/db.py`
- `get_client() -> Client` — cached Supabase client
- `get_expiring_inventory(window_days: int) -> list[dict]` — joins `inventory` + `items`, filters by computed `days_to_expiry`
- `get_users(role: str = None) -> list[dict]` — fetches users, optionally filtered by role
- `get_purchase_history(user_id: str) -> list[dict]` — past purchases within lookback window
- `insert_notification(row: dict) -> None` — records a sent notification
- `insert_offer(row: dict) -> None` — records a sent offer
- `get_notifications(user_id: str = None) -> list[dict]` — query notifications
- `get_offers(user_id: str = None) -> list[dict]` — query offers
- `update_inventory_stock(inventory_id: str, new_qty: int) -> dict` — update stock quantity

### `backend/agent.py`
#### Automated Campaign Pipeline:
- `compute_urgency_score(inventory_row: dict) -> float`
  Normalizes `days_to_expiry` against `perishability_tier` weight → `0.0–1.0`.
- `compute_affinity_score(user_id: str, category: str) -> float`
  Purchase frequency in that category within `AFFINITY_LOOKBACK_DAYS`, normalized → `0.0–1.0`.
- `compute_would_buy_anyway_score(user_row: dict) -> float`
  Combines `loyalty_tier`, `visit_frequency_per_month`, and `discount_sensitivity`.
- `decide_strategy(urgency: float, affinity: float, would_buy_anyway: float) -> tuple[str, float]`
  Deterministic decision function → `(strategy_type_or_'notify', discount_pct)`.
  Weighted-score decision surface rather than brittle hardcoded `if/else` checks.
- `generate_reasoning_text(user_row: dict, item_row: dict, scores: dict, strategy: str) -> str`
  Single Claude API call; feeds computed scores + strategy + product/customer context,
  returning 2–3 sentences of customer-facing copy and rationale. Scores decide *what*;
  Claude writes *why*, in prose.
- `run_campaign() -> list[dict]`
  Orchestrates: fetch expiring inventory → match users → score → decide →
  generate text → write to `notifications` or `offers` → return log of
  all decisions made (for Owner & Agent Log views).

#### Conversational AI Agent Functions (see §7):
- `parse_owner_query(query_text: str) -> dict` — Intent classifier & entity extractor for owner
- `analyze_inventory_health() -> list[dict]` — Stock velocity, days-of-stock-remaining, urgency flags
- `apply_inventory_update(parsed_action: dict) -> dict` — Validates constraints and updates inventory
- `answer_owner_query(query_text: str) -> str` — Orchestrates owner query handling
- `parse_customer_query(query_text: str) -> dict` — Intent classifier for customer
- `answer_availability(item_query: str) -> str` — Product availability query handler
- `get_live_offers_for_user(user_id: str) -> list[dict]` — Read-time live scoring without writing duplicate rows
- `answer_customer_query(query_text: str, user_id: str) -> str` — Orchestrates customer query handling

### Frontend Views (`frontend/app.py` or pages)
- `render_owner_tab()` — Expiring inventory table, "Run Campaign Agent" button, merged notifications+offers view, aggregate stats (discount spend, notify vs. offer split).
- `render_customer_tab()` — User picker, shows that user's notifications + offers.
- `render_agent_log_tab()` — Raw scored table: every evaluated `(user, inventory)` pair, scores, decision, reasoning — full transparency view.
- `render_owner_ai_agent_tab()` — Chat-based stock analysis and inventory control (see §7.1).
- `render_customer_ai_agent_tab()` — Chat-based availability lookup and live personal offers (see §7.2).

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

## 7. AI Agent Pages (Per Role)

Both pages are chat-style: a text input where the role asks a question in plain language, the agent parses intent, pulls the relevant DB rows, and answers — this is the "dynamic reasoning" layer surfaced directly to the user, distinct from the automated `run_campaign()` batch job in §6.

### 7.1 Owner AI Agent Page

**Purpose:** Inventory analysis + stock control, in conversation.

**Capabilities:**
- Analyze current stock: which items are low, which are overstocked relative to their sale velocity (derived from `purchases`), which batches are expiring soonest.
- Surface item stock details on request: quantity, batch, expiry, perishability tier, cost/margin (`mrp - unit_cost`).
- Update inventory directly from the chat: restock a batch, adjust `stock_qty`, add a new batch, correct an expiry date — agent parses the instruction, confirms the parsed action back to the owner, then writes to `inventory` on confirmation.
- Explain *why* a stock level or expiry is a concern (ties into `compute_urgency_score` from §5, ensuring reasoning is consistent with the campaign agent).

**Functions (in `agent.py`):**
- `parse_owner_query(query_text: str) -> dict`
  Claude call — classifies intent: `{lookup | update | analysis}` and extracts entities (item name, batch, quantity, field to change).
- `analyze_inventory_health() -> list[dict]`
  Computes per-item: stock velocity (units sold / day, from `purchases`), days-of-stock-remaining, urgency flag. Deterministic, reused by both the chat answer and the Owner tab summary stats.
- `apply_inventory_update(parsed_action: dict) -> dict`
  Validates parsed action against constraints (§4 CHECKs — e.g. `stock_qty >= 0`), writes to `inventory` via `db.py`, returns a confirmation record. Never writes without an explicit owner confirmation step in the UI.
- `answer_owner_query(query_text: str) -> str`
  Orchestrates: `parse_owner_query` → routes to `analyze_inventory_health` or `apply_inventory_update` or a direct `db.py` lookup → Claude call to phrase the final natural-language answer over the retrieved data.

**UI (`render_owner_ai_agent_tab`):**
- Chat input + conversation history (session state, not persisted).
- Any proposed inventory update is shown as a diff ("`stock_qty: 40 → 55`") with a Confirm/Cancel action before it touches the database.

---

### 7.2 Customer AI Agent Page

**Purpose:** Item availability + personalized offers, in conversation.

**Capabilities:**
- Answer availability questions ("do you have milk in stock?") against live `inventory` + `items`.
- Show the customer their current live offers/notifications — **re-derived on demand**, not just a static read of `offers`/`notifications`: if asked "any deals for me today?", the agent re-runs the same scoring path as §6 (`compute_urgency_score`, `compute_affinity_score`, `compute_would_buy_anyway_score`, `decide_strategy`) for that one customer against currently-expiring inventory, so the answer reflects live stock, not stale rows.
- Never reveals another customer's data, cost/margin figures, or raw scores — customer-facing answers surface strategy and discount only.

**Functions (in `agent.py`):**
- `parse_customer_query(query_text: str) -> dict`
  Claude call — classifies intent: `{availability | offers | general}`.
- `answer_availability(item_query: str) -> str`
  Looks up matching `items` + `inventory` (`stock_qty > 0`), phrases result.
- `get_live_offers_for_user(user_id: str) -> list[dict]`
  Runs the §6 scoring pipeline scoped to one user against all currently-expiring inventory; returns only the `offer`/`notify` outcomes for that user (does not write new rows — read-time-only variant of `run_campaign`, so browsing the agent page never itself triggers a discount to be issued).
- `answer_customer_query(query_text: str, user_id: str) -> str`
  Orchestrates: `parse_customer_query` → `answer_availability` or `get_live_offers_for_user` → Claude call to phrase the final answer, applying constraints (no margin/score leakage).

**UI (`render_customer_ai_agent_tab`):**
- Chat input + conversation history, scoped to the selected `user_id`.
- Live offers rendered as cards (item, `discount_pct` or "notify only", short `reasoning_text`) below the chat, refreshed each time the agent recomputes them.

---

## 8. Developer Commands & Conventions

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
- Scoring logic is strictly deterministic and auditable; Claude/LLM is used solely for natural-language reasoning text and conversational intent parsing.
- Clear separation of concerns: `db.py` handles database queries, `config.py` holds tunable parameters, `agent.py` contains decision & chat logic, and `frontend/` handles rendering and user interaction.
- Hand-authored migration files in `migrations/` are applied sequentially (`0001` through `0006`).