# Tapo H100 Device Lister

A Python application that connects to a TP-Link Tapo H100 Hub and lists all connected child devices with their status and details. This tool is particularly useful for managing and monitoring Tapo smart home devices connected to your H100 hub, now with real-time status updates.

## Features

### Tapo H100 Hub Monitor (`tapo-chatter`)

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
-   🔄 **Real-time Monitoring:** Continuously polls the hub at a set interval (default: 10 seconds) and refreshes the device display, allowing you to see live status changes, including devices going offline.
-   📝 Debugging information available through code modification if deeper inspection is needed.

### Network Device Discovery Tool (`tapo-discover`)

-   🔎 **Auto Network Detection:** Automatically identifies your local network subnet.
-   ⚡ **Parallel Scanning:** Concurrently probes multiple IP addresses for faster discovery.
-   🚀 **Optimized for Speed:** Higher default concurrency (20) and lower timeout (0.5s) for faster scanning.
-   🎯 **Early Stopping:** Ability to stop scanning after finding a specific number of devices.
-   🎚️ **Configurable Scanning:** Customize subnet, IP range, concurrency limit, and timeout.
-   📋 **Detailed Device Information:** Displays comprehensive information about discovered devices, including:
    -   IP Address
    -   Device Name
    -   Model
    -   Type
    -   Connection Status (Online/Offline) or Power State (On/Off) depending on device type
    -   Signal Level (Color-coded)
    -   MAC Address
-   🔁 **Thread Management:** Uses semaphores to limit concurrent connections, preventing network overload.
-   📊 **JSON Output Option:** Export discovery results in JSON format for further processing.
-   🔍 **Improved Error Handling:** Verbose mode now provides a structured summary of connection errors by type instead of raw error messages.
-   📝 **Scan Statistics:** Shows comprehensive scan information including IPs scanned and error count.

## Supported Devices

The application can detect and display information for various Tapo devices connected to your H100 hub, including:

-   T110 Contact Sensors
-   KE100 Radiator Controllers (TRV)
-   T100 Motion Sensors
-   S200B Smart Buttons
-   T300 Water Leak Sensors
-   T31x Temperature/Humidity Sensors

## Prerequisites

-   Python 3.13+ installed.
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
   The application requires your Tapo username (email), password, and the IP address of your H100 hub.
   These can be configured in several ways, with the following order of precedence (highest first):

    1. **Shell Environment Variables:** Export `TAPO_USERNAME`, `TAPO_PASSWORD`, and `TAPO_IP_ADDRESS` in your shell.
    2. **User-Specific `.env` File:** Create a file named `.env` in the application\'s user-specific configuration directory. This is the recommended way for `pipx` users or for a global setup.
        - **Linux/macOS:** `~/.config/tapo_chatter/.env`
        - **Windows:** Typically `C:\Users\<YourUser>\AppData\Roaming\tapo_chatter\Config\.env` (The application will create the `tapo_chatter` directory if it doesn\'t exist; you just need to create the `.env` file inside it).
          You can find the exact path for your system if the application fails to find the configuration variables as it will be printed in the error message.
    3. **Local Project `.env` File:** Create a file named `.env` in your project\'s root directory (or any parent directory from where you run the command if not installed).

    **Example `.env` file content:**

    ```.env
    TAPO_USERNAME="your_tapo_email@example.com"
    TAPO_PASSWORD="your_tapo_password"
    TAPO_IP_ADDRESS="your_h100_hub_ip_address"
    ```

    **Note on Configuration for `pipx` users:**
    After installing with `pipx`, `tapo-chatter` will be available globally. To configure credentials, it is recommended to create a `.env` file in the user-specific configuration directory mentioned in step 3 (Configure Environment Variables) above. For example:

    - **Linux/macOS:** `~/.config/tapo_chatter/.env`
    - **Windows:** `C:\Users\<YourUser>\AppData\Roaming\tapo_chatter\Config\.env` (or similar path indicated by `platformdirs`)
      Alternatively, you can set `TAPO_USERNAME`, `TAPO_PASSWORD`, and `TAPO_IP_ADDRESS` as system environment variables in your shell.

**4. Installing the Package:**

You have a few options to install and use `tapo-chatter`:

-   **For Development (Editable Install):**
    If you plan to modify the code, it's best to do an editable install from your local clone. This way, changes to the source code are immediately reflected.
    Navigate to the project's root directory:

    ```bash
    # Using pip
    pip install -e .
    # Or using uv
    # uv pip install -e .
    ```

-   **Standard Local Install:**
    To install the package as it is from your local clone (changes won't reflect without re-installation):
    Navigate to the project's root directory:

    ```bash
    # Using pip
    pip install .
    # Or using uv
    # uv pip install .
    ```

-   **Installing from GitHub (for end-users or collaborators):**
    Once the project is pushed to a public GitHub repository (e.g., `https://github.com/yourusername/tapo_chatter`), others can install it directly using pip:
    ```bash
    pip install git+https://github.com/yourusername/tapo_chatter.git
    ```
    Replace `yourusername` with the actual GitHub username and `tapo_chatter` with the repository name if it differs.
    To install a specific version or branch, append `@<tag_name_or_branch_name>` to the URL:
    ```bash
    pip install git+https://github.com/yourusername/tapo_chatter.git@v0.1.0
    ```

*   **Installing with `pipx` (Recommended for CLI tools):**
    `pipx` installs Python applications into isolated environments, which is great for CLI tools.
    First, ensure you have `pipx` installed (see [pipx installation guide](https://pypa.github.io/pipx/installation/)).
    Then, you can install `tapo-chatter` directly from GitHub:
    ```bash
    pipx install git+https://github.com/yourusername/tapo_chatter.git
    ```
    To install a specific version:
    ```bash
    pipx install git+https://github.com/yourusername/tapo_chatter.git@v0.1.0
    ```
    **Note on Configuration for `pipx` users:**
    After installing with `pipx`, `tapo-chatter` will be available globally. You'll need to ensure the required environment variables (`TAPO_USERNAME`, `TAPO_PASSWORD`, `TAPO_IP_ADDRESS`) are set. You can do this by:
    1.  Creating a `.env` file in the directory from which you run the `tapo-chatter` command (or any parent directory).
    2.  Setting these as system environment variables in your shell (e.g., in your `.bashrc` or `.zshrc`).

## Usage

The application will connect to your Tapo H100 hub, retrieve information about connected child devices, and display it in your console. With the new real-time monitoring feature, the display will automatically refresh every 10 seconds.

**1. Ensure Prerequisites are Met:**

-   Python 3.13+ installed.
-   Environment variables (`TAPO_USERNAME`, `TAPO_PASSWORD`, `TAPO_IP_ADDRESS`) are set either in a `.env` file in the project root or exported in your shell. Refer to the "Installation" section for details on setting these up.
-   Your Tapo H100 hub is online and on the same network.

**2. Running the Application:**

After ensuring prerequisites and installation (see section "4. Installing the Package" above), you can run the application:

-   **Directly via Python (if you haven\'t installed the package or are in a development environment where you used `pip install -e .`):**
    Navigate to the project\'s root directory in your terminal and run:

    ```bash
    python -m src.tapo_chatter.main
    ```

    Alternatively:

    ```bash
    python src/tapo_chatter/main.py
    ```

-   **As an Installed Console Script (if you installed the package, e.g., via `pip install .` or `pip install git+...`):**
    You can run the application from anywhere by simply typing:
    ```bash
    tapo-chatter
    ```

**Stopping the Application:**
In either mode, press `Ctrl+C` to stop the real-time monitoring and exit the application.

The application will:

1. Load your configuration
2. Check network connectivity to your hub
3. Initialize connection with the hub
4. Retrieve and display information about connected devices

**3. Using the Device Discovery Tool:**

The package also includes a tool to discover Tapo devices on your local network by scanning IP addresses in parallel:

-   **Run the discovery tool:**

    ```bash
    tapo-discover
    ```

-   **Customize discovery options:**

    ```bash
    # Specify subnet to scan
    tapo-discover --subnet 192.168.0

    # Limit IP range to scan (last octet)
    tapo-discover --range 50-100

    # Adjust concurrency and timeout for faster scanning
    tapo-discover --limit 30 --timeout 0.3

    # Stop scanning after finding a specific number of devices
    tapo-discover --num-devices 5

    # Output results in JSON format
    tapo-discover --json

    # Enable cleaner error summary report
    tapo-discover --verbose

    # Combine multiple options for optimized scanning
    tapo-discover --subnet 192.168.107 --range 220-230 --timeout 0.3 --limit 30 --num-devices 3 --verbose
    ```

-   **Full help information:**
    ```bash
    tapo-discover --help
    ```

The discovery tool:

1. Auto-detects your network subnet
2. Scans for Tapo devices on your local network
3. Displays detailed information about discovered devices
4. Shows connection status for hubs/sensors and power state for plugs/bulbs
5. Provides scan statistics showing total IPs scanned and connection errors
6. With verbose mode, displays categorized error summary for network troubleshooting

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

### Network Scan Error Summary

When running the discovery tool with the `--verbose` flag, you'll see a clean, organized table of error types instead of raw error messages:

```
Connection Statistics:
                      Network Scan Results
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error Type            ┃ Count ┃ Description                             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Timeout               │ 94    │ Normal timeouts from non-responsive IPs │
│ Connection Refused    │ 5     │ Device refused connection (port closed) │
│ Network Unreachable   │ 3     │ Network segment unreachable             │
│ Hash Mismatch         │ 2     │ Security hash mismatch (non-Tapo device)│
└────────────────────────┴───────┴─────────────────────────────────────────┘
```

This summary helps you understand network connectivity issues without overwhelming you with technical error messages.

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
│       ├── config.py
│       ├── device_discovery.py
│       └── discover.py
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
