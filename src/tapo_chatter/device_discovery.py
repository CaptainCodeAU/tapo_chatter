"""Device discovery module for Tapo Chatter.

This module provides functionality to discover Tapo devices on the local network
by concurrently probing IP addresses in a given range.
"""
import asyncio
import socket
from typing import Any, Dict, List, Optional, Tuple

import netifaces
from tapo import ApiClient

from .config import TapoConfig
from .utils import check_host_connectivity, console, process_device_data

# console is imported from utils, so remove this duplicate
# console = Console()


def get_local_ip_subnet() -> Optional[str]:
    """
    Get the local IP subnet (first three octets) of the primary network interface.
    
    Returns:
        Optional[str]: The subnet in the format "xxx.xxx.xxx" or None if it can't be determined.
    """
    try:
        # Get default gateway interface
        default_gateway = netifaces.gateways()['default']
        if not default_gateway or not default_gateway.get(netifaces.AF_INET):
            return None

        default_interface = default_gateway[netifaces.AF_INET][1]

        # Get IP address for the interface
        interface_addresses = netifaces.ifaddresses(default_interface)
        if not interface_addresses or not interface_addresses.get(netifaces.AF_INET):
            return None

        ip_address = interface_addresses[netifaces.AF_INET][0]['addr']
        # Return first three octets
        return '.'.join(ip_address.split('.')[:3])
    except (KeyError, IndexError, ValueError):
        # Fallback to a common subnet if we can't determine
        return "192.168.1"


def get_useful_device_info(device_info: Any) -> Dict[str, Any]:
    """
    Extract useful properties from device_info object.
    
    Args:
        device_info: The device info object returned by the Tapo API
        
    Returns:
        Dict[str, Any]: Dictionary containing useful device information
    """
    # Utilize the common function in utils.py
    return process_device_data(device_info)


async def device_probe(client: ApiClient, ip_address: str, timeout_seconds: float = 1.0) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Probe a single IP address for a Tapo device.
    
    Args:
        client: The Tapo ApiClient instance
        ip_address: The IP address to probe
        timeout_seconds: Maximum time to wait for a response
        
    Returns:
        Tuple[bool, Optional[Dict]]: Tuple containing (success, device_data)
    """
    # Redirect console output to suppress raw error messages
    import io
    import sys
    original_stderr = sys.stderr
    sys.stderr = io.StringIO()  # Capture stderr output

    try:
        device = await client.generic_device(ip_address)
        device_info = await device.get_device_info()
        # Restore stderr before returning
        sys.stderr = original_stderr

        if device_info:
            device_instance = {
                'ip_address': ip_address,
                'device_info': get_useful_device_info(device_info)
            }
            return True, device_instance
        return False, None
    except Exception:
        # Restore stderr before returning
        sys.stderr = original_stderr
        return False, None


async def device_probe_semaphore(sem: asyncio.Semaphore, client: ApiClient, ip_address: str,
                               timeout_seconds: float) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Probe a single IP address with semaphore for concurrency control.
    
    Args:
        sem: Asyncio Semaphore for limiting concurrent connections
        client: The Tapo ApiClient instance
        ip_address: The IP address to probe
        timeout_seconds: Maximum time to wait for a response
        
    Returns:
        Tuple[bool, Optional[Dict]]: Tuple containing (success, device_data)
    """
    async with sem:
        return await asyncio.wait_for(device_probe(client, ip_address), timeout=timeout_seconds)


async def discover_devices(client: ApiClient, subnet: Optional[str] = None,
                         ip_range: Optional[Tuple[int, int]] = (1, 254),
                         limit: int = 20,
                         timeout_seconds: float = 0.5,
                         stop_after: Optional[int] = None
                         ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Discover Tapo devices on the network by probing IP addresses.
    
    Args:
        client: The Tapo ApiClient instance
        subnet: The subnet to scan (e.g. "192.168.1"), if None will be auto-detected
        ip_range: Range of IP addresses to scan (last octet), defaults to (1, 254)
        limit: Maximum number of concurrent probes (higher means faster scanning)
        timeout_seconds: Maximum time to wait for each probe (lower means faster scanning)
        stop_after: Stop scanning after finding this many devices (None means scan all IPs)
        
    Returns:
        Tuple[List[Dict[str, Any]], Dict[str, int]]: 
            - List of discovered devices with their information
            - Dictionary with error statistics by type
    """
    if subnet is None:
        # Try to get subnet from configuration first
        config = TapoConfig.from_env()
        if config.ip_ranges:
            subnet = config.ip_ranges[0].subnet
        else:
            # Fall back to auto-detection if no configured range
            subnet = get_local_ip_subnet()
            if subnet is None:
                console.print("[yellow]Warning: Could not determine local subnet. Falling back to 192.168.1[/yellow]")
                subnet = "192.168.1"

    # Use default IP range if none provided
    if ip_range is None:
        ip_range = (1, 254)

    console.print(f"[yellow]Discovering Tapo devices on subnet {subnet}.* (range {ip_range[0]}-{ip_range[1]})[/yellow]")
    console.print(f"[yellow]Using concurrency limit of {limit} with {timeout_seconds}s timeout[/yellow]")

    device_data = []
    sem = asyncio.Semaphore(limit)  # Limit concurrent tasks

    # Validate and adjust range
    start_ip = max(1, min(254, ip_range[0]))
    end_ip = max(1, min(254, ip_range[1]))
    if start_ip > end_ip:
        start_ip, end_ip = end_ip, start_ip

    # Create tasks for each IP in the range
    tasks = []
    for ip_octet in range(start_ip, end_ip + 1):
        ip_address = f"{subnet}.{ip_octet}"
        task = asyncio.create_task(device_probe_semaphore(sem, client, ip_address, timeout_seconds))
        tasks.append(task)

    console.print(f"[yellow]Created {len(tasks)} probe tasks, waiting for completion...[/yellow]")

    # Collect results as they complete
    completed = 0
    found = 0
    errors = 0
    error_types = {
        'timeout': 0,
        'connection_refused': 0,
        'network_unreachable': 0,
        'invalid_url': 0,
        'hash_mismatch': 0,
        'cancelled': 0,
        'other': 0
    }

    with console.status(f"[bold green]Scanning network... (0/{len(tasks)} completed, 0 devices found)") as status:
        for task in asyncio.as_completed(tasks):
            try:
                is_device, device_instance = await task
                completed += 1
                status.update(f"[bold green]Scanning network... ({completed}/{len(tasks)} completed, {found} devices found, {errors} errors)")

                if is_device and device_instance:
                    found += 1
                    device_data.append(device_instance)
                    ip = device_instance['ip_address']
                    nickname = device_instance['device_info'].get('nickname', 'Unknown')
                    model = device_instance['device_info'].get('model', 'Unknown')
                    status.update(f"[bold green]Scanning network... ({completed}/{len(tasks)} completed, {found} devices found, {errors} errors) - Found {model} '{nickname}' at {ip}")

                    # Check if we've reached the desired number of devices
                    if stop_after is not None and found >= stop_after:
                        console.print(f"[yellow]Reached target of {stop_after} devices, stopping scan early[/yellow]")
                        # Cancel remaining tasks
                        for t in tasks:
                            if not t.done():
                                t.cancel()
                                error_types['cancelled'] += 1
                        break

            except asyncio.TimeoutError:
                errors += 1
                error_types['timeout'] += 1
            except ConnectionRefusedError:
                errors += 1
                error_types['connection_refused'] += 1
            except OSError as e:
                errors += 1
                if e.errno == 113:  # No route to host
                    error_types['network_unreachable'] += 1
                else:
                    error_types['other'] += 1
            except Exception as e:
                errors += 1
                if 'Invalid URL' in str(e):
                    error_types['invalid_url'] += 1
                elif 'hash mismatch' in str(e).lower():
                    error_types['hash_mismatch'] += 1
                else:
                    error_types['other'] += 1

    return device_data, error_types


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
