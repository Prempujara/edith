"""Shared pytest configuration for the backend suite.

Force offline mock mode for the LLM. API-level tests build the real dependency
singletons (which pick the LLM client from configuration); this guarantees they
use the deterministic fake client and never construct a real provider or hit
the network, regardless of any API key present in the environment.
"""

from __future__ import annotations

import os

os.environ["EDITH_LLM_MOCK"] = "1"
