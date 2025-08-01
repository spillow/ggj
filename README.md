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
- **Movement**: `go to [room]`, `enter [room]`
- **Inventory**: `inventory`, `get [item] from [container]`
- **Interaction**: `examine [object]`, `open/close [container]`
- **Phone**: `call phone`, `rolodex` (to see numbers)
- **Food**: `eat [food]` (from opened fridge)
- **Time**: `look at watch`, `ponder` (waste time)
- **Status**: `balance` (money), `feel` (energy)
- **Special**: `nail self in` (in closet with required items)

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
- **I/O Abstraction**: `IOInterface` allows both console and mock implementations
- **Event System**: Time-based delivery and event scheduling

### Testing
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_gamestate.py

# Run specific test
python -m pytest tests/test_gamestate.py::TestHero::test_pickup_success
```

The test suite covers:
- Game object functionality (Hero, Container, Food, etc.)
- Game mechanics (pickup, inventory, room navigation)
- I/O operations using mock interfaces
- State management and time progression

### Code Style
- Follows PEP-8 guidelines
- Type hints throughout codebase
- Comprehensive docstrings for all classes and methods

## Game Mechanics

### Stats
- **Feel (Energy)**: Starts at 50, decreases over time. Eating food restores it. Player passes out at 0.
- **Balance (Money)**: Starts at $100. Spend on phone orders, earn from government checks.

### Shopping
- **Grocery Store (288-7955)**: Food items ($2-$10)
- **Hardware Store (592-2874)**: Tools ($5-$30)
- **Building Super (198-2888)**: Never answers, wastes time and energy

### Time System
Actions consume different amounts of time:
- Most actions: Minimal time
- Pondering: Variable hours (user choice)
- Phone calls: 2-30 minutes depending on store
- Eating: 20 minutes

## Contributing

This is a preserved Global Game Jam 2015 project. The codebase demonstrates clean architecture patterns for text adventure games and serves as an educational example of:
- Test-driven development
- I/O abstraction for testability
- Object-oriented game design
- Event-driven programming

## License

Created for Global Game Jam 2015. See game jam page for original context and rules.