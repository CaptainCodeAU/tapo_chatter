"""Main module for Tapo Chatter."""
import asyncio
import socket
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from tapo import ApiClient

from .config import TapoConfig

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


async def get_child_devices(client: ApiClient, host: str) -> List[Dict[str, Any]]:
    """Get all child devices from the H100 hub."""
    try:
        # First check if we can reach the host
        console.print(f"[yellow]Checking connectivity to {host}...[/yellow]")
        if not await check_host_connectivity(host):
            console.print(f"[red]Error: Cannot reach host {host}. Please check:[/red]")
            console.print("  • The device is powered on")
            console.print("  • You are on the same network as the device")
            console.print("  • The IP address is correct")
            console.print("  • No firewall is blocking the connection")
            return []

        console.print(f"[green]Successfully connected to {host}[/green]")
        
        # Get the hub device first
        console.print("[yellow]Attempting to initialize H100 hub...[/yellow]")
        hub = await client.h100(host)
        console.print("[green]Successfully initialized H100 hub[/green]")
        
        # Then get the child devices
        console.print("[yellow]Fetching child devices...[/yellow]")
        result = await hub.get_child_device_list()
        
        # Debug the raw result
        console.print(Panel(
            f"[cyan]Raw Result Type:[/cyan] {type(result)}\n"
            f"[cyan]Raw Result Dir:[/cyan] {dir(result)}\n"
            f"[cyan]Raw Result String:[/cyan] {str(result)}",
            title="Raw API Response",
            border_style="blue"
        ))
        
        # Try different ways to access the data
        data = {}
        if hasattr(result, '__dict__'):
            data = result.__dict__
        elif hasattr(result, 'result'):
            data = result.result
        elif hasattr(result, 'get_dict'):
            data = result.get_dict()
        
        # Show the extracted data structure
        console.print(Panel(
            f"[cyan]Extracted Data Structure:[/cyan]\n{str(data)}",
            title="Processed Data",
            border_style="blue"
        ))
        
        # Try to get the device list
        devices = []
        if isinstance(data, dict):
            devices = data.get('result', {}).get('child_device_list', [])
        elif isinstance(data, list):
            devices = data
        
        console.print(f"[green]Successfully retrieved {len(devices)} child devices[/green]")
        return devices
        
    except Exception as e:
        console.print(Panel(
            f"[red]Error getting child devices: {str(e)}[/red]\n\n"
            "[yellow]This could be due to:[/yellow]\n"
            "• Invalid credentials\n"
            "• Device is not a H100 hub\n"
            "• Network connectivity issues\n"
            "• Device firmware incompatibility",
            title="Error Details",
            border_style="red"
        ))
        return []


def print_device_table(devices: List[Dict[str, Any]]) -> None:
    """Print a formatted table of devices."""
    if not devices:
        console.print("[yellow]No devices found[/yellow]")
        return

    table = Table(title="Tapo H100 Child Devices")
    
    # Add columns
    table.add_column("Device Name", style="cyan")
    table.add_column("Device ID", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Details", style="blue")
    
    # Add rows
    for device in devices:
        # Extract additional details if available
        details = []
        device_params = device.get('params', {})
        
        if isinstance(device_params, dict):
            if "temperature" in device_params:
                details.append(f"Temp: {device_params['temperature']}°C")
            if "humidity" in device_params:
                details.append(f"Humidity: {device_params['humidity']}%")
            if "battery" in device_params:
                details.append(f"Battery: {device_params['battery']}%")
        
        table.add_row(
            device.get("nickname", "Unknown"),
            device.get("device_id", "Unknown"),
            device.get("device_type", "Unknown"),
            "Online" if device.get("status", 0) == 1 else "Offline",
            ", ".join(details) if details else "No additional info"
        )
    
    console.print(table)


async def main() -> None:
    """Main entry point."""
    try:
        # Get configuration from environment variables
        console.print("[yellow]Loading configuration...[/yellow]")
        config = TapoConfig.from_env()
        console.print("[green]Configuration loaded successfully[/green]")
        
        # Print configuration (masked password)
        console.print(Panel(
            f"[cyan]Username:[/cyan] {config.username}\n"
            f"[cyan]IP Address:[/cyan] {config.ip_address}\n"
            f"[cyan]Password:[/cyan] {'*' * len(config.password)}",
            title="Configuration",
            border_style="blue"
        ))
        
        # Initialize the API client
        console.print("[yellow]Initializing Tapo API client...[/yellow]")
        client = ApiClient(config.username, config.password)
        console.print("[green]API client initialized[/green]")
        
        # Get child devices
        devices = await get_child_devices(client, config.ip_address)
        
        # Print the devices
        print_device_table(devices)
        
    except Exception as e:
        console.print(Panel(
            f"[red]Error: {str(e)}[/red]",
            title="Fatal Error",
            border_style="red"
        ))
        raise


if __name__ == "__main__":
    asyncio.run(main())
