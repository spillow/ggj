"""
Test suite for io_interface.py

Tests the I/O interface implementations.
"""

import pytest
import sys
import os

# Add parent directory to path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io_interface import IOInterface, ConsoleIO, MockIO


class TestMockIO:
    """Test the MockIO implementation."""

    def test_output_recording(self):
        """Test that output is recorded correctly."""
        mock_io = MockIO()

        mock_io.output("Hello")
        mock_io.output("World")

        outputs = mock_io.get_all_outputs()
        assert outputs == ["Hello", "World"]

    def test_input_responses(self):
        """Test that input responses work correctly."""
        mock_io = MockIO()
        mock_io.set_inputs(["yes", "no", "maybe"])

        assert mock_io.get_input("Question 1: ") == "yes"
        assert mock_io.get_input("Question 2: ") == "no"
        assert mock_io.get_input("Question 3: ") == "maybe"

        # Check that prompts were recorded as outputs
        outputs = mock_io.get_all_outputs()
        assert "Question 1: " in outputs
        assert "Question 2: " in outputs
        assert "Question 3: " in outputs

    def test_input_exhaustion(self):
        """Test behavior when input responses are exhausted."""
        mock_io = MockIO()
        mock_io.set_inputs(["only"])

        assert mock_io.get_input("First: ") == "only"
        assert mock_io.get_input("Second: ") == ""  # Default empty response

    def test_sleep_recording(self):
        """Test that sleep calls are recorded."""
        mock_io = MockIO()

        mock_io.sleep(1.0)
        mock_io.sleep(2.5)

        assert mock_io.sleep_calls == [1.0, 2.5]

    def test_clear_functionality(self):
        """Test that clear removes all recorded data."""
        mock_io = MockIO()
        mock_io.set_inputs(["test"])
        mock_io.output("test output")
        mock_io.sleep(1.0)
        mock_io.get_input("prompt")

        mock_io.clear()

        assert mock_io.get_all_outputs() == []
        assert mock_io.inputs == []
        assert mock_io.input_index == 0
        assert mock_io.sleep_calls == []


class TestIOInterface:
    """Test the abstract IOInterface."""

    def test_interface_is_abstract(self):
        """Test that IOInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IOInterface()


if __name__ == "__main__":
    pytest.main([__file__])
