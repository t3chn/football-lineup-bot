#!/usr/bin/env python3
"""Test script for API-Football integration.

This script helps verify that the API integration is working correctly.
Run this after configuring your API key in the .env file.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.api_football_client import APIFootballClient
from app.services.prediction import PredictionService
from app.settings import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def test_api_configuration():
    """Test if API is properly configured."""
    print("\n=== Testing API Configuration ===")
    settings = get_settings()

    if not settings.api_football_key or settings.api_football_key == "your_rapidapi_key_here":
        print("❌ API key not configured")
        print("   Please set API_FOOTBALL_KEY in your .env file")
        return False

    print(f"✅ API key configured: {settings.api_football_key[:10]}...")
    print(f"✅ API base URL: {settings.api_football_base_url}")
    return True


async def test_team_search():
    """Test searching for teams."""
    print("\n=== Testing Team Search ===")
    client = APIFootballClient()

    if not client.is_configured:
        print("⚠️  API client not configured, skipping team search test")
        return False

    test_teams = ["Arsenal", "Liverpool", "Real Madrid"]

    for team_name in test_teams:
        print(f"\nSearching for: {team_name}")
        team_info = await client.search_team(team_name)

        if team_info:
            print(f"  ✅ Found: {team_info.name} (ID: {team_info.id})")
            if team_info.logo:
                print(f"     Logo: {team_info.logo}")
        else:
            print(f"  ❌ Not found: {team_name}")

    return True


async def test_team_squad():
    """Test fetching team squad."""
    print("\n=== Testing Team Squad Fetch ===")
    client = APIFootballClient()

    if not client.is_configured:
        print("⚠️  API client not configured, skipping squad test")
        return False

    test_team = "arsenal"
    print(f"\nFetching squad for: {test_team}")

    try:
        squad = await client.get_team_squad(test_team)

        if squad:
            print(f"✅ Found {len(squad)} players in squad")

            # Group by position
            by_position = {}
            for player in squad[:5]:  # Show first 5 players
                pos = player.position
                if pos not in by_position:
                    by_position[pos] = []
                by_position[pos].append(player)
                print(f"  - {player.name} (#{player.number}) - {player.position}")

            if len(squad) > 5:
                print(f"  ... and {len(squad) - 5} more players")

            # Show position distribution
            print("\nPosition distribution:")
            position_counts = {}
            for player in squad:
                pos = player.position
                position_counts[pos] = position_counts.get(pos, 0) + 1

            for pos, count in sorted(position_counts.items()):
                print(f"  {pos}: {count} players")
        else:
            print("❌ No squad data returned")

    except Exception as e:
        print(f"❌ Error fetching squad: {e}")
        return False

    return True


async def test_last_lineup():
    """Test fetching last match lineup."""
    print("\n=== Testing Last Match Lineup ===")
    client = APIFootballClient()

    if not client.is_configured:
        print("⚠️  API client not configured, skipping lineup test")
        return False

    test_team = "liverpool"
    print(f"\nFetching last lineup for: {test_team}")

    try:
        formation, lineup = await client.get_last_lineup(test_team)

        if lineup:
            print(f"✅ Found lineup with formation: {formation}")
            print(f"   {len(lineup)} players in starting XI")

            for player in lineup:
                captain_mark = " (C)" if player.is_captain else ""
                print(f"  - {player.name} (#{player.number}) - {player.position}{captain_mark}")
        else:
            print("⚠️  No recent lineup found (team might not have played recently)")

    except Exception as e:
        print(f"❌ Error fetching lineup: {e}")
        return False

    return True


async def test_prediction_service():
    """Test the full prediction service."""
    print("\n=== Testing Prediction Service ===")
    service = PredictionService()

    test_teams = ["chelsea", "manchester united", "barcelona"]

    for team in test_teams:
        print(f"\nGetting prediction for: {team}")

        try:
            prediction = await service.get_prediction(team)

            print("✅ Prediction generated:")
            print(f"   Team: {prediction.team}")
            print(f"   Formation: {prediction.formation}")
            print(f"   Source: {prediction.source}")
            print(f"   Confidence: {prediction.confidence:.0%}")
            print(f"   Players: {len(prediction.lineup)}")

            if prediction.lineup:
                print("   Starting XI:")
                for player in prediction.lineup[:5]:
                    captain_mark = " (C)" if player.is_captain else ""
                    print(f"     - {player.name} - {player.position}{captain_mark}")
                if len(prediction.lineup) > 5:
                    print(f"     ... and {len(prediction.lineup) - 5} more players")

        except Exception as e:
            print(f"❌ Error getting prediction: {e}")
            continue

    return True


async def test_api_limits():
    """Check API usage and limits."""
    print("\n=== API Usage Information ===")
    print("Free plan limits:")
    print("  - 100 requests per day")
    print("  - Rate limit: 10 requests per minute")
    print("\nTo check your current usage:")
    print("  1. Go to https://rapidapi.com/developer/dashboard")
    print("  2. Find API-Football in your subscriptions")
    print("  3. Check the usage statistics")

    return True


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Football Lineup Bot - API Integration Test")
    print("=" * 50)

    # Check if .env file exists
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("\n❌ .env file not found!")
        print("   Please copy .env.example to .env and configure your API key")
        print(f"   Run: cp {env_path.parent}/.env.example {env_path}")
        return

    # Run tests
    tests = [
        ("Configuration", test_api_configuration),
        ("Team Search", test_team_search),
        ("Team Squad", test_team_squad),
        ("Last Lineup", test_last_lineup),
        ("Prediction Service", test_prediction_service),
        ("API Limits", test_api_limits),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your API integration is working correctly.")
    elif passed > 0:
        print("\n⚠️  Some tests passed. Check the failed tests above.")
    else:
        print("\n❌ No tests passed. Please check your API configuration.")


if __name__ == "__main__":
    asyncio.run(main())
