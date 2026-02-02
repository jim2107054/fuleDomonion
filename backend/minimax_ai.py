import copy
from typing import List, Tuple, Optional
from game_state import GameState, AgentType, Position, CellType
from scoring import evaluate_state
import config

class MinimaxAI:
    """
    Unit S (Strategist) - Minimax AI with Alpha-Beta pruning
    Optimized for long-term planning and strategic positioning
    """
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.opponent_type = (AgentType.INSTINCT if agent_type == AgentType.STRATEGIST 
                             else AgentType.STRATEGIST)
        self.nodes_explored = 0
    
    def get_best_action(self, state: GameState) -> Tuple[str, Optional[Position]]:
        """
        Determine the best action using Minimax with Alpha-Beta pruning
        Returns: (action_type, target_position)
        """
        self.nodes_explored = 0
        
        best_score = float('-inf')
        best_action = None
        best_target = None
        
        # Generate all possible actions
        actions = self._generate_actions(state, self.agent_type)
        
        if not actions:
            return ("wait", None)
        
        # Evaluate each action using minimax
        for action_type, target in actions:
            # Simulate action
            next_state = state.clone()
            self._apply_action(next_state, self.agent_type, action_type, target)
            
            # Minimax evaluation
            score = self._minimax(
                next_state,
                depth=config.MINIMAX_DEPTH - 1,
                alpha=float('-inf'),
                beta=float('inf'),
                maximizing=False  # Next turn is opponent's
            )
            
            if score > best_score:
                best_score = score
                best_action = action_type
                best_target = target
        
        return (best_action, best_target)
    
    def _minimax(self, state: GameState, depth: int, alpha: float, beta: float, 
                 maximizing: bool) -> float:
        """
        Minimax algorithm with Alpha-Beta pruning
        """
        self.nodes_explored += 1
        
        # Terminal conditions
        if depth == 0 or state.is_game_over():
            return evaluate_state(state, self.agent_type)
        
        current_player = self.agent_type if maximizing else self.opponent_type
        actions = self._generate_actions(state, current_player)
        
        if not actions:
            return evaluate_state(state, self.agent_type)
        
        if maximizing:
            max_eval = float('-inf')
            
            for action_type, target in actions:
                next_state = state.clone()
                self._apply_action(next_state, current_player, action_type, target)
                
                eval_score = self._minimax(next_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval
        else:
            min_eval = float('inf')
            
            for action_type, target in actions:
                next_state = state.clone()
                self._apply_action(next_state, current_player, action_type, target)
                
                eval_score = self._minimax(next_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval
    
    def _generate_actions(self, state: GameState, agent_type: AgentType) -> List[Tuple[str, Optional[Position]]]:
        """Generate all possible actions for the agent"""
        actions = []
        agent = state.agents[agent_type]
        
        # 1. Control/Capture node at current position - ALWAYS consider this
        node = state.can_control_node(agent_type)
        if node:
            actions.append(("control_node", None))
        
        # 2. Refuel at current position (consider when fuel is not full)
        if state.can_refuel(agent_type) and agent.fuel < config.MAX_FUEL:
            actions.append(("refuel", None))
        
        # 3. Move to adjacent positions
        possible_moves = state.get_possible_moves(agent_type)
        for move_pos in possible_moves:
            actions.append(("move", move_pos))
        
        # Prioritize strategic actions for alpha-beta efficiency
        actions = self._prioritize_actions(state, agent_type, actions)
        
        return actions
    
    def _prioritize_actions(self, state: GameState, agent_type: AgentType, 
                           actions: List[Tuple[str, Optional[Position]]]) -> List[Tuple[str, Optional[Position]]]:
        """Prioritize actions based on strategic value for better alpha-beta pruning"""
        agent = state.agents[agent_type]
        opponent_type = (AgentType.INSTINCT if agent_type == AgentType.STRATEGIST 
                        else AgentType.STRATEGIST)
        
        # Separate actions by type
        control_actions = [a for a in actions if a[0] == "control_node"]
        refuel_actions = [a for a in actions if a[0] == "refuel"]
        move_actions = [a for a in actions if a[0] == "move"]
        
        prioritized = []
        
        # 1. Control/capture nodes FIRST (this is how you win!)
        prioritized.extend(control_actions)
        
        # 2. Refuel if critically low (can't do anything without fuel)
        if agent.fuel <= config.FUEL_COST_CONTROL_EMPTY:
            prioritized.extend(refuel_actions)
        
        # 3. Moves sorted by strategic value
        move_actions = self._sort_moves_by_value(state, agent_type, move_actions)
        prioritized.extend(move_actions)
        
        # 4. Refuel if moderately low
        if config.FUEL_COST_CONTROL_EMPTY < agent.fuel < config.MAX_FUEL * 0.5:
            prioritized.extend(refuel_actions)
        
        return prioritized
    
    def _sort_moves_by_value(self, state: GameState, agent_type: AgentType,
                            move_actions: List[Tuple[str, Position]]) -> List[Tuple[str, Position]]:
        """Sort move actions by strategic value"""
        agent = state.agents[agent_type]
        opponent_type = (AgentType.INSTINCT if agent_type == AgentType.STRATEGIST 
                        else AgentType.STRATEGIST)
        
        def move_value(action):
            _, target = action
            value = 0
            
            # HIGH PRIORITY: Moves that put us ON a light node we can control
            for node in state.light_nodes:
                if node.position.x == target.x and node.position.y == target.y:
                    if not node.is_controlled():
                        if agent.fuel >= config.FUEL_COST_CONTROL_EMPTY:
                            value += 100  # Can control next turn!
                    elif node.controlled_by == opponent_type:
                        if agent.fuel >= config.FUEL_COST_CAPTURE:
                            value += 80  # Can capture next turn!
            
            # Distance to unclaimed nodes
            unclaimed = [n for n in state.light_nodes if not n.is_controlled()]
            if unclaimed:
                min_dist = min(target.distance_to(n.position) for n in unclaimed)
                value += max(0, 30 - min_dist * 2)
            
            # Distance to opponent nodes (for capturing)
            opponent_nodes = [n for n in state.light_nodes if n.controlled_by == opponent_type]
            if opponent_nodes and agent.fuel >= config.FUEL_COST_CAPTURE:
                min_dist = min(target.distance_to(n.position) for n in opponent_nodes)
                value += max(0, 25 - min_dist * 2)
            
            # Move toward fuel station if low on fuel
            if agent.fuel < config.MAX_FUEL * 0.3:
                active_stations = [fs for fs in state.fuel_stations 
                                  if fs.is_active and not fs.is_depleted()]
                if active_stations:
                    min_dist = min(target.distance_to(fs.position) for fs in active_stations)
                    value += max(0, 20 - min_dist * 3)
            
            return value
        
        return sorted(move_actions, key=move_value, reverse=True)
    
    def _apply_action(self, state: GameState, agent_type: AgentType, 
                     action_type: str, target: Optional[Position]):
        """Apply an action to the game state (for simulation)"""
        if action_type == "move":
            agent = state.agents[agent_type]
            agent.position = target
        
        elif action_type == "refuel":
            agent = state.agents[agent_type]
            for station in state.fuel_stations:
                if station.position == agent.position and station.is_active:
                    fuel_gained = min(config.FUEL_REFUEL_AMOUNT, 
                                     config.MAX_FUEL - agent.fuel,
                                     station.fuel_remaining)
                    agent.fuel += fuel_gained
                    station.fuel_remaining -= fuel_gained
                    
                    if station.is_depleted():
                        station.is_active = False
                    break
        
        elif action_type == "control_node":
            agent = state.agents[agent_type]
            for node in state.light_nodes:
                if node.position == agent.position:
                    if not node.is_controlled():
                        agent.fuel -= config.FUEL_COST_CONTROL_EMPTY
                        node.controlled_by = agent_type
                        agent.nodes_controlled += 1
                    elif node.controlled_by != agent_type:
                        agent.fuel -= config.FUEL_COST_CAPTURE
                        
                        # Update previous owner
                        if node.controlled_by:
                            state.agents[node.controlled_by].nodes_controlled -= 1
                        
                        node.controlled_by = agent_type
                        agent.nodes_controlled += 1
                    break
        
        # Advance turn
        state.next_turn()
