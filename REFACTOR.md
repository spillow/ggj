# Comprehensive Architectural Refactor Plan

## Architectural Philosophy: MVC + Clean Architecture

**Core Principle**: Complete separation of game logic, presentation, and input handling to enable multiple interfaces (console, web, mobile, VR, etc.)

### Architecture Layers
1. **Model Layer** - Pure game logic, no I/O dependencies
2. **Controller Layer** - Handles input, coordinates between model and view
3. **View Layer** - Presentation only, multiple implementations possible
4. **Infrastructure Layer** - Persistence, external services, frameworks

## Current Architecture Issues
- **Monolithic Design**: 894-line gamestate.py mixing logic and presentation
- **Tight I/O Coupling**: Game logic directly calls print() and input()
- **No Interface Abstraction**: Cannot swap out presentation layers
- **Limited Extensibility**: Hard to add new scenarios or AI behaviors
- **Command Pattern Missing**: No undo/macro/AI action queuing
- **Primitive Input**: Simple pattern matching instead of NLP

## Phase 0: Single Concern File Separation (Week 1)

### 0.1 Extract Core Game Objects from gamestate.py (894 lines)
**Create `src/core/` - fundamental game entities**:
- `game_objects.py` - Base Object, Container, Openable classes with core functionality
- `characters.py` - Hero class with inventory, stats, and interaction logic
- `rooms.py` - Room hierarchy (MainRoom, Bedroom, Bathroom, Closet) and Apartment structure
- `items.py` - Specialized objects (Food, Phone, TV, tools) with interaction methods
- `time_system.py` - Watch class and time management utilities
- `game_world.py` - GameState coordination and world state management

### 0.2 Separate Business Logic from Presentation
**Create `src/logic/` - pure game mechanics**:
- `inventory_logic.py` - Item pickup, weight limits, container operations
- `movement_logic.py` - Room transitions, navigation rules
- `interaction_logic.py` - Object interaction rules and validations
- `time_logic.py` - Time advancement, scheduling mechanics
- `stats_logic.py` - Feel/balance calculations, state effects

### 0.3 Extract Action System
**Create `src/game_actions/` - current action functions refined**:
- `movement_actions.py` - Room navigation functions from actions.py
- `inventory_actions.py` - Pickup, examine, inventory functions
- `interaction_actions.py` - Phone, eating, object manipulation
- `utility_actions.py` - Debug, status check, time functions
- `action_decorators.py` - @sameroom, @thingify decorators

**Goal**: Each file <200 lines, single responsibility, easier to understand and test.

## Phase 0.5: Design Pattern Implementation (Week 1-2)

### 0.5.1 Command Pattern for Actions
**Concrete Tasks**:
- Create `src/commands/base_command.py` - Abstract Command interface with execute()/undo()
- Convert all action functions to Command classes in `src/commands/game_commands.py`
- Implement `CommandInvoker` class to queue and execute commands
- Add `CommandHistory` for undo/redo functionality
- Enable macro commands for complex action sequences

**Benefits**: AI can use same commands, action replay, debugging, undo functionality

### 0.5.2 Observer Pattern for State Changes  
**Concrete Tasks**:
- Create `src/events/event_system.py` - Event dispatcher and listener registration
- Define game events (ItemPickedUp, RoomEntered, TimeAdvanced, StatChanged)
- Refactor objects to emit events instead of direct I/O calls
- Implement event handlers for presentation updates
- Replace direct IOInterface calls with event notifications

**Benefits**: Decoupled presentation, multiple views can respond to same events

### 0.5.3 State Pattern for Game States
**Concrete Tasks**:
- Create `src/states/game_state_machine.py` - State machine implementation
- Define states: MenuState, PlayingState, PausedState, GameOverState
- Implement HeroConditionStates: NormalState, UnconsciousState, etc.
- Add RoomStates: LockedState, UnlockedState for special room conditions
- Move state-specific logic into State classes

**Benefits**: Cleaner state transitions, easier to add new game modes

### 0.5.4 Factory Pattern for Object Creation
**Concrete Tasks**:
- Create `src/factories/object_factory.py` - Centralized object creation
- Define JSON/YAML configuration for all game objects
- Implement `ItemFactory`, `RoomFactory`, `CharacterFactory` classes
- Move hardcoded object creation from gamestate.py to configuration files
- Enable dynamic scenario loading from data files

**Benefits**: Data-driven content, easy scenario creation, modding support

### 0.5.5 Strategy Pattern for Behaviors
**Concrete Tasks**:
- Create `src/strategies/ai_behavior.py` - Pluggable AI strategies
- Implement different AI personalities: AggressiveAI, PassiveAI, RandomAI
- Create `src/strategies/input_processor.py` - Multiple input parsing strategies
- Add rendering strategies for different output formats
- Enable runtime strategy switching

**Benefits**: Flexible AI, customizable input handling, pluggable behaviors

### 0.5.6 Component System (Partial ECS)
**Concrete Tasks**:
- Create `src/components/` - Data components (HealthComponent, InventoryComponent)  
- Create `src/systems/` - Behavior systems (MovementSystem, InteractionSystem)
- Refactor Hero and Object classes to use component composition
- Implement ComponentManager for efficient component queries
- Separate data (components) from behavior (systems)

**Benefits**: Flexible object composition, easier complex interactions, better performance

## Phase 1: MVC Foundation & Core Refactoring (Week 2-3)

### 1.1 Pure Model Layer (Game Logic Only)
**Create `src/model/` - zero I/O dependencies**:
- `game_state.py` - Pure game state without any I/O
- `world_model.py` - Rooms, connections, spatial relationships
- `inventory_model.py` - Item management, weight, containers
- `character_model.py` - Hero stats, feel, balance, state
- `time_model.py` - Game time, scheduling, time advancement
- `rule_engine.py` - Game rules, constraints, validations

**Key principle**: Model layer never imports IOInterface or calls any I/O operations.

### 1.2 Controller Layer (Command Processing)
**Create `src/controllers/` - coordinates model updates**:
- `game_controller.py` - Main game flow controller
- `input_controller.py` - Process user commands into model updates
- `command_processor.py` - Execute commands using Command pattern
- `state_controller.py` - Manage game state transitions
- `ai_controller.py` - Handle AI/AlterEgo actions

**Command Pattern Implementation**:
- `src/commands/base_command.py` - Abstract command with execute/undo
- `src/commands/game_commands.py` - All actions as command objects
- `src/commands/command_history.py` - Undo/redo stack
- `src/commands/macro_commands.py` - Complex command sequences

### 1.3 View Layer Abstraction (Interface Flexibility)
**Create `src/views/` - presentation interfaces**:
- `view_interface.py` - Abstract view contract
- `console_view.py` - Current text-based interface  
- `gui_view.py` - Future graphical interface preparation
- `api_view.py` - Structured data view for external clients
- `debug_view.py` - Developer debugging interface

**View Components**:
- `src/views/components/` - Reusable presentation elements
  - `inventory_renderer.py` - Format inventory display
  - `room_renderer.py` - Format room descriptions
  - `dialogue_renderer.py` - Format conversations
  - `status_renderer.py` - Hero stats, time, balance

### 1.4 Enhanced Input Processing
**Create `src/input/` - input abstraction**:
- `input_interface.py` - Abstract input contract
- `console_input.py` - Console input implementation
- `gui_input.py` - Future graphical input handling
- `mock_input.py` - Testing input implementation

## Phase 2: Advanced Input & Content Management (Week 2-3)

### 2.1 Enhanced Input Processing
**Create `src/nlp/` - advanced input understanding**:
- `nlp_processor.py` - Natural language processing integration
- `intent_classifier.py` - Classify user intents
- `entity_extractor.py` - Extract objects, rooms, quantities
- `context_manager.py` - Handle pronoun references
- `command_builder.py` - Build Command objects from NLP results

**Integration**: Enhanced input feeds into Controller layer, maintaining separation from Model.

### 2.2 Content Management System
**Create `src/content/` - data-driven content**:
- `content_manager.py` - Load/manage all game content
- `item_definitions.py` - Item templates from JSON
- `room_definitions.py` - Room layouts from data files
- `scenario_loader.py` - Complete scenario definitions
- `dialogue_system.py` - All text/conversations from files

**Data separation**: All content in `data/` directory, loaded by Content layer.

### 2.3 Event System (Model-View Communication)
**Create `src/events/` - decoupled communication**:
- `event_bus.py` - Central event dispatcher
- `model_events.py` - Events emitted by model layer
- `view_events.py` - Events from view layer (user actions)
- `event_handlers.py` - Cross-layer event handling

**Flow**: View → Controller → Model → Events → View Updates


## Phase 4: AI Framework & Developer Tools (Week 4-5)

### 4.1 AI as Controller
**Enhanced `src/controllers/ai_controller.py`**:
- Uses same Command objects as human players
- Can analyze Model state to make decisions
- Pluggable personality/strategy systems
- No special access to internals

**AI Framework**:
- `src/ai/behavior_tree.py` - Decision-making trees
- `src/ai/goal_planner.py` - Action sequence planning
- `src/ai/learning_system.py` - Adapt to player behavior

### 4.2 Developer CLI Tools
**Create `cli/` - development utilities**:
- `dev_server.py` - Development web server
- `content_validator.py` - Validate JSON content files
- `scenario_generator.py` - Create new scenarios
- `api_tester.py` - Test API endpoints

**Click integration**: `ggj-dev serve --port 8000 --debug --scenario apartment`

### 4.3 Multiple Interface Support
**Interface Examples**:
- **Console**: Current text interface (maintained)
- **GUI Application**: Rich graphical interface with maps, images
- **Mobile App**: Native mobile app using API
- **Discord Bot**: Play via Discord commands
- **Voice Assistant**: Alexa/Google integration
- **VR Interface**: 3D room visualization

## Implementation Benefits

### Complete Interface Flexibility
- **Model layer** runs identically regardless of interface
- **Add new interfaces** (console, GUI, mobile, API) without touching game logic
- **Multiple simultaneous interfaces** with same underlying game
- **Clean architecture** enables future integrations

### Testing Advantages
- **Model tests** don't require any I/O mocking
- **Controller tests** use mock views and inputs
- **View tests** only test rendering, not logic
- **Integration tests** verify layer communication

### Scalability Benefits
- **Modular deployment**: Model + Controllers can run anywhere
- **Service separation**: Split into separate services by layer
- **Flexible storage**: Persistence layer handles file/database storage
- **Performance**: View layer can cache rendered output, component system optimizes updates

## Example Architecture Flow

```
User Input (Console/GUI/API/Mobile)
↓
Input Controller (parse, validate)
↓  
Command Processor (create Command objects)
↓
Model Layer (pure game logic)
↓
Event Bus (state change notifications)
↓
View Layer (render response)
↓
User sees result
```

### Implementation Strategy
1. **Week 1**: Phase 0 - Extract single concern files from monolithic gamestate.py
2. **Week 1-2**: Phase 0.5 - Implement design patterns (Command, Observer, State, Factory)
3. **Week 2-3**: Phase 1 - Extract pure Model layer and implement MVC foundation
4. **Week 3-4**: Phase 2 - Enhanced input processing and content management
5. **Week 4-5**: Advanced features - AI framework and developer tools

### Risk Mitigation
- **Facade patterns** maintain backward compatibility during transition
- **Progressive enhancement** - each layer can be developed independently
- **Interface contracts** prevent breaking changes between layers
- **Comprehensive testing** at each layer boundary

This MVC-based architecture with design patterns enables unlimited presentation possibilities while maintaining clean, testable, maintainable code with complete separation of concerns.

## Design Pattern Benefits

### Command Pattern Integration
- **AI Compatibility**: AI agents use same Command objects as human players
- **Action Replay**: Record and replay game sessions for debugging
- **Macro Support**: Complex action sequences for power users
- **Undo/Redo**: Full action history and reversal capability

### Observer Pattern Communication
- **Decoupled Views**: Multiple interfaces can respond to same game events
- **Event-Driven Architecture**: Clean separation between game logic and presentation
- **Extensible Notifications**: Easy to add new event types and handlers
- **Testing Benefits**: Mock event handlers for comprehensive testing

### Factory Pattern Flexibility
- **Data-Driven Content**: All game objects defined in configuration files
- **Scenario Generation**: Easy creation of new game scenarios
- **Modding Support**: External content creators can add new items/rooms
- **Dynamic Loading**: Runtime scenario switching and content updates

---

## Notes

**Created**: 2025-08-07  
**Status**: Planning Phase  
**Next Steps**: Begin Phase 1 implementation  
**Reference**: See CLAUDE.md for current development commands and architecture