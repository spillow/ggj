# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Game
```bash
python main.py
```

### Testing
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_gamestate.py

# Run specific test
python -m pytest tests/test_gamestate.py::TestHero::test_pickup_success
```

The codebase uses pytest for automated testing with a comprehensive test suite covering:
- Game object functionality (Hero, Container, Food, etc.)
- Game mechanics (pickup, inventory, room navigation)
- I/O operations using mock interfaces
- State management and time progression

## Code Architecture

This is a text-based adventure game written in Python for Global Game Jam 2015. The game simulates a psychological scenario where the player controls a character who believes he has mobility issues confining him to his apartment.

### Core Architecture

**Game Loop (`src/gameloop.py`)**
- Main game loop that initializes the game state and processes user input
- Handles the event queue for scheduled deliveries (government checks every 2 weeks)
- Coordinates between input parsing, action execution, and state examination

**Game State (`src/gamestate.py`)**
- Contains the complete object model with inheritance hierarchy:
  - `Object` (base class for all game items)
  - `Container` (objects that hold other objects)
  - `Openable` (containers that can be opened/closed)
  - `Room` (game locations)
  - `Hero` (player character with inventory and feel/balance stats)
- Manages the apartment layout with rooms: main, bedroom, bathroom, closet
- Implements time system using Python's datetime (starting March 15, 1982 at 3:14 AM)
- Tracks player stats: feel (energy), balance (money)

**Input System (`src/inputparser.py`)**
- Pattern-based command parser using string templates with variables like `{a}` and `{b}`
- Maps natural language commands to action functions
- Supports commands like "get {item} from {container}", "go to {room}", etc.

**Actions (`src/actions.py`)**
- Individual action functions that modify game state
- Each action handles time advancement and validation
- Key mechanics: inventory management, room navigation, phone calls, eating food

**Event System (`src/delivery.py`)**
- Time-based event queue for scheduled events
- Handles deliveries from stores (grocery, hardware)
- Government check deliveries every 2 weeks

**I/O Interface (`src/io_interface.py`)**
- Abstraction layer for input/output operations
- `ConsoleIO` for real gameplay, `MockIO` for testing
- Enables deterministic, fast testing without blocking I/O

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

## Testing Architecture & Design Principles

The codebase has been refactored to follow testable design patterns:

### I/O Abstraction (`src/io_interface.py`)

**Interface Pattern**: All user interaction goes through the `IOInterface` abstraction:
- `ConsoleIO`: Real console I/O for gameplay
- `MockIO`: Test implementation that records outputs and provides scripted inputs

**Benefits**:
- Tests run instantly without blocking on user input
- Deterministic testing with pre-configured responses
- Complete verification of all game output

### Dependency Injection

**Pattern**: Core classes accept their dependencies as constructor parameters:
```python
# Before: Hard-coded dependencies
def some_method(self):
    print("message")  # Hard to test

# After: Injected dependencies
def some_method(self):
    self.io.output("message")  # Easily mockable
```

**Implementation**:
- `GameState(io: IOInterface = None)` - accepts optional IO interface
- `Hero(startRoom: Room, io: IOInterface)` - requires IO for interactions
- All game objects use `hero.io` for output instead of direct `print()`

### Pure Business Logic

**Separation of Concerns**: Core game logic is separated from I/O side effects:
- **Pure Functions**: Game mechanics like inventory rules, time calculations
- **Stateful Objects**: Game state management without I/O coupling
- **I/O Layer**: User interface completely abstracted away

### Test Structure

**Test Categories**:
- **Unit Tests**: Individual object behavior (`TestHero`, `TestContainer`)
- **Integration Tests**: Object interactions and game mechanics
- **Mock Tests**: User interaction scenarios with scripted inputs

**Test Fixtures**: Each test gets fresh instances to prevent test pollution:
```python
def setup_method(self):
    self.mock_io = MockIO()
    self.state = GameState(self.mock_io)
    self.hero = self.state.hero
```

### Best Practices for New Features

When adding new features, follow these patterns:

1. **Accept IO Interface**: New classes should accept `IOInterface` parameter
2. **Use Dependency Injection**: Don't create dependencies internally, accept them
3. **Separate Logic from I/O**: Keep business logic pure, delegate I/O to interface
4. **Write Tests First**: Use `MockIO` to script interactions and verify outputs
5. **Test Edge Cases**: Cover error conditions, boundary values, and state transitions

**Example**:
```python
# Good: Testable design
class NewFeature:
    def __init__(self, io: IOInterface):
        self.io = io

    def process(self, data: str) -> bool:
        result = self._calculate(data)  # Pure function
        self.io.output(f"Result: {result}")  # I/O via interface
        return result > 0

# Test
def test_new_feature():
    mock_io = MockIO()
    feature = NewFeature(mock_io)
    assert feature.process("test") == True
    assert "Result:" in mock_io.get_all_outputs()
```

This architecture ensures all new code is testable, maintainable, and follows separation of concerns.

## Coding style
This project adheres to PEP-8 guidelines and requires type hints.