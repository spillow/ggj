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

## Phase 1: MVC Foundation & Core Refactoring (Week 1-2)

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

### 1.3 View Layer Abstraction (Multiple Presentations)
**Create `src/views/` - presentation interfaces**:
- `view_interface.py` - Abstract view contract
- `console_view.py` - Current text-based interface
- `web_view.py` - Future web interface preparation
- `api_view.py` - REST API view for external clients
- `debug_view.py` - Developer debugging interface

**View Components**:
- `src/views/components/` - Reusable UI elements
  - `inventory_renderer.py` - Format inventory display
  - `room_renderer.py` - Format room descriptions/maps
  - `dialogue_renderer.py` - Format conversations
  - `status_renderer.py` - Hero stats, time, balance

### 1.4 Enhanced Input Processing
**Create `src/input/` - input abstraction**:
- `input_interface.py` - Abstract input contract
- `console_input.py` - Console input implementation
- `web_input.py` - Future web input handling
- `mock_input.py` - Testing input implementation

## Phase 2: Advanced Input & Content Management (Week 2-3)

### 2.1 Natural Language Processing with SpaCy
**Create `src/nlp/` - input understanding**:
- `nlp_processor.py` - Main SpaCy integration
- `intent_classifier.py` - Classify user intents
- `entity_extractor.py` - Extract objects, rooms, quantities
- `context_manager.py` - Handle pronoun references
- `command_builder.py` - Build Command objects from NLP results

**Integration**: NLP output feeds into Controller layer, never directly to Model.

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

## Phase 3: Web Interface & Persistence (Week 3-4)

### 3.1 Web Interface Implementation
**Create `src/web/` - web presentation layer**:
- `web_app.py` - Flask/FastAPI web application
- `websocket_handler.py` - Real-time game updates
- `rest_api.py` - RESTful game state API
- `web_renderer.py` - HTML/JSON response formatting

**Architecture**: Web layer only communicates with Controllers, never Model directly.

### 3.2 API-First Design
**Create `src/api/` - external interface layer**:
- `game_api.py` - Public API for game operations
- `serializers.py` - Convert model objects to JSON
- `validators.py` - Validate external input
- `authentication.py` - User session management

**Benefits**: Same API serves web interface, mobile apps, and future integrations.

### 3.3 Persistence Layer
**Create `src/persistence/` - data storage**:
- `save_manager.py` - Save/load game states
- `serializers.py` - Convert models to storage format
- `storage_backends.py` - File, database, cloud storage
- `migration_system.py` - Handle save format changes

**Separation**: Persistence layer only serializes Model objects, not views.

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
- **Web Browser**: Rich HTML interface with maps, images
- **Mobile App**: React Native app using REST API
- **Discord Bot**: Play via Discord commands
- **Voice Assistant**: Alexa/Google integration
- **VR Interface**: 3D room visualization

## Implementation Benefits

### Complete Interface Flexibility
- **Model layer** runs identically regardless of interface
- **Add new interfaces** without touching game logic
- **A/B test interfaces** with same underlying game
- **API-first** enables third-party integrations

### Testing Advantages
- **Model tests** don't require any I/O mocking
- **Controller tests** use mock views and inputs
- **View tests** only test rendering, not logic
- **Integration tests** verify layer communication

### Scalability Benefits
- **Web deployment**: Model + Controllers run server-side
- **Microservices**: Split into separate services by layer
- **Database integration**: Persistence layer handles all storage
- **Caching**: View layer can cache rendered output

## Example Architecture Flow

```
User Input (Web/Console/API)
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
1. **Week 1**: Extract pure Model layer from current code
2. **Week 1-2**: Implement Controller layer with Command pattern
3. **Week 2**: Create View abstraction, port console interface
4. **Week 2-3**: Add NLP and content management
5. **Week 3**: Implement basic web interface proof-of-concept
6. **Week 3-4**: Add persistence and API layer
7. **Week 4-5**: AI framework and developer tools

### Risk Mitigation
- **Facade patterns** maintain backward compatibility during transition
- **Progressive enhancement** - each layer can be developed independently
- **Interface contracts** prevent breaking changes between layers
- **Comprehensive testing** at each layer boundary

This MVC-based architecture enables unlimited presentation possibilities while maintaining clean, testable, maintainable code with complete separation of concerns.

---

## Notes

**Created**: 2025-08-07  
**Status**: Planning Phase  
**Next Steps**: Begin Phase 1 implementation  
**Reference**: See CLAUDE.md for current development commands and architecture