"""
Abstract Command interface for the Command Pattern implementation.

This module provides the foundation for converting action functions into 
Command objects, enabling features like undo/redo, action replay, macros,
and AI agent compatibility.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_world import GameState


class CommandResult:
    """
    Encapsulates the result of command execution.
    
    Attributes:
        success: Whether the command executed successfully
        message: Optional message to display to the user
        data: Optional data payload for the command result
        time_advanced: Whether the command advanced game time
    """
    
    def __init__(self, success: bool = True, message: str = "", 
                 data: Optional[Dict[str, Any]] = None, time_advanced: bool = False):
        self.success = success
        self.message = message
        self.data = data or {}
        self.time_advanced = time_advanced
    
    def __bool__(self) -> bool:
        """Allow CommandResult to be used in boolean contexts."""
        return self.success


class BaseCommand(ABC):
    """
    Abstract base class for all game commands.
    
    Implements the Command pattern, allowing actions to be:
    - Queued and executed later
    - Undone and redone
    - Recorded for replay
    - Used by AI agents
    - Combined into macros
    """
    
    def __init__(self, description: str = ""):
        """
        Initialize the command.
        
        Args:
            description: Human-readable description of what this command does
        """
        self.description = description
        self._executed = False
        self._undo_data: Optional[Dict[str, Any]] = None
    
    @abstractmethod
    def execute(self, game_state: "GameState") -> CommandResult:
        """
        Execute the command against the game state.
        
        Args:
            game_state: Current game state to operate on
            
        Returns:
            CommandResult indicating success/failure and any output
        """
        pass
    
    def can_execute(self, game_state: "GameState") -> bool:
        """
        Check if the command can be executed in the current game state.
        
        Args:
            game_state: Current game state to check against
            
        Returns:
            True if the command can be executed, False otherwise
        """
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """
        Undo the effects of this command.
        
        Default implementation returns failure. Subclasses should override
        this method to provide undo functionality where possible.
        
        Args:
            game_state: Current game state to operate on
            
        Returns:
            CommandResult indicating success/failure of the undo operation
        """
        return CommandResult(success=False, message="This command cannot be undone")
    
    def can_undo(self) -> bool:
        """
        Check if this command can be undone.
        
        Returns:
            True if the command supports undo, False otherwise
        """
        return False
    
    def store_undo_data(self, data: Dict[str, Any]) -> None:
        """
        Store data needed for undo operations.
        
        Args:
            data: Dictionary containing state information needed for undo
        """
        self._undo_data = data.copy()
    
    def get_undo_data(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored undo data.
        
        Returns:
            Dictionary of undo data, or None if no data stored
        """
        return self._undo_data.copy() if self._undo_data else None
    
    @property
    def executed(self) -> bool:
        """Whether this command has been executed."""
        return self._executed
    
    def mark_executed(self) -> None:
        """Mark this command as having been executed."""
        self._executed = True
    
    def __str__(self) -> str:
        """String representation of the command."""
        return self.description or self.__class__.__name__
    
    def __repr__(self) -> str:
        """Detailed string representation of the command."""
        return f"{self.__class__.__name__}(description='{self.description}', executed={self._executed})"


class MacroCommand(BaseCommand):
    """
    A command that executes a sequence of other commands.
    
    Useful for creating complex action sequences that can be treated
    as a single unit for undo/redo and replay purposes.
    """
    
    def __init__(self, commands: list[BaseCommand], description: str = "Macro command"):
        """
        Initialize the macro command.
        
        Args:
            commands: List of commands to execute in sequence
            description: Description of what this macro does
        """
        super().__init__(description)
        self.commands = commands.copy()
        self._executed_commands: list[BaseCommand] = []
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """
        Execute all commands in sequence.
        
        If any command fails, execution stops and the macro is considered failed.
        
        Args:
            game_state: Current game state to operate on
            
        Returns:
            CommandResult with combined results of all commands
        """
        results = []
        messages = []
        
        for command in self.commands:
            if not command.can_execute(game_state):
                return CommandResult(
                    success=False, 
                    message=f"Cannot execute command: {command}"
                )
            
            result = command.execute(game_state)
            results.append(result)
            
            if result.message:
                messages.append(result.message)
            
            if result.success:
                command.mark_executed()
                self._executed_commands.append(command)
            else:
                # Command failed, stop execution
                return CommandResult(
                    success=False,
                    message=f"Macro failed at command: {command}. {result.message}",
                    data={"partial_results": results}
                )
        
        self.mark_executed()
        return CommandResult(
            success=True,
            message="\n".join(messages) if messages else "",
            data={"results": results},
            time_advanced=any(r.time_advanced for r in results)
        )
    
    def can_execute(self, game_state: "GameState") -> bool:
        """
        Check if all commands in the macro can be executed.
        
        Args:
            game_state: Current game state to check against
            
        Returns:
            True if all commands can be executed, False otherwise
        """
        return all(cmd.can_execute(game_state) for cmd in self.commands)
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """
        Undo all executed commands in reverse order.
        
        Args:
            game_state: Current game state to operate on
            
        Returns:
            CommandResult indicating success/failure of the undo operation
        """
        if not self.can_undo():
            return CommandResult(success=False, message="Macro cannot be undone")
        
        # Undo in reverse order
        for command in reversed(self._executed_commands):
            result = command.undo(game_state)
            if not result.success:
                return CommandResult(
                    success=False,
                    message=f"Failed to undo command: {command}. {result.message}"
                )
        
        self._executed_commands.clear()
        return CommandResult(success=True, message="Macro undone successfully")
    
    def can_undo(self) -> bool:
        """
        Check if the macro can be undone.
        
        Returns:
            True if all executed commands support undo, False otherwise
        """
        return all(cmd.can_undo() for cmd in self._executed_commands)