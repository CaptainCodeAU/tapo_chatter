"""Unified CLI interface for Tapo Chatter."""
import asyncio
import argparse
import sys
from typing import List, Optional, Tuple, Dict, Any

from .config import TapoConfig
from .utils import console, setup_console
from .main import main as monitor_main
from .discover import discover_main


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments for the unified CLI."""
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Tapo Chatter - Manage, monitor, and discover TP-Link Tapo smart home devices",
        epilog="Use 'tapo-chatter <mode> --help' for more information on a specific mode"
    )
    
    # Add global arguments applicable to all modes
    parser.add_argument("--version", action="store_true", help="Show version information and exit")
    
    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
    
    # MONITOR mode (original tapo-chatter functionality)
    monitor_parser = subparsers.add_parser("monitor", help="Monitor a Tapo hub and its devices continuously")
    monitor_parser.add_argument("--ip", type=str, help="IP address of the Tapo hub to monitor (overrides TAPO_IP_ADDRESS)")
    monitor_parser.add_argument("--interval", type=int, default=10, 
                              help="Refresh interval in seconds (default: 10)")
    
    # DISCOVER mode (original tapo-discover functionality)
    discover_parser = subparsers.add_parser("discover", help="Discover Tapo devices on your network")
    discover_parser.add_argument("-s", "--subnet", type=str, default=None, 
                               help="Network subnet to scan (e.g. 192.168.1)")
    discover_parser.add_argument("-r", "--range", type=str, default="1-254",
                               help="Range of IP addresses to scan, format: start-end (e.g. 1-254)")
    discover_parser.add_argument("-l", "--limit", type=int, default=20,
                               help="Maximum number of concurrent network probes (default: 20)")
    discover_parser.add_argument("-t", "--timeout", type=float, default=0.5,
                               help="Timeout for each probe in seconds (default: 0.5)")
    discover_parser.add_argument("-n", "--num-devices", type=int, default=None,
                               help="Stop after finding this many devices (default: scan entire range)")
    discover_parser.add_argument("-j", "--json", action="store_true",
                               help="Output results in JSON format")
    discover_parser.add_argument("-v", "--verbose", action="store_true",
                               help="Show verbose error output")
    discover_parser.add_argument("--no-children", action="store_true",
                               help="Skip fetching and displaying child devices from hubs")
    
    return parser.parse_args(args)


async def monitor_mode(args: argparse.Namespace) -> None:
    """Run the monitor mode (original tapo-chatter functionality)."""
    # If custom IP is provided, update the config temporarily
    config = TapoConfig.from_env()
    if args.ip:
        if TapoConfig.is_valid_ip(args.ip):
            config.ip_address = args.ip
        else:
            console.print(f"[red]Invalid IP address format: {args.ip}[/red]")
            sys.exit(1)
    
    # Run the monitor with the specified refresh interval
    await monitor_main(refresh_interval=args.interval, config=config)


async def discover_mode(args: argparse.Namespace) -> None:
    """Run the discover mode (original tapo-discover functionality)."""
    # Parse the IP range
    try:
        start, end = map(int, args.range.split('-'))
        ip_range = (start, end)
    except ValueError:
        console.print(f"[bold red]Invalid IP range format: {args.range}. Should be start-end (e.g. 1-254)[/bold red]")
        sys.exit(1)
    
    # Run discovery with the specified parameters
    await discover_main(
        subnet=args.subnet,
        ip_range=ip_range,
        limit=args.limit,
        timeout=args.timeout,
        stop_after=args.num_devices,
        json_output=args.json,
        verbose=args.verbose,
        show_children=not args.no_children
    )


def get_version() -> str:
    """Get the current version of tapo-chatter."""
    from . import __version__
    return __version__


async def main_async(args: argparse.Namespace) -> None:
    """Asynchronous entry point for the CLI."""
    # Initialize console
    setup_console()
    
    # Show version if requested
    if args.version:
        console.print(f"Tapo Chatter v{get_version()}")
        return
    
    # Handle the mode selection
    if args.mode == "monitor":
        await monitor_mode(args)
    elif args.mode == "discover":
        await discover_mode(args)
    else:
        # No mode specified, show help
        console.print("[yellow]Error: No mode specified[/yellow]")
        console.print("Please specify a mode: 'monitor' or 'discover'")
        console.print("Example: tapo-chatter monitor")
        console.print("Example: tapo-chatter discover")
        console.print("\nUse 'tapo-chatter --help' for more information")


def main_cli() -> None:
    """Synchronous entry point for the console script."""
    try:
        args = parse_args()
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exiting application...[/bold yellow]")
    # Other exceptions are caught within the mode handlers


if __name__ == "__main__":
    main_cli() 