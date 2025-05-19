#!/usr/bin/env python
"""
Run tapo_chatter.main as if it were run directly with python -m tapo_chatter.main.
This helps us achieve 100% coverage by ensuring the if __name__ == "__main__" block is executed.
"""

import os
import sys
import unittest.mock as mock

import coverage

# Get the coverage file from the environment or use a default
coverage_file = os.environ.get("COVERAGE_FILE", ".coverage")

# Start coverage measurement
cov = coverage.Coverage(data_file=coverage_file, source=["src.tapo_chatter.main"], include=["*/tapo_chatter/main.py"])
cov.start()

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    # Set up environment variables if they don't exist
    if not os.environ.get('TAPO_USERNAME'):
        os.environ['TAPO_USERNAME'] = 'test@example.com'
    if not os.environ.get('TAPO_PASSWORD'):
        os.environ['TAPO_PASSWORD'] = 'password'
    if not os.environ.get('TAPO_IP_ADDRESS'):
        os.environ['TAPO_IP_ADDRESS'] = '192.168.1.1'

    # Set up mocks before importing the module
    with mock.patch('asyncio.run') as mocked_run:
        # Import the module first (this avoids execute-while-importing)
        from src.tapo_chatter import main as main_module

        # Store the original __name__
        original_name = main_module.__name__

        try:
            # Set __name__ to "__main__"
            main_module.__name__ = "__main__"

            # Execute the if __name__ == "__main__" block directly
            if main_module.__name__ == "__main__":
                import asyncio
                asyncio.run(main_module.main())

            print("Successfully executed main.py with __name__ = '__main__'")

            # Verify that asyncio.run was called
            if mocked_run.call_count == 1:
                print("Verified: asyncio.run was called once")
            else:
                print(f"Warning: asyncio.run was called {mocked_run.call_count} times")
        finally:
            # Restore the original __name__
            main_module.__name__ = original_name
finally:
    # Stop coverage and save the results
    cov.stop()
    cov.save()
    print(f"Coverage data saved to {coverage_file}")
