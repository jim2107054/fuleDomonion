// Three.js Scene Setup
class GameScene {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.grid = null;
        this.agents = {};
        this.fuelStations = {};
        this.lightNodes = {};
        this.environment = {};
        this.gridSize = 16;  // Match backend config
        this.cellSize = 2;
        this.autoRotate = false;
        
        this.init();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0f);
        this.scene.fog = new THREE.Fog(0x0a0a0f, 40, 80);
        
        // Setup camera
        const container = document.getElementById('canvas-container');
        this.camera = new THREE.PerspectiveCamera(
            60,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(this.gridSize * 1.5, this.gridSize * 1.5, this.gridSize * 1.5);
        this.camera.lookAt(this.gridSize, 0, this.gridSize);
        
        // Setup renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(this.renderer.domElement);
        
        // Setup controls
        this.setupControls();
        
        // Lighting
        this.setupLighting();
        
        // Create ground
        this.createGround();
        
        // Handle resize
        window.addEventListener('resize', () => this.onResize());
        
        // Add camera toggle
        this.addCameraControls();
        
        // Start animation loop
        this.animate();
    }
    
    setupControls() {
        const canvas = this.renderer.domElement;
        let isDragging = false;
        let previousMousePosition = { x: 0, y: 0 };
        
        canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            previousMousePosition = { x: e.offsetX, y: e.offsetY };
        });
        
        canvas.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const deltaX = e.offsetX - previousMousePosition.x;
                const deltaY = e.offsetY - previousMousePosition.y;
                
                const rotationSpeed = 0.01;
                this.camera.position.x += deltaX * rotationSpeed * 3;
                this.camera.position.z += deltaY * rotationSpeed * 3;
                this.camera.lookAt(this.gridSize, 0, this.gridSize);
            }
            previousMousePosition = { x: e.offsetX, y: e.offsetY };
        });
        
        canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        canvas.addEventListener('mouseleave', () => {
            isDragging = false;
        });
        
        // Zoom with mouse wheel
        canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomSpeed = 2;
            const direction = e.deltaY > 0 ? 1 : -1;
            
            this.camera.position.y += direction * zoomSpeed;
            this.camera.position.y = Math.max(10, Math.min(50, this.camera.position.y));
        });
    }
    
    addCameraControls() {
        const controlDiv = document.createElement('div');
        controlDiv.style.position = 'absolute';
        controlDiv.style.bottom = '200px';
        controlDiv.style.right = '20px';
        controlDiv.style.padding = '10px';
        controlDiv.style.background = 'rgba(10, 10, 20, 0.9)';
        controlDiv.style.border = '2px solid #00ff88';
        controlDiv.style.borderRadius = '10px';
        controlDiv.style.color = '#00ff88';
        controlDiv.style.fontFamily = 'Courier New, monospace';
        controlDiv.style.zIndex = '20';
        
        const toggleBtn = document.createElement('button');
        toggleBtn.textContent = 'Auto Rotate: OFF';
        toggleBtn.style.padding = '8px 16px';
        toggleBtn.style.background = '#00ff88';
        toggleBtn.style.color = '#0a0a0f';
        toggleBtn.style.border = 'none';
        toggleBtn.style.borderRadius = '5px';
        toggleBtn.style.cursor = 'pointer';
        toggleBtn.style.fontWeight = 'bold';
        toggleBtn.style.fontFamily = 'Courier New, monospace';
        
        toggleBtn.addEventListener('click', () => {
            this.autoRotate = !this.autoRotate;
            toggleBtn.textContent = `Auto Rotate: ${this.autoRotate ? 'ON' : 'OFF'}`;
        });
        
        const hint = document.createElement('div');
        hint.style.marginTop = '10px';
        hint.style.fontSize = '0.9em';
        hint.innerHTML = 'Drag: Pan<br>Wheel: Zoom';
        
        controlDiv.appendChild(toggleBtn);
        controlDiv.appendChild(hint);
        document.body.appendChild(controlDiv);
    }
    
    setupLighting() {
        // Bright ambient light
        const ambient = new THREE.AmbientLight(0x6a7a9a, 0.7);
        this.scene.add(ambient);
        
        // Directional light (moon - bright)
        const moonLight = new THREE.DirectionalLight(0x8899bb, 1.0);
        moonLight.position.set(15, 30, 10);
        moonLight.castShadow = true;
        moonLight.shadow.camera.left = -40;
        moonLight.shadow.camera.right = 40;
        moonLight.shadow.camera.top = 40;
        moonLight.shadow.camera.bottom = -40;
        this.scene.add(moonLight);
        
        // Fill light from opposite side
        const fillLight = new THREE.DirectionalLight(0x7a8aaa, 0.6);
        fillLight.position.set(-15, 25, -10);
        this.scene.add(fillLight);
        
        // Hemisphere light
        const hemiLight = new THREE.HemisphereLight(0xaabbcc, 0x445566, 0.6);
        this.scene.add(hemiLight);
        
        // Scattered atmospheric lights
        for (let i = 0; i < 6; i++) {
            const light = new THREE.PointLight(0x88aaff, 0.4, 25);
            light.position.set(
                Math.random() * this.gridSize * this.cellSize,
                4,
                Math.random() * this.gridSize * this.cellSize
            );
            this.scene.add(light);
        }
    }
    
    createGround() {
        // Ground plane
        const geometry = new THREE.PlaneGeometry(
            this.gridSize * this.cellSize + 10,
            this.gridSize * this.cellSize + 10
        );
        const material = new THREE.MeshStandardMaterial({
            color: 0x2a2a3e,
            roughness: 0.8,
            metalness: 0.2
        });
        const ground = new THREE.Mesh(geometry, material);
        ground.rotation.x = -Math.PI / 2;
        ground.position.set(
            this.gridSize * this.cellSize / 2,
            0,
            this.gridSize * this.cellSize / 2
        );
        ground.receiveShadow = true;
        this.scene.add(ground);
        
        // Grid lines (bright green)
        const gridHelper = new THREE.GridHelper(
            this.gridSize * this.cellSize,
            this.gridSize,
            0x00ff88,
            0x007744
        );
        gridHelper.position.set(
            this.gridSize * this.cellSize / 2,
            0.02,
            this.gridSize * this.cellSize / 2
        );
        this.scene.add(gridHelper);
    }
    
    createAgent(agentType, position, color) {
        const group = new THREE.Group();
        
        // Robot body
        const bodyGeometry = new THREE.BoxGeometry(0.8, 1.2, 0.8);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.3,
            metalness: 0.7,
            roughness: 0.3
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 0.6;
        body.castShadow = true;
        group.add(body);
        
        // Head
        const headGeometry = new THREE.SphereGeometry(0.4, 16, 16);
        const head = new THREE.Mesh(headGeometry, bodyMaterial);
        head.position.y = 1.5;
        head.castShadow = true;
        group.add(head);
        
        // Glowing core
        const coreGeometry = new THREE.SphereGeometry(0.2, 16, 16);
        const coreMaterial = new THREE.MeshBasicMaterial({ color: color });
        const core = new THREE.Mesh(coreGeometry, coreMaterial);
        core.position.y = 0.6;
        group.add(core);
        
        // Point light
        const light = new THREE.PointLight(color, 1, 5);
        light.position.y = 0.6;
        group.add(light);
        
        // Position in world
        group.position.set(
            position.x * this.cellSize + this.cellSize / 2,
            0,
            position.y * this.cellSize + this.cellSize / 2
        );
        
        this.scene.add(group);
        this.agents[agentType] = { mesh: group, light: light };
        
        return group;
    }
    
    createWall(position) {
        const geometry = new THREE.BoxGeometry(1.8, 2.5, 1.8);
        const material = new THREE.MeshStandardMaterial({
            color: 0x3a3a4e,
            roughness: 0.9
        });
        const wall = new THREE.Mesh(geometry, material);
        wall.position.set(
            position.x * this.cellSize + this.cellSize / 2,
            1.25,
            position.y * this.cellSize + this.cellSize / 2
        );
        wall.castShadow = true;
        wall.receiveShadow = true;
        this.scene.add(wall);
        
        const key = `${position.x},${position.y}`;
        this.environment[key] = wall;
    }
    
    createFuelStation(position) {
        const group = new THREE.Group();
        
        // Base
        const baseGeometry = new THREE.CylinderGeometry(0.6, 0.7, 0.3, 8);
        const baseMaterial = new THREE.MeshStandardMaterial({
            color: 0x5a5a6a,
            metalness: 0.6
        });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = 0.15;
        base.castShadow = true;
        group.add(base);
        
        // Tank
        const tankGeometry = new THREE.CylinderGeometry(0.4, 0.4, 1.2, 8);
        const tankMaterial = new THREE.MeshStandardMaterial({
            color: 0xffaa00,
            emissive: 0xffaa00,
            emissiveIntensity: 0.3,
            metalness: 0.8
        });
        const tank = new THREE.Mesh(tankGeometry, tankMaterial);
        tank.position.y = 0.9;
        tank.castShadow = true;
        group.add(tank);
        
        // Glow
        const glowGeometry = new THREE.SphereGeometry(0.25, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({ color: 0xffaa00 });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.y = 1.6;
        group.add(glow);
        
        // Light
        const light = new THREE.PointLight(0xffaa00, 1.0, 8);
        light.position.y = 1.6;
        group.add(light);
        
        group.position.set(
            position.x * this.cellSize + this.cellSize / 2,
            0,
            position.y * this.cellSize + this.cellSize / 2
        );
        
        this.scene.add(group);
        
        const key = `${position.x},${position.y}`;
        this.fuelStations[key] = { mesh: group, light: light, tank: tank };
    }
    
    createLightNode(position, controlledBy = null) {
        const group = new THREE.Group();
        
        // Pole
        const poleGeometry = new THREE.CylinderGeometry(0.05, 0.08, 2.5, 8);
        const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x4a4a5a });
        const pole = new THREE.Mesh(poleGeometry, poleMaterial);
        pole.position.y = 1.25;
        pole.castShadow = true;
        group.add(pole);
        
        // Light bulb
        const color = controlledBy === 'strategist' ? 0x00ff88 :
                     controlledBy === 'instinct' ? 0xff00ff :
                     0x888888;
        
        const bulbGeometry = new THREE.SphereGeometry(0.35, 16, 16);
        const bulbMaterial = new THREE.MeshStandardMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: controlledBy ? 0.6 : 0.2
        });
        const bulb = new THREE.Mesh(bulbGeometry, bulbMaterial);
        bulb.position.y = 2.7;
        group.add(bulb);
        
        // Point light
        const light = new THREE.PointLight(color, controlledBy ? 1.5 : 0.4, 10);
        light.position.y = 2.7;
        group.add(light);
        
        group.position.set(
            position.x * this.cellSize + this.cellSize / 2,
            0,
            position.y * this.cellSize + this.cellSize / 2
        );
        
        this.scene.add(group);
        
        const key = `${position.x},${position.y}`;
        this.lightNodes[key] = { mesh: group, light: light, bulb: bulb, controlledBy: controlledBy };
    }
    
    updateLightNode(position, controlledBy) {
        const key = `${position.x},${position.y}`;
        const node = this.lightNodes[key];
        
        if (node) {
            const color = controlledBy === 'strategist' ? 0x00ff88 :
                         controlledBy === 'instinct' ? 0xff00ff :
                         0x888888;
            
            node.bulb.material.color.setHex(color);
            node.bulb.material.emissive.setHex(color);
            node.bulb.material.emissiveIntensity = controlledBy ? 0.6 : 0.2;
            node.light.color.setHex(color);
            node.light.intensity = controlledBy ? 1.5 : 0.4;
            node.controlledBy = controlledBy;
            
            // Pulse animation
            this.pulseLightNode(node);
        }
    }
    
    pulseLightNode(node) {
        const originalIntensity = node.light.intensity;
        const startTime = Date.now();
        const duration = 500;
        
        const pulse = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            node.light.intensity = originalIntensity + Math.sin(progress * Math.PI) * 0.5;
            
            if (progress < 1) {
                requestAnimationFrame(pulse);
            } else {
                node.light.intensity = originalIntensity;
            }
        };
        
        pulse();
    }
    
    moveAgent(agentType, targetPosition) {
        const agent = this.agents[agentType];
        if (!agent) return;
        
        const targetX = targetPosition.x * this.cellSize + this.cellSize / 2;
        const targetZ = targetPosition.y * this.cellSize + this.cellSize / 2;
        
        // Smooth animation
        const startX = agent.mesh.position.x;
        const startZ = agent.mesh.position.z;
        const duration = 300;  // Faster animation
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease in-out
            const eased = progress < 0.5 
                ? 2 * progress * progress 
                : 1 - Math.pow(-2 * progress + 2, 2) / 2;
            
            agent.mesh.position.x = startX + (targetX - startX) * eased;
            agent.mesh.position.z = startZ + (targetZ - startZ) * eased;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }
    
    updateFuelStation(position, isActive) {
        const key = `${position.x},${position.y}`;
        const station = this.fuelStations[key];
        
        if (station) {
            if (isActive) {
                station.light.intensity = 1.0;
                station.tank.material.emissiveIntensity = 0.3;
            } else {
                station.light.intensity = 0.2;
                station.tank.material.emissiveIntensity = 0.05;
            }
        }
    }
    
    buildScene(gameState) {
        console.log('Building scene with game state:', gameState);
        
        // Clear existing elements (except ground and grid)
        Object.values(this.agents).forEach(a => this.scene.remove(a.mesh));
        Object.values(this.fuelStations).forEach(f => this.scene.remove(f.mesh));
        Object.values(this.lightNodes).forEach(l => this.scene.remove(l.mesh));
        Object.values(this.environment).forEach(e => this.scene.remove(e));
        
        this.agents = {};
        this.fuelStations = {};
        this.lightNodes = {};
        this.environment = {};
        
        // Update grid size from game state
        if (gameState.grid_size) {
            this.gridSize = gameState.grid_size;
        }
        
        // Create environment (walls only)
        for (let y = 0; y < gameState.grid_size; y++) {
            for (let x = 0; x < gameState.grid_size; x++) {
                const cellType = gameState.grid[y][x];
                const pos = { x, y };
                
                if (cellType === 'wall') {
                    this.createWall(pos);
                }
            }
        }
        
        // Create fuel stations
        gameState.fuel_stations.forEach(fs => {
            this.createFuelStation(fs.position);
        });
        
        // Create light nodes
        gameState.light_nodes.forEach(node => {
            this.createLightNode(node.position, node.controlled_by);
        });
        
        // Create agents
        const sPos = gameState.agents.strategist.position;
        this.createAgent('strategist', sPos, 0x00ff88);
        
        const iPos = gameState.agents.instinct.position;
        this.createAgent('instinct', iPos, 0xff00ff);
        
        console.log('Scene built successfully:', {
            walls: Object.keys(this.environment).length,
            fuelStations: Object.keys(this.fuelStations).length,
            lightNodes: Object.keys(this.lightNodes).length,
            agents: Object.keys(this.agents).length
        });
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Auto-rotate camera if enabled
        if (this.autoRotate) {
            const time = Date.now() * 0.0002;
            const radius = this.gridSize * 1.5;
            this.camera.position.x = this.gridSize + Math.sin(time) * radius;
            this.camera.position.z = this.gridSize + Math.cos(time) * radius;
            this.camera.lookAt(this.gridSize, 0, this.gridSize);
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    onResize() {
        const container = document.getElementById('canvas-container');
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }
}

// Initialize
let gameScene;
document.addEventListener('DOMContentLoaded', () => {
    gameScene = new GameScene();
});
