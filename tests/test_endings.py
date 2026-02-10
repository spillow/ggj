"""
Tests for the GameEndings class and ending condition logic.
"""

from __future__ import annotations

from datetime import timedelta

from src.io_interface import MockIO
from src.gamestate import GameState
from src.endings import (
    GameEndings,
    VICTORY_TEXT,
    PARTIAL_VICTORY_TEXT,
    DEFEAT_TEXT,
    DREAM_CONFRONTATION_TEXT,
    SECRET_ENDING_TEXT,
)


class TestCheckEnding:
    """Tests for GameEndings.check_ending()."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_no_ending_day1(self):
        """Day 1, no device activation -> None."""
        assert GameEndings.check_ending(self.state) is None

    def test_no_ending_day6(self):
        """Day 6 should not trigger an ending yet."""
        self.state.watch.curr_time += timedelta(days=5)
        assert self.state.get_current_day() == 6
        assert GameEndings.check_ending(self.state) is None

    def test_victory_day7_all_missing(self):
        """Day 7 with all 5 components missing -> victory."""
        self.state.watch.curr_time += timedelta(days=6)
        assert self.state.get_current_day() == 7
        assert self.state.device_state.count_missing_components() == 5
        assert GameEndings.check_ending(self.state) == "victory"

    def test_victory_day7_two_missing(self):
        """Day 7 with exactly 2 missing components -> victory."""
        self.state.watch.curr_time += timedelta(days=6)
        self.state.device_state.build_component("device-frame")
        self.state.device_state.build_component("wiring-harness")
        self.state.device_state.build_component("power-core")
        assert self.state.device_state.count_missing_components() == 2
        assert GameEndings.check_ending(self.state) == "victory"

    def test_partial_victory_day7_one_missing(self):
        """Day 7 with exactly 1 missing component -> partial_victory."""
        self.state.watch.curr_time += timedelta(days=6)
        self.state.device_state.build_component("device-frame")
        self.state.device_state.build_component("wiring-harness")
        self.state.device_state.build_component("power-core")
        self.state.device_state.build_component("focusing-array")
        assert self.state.device_state.count_missing_components() == 1
        assert GameEndings.check_ending(self.state) == "partial_victory"

    def test_defeat_day7_all_built(self):
        """Day 7 with 0 missing components -> defeat."""
        self.state.watch.curr_time += timedelta(days=6)
        for comp in self.state.device_state.COMPONENTS:
            self.state.device_state.build_component(comp)
        assert self.state.device_state.count_missing_components() == 0
        assert GameEndings.check_ending(self.state) == "defeat"

    def test_defeat_device_activated(self):
        """Device activated (any day) -> defeat."""
        self.state.device_activated = True
        assert GameEndings.check_ending(self.state) == "defeat"

    def test_defeat_device_activated_overrides_day(self):
        """Device activated on day 1 still returns defeat."""
        self.state.device_activated = True
        assert self.state.get_current_day() == 1
        assert GameEndings.check_ending(self.state) == "defeat"

    def test_victory_day8(self):
        """Days beyond 7 still trigger endings."""
        self.state.watch.curr_time += timedelta(days=7)
        assert self.state.get_current_day() == 8
        assert GameEndings.check_ending(self.state) == "victory"


class TestCheckSecretEnding:
    """Tests for GameEndings.check_secret_ending()."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def _setup_secret_conditions(self):
        """Set up all conditions for secret ending."""
        self.state.journal_read = True
        self.state.mirror_seen = True
        # All components missing (>= 2)
        self.state.watch.curr_time += timedelta(days=5)  # Day 6

    def test_all_conditions_met(self):
        """All secret conditions met -> True."""
        self._setup_secret_conditions()
        assert GameEndings.check_secret_ending(self.state) is True

    def test_missing_journal(self):
        """Journal not read -> False."""
        self._setup_secret_conditions()
        self.state.journal_read = False
        assert GameEndings.check_secret_ending(self.state) is False

    def test_missing_mirror(self):
        """Mirror not seen -> False."""
        self._setup_secret_conditions()
        self.state.mirror_seen = False
        assert GameEndings.check_secret_ending(self.state) is False

    def test_too_few_missing_components(self):
        """Only 1 missing component -> False."""
        self._setup_secret_conditions()
        self.state.device_state.build_component("device-frame")
        self.state.device_state.build_component("wiring-harness")
        self.state.device_state.build_component("power-core")
        self.state.device_state.build_component("focusing-array")
        assert self.state.device_state.count_missing_components() == 1
        assert GameEndings.check_secret_ending(self.state) is False

    def test_day_too_early(self):
        """Day 5 -> False (needs Day 6+)."""
        self.state.journal_read = True
        self.state.mirror_seen = True
        self.state.watch.curr_time += timedelta(days=4)  # Day 5
        assert self.state.get_current_day() == 5
        assert GameEndings.check_secret_ending(self.state) is False

    def test_day6_is_sufficient(self):
        """Day 6 exactly is enough."""
        self._setup_secret_conditions()
        assert self.state.get_current_day() == 6
        assert GameEndings.check_secret_ending(self.state) is True

    def test_day7_also_works(self):
        """Day 7 is also valid."""
        self.state.journal_read = True
        self.state.mirror_seen = True
        self.state.watch.curr_time += timedelta(days=6)  # Day 7
        assert GameEndings.check_secret_ending(self.state) is True


class TestDisplayMethods:
    """Tests that display methods produce output."""

    def setup_method(self):
        self.mock_io = MockIO()

    def test_display_victory(self):
        GameEndings.display_victory(self.mock_io)
        output = "\n".join(self.mock_io.outputs)
        assert "THE ANOMALY HAS CLOSED" in output
        assert "front door" in output

    def test_display_partial_victory(self):
        GameEndings.display_partial_victory(self.mock_io)
        output = "\n".join(self.mock_io.outputs)
        assert "THE ANOMALY HAS CLOSED" in output
        assert "scorched" in output

    def test_display_defeat(self):
        GameEndings.display_defeat(self.mock_io)
        output = "\n".join(self.mock_io.outputs)
        assert "GAME OVER" in output
        assert "rift widens" in output

    def test_display_dream_confrontation(self):
        GameEndings.display_dream_confrontation(self.mock_io)
        output = "\n".join(self.mock_io.outputs)
        assert "Darkness" in output
        assert "You still need me" in output

    def test_display_secret_ending(self):
        GameEndings.display_secret_ending(self.mock_io)
        output = "\n".join(self.mock_io.outputs)
        assert "Your legs work fine" in output
        assert "sunlight" in output


class TestGameStateFlags:
    """Tests for the Phase 5 flags on GameState."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_game_over_default(self):
        assert self.state.game_over is False

    def test_ending_type_default(self):
        assert self.state.ending_type is None

    def test_in_dream_confrontation_default(self):
        assert self.state.in_dream_confrontation is False


class TestExamineSecretEndingTrigger:
    """Tests that GameState.Examine() triggers secret ending correctly."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_examine_triggers_dream_when_secret_conditions_met(self):
        """When secret conditions are met and feel <= 0, dream starts."""
        self.state.journal_read = True
        self.state.mirror_seen = True
        self.state.watch.curr_time += timedelta(days=5)  # Day 6
        self.state.hero.feel = 0

        self.state.Examine()

        assert self.state.in_dream_confrontation is True
        assert self.state.hero.feel == self.state.hero.INITIAL_FEEL
        output = "\n".join(self.mock_io.outputs)
        assert "Darkness" in output

    def test_examine_does_not_run_ae_during_secret(self):
        """When secret ending triggers, AE should NOT run."""
        self.state.journal_read = True
        self.state.mirror_seen = True
        self.state.watch.curr_time += timedelta(days=5)  # Day 6
        self.state.hero.feel = 0
        initial_phase = self.state.alter_ego.current_phase

        self.state.Examine()

        # AE phase should not have advanced
        assert self.state.alter_ego.current_phase == initial_phase

    def test_examine_triggers_defeat_when_device_activated(self):
        """When AE completes device during Examine, game_over is set."""
        # Set up AE at phase 4 about to activate
        self.state.alter_ego.current_phase = 4
        self.state.device_state.ae_phase = 4
        # Build all components except convergence-device
        for comp in ["device-frame", "wiring-harness", "power-core", "focusing-array"]:
            self.state.device_state.build_component(comp)
        # Put signal-amplifier in apartment for AE to use
        from src.core.game_objects import Object
        Object("signal-amplifier", self.state.apartment.main.toolbox)

        self.state.hero.feel = 0
        self.state.Examine()

        assert self.state.device_activated is True
        assert self.state.game_over is True
        assert self.state.ending_type == "defeat"
        output = "\n".join(self.mock_io.outputs)
        assert "GAME OVER" in output
