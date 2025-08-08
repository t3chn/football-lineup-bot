#!/usr/bin/env python3
"""Quick test script for checking specific teams and API responses.

Usage:
    python quick_test.py                    # Interactive mode
    python quick_test.py arsenal            # Test specific team
    python quick_test.py "real madrid"      # Test team with space in name
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.api_football_client import APIFootballClient
from app.services.prediction import PredictionService
from app.settings import get_settings


async def quick_test(team_name: str):
    """Quick test for a specific team."""
    print(f"\n🔍 Testing: {team_name}")
    print("-" * 40)

    # Check if API is configured
    settings = get_settings()
    if not settings.api_football_key or settings.api_football_key == "your_rapidapi_key_here":
        print("❌ API not configured - using mock data")
        print("   To use real data, set API_FOOTBALL_KEY in .env file")
    else:
        print(f"✅ Using API key: {settings.api_football_key[:10]}...")

    # Test prediction service
    service = PredictionService()

    try:
        print(f"\n📊 Getting prediction for {team_name}...")
        prediction = await service.get_prediction(team_name)

        print("\n✅ Success!")
        print(f"   Source: {prediction.source}")
        print(f"   Formation: {prediction.formation}")
        print(f"   Confidence: {prediction.confidence:.0%}")
        print("\n📋 Starting XI:")

        # Group players by position
        positions_order = [
            "GK",
            "RB",
            "CB",
            "LB",
            "DEF",
            "CDM",
            "CM",
            "CAM",
            "MID",
            "RW",
            "LW",
            "ST",
            "CF",
            "FW",
        ]
        sorted_lineup = sorted(
            prediction.lineup,
            key=lambda p: positions_order.index(p.position)
            if p.position in positions_order
            else 99,
        )

        for player in sorted_lineup:
            captain = " ⭐" if player.is_captain else ""
            number = f"#{player.number}" if player.number else "#?"
            print(f"   {number:>3} | {player.position:<3} | {player.name}{captain}")

        # Save to file for inspection
        output_file = f"test_output_{team_name.replace(' ', '_')}.json"
        with open(output_file, "w") as f:
            json.dump(prediction.model_dump(mode="json"), f, indent=2)
        print(f"\n💾 Full response saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

    return True


async def interactive_mode():
    """Interactive mode for testing multiple teams."""
    print("\n🎮 Interactive Test Mode")
    print("=" * 50)
    print("Enter team names to test (or 'quit' to exit)")
    print("\nAvailable teams with mappings:")

    # Show available team mappings
    client = APIFootballClient()
    teams_list = list(client.TEAM_IDS.keys())

    # Display in columns
    for i in range(0, len(teams_list), 3):
        row = teams_list[i : i + 3]
        print("  " + " | ".join(f"{team:<20}" for team in row))

    print("\nYou can also try other team names (will search via API)")

    while True:
        try:
            team_input = input("\n🏟️  Enter team name: ").strip()

            if team_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            if not team_input:
                continue

            await quick_test(team_input)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Test specific team from command line
        team_name = " ".join(sys.argv[1:])
        await quick_test(team_name)
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
