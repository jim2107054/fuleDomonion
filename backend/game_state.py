import random
import copy
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import config

class CellType(Enum):
    EMPTY = "empty"
    WALL = "wall"
    DOOR = "door"
    WINDOW = "window"
    TREE = "tree"
    FUEL_STATION = "fuel_station"
    LIGHT_NODE = "light_node"

class AgentType(Enum):
    STRATEGIST = "strategist"  # Unit S - Minimax
    INSTINCT = "instinct"  # Unit I - MCTS

@dataclass
class Position:
    x: int
    y: int
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def distance_to(self, other: 'Position') -> int:
        """Manhattan distance"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def is_adjacent(self, other: 'Position') -> bool:
        """Check if positions are adjacent (not diagonal)"""
        return self.distance_to(other) == 1

@dataclass
class Agent:
    agent_type: AgentType
    position: Position
    fuel: int
    nodes_controlled: int = 0
    score: int = 0
    
    def __repr__(self):
        return f"{self.agent_type.value}@({self.position.x},{self.position.y})"

@dataclass
class FuelStation:
    position: Position
    fuel_remaining: int
    is_active: bool = True
    respawn_counter: int = 0
    
    def is_depleted(self) -> bool:
        return self.fuel_remaining <= 0

@dataclass
class LightNode:
    position: Position
    controlled_by: Optional[AgentType] = None
    
    def is_controlled(self) -> bool:
        return self.controlled_by is not None

class GameState:
    def __init__(self):
        self.grid_size = config.GRID_SIZE
        self.turn = 0
        self.max_turns = config.MAX_TURNS
        self.current_player = AgentType.STRATEGIST
        
        # Initialize grid
        self.grid: List[List[CellType]] = [[CellType.EMPTY for _ in range(self.grid_size)] 
                                            for _ in range(self.grid_size)]
        
        # Game entities
        self.agents: Dict[AgentType, Agent] = {}
        self.fuel_stations: List[FuelStation] = []
        self.light_nodes: List[LightNode] = []
        self.doors_open: Set[Position] = set()
        
        # History
        self.action_history: List[Dict] = []
        
        # Initialize game
        self._initialize_game()
    
    def _initialize_game(self):
        """Set up the initial game state"""
        # Place agents in opposite corners
        self.agents[AgentType.STRATEGIST] = Agent(
            agent_type=AgentType.STRATEGIST,
            position=Position(1, 1),
            fuel=config.INITIAL_FUEL
        )
        self.agents[AgentType.INSTINCT] = Agent(
            agent_type=AgentType.INSTINCT,
            position=Position(self.grid_size - 2, self.grid_size - 2),
            fuel=config.INITIAL_FUEL
        )
        
        # Generate environment (only walls now, removed doors/windows/trees)
        self._generate_walls()
        self._generate_fuel_stations()
        self._generate_light_nodes()
    
    def _is_valid_position(self, pos: Position) -> bool:
        """Check if position is within grid bounds"""
        return 0 <= pos.x < self.grid_size and 0 <= pos.y < self.grid_size
    
    def _is_position_free(self, pos: Position, min_distance: int = 0) -> bool:
        """Check if position is free for placement with optional spacing"""
        if not self._is_valid_position(pos):
            return False
        
        # Check if agents are here
        for agent in self.agents.values():
            if agent.position == pos:
                return False
        
        # Check if cell is empty
        if self.grid[pos.y][pos.x] != CellType.EMPTY:
            return False
        
        # Check spacing from other objects
        if min_distance > 0:
            for dy in range(-min_distance, min_distance + 1):
                for dx in range(-min_distance, min_distance + 1):
                    check_pos = Position(pos.x + dx, pos.y + dy)
                    if self._is_valid_position(check_pos):
                        if self.grid[check_pos.y][check_pos.x] != CellType.EMPTY:
                            return False
        
        return True
    
    def _generate_walls(self):
        """Generate walls with proper spacing"""
        placed = 0
        attempts = 0
        max_attempts = config.NUM_WALLS * 20
        
        while placed < config.NUM_WALLS and attempts < max_attempts:
            x, y = random.randint(3, self.grid_size - 4), random.randint(3, self.grid_size - 4)
            pos = Position(x, y)
            
            # Ensure minimum spacing and not near agent spawn points
            agent_positions = [Position(1, 1), Position(self.grid_size - 2, self.grid_size - 2)]
            too_close_to_agent = any(pos.distance_to(ap) < config.MIN_AGENT_CLEARANCE 
                                     for ap in agent_positions)
            
            if not too_close_to_agent and self._is_position_free(pos, config.MIN_SPACING):
                self.grid[y][x] = CellType.WALL
                placed += 1
            
            attempts += 1
    
    def _generate_fuel_stations(self):
        """Generate fuel stations with proper spacing"""
        placed = 0
        attempts = 0
        max_attempts = config.NUM_FUEL_STATIONS * 20
        
        while placed < config.NUM_FUEL_STATIONS and attempts < max_attempts:
            x, y = random.randint(3, self.grid_size - 4), random.randint(3, self.grid_size - 4)
            pos = Position(x, y)
            
            # Place fuel stations on grid but allow agents to pass through them
            if self._is_position_free(pos, config.MIN_SPACING):
                self.grid[y][x] = CellType.FUEL_STATION
                self.fuel_stations.append(FuelStation(
                    position=pos,
                    fuel_remaining=config.FUEL_STATION_INITIAL
                ))
                placed += 1
            
            attempts += 1
    
    def _generate_light_nodes(self):
        """Generate light nodes (control points) with proper spacing"""
        placed = 0
        attempts = 0
        max_attempts = config.NUM_LIGHT_NODES * 20
        
        while placed < config.NUM_LIGHT_NODES and attempts < max_attempts:
            x, y = random.randint(2, self.grid_size - 3), random.randint(2, self.grid_size - 3)
            pos = Position(x, y)
            
            # Place light nodes on grid but allow agents to pass through them
            if self._is_position_free(pos, config.MIN_SPACING):
                self.grid[y][x] = CellType.LIGHT_NODE
                self.light_nodes.append(LightNode(position=pos))
                placed += 1
            
            attempts += 1
    
    def get_possible_moves(self, agent_type: AgentType) -> List[Position]:
        """Get all valid adjacent moves for an agent"""
        agent = self.agents[agent_type]
        moves = []
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_pos = Position(agent.position.x + dx, agent.position.y + dy)
            
            if not self._is_valid_position(new_pos):
                continue
            
            cell_type = self.grid[new_pos.y][new_pos.x]
            
            # Can move to any cell except walls
            # Agents can now pass through fuel stations and light nodes
            if cell_type != CellType.WALL:
                moves.append(new_pos)
        
        return moves
    
    def can_refuel(self, agent_type: AgentType) -> bool:
        """Check if agent can refuel at current position"""
        agent = self.agents[agent_type]
        
        for station in self.fuel_stations:
            if station.position == agent.position and station.is_active and not station.is_depleted():
                return True
        
        return False
    
    def can_control_node(self, agent_type: AgentType) -> Optional[LightNode]:
        """Check if agent can control a node at current position"""
        agent = self.agents[agent_type]
        
        for node in self.light_nodes:
            if node.position == agent.position:
                # Empty node - needs 1 fuel
                if not node.is_controlled() and agent.fuel >= config.FUEL_COST_CONTROL_EMPTY:
                    return node
                elif node.controlled_by != agent_type:
                    # Opponent's node - needs 2 fuel
                    if agent.fuel >= config.FUEL_COST_CAPTURE:
                        return node
        
        return None
    
    def execute_move(self, agent_type: AgentType, target: Position) -> Dict:
        """Execute a move action"""
        agent = self.agents[agent_type]
        old_pos = copy.copy(agent.position)
        agent.position = target
        
        # Consume fuel for movement
        agent.fuel -= config.FUEL_COST_MOVE
        
        action = {
            "type": "move",
            "agent": agent_type.value,
            "from": {"x": old_pos.x, "y": old_pos.y},
            "to": {"x": target.x, "y": target.y},
            "fuel_cost": config.FUEL_COST_MOVE,
            "new_fuel": agent.fuel,
            "turn": self.turn
        }
        
        self.action_history.append(action)
        return action
    
    def execute_refuel(self, agent_type: AgentType) -> Dict:
        """Execute a refuel action"""
        agent = self.agents[agent_type]
        
        for station in self.fuel_stations:
            if station.position == agent.position and station.is_active:
                # Refuel
                fuel_gained = min(config.FUEL_REFUEL_AMOUNT, 
                                 config.MAX_FUEL - agent.fuel,
                                 station.fuel_remaining)
                
                agent.fuel += fuel_gained
                station.fuel_remaining -= fuel_gained
                
                # Deactivate if empty
                if station.is_depleted():
                    station.is_active = False
                    station.respawn_counter = config.FUEL_STATION_RESPAWN_TURNS
                
                action = {
                    "type": "refuel",
                    "agent": agent_type.value,
                    "position": {"x": agent.position.x, "y": agent.position.y},
                    "fuel_gained": fuel_gained,
                    "new_fuel": agent.fuel,
                    "station_remaining": station.fuel_remaining,
                    "turn": self.turn
                }
                
                self.action_history.append(action)
                return action
        
        return {"type": "refuel_failed", "agent": agent_type.value}
    
    def execute_control_node(self, agent_type: AgentType) -> Dict:
        """Execute a control/capture node action"""
        agent = self.agents[agent_type]
        
        # Find node at agent's position
        for node in self.light_nodes:
            if node.position == agent.position:
                was_controlled = node.is_controlled()
                previous_owner = node.controlled_by
                
                if not was_controlled:
                    # Control empty node
                    agent.fuel -= config.FUEL_COST_CONTROL_EMPTY
                    node.controlled_by = agent_type
                    agent.nodes_controlled += 1
                    
                    action = {
                        "type": "control_node",
                        "agent": agent_type.value,
                        "position": {"x": node.position.x, "y": node.position.y},
                        "fuel_cost": config.FUEL_COST_CONTROL_EMPTY,
                        "new_fuel": agent.fuel,
                        "turn": self.turn
                    }
                elif previous_owner != agent_type:
                    # Capture opponent's node
                    agent.fuel -= config.FUEL_COST_CAPTURE
                    
                    # Update previous owner
                    if previous_owner:
                        self.agents[previous_owner].nodes_controlled -= 1
                    
                    node.controlled_by = agent_type
                    agent.nodes_controlled += 1
                    
                    action = {
                        "type": "capture_node",
                        "agent": agent_type.value,
                        "from_agent": previous_owner.value if previous_owner else None,
                        "position": {"x": node.position.x, "y": node.position.y},
                        "fuel_cost": config.FUEL_COST_CAPTURE,
                        "new_fuel": agent.fuel,
                        "turn": self.turn
                    }
                else:
                    return {"type": "control_failed", "agent": agent_type.value, "reason": "already_controlled"}
                
                self.action_history.append(action)
                return action
        
        return {"type": "control_failed", "agent": agent_type.value, "reason": "no_node"}
    
    def update_fuel_stations(self):
        """Update fuel station respawn timers"""
        for station in self.fuel_stations:
            if not station.is_active:
                station.respawn_counter -= 1
                if station.respawn_counter <= 0:
                    station.is_active = True
                    station.fuel_remaining = config.FUEL_STATION_INITIAL
    
    def next_turn(self):
        """Advance to next turn"""
        self.turn += 1
        self.current_player = (AgentType.INSTINCT if self.current_player == AgentType.STRATEGIST 
                              else AgentType.STRATEGIST)
        
        # Update fuel stations
        self.update_fuel_stations()
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.turn >= self.max_turns
    
    def get_winner(self) -> Optional[AgentType]:
        """Determine winner"""
        s_agent = self.agents[AgentType.STRATEGIST]
        i_agent = self.agents[AgentType.INSTINCT]
        
        # Primary: node control
        if s_agent.nodes_controlled > i_agent.nodes_controlled:
            return AgentType.STRATEGIST
        elif i_agent.nodes_controlled > s_agent.nodes_controlled:
            return AgentType.INSTINCT
        
        # Tie-breaker: fuel
        if s_agent.fuel > i_agent.fuel:
            return AgentType.STRATEGIST
        elif i_agent.fuel > s_agent.fuel:
            return AgentType.INSTINCT
        
        # Draw
        return None
    
    def clone(self) -> 'GameState':
        """Create a deep copy of the game state"""
        return copy.deepcopy(self)
    
    def to_dict(self) -> Dict:
        """Convert game state to dictionary for JSON serialization"""
        return {
            "turn": self.turn,
            "max_turns": self.max_turns,
            "current_player": self.current_player.value,
            "grid_size": self.grid_size,
            "agents": {
                agent_type.value: {
                    "position": {"x": agent.position.x, "y": agent.position.y},
                    "fuel": agent.fuel,
                    "nodes_controlled": agent.nodes_controlled,
                    "score": agent.score
                }
                for agent_type, agent in self.agents.items()
            },
            "fuel_stations": [
                {
                    "position": {"x": fs.position.x, "y": fs.position.y},
                    "fuel_remaining": fs.fuel_remaining,
                    "is_active": fs.is_active
                }
                for fs in self.fuel_stations
            ],
            "light_nodes": [
                {
                    "position": {"x": ln.position.x, "y": ln.position.y},
                    "controlled_by": ln.controlled_by.value if ln.controlled_by else None
                }
                for ln in self.light_nodes
            ],
            "grid": [[cell.value for cell in row] for row in self.grid],
            "doors_open": [{"x": pos.x, "y": pos.y} for pos in self.doors_open],
            "is_game_over": self.is_game_over()
        }
