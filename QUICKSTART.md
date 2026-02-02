# Quick Start Guide - Fuel Dominion

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
Open PowerShell/Command Prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Start the Server
**Option A - Using the batch file (Windows):**
```bash
start.bat
```

**Option B - Manual start:**
```bash
cd backend
python main.py
```

### Step 3: Open in Browser
Navigate to: **http://localhost:8000**

Click **START GAME** to begin the AI battle!

---

## 🎮 What to Expect

1. **Cinematic Intro** (12 seconds)
   - Story narrative about the blackout
   - Introduction of Unit S and Unit I
   - City overview with lighting effects

2. **Automatic Gameplay**
   - AIs alternate turns automatically
   - Watch the action log for detailed moves
   - Monitor fuel levels and node control
   - No player input required!

3. **Game End**
   - Winner determined by node control
   - Final statistics displayed
   - Option to play again

---

## 📊 Understanding the HUD

### Left Panel - Unit S (Strategist)
- Green color scheme
- Minimax algorithm
- Strategic, long-term planning

### Right Panel - Unit I (Instinct)
- Magenta/purple color scheme
- MCTS algorithm
- Reactive, probabilistic decisions

### Center - Turn Counter
- Current turn / Maximum turns (100)

### Bottom - Action Log
- Real-time action descriptions
- Scrollable history
- Color-coded by importance

---

## 🎨 Visual Guide

### Colors in the Game
- **Green (0x00ff88)** - Unit S (Strategist) and controlled nodes
- **Magenta (0xff00ff)** - Unit I (Instinct) and controlled nodes
- **Orange (0xffaa00)** - Fuel stations
- **Gray (0x666666)** - Unclaimed light nodes
- **Blue tints** - Atmospheric lighting and fog

### 3D Elements
- **Cylindrical objects** - Fuel stations
- **Street poles with lights** - Light nodes (control points)
- **Box shapes** - Walls and ruins
- **Robotic figures** - AI agents

---

## ⚙️ Advanced Configuration

Want to customize the game? Edit `backend/config.py`:

### Make it Faster
```python
MAX_TURNS = 50              # Shorter games
MINIMAX_DEPTH = 2           # Faster AI decisions
MCTS_SIMULATIONS = 50       # Fewer simulations
```

### More Strategic
```python
MAX_TURNS = 200             # Longer games
MINIMAX_DEPTH = 4           # Deeper planning
NUM_LIGHT_NODES = 15        # More control points
```

### Fuel Scarcity Mode
```python
INITIAL_FUEL = 5            # Start with less fuel
FUEL_REFUEL_AMOUNT = 3      # Less fuel per refill
FUEL_STATION_INITIAL = 10   # Stations hold less
```

---

## 🐛 Common Issues

### "Module not found" error
```bash
pip install fastapi uvicorn websockets
```

### Port 8000 already in use
Edit `backend/main.py`, change the last line:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```
Then access: http://localhost:8001

### WebSocket won't connect
- Check if backend server is running
- Look for errors in terminal
- Ensure no firewall blocking
- Try restarting the server

### Slow performance
- Reduce MCTS_SIMULATIONS in config.py
- Lower MINIMAX_DEPTH
- Close other browser tabs
- Use Chrome or Firefox

---

## 🎓 Understanding the AI

### Minimax (Unit S)
- **How it works:** Looks ahead several turns, assuming optimal opponent play
- **Strengths:** Strategic planning, long-term optimization
- **Weaknesses:** Computationally expensive, slower decisions
- **Best at:** Territory control, resource management

### MCTS (Unit I)
- **How it works:** Runs random simulations to find promising moves
- **Strengths:** Handles uncertainty well, faster exploration
- **Weaknesses:** Less strategic long-term planning
- **Best at:** Opportunistic captures, adaptive play

---

## 🏆 Winning Strategies (for the AI)

The AIs are programmed to:
1. **Prioritize unclaimed nodes** - Easy points
2. **Manage fuel carefully** - Don't get stranded
3. **Capture strategically** - When cost-effective
4. **Position optimally** - Near multiple objectives
5. **Deny opponent** - Block their expansion

---

## 📸 Screenshots

When running, you'll see:
- Dark, atmospheric 3D city grid
- Glowing agents moving around
- Light nodes changing colors when captured
- Fuel stations with orange glow
- Real-time statistics updates
- Smooth animations between moves

---

## 🎉 Have Fun!

Watch as two AI systems compete using completely different strategies. Who will dominate the night? The strategic planner or the reactive opportunist?

**Remember:** You're just an observer - let the AIs do their thing! 🤖⚡
