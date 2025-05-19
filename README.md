# Tapo Chatter

A comprehensive Python application for managing, monitoring, and discovering TP-Link Tapo smart home devices, with special focus on the H100 Hub ecosystem and its connected child devices.

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
-   🔄 **Hub Child Device Detection:** Automatically detects Tapo Hubs and shows all connected child devices with detailed status information
-   🔁 **Thread Management:** Uses semaphores to limit concurrent connections, preventing network overload.
-   📊 **JSON Output Option:** Export discovery results in JSON format for further processing.
-   🔍 **Improved Error Handling:** Verbose mode now provides a structured summary of connection errors by type instead of raw error messages.
-   📝 **Scan Statistics:** Shows comprehensive scan information including IPs scanned and error count.

## Supported Devices

The application can detect and display information for various Tapo devices on your network, including:

-   H100 Hub and all connected child devices
-   T110 Contact Sensors
-   KE100 Radiator Controllers (TRV)
-   T100 Motion Sensors
-   S200B Smart Buttons
-   T300 Water Leak Sensors
-   T31x Temperature/Humidity Sensors
-   P100/P110 Smart Plugs
-   L510/L530 Smart Bulbs
-   And other compatible Tapo smart home devices

## Prerequisites

-   Python 3.13+ installed.
-   [`uv`](https://github.com/astral-sh/uv) package manager
-   [`direnv`](https://direnv.net/) (recommended for environment management)
-   A Tapo account
-   A Tapo H100 Hub or other Tapo devices on your local network

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
    python_setup 3.13
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

### H100 Hub Monitor

Run the monitor to view connected devices to your H100 hub:

```bash
tapo-chatter
```

The application will:

1. Load your configuration
2. Check network connectivity to your hub
3. Initialize connection with the hub
4. Retrieve and display information about connected devices
5. Continuously update the display every 10 seconds

**Stopping the Application:**
Press `Ctrl+C` to stop the real-time monitoring and exit the application.

### Device Discovery Tool

The package includes a powerful tool to discover all Tapo devices on your local network:

```bash
tapo-discover
```

**Customize discovery options:**

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

# Skip fetching child devices from discovered hubs
tapo-discover --no-children
```

## Troubleshooting

If you encounter issues:

1. **Connectivity Problems:**

    - Verify you're on the same network as your Tapo devices
    - Check if your firewall is blocking connections
    - Confirm the IP address of your hub is correct

2. **Authentication Issues:**

    - Check your Tapo username and password
    - Verify you're using the email address associated with your Tapo account

3. **Device Not Showing:**
    - Ensure the device is powered on and connected to your network
    - Try rebooting the device
    - Check if the device is visible in the official Tapo app

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

-   Built using the [Tapo Python Library](https://github.com/mihai-dinculescu/tapo)
-   Thanks to the TP-Link Tapo team for their smart home devices
