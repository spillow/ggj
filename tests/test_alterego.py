"""
Tests for the AlterEgo system.
"""

import pytest
from src.alterego import AlterEgo
from src.gamestate import GameState
from src.io_interface import MockIO


class TestAlterEgo:
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.alter_ego = AlterEgo()

    def test_alter_ego_initialization(self):
        """Test AlterEgo can be created."""
        alter_ego = AlterEgo()
        assert alter_ego is not None

    def test_alter_ego_run_method(self):
        """Test AlterEgo run method can be called without errors."""
        # This tests line 7 which was missing coverage
        result = self.alter_ego.run(self.state)
        assert result is None  # run() method returns None