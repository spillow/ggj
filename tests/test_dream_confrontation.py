"""
Tests for the dream confrontation sequence and LetGo/HoldOn commands.
"""

from __future__ import annotations

from datetime import timedelta

from src.io_interface import MockIO
from src.gamestate import GameState
from src.commands.game_commands import LetGoCommand, HoldOnCommand
from src.commands.base_command import CommandResult


class TestLetGoCommand:
    """Tests for the LetGoCommand."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_let_go_outside_dream(self):
        """let go outside dream confrontation fails."""
        cmd = LetGoCommand()
        result = cmd.execute(self.state)
        assert result.success is False
        assert "doesn't make sense" in result.message

    def test_let_go_during_dream(self):
        """let go during dream triggers secret ending."""
        self.state.in_dream_confrontation = True
        cmd = LetGoCommand()
        result = cmd.execute(self.state)
        assert result.success is True
        assert self.state.game_over is True
        assert self.state.ending_type == "secret"
        assert self.state.in_dream_confrontation is False
        output = "\n".join(self.mock_io.outputs)
        assert "Your legs work fine" in output

    def test_let_go_cannot_undo(self):
        cmd = LetGoCommand()
        assert cmd.can_undo() is False


class TestHoldOnCommand:
    """Tests for the HoldOnCommand."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_hold_on_outside_dream(self):
        """hold on outside dream confrontation fails."""
        cmd = HoldOnCommand()
        result = cmd.execute(self.state)
        assert result.success is False
        assert "doesn't make sense" in result.message

    def test_hold_on_during_dream(self):
        """hold on during dream clears dream state and resumes."""
        self.state.in_dream_confrontation = True
        cmd = HoldOnCommand()
        result = cmd.execute(self.state)
        assert result.success is True
        assert self.state.in_dream_confrontation is False
        assert self.state.game_over is False
        assert self.state.hero.feel == self.state.hero.INITIAL_FEEL
        output = "\n".join(self.mock_io.outputs)
        assert "You hold on" in output
        # IntroPrompt should have been called
        assert "You wake up" in output

    def test_hold_on_cannot_undo(self):
        cmd = HoldOnCommand()
        assert cmd.can_undo() is False


class TestInputParserIntegration:
    """Tests that 'let go' and 'hold on' are parseable."""

    def setup_method(self):
        self.mock_io = MockIO()

    def test_parse_let_go(self):
        from src.inputparser import parse
        ok, cmd = parse("let go", self.mock_io)
        assert ok is True
        assert isinstance(cmd, LetGoCommand)

    def test_parse_hold_on(self):
        from src.inputparser import parse
        ok, cmd = parse("hold on", self.mock_io)
        assert ok is True
        assert isinstance(cmd, HoldOnCommand)


class TestDreamFullSequence:
    """Integration tests for the full dream confrontation flow."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_secret_ending_full_flow(self):
        """Full flow: conditions met -> feel 0 -> dream -> let go -> secret ending."""
        # Set up secret conditions
        self.state.journal_read = True
        self.state.mirror_seen = True
        self.state.watch.curr_time += timedelta(days=5)  # Day 6

        # Trigger passout
        self.state.hero.feel = 0
        self.state.Examine()

        # Should be in dream
        assert self.state.in_dream_confrontation is True
        output = "\n".join(self.mock_io.outputs)
        assert "Darkness" in output

        # Now let go
        self.mock_io.outputs.clear()
        cmd = LetGoCommand()
        result = self.state.command_invoker.execute_command(cmd, self.state)
        assert result.success is True
        assert self.state.game_over is True
        assert self.state.ending_type == "secret"

    def test_hold_on_then_continue(self):
        """Full flow: conditions met -> feel 0 -> dream -> hold on -> continue."""
        self.state.journal_read = True
        self.state.mirror_seen = True
        self.state.watch.curr_time += timedelta(days=5)  # Day 6

        self.state.hero.feel = 0
        self.state.Examine()
        assert self.state.in_dream_confrontation is True

        # Hold on
        self.mock_io.outputs.clear()
        cmd = HoldOnCommand()
        result = self.state.command_invoker.execute_command(cmd, self.state)
        assert result.success is True
        assert self.state.in_dream_confrontation is False
        assert self.state.game_over is False
        # Hero feel should be reset to initial
        assert self.state.hero.feel == self.state.hero.INITIAL_FEEL
