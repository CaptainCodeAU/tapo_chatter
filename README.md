# Tapo H100 Device Lister

A Python application that connects to a TP-Link Tapo H100 Hub and lists all connected child devices with their status and details. This tool is particularly useful for managing and monitoring Tapo smart home devices connected to your H100 hub.

## Features

-   🔍 Discovers and lists all child devices connected to your H100 hub.
-   📊 Displays device information across two detailed tables:
    -   **Additional Device Information Table:**
        -   Device Name
        -   Hardware Version (HW Ver)
        -   MAC Address
        -   Region
        -   Signal Level
        -   Battery Status (OK/Low)
        -   Jamming RSSI (Color-coded: Green for good, Yellow for fair, Red for poor)
        -   Report Interval (s)
        -   Last Onboarded Timestamp
    -   **Main Device Status Table:**
        -   Device Name
        -   Device ID
        -   Device Type
        -   Online/Offline Status
        -   RSSI (Received Signal Strength Indicator, color-coded: Green for good, Yellow for fair, Red for poor)
        -   Details: Sensor-specific status (e.g., "Motion: Clear", "Contact: Closed").
            -   Critical states like "Motion: Detected" and "Contact: Open" are highlighted in bold red.
            -   Temperature and Humidity levels are shown here for compatible sensors (e.g., T31x).
-   🚦 Network connectivity checking to the hub.
-   🔐 Secure authentication handling (credentials are not displayed in logs or console during normal operation).
-   📊 Enhanced error reporting and more robust device data parsing.
-   📝 Debugging information available through code modification if deeper inspection is needed.

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

The application's code contains commented-out sections (primarily in `src/tapo_chatter/main.py`) that can be re-enabled to provide detailed debug output. This includes:

-   Raw API responses from the Tapo Hub.
-   Detailed data structures after processing.
-   Connection status messages.

This debug output can be helpful for identifying issues or understanding the data flow if you encounter problems or wish to extend the application.

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
uv pip install pytest pytest-asyncio
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
