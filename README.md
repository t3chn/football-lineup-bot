# ⚽ Football Lineup Bot

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AI-powered Football Lineup Predictor with Telegram Bot integration and Web Interface

[Features](#features) • [Quick Start](#quick-start) • [User Guide](USER_GUIDE.md) • [API Docs](#api-documentation) • [Contributing](CONTRIBUTING.md)

</div>

## 🌟 Features

- **🤖 AI-Powered Predictions** - Smart lineup predictions based on team data and formations
- **💬 Telegram Bot** - Interactive bot for getting predictions on the go
- **🌐 Web Interface** - Modern React interface with real-time predictions
- **⚡ Fast API** - RESTful API built with FastAPI for high performance
- **💾 Smart Caching** - In-memory caching for improved response times
- **🐳 Docker Ready** - Production-ready Docker setup with multi-stage builds
- **✅ Well Tested** - Comprehensive test coverage with pytest
- **🔄 CI/CD Ready** - Pre-configured GitHub Actions workflows

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)
- Telegram Bot Token (for bot features)
- API-Football Key (for real data - see [API Setup Guide](SETUP_API.md))

### 🏃 Running Locally

1. **Clone the repository**

```bash
git clone https://github.com/t3chn/football-lineup-bot.git
cd football-lineup-bot
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Install dependencies and run**

**Option A: Using UV (Recommended)**

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install backend dependencies
uv sync

# Run backend
uv run uvicorn backend.app.main:app --reload

# In another terminal, run frontend
cd frontend
npm install
npm run dev
```

**Option B: Using Docker**

```bash
docker-compose up
```

4. **Access the applications**

- 🌐 Web Interface: http://localhost:5173
- 📡 API Documentation: http://localhost:8000/docs
- 🏥 Health Check: http://localhost:8000/health

## 📖 Documentation

### Project Structure

```
football-lineup-bot/
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── adapters/    # External API clients
│   │   ├── bot/         # Telegram bot handlers
│   │   ├── models/      # Pydantic models
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   └── main.py      # Application entry point
│   └── tests/           # Unit tests
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── api/        # API client
│   │   ├── components/ # React components
│   │   └── App.tsx     # Main application
├── docker-compose.yml   # Docker composition
├── Dockerfile          # Multi-stage Docker build
└── pyproject.toml      # Python project configuration
```

### API Documentation

The API provides the following endpoints:

#### Core Endpoints

| Method | Endpoint          | Description                      |
| ------ | ----------------- | -------------------------------- |
| GET    | `/health`         | Health check endpoint            |
| GET    | `/predict/{team}` | Get lineup prediction for a team |
| POST   | `/telegram`       | Telegram webhook endpoint        |

#### Example Request

```bash
curl http://localhost:8000/predict/Arsenal
```

#### Example Response

```json
{
  "team": "Arsenal",
  "formation": "4-3-3",
  "confidence": 0.85,
  "lineup": [
    {
      "name": "Raya",
      "position": "GK",
      "number": 22,
      "is_captain": false
    }
  ],
  "predicted_at": "2025-08-07T10:00:00Z"
}
```

## 🤖 Telegram Bot

### Setup

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Set the token in `.env` file
4. Configure webhook URL if using webhook mode

### Commands

- `/start` - Start the bot
- `/predict <team>` - Get lineup prediction
- `/help` - Show help message

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=backend

# Run specific test file
uv run pytest backend/tests/test_prediction_service.py
```

### API Integration Testing

After configuring your API key, test the integration:

```bash
# Run comprehensive API tests
cd backend
python test_api_integration.py

# Quick test for specific teams
python quick_test.py                    # Interactive mode
python quick_test.py arsenal            # Test specific team
python quick_test.py "real madrid"      # Test team with space in name
```

## 🔧 Development

### Code Quality

```bash
# Run linting
uv run ruff check .

# Format code
uv run ruff format .

# Run pre-commit hooks
pre-commit run --all-files
```

### Environment Variables

| Variable             | Description                          | Default                                           |
| -------------------- | ------------------------------------ | ------------------------------------------------- |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token                   | -                                                 |
| `API_FOOTBALL_KEY`   | Football API key                     | -                                                 |
| `WEBHOOK_URL`        | Telegram webhook URL                 | -                                                 |
| `WEBHOOK_SECRET`     | Webhook secret key                   | webhook_secret                                    |
| `ENVIRONMENT`        | Environment (development/production) | development                                       |
| `CORS_ORIGINS`       | Allowed CORS origins                 | ["http://localhost:3000","http://localhost:5173"] |

## 🐳 Docker

### Build and Run

```bash
# Build image
docker build -t football-lineup-bot .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Production Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Performance

- **Response Time**: < 100ms for cached requests
- **Cache TTL**: 5 minutes for predictions
- **Concurrent Users**: Supports 1000+ concurrent connections
- **Memory Usage**: < 256MB under normal load

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [React](https://reactjs.org/) and [Vite](https://vitejs.dev/)
- Bot framework by [aiogram](https://docs.aiogram.dev/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)

## 📧 Contact

- GitHub: [@t3chn](https://github.com/t3chn)
- Project Link: [https://github.com/t3chn/football-lineup-bot](https://github.com/t3chn/football-lineup-bot)

---

<div align="center">
  Made with ❤️ by the Football Lineup Bot Team
</div>
