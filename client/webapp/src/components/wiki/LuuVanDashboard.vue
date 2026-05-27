<script setup>
/**
 * LuuVanDashboard — 7 vòng quẻ paradigm Khang Tiết.
 *
 * ⚠️ Iron Rule #4: KHÔNG hiển thị "cát/hung". Chỉ paradigm CẤU TRÚC.
 * Reference: docs/design/MAI-HOA-LUU-VAN-GOAL.md
 *
 * 3 view:
 *   A. Snapshot bây giờ (7 quẻ + giao thoa)
 *   B. Diễn giải paradigm từng vòng
 *   C. (sau phase 2) Nhật ký việc thực
 */
import { ref, computed, onMounted, watch } from "vue";
import HexagramSvg from "./diagrams/HexagramSvg.vue";

// Birth input — default founder (sẽ wire user profile sau)
const birthInput = ref({
  year_chi: "Thìn",
  lunar_month: 4,
  lunar_day: 22,
  hour_chi: "Tý",
});
const customNow = ref(false);
const nowInput = ref({
  year_chi: "Ngọ",
  lunar_month: 4,
  lunar_day: 12,
  hour_chi: "Tý",
});

const snapshot = ref(null);
const loading = ref(false);
const error = ref("");

const CHI_LIST = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"];

const VONG_ORDER = [
  { key: "vong_1_khoi_sinh", color: "#f59e0b", label: "1. Khởi Sinh" },
  { key: "vong_2_luu_nien", color: "#10b981", label: "2. Lưu Niên" },
  { key: "vong_3_luu_nguyet", color: "#3b82f6", label: "3. Lưu Nguyệt" },
  { key: "vong_4_luu_nhat", color: "#8b5cf6", label: "4. Lưu Nhật" },
  { key: "vong_5_luu_thoi", color: "#ec4899", label: "5. Lưu Thời" },
  { key: "vong_6_vu_tru", color: "#6b7280", label: "6. Vũ trụ" },
  { key: "vong_7_cong_huong", color: "#dc2626", label: "7. Cộng hưởng" },
];

const RELATION_COLOR = {
  "ti_hoa": "#94a3b8",
  "A_sinh_B": "#10b981",
  "B_sinh_A": "#10b981",
  "A_khac_B": "#f59e0b",
  "B_khac_A": "#f59e0b",
  "unknown": "#6b7280",
};

async function loadSnapshot() {
  loading.value = true;
  error.value = "";
  const body = {
    birth_year_chi: birthInput.value.year_chi,
    birth_lunar_month: parseInt(birthInput.value.lunar_month),
    birth_lunar_day: parseInt(birthInput.value.lunar_day),
    birth_hour_chi: birthInput.value.hour_chi,
  };
  if (customNow.value) {
    body.now_year_chi = nowInput.value.year_chi;
    body.now_lunar_month = parseInt(nowInput.value.lunar_month);
    body.now_lunar_day = parseInt(nowInput.value.lunar_day);
    body.now_hour_chi = nowInput.value.hour_chi;
  }
  try {
    const r = await fetch("/api/yi-wiki/luu-van/snapshot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    snapshot.value = await r.json();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

onMounted(loadSnapshot);
</script>

<template>
  <div class="lvd">
    <header class="lvd-head">
      <h3>🌀 Mai Hoa Lưu Vận — 7 Vòng Quẻ</h3>
      <p class="lvd-subtitle">
        Theo Khang Tiết Q3 (Tam Tài). <b>Không predict cát/hung</b> — chỉ <i>tượng cấu trúc</i>.
      </p>
    </header>

    <div class="lvd-form">
      <div class="form-row">
        <span class="form-label">Sinh:</span>
        <select v-model="birthInput.year_chi">
          <option v-for="c in CHI_LIST" :key="c" :value="c">{{ c }}</option>
        </select>
        <input type="number" v-model="birthInput.lunar_month" min="1" max="12" placeholder="Tháng âm" />
        <input type="number" v-model="birthInput.lunar_day" min="1" max="30" placeholder="Ngày âm" />
        <select v-model="birthInput.hour_chi">
          <option v-for="c in CHI_LIST" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>
      <label class="form-toggle">
        <input type="checkbox" v-model="customNow" />
        Tự nhập "thời điểm hiện tại" âm lịch (mặc định = server time approx)
      </label>
      <div v-if="customNow" class="form-row">
        <span class="form-label">Bây giờ:</span>
        <select v-model="nowInput.year_chi">
          <option v-for="c in CHI_LIST" :key="c" :value="c">{{ c }}</option>
        </select>
        <input type="number" v-model="nowInput.lunar_month" min="1" max="12" />
        <input type="number" v-model="nowInput.lunar_day" min="1" max="30" />
        <select v-model="nowInput.hour_chi">
          <option v-for="c in CHI_LIST" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>
      <button class="btn-load" @click="loadSnapshot" :disabled="loading">
        {{ loading ? '⏳ Đang tính...' : '🔄 Tính 7 vòng' }}
      </button>
    </div>

    <div v-if="error" class="lvd-error">{{ error }}</div>

    <!-- 7 vòng -->
    <div v-if="snapshot" class="lvd-grid">
      <div v-for="(vong, i) in VONG_ORDER" :key="vong.key" class="vong-card"
           :style="{borderTopColor: vong.color}">
        <div class="vong-header">
          <span class="vong-label" :style="{color: vong.color}">{{ vong.label }}</span>
          <span class="vong-doi-moi">{{ snapshot[vong.key].paradigm_meta.doi_moi_khi }}</span>
        </div>
        <div class="vong-svg">
          <HexagramSvg
            :upper="snapshot[vong.key].chinh.upper"
            :lower="snapshot[vong.key].chinh.lower"
            :moving-line="snapshot[vong.key].moving_line"
            :size="80" :show-label="false" />
        </div>
        <div class="vong-name">{{ snapshot[vong.key].chinh.name }}</div>
        <div class="vong-meta">
          <span>Hào động: <b>{{ snapshot[vong.key].moving_line }}</b></span>
        </div>
        <div class="vong-bien-ho">
          <span>Biến: <code>{{ snapshot[vong.key].bien.name }}</code></span>
          <span>Hỗ: <code>{{ snapshot[vong.key].ho.name }}</code></span>
        </div>
        <details class="vong-paradigm">
          <summary>📜 Paradigm</summary>
          <p>{{ snapshot[vong.key].paradigm_meta.phan_anh }}</p>
          <p><i>{{ snapshot[vong.key].paradigm_meta.paradigm }}</i></p>
        </details>
      </div>
    </div>

    <!-- Giao thoa -->
    <div v-if="snapshot" class="lvd-giao-thoa">
      <h4>⚡ Giao thoa Ngũ hành (KHÔNG cát/hung — chỉ cấu trúc)</h4>
      <table class="gt-table">
        <thead>
          <tr>
            <th>Cặp quẻ</th>
            <th>Thể vs Thể</th>
            <th>Dụng vs Dụng</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(gt, k) in snapshot.giao_thoa" :key="k">
            <td><b>{{ k.replace(/_/g, ' ') }}</b><br><small>{{ gt.que_A }} ↔ {{ gt.que_B }}</small></td>
            <td>
              <span :style="{color: RELATION_COLOR[gt.the_vs_the.relation]}">●</span>
              {{ gt.the_vs_the.label_vi }}
            </td>
            <td>
              <span :style="{color: RELATION_COLOR[gt.dung_vs_dung.relation]}">●</span>
              {{ gt.dung_vs_dung.label_vi }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paradigm footer -->
    <div v-if="snapshot" class="lvd-foot">
      <p><b>⚠️ Paradigm Tổ sư Khang Tiết</b>: <i>"Quan vật chí huyền chí vi, lý chỉ dị minh"</i> — Trần Đoàn. {{ snapshot._paradigm_note }}</p>
    </div>
  </div>
</template>

<style scoped>
.lvd {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 8px;
  margin: 0.5rem 0;
}
.lvd-head h3 { margin: 0; color: #fcd34d; font-size: 1.05rem; }
.lvd-subtitle {
  color: #94a3b8; font-style: italic; font-size: 0.85rem;
  margin: 0.3rem 0 0.8rem;
}
.lvd-form {
  background: rgba(252, 211, 77, 0.05);
  border: 1px solid rgba(252, 211, 77, 0.2);
  border-radius: 6px; padding: 0.6rem 0.9rem; margin-bottom: 1rem;
}
.form-row {
  display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap; margin-bottom: 0.4rem;
}
.form-label { color: #fcd34d; font-size: 0.85rem; min-width: 80px; font-weight: 600; }
.form-row select, .form-row input {
  background: #1e1b4b; color: #e0e7ff;
  border: 1px solid rgba(196, 181, 253, 0.3);
  padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem;
}
.form-row input[type=number] { width: 80px; }
.form-toggle {
  font-size: 0.78rem; color: #cbd5e1; display: flex; align-items: center; gap: 0.3rem;
  margin: 0.3rem 0;
}
.btn-load {
  background: rgba(167, 139, 250, 0.2); border: 1px solid rgba(167, 139, 250, 0.5);
  color: #c4b5fd; padding: 0.4rem 0.9rem; border-radius: 5px; cursor: pointer;
  font-size: 0.85rem; margin-top: 0.3rem;
}
.btn-load:hover { background: rgba(167, 139, 250, 0.3); }
.lvd-error { color: #f87171; padding: 0.5rem; }

.lvd-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.6rem;
}
.vong-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(196, 181, 253, 0.15);
  border-top: 3px solid #fbbf24;
  border-radius: 6px;
  padding: 0.6rem 0.7rem;
  display: flex; flex-direction: column; gap: 0.3rem;
}
.vong-header { display: flex; justify-content: space-between; align-items: baseline; }
.vong-label { font-weight: 600; font-size: 0.85rem; }
.vong-doi-moi { font-size: 0.65rem; color: #6b7280; font-style: italic; }
.vong-svg { text-align: center; margin: 0.2rem 0; }
.vong-name { color: #fcd34d; font-size: 0.95rem; text-align: center; font-weight: 600; }
.vong-meta { font-size: 0.78rem; color: #cbd5e1; text-align: center; }
.vong-bien-ho {
  display: flex; justify-content: space-between; font-size: 0.72rem; color: #94a3b8;
  margin-top: 0.2rem;
}
.vong-bien-ho code {
  background: rgba(196, 181, 253, 0.12); padding: 1px 4px; border-radius: 3px;
  color: #c4b5fd; font-size: 0.7rem;
}
.vong-paradigm {
  margin-top: 0.3rem; font-size: 0.78rem;
}
.vong-paradigm summary { color: #94a3b8; cursor: pointer; font-size: 0.75rem; }
.vong-paradigm p { color: #cbd5e1; margin: 0.3rem 0; line-height: 1.4; }
.vong-paradigm i { color: #fbbf24; }

.lvd-giao-thoa { margin-top: 1.2rem; }
.lvd-giao-thoa h4 { color: #a78bfa; font-size: 0.95rem; margin: 0 0 0.4rem; }
.gt-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
.gt-table th, .gt-table td {
  border: 1px solid rgba(196, 181, 253, 0.15);
  padding: 0.35rem 0.55rem; text-align: left; vertical-align: top;
}
.gt-table th { background: rgba(167, 139, 250, 0.1); color: #c4b5fd; }
.gt-table td { color: #cbd5e1; }
.gt-table small { color: #6b7280; font-size: 0.72rem; }

.lvd-foot {
  margin-top: 1rem; padding: 0.6rem 0.8rem;
  background: rgba(252, 211, 77, 0.05);
  border-left: 2px solid #fbbf24;
  font-size: 0.78rem; color: #cbd5e1; line-height: 1.5;
}
.lvd-foot b { color: #fbbf24; }
.lvd-foot i { color: #fde68a; }
</style>
