from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
from typing import Dict, Optional
import os

from game_state import GameState, AgentType, Position
from minimax_ai import MinimaxAI
from mcts_ai import MCTSAI
from scoring import update_agent_score, calculate_final_scores
import config

app = FastAPI(title="Fuel Dominion")

# Game state
game: Optional[GameState] = None
minimax_ai: Optional[MinimaxAI] = None
mcts_ai: Optional[MCTSAI] = None
active_websocket: Optional[WebSocket] = None

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    """Serve the main HTML file"""
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.post("/api/start")
async def start_game():
    """Initialize a new game"""
    global game, minimax_ai, mcts_ai
    
    game = GameState()
    minimax_ai = MinimaxAI(AgentType.STRATEGIST)
    mcts_ai = MCTSAI(AgentType.INSTINCT)
    
    return {
        "status": "started",
        "initial_state": game.to_dict()
    }

@app.get("/api/state")
async def get_state():
    """Get current game state"""
    if game is None:
        return {"error": "Game not started"}
    
    return game.to_dict()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time game updates"""
    global active_websocket, game
    
    await websocket.accept()
    active_websocket = websocket
    
    try:
        # Initialize game if not exists
        if game is None:
            await start_game()
        
        # Send initial game state
        await websocket.send_json({
            "type": "state_update",
            "data": game.to_dict()
        })
        
        # Wait for start command
        while True:
            data = await websocket.receive_json()
            
            if data.get("command") == "start":
                await start_game_loop(websocket)
            elif data.get("command") == "reset":
                await start_game()
                await websocket.send_json({
                    "type": "state_update",
                    "data": game.to_dict()
                })
    
    except WebSocketDisconnect:
        active_websocket = None
        print("WebSocket disconnected")

async def start_game_loop(websocket: WebSocket):
    """Run the game loop, alternating AI turns"""
    global game
    
    if game is None:
        await start_game()
    
    # Send game start notification
    await websocket.send_json({
        "type": "game_start",
        "data": game.to_dict()
    })
    
    # Wait a bit for cinematic intro
    await asyncio.sleep(3)
    
    # Game loop
    while not game.is_game_over():
        current_agent = game.current_player
        
        # Update scores
        update_agent_score(game, current_agent)
        
        # Get AI decision
        if current_agent == AgentType.STRATEGIST:
            action_type, target = minimax_ai.get_best_action(game)
            ai_name = "Unit S (Strategist)"
            ai_info = {
                "algorithm": "Minimax",
                "nodes_explored": minimax_ai.nodes_explored
            }
        else:
            action_type, target = mcts_ai.get_best_action(game)
            ai_name = "Unit I (Instinct)"
            ai_info = {
                "algorithm": "MCTS",
                "simulations": mcts_ai.simulations_run
            }
        
        # Execute action
        action_result = None
        
        if action_type == "move" and target:
            action_result = game.execute_move(current_agent, target)
        elif action_type == "refuel":
            action_result = game.execute_refuel(current_agent)
        elif action_type == "control_node":
            action_result = game.execute_control_node(current_agent)
        elif action_type == "wait":
            action_result = {
                "type": "wait",
                "agent": current_agent.value,
                "turn": game.turn
            }
        
        # Advance turn
        game.next_turn()
        
        # Send update to frontend
        if action_result:
            await websocket.send_json({
                "type": "action",
                "data": {
                    "action": action_result,
                    "ai_info": ai_info,
                    "ai_name": ai_name,
                    "state": game.to_dict()
                }
            })
        
        # Wait before next turn
        await asyncio.sleep(config.WS_UPDATE_DELAY)
    
    # Game over - calculate final scores
    calculate_final_scores(game)
    winner = game.get_winner()
    
    await websocket.send_json({
        "type": "game_over",
        "data": {
            "winner": winner.value if winner else "draw",
            "final_state": game.to_dict(),
            "strategist_score": game.agents[AgentType.STRATEGIST].score,
            "instinct_score": game.agents[AgentType.INSTINCT].score
        }
    })

@app.get("/api/stats")
async def get_stats():
    """Get current game statistics"""
    if game is None:
        return {"error": "Game not started"}
    
    return {
        "turn": game.turn,
        "max_turns": game.max_turns,
        "strategist": {
            "nodes_controlled": game.agents[AgentType.STRATEGIST].nodes_controlled,
            "fuel": game.agents[AgentType.STRATEGIST].fuel,
            "score": game.agents[AgentType.STRATEGIST].score
        },
        "instinct": {
            "nodes_controlled": game.agents[AgentType.INSTINCT].nodes_controlled,
            "fuel": game.agents[AgentType.INSTINCT].fuel,
            "score": game.agents[AgentType.INSTINCT].score
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
