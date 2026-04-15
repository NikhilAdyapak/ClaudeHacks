#!/usr/bin/env python3
"""
Big Talk — Demo seed script & end-to-end test runner.
Usage:
    python demo_profiles.py                      # defaults to http://localhost:8000
    python demo_profiles.py http://192.168.1.42:8000
"""

import sys
import json
import requests

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"

# ── Demo profiles ─────────────────────────────────────────────────────────────
PROFILES = [
    {
        "name": "Alex",
        "anime": ["Attack on Titan", "Fullmetal Alchemist", "Vinland Saga"],
        "games": ["Elden Ring", "Sekiro", "Dark Souls"],
        "shows": ["The Wire", "Breaking Bad", "Chernobyl"],
        "hot_take": "Subbed anime is objectively better, dubbed watchers are cowards",
        "secret": "I cried at the end of Fullmetal Alchemist Brotherhood and I'm not ashamed",
    },
    {
        "name": "Jordan",
        "anime": ["Studio Ghibli films", "Avatar: The Last Airbender", "Spirited Away"],
        "games": ["Stardew Valley", "Animal Crossing", "Breath of the Wild"],
        "shows": ["Ted Lasso", "Schitt's Creek", "The Good Place"],
        "hot_take": "Competitive gaming ruined gaming culture — we forgot games are supposed to be fun",
        "secret": "I have 800+ hours in Stardew Valley and I'm still on year 2",
    },
    {
        "name": "Sam",
        "anime": ["Death Note", "Code Geass", "Psycho-Pass"],
        "games": ["League of Legends", "Valorant", "Chess.com"],
        "shows": ["Succession", "Mindhunter", "Sherlock"],
        "hot_take": "College rankings are a scam and everyone secretly knows it",
        "secret": "I've memorized the first 50 digits of pi for absolutely no reason",
    },
    {
        "name": "Riley",
        "anime": ["Your Name", "A Silent Voice", "Wolf Children"],
        "games": ["The Last of Us", "Red Dead Redemption 2", "Disco Elysium"],
        "shows": ["Interstellar", "Everything Everywhere All at Once", "Parasite"],
        "hot_take": "Marvel peaked at Endgame and should have stopped — everything after is damage control",
        "secret": "I once rewatched Interstellar three times in one weekend trying to fully understand it",
    },
    {
        "name": "Morgan",
        "anime": ["Your Lie in April", "K-On!", "Beck: Mongolian Chop Squad"],
        "games": ["Osu!", "Beat Saber", "Hatsune Miku: Project DIVA"],
        "shows": ["Whiplash", "Soul", "La La Land"],
        "hot_take": "AI-generated music will be better than human music within 5 years and that's okay",
        "secret": "I have a Spotify playlist for every emotion I've ever felt — currently at 47 playlists",
    },
]

# Pairs designed for surprising connections:
#   Alex  <-> Jordan : hardcore vs cozy — but both love stories about sacrifice and found family
#   Sam   <-> Morgan : strategy vs rhythm — both are about pattern recognition under pressure
#   Alex  <-> Sam    : different aesthetics, same obsession with broken protagonists clawing upward
DEMO_MATCHES = [
    ("Alex", "Jordan"),
    ("Sam", "Morgan"),
    ("Alex", "Sam"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────
def print_section(title: str):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print('═' * 60)


def print_match_result(name1: str, name2: str, result: dict):
    match = result.get("result", {})
    print(f"\n  🔗  {name1}  ×  {name2}")
    print(f"  Vibe Match Score: {match.get('vibe_match_score', '?')}/100")
    print(f"\n  Opening line: \"{match.get('opening_line', '')}\"")
    print(f"\n  Connections:")
    for i, conn in enumerate(match.get("connections", []), 1):
        print(f"    {i}. {conn.get('title', '')}")
        print(f"       {conn.get('insight', '')}")
        print(f"       💬 \"{conn.get('big_talk_question', '')}\"")
    print(f"\n  Wild card: {match.get('wild_card', '')}")


# ── Part 1: Seed demo data ────────────────────────────────────────────────────
def seed_demo_data(base_url: str, room_code: str = "DEMO") -> dict[str, str]:
    """POST all 5 profiles to the given room. Returns {name: profile_id}."""
    print_section(f"Seeding profiles into room '{room_code}'")
    ids = {}
    for profile in PROFILES:
        payload = {**profile, "room_code": room_code}
        resp = requests.post(f"{base_url}/api/join", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        ids[profile["name"]] = data["profile_id"]
        print(f"  ✓  {profile['name']:8s}  →  {data['profile_id']}")
    return ids


# ── Part 2: Run demo matches ──────────────────────────────────────────────────
def run_demo(base_url: str):
    # Health check
    print_section("Health check")
    resp = requests.get(f"{base_url}/api/health", timeout=5)
    resp.raise_for_status()
    print(f"  {resp.json()}")

    # Seed
    room_code = "DEMO"
    ids = seed_demo_data(base_url, room_code)

    # Room state
    print_section(f"Room '{room_code}' — all profiles")
    resp = requests.get(f"{base_url}/api/room/{room_code}", timeout=5)
    resp.raise_for_status()
    room = resp.json()
    print(f"  {room['count']} people in the room:")
    for p in room["profiles"]:
        print(f"    • {p['name']} — anime: {p['anime']}, games: {p['games']}")

    # Matches
    print_section("Running 3 matches (calling Claude)...")
    for name1, name2 in DEMO_MATCHES:
        print(f"\n  Matching {name1} × {name2}…", end=" ", flush=True)
        payload = {
            "room_code": room_code,
            "profile_id_1": ids[name1],
            "profile_id_2": ids[name2],
        }
        resp = requests.post(f"{base_url}/api/match", json=payload, timeout=30)
        resp.raise_for_status()
        print("done ✓")
        print_match_result(name1, name2, resp.json())

    # Leaderboard
    print_section(f"Leaderboard for '{room_code}'")
    resp = requests.get(f"{base_url}/api/leaderboard/{room_code}", timeout=5)
    resp.raise_for_status()
    board = resp.json()["leaderboard"]
    for entry in board:
        bar = "█" * entry["match_count"]
        print(f"  #{entry['rank']}  {entry['name']:8s}  {bar or '—'}  "
              f"matches: {entry['match_count']}  avg vibe: {entry['avg_vibe_score']}")

    print_section("Demo complete ✓")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Big Talk demo runner → {BASE_URL}")
    try:
        run_demo(BASE_URL)
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Could not connect to {BASE_URL}")
        print("  Make sure the server is running:  uvicorn main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP error: {e}")
        print(f"  Response: {e.response.text}")
        sys.exit(1)
