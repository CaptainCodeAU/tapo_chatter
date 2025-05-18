"""Configuration module for Tapo Chatter."""
import os
import re
from dataclasses import dataclass
from typing import Optional, cast
from pathlib import Path
import sys

from dotenv import load_dotenv, dotenv_values, find_dotenv
import platformdirs
from rich.console import Console

# Load environment variables from .env file if it exists
# load_dotenv() # This will be handled more specifically now

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

        # Define paths for .env files
        # User-specific config directory (e.g., ~/.config/tapo_chatter/.env)
        user_config_dir = Path(platformdirs.user_config_dir("tapo_chatter", appauthor=False))
        user_config_env_path = user_config_dir / ".env"

        # Ensure user config directory exists for guidance, but don't fail if not writable yet
        try:
            user_config_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # If we can't create it (e.g., permissions), we'll still proceed.
            # The paths will be used in error messages later.
            pass 

        # Local .env path (searches CWD and parents)
        local_env_path_str = find_dotenv(usecwd=True, raise_error_if_not_found=False)

        # Load configuration with precedence: Shell Env > User-specific .env > Local .env
        # 1. Start with an empty dictionary for file-based configs
        file_configs = {}

        # 2. Load from local .env file if found
        if local_env_path_str and Path(local_env_path_str).exists():
            file_configs.update(dotenv_values(local_env_path_str))
        
        # 3. Load from user-specific .env file if found (overrides local .env values)
        if user_config_env_path.exists():
            file_configs.update(dotenv_values(user_config_env_path))

        # 4. Get final values, prioritizing os.getenv (shell) over file_configs
        username = os.getenv("TAPO_USERNAME") or file_configs.get("TAPO_USERNAME")
        password = os.getenv("TAPO_PASSWORD") or file_configs.get("TAPO_PASSWORD")
        ip_address = os.getenv("TAPO_IP_ADDRESS") or file_configs.get("TAPO_IP_ADDRESS")

        # Check for missing variables
        missing = []
        if not username:
            missing.append("TAPO_USERNAME")
        if not password:
            missing.append("TAPO_PASSWORD")
        if not ip_address:
            missing.append("TAPO_IP_ADDRESS")
        
        if missing:
            console.print("[red]Configuration Error:[/red]")
            console.print("Missing required environment variables:")
            for var in missing:
                console.print(f"  • {var}")
            console.print("\nPlease set these variables in your shell environment, or in one of the following .env files:")
            console.print(f"  1. User-specific global config: [cyan]{user_config_env_path}[/cyan]")
            if local_env_path_str:
                console.print(f"  2. Local project config: [cyan]{local_env_path_str}[/cyan]")
            else:
                console.print(f"  2. Local project config: .env (in your project directory)")
            console.print("\nExample .env file content:")
            console.print("TAPO_USERNAME=\"your_tapo_email@example.com\"")
            console.print("TAPO_PASSWORD=\"your_tapo_password\"")
            console.print("TAPO_IP_ADDRESS=\"your_h100_hub_ip_address\"")
            sys.exit(1)

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