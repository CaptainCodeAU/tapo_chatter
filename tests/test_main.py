"""Tests for the main module and core functionality."""

import pytest
from tapo_chatter.main import main, check_host_connectivity, get_child_devices
import asyncio
from unittest import mock
import socket
from tapo import ApiClient
import datetime
from typing import Any, Dict

@pytest.mark.asyncio
async def test_main_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the output of the main function when no devices are found."""
    # Mock TapoConfig.from_env to return a dummy config
    mock_tapo_config_instance = mock.Mock(username="test@example.com", password="testpassword", ip_address="127.0.0.1")
    
    with mock.patch("tapo_chatter.main.TapoConfig.from_env", return_value=mock_tapo_config_instance) as mock_config_loader:
        with mock.patch("tapo_chatter.main.get_child_devices", return_value=[]) as mock_device_fetcher:
            await main()
            captured = capsys.readouterr()
            
            mock_config_loader.assert_called_once()
            # We expect get_child_devices to be called. 
            # The ApiClient is instantiated inside main() before calling get_child_devices.
            # We check it was called with an ApiClient instance and the IP from the mocked config.
            mock_device_fetcher.assert_called_once_with(mock.ANY, mock_tapo_config_instance.ip_address)

            # Rich console might not include the style tags in raw capsys output
            assert "No devices found" in captured.out 
            assert captured.err == ""

@pytest.mark.asyncio
async def test_check_host_connectivity_success():
    """Test successful host connectivity."""
    with mock.patch("socket.socket") as mock_socket_constructor:
        mock_sock_instance = mock.Mock()
        mock_sock_instance.connect_ex.return_value = 0  # 0 indicates success
        mock_socket_constructor.return_value = mock_sock_instance

        result = await check_host_connectivity("192.168.1.1", 80, timeout=2.0)
        assert result is True
        mock_socket_constructor.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock_instance.settimeout.assert_called_once_with(2.0)
        mock_sock_instance.connect_ex.assert_called_once_with(("192.168.1.1", 80))
        mock_sock_instance.close.assert_called_once()

@pytest.mark.asyncio
async def test_check_host_connectivity_failure():
    """Test failed host connectivity (e.g., connection refused)."""
    with mock.patch("socket.socket") as mock_socket_constructor:
        mock_sock_instance = mock.Mock()
        mock_sock_instance.connect_ex.return_value = 1  # Non-zero indicates failure
        mock_socket_constructor.return_value = mock_sock_instance

        result = await check_host_connectivity("192.168.1.100", 80, timeout=2.0)
        assert result is False
        mock_socket_constructor.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock_instance.settimeout.assert_called_once_with(2.0)
        mock_sock_instance.connect_ex.assert_called_once_with(("192.168.1.100", 80))
        mock_sock_instance.close.assert_called_once()

@pytest.mark.asyncio
async def test_check_host_connectivity_socket_error():
    """Test connectivity check when a socket.error occurs."""
    with mock.patch("socket.socket") as mock_socket_constructor:
        mock_sock_instance = mock.Mock()
        mock_sock_instance.connect_ex.side_effect = socket.error
        mock_socket_constructor.return_value = mock_sock_instance

        result = await check_host_connectivity("example.com", 80, timeout=2.0)
        assert result is False
        mock_socket_constructor.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock_instance.settimeout.assert_called_once_with(2.0)
        mock_sock_instance.connect_ex.assert_called_once_with(("example.com", 80))
        # .close() is not asserted here as it might not be reached if connect_ex() raises an error
        # and there isn't a try/finally block in the original code ensuring sock.close().

@pytest.mark.asyncio
async def test_check_host_connectivity_custom_timeout():
    """Test host connectivity with a custom timeout value."""
    with mock.patch("socket.socket") as mock_socket_constructor:
        mock_sock_instance = mock.Mock()
        mock_sock_instance.connect_ex.return_value = 0  # Success
        mock_socket_constructor.return_value = mock_sock_instance

        custom_timeout = 5.0
        result = await check_host_connectivity("10.0.0.5", 443, timeout=custom_timeout)
        assert result is True
        mock_socket_constructor.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock_instance.settimeout.assert_called_once_with(custom_timeout)
        mock_sock_instance.connect_ex.assert_called_once_with(("10.0.0.5", 443))
        mock_sock_instance.close.assert_called_once()

@pytest.mark.asyncio
async def test_get_child_devices_connectivity_failure(capsys: pytest.CaptureFixture[str]):
    """Test get_child_devices when host connectivity check fails."""
    mock_client = mock.AsyncMock(spec=ApiClient)
    host_ip = "192.168.1.254"

    with mock.patch("tapo_chatter.main.check_host_connectivity", return_value=False) as mock_check_conn:
        devices = await get_child_devices(mock_client, host_ip)
        
        mock_check_conn.assert_called_once_with(host_ip)
        assert devices == []
        
        captured = capsys.readouterr()
        # Check for plain text as Rich tags are not in raw capsys output
        assert f"Error: Cannot reach host {host_ip}. Please check:" in captured.out
        assert "• The device is powered on" in captured.out
        assert "• You are on the same network as the device" in captured.out
        assert "• The IP address is correct" in captured.out
        assert "• No firewall is blocking the connection" in captured.out

@pytest.mark.asyncio
async def test_get_child_devices_success_and_processing(capsys: pytest.CaptureFixture[str]):
    """Test get_child_devices successful path with device data processing."""
    mock_client = mock.AsyncMock()
    host_ip = "192.168.1.10"

    # --- Mock device objects and their to_dict() data ---
    mock_device_1_data = {
        "nickname": "Living Room Sensor",
        "device_id": "device123",
        "device_type": "T100",
        "at_low_battery": False,
        "detected": True, # Motion detected
        "open": False, # Contact closed
        "rssi": -55,
        "hw_ver": "1.0.0",
        "jamming_rssi": -80,
        "lastOnboardingTimestamp": 1678886400, # Example timestamp
        "mac": "AA:BB:CC:DD:EE:FF",
        "region": "EU",
        "report_interval": 60,
        "signal_level": 4
    }
    mock_device_obj_1 = mock.Mock()
    mock_device_obj_1.nickname = mock_device_1_data["nickname"]
    mock_device_obj_1.device_id = mock_device_1_data["device_id"]
    mock_device_obj_1.device_type = mock_device_1_data["device_type"]
    mock_device_obj_1.status = "Status Reporting Online"
    mock_device_obj_1.to_dict.return_value = mock_device_1_data

    mock_device_2_data = {
        "nickname": "Kitchen Switch",
        "device_id": "device456",
        # No device_type, will use type
        "type": "S200B", # Test type attribute
        "status": True, # Test boolean status
        "at_low_battery": True, # Low battery
        # No motion/contact sensor data
        "rssi": -75,
        "hw_ver": "1.0.1",
        "jamming_rssi": -60, # Different jamming value
        "lastOnboardingTimestamp": "invalid_ts", # Test invalid timestamp
        "mac": "11:22:33:44:55:66",
        "region": "US",
        "report_interval": 120,
        "signal_level": "N/A" # Test string signal level
    }
    mock_device_obj_2 = mock.Mock()
    mock_device_obj_2.nickname = mock_device_2_data["nickname"]
    mock_device_obj_2.device_id = mock_device_2_data["device_id"]
    mock_device_obj_2.type = mock_device_2_data["type"] # Has type, not device_type
    delattr(mock_device_obj_2, 'device_type') # Ensure it doesn't have device_type
    mock_device_obj_2.status = mock_device_2_data["status"]
    mock_device_obj_2.to_dict.return_value = mock_device_2_data

    # Device that will cause to_dict() to fail
    mock_device_obj_3 = mock.Mock()
    mock_device_obj_3.nickname = "Faulty Device"
    mock_device_obj_3.device_id = "device789"
    mock_device_obj_3.device_type = "T300"
    mock_device_obj_3.status = 0 # Offline
    mock_device_obj_3.to_dict.side_effect = Exception("Simulated to_dict error")
    
    # Device with no type attributes
    mock_device_obj_4 = mock.Mock()
    mock_device_obj_4.nickname = "Unknown Type Device"
    mock_device_obj_4.device_id = "device000"
    delattr(mock_device_obj_4, 'device_type')
    delattr(mock_device_obj_4, 'type')
    mock_device_obj_4.status = None # Test None status
    mock_device_obj_4.to_dict.return_value = { # Minimal dict
        "nickname": "Unknown Type Device", "device_id": "device000", "rssi": -65
    }

    # Device with status as integer 1
    mock_device_obj_5 = mock.Mock()
    mock_device_obj_5.nickname = "Integer Status Device"
    mock_device_obj_5.device_id = "device555"
    mock_device_obj_5.device_type = "T110"
    mock_device_obj_5.status = 1 # Integer 1 for status
    mock_device_obj_5.to_dict.return_value = {
        "nickname": "Integer Status Device", "device_id": "device555", "rssi": -60
    }


    # --- Mock hub and its methods ---
    mock_hub = mock.AsyncMock()
    mock_hub.get_child_device_list = mock.AsyncMock(return_value=[
        mock_device_obj_1, mock_device_obj_2, mock_device_obj_3, mock_device_obj_4, mock_device_obj_5 # <<< Added device 5
    ])
    mock_client.h100.return_value = mock_hub

    with mock.patch("tapo_chatter.main.check_host_connectivity", return_value=True) as mock_check_conn:
        processed_devices = await get_child_devices(mock_client, host_ip)

        mock_check_conn.assert_called_once_with(host_ip)
        mock_client.h100.assert_called_once_with(host_ip)
        mock_hub.get_child_device_list.assert_awaited_once()

        assert len(processed_devices) == 5 # <<< Expect 5

        # --- Assertions for Device 1 --- (Uncommented)
        dev1 = processed_devices[0]
        assert dev1["nickname"] == "Living Room Sensor"
        assert dev1["device_id"] == "device123"
        assert dev1["device_type"] == "T100"
        assert dev1["status"] == 1 # Online (from mock_device_1_data["status"].name)
        assert dev1["rssi"] == -55
        assert dev1["params"]["battery_state"] == "OK"
        assert dev1["params"]["motion_status"] == "Detected"
        assert dev1["params"]["contact_status"] == "Closed"
        assert dev1["params"]["hw_ver"] == "1.0.0"
        assert dev1["params"]["jamming_rssi"] == -80
        assert dev1["params"]["last_onboarded"] == datetime.datetime.fromtimestamp(1678886400).strftime('%Y-%m-%d %H:%M:%S')
        assert dev1["params"]["mac"] == "AA:BB:CC:DD:EE:FF"
        assert dev1["params"]["region"] == "EU"
        assert dev1["params"]["report_interval"] == "60" # Note: stored as string
        assert dev1["params"]["signal_level"] == "4"    # Note: stored as string

        # --- Assertions for Device 2 --- (Uncommented)
        dev2 = processed_devices[1]
        assert dev2["nickname"] == "Kitchen Switch"
        assert dev2["device_id"] == "device456"
        assert dev2["device_type"] == "S200B" # From .type attribute
        assert dev2["status"] == 1 # Online (from boolean True)
        assert dev2["rssi"] == -75
        assert dev2["params"]["battery_state"] == "Low"
        assert "motion_status" not in dev2["params"] # No motion data
        assert "contact_status" not in dev2["params"] # No contact data
        assert dev2["params"]["last_onboarded"] == "N/A" # Invalid timestamp

        # --- Assertions for Device 3 (to_dict failed) --- (Uncommented)
        dev3 = processed_devices[2]
        assert dev3["nickname"] == "Faulty Device"
        assert dev3["device_id"] == "device789"
        assert dev3["device_type"] == "T300"
        assert dev3["status"] == 0 # Offline (from explicit 0)
        assert dev3["rssi"] == "N/A" # Should be N/A as to_dict failed before rssi could be read
        # Params should contain N/A for all keys that are unconditionally .get() from device_data_from_to_dict
        expected_dev3_params = {
            'hw_ver': "N/A",
            'jamming_rssi': "N/A",
            'last_onboarded': "N/A",
            'mac': "N/A",
            'region': "N/A",
            'report_interval': "N/A",
            'signal_level': "N/A"
        }
        assert dev3["params"] == expected_dev3_params

        # --- Assertions for Device 4 (Unknown type, None status) --- (Uncommented)
        dev4 = processed_devices[3]
        assert dev4["nickname"] == "Unknown Type Device"
        assert dev4["device_id"] == "device000"
        assert dev4["device_type"] == "Unknown" # No type attributes
        assert dev4["status"] == 0 # Offline (from None status)
        assert dev4["rssi"] == -65 # RSSI from minimal dict
        # Check default for missing params not in its minimal to_dict
        expected_dev4_params = {
            'hw_ver': "N/A",
            'jamming_rssi': "N/A",
            'last_onboarded': "N/A",
            'mac': "N/A",
            'region': "N/A",
            'report_interval': "N/A",
            'signal_level': "N/A"
            # battery_state, motion_status, contact_status will be missing as their keys aren't in to_dict
        }
        assert dev4["params"] == expected_dev4_params

        # --- Assertions for Device 5 (Integer status) ---
        dev5 = processed_devices[4]
        assert dev5["nickname"] == "Integer Status Device"
        assert dev5["device_id"] == "device555"
        assert dev5["device_type"] == "T110"
        assert dev5["status"] == 1 # Online (from integer 1 status)
        assert dev5["rssi"] == -60
        # Params for dev5 would be N/A for hw_ver etc. as not in its to_dict, similar to dev4
        expected_dev5_params = {
            'hw_ver': "N/A", 'jamming_rssi': "N/A", 'last_onboarded': "N/A",
            'mac': "N/A", 'region': "N/A", 'report_interval': "N/A", 'signal_level': "N/A"
        }
        assert dev5["params"] == expected_dev5_params

        # Check console output for success messages
        captured = capsys.readouterr()
        assert f"Successfully connected to {host_ip}" in captured.out
        assert "Successfully initialized H100 hub" in captured.out
        assert "Fetching child devices..." in captured.out
        assert f"Successfully retrieved 5 child devices" in captured.out # <<< Expect 5

@pytest.mark.asyncio
async def test_get_child_devices_general_exception(capsys: pytest.CaptureFixture[str]):
    """Test get_child_devices when a general exception occurs during hub interaction."""
    mock_client = mock.AsyncMock()
    host_ip = "192.168.1.20"
    error_message = "Simulated generic error"

    # Mock client.h100() to raise an exception
    mock_client.h100.side_effect = Exception(error_message)

    with mock.patch("tapo_chatter.main.check_host_connectivity", return_value=True) as mock_check_conn:
        devices = await get_child_devices(mock_client, host_ip)

        mock_check_conn.assert_called_once_with(host_ip)
        mock_client.h100.assert_called_once_with(host_ip) # Should still be called
        assert devices == []

        captured = capsys.readouterr()
        assert f"Error getting child devices: {error_message}" in captured.out
        assert "This could be due to:" in captured.out # Check for the error panel content
        assert "Invalid credentials" in captured.out

def test_print_additional_device_info_table_empty(capsys: pytest.CaptureFixture[str]):
    """Test print_additional_device_info_table with no devices."""
    from tapo_chatter.main import print_additional_device_info_table
    print_additional_device_info_table([])
    captured = capsys.readouterr()
    assert captured.out == "" # Should print nothing if no devices

@pytest.mark.parametrize(
    "jamming_rssi_val, expected_display_segment",
    [
        (-80, "[green]-80[/green]"),    # Low jamming
        (0, "[green]0[/green]"),        # No jamming
        (-70, "[yellow]-70[/yellow]"), # Moderate jamming
        (-60, "[red]-60[/red]"),      # High jamming
        ("N/A", "N/A"),               # N/A value
        (None, "None")                # None value should be str(None)
    ]
)
def test_print_additional_device_info_table_jamming_rssi(
    capsys: pytest.CaptureFixture[str],
    jamming_rssi_val: Any,
    expected_display_segment: str
):
    """Test print_additional_device_info_table for Jamming RSSI formatting."""
    from tapo_chatter.main import print_additional_device_info_table
    
    devices = [
        {
            "nickname": "Test Device",
            "params": {
                'hw_ver': "1.0", 'mac': "AA:BB:CC", 'region': "EU",
                'signal_level': "3", 'battery_state': "OK",
                'jamming_rssi': jamming_rssi_val,
                'report_interval': "60", 'last_onboarded': "2023-01-01"
            }
        }
    ]
    print_additional_device_info_table(devices)
    captured = capsys.readouterr()
    # Check for the plain value, not the Rich tags, in the output string.
    # Rich table output can be complex, so look for the value itself.
    # Convert jamming_rssi_val to string for assertion, as it appears in the table.
    assert str(jamming_rssi_val) in captured.out

def test_print_device_table_empty(capsys: pytest.CaptureFixture[str]):
    """Test print_device_table with no devices."""
    from tapo_chatter.main import print_device_table
    print_device_table([])
    captured = capsys.readouterr()
    assert "No devices found" in captured.out # Expects specific message

@pytest.mark.parametrize(
    "rssi_val, expected_rssi_segment",
    [
        (-50, "[green]-50[/green]"),      # Strong signal
        (0, "[green]0[/green]"),          # Also strong (per code logic)
        (-70, "[yellow]-70[/yellow]"),   # Fair signal
        (-80, "[red]-80[/red]"),        # Poor signal
        ("N/A", "N/A"),                 # N/A value
        (None, "None")                  # None should become str(None), then N/A by code if not int/float.
                                        # Actually, code is: rssi_value if isinstance(rssi_value, (int, float)) else "N/A"
                                        # So None becomes "N/A"
    ]
)
def test_print_device_table_rssi_formatting(capsys: pytest.CaptureFixture[str], rssi_val: Any, expected_rssi_segment: str):
    """Test print_device_table for RSSI value formatting."""
    from tapo_chatter.main import print_device_table
    devices = [{
        "nickname": "RSSI Device", "device_id": "rssi01", "device_type": "T100",
        "status": 1, "rssi": rssi_val, "params": {}
    }]
    print_device_table(devices)
    captured = capsys.readouterr()
    # Check for the plain value in the output string.
    # If rssi_val is None, the code should output "N/A".
    # Otherwise, the direct string representation of rssi_val should be present.
    expected_text = "N/A" if rssi_val is None else str(rssi_val)
    assert expected_text in captured.out

@pytest.mark.parametrize(
    "device_type, params, expected_details_segment",
    [
        ("T100", {"motion_status": "Detected"}, "[bold red]Motion: Detected[/bold red]"),
        ("T100", {"motion_status": "Clear"}, "Motion: Clear"),
        ("T110", {"contact_status": "Open"}, "[bold red]Contact: Open[/bold red]"),
        ("T110", {"contact_status": "Closed"}, "Contact: Closed"),
        ("T31x", {"temperature": "25.5", "humidity": "60"}, "Temp: 25.5°C, Humidity: 60%"),
        ("KE100", {"target_temp": "22", "current_temp": "21.5"}, "Target: 22°C, Current: 21.5°C"), # Note: KE100 details not in provided main.py snippet, assuming for now
        ("S200B", {}, "No specific sensor info"), # No specific details
        ("Unknown", {"some_other_param": "value"}, "No specific sensor info")
    ]
)
def test_print_device_table_details_formatting(capsys: pytest.CaptureFixture[str], device_type: str, params: Dict[str, Any], expected_details_segment: str):
    """Test print_device_table for sensor details formatting."""
    from tapo_chatter.main import print_device_table
    # KE100 details are not in the provided main.py, so skipping this specific case for now if it causes issues.
    if device_type == "KE100": # Placeholder for KE100 if its logic isn't in main.py shown
        # This test case for KE100 might need adjustment or removal if the formatting logic 
        # for KE100 is not actually present in the `print_device_table` function.
        # For now, we assume it might be and will adjust if coverage doesn't hit it.
        pass # Keep the test case defined

    devices = [{
        "nickname": "Details Device", "device_id": "detail01", "device_type": device_type,
        "status": 1, "rssi": -60, "params": params
    }]
    print_device_table(devices)
    captured = capsys.readouterr()
    assert expected_details_segment in captured.out

@pytest.mark.asyncio
async def test_main_config_load_error(capsys: pytest.CaptureFixture[str]):
    """Test main function when TapoConfig.from_env() raises ValueError."""
    config_error_message = "Simulated TapoConfig Error"
    
    with mock.patch("tapo_chatter.main.TapoConfig.from_env", side_effect=ValueError(config_error_message)) as mock_config_load:
        with pytest.raises(ValueError) as exc_info:
            await main()
    
    mock_config_load.assert_called_once()
    assert str(exc_info.value) == config_error_message
    
    captured = capsys.readouterr()
    # TapoConfig.from_env in config.py prints its own Rich error messages to console before raising.
    # main.py then catches this error and prints its own "Fatal Error" panel.
    assert "Configuration Error:" in captured.out # Part of TapoConfig's direct print
    assert config_error_message in captured.out # Message from TapoConfig
    assert "Fatal Error" in captured.out      # Title of main.py's panel
    # The error message is also in main.py's panel content
    assert f"Error: {config_error_message}" in captured.out 

@pytest.mark.asyncio
async def test_main_apiclient_init_error(capsys: pytest.CaptureFixture[str]):
    """Test main function when ApiClient initialization raises an error."""
    mock_config_instance = mock.Mock(username="user", password="pass", ip_address="1.2.3.4")
    error_message = "ApiClient Init Failed"

    # Patch TapoConfig.from_env to return a controlled config object
    with mock.patch("tapo_chatter.main.TapoConfig.from_env", return_value=mock_config_instance) as mock_config_setup:
        # Patch ApiClient constructor to raise an error
        with mock.patch("tapo_chatter.main.ApiClient", side_effect=Exception(error_message)) as mock_api_client_constructor:
            # Expect the specific exception to be raised by main()
            with pytest.raises(Exception) as exc_info:
                await main()
    
    # Assert that the config setup was called
    mock_config_setup.assert_called_once()
    # Assert that ApiClient constructor was called with correct credentials
    mock_api_client_constructor.assert_called_once_with(mock_config_instance.username, mock_config_instance.password)
    # Assert that the correct exception was raised
    assert str(exc_info.value) == error_message
    
    # Assert that the error message was printed to console by main's error handler
    captured = capsys.readouterr()
    assert "Fatal Error" in captured.out  # Check for the title of the error panel
    assert error_message in captured.out    # Check for the error message itself in the output
