# Retail Expiry Campaigner

Track retail products approaching expiry and trigger targeted campaigns.

## System Architecture

### Data & Logic Flow
```mermaid
graph TD
    subgraph Frontend [Streamlit Frontend]
        UI[Dashboard/AI Chat]
    end
    
    subgraph Backend [FastAPI Backend]
        API[API Routers]
        Agent[Agent Engine / LangChain]
        DBMod[DB Access Layer]
    end
    
    subgraph External [External Services]
        Supabase[(Supabase DB)]
        Mistral[Mistral AI LLM]
    end
    
    UI <--> API
    API <--> Agent
    API <--> DBMod
    Agent <--> Mistral
    Agent <--> DBMod
    DBMod <--> Supabase
```

### Campaign Decision Pipeline
```mermaid
graph LR
    A[Expiring Inventory] --> B[Scoring Engine]
    B --> C{Strategy Decision}
    C -- Score > Threshold --> D[Notification Only]
    C -- Score < Threshold --> E[Personalized Offer]
    D --> F[LLM Reasoning Text]
    E --> F
    F --> G[Write to Supabase]
```

### Database Schema
```mermaid
erDiagram
    USER ||--o{ PURCHASE : makes
    USER ||--o{ NOTIFICATION : receives
    USER ||--o{ OFFER : receives
    ITEM ||--o{ INVENTORY : contains
    ITEM ||--o{ PURCHASE : is_bought
    INVENTORY ||--o{ NOTIFICATION : triggers
    INVENTORY ||--o{ OFFER : triggers

    USER {
        uuid user_id PK
        string name
        string role
        string loyalty_tier
        string discount_sensitivity
    }
    ITEM {
        uuid item_id PK
        string name
        string category
        string perishability_tier
    }
    INVENTORY {
        uuid inventory_id PK
        uuid item_id FK
        date expiry_date
        int stock_qty
    }
    PURCHASE {
        uuid purchase_id PK
        uuid user_id FK
        uuid item_id FK
        datetime purchased_at
    }
    NOTIFICATION {
        uuid notification_id PK
        uuid user_id FK
        uuid inventory_id FK
        text message
    }
    OFFER {
        uuid offer_id PK
        uuid user_id FK
        uuid inventory_id FK
        string strategy_type
        numeric discount_pct
    }
```

### User Flow
```mermaid
sequenceDiagram
    participant Owner
    participant Frontend
    participant Backend
    participant DB
    participant LLM

    Owner->>Frontend: Log in as Owner
    Frontend->>Backend: GET /inventory
    Backend->>DB: Query expiring items
    DB-->>Backend: Return list
    Backend-->>Frontend: Display Table
    Owner->>Frontend: Click "Run Campaign"
    Frontend->>Backend: POST /campaigns/run
    Backend->>Backend: Start Background Task
    Backend-->>Frontend: Return "Started"
    
    loop for each user/item
        Backend->>DB: Fetch user history
        Backend->>Backend: Calculate Scores
        Backend->>LLM: Generate personalized text
        Backend->>DB: Write Offer/Notification
    end
```

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

### Backend (from root)

```bash
uvicorn backend.main:app --reload
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Frontend (from root)

```bash
streamlit run frontend/app.py
```

- App: http://localhost:8501

## Database & Seeding

To populate the database with mock data, run the following from the root directory:

### Seed Data (Append)
```bash
export PYTHONPATH=$PYTHONPATH:. && ./.venv/bin/python backend/seed.py
```

### Reset & Seed (Clean Slate)
```bash
export PYTHONPATH=$PYTHONPATH:. && ./.venv/bin/python backend/seed.py reset
```

## Configuration

- Backend: `frontend/src/config.py` holds the `API_BASE_URL` used to reach the API.
- Streamlit options live in `frontend/.streamlit/config.toml`.
