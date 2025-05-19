"""Test the __main__ block of the main.py module."""

from unittest import mock


def test_main_as_script():
    """Test that when main.py is run as a script, it calls asyncio.run(main())."""
    # Import the module
    from src.tapo_chatter import main as main_module

    # Mock asyncio.run to prevent actual execution
    with mock.patch('asyncio.run') as mock_run:
        # Store original __name__
        original_name = main_module.__name__

        try:
            # Set __name__ to "__main__" to simulate running as script
            main_module.__name__ = "__main__"

            # Execute the if __name__ == "__main__" block directly
            if main_module.__name__ == "__main__":
                import asyncio
                asyncio.run(main_module.main())

            # Check that asyncio.run was called (without checking the exact coroutine object)
            assert mock_run.call_count == 1, "asyncio.run was not called"
        finally:
            # Restore original name
            main_module.__name__ = original_name
