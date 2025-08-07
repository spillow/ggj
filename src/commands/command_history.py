"""
Command History module - Manages undo/redo functionality for commands.

The CommandHistory class maintains a stack of executed commands and provides
undo/redo functionality, enabling players to reverse actions and replay them.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Deque
from collections import deque

from .base_command import BaseCommand, CommandResult

if TYPE_CHECKING:
    from ..core.game_world import GameState


class CommandHistory:
    """
    Manages command history for undo/redo operations.
    
    Maintains two stacks:
    - undo_stack: Commands that can be undone (most recent first)
    - redo_stack: Commands that can be redone (cleared when new command added)
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize command history.
        
        Args:
            max_history: Maximum number of commands to keep in history
        """
        self.max_history = max_history
        self.undo_stack: Deque[BaseCommand] = deque(maxlen=max_history)
        self.redo_stack: Deque[BaseCommand] = deque()
    
    def add_command(self, command: BaseCommand) -> None:
        """
        Add a command to the history.
        
        Only commands that can be undone are added to the history.
        Adding a command clears the redo stack.
        
        Args:
            command: The command to add to history
        """
        if command.can_undo():
            self.undo_stack.append(command)
            # Clear redo stack when new command is added
            self.redo_stack.clear()
    
    def can_undo(self) -> bool:
        """
        Check if there are any commands that can be undone.
        
        Returns:
            True if undo is possible
        """
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """
        Check if there are any commands that can be redone.
        
        Returns:
            True if redo is possible
        """
        return len(self.redo_stack) > 0
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """
        Undo the most recent command.
        
        Args:
            game_state: Current game state
            
        Returns:
            CommandResult indicating success/failure of the undo operation
        """
        if not self.can_undo():
            return CommandResult(
                success=False,
                message="Nothing to undo"
            )
        
        command = self.undo_stack.pop()
        
        try:
            result = command.undo(game_state)
            
            if result.success:
                # Move command to redo stack
                self.redo_stack.append(command)
                return CommandResult(
                    success=True,
                    message=f"Undid: {command}. {result.message}".strip()
                )
            else:
                # Undo failed, put command back
                self.undo_stack.append(command)
                return CommandResult(
                    success=False,
                    message=f"Failed to undo {command}: {result.message}"
                )
                
        except Exception as e:
            # Undo failed, put command back
            self.undo_stack.append(command)
            return CommandResult(
                success=False,
                message=f"Undo failed with error: {str(e)}"
            )
    
    def redo(self, game_state: "GameState") -> CommandResult:
        """
        Redo the most recently undone command.
        
        Args:
            game_state: Current game state
            
        Returns:
            CommandResult indicating success/failure of the redo operation
        """
        if not self.can_redo():
            return CommandResult(
                success=False,
                message="Nothing to redo"
            )
        
        command = self.redo_stack.pop()
        
        # Check if command can still be executed
        if not command.can_execute(game_state):
            return CommandResult(
                success=False,
                message=f"Cannot redo {command}: conditions no longer valid"
            )
        
        try:
            result = command.execute(game_state)
            
            if result.success:
                # Move command back to undo stack
                self.undo_stack.append(command)
                return CommandResult(
                    success=True,
                    message=f"Redid: {command}. {result.message}".strip()
                )
            else:
                # Redo failed, command stays in redo stack for another attempt
                self.redo_stack.append(command)
                return CommandResult(
                    success=False,
                    message=f"Failed to redo {command}: {result.message}"
                )
                
        except Exception as e:
            # Redo failed, command stays in redo stack
            self.redo_stack.append(command)
            return CommandResult(
                success=False,
                message=f"Redo failed with error: {str(e)}"
            )
    
    def undo_multiple(self, count: int, game_state: "GameState") -> List[CommandResult]:
        """
        Undo multiple commands in sequence.
        
        Args:
            count: Number of commands to undo
            game_state: Current game state
            
        Returns:
            List of CommandResults, one for each undo operation
        """
        results = []
        
        for i in range(count):
            if not self.can_undo():
                results.append(CommandResult(
                    success=False,
                    message=f"No more commands to undo (undid {i} of {count})"
                ))
                break
            
            result = self.undo(game_state)
            results.append(result)
            
            # Stop if undo fails
            if not result.success:
                break
        
        return results
    
    def redo_multiple(self, count: int, game_state: "GameState") -> List[CommandResult]:
        """
        Redo multiple commands in sequence.
        
        Args:
            count: Number of commands to redo
            game_state: Current game state
            
        Returns:
            List of CommandResults, one for each redo operation
        """
        results = []
        
        for i in range(count):
            if not self.can_redo():
                results.append(CommandResult(
                    success=False,
                    message=f"No more commands to redo (redid {i} of {count})"
                ))
                break
            
            result = self.redo(game_state)
            results.append(result)
            
            # Stop if redo fails
            if not result.success:
                break
        
        return results
    
    def get_undo_history(self, limit: int = 10) -> List[str]:
        """
        Get a list of recent commands that can be undone.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of command descriptions (most recent first)
        """
        return [str(cmd) for cmd in list(self.undo_stack)[-limit:]][::-1]
    
    def get_redo_history(self, limit: int = 10) -> List[str]:
        """
        Get a list of commands that can be redone.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of command descriptions (most recent first)
        """
        return [str(cmd) for cmd in list(self.redo_stack)[-limit:]][::-1]
    
    def clear_history(self) -> None:
        """Clear all command history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def clear_redo_history(self) -> None:
        """Clear only the redo history."""
        self.redo_stack.clear()
    
    def get_history_size(self) -> dict[str, int]:
        """
        Get the current size of both history stacks.
        
        Returns:
            Dictionary with 'undo' and 'redo' counts
        """
        return {
            'undo': len(self.undo_stack),
            'redo': len(self.redo_stack)
        }
    
    def peek_undo(self) -> Optional[BaseCommand]:
        """
        Peek at the next command that would be undone.
        
        Returns:
            The next command to undo, or None if no commands available
        """
        return self.undo_stack[-1] if self.undo_stack else None
    
    def peek_redo(self) -> Optional[BaseCommand]:
        """
        Peek at the next command that would be redone.
        
        Returns:
            The next command to redo, or None if no commands available
        """
        return self.redo_stack[-1] if self.redo_stack else None
    
    def save_checkpoint(self) -> "HistoryCheckpoint":
        """
        Create a checkpoint of the current history state.
        
        Returns:
            A checkpoint that can be used to restore history state
        """
        return HistoryCheckpoint(
            undo_stack=list(self.undo_stack),
            redo_stack=list(self.redo_stack)
        )
    
    def restore_checkpoint(self, checkpoint: "HistoryCheckpoint") -> None:
        """
        Restore history to a previous checkpoint state.
        
        Args:
            checkpoint: The checkpoint to restore
        """
        self.undo_stack = deque(checkpoint.undo_stack, maxlen=self.max_history)
        self.redo_stack = deque(checkpoint.redo_stack)


class HistoryCheckpoint:
    """
    Represents a saved state of command history.
    
    Used for saving and restoring history states, useful for game saves
    or temporary rollbacks.
    """
    
    def __init__(self, undo_stack: List[BaseCommand], redo_stack: List[BaseCommand]):
        """
        Initialize a history checkpoint.
        
        Args:
            undo_stack: Snapshot of the undo stack
            redo_stack: Snapshot of the redo stack
        """
        self.undo_stack = undo_stack.copy()
        self.redo_stack = redo_stack.copy()
        
    def get_total_commands(self) -> int:
        """Get the total number of commands in this checkpoint."""
        return len(self.undo_stack) + len(self.redo_stack)


class UndoCommand(BaseCommand):
    """
    Meta-command that performs an undo operation.
    
    This allows undo operations to be treated as commands themselves,
    enabling features like "undo the undo" (which is just redo).
    """
    
    def __init__(self, history: CommandHistory):
        super().__init__("Undo last command")
        self.history = history
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if undo is possible."""
        return self.history.can_undo()
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the undo operation."""
        return self.history.undo(game_state)
    
    def can_undo(self) -> bool:
        """Undo commands can be "undone" via redo."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Undo the undo (i.e., redo)."""
        return self.history.redo(game_state)


class RedoCommand(BaseCommand):
    """
    Meta-command that performs a redo operation.
    
    This allows redo operations to be treated as commands themselves.
    """
    
    def __init__(self, history: CommandHistory):
        super().__init__("Redo last undone command")
        self.history = history
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if redo is possible."""
        return self.history.can_redo()
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the redo operation."""
        return self.history.redo(game_state)
    
    def can_undo(self) -> bool:
        """Redo commands can be "undone" via undo."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Undo the redo (i.e., undo)."""
        return self.history.undo(game_state)