# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Game
```bash
python main.py
```

### Testing
No automated tests are present in the codebase. Testing is done manually by running the game and playing through scenarios.

## Code Architecture

This is a text-based adventure game written in Python for Global Game Jam 2015. The game simulates a psychological scenario where the player controls a character who believes he has mobility issues confining him to his apartment.

### Core Architecture

**Game Loop (`gameloop.py`)**
- Main game loop that initializes the game state and processes user input
- Handles the event queue for scheduled deliveries (government checks every 2 weeks)
- Coordinates between input parsing, action execution, and state examination

**Game State (`gamestate.py`)**
- Contains the complete object model with inheritance hierarchy:
  - `Object` (base class for all game items)
  - `Container` (objects that hold other objects)
  - `Openable` (containers that can be opened/closed)
  - `Room` (game locations)
  - `Hero` (player character with inventory and feel/balance stats)
- Manages the apartment layout with rooms: main, bedroom, bathroom, closet
- Implements time system using Python's datetime (starting March 15, 1982 at 3:14 AM)
- Tracks player stats: feel (energy), balance (money)

**Input System (`inputparser.py`)**
- Pattern-based command parser using string templates with variables like `{a}` and `{b}`
- Maps natural language commands to action functions
- Supports commands like "get {item} from {container}", "go to {room}", etc.

**Actions (`actions.py`)**
- Individual action functions that modify game state
- Each action handles time advancement and validation
- Key mechanics: inventory management, room navigation, phone calls, eating food

**Event System (`delivery.py`)**
- Time-based event queue for scheduled events
- Handles deliveries from stores (grocery, hardware)
- Government check deliveries every 2 weeks

### Key Game Mechanics

- **Feel System**: Player energy that decreases over time, causes passing out at 0
- **Money System**: Player has $100 starting balance, can order items by phone
- **Time System**: All actions advance time, some significantly (pondering, phone calls)
- **Inventory**: Weight-based system, hero can carry up to 100 weight units
- **Room Navigation**: Movement between apartment rooms with special closet mechanics
- **Store Orders**: Phone-based ordering system with delivery scheduling

### Special Features

- **Closet Nailing**: Player can nail themselves into the closet using hammer, nails, and plywood
- **AlterEgo System**: Placeholder system that activates when player passes out (currently empty)
- **Phone System**: Three numbers - grocery store, hardware store, and building super
- **TV News**: Shows astrophysics anomaly news when examined

### State Management

The game uses a centralized `GameState` object that contains:
- `apartment`: The apartment container with all rooms and objects
- `hero`: Player character with stats and inventory
- `watch`: Time tracking object
- `eventQueue`: Scheduled events system

All game objects maintain parent-child relationships for location tracking, and the `@sameroom` decorator ensures actions only work when the player is in the same room as objects.