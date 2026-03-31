# Restaurant Name Generator

A simple Streamlit app that generates:
- a restaurant name based on selected cuisine
- suggested menu items for that restaurant

It uses LangChain `SequentialChain` with Groq's `llama-3.1-8b-instant` model.

## Features

- Cuisine picker from a Streamlit sidebar
- AI-generated restaurant name
- AI-generated comma-separated menu items displayed as a list
- Clean two-step prompt flow (name generation -> menu generation)

## Tech Stack

- Python 3.12+
- Streamlit
- LangChain
- Groq (`langchain-groq`)
- python-dotenv

## Prerequisites

- Python 3.12 or above
- [uv](https://docs.astral.sh/uv/) installed
- A Groq API key

## Setup

1. Clone the repository and move into the project directory.
2. Install dependencies:

```bash
uv sync
```

3. Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## Run the App

```bash
uv run streamlit run main.py
```

Then open the local URL shown in the terminal (usually `http://localhost:8501`).

## Project Structure

- `main.py` - Streamlit UI
- `langchain_helper.py` - LangChain prompt + chain logic
- `pyproject.toml` - project metadata and dependencies

## How It Works

1. User selects a cuisine in the sidebar.
2. First prompt generates a restaurant name.
3. Second prompt uses that name to generate menu items.
4. Results are rendered in Streamlit.
