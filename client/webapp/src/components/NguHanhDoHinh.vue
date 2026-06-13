<script setup>
/**
 * ☯ Đồ hình tương tác Âm Dương — Thái cực · Tiên thiên · Hậu thiên · Hà Đồ.
 * Dữ liệu từ /api/tu-vi/do-hinh-co (bồi từ vòng đọc sâu Lê Văn Sửu p21-40).
 * Anh duyệt 2026-06-13: đầu tư đồ hình luôn; trục thời gian làm trục chính.
 *
 * SVG thuần, hover/click hiện diễn giải. Tọa độ 8 cung quanh vòng tròn theo
 * key vị trí ("trên", "trên-phải", ... thuận chiều kim đồng hồ).
 */
import { ref, computed, onMounted } from "vue";

const loading = ref(false);
const error = ref("");
const data = ref(null);
const tab = ref("thai_cuc");
const hovered = ref(null);

const TABS = [
  { id: "thai_cuc", label: "☯ Thái cực" },
  { id: "tien_thien", label: "Tiên thiên" },
  { id: "hau_thien", label: "Hậu thiên" },
  { id: "ha_do", label: "Hà Đồ" },
];

// vị trí 8 cung → (x, y) trên vòng bán kính R quanh tâm (cx, cy)
const POS_ANGLE = {
  "trên": -90, "trên-phải": -45, "phải": 0, "dưới-phải": 45,
  "dưới": 90, "dưới-trái": 135, "trái": 180, "trên-trái": -135,
};
function xy(pos, cx, cy, r) {
  const a = (POS_ANGLE[pos] * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
}

const HANH_COLOR = {
  "mộc": "#5ab07a", "hỏa": "#d6593a", "thổ": "#c0a878",
  "kim": "#dcdce6", "thủy": "#6ea0dc",
};

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const resp = await fetch("/api/tu-vi/do-hinh-co");
    const d = await resp.json();
    if (d.status !== "ok") throw new Error("API " + d.status);
    data.value = d;
  } catch (e) {
    error.value = "Không tải được đồ hình: " + (e?.message || e);
  } finally {
    loading.value = false;
  }
}
onMounted(load);

// trigram bars: lines = [hào dưới, giữa, trên]; vẽ từ trên xuống nên đảo
function barRows(lines) {
  return [...lines].reverse(); // index0 = hào thượng (vẽ trên cùng)
}

// Hà Đồ: vị trí ngũ phương → tọa độ (tránh object literal inline trong template)
const HADO_XY = {
  "trên": [120, 52], "dưới": [120, 188], "trái": [52, 120],
  "phải": [188, 120], "giữa": [120, 120],
};
function hadoXY(viTri) {
  return HADO_XY[viTri] || [120, 120];
}

const tienThien = computed(() => data.value?.tien_thien?.cung || []);
const hauThien = computed(() => data.value?.hau_thien?.cung || []);
const haDo = computed(() => data.value?.ha_do?.diem || []);
</script>

<template>
  <section class="dh-block">
    <div class="dh-tabs">
      <button v-for="t in TABS" :key="t.id" type="button"
        class="dh-tab" :class="{ active: tab === t.id }" @click="tab = t.id">
        {{ t.label }}
      </button>
    </div>

    <p v-if="loading" class="dh-note">Đang tải đồ hình…</p>
    <p v-else-if="error" class="dh-error">{{ error }}</p>

    <template v-else-if="data">
      <!-- ☯ THÁI CỰC -->
      <div v-show="tab === 'thai_cuc'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Thái cực đồ">
          <defs>
            <clipPath id="tc-clip"><circle cx="120" cy="120" r="100" /></clipPath>
          </defs>
          <g clip-path="url(#tc-clip)">
            <rect x="20" y="20" width="200" height="200" fill="#e9e4d6" />
            <!-- nửa đen (âm) + lưỡi S: hai nửa cá cắn đuôi -->
            <path d="M120,20 A100,100 0 0,1 120,220 A50,50 0 0,1 120,120 A50,50 0 0,0 120,20 Z"
              fill="#1c2230" />
            <circle cx="120" cy="70" r="16" fill="#e9e4d6" /><!-- điểm trắng trong đen -->
            <circle cx="120" cy="170" r="16" fill="#1c2230" /><!-- điểm đen trong trắng -->
          </g>
          <circle cx="120" cy="120" r="100" fill="none" stroke="#e8c95a" stroke-width="2" />
          <text x="120" y="16" text-anchor="middle" class="dh-axis">Dương ▲</text>
          <text x="120" y="236" text-anchor="middle" class="dh-axis">▼ Âm</text>
        </svg>
        <div class="dh-info">
          <p>{{ data.thai_cuc.mo_ta }}</p>
          <p class="dh-tacgia">✦ {{ data.thai_cuc.tac_gia }}</p>
          <ul>
            <li v-for="(t, i) in data.thai_cuc.tinh_chat" :key="i">{{ t }}</li>
          </ul>
        </div>
      </div>

      <!-- TIÊN THIÊN -->
      <div v-show="tab === 'tien_thien'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Tiên thiên bát quái">
          <circle cx="120" cy="120" r="104" fill="none" stroke="rgba(232,201,90,0.3)" stroke-width="1" />
          <g v-for="c in tienThien" :key="c.que.ten">
            <g :transform="`translate(${xy(c.pos,120,120,86)[0]},${xy(c.pos,120,120,86)[1]})`"
               class="dh-que" @mouseenter="hovered = c" @mouseleave="hovered = null">
              <!-- 3 hào -->
              <g v-for="(h, ri) in barRows(c.que.lines)" :key="ri">
                <rect v-if="h === 1" :x="-15" :y="ri * 7 - 9" width="30" height="4" rx="1"
                  :fill="HANH_COLOR[c.que.hanh]" />
                <template v-else>
                  <rect :x="-15" :y="ri * 7 - 9" width="12" height="4" rx="1" :fill="HANH_COLOR[c.que.hanh]" />
                  <rect :x="3" :y="ri * 7 - 9" width="12" height="4" rx="1" :fill="HANH_COLOR[c.que.hanh]" />
                </template>
              </g>
              <text :y="22" text-anchor="middle" class="dh-que-label">{{ c.que.ten }}</text>
            </g>
          </g>
          <text x="120" y="124" text-anchor="middle" class="dh-center">THỂ</text>
        </svg>
        <div class="dh-info">
          <p><b>{{ data.tien_thien.ten }}</b></p>
          <p>{{ data.tien_thien.y_nghia }}</p>
          <p v-if="hovered" class="dh-hover">
            {{ hovered.que.symbol }} <b>{{ hovered.que.ten }}</b> ({{ hovered.que.tuong }} · {{ hovered.que.hanh }})
            — đối tâm với <b>{{ hovered.doi_tam }}</b>, trái dấu âm dương = lực hút bền vững.
          </p>
        </div>
      </div>

      <!-- HẬU THIÊN -->
      <div v-show="tab === 'hau_thien'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Hậu thiên bát quái">
          <circle cx="120" cy="120" r="104" fill="none" stroke="rgba(232,201,90,0.3)" stroke-width="1" />
          <g v-for="c in hauThien" :key="c.que.ten">
            <g :transform="`translate(${xy(c.pos,120,120,86)[0]},${xy(c.pos,120,120,86)[1]})`"
               class="dh-que" @mouseenter="hovered = c" @mouseleave="hovered = null">
              <g v-for="(h, ri) in barRows(c.que.lines)" :key="ri">
                <rect v-if="h === 1" :x="-15" :y="ri * 7 - 9" width="30" height="4" rx="1"
                  :fill="HANH_COLOR[c.que.hanh]" />
                <template v-else>
                  <rect :x="-15" :y="ri * 7 - 9" width="12" height="4" rx="1" :fill="HANH_COLOR[c.que.hanh]" />
                  <rect :x="3" :y="ri * 7 - 9" width="12" height="4" rx="1" :fill="HANH_COLOR[c.que.hanh]" />
                </template>
              </g>
              <text :y="22" text-anchor="middle" class="dh-que-label">{{ c.que.ten }}</text>
              <text :y="32" text-anchor="middle" class="dh-que-sub">{{ c.huong }}</text>
            </g>
          </g>
          <text x="120" y="124" text-anchor="middle" class="dh-center">DỤNG</text>
        </svg>
        <div class="dh-info">
          <p><b>{{ data.hau_thien.ten }}</b></p>
          <p>{{ data.hau_thien.y_nghia }}</p>
          <p v-if="hovered" class="dh-hover">
            {{ hovered.que.symbol }} <b>{{ hovered.que.ten }}</b> — {{ hovered.huong }},
            {{ hovered.mua }} ({{ hovered.tiet }}): {{ hovered.giai }}
          </p>
        </div>
      </div>

      <!-- HÀ ĐỒ -->
      <div v-show="tab === 'ha_do'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Hà Đồ">
          <g v-for="d in haDo" :key="d.phuong">
            <g :transform="`translate(${hadoXY(d.vi_tri)[0]},${hadoXY(d.vi_tri)[1]})`"
               class="dh-hado" @mouseenter="hovered = d" @mouseleave="hovered = null">
              <circle r="26" :fill="HANH_COLOR[d.hanh] + '22'" :stroke="HANH_COLOR[d.hanh]" stroke-width="1.5" />
              <text y="-3" text-anchor="middle" class="dh-hado-num">{{ d.sinh }}<tspan class="dh-hado-sep"> · </tspan>{{ d.thanh }}</text>
              <text y="12" text-anchor="middle" class="dh-hado-hanh">{{ d.hanh }}</text>
            </g>
          </g>
          <line x1="120" y1="78" x2="120" y2="162" stroke="rgba(232,201,90,0.25)" stroke-dasharray="3 3" />
          <line x1="78" y1="120" x2="162" y2="120" stroke="rgba(232,201,90,0.25)" stroke-dasharray="3 3" />
        </svg>
        <div class="dh-info">
          <p><b>{{ data.ha_do.ten }}</b></p>
          <p>{{ data.ha_do.y_nghia }}</p>
          <p v-if="hovered && hovered.phuong" class="dh-hover">
            <b>{{ hovered.phuong }}</b> — số sinh <b>{{ hovered.sinh }}</b> (
            {{ hovered.sinh % 2 ? 'dương/lẻ' : 'âm/chẵn' }}) ↔ số thành <b>{{ hovered.thanh }}</b>,
            cách nhau 5 = hành <b>{{ hovered.hanh }}</b>.
          </p>
        </div>
      </div>

      <p class="dh-truc">🕓 Trục chính: {{ data.truc_chinh }}</p>
      <p class="dh-nguon">— {{ data.nguon }}</p>
    </template>
  </section>
</template>

<style scoped>
.dh-block {
  margin: 12px 0;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(232, 201, 90, 0.18);
  border-radius: 8px;
}
.dh-tabs { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.dh-tab {
  padding: 5px 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: var(--text-primary, rgba(230, 238, 245, 0.85));
  font-size: 12.5px;
  cursor: pointer;
}
.dh-tab.active { border-color: var(--accent-gold, #e8c95a); background: rgba(232, 201, 90, 0.12); color: var(--accent-gold, #e8c95a); }
.dh-note, .dh-error { font-size: 12.5px; color: var(--text-secondary, rgba(230,238,245,0.7)); }
.dh-error { color: #f5a08c; }
.dh-pane { display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start; }
.dh-svg {
  width: 240px; height: 240px; flex-shrink: 0;
  background: radial-gradient(circle at 50% 45%, rgba(232,201,90,0.05), transparent 70%);
  border-radius: 8px;
}
.dh-axis { fill: var(--text-secondary, rgba(230,238,245,0.5)); font-size: 9px; }
.dh-que { cursor: pointer; }
.dh-que:hover .dh-que-label { fill: var(--accent-gold, #e8c95a); }
.dh-que-label { fill: var(--text-primary, rgba(230,238,245,0.9)); font-size: 11px; }
.dh-que-sub { fill: var(--text-secondary, rgba(230,238,245,0.55)); font-size: 8.5px; }
.dh-center { fill: rgba(232,201,90,0.5); font-size: 13px; font-weight: 700; letter-spacing: 2px; }
.dh-hado { cursor: pointer; }
.dh-hado-num { fill: var(--text-primary, rgba(230,238,245,0.95)); font-size: 13px; font-weight: 600; }
.dh-hado-sep { fill: var(--text-secondary, rgba(230,238,245,0.5)); }
.dh-hado-hanh { fill: var(--text-secondary, rgba(230,238,245,0.7)); font-size: 9px; }
.dh-info { flex: 1; min-width: 200px; }
.dh-info p { margin: 0 0 6px 0; font-size: 12.5px; line-height: 1.55; color: var(--text-secondary, rgba(230,238,245,0.8)); }
.dh-info b { color: var(--text-primary, rgba(230,238,245,0.92)); }
.dh-tacgia { color: var(--accent-gold, #e8c95a) !important; font-style: italic; }
.dh-info ul { margin: 4px 0 0 0; padding-left: 16px; }
.dh-info li { font-size: 12px; line-height: 1.5; color: var(--text-secondary, rgba(230,238,245,0.75)); }
.dh-hover {
  margin-top: 8px !important; padding: 7px 10px;
  background: rgba(232, 201, 90, 0.07);
  border-left: 2px solid rgba(232, 201, 90, 0.5);
  border-radius: 4px; font-size: 12px !important;
}
.dh-truc { margin: 10px 0 2px 0; font-size: 11.5px; color: var(--text-secondary, rgba(230,238,245,0.65)); }
.dh-nguon { margin: 0; font-size: 11px; font-style: italic; color: var(--text-secondary, rgba(230,238,245,0.5)); }
</style>
