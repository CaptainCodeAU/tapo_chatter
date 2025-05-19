"""Configuration module for Tapo Chatter."""
import ipaddress
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from rich.console import Console

# Load environment variables from .env file if it exists
# load_dotenv() # This will be handled more specifically now

console = Console()


@dataclass
class IpRange:
    """Represents a range of IP addresses."""
    subnet: str
    start: int
    end: int

    @classmethod
    def from_string(cls, ip_range: str) -> 'IpRange':
        """Parse an IP range string into subnet and range components."""
        if '-' in ip_range:
            # Handle range format (e.g., "192.168.1.1-192.168.1.254")
            start_ip, end_ip = ip_range.split('-')
            start_parts = start_ip.split('.')
            end_parts = end_ip.split('.')

            # Ensure both IPs are in the same subnet
            if start_parts[:3] != end_parts[:3]:
                raise ValueError("IP range must be within the same subnet")

            subnet = '.'.join(start_parts[:3])
            start = int(start_parts[3])
            end = int(end_parts[3])

            return cls(subnet=subnet, start=start, end=end)
        elif '/' in ip_range:
            # Handle CIDR notation (e.g., "192.168.1.0/24")
            network = ipaddress.ip_network(ip_range)
            first_ip = network.network_address
            subnet = '.'.join(str(first_ip).split('.')[:3])
            return cls(subnet=subnet, start=1, end=254)  # Standard usable range for /24
        else:
            # Handle single IP (e.g., "192.168.1.100")
            parts = ip_range.split('.')
            if len(parts) != 4:
                raise ValueError("Invalid IP address format")
            subnet = '.'.join(parts[:3])
            octet = int(parts[3])
            return cls(subnet=subnet, start=octet, end=octet)


@dataclass
class TapoConfig:
    """Configuration for Tapo Chatter."""
    username: str
    password: str
    ip_address: Optional[str] = None
    ip_ranges: List[IpRange] = field(default_factory=list)

    def __post_init__(self):
        """Initialize default values after dataclass initialization."""
        if self.ip_ranges is None:
            self.ip_ranges = []

    @classmethod
    def from_env(cls) -> 'TapoConfig':
        """Load configuration from environment variables."""
        load_dotenv()

        # Required fields
        username = os.getenv('TAPO_USERNAME')
        password = os.getenv('TAPO_PASSWORD')

        if not username or not password:
            raise ValueError(
                "TAPO_USERNAME and TAPO_PASSWORD environment variables are required"
            )

        # Optional fields
        ip_address = os.getenv('TAPO_IP_ADDRESS')
        ip_range_str = os.getenv('TAPO_IP_RANGE')

        ip_ranges: List[IpRange] = []
        if ip_range_str:
            # Handle comma-separated ranges
            for range_part in ip_range_str.split(','):
                range_part = range_part.strip()
                if range_part:
                    ip_ranges.append(IpRange.from_string(range_part))

        return cls(
            username=username,
            password=password,
            ip_address=ip_address,
            ip_ranges=ip_ranges
        )

    def get_discovery_params(self) -> Tuple[Optional[str], Tuple[int, int]]:
        """Get the subnet and IP range for device discovery."""
        if not self.ip_ranges:
            # Default fallback
            return None, (1, 254)

        # For now, use the first range. In the future, we could scan multiple ranges
        first_range = self.ip_ranges[0]
        return first_range.subnet, (first_range.start, first_range.end)
