"""Test that the main module can be run directly."""

import os
import subprocess
import sys


def test_run_main_directly():
    """Test running the main module directly to cover the __main__ block."""
    # Get the path to the run_main_directly.py script
    run_script_path = os.path.join(os.path.dirname(__file__), "run_main_directly.py")

    # Make sure the script exists
    assert os.path.exists(run_script_path), f"Script not found: {run_script_path}"

    # Set up environment variables for the subprocess
    env = os.environ.copy()
    env.update({
        'TAPO_USERNAME': 'test@example.com',
        'TAPO_PASSWORD': 'password',
        'TAPO_IP_ADDRESS': '192.168.1.1',
        # Add coverage file path to ensure it's included in the main coverage
        'COVERAGE_FILE': os.path.join(os.path.dirname(os.path.dirname(__file__)), '.coverage')
    })

    # Run the script
    result = subprocess.run(
        [sys.executable, run_script_path],
        env=env,
        capture_output=True,
        text=True
    )

    # Check that it ran successfully
    assert result.returncode == 0, f"Script failed with: {result.stderr}"

    # Check that it executed the __main__ block
    assert "Successfully executed main.py with __name__ = '__main__'" in result.stdout
    assert "Verified: asyncio.run was called once" in result.stdout
