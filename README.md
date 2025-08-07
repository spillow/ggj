# Global Game Jam 2015 - Text Adventure Game

A text-based adventure game created for Global Game Jam 2015. This is a psychological thriller about a character who believes he has mobility issues confining him to his apartment. The goal is to figure out what is happening and prevent an unrecoverable event.

**Game Jam Page:** http://globalgamejam.org/2015/games/leggo-my-ego

## Features

- **Rich Text Adventure Mechanics**: Navigate rooms, interact with objects, manage inventory
- **Command Pattern Architecture**: Undo/redo functionality, action replay, macro commands, and AI agent support
- **Time System**: All actions advance the in-game clock (starting March 15, 1982 at 3:14 AM)
- **Feel/Energy System**: Player energy decreases over time; eating food restores it
- **Money Management**: Start with $100, order items by phone with delivery scheduling
- **Phone System**: Call three numbers - grocery store, hardware store, and building super
- **Event Queue**: Scheduled deliveries and government checks every 2 weeks
- **Special Mechanics**: Nail yourself into the closet using hammer, nails, and plywood
- **Comprehensive Testing**: 177+ unit tests + 11 end-to-end tests covering all game mechanics
- **Modern Architecture**: Modular design with clean separation of concerns and dependency injection

## Installation

### Requirements
- Python 3.13+ (supports latest Python features)
- pytest (for running tests)
- pytest-cov (for coverage analysis)

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

## Architecture

### Modern Python 3.13 Design
The codebase leverages modern Python 3.13+ features and follows contemporary best practices:

- **Command Pattern Implementation**: Full undo/redo support with command queuing and macro functionality
- **Modular Architecture**: Clean separation between core game logic, actions, commands, and presentation
- **Type Safety**: Comprehensive type hints using latest Python typing features
- **Dependency Injection**: Testable design with IOInterface abstraction
- **Modern Python Syntax**: Uses Python 3.13+ syntax including enhanced type unions and pattern matching

### Core Components

#### Command System (`src/commands/`)
- **BaseCommand**: Abstract command interface with execute/undo capabilities
- **CommandInvoker**: Manages command execution, queuing, and batch operations
- **CommandHistory**: Full undo/redo functionality with history management
- **MacroCommands**: Pre-built and custom macro sequences
- **Game Commands**: 15+ concrete command implementations for all game actions

#### Core Game Logic (`src/core/`)
- **GameWorld**: Central game state management
- **Characters**: Hero class with inventory and stats
- **Rooms**: Apartment layout and room hierarchy
- **Items**: Specialized objects (Food, Phone, TV, Watch)
- **Game Objects**: Base object and container classes
- **Time System**: Game time tracking and advancement

#### Business Logic (`src/logic/`)
- **Inventory Logic**: Item pickup rules and weight limits
- **Movement Logic**: Room transition validation
- **Interaction Logic**: Object interaction rules
- **Stats Logic**: Feel/balance calculations
- **Time Logic**: Time advancement mechanics

#### Actions (`src/game_actions/`)
- **Movement Actions**: Room navigation and special room mechanics
- **Inventory Actions**: Object pickup, examination, container operations
- **Interaction Actions**: Phone calls, eating, TV watching
- **Utility Actions**: Debug commands, status checks
- **Action Decorators**: Reusable decorators for validation

### Object Hierarchy
- **Object**: Base class with name, weight, parent relationships
- **Container**: Objects that hold other objects
- **Openable**: Containers with open/closed state
- **Room**: Game locations with special behavior
- **Hero**: Player character with inventory and stats
- **Specialized Items**: Food, Phone, TV, Watch with unique interactions

## Development

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

# Run command pattern tests
python -m pytest tests/test_command_pattern.py
```

The codebase has **177+ unit tests** covering:
- **Game Object Functionality**: Hero, Container, Food, Watch, Phone, etc.
- **Command Pattern**: All command implementations, invokers, history, and macros
- **Game Mechanics**: Pickup, inventory, room navigation, eating, time progression
- **I/O Operations**: Mock interfaces for deterministic testing
- **State Management**: Game state initialization and progression
- **Command Parsing**: All supported commands and edge cases
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

The project includes **11 end-to-end tests** using a FileCheck-like testing tool:
- **Test File Format**: Similar to LLVM's FileCheck with `# CHECK:` and `# CHECK-NEXT:` directives
- **Input Simulation**: Lines starting with `>` represent player input
- **Output Validation**: Whitespace-insensitive pattern matching against game output
- **Comprehensive Coverage**: Tests for all major game mechanics and interactions

**Test File Example:**
```
# CHECK: What do we do next?:
> call phone
# CHECK: What number?:
> 288-7955
# CHECK: Hello this is the grocery store
```

#### Code Coverage
```bash
# Basic coverage report
python -m pytest --cov=src --cov-report=term-missing

# Coverage with branch analysis (recommended)
python -m pytest --cov=src --cov-report=term-missing --cov-branch

# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html --cov-branch

# Combined coverage: unit tests + e2e tests (recommended)
coverage erase && coverage run -m pytest && coverage run -a tools/run_e2e_tests.py && coverage report --show-missing
```

**Current Coverage**: 91% statement coverage with combined unit and e2e tests

### Code Style

#### Modern Python 3.13 Guidelines
- **Type Hints**: Comprehensive type annotations using latest Python typing features
- **PEP-8 Compliance**: Clean, readable code following Python style guidelines
- **Modern Syntax**: Leverages Python 3.13+ features like enhanced type unions
- **Dependency Injection**: Testable design with interface abstractions
- **Comprehensive Documentation**: Detailed docstrings for all classes and methods
- **Test-Driven Development**: MockIO interfaces for fast, deterministic testing

#### Architecture Patterns
- **Command Pattern**: Undo/redo, action replay, macro support, AI compatibility
- **Observer Pattern**: Event-driven architecture (in progress)
- **Factory Pattern**: Planned for data-driven object creation
- **Strategy Pattern**: Planned for pluggable behaviors
- **Clean Architecture**: Clear separation between business logic and presentation

## Game Mechanics

### Stats
- **Feel (Energy)**: Starts at 50, decreases over time. Eating food restores it. Player passes out at 0.
- **Balance (Money)**: Starts at $100. Spend on phone orders, earn from government checks.

### Shopping
- **Grocery Store (288-7955)**: Food items with different feel boosts
  - spicy-food: +30 feel ($10)
  - caffeine: +20 feel ($5)
  - bananas: +5 feel ($2)
  - ice-cubes: +2 feel ($6)
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

### Command System Features
- **Undo/Redo**: Most actions can be undone (where logically possible)
- **Action Replay**: Commands can be recorded and replayed for debugging
- **Macro Commands**: Complex action sequences can be combined into single commands
- **Command Queuing**: Commands can be queued and executed in batches
- **AI Compatibility**: AI agents can use the same command objects as human players

## Recent Updates

### Major Features Added
- **Command Pattern Architecture**: Complete implementation with undo/redo, macros, and AI support
- **Enhanced Testing**: Added 29 comprehensive command pattern tests
- **Modular Refactoring**: Separated concerns into logical modules (core, logic, actions, commands)
- **Python 3.13 Compatibility**: Updated for latest Python features and best practices

### Bug Fixes
- **Nail Consumption Fix**: Fixed unrealistic behavior where nailing yourself into the closet only consumed plywood but not the box-of-nails. Now both materials are properly consumed when nailing.

## Contributing

This is a preserved Global Game Jam 2015 project that has been modernized and refactored. The codebase demonstrates clean architecture patterns for text adventure games and serves as an educational example of:

- **Modern Python 3.13 Development**: Latest language features and best practices
- **Command Pattern Implementation**: Full-featured command system with undo/redo
- **Test-Driven Development**: Comprehensive testing with mock interfaces
- **Clean Architecture**: Modular design with clear separation of concerns
- **Design Pattern Usage**: Real-world examples of common software patterns
- **Game Engine Architecture**: Text adventure game engine design principles

## File Structure

```
ggj/
├── main.py                     # Entry point
├── requirements.txt            # Python 3.13+ dependencies
├── pytest.ini                # Pytest configuration
├── README.md                  # This file
├── CLAUDE.md                  # Developer documentation
├── REFACTOR.md               # Architectural refactoring plan
├── src/
│   ├── commands/             # Command Pattern implementation
│   │   ├── base_command.py   # Abstract command interface
│   │   ├── game_commands.py  # Concrete command implementations
│   │   ├── command_invoker.py # Command execution management
│   │   ├── command_history.py # Undo/redo functionality
│   │   └── macro_commands.py # Macro and batch commands
│   ├── core/                 # Core game logic
│   │   ├── game_world.py     # Central game state
│   │   ├── characters.py     # Hero and character classes
│   │   ├── rooms.py          # Room hierarchy and apartment
│   │   ├── items.py          # Specialized items and objects
│   │   ├── game_objects.py   # Base object and container classes
│   │   └── time_system.py    # Time tracking and advancement
│   ├── logic/                # Business logic
│   │   ├── inventory_logic.py # Item management rules
│   │   ├── movement_logic.py  # Room transition logic
│   │   ├── interaction_logic.py # Object interaction rules
│   │   ├── stats_logic.py     # Feel/balance calculations
│   │   └── time_logic.py      # Time advancement mechanics
│   ├── game_actions/         # Action implementations
│   │   ├── movement_actions.py    # Room navigation
│   │   ├── inventory_actions.py   # Item management
│   │   ├── interaction_actions.py # Object interactions
│   │   ├── utility_actions.py     # Debug and utility commands
│   │   └── action_decorators.py   # Reusable decorators
│   ├── gamestate.py          # Legacy game state (compatibility)
│   ├── actions.py            # Legacy actions (compatibility)
│   ├── gameloop.py           # Main game loop
│   ├── inputparser.py        # Command parsing
│   ├── io_interface.py       # I/O abstraction
│   ├── delivery.py           # Event system
│   └── alterego.py           # AlterEgo system (placeholder)
├── tests/
│   ├── test_command_pattern.py # Command pattern tests (29 tests)
│   ├── test_gamestate.py       # Game state tests
│   ├── test_actions.py         # Action function tests
│   ├── test_apartment.py       # Room and apartment tests
│   ├── test_io_interface.py    # I/O interface tests
│   ├── test_inputparser.py     # Command parsing tests
│   ├── test_delivery.py        # Event system tests
│   ├── test_gameloop.py        # Game loop tests
│   └── test_alterego.py        # AlterEgo tests
└── tools/
    ├── filecheck.py            # FileCheck-like testing tool
    ├── run_e2e_tests.py        # End-to-end test runner
    └── test_*.txt              # 11 end-to-end test files
```

## License

Created for Global Game Jam 2015. See game jam page for original context and rules.