<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const props = defineProps({
  universe: {
    type: Object,
    default: null
  },
  planetPositions: {
    type: Object,
    default: null
  },
  selectedTimeZone: {
    type: String,
    default: "Asia/Ho_Chi_Minh"
  },
  now: {
    type: Date,
    default: () => new Date()
  },
  natalData: {
    type: Object,
    default: null
  }
});

const canvasRef = ref(null);
const viewMode = ref("heliocentric");
const centerBodyName = ref("Mặt Trời");
let renderer;
let scene;
let camera;
let controls;
let solarSystem;
let planetPivots = [];
const planetCarriers = new Map();
const planetSpecsMap = new Map();
const bodyMeshes = [];
let earthSpinGroup;
let moonOrbitPivot;
let earthCarrier;
let sun;
let sunGlow;
let hexagramGroup;
let constellationGroup;
let natalGroup;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let frameId;
let lastTickMs = 0;

const binary = computed(() => props.universe?.yi_state?.hexagram_binary || "000000");
const currentName = computed(() => props.universe?.yi_state?.hexagram_name || "Đang chờ tín hiệu");
const timestamp = computed(() => props.universe?.timestamp_utc || "--");
const dataSource = computed(() => {
  const source = props.planetPositions?.source || "UNKNOWN";
  if (source === "NASA/JPL Horizons" && !props.planetPositions?.stale) return "LIVE NASA/JPL";
  if (source === "NASA/JPL Horizons" && props.planetPositions?.stale) return "CACHED NASA/JPL";
  if (source === "LOCAL_FALLBACK") return "FALLBACK LOCAL";
  return source;
});
const isLiveNasa = computed(
  () => props.planetPositions?.source === "NASA/JPL Horizons" && !props.planetPositions?.stale
);
const selectedTime = computed(() =>
  new Intl.DateTimeFormat("vi-VN", {
    timeZone: props.selectedTimeZone,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  }).format(props.now)
);
const hanoiTime = computed(() =>
  new Intl.DateTimeFormat("vi-VN", {
    timeZone: "Asia/Ho_Chi_Minh",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  }).format(props.now)
);

const planetSpecs = [
  { name: "Sao Thủy", au: 0.39, period: 88, size: 0.052, color: 0xa7a29a, speed: 0.018, start: 0.4 },
  { name: "Sao Kim", au: 0.72, period: 225, size: 0.083, color: 0xd7b56d, speed: 0.012, start: 1.25 },
  { name: "Trái Đất", au: 1, period: 365, size: 0.095, color: 0x1f6f86, speed: 0.009, start: 2.35, earth: true },
  { name: "Sao Hỏa", au: 1.52, period: 687, size: 0.065, color: 0xc4663f, speed: 0.007, start: 3.12 },
  { name: "Sao Mộc", au: 5.2, period: 4333, size: 0.19, color: 0xd2a06f, speed: 0.0032, start: 4.18 },
  { name: "Sao Thổ", au: 9.58, period: 10759, size: 0.165, color: 0xd6c28a, speed: 0.0025, start: 5.05, rings: true },
  { name: "Sao Thiên Vương", au: 19.2, period: 30687, size: 0.125, color: 0x8ed7d4, speed: 0.0018, start: 5.78 },
  { name: "Sao Hải Vương", au: 30.05, period: 60190, size: 0.12, color: 0x4f75d8, speed: 0.00145, start: 0.15 }
];

function orbitRadiusFromAu(au) {
  return 0.72 + Math.sqrt(au) * 0.72;
}

function visualRadiusFromAu(au) {
  return 0.72 + Math.sqrt(au) * 0.72;
}

function visualPositionFromRawVector(x, y, z) {
  const distance = Math.max(Math.sqrt(x * x + y * y + z * z), 0.0001);
  const scale = visualRadiusFromAu(distance) / distance;
  // Keep near-true geometric relationship; only slight vertical amplification for readability.
  const verticalScale = 1.2;
  return new THREE.Vector3(x * scale, z * scale * verticalScale, y * scale);
}

function latLonToVector3(lat, lon, radius = 0.47) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function initScene() {
  const canvas = canvasRef.value;
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(46, 1, 0.1, 100);
  camera.position.set(0, 4.6, 8.9);
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.minDistance = 6.8;
  controls.maxDistance = 14.5;
  controls.target.set(0, 0, 0);

  addStars();
  addSolarSystem();
  addConstellationGuide();
  addHexagramMarkers();

  const sunLight = new THREE.PointLight(0xfff1c2, 5.4, 18, 1.5);
  sunLight.position.set(0, 0, 0);
  scene.add(sunLight);
  scene.add(new THREE.AmbientLight(0x8ab7c2, 0.72));
  resize();
  animate();
  window.addEventListener("resize", resize);
  renderer.domElement.addEventListener("pointerdown", onPointerDown);
  if (props.natalData) {
    buildNatalScene();
    switchToNatal();
  }
}

function addStars() {
  const geometry = new THREE.BufferGeometry();
  const positions = [];
  for (let index = 0; index < 900; index += 1) {
    const a = Math.sin(index * 12.9898) * 43758.5453;
    const b = Math.sin(index * 78.233) * 24634.6345;
    const c = Math.sin(index * 37.719) * 13579.0246;
    positions.push(
      ((a - Math.floor(a)) - 0.5) * 20,
      ((b - Math.floor(b)) - 0.5) * 11,
      ((c - Math.floor(c)) - 0.5) * 14
    );
  }
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({ color: 0xe2f5f7, size: 0.015, transparent: true, opacity: 0.86 });
  scene.add(new THREE.Points(geometry, material));
}

function addSolarSystem() {
  solarSystem = new THREE.Group();
  scene.add(solarSystem);
  planetCarriers.clear();
  planetSpecsMap.clear();
  earthCarrier = null;

  sun = new THREE.Mesh(
    new THREE.SphereGeometry(0.38, 64, 48),
    new THREE.MeshBasicMaterial({ color: 0xffc857 })
  );
  sun.userData.bodyName = "Mặt Trời";
  bodyMeshes.push(sun);
  solarSystem.add(sun);

  sunGlow = new THREE.Mesh(
    new THREE.SphereGeometry(0.58, 64, 48),
    new THREE.MeshBasicMaterial({ color: 0xffc857, transparent: true, opacity: 0.14, depthWrite: false })
  );
  solarSystem.add(sunGlow);

  planetPivots = [];
  const livePlanets = props.planetPositions?.planets?.length === 8 ? props.planetPositions.planets : null;
  planetSpecs.forEach((spec) => {
    const live = livePlanets?.find((planet) => planet.name_vi === spec.name);
    const merged = { ...spec, ...(live || {}) };
    planetSpecsMap.set(merged.name, merged);
    addPlanet(merged);
  });
  applyCenteredLayout();
}

function addPlanet(spec) {
  const orbitDistance = spec.distance_au || spec.au || spec.fallback_au;
  const radius = orbitRadiusFromAu(orbitDistance);
  solarSystem.add(makeOrbitLine(radius, spec.earth ? 0x99f6e4 : 0x7aa6ad, spec.earth ? 0.34 : 0.18));

  const pivot = new THREE.Group();
  pivot.rotation.y = props.planetPositions?.source === "NASA/JPL Horizons" ? 0 : spec.start;
  pivot.userData.speed = props.planetPositions?.source === "NASA/JPL Horizons" ? 0 : spec.speed;
  solarSystem.add(pivot);

  const carrier = new THREE.Group();
  const position = props.planetPositions?.source === "NASA/JPL Horizons"
    ? visualPositionFromRawVector(spec.x_au || 0, spec.y_au || 0, spec.z_au || 0)
    : new THREE.Vector3(radius, 0, 0);
  carrier.position.copy(position);
  carrier.userData.heliocentric = position.clone();
  carrier.userData.planetName = spec.name;
  pivot.add(carrier);
  planetCarriers.set(spec.name, carrier);

  if (spec.earth) {
    earthSpinGroup = makeEarth();
    carrier.add(earthSpinGroup);
    earthCarrier = carrier;

    moonOrbitPivot = new THREE.Group();
    carrier.add(moonOrbitPivot);
    moonOrbitPivot.add(makeOrbitLine(0.34, 0xdce5ec, 0.38));

    const moon = new THREE.Mesh(
      new THREE.SphereGeometry(0.055, 32, 24),
      new THREE.MeshStandardMaterial({ color: 0xdce5ec, roughness: 0.9 })
    );
    moon.position.set(0.34, 0, 0);
    moonOrbitPivot.add(moon);
  } else {
    const planet = new THREE.Mesh(
      new THREE.SphereGeometry(spec.size, 40, 28),
      new THREE.MeshStandardMaterial({
        color: spec.color,
        roughness: 0.76,
        metalness: 0.02,
        emissive: spec.color,
        emissiveIntensity: 0.035
      })
    );
    planet.userData.bodyName = spec.name;
    bodyMeshes.push(planet);
    carrier.add(planet);
    if (spec.rings) {
      const rings = new THREE.Mesh(
        new THREE.RingGeometry(spec.size * 1.45, spec.size * 2.1, 48),
        new THREE.MeshBasicMaterial({ color: 0xd9c98f, transparent: true, opacity: 0.5, side: THREE.DoubleSide })
      );
      rings.rotation.x = Math.PI / 2.55;
      carrier.add(rings);
    }
  }

  // Add a larger invisible hit area so clicking bodies is reliable.
  const hitRadius = spec.earth ? 0.22 : Math.max(spec.size * 1.8, 0.14);
  const hitArea = new THREE.Mesh(
    new THREE.SphereGeometry(hitRadius, 16, 12),
    new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false })
  );
  hitArea.userData.bodyName = spec.name;
  carrier.add(hitArea);
  bodyMeshes.push(hitArea);

  if (spec.earth || spec.au >= 1.5) {
    const label = makePlanetLabel(spec.name, spec.distance_au || spec.au, spec.period_days || spec.period);
    label.position.set(0, spec.size + 0.12, 0);
    carrier.add(label);
  }
  planetPivots.push(pivot);
}

function applyCenteredLayout() {
  const center =
    centerBodyName.value === "Mặt Trời"
      ? { x_au: 0, y_au: 0, z_au: 0 }
      : planetSpecsMap.get(centerBodyName.value) || { x_au: 0, y_au: 0, z_au: 0 };

  planetCarriers.forEach((carrier, name) => {
    const spec = planetSpecsMap.get(name);
    if (!spec || typeof spec.x_au !== "number") {
      if (carrier.userData.heliocentric) carrier.position.copy(carrier.userData.heliocentric);
      return;
    }
    const rx = (spec.x_au || 0) - (center.x_au || 0);
    const ry = (spec.y_au || 0) - (center.y_au || 0);
    const rz = (spec.z_au || 0) - (center.z_au || 0);
    carrier.position.copy(visualPositionFromRawVector(rx, ry, rz));
  });

  if (sun) {
    const sx = 0 - (center.x_au || 0);
    const sy = 0 - (center.y_au || 0);
    const sz = 0 - (center.z_au || 0);
    sun.position.copy(visualPositionFromRawVector(sx, sy, sz));
    sun.visible = true;
  }
  if (sunGlow && sun) {
    sunGlow.position.copy(sun.position);
    sunGlow.visible = true;
  }
}

function switchToGeocentric() {
  viewMode.value = "geocentric";
  centerBodyName.value = "Trái Đất";
  if (natalGroup) natalGroup.visible = false;
  setLiveVisible(true);
  applyCenteredLayout();
  controls.target.set(0, 0, 0);
  camera.position.set(0, 2.3, 4.2);
  controls.update();
}

function switchToHeliocentric() {
  viewMode.value = "heliocentric";
  centerBodyName.value = "Mặt Trời";
  if (natalGroup) natalGroup.visible = false;
  setLiveVisible(true);
  applyCenteredLayout();
  controls.target.set(0, 0, 0);
  camera.position.set(0, 4.6, 8.9);
  controls.update();
}

function onPointerDown(event) {
  if (!renderer || !camera) return;
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(bodyMeshes, true);
  if (hits.length) {
    const name = hits[0].object?.userData?.bodyName;
    if (name) {
      centerBodyName.value = name;
      viewMode.value = name === "Mặt Trời" ? "heliocentric" : "geocentric";
      applyCenteredLayout();
      controls.target.set(0, 0, 0);
      camera.position.set(0, 2.2, 4.1);
      controls.update();
    }
  }
}

function addConstellationGuide() {
  constellationGroup = new THREE.Group();
  const labels = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"];
  const radius = 3.9;
  labels.forEach((name, index) => {
    const angle = (index / labels.length) * Math.PI * 2;
    const x = Math.cos(angle) * radius;
    const z = Math.sin(angle) * radius;
    const marker = new THREE.Mesh(
      new THREE.SphereGeometry(0.014, 8, 8),
      new THREE.MeshBasicMaterial({ color: 0x99f6e4, transparent: true, opacity: 0.75 })
    );
    marker.position.set(x, 0, z);
    constellationGroup.add(marker);
    const label = makeTextSprite(name, "#9fe9e0");
    label.position.set(x * 1.07, 0.04, z * 1.07);
    constellationGroup.add(label);
  });
  scene.add(constellationGroup);
}

function makeTextSprite(text, color = "#f8fafc") {
  const canvas = document.createElement("canvas");
  canvas.width = 260;
  canvas.height = 72;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "rgba(2, 10, 14, 0.62)";
  ctx.fillRect(0, 14, canvas.width, 44);
  ctx.fillStyle = color;
  ctx.font = "600 24px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(text, canvas.width / 2, 43);
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(0.7, 0.19, 1);
  return sprite;
}

function makeEarth() {
  const group = new THREE.Group();
  group.rotation.y = -2.15;
  group.rotation.x = 0.16;

  const earthGeometry = new THREE.SphereGeometry(0.095, 96, 64);
  const earthMaterial = new THREE.MeshStandardMaterial({
    color: 0x1f6f86,
    roughness: 0.78,
    metalness: 0.02,
    emissive: 0x09252f,
    emissiveIntensity: 0.18
  });
  const earthMesh = new THREE.Mesh(earthGeometry, earthMaterial);
  earthMesh.userData.bodyName = "Trái Đất";
  bodyMeshes.push(earthMesh);
  group.add(earthMesh);

  const landMaterial = new THREE.LineBasicMaterial({ color: 0xb8e3d4, transparent: true, opacity: 0.62 });
  [
    [
      [8, 101],
      [20, 97],
      [37, 103],
      [52, 112],
      [59, 132]
    ],
    [
      [-36, 112],
      [-20, 122],
      [-7, 142],
      [3, 151]
    ],
    [
      [34, -10],
      [48, 12],
      [57, 38],
      [45, 80]
    ],
    [
      [-55, -70],
      [-34, -58],
      [-12, -77],
      [10, -82],
      [24, -98],
      [48, -124]
    ]
  ].forEach((line) => group.add(makeGeoLine(line, landMaterial, 0.099)));

  const vietnamBorder = [
    [23.39, 105.30],
    [22.65, 106.80],
    [21.55, 107.35],
    [21.03, 106.05],
    [20.25, 105.95],
    [19.25, 105.80],
    [18.40, 105.65],
    [17.20, 106.55],
    [16.05, 107.45],
    [14.95, 108.10],
    [13.75, 109.20],
    [12.20, 109.10],
    [10.85, 107.05],
    [9.65, 105.15],
    [8.65, 104.85],
    [10.10, 104.45],
    [11.10, 105.05],
    [12.60, 106.30],
    [14.45, 107.50],
    [16.90, 106.25],
    [18.70, 104.85],
    [20.85, 103.20],
    [22.55, 102.20],
    [23.39, 105.30]
  ];
  group.add(makeGeoLine(vietnamBorder, new THREE.LineBasicMaterial({ color: 0xffb020, linewidth: 2 }), 0.104));

  const hanoi = latLonToVector3(21.0278, 105.8342, 0.112);
  const starGeometry = new THREE.SphereGeometry(0.008, 18, 18);
  const starMaterial = new THREE.MeshBasicMaterial({ color: 0xffd166 });
  const hanoiStar = new THREE.Mesh(starGeometry, starMaterial);
  hanoiStar.position.copy(hanoi);
  hanoiStar.name = "hanoi-star";
  group.add(hanoiStar);

  const haloGeometry = new THREE.RingGeometry(0.014, 0.021, 24);
  const haloMaterial = new THREE.MeshBasicMaterial({ color: 0xffd166, transparent: true, opacity: 0.65, side: THREE.DoubleSide });
  const halo = new THREE.Mesh(haloGeometry, haloMaterial);
  halo.position.copy(hanoi.clone().multiplyScalar(1.012));
  halo.lookAt(new THREE.Vector3(0, 0, 0));
  group.add(halo);

  const cloudBand = new THREE.Mesh(
    new THREE.TorusGeometry(0.108, 0.0012, 8, 128),
    new THREE.MeshBasicMaterial({ color: 0xdffafa, transparent: true, opacity: 0.32 })
  );
  cloudBand.rotation.x = Math.PI / 2.5;
  group.add(cloudBand);
  return group;
}

function makePlanetLabel(name, au, period) {
  const canvas = document.createElement("canvas");
  canvas.width = 300;
  canvas.height = 92;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "rgba(5, 18, 21, 0.72)";
  ctx.strokeStyle = "rgba(153, 246, 228, 0.25)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(8, 8, 284, 76, 12);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#f8fafc";
  ctx.font = "700 22px system-ui, sans-serif";
  ctx.fillText(name, 24, 38);
  ctx.fillStyle = "#99f6e4";
  ctx.font = "600 15px system-ui, sans-serif";
  ctx.fillText(`${au} AU · ${period.toLocaleString("vi-VN")} ngày`, 24, 62);
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(0.62, 0.19, 1);
  return sprite;
}

function makeOrbitLine(radius, color, opacity) {
  const points = [];
  for (let index = 0; index <= 192; index += 1) {
    const angle = (index / 192) * Math.PI * 2;
    points.push(new THREE.Vector3(Math.cos(angle) * radius, 0, Math.sin(angle) * radius));
  }
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({ color, transparent: true, opacity });
  return new THREE.Line(geometry, material);
}

function makeGeoLine(points, material, radius) {
  const vectors = points.map(([lat, lon]) => latLonToVector3(lat, lon, radius));
  const geometry = new THREE.BufferGeometry().setFromPoints(vectors);
  return new THREE.Line(geometry, material);
}

function addHexagramMarkers() {
  hexagramGroup = new THREE.Group();
  for (let i = 0; i < 6; i += 1) {
    const isYang = binary.value[i] === "1";
    const geometry = new THREE.BoxGeometry(isYang ? 0.5 : 0.22, 0.03, 0.03);
    const material = new THREE.MeshBasicMaterial({ color: isYang ? 0x0f766e : 0xf59e0b });
    const marker = new THREE.Mesh(geometry, material);
    marker.position.set(2.85, (i - 2.5) * -0.13 - 1.45, 0.25);
    hexagramGroup.add(marker);
  }
  hexagramGroup.name = "line-markers";
  scene.add(hexagramGroup);
}

function refreshMarkers() {
  if (!scene) return;
  const old = scene.getObjectByName("line-markers");
  if (old) scene.remove(old);
  addHexagramMarkers();
}

// ---- NATAL MODE: lá số trên nền vũ trụ thật (additive, mặc định tắt) ----
const HANH_HEX = { thuy: 0x4a90d9, moc: 0x4caf50, hoa: 0xe05a4a, tho: 0xd4a82a, kim: 0x9aa0a6 };
const HANH_CSS = { thuy: "#8fbdee", moc: "#86d28f", hoa: "#f0897c", tho: "#e6c45a", kim: "#c2c7cc" };
const NATAL_BODY_VI = {
  sun: "Nhật", moon: "Nguyệt", mercury: "Thủy", venus: "Kim", mars: "Hỏa",
  jupiter: "Mộc", saturn: "Thổ", uranus: "Thiên", neptune: "Hải", pluto: "Diêm"
};

function eclipticVec(lonDeg, radius, y = 0) {
  const a = (lonDeg * Math.PI) / 180;
  return new THREE.Vector3(Math.cos(a) * radius, y, Math.sin(a) * radius);
}

function disposeNatal() {
  if (!natalGroup) return;
  natalGroup.traverse((obj) => {
    obj.geometry?.dispose?.();
    if (obj.material) {
      obj.material.map?.dispose?.();
      obj.material.dispose?.();
    }
  });
  scene.remove(natalGroup);
  natalGroup = null;
}

function buildNatalScene() {
  if (!scene || !props.natalData) return;
  disposeNatal();
  natalGroup = new THREE.Group();
  natalGroup.name = "natal-group";
  const data = props.natalData;
  const R_DIA = 2.35;
  const R_PLANET = 3.15;
  const R_ZOD = 3.9;

  // Trái Đất (tâm — geocentric)
  const earth = new THREE.Mesh(
    new THREE.SphereGeometry(0.16, 48, 32),
    new THREE.MeshStandardMaterial({ color: 0x2a6ea5, roughness: 0.82, emissive: 0x0b2838, emissiveIntensity: 0.22 })
  );
  natalGroup.add(earth);

  // vòng tham chiếu
  natalGroup.add(makeOrbitLine(R_DIA, 0xd4a82a, 0.16));
  natalGroup.add(makeOrbitLine(R_PLANET, 0x99f6e4, 0.1));

  // địa bàn 12 cung (ký hiệu, neo tiết khí) — Mệnh tô đậm
  (data.dia_ban?.cung || []).forEach((c) => {
    const css = HANH_CSS[c.hanh] || "#c5f8f1";
    const label = makeTextSprite(c.is_menh ? `${c.chi} ★` : c.chi, css);
    label.scale.set(c.is_menh ? 0.86 : 0.6, c.is_menh ? 0.23 : 0.16, 1);
    label.position.copy(eclipticVec(c.lon_center, R_DIA, 0.02));
    natalGroup.add(label);
    if (c.is_menh) {
      const marker = new THREE.Mesh(
        new THREE.SphereGeometry(0.05, 16, 12),
        new THREE.MeshBasicMaterial({ color: HANH_HEX[c.hanh] || 0xe05a4a })
      );
      marker.position.copy(eclipticVec(c.lon_center, R_DIA, 0));
      natalGroup.add(marker);
    }
  });

  // 10 thiên thể tại vị trí hoàng đạo THẬT
  (data.sky?.bodies || []).forEach((b) => {
    const isSun = b.name === "sun";
    const color = isSun ? 0xffc857 : b.name === "moon" ? 0xdce5ec : 0xc5d4d8;
    const dot = new THREE.Mesh(
      new THREE.SphereGeometry(isSun ? 0.07 : 0.045, 18, 14),
      new THREE.MeshBasicMaterial({ color })
    );
    dot.position.copy(eclipticVec(b.ecliptic_longitude, R_PLANET, 0));
    natalGroup.add(dot);
    const nm = NATAL_BODY_VI[b.name] || b.name;
    const label = makeTextSprite(b.is_retrograde && !isSun ? `${nm} ngh` : nm, isSun ? "#ffd98a" : "#cfe9e4");
    label.scale.set(0.46, 0.14, 1);
    label.position.copy(eclipticVec(b.ecliptic_longitude, R_PLANET, 0.15));
    natalGroup.add(label);
  });

  // cầu nối Mặt Trời (vạch đứt từ tâm ra vòng trời thật)
  const sunLon = data.sky?.sun_longitude;
  if (typeof sunLon === "number") {
    const line = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([eclipticVec(sunLon, R_DIA * 0.5, 0), eclipticVec(sunLon, R_ZOD, 0)]),
      new THREE.LineDashedMaterial({ color: 0xffc857, dashSize: 0.12, gapSize: 0.08, transparent: true, opacity: 0.85 })
    );
    line.computeLineDistances();
    natalGroup.add(line);
  }

  natalGroup.visible = false;
  scene.add(natalGroup);
}

function setLiveVisible(on) {
  if (solarSystem) solarSystem.visible = on;
  if (hexagramGroup) hexagramGroup.visible = on;
}

function switchToNatal() {
  if (!props.natalData) return;
  if (!natalGroup) buildNatalScene();
  if (!natalGroup) return;
  viewMode.value = "natal";
  setLiveVisible(false);
  natalGroup.visible = true;
  controls.target.set(0, 0, 0);
  camera.position.set(0, 4.4, 6.6);
  controls.update();
}

function resize() {
  if (!renderer || !canvasRef.value) return;
  const parent = canvasRef.value.parentElement;
  const width = parent.clientWidth;
  const height = parent.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function animate() {
  frameId = requestAnimationFrame(animate);
  const nowMs = performance.now();
  const dtSec = lastTickMs ? (nowMs - lastTickMs) / 1000 : 0;
  lastTickMs = nowMs;

  if (!isLiveNasa.value) {
    planetPivots.forEach((pivot) => {
      // Keep non-live mode visually smooth but not exaggerated.
      pivot.rotation.y += pivot.userData.speed * Math.max(dtSec * 60, 1);
    });
  }
  if (earthSpinGroup) {
    // Near-real-time rotation: one turn per sidereal day (~86164s).
    earthSpinGroup.rotation.y += dtSec * (Math.PI * 2 / 86164);
  }
  if (moonOrbitPivot) {
    // Near-real-time lunar revolution: ~27.321661 days.
    moonOrbitPivot.rotation.y += dtSec * (Math.PI * 2 / (27.321661 * 86400));
  }
  if (sun) {
    sun.scale.setScalar(1 + Math.sin(nowMs / 900) * 0.025);
  }
  controls?.update();
  renderer.render(scene, camera);
}

onMounted(initScene);
onBeforeUnmount(() => {
  cancelAnimationFrame(frameId);
  lastTickMs = 0;
  window.removeEventListener("resize", resize);
  renderer?.domElement?.removeEventListener("pointerdown", onPointerDown);
  controls?.dispose();
  renderer?.dispose();
});
watch(binary, refreshMarkers);
watch(
  () => props.planetPositions?.timestamp_utc,
  () => {
    if (!scene || !solarSystem) return;
    scene.remove(solarSystem);
    bodyMeshes.length = 0;
    addSolarSystem();
  }
);
watch(
  () => props.natalData,
  (val) => {
    if (!scene) return;
    if (val) {
      buildNatalScene();
      switchToNatal();
    } else {
      switchToHeliocentric();
    }
  }
);
</script>

<template>
  <div class="universe-core">
    <canvas ref="canvasRef" aria-label="Lõi năng lượng quẻ"></canvas>
    <div class="core-overlay">
      <p class="mono-label">{{ timestamp }}</p>
      <h2>{{ currentName }}</h2>
      <div class="binary-readout">{{ binary }}</div>
      <p class="source-badge" :class="{ cached: dataSource.includes('CACHED') || dataSource.includes('FALLBACK') }">
        {{ dataSource }}
      </p>
    </div>
    <div class="space-legend">
      <div>
        <span>Múi giờ đang xem</span>
        <strong>{{ selectedTimeZone }}</strong>
        <b>{{ selectedTime }}</b>
      </div>
      <div>
        <span>Ngôi sao Hà Nội</span>
        <strong>Asia/Ho_Chi_Minh</strong>
        <b>{{ hanoiTime }}</b>
      </div>
    </div>
    <div class="core-footer">
      <span>Giữ chuột để xoay, cuộn để phóng to/thu nhỏ · bấm vào bất kỳ thiên thể để lấy làm tâm</span>
      <span>
        {{
          isLiveNasa
            ? `Vị trí NASA/JPL snapshot · tâm hiện tại: ${centerBodyName}`
            : `Mô phỏng quỹ đạo + dữ liệu dự phòng · tâm hiện tại: ${centerBodyName}`
        }}
      </span>
    </div>
    <div class="view-controls">
      <button type="button" :class="{ active: viewMode === 'heliocentric' }" @click="switchToHeliocentric">Nhật tâm</button>
      <button type="button" :class="{ active: viewMode === 'geocentric' }" @click="switchToGeocentric">Địa tâm</button>
      <button v-if="natalData" type="button" :class="{ active: viewMode === 'natal' }" @click="switchToNatal">Lá số</button>
    </div>
  </div>
</template>

<style scoped>
.source-badge {
  margin: 0.5rem 0 0;
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.56rem;
  border-radius: 999px;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
  border: 1px solid rgba(153, 246, 228, 0.36);
  color: #9af8eb;
  background: rgba(9, 25, 30, 0.58);
}

.source-badge.cached {
  border-color: rgba(251, 191, 36, 0.5);
  color: #facc7a;
}

.view-controls {
  position: absolute;
  left: 28px;
  bottom: 58px;
  display: inline-flex;
  gap: 8px;
}

.view-controls button {
  border: 1px solid rgba(153, 246, 228, 0.4);
  background: rgba(5, 18, 21, 0.7);
  color: #c5f8f1;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.view-controls button.active {
  background: rgba(15, 118, 110, 0.8);
  color: #f8fffd;
}

@media (max-width: 560px) {
  .view-controls {
    left: 18px;
    bottom: 18px;
  }
}
</style>
