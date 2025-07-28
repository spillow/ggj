"""
io_interface.py

Interface abstraction for input/output operations to make the game testable.
Provides both console and mock implementations.
"""

from abc import ABC, abstractmethod
import time
from typing import List


class IOInterface(ABC):
    """Abstract interface for input/output operations."""
    
    @abstractmethod
    def output(self, message: str) -> None:
        """Output a message to the user."""
        pass
    
    @abstractmethod
    def get_input(self, prompt: str) -> str:
        """Get input from the user with a prompt."""
        pass
    
    @abstractmethod
    def sleep(self, seconds: float) -> None:
        """Sleep for the specified number of seconds."""
        pass


class ConsoleIO(IOInterface):
    """Console implementation of the I/O interface."""
    
    def output(self, message: str) -> None:
        """Print message to console."""
        print(message)
    
    def get_input(self, prompt: str) -> str:
        """Get input from console."""
        return input(prompt)
    
    def sleep(self, seconds: float) -> None:
        """Sleep using time.sleep."""
        time.sleep(seconds)


class MockIO(IOInterface):
    """Mock implementation for testing."""
    
    def __init__(self):
        self.outputs: List[str] = []
        self.inputs: List[str] = []
        self.input_index = 0
        self.sleep_calls: List[float] = []
    
    def output(self, message: str) -> None:
        """Store output message for verification."""
        self.outputs.append(message)
    
    def get_input(self, prompt: str) -> str:
        """Return pre-configured input response."""
        self.outputs.append(prompt)  # Store prompt as output too
        if self.input_index < len(self.inputs):
            response = self.inputs[self.input_index]
            self.input_index += 1
            return response
        return ""  # Default response if no more inputs configured
    
    def sleep(self, seconds: float) -> None:
        """Record sleep calls without actually sleeping."""
        self.sleep_calls.append(seconds)
    
    def set_inputs(self, inputs: List[str]) -> None:
        """Configure input responses for testing."""
        self.inputs = inputs
        self.input_index = 0
    
    def get_all_outputs(self) -> List[str]:
        """Get all output messages for verification."""
        return self.outputs.copy()
    
    def clear(self) -> None:
        """Clear all recorded data."""
        self.outputs.clear()
        self.inputs.clear()
        self.input_index = 0
        self.sleep_calls.clear()