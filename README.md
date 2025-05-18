# Tapo H100 Device Lister

A Python application that connects to a TP-Link Tapo H100 Hub and lists all connected child devices with their status and details. This tool is particularly useful for managing and monitoring Tapo smart home devices connected to your H100 hub.

## Features

-   🔍 Discovers and lists all child devices connected to your H100 hub
-   📊 Displays detailed device information including:
    -   Device name and ID
    -   Device type
    -   Online/offline status
    -   Temperature (for compatible sensors)
    -   Humidity levels (for compatible sensors)
    -   Battery levels (for battery-powered devices)
-   🚦 Network connectivity checking
-   🔐 Secure authentication handling
-   📝 Detailed logging and debugging information

## Supported Devices

The application can detect and display information for various Tapo devices connected to your H100 hub, including:

-   T110 Contact Sensors
-   KE100 Radiator Controllers (TRV)
-   T100 Motion Sensors
-   S200B Smart Buttons
-   T300 Water Leak Sensors
-   T31x Temperature/Humidity Sensors

## Prerequisites

-   Python 3.11 or higher
-   [`uv`](https://github.com/astral-sh/uv) package manager
-   [`direnv`](https://direnv.net/) (recommended for environment management)
-   A Tapo account
-   A Tapo H100 Hub on your local network

## Installation

1. **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd tapo_chatter
    ```

2. **Set up Python Environment:**

    ```bash
    # Install uv if you haven't already
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Create and activate virtual environment
    python_setup 3.11
    ```

3. **Configure Environment Variables:**
   Create a `.env` file in the project root:

    ```bash
    TAPO_USERNAME="your_tapo_email@example.com"
    TAPO_PASSWORD="your_tapo_password"
    TAPO_IP_ADDRESS="your_h100_hub_ip_address"
    ```

    Or set them in your shell:

    ```bash
    export TAPO_USERNAME="your_tapo_email@example.com"
    export TAPO_PASSWORD="your_tapo_password"
    export TAPO_IP_ADDRESS="your_h100_hub_ip_address"
    ```

## Usage

Run the application:

```bash
python -m tapo_chatter.main
```

The application will:

1. Load your configuration
2. Check network connectivity to your hub
3. Initialize connection with the hub
4. Retrieve and display information about connected devices

## Troubleshooting

### Common Issues

1. **No Devices Found**

    - Verify your H100 hub is powered on and connected to your network
    - Confirm you're on the same local network as the hub
    - Check if the IP address is correct
    - Ensure your Tapo account has access to the hub

2. **Connection Errors**

    - Verify your network connectivity
    - Check if your firewall is blocking the connection
    - Confirm the hub's IP address hasn't changed
    - Try refreshing your Tapo account authentication

3. **Authentication Issues**
    - Double-check your Tapo username and password
    - Ensure your Tapo account has permissions for the hub
    - Try logging out and back in to the Tapo app

### Debug Mode

The application includes detailed debug output that can help identify issues:

-   Shows raw API responses
-   Displays detailed connection status
-   Provides information about data structure and parsing

## Development

### Project Structure

```
tapo_chatter/
├── src/
│   └── tapo_chatter/
│       ├── __init__.py
│       ├── main.py
│       └── config.py
├── .env
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
uv pip install pytest
pytest
```

### Code Style

The project uses ruff for linting and formatting:

```bash
# Install ruff
uv pip install ruff

# Check code
ruff check .

# Format code
ruff format .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

-   Built using the [Tapo Python Library](https://github.com/mihai-dinculescu/tapo)
-   Thanks to the TP-Link Tapo team for their smart home devices
