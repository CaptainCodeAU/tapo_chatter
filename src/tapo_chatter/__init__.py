"""Tapo Chatter - A Python application to list and manage Tapo H100 Hub devices."""

__version__ = "0.1.0"

import asyncio
from .config import TapoConfig
from .device_discovery import discover_devices, check_host_connectivity

__all__ = ["TapoConfig", "discover_devices", "check_host_connectivity"]

