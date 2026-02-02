from game_state import GameState, AgentType, Position
import config

def evaluate_state(state: GameState, agent_type: AgentType) -> float:
    """
    Evaluate the game state from the perspective of the given agent.
    Higher scores are better for the agent.
    """
    agent = state.agents[agent_type]
    opponent_type = AgentType.INSTINCT if agent_type == AgentType.STRATEGIST else AgentType.STRATEGIST
    opponent = state.agents[opponent_type]
    
    score = 0.0
    
    # 1. Node control (most important)
    score += agent.nodes_controlled * config.SCORE_NODE_CONTROL
    score -= opponent.nodes_controlled * config.SCORE_NODE_CONTROL
    
    # 2. Fuel remaining
    score += agent.fuel * config.SCORE_FUEL_REMAINING
    score -= opponent.fuel * config.SCORE_FUEL_REMAINING * 0.5  # Opponent fuel matters less
    
    # 3. Strategic positioning
    position_score = evaluate_position(state, agent_type)
    score += position_score * config.SCORE_STRATEGIC_POSITION
    
    # 4. Proximity to unclaimed nodes
    unclaimed_bonus = evaluate_unclaimed_nodes_proximity(state, agent_type)
    score += unclaimed_bonus
    
    # 5. Fuel station access
    fuel_access_bonus = evaluate_fuel_station_access(state, agent_type)
    score += fuel_access_bonus
    
    # 6. Line of sight / fog considerations
    visibility_bonus = evaluate_visibility(state, agent_type)
    score += visibility_bonus
    
    return score

def evaluate_position(state: GameState, agent_type: AgentType) -> float:
    """Evaluate strategic value of agent's position"""
    agent = state.agents[agent_type]
    score = 0.0
    
    # Central positions are generally better
    center = state.grid_size / 2
    distance_from_center = abs(agent.position.x - center) + abs(agent.position.y - center)
    score += (state.grid_size - distance_from_center) * 0.5
    
    return score

def evaluate_unclaimed_nodes_proximity(state: GameState, agent_type: AgentType) -> float:
    """Reward proximity to unclaimed nodes"""
    agent = state.agents[agent_type]
    score = 0.0
    
    unclaimed_nodes = [node for node in state.light_nodes if not node.is_controlled()]
    
    if unclaimed_nodes:
        # Find closest unclaimed node
        min_distance = min(agent.position.distance_to(node.position) for node in unclaimed_nodes)
        
        # Closer is better
        score += max(0, 10 - min_distance)
    
    return score

def evaluate_fuel_station_access(state: GameState, agent_type: AgentType) -> float:
    """Reward proximity to active fuel stations when low on fuel"""
    agent = state.agents[agent_type]
    score = 0.0
    
    # If fuel is low, prioritize fuel station access
    if agent.fuel < config.MAX_FUEL * 0.3:
        active_stations = [fs for fs in state.fuel_stations if fs.is_active and not fs.is_depleted()]
        
        if active_stations:
            min_distance = min(agent.position.distance_to(fs.position) for fs in active_stations)
            score += max(0, 15 - min_distance * 2)
    
    return score

def evaluate_visibility(state: GameState, agent_type: AgentType) -> float:
    """Evaluate visibility advantages (windows, clear lines)"""
    agent = state.agents[agent_type]
    opponent_type = AgentType.INSTINCT if agent_type == AgentType.STRATEGIST else AgentType.STRATEGIST
    opponent = state.agents[opponent_type]
    
    score = 0.0
    
    # Check if agent has line of sight to opponent
    if has_line_of_sight(state, agent.position, opponent.position):
        score += 3
    
    return score

def has_line_of_sight(state: GameState, pos1: Position, pos2: Position) -> bool:
    """Check if there's line of sight between two positions"""
    # Simple implementation - check if path is clear
    dx = 1 if pos2.x > pos1.x else -1 if pos2.x < pos1.x else 0
    dy = 1 if pos2.y > pos1.y else -1 if pos2.y < pos1.y else 0
    
    current = Position(pos1.x, pos1.y)
    
    while current != pos2:
        current.x += dx if current.x != pos2.x else 0
        current.y += dy if current.y != pos2.y else 0
        
        if current == pos2:
            break
        
        # Check for blocking obstacles
        from game_state import CellType
        cell = state.grid[current.y][current.x]
        if cell in [CellType.WALL, CellType.TREE]:
            return False
    
    return True

def update_agent_score(state: GameState, agent_type: AgentType):
    """Update the agent's score based on current state"""
    agent = state.agents[agent_type]
    
    # Base score from evaluation
    agent.score = int(evaluate_state(state, agent_type))
    
    # Additional bonus for efficiency
    if agent.fuel > config.MAX_FUEL * 0.7:
        agent.score += config.SCORE_FUEL_EFFICIENCY

def calculate_final_scores(state: GameState):
    """Calculate final scores for both agents"""
    for agent_type in [AgentType.STRATEGIST, AgentType.INSTINCT]:
        update_agent_score(state, agent_type)
