"""
test_day_tracking.py

Unit tests for the day computation system (Phase 2).
Tests get_current_day() method on GameState.
"""

from datetime import datetime, timedelta

from src.io_interface import MockIO
from src.core.game_world import GameState


class TestGetCurrentDay:
    """Tests for GameState.get_current_day()."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_day1_at_game_start(self) -> None:
        """Game starts on March 15 at 3:14 AM — should be Day 1."""
        assert self.state.get_current_day() == 1

    def test_day2_on_march_16(self) -> None:
        """March 16, 1982 should be Day 2."""
        self.state.watch.curr_time = datetime(1982, 3, 16, 10, 0)
        assert self.state.get_current_day() == 2

    def test_day3_on_march_17(self) -> None:
        """March 17, 1982 should be Day 3."""
        self.state.watch.curr_time = datetime(1982, 3, 17, 8, 0)
        assert self.state.get_current_day() == 3

    def test_day4_on_march_18(self) -> None:
        """March 18, 1982 should be Day 4."""
        self.state.watch.curr_time = datetime(1982, 3, 18, 12, 0)
        assert self.state.get_current_day() == 4

    def test_day5_on_march_19(self) -> None:
        """March 19, 1982 should be Day 5."""
        self.state.watch.curr_time = datetime(1982, 3, 19, 6, 0)
        assert self.state.get_current_day() == 5

    def test_day6_on_march_20(self) -> None:
        """March 20, 1982 should be Day 6."""
        self.state.watch.curr_time = datetime(1982, 3, 20, 15, 0)
        assert self.state.get_current_day() == 6

    def test_day7_on_march_21(self) -> None:
        """March 21, 1982 should be Day 7."""
        self.state.watch.curr_time = datetime(1982, 3, 21, 0, 0)
        assert self.state.get_current_day() == 7

    def test_day1_at_1159pm(self) -> None:
        """11:59 PM on March 15 should still be Day 1 (date-only comparison)."""
        self.state.watch.curr_time = datetime(1982, 3, 15, 23, 59)
        assert self.state.get_current_day() == 1

    def test_day8_on_march_22_no_cap(self) -> None:
        """March 22 should be Day 8 — no cap at 7."""
        self.state.watch.curr_time = datetime(1982, 3, 22, 9, 0)
        assert self.state.get_current_day() == 8

    def test_day14_on_march_28(self) -> None:
        """March 28 should be Day 14 — days continue well past 7."""
        self.state.watch.curr_time = datetime(1982, 3, 28, 12, 0)
        assert self.state.get_current_day() == 14

    def test_day1_at_midnight(self) -> None:
        """Midnight on March 15 should be Day 1."""
        self.state.watch.curr_time = datetime(1982, 3, 15, 0, 0)
        assert self.state.get_current_day() == 1

    def test_day_advances_across_midnight(self) -> None:
        """Day should advance when crossing midnight boundary."""
        # 11:59 PM March 15 = Day 1
        self.state.watch.curr_time = datetime(1982, 3, 15, 23, 59)
        assert self.state.get_current_day() == 1

        # Advance 2 minutes => 12:01 AM March 16 = Day 2
        self.state.watch.curr_time += timedelta(minutes=2)
        assert self.state.get_current_day() == 2
