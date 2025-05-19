"""Utility functions shared between different Tapo Chatter modules."""
import socket
from typing import Any, Dict

from rich.console import Console
from tapo import ApiClient

console = Console()


async def check_host_connectivity(host: str, port: int = 80, timeout: float = 2) -> bool:
    """Check if the host is reachable on the network."""
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        # Attempt to connect to the host
        result = sock.connect_ex((host, port))
        sock.close()

        return result == 0
    except socket.error:
        return False


def setup_console() -> Console:
    """Set up and return a Rich console instance for display."""
    return Console()


async def create_tapo_protocol(username: str, password: str) -> ApiClient:
    """Create and return an authenticated Tapo API client."""
    console.print("[yellow]Initializing Tapo API client...[/yellow]")
    client = ApiClient(username, password)
    console.print("[green]API client initialized[/green]")
    return client


def process_device_data(device_data: Any) -> Dict[str, Any]:
    """Process raw device data into a standardized format."""
    # Extract useful properties from device_info object
    useful_info = {}
    useful_properties = [
        'avatar', 'device_on', 'model', 'nickname',
        'signal_level', 'ssid', 'device_id', 'device_type',
        'hw_ver', 'mac', 'region', 'type', 'status'
    ]

    for property in dir(device_data):
        if property in useful_properties:
            useful_info[property] = getattr(device_data, property)

    return useful_info


async def cleanup_resources() -> None:
    """Clean up any resources before exiting."""
    # Currently just a placeholder for future cleanup needs
    pass
