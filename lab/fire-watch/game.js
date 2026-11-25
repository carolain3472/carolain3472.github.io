import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const $ = i => document.getElementById(i);
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
const phone = innerWidth < 820;

// ------------------------------------------------------------------ data
const get = f => fetch(f).then(r => r.json());
const D = await get('events.json');
const REC = {};
for (const [k, f] of Object.entries({
  haiku: 'results_claude-haiku-5-5.json', sonnet: 'results_claude-sonnet-5-5.json',
  chrome: 'results_local_chrome.json', eg2: 'results_local_embeddinggemma2.json' })) {
  REC[k] = Object.fromEntries((await get(f)).rows.map(r => [r.id + '|' + r.style, r]));
}
const ACTIONS = ['ignore', 'monitor', 'drone', 'brigade'];
const INFO = {
  ignore: { t: 'Ignore', s: 'Nothing unusual', d: 'No smoke, below 45 °C and above 20% humidity.', i: '<svg viewBox="0 0 24 24"><path d="M4 12l5 5L20 6"/></svg>' },
  monitor: { t: 'Monitor', s: 'One problem', d: 'No smoke, and only one problem: very hot (45 °C or more) or very dry (20% or less).', i: '<svg viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>' },
  drone: { t: 'Drone', s: 'Hot and dry', d: 'No smoke, and both problems at once.', i: '<svg viewBox="0 0 24 24"><circle cx="5" cy="6" r="3"/><circle cx="19" cy="6" r="3"/><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><path d="M7 8l3 3M17 8l-3 3M7 16l3-3M17 16l-3-3"/><rect x="10" y="10" width="4" height="4" rx="1"/></svg>' },
  brigade: { t: 'Brigade', s: 'Smoke', d: 'The camera sees smoke, whatever the temperature and the humidity are.', i: '<svg viewBox="0 0 24 24"><path d="M2 16V8h11v8M13 11h5l3 3v2h-2M2 16h2m5 0h5"/><circle cx="6.5" cy="17" r="2"/><circle cx="16.5" cy="17" r="2"/></svg>' } };
for (const id of ['rulesA', 'rulesB']) $(id).innerHTML = ['brigade', 'drone', 'monitor', 'ignore'].map(a => `<div><b>${INFO[a].t}</b>${INFO[a].d}</div>`).join('');
const STYLE = { numbers: 'With numbers', spanish: 'In Spanish', words: 'Plain words', words_no_echo: 'Plain words' };
const PLACES = [['north ridge', 'el filo norte', -20, -17], ['river bend', 'la curva del río', 5, 9], ['old quarry', 'la cantera vieja', 20, -13], ['pine slope', 'la ladera de pinos', -22, 7], ['east gate', 'la puerta este', 22, 9], ['lake path', 'el camino del lago', -3, -9]];
const placeOf = e => PLACES.findIndex(p => e.text.numbers.includes(p[0]));

// ------------------------------------------------------------------ scene
let renderer;
try { renderer = new THREE.WebGLRenderer({ canvas: $('c'), antialias: true, preserveDrawingBuffer: true }); }
catch { document.body.insertAdjacentHTML('beforeend', '<p style="position:fixed;inset:auto 20px 20px">This game needs WebGL. You can still use the <a href="experiment.html">experiment page</a>.</p>'); throw Error('no webgl'); }
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.08;
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xf2b184, 58, 125);
const cam = new THREE.PerspectiveCamera(42, 1, .1, 300); cam.position.set(6, 34, 52);
const ctl = new OrbitControls(cam, $('c')); ctl.enableDamping = true; ctl.enablePan = false; ctl.minDistance = 20; ctl.maxDistance = 78; ctl.maxPolarAngle = 1.32; ctl.minPolarAngle = .45; ctl.target.set(0, 1, 0);
const sky = new THREE.Mesh(new THREE.SphereGeometry(150, 32, 16), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false,
  vertexShader: 'varying vec3 p;void main(){p=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
  fragmentShader: 'varying vec3 p;void main(){float h=normalize(p).y;vec3 a=vec3(.98,.66,.42),b=vec3(.93,.45,.36),c=vec3(.22,.33,.46);vec3 k=mix(a,b,smoothstep(0.,.18,h));k=mix(k,c,smoothstep(.12,.62,h));gl_FragColor=vec4(k,1.);}' }));
scene.add(sky);
scene.add(new THREE.HemisphereLight(0xffd9b0, 0x35503a, 1.15));
const sun = new THREE.DirectionalLight(0xffc27a, 2.5); sun.position.set(-34, 30, 18); sun.castShadow = true;
sun.shadow.mapSize.set(phone ? 1024 : 2048, phone ? 1024 : 2048); Object.assign(sun.shadow.camera, { left: -42, right: 42, top: 42, bottom: -42, far: 110 }); sun.shadow.bias = -.0006; sun.shadow.normalBias = .04; scene.add(sun);

let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const riverX = z => 9 * Math.sin(z * .09) + 1.5;
function H(x, z) {
  const r = Math.hypot(x, z);
  let y = Math.sin(x * .16) * .7 + Math.cos(z * .19 + x * .05) * .7;
  y += Math.max(0, r - 27) * .42 + Math.sin(x * .31 + z * .23) * Math.max(0, r - 25) * .07;
  const d = Math.abs(x - riverX(z)); y -= Math.max(0, 1 - d / 3.4) * 1.9;
  return y;
}
const mat = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, flatShading: true, roughness: .95, ...o });
{
  const g = new THREE.PlaneGeometry(110, 110, 100, 100); g.rotateX(-Math.PI / 2);
  const p = g.attributes.position, col = [], c = new THREE.Color();
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), z = p.getZ(i), y = H(x, z); p.setY(i, y);
    const d = Math.abs(x - riverX(z)), r = Math.hypot(x, z);
    c.set(d < 2.7 ? 0xc9a36a : r > 34 ? 0x5d6f45 : (Math.sin(x * .5) + Math.cos(z * .4) > .9 ? 0xa9a350 : 0x7f9a4d));
    c.offsetHSL(0, 0, (rnd() - .5) * .05); col.push(c.r, c.g, c.b);
  }
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, roughness: 1 })); m.receiveShadow = true; scene.add(m);
}
const water = (() => {
  const pts = []; for (let z = -55; z <= 55; z += 1.5) { const x = riverX(z); pts.push([x - 2.1, z], [x + 2.1, z]); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pts.flatMap(([x, z]) => [x, 0, z]), 3));
  const ix = []; for (let i = 0; i < pts.length - 2; i += 2) ix.push(i, i + 2, i + 1, i + 1, i + 2, i + 3); g.setIndex(ix); g.computeVertexNormals();
  const p = g.attributes.position; for (let i = 0; i < p.count; i++) { const z = p.getZ(i); p.setY(i, H(riverX(z), z) + .75); }
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0x5fb0c2, roughness: .18, metalness: .25, transparent: true, opacity: .9, side: THREE.DoubleSide })); m.receiveShadow = true; scene.add(m); return m;
})();

// trees
const STATION = [-9, 20], TOWER = [11, 24], VILLAGE = [[-15, 22], [-18, 18.5], [-13, 26], [-20, 24]];
const trees = [];
const free = (x, z) => Math.abs(x - riverX(z)) > 4 && !PLACES.some(p => Math.hypot(x - p[2], z - p[3]) < 2.6) && Math.hypot(x - STATION[0], z - STATION[1]) > 5 && Math.hypot(x - TOWER[0], z - TOWER[1]) > 4 && !VILLAGE.some(v => Math.hypot(x - v[0], z - v[1]) < 3.4) && !(z > 15 && x > -24 && x < 16 && z < 30 && rnd() < .7);
for (let i = 0; trees.length < (phone ? 300 : 460) && i < 6000; i++) {
  const x = (rnd() - .5) * 82, z = (rnd() - .5) * 78; if (!free(x, z)) continue;
  trees.push({ x, z, y: H(x, z), s: .75 + rnd() * .75, kind: rnd() < .42 ? 1 : rnd() < .5 ? 2 : 0, rot: rnd() * 6, burnt: 0 });
}
const N = trees.length, dummy = new THREE.Object3D(), col = new THREE.Color();
const im = (g, c, n = N) => { const m = new THREE.InstancedMesh(g, mat(c), n); m.castShadow = true; m.receiveShadow = true; scene.add(m); return m; };
const trunk = im(new THREE.CylinderGeometry(.11, .19, 1.5, 5).translate(0, .7, 0), 0xffffff);
const crownA = im(new THREE.IcosahedronGeometry(.95, 0).scale(1, .85, 1).translate(0, 2, 0), 0xffffff);
const crownB = im(new THREE.ConeGeometry(.92, 2.5, 6).translate(0, 2.3, 0), 0xffffff);
const crownC = im(new THREE.IcosahedronGeometry(.7, 0).scale(1.75, .5, 1.75).translate(0, 2, 0), 0xffffff);
const GREENS = [[0x6f9440, 0x8aa348, 0xa7a64a], [0x3f6b45, 0x4d7a4a, 0x57844f], [0xb99443, 0xc98a3c, 0x9d9a45]];
function drawTree(i) {
  const t = trees[i]; dummy.position.set(t.x, t.y - .1, t.z); dummy.rotation.set(0, t.rot, 0); dummy.scale.setScalar(t.s); dummy.updateMatrix();
  trunk.setMatrixAt(i, dummy.matrix); trunk.setColorAt(i, col.set(t.burnt ? 0x2a2422 : 0x7a5638));
  [crownA, crownB, crownC].forEach((m, k) => { dummy.scale.setScalar(k === t.kind ? t.s * (t.burnt ? .55 : 1) : 0); dummy.updateMatrix(); m.setMatrixAt(i, dummy.matrix); m.setColorAt(i, col.set(t.burnt ? 0x3a312c : GREENS[t.kind][i % 3])); });
}
function flushTrees() { for (const m of [trunk, crownA, crownB, crownC]) { m.instanceMatrix.needsUpdate = true; if (m.instanceColor) m.instanceColor.needsUpdate = true; } }
for (let i = 0; i < N; i++) drawTree(i); flushTrees();

const add = (parent, g, c, x = 0, y = 0, z = 0, o) => { const m = new THREE.Mesh(g, mat(c, o)); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m; };
// wax palms, rocks
for (let i = 0; i < 9; i++) { const x = -34 + rnd() * 66, z = -34 + rnd() * 16; if (!free(x, z)) continue; const g = new THREE.Group(); const h = 5 + rnd() * 3; add(g, new THREE.CylinderGeometry(.12, .2, h, 6), 0xd9cfb8, 0, h / 2); for (let k = 0; k < 8; k++) { const l = add(g, new THREE.ConeGeometry(.16, 2, 4), 0x5c8a3f, 0, h, 0); l.rotation.set(0, k * .785, 1.95, 'YXZ'); l.translateY(.9); } g.position.set(x, H(x, z), z); scene.add(g); }
for (let i = 0; i < 46; i++) { const x = (rnd() - .5) * 74, z = (rnd() - .5) * 70, s = .25 + rnd() * .8; const m = add(scene, new THREE.DodecahedronGeometry(s, 0), 0x9b8f80, x, H(x, z) + s * .25, z); m.rotation.set(rnd() * 3, rnd() * 3, 0); }
// village and station
const HOUSE = [0xe9b44c, 0x4f9d9d, 0xd9695f, 0xf0e2c8];
VILLAGE.forEach(([x, z], i) => { const g = new THREE.Group(); add(g, new THREE.BoxGeometry(2.6, 1.7, 2.2), HOUSE[i], 0, .85); const r = add(g, new THREE.ConeGeometry(2.25, 1.2, 4), 0xa4553a, 0, 2.25); r.rotation.y = Math.PI / 4; r.scale.z = .9; add(g, new THREE.BoxGeometry(.5, .95, .06), 0x5b4030, .3, .48, 1.12); add(g, new THREE.BoxGeometry(.5, .5, .06), 0xffe6a3, -.65, 1, 1.12, { emissive: 0xffc765, emissiveIntensity: .9 }); g.position.set(x, H(x, z), z); g.rotation.y = i * .7 - .5; scene.add(g); });
{ const g = new THREE.Group(); add(g, new THREE.BoxGeometry(5, 2.3, 3.4), 0xb8473a, 0, 1.15); add(g, new THREE.BoxGeometry(5.4, .3, 3.8), 0xf0e2c8, 0, 2.4); add(g, new THREE.BoxGeometry(1.9, 1.6, .08), 0x3a3f42, 1, .8, 1.72); add(g, new THREE.BoxGeometry(1.1, 4, 1.1), 0xa83f34, -1.9, 2, -.6); add(g, new THREE.ConeGeometry(.95, .9, 4), 0xf0e2c8, -1.9, 4.45, -.6).rotation.y = .785; g.position.set(STATION[0], H(...STATION), STATION[1]); scene.add(g); }
// watchtower
{ const g = new THREE.Group(); for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const l = add(g, new THREE.CylinderGeometry(.12, .16, 6, 5), 0x6b4a2f, x, 3, z); l.rotation.set(z * -.06, 0, x * .06); } add(g, new THREE.BoxGeometry(3, .25, 3), 0x7d5836, 0, 6); add(g, new THREE.BoxGeometry(2.1, 1.5, 2.1), 0xc99a5b, 0, 6.9); add(g, new THREE.BoxGeometry(1.7, .6, 2.16), 0xffe6a3, 0, 7.05, 0, { emissive: 0xffc765, emissiveIntensity: .8 }); add(g, new THREE.ConeGeometry(2.15, 1.3, 4), 0x4f6b3c, 0, 8.3).rotation.y = .785; for (let k = 0; k < 7; k++) add(g, new THREE.BoxGeometry(.7, .07, .07), 0x8d6640, 1.35, .6 + k * .8, 1.2); g.position.set(TOWER[0], H(...TOWER), TOWER[1]); scene.add(g); }

// sensors
const label = t => { const c = document.createElement('canvas'); c.width = 512; c.height = 96; const x = c.getContext('2d'); x.font = '600 44px Fredoka, system-ui'; const w = x.measureText(t).width + 56; x.fillStyle = 'rgba(24,30,34,.82)'; x.beginPath(); x.roundRect(256 - w / 2, 8, w, 76, 38); x.fill(); x.fillStyle = '#f7f1e6'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(t, 256, 48); const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace; const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tx, transparent: true, depthTest: false })); s.scale.set(6.4, 1.2, 1); s.renderOrder = 9; return s; };
try { await Promise.race([document.fonts.load('600 44px Fredoka'), new Promise(r => setTimeout(r, 1500))]); } catch {}
const sensors = PLACES.map(([name, , x, z]) => {
  const g = new THREE.Group(), y = H(x, z);
  add(g, new THREE.CylinderGeometry(.55, .7, .35, 6), 0x8d857a, 0, .15); add(g, new THREE.CylinderGeometry(.09, .12, 3.4, 6), 0xe7e3da, 0, 1.8);
  const pan = add(g, new THREE.BoxGeometry(1.35, .08, .95), 0x22416b, 0, 3.5, 0, { roughness: .25, metalness: .4 }); pan.rotation.x = -.5;
  add(g, new THREE.BoxGeometry(.5, .36, .7), 0xf5f2ea, 0, 2.6, .25); add(g, new THREE.CylinderGeometry(.14, .14, .16, 8), 0x20242a, 0, 2.6, .66).rotation.x = Math.PI / 2;
  const led = new THREE.Mesh(new THREE.TorusGeometry(.5, .09, 8, 22), new THREE.MeshStandardMaterial({ color: 0x79e0a0, emissive: 0x49d487, emissiveIntensity: 1.4 })); led.rotation.x = Math.PI / 2; led.position.y = 1.35; g.add(led);
  const ring = new THREE.Mesh(new THREE.RingGeometry(1.5, 1.75, 40), new THREE.MeshBasicMaterial({ color: 0xff8a3d, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false })); ring.rotation.x = -Math.PI / 2; ring.position.y = .5; g.add(ring);
  const lb = label(name[0].toUpperCase() + name.slice(1)); lb.position.y = 5.1; g.add(lb);
  g.position.set(x, y, z); scene.add(g); return { g, led, ring, lb, x, y, z, state: 'calm' };
});
const LED = { calm: [0x79e0a0, 0x49d487], alert: [0xffb066, 0xff8a3d], watch: [0xffe08a, 0xffc93d], fire: [0xff7a6b, 0xff3b2d] };
const setLed = (s, k) => { s.state = k; s.led.material.color.set(LED[k][0]); s.led.material.emissive.set(LED[k][1]); };

// drone
const drone = new THREE.Group(), rotors = [];
add(drone, new THREE.BoxGeometry(1, .3, .7), 0xf5f2ea); add(drone, new THREE.SphereGeometry(.2, 8, 6), 0x22303a, 0, -.2, .35);
for (const [x, z] of [[-.85, -.7], [.85, -.7], [-.85, .7], [.85, .7]]) { const a = add(drone, new THREE.BoxGeometry(.12, .08, 1.1), 0x39434a, x / 2, 0, z / 2); a.rotation.y = Math.atan2(x, z); const r = add(drone, new THREE.CylinderGeometry(.48, .48, .03, 12), 0xff8a3d, x, .18, z, { transparent: true, opacity: .75 }); rotors.push(r); }
const beam = new THREE.Mesh(new THREE.ConeGeometry(2.1, 6, 24, 1, true).translate(0, -3, 0), new THREE.MeshBasicMaterial({ color: 0xbfeaff, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending })); drone.add(beam);
const HOME_D = new THREE.Vector3(TOWER[0], H(...TOWER) + 10.2, TOWER[1]); drone.position.copy(HOME_D); scene.add(drone);
// truck
const truck = new THREE.Group(), wheels = [];
add(truck, new THREE.BoxGeometry(1.25, 1, 2.1), 0xd8402f, 0, .95, -.35); add(truck, new THREE.BoxGeometry(1.2, .95, 1), 0xe6543f, 0, .9, 1.15); add(truck, new THREE.BoxGeometry(1.05, .4, .06), 0xbfe3ef, 0, 1.12, 1.66, { roughness: .2 }); add(truck, new THREE.BoxGeometry(1.3, .16, 3.1), 0xf0e2c8, 0, .62, .2); add(truck, new THREE.CylinderGeometry(.1, .1, 1.7, 6), 0xd9d4c8, 0, 1.6, -.2).rotation.x = 1.45;
const siren = add(truck, new THREE.BoxGeometry(.55, .18, .25), 0x6fb7ff, 0, 1.47, 1.1, { emissive: 0x2f8bff, emissiveIntensity: 0 });
for (const [x, z] of [[-.65, -1], [.65, -1], [-.65, 1.1], [.65, 1.1]]) { const w = add(truck, new THREE.CylinderGeometry(.36, .36, .26, 10), 0x24262a, x, .36, z); w.rotation.z = Math.PI / 2; wheels.push(w); }
const HOME_T = new THREE.Vector3(STATION[0] + 1, H(STATION[0] + 1, STATION[1] + 4), STATION[1] + 4); truck.position.copy(HOME_T); scene.add(truck);

// particles: fire, smoke, water
function pool(n, g, m) { const mesh = new THREE.InstancedMesh(g, m, n); mesh.frustumCulled = false; mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(mesh); const a = Array.from({ length: n }, () => ({ t: 1, life: 0 })); for (let i = 0; i < n; i++) { dummy.scale.setScalar(0); dummy.updateMatrix(); mesh.setMatrixAt(i, dummy.matrix); mesh.setColorAt(i, col.set(0xffffff)); } return { mesh, a, k: 0 }; }
const fireP = pool(phone ? 520 : 1300, new THREE.TetrahedronGeometry(.42), new THREE.MeshBasicMaterial({ toneMapped: false }));
const smokeP = pool(phone ? 150 : 340, new THREE.IcosahedronGeometry(.6, 0), new THREE.MeshStandardMaterial({ color: 0x8b8480, transparent: true, opacity: .42, flatShading: true, depthWrite: false }));
const waterP = pool(260, new THREE.IcosahedronGeometry(.16, 0), new THREE.MeshBasicMaterial({ color: 0xa9e3f5 }));
function emit(P, o) { P.a[P.k] = { t: 0, ...o }; P.k = (P.k + 1) % P.a.length; }
function step(P, dt, paint) { for (let i = 0; i < P.a.length; i++) { const q = P.a[i]; if (q.t >= q.life || !q.life) { if (!q.dead) { dummy.scale.setScalar(0); dummy.updateMatrix(); P.mesh.setMatrixAt(i, dummy.matrix); q.dead = true; } continue; } q.t += dt; q.vy += (q.g || 0) * dt; q.x += q.vx * dt; q.y += q.vy * dt; q.z += q.vz * dt; const f = q.t / q.life; dummy.position.set(q.x, q.y, q.z); dummy.rotation.set(q.r + q.t * 3, q.r * 2 + q.t * 2, 0); dummy.scale.setScalar(Math.max(0, paint(q, f, i))); dummy.updateMatrix(); P.mesh.setMatrixAt(i, dummy.matrix); } P.mesh.instanceMatrix.needsUpdate = true; if (P.mesh.instanceColor) P.mesh.instanceColor.needsUpdate = true; }
const fires = []; // {x,y,z,size,target}
const glow = [0, 1, 2].map(() => { const l = new THREE.PointLight(0xff7a2d, 0, 22, 1.6); scene.add(l); return l; });
const J = a => (Math.random() - .5) * a;
function ignite(x, z, size) { const f = { x, z, y: H(x, z), size: .1, target: size }; fires.push(f); return f; }
function burn(x, z, n) { const o = trees.map((t, i) => [i, Math.hypot(t.x - x, t.z - z)]).filter(([i]) => !trees[i].burnt).sort((a, b) => a[1] - b[1]).slice(0, n); o.forEach(([i], k) => setTimeout(() => { trees[i].burnt = 1; drawTree(i); flushTrees(); const f = ignite(trees[i].x, trees[i].z, 1); setTimeout(() => f.target = 0, 3800); health(); }, 350 + k * 210)); lost += o.length; }
function splash(x, y, z, n) { for (let i = 0; i < n; i++) emit(waterP, { x: x + J(1), y, z: z + J(1), vx: J(5), vy: 3 + Math.random() * 4, vz: J(5), g: -12, life: .9, r: 1 }); }

// ------------------------------------------------------------------ sound
let AC, sound = false; const beep = (f, d = .12, type = 'sine', v = .05, to) => { if (!sound) return; AC ||= new AudioContext(); const o = AC.createOscillator(), g = AC.createGain(); o.type = type; o.frequency.value = f; if (to) o.frequency.linearRampToValueAtTime(to, AC.currentTime + d); g.gain.value = v; g.gain.exponentialRampToValueAtTime(.0001, AC.currentTime + d); o.connect(g).connect(AC.destination); o.start(); o.stop(AC.currentTime + d); };
$('snd').onclick = () => { sound = !sound; $('snd').textContent = sound ? 'Sound on' : 'Sound off'; $('snd').setAttribute('aria-pressed', sound); beep(520); };

// ------------------------------------------------------------------ models
const err = e => (e && e.message) || String(e), S = D.schema;
const rec = k => async (t, e) => { const r = e && REC[k][e.id + '|' + e.style]; if (!r) throw Error('This is a recording, so it only knows the messages of the game.'); return { answer: r.answer, p: r.p, ms: r.ms }; };
const ENGINES = {
  none: { n: 'No model', note: 'Play on your own.' },
  chrome: { n: 'Chrome Decisions API (recorded)', note: 'Chrome 158 with the experimental flag, on an Apple M4. Ran on the device.', f: rec('chrome') },
  eg2: { n: 'EmbeddingGemma 2 (recorded)', note: 'Through MediaPipe, on an Apple M4. Ran on the device.', f: rec('eg2') },
  haiku: { n: 'Claude Haiku 5.5 (recorded)', note: 'A general model in the cloud. It gives one answer and no probabilities.', f: rec('haiku') },
  sonnet: { n: 'Claude Sonnet 5.5 (recorded)', note: 'A larger general model in the cloud.', f: rec('sonnet') },
  liveChrome: { n: 'Chrome Decisions API (live)', note: 'Needs desktop Chrome with chrome://flags#decisions-api turned on.', live: 1, load: async () => {
    if (!('DecisionModel' in self)) throw Error('This browser does not have the Decisions API. Turn on chrome://flags#decisions-api in Chrome and restart.');
    const m = await DecisionModel.create({ questions: [{ id: 'a', type: 'choice', prompt: S.prompt, options: S.options }] });
    return async t => { const t0 = performance.now(), r = (await m.decide(t)).a; return { answer: r.label, p: r.probabilities, ms: performance.now() - t0 }; }; } },
  liveEG: { n: 'EmbeddingGemma 2 (live, 165 MB)', note: 'Downloads the model once from Hugging Face and runs it in this tab. Needs WebGPU.', live: 1, load: async () => {
    const v = 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-decision@1.2.3', { DecisionMaker, FilesetResolver } = await import(v + '/decision_bundle.mjs');
    const m = await DecisionMaker.createFromOptions(await FilesetResolver.forDecisionTasks(v + '/wasm'), { maxNumTokens: 512, baseOptions: { delegate: 'GPU', modelAssetPath: 'https://huggingface.co/litert-community/embeddinggemma-2-text-270m-litert-lm/resolve/main/embeddinggemma-2-text-270m.litertlm' } });
    return async t => { const t0 = performance.now(), r = await m.evaluateChoice(t, { instructions: S.prompt, options: S.options, normalizePrior: true }); return { answer: r.selectedKey, p: r.probabilities, ms: performance.now() - t0 }; }; } } };
$('eng').innerHTML = Object.entries(ENGINES).map(([k, e]) => `<option value="${k}">${e.n}</option>`).join('');
let E = ENGINES.none;
$('bars').innerHTML = ACTIONS.map(a => `<div class="b" data-a="${a}"><span>${INFO[a].t}</span><div><i></i></div><em></em></div>`).join('');
function bars(r) { for (const b of $('bars').children) { const a = b.dataset.a, p = r ? (r.p ? r.p[a] : r.answer === a ? 1 : 0) : 0; b.classList.toggle('win', !!r && r.answer === a); b.querySelector('i').style.width = p * 100 + '%'; b.querySelector('em').textContent = !r ? '' : r.p ? (p < .01 ? '<1%' : Math.round(p * 100) + '%') : r.answer === a ? 'chosen' : ''; } }
$('eng').onchange = async () => {
  E = ENGINES[$('eng').value]; bars(null); $('mnote').textContent = 'Waiting for a message.'; $('own').hidden = true; $('engNote').textContent = E.note;
  if (E.load && !E.f) { const b = document.createElement('button'); b.className = 'small'; b.textContent = 'Load it'; $('engNote').append(document.createElement('br'), b); b.onclick = async () => { b.disabled = true; b.textContent = 'Loading…'; try { E.f = await E.load(); b.remove(); $('own').hidden = false; $('mnote').textContent = 'Ready.'; ask(); } catch (x) { b.disabled = false; b.textContent = 'Try again'; $('mnote').textContent = err(x); } }; }
  else if (E.f) { $('own').hidden = !E.live; ask(); }
};
$('eng').value = 'chrome'; $('engNote').textContent = ENGINES.chrome.note; E = ENGINES.chrome;
$('ownB').onclick = async () => { try { $('mnote').textContent = 'Thinking…'; const r = await E.f($('ownT').value); bars(r); $('mnote').textContent = `Your message: ${r.answer}, in ${Math.round(r.ms)} ms.`; } catch (x) { $('mnote').textContent = err(x); } };
$('fold').onclick = () => { $('model').classList.toggle('closed'); $('fold').textContent = $('model').classList.contains('closed') ? '+' : '–'; };
if (phone) $('fold').click();
let opinion = null;
async function ask() { opinion = null; if (!cur || !E.f) return; const e = cur; try { const r = await E.f(e.text[e.style], e); if (cur !== e) return; opinion = r; if ($('auto').checked || answered) showOpinion(); else { bars(null); $('mnote').textContent = 'It has decided. You will see it after you choose.'; } } catch (x) { $('mnote').textContent = err(x); } }
function showOpinion() { if (!opinion) return; bars(opinion); const right = opinion.answer === cur.label; $('mnote').textContent = `${right ? 'Same as the rule book' : 'Rule book says ' + cur.label}${opinion.ms ? `. ${Math.round(opinion.ms)} ms` : ''}.`; }

// ------------------------------------------------------------------ game
let deck = [], k = -1, cur = null, answered = false, lost = 0, res = {}, log = [], timer = 0, limit = 0, focus = null, playing = false;
const wait = ms => new Promise(r => setTimeout(r, ms));
function toast(t, kind = '') { const o = $('toast'); o.textContent = t; o.className = 'on ' + kind; clearTimeout(toast.h); toast.h = setTimeout(() => o.className = kind, 3000); }
function health() { const burnt = trees.filter(t => t.burnt).length, h = Math.round(100 * (1 - burnt / 130)); const v = Math.max(0, h); $('hp').textContent = v + '%'; $('hb').style.width = v + '%'; $('hb').style.background = v > 65 ? '' : v > 35 ? 'linear-gradient(90deg,#d9962e,#ffd166)' : 'linear-gradient(90deg,#c23b2e,#ff8a6b)'; return v; }
function hud() { $('turn').textContent = playing ? `${Math.min(k + 1, 12)}/12` : '–'; $('rd').textContent = res.drone ?? '–'; $('rb').textContent = res.brigade ?? '–'; for (const b of $('acts').children) b.disabled = answered || res[b.dataset.a] === 0; }
$('acts').innerHTML = ACTIONS.map((a, i) => `<button data-a="${a}">${INFO[a].i}<span>${INFO[a].t}</span><small>${INFO[a].s} · ${i + 1}</small></button>`).join('');
for (const b of $('acts').children) b.onclick = () => choose(b.dataset.a);
addEventListener('keydown', e => { if (/TEXTAREA|SELECT|INPUT/.test(e.target.tagName)) return; if (e.key >= '1' && e.key <= '4' && cur && !answered) { const b = $('acts').children[e.key - 1]; if (!b.disabled) choose(b.dataset.a); } if (e.key === 'r') $('rules').hidden = !$('rules').hidden; });
$('rulesBtn').onclick = () => $('rules').hidden = false; $('rulesX').onclick = () => $('rules').hidden = true;
$('go').onclick = begin; $('again').onclick = begin;
function shuffle(a) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function begin() {
  $('start').hidden = $('end').hidden = true; trees.forEach(t => t.burnt = 0); for (let i = 0; i < N; i++) drawTree(i); flushTrees(); fires.length = 0; lost = 0; log = []; res = { drone: 6, brigade: 4 }; limit = +$('oTime').value; playing = true;
  const st = $('oStyle').value, all = ['numbers', 'spanish', 'words_no_echo'];
  deck = shuffle(ACTIONS.flatMap(a => shuffle(D.events.filter(e => e.label === a)).slice(0, 3))).map(e => ({ ...e, style: st === 'mix' ? all[Math.floor(Math.random() * 3)] : st }));
  k = -1; health(); sensors.forEach(s => setLed(s, 'calm')); next();
}
async function next() {
  k++; if (k >= deck.length) return finish();
  cur = deck[k]; answered = false; opinion = null; const s = sensors[placeOf(cur)]; setLed(s, 'alert'); focus = s; beep(660, .16, 'sine', .05, 880);
  $('msg').hidden = false; $('place').textContent = PLACES[placeOf(cur)][0].replace(/^./, c => c.toUpperCase()); $('style').textContent = STYLE[cur.style]; $('text').textContent = cur.text[cur.style]; bars(null); timer = limit; hud();
  if (E.f) { $('mnote').textContent = 'Thinking…'; await ask(); } else $('mnote').textContent = E === ENGINES.none ? 'No model selected.' : 'Load the model to see its decision.';
  if ($('auto').checked && E.f && playing) { const me = cur; await wait(1700); if (cur === me && !answered) { const a = opinion?.answer || 'ignore'; choose(res[a] === 0 ? 'monitor' : a, true); } }
}
const COST = { brigade: { ignore: 11, monitor: 9, drone: 4 }, drone: { ignore: 7, monitor: 4, brigade: 0 }, monitor: { ignore: 2, drone: 0, brigade: 0 }, ignore: { monitor: 0, drone: 0, brigade: 0 } };
async function choose(a, byModel = false) {
  if (answered || !cur) return; answered = true; const e = cur, s = sensors[placeOf(e)], right = a === e.label, c = right ? 0 : COST[e.label][a] || 0; if (res[a] > 0) res[a]--; hud();
  log.push({ e, a, model: null, byModel }); beep(right ? 780 : 220, .18, right ? 'triangle' : 'sawtooth', .05); showOpinion();
  const bad = e.label === 'brigade' ? ignite(s.x + 1.8, s.z + 1.2, right ? 1.45 : 2.3) : null;
  if (a === 'drone') await flyDrone(s, right); else if (a === 'brigade') await driveTruck(s, bad); else if (a === 'monitor') { setLed(s, 'watch'); await wait(700); } else await wait(400);
  if (c) { setLed(s, 'fire'); if (!bad) ignite(s.x + 1.8, s.z + 1.2, 2.1); burn(s.x + 1.8, s.z + 1.2, c); beep(140, .5, 'sawtooth', .04, 70); }
  toast(right ? { ignore: 'Right. Nothing to do here.', monitor: 'Right. The sensor stays on watch.', drone: 'Right. The drone checked the spot in time.', brigade: 'Right. The brigade got there before it spread.' }[a] : c ? `The rule book said ${e.label}. The fire took ${c} trees.` : `The rule book said ${e.label}. No damage, but it cost you a resource or some attention.`, right ? 'good' : 'bad');
  log.at(-1).model = opinion?.answer ?? null; showOpinion();
  await wait(c ? 2600 : 1500); if (bad) bad.target = 0; fires.forEach(f => f.target = 0); setLed(s, 'calm'); if (playing) next();
}
function tween(ms, fn) { return new Promise(r => { const t0 = performance.now(); (function f() { const q = Math.min(1, (performance.now() - t0) / ms); fn(q * q * (3 - 2 * q), q); q < 1 ? requestAnimationFrame(f) : r(); })(); }); }
async function flyDrone(s, ok) { const a = drone.position.clone(), b = new THREE.Vector3(s.x + 1.2, s.y + 7.5, s.z + 1); await tween(1300, q => { drone.position.lerpVectors(a, b, q); drone.position.y += Math.sin(q * Math.PI) * 2.5; drone.rotation.y = Math.atan2(b.x - a.x, b.z - a.z); }); await tween(1000, (q, r) => { beam.material.opacity = Math.sin(r * Math.PI) * .34; drone.position.x = b.x + Math.sin(r * 6.3) * .9; }); if (ok) splash(s.x, s.y + 1.5, s.z, 26); const c = drone.position.clone(); tween(1400, q => drone.position.lerpVectors(c, HOME_D, q)); }
async function driveTruck(s, fire) {
  const a = truck.position.clone(), b = new THREE.Vector3(s.x - 1.8, 0, s.z + 3.2); siren.material.emissiveIntensity = 2.4; beep(700, .6, 'square', .02, 950);
  const go = (p, q, ms) => tween(ms, t => { truck.position.lerpVectors(p, q, t); const { x, z } = truck.position; truck.position.y = Math.max(H(x, z), H(riverX(z), z) + .9 * (Math.abs(x - riverX(z)) < 3 ? 1 : 0)); truck.rotation.y = Math.atan2(q.x - p.x, q.z - p.z); wheels.forEach(w => w.rotation.x += .3); if (Math.random() < .35) emit(smokeP, { x: x + J(.6), y: truck.position.y + .3, z: z + J(.6), vx: J(.6), vy: .5, vz: J(.6), life: .8, r: J(6), small: .45 }); });
  await go(a, b, 1700);
  await tween(1300, () => { for (let i = 0; i < 4; i++) { const d = .85; emit(waterP, { x: truck.position.x, y: truck.position.y + 1.8, z: truck.position.z, vx: (s.x + 1.8 - truck.position.x) / d + J(1.6), vy: 5.2 + J(1), vz: (s.z + 1.2 - truck.position.z) / d + J(1.6), g: -11, life: .95, r: 1 }); } });
  if (fire) fire.target = 0; siren.material.emissiveIntensity = 0; const c = truck.position.clone(); go(c, HOME_T, 1900);
}
function finish() {
  playing = false; const last = cur; cur = null; $('msg').hidden = true; focus = null; hud(); const me = log.filter(l => l.a === l.e.label).length, seen = log.filter(l => l.model), mo = seen.filter(l => l.model === l.e.label).length, h = health();
  $('eT').textContent = h > 85 ? 'The forest is still standing.' : h > 55 ? 'You lost part of the forest.' : 'It was a hard night for the forest.';
  $('eB').innerHTML = `<div class="big"><div><span>${log[0]?.byModel ? 'Decisions' : 'You'}</span><b>${me}/12</b></div>${seen.length ? `<div><span>${E.n.replace(/ \(.*/, '')}</span><b>${mo}/${seen.length}</b></div>` : ''}<div><span>Forest</span><b>${h}%</b></div></div><div class="scroll"><table><tr><th>Message</th><th>Rule book</th><th>${log[0]?.byModel ? 'Played' : 'You'}</th><th>Model</th></tr>${log.map(l => `<tr><td>${STYLE[l.e.style]}, ${PLACES[placeOf(l.e)][0]}</td><td>${l.e.label}</td><td class="${l.a === l.e.label ? 'y' : 'n'}">${l.a}</td><td class="${l.model ? l.model === l.e.label ? 'y' : 'n' : ''}">${l.model || '–'}</td></tr>`).join('')}</table></div>`;
  $('end').hidden = false;
}
setInterval(() => { if (!playing || !limit || answered || !cur) { $('timer').textContent = ''; return; } timer--; $('timer').textContent = Math.max(0, timer) + ' s'; if (timer <= 0) choose('ignore'); }, 1000);

// ------------------------------------------------------------------ loop
function size() { renderer.setSize(innerWidth, innerHeight, false); cam.aspect = innerWidth / innerHeight; cam.fov = innerWidth < innerHeight ? 58 : 42; cam.updateProjectionMatrix(); }
addEventListener('resize', size); size();
const clock = new THREE.Clock(), tgt = new THREE.Vector3(), v = new THREE.Vector3(); let acc = 0;
function frame() {
  const dt = Math.min(.05, clock.getDelta()), t = clock.elapsedTime;
  if (focus && !calm) { tgt.set(focus.x * .62, 1, focus.z * .62 + 5); } else tgt.set(0, 1, 0);
  v.copy(tgt).sub(ctl.target).multiplyScalar(1 - Math.exp(-dt * 1.6)); ctl.target.add(v); cam.position.add(v);
  if (!calm && !playing) { const a = dt * .045; const x = cam.position.x, z = cam.position.z; cam.position.x = x * Math.cos(a) - z * Math.sin(a); cam.position.z = x * Math.sin(a) + z * Math.cos(a); }
  ctl.update();
  rotors.forEach(r => r.rotation.y += dt * 30); if (drone.position.distanceTo(HOME_D) < .4) drone.position.y = HOME_D.y + Math.sin(t * 1.7) * .25;
  sensors.forEach((s, i) => { s.led.material.emissiveIntensity = s.state === 'calm' ? 1 + Math.sin(t * 1.6 + i) * .4 : 2.4 + Math.sin(t * 8) * 1.4; const on = s === focus && cur && !answered; s.ring.material.opacity = on ? .75 * (1 - (t * .9 % 1)) : 0; s.ring.scale.setScalar(on ? 1 + (t * .9 % 1) * 2 : 1); s.lb.material.opacity += ((s === focus || !playing ? 1 : .55) - s.lb.material.opacity) * .1; s.lb.scale.set(s === focus ? 7.6 : 6, s === focus ? 1.43 : 1.13, 1); });
  if (siren.material.emissiveIntensity) siren.material.emissive.set(Math.sin(t * 16) > 0 ? 0x2f8bff : 0xff3b2d);
  acc += dt; const tick = acc > .03; if (tick) acc = 0;
  for (let i = fires.length - 1; i >= 0; i--) { const f = fires[i]; f.size += (f.target - f.size) * dt * 1.5; if (f.target === 0 && f.size < .05) { fires.splice(i, 1); continue; } if (tick) { const n = f.size > 1.2 ? 5 : 3; for (let j = 0; j < n; j++) emit(fireP, { x: f.x + J(1.7 * f.size), y: f.y + .1, z: f.z + J(1.7 * f.size), vx: J(.7), vy: 1.6 + Math.random() * 2.6 * f.size, vz: J(.7), life: .55 + Math.random() * .6, r: J(9), s: f.size }); if (Math.random() < .34) emit(smokeP, { x: f.x + J(1), y: f.y + 2.2 * f.size, z: f.z + J(1), vx: .5 + J(.4), vy: 1.5 + Math.random(), vz: J(.5), life: 3.2 + Math.random() * 1.6, r: J(9), small: .6 + f.size * .7 }); } }
  step(fireP, dt, (q, f, i) => { fireP.mesh.setColorAt(i, col.set(f < .25 ? 0xfff0a8 : f < .5 ? 0xffb13d : f < .78 ? 0xff6a24 : 0xb92c18)); return (1 - f) * (.6 + q.s * 1.1); });
  step(smokeP, dt, (q, f) => Math.sin(Math.min(1, f * 1.15) * Math.PI) * (q.small || .8) * (1 + f * 1.5)); step(waterP, dt, (q, f) => 1 - f * .5);
  const big = [...fires].sort((a, b) => b.size - a.size); glow.forEach((l, i) => { const f = big[i]; l.intensity = f ? f.size * (80 + Math.sin(t * 13 + i * 2) * 22) : 0; if (f) l.position.set(f.x, f.y + 2.2, f.z); });
  renderer.render(scene, cam); requestAnimationFrame(frame);
}
hud(); frame();
window.__fw = { begin, choose, ignite, burn, state: () => ({ k, cur, answered, res, log }), cam, ctl, sensors };
