import os
from unittest import mock

import pytest

from tapo_chatter.config import TapoConfig

# Valid and invalid inputs for testing
VALID_IP = "192.168.1.1"
INVALID_IP_FORMAT = "192.168.1"
INVALID_IP_RANGE = "192.168.1.256"
VALID_EMAIL = "test@example.com"
INVALID_EMAIL_FORMAT = "test@example"
INVALID_EMAIL_DOMAIN = "test@.com"
INVALID_EMAIL_USER = "@example.com"

@pytest.mark.parametrize(
    "ip_address, expected",
    [
        (VALID_IP, True),
        ("10.0.0.1", True),
        ("0.0.0.0", True),
        ("255.255.255.255", True),
        (INVALID_IP_FORMAT, False),
        ("192.168.1.1.1", False),
        (INVALID_IP_RANGE, False),
        ("abc.def.ghi.jkl", False),
        ("", False),
        ("192.168.1. 254", False), # Space in segment
    ]
)
def test_is_valid_ip(ip_address, expected):
    assert TapoConfig.is_valid_ip(ip_address) == expected

@pytest.mark.parametrize(
    "email, expected",
    [
        (VALID_EMAIL, True),
        ("firstname.lastname@example.co.uk", True),
        ("user123@sub.domain.com", True),
        (INVALID_EMAIL_FORMAT, False),
        (INVALID_EMAIL_DOMAIN, False),
        (INVALID_EMAIL_USER, False),
        ("test.example.com", False), # No @
        ("test@example_com", False), # Underscore in domain
        ("", False),
    ]
)
def test_is_valid_email(email, expected):
    assert TapoConfig.is_valid_email(email) == expected

@mock.patch.dict(
    os.environ,
    {
        "TAPO_USERNAME": VALID_EMAIL,
        "TAPO_PASSWORD": "test_password",
        "TAPO_IP_ADDRESS": VALID_IP,
    },
)
def test_from_env_valid():
    config = TapoConfig.from_env()
    assert config.username == VALID_EMAIL
    assert config.password == "test_password"
    assert config.ip_address == VALID_IP

@mock.patch.dict(os.environ, {}, clear=True)
def test_from_env_missing_all():
    with pytest.raises(ValueError) as excinfo:
        TapoConfig.from_env()
    assert "Missing required environment variables" in str(excinfo.value)
    assert "TAPO_USERNAME" in str(excinfo.value)
    assert "TAPO_PASSWORD" in str(excinfo.value)
    assert "TAPO_IP_ADDRESS" in str(excinfo.value)

@mock.patch.dict(
    os.environ,
    {
        "TAPO_PASSWORD": "test_password",
        "TAPO_IP_ADDRESS": VALID_IP,
    },
    clear=True
)
def test_from_env_missing_username():
    with pytest.raises(ValueError) as excinfo:
        TapoConfig.from_env()
    assert "Missing required environment variables: TAPO_USERNAME" in str(excinfo.value)

@mock.patch.dict(
    os.environ,
    {
        "TAPO_USERNAME": VALID_EMAIL,
        "TAPO_IP_ADDRESS": VALID_IP,
    },
    clear=True
)
def test_from_env_missing_password():
    with pytest.raises(ValueError) as excinfo:
        TapoConfig.from_env()
    assert "Missing required environment variables: TAPO_PASSWORD" in str(excinfo.value)


@mock.patch.dict(
    os.environ,
    {
        "TAPO_USERNAME": VALID_EMAIL,
        "TAPO_PASSWORD": "test_password",
    },
    clear=True
)
def test_from_env_missing_ip():
    with pytest.raises(ValueError) as excinfo:
        TapoConfig.from_env()
    assert "Missing required environment variables: TAPO_IP_ADDRESS" in str(excinfo.value)


@mock.patch.dict(
    os.environ,
    {
        "TAPO_USERNAME": INVALID_EMAIL_FORMAT,
        "TAPO_PASSWORD": "test_password",
        "TAPO_IP_ADDRESS": VALID_IP,
    },
)
def test_from_env_invalid_email():
    with pytest.raises(ValueError) as excinfo:
        TapoConfig.from_env()
    assert f"Invalid email format for TAPO_USERNAME: {INVALID_EMAIL_FORMAT}" in str(excinfo.value)

@mock.patch.dict(
    os.environ,
    {
        "TAPO_USERNAME": VALID_EMAIL,
        "TAPO_PASSWORD": "test_password",
        "TAPO_IP_ADDRESS": INVALID_IP_FORMAT,
    },
)
def test_from_env_invalid_ip():
    with pytest.raises(ValueError) as excinfo:
        TapoConfig.from_env()
    assert f"Invalid IP address format: {INVALID_IP_FORMAT}" in str(excinfo.value)

@mock.patch.dict(
    os.environ,
    {
        "TAPO_USERNAME": VALID_EMAIL,
        "TAPO_PASSWORD": "test_password",
        "TAPO_IP_ADDRESS": INVALID_IP_RANGE, # Test with invalid range too
    },
)
def test_from_env_invalid_ip_range():
    with pytest.raises(ValueError) as excinfo:
        TapoConfig.from_env()
    assert f"Invalid IP address format: {INVALID_IP_RANGE}" in str(excinfo.value)

# Test with one var missing to ensure individual checks work
@mock.patch.dict(
    os.environ,
    {
        "TAPO_USERNAME": VALID_EMAIL,
        "TAPO_PASSWORD": "test_password",
        # TAPO_IP_ADDRESS is missing
    },
    clear=True
)
def test_from_env_missing_single_variable_ip():
    with pytest.raises(ValueError) as excinfo:
        TapoConfig.from_env()
    assert "Missing required environment variables: TAPO_IP_ADDRESS" in str(excinfo.value)
    assert "TAPO_USERNAME" not in str(excinfo.value) # Ensure only missing var is reported
    assert "TAPO_PASSWORD" not in str(excinfo.value)

def test_tapo_config_instantiation():
    """Test direct instantiation of TapoConfig."""
    config = TapoConfig(username="user@example.com", password="pass123", ip_address="192.168.1.1")
    assert config.username == "user@example.com"
    assert config.password == "pass123"
    assert config.ip_address == "192.168.1.1"

def test_dotenv_loading():
    """Test that dotenv is being loaded from the config module."""
    # We don't test the actual loading, just that the import happens
    import tapo_chatter.config
    assert hasattr(tapo_chatter.config, "load_dotenv")

def test_console_instance():
    """Test that a console instance is created in the config module."""
    import tapo_chatter.config
    assert hasattr(tapo_chatter.config, "console")
    from rich.console import Console
    assert isinstance(tapo_chatter.config.console, Console)
