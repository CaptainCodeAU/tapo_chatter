"""Tapo Chatter - A Python application to list and manage Tapo H100 Hub devices."""

__version__ = "0.1.0"

import asyncio
from .config import TapoConfig
from .main import main

__all__ = ["TapoConfig", "main"]

if __name__ == "__main__":
    asyncio.run(main())

def hello() -> str:
    """Return a greeting message."""
    return f"Hello from tapo_chatter version {__version__}!"
