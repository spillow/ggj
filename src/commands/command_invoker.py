"""
Command Invoker module - Manages command execution, queuing, and coordination.

The CommandInvoker is responsible for:
- Executing individual commands
- Managing command queues
- Coordinating with command history
- Providing a clean interface for command execution
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from queue import Queue

from .base_command import BaseCommand, CommandResult

if TYPE_CHECKING:
    from ..core.game_world import GameState
    from .command_history import CommandHistory


class CommandInvoker:
    """
    Manages command execution and queuing.
    
    The CommandInvoker serves as the central point for executing commands,
    managing command queues, and coordinating with the command history system.
    """
    
    def __init__(self, history: Optional["CommandHistory"] = None):
        """
        Initialize the command invoker.
        
        Args:
            history: Optional command history manager for undo/redo functionality
        """
        self.history = history
        self.command_queue: Queue[BaseCommand] = Queue()
        self._is_executing = False
    
    def execute_command(self, command: BaseCommand, game_state: "GameState") -> CommandResult:
        """
        Execute a single command immediately.
        
        Args:
            command: The command to execute
            game_state: Current game state
            
        Returns:
            CommandResult indicating success/failure and any output
        """        
        # Execute the command (let it handle its own error checking and messaging)
        try:
            result = command.execute(game_state)
            
            # If successful and we have history, record it
            if result.success and self.history and command.executed:
                self.history.add_command(command)
            
            return result
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Command execution failed: {str(e)}"
            )
    
    def queue_command(self, command: BaseCommand) -> None:
        """
        Add a command to the execution queue.
        
        Args:
            command: The command to queue for later execution
        """
        self.command_queue.put(command)
    
    def execute_queued_commands(self, game_state: "GameState") -> List[CommandResult]:
        """
        Execute all queued commands in order.
        
        Args:
            game_state: Current game state
            
        Returns:
            List of CommandResults for each executed command
        """
        if self._is_executing:
            return [CommandResult(
                success=False,
                message="Command execution already in progress"
            )]
        
        self._is_executing = True
        results = []
        
        try:
            while not self.command_queue.empty():
                command = self.command_queue.get()
                result = self.execute_command(command, game_state)
                results.append(result)
                
                # If a command fails, stop executing the queue
                if not result.success:
                    break
                
        finally:
            self._is_executing = False
        
        return results
    
    def clear_queue(self) -> int:
        """
        Clear all queued commands.
        
        Returns:
            Number of commands that were cleared
        """
        count = 0
        while not self.command_queue.empty():
            self.command_queue.get()
            count += 1
        return count
    
    def queue_size(self) -> int:
        """
        Get the current size of the command queue.
        
        Returns:
            Number of commands in the queue
        """
        return self.command_queue.qsize()
    
    def is_executing(self) -> bool:
        """
        Check if commands are currently being executed.
        
        Returns:
            True if command execution is in progress
        """
        return self._is_executing
    
    def execute_command_sequence(self, commands: List[BaseCommand], 
                                game_state: "GameState") -> List[CommandResult]:
        """
        Execute a sequence of commands, stopping on first failure.
        
        Args:
            commands: List of commands to execute in order
            game_state: Current game state
            
        Returns:
            List of CommandResults for each command that was attempted
        """
        results = []
        
        for command in commands:
            result = self.execute_command(command, game_state)
            results.append(result)
            
            # Stop on first failure
            if not result.success:
                break
        
        return results
    
    def can_execute_sequence(self, commands: List[BaseCommand], 
                           game_state: "GameState") -> bool:
        """
        Check if a sequence of commands can all be executed.
        
        Note: This is a best-effort check. Game state could change between
        the check and actual execution.
        
        Args:
            commands: List of commands to check
            game_state: Current game state
            
        Returns:
            True if all commands appear executable
        """
        return all(cmd.can_execute(game_state) for cmd in commands)
    
    def set_history(self, history: "CommandHistory") -> None:
        """
        Set the command history manager.
        
        Args:
            history: Command history manager for undo/redo
        """
        self.history = history
    
    def get_history(self) -> Optional["CommandHistory"]:
        """
        Get the current command history manager.
        
        Returns:
            The command history manager, or None if not set
        """
        return self.history


class BatchCommandInvoker(CommandInvoker):
    """
    Extended command invoker that supports batch operations and rollback.
    
    This invoker can execute commands as atomic transactions, rolling back
    all changes if any command in the batch fails.
    """
    
    def execute_batch_atomic(self, commands: List[BaseCommand], 
                           game_state: "GameState") -> CommandResult:
        """
        Execute a batch of commands atomically.
        
        If any command fails, all previously executed commands in the batch
        are undone, leaving the game state unchanged.
        
        Args:
            commands: List of commands to execute atomically
            game_state: Current game state
            
        Returns:
            CommandResult indicating success/failure of the entire batch
        """
        if not commands:
            return CommandResult(success=True, message="Empty command batch")
        
        executed_commands = []
        
        # Try to execute all commands
        for i, command in enumerate(commands):
            if not command.can_execute(game_state):
                # Rollback any commands we've already executed
                self._rollback_commands(executed_commands, game_state)
                return CommandResult(
                    success=False,
                    message=f"Batch failed: Command {i} cannot be executed: {command}"
                )
            
            result = command.execute(game_state)
            
            if result.success:
                executed_commands.append(command)
            else:
                # Command failed, rollback everything
                self._rollback_commands(executed_commands, game_state)
                return CommandResult(
                    success=False,
                    message=f"Batch failed at command {i}: {command}. {result.message}"
                )
        
        # All commands succeeded, add them to history if available
        if self.history:
            for command in executed_commands:
                self.history.add_command(command)
        
        return CommandResult(
            success=True,
            message=f"Successfully executed {len(commands)} commands",
            data={"commands_executed": len(commands)}
        )
    
    def _rollback_commands(self, commands: List[BaseCommand], 
                          game_state: "GameState") -> None:
        """
        Rollback a list of commands in reverse order.
        
        Args:
            commands: List of commands to rollback (in execution order)
            game_state: Current game state
        """
        # Undo in reverse order
        for command in reversed(commands):
            if command.can_undo():
                try:
                    command.undo(game_state)
                except Exception:
                    # Log error but continue with rollback
                    pass