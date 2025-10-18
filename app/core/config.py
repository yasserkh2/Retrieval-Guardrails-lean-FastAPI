"""
Environment-driven configuration (12-Factor compliant).
Reads from environment variables with safe defaults.
"""
import os
from typing import Literal

# Retrieval configuration
CONFIG_DEFAULT: Literal["cosine", "dot"] = os.getenv("CONFIG_DEFAULT", "cosine")  # type: ignore
TOP_K_DEFAULT: int = int(os.getenv("TOP_K_DEFAULT", "3"))

# Guardrail thresholds
LOW_CONF_THRESHOLD: float = float(os.getenv("LOW_CONF_THRESHOLD", "0.15"))

# Server configuration
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
