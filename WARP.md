# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project overview and architecture

- **Runtime environment**
  - Python version is constrained to **3.11.x** via `pyproject.toml`.
  - Dependencies are declared in `pyproject.toml` and locked in `uv.lock`, indicating the project is managed with **uv**.
  - Runtime configuration is supplied via environment variables loaded from a `.env` file using `python-dotenv`.

- **LiveKit voice assistant worker (`agent.py`)**
  - Defines an `Assistant` class that subclasses `livekit.agents.Agent`.
  - The agent is initialized with Spanish/English bilingual instructions and uses an `AsyncOpenAI` client if `OPENAI_API_KEY` is present.
  - The `entrypoint(ctx)` coroutine creates a `livekit.agents.AgentSession` wired to:
    - STT: `assemblyai/universal-streaming`
    - LLM: `openai/gpt-4o-mini`
    - TTS: `cartesia/sonic-3:5ef98b2a-68d2-4a35-ac52-632a2d288ea6`
    - VAD: `livekit.plugins.silero.VAD`
    - Turn detection: `MultilingualModel` from `livekit.plugins.turn_detector.multilingual`
  - At startup, the worker connects the job context to LiveKit, starts an `AgentSession` bound to the room in `ctx`, and greets the user with a bilingual welcome message.
  - `cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))` is used as the executable entrypoint, so this module is intended to be run as a long-lived LiveKit worker process.

- **FastAPI + Supabase service (`supabase_services.py`)**
  - Creates a global `FastAPI` app and a global Supabase `Client` using `SUPABASE_URL` and `SUPABASE_ANON_KEY` loaded from the environment.
  - Exposes two HTTP endpoints:
    - `GET /`: simple health check returning `{ "message": "FastAPI + Supabase OK" }`.
    - `GET /users`: queries the `users` table via `supabase.table("users").select("*").execute()` and returns the raw `.data` payload.
  - The FastAPI app is defined at module level as `app`, so it is directly importable by ASGI servers like `uvicorn`.

- **Environment configuration expectations**
  - `.env` (not checked in) is expected to define at least:
    - `OPENAI_API_KEY` for the LiveKit agent to initialize `AsyncOpenAI`.
    - `SUPABASE_URL` and `SUPABASE_ANON_KEY` for the FastAPI service to construct the Supabase client.

## Dependency management and setup

From the project root, use **uv** to create and manage the environment based on `pyproject.toml` and `uv.lock`:

```bash path=null start=null
uv sync
```

This will create a virtual environment (managed by uv) and install all declared dependencies with versions pinned in `uv.lock`.

## Running the LiveKit voice assistant worker

- Ensure `OPENAI_API_KEY` is set in your environment or defined in a `.env` file in the project root.
- From the project root, run the worker via uv (mirroring the comment in `agent.py`):

```bash path=null start=null
uv run python agent.py dev
```

Notes:
- The trailing `dev` argument is currently unused by `agent.py` but can be repurposed later for mode selection.
- The worker connects to a LiveKit room via the `JobContext` provided by `livekit.agents.cli.run_app`.

## Running the FastAPI + Supabase service

- Ensure `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set in your environment or `.env`.
- Run the ASGI server with `uvicorn`, using the `app` instance defined in `supabase_services.py`:

```bash path=null start=null
uv run uvicorn supabase_services:app --reload --host 0.0.0.0 --port 8000
```

Key behaviors:
- `GET /` can be used as a basic health check for the service.
- `GET /users` returns the raw list of rows from the Supabase `users` table; adjust the query or response shaping here if you introduce more complex domain models.

## Testing and linting

- This repository currently does **not** define any explicit test suite or linting/formatting configuration files.
- If you introduce tools such as `pytest`, `ruff`, or `black`, prefer to run them through uv so they use the same managed environment, for example:

```bash path=null start=null
uv run pytest
```

- Once tests exist and you are using `pytest`, a common pattern to run a **single test** is:

```bash path=null start=null
uv run pytest path/to/test_file.py::test_name
```