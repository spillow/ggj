"""
test_sabotage_commands.py

Unit tests for the 6 Phase 3 commands:
- DisassembleFrameCommand
- CutWiresCommand
- RemoveBatteryCommand
- RemoveCrystalCommand
- BarricadeBedroomCommand
- ReadJournalCommand
"""

import pytest
from datetime import timedelta

from src.io_interface import MockIO
from src.core.game_world import GameState
from src.core.game_objects import Object
from src.commands.game_commands import (
    DisassembleFrameCommand,
    CutWiresCommand,
    RemoveBatteryCommand,
    RemoveCrystalCommand,
    BarricadeBedroomCommand,
    ReadJournalCommand,
)


class TestDisassembleFrameCommand:
    """Tests for the disassemble frame sabotage command."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_fails_outside_bedroom(self):
        """Must be in bedroom to disassemble."""
        # hero starts in main room
        hammer = Object("hammer", None)
        hammer.weight = 15
        hammer.parent = self.state.apartment.main
        self.state.apartment.main.contents.append(hammer)
        self.hero.Pickup(hammer)
        self.state.device_state.build_component("device-frame")

        cmd = DisassembleFrameCommand()
        assert not cmd.can_execute(self.state)

    def test_fails_without_hammer(self):
        """Must have hammer in inventory."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)
        self.state.device_state.build_component("device-frame")

        cmd = DisassembleFrameCommand()
        assert not cmd.can_execute(self.state)

    def test_fails_when_not_built(self):
        """device-frame must be BUILT."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)
        hammer = Object("hammer", None)
        hammer.weight = 15
        hammer.parent = bedroom
        bedroom.contents.append(hammer)
        self.hero.Pickup(hammer)

        cmd = DisassembleFrameCommand()
        assert not cmd.can_execute(self.state)

    def test_succeeds_with_all_prereqs(self):
        """Disassemble succeeds with hammer, in bedroom, frame built."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        hammer = Object("hammer", None)
        hammer.weight = 15
        hammer.parent = bedroom
        bedroom.contents.append(hammer)
        self.hero.Pickup(hammer)

        # Build the frame and place a frame object
        self.state.device_state.build_component("device-frame")
        Object("device-frame", bedroom)

        cmd = DisassembleFrameCommand()
        assert cmd.can_execute(self.state)
        result = cmd.execute(self.state)
        assert result.success
        assert not self.state.device_state.is_component_built("device-frame")
        assert bedroom.GetFirstItemByName("device-frame") is None

    def test_time_and_feel_cost(self):
        """Disassembling costs 1 hour and 15 feel."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        hammer = Object("hammer", None)
        hammer.weight = 15
        hammer.parent = bedroom
        bedroom.contents.append(hammer)
        self.hero.Pickup(hammer)

        self.state.device_state.build_component("device-frame")
        Object("device-frame", bedroom)

        initial_feel = self.hero.feel
        initial_time = self.state.watch.curr_time

        cmd = DisassembleFrameCommand()
        cmd.execute(self.state)

        assert self.hero.feel == initial_feel - 15
        assert self.state.watch.curr_time == initial_time + timedelta(hours=1)


class TestCutWiresCommand:
    """Tests for the cut wires sabotage command."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_fails_without_wire_cutters(self):
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)
        self.state.device_state.build_component("wiring-harness")

        cmd = CutWiresCommand()
        assert not cmd.can_execute(self.state)

    def test_fails_when_not_built(self):
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)
        cutters = Object("wire-cutters", None)
        cutters.weight = 5
        cutters.parent = bedroom
        bedroom.contents.append(cutters)
        self.hero.Pickup(cutters)

        cmd = CutWiresCommand()
        assert not cmd.can_execute(self.state)

    def test_succeeds_correctly(self):
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        cutters = Object("wire-cutters", None)
        cutters.weight = 5
        cutters.parent = bedroom
        bedroom.contents.append(cutters)
        self.hero.Pickup(cutters)

        self.state.device_state.build_component("wiring-harness")
        Object("wiring-harness", bedroom)

        initial_feel = self.hero.feel
        initial_time = self.state.watch.curr_time

        cmd = CutWiresCommand()
        result = cmd.execute(self.state)

        assert result.success
        assert not self.state.device_state.is_component_built("wiring-harness")
        assert self.hero.feel == initial_feel - 10
        assert self.state.watch.curr_time == initial_time + timedelta(minutes=30)


class TestRemoveBatteryCommand:
    """Tests for the remove battery sabotage command."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_fails_when_not_built(self):
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        cmd = RemoveBatteryCommand()
        assert not cmd.can_execute(self.state)

    def test_fails_outside_bedroom(self):
        self.state.device_state.build_component("power-core")
        cmd = RemoveBatteryCommand()
        assert not cmd.can_execute(self.state)

    def test_succeeds_correctly(self):
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        self.state.device_state.build_component("power-core")
        Object("power-core", bedroom)

        initial_feel = self.hero.feel
        initial_time = self.state.watch.curr_time

        cmd = RemoveBatteryCommand()
        result = cmd.execute(self.state)

        assert result.success
        assert not self.state.device_state.is_component_built("power-core")
        assert bedroom.GetFirstItemByName("power-core") is None
        assert self.hero.feel == initial_feel - 5
        assert self.state.watch.curr_time == initial_time + timedelta(minutes=20)


class TestRemoveCrystalCommand:
    """Tests for the remove crystal sabotage command."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_fails_when_not_built(self):
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        cmd = RemoveCrystalCommand()
        assert not cmd.can_execute(self.state)

    def test_fails_outside_bedroom(self):
        self.state.device_state.build_component("focusing-array")
        cmd = RemoveCrystalCommand()
        assert not cmd.can_execute(self.state)

    def test_succeeds_correctly(self):
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        self.state.device_state.build_component("focusing-array")
        Object("focusing-array", bedroom)

        initial_feel = self.hero.feel
        initial_time = self.state.watch.curr_time

        cmd = RemoveCrystalCommand()
        result = cmd.execute(self.state)

        assert result.success
        assert not self.state.device_state.is_component_built("focusing-array")
        assert bedroom.GetFirstItemByName("focusing-array") is None
        assert self.hero.feel == initial_feel - 5
        assert self.state.watch.curr_time == initial_time + timedelta(minutes=20)


class TestBarricadeBedroomCommand:
    """Tests for the barricade bedroom command."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def _give_materials(self):
        """Give hero hammer, nails, and plywood."""
        main = self.state.apartment.main
        hammer = Object("hammer", main)
        hammer.weight = 15
        nails = Object("box-of-nails", main)
        nails.weight = 10
        plywood = Object("plywood-sheet", main)
        plywood.weight = 25
        self.hero.Pickup(hammer)
        self.hero.Pickup(nails)
        self.hero.Pickup(plywood)

    def test_fails_when_inside_bedroom(self):
        """Cannot barricade from inside."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)
        self._give_materials()

        cmd = BarricadeBedroomCommand()
        assert not cmd.can_execute(self.state)

    def test_fails_without_hammer(self):
        # Only give nails and plywood
        main = self.state.apartment.main
        Object("box-of-nails", main)
        Object("plywood-sheet", main)
        self.hero.Pickup(main.GetFirstItemByName("box-of-nails"))
        self.hero.Pickup(main.GetFirstItemByName("plywood-sheet"))

        cmd = BarricadeBedroomCommand()
        assert not cmd.can_execute(self.state)

    def test_fails_without_nails(self):
        main = self.state.apartment.main
        hammer = Object("hammer", main)
        hammer.weight = 15
        plywood = Object("plywood-sheet", main)
        plywood.weight = 25
        self.hero.Pickup(hammer)
        self.hero.Pickup(plywood)

        cmd = BarricadeBedroomCommand()
        assert not cmd.can_execute(self.state)

    def test_fails_without_plywood(self):
        main = self.state.apartment.main
        hammer = Object("hammer", main)
        hammer.weight = 15
        nails = Object("box-of-nails", main)
        nails.weight = 10
        self.hero.Pickup(hammer)
        self.hero.Pickup(nails)

        cmd = BarricadeBedroomCommand()
        assert not cmd.can_execute(self.state)

    def test_succeeds_and_consumes_materials(self):
        """Barricading consumes plywood and nails but keeps hammer."""
        self._give_materials()

        cmd = BarricadeBedroomCommand()
        assert cmd.can_execute(self.state)
        result = cmd.execute(self.state)

        assert result.success
        assert self.state.bedroom_barricaded is True
        assert self.state.apartment.bedroom.barricaded is True

        # Plywood and nails consumed
        assert self.hero.GetFirstItemByName("plywood-sheet") is None
        assert self.hero.GetFirstItemByName("box-of-nails") is None
        # Hammer is kept
        assert self.hero.GetFirstItemByName("hammer") is not None

    def test_time_and_feel_cost(self):
        self._give_materials()
        initial_feel = self.hero.feel
        initial_time = self.state.watch.curr_time

        cmd = BarricadeBedroomCommand()
        cmd.execute(self.state)

        assert self.hero.feel == initial_feel - 15
        assert self.state.watch.curr_time == initial_time + timedelta(hours=1)


class TestReadJournalCommand:
    """Tests for the read journal investigation command."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_fails_when_journal_inaccessible(self):
        """Journal must be in inventory or nearby."""
        # Hero is in main room, journal is in bedroom bookshelf
        cmd = ReadJournalCommand()
        assert not cmd.can_execute(self.state)

    def test_succeeds_from_bedroom_bookshelf(self):
        """Can read journal when in bedroom (journal is in bookshelf)."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        cmd = ReadJournalCommand()
        assert cmd.can_execute(self.state)
        result = cmd.execute(self.state)
        assert result.success

    def test_sets_journal_read_flag(self):
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        assert not self.state.journal_read

        cmd = ReadJournalCommand()
        cmd.execute(self.state)

        assert self.state.journal_read is True

    def test_succeeds_from_inventory(self):
        """Can read journal when carrying it."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        # Pick up the journal
        journal = bedroom.bookshelf.GetFirstItemByName("journal")
        self.hero.Pickup(journal)

        # Go back to main room
        self.state.apartment.main.Enter(bedroom, self.hero)

        cmd = ReadJournalCommand()
        assert cmd.can_execute(self.state)
        result = cmd.execute(self.state)
        assert result.success
        assert self.state.journal_read is True

    def test_no_time_or_feel_cost(self):
        """Reading journal should not cost time or feel."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        initial_feel = self.hero.feel
        initial_time = self.state.watch.curr_time

        cmd = ReadJournalCommand()
        cmd.execute(self.state)

        assert self.hero.feel == initial_feel
        assert self.state.watch.curr_time == initial_time

    def test_journal_text_output(self):
        """Reading journal outputs backstory text."""
        bedroom = self.state.apartment.bedroom
        bedroom.Enter(self.state.apartment.main, self.hero)

        cmd = ReadJournalCommand()
        cmd.execute(self.state)

        output = "\n".join(self.mock_io.outputs)
        assert "worn leather journal" in output
        assert "imaginary friend" in output
        assert "door became a wall" in output


class TestMirrorWithGamestate:
    """Tests for the updated Mirror with day-based flicker."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_mirror_day1_no_flicker(self):
        """On Day 1, mirror should show normal text only."""
        bathroom = self.state.apartment.bathroom
        bathroom.Enter(self.state.apartment.main, self.hero)
        self.mock_io.outputs.clear()

        bathroom.mirror.Examine(self.hero)

        output = "\n".join(self.mock_io.outputs)
        assert "You look tired" in output
        assert "reflection moves" not in output
        assert not self.state.mirror_seen

    def test_mirror_day4_shows_flicker(self):
        """On Day 4+, mirror should show AE flicker and set flag."""
        # Advance to Day 4 (March 18)
        self.state.watch.curr_time = self.state.watch.curr_time.replace(day=18)

        bathroom = self.state.apartment.bathroom
        bathroom.Enter(self.state.apartment.main, self.hero)
        self.mock_io.outputs.clear()

        bathroom.mirror.Examine(self.hero)

        output = "\n".join(self.mock_io.outputs)
        assert "You look tired" in output
        assert "reflection moves on its own" in output
        assert self.state.mirror_seen is True

    def test_mirror_day7_shows_flicker(self):
        """Day 7 also has flicker."""
        self.state.watch.curr_time = self.state.watch.curr_time.replace(day=21)

        bathroom = self.state.apartment.bathroom
        bathroom.Enter(self.state.apartment.main, self.hero)
        self.mock_io.outputs.clear()

        bathroom.mirror.Examine(self.hero)

        assert self.state.mirror_seen is True


class TestDeviceStateIntegration:
    """Integration tests for device state with GameState."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_gamestate_has_device_state(self):
        assert hasattr(self.state, 'device_state')
        assert isinstance(self.state.device_state, __import__('src.core.device_state', fromlist=['DeviceState']).DeviceState)

    def test_gamestate_has_journal_read_flag(self):
        assert hasattr(self.state, 'journal_read')
        assert self.state.journal_read is False

    def test_gamestate_has_mirror_seen_flag(self):
        assert hasattr(self.state, 'mirror_seen')
        assert self.state.mirror_seen is False

    def test_gamestate_has_bedroom_barricaded_flag(self):
        assert hasattr(self.state, 'bedroom_barricaded')
        assert self.state.bedroom_barricaded is False

    def test_bedroom_has_barricaded_flag(self):
        assert hasattr(self.state.apartment.bedroom, 'barricaded')
        assert self.state.apartment.bedroom.barricaded is False


class TestCommandParsing:
    """Tests that the 6 new commands parse correctly."""

    def setup_method(self):
        self.mock_io = MockIO()

    def test_parse_disassemble_frame(self):
        from src.inputparser import parse
        ok, cmd = parse("disassemble frame")
        assert ok
        assert isinstance(cmd, DisassembleFrameCommand)

    def test_parse_cut_wires(self):
        from src.inputparser import parse
        ok, cmd = parse("cut wires")
        assert ok
        assert isinstance(cmd, CutWiresCommand)

    def test_parse_remove_battery(self):
        from src.inputparser import parse
        ok, cmd = parse("remove battery")
        assert ok
        assert isinstance(cmd, RemoveBatteryCommand)

    def test_parse_remove_crystal(self):
        from src.inputparser import parse
        ok, cmd = parse("remove crystal")
        assert ok
        assert isinstance(cmd, RemoveCrystalCommand)

    def test_parse_barricade_bedroom(self):
        from src.inputparser import parse
        ok, cmd = parse("barricade bedroom")
        assert ok
        assert isinstance(cmd, BarricadeBedroomCommand)

    def test_parse_read_journal(self):
        from src.inputparser import parse
        ok, cmd = parse("read journal")
        assert ok
        assert isinstance(cmd, ReadJournalCommand)
