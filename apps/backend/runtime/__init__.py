"""Agent Runtime: shared infrastructure for the EDITH, JARVIS, and FRIDAY agents.

Per the architecture baseline, the runtime provides agent registry, messaging,
shared context, memory, events, task tracking, tools, permissions, and execution
coordination. It is not a central AI decision-maker; the agents themselves make
delegation decisions.
"""
