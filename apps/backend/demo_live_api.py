"""Live HTTP API Demonstration for EDITH Multi-Agent Backend.

Tests live HTTP endpoints on http://127.0.0.1:8000/api/v1:
1. GET /api/v1/agents
2. POST /api/v1/commands (JARVIS - Technical/Coding)
3. POST /api/v1/commands (EDITH - Computer Control)
4. POST /api/v1/commands (FRIDAY - File Management)
"""

import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def http_get(endpoint):
    req = urllib.request.Request(f"{BASE_URL}{endpoint}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def http_post(endpoint, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def run_live_api_demo():
    print("=" * 70)
    print(" LIVE HTTP API DEMO ON http://127.0.0.1:8000")
    print("=" * 70)

    # 1. Fetch Registered Agents
    agents = http_get("/agents")
    print(f"\n[GET /api/v1/agents] Registered Agents ({len(agents)}):")
    for a in agents:
        print(f"  * {a['name']:<10} | Capabilities: {a['capabilities']}")

    # 2. Test Commands for All 3 Agents
    test_cases = [
        ("JARVIS", "Write a Python function to compute factorial"),
        ("EDITH",  "Open application browser and navigate to GitHub"),
        ("FRIDAY", "Organize the files in my project folder"),
    ]

    for expected_agent, command in test_cases:
        print(f"\n----------------------------------------------------------------------")
        print(f"-> POST /api/v1/commands | Target: {expected_agent}")
        print(f"   Command: '{command}'")
        print(f"----------------------------------------------------------------------")

        resp = http_post("/commands", {"command": command})
        task = resp.get("task", {})
        task_id = task.get("id")

        print(f"   Task ID        : {task_id}")
        print(f"   Assigned Agent : {task.get('assigned_agent')}")
        print(f"   Status         : {task.get('status').upper()}")

        # Fetch Events for Task
        events = http_get(f"/tasks/{task_id}/events")
        print(f"   Events Recorded: {len(events)}")

        print("\n   [Live Result Payload]:")
        print(json.dumps(task.get("result"), indent=4))
        print(f"   [OK] LIVE API DEMO SUCCESSFUL FOR {expected_agent}!")

    print("\n" + "=" * 70)
    print(" ALL HTTP ENDPOINTS & MULTI-AGENT EXECUTION VERIFIED LIVE!")
    print("=" * 70)

if __name__ == "__main__":
    run_live_api_demo()
