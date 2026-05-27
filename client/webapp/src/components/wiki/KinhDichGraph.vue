<script setup>
/**
 * KinhDichGraph — D3 force-layout visualization 64 quẻ + cross-ref network.
 *
 * Uses zero deps: vanilla SVG + force simulation.
 * Edge types: sequential (cyc), pair (đối ngẫu), thuan (8 thuần), crossref.
 */
import { ref, onMounted, onUnmounted, computed, watch } from "vue";

const data = ref({ nodes: [], edges: [] });
const loading = ref(false);
const error = ref("");
const hoverNode = ref(null);
const selectedNode = ref(null);

const showSequential = ref(false);
const showPair = ref(true);
const showThuan = ref(true);
const showCrossref = ref(true);

const SVG_W = 900;
const SVG_H = 700;

const groupColor = {
  "thuong-kinh": "#fbbf24",
  "ha-kinh": "#c4b5fd",
  "thuan": "#dc2626",
};
const edgeColor = {
  "sequential": "#94a3b8",
  "pair": "#fbbf24",
  "thuan": "#dc2626",
  "crossref": "#a78bfa",
};

const nodes = ref([]);
const edges = ref([]);
let simulation = null;
let animFrameId = null;
const tick = ref(0);

async function loadGraph() {
  loading.value = true;
  try {
    const r = await fetch("/api/yi-wiki/kinh-dich/graph");
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    data.value = d;
    // Init positions in spiral
    const N = d.nodes.length;
    nodes.value = d.nodes.map((n, i) => {
      const angle = (i / N) * Math.PI * 2;
      const r = 250;
      return {
        ...n,
        x: SVG_W / 2 + r * Math.cos(angle),
        y: SVG_H / 2 + r * Math.sin(angle),
        vx: 0, vy: 0,
      };
    });
    edges.value = d.edges.map(e => ({
      ...e,
      sourceNode: nodes.value.find(n => n.id === e.source),
      targetNode: nodes.value.find(n => n.id === e.target),
    }));
    startSimulation();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

// Lightweight force simulation (no d3 dep)
function startSimulation() {
  let alpha = 1;
  const cool = 0.985;
  function step() {
    if (alpha < 0.005) {
      animFrameId = null;
      return;
    }
    // Repulsion between all pairs (O(N²) — OK với N=64)
    const REPEL = 1800;
    for (let i = 0; i < nodes.value.length; i++) {
      for (let j = i + 1; j < nodes.value.length; j++) {
        const a = nodes.value[i], b = nodes.value[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d2 = dx * dx + dy * dy + 1;
        const f = REPEL / d2;
        const dlen = Math.sqrt(d2);
        const fx = (dx / dlen) * f;
        const fy = (dy / dlen) * f;
        a.vx -= fx * alpha;
        a.vy -= fy * alpha;
        b.vx += fx * alpha;
        b.vy += fy * alpha;
      }
    }
    // Spring force per edge (only visible types)
    for (const e of edges.value) {
      if (!isEdgeVisible(e.type)) continue;
      const a = e.sourceNode, b = e.targetNode;
      if (!a || !b) continue;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) + 1;
      const target = e.type === "pair" ? 60 : e.type === "thuan" ? 120 : 100;
      const f = (d - target) * 0.04;
      const fx = (dx / d) * f;
      const fy = (dy / d) * f;
      a.vx += fx * alpha;
      a.vy += fy * alpha;
      b.vx -= fx * alpha;
      b.vy -= fy * alpha;
    }
    // Centering + damping
    for (const n of nodes.value) {
      n.vx += (SVG_W / 2 - n.x) * 0.0015 * alpha;
      n.vy += (SVG_H / 2 - n.y) * 0.0015 * alpha;
      n.vx *= 0.85;
      n.vy *= 0.85;
      n.x += n.vx;
      n.y += n.vy;
      // Bounds
      n.x = Math.max(30, Math.min(SVG_W - 30, n.x));
      n.y = Math.max(30, Math.min(SVG_H - 30, n.y));
    }
    alpha *= cool;
    tick.value++;
    animFrameId = requestAnimationFrame(step);
  }
  if (animFrameId) cancelAnimationFrame(animFrameId);
  step();
}

function isEdgeVisible(type) {
  if (type === "sequential") return showSequential.value;
  if (type === "pair") return showPair.value;
  if (type === "thuan") return showThuan.value;
  if (type === "crossref") return showCrossref.value;
  return true;
}

function relevantEdges() {
  return edges.value.filter(e => isEdgeVisible(e.type));
}

function nodeNeighbors(node) {
  if (!node) return new Set();
  const ids = new Set();
  for (const e of edges.value) {
    if (e.source === node.id) ids.add(e.target);
    if (e.target === node.id) ids.add(e.source);
  }
  return ids;
}

const highlightedNeighbors = computed(() => {
  return nodeNeighbors(selectedNode.value || hoverNode.value);
});

function nodeOpacity(n) {
  const hl = selectedNode.value || hoverNode.value;
  if (!hl) return 1;
  if (n.id === hl.id) return 1;
  return highlightedNeighbors.value.has(n.id) ? 1 : 0.25;
}

function edgeOpacity(e) {
  const hl = selectedNode.value || hoverNode.value;
  if (!hl) return 0.4;
  if (e.source === hl.id || e.target === hl.id) return 1;
  return 0.05;
}

// Watch settings → restart sim
watch([showSequential, showPair, showThuan, showCrossref], () => startSimulation());

onMounted(loadGraph);
onUnmounted(() => {
  if (animFrameId) cancelAnimationFrame(animFrameId);
});
</script>

<template>
  <div class="kdg">
    <header class="kdg-head">
      <h3>🕸️ Cross-ref Graph — 64 Quẻ + Mạng tâm pháp</h3>
      <div class="legend">
        <label><input type="checkbox" v-model="showPair" /> <span style="color:#fbbf24">●</span> Cặp đối ngẫu</label>
        <label><input type="checkbox" v-model="showThuan" /> <span style="color:#dc2626">●</span> 8 Quẻ thuần</label>
        <label><input type="checkbox" v-model="showCrossref" /> <span style="color:#a78bfa">●</span> Cross-ref</label>
        <label><input type="checkbox" v-model="showSequential" /> <span style="color:#94a3b8">●</span> Tuần tự 1→64</label>
      </div>
    </header>

    <div v-if="loading" class="kdg-status">Đang tải graph...</div>
    <div v-if="error" class="kdg-error">{{ error }}</div>

    <div class="kdg-svg-wrap" :style="{ height: SVG_H + 'px' }">
      <svg :viewBox="`0 0 ${SVG_W} ${SVG_H}`" preserveAspectRatio="xMidYMid meet" class="kdg-svg">
        <!-- Edges -->
        <line
          v-for="(e, i) in relevantEdges()"
          :key="`e${i}-${tick}`"
          :x1="e.sourceNode?.x" :y1="e.sourceNode?.y"
          :x2="e.targetNode?.x" :y2="e.targetNode?.y"
          :stroke="edgeColor[e.type]"
          :stroke-width="e.type === 'pair' ? 1.6 : 1"
          :stroke-opacity="edgeOpacity(e)"
        />

        <!-- Nodes -->
        <g
          v-for="n in nodes"
          :key="`n${n.id}`"
          :transform="`translate(${n.x},${n.y})`"
          :opacity="nodeOpacity(n)"
          @mouseenter="hoverNode = n"
          @mouseleave="hoverNode = null"
          @click="selectedNode = (selectedNode?.id === n.id) ? null : n"
          class="kdg-node"
        >
          <circle :r="(selectedNode?.id === n.id || hoverNode?.id === n.id) ? 18 : 14"
                  :fill="groupColor[n.group]"
                  :stroke="(selectedNode?.id === n.id) ? '#fff' : 'none'"
                  stroke-width="2" />
          <text text-anchor="middle" dy="0.35em" font-size="9" font-weight="bold" fill="#1e1b4b">
            {{ n.number }}
          </text>
        </g>
      </svg>
    </div>

    <!-- Info panel -->
    <div v-if="selectedNode || hoverNode" class="kdg-info">
      <div class="kdg-info-card">
        <span class="kdg-num">#{{ (selectedNode || hoverNode).number }}</span>
        <span class="kdg-name">{{ (selectedNode || hoverNode).name_vi }}</span>
        <span class="kdg-zh">{{ (selectedNode || hoverNode).name_zh }}</span>
        <span class="kdg-uni">{{ (selectedNode || hoverNode).structure_unicode }}</span>
        <span class="kdg-grp">{{ (selectedNode || hoverNode).upper }} / {{ (selectedNode || hoverNode).lower }}</span>
      </div>
    </div>

    <p class="kdg-foot">
      ⓘ Hover node → highlight neighbors. Click node → lock highlight. {{ data.nodes.length }} nodes / {{ relevantEdges().length }} edges visible.
    </p>
  </div>
</template>

<style scoped>
.kdg {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 8px;
  margin: 0.5rem 0;
}
.kdg-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  flex-wrap: wrap; gap: 0.8rem; margin-bottom: 0.6rem;
}
.kdg-head h3 { margin: 0; color: #a78bfa; font-size: 1rem; }
.legend {
  display: flex; gap: 0.8rem; flex-wrap: wrap;
  font-size: 0.78rem; color: #cbd5e1;
}
.legend label { display: flex; gap: 0.25rem; align-items: center; cursor: pointer; }
.kdg-svg-wrap {
  background: linear-gradient(135deg, #0f172a, #1e1b4b);
  border-radius: 6px;
  overflow: hidden;
}
.kdg-svg { width: 100%; height: 100%; display: block; }
.kdg-node { cursor: pointer; transition: opacity .2s; }
.kdg-node:hover circle { stroke: rgba(255,255,255,0.5); stroke-width: 2; }
.kdg-status, .kdg-error {
  padding: 1rem; text-align: center; color: #94a3b8;
}
.kdg-error { color: #f87171; }
.kdg-info {
  margin-top: 0.5rem;
}
.kdg-info-card {
  background: rgba(252, 211, 77, 0.08);
  border: 1px solid rgba(252, 211, 77, 0.3);
  padding: 0.4rem 0.8rem; border-radius: 6px;
  display: inline-flex; gap: 0.7rem; align-items: center; flex-wrap: wrap;
  font-size: 0.9rem;
}
.kdg-num { color: #fcd34d; font-weight: bold; }
.kdg-name { color: #fbbf24; font-weight: 600; }
.kdg-zh { color: #e0e7ff; }
.kdg-uni { font-size: 1.2rem; color: #c4b5fd; }
.kdg-grp { color: #94a3b8; font-size: 0.78rem; }
.kdg-foot {
  margin-top: 0.5rem; font-size: 0.75rem; color: #6b7280;
}
</style>
