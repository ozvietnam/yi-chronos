<script setup>
/**
 * LuuVanDashboard — 7 vòng quẻ paradigm Khang Tiết.
 *
 * ⚠️ Iron Rule #4: KHÔNG hiển thị "cát/hung". Chỉ paradigm CẤU TRÚC.
 * Reference: docs/design/MAI-HOA-LUU-VAN-GOAL.md
 *
 * Input: solar datetime (dương lịch) — engine tự convert → lunar.
 * Hiển thị: SONG SONG dương + âm + can chi.
 * Auto-load: nếu user logged in → tự fetch birth từ profile DB.
 */
import { ref, computed, onMounted, watch } from "vue";
import HexagramSvg from "./diagrams/HexagramSvg.vue";

// Solar birth input — default founder (sẽ thay khi auto-load)
const birthSolar = ref("1988-06-05T23:30");
const useNow = ref(true);
const nowSolar = ref("");

const autoLoadUser = ref(true);  // Try logged-in user first
const snapshot = ref(null);
const loading = ref(false);
const error = ref("");

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
    auto_load_user: autoLoadUser.value,
    birth_solar: birthSolar.value.replace("T", " "),
  };
  if (!useNow.value && nowSolar.value) {
    body.now_solar = nowSolar.value.replace("T", " ");
  }
  try {
    const r = await fetch("/api/yi-wiki/luu-van/snapshot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const txt = await r.text();
      throw new Error(`HTTP ${r.status}: ${txt}`);
    }
    snapshot.value = await r.json();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

const calendarsBirth = computed(() => snapshot.value?.calendars?.birth);
const calendarsNow = computed(() => snapshot.value?.calendars?.now);

// V1 — LLM Tổng đọc
const llmNarrative = ref("");
const llmLoading = ref(false);
const llmError = ref("");
const llmMeta = ref(null);

async function callLLMTongDoc() {
  llmLoading.value = true;
  llmError.value = "";
  llmNarrative.value = "";
  try {
    const body = {};
    if (birthSolar.value) body.birth_solar = birthSolar.value.replace("T", " ");
    if (!useNow.value && nowSolar.value) body.now_solar = nowSolar.value.replace("T", " ");
    const r = await fetch("/api/yi-wiki/luu-van/llm-tong-doc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const t = await r.text();
      throw new Error(`HTTP ${r.status}: ${t}`);
    }
    const d = await r.json();
    llmNarrative.value = d.narrative || "(LLM trả về empty)";
    llmMeta.value = {
      provider: d.provider, model: d.model,
      tokens: d.tokens_used, patterns: d.patterns_count,
    };
  } catch (e) {
    llmError.value = String(e.message || e);
  } finally {
    llmLoading.value = false;
  }
}

// Drawer chi tiết quẻ (Cải tiến B)
const drawerHexagram = ref(null);
const drawerLoading = ref(false);
const drawerError = ref("");

async function openDrawer(vongKey) {
  const v = snapshot.value?.[vongKey];
  if (!v?.chinh?.number) return;
  drawerHexagram.value = { loading: true, vongLabel: v.paradigm_meta.ten, movingLine: v.moving_line };
  drawerLoading.value = true;
  drawerError.value = "";
  try {
    const r = await fetch(`/api/yi-wiki/kinh-dich/que/${v.chinh.number}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    drawerHexagram.value = { ...data, vongLabel: v.paradigm_meta.ten, movingLine: v.moving_line };
  } catch (e) {
    drawerError.value = String(e.message || e);
    drawerHexagram.value = null;
  } finally {
    drawerLoading.value = false;
  }
}
function closeDrawer() {
  drawerHexagram.value = null;
}

// Lightweight markdown renderer cho narrative
function renderInline(s) {
  if (!s) return "";
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/_([^_]+)_/g, "<i>$1</i>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function renderMarkdown(md) {
  if (!md) return "";
  const lines = md.split("\n");
  const out = [];
  let inList = false, inTable = false;
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i];
    const s = ln.trim();
    // Tables
    if (s.startsWith("|") && s.endsWith("|")) {
      if (!inTable) { out.push("<table>"); inTable = true; }
      if (s.match(/^\|\s*[-:]+\s*\|/)) continue; // separator
      const cells = s.slice(1, -1).split("|").map(c => c.trim());
      const isHeader = (i + 1 < lines.length && lines[i + 1].trim().match(/^\|\s*[-:]+/));
      const tag = isHeader ? "th" : "td";
      out.push("<tr>" + cells.map(c => `<${tag}>${renderInline(c)}</${tag}>`).join("") + "</tr>");
      continue;
    } else if (inTable) { out.push("</table>"); inTable = false; }

    if (!s) { if (inList) { out.push("</ul>"); inList = false; } continue; }
    let m;
    if ((m = s.match(/^(#{1,6})\s+(.*)$/))) {
      const lvl = m[1].length;
      if (inList) { out.push("</ul>"); inList = false; }
      out.push(`<h${lvl}>${renderInline(m[2])}</h${lvl}>`);
      continue;
    }
    if (s === "---") { out.push("<hr>"); continue; }
    if (s.startsWith("> ")) {
      if (inList) { out.push("</ul>"); inList = false; }
      out.push(`<blockquote>${renderInline(s.slice(2))}</blockquote>`);
      continue;
    }
    if (s.startsWith("- ") || s.startsWith("→ ") || s.match(/^[*]\s+/)) {
      if (!inList) { out.push("<ul>"); inList = true; }
      out.push(`<li>${renderInline(s.replace(/^[-→*]\s+/, ""))}</li>`);
      continue;
    }
    if (inList) { out.push("</ul>"); inList = false; }
    out.push(`<p>${renderInline(s)}</p>`);
  }
  if (inList) out.push("</ul>");
  if (inTable) out.push("</table>");
  return out.join("\n");
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
      <label class="form-toggle">
        <input type="checkbox" v-model="autoLoadUser" />
        Tự load ngày sinh từ profile (nếu đã đăng nhập)
      </label>

      <div class="form-row">
        <span class="form-label">📅 Sinh (dương):</span>
        <input type="datetime-local" v-model="birthSolar" />
        <small class="form-hint">→ sẽ tự convert sang âm lịch + can chi</small>
      </div>

      <label class="form-toggle">
        <input type="checkbox" v-model="useNow" />
        Dùng thời điểm hiện tại (bỏ check để chọn 1 thời điểm cụ thể)
      </label>
      <div v-if="!useNow" class="form-row">
        <span class="form-label">⏰ Bây giờ (dương):</span>
        <input type="datetime-local" v-model="nowSolar" />
      </div>

      <button class="btn-load" @click="loadSnapshot" :disabled="loading">
        {{ loading ? '⏳ Đang tính...' : '🔄 Tính 7 vòng' }}
      </button>
    </div>

    <div v-if="error" class="lvd-error">{{ error }}</div>

    <!-- Lịch song song -->
    <div v-if="calendarsBirth && calendarsNow" class="lvd-calendars">
      <div class="cal-card">
        <div class="cal-head">📅 Sinh</div>
        <div class="cal-grid">
          <div><span>Dương:</span> <code>{{ calendarsBirth.solar }}</code></div>
          <div><span>Âm:</span> <code>{{ calendarsBirth.lunar }}{{ calendarsBirth.is_leap ? ' (nhuận)' : '' }}</code></div>
          <div><span>Năm:</span> <b>{{ calendarsBirth.year_can_chi }}</b></div>
          <div><span>Giờ:</span> <b>{{ calendarsBirth.hour_chi }}</b></div>
        </div>
      </div>
      <div class="cal-card">
        <div class="cal-head">⏰ Bây giờ</div>
        <div class="cal-grid">
          <div><span>Dương:</span> <code>{{ calendarsNow.solar }}</code></div>
          <div><span>Âm:</span> <code>{{ calendarsNow.lunar }}{{ calendarsNow.is_leap ? ' (nhuận)' : '' }}</code></div>
          <div><span>Năm:</span> <b>{{ calendarsNow.year_can_chi }}</b></div>
          <div><span>Giờ:</span> <b>{{ calendarsNow.hour_chi }}</b></div>
        </div>
      </div>
    </div>

    <!-- 7 vòng -->
    <div v-if="snapshot" class="lvd-grid">
      <div v-for="(vong, i) in VONG_ORDER" :key="vong.key" class="vong-card"
           :style="{borderTopColor: vong.color}"
           @click="openDrawer(vong.key)" :title="'Bấm để mở chi tiết quẻ'">
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
        <div class="vong-name">
          <span v-if="snapshot[vong.key].chinh.number">#{{ snapshot[vong.key].chinh.number }} </span>
          {{ snapshot[vong.key].chinh.name_vi || snapshot[vong.key].chinh.name }}
          <span v-if="snapshot[vong.key].chinh.name_zh && snapshot[vong.key].chinh.name_zh !== '?'" class="vn-zh">{{ snapshot[vong.key].chinh.name_zh }}</span>
        </div>
        <div class="vong-struct">{{ snapshot[vong.key].chinh.name }}</div>
        <div class="vong-meta">
          <span>Hào động: <b>{{ snapshot[vong.key].moving_line }}</b></span>
        </div>

        <!-- Luận giải CỐT (mới) -->
        <div v-if="snapshot[vong.key].luan_giai?.loi_kinh" class="vong-luan">
          <div class="vong-han" v-if="snapshot[vong.key].luan_giai.loi_kinh">
            <span class="lbl">📜</span> {{ snapshot[vong.key].luan_giai.loi_kinh }}
          </div>
          <div class="vong-dich" v-if="snapshot[vong.key].luan_giai.loi_kinh_dich">
            <i>{{ snapshot[vong.key].luan_giai.loi_kinh_dich }}</i>
          </div>
          <div class="vong-hao" v-if="snapshot[vong.key].luan_giai.hao_brief">
            <span class="lbl">▸</span>
            <span v-html="renderInline(snapshot[vong.key].luan_giai.hao_brief)"></span>
          </div>
          <details v-if="snapshot[vong.key].luan_giai.tom_cot" class="vong-tom">
            <summary>📖 Tóm cốt + paradigm</summary>
            <p class="tom-cot">{{ snapshot[vong.key].luan_giai.tom_cot }}</p>
            <p class="paradigm-line"><b>Paradigm:</b> {{ snapshot[vong.key].paradigm_meta.paradigm }}</p>
          </details>
        </div>

        <div class="vong-bien-ho">
          <span>Biến: <code>{{ snapshot[vong.key].bien.name }}</code></span>
          <span>Hỗ: <code>{{ snapshot[vong.key].ho.name }}</code></span>
        </div>
      </div>
    </div>

    <!-- V2 — Patterns insight box -->
    <div v-if="snapshot?.patterns?.length" class="lvd-patterns">
      <h4>🔮 Patterns phát hiện ({{ snapshot.patterns.length }})</h4>
      <div v-for="(p, i) in snapshot.patterns" :key="i" class="pattern-card" :class="`sev-${p.severity}`">
        <div class="p-label">{{ p.label }}</div>
        <div class="p-detail">{{ p.detail }}</div>
      </div>
    </div>

    <!-- V1 — LLM Tổng đọc -->
    <div v-if="snapshot" class="lvd-llm-section">
      <div class="llm-header">
        <h4>🤖 LLM Tổng đọc sâu (DeepSeek)</h4>
        <button class="btn-llm" @click="callLLMTongDoc" :disabled="llmLoading">
          {{ llmLoading ? '⏳ Đang luận sâu (~15s)...' : (llmNarrative ? '🔄 Đọc lại' : '📜 Gọi LLM luận sâu') }}
        </button>
      </div>
      <div v-if="llmError" class="lvd-error">{{ llmError }}</div>
      <div v-if="llmNarrative" class="llm-result">
        <div v-if="llmMeta" class="llm-meta">
          Provider: <b>{{ llmMeta.provider }}</b> · Model: {{ llmMeta.model }} · Tokens: {{ llmMeta.tokens }} · Patterns: {{ llmMeta.patterns }}
        </div>
        <article class="llm-narrative" v-html="renderMarkdown(llmNarrative)"></article>
      </div>
    </div>

    <!-- Tổng đọc rule-based (fallback narrative) -->
    <div v-if="snapshot?.tong_doc" class="lvd-tong-doc">
      <h4>📖 Tổng đọc — 7 vòng kể chuyện gì?</h4>
      <article v-html="renderMarkdown(snapshot.tong_doc.narrative)"></article>
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
              <div>
                <span :style="{color: RELATION_COLOR[gt.the_vs_the.relation]}">●</span>
                {{ gt.the_vs_the.label_vi }}
              </div>
              <div v-if="gt.the_vs_the.paradigm_rich" class="gt-rich">{{ gt.the_vs_the.paradigm_rich }}</div>
            </td>
            <td>
              <div>
                <span :style="{color: RELATION_COLOR[gt.dung_vs_dung.relation]}">●</span>
                {{ gt.dung_vs_dung.label_vi }}
              </div>
              <div v-if="gt.dung_vs_dung.paradigm_rich" class="gt-rich">{{ gt.dung_vs_dung.paradigm_rich }}</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Drawer chi tiết quẻ (Cải tiến B) -->
    <aside v-if="drawerHexagram" class="lvd-drawer">
      <div class="ldr-head">
        <button class="ldr-close" @click="closeDrawer">✕</button>
        <span class="ldr-title">
          <small>{{ drawerHexagram.vongLabel }} · hào động {{ drawerHexagram.movingLine }}</small>
          <span v-if="drawerHexagram.number">#{{ drawerHexagram.number }} {{ drawerHexagram.name_vi }} {{ drawerHexagram.name_zh }}</span>
        </span>
      </div>
      <div class="ldr-body">
        <div v-if="drawerLoading" class="ldr-status">Đang đọc quẻ...</div>
        <div v-if="drawerError" class="ldr-error">Lỗi: {{ drawerError }}</div>
        <article v-if="drawerHexagram.body_markdown" v-html="renderMarkdown(drawerHexagram.body_markdown)"></article>
      </div>
    </aside>

    <!-- Paradigm footer -->
    <div v-if="snapshot" class="lvd-foot">
      <p>
        <b>⚠️ Paradigm Tổ sư Khang Tiết</b>: <i>"Quan vật chí huyền chí vi, lý chỉ dị minh"</i> — Trần Đoàn.
        {{ snapshot._paradigm_note }}
      </p>
      <p v-if="snapshot.birth_source" class="src">
        Source sinh thần: <code>{{ snapshot.birth_source }}</code>
      </p>
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
  display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; margin: 0.3rem 0;
}
.form-label { color: #fcd34d; font-size: 0.85rem; min-width: 130px; font-weight: 600; }
.form-row input[type=datetime-local] {
  background: #1e1b4b; color: #e0e7ff;
  border: 1px solid rgba(196, 181, 253, 0.3);
  padding: 0.3rem 0.5rem; border-radius: 4px; font-size: 0.85rem;
}
.form-hint { color: #6b7280; font-size: 0.75rem; font-style: italic; }
.form-toggle {
  font-size: 0.82rem; color: #cbd5e1; display: flex; align-items: center; gap: 0.35rem;
  margin: 0.3rem 0; cursor: pointer;
}
.btn-load {
  background: rgba(167, 139, 250, 0.2); border: 1px solid rgba(167, 139, 250, 0.5);
  color: #c4b5fd; padding: 0.45rem 1rem; border-radius: 5px; cursor: pointer;
  font-size: 0.88rem; margin-top: 0.4rem;
}
.btn-load:hover { background: rgba(167, 139, 250, 0.3); }
.lvd-error {
  color: #f87171; padding: 0.5rem 0.8rem;
  background: rgba(248, 113, 113, 0.08);
  border-left: 2px solid #f87171;
  border-radius: 4px; margin-bottom: 0.5rem;
}

/* Lịch song song */
.lvd-calendars {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-bottom: 1rem;
}
.cal-card {
  background: rgba(252, 211, 77, 0.06);
  border: 1px solid rgba(252, 211, 77, 0.18);
  border-radius: 5px; padding: 0.5rem 0.7rem;
}
.cal-head { color: #fcd34d; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.3rem; }
.cal-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.2rem 0.6rem;
  font-size: 0.8rem; color: #cbd5e1;
}
.cal-grid span { color: #94a3b8; margin-right: 0.3rem; }
.cal-grid b { color: #fbbf24; }
.cal-grid code {
  background: rgba(196, 181, 253, 0.12); padding: 1px 4px; border-radius: 3px;
  color: #c4b5fd; font-size: 0.78rem;
}

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
  cursor: pointer; transition: all .15s;
}
.vong-card:hover {
  background: rgba(252, 211, 77, 0.04);
  border-color: rgba(252, 211, 77, 0.3);
  transform: translateY(-1px);
}
.vong-header { display: flex; justify-content: space-between; align-items: baseline; }
.vong-label { font-weight: 600; font-size: 0.85rem; }
.vong-doi-moi { font-size: 0.65rem; color: #6b7280; font-style: italic; text-align: right; }
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
.vong-paradigm { margin-top: 0.3rem; font-size: 0.78rem; }
.vong-paradigm summary { color: #94a3b8; cursor: pointer; font-size: 0.75rem; }
.vong-paradigm p { color: #cbd5e1; margin: 0.3rem 0; line-height: 1.4; }
.vong-paradigm i { color: #fbbf24; }

/* CỐT: luận giải Lời Kinh + hào động */
.vong-struct {
  text-align: center; font-size: 0.72rem; color: #6b7280; margin-top: -0.1rem;
}
.vn-zh { font-size: 0.85rem; color: #e0e7ff; margin-left: 0.2rem; }
.vong-luan {
  background: rgba(252, 211, 77, 0.05);
  border-left: 2px solid rgba(252, 211, 77, 0.4);
  padding: 0.4rem 0.5rem; margin: 0.4rem 0;
  font-size: 0.78rem; line-height: 1.5;
}
.vong-han {
  color: #fde68a; font-weight: 600; margin-bottom: 0.2rem;
}
.vong-han .lbl { color: #fcd34d; margin-right: 0.25rem; }
.vong-dich { color: #cbd5e1; margin-bottom: 0.3rem; font-size: 0.78rem; }
.vong-dich i { color: #e0e7ff; font-style: italic; }
.vong-hao {
  color: #c4b5fd;
  border-top: 1px dashed rgba(196, 181, 253, 0.2);
  padding-top: 0.3rem;
  margin-top: 0.3rem;
  line-height: 1.5;
}
.vong-hao .lbl { color: #a78bfa; }
.vong-hao :deep(b) { color: #fbbf24; }
.vong-hao :deep(i) { color: #fde68a; }
.vong-tom { margin-top: 0.4rem; }
.vong-tom summary { color: #94a3b8; cursor: pointer; font-size: 0.7rem; }
.vong-tom .tom-cot { color: #cbd5e1; font-size: 0.75rem; margin: 0.3rem 0; line-height: 1.5; }
.vong-tom .paradigm-line { color: #94a3b8; font-size: 0.72rem; font-style: italic; }
.vong-tom .paradigm-line b { color: #fbbf24; font-style: normal; }

/* TỔNG ĐỌC narrative */
.lvd-tong-doc {
  margin-top: 1.5rem;
  background: linear-gradient(135deg, rgba(252, 211, 77, 0.06), rgba(167, 139, 250, 0.06));
  border: 1px solid rgba(252, 211, 77, 0.25);
  border-radius: 8px;
  padding: 1rem 1.2rem;
}
.lvd-tong-doc h4 {
  color: #fcd34d; margin: 0 0 0.5rem; font-size: 1rem;
}
.lvd-tong-doc article :deep(h2) {
  color: #fbbf24; font-size: 0.95rem; margin: 1rem 0 0.4rem;
  border-bottom: 1px solid rgba(252, 211, 77, 0.18); padding-bottom: 0.2rem;
}
.lvd-tong-doc article :deep(p) {
  color: #cbd5e1; line-height: 1.65; margin: 0.4rem 0; font-size: 0.88rem;
}
.lvd-tong-doc article :deep(b) { color: #fcd34d; }
.lvd-tong-doc article :deep(i) { color: #fde68a; }
.lvd-tong-doc article :deep(code) {
  background: rgba(196, 181, 253, 0.12); color: #c4b5fd;
  padding: 1px 5px; border-radius: 3px; font-size: 0.85rem;
}
.lvd-tong-doc article :deep(blockquote) {
  background: rgba(252, 211, 77, 0.06);
  border-left: 2px solid #fbbf24;
  padding: 0.4rem 0.7rem; margin: 0.5rem 0;
  font-style: italic; color: #fef3c7;
}
.lvd-tong-doc article :deep(ul) {
  padding-left: 1.4rem; line-height: 1.6; color: #cbd5e1;
}
.lvd-tong-doc article :deep(li) { margin: 0.2rem 0; }

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
.lvd-foot .src { font-size: 0.7rem; color: #6b7280; margin-top: 0.3rem; }
.lvd-foot code {
  background: rgba(196, 181, 253, 0.12); padding: 1px 4px; border-radius: 3px;
  color: #c4b5fd;
}

/* V2 — Patterns insight */
.lvd-patterns {
  margin-top: 1rem;
  background: rgba(248, 113, 113, 0.04);
  border: 1px solid rgba(248, 113, 113, 0.18);
  border-radius: 8px; padding: 0.8rem 1rem;
}
.lvd-patterns h4 { color: #f87171; margin: 0 0 0.5rem; font-size: 0.95rem; }
.pattern-card {
  padding: 0.5rem 0.7rem; margin-bottom: 0.5rem; border-radius: 5px;
  border-left: 3px solid;
}
.pattern-card.sev-high { background: rgba(248, 113, 113, 0.08); border-color: #f87171; }
.pattern-card.sev-medium { background: rgba(251, 191, 36, 0.06); border-color: #fbbf24; }
.pattern-card.sev-low { background: rgba(52, 211, 153, 0.06); border-color: #34d399; }
.p-label { font-weight: 600; color: #fcd34d; font-size: 0.92rem; margin-bottom: 0.2rem; }
.p-detail { color: #cbd5e1; font-size: 0.82rem; line-height: 1.5; }

/* V1 — LLM section */
.lvd-llm-section {
  margin-top: 1rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.06), rgba(252,211,77,0.04));
  border: 1px solid rgba(167,139,250,0.3);
  border-radius: 8px; padding: 0.8rem 1rem;
}
.llm-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; }
.llm-header h4 { color: #c4b5fd; margin: 0; font-size: 0.95rem; }
.btn-llm {
  background: rgba(167, 139, 250, 0.25); border: 1px solid rgba(167, 139, 250, 0.55);
  color: #c4b5fd; padding: 0.45rem 0.95rem; border-radius: 5px; cursor: pointer; font-size: 0.85rem;
}
.btn-llm:hover { background: rgba(167, 139, 250, 0.35); }
.btn-llm:disabled { opacity: 0.6; cursor: wait; }
.llm-result { margin-top: 0.7rem; }
.llm-meta {
  font-size: 0.74rem; color: #94a3b8; padding: 0.3rem 0.5rem;
  background: rgba(15, 23, 42, 0.4); border-radius: 4px; margin-bottom: 0.5rem;
}
.llm-meta b { color: #c4b5fd; }
.llm-narrative :deep(h1), .llm-narrative :deep(h2), .llm-narrative :deep(h3) {
  color: #fbbf24; margin: 0.8rem 0 0.4rem;
}
.llm-narrative :deep(h1) { font-size: 1.1rem; }
.llm-narrative :deep(h2) { font-size: 1rem; border-bottom: 1px solid rgba(252,211,77,0.18); padding-bottom: 0.15rem; }
.llm-narrative :deep(h3) { font-size: 0.92rem; }
.llm-narrative :deep(p) { color: #e2e8f0; line-height: 1.7; margin: 0.5rem 0; font-size: 0.9rem; }
.llm-narrative :deep(b) { color: #fcd34d; }
.llm-narrative :deep(i) { color: #fde68a; font-style: italic; }
.llm-narrative :deep(blockquote) {
  background: rgba(252,211,77,0.06); border-left: 2px solid #fbbf24;
  padding: 0.4rem 0.7rem; margin: 0.5rem 0; font-style: italic; color: #fef3c7;
}

/* V3 — paradigm_rich trong giao thoa */
.gt-rich {
  font-size: 0.75rem; color: #fde68a; margin-top: 0.2rem;
  font-style: italic; line-height: 1.4;
}

/* Drawer chi tiết quẻ (Cải tiến B) */
.lvd-drawer {
  position: fixed; top: 60px; right: 0; bottom: 0; width: 540px; max-width: 92vw;
  background: #0f172a; border-left: 2px solid #fcd34d; z-index: 200;
  display: flex; flex-direction: column; box-shadow: -4px 0 24px rgba(0,0,0,0.5);
}
.ldr-head {
  padding: 0.6rem 0.9rem; background: #422006; color: white;
  display: flex; gap: 0.7rem; align-items: center; flex-shrink: 0;
}
.ldr-close {
  background: rgba(255,255,255,0.18); border: none; color: white;
  padding: 0.25rem 0.6rem; border-radius: 4px; cursor: pointer; font-weight: bold;
}
.ldr-close:hover { background: rgba(255,255,255,0.3); }
.ldr-title { display: flex; flex-direction: column; line-height: 1.2; }
.ldr-title small { color: #fde68a; font-size: 0.72rem; font-style: italic; }
.ldr-title span { color: #fcd34d; font-weight: 600; }
.ldr-body { flex: 1; overflow-y: auto; padding: 1rem 1.2rem; }
.ldr-status, .ldr-error { padding: 1rem; text-align: center; color: #94a3b8; }
.ldr-error { color: #f87171; }
.ldr-body :deep(h1) { font-size: 1.25rem; color: #fcd34d; margin: 0.5rem 0; }
.ldr-body :deep(h2) { font-size: 1.05rem; color: #fbbf24; margin: 1rem 0 0.4rem; border-bottom: 1px solid rgba(252,211,77,0.18); padding-bottom: 0.2rem; }
.ldr-body :deep(h3) { font-size: 0.95rem; color: #fde68a; margin: 0.7rem 0 0.3rem; }
.ldr-body :deep(p) { color: #cbd5e1; line-height: 1.6; margin: 0.4rem 0; font-size: 0.88rem; }
.ldr-body :deep(b) { color: #fcd34d; }
.ldr-body :deep(i) { color: #fde68a; }
.ldr-body :deep(code) { background: rgba(196,181,253,0.12); color: #c4b5fd; padding: 1px 5px; border-radius: 3px; font-size: 0.85rem; }
.ldr-body :deep(blockquote) {
  background: rgba(252,211,77,0.06); border-left: 2px solid #fbbf24;
  padding: 0.4rem 0.7rem; margin: 0.5rem 0; color: #fef3c7; font-style: italic;
}
.ldr-body :deep(table) { border-collapse: collapse; width: 100%; margin: 0.5rem 0; font-size: 0.82rem; }
.ldr-body :deep(th), .ldr-body :deep(td) {
  border: 1px solid rgba(196,181,253,0.15); padding: 0.3rem 0.5rem; text-align: left; vertical-align: top;
}
.ldr-body :deep(th) { background: rgba(252,211,77,0.08); color: #fcd34d; }
.ldr-body :deep(td) { color: #cbd5e1; }
.ldr-body :deep(ul) { padding-left: 1.3rem; line-height: 1.55; }
.ldr-body :deep(li) { color: #cbd5e1; margin: 0.2rem 0; }
.ldr-body :deep(hr) { border: 0; border-top: 1px dashed rgba(252,211,77,0.25); margin: 1rem 0; }

@media (max-width: 700px) {
  .lvd-calendars { grid-template-columns: 1fr; }
  .cal-grid { grid-template-columns: 1fr; }
  .lvd-drawer { width: 100%; }
}
</style>
