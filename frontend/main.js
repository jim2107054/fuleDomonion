// Main Game Controller
class GameController {
    constructor() {
        this.ws = null;
        this.gameState = null;
        this.isConnected = false;
        
        this.connectWebSocket();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        console.log('Connecting to WebSocket:', wsUrl);
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            uiController.addLogEntry('Connected to game server.');
        };
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            uiController.addLogEntry('Connection error. Please refresh.');
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            uiController.addLogEntry('Disconnected from server.');
        };
    }
    
    handleMessage(message) {
        console.log('Received message:', message);
        
        switch (message.type) {
            case 'state_update':
                this.handleStateUpdate(message.data);
                break;
            case 'game_start':
                this.handleGameStart(message.data);
                break;
            case 'action':
                this.handleAction(message.data);
                break;
            case 'game_over':
                this.handleGameOver(message.data);
                break;
        }
    }
    
    handleStateUpdate(state) {
        this.gameState = state;
        
        // Build 3D scene
        if (gameScene && state) {
            gameScene.buildScene(state);
            console.log('✓ Scene built successfully with', state.light_nodes.length, 'nodes');
        }
        
        // Update UI
        if (state.agents) {
            uiController.updateAgentStats('strategist', state.agents.strategist);
            uiController.updateAgentStats('instinct', state.agents.instinct);
        }
        
        uiController.updateTurn(state.turn, state.max_turns);
    }
    
    handleGameStart(state) {
        console.log('Game started:', state);
        this.gameState = state;
        
        // Build scene
        gameScene.buildScene(state);
        
        // Update UI
        uiController.updateAgentStats('strategist', state.agents.strategist);
        uiController.updateAgentStats('instinct', state.agents.instinct);
        uiController.updateTurn(state.turn, state.max_turns);
    }
    
    handleAction(data) {
        const { action, ai_info, ai_name, state } = data;
        
        console.log('Action:', action, 'AI Info:', ai_info);
        
        // Update game state
        this.gameState = state;
        
        // Animate action in scene
        if (action.type === 'move') {
            gameScene.moveAgent(action.agent, action.to);
        } else if (action.type === 'control_node' || action.type === 'capture_node') {
            gameScene.updateLightNode(action.position, action.agent);
        }
        
        // Update fuel stations
        if (state.fuel_stations) {
            state.fuel_stations.forEach(fs => {
                gameScene.updateFuelStation(fs.position, fs.is_active);
            });
        }
        
        // Update UI
        uiController.updateAgentStats('strategist', state.agents.strategist);
        uiController.updateAgentStats('instinct', state.agents.instinct);
        uiController.updateTurn(state.turn, state.max_turns);
        
        // Log action
        const logMessage = uiController.formatAction(action, ai_info);
        uiController.addLogEntry(logMessage);
    }
    
    handleGameOver(data) {
        console.log('Game over:', data);
        
        // Update final state
        this.gameState = data.final_state;
        
        // Update UI stats
        uiController.updateAgentStats('strategist', data.final_state.agents.strategist);
        uiController.updateAgentStats('instinct', data.final_state.agents.instinct);
        
        // Show game over screen
        uiController.showGameOver(data);
    }
    
    startGame() {
        if (this.isConnected && this.ws) {
            console.log('Sending start command');
            this.ws.send(JSON.stringify({ command: 'start' }));
        } else {
            console.error('WebSocket not connected');
            uiController.addLogEntry('Cannot start game - not connected to server.');
        }
    }
    
    resetGame() {
        if (this.isConnected && this.ws) {
            this.ws.send(JSON.stringify({ command: 'reset' }));
        }
    }
}

// Initialize game controller
let gameController;
document.addEventListener('DOMContentLoaded', () => {
    // Wait for other components to initialize
    setTimeout(() => {
        gameController = new GameController();
    }, 500);
});
