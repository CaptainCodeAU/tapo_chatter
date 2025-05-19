"""Main module for Tapo Chatter."""
import asyncio
import datetime  # Added for timestamp conversion
import os  # Added for clearing screen
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from tapo import ApiClient

from .config import TapoConfig
from .utils import check_host_connectivity

console = Console()


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

        # Debug the raw result - COMMENTED OUT
        # console.print(Panel(
        #     f"[cyan]Raw Result Type:[/cyan] {type(result)}\\n"
        #     f"[cyan]Raw Result Dir:[/cyan] {dir(result)}\\n"
        #     f"[cyan]Raw Result String:[/cyan] {str(result)}",
        #     title="Raw API Response",
        #     border_style="blue"
        # ))

        processed_devices: List[Dict[str, Any]] = []
        if isinstance(result, list):
            for i, device_obj in enumerate(result):
                device_dict: Dict[str, Any] = {}

                device_dict["nickname"] = getattr(device_obj, 'nickname', "Unknown")
                device_dict["device_id"] = getattr(device_obj, 'device_id', "Unknown")

                if hasattr(device_obj, 'device_type'):
                    device_dict["device_type"] = getattr(device_obj, 'device_type', "Unknown")
                elif hasattr(device_obj, 'type'):
                    device_dict["device_type"] = getattr(device_obj, 'type', "Unknown")
                else:
                    device_dict["device_type"] = "Unknown"

                # The print_device_table function expects 'status' to be 1 for Online.
                # We need to see what attribute on device_obj represents this.
                # Common names: 'status', 'online'. Let's assume 'status' for now.
                # If 'status' is boolean True for online, it also needs conversion.
                # For now, assuming it's already 0 or 1 as print_device_table expects.
                raw_status = getattr(device_obj, 'status', 0)

                current_status_val = 0 # Default to Offline
                if raw_status is not None:
                    # Check common ways an 'online' status might be represented
                    status_name = getattr(raw_status, 'name', '').lower() # For enums with .name
                    status_value = getattr(raw_status, 'value', None) # For enums with .value
                    status_str = str(raw_status).lower() # For string comparison

                    if 'online' in status_name: # e.g., Status.Online.name == 'Online'
                        current_status_val = 1
                    elif status_value == 1: # e.g., Status.Online.value == 1
                        current_status_val = 1
                    elif 'online' in status_str: # e.g., str(Status.Online) is "Status.Online" or "online"
                        current_status_val = 1
                    elif isinstance(raw_status, bool) and raw_status is True: # if it's a boolean True
                        current_status_val = 1
                    elif raw_status == 1: # if it's already the integer 1
                        current_status_val = 1
                device_dict["status"] = current_status_val


                params: Dict[str, Any] = {}
                device_data_from_to_dict = {}

                if hasattr(device_obj, 'to_dict') and callable(device_obj.to_dict):
                    try:
                        device_data_from_to_dict = device_obj.to_dict() # type: ignore[attr-defined]
                    except Exception:  # pylint: disable=broad-except
                        # If to_dict fails, params will remain empty for this device
                        pass

                if isinstance(device_data_from_to_dict, dict):
                    # Battery status from 'at_low_battery'
                    at_low_battery = device_data_from_to_dict.get('at_low_battery')
                    if isinstance(at_low_battery, bool):
                        # device_dict['battery_state'] = "Low" if at_low_battery else "OK" # No longer direct
                        params['battery_state'] = "Low" if at_low_battery else "OK" # Back to params

                    # Motion sensor status from 'detected'
                    detected = device_data_from_to_dict.get('detected')
                    if isinstance(detected, bool):
                        params['motion_status'] = "Detected" if detected else "Clear"

                    # Contact sensor status from 'open'
                    is_open = device_data_from_to_dict.get('open')
                    if isinstance(is_open, bool):
                        params['contact_status'] = "Open" if is_open else "Closed"

                    # RSSI (Signal Strength)
                    rssi_value = device_data_from_to_dict.get('rssi')
                    # if rssi_value is not None:
                    #     device_dict['rssi'] = str(rssi_value) # Store directly in device_dict
                    # else:
                    #     device_dict['rssi'] = "N/A"
                    device_dict['rssi'] = rssi_value if isinstance(rssi_value, (int, float)) else "N/A"

                    # Additional device info for the new table (remains in params)
                    params['hw_ver'] = str(device_data_from_to_dict.get('hw_ver', "N/A"))
                    # params['jamming_rssi'] = str(device_data_from_to_dict.get('jamming_rssi', "N/A"))
                    jamming_rssi_val = device_data_from_to_dict.get('jamming_rssi')
                    params['jamming_rssi'] = jamming_rssi_val if isinstance(jamming_rssi_val, (int, float)) else "N/A"

                    last_onboard_ts = device_data_from_to_dict.get('lastOnboardingTimestamp')
                    if isinstance(last_onboard_ts, (int, float)):
                        params['last_onboarded'] = datetime.datetime.fromtimestamp(last_onboard_ts).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        params['last_onboarded'] = "N/A"
                    params['mac'] = str(device_data_from_to_dict.get('mac', "N/A"))
                    params['region'] = str(device_data_from_to_dict.get('region', "N/A"))
                    params['report_interval'] = str(device_data_from_to_dict.get('report_interval', "N/A"))
                    params['signal_level'] = str(device_data_from_to_dict.get('signal_level', "N/A"))

                device_dict["params"] = params
                processed_devices.append(device_dict)

        # Show the extracted data structure - COMMENTED OUT
        # console.print(Panel(
        #     f"[cyan]Extracted Data Structure:[/cyan]\\n{str(processed_devices)}",
        #     title="Processed Data",
        #     border_style="blue"
        # ))

        console.print(f"[green]Successfully retrieved {len(processed_devices)} child devices[/green]")
        return processed_devices

    except Exception as e:
        console.print(Panel(
            f"[red]Error getting child devices: {e!s}[/red]\n\n"
            "[yellow]This could be due to:[/yellow]\n"
            "• Invalid credentials\n"
            "• Device is not a H100 hub\n"
            "• Network connectivity issues\n"
            "• Device firmware incompatibility",
            title="Error Details",
            border_style="red"
        ))
        return []


def print_additional_device_info_table(devices: List[Dict[str, Any]]) -> None:
    """Print a table of additional device information."""
    if not devices:
        # No need to print "No devices found" here, main table will handle it
        return

    table = Table(title="Additional Device Information")
    table.add_column("Device Name", style="cyan")
    table.add_column("HW Ver", style="green")
    table.add_column("MAC", style="blue")
    table.add_column("Region", style="yellow")
    table.add_column("Signal Lvl", style="magenta") # Shortened for space
    table.add_column("Battery", style="green") # New column for Battery in additional info table
    table.add_column("Jamming RSSI", style="red")
    table.add_column("Report Int (s)", style="green")
    table.add_column("Last Onboarded", style="blue")

    for device in devices:
        device_params = device.get('params', {})

        jamming_rssi_val = device_params.get('jamming_rssi', "N/A")
        jamming_rssi_display = str(jamming_rssi_val)
        if isinstance(jamming_rssi_val, (int, float)):
            if jamming_rssi_val == 0: # Assuming 0 means no jamming or very low
                jamming_rssi_display = f"[green]{jamming_rssi_val}[/green]"
            elif jamming_rssi_val < -79: # Threshold for very low jamming
                jamming_rssi_display = f"[green]{jamming_rssi_val}[/green]"
            elif jamming_rssi_val < -69: # Threshold for moderate jamming
                jamming_rssi_display = f"[yellow]{jamming_rssi_val}[/yellow]"
            else: # Higher jamming
                jamming_rssi_display = f"[red]{jamming_rssi_val}[/red]"

        table.add_row(
            device.get("nickname", "Unknown"),
            device_params.get('hw_ver', "N/A"),
            device_params.get('mac', "N/A"),
            device_params.get('region', "N/A"),
            device_params.get('signal_level', "N/A"),
            device_params.get('battery_state', "N/A"), # Correctly add battery_state here
            jamming_rssi_display,
            device_params.get('report_interval', "N/A"),
            device_params.get('last_onboarded', "N/A"),
        )
    console.print(table)
    console.print() # Add a blank line for spacing before the next table


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
    table.add_column("RSSI", style="magenta")
    table.add_column("Details", style="blue")

    # Add rows
    for device in devices:
        # Extract additional details if available
        details = []
        device_params = device.get('params', {})

        if isinstance(device_params, dict):
            # Standard sensor data (if present) - Temperature/Humidity remain in details
            if "temperature" in device_params:
                details.append(f"Temp: {device_params['temperature']}°C")
            if "humidity" in device_params:
                details.append(f"Humidity: {device_params['humidity']}%")

            # Parsed status based on to_dict() data - Battery and RSSI removed from here
            if "motion_status" in device_params:
                motion_text = f"Motion: {device_params['motion_status']}"
                if device_params['motion_status'] == "Detected":
                    details.append(f"[bold red]{motion_text}[/bold red]")
                else:
                    details.append(motion_text)
            if "contact_status" in device_params:
                contact_text = f"Contact: {device_params['contact_status']}"
                if device_params['contact_status'] == "Open":
                    details.append(f"[bold red]{contact_text}[/bold red]")
                else:
                    details.append(contact_text)

        rssi_val = device.get('rssi', "N/A")
        rssi_display = str(rssi_val)
        if isinstance(rssi_val, (int, float)):
            if rssi_val == 0: # Assuming 0 is a very strong signal
                rssi_display = f"[green]{rssi_val}[/green]"
            elif rssi_val > -65:
                rssi_display = f"[green]{rssi_val}[/green]"
            elif rssi_val > -75:
                rssi_display = f"[yellow]{rssi_val}[/yellow]"
            else:
                rssi_display = f"[red]{rssi_val}[/red]"

        table.add_row(
            device.get("nickname", "Unknown"),
            device.get("device_id", "Unknown"),
            device.get("device_type", "Unknown"),
            "Online" if device.get("status", 0) == 1 else "Offline",
            rssi_display,    # Colored RSSI
            ", ".join(details) if details else "No specific sensor info"
        )

    console.print(table)


async def main(refresh_interval: int = 10, config: Optional[TapoConfig] = None) -> None:
    """Main entry point."""
    try:
        # Get configuration from environment variables if not provided
        if config is None:
            console.print("[yellow]Loading configuration...[/yellow]")
            config = TapoConfig.from_env()
            console.print("[green]Configuration loaded successfully[/green]")

        # Initialize the API client
        console.print("[yellow]Initializing Tapo API client...[/yellow]")
        client = ApiClient(config.username, config.password)
        console.print("[green]API client initialized[/green]")

        refresh_interval_seconds = refresh_interval
        console.print(f"[blue]Starting real-time monitoring. Refreshing every {refresh_interval_seconds} seconds. Press Ctrl+C to exit.[/blue]")
        await asyncio.sleep(2) # Brief pause before first clear

        while True:
            # Clear the console
            os.system('cls' if os.name == 'nt' else 'clear')

            console.print(f"[bold blue]Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold blue]")
            # Get child devices
            devices = await get_child_devices(client, config.ip_address)

            # Print the additional device information table
            print_additional_device_info_table(devices)

            # Print the main devices table
            print_device_table(devices)

            await asyncio.sleep(refresh_interval_seconds)

    except KeyboardInterrupt:
        # This is now handled by main_cli, but kept here as a safeguard if main() is called directly.
        console.print("\n[bold yellow]Monitoring stopped by user.[/bold yellow]")
    except Exception as e:
        console.print(Panel(
            f"[red]Error: {e!s}[/red]",
            title="Fatal Error",
            border_style="red"
        ))
        raise


def main_cli():
    """Synchronous entry point for the console script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exiting application...[/bold yellow]")
    # Other exceptions are caught and printed within main() or TapoConfig


if __name__ == "__main__":
    # asyncio.run(main()) # Old way
    main_cli() # New way, to handle KeyboardInterrupt gracefully here
