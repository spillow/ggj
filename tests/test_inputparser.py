"""
Test suite for inputparser.py

Tests the command parsing system including pattern variables,
command matching, and argument extraction.
"""

import pytest
import sys
import os

# Add parent directory to path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.inputparser import PatVar, unify, expand, parse_legacy as parse, COMMANDS
from src import actions


class TestPatVar:
    """Test the PatVar class for pattern variable detection."""

    def test_patvar_with_valid_pattern(self):
        """Test PatVar recognizes valid pattern variables."""
        var = PatVar("{a}")
        assert bool(var) is True
        
        var = PatVar("{item}")
        assert bool(var) is True
        
        var = PatVar("{room}")
        assert bool(var) is True

    def test_patvar_with_invalid_patterns(self):
        """Test PatVar rejects invalid pattern variables."""
        var = PatVar("hello")
        assert bool(var) is False
        
        var = PatVar("{incomplete")
        assert bool(var) is False
        
        var = PatVar("incomplete}")
        assert bool(var) is False
        
        var = PatVar("")
        assert bool(var) is False
        
        var = PatVar("{}")
        assert bool(var) is True  # Empty braces are still valid pattern

    def test_patvar_initialization(self):
        """Test PatVar stores the string correctly."""
        test_string = "{variable}"
        var = PatVar(test_string)
        assert var.s == test_string


class TestUnify:
    """Test the unify function for command token matching."""

    def test_unify_exact_match(self):
        """Test unify with exact matching tokens."""
        command_tokens = ["look", "at", "watch"]
        input_tokens = ["look", "at", "watch"]
        
        success, bindings = unify(command_tokens, input_tokens)
        assert success is True
        assert bindings == []

    def test_unify_with_pattern_variables(self):
        """Test unify with pattern variables."""
        command_tokens = ["examine", "{a}"]
        input_tokens = ["examine", "toolbox"]
        
        success, bindings = unify(command_tokens, input_tokens)
        assert success is True
        assert bindings == ["toolbox"]

    def test_unify_multiple_pattern_variables(self):
        """Test unify with multiple pattern variables."""
        command_tokens = ["get", "{a}", "from", "{b}"]
        input_tokens = ["get", "hammer", "from", "toolbox"]
        
        success, bindings = unify(command_tokens, input_tokens)
        assert success is True
        assert bindings == ["hammer", "toolbox"]

    def test_unify_mismatch(self):
        """Test unify with mismatched tokens."""
        command_tokens = ["look", "at", "watch"]
        input_tokens = ["look", "at", "tv"]
        
        success, bindings = unify(command_tokens, input_tokens)
        assert success is False
        assert bindings == []

    def test_unify_pattern_in_middle(self):
        """Test unify with pattern variable in middle of command."""
        command_tokens = ["nail", "{a}", "to", "door"]
        input_tokens = ["nail", "wood", "to", "door"]
        
        success, bindings = unify(command_tokens, input_tokens)
        assert success is True
        assert bindings == ["wood"]

    def test_unify_empty_lists(self):
        """Test unify with empty token lists."""
        success, bindings = unify([], [])
        assert success is True
        assert bindings == []


class TestExpand:
    """Test the expand function for command expansion."""

    def test_expand_simple_command(self):
        """Test expand with simple command without variables."""
        command = "balance"
        user_input = "balance"
        
        success, args = expand(command, user_input)
        assert success is True
        assert args == []

    def test_expand_with_single_variable(self):
        """Test expand with single pattern variable."""
        command = "examine {a}"
        user_input = "examine toolbox"
        
        success, args = expand(command, user_input)
        assert success is True
        assert args == ["toolbox"]

    def test_expand_with_multiple_variables(self):
        """Test expand with multiple pattern variables."""
        command = "get {a} from {b}"
        user_input = "get hammer from toolbox"
        
        success, args = expand(command, user_input)
        assert success is True
        assert args == ["hammer", "toolbox"]

    def test_expand_length_mismatch(self):
        """Test expand with mismatched token lengths."""
        command = "examine {a}"
        user_input = "examine"
        
        success, args = expand(command, user_input)
        assert success is False
        assert args == []

    def test_expand_too_many_tokens(self):
        """Test expand with too many input tokens."""
        command = "balance"
        user_input = "balance extra tokens"
        
        success, args = expand(command, user_input)
        assert success is False
        assert args == []

    def test_expand_multiword_arguments(self):
        """Test expand handles multiword arguments correctly."""
        command = "enter the {a}"
        user_input = "enter the main"
        
        success, args = expand(command, user_input)
        assert success is True
        assert args == ["main"]


class TestParse:
    """Test the main parse function."""

    def test_parse_valid_simple_command(self):
        """Test parsing valid simple commands."""
        success, action, args = parse("balance")
        assert success is True
        assert action == actions.check_balance
        assert args == []

    def test_parse_valid_command_with_args(self):
        """Test parsing valid commands with arguments."""
        success, action, args = parse("examine toolbox")
        assert success is True
        assert action == actions.examine_thing
        assert args == ["toolbox"]

    def test_parse_command_with_multiple_args(self):
        """Test parsing commands with multiple arguments."""
        success, action, args = parse("get hammer from toolbox")
        assert success is True
        assert action == actions.get_object
        assert args == ["hammer", "toolbox"]

    def test_parse_invalid_command(self):
        """Test parsing invalid commands."""
        success, action, args = parse("invalid command here")
        assert success is False
        assert action == "Don't understand command."
        assert args == []

    def test_parse_empty_input(self):
        """Test parsing empty input."""
        success, action, args = parse("")
        assert success is False
        assert action == "Don't understand command."
        assert args == []

    def test_parse_partial_command(self):
        """Test parsing partial commands that don't match."""
        success, action, args = parse("exam")  # Partial "examine"
        assert success is False
        assert action == "Don't understand command."
        assert args == []

    def test_parse_case_sensitive(self):
        """Test that parsing is case sensitive."""
        success, action, args = parse("BALANCE")  # Uppercase
        assert success is False
        assert action == "Don't understand command."
        assert args == []

    def test_parse_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        # The split() method should handle extra whitespace
        success, action, args = parse("  balance  ")
        assert success is True
        assert action == actions.check_balance
        assert args == []


class TestCommandPatterns:
    """Test specific command patterns from the COMMANDS dictionary."""

    def test_debug_items_command(self):
        """Test debug items command parsing."""
        success, action, args = parse("debug items")
        assert success is True
        assert action == actions.debug_items
        assert args == []

    def test_phone_commands(self):
        """Test phone-related commands."""
        success, action, args = parse("call phone")
        assert success is True
        assert action == actions.call_phone
        assert args == []

        success, action, args = parse("rolodex")
        assert success is True
        assert action == actions.rolodex
        assert args == []

    def test_movement_commands(self):
        """Test room movement commands."""
        commands_and_args = [
            ("go in main", actions.enter_room, ["main"]),
            ("go to bedroom", actions.enter_room, ["bedroom"]),
            ("enter bathroom", actions.enter_room, ["bathroom"]),
            ("enter the closet", actions.enter_room, ["closet"])
        ]
        
        for command, expected_action, expected_args in commands_and_args:
            success, action, args = parse(command)
            assert success is True, f"Failed to parse: {command}"
            assert action == expected_action, f"Wrong action for: {command}"
            assert args == expected_args, f"Wrong args for: {command}"

    def test_object_interaction_commands(self):
        """Test object interaction commands."""
        commands_and_args = [
            ("examine toolbox", actions.examine_thing, ["toolbox"]),
            ("look in fridge", actions.examine_thing, ["fridge"]),
            ("open cabinet", actions.open_thing, ["cabinet"]),
            ("close door", actions.close_thing, ["door"]),
            ("watch tv", actions.watch_tv, ["tv"])
        ]
        
        for command, expected_action, expected_args in commands_and_args:
            success, action, args = parse(command)
            assert success is True, f"Failed to parse: {command}"
            assert action == expected_action, f"Wrong action for: {command}"
            assert args == expected_args, f"Wrong args for: {command}"

    def test_inventory_commands(self):
        """Test inventory-related commands."""
        commands_and_args = [
            ("get hammer from toolbox", actions.get_object, ["hammer", "toolbox"]),
            ("pick up nails from table", actions.get_object, ["nails", "table"]),
            ("inventory", actions.inventory, [])
        ]
        
        for command, expected_action, expected_args in commands_and_args:
            success, action, args = parse(command)
            assert success is True, f"Failed to parse: {command}"
            assert action == expected_action, f"Wrong action for: {command}"
            assert args == expected_args, f"Wrong args for: {command}"

    def test_special_commands(self):
        """Test special game commands."""
        commands_and_args = [
            ("nail wood to exit", actions.nail_self_in, []),
            ("nail wood to door", actions.nail_self_in, []),
            ("nail self in", actions.nail_self_in, []),
            ("nail self in closet", actions.nail_self_in, []),
            ("mail check", actions.mail_check, [])
        ]
        
        for command, expected_action, expected_args in commands_and_args:
            success, action, args = parse(command)
            assert success is True, f"Failed to parse: {command}"
            assert action == expected_action, f"Wrong action for: {command}"
            assert args == expected_args, f"Wrong args for: {command}"

    def test_room_inspection_commands(self):
        """Test room inspection commands."""
        commands_and_args = [
            ("inspect room", actions.inspect_room, []),
            ("view room", actions.inspect_room, []),
            ("look around room", actions.inspect_room, [])
        ]
        
        for command, expected_action, expected_args in commands_and_args:
            success, action, args = parse(command)
            assert success is True, f"Failed to parse: {command}"
            assert action == expected_action, f"Wrong action for: {command}"
            assert args == expected_args, f"Wrong args for: {command}"


class TestCommandsDict:
    """Test the COMMANDS dictionary structure."""

    def test_commands_dict_not_empty(self):
        """Test that COMMANDS dictionary is not empty."""
        assert len(COMMANDS) > 0

    def test_commands_dict_keys_are_strings(self):
        """Test that all keys in COMMANDS are strings."""
        for key in COMMANDS.keys():
            assert isinstance(key, str)

    def test_commands_dict_values_are_callable(self):
        """Test that all values in COMMANDS are callable."""
        for value in COMMANDS.values():
            assert callable(value)

    def test_pattern_variables_in_commands(self):
        """Test that pattern variable commands are properly formatted."""
        pattern_commands = [cmd for cmd in COMMANDS.keys() if '{' in cmd]
        assert len(pattern_commands) > 0
        
        for cmd in pattern_commands:
            # Should have proper opening and closing braces
            assert cmd.count('{') == cmd.count('}')
            
            # Pattern variables should be well-formed
            tokens = cmd.split()
            for token in tokens:
                if '{' in token:
                    assert token.startswith('{') and token.endswith('}')


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_parse_with_special_characters(self):
        """Test parsing with special characters."""
        success, action, args = parse("examine tool-box")
        assert success is True
        assert args == ["tool-box"]

    def test_parse_with_numbers(self):
        """Test parsing with numbers."""
        success, action, args = parse("examine item123")
        assert success is True
        assert args == ["item123"]

    def test_unify_with_mismatched_lengths(self):
        """Test unify with different length lists - zip stops at shorter list."""
        # unify uses zip(), so it only processes the common length
        # Length checking is done in expand(), not unify()
        success, bindings = unify(["a", "b"], ["a"])
        assert success is True  # Only processes the first pair: "a" == "a"
        assert bindings == []

        success, bindings = unify(["a"], ["a", "b"])
        assert success is True  # Only processes the first pair: "a" == "a"
        assert bindings == []
        
        # Test mismatch within the common length
        success, bindings = unify(["a", "b"], ["x", "y"])
        assert success is False  # "a" != "x"
        assert bindings == []

    def test_expand_with_empty_strings(self):
        """Test expand with empty command or input."""
        success, args = expand("", "")
        assert success is True
        assert args == []

        success, args = expand("command", "")
        assert success is False
        assert args == []

        success, args = expand("", "input")
        assert success is False
        assert args == []