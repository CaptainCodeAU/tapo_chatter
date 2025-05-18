"""Configuration module for Tapo Chatter."""
import os
import re
from dataclasses import dataclass
from typing import Optional, cast

from dotenv import load_dotenv
from rich.console import Console

# Load environment variables from .env file if it exists
load_dotenv()

console = Console()


@dataclass
class TapoConfig:
    """Configuration for Tapo device interaction."""
    username: str
    password: str
    ip_address: str

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """Validate IP address format."""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        return all(0 <= int(part) <= 255 for part in ip.split('.'))

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @classmethod
    def from_env(cls) -> "TapoConfig":
        """Create a config instance from environment variables."""
        username = os.getenv("TAPO_USERNAME")
        password = os.getenv("TAPO_PASSWORD")
        ip_address = os.getenv("TAPO_IP_ADDRESS")

        # Check for missing variables
        missing = [
            name for name, value in {
                "TAPO_USERNAME": username,
                "TAPO_PASSWORD": password,
                "TAPO_IP_ADDRESS": ip_address
            }.items() if not value
        ]
        
        if missing:
            console.print("[red]Configuration Error:[/red]")
            console.print("Missing required environment variables:")
            for var in missing:
                console.print(f"  • {var}")
            console.print("\nPlease set these variables in your environment or .env file")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        # Validate username format (should be an email)
        if not cls.is_valid_email(cast(str, username)):
            console.print("[red]Configuration Error:[/red]")
            console.print(f"Invalid email format for TAPO_USERNAME: {username}")
            console.print("The username should be a valid email address")
            raise ValueError(f"Invalid email format for TAPO_USERNAME: {username}")

        # Validate IP address format
        if not cls.is_valid_ip(cast(str, ip_address)):
            console.print("[red]Configuration Error:[/red]")
            console.print(f"Invalid IP address format: {ip_address}")
            console.print("The IP address should be in the format: xxx.xxx.xxx.xxx")
            console.print("Each number should be between 0 and 255")
            raise ValueError(f"Invalid IP address format: {ip_address}")

        # At this point we know these values are valid
        return cls(
            username=cast(str, username),
            password=cast(str, password),
            ip_address=cast(str, ip_address)
        ) 