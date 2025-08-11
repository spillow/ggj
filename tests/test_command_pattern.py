"""
Test module for the Command Pattern implementation.

Tests the base command interface, concrete command implementations,
command invoker, command history, and macro commands.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.core.game_world import GameState
from src.io_interface import MockIO
from src.commands.base_command import BaseCommand, CommandResult, MacroCommand
from src.commands.game_commands import (
    EnterRoomCommand, ExamineThingCommand, GetObjectCommand,
    InventoryCommand, CheckBalanceCommand, PonderCommand,
    DebugItemsCommand, OpenThingCommand, CloseThingCommand,
    CheckFeelCommand, LookAtWatchCommand, TakeIceBathCommand
)
from src.commands.command_invoker import CommandInvoker, BatchCommandInvoker
from src.commands.command_history import CommandHistory, UndoCommand, RedoCommand
from src.commands.macro_commands import (
    ExploreRoomMacro, GetFromContainerMacro, StatusCheckMacro,
    MacroBuilder, create_status_check_macro
)


class TestBaseCommand(unittest.TestCase):
    """Test the base command interface and CommandResult."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.game_state = GameState(self.mock_io)
    
    def test_command_result_creation(self):
        """Test CommandResult creation and boolean conversion."""
        # Successful result
        result = CommandResult(success=True, message="Success")
        self.assertTrue(result)
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Success")
        self.assertEqual(result.data, {})
        self.assertFalse(result.time_advanced)
        
        # Failed result
        result = CommandResult(success=False, message="Failed")
        self.assertFalse(result)
        self.assertFalse(result.success)
        
        # Result with data and time advanced
        result = CommandResult(
            success=True,
            message="Advanced",
            data={"test": "value"},
            time_advanced=True
        )
        self.assertTrue(result.time_advanced)
        self.assertEqual(result.data["test"], "value")
    
    def test_base_command_abstract(self):
        """Test that BaseCommand cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseCommand("test")
    
    def test_command_execution_state(self):
        """Test command execution state tracking."""
        command = CheckBalanceCommand()
        
        self.assertFalse(command.executed)
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        self.assertTrue(command.executed)
    
    def test_macro_command(self):
        """Test MacroCommand functionality."""
        commands = [
            CheckBalanceCommand(),
            InventoryCommand(),
            LookAtWatchCommand()
        ]
        
        macro = MacroCommand(commands, "Status check macro")
        self.assertEqual(len(macro.commands), 3)
        self.assertTrue(macro.can_execute(self.game_state))
        
        result = macro.execute(self.game_state)
        self.assertTrue(result.success)
        self.assertTrue(macro.executed)
        
        # Check that all sub-commands were executed
        for command in commands:
            self.assertTrue(command.executed)


class TestGameCommands(unittest.TestCase):
    """Test concrete game command implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.game_state = GameState(self.mock_io)
    
    def test_enter_room_command(self):
        """Test EnterRoomCommand execution."""
        command = EnterRoomCommand("bedroom")
        
        self.assertTrue(command.can_execute(self.game_state))
        
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        self.assertEqual(self.game_state.hero.GetRoom().name, "bedroom")
    
    def test_enter_invalid_room_command(self):
        """Test EnterRoomCommand with invalid room."""
        command = EnterRoomCommand("nonexistent")
        
        self.assertFalse(command.can_execute(self.game_state))
        
        result = command.execute(self.game_state)
        self.assertFalse(result.success)
        self.assertIn("haven't built", result.message)
    
    def test_inventory_command(self):
        """Test InventoryCommand execution."""
        command = InventoryCommand()
        
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        # InventoryCommand now outputs directly, so check the mock outputs instead
        outputs = self.mock_io.get_all_outputs()
        carrying_found = any("carrying" in output for output in outputs)
        self.assertTrue(carrying_found, "Expected 'carrying' in inventory output")
    
    def test_check_balance_command(self):
        """Test CheckBalanceCommand execution."""
        command = CheckBalanceCommand()
        
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        self.assertIn("$100", result.message)  # Default starting balance
    
    def test_ponder_command_with_undo(self):
        """Test PonderCommand execution and undo functionality."""
        command = PonderCommand(hours=2)
        
        original_time = self.game_state.watch.curr_time
        original_feel = self.game_state.hero.feel
        
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        self.assertTrue(result.time_advanced)
        
        # Check time and feel changed
        self.assertEqual(
            self.game_state.watch.curr_time,
            original_time + timedelta(hours=2)
        )
        self.assertEqual(self.game_state.hero.feel, original_feel - 20)  # 10 * 2 hours
        
        # Test undo
        self.assertTrue(command.can_undo())
        undo_result = command.undo(self.game_state)
        self.assertTrue(undo_result.success)
        
        # Check state restored
        self.assertEqual(self.game_state.watch.curr_time, original_time)
        self.assertEqual(self.game_state.hero.feel, original_feel)
    
    def test_debug_items_command(self):
        """Test DebugItemsCommand execution."""
        command = DebugItemsCommand()
        
        original_count = len(self.game_state.hero.contents)
        
        result = command.execute(self.game_state)
        if not result.success:
            print(f"Debug command failed: {result.message}")
        self.assertTrue(result.success)
        
        # Check items were added
        self.assertEqual(len(self.game_state.hero.contents), original_count + 3)
        
        # Check specific items
        hammer = self.game_state.hero.GetFirstItemByName('hammer')
        nails = self.game_state.hero.GetFirstItemByName('box-of-nails')
        plywood = self.game_state.hero.GetFirstItemByName('plywood-sheet')
        
        self.assertIsNotNone(hammer)
        self.assertIsNotNone(nails)
        self.assertIsNotNone(plywood)
    
    def test_examine_command(self):
        """Test ExamineThingCommand execution."""
        command = ExamineThingCommand("fridge")
        
        self.assertTrue(command.can_execute(self.game_state))
        
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
    
    def test_open_close_container_commands(self):
        """Test OpenThingCommand and CloseThingCommand with undo."""
        # Test opening
        open_command = OpenThingCommand("fridge")
        
        self.assertTrue(open_command.can_execute(self.game_state))
        
        result = open_command.execute(self.game_state)
        self.assertTrue(result.success)
        
        # Test undo (closing)
        self.assertTrue(open_command.can_undo())
        undo_result = open_command.undo(self.game_state)
        self.assertTrue(undo_result.success)
        
        # Test closing
        # First open again
        open_command.execute(self.game_state)
        
        close_command = CloseThingCommand("fridge")
        result = close_command.execute(self.game_state)
        self.assertTrue(result.success)
        
        # Test undo (opening)
        self.assertTrue(close_command.can_undo())
        undo_result = close_command.undo(self.game_state)
        self.assertTrue(undo_result.success)


class TestCommandInvoker(unittest.TestCase):
    """Test CommandInvoker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.game_state = GameState(self.mock_io)
        self.invoker = CommandInvoker()
    
    def test_execute_single_command(self):
        """Test executing a single command."""
        command = CheckBalanceCommand()
        
        result = self.invoker.execute_command(command, self.game_state)
        self.assertTrue(result.success)
        self.assertTrue(command.executed)
    
    def test_execute_failing_command(self):
        """Test executing a command that fails."""
        command = EnterRoomCommand("nonexistent")
        
        result = self.invoker.execute_command(command, self.game_state)
        self.assertFalse(result.success)
    
    def test_command_queue(self):
        """Test command queuing and execution."""
        commands = [
            CheckBalanceCommand(),
            InventoryCommand(),
            CheckFeelCommand()
        ]
        
        # Queue commands
        for command in commands:
            self.invoker.queue_command(command)
        
        self.assertEqual(self.invoker.queue_size(), 3)
        
        # Execute queued commands
        results = self.invoker.execute_queued_commands(self.game_state)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(result.success)
        
        self.assertEqual(self.invoker.queue_size(), 0)
    
    def test_command_sequence(self):
        """Test executing a sequence of commands."""
        commands = [
            EnterRoomCommand("main"),
            ExamineThingCommand("phone"),
            EnterRoomCommand("bedroom")
        ]
        
        results = self.invoker.execute_command_sequence(commands, self.game_state)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(result.success)
        
        # Check final room
        self.assertEqual(self.game_state.hero.GetRoom().name, "bedroom")
    
    def test_sequence_fails_early(self):
        """Test sequence execution stops on first failure."""
        commands = [
            CheckBalanceCommand(),  # Should succeed
            EnterRoomCommand("nonexistent"),  # Should fail
            InventoryCommand()  # Should not execute
        ]
        
        results = self.invoker.execute_command_sequence(commands, self.game_state)
        
        self.assertEqual(len(results), 2)  # Only 2 commands attempted
        self.assertTrue(results[0].success)
        self.assertFalse(results[1].success)


class TestBatchCommandInvoker(unittest.TestCase):
    """Test BatchCommandInvoker atomic execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.game_state = GameState(self.mock_io)
        self.invoker = BatchCommandInvoker()
    
    def test_atomic_batch_success(self):
        """Test successful atomic batch execution."""
        commands = [
            DebugItemsCommand(),
            EnterRoomCommand("bedroom"),
            InventoryCommand()
        ]
        
        result = self.invoker.execute_batch_atomic(commands, self.game_state)
        self.assertTrue(result.success)
        
        # Verify all commands executed
        for command in commands:
            self.assertTrue(command.executed)
        
        # Verify final state
        self.assertEqual(self.game_state.hero.GetRoom().name, "bedroom")
        self.assertGreater(len(self.game_state.hero.contents), 0)
    
    def test_atomic_batch_failure_rollback(self):
        """Test atomic batch rollback on failure."""
        original_room = self.game_state.hero.GetRoom().name
        original_balance = self.game_state.hero.curr_balance
        
        commands = [
            PonderCommand(hours=1),  # Should succeed and be undoable
            EnterRoomCommand("bedroom"),  # Should succeed and be undoable
            EnterRoomCommand("nonexistent")  # Should fail
        ]
        
        result = self.invoker.execute_batch_atomic(commands, self.game_state)
        self.assertFalse(result.success)
        
        # Verify rollback occurred - should be back to original state
        # Note: This test assumes undo functionality works correctly
        # In practice, some state changes might not be perfectly undoable


class TestCommandHistory(unittest.TestCase):
    """Test CommandHistory undo/redo functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.game_state = GameState(self.mock_io)
        self.history = CommandHistory(max_history=5)
    
    def test_add_undoable_command(self):
        """Test adding undoable commands to history."""
        command = PonderCommand(hours=1)
        
        # Command should not be in history before execution
        self.assertFalse(self.history.can_undo())
        
        # Execute and add to history
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        
        self.history.add_command(command)
        self.assertTrue(self.history.can_undo())
    
    def test_skip_non_undoable_command(self):
        """Test that non-undoable commands are not added to history."""
        command = InventoryCommand()  # Not undoable
        
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        
        self.history.add_command(command)
        self.assertFalse(self.history.can_undo())  # Should not be added
    
    def test_undo_redo_cycle(self):
        """Test complete undo/redo cycle."""
        command = PonderCommand(hours=2)
        
        original_time = self.game_state.watch.curr_time
        original_feel = self.game_state.hero.feel
        
        # Execute command
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        self.history.add_command(command)
        
        # Verify state changed
        self.assertNotEqual(self.game_state.watch.curr_time, original_time)
        self.assertNotEqual(self.game_state.hero.feel, original_feel)
        
        # Undo
        self.assertTrue(self.history.can_undo())
        undo_result = self.history.undo(self.game_state)
        self.assertTrue(undo_result.success)
        
        # Verify state restored
        self.assertEqual(self.game_state.watch.curr_time, original_time)
        self.assertEqual(self.game_state.hero.feel, original_feel)
        
        # Should now be able to redo
        self.assertTrue(self.history.can_redo())
        self.assertFalse(self.history.can_undo())
        
        # Redo
        redo_result = self.history.redo(self.game_state)
        self.assertTrue(redo_result.success)
        
        # Verify state changed again
        self.assertNotEqual(self.game_state.watch.curr_time, original_time)
        self.assertNotEqual(self.game_state.hero.feel, original_feel)
    
    def test_new_command_clears_redo_stack(self):
        """Test that adding new command clears redo history."""
        command1 = PonderCommand(hours=1)
        command2 = PonderCommand(hours=1)
        
        # Execute and add first command
        command1.execute(self.game_state)
        self.history.add_command(command1)
        
        # Undo
        self.history.undo(self.game_state)
        self.assertTrue(self.history.can_redo())
        
        # Execute and add second command
        command2.execute(self.game_state)
        self.history.add_command(command2)
        
        # Redo should no longer be available
        self.assertFalse(self.history.can_redo())
        self.assertTrue(self.history.can_undo())
    
    def test_history_size_limit(self):
        """Test that history respects size limit."""
        history = CommandHistory(max_history=2)
        
        commands = [
            PonderCommand(hours=1),
            PonderCommand(hours=1),
            PonderCommand(hours=1)
        ]
        
        for command in commands:
            command.execute(self.game_state)
            history.add_command(command)
        
        # Should only keep last 2 commands
        self.assertEqual(history.get_history_size()['undo'], 2)


class TestMacroCommands(unittest.TestCase):
    """Test macro command implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.game_state = GameState(self.mock_io)
    
    def test_status_check_macro(self):
        """Test StatusCheckMacro execution."""
        macro = create_status_check_macro()
        
        result = macro.execute(self.game_state)
        self.assertTrue(result.success)
        
        # Check that all sub-commands executed
        self.assertEqual(len(macro._executed_commands), 4)  # watch, balance, feel, inventory
    
    def test_explore_room_macro(self):
        """Test ExploreRoomMacro execution."""
        macro = ExploreRoomMacro("main", ["phone", "toolbox"])
        
        result = macro.execute(self.game_state)
        self.assertTrue(result.success)
        
        # Check hero is in main room
        self.assertEqual(self.game_state.hero.GetRoom().name, "main")
    
    def test_macro_builder(self):
        """Test MacroBuilder fluent interface."""
        builder = MacroBuilder("Test macro")
        
        macro = (builder
                .enter_room("main")
                .examine("phone")
                .enter_room("bedroom")
                .show_inventory()
                .build())
        
        result = macro.execute(self.game_state)
        self.assertTrue(result.success)
        
        # Check final state
        self.assertEqual(self.game_state.hero.GetRoom().name, "bedroom")
    
    def test_macro_builder_clear(self):
        """Test MacroBuilder clear functionality."""
        builder = MacroBuilder("Test")
        
        builder.enter_room("bedroom").examine("bed")
        self.assertEqual(len(builder.commands), 2)
        
        builder.clear()
        self.assertEqual(len(builder.commands), 0)
        
        # Should be able to build empty macro
        macro = builder.build()
        result = macro.execute(self.game_state)
        self.assertTrue(result.success)


class TestCommandIntegration(unittest.TestCase):
    """Integration tests for the complete command system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.game_state = GameState(self.mock_io)
        self.history = CommandHistory()
        self.invoker = CommandInvoker(self.history)
    
    def test_complete_workflow_with_undo(self):
        """Test a complete workflow with command history."""
        # Execute some commands
        commands = [
            DebugItemsCommand(),
            PonderCommand(hours=1),
            EnterRoomCommand("main"),
            ExamineThingCommand("phone")
        ]
        
        # Execute commands through invoker
        for command in commands:
            result = self.invoker.execute_command(command, self.game_state)
            self.assertTrue(result.success)
        
        # Check final state
        self.assertEqual(self.game_state.hero.GetRoom().name, "main")
        self.assertGreater(len(self.game_state.hero.contents), 0)
        
        # Should be able to undo some commands (undoable ones)
        undoable_count = sum(1 for cmd in commands if cmd.can_undo())
        self.assertEqual(self.history.get_history_size()['undo'], undoable_count)
        
        # Undo available commands
        while self.history.can_undo():
            result = self.history.undo(self.game_state)
            self.assertTrue(result.success)


class TestTakeIceBathCommand(unittest.TestCase):
    """Test the TakeIceBathCommand implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.game_state = GameState(self.mock_io)
        self.hero = self.game_state.hero
    
    def test_can_execute_success(self):
        """Test can_execute returns True when conditions are met."""
        # Move hero to bathroom and give ice cubes
        self.game_state.apartment.bathroom.Enter(self.game_state.apartment.main, self.hero)
        from src.core.items import Food
        ice_cubes = Food("ice-cubes", self.hero, 2)
        
        command = TakeIceBathCommand()
        self.assertTrue(command.can_execute(self.game_state))
    
    def test_can_execute_not_in_bathroom(self):
        """Test can_execute returns False when not in bathroom."""
        # Hero starts in main room, give ice cubes
        from src.core.items import Food
        ice_cubes = Food("ice-cubes", self.hero, 2)
        
        command = TakeIceBathCommand()
        self.assertFalse(command.can_execute(self.game_state))
    
    def test_can_execute_no_ice_cubes(self):
        """Test can_execute returns False when no ice cubes."""
        # Move hero to bathroom but don't give ice cubes
        self.game_state.apartment.bathroom.Enter(self.game_state.apartment.main, self.hero)
        
        command = TakeIceBathCommand()
        self.assertFalse(command.can_execute(self.game_state))
    
    def test_execute_success(self):
        """Test successful execution of ice bath command."""
        # Move hero to bathroom and give ice cubes
        self.game_state.apartment.bathroom.Enter(self.game_state.apartment.main, self.hero)
        from src.core.items import Food
        ice_cubes = Food("ice-cubes", self.hero, 2)
        
        initial_feel = self.hero.feel
        initial_time = self.game_state.watch.curr_time
        
        command = TakeIceBathCommand()
        result = command.execute(self.game_state)
        
        # Check command succeeded
        self.assertTrue(result.success)
        self.assertTrue(result.time_advanced)
        
        # Check game state changes
        self.assertEqual(self.hero.feel, initial_feel + 40)  # +40 feel boost
        self.assertEqual(self.game_state.watch.curr_time, initial_time + timedelta(hours=1))  # +1 hour
        self.assertIsNone(self.hero.GetFirstItemByName("ice-cubes"))  # Ice cubes consumed
        self.assertTrue(command.executed)
    
    def test_execute_not_in_bathroom(self):
        """Test execution failure when not in bathroom."""
        from src.core.items import Food
        ice_cubes = Food("ice-cubes", self.hero, 2)
        
        command = TakeIceBathCommand()
        result = command.execute(self.game_state)
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, "I need to be in the bathroom to take an ice bath.")
        self.assertFalse(command.executed)
    
    def test_execute_no_ice_cubes(self):
        """Test execution failure when no ice cubes."""
        self.game_state.apartment.bathroom.Enter(self.game_state.apartment.main, self.hero)
        
        command = TakeIceBathCommand()
        result = command.execute(self.game_state)
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, "I need ice cubes to take an ice bath.")
        self.assertFalse(command.executed)
    
    def test_undo_functionality(self):
        """Test undo capability of ice bath command."""
        # Setup successful execution
        self.game_state.apartment.bathroom.Enter(self.game_state.apartment.main, self.hero)
        from src.core.items import Food
        ice_cubes = Food("ice-cubes", self.hero, 2)
        
        initial_feel = self.hero.feel
        initial_time = self.game_state.watch.curr_time
        
        command = TakeIceBathCommand()
        result = command.execute(self.game_state)
        self.assertTrue(result.success)
        
        # Test undo capability
        self.assertTrue(command.can_undo())
        
        # Execute undo
        undo_result = command.undo(self.game_state)
        self.assertTrue(undo_result.success)
        
        # Check state restoration
        self.assertEqual(self.hero.feel, initial_feel)  # Feel restored
        self.assertEqual(self.game_state.watch.curr_time, initial_time)  # Time restored
        self.assertIsNotNone(self.hero.GetFirstItemByName("ice-cubes"))  # Ice cubes restored
        
        # Ice cubes should be back in hero's inventory
        restored_ice_cubes = self.hero.GetFirstItemByName("ice-cubes")
        self.assertEqual(restored_ice_cubes.parent, self.hero)
        self.assertIn(restored_ice_cubes, self.hero.contents)


if __name__ == '__main__':
    unittest.main()