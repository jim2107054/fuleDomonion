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
        this.gridSize = 12;
        this.cellSize = 2;
        
        this.init();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0f);
        this.scene.fog = new THREE.Fog(0x0a0a0f, 20, 50);
        
        // Setup camera
        const container = document.getElementById('canvas-container');
        this.camera = new THREE.PerspectiveCamera(
            60,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(this.gridSize, this.gridSize * 1.5, this.gridSize);
        this.camera.lookAt(this.gridSize / 2, 0, this.gridSize / 2);
        
        // Setup renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(this.renderer.domElement);
        
        // Lighting
        this.setupLighting();
        
        // Create ground
        this.createGround();
        
        // Handle resize
        window.addEventListener('resize', () => this.onResize());
        
        // Start animation
        this.animate();
    }
    
    setupLighting() {
        // Ambient light (moonlight)
        const ambient = new THREE.AmbientLight(0x1a1a2e, 0.3);
        this.scene.add(ambient);
        
        // Directional light (moon)
        const moonLight = new THREE.DirectionalLight(0x4a5a8a, 0.5);
        moonLight.position.set(10, 20, 5);
        moonLight.castShadow = true;
        moonLight.shadow.camera.left = -20;
        moonLight.shadow.camera.right = 20;
        moonLight.shadow.camera.top = 20;
        moonLight.shadow.camera.bottom = -20;
        this.scene.add(moonLight);
        
        // Atmospheric point lights (scattered)
        for (let i = 0; i < 5; i++) {
            const light = new THREE.PointLight(0x00ccff, 0.3, 15);
            light.position.set(
                Math.random() * this.gridSize * this.cellSize,
                2,
                Math.random() * this.gridSize * this.cellSize
            );
            this.scene.add(light);
        }
    }
    
    createGround() {
        const geometry = new THREE.PlaneGeometry(
            this.gridSize * this.cellSize,
            this.gridSize * this.cellSize
        );
        const material = new THREE.MeshStandardMaterial({
            color: 0x1a1a2e,
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
        
        // Grid lines
        const gridHelper = new THREE.GridHelper(
            this.gridSize * this.cellSize,
            this.gridSize,
            0x00ff88,
            0x003322
        );
        gridHelper.position.set(
            this.gridSize * this.cellSize / 2,
            0.01,
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
            color: 0x2a2a3e,
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
    
    createDoor(position, isOpen = false) {
        const geometry = new THREE.BoxGeometry(1.8, 2.2, 0.3);
        const material = new THREE.MeshStandardMaterial({
            color: isOpen ? 0x4a5a6a : 0x3a4a5a,
            roughness: 0.7,
            metalness: 0.3
        });
        const door = new THREE.Mesh(geometry, material);
        door.position.set(
            position.x * this.cellSize + this.cellSize / 2,
            1.1,
            position.y * this.cellSize + this.cellSize / 2
        );
        door.castShadow = true;
        this.scene.add(door);
        
        const key = `${position.x},${position.y}`;
        this.environment[key] = door;
    }
    
    createWindow(position) {
        const geometry = new THREE.BoxGeometry(1.5, 1.5, 0.1);
        const material = new THREE.MeshStandardMaterial({
            color: 0x88aacc,
            transparent: true,
            opacity: 0.3,
            metalness: 0.9,
            roughness: 0.1
        });
        const window = new THREE.Mesh(geometry, material);
        window.position.set(
            position.x * this.cellSize + this.cellSize / 2,
            1.5,
            position.y * this.cellSize + this.cellSize / 2
        );
        this.scene.add(window);
        
        const key = `${position.x},${position.y}`;
        this.environment[key] = window;
    }
    
    createTree(position) {
        const group = new THREE.Group();
        
        // Trunk
        const trunkGeometry = new THREE.CylinderGeometry(0.15, 0.2, 1.5, 8);
        const trunkMaterial = new THREE.MeshStandardMaterial({ color: 0x3a2a1a });
        const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
        trunk.position.y = 0.75;
        trunk.castShadow = true;
        group.add(trunk);
        
        // Foliage
        const foliageGeometry = new THREE.ConeGeometry(0.8, 1.5, 8);
        const foliageMaterial = new THREE.MeshStandardMaterial({ color: 0x1a3a1a });
        const foliage = new THREE.Mesh(foliageGeometry, foliageMaterial);
        foliage.position.y = 2;
        foliage.castShadow = true;
        group.add(foliage);
        
        group.position.set(
            position.x * this.cellSize + this.cellSize / 2,
            0,
            position.y * this.cellSize + this.cellSize / 2
        );
        
        this.scene.add(group);
        
        const key = `${position.x},${position.y}`;
        this.environment[key] = group;
    }
    
    createFuelStation(position) {
        const group = new THREE.Group();
        
        // Base
        const baseGeometry = new THREE.CylinderGeometry(0.6, 0.7, 0.3, 8);
        const baseMaterial = new THREE.MeshStandardMaterial({
            color: 0x4a4a5a,
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
            emissiveIntensity: 0.2,
            metalness: 0.8
        });
        const tank = new THREE.Mesh(tankGeometry, tankMaterial);
        tank.position.y = 0.9;
        tank.castShadow = true;
        group.add(tank);
        
        // Glow
        const glowGeometry = new THREE.SphereGeometry(0.2, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({ color: 0xffaa00 });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.y = 1.5;
        group.add(glow);
        
        // Light
        const light = new THREE.PointLight(0xffaa00, 0.8, 6);
        light.position.y = 1.5;
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
        const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x3a3a4a });
        const pole = new THREE.Mesh(poleGeometry, poleMaterial);
        pole.position.y = 1.25;
        pole.castShadow = true;
        group.add(pole);
        
        // Light bulb
        const color = controlledBy === 'strategist' ? 0x00ff88 :
                     controlledBy === 'instinct' ? 0xff00ff :
                     0x666666;
        
        const bulbGeometry = new THREE.SphereGeometry(0.3, 16, 16);
        const bulbMaterial = new THREE.MeshStandardMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: controlledBy ? 0.5 : 0.1
        });
        const bulb = new THREE.Mesh(bulbGeometry, bulbMaterial);
        bulb.position.y = 2.7;
        group.add(bulb);
        
        // Point light
        const light = new THREE.PointLight(color, controlledBy ? 1.5 : 0.2, 8);
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
                         0x666666;
            
            node.bulb.material.color.setHex(color);
            node.bulb.material.emissive.setHex(color);
            node.bulb.material.emissiveIntensity = controlledBy ? 0.5 : 0.1;
            node.light.color.setHex(color);
            node.light.intensity = controlledBy ? 1.5 : 0.2;
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
        const duration = 500;
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
                station.light.intensity = 0.8;
                station.tank.material.emissiveIntensity = 0.2;
            } else {
                station.light.intensity = 0.1;
                station.tank.material.emissiveIntensity = 0;
            }
        }
    }
    
    buildScene(gameState) {
        // Clear existing elements (except ground and grid)
        Object.values(this.agents).forEach(a => this.scene.remove(a.mesh));
        Object.values(this.fuelStations).forEach(fs => this.scene.remove(fs.mesh));
        Object.values(this.lightNodes).forEach(ln => this.scene.remove(ln.mesh));
        Object.values(this.environment).forEach(e => this.scene.remove(e));
        
        this.agents = {};
        this.fuelStations = {};
        this.lightNodes = {};
        this.environment = {};
        
        // Build grid elements
        for (let y = 0; y < gameState.grid_size; y++) {
            for (let x = 0; x < gameState.grid_size; x++) {
                const cellType = gameState.grid[y][x];
                const pos = { x, y };
                
                switch (cellType) {
                    case 'wall':
                        this.createWall(pos);
                        break;
                    case 'door':
                        this.createDoor(pos);
                        break;
                    case 'window':
                        this.createWindow(pos);
                        break;
                    case 'tree':
                        this.createTree(pos);
                        break;
                    case 'fuel_station':
                        this.createFuelStation(pos);
                        break;
                    case 'light_node':
                        this.createLightNode(pos);
                        break;
                }
            }
        }
        
        // Create agents
        const sPos = gameState.agents.strategist.position;
        this.createAgent('strategist', sPos, 0x00ff88);
        
        const iPos = gameState.agents.instinct.position;
        this.createAgent('instinct', iPos, 0xff00ff);
        
        // Update light nodes with control status
        gameState.light_nodes.forEach(node => {
            this.updateLightNode(node.position, node.controlled_by);
        });
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Subtle camera movement
        const time = Date.now() * 0.0001;
        this.camera.position.x += Math.sin(time) * 0.01;
        this.camera.position.z += Math.cos(time) * 0.01;
        this.camera.lookAt(this.gridSize, 0, this.gridSize);
        
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
