<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>3D Rubik's Cube</title>
<style>
  * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
  body {
    margin: 0;
    overflow: hidden;
    background-color: #0f172a;
    touch-action: none;
    font-family: system-ui, sans-serif;
  }
  canvas { display: block; }
  
  #ui {
    position: absolute;
    top: 20px;
    left: 0;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    pointer-events: none;
    color: white;
  }
  #timer {
    font-size: 48px;
    font-weight: bold;
    font-variant-numeric: tabular-nums;
    text-shadow: 0 4px 10px rgba(0,0,0,0.8);
    color: #facc15;
  }
  #instructions {
    margin-top: 10px;
    font-size: 14px;
    color: #94a3b8;
  }
</style>

<!-- THE CORRECT WAY TO IMPORT THREE.JS -->
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>

<div id="ui">
  <div id="timer">00:00.0</div>
  <div id="instructions">Drag to rotate • Agent, add twisting to this file!</div>
</div>

<script type="module">
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

  // --- TIMER LOGIC ---
  const timerDisplay = document.getElementById('timer');
  let startTime = Date.now();

  function updateTimer() {
    const elapsed = Date.now() - startTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    const tenths = Math.floor((elapsed % 1000) / 100);
    
    timerDisplay.textContent = 
      `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${tenths}`;
      
    requestAnimationFrame(updateTimer);
  }
  updateTimer();

  // --- SETUP SCENE, CAMERA, RENDERER ---
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(4, 4, 6);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  // --- CONTROLS ---
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.enableZoom = true;
  controls.enablePan = false;

  // --- LIGHTS ---
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);
  
  const dirLight = new THREE.DirectionalLight(0xffffff, 1);
  dirLight.position.set(10, 10, 10);
  scene.add(dirLight);

  // --- BUILD THE RUBIK'S CUBE ---
  const size = 0.95; 
  const gap = 1;     
  
  const colors = {
    right: 0xff0000, left: 0xff8800, top: 0xffffff,
    bottom: 0xffdd00, front: 0x00ff00, back: 0x0000ff
  };

  const cubeGroup = new THREE.Group();
  scene.add(cubeGroup);

  for (let x = -1; x <= 1; x++) {
    for (let y = -1; y <= 1; y++) {
      for (let z = -1; z <= 1; z++) {
        
        const materials = [
          new THREE.MeshStandardMaterial({ color: (x === 1) ? colors.right : 0x111111 }),
          new THREE.MeshStandardMaterial({ color: (x === -1) ? colors.left : 0x111111 }),
          new THREE.MeshStandardMaterial({ color: (y === 1) ? colors.top : 0x111111 }),
          new THREE.MeshStandardMaterial({ color: (y === -1) ? colors.bottom : 0x111111 }),
          new THREE.MeshStandardMaterial({ color: (z === 1) ? colors.front : 0x111111 }),
          new THREE.MeshStandardMaterial({ color: (z === -1) ? colors.back : 0x111111 })
        ];

        const geometry = new THREE.BoxGeometry(size, size, size);
        const cube = new THREE.Mesh(geometry, materials);
        
        cube.position.set(x * gap, y * gap, z * gap);
        cube.userData = { initialX: x, initialY: y, initialZ: z };
        
        cubeGroup.add(cube);
      }
    }
  }

  // --- RESIZE ---
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // --- LOOP ---
  function animate() {
    requestAnimationFrame(animate);
    controls.update(); 
    renderer.render(scene, camera);
  }

  animate();
</script>
</body>
</html>
