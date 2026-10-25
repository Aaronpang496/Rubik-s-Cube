import streamlit as st
import streamlit.components.v1 as components

# Set page config for a better mobile/full-width experience
st.set_page_config(layout="wide", page_title="3D Rubik's Cube")

st.title("Rubik's Cube 3D")
st.write("Swipe background to turn cube • Drag a face to twist slice")

# The entire game logic bundled into one HTML string
cube_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>3D Rubik's Cube</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
    body { margin: 0; overflow: hidden; background-color: #0f172a; touch-action: none; font-family: system-ui, sans-serif; height: 100vh; width: 100vw; color: white; }
    canvas { display: block; width: 100%; height: 100%; }
    #ui { position: absolute; top: 20px; left: 0; width: 100%; display: flex; flex-direction: column; align-items: center; pointer-events: none; z-index: 10; }
    #timer { font-size: 32px; font-weight: bold; color: #facc15; }
    #controls-container { position: absolute; bottom: 30px; width: 100%; display: flex; justify-content: center; z-index: 10; }
    button { pointer-events: auto; background: #2563eb; color: white; border: none; padding: 12px 24px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; }
    #win-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.9); display: none; flex-direction: column; justify-content: center; align-items: center; color: #4ade80; z-index: 20; }
    #win-screen.show { display: flex; }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
  <div id="ui"><div id="timer">00:00.0</div></div>
  <div id="controls-container"><button id="scramble-btn">Scramble</button></div>
  <div id="win-screen">
    🎉 CUBE SOLVED! 🎉
    <button id="restart-btn" style="margin-top: 20px; background: #4ade80; color: #0f172a;">Play Again</button>
  </div>

  <script>
    const timerDisplay = document.getElementById("timer");
    let startTime = Date.now(), timerActive = false, hasScrambled = false;

    function updateTimer() {
      if (!timerActive) return;
      const elapsed = Date.now() - startTime;
      const minutes = Math.floor(elapsed / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);
      const tenths = Math.floor((elapsed % 1000) / 100);
      timerDisplay.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${tenths}`;
      requestAnimationFrame(updateTimer);
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(4, 4, 6);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const l = new THREE.DirectionalLight(0xffffff, 0.8); l.position.set(10,10,10); scene.add(l);

    const cubes = [];
    const colors = { right: 0xb91c1c, left: 0xea580c, top: 0xf8fafc, bottom: 0xeab308, front: 0x16a34a, back: 0x2563eb };
    
    function createSticker(color) {
      const c = document.createElement("canvas"); c.width = 256; c.height = 256;
      const ctx = c.getContext("2d"); ctx.fillStyle = "#111111"; ctx.fillRect(0,0,256,256);
      ctx.fillStyle = color; ctx.roundRect ? ctx.roundRect(16,16,224,224,32) : ctx.rect(16,16,224,224); ctx.fill();
      return new THREE.CanvasTexture(c);
    }

    const mats = Object.values(colors).map(c => new THREE.MeshStandardMaterial({ map: createSticker("#"+c.toString(16).padStart(6,'0')), roughness: 0.2 }));
    const black = new THREE.MeshStandardMaterial({ color: 0x111111 });

    for(let x=-1; x<=1; x++) for(let y=-1; y<=1; y++) for(let z=-1; z<=1; z++) {
      if(x===0 && y===0 && z===0) continue;
      const m = [x==1?mats[0]:black, x==-1?mats[1]:black, y==1?mats[2]:black, y==-1?mats[3]:black, z==1?mats[4]:black, z==-1?mats[5]:black];
      const cube = new THREE.Mesh(new THREE.BoxGeometry(0.92, 0.92, 0.92), m);
      cube.position.set(x, y, z); cube.userData = { initial: new THREE.Vector3(x,y,z) };
      scene.add(cube); cubes.push(cube);
    }

    let isTransitioning = false;
    const raycaster = new THREE.Raycaster();
    let pStart = new THREE.Vector2(), intersect = null, normal = null;

    window.addEventListener("pointerdown", e => {
      if(isTransitioning) return;
      const m = new THREE.Vector2((e.clientX/window.innerWidth)*2-1, -(e.clientY/window.innerHeight)*2+1);
      raycaster.setFromCamera(m, camera); const hits = raycaster.intersectObjects(cubes);
      if(hits.length > 0) { controls.enabled = false; intersect = hits[0].object; normal = hits[0].face.normal.clone().applyQuaternion(intersect.quaternion); pStart.set(e.clientX, e.clientY); }
    });

    window.addEventListener("pointerup", e => {
      if(!controls.enabled && intersect) {
        const dx = e.clientX - pStart.x, dy = e.clientY - pStart.y;
        if(Math.sqrt(dx*dx+dy*dy) > 20) {
          const sDir = new THREE.Vector3(dx, -dy, 0).normalize();
          const wDir = new THREE.Vector3().addScaledVector(new THREE.Vector3(1,0,0).applyQuaternion(camera.quaternion), sDir.x).addScaledVector(new THREE.Vector3(0,1,0).applyQuaternion(camera.quaternion), sDir.y).projectOnPlane(normal).normalize();
          const tDir = new THREE.Vector3().crossVectors(normal, wDir).normalize();
          let best = new THREE.Vector3(1,0,0), max = 0;
          [new THREE.Vector3(1,0,0), new THREE.Vector3(0,1,0), new THREE.Vector3(0,0,1)].forEach(a => {
            const d = Math.abs(tDir.dot(a)); if(d > max) { max = d; best = a.clone().multiplyScalar(Math.sign(tDir.dot(a))); }
          });
          const axis = best.x !== 0 ? 'x' : (best.y !== 0 ? 'y' : 'z');
          const slice = cubes.filter(c => Math.abs(c.position[axis] - intersect.position[axis]) < 0.1);
          rotate(slice, new THREE.Vector3(best.x!=0?1:0, best.y!=0?1:0, best.z!=0?1:0), (best.x+best.y+best.z)*Math.PI/2);
        }
      }
      controls.enabled = true; intersect = null;
    });

    function rotate(slice, axis, angle, fast=false) {
      isTransitioning = true; const pivot = new THREE.Group(); scene.add(pivot); slice.forEach(c => pivot.attach(c));
      const start = performance.now(), dur = fast ? 50 : 250, qS = pivot.quaternion.clone(), qT = new THREE.Quaternion().setFromAxisAngle(axis, angle).multiply(qS);
      function step() {
        const p = Math.min((performance.now()-start)/dur, 1);
        pivot.quaternion.slerpQuaternions(qS, qT, p);
        if(p < 1) requestAnimationFrame(step);
        else {
          slice.forEach(c => { scene.attach(c); c.position.set(Math.round(c.position.x), Math.round(c.position.y), Math.round(c.position.z)); });
          scene.remove(pivot); isTransitioning = false; check();
        }
      }
      step();
    }

    document.getElementById("scramble-btn").onclick = async () => {
      if(isTransitioning) return; hasScrambled = true; timerActive = false;
      for(let i=0; i<15; i++) {
        const ax = ['x','y','z'][Math.floor(Math.random()*3)];
        const sl = cubes.filter(c => Math.abs(c.position[ax] - (Math.floor(Math.random()*3)-1)) < 0.1);
        rotate(sl, new THREE.Vector3(ax=='x'?1:0, ax=='y'?1:0, ax=='z'?1:0), (Math.random()>0.5?1:-1)*Math.PI/2, true);
        await new Promise(r => setTimeout(r, 60));
      }
      startTime = Date.now(); timerActive = true; updateTimer();
    };

    function check() {
      if(!hasScrambled || isTransitioning) return;
      let solved = true;
      const axes = ['x','y','z'];
      for(let ax of axes) for(let v of [-1,1]) {
        const face = cubes.filter(c => Math.abs(c.position[ax]-v) < 0.1);
        const ref = face[0].userData.initial.clone().applyQuaternion(face[0].quaternion).normalize();
        if(face.some(c => c.userData.initial.clone().applyQuaternion(c.quaternion).normalize().distanceTo(ref) > 0.1)) solved = false;
      }
      if(solved) { timerActive = false; document.getElementById("win-screen").classList.add("show"); }
    }

    document.getElementById("restart-btn").onclick = () => { document.getElementById("win-screen").classList.remove("show"); hasScrambled = false; timerDisplay.textContent = "00:00.0"; };

    function animate() { requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }
    animate();
    window.onresize = () => { camera.aspect = window.innerWidth/window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight); };
  </script>
</body>
</html>
"""

# Render the game
components.html(cube_html, height=700, scrolling=False)
