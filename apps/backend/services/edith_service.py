"""EDITH service boundary (baseline §3.2).

EDITH is the computer-control agent (screen, mouse/keyboard, browser).
Real computer control is explicitly out of scope for this slice, so this
is a deterministic *mock* that describes what EDITH would do without
performing any real action. It exists to prove the delegation pipeline
can reach EDITH, not to implement its capabilities.
"""

from __future__ import annotations


def execute(command: str) -> dict:
    """Return a deterministic, side-effect-free description of the request.

    No screen, mouse, keyboard, or browser interaction is performed.
    """
    return {
        "agent": "EDITH",
        "kind": "computer_control",
        "mock": True,
        "command": command,
        "summary": (
            "EDITH would perform a computer-control operation for this "
            "request. Real computer control is not implemented in this slice."
        ),
    }
