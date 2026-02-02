import math
import random
import copy
from typing import List, Tuple, Optional
from game_state import GameState, AgentType, Position, CellType
from scoring import evaluate_state
import config

class MCTSNode:
    """Node in the Monte Carlo Tree Search"""
    
    def __init__(self, state: GameState, agent_type: AgentType, 
                 parent=None, action=None):
        self.state = state
        self.agent_type = agent_type
        self.parent = parent
        self.action = action  # (action_type, target)
        
        self.children: List['MCTSNode'] = []
        self.wins = 0.0
        self.visits = 0
        self.untried_actions = self._get_possible_actions()
    
    def _get_possible_actions(self) -> List[Tuple[str, Optional[Position]]]:
        """Get all possible actions from this state"""
        actions = []
        agent = self.state.agents[self.agent_type]
        
        # Control/Capture node
        node = self.state.can_control_node(self.agent_type)
        if node:
            actions.append(("control_node", None))
        
        # Refuel
        if self.state.can_refuel(self.agent_type):
            actions.append(("refuel", None))
        
        # Move
        possible_moves = self.state.get_possible_moves(self.agent_type)
        for move_pos in possible_moves:
            actions.append(("move", move_pos))
        
        random.shuffle(actions)
        return actions
    
    def is_fully_expanded(self) -> bool:
        """Check if all actions have been tried"""
        return len(self.untried_actions) == 0
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal state"""
        return self.state.is_game_over()
    
    def best_child(self, exploration_weight: float = config.MCTS_EXPLORATION) -> 'MCTSNode':
        """Select best child using UCB1 formula"""
        best_score = float('-inf')
        best_child = None
        
        for child in self.children:
            if child.visits == 0:
                ucb_score = float('inf')
            else:
                exploitation = child.wins / child.visits
                exploration = exploration_weight * math.sqrt(
                    math.log(self.visits) / child.visits
                )
                ucb_score = exploitation + exploration
            
            if ucb_score > best_score:
                best_score = ucb_score
                best_child = child
        
        return best_child
    
    def expand(self) -> 'MCTSNode':
        """Expand tree by trying an untried action"""
        action = self.untried_actions.pop()
        
        # Apply action to create new state
        next_state = self.state.clone()
        MCTSAI._apply_action(next_state, self.agent_type, action[0], action[1])
        
        # Create child node (with opponent's turn)
        opponent_type = (AgentType.INSTINCT if self.agent_type == AgentType.STRATEGIST 
                        else AgentType.STRATEGIST)
        child_node = MCTSNode(next_state, opponent_type, parent=self, action=action)
        
        self.children.append(child_node)
        return child_node
    
    def update(self, result: float):
        """Backpropagate result"""
        self.visits += 1
        self.wins += result

class MCTSAI:
    """
    Unit I (Instinct) - Monte Carlo Tree Search AI
    Reactive and probabilistic, relies on simulations
    """
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.opponent_type = (AgentType.INSTINCT if agent_type == AgentType.STRATEGIST 
                             else AgentType.STRATEGIST)
        self.simulations_run = 0
    
    def get_best_action(self, state: GameState) -> Tuple[str, Optional[Position]]:
        """
        Determine the best action using Monte Carlo Tree Search
        Returns: (action_type, target_position)
        """
        self.simulations_run = 0
        
        # Create root node
        root = MCTSNode(state, self.agent_type)
        
        # Run MCTS simulations
        for _ in range(config.MCTS_SIMULATIONS):
            self.simulations_run += 1
            
            # Selection
            node = self._select(root)
            
            # Expansion
            if not node.is_terminal() and not node.is_fully_expanded():
                node = node.expand()
            
            # Simulation
            result = self._simulate(node.state, self.agent_type)
            
            # Backpropagation
            self._backpropagate(node, result)
        
        # Choose best action
        if not root.children:
            # No valid actions
            return ("wait", None)
        
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.action
    
    def _select(self, node: MCTSNode) -> MCTSNode:
        """Selection phase: traverse tree using UCB1"""
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node
            else:
                node = node.best_child()
        return node
    
    def _simulate(self, state: GameState, starting_agent: AgentType) -> float:
        """
        Simulation phase: random playout from current state
        Returns normalized result (0.0 to 1.0)
        """
        sim_state = state.clone()
        current_agent = starting_agent
        max_sim_turns = 10  # Limit simulation depth
        
        for _ in range(max_sim_turns):
            if sim_state.is_game_over():
                break
            
            # Get random action
            actions = self._get_quick_actions(sim_state, current_agent)
            
            if not actions:
                break
            
            action = random.choice(actions)
            self._apply_action(sim_state, current_agent, action[0], action[1])
            
            # Switch player
            current_agent = (AgentType.INSTINCT if current_agent == AgentType.STRATEGIST 
                           else AgentType.STRATEGIST)
        
        # Evaluate final state
        score = evaluate_state(sim_state, self.agent_type)
        
        # Normalize to [0, 1]
        # Higher scores are better, use sigmoid-like normalization
        normalized = 1.0 / (1.0 + math.exp(-score / 50.0))
        
        return normalized
    
    def _backpropagate(self, node: MCTSNode, result: float):
        """Backpropagation phase: update all ancestors"""
        while node is not None:
            # Flip result for opponent nodes
            if node.agent_type != self.agent_type:
                node.update(1.0 - result)
            else:
                node.update(result)
            
            node = node.parent
    
    def _get_quick_actions(self, state: GameState, agent_type: AgentType) -> List[Tuple[str, Optional[Position]]]:
        """Get possible actions quickly (for simulation)"""
        actions = []
        agent = state.agents[agent_type]
        
        # Control node
        node = state.can_control_node(agent_type)
        if node:
            actions.append(("control_node", None))
        
        # Refuel (only if low)
        if state.can_refuel(agent_type) and agent.fuel < config.MAX_FUEL * 0.3:
            actions.append(("refuel", None))
        
        # Move (limit to few best moves for speed)
        possible_moves = state.get_possible_moves(agent_type)
        if len(possible_moves) > 4:
            possible_moves = random.sample(possible_moves, 4)
        
        for move_pos in possible_moves:
            actions.append(("move", move_pos))
        
        return actions
    
    @staticmethod
    def _apply_action(state: GameState, agent_type: AgentType, 
                     action_type: str, target: Optional[Position]):
        """Apply an action to the game state (static for simulation)"""
        if action_type == "move":
            agent = state.agents[agent_type]
            agent.position = target
            
            if state.grid[target.y][target.x] == CellType.DOOR:
                state.doors_open.add(target)
        
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
                        
                        if node.controlled_by:
                            state.agents[node.controlled_by].nodes_controlled -= 1
                        
                        node.controlled_by = agent_type
                        agent.nodes_controlled += 1
                    break
        
        state.next_turn()
