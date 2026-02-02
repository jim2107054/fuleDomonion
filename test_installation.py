#!/usr/bin/env python3
"""
Test script to verify Fuel Dominion installation and components
Run this to check if everything is set up correctly
"""

import sys
import importlib
from pathlib import Path

def test_python_version():
    """Check Python version"""
    print("✓ Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} (Need 3.8+)")
        return False

def test_dependencies():
    """Check if required packages are installed"""
    print("\n✓ Testing dependencies...")
    required = ['fastapi', 'uvicorn', 'websockets']
    all_good = True
    
    for package in required:
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"  ✓ {package} {version}")
        except ImportError:
            print(f"  ✗ {package} NOT FOUND")
            all_good = False
    
    return all_good

def test_file_structure():
    """Check if all required files exist"""
    print("\n✓ Testing file structure...")
    
    base = Path(__file__).parent
    
    required_files = [
        'backend/main.py',
        'backend/game_state.py',
        'backend/minimax_ai.py',
        'backend/mcts_ai.py',
        'backend/scoring.py',
        'backend/config.py',
        'frontend/index.html',
        'frontend/main.js',
        'frontend/scene.js',
        'frontend/ui.js',
        'README.md'
    ]
    
    all_good = True
    for file_path in required_files:
        full_path = base / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} MISSING")
            all_good = False
    
    return all_good

def test_imports():
    """Test if backend modules can be imported"""
    print("\n✓ Testing backend imports...")
    
    # Add backend to path
    sys.path.insert(0, str(Path(__file__).parent / 'backend'))
    
    modules = [
        'config',
        'game_state',
        'minimax_ai',
        'mcts_ai',
        'scoring'
    ]
    
    all_good = True
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✓ {module}.py")
        except Exception as e:
            print(f"  ✗ {module}.py - Error: {str(e)[:50]}")
            all_good = False
    
    return all_good

def test_game_state():
    """Test basic game state creation"""
    print("\n✓ Testing game state initialization...")
    
    sys.path.insert(0, str(Path(__file__).parent / 'backend'))
    
    try:
        from game_state import GameState
        
        game = GameState()
        
        # Check basic properties
        assert game.grid_size == 12, "Grid size should be 12"
        assert len(game.agents) == 2, "Should have 2 agents"
        assert game.turn == 0, "Should start at turn 0"
        assert len(game.light_nodes) > 0, "Should have light nodes"
        assert len(game.fuel_stations) > 0, "Should have fuel stations"
        
        print("  ✓ GameState created successfully")
        print(f"  ✓ Grid: {game.grid_size}x{game.grid_size}")
        print(f"  ✓ Agents: {len(game.agents)}")
        print(f"  ✓ Light Nodes: {len(game.light_nodes)}")
        print(f"  ✓ Fuel Stations: {len(game.fuel_stations)}")
        print(f"  ✓ Walls: {sum(1 for row in game.grid for cell in row if cell.value == 'wall')}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def test_ai_algorithms():
    """Test AI algorithm initialization"""
    print("\n✓ Testing AI algorithms...")
    
    sys.path.insert(0, str(Path(__file__).parent / 'backend'))
    
    try:
        from game_state import GameState, AgentType
        from minimax_ai import MinimaxAI
        from mcts_ai import MCTSAI
        
        game = GameState()
        
        # Test Minimax
        minimax = MinimaxAI(AgentType.STRATEGIST)
        action_m = minimax.get_best_action(game)
        print(f"  ✓ Minimax AI initialized (explored {minimax.nodes_explored} nodes)")
        print(f"    Action: {action_m[0]}")
        
        # Test MCTS
        mcts = MCTSAI(AgentType.INSTINCT)
        action_i = mcts.get_best_action(game)
        print(f"  ✓ MCTS AI initialized (ran {mcts.simulations_run} simulations)")
        print(f"    Action: {action_i[0]}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("  FUEL DOMINION - Installation Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("File Structure", test_file_structure()))
    results.append(("Module Imports", test_imports()))
    results.append(("Game State", test_game_state()))
    results.append(("AI Algorithms", test_ai_algorithms()))
    
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! You're ready to run the game.")
        print("\nTo start the game:")
        print("  1. Run: python backend/main.py")
        print("  2. Open: http://localhost:8000")
        print("  3. Click START GAME")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Check file locations and names")
        print("  - Ensure Python 3.8+ is installed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
