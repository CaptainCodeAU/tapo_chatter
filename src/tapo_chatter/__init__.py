"""Tapo Chatter - A comprehensive Python application for managing, monitoring, and discovering TP-Link Tapo smart home devices."""

__version__ = "0.3.0"

import asyncio

from .cli import main_cli as unified_cli
from .config import TapoConfig
from .device_discovery import check_host_connectivity, discover_devices
from .utils import (
    cleanup_resources,
    console,
    create_tapo_protocol,
    process_device_data,
    setup_console,
)

__all__ = [
    "TapoConfig",
    "check_host_connectivity",
    "cleanup_resources",
    "console",
    "create_tapo_protocol",
    "discover_devices",
    "process_device_data",
    "setup_console",
    "unified_cli"
]

