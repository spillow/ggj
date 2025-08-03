# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Game
```bash
python main.py
```

### Testing

#### Unit Testing
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all unit tests
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

#### End-to-End Testing
```bash
# Run all end-to-end tests
python tools/run_e2e_tests.py

# Run specific FileCheck test
python tools/filecheck.py tools/test_basic.txt --verbose
```

The project includes a **FileCheck-like tool** (`tools/filecheck.py`) for end-to-end testing:
- **Test Format**: Similar to LLVM's FileCheck tool
- **Directives**: 
  - `# CHECK: pattern` - Find pattern anywhere in remaining output
  - `# CHECK-NEXT: pattern` - Find pattern in the very next output line
- **Input Simulation**: Lines starting with `>` represent player input
- **Output Validation**: Whitespace-insensitive pattern matching
- **Test Files**: Located in `tools/` directory with `.txt` extension

#### Code Coverage

The project uses `pytest-cov` (a wrapper around coverage.py) for test coverage analysis. **Run coverage analysis on every code change to determine if new tests are needed.**

```bash
# Basic coverage report (terminal output with missing lines)
python -m pytest --cov=src --cov-report=term-missing

# Coverage with branch analysis (recommended)
python -m pytest --cov=src --cov-report=term-missing --cov-branch

# Generate HTML coverage report for detailed analysis
python -m pytest --cov=src --cov-report=html --cov-branch

# Set coverage threshold (fail if below 80%)
python -m pytest --cov=src --cov-fail-under=80 --cov-branch
```

**Coverage Analysis:**
- **Overall Coverage**: 73% statement coverage with 19 branch coverage gaps
- **Well-Tested Modules**: 
  - `inputparser.py`: 100% coverage (command parsing system)
  - `actions.py`: 93% coverage (game action functions)
- **Needs Testing**:
  - `gameloop.py`: 0% coverage (main game loop)
  - `delivery.py`: 59% coverage (event queue system)
  - `gamestate.py`: 66% coverage (core game objects)

**HTML Report**: After running with `--cov-report=html`, view detailed coverage at `htmlcov/index.html`

## Code Architecture

This is a text-based adventure game written in Python for Global Game Jam 2015. The game simulates a psychological scenario where the player controls a character who believes he has mobility issues confining him to his apartment.

### Core Architecture

**Main Entry Point (`main.py`)**
- Simple entry point that imports and runs the game loop
- No command-line arguments or configuration

**Game Loop (`src/gameloop.py`)**
- Main game loop that initializes the game state and processes user input
- Handles the event queue for scheduled deliveries (government checks every 2 weeks)
- Coordinates between input parsing, action execution, and state examination
- Supports dependency injection with optional `IOInterface` parameter for testing

**Game State (`src/gamestate.py`)**
- Contains the complete object model with inheritance hierarchy:
  - `Object` (base class for all game items with name, weight, parent container)
  - `Container` (objects that hold other objects with contents list)
  - `Openable` (containers that can be opened/closed with state tracking)
  - `Room` (game locations with Enter/Leave logic)
  - `Hero` (player character with inventory, feel/balance stats, and pickup logic)
- Manages the apartment layout with rooms: main, bedroom, bathroom, closet
- Implements time system using Python's datetime (starting March 15, 1982 at 3:14 AM)
- Tracks player stats: feel (energy starting at 50), balance (money starting at $100)

**Input System (`src/inputparser.py`)**
- Pattern-based command parser using string templates with variables like `{a}` and `{b}`
- Maps natural language commands to action functions via COMMANDS dictionary
- Supports commands like "get {item} from {container}", "go to {room}", etc.
- Returns tuple of (success, action/error_message, args)

**Actions (`src/actions.py`)**
- Individual action functions that modify game state
- Each action handles time advancement and validation
- Key mechanics: inventory management, room navigation, phone calls, eating food
- Uses decorators like `@thingify` to convert string names to objects
- Uses `@sameroom` decorator to ensure hero and object are in same room

**Event System (`src/delivery.py`)**
- Time-based event queue for scheduled events (`EventQueue` class)
- Handles deliveries from stores (grocery, hardware)
- Government check deliveries every 2 weeks
- Events fire when current time >= scheduled time

**I/O Interface (`src/io_interface.py`)**
- Abstraction layer for input/output operations
- `IOInterface` abstract base class with output(), get_input(), sleep() methods
- `ConsoleIO` for real gameplay, `MockIO` for testing
- Enables deterministic, fast testing without blocking I/O

**AlterEgo System (`src/alterego.py`)**
- Placeholder system that activates when player passes out (currently empty)
- Contains `AlterEgo` class with empty `run()` method for future implementation

### Key Game Mechanics

- **Feel System**: Player energy that decreases over time, causes passing out at 0, restored by eating
- **Money System**: Player has $100 starting balance, can order items by phone with costs deducted
- **Time System**: All actions advance time, some significantly (pondering, phone calls)
- **Inventory**: Weight-based system, hero can carry up to 100 weight units
- **Room Navigation**: Movement between apartment rooms with special closet mechanics
- **Store Orders**: Phone-based ordering system with delivery scheduling
- **Object Interaction**: `@sameroom` decorator ensures actions only work when player is in same room

### Special Features

- **Closet Nailing**: Player can nail themselves into the closet using hammer, nails, and plywood
- **Phone System**: Three numbers - grocery store (288-7955), hardware store (592-2874), and building super (198-2888)
- **TV News**: Shows astrophysics anomaly news when examined
- **Food System**: Different foods provide different feel boosts (spicy-food: 30, caffeine: 20, bananas: 5, ice-cubes: 2)
- **Hardware Items**: Hammer ($20), box-of-nails ($5), plywood-sheet ($30)

### State Management

The game uses a centralized `GameState` object that contains:
- `apartment`: The apartment container with all rooms and objects
- `hero`: Player character with stats and inventory
- `watch`: Time tracking object (Watch class)
- `event_queue`: Scheduled events system (EventQueue class)
- `alterEgo`: AlterEgo system (currently unused)
- `io`: IOInterface for all input/output operations

All game objects maintain parent-child relationships for location tracking, and the `@sameroom` decorator ensures actions only work when the player is in the same room as objects.

### Object Hierarchy Details

**Object Classes:**
- `Object`: Base class with name, weight, parent
- `Food`: Extends Object, has feelBoost property and Eat() method
- `Container`: Extends Object, has contents list and item lookup methods
- `Openable`: Extends Container, adds open/closed state with Open()/Close() methods
- `Room`: Extends Container, base class for game locations with Enter()/Leave() methods
- `Hero`: Extends Container, player character with feel, curr_balance, and Pickup() logic
- `Watch`: Extends Object, tracks current game time with GetDateAsString() method
- `Phone`: Extends Object, handles phone calls with list of PhoneNumber objects
- `TV`: Extends Object, displays news when examined

**Specialized Rooms:**
- `MainRoom`: Contains phone, toolbox, fridge, cabinet, table, tv
- `Closet`: Can be nailed shut, prevents leaving when CLOSET_NAILED state
- `Apartment`: Top-level container holding all rooms

**Phone System:**
- `PhoneNumber`: Base class for callable numbers
- `StoreNumber`: Abstract base for stores with ordering logic
- `GroceryNumber`: Grocery store with food items and next-day delivery
- `HardwareNumber`: Hardware store with tools and 2-day delivery
- `SuperNumber`: Building super who never answers

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
- `GameState(io: IOInterface = None)` - accepts optional IO interface, defaults to ConsoleIO
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

**Test Files**:
- `tests/test_gamestate.py`: Core game objects and state management
- `tests/test_actions.py`: Action functions and game mechanics
- `tests/test_apartment.py`: Room and apartment structure
- `tests/test_io_interface.py`: I/O interface implementations
- `tests/test_inputparser.py`: Command parsing system

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

## Available Game Commands

The game supports the following commands (defined in `src/inputparser.py`):

### Debug and Development
- `debug items` - Give player hammer, nails, and plywood for testing

### Phone System
- `call phone` - Make a phone call using the main room phone
- `rolodex` - Show available phone numbers

### Time and Status
- `look at watch` - Check current game time
- `ponder` - Waste time pondering (prompts for hours)
- `balance` - Check current money balance
- `feel` - Check current energy level

### Food and Eating
- `eat {food}` - Eat food from the opened fridge

### Object Interaction
- `examine {object}` - Examine an object in the room
- `watch {object}` - Watch something (specifically TV)
- `look in {object}` - Look inside a container
- `open {object}` - Open a container
- `close {object}` - Close a container

### Inventory Management
- `pick up {item} from {container}` - Get item from container
- `get {item} from {container}` - Alternative get command
- `inventory` - Show current inventory

### Movement
- `go in {room}` - Enter a room
- `go to {room}` - Go to a room
- `enter {room}` - Enter a room
- `enter the {room}` - Enter a room (with article)

### Special Actions
- `nail wood to exit` - Nail yourself into closet
- `nail wood to door` - Alternative nailing command
- `nail self in` - Alternative nailing command
- `nail self in closet` - Alternative nailing command
- `inspect room` - Look around current room
- `view room` - Alternative room inspection
- `look around room` - Alternative room inspection
- `mail check` - Mail a government check for money

## File Structure

```
ggj/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── pytest.ini            # Pytest configuration
├── README.md              # User documentation
├── CLAUDE.md              # This file
├── src/
│   ├── __init__.py
│   ├── gameloop.py        # Main game loop
│   ├── gamestate.py       # Core game objects and state
│   ├── actions.py         # Action functions
│   ├── inputparser.py     # Command parsing
│   ├── io_interface.py    # I/O abstraction
│   ├── delivery.py        # Event queue system
│   └── alterego.py        # Placeholder system
├── tests/
│   ├── __init__.py
│   ├── test_gamestate.py   # Game state tests
│   ├── test_actions.py     # Action function tests
│   ├── test_apartment.py   # Room and apartment tests
│   ├── test_io_interface.py # I/O interface tests
│   └── test_inputparser.py # Command parsing tests
└── tools/
    ├── __init__.py
    ├── filecheck.py        # FileCheck-like testing tool
    ├── run_e2e_tests.py    # End-to-end test runner
    ├── test_basic.txt      # Basic functionality test
    └── test_phone_call.txt # Phone system test
```

## Coding Style

This project adheres to PEP-8 guidelines and requires type hints.

### Style Guidelines
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all classes and methods
- Follow PEP-8 naming conventions (snake_case for functions/variables, PascalCase for classes)
- Keep line length under 100 characters
- Use descriptive variable and function names

### Code Quality
- All new code must have corresponding tests
- Use the MockIO interface for testing interactive features
- Separate business logic from I/O operations
- Follow the existing object hierarchy patterns