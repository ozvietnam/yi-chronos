<script setup>
/**
 * AuspiciousDayPanel — Chọn ngày tốt theo Bát Tự + Mai Hoa.
 *
 * Input form: sinh thần + tháng cần chọn + intent + hướng + zone
 * Output: Bát Tự breakdown + Top 7 ngày + Taboos
 */
import { ref, computed, onMounted } from "vue";

const form = ref({
  birth_date: "1988-05-02",
  birth_hour: 8,
  target_year: 2026,
  target_month: 6,
  intent: "chuyen_nha",
  direction: "đông",
  location_zone: "bac",
});

const result = ref(null);
const loading = ref(false);
const error = ref("");
const intents = ref([]);

const DIRECTIONS = [
  { v: "", label: "(không chọn)" },
  { v: "đông", label: "Đông (Mộc)" },
  { v: "tây", label: "Tây (Kim)" },
  { v: "nam", label: "Nam (Hoả)" },
  { v: "bắc", label: "Bắc (Thuỷ)" },
  { v: "đông nam", label: "Đông Nam (Mộc-Tốn)" },
  { v: "đông bắc", label: "Đông Bắc (Thổ-Cấn)" },
  { v: "tây nam", label: "Tây Nam (Thổ-Khôn)" },
  { v: "tây bắc", label: "Tây Bắc (Kim-Càn)" },
];

const ZONES = [
  { v: "", label: "(không chọn)" },
  { v: "bac", label: "Miền Bắc / biên giới Bắc (vd: Lạng Sơn)" },
  { v: "nam", label: "Miền Nam" },
  { v: "đông", label: "Miền Đông / ven biển" },
  { v: "tây", label: "Miền Tây" },
];

async function loadIntents() {
  try {
    const r = await fetch("/api/yi-wiki/auspicious-intents");
    const d = await r.json();
    if (d.status === "ok") intents.value = d.intents;
  } catch (e) {}
}
loadIntents();

async function compute() {
  loading.value = true;
  error.value = "";
  result.value = null;
  try {
    const birth_iso = `${form.value.birth_date}T${String(form.value.birth_hour).padStart(2, '0')}:00:00`;
    const r = await fetch("/api/yi-wiki/auspicious-day", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth_iso,
        target_year: form.value.target_year,
        target_month: form.value.target_month,
        intent: form.value.intent,
        direction: form.value.direction,
        location_zone: form.value.location_zone,
      }),
    });
    const d = await r.json();
    if (d.status !== "ok") {
      error.value = d.message || "Lỗi tính toán";
      return;
    }
    result.value = d;
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

const monthLabel = computed(() =>
  result.value ? `tháng ${form.value.target_month}/${form.value.target_year}` : ""
);

function flagClass(flag) {
  if (flag.includes("XUẤT SẮC")) return "f-best";
  if (flag.includes("RẤT TỐT")) return "f-great";
  if (flag.includes("Tốt")) return "f-good";
  if (flag.includes("CẤM")) return "f-taboo";
  if (flag.includes("Tránh") || flag.includes("Không nên")) return "f-bad";
  return "f-neutral";
}
</script>

<template>
  <div class="ausp-panel">
    <header class="ap-header">
      <h2>📅 Chọn Ngày Tốt — Tích hợp Bát Tự + Mai Hoa + Hoàng Đạo</h2>
      <p class="hint">
        Phân tích Tứ Trụ đệ tử → xét xung-hợp năm chi · Quý Nhân · Tam Sát mùa ·
        Hoàng/Hắc Đạo · bù hành thiếu · cộng hưởng hướng cửa · ưu tiên intent.
      </p>
    </header>

    <!-- Form -->
    <section class="ap-form">
      <div class="form-row">
        <label>
          Ngày sinh:
          <input v-model="form.birth_date" type="date" />
        </label>
        <label>
          Giờ sinh:
          <select v-model.number="form.birth_hour">
            <option v-for="h in 24" :key="h" :value="h-1">
              {{ String(h-1).padStart(2, '0') }}h ({{
                h-1 >= 23 || h-1 < 1 ? 'Tý' :
                h-1 < 3 ? 'Sửu' : h-1 < 5 ? 'Dần' : h-1 < 7 ? 'Mão' :
                h-1 < 9 ? 'Thìn' : h-1 < 11 ? 'Tỵ' : h-1 < 13 ? 'Ngọ' :
                h-1 < 15 ? 'Mùi' : h-1 < 17 ? 'Thân' : h-1 < 19 ? 'Dậu' :
                h-1 < 21 ? 'Tuất' : 'Hợi'
              }})
            </option>
          </select>
        </label>
      </div>

      <div class="form-row">
        <label>
          Năm cần chọn:
          <input v-model.number="form.target_year" type="number" min="2024" max="2030" />
        </label>
        <label>
          Tháng:
          <select v-model.number="form.target_month">
            <option v-for="m in 12" :key="m" :value="m">Tháng {{ m }}</option>
          </select>
        </label>
      </div>

      <div class="form-row">
        <label class="flex-1">
          Loại việc (intent):
          <select v-model="form.intent">
            <option v-for="i in intents" :key="i.key" :value="i.key">{{ i.label }}</option>
          </select>
        </label>
      </div>

      <div class="form-row">
        <label class="flex-1">
          Hướng cửa nhà / văn phòng (tuỳ chọn):
          <select v-model="form.direction">
            <option v-for="d in DIRECTIONS" :key="d.v" :value="d.v">{{ d.label }}</option>
          </select>
        </label>
        <label class="flex-1">
          Khu vực sống:
          <select v-model="form.location_zone">
            <option v-for="z in ZONES" :key="z.v" :value="z.v">{{ z.label }}</option>
          </select>
        </label>
      </div>

      <button class="btn-primary" @click="compute" :disabled="loading">
        {{ loading ? "Đang tính..." : "🪷 Luận ngày tốt" }}
      </button>
      <p v-if="error" class="err">❌ {{ error }}</p>
    </section>

    <!-- Result -->
    <section v-if="result" class="ap-result">
      <!-- Bát Tự -->
      <div class="bat-tu-block">
        <h3>🐉 Tứ Trụ</h3>
        <div class="bt-pillars">
          <div class="bt-cell">
            <span class="bt-pos">Năm</span>
            <span class="bt-gz">{{ result.bat_tu.year }}</span>
          </div>
          <div class="bt-cell">
            <span class="bt-pos">Tháng</span>
            <span class="bt-gz">{{ result.bat_tu.month }}</span>
          </div>
          <div class="bt-cell highlight">
            <span class="bt-pos">Ngày ⭐</span>
            <span class="bt-gz">{{ result.bat_tu.day }}</span>
            <span class="bt-tag">Nhật chủ: {{ result.bat_tu.nhat_chu }} ({{ result.bat_tu.nhat_chu_hanh }})</span>
          </div>
          <div class="bt-cell">
            <span class="bt-pos">Giờ</span>
            <span class="bt-gz">{{ result.bat_tu.hour }}</span>
          </div>
        </div>

        <div class="bt-details">
          <div class="bt-row">
            <b>Ngũ hành 8 chữ:</b>
            <span v-for="(c, h) in result.bat_tu.all_hanh" :key="h" class="hanh-pill">
              {{ h }}: {{ c }}
            </span>
          </div>
          <div v-if="result.bat_tu.thieu_hanh.length" class="bt-row">
            <b>Hành thiếu (cần bù):</b>
            <span v-for="h in result.bat_tu.thieu_hanh" :key="h" class="thieu-pill">{{ h }}</span>
          </div>
          <div class="bt-row">
            <b>Thiên Ất Quý Nhân:</b>
            <span class="qn-pill" v-for="b in result.bat_tu.quy_nhan_day" :key="b">{{ b }}</span>
            <span class="qn-meta">(theo Nhật can {{ result.bat_tu.nhat_chu }})</span>
          </div>
          <div class="bt-row" v-if="result.direction">
            <b>Hướng cửa:</b> {{ result.direction }}
          </div>
        </div>
      </div>

      <!-- TOP days -->
      <h3>🌟 TOP 7 ngày đẹp nhất {{ monthLabel }} — {{ result.intent.label }}</h3>
      <div class="top-grid">
        <div v-for="(d, i) in result.top_days" :key="d.date"
             class="day-card" :class="flagClass(d.flag)">
          <div class="dc-head">
            <span class="dc-rank">#{{ i+1 }}</span>
            <span class="dc-flag">{{ d.flag }}</span>
          </div>
          <div class="dc-date">
            📅 {{ d.day_num }}/{{ form.target_month }} ({{ d.weekday }})
          </div>
          <div class="dc-gz">
            <b>{{ d.stem }} {{ d.branch }}</b>
            <span class="dc-hanh">{{ d.can_hanh }}/{{ d.chi_hanh }}</span>
          </div>
          <div class="dc-score">Score: <b>{{ d.score >= 0 ? '+' : '' }}{{ d.score }}</b></div>
          <ul class="dc-notes">
            <li v-for="n in d.notes.slice(0, 5)" :key="n">{{ n }}</li>
          </ul>
          <div class="dc-hour">⏰ Giờ tốt: {{ d.suggested_hour }}</div>
        </div>
      </div>

      <!-- Taboos -->
      <details v-if="result.taboos.length" class="taboo-block">
        <summary>❌ Ngày TUYỆT ĐỐI TRÁNH ({{ result.taboos.length }} ngày)</summary>
        <div class="taboo-list">
          <div v-for="t in result.taboos" :key="t.date" class="taboo-item">
            <b>{{ t.day_num }}/{{ form.target_month }}</b>
            ({{ t.weekday }}) {{ t.stem }} {{ t.branch }}
            <span class="t-notes">{{ t.notes.join(' · ') }}</span>
          </div>
        </div>
      </details>

      <!-- Method note -->
      <details class="method-note">
        <summary>📐 Phương pháp luận của Thầy</summary>
        <ul>
          <li><b>Xung tuổi (Lục Xung)</b>: chi ngày XUNG chi năm sinh → CẤM. Vd Thìn xung Tuất.</li>
          <li><b>Tam Sát mùa</b>: mùa hạ kỵ phương Bắc (Hợi/Tý/Sửu); mùa thu kỵ Đông; mùa đông kỵ Nam; mùa xuân kỵ Tây.</li>
          <li><b>Lục Hợp / Tam Hợp</b>: cộng điểm khi chi ngày hợp với chi năm.</li>
          <li><b>Thiên Ất Quý Nhân</b>: 2 chi quý nhân theo Nhật can hoặc Năm can — bậc nhất.</li>
          <li><b>Hoàng/Hắc Đạo</b>: theo Kiến Trừ pháp tháng âm.</li>
          <li><b>Bù hành thiếu</b>: nếu Bát Tự thiếu hành nào → chọn ngày có hành đó.</li>
          <li><b>Cộng hưởng hướng cửa</b>: ngày cùng hành với hướng cửa nhà mới → cộng điểm.</li>
          <li><b>Intent-aware</b>: chuyển nhà ưu Mộc-Thổ; cầu tài ưu Mộc-Kim; hôn nhân ưu Mộc + Quý Nhân.</li>
        </ul>
        <p class="note-warning">
          ⚠️ Đây là pp ƯỚC LƯỢNG dùng quy tắc cổ truyền + Bát Tự cá nhân.
          Nếu có việc trọng đại (cưới hỏi, khai trương quy mô lớn), nên thêm tham vấn thầy thực địa.
        </p>
      </details>
    </section>
  </div>
</template>

<style scoped>
.ausp-panel { padding: 0.5rem 0; color: #e2e8f0; }

.ap-header h2 { margin: 0 0 0.4rem; color: #fbbf24; }
.ap-header .hint {
  font-size: 0.83rem;
  color: #94a3b8;
  margin: 0 0 1rem;
  line-height: 1.6;
}

.ap-form {
  background: rgba(15,23,42,0.55);
  border-radius: 6px;
  padding: 0.85rem 1rem;
  margin-bottom: 1rem;
}
.form-row { display: flex; gap: 0.7rem; flex-wrap: wrap; margin-bottom: 0.6rem; }
.form-row label { display: flex; flex-direction: column; font-size: 0.78rem; color: #94a3b8; min-width: 140px; }
.form-row label.flex-1 { flex: 1; }
.form-row input, .form-row select {
  margin-top: 0.18rem;
  padding: 0.4rem 0.55rem;
  background: rgba(15,23,42,0.7);
  border: 1px solid rgba(255,255,255,0.15);
  color: #e2e8f0;
  border-radius: 3px;
  font-size: 0.85rem;
}
.btn-primary {
  padding: 0.55rem 1.1rem;
  background: #a78bfa;
  color: #1e1b4b;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-primary:hover { background: #c4b5fd; }
.btn-primary:disabled { opacity: 0.5; }
.err { color: #f87171; margin: 0.4rem 0 0; }

/* Bát Tự */
.bat-tu-block {
  background: linear-gradient(135deg, rgba(251,191,36,0.07), rgba(167,139,250,0.05));
  border-radius: 6px;
  padding: 0.85rem 1rem;
  margin-bottom: 1rem;
}
.bat-tu-block h3 { margin: 0 0 0.5rem; color: #fbbf24; font-size: 0.95rem; }
.bt-pillars {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.7rem;
}
.bt-cell {
  background: rgba(15,23,42,0.6);
  padding: 0.5rem 0.6rem;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
}
.bt-cell.highlight {
  background: rgba(251,191,36,0.12);
  border: 1px solid rgba(251,191,36,0.4);
}
.bt-pos { font-size: 0.7rem; color: #94a3b8; }
.bt-gz { font-size: 1rem; font-weight: 600; color: #fef3c7; }
.bt-tag { font-size: 0.7rem; color: #c4b5fd; margin-top: 0.2rem; }

.bt-details { font-size: 0.83rem; }
.bt-row { padding: 0.3rem 0; line-height: 1.65; }
.bt-row b { color: #c4b5fd; margin-right: 0.4rem; }
.hanh-pill {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  margin: 0 0.2rem 0.2rem 0;
  background: rgba(167,139,250,0.15);
  color: #cbd5e1;
  border-radius: 3px;
  font-size: 0.78rem;
}
.thieu-pill {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  margin: 0 0.2rem 0 0;
  background: rgba(248,113,113,0.18);
  color: #fca5a5;
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: 600;
}
.qn-pill {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  margin: 0 0.2rem 0 0;
  background: rgba(251,191,36,0.18);
  color: #fbbf24;
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: 600;
}
.qn-meta { font-size: 0.7rem; color: #94a3b8; margin-left: 0.3rem; }

/* TOP days */
.ap-result > h3 {
  color: #fbbf24;
  margin: 1rem 0 0.5rem;
  font-size: 1rem;
}
.top-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.6rem;
}
.day-card {
  background: rgba(15,23,42,0.55);
  border-radius: 6px;
  padding: 0.65rem 0.85rem;
  border-left: 3px solid #94a3b8;
}
.day-card.f-best { border-left-color: #fbbf24; background: rgba(251,191,36,0.06); }
.day-card.f-great { border-left-color: #c4b5fd; background: rgba(167,139,250,0.06); }
.day-card.f-good { border-left-color: #6ee7b7; }
.day-card.f-bad { border-left-color: #fca5a5; }
.day-card.f-taboo { border-left-color: #f87171; background: rgba(248,113,113,0.08); }

.dc-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem; }
.dc-rank { font-size: 0.78rem; color: #94a3b8; font-weight: 600; }
.dc-flag { font-size: 0.75rem; }
.dc-date { font-size: 0.88rem; color: #fef3c7; margin-bottom: 0.2rem; }
.dc-gz { display: flex; justify-content: space-between; align-items: baseline; margin: 0.2rem 0; }
.dc-gz b { color: #fbbf24; font-size: 0.95rem; }
.dc-hanh { color: #94a3b8; font-size: 0.78rem; }
.dc-score { font-size: 0.78rem; color: #cbd5e1; margin: 0.2rem 0; }
.dc-score b { color: #c4b5fd; }
.dc-notes {
  margin: 0.3rem 0;
  padding-left: 1.1rem;
  font-size: 0.75rem;
  color: #cbd5e1;
  line-height: 1.5;
}
.dc-notes li { margin: 0.15rem 0; }
.dc-hour {
  margin-top: 0.3rem;
  padding: 0.25rem 0.4rem;
  background: rgba(167,139,250,0.1);
  border-radius: 3px;
  font-size: 0.75rem;
  color: #c4b5fd;
}

/* Taboos */
.taboo-block {
  margin-top: 1rem;
  background: rgba(248,113,113,0.05);
  border-radius: 4px;
  padding: 0.5rem 0.85rem;
}
.taboo-block summary { color: #fca5a5; cursor: pointer; font-size: 0.85rem; }
.taboo-item {
  font-size: 0.82rem;
  padding: 0.25rem 0;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.taboo-item b { color: #fca5a5; }
.taboo-item .t-notes { color: #94a3b8; font-size: 0.75rem; display: block; }

/* Method note */
.method-note {
  margin-top: 1rem;
  background: rgba(15,23,42,0.4);
  padding: 0.5rem 0.85rem;
  border-radius: 4px;
}
.method-note summary { color: #c4b5fd; cursor: pointer; font-size: 0.85rem; }
.method-note ul {
  margin: 0.4rem 0;
  padding-left: 1.2rem;
  font-size: 0.8rem;
  color: #cbd5e1;
  line-height: 1.7;
}
.method-note b { color: #fbbf24; }
.note-warning {
  margin: 0.4rem 0 0;
  font-size: 0.78rem;
  color: #fbbf24;
  font-style: italic;
}
</style>
