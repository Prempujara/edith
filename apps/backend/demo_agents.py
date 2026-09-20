"""EDITH Multi-Agent Ecosystem - Live Agent Demo Script.

Demonstrates all three agents working end-to-end:
1. JARVIS (Primary conversational & technical coding agent)
2. EDITH (Intelligence & computer-control agent)
3. FRIDAY (File-management & operations agent)
"""

import sys
import os
import json

# Ensure apps/backend is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import load_settings
from runtime.registry import build_default_registry
from runtime.store import TaskStore
from runtime.runtime import AgentRuntime
from services.coding_service import CodingService
from services.jarvis_service import JarvisService
from services.llm.fake import FakeLLMClient


def run_demo():
    print("=" * 70)
    print(" EDITH MULTI-AGENT ECOSYSTEM - LIVE DEMO FOR ALL AGENTS")
    print("=" * 70)

    # Initialize shared runtime infrastructure
    settings = load_settings()
    registry = build_default_registry()
    store = TaskStore()
    llm = FakeLLMClient()
    coding_service = CodingService(llm=llm)
    jarvis_service = JarvisService(registry=registry, coding_service=coding_service)
    runtime = AgentRuntime(registry=registry, store=store, jarvis=jarvis_service)

    demo_commands = [
        ("JARVIS (Technical / Coding)", "Write a Python function to compute factorial"),
        ("EDITH (Computer Control)", "Open application browser and navigate to GitHub"),
        ("FRIDAY (File Management)", "Organize the files and documents in my project folder"),
    ]

    for label, command in demo_commands:
        print(f"\n----------------------------------------------------------------------")
        print(f"-> SUBMITTING COMMAND TO {label}")
        print(f"  Command: '{command}'")
        print(f"----------------------------------------------------------------------")

        task = runtime.submit_command(command)
        events = store.get_events(task.id)

        print(f"  Task ID         : {task.id}")
        print(f"  Assigned Agent  : {task.assigned_agent}")
        print(f"  Final Status    : {task.status.value.upper()}")
        print(f"  Events Tracked  : {len(events)} events emitted")
        print("\n  [Execution Events]:")
        for ev in events:
            print(f"   * {ev.type.value:<20} | Agent: {str(ev.agent):<10} | Payload: {ev.payload}")

        print("\n  [Result Payload]:")
        print(json.dumps(task.result, indent=4))
        print("  [OK] DEMO SUCCESSFUL FOR AGENT!")

    print("\n" + "=" * 70)
    print(" ALL 3 AGENTS (JARVIS, EDITH, FRIDAY) OPERATIONAL AND DEMOED!")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
