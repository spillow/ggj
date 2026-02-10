"""
alterego.py

The Alter Ego AI system — a 5-phase construction logic that runs while
Arthur sleeps. The AE takes over the body, checks available resources,
places phone orders, picks up deliveries, consumes materials, and builds
device components toward activating the Convergence Amplifier.

Phases:
    1. Surveying — order initial materials (copper-wire, metal-brackets,
       vacuum-tubes, battery-pack)
    2. Frame — build device-frame from plywood/brackets/nails/hammer;
       order next round (soldering-iron, insulated-cable, copper-coil)
    3. Wiring — build wiring-harness from copper-wire/insulated-cable/
       soldering-iron; order next round (crystal-oscillator,
       signal-amplifier, ice-cubes)
    4. Power Core — build power-core from battery-pack/copper-coil;
       build focusing-array from crystal-oscillator/ice-cubes
    5. Activation — install convergence-device from signal-amplifier;
       if all components built, activate the device
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gamestate import GameState
    from .core.game_objects import Object, Container


class AlterEgo:
    """
    The Alter Ego — a dissociated personality that takes control of Arthur's
    body during sleep and works toward building the Convergence Amplifier.

    Attributes:
        current_phase: Current AE construction phase (0 = not started, 1-5)
        orders_placed: List of item names the AE has ordered but not yet used
    """

    def __init__(self) -> None:
        """Initialize the Alter Ego at phase 0 (not started)."""
        self.current_phase: int = 0
        self.orders_placed: list[str] = []

    def run(self, gamestate: GameState) -> None:
        """
        Main entry point — called when Arthur passes out (feel <= 0).

        Control flow:
            1. Check closet trap → if trapped, waste turn
            2. Check bedroom barricade → if barricaded, clear it, waste turn
            3. Advance phase and execute phase logic
            4. Advance time by ~6 hours (sleep duration)
        """
        # 1. Check closet trap
        if self._is_trapped_in_closet(gamestate):
            gamestate.watch.curr_time += timedelta(hours=6)
            return

        # 2. Check bedroom barricade
        if self._handle_barricade(gamestate):
            gamestate.watch.curr_time += timedelta(hours=6)
            return

        # 3. Advance phase (cap at 5)
        if self.current_phase < 5:
            self.current_phase += 1

        # Sync phase to device_state for evidence text
        gamestate.device_state.ae_phase = self.current_phase

        # 4. Execute phase logic
        match self.current_phase:
            case 1:
                self._phase_surveying(gamestate)
            case 2:
                self._phase_frame(gamestate)
            case 3:
                self._phase_wiring(gamestate)
            case 4:
                self._phase_power_core(gamestate)
            case 5:
                self._phase_activation(gamestate)

        # 5. Advance time by ~6 hours (sleep duration)
        gamestate.watch.curr_time += timedelta(hours=6)

    # ------------------------------------------------------------------ #
    #                        Phase implementations                        #
    # ------------------------------------------------------------------ #

    def _phase_surveying(self, gamestate: GameState) -> None:
        """
        Phase 1 — Surveying: Order initial construction materials.

        Orders from hardware store: copper-wire ($15), metal-brackets ($10)
        Orders from electronics store: vacuum-tubes ($20), battery-pack ($12)
        Only orders what the hero can afford.
        """
        orders = [
            ("copper-wire", 15),
            ("metal-brackets", 10),
            ("vacuum-tubes", 20),
            ("battery-pack", 12),
        ]
        for item_name, cost in orders:
            self._try_order(gamestate, item_name, cost)

    def _phase_frame(self, gamestate: GameState) -> None:
        """
        Phase 2 — Frame: Build the device frame and order more materials.

        Requires: plywood-sheet, metal-brackets, box-of-nails, hammer
        Consumes: plywood-sheet, metal-brackets, box-of-nails (hammer kept)
        Creates: device-frame Object in bedroom
        Then orders: soldering-iron ($25), insulated-cable ($8), copper-coil ($18)
        """
        from .core.game_objects import Object as GameObj

        plywood = self._find_item_in_apartment(gamestate, "plywood-sheet")
        brackets = self._find_item_in_apartment(gamestate, "metal-brackets")
        nails = self._find_item_in_apartment(gamestate, "box-of-nails")
        hammer = self._find_item_in_apartment(gamestate, "hammer")

        if plywood and brackets and nails and hammer:
            self._consume_item(plywood)
            self._consume_item(brackets)
            self._consume_item(nails)
            # Leave hammer in bedroom
            self._move_item_to(hammer, gamestate.apartment.bedroom)
            GameObj("device-frame", gamestate.apartment.bedroom)
            gamestate.device_state.build_component("device-frame")

        # Order next round of materials
        next_orders = [
            ("soldering-iron", 25),
            ("insulated-cable", 8),
            ("copper-coil", 18),
        ]
        for item_name, cost in next_orders:
            self._try_order(gamestate, item_name, cost)

    def _phase_wiring(self, gamestate: GameState) -> None:
        """
        Phase 3 — Wiring: Build the wiring harness.

        Requires: device-frame BUILT + copper-wire, insulated-cable, soldering-iron
        Consumes: copper-wire, insulated-cable (soldering-iron kept)
        Creates: wiring-harness Object in bedroom
        Then orders: crystal-oscillator ($35), signal-amplifier ($40), ice-cubes ($6)
        """
        from .core.game_objects import Object as GameObj

        if not gamestate.device_state.is_component_built("device-frame"):
            # Can't build wiring without the frame
            pass
        else:
            copper_wire = self._find_item_in_apartment(gamestate, "copper-wire")
            cable = self._find_item_in_apartment(gamestate, "insulated-cable")
            iron = self._find_item_in_apartment(gamestate, "soldering-iron")

            if copper_wire and cable and iron:
                self._consume_item(copper_wire)
                self._consume_item(cable)
                # Leave soldering-iron in bedroom
                self._move_item_to(iron, gamestate.apartment.bedroom)
                GameObj("wiring-harness", gamestate.apartment.bedroom)
                gamestate.device_state.build_component("wiring-harness")

        # Order next round of materials
        next_orders = [
            ("crystal-oscillator", 35),
            ("signal-amplifier", 40),
            ("ice-cubes", 6),
        ]
        for item_name, cost in next_orders:
            self._try_order(gamestate, item_name, cost)

    def _phase_power_core(self, gamestate: GameState) -> None:
        """
        Phase 4 — Power Core: Build power-core and focusing-array.

        Power Core: battery-pack + copper-coil → power-core
        Focusing Array: crystal-oscillator + ice-cubes → focusing-array
        No new orders.
        """
        from .core.game_objects import Object as GameObj

        # Build power-core
        battery = self._find_item_in_apartment(gamestate, "battery-pack")
        coil = self._find_item_in_apartment(gamestate, "copper-coil")

        if battery and coil:
            self._consume_item(battery)
            self._consume_item(coil)
            GameObj("power-core", gamestate.apartment.bedroom)
            gamestate.device_state.build_component("power-core")

        # Build focusing-array
        oscillator = self._find_item_in_apartment(
            gamestate, "crystal-oscillator"
        )
        ice = self._find_item_in_apartment(gamestate, "ice-cubes")

        if oscillator and ice:
            self._consume_item(oscillator)
            self._consume_item(ice)
            GameObj("focusing-array", gamestate.apartment.bedroom)
            gamestate.device_state.build_component("focusing-array")

    def _phase_activation(self, gamestate: GameState) -> None:
        """
        Phase 5 — Activation: Install convergence-device and attempt activation.

        Requires: signal-amplifier → convergence-device
        If device complete: set device_activated = True
        """
        from .core.game_objects import Object as GameObj

        amplifier = self._find_item_in_apartment(
            gamestate, "signal-amplifier"
        )
        if amplifier:
            self._consume_item(amplifier)
            GameObj("convergence-device", gamestate.apartment.bedroom)
            gamestate.device_state.build_component("convergence-device")

        # Check for full activation
        if gamestate.device_state.is_device_complete():
            gamestate.device_activated = True

    # ------------------------------------------------------------------ #
    #                     Counter-mechanic helpers                        #
    # ------------------------------------------------------------------ #

    def _is_trapped_in_closet(self, gamestate: GameState) -> bool:
        """
        Check if the hero is trapped in the nailed closet.

        If trapped: output splintering text, reset closet to READY.
        The AE's phase does NOT advance.

        Returns:
            True if the AE was trapped (turn wasted), False otherwise.
        """
        from .core.rooms import Closet

        closet = gamestate.apartment.closet
        hero_room = gamestate.hero.GetRoom()

        if hero_room == closet and closet.state == Closet.State.NAILED:
            gamestate.io.output(
                "You hear sounds of splintering wood and muffled cursing "
                "from the closet..."
            )
            closet.state = Closet.State.READY
            return True
        return False

    def _handle_barricade(self, gamestate: GameState) -> bool:
        """
        Check if the bedroom is barricaded.

        If barricaded: output pounding text, clear barricade flag.
        The AE's phase does NOT advance.

        Returns:
            True if the AE had to clear a barricade (turn wasted), False otherwise.
        """
        if gamestate.bedroom_barricaded:
            gamestate.io.output(
                "You hear heavy pounding and the sound of wood cracking "
                "as the barricade is torn away..."
            )
            gamestate.bedroom_barricaded = False
            return True
        return False

    # ------------------------------------------------------------------ #
    #                        Item search helpers                          #
    # ------------------------------------------------------------------ #

    def _find_item_in_apartment(
        self, gamestate: GameState, name: str
    ) -> Object | None:
        """
        Recursively search all rooms and containers in the apartment
        for a named item.

        Also checks hero's inventory.

        Args:
            gamestate: The current game state
            name: The item name to search for

        Returns:
            The Object if found, None otherwise
        """
        # Check hero inventory first
        item = gamestate.hero.GetFirstItemByName(name)
        if item:
            return item

        # Recursively search all rooms/containers in the apartment
        return self._search_container(gamestate.apartment, name)

    def _search_container(
        self, container: Container, name: str
    ) -> Object | None:
        """
        Recursively search a container and its sub-containers for an item.

        Args:
            container: The container to search
            name: The item name to find

        Returns:
            The Object if found, None otherwise
        """
        from .core.game_objects import Container as ContainerClass

        for item in container.contents:
            if item.name == name:
                return item
            # Recurse into sub-containers
            if isinstance(item, ContainerClass):
                found = self._search_container(item, name)
                if found:
                    return found
        return None

    def _consume_item(self, item: Object) -> None:
        """
        Remove an item from its parent container (simulating the AE
        picking it up and using it as construction material).

        Args:
            item: The item to consume/remove
        """
        if item.parent is not None and hasattr(item.parent, 'contents'):
            if item in item.parent.contents:
                item.parent.contents.remove(item)
        item.parent = None

    def _move_item_to(self, item: Object, target: Container) -> None:
        """
        Move an item from its current location to a target container.

        Args:
            item: The item to move
            target: The destination container
        """
        # Remove from current parent
        if item.parent is not None and hasattr(item.parent, 'contents'):
            if item in item.parent.contents:
                item.parent.contents.remove(item)
        # Add to target
        item.parent = target
        target.contents.append(item)

    def _try_order(
        self, gamestate: GameState, item_name: str, cost: int
    ) -> bool:
        """
        Attempt to order an item if the hero can afford it.

        Deducts cost from hero's balance and schedules a delivery event
        via the event queue (delivers to toolbox in 1 day).

        Args:
            gamestate: The current game state
            item_name: Name of the item to order
            cost: Cost in dollars

        Returns:
            True if the order was placed, False otherwise
        """
        if gamestate.hero.curr_balance < cost:
            return False

        gamestate.hero.curr_balance -= cost
        self.orders_placed.append(item_name)

        # Schedule delivery to toolbox in 1 day
        from .core.game_objects import Object as GameObj
        from datetime import datetime

        delivery_time = gamestate.watch.curr_time + timedelta(days=1)

        def deliver(_curr_time: datetime, _event_time: datetime) -> None:
            GameObj(item_name, gamestate.apartment.main.toolbox)

        if gamestate.event_queue is not None:
            gamestate.event_queue.AddEvent(deliver, delivery_time)

        return True
