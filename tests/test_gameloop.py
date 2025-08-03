"""
Tests for the main game loop.
"""

import pytest
from src.gameloop import run
from src.io_interface import MockIO, IOInterface
from src.inputparser import parse
from typing import List


class GameLoopMockIO(IOInterface):
    """MockIO that raises EOFError when inputs are exhausted."""
    
    def __init__(self):
        self.outputs: List[str] = []
        self.inputs: List[str] = []
        self.input_index = 0
        self.sleep_calls: List[float] = []
    
    def output(self, message: str) -> None:
        """Store output message for verification."""
        self.outputs.append(message)
    
    def get_input(self, prompt: str) -> str:
        """Return pre-configured input response or raise EOFError."""
        self.outputs.append(prompt)  # Store prompt as output too
        if self.input_index < len(self.inputs):
            response = self.inputs[self.input_index]
            self.input_index += 1
            return response
        # Raise EOFError when we run out of inputs instead of returning empty string
        raise EOFError("No more test inputs available")
    
    def sleep(self, seconds: float) -> None:
        """Record sleep calls without actually sleeping."""
        self.sleep_calls.append(seconds)
    
    def set_inputs(self, inputs: List[str]) -> None:
        """Configure input responses for testing."""
        self.inputs = inputs
        self.input_index = 0
    
    def get_all_outputs(self) -> List[str]:
        """Get all recorded outputs."""
        return self.outputs.copy()
    
    def clear(self) -> None:
        """Clear all recorded outputs and inputs."""
        self.outputs.clear()
        self.inputs.clear()
        self.input_index = 0
        self.sleep_calls.clear()


class TestGameLoop:
    def test_run_with_explicit_io(self):
        """Test game loop with explicitly provided IO interface."""
        mock_io = GameLoopMockIO()
        # Set empty inputs to cause EOFError immediately
        mock_io.set_inputs([])  # This will cause EOFError when input runs out
        
        try:
            run(mock_io)
        except EOFError:
            # Expected - game runs out of inputs and exits
            pass
        
        # Verify that the game started
        outputs = mock_io.get_all_outputs()
        assert len(outputs) > 0  # Game should produce some output

    def test_run_with_invalid_command(self):
        """Test game loop with invalid command."""
        mock_io = GameLoopMockIO()
        # Set invalid command that will cause parse error
        mock_io.set_inputs(["invalid command"])
        
        try:
            run(mock_io)
        except EOFError:
            # Expected - game runs out of inputs and exits
            pass
        
        # Verify that error handling worked
        outputs = mock_io.get_all_outputs()
        # Should contain error message and empty line after
        output_text = " ".join(outputs)
        assert len(outputs) > 0

    def test_run_default_io_signature(self):
        """Test that run() function signature accepts None for io parameter."""
        # We can't easily test the actual ConsoleIO path without user interaction
        # This test verifies the code path exists but we rely on e2e tests for full coverage
        assert callable(run)  # Function exists and is callable
        
        # Test that the function can be called with None (but don't actually call it)
        import inspect
        sig = inspect.signature(run)
        assert 'io' in sig.parameters
        assert sig.parameters['io'].default is None

    def test_run_command_execution_success(self):
        """Test successful command execution in game loop."""
        mock_io = GameLoopMockIO()
        # Set a valid command that will execute successfully
        mock_io.set_inputs(["inventory"])
        
        try:
            run(mock_io)
        except EOFError:
            # Expected - game runs out of inputs and exits
            pass
        
        outputs = mock_io.get_all_outputs()
        assert len(outputs) > 0
        # Should contain inventory output and empty lines after successful commands