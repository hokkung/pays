# Pays — Personal Finance & Asset Management

A self-hosted, single-user web app for managing your financial news feed, asset
watchlists, and FX rates. Built with FastAPI + PostgreSQL, with a Next.js frontend
(coming soon).

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16
- [uv](https://docs.astral.sh/uv/) for dependency management
- (Optional) Docker & Docker Compose

### Using Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up -d
```

This starts PostgreSQL, the API server, and the scheduler worker.

### Local Development

```bash
cd backend

# Install dependencies
uv sync --extra dev

# Run database migrations
uv run alembic upgrade head

# Start the API server (with hot reload)
uv run uvicorn app.main:app --reload

# In another terminal, start the scheduler worker
uv run pays jobs scheduler
```

## Configuration

All config is via environment variables (see `.env.example`). Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Postgres connection string |
| `API_TOKEN` | `changeme` | Bearer token for API auth |
| `FETCH_NEWS_CRON` | `0 * * * *` | News fetch schedule (hourly) |
| `REFRESH_PRICES_CRON` | `0 * * * *` | Price refresh schedule |
| `REFRESH_FX_CRON` | `0 * * * *` | FX rate refresh schedule |
| `FRED_API_KEY` | _(none)_ | Optional, for treasury yields |

## Running Jobs Manually

```bash
cd backend
uv run pays jobs fetch-news
uv run pays jobs refresh-prices
uv run pays jobs refresh-fx
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Health check (no auth) |
| GET | `/api/news` | List articles (filters: topic, is_read, limit, cursor) |
| POST | `/api/news/{id}/read` | Mark article as read |
| GET/POST/DELETE | `/api/topics` | Manage topic watchlist |
| GET/POST/DELETE | `/api/assets` | Manage asset watchlist |
| GET | `/api/assets/with-latest` | Assets with latest price + THB value |
| GET | `/api/assets/{id}/prices` | Price history |
| GET | `/api/fx` | Latest FX rates |
| GET | `/api/fx/history` | FX rate history |
| POST | `/api/jobs/{name}/run` | Manually trigger a job |
| GET | `/api/jobs/runs` | Recent job run history |

All `/api/*` endpoints require `Authorization: Bearer <API_TOKEN>`.

## Data Sources (all free, zero paid keys)

- **News:** Google News RSS (via `feedparser`)
- **Stocks/ETFs/Gold/Bonds:** yfinance (Yahoo Finance)
- **FX:** Frankfurter (ECB data, includes THB)

### Adding a New Source

1. Implement the relevant Protocol (`NewsSource`, `PriceSource`, or `FXSource`)
2. Add configuration to `app/config.py`
3. Wire it into the service layer (`app/services/`)
4. Add tests with mocked HTTP

## Testing

```bash
cd backend
uv run pytest
uv run mypy app
uv run black --check app tests
uv run ruff check app tests
```

## Project Structure

```
backend/
  app/
    main.py          # FastAPI app factory
    config.py        # pydantic-settings
    db.py            # async engine + session
    models/          # SQLAlchemy models
    schemas/         # Pydantic v2 schemas
    api/             # FastAPI routers
    services/        # Business logic
    sources/         # Pluggable data sources
    jobs/            # APScheduler + job definitions
    cli.py           # Typer CLI
  alembic/           # Migrations
  tests/             # pytest suite
frontend/            # Next.js app (coming soon)
docker-compose.yml
```
