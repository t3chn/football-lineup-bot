# 🚀 API Setup Guide for Football Lineup Bot

## Step 1: Get API-Football Key

1. Go to https://rapidapi.com/api-sports/api/api-football
2. Click "Subscribe to Test" button
3. Choose the free plan (100 requests/day)
4. Sign up or login to RapidAPI
5. After subscribing, go to "Endpoints" tab
6. Find your API key in the header section (X-RapidAPI-Key)

## Step 2: Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# API Configuration
API_FOOTBALL_KEY=your_rapidapi_key_here
API_FOOTBALL_BASE_URL=https://api-football-v1.p.rapidapi.com/v3

# Environment
ENVIRONMENT=development

# Optional: Your own API key for rate limiting
API_KEY=your_custom_api_key_here
```

## Step 3: Available Endpoints

With API-Football you can get:

- **Teams**: `/teams` - Get team information
- **Players**: `/players` - Get player details
- **Lineups**: `/fixtures/lineups` - Get match lineups
- **Squads**: `/players/squads` - Get team squads
- **Statistics**: `/players/statistics` - Player statistics

## Step 4: Test API Connection

```bash
# Test with curl
curl -X GET "https://api-football-v1.p.rapidapi.com/v3/teams?league=39&season=2024" \
  -H "X-RapidAPI-Key: YOUR_API_KEY" \
  -H "X-RapidAPI-Host: api-football-v1.p.rapidapi.com"
```

## API Limits

- **Free Plan**: 100 requests/day
- **Basic Plan**: 1,000 requests/day ($24/month)
- **Pro Plan**: 10,000 requests/day ($99/month)

## Popular League IDs

- Premier League: 39
- La Liga: 140
- Serie A: 135
- Bundesliga: 78
- Ligue 1: 61
- Champions League: 2

## Popular Team IDs

- Arsenal: 42
- Chelsea: 49
- Liverpool: 40
- Manchester United: 33
- Manchester City: 50
- Real Madrid: 541
- Barcelona: 529
- Bayern Munich: 157
- PSG: 85
- Juventus: 496
