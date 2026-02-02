# Game Configuration
GRID_SIZE = 16  # 16x16 grid (bigger for better spacing)
MAX_TURNS = 100  # Maximum game turns
MAX_FUEL = 20  # Maximum fuel per agent
INITIAL_FUEL = 10  # Starting fuel

# Fuel costs
FUEL_COST_MOVE = 0  # Moving is free (but uses turn)
FUEL_COST_CONTROL_EMPTY = 1  # Control empty node
FUEL_COST_CAPTURE = 2  # Capture opponent's node
FUEL_REFUEL_AMOUNT = 5  # Fuel gained per refuel action

# Fuel station config
FUEL_STATION_INITIAL = 15  # Initial fuel in each station
FUEL_STATION_RESPAWN_TURNS = 20  # Turns before respawn

# Scoring weights
SCORE_NODE_CONTROL = 10  # Points per node controlled
SCORE_FUEL_REMAINING = 2  # Points per fuel unit
SCORE_STRATEGIC_POSITION = 5  # Bonus for good positioning
SCORE_FUEL_EFFICIENCY = 3  # Bonus for efficient fuel use
SCORE_CAPTURE = 15  # Bonus for capturing opponent node

# AI parameters - BALANCED for fair competition
MINIMAX_DEPTH = 4  # Minimax search depth (balanced)
MCTS_SIMULATIONS = 1000  # MCTS simulation count (increased significantly for fairness)
MCTS_EXPLORATION = 1.5  # UCB1 exploration constant (slightly higher for better exploration)
MCTS_SIM_DEPTH = 30  # Maximum simulation depth for MCTS rollouts (deeper lookahead)

# Environment elements (fewer obstacles, better spacing)
NUM_WALLS = 8  # Reduced obstacles
NUM_FUEL_STATIONS = 5  # More fuel stations
NUM_LIGHT_NODES = 12  # More control points

# Spacing rules - minimum distance between objects
MIN_SPACING = 2  # At least 2 cells between major objects
MIN_AGENT_CLEARANCE = 3  # Clear area around agent spawn points

# WebSocket settings
WS_UPDATE_DELAY = 0.1  # Seconds between turn updates (100ms for visibility)
TURN_DELAY = 0.3  # Configurable delay between agent turns (300ms for visibility)
