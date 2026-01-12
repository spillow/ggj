# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management. Dependencies are defined in `pyproject.toml`.

### Setup

```bash
# Install uv (if not already installed)
# On Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates venv and installs packages)
uv sync

# Install optional development tools
uv sync --extra dev
```

### Running the Game
```bash
# Using uv (recommended)
uv run python main.py

# Or activate venv and run directly
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # macOS/Linux
python main.py
```

### Testing

#### Unit Testing
```bash
# Run all unit tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_gamestate.py

# Run specific test
uv run pytest tests/test_gamestate.py::TestHero::test_pickup_success

# Run Command Pattern tests
uv run pytest tests/test_command_pattern.py

# Run tests with pattern matching
uv run pytest -k "command" -v
```

The codebase uses pytest for automated testing with a comprehensive test suite covering:
- Game object functionality (Hero, Container, Food, etc.)
- Game mechanics (pickup, inventory, room navigation)
- I/O operations using mock interfaces
- State management and time progression
- **Command Pattern implementation** (commands, invokers, history, macros)

**Current Test Count**: 177+ unit tests covering all aspects of the game, including 29 Command Pattern tests

#### End-to-End Testing
```bash
# Run all end-to-end tests
uv run python tools/run_e2e_tests.py

# Run specific FileCheck test
uv run python tools/filecheck.py tools/test_basic.txt --verbose
```

The project includes a **FileCheck-like tool** (`tools/filecheck.py`) for end-to-end testing:
- **Test Format**: Similar to LLVM's FileCheck tool
- **Directives**: 
  - `# CHECK: pattern` - Find pattern anywhere in remaining output
  - `# CHECK-NEXT: pattern` - Find pattern in the very next output line
- **Input Simulation**: Lines starting with `>` represent player input
- **Output Validation**: Whitespace-insensitive pattern matching
- **Test Files**: Located in `tools/` directory with `.txt` extension

**Current E2E Tests**: 27 comprehensive test files including:
- `test_basic.txt` - Basic game functionality
- `test_comprehensive_start.txt` - Game startup and initial state
- `test_fridge_food.txt` - Food system and eating mechanics
- `test_government_check.txt` - Government check mailing system
- `test_inventory_management.txt` - Inventory and pickup mechanics
- `test_nail_consumption_fixed.txt` - Nail consumption bug fix verification
- `test_object_examine.txt` - Base Object.Examine() method functionality
- `test_phone_call.txt` - Phone system interactions
- `test_room_navigation.txt` - Room movement and navigation
- `test_time_pondering.txt` - Time progression system
- `test_toolbox_exploration.txt` - Container exploration mechanics
- `test_tv_news.txt` - TV interaction and news display
- `test_ice_bath.txt` - Ice bath command parsing and error handling
- `test_ice_bath_success.txt` - Complete ice bath workflow testing

#### Code Coverage

The project uses `pytest-cov` (a wrapper around coverage.py) for test coverage analysis. **Run coverage analysis on every code change to determine if new tests are needed.**

```bash
# Basic coverage report (terminal output with missing lines)
uv run pytest --cov=src --cov-report=term-missing

# Coverage with branch analysis (recommended)
uv run pytest --cov=src --cov-report=term-missing --cov-branch

# Generate HTML coverage report for detailed analysis
uv run pytest --cov=src --cov-report=html --cov-branch

# Set coverage threshold (fail if below 80%)
uv run pytest --cov=src --cov-fail-under=80 --cov-branch

# Coverage from end-to-end tests only
uv run coverage run tools/run_e2e_tests.py
uv run coverage report --show-missing

# Combined coverage: unit tests + e2e tests
uv run coverage run -m pytest
uv run coverage run -a tools/run_e2e_tests.py
uv run coverage report --show-missing
uv run coverage html

# Run all tests with combined coverage (recommended)
uv run coverage erase && uv run coverage run -m pytest && uv run coverage run -a tools/run_e2e_tests.py && uv run coverage report --show-missing
```

**Coverage Analysis:**
- **Unit Tests Only**: 73% statement coverage 
- **Combined (Unit + E2E)**: 91% statement coverage ⭐

**Module Breakdown (Combined Coverage):**
- **🟢 Excellent (100%)**: `inputparser.py` - command parsing fully tested
- **🟢 Excellent (95%)**: `actions.py` - game actions comprehensively covered
- **🟢 Good (93%)**: `delivery.py` - event system well tested by e2e
- **🟢 Good (87%)**: `io_interface.py` - I/O abstractions mostly covered  
- **🟢 Good (80%)**: `gamestate.py` - core game objects well exercised
- **🟢 Good (77%)**: `gameloop.py` - main game loop tested via e2e
- **🟠 Fair (80%)**: `alterego.py` - placeholder system (1 line missing)

**Key Insight**: E2E tests dramatically improve coverage by exercising the full game loop and real user interactions that unit tests miss.

**HTML Report**: After running with `--cov-report=html`, view detailed coverage at `htmlcov/index.html`

## Code Architecture

This is a text-based adventure game written in Python for Global Game Jam 2015. The game simulates a psychological scenario where the player controls a character who believes he has mobility issues confining him to his apartment.

### Core Architecture

**Modern Python 3.13+ Design**
- **Command Pattern Implementation**: Complete undo/redo system with macro support and AI compatibility
- **Modular Architecture**: Clean separation of concerns across logical modules
- **Type Safety**: Comprehensive type hints using latest Python typing features
- **Dependency Injection**: Testable design with IOInterface abstraction
- **Contemporary Best Practices**: Leverages Python 3.13+ features and modern development patterns

**Main Entry Point (`main.py`)**
- Simple entry point that imports and runs the game loop
- No command-line arguments or configuration

**Game Loop (`src/gameloop.py`)**
- Main game loop that initializes the game state and processes user input
- Handles the event queue for scheduled deliveries (government checks every 2 weeks)
- Coordinates between input parsing, action execution, and state examination
- Supports dependency injection with optional `IOInterface` parameter for testing

### Command Pattern Architecture (`src/commands/`)

**Base Command Interface (`base_command.py`)**
- `BaseCommand`: Abstract base class for all game commands with execute/undo capabilities
- `CommandResult`: Encapsulates command execution results with success status and metadata
- `MacroCommand`: Combines multiple commands into single executable units

**Concrete Commands (`game_commands.py`)**
- **Movement Commands**: `EnterRoomCommand`, `NailSelfInCommand`, `InspectRoomCommand`
- **Inventory Commands**: `ExamineThingCommand`, `OpenThingCommand`, `CloseThingCommand`, `GetObjectCommand`, `InventoryCommand`
- **Interaction Commands**: `CallPhoneCommand`, `EatThingCommand`, `WatchTvCommand`, `MailCheckCommand`, `RolodexCommand`
- **Utility Commands**: `CheckBalanceCommand`, `CheckFeelCommand`, `LookAtWatchCommand`, `PonderCommand`, `DebugItemsCommand`

**Command Management (`command_invoker.py`)**
- `CommandInvoker`: Manages command execution, queuing, and batch operations
- `BatchCommandInvoker`: Atomic command execution with rollback capabilities
- Command queuing and sequence execution with failure handling

**History Management (`command_history.py`)**
- `CommandHistory`: Full undo/redo functionality with configurable history limits
- `UndoCommand` and `RedoCommand`: Meta-commands for undo/redo operations
- History checkpoints and state management

**Macro System (`macro_commands.py`)**
- Pre-built macros: `ExploreRoomMacro`, `GatherToolsMacro`, `StatusCheckMacro`
- `MacroBuilder`: Fluent interface for creating custom macro sequences
- Factory functions for common macro patterns

### Core Game Logic (`src/core/`)

**Game State (`game_world.py`)**
- Contains the complete object model with inheritance hierarchy:
  - `Object` (base class for all game items with name, weight, parent container)
  - `Container` (objects that hold other objects with contents list)
  - `Openable` (containers that can be opened/closed with state tracking)
  - `Room` (game locations with Enter/Leave logic)
  - `Hero` (player character with inventory, feel/balance stats, and pickup logic)
- Manages the apartment layout with rooms: main, bedroom, bathroom, closet
- Implements time system using Python's datetime (starting March 15, 1982 at 3:14 AM)
- Tracks player stats: feel (energy starting at 50), balance (money starting at $100)

**Character System (`characters.py`)**
- `Hero` class with inventory management, stats tracking, and pickup logic
- Weight-based inventory system (100 weight unit limit)
- Feel and balance stat management with state effects

**Room System (`rooms.py`)**
- `Room` base class with enter/leave mechanics
- Specialized rooms: `MainRoom`, `Bedroom`, `Bathroom`, `Closet`
- `Apartment` container managing all room relationships
- Special mechanics like closet nailing states

**Item System (`items.py`)**
- `Food` class with feel boost mechanics and eating interactions
- `Phone` system with multiple callable numbers
- `TV` class with news display functionality
- `Watch` class for time tracking and display

**Object Foundation (`game_objects.py`)**
- Base `Object` class with weight, name, and parent relationships
- `Container` class for objects that hold other objects
- `Openable` class for containers with open/closed states
- `@sameroom` decorator ensuring location-based interactions

**Time System (`time_system.py`)**
- `Watch` class for game time tracking
- Time advancement mechanics for different actions
- Integration with event scheduling system

### Business Logic Layer (`src/logic/`)

**Inventory Logic (`inventory_logic.py`)**
- Item pickup validation and weight limit enforcement
- Container interaction rules and item management
- Inventory state calculations

**Movement Logic (`movement_logic.py`)**
- Room transition validation and pathfinding
- Location-based interaction requirements
- Movement state management

**Interaction Logic (`interaction_logic.py`)**
- Object interaction rules and validation
- Same-room requirement enforcement
- Interaction state tracking

**Stats Logic (`stats_logic.py`)**
- Feel (energy) and balance (money) calculations
- State effect processing and validation
- Stat-based action availability

**Time Logic (`time_logic.py`)**
- Time advancement calculations for different actions
- Event scheduling and timing mechanics
- Time-based state changes

### Action Layer (`src/game_actions/`)

**Movement Actions (`movement_actions.py`)**
- Room navigation functions: `enter_room`, `inspect_room`
- Special actions: `nail_self_in` (with proper resource consumption)
- Room-specific behavior and validation

**Inventory Actions (`inventory_actions.py`)**
- Item management: `examine_thing`, `get_object`, `inventory`
- Container operations: `open_thing`, `close_thing`
- Inventory display and validation

**Interaction Actions (`interaction_actions.py`)**
- Phone system: `call_phone`, `rolodex`
- Food system: `eat_thing`
- Entertainment: `watch_tv`
- Financial: `mail_check`

**Utility Actions (`utility_actions.py`)**
- Status commands: `check_balance`, `check_feel`, `look_at_watch`
- Time manipulation: `ponder`
- Debug functionality: `debug_items`

**Action Decorators (`action_decorators.py`)**
- `@attempt`: Exception handling wrapper for actions
- `@thingify`: String-to-object conversion decorator
- `@sameroom`: Location validation decorator (in game_objects.py)

### Input System (`src/inputparser.py`)
- Pattern-based command parser using string templates with variables like `{a}` and `{b}`
- Maps natural language commands to action functions via COMMANDS dictionary
- Supports commands like "get {item} from {container}", "go to {room}", etc.
- Returns tuple of (success, action/error_message, args)

### Event System (`src/delivery.py`)
- Time-based event queue for scheduled events (`EventQueue` class)
- Handles deliveries from stores (grocery, hardware)
- Government check deliveries every 2 weeks
- Events fire when current time >= scheduled time

### I/O Interface (`src/io_interface.py`)
- Abstraction layer for input/output operations
- `IOInterface` abstract base class with output(), get_input(), sleep() methods
- `ConsoleIO` for real gameplay, `MockIO` for testing
- Enables deterministic, fast testing without blocking I/O

### Legacy Compatibility

**Legacy Game State (`src/gamestate.py`)**
- Original monolithic game state implementation
- Maintained for backward compatibility
- Being gradually phased out in favor of modular core system

**Legacy Actions (`src/actions.py`)**
- Re-exports from modular action system
- Maintains backward compatibility with existing code
- Bridge between old and new architecture

### Key Game Mechanics

- **Feel System**: Player energy that decreases over time, causes passing out at 0, restored by eating or ice baths
- **Money System**: Player has $100 starting balance, can order items by phone with costs deducted
- **Time System**: All actions advance time, some significantly (pondering, phone calls, ice baths)
- **Inventory**: Weight-based system, hero can carry up to 100 weight units
- **Room Navigation**: Movement between apartment rooms with special closet and bathroom mechanics
- **Store Orders**: Phone-based ordering system with delivery scheduling
- **Object Interaction**: `@sameroom` decorator ensures actions only work when player is in same room
- **Command Pattern Features**:
  - **Undo/Redo**: Most actions can be reversed (where logically possible)
  - **Action Replay**: Commands can be recorded and replayed for debugging
  - **Macro Commands**: Complex sequences can be combined into single commands
  - **Command Queuing**: Commands can be queued and executed in batches
  - **AI Compatibility**: AI agents can use same command objects as humans

### Special Features

- **Closet Nailing**: Player can nail themselves into the closet using hammer, nails, and plywood (both nails and plywood are consumed)
- **Ice Bath**: Player can take an ice bath in the bathroom using ice cubes (+40 feel boost, +1 hour time, consumes ice cubes)
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
- **Command Pattern Tests**: Complete command system testing
- **End-to-End Tests**: Full game flow testing with FileCheck-like tool

**Test Files**:
- `tests/test_gamestate.py`: Core game objects and state management
- `tests/test_actions.py`: Action functions and game mechanics
- `tests/test_apartment.py`: Room and apartment structure
- `tests/test_io_interface.py`: I/O interface implementations
- `tests/test_inputparser.py`: Command parsing system
- `tests/test_delivery.py`: Event queue system
- `tests/test_gameloop.py`: Main game loop functionality
- `tests/test_alterego.py`: AlterEgo system (placeholder)
- **`tests/test_command_pattern.py`: Command pattern implementation (29 tests)**

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
6. **Add E2E Tests**: Create FileCheck tests for new gameplay features
7. **Use Command Pattern**: Convert actions to Command objects for undo/redo support
8. **Modern Python 3.13+**: Use latest Python features and type hints

**Command Pattern Example**:
```python
# Good: Command-based design
class NewActionCommand(BaseCommand):
    def __init__(self, parameter: str):
        super().__init__(f"New action: {parameter}")
        self.parameter = parameter

    def execute(self, game_state: GameState) -> CommandResult:
        # Pure business logic
        result = self._process_action(game_state, self.parameter)
        self.mark_executed()
        return CommandResult(
            success=True,
            message=f"Action completed: {result}"
        )

    def can_undo(self) -> bool:
        return True

    def undo(self, game_state: GameState) -> CommandResult:
        # Reverse the action
        self._reverse_action(game_state, self.parameter)
        return CommandResult(success=True, message="Action undone")
```

This architecture ensures all new code is testable, maintainable, follows separation of concerns, and supports advanced features like undo/redo.

## Available Game Commands

The game supports the following commands (defined in `src/inputparser.py`):

### Debug and Development
- `debug items` - Give player hammer, nails, plywood, and ice cubes for testing

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

### Bathroom Actions
- `take an ice bath` - Take an ice bath in the bathroom (requires ice cubes)
- `take ice bath` - Alternative ice bath command
- `ice bath` - Shorter ice bath command

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
├── pyproject.toml          # Project metadata and dependencies (uv)
├── pytest.ini              # Pytest configuration
├── README.md               # User documentation
├── CLAUDE.md               # This file
├── REFACTOR.md             # Architectural refactoring plan
├── src/
│   ├── commands/          # Command Pattern implementation
│   │   ├── __init__.py
│   │   ├── base_command.py        # Abstract command interface
│   │   ├── game_commands.py       # Concrete command implementations
│   │   ├── command_invoker.py     # Command execution management
│   │   ├── command_history.py     # Undo/redo functionality
│   │   └── macro_commands.py      # Macro and batch commands
│   ├── core/              # Core game logic
│   │   ├── __init__.py
│   │   ├── game_world.py         # Central game state
│   │   ├── characters.py         # Hero and character classes
│   │   ├── rooms.py              # Room hierarchy and apartment
│   │   ├── items.py              # Specialized items and objects
│   │   ├── game_objects.py       # Base object and container classes
│   │   └── time_system.py        # Time tracking and advancement
│   ├── logic/             # Business logic
│   │   ├── __init__.py
│   │   ├── inventory_logic.py    # Item management rules
│   │   ├── movement_logic.py     # Room transition logic
│   │   ├── interaction_logic.py  # Object interaction rules
│   │   ├── stats_logic.py        # Feel/balance calculations
│   │   └── time_logic.py         # Time advancement mechanics
│   ├── game_actions/      # Action implementations
│   │   ├── __init__.py
│   │   ├── movement_actions.py   # Room navigation
│   │   ├── inventory_actions.py  # Item management
│   │   ├── interaction_actions.py # Object interactions
│   │   ├── utility_actions.py    # Debug and utility commands
│   │   └── action_decorators.py  # Reusable decorators
│   ├── gamestate.py       # Legacy game state (compatibility)
│   ├── actions.py         # Legacy actions (compatibility)
│   ├── gameloop.py        # Main game loop
│   ├── inputparser.py     # Command parsing
│   ├── io_interface.py    # I/O abstraction
│   ├── delivery.py        # Event system
│   └── alterego.py        # AlterEgo system (placeholder)
├── tests/
│   ├── __init__.py
│   ├── test_command_pattern.py   # Command pattern tests (29 tests)
│   ├── test_gamestate.py         # Game state tests
│   ├── test_actions.py           # Action function tests
│   ├── test_apartment.py         # Room and apartment tests
│   ├── test_io_interface.py      # I/O interface tests
│   ├── test_inputparser.py       # Command parsing tests
│   ├── test_delivery.py          # Event system tests
│   ├── test_gameloop.py          # Game loop tests
│   └── test_alterego.py          # AlterEgo tests
└── tools/
    ├── __init__.py
    ├── filecheck.py              # FileCheck-like testing tool
    ├── run_e2e_tests.py          # End-to-end test runner
    ├── test_basic.txt            # Basic functionality test
    ├── test_comprehensive_start.txt # Game startup test
    ├── test_fridge_food.txt      # Food system test
    ├── test_government_check.txt # Government check test
    ├── test_inventory_management.txt # Inventory test
    ├── test_nail_consumption_fixed.txt # Nail bug fix test
    ├── test_phone_call.txt       # Phone system test
    ├── test_room_navigation.txt  # Room movement test
    ├── test_time_pondering.txt   # Time system test
    ├── test_toolbox_exploration.txt # Container test
    └── test_tv_news.txt          # TV interaction test
```

## Coding Style

This project adheres to PEP-8 guidelines and requires type hints, with emphasis on Python 3.13+ features.

### Style Guidelines
- **Python 3.13+ Features**: Use modern Python syntax and typing features
- **Type Hints**: Comprehensive type annotations for all function parameters and return values
- **Documentation**: Include comprehensive docstrings for all classes and methods
- **Naming Conventions**: Follow PEP-8 naming conventions (snake_case for functions/variables, PascalCase for classes)
- **Line Length**: Keep under 100 characters
- **Descriptive Names**: Use descriptive variable and function names

### Code Quality
- **Test Coverage**: All new code must have corresponding tests
- **Command Pattern**: Convert actions to Command objects for undo/redo support
- **MockIO Testing**: Use the MockIO interface for testing interactive features
- **Logic Separation**: Separate business logic from I/O operations
- **Design Patterns**: Follow existing architectural patterns (Command, Observer, Factory)

### Modern Python 3.13+ Practices
- **Enhanced Type Hints**: Use latest typing features and union syntax
- **Pattern Matching**: Utilize match/case statements where appropriate
- **Dataclasses**: Use dataclasses for data containers
- **Context Managers**: Use context managers for resource management
- **Async/Await**: Use async patterns where beneficial (future consideration)

## Recent Updates and Bug Fixes

### Major Architectural Changes
- **Command Pattern Implementation**: Complete command system with undo/redo, macros, and AI support
- **Modular Refactoring**: Separated monolithic code into logical modules (core, logic, actions, commands)
- **Enhanced Testing**: Added 29 comprehensive Command Pattern tests
- **Python 3.13 Modernization**: Updated codebase to use latest Python features and best practices

### Bug Fixes
- **Nail Consumption Fix**: Modified `nail_self_in` function in `src/actions.py:284` to consume both plywood and nails: `hero.Destroy([plywood, nails])`
- **Test Coverage**: Added `test_nail_consumption_fixed.txt` e2e test to verify the fix
- **Impact**: More realistic resource consumption mechanics

### Design Pattern Implementation Status
- ✅ **Command Pattern**: Complete with undo/redo, macros, queuing, and AI compatibility
- 🚧 **Observer Pattern**: Planned for event-driven architecture (Phase 0.5.2)
- 📋 **Factory Pattern**: Planned for data-driven object creation (Phase 0.5.4)
- 📋 **Strategy Pattern**: Planned for pluggable behaviors (Phase 0.5.5)
