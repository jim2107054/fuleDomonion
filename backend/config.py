# Game Configuration
GRID_SIZE = 12  # 12x12 grid
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

# AI parameters
MINIMAX_DEPTH = 3  # Minimax search depth
MCTS_SIMULATIONS = 100  # MCTS simulation count
MCTS_EXPLORATION = 1.414  # UCB1 exploration constant

# Environment elements (positions will be generated)
NUM_WALLS = 15
NUM_DOORS = 5
NUM_WINDOWS = 8
NUM_TREES = 6
NUM_FUEL_STATIONS = 4
NUM_LIGHT_NODES = 10

# WebSocket settings
WS_UPDATE_DELAY = 0.5  # Seconds between turn updates
