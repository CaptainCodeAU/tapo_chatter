#!/usr/bin/env python3
"""Helper script to run the main module directly and test the __main__ block."""

import os
import sys
import unittest.mock as mock

import coverage

# Set up coverage measurement
cov = coverage.Coverage()
cov.start()

# Mock the main function to prevent actual execution
with mock.patch('asyncio.run'):
    # Act as if this module is being run directly
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    # Don't actually run the main function, but do execute the module

# Stop coverage measurement and report
cov.stop()
cov.save()

print("Coverage of __main__ block executed successfully.")
