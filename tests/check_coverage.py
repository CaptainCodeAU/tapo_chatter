#!/usr/bin/env python
"""
Check the current test coverage of the tapo_chatter package.
This script will run pytest with coverage and display the results.
"""

import os
import subprocess
import sys


def run_coverage():
    """Run pytest with coverage and display the results."""
    # Make sure we're in the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(project_root)

    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=src.tapo_chatter",
        "--cov-report=term",
        "tests/"
    ]

    print("Running command:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print the output
    print("Exit code:", result.returncode)
    print("\nSTDOUT:")
    print(result.stdout)

    print("\nSTDERR:")
    print(result.stderr)

    # Parse coverage report lines to identify gaps
    stdout_lines = result.stdout.splitlines()
    for i, line in enumerate(stdout_lines):
        if "TOTAL" in line:
            print("\nTest Coverage Summary:")
            coverage_start = max(0, i-5)
            for j in range(coverage_start, min(i+2, len(stdout_lines))):
                print(stdout_lines[j])
            break

if __name__ == "__main__":
    run_coverage()
