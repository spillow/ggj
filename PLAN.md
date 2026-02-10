# Plan: Create PLAN.md — Implementation Roadmap

## Context

The game has solid mechanics but the story (STORY.md) is unimplemented. The AlterEgo is an empty placeholder. We need to build: expanded stores/items (~3x inventory), a new electronics surplus store, new room objects, a day-tracking system, evolving TV/super, a device component system, sabotage commands, a full 5-phase Alter Ego AI, 4 game endings, and a dream confrontation sequence. PLAN.md will break this into 5 self-contained phases with TODOs, testing plans, and exit criteria for junior engineers.

## Deliverable

A single file: `PLAN.md` at the project root. Content follows below — this IS the PLAN.md content.

---

# Leggo My Ego — Implementation Plan

## Overview

5 phases to complete the game. Phases 1 and 2 are parallelizable. Phase 3 requires Phase 1. Phase 4 requires 1+2+3. Phase 5 requires 4.

```
Phase 1 (Items/Stores)  ──┐
                           ├──> Phase 3 (Device/Sabotage) ──> Phase 4 (AE AI) ──> Phase 5 (Endings)
Phase 2 (Day/World)    ──┘
```

| Phase | Summary | New Unit Tests | New E2E Tests | Depends On |
|-------|---------|---------------|---------------|------------|
| 1 | Expanded inventory, new store, new room objects | 20+ | 4+ | None |
| 2 | Day tracking, evolving TV, evolving super | 15+ | 3+ | None |
| 3 | Device system, sabotage & investigation commands | 25+ | 3+ | Phase 1 |
| 4 | Alter Ego 5-phase AI, evidence, counter-mechanics | 30+ | 3+ | Phases 1,2,3 |
| 5 | 4 endings, dream confrontation, game over logic | 20+ | 3+ | Phase 4 |

---

## Phase 1: Expanded Inventory and New Store

### Goal

Triple the game's item count by expanding the grocery and hardware stores, adding a new Electronics Surplus Store, and adding new interactive objects to the bedroom and bathroom. Purely additive — no existing behavior changes.

### Dependencies

None. Can be developed in parallel with Phase 2.

### TODO

- [x] **1.1** Add 4 new grocery items to `GroceryNumber` in `src/core/items.py`
  - `GetStoreItems()` additions: `"energy-drinks": 8`, `"canned-soup": 4`, `"chocolate-bar": 3`, `"protein-bar": 6`
  - `FoodFeel()` additions: `"energy-drinks": 25`, `"canned-soup": 10`, `"chocolate-bar": 8`, `"protein-bar": 15`
  - No other method changes needed — delivery and feel mechanics work generically

- [x] **1.2** Add 5 new hardware items to `HardwareNumber` in `src/core/items.py`
  - `GetStoreItems()` additions: `"copper-wire": 15`, `"metal-brackets": 10`, `"soldering-iron": 25`, `"duct-tape": 3`, `"wire-cutters": 12`
  - `ScheduleOrder()`: all new items follow the existing non-plywood path (delivered to `toolbox` — see line 247)

- [x] **1.3** Create `ElectronicsNumber(StoreNumber)` class in `src/core/items.py`
  - Follow the `HardwareNumber` pattern (line 200)
  - `GetStoreItems()`: `{"vacuum-tubes": 20, "crystal-oscillator": 35, "copper-coil": 18, "battery-pack": 12, "signal-amplifier": 40, "insulated-cable": 8}`
  - `Greeting()`: `"Electronics Surplus. What do you need?"`
  - `TimeWaste()`: advance time 5 minutes
  - `FeelChange()`: decrease feel by 5
  - `ScheduleOrder()`: deliver in 3 days to `toolbox`; message: `"We'll ship that out. Should arrive in about 3 days."`

- [x] **1.4** Register new store in `Phone.__init__()` in `src/core/items.py` (line 318)
  - Add `ElectronicsNumber("Electronics Surplus", "743-8291", gamestate)` to `self.phone_numbers`

- [x] **1.5** Create `Bedroom(Room)` class in `src/core/rooms.py`
  - Follow the `MainRoom` pattern (line 53)
  - Constructor creates `self.bookshelf = Container("bookshelf", self)`
  - Creates a `Journal` inside the bookshelf (see 1.7)

- [x] **1.6** Create `Bathroom(Room)` class in `src/core/rooms.py`
  - Constructor creates `self.medicine_cabinet = Openable("medicine-cabinet", self)`
  - Creates `self.mirror = Mirror(self)` (see 1.8)
  - Optionally: `Object("aspirin", self.medicine_cabinet)`

- [x] **1.7** Create `Journal` class in `src/core/items.py`
  - Extends `Object`, weight = 1 (pickable)
  - `@sameroom` decorated `Examine()` outputs placeholder text: `"A worn leather journal. The pages are filled with your handwriting, though you don't remember writing most of it."`
  - Phase 5 will add the full backstory text

- [x] **1.8** Create `Mirror` class in `src/core/items.py`
  - Extends `Object`, weight = 1000 (not pickable)
  - `@sameroom` decorated `Examine()` outputs: `"You look in the mirror. You see yourself. You look tired."`
  - Phase 2 will add day-based AE flicker; Phase 3 will add `mirror_seen` flag

- [x] **1.9** Update `Apartment.__init__()` in `src/core/rooms.py` (line 136)
  - Change `self.bedroom = Room("bedroom", self)` → `self.bedroom = Bedroom("bedroom", self, gamestate)`
  - Change `self.bathroom = Room("bathroom", self)` → `self.bathroom = Bathroom("bathroom", self)`
  - Update type annotations: `bedroom: Bedroom`, `bathroom: Bathroom`

- [x] **1.10** Update legacy exports in `src/gamestate.py` `__all__` if new classes need to be importable externally

- [x] **1.11** Update `debug_items` in `src/game_actions/utility_actions.py` to also give wire-cutters (for testing sabotage commands in Phase 3)

### Files Modified

| File | Changes |
|------|---------|
| `src/core/items.py` | Add items to GroceryNumber/HardwareNumber, create ElectronicsNumber, create Journal, create Mirror, register in Phone |
| `src/core/rooms.py` | Create Bedroom class, create Bathroom class, update Apartment.__init__() |
| `src/game_actions/utility_actions.py` | Update debug_items to include wire-cutters |
| `src/gamestate.py` | Update __all__ exports |

### Files Created

| File | Purpose |
|------|---------|
| `tests/test_expanded_inventory.py` | Unit tests for new store items and expanded stores |
| `tests/test_room_objects.py` | Unit tests for bookshelf, journal, mirror, medicine-cabinet |
| `tools/test_grocery_expanded.txt` | E2E: order new grocery item, verify delivery |
| `tools/test_hardware_expanded.txt` | E2E: order new hardware item, verify delivery |
| `tools/test_electronics_store.txt` | E2E: call 743-8291, browse menu, order item |
| `tools/test_new_room_objects.txt` | E2E: visit bedroom/bathroom, interact with new objects |

### Testing Plan

**Unit tests** (20+ minimum in `test_expanded_inventory.py` and `test_room_objects.py`):
- GroceryNumber.GetStoreItems() returns 8 items with correct prices
- GroceryNumber.FoodFeel() returns 8 items with correct boosts
- HardwareNumber.GetStoreItems() returns 8 items with correct prices
- ElectronicsNumber.GetStoreItems() returns 6 items with correct prices
- ElectronicsNumber.Greeting() outputs correct text
- ElectronicsNumber.ScheduleOrder() schedules 3-day delivery
- ElectronicsNumber.TimeWaste() advances time 5 minutes
- ElectronicsNumber.FeelChange() decreases feel by 5
- Phone has 4 phone numbers
- Ordering from electronics deducts correct balance
- Electronics delivery arrives at toolbox after 3 days
- Bedroom has bookshelf attribute
- Bookshelf contains journal
- Journal is examinable (outputs text)
- Journal is pickable (weight <= 100)
- Bathroom has medicine_cabinet attribute
- Bathroom has mirror attribute
- Medicine-cabinet starts closed
- Mirror is examinable
- Mirror cannot be picked up

**E2E tests** (4+ files): grocery expanded, hardware expanded, electronics store, new room objects

### Exit Criteria

- [x] All 192 existing tests pass (zero regressions)
- [x] All 44 new unit tests pass (22 inventory + 22 room objects)
- [x] All 4 new e2e tests pass (grocery, hardware, electronics, room objects)
- [x] `rolodex` shows 4 phone numbers including `Electronics Surplus: 743-8291`
- [x] All 8 grocery items, 8 hardware items, 6 electronics items visible in store menus
- [x] Bedroom has bookshelf containing journal; bathroom has medicine-cabinet and mirror
- [x] Combined test coverage ≥ 80% (91% on actively-used modules)

---

## Phase 2: Day Tracking and Evolving World

### Goal

Add a day-computation system, make TV news change daily (7 broadcasts matching STORY.md), and make the building super answer the phone starting Day 4. These create the narrative timeline and urgency.

### Dependencies

None. Can be developed in parallel with Phase 1.

### TODO

- [ ] **2.1** Add `get_current_day() -> int` method to `GameState` in `src/core/game_world.py`
  - `Day 1 = March 15, 1982`, `Day 7 = March 21, 1982`
  - Formula: `(self.watch.curr_time.date() - date(1982, 3, 15)).days + 1`
  - Days > 7 return actual day number (no cap)

- [ ] **2.2** Define `TV_NEWS` dictionary as module-level constant in `src/core/items.py`
  - 7 entries keyed by day number, values are the broadcast strings from STORY.md
  - Default for days > 7: use the Day 7 message

- [ ] **2.3** Modify `TV.__init__()` to accept `gamestate` parameter in `src/core/items.py` (line 274)
  - Store `self.gamestate = gamestate`
  - Update `MainRoom.__init__()` (line 78): change `TV(self)` to `TV(self, gamestate)`

- [ ] **2.4** Modify `TV.Examine()` to use day-based news in `src/core/items.py`
  - Look up `self.gamestate.get_current_day()` and display corresponding `TV_NEWS` entry
  - Keep the `"You turn on the tv."` preamble
  - **Important**: Day 1 message must match the existing text exactly so `tools/test_tv_news.txt` doesn't break

- [ ] **2.5** Define `SUPER_RESPONSES` dictionary in `src/core/items.py`
  - Day 4: `"Yeah? Oh, you. Listen, other tenants have been complaining about noises from your apartment at night. Banging, drilling sounds. And the electrical -- the whole building's been having power surges. You know anything about that?"`
  - Day 5: `"Look, whatever you're doing up there, the power company is threatening to cut the whole building's service. I've got half a mind to come up there myself."`
  - Day 6+: `"Things seem to have calmed down. Try to keep it that way."` (default; Phase 4 can add device-conditional text later)

- [ ] **2.6** Modify `SuperNumber.Interact()` in `src/core/items.py` (line 259)
  - Days 1-3: keep existing behavior (ring 3 times, no answer, -30 feel, +20 min)
  - Day 4+: super answers with day-specific response, still apply feel/time penalties (reduced: -10 feel, +5 min since they actually picked up)

### Files Modified

| File | Changes |
|------|---------|
| `src/core/game_world.py` | Add `get_current_day()` method |
| `src/core/items.py` | Add TV_NEWS dict, modify TV class (constructor + Examine), add SUPER_RESPONSES dict, modify SuperNumber.Interact() |
| `src/core/rooms.py` | Update MainRoom.__init__() to pass gamestate to TV |

### Files Created

| File | Purpose |
|------|---------|
| `tests/test_day_tracking.py` | Unit tests for day computation |
| `tests/test_evolving_world.py` | Unit tests for TV news and super responses per day |
| `tools/test_tv_day1.txt` | E2E: watch TV on Day 1 |
| `tools/test_super_day4.txt` | E2E: advance to Day 4, call super, verify response |

### Testing Plan

**Unit tests** (15+ minimum):
- `get_current_day()` returns 1 at game start
- `get_current_day()` returns 2 on March 16
- `get_current_day()` returns 7 on March 21
- `get_current_day()` returns 1 at 11:59 PM March 15
- `get_current_day()` returns 8 on March 22 (no cap)
- TV Day 1 message matches original text (backward compat)
- TV Day 2-7 messages each display correct text
- TV Day 8+ defaults to Day 7 message
- Super Days 1-3: no answer (existing behavior)
- Super Day 4: answers with complaint text
- Super Day 5: answers with threat text
- Super Day 6+: answers with default text
- Super Day 4+ still applies feel/time penalties
- Day computation handles time zones correctly (just date comparison)

**E2E tests** (3+ files): Day 1 TV, Day 4 super, day tracking via ponder+watch

### Exit Criteria

- [ ] All existing tests pass (zero regressions) — particularly `tools/test_tv_news.txt`
- [ ] All 15+ new unit tests pass
- [ ] All 3+ new e2e tests pass
- [ ] `get_current_day()` correctly returns 1-7+ from watch time
- [ ] TV shows 7 distinct day-appropriate broadcasts
- [ ] Super has 3 response patterns (Days 1-3, Day 4, Day 5+)
- [ ] Combined test coverage ≥ 80%

---

## Phase 3: Device System and Sabotage Commands

### Goal

Implement the Convergence Amplifier tracking system, the physical device-component objects that appear in the bedroom, and 6 new player commands for sabotaging the device and investigating the story. This provides the "battlefield" that the AE and player contest over.

### Dependencies

**Phase 1 must be complete** (Bedroom class, wire-cutters in hardware store, Journal and Mirror objects).

Phase 2 is optional — the mirror's day-based flicker can use `gamestate.get_current_day()` if available, or defer to Phase 4 integration.

### TODO

- [ ] **3.1** Create `src/core/device_state.py` with `DeviceState` class
  ```
  COMPONENTS = ["device-frame", "wiring-harness", "power-core", "focusing-array", "convergence-device"]
  ```
  Methods: `build_component(name)`, `remove_component(name)`, `is_component_built(name)`, `count_built_components()`, `count_missing_components()`, `is_device_complete()`, `get_built_components()`, `get_missing_components()`
  - Also track `ae_phase: int` (0 = not started, 1-5 = current phase)

- [ ] **3.2** Add `DeviceState` to `GameState` in `src/core/game_world.py`
  - `self.device_state = DeviceState()` in `__init__()`
  - `self.journal_read: bool = False` — set when player reads the journal
  - `self.mirror_seen: bool = False` — set when player sees AE flicker
  - `self.bedroom_barricaded: bool = False` — set by barricade command

- [ ] **3.3** Add `barricaded: bool = False` to `Bedroom` class in `src/core/rooms.py`

- [ ] **3.4** Create `DisassembleFrameCommand` in `src/commands/game_commands.py`
  - Requires: hero in bedroom + hammer in inventory + `device_state.is_component_built("device-frame")`
  - Execute: set component to MISSING, remove `device-frame` Object from bedroom, output sabotage text
  - Time: +1 hour, Feel: -15

- [ ] **3.5** Create `CutWiresCommand` in `src/commands/game_commands.py`
  - Requires: hero in bedroom + wire-cutters in inventory + `device_state.is_component_built("wiring-harness")`
  - Execute: set component to MISSING, remove Object, output sabotage text
  - Time: +30 min, Feel: -10

- [ ] **3.6** Create `RemoveBatteryCommand` in `src/commands/game_commands.py`
  - Requires: hero in bedroom + `device_state.is_component_built("power-core")`
  - Execute: set component to MISSING, remove Object, output text
  - Time: +20 min, Feel: -5

- [ ] **3.7** Create `RemoveCrystalCommand` in `src/commands/game_commands.py`
  - Requires: hero in bedroom + `device_state.is_component_built("focusing-array")`
  - Execute: set component to MISSING, remove Object, output text
  - Time: +20 min, Feel: -5

- [ ] **3.8** Create `BarricadeBedroomCommand` in `src/commands/game_commands.py`
  - Requires: hero NOT in bedroom + plywood + nails + hammer in inventory
  - Execute: consume plywood and nails, set `bedroom_barricaded = True`, output text
  - Time: +1 hour, Feel: -15

- [ ] **3.9** Create `ReadJournalCommand` in `src/commands/game_commands.py`
  - Requires: journal in hero inventory OR same room
  - Execute: output journal text, set `gamestate.journal_read = True`
  - No time/feel cost

- [ ] **3.10** Update `Mirror.Examine()` in `src/core/items.py`
  - If `gamestate.get_current_day() >= 4` (requires Phase 2, add TODO if unavailable): show AE flicker text, set `gamestate.mirror_seen = True`
  - Pass gamestate to Mirror via constructor: `Mirror(parent, gamestate)`

- [ ] **3.11** Create factory functions and register all 6 commands in `src/inputparser.py`
  ```
  "disassemble frame": create_disassemble_frame_command,
  "cut wires": create_cut_wires_command,
  "remove battery": create_remove_battery_command,
  "remove crystal": create_remove_crystal_command,
  "barricade bedroom": create_barricade_bedroom_command,
  "read journal": create_read_journal_command,
  ```

### Files Modified

| File | Changes |
|------|---------|
| `src/core/game_world.py` | Add DeviceState, journal_read, mirror_seen, bedroom_barricaded flags |
| `src/core/rooms.py` | Add barricaded attr to Bedroom |
| `src/core/items.py` | Update Mirror.Examine() with day-based flicker and gamestate ref |
| `src/commands/game_commands.py` | 6 new command classes |
| `src/inputparser.py` | 6 new command registrations + factory functions |

### Files Created

| File | Purpose |
|------|---------|
| `src/core/device_state.py` | DeviceState class tracking 5 components |
| `tests/test_device_system.py` | Unit tests for DeviceState |
| `tests/test_sabotage_commands.py` | Unit tests for 6 new commands |
| `tools/test_read_journal.txt` | E2E: find and read the journal |
| `tools/test_barricade_bedroom.txt` | E2E: get materials, barricade bedroom |
| `tools/test_sabotage_device.txt` | E2E: simulate device components present, disassemble them |

### Testing Plan

**Unit tests** (25+ minimum):
- DeviceState initializes all 5 components as MISSING
- build_component() sets to BUILT
- remove_component() sets to MISSING
- is_component_built() returns correct status
- count_built/missing returns correct counts
- is_device_complete() true when all BUILT, false otherwise
- DisassembleFrameCommand: fails without hammer, fails outside bedroom, fails when not built, succeeds correctly
- CutWiresCommand: fails without wire-cutters, succeeds correctly
- RemoveBatteryCommand: fails when not built, succeeds correctly
- RemoveCrystalCommand: fails when not built, succeeds correctly
- BarricadeBedroomCommand: fails when inside bedroom, fails without materials, succeeds and consumes plywood+nails, sets flag
- ReadJournalCommand: fails when journal inaccessible, succeeds and sets journal_read flag

**E2E tests** (3+ files): read journal, barricade bedroom, device sabotage

### Exit Criteria

- [ ] All existing tests pass (zero regressions)
- [ ] All 25+ new unit tests pass
- [ ] All 3+ new e2e tests pass
- [ ] DeviceState tracks all 5 components correctly
- [ ] All 6 new commands parse and execute with proper validation
- [ ] Barricade consumes plywood + nails
- [ ] ReadJournalCommand sets `journal_read` flag
- [ ] Combined test coverage ≥ 80%

---

## Phase 4: Alter Ego AI

### Goal

Implement the full 5-phase Alter Ego construction logic. When Arthur sleeps, the AE takes over: it checks available resources, places phone orders, picks up deliveries, consumes materials, and builds device components. Also implement the closet-trap and barricade counter-mechanics, and the evidence system that changes wake-up text based on the AE's progress.

### Dependencies

**Phases 1, 2, and 3 must all be complete.**

### TODO

- [ ] **4.1** Rewrite `AlterEgo` class in `src/alterego.py` with state tracking:
  - `current_phase: int = 0` (0 = not started, 1-5)
  - `orders_placed: list[str]` — tracks pending orders
  - `run(gamestate)` — main entry point, called during sleep

- [ ] **4.2** Implement `run()` control flow:
  ```
  1. Check closet trap → if trapped, waste turn, reset closet, return
  2. Check bedroom barricade → if barricaded, clear it, waste turn, return
  3. Advance current_phase by 1
  4. Execute phase logic (match/case on current_phase)
  5. Advance time by ~6 hours (sleep duration)
  ```

- [ ] **4.3** Implement `_phase_surveying()` (Phase 1):
  - Check hero.curr_balance for each order
  - Order from hardware: copper-wire ($15), metal-brackets ($10) if affordable
  - Order from electronics: vacuum-tubes ($20), battery-pack ($12) if affordable
  - Deduct costs from hero.curr_balance
  - Schedule deliveries via event_queue.AddEvent()

- [ ] **4.4** Implement `_phase_frame()` (Phase 2):
  - Search apartment for: plywood-sheet, metal-brackets, box-of-nails, hammer
  - If all found: consume plywood/brackets/nails, create `Object("device-frame", bedroom)`, set `device_state.build_component("device-frame")`, leave hammer in bedroom
  - If not all found: skip building (phase still advances)
  - Order: soldering-iron ($25), insulated-cable ($8), copper-coil ($18) if affordable

- [ ] **4.5** Implement `_phase_wiring()` (Phase 3):
  - Search for: copper-wire, insulated-cable, soldering-iron
  - If frame exists AND materials found: build wiring-harness, consume copper-wire + insulated-cable
  - Order: crystal-oscillator ($35), signal-amplifier ($40), ice-cubes ($6) if affordable

- [ ] **4.6** Implement `_phase_power_core()` (Phase 4):
  - Search for: battery-pack, copper-coil → build power-core if found
  - Search for: crystal-oscillator, ice-cubes → build focusing-array if found
  - No new orders

- [ ] **4.7** Implement `_phase_activation()` (Phase 5):
  - Search for: signal-amplifier → install as convergence-device
  - Check `device_state.is_device_complete()`
  - If complete: set `gamestate.device_activated = True`
  - If incomplete: output evidence of failed activation

- [ ] **4.8** Implement `_is_trapped_in_closet()` helper:
  - Check: hero is in closet AND closet.state == NAILED
  - If trapped: output "You hear sounds of splintering wood...", reset closet.state to READY
  - AE's phase does NOT advance

- [ ] **4.9** Implement `_handle_barricade()` helper:
  - Check: `gamestate.bedroom_barricaded == True`
  - If barricaded: output "You hear heavy pounding...", set barricaded to False
  - AE's phase does NOT advance

- [ ] **4.10** Implement `_find_item_in_apartment()` helper:
  - Recursively search all rooms and containers for a named item
  - Return the Object if found, None otherwise
  - The AE uses this to locate delivered materials anywhere in the apartment

- [ ] **4.11** Implement `_consume_item()` helper:
  - Remove an item from its parent container (simulating AE picking it up and using it)

- [ ] **4.12** Add `device_activated: bool = False` flag to `GameState` in `src/core/game_world.py`

- [ ] **4.13** Update `GameState.IntroPrompt()` in `src/core/game_world.py` to display phase-specific evidence text:
  - After Phase 1: `"Something feels... off. The phone is sitting off the hook."`
  - After Phase 2: `"There's a strange smell. Sawdust?"`
  - After Phase 3: `"Your fingertips are blackened. Solder burns?"`
  - After Phase 4: `"The lights flicker as you open your eyes."`
  - After Phase 5 (failed): `"The device sparks and whines, then falls silent. Something is missing."`

- [ ] **4.14** Update `SuperNumber.Interact()` Day 6+ response in `src/core/items.py`:
  - If device has power-core: `"The power surges have stopped, at least. But if I hear one more complaint, I'm calling the city."`
  - If not: `"Things seem to have calmed down. Try to keep it that way."`

### Files Modified

| File | Changes |
|------|---------|
| `src/alterego.py` | Complete rewrite: 5-phase AI + helpers |
| `src/core/game_world.py` | Add device_activated flag, update IntroPrompt() with evidence text |
| `src/core/items.py` | Update SuperNumber Day 6+ conditional response |

### Files Created

| File | Purpose |
|------|---------|
| `tests/test_alterego.py` | Rewrite existing placeholder: 30+ comprehensive AE tests |
| `tools/test_ae_phase1.txt` | E2E: let feel drop to 0, verify AE Phase 1 evidence |
| `tools/test_ae_closet_trap.txt` | E2E: nail in closet, sleep, verify AE wasted turn |
| `tools/test_ae_resource_denial.txt` | E2E: spend all money, sleep, verify AE couldn't order |

### Testing Plan

**Unit tests** (30+ minimum, replacing `tests/test_alterego.py`):
- AE starts at phase 0
- AE advances to phase 1 on first run()
- Phase 1: places correct orders if money available
- Phase 1: deducts money correctly
- Phase 1: skips orders if insufficient funds
- Phase 2: builds frame when all materials available
- Phase 2: consumes plywood/brackets/nails but not hammer
- Phase 2: creates device-frame Object in bedroom
- Phase 2: skips building when materials missing
- Phase 2: updates device_state correctly
- Phase 3: builds wiring-harness when materials available
- Phase 3: skips when materials missing
- Phase 4: builds power-core when battery+coil available
- Phase 4: builds focusing-array when oscillator+ice available
- Phase 4: builds neither when materials missing
- Phase 5: sets device_activated when device complete
- Phase 5: does NOT set flag when device incomplete
- Closet trap: AE phase does not advance
- Closet trap: closet state resets to READY
- Barricade: AE phase does not advance
- Barricade: bedroom_barricaded resets to False
- AE finds items in toolbox, fridge, table, hero inventory
- AE finds items across multiple containers
- AE cannot order without sufficient funds
- Evidence text after Phase 1 includes phone off hook
- Evidence text after Phase 2 includes sawdust
- Evidence text after Phase 4 includes lights flicker
- Full 5-phase lifecycle with all materials available
- Full 5-phase lifecycle with resource denial at phase 3
- AE does not advance past phase 5

**E2E tests** (3+ files): AE Phase 1 evidence, closet trap, resource denial

### Exit Criteria

- [ ] All existing tests pass (zero regressions)
- [ ] All 30+ new unit tests pass
- [ ] All 3+ new e2e tests pass
- [ ] AE correctly advances through 5 phases
- [ ] AE orders materials, checks affordability, builds components when materials present
- [ ] AE skips building when materials are absent (graceful degradation)
- [ ] Closet trap wastes AE turn and resets closet
- [ ] Barricade wastes AE turn and clears flag
- [ ] Evidence text changes appropriately after each phase
- [ ] `device_activated` set only when all 5 components are BUILT
- [ ] Combined test coverage ≥ 80%

---

## Phase 5: Game Endings and Secret Story

### Goal

Implement all 4 game endings (Victory, Partial Victory, Defeat, Secret), the win/lose condition checks that trigger when Day 7 arrives or the device activates, the dream confrontation interactive sequence, and the `let go`/`hold on` commands. Finalize the journal text with the full STORY.md backstory. This is the narrative capstone.

### Dependencies

**Phase 4 must be complete.**

### TODO

- [ ] **5.1** Create `src/endings.py` module with `GameEndings` class:
  - `check_ending(gamestate) -> str | None` — returns `"victory"`, `"partial_victory"`, `"defeat"`, or None
    - If `device_activated`: return `"defeat"`
    - If day >= 7 and missing >= 2: return `"victory"`
    - If day >= 7 and missing == 1: return `"partial_victory"`
    - If day >= 7 and missing == 0: return `"defeat"`
  - `check_secret_ending(gamestate) -> bool` — all of: `journal_read`, `mirror_seen`, `missing >= 2`, `day >= 6`
  - `display_victory(io)`, `display_partial_victory(io)`, `display_defeat(io)`, `display_secret_ending(io)` — output ending text from STORY.md
  - `display_dream_confrontation(io)` — output the AE's monologue

- [ ] **5.2** Add ending state flags to `GameState` in `src/core/game_world.py`:
  - `self.game_over: bool = False`
  - `self.ending_type: str | None = None`
  - `self.in_dream_confrontation: bool = False`

- [ ] **5.3** Create `LetGoCommand` in `src/commands/game_commands.py`:
  - `can_execute()`: only valid when `gamestate.in_dream_confrontation == True`
  - Execute: display secret ending text, set `game_over = True`, `ending_type = "secret"`

- [ ] **5.4** Create `HoldOnCommand` in `src/commands/game_commands.py`:
  - `can_execute()`: only valid when `gamestate.in_dream_confrontation == True`
  - Execute: clear `in_dream_confrontation`, return to normal — standard victory ending will trigger

- [ ] **5.5** Register `"let go"` and `"hold on"` in `src/inputparser.py` COMMANDS dict

- [ ] **5.6** Update `GameState.Examine()` in `src/core/game_world.py`:
  - Before calling `alter_ego.run()` when feel <= 0: check `GameEndings.check_secret_ending(self)`
  - If secret conditions met: call `display_dream_confrontation(io)`, set `in_dream_confrontation = True`, reset feel, and **return without calling alter_ego.run()** — the game loop will handle the dream input
  - After `alter_ego.run()`: if `device_activated`, display defeat ending, set `game_over = True`

- [ ] **5.7** Update main game loop in `src/gameloop.py`:
  - Change `while True:` to `while not state.game_over:`
  - After each `state.Examine()` call, check `GameEndings.check_ending(state)`
  - If ending detected and not already game_over: display appropriate ending, set `game_over = True`
  - During dream confrontation: only accept `let go` and `hold on` (reject other commands with message like `"The voice echoes in the darkness. What do you do?"`)
  - After the loop exits: display a final message or clean exit

- [ ] **5.8** Finalize journal text in `Journal.Examine()` (`src/core/items.py`):
  - Replace placeholder with full STORY.md backstory: childhood event at age 8, imaginary friend, gradual onset of fears, final entry about not remembering when the door became a wall

- [ ] **5.9** Add all ending text constants to `src/endings.py` from STORY.md:
  - Victory: "The TV flickers to life..." through "Maybe tomorrow."
  - Partial Victory: "The TV crackles..." through "He starts planning."
  - Defeat: "You wake to a sound..." through "GAME OVER"
  - Secret: Dream confrontation + "No, you say..." through "They always did."

- [ ] **5.10** End-of-game event queue check in `src/gameloop.py`:
  - On each loop iteration, before prompting: if `get_current_day() >= 7` and not `in_dream_confrontation`, trigger ending check
  - This ensures endings fire even if the player hasn't slept

### Files Modified

| File | Changes |
|------|---------|
| `src/core/game_world.py` | Add game_over/ending_type/in_dream_confrontation flags, update Examine() |
| `src/gameloop.py` | Add ending checks, dream confrontation input restriction, loop exit condition |
| `src/commands/game_commands.py` | Add LetGoCommand, HoldOnCommand |
| `src/inputparser.py` | Register let go / hold on commands |
| `src/core/items.py` | Finalize Journal.Examine() with full backstory text |

### Files Created

| File | Purpose |
|------|---------|
| `src/endings.py` | GameEndings class with condition checks + all ending text |
| `tests/test_endings.py` | Unit tests for ending conditions and text |
| `tests/test_dream_confrontation.py` | Unit tests for dream sequence + let go/hold on |
| `tools/test_victory_ending.txt` | E2E: simulate Day 7 with 2+ missing components |
| `tools/test_defeat_ending.txt` | E2E: simulate device activation |
| `tools/test_secret_ending.txt` | E2E: full secret ending path |

### Testing Plan

**Unit tests** (20+ minimum):
- check_ending() returns None before Day 7 with incomplete device
- check_ending() returns "victory" at Day 7 with 2+ missing
- check_ending() returns "partial_victory" at Day 7 with 1 missing
- check_ending() returns "defeat" at Day 7 with 0 missing
- check_ending() returns "defeat" when device_activated
- check_secret_ending() true when all 4 conditions met
- check_secret_ending() false when journal not read
- check_secret_ending() false when mirror not seen
- check_secret_ending() false when too few missing components
- check_secret_ending() false before Day 6
- LetGoCommand only valid during dream confrontation
- LetGoCommand sets game_over + ending_type="secret"
- HoldOnCommand only valid during dream confrontation
- HoldOnCommand clears dream state
- Victory text displayed correctly
- Defeat text displayed correctly
- Partial victory text displayed correctly
- Secret ending text displayed correctly
- Dream confrontation text displayed
- Game loop terminates when game_over is True

**E2E tests** (3+ files): victory, defeat, secret ending (each exercises the full game flow to an ending)

### Exit Criteria

- [ ] All existing tests pass (zero regressions)
- [ ] All 20+ new unit tests pass
- [ ] All 3+ new e2e tests pass
- [ ] Victory: triggers Day 7 + 2+ missing components, displays correct text
- [ ] Partial Victory: triggers Day 7 + exactly 1 missing, displays correct text
- [ ] Defeat: triggers when device_activated, displays correct text
- [ ] Secret: triggers with journal+mirror+victory conditions, dream confrontation appears
- [ ] `let go` displays full secret ending including walking outside
- [ ] `hold on` returns to normal gameplay → victory ending
- [ ] Game loop cleanly terminates on all 4 endings
- [ ] **Full playthrough possible from start to each of the 4 endings**
- [ ] Combined test coverage ≥ 80%

---

## Final Verification

After all 5 phases are complete, run the full validation suite:

```bash
# All unit tests
uv run pytest -v

# All e2e tests
uv run python tools/run_e2e_tests.py

# Combined coverage
uv run coverage erase && uv run coverage run -m pytest && uv run coverage run -a tools/run_e2e_tests.py && uv run coverage report --show-missing
```

**Final acceptance criteria:**
- [ ] 287+ unit tests pass (110+ new)
- [ ] 43+ e2e tests pass (16+ new)
- [ ] Combined coverage ≥ 85%
- [ ] All 4 endings reachable from a fresh game start
- [ ] No regressions in any original test
