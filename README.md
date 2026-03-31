# Restaurant Name Generator + AI Analytics Pipeline

This project combines a Streamlit restaurant generator with a real-time event pipeline:

- Frontend generates restaurant ideas from cuisine selections
- Events are published to Kafka (Redpanda)
- A background consumer stores events in PostgreSQL
- The consumer also generates AI reviews and stores vectors in Pinecone
- Streamlit includes a live analytics dashboard backed by PostgreSQL

## Architecture

- `main.py`
  - Streamlit UI with two tabs:
    - `✨ Generator`
    - `📊 Analytics Dashboard`
  - Produces generation events to Kafka topic `restaurant-events`
  - Reads analytics data from PostgreSQL for dashboard stats/table
- `langchain_helper.py`
  - LangChain chain to generate restaurant names and menu items
- `consumer.py`
  - Kafka consumer (`ai-analytics-group`)
  - Writes events to PostgreSQL table `generations`
  - Uses Groq LLM to generate short reviews
  - Uses HuggingFace embeddings + Pinecone for vector storage
- `docker-compose.yml`
  - Redpanda (Kafka-compatible broker)
  - Redpanda Console
  - PostgreSQL

## Event Payload

Produced from `main.py`:

```json
{
  "timestamp": "2026-03-31T12:34:56.789012",
  "cuisine_requested": "Italian",
  "restaurant_generated": "Casa Bella"
}
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker + Docker Compose
- API keys:
  - Groq (`GROQ_API_KEY`)
  - Pinecone (`PINECONE_API_KEY`)

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Create `.env` in project root:

```env
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

3. Start infrastructure:

```bash
docker compose up -d
```

Services:
- Kafka broker: `localhost:9092`
- Redpanda Console: `http://localhost:8081`
- PostgreSQL: `localhost:5433`

## Database

Create the `generations` table once in PostgreSQL:

```sql
CREATE TABLE IF NOT EXISTS generations (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP,
  cuisine_requested TEXT NOT NULL,
  restaurant_name TEXT NOT NULL
);
```

You can run this with any Postgres client connected to:
- DB: `restaurant_analytics`
- User: `admin`
- Password: `adminpassword`
- Host: `localhost`
- Port: `5433`

## Run the App

Use two terminals from project root.

1) Start the background consumer:

```bash
uv run python consumer.py
```

2) Start Streamlit:

```bash
uv run streamlit run main.py
```

Open `http://localhost:8501`.

## How to Verify

- Generate restaurants from the `✨ Generator` tab
- Check consumer logs for pipeline steps (Postgres save, review generation, Pinecone upsert)
- Open `📊 Analytics Dashboard` tab and click `Fetch Latest Data`
- Confirm stats and table populate from PostgreSQL

## Stop Services

```bash
docker compose down
```

## Key Files

- `main.py` - Streamlit frontend, Kafka producer, analytics dashboard
- `consumer.py` - Kafka consumer, Postgres writer, Groq + embeddings + Pinecone pipeline
- `langchain_helper.py` - Restaurant/menu generation logic
- `docker-compose.yml` - Redpanda, console, and PostgreSQL services
