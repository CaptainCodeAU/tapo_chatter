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

### Cursor AI Codebase Understanding (Cursor Rules)

This project utilizes Cursor Rules (`.cursor/rules/*.mdc`) to provide the AI with a better understanding of the codebase structure, key files, and functionalities. These rules help in:

-   Faster navigation and context gathering.
-   More accurate code generation and modification.
-   Improved understanding of project-specific conventions.

The rules cover:

-   Project Overview
-   Main Module Structure (`src/tapo_chatter/main.py`)
-   Configuration Handling (`src/tapo_chatter/config.py`)
-   Testing Guide (`tests/`)
-   Dependencies and Development (`pyproject.toml`)
-   Device Data Processing (`src/tapo_chatter/`)
-   Linting Guide (`.cursor/rules/linting-guide.mdc`)
-   Formatting Guide (`.cursor/rules/formatting-guide.mdc`)
-   Docstring Guide (`.cursor/rules/docstring-guide.mdc`)
-   Commit Helper (`.cursor/rules/commit-helper.mdc`)

These rules are written in Markdown with Cursor-specific extensions and are automatically used by the Cursor AI when interacting with this project.

## Development

### Project Structure

```
tapo_chatter/
├── .cursor/
│   └── rules/
│       ├── commit-helper.mdc
│       ├── configuration-handling.mdc
│       ├── dependencies-and-development.mdc
│       ├── device-data-processing.mdc
│       ├── docstring-guide.mdc
│       ├── formatting-guide.mdc
│       ├── linting-guide.mdc
│       ├── main-module-structure.mdc
│       ├── project-overview.mdc
│       └── testing-guide.mdc
├── src/
│   └── tapo_chatter/
│       ├── __init__.py
│       ├── main.py
│       └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_main.py
│   ├── test_main_entry.py
│   └── check_coverage.py
├── .env
├── pyproject.toml
└── README.md
```

### Running Tests

The project has a comprehensive test suite with over 99% code coverage. To run the tests:

```bash
# Install test dependencies
uv pip install pytest pytest-asyncio pytest-cov

# Run all tests
python -m pytest

# Run tests with coverage report
python tests/check_coverage.py

# Run specific test files
python -m pytest tests/test_config.py
python -m pytest tests/test_main.py

# Run a specific test function
python -m pytest tests/test_main.py::test_check_host_connectivity_success

# Run tests with verbose output
python -m pytest -v
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

## Testing

### Code Coverage

The project maintains high code coverage (>99%) to ensure reliability and stability. We use pytest and pytest-cov for testing and coverage reporting.

To check the current test coverage:

```bash
python tests/check_coverage.py
```

### Test Organization

The test suite is organized into several files:

-   `test_config.py`: Tests for the configuration module, including environment variable handling, validation, and error cases.
-   `test_main.py`: Comprehensive tests for the main module, including device discovery, connectivity checks, and output formatting.
-   `test_main_entry.py`: Tests for ensuring the entry point logic works correctly when the module is run directly.
-   Additional helper scripts for testing the main module's entry point behavior.

### Running the Application in Test Mode

You can run the application with mock data for testing purposes:

```bash
# With environment variables
TAPO_USERNAME="test@example.com" TAPO_PASSWORD="test_password" TAPO_IP_ADDRESS="127.0.0.1" python -m src.tapo_chatter.main

# Using different methods
python -m src.tapo_chatter.main  # As a module
python src/tapo_chatter/main.py  # Directly
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

-   Built using the [Tapo Python Library](https://github.com/mihai-dinculescu/tapo)
-   Thanks to the TP-Link Tapo team for their smart home devices
