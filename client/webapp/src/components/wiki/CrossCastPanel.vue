<script setup>
/**
 * CrossCastPanel — Cải tiến #4: Cross-cast correlation.
 *
 * Đối chiếu chéo nhiều quẻ gieo cùng kỳ (cùng ngày, cùng sự kiện) → phát hiện:
 *   1. Trường năng lượng cùng kỳ (Chính quẻ trùng nhau ở nhiều cast)
 *   2. Vai trò Thể khác nhau giữa các intent
 *   3. Pattern xuyên cast (cảnh báo chung, Trùng Phùng tổng)
 *
 * Cơ sở thực nghiệm: Pr#3 (tổng ngày 17/5) và Pr#5 (riêng anh 86) cùng cast
 * được Chính Chấn/Tốn (Hằng) — bằng chứng đầu tay cho trường năng lượng ngày.
 */
import { ref, computed, onMounted } from "vue";

const CHI_OPTIONS = [
  "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
  "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
];

function getCurrentHourChi() {
  const h = new Date().getHours();
  if (h >= 23 || h < 1) return "Tý";
  const map = ["Sửu","Sửu","Dần","Dần","Mão","Mão","Thìn","Thìn","Tỵ","Tỵ",
               "Ngọ","Ngọ","Mùi","Mùi","Thân","Thân","Dậu","Dậu","Tuất","Tuất","Hợi","Hợi"];
  return map[h - 1] || "Tý";
}

function newEntry(label = "") {
  const now = new Date();
  return {
    label,
    year_chi: "Ngọ",
    month: now.getMonth() + 1,
    day: now.getDate(),
    hour_chi: getCurrentHourChi(),
    intent: "general",
  };
}

const intents = ref([]);
const entries = ref([
  newEntry("Cast 1 — tổng ngày"),
  newEntry("Cast 2 — đối tác A"),
]);
const result = ref(null);
const loading = ref(false);
const error = ref("");

async function loadIntents() {
  try {
    const r = await fetch("/api/yi-wiki/intents");
    const d = await r.json();
    if (d.status === "ok") intents.value = d.intents;
  } catch (e) {}
}
onMounted(loadIntents);

function addEntry() {
  if (entries.value.length >= 6) return;
  entries.value.push(newEntry(`Cast ${entries.value.length + 1}`));
}

function removeEntry(idx) {
  if (entries.value.length <= 2) return;
  entries.value.splice(idx, 1);
}

async function correlate() {
  loading.value = true;
  error.value = "";
  result.value = null;
  try {
    const r = await fetch("/api/yi-wiki/correlate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entries: entries.value }),
    });
    const d = await r.json();
    if (d.status !== "ok") {
      error.value = d.message || "Lỗi đối chiếu";
      return;
    }
    result.value = d;
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

// Demo preset: Pr#3 + Pr#5 ngày 17/5
function loadDemoPr3Pr5() {
  entries.value = [
    { label: "Pr#3 tổng ngày 17/5", year_chi: "Ngọ", month: 5, day: 16, hour_chi: "Tý", intent: "yet_kien" },
    { label: "Pr#5 anh 86 dự án 1 tháng", year_chi: "Ngọ", month: 5, day: 16, hour_chi: "Thân", intent: "cau_tai" },
  ];
}

const hasResults = computed(() => result.value && result.value.n_casts > 0);
</script>

<template>
  <div class="cc-panel">
    <div class="cc-header">
      <h3>🔗 Đối chiếu chéo nhiều quẻ <span class="src-ref">(Cải tiến #4)</span></h3>
      <p class="cc-intro">
        Khi anh gieo <b>nhiều quẻ trong cùng 1 kỳ</b> (cùng ngày / cùng sự kiện, intent khác nhau)
        → engine sẽ tìm <b>trường năng lượng</b>, so sánh <b>vai trò Thể</b>,
        và tổng hợp <b>cảnh báo chung</b>.
      </p>
      <button class="btn-demo" @click="loadDemoPr3Pr5">
        🎯 Demo: Pr#3 + Pr#5 (ngày 17/5/2026 — bằng chứng trường năng lượng)
      </button>
    </div>

    <div class="entries">
      <div v-for="(e, i) in entries" :key="i" class="entry-row">
        <div class="entry-num">#{{ i + 1 }}</div>
        <input v-model="e.label" placeholder="Nhãn (vd: anh 83, tổng ngày...)"
               class="entry-label" />
        <div class="entry-inputs">
          <select v-model="e.year_chi" title="Năm chi">
            <option v-for="c in CHI_OPTIONS" :key="c" :value="c">{{ c }}</option>
          </select>
          <input v-model.number="e.month" type="number" min="1" max="12" title="Tháng" />
          <input v-model.number="e.day" type="number" min="1" max="31" title="Ngày" />
          <select v-model="e.hour_chi" title="Giờ chi">
            <option v-for="c in CHI_OPTIONS" :key="c" :value="c">{{ c }}</option>
          </select>
          <select v-model="e.intent" title="Loại việc">
            <option value="general">— Không xác định</option>
            <option v-for="it in intents" :key="it.key" :value="it.key">
              {{ it.label }}
            </option>
          </select>
        </div>
        <button class="btn-remove" :disabled="entries.length <= 2"
                @click="removeEntry(i)" title="Xoá entry">×</button>
      </div>
      <button class="btn-add" :disabled="entries.length >= 6" @click="addEntry">
        + Thêm cast
      </button>
    </div>

    <div class="cc-actions">
      <button class="btn-primary" :disabled="loading" @click="correlate">
        {{ loading ? "Đang đối chiếu..." : "🔗 Đối chiếu chéo" }}
      </button>
    </div>

    <p v-if="error" class="err-msg">⚠️ {{ error }}</p>

    <!-- ⭐ Results -->
    <section v-if="hasResults" class="cc-results">
      <h3>📊 Báo cáo đối chiếu — {{ result.n_casts }} cast</h3>

      <!-- (1) Trường năng lượng -->
      <div class="block tnl-block"
           :class="{ 'has-trung': Object.keys(result.truong_nang_luong.chinh_trung).length > 0 }">
        <h4>📊 (1) Trường năng lượng kỳ</h4>
        <p style="white-space: pre-line">{{ result.truong_nang_luong.summary }}</p>
        <div v-if="Object.keys(result.truong_nang_luong.chinh_trung).length > 0" class="trung-list">
          <div v-for="(labels, qname) in result.truong_nang_luong.chinh_trung" :key="qname"
               class="trung-item">
            ★ <b>{{ qname }}</b>
            <span class="trung-count">({{ labels.length }} cast)</span>
            <div class="trung-labels">
              <span v-for="(l, i) in labels" :key="i" class="lbl">{{ l }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- (2) Vai trò Thể -->
      <div class="block roles-block">
        <h4>👤 (2) Vai trò Thể qua các cast</h4>
        <p>{{ result.the_roles.summary }}</p>
        <table class="roles-table">
          <thead>
            <tr>
              <th>Cast</th>
              <th>Intent</th>
              <th>THỂ</th>
              <th>DỤNG</th>
              <th>Quan hệ</th>
              <th>Auspice</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in result.the_roles.roles" :key="i">
              <td>{{ r.label }}</td>
              <td class="td-intent">{{ r.intent }}</td>
              <td><b>{{ r.the_que }}</b> <small>({{ r.the_hanh }})</small></td>
              <td>{{ r.dung_que }} <small>({{ r.dung_hanh }})</small></td>
              <td>{{ r.relationship.replace("_", " ") }}</td>
              <td :class="'aus-' + r.auspice">{{ r.auspice.toUpperCase() }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- (3) Pattern xuyên cast -->
      <div class="block pattern-block">
        <h4>🎯 (3) Pattern xuyên cast</h4>
        <pre>{{ result.cross_pattern }}</pre>
      </div>
    </section>
  </div>
</template>

<style scoped>
.cc-panel { padding: 0.5rem 0; color: #e2e8f0; }
.cc-header { margin-bottom: 0.85rem; }
.cc-header h3 { margin: 0 0 0.4rem; color: #c4b5fd; font-size: 1.05rem; }
.src-ref { font-size: 0.75rem; color: #94a3b8; font-weight: normal; }
.cc-intro {
  margin: 0 0 0.6rem; font-size: 0.85rem; color: #cbd5e1; line-height: 1.55;
}
.btn-demo {
  padding: 0.4rem 0.7rem; background: rgba(196,181,253,0.1);
  border: 1px dashed rgba(196,181,253,0.4); color: #ddd6fe;
  border-radius: 4px; font-size: 0.8rem; cursor: pointer;
}
.btn-demo:hover { background: rgba(196,181,253,0.2); }

.entries { display: flex; flex-direction: column; gap: 0.45rem; margin-bottom: 0.7rem; }
.entry-row {
  display: grid;
  grid-template-columns: auto 1.5fr 3fr auto;
  gap: 0.4rem;
  align-items: center;
  padding: 0.45rem 0.5rem;
  background: rgba(0,0,0,0.25);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 4px;
}
.entry-num { font-size: 0.8rem; color: #94a3b8; font-weight: 600; }
.entry-label, .entry-inputs select, .entry-inputs input {
  padding: 0.3rem 0.4rem;
  background: rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.12);
  color: #e2e8f0;
  border-radius: 3px;
  font-size: 0.8rem;
  font-family: inherit;
}
.entry-inputs {
  display: grid;
  grid-template-columns: 1fr 0.6fr 0.6fr 1fr 1.5fr;
  gap: 0.3rem;
}
.btn-remove {
  width: 26px; height: 26px;
  background: rgba(248,113,113,0.15); border: 1px solid rgba(248,113,113,0.4);
  color: #fecaca; border-radius: 3px; cursor: pointer; font-size: 1rem;
}
.btn-remove:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-add {
  align-self: flex-start;
  padding: 0.35rem 0.7rem;
  background: rgba(96,165,250,0.1); border: 1px dashed rgba(96,165,250,0.4);
  color: #93c5fd; border-radius: 3px; cursor: pointer; font-size: 0.8rem;
}
.btn-add:disabled { opacity: 0.3; cursor: not-allowed; }

.cc-actions { margin: 0.6rem 0 0.8rem; }
.btn-primary {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  border: none; color: #fff; border-radius: 4px; cursor: pointer;
  font-size: 0.88rem; font-weight: 600;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.err-msg { color: #fca5a5; font-size: 0.85rem; }

.cc-results { margin-top: 1rem; }
.cc-results h3 { color: #c4b5fd; font-size: 1rem; margin: 0 0 0.5rem; }
.block {
  margin-bottom: 0.7rem; padding: 0.7rem;
  background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 5px;
}
.block h4 { margin: 0 0 0.4rem; font-size: 0.88rem; color: #cbd5e1; }
.tnl-block.has-trung {
  background: rgba(196,181,253,0.08); border-color: rgba(196,181,253,0.3);
}
.tnl-block.has-trung h4 { color: #ddd6fe; }
.trung-list { margin-top: 0.5rem; }
.trung-item {
  padding: 0.45rem 0.55rem; margin-bottom: 0.3rem;
  background: rgba(196,181,253,0.1); border-left: 3px solid #c4b5fd;
  border-radius: 3px; font-size: 0.85rem;
}
.trung-count { color: #94a3b8; font-size: 0.78rem; margin-left: 0.35rem; }
.trung-labels { margin-top: 0.25rem; display: flex; flex-wrap: wrap; gap: 0.3rem; }
.lbl {
  padding: 0.15rem 0.5rem; background: rgba(255,255,255,0.06);
  border-radius: 2px; font-size: 0.75rem; color: #cbd5e1;
}

.roles-table {
  width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 0.4rem;
}
.roles-table th, .roles-table td {
  padding: 0.3rem 0.5rem; border: 1px solid rgba(255,255,255,0.08);
  text-align: left;
}
.roles-table th { background: rgba(255,255,255,0.04); color: #cbd5e1; font-weight: 600; }
.roles-table small { color: #94a3b8; }
.td-intent { color: #94a3b8; font-size: 0.75rem; }
.aus-cát { color: #6ee7b7; font-weight: 700; }
.aus-hung { color: #fca5a5; font-weight: 700; }
.aus-bình { color: #cbd5e1; }

.pattern-block pre {
  margin: 0; padding: 0.55rem; background: rgba(0,0,0,0.3); border-radius: 3px;
  font-size: 0.78rem; color: #e2e8f0; white-space: pre-wrap; font-family: inherit;
  line-height: 1.5;
}

@media (max-width: 700px) {
  .entry-row { grid-template-columns: 1fr; }
  .entry-inputs { grid-template-columns: 1fr 1fr 1fr 1fr 1fr; }
  .roles-table { font-size: 0.7rem; }
}
</style>
