# Global Game Jam 2015 - Text Adventure Game

A text-based adventure game created for Global Game Jam 2015. This is a psychological thriller about a character who believes he has mobility issues confining him to his apartment. The goal is to figure out what is happening and prevent an unrecoverable event.

**Game Jam Page:** http://globalgamejam.org/2015/games/leggo-my-ego

## Features

- **Rich Text Adventure Mechanics**: Navigate rooms, interact with objects, manage inventory
- **Time System**: All actions advance the in-game clock (starting March 15, 1982 at 3:14 AM)
- **Feel/Energy System**: Player energy decreases over time; eating food restores it
- **Money Management**: Start with $100, order items by phone with delivery scheduling
- **Phone System**: Call three numbers - grocery store, hardware store, and building super
- **Event Queue**: Scheduled deliveries and government checks every 2 weeks
- **Special Mechanics**: Nail yourself into the closet using hammer, nails, and plywood
- **Comprehensive Testing**: 125+ tests covering all game mechanics using mock I/O

## Installation

### Requirements
- Python 3.7+
- pytest (for running tests)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd ggj

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Game
```bash
python main.py
```

### Game Commands

The game supports the following commands (case-sensitive):

#### Debug and Development
- `debug items` - Give player hammer, nails, and plywood for testing

#### Phone System
- `call phone` - Make a phone call using the main room phone
- `rolodex` - Show available phone numbers

#### Time and Status
- `look at watch` - Check current game time
- `ponder` - Waste time pondering (prompts for hours)
- `balance` - Check current money balance
- `feel` - Check current energy level

#### Food and Eating
- `eat {food}` - Eat food from the opened fridge

#### Object Interaction
- `examine {object}` - Examine an object in the room
- `watch {object}` - Watch something (specifically TV)
- `look in {object}` - Look inside a container
- `open {object}` - Open a container
- `close {object}` - Close a container

#### Inventory Management
- `pick up {item} from {container}` - Get item from container
- `get {item} from {container}` - Alternative get command
- `inventory` - Show current inventory

#### Movement
- `go in {room}` - Enter a room
- `go to {room}` - Go to a room
- `enter {room}` - Enter a room
- `enter the {room}` - Enter a room (with article)

#### Special Actions
- `nail wood to exit` - Nail yourself into closet
- `nail wood to door` - Alternative nailing command
- `nail self in` - Alternative nailing command
- `nail self in closet` - Alternative nailing command
- `inspect room` - Look around current room
- `view room` - Alternative room inspection
- `look around room` - Alternative room inspection
- `mail check` - Mail a government check for money

### Game World
The apartment contains:
- **Main Room**: Phone, toolbox, fridge, cabinet, table, TV
- **Bedroom**: Basic sleeping area
- **Bathroom**: Standard bathroom
- **Closet**: Can be nailed shut for special gameplay

## Development

### Architecture
- **Modular Design**: Separated game logic, I/O, actions, and state management
- **Object Hierarchy**: Base `Object` class with specialized containers, rooms, and items
- **I/O Abstraction**: `IOInterface` allows both console and mock implementations for testing
- **Event System**: Time-based delivery and event scheduling
- **Command Parser**: Pattern-based command parsing with variable substitution
- **Type Safety**: Comprehensive type hints throughout the codebase

### Testing

#### Unit Tests
```bash
# Run all unit tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_gamestate.py

# Run specific test
python -m pytest tests/test_gamestate.py::TestHero::test_pickup_success
```

The codebase has **125 unit tests** covering:
- **Game Object Functionality**: Hero, Container, Food, Watch, Phone, etc.
- **Game Mechanics**: Pickup, inventory, room navigation, eating, time progression
- **I/O Operations**: Mock interfaces for deterministic testing
- **State Management**: Game state initialization and progression
- **Command Parsing**: All 31 supported commands and edge cases
- **Action Functions**: All game actions with success and error conditions
- **Apartment Structure**: Room layout and object placement

#### End-to-End Tests
```bash
# Run all end-to-end tests
python tools/run_e2e_tests.py

# Run a specific test file
python tools/filecheck.py tools/test_basic.txt

# Run with verbose output to see game output
python tools/filecheck.py tools/test_basic.txt --verbose
```

The project includes a **FileCheck-like testing tool** for end-to-end game testing:
- **Test File Format**: Similar to LLVM's FileCheck with `# CHECK:` and `# CHECK-NEXT:` directives
- **Input Simulation**: Lines starting with `>` represent player input
- **Output Validation**: Whitespace-insensitive pattern matching against game output
- **Example Tests**: Basic functionality and phone system interaction tests

**Test File Example:**
```
# CHECK: What do we do next?:
> call phone
# CHECK: What number?:
> 288-7955
# CHECK: Hello this is the grocery store
```

### Code Style
- Follows PEP-8 guidelines with comprehensive type hints
- Uses dependency injection for testability
- Separates business logic from I/O operations
- Comprehensive docstrings for all classes and methods
- Test-driven development with MockIO for fast, deterministic tests

## Game Mechanics

### Stats
- **Feel (Energy)**: Starts at 50, decreases over time. Eating food restores it. Player passes out at 0.
- **Balance (Money)**: Starts at $100. Spend on phone orders, earn from government checks.

### Shopping
- **Grocery Store (288-7955)**: Food items with different feel boosts
  - spicy-food: +30 feel ($10)
  - caffeine: +20 feel ($5)
  - bananas: +5 feel ($2)
  - ice-cubes: +2 feel ($2)
- **Hardware Store (592-2874)**: Tools for special actions
  - hammer: $20
  - box-of-nails: $5
  - plywood-sheet: $30
- **Building Super (198-2888)**: Never answers, wastes time and energy

### Time System
Actions consume different amounts of time:
- Most actions: Minimal time advancement
- Pondering: Variable hours (user choice)
- Phone calls: 2-30 minutes depending on store interaction
- Eating: 20 minutes
- Nailing self in closet: 2 hours

### Object System
- **Weight-based inventory**: Hero can carry up to 100 weight units
- **Parent-child relationships**: All objects track their containers
- **Room-based interactions**: `@sameroom` decorator ensures actions only work when player is in same room
- **Openable containers**: Some containers must be opened before accessing contents

## Contributing

This is a preserved Global Game Jam 2015 project. The codebase demonstrates clean architecture patterns for text adventure games and serves as an educational example of:
- Test-driven development with comprehensive mock testing
- I/O abstraction for testability
- Object-oriented game design with clear inheritance hierarchies
- Event-driven programming with time-based events
- Command parsing with pattern matching
- Dependency injection for loose coupling

## License

Created for Global Game Jam 2015. See game jam page for original context and rules.