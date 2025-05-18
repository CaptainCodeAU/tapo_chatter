"""Command-line tool for discovering Tapo devices on the network."""
import asyncio
import argparse
import json
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.table import Table
from tapo import ApiClient

from .config import TapoConfig
from .device_discovery import discover_devices

console = Console()


def print_device_table(devices: List[Dict[str, Any]]) -> None:
    """Print a formatted table of discovered devices."""
    if not devices:
        console.print("[yellow]No devices found[/yellow]")
        return

    table = Table(title="Discovered Tapo Devices")
    
    # Add columns
    table.add_column("IP Address", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Model", style="blue")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="yellow")
    table.add_column("Signal", style="red")
    table.add_column("MAC", style="dim")
    
    # Add rows
    for device in devices:
        device_info = device.get('device_info', {})
        
        # Format signal level
        signal_level = device_info.get('signal_level')
        if isinstance(signal_level, (int, float)):
            if signal_level >= 3:
                signal_display = f"[green]{signal_level}[/green]"
            elif signal_level >= 2:
                signal_display = f"[yellow]{signal_level}[/yellow]"
            else:
                signal_display = f"[red]{signal_level}[/red]"
        else:
            signal_display = "N/A"
        
        # Status display
        status = "On" if device_info.get('device_on', False) else "Off"
        
        table.add_row(
            device.get('ip_address', 'Unknown'),
            device_info.get('nickname', 'Unknown'),
            device_info.get('model', 'Unknown'),
            device_info.get('type', device_info.get('device_type', 'Unknown')),
            status,
            signal_display,
            device_info.get('mac', 'N/A'),
        )
    
    console.print(table)


async def discover_main(subnet: Optional[str] = None, 
                       ip_range: tuple = (1, 254), 
                       limit: int = 10, 
                       timeout: float = 1.0,
                       json_output: bool = False,
                       verbose: bool = False) -> None:
    """
    Main discovery function.
    
    Args:
        subnet: Network subnet to scan (e.g. "192.168.1")
        ip_range: Range of IP addresses to scan (last octet)
        limit: Maximum number of concurrent probes
        timeout: Timeout for each probe in seconds
        json_output: Whether to output JSON instead of a table
        verbose: Whether to show verbose error output
    """
    try:
        # Get configuration
        console.print("[yellow]Loading configuration...[/yellow]")
        config = TapoConfig.from_env()
        console.print("[green]Configuration loaded successfully[/green]")
        
        # Initialize API client
        console.print("[yellow]Initializing Tapo API client...[/yellow]")
        client = ApiClient(config.username, config.password)
        console.print("[green]API client initialized[/green]")
        
        # Start discovery
        devices = await discover_devices(
            client=client,
            subnet=subnet,
            ip_range=ip_range,
            limit=limit,
            timeout_seconds=timeout
        )
        
        if json_output:
            # Output in JSON format
            console.print(json.dumps(devices, indent=2))
        else:
            # Output as a table
            print_device_table(devices)
            
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Discovery stopped by user[/bold yellow]")
    except Exception as e:
        error_msg = str(e)
        if verbose:
            import traceback
            error_msg += f"\n{traceback.format_exc()}"
        console.print(f"[bold red]Error during discovery: {error_msg}[/bold red]")


def discover_cli():
    """Command-line entry point for device discovery."""
    parser = argparse.ArgumentParser(description="Discover Tapo devices on your network")
    parser.add_argument("-s", "--subnet", type=str, default=None, 
                      help="Network subnet to scan (e.g. 192.168.1)")
    parser.add_argument("-r", "--range", type=str, default="1-254",
                      help="Range of IP addresses to scan, format: start-end (e.g. 1-254)")
    parser.add_argument("-l", "--limit", type=int, default=10,
                      help="Maximum number of concurrent network probes (default: 10)")
    parser.add_argument("-t", "--timeout", type=float, default=1.0,
                      help="Timeout for each probe in seconds (default: 1.0)")
    parser.add_argument("-j", "--json", action="store_true",
                      help="Output results in JSON format")
    parser.add_argument("-v", "--verbose", action="store_true",
                      help="Show verbose error output")
    
    args = parser.parse_args()
    
    # Parse the IP range
    try:
        start, end = map(int, args.range.split('-'))
        ip_range = (start, end)
    except ValueError:
        console.print(f"[bold red]Invalid IP range format: {args.range}. Should be start-end (e.g. 1-254)[/bold red]")
        return
    
    try:
        asyncio.run(discover_main(
            subnet=args.subnet,
            ip_range=ip_range,
            limit=args.limit,
            timeout=args.timeout,
            json_output=args.json,
            verbose=args.verbose
        ))
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Discovery stopped by user[/bold yellow]")


if __name__ == "__main__":
    discover_cli() 