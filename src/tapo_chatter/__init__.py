"""Tapo Chatter - A comprehensive Python application for managing, monitoring, and discovering TP-Link Tapo smart home devices."""

__version__ = "0.20"

import asyncio
from .config import TapoConfig
from .device_discovery import discover_devices, check_host_connectivity

__all__ = ["TapoConfig", "discover_devices", "check_host_connectivity"]

