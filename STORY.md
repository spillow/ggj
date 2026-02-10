# Leggo My Ego — Complete Story Design

## Premise

**March 15, 1982, 3:14 AM.** Arthur wakes in his apartment. He's been homebound for months — agoraphobia, he thinks, or maybe something physical. He doesn't question it anymore. Government checks keep the lights on. The phone connects him to the grocery store, the hardware store, and a building super who never picks up. That's his world.

Tonight, the TV shows something different: astrophysicists have detected a spacetime anomaly. A rift. Growing.

What Arthur doesn't know: an entity — the Alter Ego (AE) — has been nesting in his psyche for years, subtly enforcing his confinement, keeping him isolated. The rift has fully awakened it. Now, every time Arthur falls asleep, the AE takes control of his body. It's building something. A device. A **Convergence Amplifier** that will lock the rift open permanently, merging realities and annihilating both.

The rift will close naturally in ~7 days. The AE is racing to finish the device before that happens. Arthur is racing to stop it.

---

## The Alter Ego

**Nature**: A fragment of an extradimensional intelligence, lodged in Arthur's mind since a childhood incident he doesn't remember. It has been dormant for decades, exerting only a subtle psychosomatic hold — the "mobility issues" that keep Arthur confined. The rift's energy has fully activated it.

**Motivation**: The AE wants to return home — or more precisely, bring its home *here*. The Convergence Amplifier will lock the rift open and widen it until the two realities collapse into each other. The AE doesn't consider this destructive; from its perspective, it's reunification.

**Capabilities during sleep**: Full control of Arthur's body. Can move between rooms, use the phone, pick up and manipulate items, build and assemble. Limited by the same physical constraints as Arthur (same inventory weight limits, same store delivery times, same money pool).

**Personality** (revealed through evidence): Methodical, patient, slightly contemptuous of Arthur. Leaves physical evidence but not deliberate messages — receipts from orders, tools left out, construction progress. The AE doesn't think Arthur is a threat.

---

## The Convergence Amplifier

A crude but functional device assembled from hardware store materials and electronics surplus parts. Built in the **bedroom**. Requires 5 major components:

| # | Component | Materials Required | Built In |
|---|---|---|---|
| 1 | **Frame** | plywood-sheet + metal-brackets + box-of-nails + hammer | AE Phase 2 |
| 2 | **Wiring Harness** | copper-wire + insulated-cable + soldering-iron | AE Phase 3 |
| 3 | **Power Core** | battery-pack + copper-coil | AE Phase 4 |
| 4 | **Focusing Array** | crystal-oscillator + ice-cubes | AE Phase 4 |
| 5 | **Signal Amplifier** | signal-amplifier (installed as final step) | AE Phase 5 |

Once all 5 components are assembled and the AE gets one more sleep cycle, it activates the device.

---

## AE's 5-Phase Construction Plan

Each phase executes during one sleep cycle (triggered when Arthur's feel reaches 0).

### Phase 1 — "Surveying"

*First sleep.*

- AE examines the apartment and takes stock of available resources
- Orders from hardware store: copper-wire, metal-brackets
- Orders from electronics surplus: vacuum-tubes, battery-pack
- Spends Arthur's money

**Evidence on waking:**
- Phone is off the hook / warm to touch
- Balance is reduced (receipts on the table show purchases)
- Items in apartment slightly rearranged
- TV left on

### Phase 2 — "The Frame"

*Second sleep.*

- AE picks up delivered hardware materials
- Builds the **device frame** in the bedroom using plywood + brackets + nails + hammer
- Orders: soldering-iron, insulated-cable, copper-coil

**Evidence on waking:**
- **Device frame** visible in bedroom (player can examine it)
- Plywood, brackets, and nails consumed from inventory/containers
- Hammer left on the bedroom floor
- More receipts on the table
- Sawdust on the bedroom floor

### Phase 3 — "The Wiring"

*Third sleep.*

- AE wires the frame with copper-wire and insulated-cable
- Uses soldering-iron to create connections
- Creates the **wiring harness** on the device
- Orders: crystal-oscillator, signal-amplifier, ice-cubes

**Evidence on waking:**
- Burn marks on bedroom floor from soldering
- Wiring visible on the device frame
- Smell of solder in the air
- Soldering-iron still hot to the touch
- More receipts

### Phase 4 — "The Power Core"

*Fourth sleep.*

- AE installs battery-pack + copper-coil as the **power core**
- Creates the **focusing array** from crystal-oscillator + ice-cubes
- TV starts showing interference (the anomaly reacting to the powered device)
- Lights in the apartment flicker

**Evidence on waking:**
- Device humming faintly in the bedroom
- TV shows static between news broadcasts
- Apartment lights occasionally dim
- Ice cubes missing from fridge/inventory
- The air feels electrically charged

### Phase 5 — "Activation"

*Fifth sleep.*

- AE installs signal-amplifier (final component)
- Attempts to activate the **convergence device**
- **If device is complete**: Activation succeeds. **LOSE ENDING.**
- **If components are missing**: Device sparks and fails. AE is frustrated. Player survives to the next cycle.

---

## Player Actions and Counter-Strategies

### Existing Actions (already implemented)

| Command | What It Does | Strategic Use |
|---|---|---|
| `call phone` | Order from stores | Drain money so AE can't order; or order items to control them |
| `rolodex` | View phone numbers | Learn about new electronics surplus store |
| `eat {food}` | Eat food, restore feel | Stay awake longer = fewer AE turns |
| `take ice bath` | +40 feel, consumes ice-cubes | Major feel boost AND denies AE the focusing array material |
| `pick up {item} from {container}` | Take items | Grab delivered materials before sleeping so AE can't use them |
| `nail self in closet` | Nail into closet with hammer + nails + plywood | **If Arthur sleeps here, AE wakes up trapped and wastes its entire turn breaking out** |
| `open / close {container}` | Manage containers | Access deliveries in fridge/toolbox/table |
| `examine {object}` | Investigate objects | Examine device components, receipts, evidence |
| `watch tv` | Watch the TV news | Track the anomaly's timeline — news evolves daily |
| `look at watch` | Check time | Track how many days have passed |
| `balance` | Check money | Monitor funds to deny AE purchasing power |
| `feel` | Check energy | Gauge how much time before sleeping |
| `ponder` | Waste time | Advance time strategically (or recklessly) |
| `inspect room` | Look around | See what's changed in a room after sleeping |
| `inventory` | Check held items | Track what you're holding vs. what AE could grab |
| `mail check` | Mail government check | Get $100 more — but AE can spend it too |
| `go to {room}` | Move between rooms | Navigate to bedroom to sabotage, bathroom for ice bath, etc. |

### New Actions (to be implemented)

| Command | What It Does | Requirements |
|---|---|---|
| `disassemble frame` | Tear down the device frame | Hammer in inventory + in bedroom |
| `cut wires` | Remove the wiring harness | Wire-cutters in inventory + in bedroom |
| `remove battery` | Pull out the power core | In bedroom |
| `remove crystal` | Remove the focusing array | In bedroom |
| `barricade bedroom` | Block the bedroom door for one cycle | Plywood + nails + hammer + NOT in bedroom |
| `read journal` | Read Arthur's journal | Journal in inventory or same room |
| `examine mirror` | Look in bathroom mirror | In bathroom. On Day 4+, triggers AE flicker |
| `let go` | Secret ending choice | Only available during dream confrontation |

### Counter-Strategy Breakdown

**Resource Denial** — prevent the AE from acquiring materials:
- Spend money before sleeping so AE can't afford to order
- Pick up delivered items before sleeping so AE can't use them
- Eat ice cubes or take ice bath — denies AE the focusing array material
- Order items yourself to control the supply

**Active Sabotage** — undo the AE's construction work:
- `disassemble frame` (requires hammer) — reverts the frame component
- `cut wires` (requires wire-cutters) — reverts the wiring harness
- `remove battery` — reverts the power core
- `remove crystal` — reverts the focusing array
- Each disassembly forces the AE to rebuild that component, costing it a phase

**Physical Obstruction** — block the AE's access:
- **Nail self in closet**: If Arthur falls asleep in the nailed closet, the AE wakes up trapped. It must spend its entire turn breaking out, wasting one build phase. The nailing is destroyed in the process (closet returns to normal).
- **Barricade bedroom**: Blocks the AE from reaching the device for one cycle. The AE must spend a turn clearing the barricade.

**Staying Awake** — reduce the number of AE turns:
- Eat food to maintain feel (delay the sleep trigger)
- Ice bath grants +40 feel — significant extension
- Caffeine and energy drinks give strong feel boosts
- Fewer sleep cycles = fewer opportunities for the AE to build

**Investigation** — learn the AE's plan to counter it effectively:
- Examine the device and its components to understand what's being built
- Read receipts on the table to see what's been ordered and what's incoming
- Read the journal to learn about the AE's long history with Arthur
- Watch TV for evolving news about the anomaly's timeline

---

## Expanded Item Inventory

### Grocery Store (288-7955) — Delivery: Next Day

| Item | Cost | Feel Boost | Notes |
|---|---|---|---|
| spicy-food | $10 | +30 | Existing. High-tier energy food |
| caffeine | $5 | +20 | Existing. Solid feel boost |
| bananas | $2 | +5 | Existing. Cheap but weak |
| ice-cubes | $6 | +2 | Existing. Low feel, but key for ice baths AND AE's focusing array |
| energy-drinks | $8 | +25 | NEW. Premium energy alternative |
| canned-soup | $4 | +10 | NEW. Reliable mid-tier staple |
| chocolate-bar | $3 | +8 | NEW. Affordable comfort food |
| protein-bar | $6 | +15 | NEW. Good value per dollar |

### Hardware Store (592-2874) — Delivery: 2 Days

| Item | Cost | Notes |
|---|---|---|
| hammer | $20 | Existing. Needed for frame construction AND disassembly |
| box-of-nails | $5 | Existing. Needed for frame, closet nailing, barricading |
| plywood-sheet | $30 | Existing. Needed for frame, closet nailing, barricading |
| copper-wire | $15 | NEW. AE needs for wiring harness |
| metal-brackets | $10 | NEW. AE needs for device frame |
| soldering-iron | $25 | NEW. AE needs for wiring connections |
| duct-tape | $3 | NEW. General utility |
| wire-cutters | $12 | NEW. Player can use to disassemble AE's wiring |

### Electronics Surplus Store (743-8291) — NEW STORE — Delivery: 3 Days

| Item | Cost | Notes |
|---|---|---|
| vacuum-tubes | $20 | Supplementary device components |
| crystal-oscillator | $35 | Key component for focusing array |
| copper-coil | $18 | Power core component |
| battery-pack | $12 | Power source for the device |
| signal-amplifier | $40 | Final and most expensive device component |
| insulated-cable | $8 | Wiring component |

### New Room Objects

| Object | Location | Type | Notes |
|---|---|---|---|
| medicine-cabinet | Bathroom | Openable container | Contains aspirin initially |
| bookshelf | Bedroom | Container | Contains Arthur's journal |
| mirror | Bathroom | Examinable | Shows AE's reflection flicker on Day 4+ |
| journal | Bookshelf (bedroom) | Readable item | Reveals Arthur's backstory and AE's long influence |

### Device Components (appear as AE builds)

| Object | Location | Appears After | Player Can... |
|---|---|---|---|
| device-frame | Bedroom | AE Phase 2 | Examine, disassemble (hammer) |
| wiring-harness | Bedroom | AE Phase 3 | Examine, cut (wire-cutters) |
| power-core | Bedroom | AE Phase 4 | Examine, remove |
| focusing-array | Bedroom | AE Phase 4 | Examine, remove |
| convergence-device | Bedroom | AE Phase 5 | Examine (too late to disassemble) |

---

## Evolving World State

### TV News Progression

The TV news evolves each in-game day, providing timeline and urgency:

| Day | Date | Broadcast |
|---|---|---|
| 1 | Mar 15 | "Breaking news: prominent astrophysicists have recently discovered a strange anomaly in space. The origins are not yet clear. Stay tuned for further details." |
| 2 | Mar 16 | "UPDATE: The anomaly has been confirmed to be growing. Scientists describe a 'spacetime distortion' of unknown origin. Localized gravitational effects have been reported near observatories worldwide." |
| 3 | Mar 17 | "DEVELOPING: Gravitational disturbances now reported worldwide. Emergency services placed on alert. Scientists say the anomaly appears to be a 'rift' in the fabric of spacetime itself." |
| 4 | Mar 18 | "EMERGENCY BULLETIN: Localized reality distortions reported near the anomaly's apparent origin point. Residents urged to remain indoors. The rift appears to be destabilizing surrounding spacetime." |
| 5 | Mar 19 | "Scientists now predict the anomaly will collapse and close within 48 to 72 hours. 'The rift is healing itself,' says Dr. Hernandez of the Jet Propulsion Laboratory. 'Spacetime wants to be whole.'" |
| 6 | Mar 20 | "The anomaly is visibly shrinking. Scientists are cautiously optimistic. 'We expect full closure within 24 hours,' says the lead researcher. Worldwide vigils continue." |
| 7 | Mar 21 | "THE ANOMALY HAS CLOSED. Scientists confirm the rift in spacetime has sealed completely. The event is over. World leaders express relief. Scientists warn that the cause remains unknown." |

### Building Super (198-2888) Progression

| Day | Response |
|---|---|
| 1-3 | No answer. Rings 3 times, nobody picks up. (Existing behavior.) |
| 4 | Answers: "Yeah? Oh, you. Listen, other tenants have been complaining about noises from your apartment at night. Banging, drilling sounds. And the electrical — the whole building's been having power surges. You know anything about that?" |
| 5 | "Look, whatever you're doing up there, the power company is threatening to cut the whole building's service. I've got half a mind to come up there myself." |
| 6+ | "The power surges have stopped, at least. But if I hear one more complaint, I'm calling the city. You hear me?" (If device has power core.) Or: "Things seem to have calmed down. Try to keep it that way." (If player has been successful.) |

### Evidence Details by Phase

When Arthur wakes after each AE phase, the game should describe what's changed. This is how the player pieces together what's happening.

**After Phase 1 (Surveying):**
- Intro prompt includes: "Something feels... off. The phone is sitting off the hook."
- Examining the table reveals receipts with unfamiliar orders
- Checking balance shows money has been spent
- Items in the main room are slightly rearranged (containers that were closed may be open)

**After Phase 2 (The Frame):**
- Intro prompt includes: "There's a strange smell. Sawdust?"
- Entering the bedroom reveals a crude wooden frame — "A structure made of plywood and metal brackets stands in the corner. It wasn't here before."
- Hammer found on bedroom floor
- Receipts on table show more orders
- Plywood, brackets, and nails are gone from containers

**After Phase 3 (The Wiring):**
- Intro prompt includes: "Your fingertips are blackened. Solder burns?"
- The device in the bedroom now has wires running through it — "The frame is now laced with copper wiring. Solder joints gleam at the connections."
- Burn marks on the bedroom floor
- Faint chemical smell

**After Phase 4 (The Power Core):**
- Intro prompt includes: "The lights flicker as you open your eyes."
- The device hums faintly — "The device has a battery assembly and a strange crystalline component. It hums with a low, steady vibration."
- TV shows static between broadcasts
- Apartment lights dim periodically
- The air feels heavy and charged

**After Phase 5 (Signal Amplifier installed):**
- If device is complete → game transitions directly to Defeat ending
- If device is incomplete → "The device sparks and whines, then falls silent. Something is missing. Whatever happened while you slept, it didn't work."

---

## The Four Endings

### 1. VICTORY — "The Rift Closes"

**Condition**: Day 7 (March 21) arrives and the Convergence Amplifier is missing 2 or more components.

> The TV flickers to life with the morning news. "THE ANOMALY HAS CLOSED," the anchor announces, barely containing their relief. "Scientists confirm the rift in spacetime has sealed completely."
>
> You look toward the bedroom. The half-built device sits there — an ugly tangle of wire and plywood, inert and harmless. Just junk.
>
> Something shifts inside you. A pressure you've felt for years — behind your eyes, at the base of your skull — simply... stops. Like a hand releasing its grip. The apartment is quiet. Really quiet. For the first time in months, the silence feels peaceful rather than oppressive.
>
> You look at the front door. Maybe tomorrow.

### 2. PARTIAL VICTORY — "Scarred but Surviving"

**Condition**: Day 7 arrives and the device is missing exactly 1 component.

> The TV crackles: "THE ANOMALY HAS CLOSED."
>
> But in the bedroom, the nearly-complete device doesn't agree. It shudders. The hum rises to a shriek. A blinding flash erupts from the crystalline array, and for a split second you see *through* the walls — a landscape that is not your city, colors that don't belong to your spectrum.
>
> Then silence. The device collapses in on itself, a smoking ruin. The bedroom wall is scorched black.
>
> You're alive. You're shaking, but alive. The TV returns: "...worldwide celebrations as the event concludes..."
>
> But you can still feel it. Faint, like a whisper at the edge of hearing. A presence. Not gone. Just dormant. Again.
>
> You look at the scorched wall and start planning.

### 3. DEFEAT — "The Convergence"

**Condition**: The AE completes all 5 components and gets a sleep cycle to activate.

> You wake to a sound you've never heard before — a deep, resonant hum that seems to come from everywhere and nowhere. The bedroom is filled with light. Not lamp light. Not sunlight. Something older. Something wrong.
>
> The device is active. It pulses with energy that makes your teeth ache and your vision swim. Through the light, you see... the other side. A landscape of impossible geometry, layered over your bedroom like a double exposure. The walls are dissolving.
>
> The rift widens.
>
> From the other room, the TV blares: "BREAKING: The anomaly is expanding rapidly. This is not a drill. All residents are advised to seek shelter immed—"
>
> Static.
>
> **GAME OVER**

### 4. SECRET ENDING — "Leggo My Ego"

**Conditions** (ALL required):
1. Player has read the **journal** from the bookshelf in the bedroom
2. Player has examined the **mirror** in the bathroom on Day 4 or later (triggers AE reflection flicker)
3. The Convergence Amplifier is missing 2+ components (Victory condition met)
4. Player falls asleep one final time on Day 6 or 7

**The Journal** reveals Arthur's childhood: a strange event at age 8, an "imaginary friend" who became less imaginary over time, the slow onset of fears — first of crowds, then of the outdoors, then of the hallway outside the apartment door. The last entry, months old, reads: *"I don't remember when I stopped wanting to leave. I don't remember when the door started feeling like a wall. Was it always like this?"*

**The Mirror**, examined on Day 4 or later, shows a momentary flicker: Arthur's reflection, but the expression is wrong — sharper, colder, with eyes that seem to look *through* the glass. Then it's gone.

**The Dream Confrontation**: Instead of the normal sleep-and-wake sequence, the screen goes dark. Then text appears:

> Darkness. But not sleep. You're aware. More aware than you've ever been.
>
> A voice. Your voice, but not your voice.
>
> "You think you've won? I've been here since you were a child. The fear. The walls. The locked door. The reasons you never leave. That was all me. You *needed* me."
>
> A pause.
>
> "You still need me."

The player is presented with two choices:
- `let go`
- `hold on`

**If the player chooses `hold on`**: Normal sleep resumes. No special ending. The game continues to the standard Victory ending.

**If the player chooses `let go`**:

> "No," you say. And you mean it.
>
> The voice fractures. Splinters. Like glass breaking in slow motion.
>
> "You can't — I'm part of —"
>
> "No. You're not."
>
> Silence. Real silence. The kind you haven't heard since you were eight years old.
>
> You wake up.
>
> The apartment is still. The device sits in the bedroom, dead and harmless. The TV murmurs about the anomaly closing. But something is different. The door. The front door of your apartment. It doesn't look like a wall anymore. It looks like a door.
>
> You walk to it. Put your hand on the knob. Turn it.
>
> The sunlight is blinding after so many months indoors. The air smells like spring. Your legs carry you over the threshold without hesitation.
>
> You take a step. Then another.
>
> Your legs work fine. They always did.

---

## Game Flow

```
DAY 1 (Mar 15):
  Wake at 3:14 AM → explore apartment → watch TV (anomaly news) →
  manage resources (eat, order, etc.) → feel drops to 0 →
  SLEEP → AE Phase 1 (Surveying)

DAY 2 (Mar 16):
  Wake → find evidence (phone off hook, receipts, balance reduced) →
  investigate → manage resources → SLEEP → AE Phase 2 (The Frame)

DAY 3 (Mar 17):
  Wake → device frame visible in bedroom →
  player can disassemble? order wire-cutters? →
  SLEEP → AE Phase 3 (The Wiring)

DAY 4 (Mar 18):
  Wake → wiring on device → super answers phone →
  TV emergency bulletin → mirror shows AE flicker →
  SLEEP → AE Phase 4 (Power Core + Focusing Array)

DAY 5 (Mar 19):
  Wake → device humming → desperate countermeasures →
  TV: "rift closing in 48-72 hours" →
  SLEEP → AE Phase 5 (Activation Attempt)

DAY 6 (Mar 20):
  Wake → if device incomplete, AE failed →
  rift closing → possible final sleep →
  secret ending triggers if conditions met

DAY 7 (Mar 21):
  Rift closes → ending determined by device completion state
```

**Note**: This flow assumes the player sleeps once per day. Strategic players who stay awake longer will compress the AE's build schedule — the AE only advances when Arthur sleeps, regardless of how many in-game days pass.

---

## Appendix: Complete Action Reference

### All Player Commands

**Navigation:**
- `go to {room}` / `go in {room}` / `enter {room}` / `enter the {room}` — move between rooms
- `inspect room` / `view room` / `look around room` — examine current room

**Inventory & Objects:**
- `pick up {item} from {container}` / `get {item} from {container}` — take items
- `inventory` — show held items
- `examine {object}` — inspect an object
- `open {object}` / `close {object}` — manage containers
- `look in {object}` — peek inside a container
- `watch {object}` — watch something (TV)

**Status:**
- `look at watch` — check current game time and date
- `balance` — check money
- `feel` — check energy level

**Phone & Commerce:**
- `call phone` — make a phone call (prompts for number)
- `rolodex` — show available phone numbers
- `mail check` — mail a government check for $100

**Food & Recovery:**
- `eat {food}` — eat food from the fridge for feel boost
- `take ice bath` / `ice bath` — ice bath in bathroom (+40 feel, consumes ice-cubes)

**Construction & Destruction:**
- `nail self in closet` / `nail wood to door` — nail into closet (hammer + nails + plywood)
- `barricade bedroom` — block bedroom door (plywood + nails + hammer, NEW)
- `disassemble frame` — tear down device frame (hammer, NEW)
- `cut wires` — remove wiring harness (wire-cutters, NEW)
- `remove battery` — pull out power core (NEW)
- `remove crystal` — remove focusing array (NEW)

**Investigation:**
- `read journal` — read Arthur's journal (NEW)
- `examine mirror` — look in bathroom mirror (NEW)

**Time:**
- `ponder` — waste time pondering (prompts for hours)

**Special:**
- `let go` / `hold on` — dream confrontation choices (secret ending, NEW)
- `debug items` — development testing shortcut

**Command System:**
- `undo` — undo last command
- `redo` — redo last undone command
