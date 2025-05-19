"""Command-line tool for discovering Tapo devices on the network."""
import argparse
import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple

from rich.table import Table
from tapo import ApiClient

from .config import TapoConfig
from .device_discovery import discover_devices
from .main import (
    get_child_devices,
    print_additional_device_info_table,
    print_device_table as print_child_device_table,
)
from .utils import console, create_tapo_protocol

# console is imported from utils, so remove this duplicate
# console = Console()


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
    table.add_column("Connection/Power", style="yellow")
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

        # Status display - prefer 'status' property over 'device_on'
        # For hubs and sensors, status indicates connectivity
        # For plugs and bulbs, device_on indicates power state
        if 'status' in device_info:
            raw_status = device_info.get('status')
            if isinstance(raw_status, (int, float)):
                status = "Online" if raw_status == 1 else "Offline"
            elif isinstance(raw_status, str):
                status = "Online" if raw_status.lower() == "online" else "Offline"
            elif raw_status is True:
                status = "Online"
            elif raw_status is False:
                status = "Offline"
            else:
                # Default fallback to device_on
                status = "On" if device_info.get('device_on', False) else "Off"
        else:
            # For smart plugs and lights, use device_on
            device_type = device_info.get('type', device_info.get('device_type', '')).upper()
            if 'HUB' in device_type or 'SENSOR' in device_type:
                status = "Online"  # Assume online since we can communicate with it
            else:
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


async def print_hub_child_devices(hub_devices: List[Dict[str, Any]], client: ApiClient, show_details: bool = True) -> None:
    """
    Print child devices for each hub discovered.
    
    Args:
        hub_devices: List of discovered hub devices
        client: The Tapo ApiClient instance
        show_details: Whether to show detail tables for each child device
    """
    for hub in hub_devices:
        ip_address = hub.get('ip_address')
        name = hub.get('device_info', {}).get('nickname', 'Unknown Hub')
        model = hub.get('device_info', {}).get('model', 'Unknown')

        console.print(f"\n[bold blue]===== Child Devices Connected to {name} ({model}) at {ip_address} =====\n[/bold blue]")

        # Get child devices from the hub
        try:
            if ip_address is None:
                console.print("[yellow]Cannot fetch child devices: No IP address available[/yellow]")
                continue

            console.print(f"[yellow]Fetching child devices from hub at {ip_address}...[/yellow]")
            child_devices = await get_child_devices(client, ip_address)

            if not child_devices:
                console.print("[yellow]No child devices found connected to this hub.[/yellow]")
                continue

            console.print(f"[green]Found {len(child_devices)} child devices connected to hub {name}[/green]")

            # Print detailed information tables
            if show_details:
                print_additional_device_info_table(child_devices)

            # Print the main child device table
            print_child_device_table(child_devices)

        except Exception as e:
            console.print(f"[red]Error fetching child devices from hub at {ip_address}: {e!s}[/red]")


async def discover_main(subnet: Optional[str] = None,
                       ip_range: Optional[Tuple[int, int]] = (1, 254),
                       limit: int = 20,
                       timeout: float = 0.5,
                       stop_after: Optional[int] = None,
                       json_output: bool = False,
                       verbose: bool = False,
                       show_children: bool = True,
                       custom_config: Optional[TapoConfig] = None) -> None:
    """
    Main discovery function.
    
    Args:
        subnet: Network subnet to scan (e.g. "192.168.1")
        ip_range: Range of IP addresses to scan (last octet), or None to use config
        limit: Maximum number of concurrent probes (higher = faster scanning)
        timeout: Timeout for each probe in seconds (lower = faster scanning)
        stop_after: Stop scanning after finding this many devices
        json_output: Whether to output JSON instead of a table
        verbose: Whether to show verbose error output
        show_children: Whether to show child devices for discovered hubs
        custom_config: Optional pre-configured TapoConfig instance
    """
    try:
        # Get configuration
        if custom_config:
            config = custom_config
        else:
            console.print("[yellow]Loading configuration...[/yellow]")
            config = TapoConfig.from_env()
            console.print("[green]Configuration loaded successfully[/green]")

        # Initialize API client
        client = await create_tapo_protocol(config.username, config.password)

        # Use configured IP range if available
        if not subnet and not ip_range:
            subnet, ip_range = config.get_discovery_params()

        # Start discovery
        devices, error_stats = await discover_devices(
            client=client,
            subnet=subnet,
            ip_range=ip_range,
            limit=limit,
            timeout_seconds=timeout,
            stop_after=stop_after
        )

        # Show verbose error statistics if requested
        if verbose and sum(error_stats.values()) > 0:
            console.print("\n[yellow]Connection Statistics:[/yellow]")

            # Create a table for error stats
            stats_table = Table(title="Network Scan Results")
            stats_table.add_column("Error Type", style="yellow")
            stats_table.add_column("Count", style="cyan")
            stats_table.add_column("Description", style="green")

            # Add error type descriptions
            descriptions = {
                'timeout': "Normal timeouts from non-responsive IPs",
                'connection_refused': "Device refused connection (port closed)",
                'network_unreachable': "Network segment unreachable",
                'invalid_url': "Invalid URL format during connection",
                'hash_mismatch': "Security hash mismatch (non-Tapo device)",
                'cancelled': "Scan cancelled by early stop option",
                'other': "Other connection errors"
            }

            # Add rows for each error type that has occurrences
            for error_type, count in error_stats.items():
                if count > 0:
                    description = descriptions.get(error_type, "Unknown error type")
                    stats_table.add_row(error_type, str(count), description)

            console.print(stats_table)
            console.print()  # Add a blank line for readability

        # Output results
        if json_output:
            # Convert devices to JSON
            output = {
                'devices': devices,
                'error_stats': error_stats
            }
            print(json.dumps(output, indent=2))
        else:
            # Print formatted table
            if devices:
                print_device_table(devices)

                # Filter hub devices
                hub_devices = [
                    device for device in devices
                    if 'HUB' in device.get('device_info', {}).get('type', '').upper()
                ]

                # Print child devices for each hub if requested
                if show_children and hub_devices:
                    await print_hub_child_devices(hub_devices, client)
            else:
                console.print("[yellow]No devices found[/yellow]")

    except Exception as e:
        console.print(f"[red]Error during device discovery: {e!s}[/red]")


def discover_cli():
    """Command-line entry point for device discovery."""
    parser = argparse.ArgumentParser(description="Discover Tapo devices on your network")
    parser.add_argument("-s", "--subnet", type=str, default=None,
                      help="Network subnet to scan (e.g. 192.168.1)")
    parser.add_argument("-r", "--range", type=str, default=None,
                      help="Range of IP addresses to scan, format: start-end (e.g. 1-254)")
    parser.add_argument("-l", "--limit", type=int, default=20,
                      help="Maximum number of concurrent network probes (default: 20)")
    parser.add_argument("-t", "--timeout", type=float, default=0.5,
                      help="Timeout for each probe in seconds (default: 0.5)")
    parser.add_argument("-n", "--num-devices", type=int, default=None,
                      help="Stop after finding this many devices (default: scan entire range)")
    parser.add_argument("-j", "--json", action="store_true",
                      help="Output results in JSON format")
    parser.add_argument("-v", "--verbose", action="store_true",
                      help="Show verbose error output")
    parser.add_argument("--no-children", action="store_true",
                      help="Skip fetching and displaying child devices from hubs")

    args = parser.parse_args()

    # Parse the IP range if provided via command line
    ip_range = None
    if args.range:
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
            stop_after=args.num_devices,
            json_output=args.json,
            verbose=args.verbose,
            show_children=not args.no_children
        ))
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Discovery stopped by user[/bold yellow]")


if __name__ == "__main__":
    discover_cli()
