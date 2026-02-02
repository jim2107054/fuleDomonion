// UI Controller
class UIController {
    constructor() {
        this.elements = {
            strategistNodes: document.getElementById('strategist-nodes'),
            strategistFuel: document.getElementById('strategist-fuel'),
            strategistScore: document.getElementById('strategist-score'),
            instinctNodes: document.getElementById('instinct-nodes'),
            instinctFuel: document.getElementById('instinct-fuel'),
            instinctScore: document.getElementById('instinct-score'),
            currentTurn: document.getElementById('current-turn'),
            maxTurns: document.getElementById('max-turns'),
            actionLog: document.getElementById('action-log'),
            startBtn: document.getElementById('start-btn'),
            resetBtn: document.getElementById('reset-btn'),
            cinematic: document.getElementById('cinematic'),
            gameOver: document.getElementById('game-over')
        };
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        this.elements.startBtn.addEventListener('click', () => {
            this.onStartGame();
        });
        
        this.elements.resetBtn.addEventListener('click', () => {
            location.reload();
        });
    }
    
    onStartGame() {
        this.elements.startBtn.disabled = true;
        this.showCinematic();
    }
    
    showCinematic() {
        this.elements.cinematic.classList.remove('hidden');
        
        // Hide after 12 seconds
        setTimeout(() => {
            this.elements.cinematic.classList.add('hidden');
            this.addLogEntry('Mission started. Agents are now active.');
        }, 12000);
    }
    
    updateAgentStats(agentType, data) {
        if (agentType === 'strategist') {
            this.elements.strategistNodes.textContent = data.nodes_controlled;
            this.elements.strategistFuel.textContent = data.fuel;
            this.elements.strategistScore.textContent = data.score;
        } else if (agentType === 'instinct') {
            this.elements.instinctNodes.textContent = data.nodes_controlled;
            this.elements.instinctFuel.textContent = data.fuel;
            this.elements.instinctScore.textContent = data.score;
        }
    }
    
    updateTurn(current, max) {
        this.elements.currentTurn.textContent = current;
        this.elements.maxTurns.textContent = max;
    }
    
    addLogEntry(message) {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        
        this.elements.actionLog.appendChild(entry);
        
        // Auto-scroll
        this.elements.actionLog.scrollTop = this.elements.actionLog.scrollHeight;
        
        // Keep only last 20 entries
        while (this.elements.actionLog.children.length > 20) {
            this.elements.actionLog.removeChild(this.elements.actionLog.firstChild);
        }
    }
    
    formatAction(action, aiInfo) {
        let message = '';
        const agentName = action.agent === 'strategist' ? 'Unit S' : 'Unit I';
        
        switch (action.type) {
            case 'move':
                message = `${agentName} moved to (${action.to.x}, ${action.to.y})`;
                break;
            case 'refuel':
                message = `${agentName} refueled +${action.fuel_gained} fuel → ${action.new_fuel}`;
                break;
            case 'control_node':
                message = `${agentName} controlled light node at (${action.position.x}, ${action.position.y})`;
                break;
            case 'capture_node':
                const fromAgent = action.from_agent === 'strategist' ? 'Unit S' : 'Unit I';
                message = `${agentName} captured node from ${fromAgent} at (${action.position.x}, ${action.position.y})`;
                break;
            case 'wait':
                message = `${agentName} is waiting...`;
                break;
            default:
                message = `${agentName} performed ${action.type}`;
        }
        
        return message;
    }
    
    showGameOver(data) {
        const elements = {
            winnerText: document.getElementById('winner-text'),
            finalStrategistNodes: document.getElementById('final-strategist-nodes'),
            finalInstinctNodes: document.getElementById('final-instinct-nodes'),
            finalStrategistScore: document.getElementById('final-strategist-score'),
            finalInstinctScore: document.getElementById('final-instinct-score')
        };
        
        // Determine winner text
        if (data.winner === 'strategist') {
            elements.winnerText.textContent = '⚙️ UNIT S (STRATEGIST) WINS';
            elements.winnerText.style.color = '#00ff88';
        } else if (data.winner === 'instinct') {
            elements.winnerText.textContent = '🎯 UNIT I (INSTINCT) WINS';
            elements.winnerText.style.color = '#ff00ff';
        } else {
            elements.winnerText.textContent = '🤝 DRAW - EQUAL PERFORMANCE';
            elements.winnerText.style.color = '#ffaa00';
        }
        
        // Update stats
        elements.finalStrategistNodes.textContent = data.final_state.agents.strategist.nodes_controlled;
        elements.finalInstinctNodes.textContent = data.final_state.agents.instinct.nodes_controlled;
        elements.finalStrategistScore.textContent = data.strategist_score;
        elements.finalInstinctScore.textContent = data.instinct_score;
        
        // Show overlay
        this.elements.gameOver.classList.add('show');
        
        // Add final log
        this.addLogEntry(`GAME OVER - Winner: ${data.winner || 'DRAW'}`);
    }
}

// Initialize
let uiController;
document.addEventListener('DOMContentLoaded', () => {
    uiController = new UIController();
});
