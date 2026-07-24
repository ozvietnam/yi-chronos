<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { getPersonalQuai, getVanTrongVan, postVanTrongVanWithFamily } from "../lib/api";
import {
  familyMembers as sharedFamilyMembers,
  serializableMembers,
} from "../stores/familyStore.js";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";
import ActivePersonBar from "./ActivePersonBar.vue";

const TRIGRAM_ELEMENT = {
  "Càn": "kim", "Đoài": "kim", "Ly": "hỏa", "Chấn": "mộc",
  "Tốn": "mộc", "Khảm": "thủy", "Cấn": "thổ", "Khôn": "thổ"
};
const ELEMENT_COLOR = {
  kim: "#c0a878", hỏa: "#d65a4a", mộc: "#5ab07a", thủy: "#3a6cb0", thổ: "#9a7b4a"
};

const inputBirth = ref("");

// MỘT NGUỒN: ngày sinh từ hồ sơ tài khoản đang chọn; đổi profile → tự cập nhật + chạy lại.
useActivePersonBirth(inputBirth, { onReady: () => load() });
const inputSpan = ref(30);
const natal = ref(null);
const outlook = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const expandedDay = ref(null);

const HOUR_BRANCH_ORDER = [
  "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
  "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
];

const familyCount = computed(() => serializableMembers().length);
const useFamily = ref(true);  // Auto-enable when family present.

async function load() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần nhập ngày giờ sinh";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  try {
    const birthIso = inputBirth.value.length === 16
      ? inputBirth.value + ":00"
      : inputBirth.value;
    natal.value = await getPersonalQuai({
      birthDatetimeLocal: birthIso,
      timezone: "Asia/Ho_Chi_Minh"
    });

    const members = serializableMembers();
    if (useFamily.value && members.length > 0) {
      const result = await postVanTrongVanWithFamily({
        birthDatetimeLocal: birthIso,
        members,
        timezone: "Asia/Ho_Chi_Minh",
        spanDays: Number(inputSpan.value),
      });
      // Strip the "status" envelope from POST response.
      const { status, ...payload } = result;
      outlook.value = payload;
    } else {
      outlook.value = await getVanTrongVan({
        birthDatetimeLocal: birthIso,
        timezone: "Asia/Ho_Chi_Minh",
        spanDays: Number(inputSpan.value)
      });
    }
    expandedDay.value = null;
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function scoreColor(score) {
  if (score >= 80) return "#5ab07a";
  if (score >= 65) return "#9adfe5";
  if (score >= 50) return "#e8c95a";
  if (score >= 35) return "#d68a4a";
  return "#d65a4a";
}

function scoreLabel(score) {
  if (score >= 80) return "rất hài hòa";
  if (score >= 65) return "thuận";
  if (score >= 50) return "trung tính";
  if (score >= 35) return "có ma sát";
  return "căng";
}

function fmtDate(iso) {
  return new Intl.DateTimeFormat("vi-VN", {
    weekday: "short", year: "numeric", month: "2-digit", day: "2-digit"
  }).format(new Date(iso));
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function isToday(d) {
  return d === todayIso();
}
</script>

<template>
  <section class="panel pq-panel">
    <div class="panel-title">
      <span>Quẻ bản mệnh + Vận trong vận 30 ngày</span>
      <small>Mai Hoa NNTT cá nhân hoá</small>
    </div>

    <p class="pq-note">
      Từ ngày giờ sinh, hệ thống dựng quẻ bản mệnh (Mai Hoa Niên-Nguyệt-Nhật-Thời).
      Sau đó so từng ngày tới với quẻ bản mệnh + Can-Chi sinh + tiết khí
      → mô tả độ hài hòa từ 0 đến 100. Đây là <b>mô tả trạng thái cộng hưởng</b>,
      không phải lời tiên tri.
    </p>

    <div class="pq-form">
      <ActivePersonBar />
      <label>
        <span>Số ngày tới</span>
        <input v-model.number="inputSpan" type="number" min="7" max="90" step="1" />
      </label>
      <button class="apply-btn" @click="load" :disabled="loading">
        {{ loading ? "Đang tính..." : "Vẽ" }}
      </button>
    </div>

    <div v-if="familyCount > 0" class="family-toggle">
      <label class="checkbox">
        <input type="checkbox" v-model="useFamily" />
        <span>Áp dụng family overlay ({{ familyCount }} thành viên trong store) — score blend 70% cá nhân + 30% gia đình</span>
      </label>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="natal">
      <div class="natal-block">
        <h5>Quẻ bản mệnh</h5>
        <div class="natal-head">
          <span class="natal-quai">
            {{ natal.primary_name }}
            <small>(quẻ {{ natal.primary_king_wen }} · {{ natal.primary_binary }})</small>
          </span>
          <span class="natal-trigrams">
            <b :style="{ color: ELEMENT_COLOR[TRIGRAM_ELEMENT[natal.upper_trigram]] }">{{ natal.upper_trigram }}</b>
            <span class="sep">/</span>
            <b :style="{ color: ELEMENT_COLOR[TRIGRAM_ELEMENT[natal.lower_trigram]] }">{{ natal.lower_trigram }}</b>
            <small>hào động {{ natal.moving_line }}</small>
          </span>
        </div>
        <div class="natal-meta">
          <span><b>Can-Chi sinh:</b> {{ natal.natal_ganzhi.year }} · {{ natal.natal_ganzhi.month }} · {{ natal.natal_ganzhi.day }} · {{ natal.natal_ganzhi.hour }}</span>
          <span><b>Tiết khí sinh:</b> {{ natal.natal_solar_term }}</span>
        </div>
        <div class="derived-row">
          <span v-for="key in ['chanh', 'ho', 'bien', 'giao', 'phuc', 'bao']" :key="key" class="d-cell">
            <span class="dk">{{ key }}</span>
            <span class="dn">{{ natal.derived_hexagrams[key].name_vi }}</span>
          </span>
        </div>
      </div>
    </template>

    <template v-if="outlook">
      <h5 class="outlook-title">{{ outlook.span_days }} ngày tới — vận trong vận</h5>
      <div class="outlook-grid">
        <div v-for="d in outlook.days" :key="d.date_local"
          :class="['day-card', { today: isToday(d.date_local), expanded: expandedDay === d.date_local }]"
          @click="expandedDay = expandedDay === d.date_local ? null : d.date_local">
          <div class="dc-head">
            <span class="dc-date">{{ fmtDate(d.date_local) }}</span>
            <span class="dc-score" :style="{ color: scoreColor(d.final_score_with_family ?? d.day_compatibility.final_score) }">
              {{ d.final_score_with_family ?? d.day_compatibility.final_score }}
              <small v-if="d.final_score_with_family !== null && d.final_score_with_family !== undefined"
                :title="`Cá nhân ${d.day_compatibility.final_score}, gia đình ${d.family_avg_score >= 0 ? '+' : ''}${d.family_avg_score}`">
                ({{ d.day_compatibility.final_score }}<span :style="{ color: d.family_avg_score >= 0 ? '#5ab07a' : '#d65a4a' }">
                  {{ d.family_avg_score >= 0 ? '+' : '' }}{{ d.family_avg_score }}fam</span>)
              </small>
            </span>
          </div>
          <div class="dc-body">
            <span class="dc-pillar">{{ d.day_pillar }}</span>
            <span class="dc-quai">{{ d.primary_name }}</span>
          </div>
          <div class="dc-meta">
            <small>Tiết: {{ d.solar_term }}</small>
            <small>Best giờ: <b>{{ d.best_hour_branch }}</b> ({{ d.best_hour_score }})</small>
          </div>
          <div class="dc-bar">
            <div class="dc-fill" :style="{
              width: d.day_compatibility.final_score + '%',
              background: scoreColor(d.day_compatibility.final_score)
            }"></div>
          </div>

          <div v-if="expandedDay === d.date_local" class="dc-detail">
            <div class="lbl">{{ scoreLabel(d.day_compatibility.final_score) }}</div>
            <ul class="notes">
              <li v-for="(n, i) in d.day_compatibility.notes" :key="i">{{ n }}</li>
            </ul>
            <h6>12 giờ — score từng giờ</h6>
            <div class="hour-grid">
              <div v-for="slot in d.all_hour_scores" :key="slot.branch"
                class="hour-cell"
                :class="{ best: slot.branch === d.best_hour_branch }"
                :style="{ background: scoreColor(slot.score) + '33' }">
                <span class="hb">{{ slot.branch }}</span>
                <span class="ht">{{ slot.midpoint_hour }}h</span>
                <span class="hs" :style="{ color: scoreColor(slot.score) }">{{ slot.score }}</span>
              </div>
            </div>

            <template v-if="d.family_overlay && d.family_overlay.length">
              <h6>Gia đình overlay (chi vs ngày)</h6>
              <ul class="family-overlay">
                <li v-for="o in d.family_overlay" :key="o.member_name"
                  :class="{ pos: o.score > 0, neg: o.score < 0 }">
                  <b>{{ o.member_role_vi }} {{ o.member_name }}</b>
                  ({{ o.member_year_branch }}):
                  {{ o.interaction }}
                  <span :class="{ pos: o.score > 0, neg: o.score < 0 }">
                    {{ o.score >= 0 ? '+' : '' }}{{ o.score }}
                  </span>
                  · <em>{{ o.explanation }}</em>
                </li>
              </ul>
            </template>
          </div>
        </div>
      </div>
    </template>

    <p v-else-if="!loading && !natal" class="empty-hint">
      Nhập ngày giờ sinh để bắt đầu.
    </p>
  </section>
</template>

<style scoped>
.pq-panel { display: flex; flex-direction: column; gap: 12px; }
.pq-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}
.pq-form {
  display: grid; grid-template-columns: 2fr 1fr auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}
.pq-form label {
  display: flex; flex-direction: column; gap: 4px;
  font-size: 0.78rem; color: rgba(255,255,255,0.7);
}
.pq-form input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 6px 8px; font-size: 0.85rem;
}
.apply-btn {
  background: rgba(232,201,90,0.18); border: 1px solid rgba(232,201,90,0.5);
  color: #e8c95a; padding: 8px 16px; border-radius: 6px;
  font-size: 0.85rem; font-weight: 600; cursor: pointer;
}
.apply-btn:disabled { opacity: 0.5; cursor: not-allowed; }

h5, .outlook-title {
  margin: 6px 0 0 0; font-size: 0.85rem;
  color: rgba(255,255,255,0.85); text-transform: uppercase;
  letter-spacing: 0.4px; font-weight: 600;
}

.natal-block {
  background: rgba(232,201,90,0.06); border: 1px solid rgba(232,201,90,0.25);
  border-radius: 8px; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 6px;
}
.natal-head {
  display: flex; justify-content: space-between; align-items: baseline;
  gap: 8px; flex-wrap: wrap;
}
.natal-quai { font-size: 1.1rem; font-weight: 700; color: #f5e6b1; }
.natal-quai small { color: rgba(255,255,255,0.55); font-weight: 400; margin-left: 4px; }
.natal-trigrams { font-size: 0.92rem; }
.natal-trigrams .sep { color: rgba(255,255,255,0.4); margin: 0 4px; }
.natal-trigrams small { margin-left: 6px; color: rgba(255,255,255,0.55); }
.natal-meta {
  display: flex; gap: 14px; flex-wrap: wrap;
  font-size: 0.78rem; color: rgba(255,255,255,0.85);
}
.natal-meta b { color: rgba(255,255,255,0.55); font-weight: 500; }
.derived-row {
  display: flex; gap: 4px; flex-wrap: wrap;
  font-size: 0.74rem;
}
.d-cell {
  display: flex; gap: 4px; align-items: baseline;
  background: rgba(255,255,255,0.04); padding: 3px 8px; border-radius: 4px;
}
.d-cell .dk { color: rgba(255,255,255,0.5); text-transform: uppercase; font-size: 0.7rem; }
.d-cell .dn { color: rgba(255,255,255,0.85); }

.outlook-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 6px;
}
.day-card {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px; padding: 8px 10px; cursor: pointer;
  display: flex; flex-direction: column; gap: 4px;
  transition: background 0.15s, border 0.15s;
}
.day-card:hover { background: rgba(255,255,255,0.07); }
.day-card.today { border-color: rgba(232,201,90,0.6); background: rgba(232,201,90,0.06); }
.day-card.expanded { grid-column: 1 / -1; background: rgba(232,201,90,0.04); }

.dc-head { display: flex; justify-content: space-between; align-items: baseline; }
.dc-date { font-size: 0.78rem; color: rgba(255,255,255,0.8); font-weight: 600; }
.dc-score { font-size: 1.3rem; font-weight: 700; }
.dc-body { display: flex; gap: 8px; align-items: baseline; font-size: 0.78rem; }
.dc-pillar { color: rgba(255,255,255,0.55); font-family: ui-monospace, monospace; font-size: 0.74rem; }
.dc-quai { color: #f5e6b1; font-weight: 600; }
.dc-meta { display: flex; gap: 6px; font-size: 0.7rem; color: rgba(255,255,255,0.5); flex-wrap: wrap; }
.dc-meta b { color: rgba(255,255,255,0.85); }
.dc-bar {
  height: 4px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden;
}
.dc-fill { height: 100%; transition: width 0.2s; }

.dc-detail {
  margin-top: 8px; padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex; flex-direction: column; gap: 6px;
}
.dc-detail .lbl {
  font-size: 0.82rem; color: #f5e6b1; font-weight: 600;
  text-transform: lowercase;
}
.notes { list-style: disc inside; margin: 0; padding: 0; font-size: 0.74rem; color: rgba(255,255,255,0.78); }
.notes li { padding: 1px 0; }

h6 {
  margin: 4px 0 2px 0; font-size: 0.74rem;
  color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 0.4px;
}

.hour-grid {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 3px;
}
.hour-cell {
  display: flex; flex-direction: column; align-items: center; gap: 1px;
  padding: 4px 2px; border-radius: 3px;
  font-size: 0.7rem;
}
.hour-cell.best { outline: 1px solid #e8c95a; }
.hb { color: rgba(255,255,255,0.85); font-weight: 600; }
.ht { color: rgba(255,255,255,0.5); font-size: 0.65rem; }
.hs { font-weight: 700; font-size: 0.78rem; }

.empty-hint {
  font-size: 0.85rem; color: rgba(255,255,255,0.5);
  text-align: center; padding: 24px 0; margin: 0;
}

.family-toggle {
  background: rgba(74,176,194,0.05); border: 1px solid rgba(74,176,194,0.2);
  border-radius: 6px; padding: 6px 10px;
}
.family-toggle label { display: flex; align-items: center; gap: 6px; cursor: pointer; }
.family-toggle span { font-size: 0.78rem; color: rgba(255,255,255,0.85); }

.dc-score small {
  display: block; font-size: 0.62rem; font-weight: 400;
  color: rgba(255,255,255,0.6); margin-top: 1px;
}

.family-overlay { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
.family-overlay li { font-size: 0.72rem; color: rgba(255,255,255,0.75); padding: 2px 6px; border-radius: 3px; }
.family-overlay li.pos { background: rgba(90,176,122,0.06); }
.family-overlay li.neg { background: rgba(214,90,74,0.06); }
.family-overlay b { color: #f5e6b1; }
.family-overlay em { color: rgba(255,255,255,0.55); font-style: italic; }
.family-overlay span.pos { color: #9adcb0; font-weight: 700; }
.family-overlay span.neg { color: #ff9080; font-weight: 700; }
</style>
