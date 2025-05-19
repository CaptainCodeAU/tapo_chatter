"""Tapo Chatter - A comprehensive Python application for managing, monitoring, and discovering TP-Link Tapo smart home devices."""

__version__ = "0.3.0"

import asyncio
from .config import TapoConfig
from .device_discovery import discover_devices, check_host_connectivity
from .utils import console, setup_console, create_tapo_protocol, process_device_data, cleanup_resources
from .cli import main_cli as unified_cli

__all__ = [
    "TapoConfig", 
    "discover_devices", 
    "check_host_connectivity",
    "unified_cli",
    "console",
    "setup_console", 
    "create_tapo_protocol", 
    "process_device_data", 
    "cleanup_resources"
]

