<script setup>
/**
 * LuuNguyetTimeline — Grid 12 tháng × N năm cho Lưu Nguyệt.
 *
 * V4 — Cải tiến UI: so sánh paradigm giữa các năm cùng tháng âm.
 * Click cell → drawer chi tiết quẻ tháng đó.
 *
 * ⚠️ Iron Rule #4: KHÔNG cát/hung. Màu = Ngũ hành relation vs Khởi Sinh.
 */
import { ref, computed, onMounted } from "vue";
import HexagramSvg from "./diagrams/HexagramSvg.vue";
import { useActivePersonBirth } from "../../stores/useActivePersonBirth.js";

// Birth datetime — user nhập, không hardcode founder (privacy 2026-05-27).
const birthSolar = ref("");
const yearChiList = ref(["Giáp Thìn", "Ất Tỵ", "Bính Ngọ"]);  // 3 năm: 2024, 2025, 2026
const data = ref(null);
const loading = ref(false);
const error = ref("");
const selectedCell = ref(null);   // { month, year, name, ... }
const drawerHexagram = ref(null);

const MONTH_NAMES = [
  "Giêng","Hai","Ba","Tư","Năm","Sáu","Bảy","Tám","Chín","Mười","Mười Một","Chạp",
];

// Map Ngũ hành relation → màu cho cell
const RELATION_BG = {
  "ti_hoa":    "rgba(148, 163, 184, 0.15)",  // grey — bình
  "A_sinh_B":  "rgba(52, 211, 153, 0.18)",   // green — nuôi
  "B_sinh_A":  "rgba(110, 231, 183, 0.18)",  // light green — được nuôi
  "A_khac_B":  "rgba(251, 191, 36, 0.18)",   // amber — áp
  "B_khac_A":  "rgba(248, 113, 113, 0.18)",  // red — bị áp
  "unknown":   "rgba(107, 114, 128, 0.1)",
};
const RELATION_LABEL = {
  "ti_hoa": "Tỉ hoà",
  "A_sinh_B": "Nuôi vũ trụ",
  "B_sinh_A": "Được vũ trụ nuôi",
  "A_khac_B": "Áp vũ trụ",
  "B_khac_A": "Vũ trụ áp Anh",
};

async function loadTimeline() {
  loading.value = true;
  error.value = "";
  try {
    const r = await fetch("/api/yi-wiki/luu-van/timeline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        birth_solar: birthSolar.value.replace("T", " "),
        year_chi_list: yearChiList.value,
      }),
    });
    if (!r.ok) {
      const t = await r.text();
      throw new Error(`HTTP ${r.status}: ${t}`);
    }
    data.value = await r.json();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function openCellDetail(cell, year, month) {
  if (!cell || cell.error) return;
  selectedCell.value = { ...cell, year, month };
  drawerHexagram.value = { loading: true };
  try {
    // Lookup quẻ number from upper/lower
    const r1 = await fetch("/api/yi-wiki/kinh-dich/list");
    const d1 = await r1.json();
    const found = (d1.hexagrams || []).find(
      h => h.upper === cell.chinh_upper && h.lower === cell.chinh_lower
    );
    if (!found) throw new Error("Không tìm thấy quẻ");
    const r2 = await fetch(`/api/yi-wiki/kinh-dich/que/${found.number}`);
    drawerHexagram.value = await r2.json();
  } catch (e) {
    drawerHexagram.value = { error: String(e.message || e) };
  }
}

function closeDrawer() {
  selectedCell.value = null;
  drawerHexagram.value = null;
}

function renderMd(s) {
  if (!s) return "";
  return s
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/_([^_]+)_/g, "<i>$1</i>")
    .replace(/\n/g, "<br>");
}

// MỘT NGUỒN: ngày sinh (dương) từ hồ sơ tài khoản; đổi profile → tự cập nhật + chạy lại.
useActivePersonBirth(birthSolar, { onReady: loadTimeline });
</script>

<template>
  <div class="lnt">
    <header class="lnt-head">
      <h3>📅 Timeline 12 Lưu Nguyệt × 3 năm — so sánh paradigm</h3>
      <p class="subtitle">
        Click 1 cell để xem chi tiết quẻ tháng đó. Màu cell = Ngũ hành relation vs Khởi Sinh.
      </p>
    </header>

    <div class="lnt-form">
      <label>
        <span>Sinh:</span>
        <input type="datetime-local" v-model="birthSolar" />
      </label>
      <label>
        <span>3 năm so sánh:</span>
        <input v-model="yearChiList[0]" placeholder="Giáp Thìn" />
        <input v-model="yearChiList[1]" placeholder="Ất Tỵ" />
        <input v-model="yearChiList[2]" placeholder="Bính Ngọ" />
      </label>
      <button class="btn-load" @click="loadTimeline" :disabled="loading">
        {{ loading ? '⏳' : '🔄 Tính' }}
      </button>
    </div>

    <!-- Legend -->
    <div class="lnt-legend">
      <span v-for="(label, rel) in RELATION_LABEL" :key="rel">
        <span class="legend-swatch" :style="{background: RELATION_BG[rel]}"></span>
        {{ label }}
      </span>
    </div>

    <div v-if="error" class="lvd-error">{{ error }}</div>

    <!-- Grid 12 × N -->
    <div v-if="data?.rows?.length" class="lnt-grid-wrap">
      <table class="lnt-grid">
        <thead>
          <tr>
            <th class="corner">Tháng âm</th>
            <th v-for="yc in data.years" :key="yc" class="th-year">
              <div>{{ yc }}</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data.rows" :key="row.month">
            <th class="th-month">{{ MONTH_NAMES[row.month - 1] }} ({{ row.month }})</th>
            <td v-for="yc in data.years" :key="yc" class="lnt-cell"
                :style="{background: row.by_year[yc] && !row.by_year[yc].error ? RELATION_BG[row.by_year[yc].vs_birth_relation] : 'rgba(0,0,0,0.2)'}"
                @click="openCellDetail(row.by_year[yc], yc, row.month)"
                :title="row.by_year[yc]?.vs_birth || ''">
              <div v-if="row.by_year[yc] && !row.by_year[yc].error" class="cell-inner">
                <HexagramSvg :upper="row.by_year[yc].chinh_upper"
                             :lower="row.by_year[yc].chinh_lower"
                             :moving-line="row.by_year[yc].moving_line"
                             :size="50" :show-label="false" />
                <div class="cell-name">{{ row.by_year[yc].chinh }}</div>
                <small class="cell-rel">{{ row.by_year[yc].vs_birth }}</small>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Drawer cell detail -->
    <aside v-if="selectedCell" class="lnt-drawer">
      <div class="ld-head">
        <button class="ld-close" @click="closeDrawer">✕</button>
        <span class="ld-title">
          <small>Tháng {{ selectedCell.month }} năm {{ selectedCell.year }}</small>
          <span v-if="drawerHexagram?.number">#{{ drawerHexagram.number }} {{ drawerHexagram.name_vi }} {{ drawerHexagram.name_zh }}</span>
        </span>
      </div>
      <div class="ld-body">
        <div v-if="drawerHexagram?.loading" class="ld-status">Đang tải...</div>
        <div v-if="drawerHexagram?.error" class="ld-error">{{ drawerHexagram.error }}</div>
        <div v-if="drawerHexagram?.body_markdown" v-html="renderMd(drawerHexagram.body_markdown.slice(0, 4000))"></div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.lnt {
  padding: 1rem; background: rgba(15, 23, 42, 0.4);
  border-radius: 8px; margin: 0.5rem 0;
}
.lnt-head h3 { margin: 0; color: #c4b5fd; font-size: 1rem; }
.subtitle { color: #94a3b8; font-style: italic; font-size: 0.82rem; margin: 0.3rem 0 0.7rem; }
.lnt-form {
  display: flex; gap: 0.6rem; align-items: center; flex-wrap: wrap;
  background: rgba(196, 181, 253, 0.05); border: 1px solid rgba(196, 181, 253, 0.18);
  border-radius: 5px; padding: 0.5rem 0.7rem; margin-bottom: 0.6rem;
}
.lnt-form label { display: flex; gap: 0.3rem; align-items: center; font-size: 0.82rem; color: #cbd5e1; flex-wrap: wrap; }
.lnt-form input {
  background: #1e1b4b; color: #e0e7ff; border: 1px solid rgba(196, 181, 253, 0.3);
  padding: 0.25rem 0.4rem; border-radius: 4px; font-size: 0.82rem; width: 110px;
}
.lnt-form input[type=datetime-local] { width: 180px; }
.btn-load {
  background: rgba(167, 139, 250, 0.2); border: 1px solid rgba(167, 139, 250, 0.5);
  color: #c4b5fd; padding: 0.35rem 0.7rem; border-radius: 4px; cursor: pointer; font-size: 0.82rem;
}
.lnt-legend {
  display: flex; gap: 0.8rem; flex-wrap: wrap; font-size: 0.75rem; color: #94a3b8;
  margin-bottom: 0.5rem;
}
.legend-swatch { display: inline-block; width: 14px; height: 14px; border-radius: 2px; vertical-align: middle; margin-right: 0.25rem; border: 1px solid rgba(255,255,255,0.1); }

.lnt-grid-wrap { overflow-x: auto; }
.lnt-grid { border-collapse: collapse; width: 100%; table-layout: fixed; }
.lnt-grid th, .lnt-grid td {
  border: 1px solid rgba(196, 181, 253, 0.15);
  padding: 0; text-align: center;
}
.lnt-grid th { background: rgba(167, 139, 250, 0.1); color: #c4b5fd; font-size: 0.78rem; padding: 0.3rem 0.2rem; }
.th-month { background: rgba(167, 139, 250, 0.06) !important; font-weight: 600; }
.lnt-cell { cursor: pointer; transition: filter .15s; }
.lnt-cell:hover { filter: brightness(1.25); }
.cell-inner { padding: 0.25rem 0.1rem; display: flex; flex-direction: column; gap: 0.1rem; align-items: center; }
.cell-name { font-size: 0.7rem; color: #fcd34d; font-weight: 600; }
.cell-rel { color: #94a3b8; font-size: 0.62rem; }

/* Drawer */
.lnt-drawer {
  position: fixed; top: 60px; right: 0; bottom: 0; width: 540px; max-width: 92vw;
  background: #0f172a; border-left: 2px solid #c4b5fd; z-index: 200;
  display: flex; flex-direction: column; box-shadow: -4px 0 24px rgba(0,0,0,0.5);
}
.ld-head { padding: 0.6rem 0.9rem; background: #312e81; color: white; display: flex; gap: 0.7rem; align-items: center; }
.ld-close { background: rgba(255,255,255,0.18); border: none; color: white; padding: 0.25rem 0.6rem; border-radius: 4px; cursor: pointer; }
.ld-title { display: flex; flex-direction: column; line-height: 1.2; }
.ld-title small { color: #c4b5fd; font-size: 0.75rem; font-style: italic; }
.ld-title span { color: #fcd34d; font-weight: 600; }
.ld-body { flex: 1; overflow-y: auto; padding: 1rem; color: #cbd5e1; line-height: 1.6; font-size: 0.88rem; }
.ld-body b { color: #fcd34d; }

.lvd-error { color: #f87171; padding: 0.4rem 0.8rem; }

@media (max-width: 700px) {
  .lnt-drawer { width: 100%; }
}
</style>
