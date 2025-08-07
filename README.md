# Football Lineup Predictor Bot

Telegram bot and Web UI for football team lineup predictions.

## Features

- 🤖 Telegram bot with lineup predictions
- 🌐 Web interface for easy access
- ⚡ Fast predictions using external API
- 🔄 Smart caching for improved performance
- 📱 Responsive design

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Bot**: aiogram 3 (webhook mode)
- **Frontend**: React, TypeScript, Vite
- **External API**: Sportmonks/API-Football
- **Deployment**: Docker, Cloud Run

## Project Structure

```
football-lineup-bot/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic
│   │   ├── adapters/  # External API clients
│   │   └── models/    # Pydantic models
│   └── tests/         # Backend tests
├── frontend/          # React frontend
│   └── src/
│       ├── components/
│       ├── services/
│       └── types/
└── docker-compose.yaml
```

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- uv (Python package manager)
- Docker (optional)

### Backend Setup

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Run development server
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

### Running with Docker

```bash
# Build and run all services
docker-compose up --build
```

## Testing

```bash
# Run backend tests
pytest

# Run with coverage
pytest --cov=backend

# Run linting
ruff check backend/
ruff format backend/
```

## Deployment

The application is designed to be deployed on Cloud Run or similar platforms.

```bash
# Build Docker image
docker build -t football-lineup-bot .

# Deploy to Cloud Run
gcloud run deploy football-lineup-bot \
  --image gcr.io/PROJECT_ID/football-lineup-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

See `.env.example` for required environment variables.

## License

MIT
