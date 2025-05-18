"""Tests for the main module and core functionality."""

import pytest
from tapo_chatter import hello
from tapo_chatter.main import main

def test_hello() -> None:
    """Test the hello function includes the project name."""
    assert "tapo_chatter" in hello()

def test_main_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the output of the main function."""
    main()
    captured = capsys.readouterr()
    assert "tapo_chatter" in captured.out
    assert captured.err == ""
