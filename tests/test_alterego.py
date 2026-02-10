"""
Comprehensive tests for the Alter Ego 5-phase AI system (Phase 4).

Tests cover:
    - AE initialization and phase tracking
    - Phase 1 (Surveying): ordering materials, affordability checks
    - Phase 2 (Frame): building device-frame, material consumption
    - Phase 3 (Wiring): building wiring-harness, dependency on frame
    - Phase 4 (Power Core): building power-core and focusing-array
    - Phase 5 (Activation): installing convergence-device, activation flag
    - Closet trap counter-mechanic
    - Barricade counter-mechanic
    - Item search helpers (_find_item_in_apartment)
    - Full 5-phase lifecycle tests
    - Evidence text in IntroPrompt
    - SuperNumber Day 6+ conditional response
"""

import pytest
from datetime import timedelta

from src.alterego import AlterEgo
from src.gamestate import GameState
from src.io_interface import MockIO
from src.core.game_objects import Object, Container
from src.core.rooms import Closet
from src.delivery import EventQueue


class TestAlterEgoInitialization:
    """Tests for AlterEgo initial state."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.ae = AlterEgo()

    def test_starts_at_phase_0(self):
        """AE starts at phase 0 (not started)."""
        assert self.ae.current_phase == 0

    def test_orders_placed_empty(self):
        """AE starts with no orders placed."""
        assert self.ae.orders_placed == []

    def test_ae_is_not_none(self):
        """AlterEgo can be created."""
        assert self.ae is not None


class TestAlterEgoPhaseAdvancement:
    """Tests for AE phase advancement logic."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae

    def test_advances_to_phase_1_on_first_run(self):
        """AE advances to phase 1 on first run()."""
        self.ae.run(self.state)
        assert self.ae.current_phase == 1

    def test_advances_to_phase_2_on_second_run(self):
        """AE advances to phase 2 on second run()."""
        self.ae.run(self.state)
        self.ae.run(self.state)
        assert self.ae.current_phase == 2

    def test_does_not_advance_past_phase_5(self):
        """AE does not advance past phase 5."""
        for _ in range(7):
            self.ae.run(self.state)
        assert self.ae.current_phase == 5

    def test_syncs_ae_phase_to_device_state(self):
        """AE phase is synced to device_state.ae_phase."""
        self.ae.run(self.state)
        assert self.state.device_state.ae_phase == 1

    def test_time_advances_6_hours_per_run(self):
        """Each run() advances time by ~6 hours."""
        start_time = self.state.watch.curr_time
        self.ae.run(self.state)
        assert self.state.watch.curr_time == start_time + timedelta(hours=6)


class TestPhaseSurveying:
    """Tests for Phase 1 - Surveying."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae

    def test_places_correct_orders_if_money_available(self):
        """Phase 1 places orders for copper-wire, metal-brackets, vacuum-tubes, battery-pack."""
        self.state.hero.curr_balance = 200
        self.ae.run(self.state)
        assert "copper-wire" in self.ae.orders_placed
        assert "metal-brackets" in self.ae.orders_placed
        assert "vacuum-tubes" in self.ae.orders_placed
        assert "battery-pack" in self.ae.orders_placed

    def test_deducts_money_correctly(self):
        """Phase 1 deducts correct costs: 15 + 10 + 20 + 12 = $57."""
        self.state.hero.curr_balance = 200
        self.ae.run(self.state)
        assert self.state.hero.curr_balance == 200 - 57

    def test_skips_orders_if_insufficient_funds(self):
        """Phase 1 skips orders that the hero can't afford."""
        self.state.hero.curr_balance = 20  # Only enough for copper-wire ($15)
        self.ae.run(self.state)
        # balance=20, copper-wire=$15 → 5 left
        # metal-brackets=$10 → can't afford, so only copper-wire ordered
        assert "copper-wire" in self.ae.orders_placed
        assert "metal-brackets" not in self.ae.orders_placed
        assert self.state.hero.curr_balance == 5

    def test_zero_balance_no_orders(self):
        """Phase 1 places no orders when hero has $0."""
        self.state.hero.curr_balance = 0
        self.ae.run(self.state)
        assert len(self.ae.orders_placed) == 0

    def test_schedules_deliveries_to_event_queue(self):
        """Phase 1 schedules delivery events."""
        self.state.hero.curr_balance = 200
        self.ae.run(self.state)
        # Should have scheduled 4 delivery events
        assert len(self.state.event_queue.queue) == 4


class TestPhaseFrame:
    """Tests for Phase 2 - Frame construction."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae
        self.state.hero.curr_balance = 500  # Plenty of money

    def _place_materials_in_toolbox(self):
        """Place all frame materials in the toolbox."""
        toolbox = self.state.apartment.main.toolbox
        Object("plywood-sheet", toolbox)
        Object("metal-brackets", toolbox)
        Object("box-of-nails", toolbox)
        hammer = Object("hammer", toolbox)
        return hammer

    def test_builds_frame_when_all_materials_available(self):
        """Phase 2 builds device-frame when all materials present."""
        self._place_materials_in_toolbox()
        # Run phase 1 first (to advance to phase 2)
        self.ae.run(self.state)
        self.ae.run(self.state)
        assert self.state.device_state.is_component_built("device-frame")

    def test_creates_device_frame_object_in_bedroom(self):
        """Phase 2 creates a device-frame Object in the bedroom."""
        self._place_materials_in_toolbox()
        self.ae.run(self.state)  # Phase 1
        self.ae.run(self.state)  # Phase 2
        frame = self.state.apartment.bedroom.GetFirstItemByName("device-frame")
        assert frame is not None

    def test_consumes_plywood_brackets_nails_but_not_hammer(self):
        """Phase 2 consumes plywood/brackets/nails but keeps hammer."""
        self._place_materials_in_toolbox()
        self.ae.run(self.state)  # Phase 1
        self.ae.run(self.state)  # Phase 2
        
        # Consumed items should not be in toolbox
        toolbox = self.state.apartment.main.toolbox
        assert toolbox.GetFirstItemByName("plywood-sheet") is None
        assert toolbox.GetFirstItemByName("metal-brackets") is None
        assert toolbox.GetFirstItemByName("box-of-nails") is None
        
        # Hammer should be in bedroom (moved there)
        bedroom = self.state.apartment.bedroom
        assert bedroom.GetFirstItemByName("hammer") is not None

    def test_skips_building_when_materials_missing(self):
        """Phase 2 skips building when not all materials present."""
        # Only place plywood, not everything
        Object("plywood-sheet", self.state.apartment.main.toolbox)
        self.ae.run(self.state)  # Phase 1
        self.ae.run(self.state)  # Phase 2
        assert not self.state.device_state.is_component_built("device-frame")

    def test_orders_next_round_materials(self):
        """Phase 2 orders soldering-iron, insulated-cable, copper-coil."""
        self.ae.run(self.state)  # Phase 1
        self.ae.run(self.state)  # Phase 2
        assert "soldering-iron" in self.ae.orders_placed
        assert "insulated-cable" in self.ae.orders_placed
        assert "copper-coil" in self.ae.orders_placed


class TestPhaseWiring:
    """Tests for Phase 3 - Wiring harness construction."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae
        self.state.hero.curr_balance = 500

    def test_builds_wiring_when_frame_and_materials_present(self):
        """Phase 3 builds wiring-harness when frame is built and materials present."""
        # Pre-build the frame
        self.state.device_state.build_component("device-frame")
        # Place wiring materials
        toolbox = self.state.apartment.main.toolbox
        Object("copper-wire", toolbox)
        Object("insulated-cable", toolbox)
        Object("soldering-iron", toolbox)
        
        self.ae.run(self.state)  # Phase 1
        self.ae.run(self.state)  # Phase 2
        self.ae.run(self.state)  # Phase 3
        assert self.state.device_state.is_component_built("wiring-harness")

    def test_skips_when_frame_not_built(self):
        """Phase 3 skips wiring if frame is not built."""
        # Place wiring materials but don't build the frame
        toolbox = self.state.apartment.main.toolbox
        Object("copper-wire", toolbox)
        Object("insulated-cable", toolbox)
        Object("soldering-iron", toolbox)
        
        self.ae.run(self.state)  # Phase 1
        self.ae.run(self.state)  # Phase 2
        self.ae.run(self.state)  # Phase 3
        assert not self.state.device_state.is_component_built("wiring-harness")

    def test_skips_when_materials_missing(self):
        """Phase 3 skips wiring when materials are missing."""
        self.state.device_state.build_component("device-frame")
        # No wiring materials placed
        self.ae.run(self.state)  # Phase 1
        self.ae.run(self.state)  # Phase 2
        self.ae.run(self.state)  # Phase 3
        assert not self.state.device_state.is_component_built("wiring-harness")

    def test_orders_next_round_materials(self):
        """Phase 3 orders crystal-oscillator, signal-amplifier, ice-cubes."""
        self.ae.run(self.state)  # Phase 1
        self.ae.run(self.state)  # Phase 2
        self.ae.run(self.state)  # Phase 3
        assert "crystal-oscillator" in self.ae.orders_placed
        assert "signal-amplifier" in self.ae.orders_placed
        assert "ice-cubes" in self.ae.orders_placed


class TestPhasePowerCore:
    """Tests for Phase 4 - Power core and focusing array."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae
        self.state.hero.curr_balance = 500

    def test_builds_power_core_when_materials_present(self):
        """Phase 4 builds power-core from battery-pack + copper-coil."""
        toolbox = self.state.apartment.main.toolbox
        Object("battery-pack", toolbox)
        Object("copper-coil", toolbox)
        
        # Run 4 phases
        for _ in range(4):
            self.ae.run(self.state)
        assert self.state.device_state.is_component_built("power-core")

    def test_builds_focusing_array_when_materials_present(self):
        """Phase 4 builds focusing-array from crystal-oscillator + ice-cubes."""
        toolbox = self.state.apartment.main.toolbox
        Object("crystal-oscillator", toolbox)
        Object("ice-cubes", toolbox)
        
        for _ in range(4):
            self.ae.run(self.state)
        assert self.state.device_state.is_component_built("focusing-array")

    def test_builds_neither_when_materials_missing(self):
        """Phase 4 builds neither when no materials present."""
        for _ in range(4):
            self.ae.run(self.state)
        assert not self.state.device_state.is_component_built("power-core")
        assert not self.state.device_state.is_component_built("focusing-array")

    def test_builds_both_when_all_materials_present(self):
        """Phase 4 builds both power-core and focusing-array."""
        toolbox = self.state.apartment.main.toolbox
        Object("battery-pack", toolbox)
        Object("copper-coil", toolbox)
        Object("crystal-oscillator", toolbox)
        Object("ice-cubes", toolbox)
        
        for _ in range(4):
            self.ae.run(self.state)
        assert self.state.device_state.is_component_built("power-core")
        assert self.state.device_state.is_component_built("focusing-array")


class TestPhaseActivation:
    """Tests for Phase 5 - Activation."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae
        self.state.hero.curr_balance = 500

    def test_sets_device_activated_when_complete(self):
        """Phase 5 sets device_activated when all components are BUILT."""
        # Pre-build all components except convergence-device
        self.state.device_state.build_component("device-frame")
        self.state.device_state.build_component("wiring-harness")
        self.state.device_state.build_component("power-core")
        self.state.device_state.build_component("focusing-array")
        
        # Place the signal-amplifier
        Object("signal-amplifier", self.state.apartment.main.toolbox)
        
        for _ in range(5):
            self.ae.run(self.state)
        assert self.state.device_activated is True

    def test_does_not_set_flag_when_incomplete(self):
        """Phase 5 does NOT set device_activated when device is incomplete."""
        # Only build some components, no signal-amplifier
        self.state.device_state.build_component("device-frame")
        
        for _ in range(5):
            self.ae.run(self.state)
        assert self.state.device_activated is False

    def test_installs_convergence_device_from_amplifier(self):
        """Phase 5 creates convergence-device from signal-amplifier."""
        Object("signal-amplifier", self.state.apartment.main.toolbox)
        
        for _ in range(5):
            self.ae.run(self.state)
        assert self.state.device_state.is_component_built("convergence-device")
        device = self.state.apartment.bedroom.GetFirstItemByName("convergence-device")
        assert device is not None


class TestClosetTrap:
    """Tests for closet trap counter-mechanic."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae

    def test_phase_does_not_advance_when_trapped(self):
        """AE phase does not advance when trapped in closet."""
        # Put hero in closet and nail it shut
        closet = self.state.apartment.closet
        self.state.hero.ChangeRoom(closet)
        closet.state = Closet.State.NAILED
        
        self.ae.run(self.state)
        assert self.ae.current_phase == 0  # Did NOT advance

    def test_closet_resets_to_ready(self):
        """Closet state resets to READY after trap is triggered."""
        closet = self.state.apartment.closet
        self.state.hero.ChangeRoom(closet)
        closet.state = Closet.State.NAILED
        
        self.ae.run(self.state)
        assert closet.state == Closet.State.READY

    def test_outputs_splintering_text(self):
        """Trapped AE outputs splintering wood text."""
        closet = self.state.apartment.closet
        self.state.hero.ChangeRoom(closet)
        closet.state = Closet.State.NAILED
        
        self.ae.run(self.state)
        output = "\n".join(self.mock_io.outputs)
        assert "splintering wood" in output

    def test_time_still_advances_when_trapped(self):
        """Time still advances by 6 hours when AE is trapped."""
        closet = self.state.apartment.closet
        self.state.hero.ChangeRoom(closet)
        closet.state = Closet.State.NAILED
        
        start_time = self.state.watch.curr_time
        self.ae.run(self.state)
        assert self.state.watch.curr_time == start_time + timedelta(hours=6)


class TestBarricade:
    """Tests for bedroom barricade counter-mechanic."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae

    def test_phase_does_not_advance_when_barricaded(self):
        """AE phase does not advance when bedroom is barricaded."""
        self.state.bedroom_barricaded = True
        
        self.ae.run(self.state)
        assert self.ae.current_phase == 0  # Did NOT advance

    def test_barricade_cleared(self):
        """Bedroom barricade is cleared after AE encounters it."""
        self.state.bedroom_barricaded = True
        
        self.ae.run(self.state)
        assert self.state.bedroom_barricaded is False

    def test_outputs_pounding_text(self):
        """AE outputs pounding text when clearing barricade."""
        self.state.bedroom_barricaded = True
        
        self.ae.run(self.state)
        output = "\n".join(self.mock_io.outputs)
        assert "heavy pounding" in output

    def test_time_still_advances_when_barricaded(self):
        """Time still advances by 6 hours when AE clears barricade."""
        self.state.bedroom_barricaded = True
        
        start_time = self.state.watch.curr_time
        self.ae.run(self.state)
        assert self.state.watch.curr_time == start_time + timedelta(hours=6)


class TestItemSearch:
    """Tests for _find_item_in_apartment helper."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.ae = AlterEgo()

    def test_finds_item_in_toolbox(self):
        """AE finds items in the toolbox."""
        Object("copper-wire", self.state.apartment.main.toolbox)
        result = self.ae._find_item_in_apartment(self.state, "copper-wire")
        assert result is not None
        assert result.name == "copper-wire"

    def test_finds_item_in_fridge(self):
        """AE finds items in the fridge."""
        Object("ice-cubes", self.state.apartment.main.fridge)
        result = self.ae._find_item_in_apartment(self.state, "ice-cubes")
        assert result is not None

    def test_finds_item_on_table(self):
        """AE finds items on the table."""
        Object("plywood-sheet", self.state.apartment.main.table)
        result = self.ae._find_item_in_apartment(self.state, "plywood-sheet")
        assert result is not None

    def test_finds_item_in_hero_inventory(self):
        """AE finds items in hero's inventory."""
        item = Object("hammer", None)
        item.parent = self.state.hero
        self.state.hero.contents.append(item)
        result = self.ae._find_item_in_apartment(self.state, "hammer")
        assert result is not None

    def test_finds_items_across_multiple_containers(self):
        """AE finds items spread across different containers."""
        Object("hammer", self.state.apartment.main.toolbox)
        Object("plywood-sheet", self.state.apartment.main.table)
        
        hammer = self.ae._find_item_in_apartment(self.state, "hammer")
        plywood = self.ae._find_item_in_apartment(self.state, "plywood-sheet")
        assert hammer is not None
        assert plywood is not None

    def test_returns_none_for_nonexistent_item(self):
        """AE returns None when item doesn't exist."""
        result = self.ae._find_item_in_apartment(self.state, "nonexistent-item")
        assert result is None

    def test_finds_item_in_bedroom(self):
        """AE finds items placed in the bedroom."""
        Object("device-frame", self.state.apartment.bedroom)
        result = self.ae._find_item_in_apartment(self.state, "device-frame")
        assert result is not None


class TestConsumeItem:
    """Tests for _consume_item helper."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.ae = AlterEgo()

    def test_removes_item_from_container(self):
        """Consuming an item removes it from its parent container."""
        toolbox = self.state.apartment.main.toolbox
        item = Object("copper-wire", toolbox)
        
        self.ae._consume_item(item)
        assert item not in toolbox.contents
        assert item.parent is None

    def test_handles_item_with_no_parent(self):
        """Consuming an item with no parent doesn't crash."""
        item = Object("test", None)
        self.ae._consume_item(item)  # Should not raise


class TestCannotOrderWithoutFunds:
    """Tests for affordability checks."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae

    def test_ae_cannot_order_without_sufficient_funds(self):
        """AE cannot order items when hero has insufficient funds."""
        self.state.hero.curr_balance = 0
        self.ae.run(self.state)
        assert len(self.ae.orders_placed) == 0
        assert self.state.hero.curr_balance == 0


class TestEvidenceText:
    """Tests for phase-specific evidence text in IntroPrompt."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_no_evidence_at_phase_0(self):
        """No evidence text when AE hasn't run."""
        self.state.IntroPrompt()
        output = "\n".join(self.mock_io.outputs)
        assert "phone" not in output.lower() or "sitting off the hook" not in output
        assert "sawdust" not in output.lower()

    def test_evidence_after_phase_1(self):
        """Evidence text after Phase 1 mentions phone off hook."""
        self.state.device_state.ae_phase = 1
        self.state.IntroPrompt()
        output = "\n".join(self.mock_io.outputs)
        assert "phone is sitting off the hook" in output

    def test_evidence_after_phase_2(self):
        """Evidence text after Phase 2 mentions sawdust."""
        self.state.device_state.ae_phase = 2
        self.state.IntroPrompt()
        output = "\n".join(self.mock_io.outputs)
        assert "Sawdust" in output

    def test_evidence_after_phase_3(self):
        """Evidence text after Phase 3 mentions solder burns."""
        self.state.device_state.ae_phase = 3
        self.state.IntroPrompt()
        output = "\n".join(self.mock_io.outputs)
        assert "Solder burns" in output

    def test_evidence_after_phase_4(self):
        """Evidence text after Phase 4 mentions lights flicker."""
        self.state.device_state.ae_phase = 4
        self.state.IntroPrompt()
        output = "\n".join(self.mock_io.outputs)
        assert "lights flicker" in output

    def test_evidence_after_phase_5_failed(self):
        """Evidence text after Phase 5 (incomplete device) mentions sparks."""
        self.state.device_state.ae_phase = 5
        self.state.device_activated = False
        self.state.IntroPrompt()
        output = "\n".join(self.mock_io.outputs)
        assert "sparks and whines" in output


class TestFullLifecycle:
    """Integration tests for the full 5-phase AE lifecycle."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        queue = EventQueue(self.state)
        self.state.SetEventQueue(queue)
        self.ae = AlterEgo()
        self.state.alter_ego = self.ae
        self.state.hero.curr_balance = 1000  # Plenty of money

    def _fire_deliveries(self):
        """Advance time enough to fire all pending deliveries."""
        # Move time forward 4 days to trigger all deliveries
        self.state.watch.curr_time += timedelta(days=4)
        self.state.event_queue.Examine()

    def test_full_lifecycle_with_all_materials(self):
        """Full 5-phase lifecycle with all materials available completes device."""
        # Phase 1: Surveying (orders materials)
        self.ae.run(self.state)
        assert self.ae.current_phase == 1
        
        # Fire deliveries from phase 1
        self._fire_deliveries()
        
        # Place extra materials needed for phase 2 (plywood, nails, hammer)
        toolbox = self.state.apartment.main.toolbox
        Object("plywood-sheet", toolbox)
        Object("box-of-nails", toolbox)
        Object("hammer", toolbox)
        
        # Phase 2: Frame construction
        self.ae.run(self.state)
        assert self.ae.current_phase == 2
        assert self.state.device_state.is_component_built("device-frame")
        
        # Fire deliveries from phase 2 orders
        self._fire_deliveries()
        
        # Phase 3: Wiring
        self.ae.run(self.state)
        assert self.ae.current_phase == 3
        assert self.state.device_state.is_component_built("wiring-harness")
        
        # Fire deliveries from phase 3 orders
        self._fire_deliveries()
        
        # Phase 4: Power Core + Focusing Array
        self.ae.run(self.state)
        assert self.ae.current_phase == 4
        assert self.state.device_state.is_component_built("power-core")
        assert self.state.device_state.is_component_built("focusing-array")
        
        # Phase 5: Activation
        self.ae.run(self.state)
        assert self.ae.current_phase == 5
        assert self.state.device_state.is_component_built("convergence-device")
        assert self.state.device_activated is True

    def test_lifecycle_with_resource_denial_at_phase_3(self):
        """AE advances phases but can't build without materials."""
        # Drain all funds after phase 1
        self.ae.run(self.state)  # Phase 1
        self.state.hero.curr_balance = 0
        
        # Don't fire deliveries, so no materials available
        self.ae.run(self.state)  # Phase 2 - no frame materials
        assert not self.state.device_state.is_component_built("device-frame")
        
        self.ae.run(self.state)  # Phase 3 - wiring impossible
        assert not self.state.device_state.is_component_built("wiring-harness")
        
        self.ae.run(self.state)  # Phase 4 - no materials
        assert not self.state.device_state.is_component_built("power-core")
        
        self.ae.run(self.state)  # Phase 5 - can't activate
        assert self.state.device_activated is False

    def test_closet_trap_delays_progression(self):
        """Closet trap delays AE progression by one turn."""
        # Trap in closet for first run
        closet = self.state.apartment.closet
        self.state.hero.ChangeRoom(closet)
        closet.state = Closet.State.NAILED
        
        self.ae.run(self.state)  # Trapped - phase stays 0
        assert self.ae.current_phase == 0
        
        # Now hero is free (closet reset to READY)
        # Move hero out of closet for next run
        self.state.hero.ChangeRoom(self.state.apartment.main)
        self.ae.run(self.state)  # Now phase 1 runs
        assert self.ae.current_phase == 1

    def test_barricade_delays_progression(self):
        """Barricade delays AE progression by one turn."""
        self.state.bedroom_barricaded = True
        
        self.ae.run(self.state)  # Barricade cleared - phase stays 0
        assert self.ae.current_phase == 0
        assert not self.state.bedroom_barricaded
        
        self.ae.run(self.state)  # Now phase 1 runs
        assert self.ae.current_phase == 1


class TestSuperDay6Response:
    """Tests for SuperNumber Day 6+ conditional response."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_super_day6_no_power_core(self):
        """Day 6+ without power-core shows default calmed down message."""
        # Advance to Day 6
        self.state.watch.curr_time += timedelta(days=5)
        
        phone = self.state.apartment.main.phone
        super_number = phone.phone_numbers[3]  # SuperNumber
        super_number.Interact()
        
        output = "\n".join(self.mock_io.outputs)
        assert "calmed down" in output

    def test_super_day6_with_power_core(self):
        """Day 6+ with power-core shows power surge message."""
        # Advance to Day 6
        self.state.watch.curr_time += timedelta(days=5)
        # Build the power-core
        self.state.device_state.build_component("power-core")
        
        phone = self.state.apartment.main.phone
        super_number = phone.phone_numbers[3]  # SuperNumber
        super_number.Interact()
        
        output = "\n".join(self.mock_io.outputs)
        assert "power surges have stopped" in output

    def test_super_day4_unchanged(self):
        """Day 4 response unchanged regardless of power-core."""
        # Advance to Day 4
        self.state.watch.curr_time += timedelta(days=3)
        self.state.device_state.build_component("power-core")
        
        phone = self.state.apartment.main.phone
        super_number = phone.phone_numbers[3]  # SuperNumber
        super_number.Interact()
        
        output = "\n".join(self.mock_io.outputs)
        assert "tenants have been complaining" in output


class TestGameStatePhase4Flags:
    """Tests for new Phase 4 GameState flags."""

    def setup_method(self):
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_device_activated_defaults_false(self):
        """device_activated defaults to False."""
        assert self.state.device_activated is False

    def test_gamestate_has_new_alter_ego(self):
        """GameState creates an AlterEgo instance."""
        assert self.state.alter_ego is not None