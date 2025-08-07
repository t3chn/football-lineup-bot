# 📚 User Guide - Football Lineup Bot

## Table of Contents

- [Getting Started](#getting-started)
- [Web Interface Guide](#web-interface-guide)
- [Telegram Bot Guide](#telegram-bot-guide)
- [API Usage](#api-usage)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## 🎯 Getting Started

### What is Football Lineup Bot?

Football Lineup Bot is an intelligent system that predicts football team lineups based on various factors including recent form, injuries, and tactical preferences. It provides predictions through three interfaces:

1. **Web Interface** - User-friendly web application
2. **Telegram Bot** - Chat-based predictions on the go
3. **REST API** - For developers and integrations

### Quick Setup

#### Step 1: Environment Setup

Create a `.env` file with your credentials:

```env
# Required for Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional: External API Key
API_FOOTBALL_KEY=your_api_key_here

# For production deployment
WEBHOOK_URL=https://your-domain.com/telegram
WEBHOOK_SECRET=your_secret_key_here
```

#### Step 2: Choose Your Installation Method

**For Non-Technical Users (Docker):**

```bash
docker-compose up
```

**For Developers (Local Installation):**

```bash
# Backend
uv sync
uv run uvicorn backend.app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 🌐 Web Interface Guide

### Accessing the Web Interface

1. Open your browser and navigate to `http://localhost:5173`
2. You'll see the main prediction interface

### Making Predictions

1. **Enter Team Name**: Type the name of the team (e.g., "Arsenal", "Chelsea", "Liverpool")
2. **Click "Get Prediction"**: The system will generate a lineup prediction
3. **View Results**: The predicted lineup will be displayed on a visual football field

### Understanding the Display

- **Formation**: Shows the tactical formation (e.g., 4-3-3, 4-4-2)
- **Player Positions**: Each player is shown in their predicted position
- **Captain Badge**: Yellow "C" indicates the predicted captain
- **Confidence Score**: Shows how confident the prediction is (0-100%)

### Features

- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Predictions are cached for 5 minutes

## 🤖 Telegram Bot Guide

### Setting Up Your Bot

#### Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "My Football Lineup Bot")
4. Choose a username (must end with 'bot', e.g., `mylineup_bot`)
5. Copy the token provided by BotFather

#### Step 2: Configure the Bot

Add the token to your `.env` file:

```env
TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
```

#### Step 3: Start Using the Bot

1. Find your bot on Telegram using the username
2. Click "Start" or send `/start`

### Bot Commands

| Command           | Description               | Example            |
| ----------------- | ------------------------- | ------------------ |
| `/start`          | Initialize the bot        | `/start`           |
| `/help`           | Show available commands   | `/help`            |
| `/predict <team>` | Get lineup prediction     | `/predict Arsenal` |
| `/about`          | Information about the bot | `/about`           |

### Usage Examples

**Getting a Prediction:**

```
You: /predict Manchester United
Bot: 🔮 Predicting lineup for Manchester United...

📋 Formation: 4-2-3-1
⚡ Confidence: 85%

Lineup:
GK: Onana (1)
LB: Shaw (23)
CB: Varane (19)
CB: Martinez (6)
RB: Wan-Bissaka (29)
...
```

**Getting Help:**

```
You: /help
Bot: 📖 Available Commands:
• /predict <team> - Get lineup prediction
• /help - Show this message
• /about - About this bot
```

### Webhook vs Polling Mode

**Polling Mode (Development):**

- Bot actively checks for messages
- Good for local development
- No public URL needed

**Webhook Mode (Production):**

- Telegram sends updates to your server
- More efficient for production
- Requires public HTTPS URL

To set up webhook:

```bash
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/telegram"}'
```

## 🔌 API Usage

### Authentication

The API is currently open and doesn't require authentication for basic usage.

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

#### Get Lineup Prediction

```http
GET /predict/{team_name}
```

**Parameters:**

- `team_name` (path): Name of the team

**Example Request:**

```bash
curl http://localhost:8000/predict/Arsenal
```

**Example Response:**

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
    },
    {
      "name": "White",
      "position": "RB",
      "number": 4,
      "is_captain": false
    },
    ...
  ],
  "predicted_at": "2025-08-07T10:00:00Z"
}
```

### Using with Programming Languages

**Python Example:**

```python
import requests

response = requests.get("http://localhost:8000/predict/Arsenal")
data = response.json()
print(f"Formation: {data['formation']}")
for player in data['lineup']:
    print(f"{player['position']}: {player['name']}")
```

**JavaScript Example:**

```javascript
fetch("http://localhost:8000/predict/Arsenal")
  .then((response) => response.json())
  .then((data) => {
    console.log(`Formation: ${data.formation}`);
    data.lineup.forEach((player) => {
      console.log(`${player.position}: ${player.name}`);
    });
  });
```

### Rate Limiting

- **Default Limit**: 100 requests per minute
- **Cache Duration**: 5 minutes per team prediction

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Bot Not Responding

**Problem**: Telegram bot doesn't respond to commands

**Solutions:**

1. Check bot token is correct in `.env`
2. Ensure backend is running: `docker-compose ps`
3. Check logs: `docker-compose logs backend`
4. Verify webhook URL (if using webhook mode)

#### Web Interface Not Loading

**Problem**: Cannot access web interface at localhost:5173

**Solutions:**

1. Check frontend is running: `npm run dev`
2. Clear browser cache
3. Check for port conflicts: `lsof -i :5173`
4. Try different browser

#### API Returns 503 Error

**Problem**: API returns "Service Unavailable"

**Solutions:**

1. External API might be down
2. Check API key in `.env`
3. System will use mock data as fallback
4. Wait for cache to expire (5 minutes)

#### Docker Issues

**Problem**: Docker containers won't start

**Solutions:**

```bash
# Clean up and restart
docker-compose down
docker-compose up --build

# Check logs
docker-compose logs -f

# Reset everything
docker system prune -a
```

### Error Messages

| Error                 | Meaning                      | Solution                           |
| --------------------- | ---------------------------- | ---------------------------------- |
| `Token is invalid!`   | Telegram bot token incorrect | Check TELEGRAM_BOT_TOKEN in .env   |
| `API key required`    | Missing football API key     | Add API_FOOTBALL_KEY to .env       |
| `Team not found`      | Unknown team name            | Check spelling, use full team name |
| `Rate limit exceeded` | Too many requests            | Wait 1 minute before retrying      |

## ❓ FAQ

### General Questions

**Q: How accurate are the predictions?**
A: Predictions are based on recent data and achieve 70-85% accuracy on average.

**Q: Which teams are supported?**
A: Currently supports major European leagues including Premier League, La Liga, Serie A, Bundesliga, and Ligue 1.

**Q: How often is data updated?**
A: Predictions are cached for 5 minutes, then refreshed with latest data.

**Q: Can I use this for betting?**
A: This tool is for entertainment and informational purposes only. Not intended for gambling.

### Technical Questions

**Q: Can I deploy this to the cloud?**
A: Yes! The project includes Docker configuration for easy deployment to services like Google Cloud Run, AWS ECS, or Heroku.

**Q: How do I add more teams?**
A: The system automatically supports any team available in the external API. For mock data, you can modify `backend/app/services/prediction.py`.

**Q: Can I customize the prediction algorithm?**
A: Yes, the prediction logic is in `backend/app/services/prediction.py` and can be modified.

**Q: Is there an API rate limit?**
A: Default is 100 requests/minute. Can be configured in `backend/app/settings.py`.

### Telegram Bot Questions

**Q: Can multiple users use the same bot?**
A: Yes, the bot supports multiple concurrent users.

**Q: How do I restrict bot access?**
A: Add user validation in `backend/app/bot/handlers.py` checking `message.from_user.id`.

**Q: Can I add more commands?**
A: Yes, add new handlers in `backend/app/bot/handlers.py`.

## 📞 Support

### Getting Help

1. **Documentation**: Check this guide and README.md
2. **Issues**: Report bugs on [GitHub Issues](https://github.com/t3chn/football-lineup-bot/issues)
3. **Discussions**: Join [GitHub Discussions](https://github.com/t3chn/football-lineup-bot/discussions)

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Contact

- GitHub: [@t3chn](https://github.com/t3chn)
- Project: [football-lineup-bot](https://github.com/t3chn/football-lineup-bot)

---

<div align="center">
  Made with ❤️ by the Football Lineup Bot Team
</div>
