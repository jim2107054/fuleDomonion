# System Architecture - Fuel Dominion

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER (Client)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │  index.html   │  │   scene.js     │  │    ui.js       │ │
│  │   (Layout)    │  │  (Three.js     │  │   (HUD/UI)     │ │
│  │               │  │   3D Render)   │  │                │ │
│  └───────────────┘  └────────────────┘  └────────────────┘ │
│           │                 │                    │           │
│           └─────────────────┴────────────────────┘           │
│                          │                                   │
│                   ┌──────▼───────┐                          │
│                   │   main.js    │                          │
│                   │ (Game Logic  │                          │
│                   │  & WebSocket)│                          │
│                   └──────┬───────┘                          │
└──────────────────────────┼──────────────────────────────────┘
                           │
                    WebSocket (ws://)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   BACKEND SERVER (Python)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                     main.py                             │ │
│  │  (FastAPI + WebSocket Server)                          │ │
│  │  - Handles client connections                          │ │
│  │  - Manages game loop                                   │ │
│  │  - Sends real-time updates                             │ │
│  └──────────┬───────────────────────────┬─────────────────┘ │
│             │                           │                    │
│    ┌────────▼────────┐       ┌─────────▼────────┐          │
│    │  game_state.py  │       │   scoring.py     │          │
│    │  - Grid/agents  │       │  - Evaluation    │          │
│    │  - Rules        │       │  - Score calc    │          │
│    │  - State mgmt   │       └──────────────────┘          │
│    └────────┬────────┘                                      │
│             │                                                │
│    ┌────────┴────────────────┐                             │
│    │                         │                             │
│ ┌──▼────────────┐  ┌────────▼──────────┐                 │
│ │ minimax_ai.py │  │   mcts_ai.py      │                 │
│ │ (Unit S)      │  │   (Unit I)        │                 │
│ │ - Alpha-Beta  │  │   - UCB1          │                 │
│ │ - Strategic   │  │   - Simulations   │                 │
│ └───────────────┘  └───────────────────┘                 │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │              config.py                              │   │
│  │  (Game parameters, AI settings, constants)         │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Game Initialization
```
User clicks START
    → WebSocket: {"command": "start"}
    → Backend: Initialize GameState
    → Backend: Create AI instances
    → WebSocket: {"type": "game_start", "data": {...}}
    → Frontend: Build 3D scene
    → Frontend: Show cinematic
```

### 2. Game Loop (Automatic)
```
Backend Game Loop:
    ┌──────────────────────────────────────┐
    │ 1. Check if game over               │
    │    - Max turns reached?              │
    │    - Victory condition?              │
    ├──────────────────────────────────────┤
    │ 2. Get current player (S or I)      │
    ├──────────────────────────────────────┤
    │ 3. AI Decision                       │
    │    - Minimax: search tree            │
    │    - MCTS: run simulations           │
    ├──────────────────────────────────────┤
    │ 4. Execute action                    │
    │    - Move / Refuel / Control node    │
    │    - Update game state               │
    ├──────────────────────────────────────┤
    │ 5. Update scores                     │
    ├──────────────────────────────────────┤
    │ 6. Send to frontend                  │
    │    WebSocket: action + state         │
    ├──────────────────────────────────────┤
    │ 7. Next turn (switch player)         │
    ├──────────────────────────────────────┤
    │ 8. Wait (0.5s delay)                 │
    └──────────────────────────────────────┘
                    │
                    ▼
            Frontend receives:
                    │
    ┌───────────────┴──────────────────┐
    │ 1. Animate action (3D scene)     │
    │    - Move agent                   │
    │    - Update light node colors     │
    │    - Update fuel stations         │
    ├───────────────────────────────────┤
    │ 2. Update HUD                     │
    │    - Agent stats                  │
    │    - Turn counter                 │
    │    - Action log                   │
    └───────────────────────────────────┘
```

### 3. Game End
```
Backend detects game over
    → Calculate final scores
    → Determine winner
    → WebSocket: {"type": "game_over", "data": {...}}
    → Frontend: Show game over screen
    → Display final statistics
```

## Component Responsibilities

### Backend Components

#### main.py
- FastAPI application setup
- WebSocket connection management
- Game loop orchestration
- Turn-by-turn execution
- Broadcasting updates

#### game_state.py
- Grid representation (12x12)
- Agent state (position, fuel, nodes)
- Environment elements (walls, doors, etc.)
- Game rules enforcement
- Action execution (move, refuel, control)
- State cloning for AI simulation

#### minimax_ai.py
- Minimax algorithm implementation
- Alpha-Beta pruning optimization
- Tree search (depth 3)
- Strategic evaluation
- Action generation & prioritization

#### mcts_ai.py
- Monte Carlo Tree Search
- UCB1 selection policy
- Random playouts (100 simulations)
- Node expansion
- Backpropagation

#### scoring.py
- State evaluation function
- Node control scoring
- Fuel management scoring
- Position value calculation
- Line-of-sight evaluation

#### config.py
- Game constants
- AI parameters
- Environment settings
- Tunable values

### Frontend Components

#### index.html
- Page structure
- HUD layout
- Styling (CSS)
- Cinematic overlay
- Game over screen

#### scene.js
- Three.js scene setup
- 3D object creation
- Lighting (moonlight, fog)
- Animation system
- Camera control
- Environment rendering

#### ui.js
- HUD updates
- Agent statistics display
- Turn counter
- Action logging
- Game over screen
- User feedback

#### main.js
- WebSocket client
- Message handling
- Game state synchronization
- Action coordination
- Frontend orchestration

## AI Decision Process

### Minimax (Unit S)
```
Decision Point
    │
    ▼
Generate all possible actions
    │
    ├─ Control node at current position?
    ├─ Refuel if low on fuel?
    └─ Move to adjacent cells
    │
    ▼
For each action:
    │
    ├─ Clone game state
    ├─ Apply action
    ├─ Minimax search (depth 3)
    │   ├─ Maximize own score
    │   ├─ Minimize opponent score
    │   └─ Alpha-Beta pruning
    ├─ Evaluate final position
    └─ Track best score
    │
    ▼
Return best action
```

### MCTS (Unit I)
```
Decision Point
    │
    ▼
Create root node (current state)
    │
    ▼
For 100 simulations:
    │
    ├─ SELECTION
    │   └─ Traverse tree using UCB1
    │       (exploitation + exploration)
    │
    ├─ EXPANSION
    │   └─ Add new child node
    │       (untried action)
    │
    ├─ SIMULATION
    │   └─ Random playout (10 turns)
    │       - Random actions
    │       - Quick evaluation
    │
    └─ BACKPROPAGATION
        └─ Update all ancestor nodes
            (wins & visits)
    │
    ▼
Select child with most visits
    │
    ▼
Return corresponding action
```

## WebSocket Message Format

### Client → Server
```json
{
  "command": "start" | "reset"
}
```

### Server → Client

**State Update:**
```json
{
  "type": "state_update",
  "data": {
    "turn": 0,
    "agents": {...},
    "fuel_stations": [...],
    "light_nodes": [...],
    "grid": [[...]]
  }
}
```

**Action:**
```json
{
  "type": "action",
  "data": {
    "action": {
      "type": "move" | "refuel" | "control_node",
      "agent": "strategist" | "instinct",
      ...
    },
    "ai_info": {
      "algorithm": "Minimax" | "MCTS",
      "nodes_explored": 1234
    },
    "state": {...}
  }
}
```

**Game Over:**
```json
{
  "type": "game_over",
  "data": {
    "winner": "strategist" | "instinct" | "draw",
    "final_state": {...},
    "strategist_score": 100,
    "instinct_score": 95
  }
}
```

## Performance Considerations

### Backend
- **Async/Await:** Non-blocking I/O with FastAPI
- **State Cloning:** Deep copy for AI simulations
- **Alpha-Beta Pruning:** Reduces Minimax search space
- **MCTS Limits:** 100 simulations, 10-turn playouts
- **Turn Delay:** 0.5s between updates (configurable)

### Frontend
- **WebGL:** Hardware-accelerated 3D rendering
- **Animation:** Smooth transitions (500ms)
- **Light Management:** Optimized point lights
- **Fog:** Reduces distant object rendering
- **Log Limit:** Keep only last 20 entries

## Extensibility Points

### Adding New AI Algorithms
1. Create new file (e.g., `a_star_ai.py`)
2. Implement `get_best_action(state)` method
3. Add to `main.py` game loop
4. Update config for algorithm selection

### Adding New Environment Elements
1. Add to `CellType` enum in `game_state.py`
2. Implement generation in `_initialize_game()`
3. Add rendering in `scene.js`
4. Update movement rules if needed

### Custom Scoring
1. Edit `evaluate_state()` in `scoring.py`
2. Add new evaluation functions
3. Adjust scoring weights in `config.py`
4. Test with different AI behaviors

---

This architecture enables:
- ✅ Real-time visualization
- ✅ Autonomous gameplay
- ✅ AI algorithm comparison
- ✅ Extensible design
- ✅ Responsive UI
- ✅ Smooth animations
