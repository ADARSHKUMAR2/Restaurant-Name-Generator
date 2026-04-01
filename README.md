# Restaurant Name Generator + AI Data Pipeline

A modular Streamlit project that:

- generates restaurant names and menu ideas
- emits generation events to Kafka (Redpanda)
- processes events in a background consumer
- stores structured data in PostgreSQL
- generates AI review text + vectors and stores them in Pinecone
- provides semantic search and analytics in the UI

## Features

- `✨ Generator` tab: cuisine -> restaurant name + menu ideas
- `📊 Analytics` tab: fetches live rows from PostgreSQL with quick stats
- `🔍 Semantic Search` tab: searches restaurant "vibes" using vector similarity
- Kafka event-driven backend with consumer worker
- Optional Discord webhook notifications on successful processing

## Current Architecture

- `main.py`
  - app entry point
  - mounts three UI tabs from `ui/`
- `ui/ui_generator.py`
  - generator tab rendering
  - publishes generation events using `services/events.py`
- `ui/ui_analytics.py`
  - PostgreSQL-backed analytics table and metrics
- `ui/ui_search.py`
  - semantic search UI over Pinecone vectors
- `consumer.py`
  - listens to Kafka topic `restaurant-events` with group `ai-analytics-group`
  - saves records to Postgres
  - uses Groq + HuggingFace embeddings
  - upserts metadata + vectors into Pinecone
  - sends Discord alerts (if configured)
- `services/`
  - `events.py`: Kafka producer
  - `storage.py`: Postgres + Pinecone persistence
  - `ai_agents.py`: review generation + vector generation
  - `search.py`: semantic search against Pinecone
  - `alerts.py`: Discord webhook integration
  - `langchain_helper.py`: restaurant/menu generation chain

## Infra (Docker Compose)

`docker-compose.yml` starts:

- Redpanda broker on `localhost:9092`
- Redpanda Console on `http://localhost:8081`
- PostgreSQL on `localhost:5433`

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker + Docker Compose
- API keys:
  - `GROQ_API_KEY`
  - `PINECONE_API_KEY`
  - `DISCORD_WEBHOOK_URL`

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Create `.env` in project root:

```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
DISCORD_WEBHOOK_URL=optional_discord_webhook_url
```

3. Start infrastructure:

```bash
docker compose up -d
```

## Database Initialization

Create the `generations` table once:

```sql
CREATE TABLE IF NOT EXISTS generations (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP,
  cuisine_requested TEXT NOT NULL,
  restaurant_name TEXT NOT NULL
);
```

Connection values used by the app:
- host: `localhost`
- port: `5433`
- db: `restaurant_analytics`
- user: `admin`
- password: `adminpassword`

## Run

Use two terminals from project root.

1) Start the consumer:

```bash
uv run python consumer.py
```

2) Start the Streamlit app:

```bash
uv run streamlit run main.py
```

Open `http://localhost:8501`.

## Verify End-to-End

1. Generate a restaurant in `✨ Generator`.
2. Confirm consumer logs show:
   - event received
   - Postgres insert
   - review generation
   - Pinecone upsert
   - Discord alert result (if configured)
3. Open `📊 Analytics` and click `Fetch Latest Data`.
4. Open `🔍 Semantic Search` and query by mood/vibe to retrieve matches.

## Stop

```bash
docker compose down
```
