<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import {
  castLucHao,
  getApiBaseDisplay,
  lucHaoFailureHint,
  portMismatchSetupHint,
  probeYiChronosBackend
} from "../lib/api";
import {
  EARTHLY_BRANCHES as branchesUtil,
  TRIGRAM_BITS as trigramBitsUtil,
  TRIGRAM_BY_NUMBER as trigramByNumberUtil,
  buildFormulaText,
  computeMaiHoaState,
  zonedDateParts,
} from "../utils/maiHoaTime.js";
import { computeCastEnergy } from "../utils/castEnergy.js";

const props = defineProps({
  now: {
    type: Date,
    required: true
  },
  selectedTimeZone: {
    type: String,
    default: "Asia/Ho_Chi_Minh"
  }
});
const emit = defineEmits(["cast-result", "open-result-page"]);

const canvasRef = ref(null);
const castPadRef = ref(null);
let renderer;
let scene;
let camera;
let controls;
let frameId;
let clockGroup;
/** @type {{ lineYang: THREE.MeshPhysicalMaterial; lineYin: THREE.MeshStandardMaterial; petal: THREE.MeshPhysicalMaterial; bronze: THREE.MeshStandardMaterial; glow: THREE.MeshBasicMaterial } | null} */
let sharedMaterials = null;
let upperTrigramRoot;
let lowerTrigramRoot;
let movingWedge;
let pearlCore;
let petalsGroup;
let branchDotGroup;
let innerLotusRing;
let lastVisualUpper;
let lastVisualLower;
let lastVisualMoving;
let castStartMs = 0;
/** Con trỏ đang giữ vùng gieo (pointer capture) */
let activeCastPointerId = null;
const isCasting = ref(false);
let castPathLength = 0;
let castEvents = 0;
let lastPointer = null;
const castStatus = ref("Sẵn sàng gieo");
const castDurationMs = ref(0);
const castEmotionBpm = ref(0);
const castEnergyScore = ref(0);
const questionText = ref("");
const selectedQuestionTopic = ref("none");
const lucHaoLoading = ref(false);
const lucHaoError = ref("");
const lucHaoState = ref(null);
const backendProbe = ref({ loading: true, result: null });
const questionTopics = [
  { id: "family", label: "Gia đình", prompt: "Gia đình đang vận động theo hướng nào trong thời gian gần?" },
  { id: "health", label: "Sức khỏe", prompt: "Tình trạng sức khỏe hiện tại và hướng cân bằng sắp tới ra sao?" },
  { id: "work", label: "Công việc", prompt: "Công việc sắp tới thuận hay nghịch, nên tiến theo hướng nào?" },
  { id: "finance", label: "Tiền tài", prompt: "Dòng tiền/tài lộc trong giai đoạn này có hanh thông không?" },
  { id: "plan", label: "Dự định", prompt: "Dự định này có nên triển khai ngay hay cần lùi nhịp?" },
  { id: "manual", label: "Nhập tay", prompt: "" },
  { id: "none", label: "Không chọn", prompt: "Luận tổng quát theo tín hiệu hiện tại" }
];

// Re-export shared names for the rest of the component (extracted to ../utils/maiHoaTime.js).
const earthlyBranches = branchesUtil;
const trigramByNumber = trigramByNumberUtil;
const TRIGRAM_BITS = trigramBitsUtil;

const maiHoaState = computed(() =>
  computeMaiHoaState(props.now, props.selectedTimeZone)
);

const formulaText = computed(() => buildFormulaText(maiHoaState.value));

const castHint = computed(() => {
  if (isCasting.value) return "Đang đồng bộ: giữ chuột và di chuyển tự nhiên theo nhịp cảm xúc.";
  if (!castDurationMs.value) return "Nhắm mắt nghĩ về điều muốn hỏi, giữ chuột và buông khi đã rõ ý.";
  return `Lần gieo gần nhất: ${castDurationMs.value}ms · Nhịp ${castEmotionBpm.value} bpm · Điểm năng lượng ${castEnergyScore.value}/100`;
});

const lucHaoVerdictClass = computed(() => {
  const tag = lucHaoState.value?.verdict?.tag;
  if (tag === "favorable") return "good";
  if (tag === "caution") return "warn";
  return "neutral";
});

const activeTopicPrompt = computed(() => {
  const topic = questionTopics.find((item) => item.id === selectedQuestionTopic.value);
  return topic?.prompt || "";
});

const finalQuestionText = computed(() => {
  const manual = questionText.value.trim();
  if (selectedQuestionTopic.value === "manual") {
    return manual || "Luận tổng quát theo tín hiệu hiện tại";
  }
  if (manual) return manual;
  return activeTopicPrompt.value || "Luận tổng quát theo tín hiệu hiện tại";
});

/** Vật liệu dùng lại (không dispose theo từng hào khi rebuild quẻ) */
const extraDisposableMaterials = [];

function trackMaterial(mat) {
  extraDisposableMaterials.push(mat);
  return mat;
}

function initScene() {
  const canvas = canvasRef.value;
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0c10);
  scene.fog = new THREE.FogExp2(0x0d1018, 0.042);

  camera = new THREE.PerspectiveCamera(40, 1, 0.1, 120);
  camera.position.set(0, 1.15, 6.35);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enablePan = false;
  controls.enableZoom = true;
  controls.minDistance = 3.9;
  controls.maxDistance = 10.5;
  controls.enableDamping = true;
  controls.dampingFactor = 0.065;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.32;
  controls.target.set(0, 0.05, 0);

  scene.add(new THREE.HemisphereLight(0xf2e6d5, 0x1a2230, 0.52));
  const sun = new THREE.DirectionalLight(0xfff2e6, 1.12);
  sun.position.set(-5, 8, 5.5);
  scene.add(sun);
  const cool = new THREE.DirectionalLight(0xa8b8ee, 0.34);
  cool.position.set(6, 2.5, -5.5);
  scene.add(cool);

  sharedMaterials = {
    lineYang: trackMaterial(
      new THREE.MeshPhysicalMaterial({
        color: 0xe6c068,
        metalness: 0.48,
        roughness: 0.26,
        emissive: 0x1f1406,
        emissiveIntensity: 0.09,
        clearcoat: 0.82,
        clearcoatRoughness: 0.16
      })
    ),
    lineYin: trackMaterial(
      new THREE.MeshStandardMaterial({
        color: 0x243142,
        metalness: 0.62,
        roughness: 0.4,
        emissive: 0x06090f,
        emissiveIntensity: 0.2
      })
    ),
    petal: trackMaterial(
      new THREE.MeshPhysicalMaterial({
        color: 0xb87a87,
        metalness: 0.22,
        roughness: 0.36,
        transmission: 0.22,
        thickness: 0.45,
        transparent: true,
        opacity: 0.86,
        emissive: 0x2a1018,
        emissiveIntensity: 0.09,
        side: THREE.DoubleSide
      })
    ),
    bronze: trackMaterial(
      new THREE.MeshStandardMaterial({
        color: 0x58452f,
        metalness: 0.72,
        roughness: 0.34,
        emissive: 0x090705,
        emissiveIntensity: 0.14
      })
    ),
    glow: trackMaterial(
      new THREE.MeshBasicMaterial({
        color: 0xf5e8d8,
        transparent: true,
        opacity: 0.12,
        depthWrite: false,
        side: THREE.DoubleSide
      })
    )
  };

  addMaiHoaModel();
  resize();
  animate();
  window.addEventListener("resize", resize);
}

/** Chỉ gỡ mesh con và dispose geometry — giữ nguyên vật liệu chia sẻ */
function emptyTrigramGroup(group) {
  if (!group) return;
  while (group.children.length) {
    const ch = group.children[0];
    group.remove(ch);
    ch.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose();
    });
  }
}

function buildTrigram(prongName) {
  const bits = TRIGRAM_BITS[prongName];
  const root = new THREE.Group();
  if (!bits) return root;

  const lineW = 0.74;
  const lineH = 0.086;
  const lineZ = 0.046;
  const step = 0.165;

  for (let i = 0; i < 3; i++) {
    const y = (1 - i) * step;
    const stroke = bits[i];
    if (stroke === "1") {
      const bar = new THREE.Mesh(new THREE.BoxGeometry(lineW, lineH, lineZ), sharedMaterials.lineYang);
      bar.position.set(0, y, 0);
      root.add(bar);
    } else {
      const piece = lineW * 0.41;
      const gap = lineW * 0.09;
      const left = new THREE.Mesh(new THREE.BoxGeometry(piece, lineH, lineZ), sharedMaterials.lineYin);
      left.position.set(-(piece / 2 + gap / 2), y, 0);
      const right = new THREE.Mesh(new THREE.BoxGeometry(piece, lineH, lineZ), sharedMaterials.lineYin);
      right.position.set(piece / 2 + gap / 2, y, 0);
      root.add(left, right);
    }
  }
  root.rotation.x = THREE.MathUtils.degToRad(-6);
  return root;
}

function addMaiHoaModel() {
  clockGroup = new THREE.Group();
  scene.add(clockGroup);

  const pedestal = new THREE.Mesh(
    new THREE.CylinderGeometry(2.12, 2.34, 0.11, 72),
    sharedMaterials.bronze
  );
  pedestal.position.y = -1.12;
  clockGroup.add(pedestal);

  innerLotusRing = new THREE.Mesh(
    new THREE.TorusGeometry(1.92, 0.016, 10, 120),
    trackMaterial(
      new THREE.MeshStandardMaterial({
        color: 0xcfae62,
        metalness: 0.82,
        roughness: 0.24,
        emissive: 0x261c08,
        emissiveIntensity: 0.18
      })
    )
  );
  innerLotusRing.rotation.x = Math.PI / 2;
  innerLotusRing.position.y = -0.02;
  clockGroup.add(innerLotusRing);

  petalsGroup = new THREE.Group();
  clockGroup.add(petalsGroup);
  const petals = 14;
  for (let i = 0; i < petals; i++) {
    const ang = (i / petals) * Math.PI * 2;
    const petal = new THREE.Mesh(new THREE.PlaneGeometry(0.52, 0.92), sharedMaterials.petal);
    const r = 2.02;
    petal.position.set(Math.cos(ang) * r, 0.04 + Math.sin(ang * 3) * 0.035, Math.sin(ang) * r);
    const vx = petal.position.x;
    const vz = petal.position.z;
    petal.lookAt(vx * 0.06, 0.12, vz * 0.06);
    petal.rotateX(0.38 + (i % 4) * 0.035);
    petalsGroup.add(petal);
  }

  upperTrigramRoot = new THREE.Group();
  upperTrigramRoot.position.set(0, 0.58, 0);
  clockGroup.add(upperTrigramRoot);

  lowerTrigramRoot = new THREE.Group();
  lowerTrigramRoot.position.set(0, -0.56, 0);
  clockGroup.add(lowerTrigramRoot);

  const wedgeMat = trackMaterial(
    new THREE.MeshBasicMaterial({
      color: 0xf0b24a,
      transparent: true,
      opacity: 0.31,
      depthWrite: false,
      side: THREE.DoubleSide
    })
  );
  movingWedge = new THREE.Mesh(new THREE.RingGeometry(1.08, 1.62, 48, 1, 0, Math.PI / 3), wedgeMat);
  movingWedge.rotation.x = -Math.PI / 2;
  movingWedge.position.y = 0.06;
  clockGroup.add(movingWedge);

  pearlCore = new THREE.Mesh(
    new THREE.SphereGeometry(0.19, 48, 36),
    trackMaterial(
      new THREE.MeshPhysicalMaterial({
        color: 0xfdf6eb,
        metalness: 0.04,
        roughness: 0.08,
        transmission: 0.62,
        thickness: 0.75,
        ior: 1.52,
        emissive: 0x55392a,
        emissiveIntensity: 0.07,
        clearcoat: 1,
        clearcoatRoughness: 0.05
      })
    )
  );
  pearlCore.position.y = -0.01;
  clockGroup.add(pearlCore);

  branchDotGroup = new THREE.Group();
  branchDotGroup.position.y = -0.05;
  clockGroup.add(branchDotGroup);
  const dotMat = trackMaterial(
    new THREE.MeshStandardMaterial({
      color: 0x7d6c52,
      metalness: 0.38,
      roughness: 0.48,
      emissive: 0x151008,
      emissiveIntensity: 0.28
    })
  );
  for (let i = 0; i < 12; i++) {
    const ang = (i / 12) * Math.PI * 2;
    const dot = new THREE.Mesh(new THREE.SphereGeometry(0.042, 10, 8), dotMat);
    dot.position.set(Math.cos(ang) * 2.18, 0, Math.sin(ang) * 2.18);
    branchDotGroup.add(dot);
  }

  const halo = new THREE.Mesh(new THREE.RingGeometry(2.32, 2.55, 72), sharedMaterials.glow);
  halo.rotation.x = -Math.PI / 2;
  halo.position.y = -0.32;
  clockGroup.add(halo);

  lastVisualUpper = null;
  lastVisualLower = null;
  lastVisualMoving = null;
  updateClockVisuals();
}

function updateClockVisuals() {
  if (!upperTrigramRoot || !lowerTrigramRoot || !movingWedge) return;
  const value = maiHoaState.value;
  const uName = trigramByNumber[value.upper];
  const lName = trigramByNumber[value.lower];

  if (value.upper !== lastVisualUpper) {
    emptyTrigramGroup(upperTrigramRoot);
    upperTrigramRoot.add(buildTrigram(uName));
    lastVisualUpper = value.upper;
  }
  if (value.lower !== lastVisualLower) {
    emptyTrigramGroup(lowerTrigramRoot);
    lowerTrigramRoot.add(buildTrigram(lName));
    lastVisualLower = value.lower;
  }

  if (value.moving !== lastVisualMoving) {
    const wedgeMat = movingWedge.material;
    const slot = Math.max(0, Math.min(5, value.moving - 1));
    const start = (-slot / 6) * Math.PI * 2 - Math.PI / 6;
    movingWedge.geometry.dispose();
    movingWedge.geometry = new THREE.RingGeometry(1.08, 1.62, 48, 1, start, Math.PI / 3);
    movingWedge.material = wedgeMat;
    lastVisualMoving = value.moving;
  }

  upperTrigramRoot.rotation.y = (value.upper / 8) * Math.PI * 2 * 0.16;
  lowerTrigramRoot.rotation.y = -(value.lower / 8) * Math.PI * 2 * 0.16;
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
  const t = performance.now() / 1000;
  if (pearlCore) {
    const amp = isCasting.value ? 0.125 : 0.072;
    const s = 1 + Math.sin(t * (isCasting.value ? 3.9 : 2)) * amp;
    pearlCore.scale.setScalar(s);
    pearlCore.position.y = -0.01 + Math.sin(t * 2.8) * 0.022;
  }
  if (petalsGroup && sharedMaterials?.petal) {
    petalsGroup.rotation.y = t * 0.048;
    const ch = petalsGroup.children;
    for (let i = 0; i < ch.length; i++) {
      ch[i].rotation.z = Math.sin(t * 1.25 + i * 0.35) * 0.07;
    }
  }
  if (innerLotusRing) {
    innerLotusRing.rotation.z = Math.sin(t * 0.85) * 0.035;
  }
  if (clockGroup && isCasting.value) {
    clockGroup.rotation.y += 0.008;
    clockGroup.position.y = Math.sin(t * 9) * 0.032;
  } else if (clockGroup && !isCasting.value) {
    clockGroup.position.y = THREE.MathUtils.lerp(clockGroup.position.y, 0, 0.08);
  }
  controls?.update();
  renderer.render(scene, camera);
}

function getPointerFromEvent(event) {
  const rect = castPadRef.value?.getBoundingClientRect();
  if (!rect) return { x: 0, y: 0 };
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  };
}

function beginCastGesture(event) {
  if (lucHaoLoading.value) return;
  if (event.pointerType === "mouse" && event.button !== 0) return;
  if (isCasting.value) return;
  const el = castPadRef.value;
  if (!el) return;
  event.preventDefault();
  try {
    el.setPointerCapture(event.pointerId);
  } catch {
    /* một số trình duyệt không hỗ trợ capture trên nút không focus */
  }
  activeCastPointerId = event.pointerId;
  isCasting.value = true;
  castStatus.value = "Đang giữ — thả tay để gieo.";
  castStartMs = performance.now();
  castPathLength = 0;
  castEvents = 0;
  lastPointer = getPointerFromEvent(event);
}

function recordCastPointerMove(event) {
  if (!isCasting.value || event.pointerId !== activeCastPointerId) return;
  event.preventDefault();
  const point = getPointerFromEvent(event);
  if (lastPointer) {
    const dx = point.x - lastPointer.x;
    const dy = point.y - lastPointer.y;
    castPathLength += Math.sqrt(dx * dx + dy * dy);
  }
  castEvents += 1;
  lastPointer = point;
}

async function finishCastGesture() {
  if (!isCasting.value) return;

  const el = castPadRef.value;
  if (activeCastPointerId != null && el?.releasePointerCapture) {
    try {
      if (el.hasPointerCapture?.(activeCastPointerId)) el.releasePointerCapture(activeCastPointerId);
    } catch {
      /* ignore */
    }
  }
  activeCastPointerId = null;

  const duration = Math.max(performance.now() - castStartMs, 1);
  isCasting.value = false;

  const energy = computeCastEnergy({
    durationMs: duration,
    pathLengthPx: castPathLength,
    eventCount: castEvents,
  });
  castDurationMs.value = energy.durationMs;
  castEmotionBpm.value = energy.emotionBpm;
  castEnergyScore.value = energy.energyScore;
  castStatus.value = "Đã thả tay — đang luận Lục Hào...";
  lastPointer = null;

  await submitLucHaoCast();
}

function onCastPointerUp(event) {
  if (!isCasting.value || event.pointerId !== activeCastPointerId) return;
  event.preventDefault();
  void finishCastGesture();
}

function onWindowBlurUnsetCast() {
  if (!isCasting.value) return;
  activeCastPointerId = null;
  isCasting.value = false;
  lastPointer = null;
  castStatus.value = "Đã hủy gieo (mất tiêu điểm cửa sổ). Giữ tay trong ô rồi thử lại.";
}

function formatLocalIsoForZone(date, timeZone) {
  const parts = zonedDateParts(date, timeZone);
  const pad = (value) => String(value).padStart(2, "0");
  return `${parts.year}-${pad(parts.month)}-${pad(parts.day)}T${pad(parts.hour)}:${pad(parts.minute)}:${pad(parts.second)}`;
}

async function submitLucHaoCast() {
  lucHaoLoading.value = true;
  lucHaoError.value = "";
  try {
    const payload = {
      datetime_local: formatLocalIsoForZone(props.now, props.selectedTimeZone),
      timezone: props.selectedTimeZone,
      question_text: finalQuestionText.value,
      interaction_signal: {
        hold_duration_ms: castDurationMs.value,
        move_event_count: castEvents,
        path_length_px: Number(castPathLength.toFixed(2)),
        release_timestamp_ms: Date.now()
      }
    };
    const response = await castLucHao(payload);
    lucHaoState.value = response.luc_hao_state;
    emit("cast-result", {
      result: response.luc_hao_state,
      meta: {
        question_text: payload.question_text,
        timezone: payload.timezone,
        interaction_signal: payload.interaction_signal
      }
    });
    castStatus.value = "Đã luận xong - mở tab Kết quả Lục Hào để xem đầy đủ.";
  } catch (error) {
    lucHaoError.value = lucHaoFailureHint(error);
    castStatus.value = "Gieo xong nhưng chưa lấy được nghiệm từ server.";
  } finally {
    lucHaoLoading.value = false;
  }
}

const showBackendMismatch = computed(() => {
  const r = backendProbe.value.result;
  return Boolean(r && !r.ok);
});

const backendMismatchBody = computed(() => {
  const r = backendProbe.value.result;
  if (!r || r.ok) return "";
  const lines = [];
  if (r.message) lines.push(r.message);
  if (r.detail) lines.push(r.detail);
  if (r.snippet) lines.push(`Trích phản hồi: ${r.snippet}`);
  if (r.status != null) lines.push(`HTTP: ${r.status}`);
  lines.push(portMismatchSetupHint());
  lines.push(`Địa chỉ API: ${getApiBaseDisplay()}`);
  return lines.join("\n\n");
});

async function recheckBackend() {
  backendProbe.value = { loading: true, result: backendProbe.value.result };
  const result = await probeYiChronosBackend();
  backendProbe.value = { loading: false, result };
}

onMounted(() => {
  initScene();
  window.addEventListener("blur", onWindowBlurUnsetCast);
  void (async () => {
    const result = await probeYiChronosBackend();
    backendProbe.value = { loading: false, result };
  })();
});
onBeforeUnmount(() => {
  window.removeEventListener("blur", onWindowBlurUnsetCast);
  if (isCasting.value) {
    isCasting.value = false;
    activeCastPointerId = null;
    lastPointer = null;
  }
  cancelAnimationFrame(frameId);
  window.removeEventListener("resize", resize);
  emptyTrigramGroup(upperTrigramRoot);
  emptyTrigramGroup(lowerTrigramRoot);
  clockGroup?.traverse((obj) => {
    obj.geometry?.dispose();
  });
  for (const m of extraDisposableMaterials) {
    m.dispose?.();
  }
  extraDisposableMaterials.length = 0;
  sharedMaterials = null;
  controls?.dispose();
  renderer?.dispose();
});

watch(
  () => [maiHoaState.value.upper, maiHoaState.value.lower, maiHoaState.value.moving],
  () => updateClockVisuals()
);
</script>

<template>
  <section class="maihoa-clock-card panel" aria-label="Đồng hồ Mai Hoa Dịch Số">
    <div class="panel-title">
      <div>
        <h3>Đồng hồ Mai Hoa Dịch Số (3D)</h3>
        <small>Chạy theo múi giờ: {{ selectedTimeZone }}</small>
      </div>
    </div>
    <div class="clock-layout">
      <div class="clock-canvas-wrap">
        <canvas ref="canvasRef" aria-label="Mô hình 3D Mai Hoa"></canvas>
      </div>
      <aside class="clock-explain">
        <p>
          Hệ này chạy ngầm theo thời gian thực. Mỗi khi vào giờ địa chi mới (mỗi 2 giờ),
          quẻ có thể chuyển trạng thái.
        </p>
        <div v-if="backendProbe.loading && !backendProbe.result" class="backend-probe-loading">
          Đang kiểm tra backend YI-CHRONOS…
        </div>
        <div v-if="showBackendMismatch" class="backend-mismatch-banner" role="alert">
          <strong>Backend không đúng hoặc không phải YI-CHRONOS</strong>
          <p class="backend-mismatch-body">{{ backendMismatchBody }}</p>
          <button
            type="button"
            class="backend-recheck-btn"
            :disabled="backendProbe.loading"
            @click="recheckBackend"
          >
            {{ backendProbe.loading ? "Đang kiểm tra…" : "Kiểm tra lại backend" }}
          </button>
        </div>
        <div class="focus-guide">
          <h4>Gợi ý gieo quẻ (Focus Mode)</h4>
          <ol>
            <li>Nhắm mắt, nghĩ rõ việc muốn hỏi.</li>
            <li>Giữ tay / chuột trong vùng cảm ứng bên dưới.</li>
            <li>Mở mắt và thả tay khi đã suy nghĩ xong.</li>
            <li>Bạn có thể rê nhẹ để đo nhịp cảm xúc.</li>
          </ol>
          <p class="focus-note">
            Mục tiêu là đồng bộ ý niệm cá nhân với nhịp vận động của trường thời-không tại thời điểm gieo.
          </p>
          <label class="question-input">
            <span>Chủ đề sự việc muốn hỏi</span>
            <div class="question-topic-chips">
              <button
                v-for="topic in questionTopics"
                :key="topic.id"
                type="button"
                :class="{ active: selectedQuestionTopic === topic.id }"
                @click="selectedQuestionTopic = topic.id"
              >
                {{ topic.label }}
              </button>
            </div>
            <small class="question-topic-note">
              <template v-if="selectedQuestionTopic === 'manual'">
                Bạn đang ở chế độ nhập tay. Hãy mô tả rõ sự việc để định đối tượng quẻ.
              </template>
              <template v-else>
                {{ activeTopicPrompt }}
              </template>
            </small>
            <textarea
              v-model="questionText"
              rows="2"
              :placeholder="
                selectedQuestionTopic === 'manual'
                  ? 'Nhập tay sự việc muốn hỏi...'
                  : 'Có thể nhập thêm chi tiết để tăng độ chính xác (không bắt buộc)'
              "
            />
          </label>
          <div
            ref="castPadRef"
            class="cast-pad"
            tabindex="0"
            aria-label="Vùng giữ tay để gieo quẻ"
            @pointerdown="beginCastGesture"
            @pointermove="recordCastPointerMove"
            @pointerup="onCastPointerUp"
            @pointercancel="onCastPointerUp"
          >
            <strong>{{ isCasting ? "Đang gieo..." : "Giữ tay / chuột tại đây để gieo" }}</strong>
            <span>{{ castHint }}</span>
          </div>
          <div class="cast-metrics">
            <div>
              <span>Thời lượng giữ</span>
              <b>{{ castDurationMs }}ms</b>
            </div>
            <div>
              <span>Nhịp cảm xúc</span>
              <b>{{ castEmotionBpm }} bpm</b>
            </div>
            <div>
              <span>Năng lượng</span>
              <b>{{ castEnergyScore }}/100</b>
            </div>
          </div>
          <p class="cast-status">{{ castStatus }}</p>
          <p v-if="lucHaoLoading" class="cast-status">Đang đồng bộ dữ liệu Lục Hào...</p>
          <p v-if="lucHaoError" class="cast-error">{{ lucHaoError }}</p>
        </div>
        <div class="formula-item">
          <span>Quẻ Thượng</span>
          <strong>{{ formulaText.upper }}</strong>
          <b>{{ maiHoaState.upperTrigram }}</b>
        </div>
        <div class="formula-item">
          <span>Quẻ Hạ</span>
          <strong>{{ formulaText.lower }}</strong>
          <b>{{ maiHoaState.lowerTrigram }}</b>
        </div>
        <div class="formula-item">
          <span>Hào Động</span>
          <strong>{{ formulaText.moving }}</strong>
          <b>Hào {{ maiHoaState.moving }}</b>
        </div>
        <ul class="state-list">
          <li>Năm chi quy đổi: {{ maiHoaState.yearNum }}</li>
          <li>Tháng: {{ maiHoaState.monthNum }}</li>
          <li>Ngày: {{ maiHoaState.dayNum }}</li>
          <li>Giờ chi hiện tại: {{ maiHoaState.hourBranch }} ({{ maiHoaState.hourNum }})</li>
        </ul>
        <div v-if="lucHaoState" class="luc-hao-result">
          <h4>Tóm tắt nghiệm Lục Hào</h4>
          <p :class="['verdict', lucHaoVerdictClass]">
            {{ lucHaoState.verdict.text }}
          </p>
          <div class="result-grid compact">
            <div>
              <span>Quẻ chủ</span>
              <strong>{{ lucHaoState.primary_hexagram.name_vi }} ({{ lucHaoState.primary_hexagram.binary }})</strong>
            </div>
            <div>
              <span>Quẻ biến</span>
              <strong>{{ lucHaoState.transformed_hexagram.name_vi }} ({{ lucHaoState.transformed_hexagram.binary }})</strong>
            </div>
            <div>
              <span>Hào động</span>
              <strong>{{ lucHaoState.moving_lines.join(", ") || "Không có" }}</strong>
            </div>
            <div>
              <span>Thế / Ứng</span>
              <strong>Hào {{ lucHaoState.the_line }} / Hào {{ lucHaoState.ung_line }}</strong>
            </div>
          </div>
          <button class="open-result-btn" type="button" @click="emit('open-result-page')">
            Mở trang kết quả chi tiết
          </button>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
h3 {
  margin: 0;
  font-size: 16px;
}

.clock-layout {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(260px, 0.92fr);
  gap: 12px;
}

.clock-canvas-wrap {
  min-height: 340px;
  border-radius: 12px;
  border: 1px solid rgba(200, 160, 120, 0.18);
  box-shadow:
    inset 0 0 120px rgba(20, 8, 12, 0.55),
    0 12px 40px rgba(0, 0, 0, 0.35);
  background:
    radial-gradient(circle at 22% 18%, rgba(180, 100, 120, 0.14), transparent 45%),
    radial-gradient(circle at 82% 78%, rgba(90, 70, 48, 0.2), transparent 42%),
    radial-gradient(ellipse 120% 80% at 50% 108%, rgba(60, 40, 52, 0.35), transparent 55%),
    linear-gradient(168deg, #0d0a11 0%, #16101c 42%, #0a0c14 100%);
  overflow: hidden;
}

.clock-canvas-wrap canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.clock-explain {
  border: 1px solid #d3e6ea;
  border-radius: 8px;
  padding: 10px;
  background: #f8fcfd;
}

.clock-explain p {
  margin: 0 0 8px;
  color: #33525a;
  font-size: 13px;
  line-height: 1.45;
}

.backend-probe-loading {
  margin: 0 0 8px;
  font-size: 12px;
  color: #4b6a72;
}

.backend-mismatch-banner {
  margin: 0 0 10px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #c94c3d;
  background: #fff5f3;
  color: #3d2420;
}

.backend-mismatch-banner strong {
  display: block;
  font-size: 13px;
  color: #8b2e22;
}

.backend-mismatch-body {
  white-space: pre-wrap;
  font-size: 12px;
  line-height: 1.45;
  margin: 8px 0;
  color: #402a26;
}

.backend-recheck-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #c94c3d;
  background: #fff;
  color: #8b2e22;
  font-size: 12px;
  cursor: pointer;
}

.backend-recheck-btn:hover:not(:disabled) {
  background: #ffeae6;
}

.backend-recheck-btn:disabled {
  opacity: 0.65;
  cursor: wait;
}

.focus-guide {
  border: 1px solid #cfe3e7;
  background: #f3fbfd;
  border-radius: 8px;
  padding: 10px;
  margin: 10px 0;
}

.focus-guide h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #0f3f47;
}

.focus-guide ol {
  margin: 0 0 8px;
  padding-left: 18px;
  color: #2f5760;
  font-size: 13px;
  line-height: 1.45;
}

.focus-note {
  margin: 0 0 8px;
  color: #3e646d;
  font-size: 12px;
}

.question-input {
  display: block;
  margin-bottom: 8px;
}

.question-input span {
  display: block;
  font-size: 12px;
  color: #456871;
  font-weight: 700;
  margin-bottom: 4px;
}

.question-input textarea {
  width: 100%;
  border: 1px solid #c7dce1;
  border-radius: 8px;
  padding: 8px 10px;
  resize: vertical;
  font-size: 13px;
  font-family: inherit;
}
.question-topic-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}
.question-topic-chips button {
  border: 1px solid #c7dce1;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 700;
  color: #345a63;
  background: #f8fcfd;
  cursor: pointer;
}
.question-topic-chips button.active {
  border-color: #0f766e;
  background: #ccfbf1;
  color: #0f4f47;
}
.question-topic-note {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: #4b6a72;
}

.cast-pad {
  border: 1px dashed #7dc9d6;
  border-radius: 10px;
  min-height: 90px;
  background: linear-gradient(145deg, #0d2730, #143842);
  color: #dafbff;
  display: grid;
  place-items: center;
  padding: 8px;
  text-align: center;
  cursor: grab;
  user-select: none;
  touch-action: none;
}

.cast-pad:active {
  cursor: grabbing;
}

.cast-pad strong {
  display: block;
  font-size: 14px;
}

.cast-pad span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #9ee8f3;
  line-height: 1.35;
}

.cast-metrics {
  margin-top: 8px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
}

.cast-metrics div {
  border: 1px solid #d4e8ed;
  border-radius: 8px;
  background: #fff;
  padding: 6px;
}

.cast-metrics span,
.cast-metrics b {
  display: block;
  text-align: center;
}

.cast-metrics span {
  font-size: 11px;
  color: #5a7780;
}

.cast-metrics b {
  margin-top: 2px;
  color: #0f3d44;
  font-size: 13px;
}

.cast-status {
  margin: 8px 0 0;
  font-size: 12px;
  color: #1f5660;
  font-weight: 600;
}

.cast-error {
  margin: 6px 0 0;
  color: #8a1f1f;
  background: #ffe7e7;
  border: 1px solid #ffd3d3;
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 12px;
  white-space: pre-wrap;
}

.formula-item {
  border: 1px solid #d7e8ec;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 8px;
  background: white;
}

.formula-item span,
.formula-item strong,
.formula-item b {
  display: block;
}

.formula-item span {
  font-size: 11px;
  color: #567177;
  font-weight: 700;
}

.formula-item strong {
  margin-top: 3px;
  font-size: 13px;
  color: #0d3b3f;
  font-family: "SFMono-Regular", Consolas, monospace;
}

.formula-item b {
  margin-top: 4px;
  color: #0f766e;
  font-size: 14px;
}

.state-list {
  margin: 8px 0 0;
  padding-left: 18px;
  color: #365860;
  font-size: 13px;
  line-height: 1.5;
}

.luc-hao-result {
  margin-top: 10px;
  border-top: 1px solid #d5e7eb;
  padding-top: 10px;
}

.luc-hao-result h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #163f47;
}

.verdict {
  margin: 0 0 8px;
  border-radius: 8px;
  padding: 8px;
  font-size: 13px;
  font-weight: 600;
}

.verdict.good {
  background: #dcfce7;
  color: #14532d;
}

.verdict.warn {
  background: #fee2e2;
  color: #7f1d1d;
}

.verdict.neutral {
  background: #e0f2fe;
  color: #0f3f66;
}

.result-grid {
  display: grid;
  gap: 6px;
}

.result-grid.compact {
  grid-template-columns: 1fr;
}

.result-grid span,
.result-grid strong {
  display: block;
}

.result-grid span {
  font-size: 11px;
  color: #57737a;
}

.result-grid strong {
  color: #123940;
  font-size: 13px;
}

.open-result-btn {
  margin-top: 8px;
  border: 1px solid #1f8a7f;
  border-radius: 8px;
  background: #0f766e;
  color: #f3fffd;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

@media (max-width: 1120px) {
  .clock-layout {
    grid-template-columns: 1fr;
  }
}
</style>
