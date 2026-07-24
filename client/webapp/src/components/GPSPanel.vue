<script setup>
import { computed, onMounted, ref, watch } from "vue";
import {
  getGpsAccuracy,
  getGpsDay,
  getGpsPredictions,
  gpsPreRegister,
  postGpsDayWithFamily,
  postGpsPreRegisterWithFamily,
  submitGpsPredictionFeedback,
} from "../lib/api";
import {
  familyMembers as sharedFamilyMembers,
  serializableMembers,
} from "../stores/familyStore.js";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";

const DOMAIN_COLOR = {
  decision:  "#e8c95a",
  work:      "#9a7b4a",
  finance:   "#c0a878",
  relations: "#3a6cb0",
  health:    "#5ab07a",
  creative:  "#d65a4a",
};

const inputBirth = ref("");

// MỘT NGUỒN: ngày sinh lấy từ hồ sơ tài khoản đang chọn; đổi profile → tự cập nhật + chạy lại.
// Nhập ngày sinh chỉ ở phần quản lý tài khoản (Iron: 2026-07-18).
useActivePersonBirth(inputBirth, { onReady: () => computePreview() });
const inputTargetDate = ref("");
const minScore = ref(70);
const gpsDay = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const registerStatus = ref("");
const predictions = ref([]);
const accuracy = ref(null);

const todayStr = computed(() => new Date().toISOString().slice(0, 10));

function tomorrow() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

const familyCount = computed(() => serializableMembers().length);
const useFamily = ref(true);

async function computePreview() {
  if (!inputBirth.value || !inputTargetDate.value) {
    errorMsg.value = "Cần ngày sinh + ngày mục tiêu";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  registerStatus.value = "";
  try {
    const birthIso = inputBirth.value.length === 16 ? inputBirth.value + ":00" : inputBirth.value;
    const members = serializableMembers();
    if (useFamily.value && members.length > 0) {
      const result = await postGpsDayWithFamily({
        birthDatetimeLocal: birthIso,
        targetDate: inputTargetDate.value,
        members,
        timezone: "Asia/Ho_Chi_Minh",
        minScore: Number(minScore.value),
      });
      const { status, ...payload } = result;
      gpsDay.value = payload;
    } else {
      gpsDay.value = await getGpsDay({
        birthDatetimeLocal: birthIso,
        targetDate: inputTargetDate.value,
        timezone: "Asia/Ho_Chi_Minh",
        minScore: Number(minScore.value),
      });
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

async function preRegister() {
  if (!gpsDay.value) return;
  loading.value = true;
  errorMsg.value = "";
  registerStatus.value = "";
  try {
    const birthIso = inputBirth.value.length === 16 ? inputBirth.value + ":00" : inputBirth.value;
    const members = serializableMembers();
    const result = (useFamily.value && members.length > 0)
      ? await postGpsPreRegisterWithFamily({
          birthDatetimeLocal: birthIso,
          targetDate: inputTargetDate.value,
          members,
          timezone: "Asia/Ho_Chi_Minh",
          minScore: Number(minScore.value),
        })
      : await gpsPreRegister({
          birthDatetimeLocal: birthIso,
          targetDate: inputTargetDate.value,
          timezone: "Asia/Ho_Chi_Minh",
          minScore: Number(minScore.value),
        });
    if (result.status === "registered") {
      registerStatus.value = `✓ Đã pre-register ${result.registered_count} prediction. Hash đã khóa.`;
      await refreshPredictions(result.profile_hash);
    } else if (result.status === "duplicate") {
      registerStatus.value = `⚠ ${result.message}`;
    } else if (result.status === "back_dating_rejected") {
      registerStatus.value = `❌ ${result.message}`;
    } else if (result.status === "gps_disabled") {
      registerStatus.value = `🔒 GPS bị khóa: ${result.message}`;
    } else {
      registerStatus.value = `Trạng thái: ${result.status}`;
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

async function refreshPredictions(profileHash) {
  predictions.value = [];
  try {
    const result = await getGpsPredictions({ profileHash, limit: 200 });
    predictions.value = result.predictions;
    const a = await getGpsAccuracy({ profileHash });
    accuracy.value = a;
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  }
}

const groupedPredictions = computed(() => {
  const map = new Map();
  for (const p of predictions.value) {
    const key = p.for_date;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(p);
  }
  return Array.from(map.entries()).sort((a, b) => b[0].localeCompare(a[0]));
});

async function submitFeedback(predictionId, responseEnum) {
  try {
    const r = await submitGpsPredictionFeedback({
      predictionId,
      responseEnum,
      confidenceEnum: "medium",
    });
    if (r.status === "stored") {
      registerStatus.value = `✓ Phản hồi ${responseEnum} đã lưu.`;
      const p = predictions.value.find((x) => x.prediction_id === predictionId);
      if (p && gpsDay.value) await refreshPredictions(gpsDay.value.profile_hash);
    } else {
      registerStatus.value = `${r.status}: ${r.message}`;
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  }
}

function isPast(forDate) {
  return forDate < todayStr.value;
}
</script>

<template>
  <section class="panel gps-panel">
    <div class="panel-title">
      <span>GPS — Điểm kích hoạt + Pre-registered prediction</span>
      <small>Phase 3 · EXPERIMENTAL</small>
    </div>

    <div v-if="gpsDay && gpsDay.runtime_mode" class="experimental-banner">
      <strong>{{ gpsDay.runtime_mode.mode }}:</strong>
      {{ gpsDay.runtime_mode.message }}
    </div>

    <p class="g-note">
      Engine đề xuất hành động cụ thể theo giờ + miền (quyết định / công việc / tài chính / quan hệ / sức khỏe / sáng tạo).
      Mỗi prediction được hash + lưu <b>immutable</b> — không sửa được sau khi đăng ký.
      Sau khi ngày trôi qua, anh phản hồi đúng/sai để hệ thống tích lũy độ tin cậy.
    </p>

    <div class="g-form">
      <label>
        <span>Ngày giờ sinh</span>
        <input v-model="inputBirth" type="datetime-local" step="60" />
      </label>
      <label>
        <span>Ngày mục tiêu</span>
        <input v-model="inputTargetDate" type="date" :min="todayStr" />
      </label>
      <label>
        <span>Min score</span>
        <input v-model.number="minScore" type="number" min="40" max="95" step="5" />
      </label>
      <button class="apply-btn" @click="computePreview" :disabled="loading">
        {{ loading ? "..." : "Preview" }}
      </button>
      <button class="register-btn" @click="preRegister" :disabled="loading || !gpsDay">
        Pre-register
      </button>
    </div>

    <div v-if="familyCount > 0" class="family-toggle">
      <label>
        <input type="checkbox" v-model="useFamily" />
        <span>Family overlay ({{ familyCount }} thành viên) — score blend 70% cá nhân + 30% gia đình</span>
      </label>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>
    <p v-if="registerStatus" class="status-message success">{{ registerStatus }}</p>

    <template v-if="gpsDay">
      <div class="g-summary">
        <div class="cell">
          <span>Ngày</span>
          <strong>{{ gpsDay.date_local }}</strong>
        </div>
        <div class="cell">
          <span>Quẻ ngày</span>
          <strong>{{ gpsDay.day_quai }} ({{ gpsDay.day_quai_king_wen }})</strong>
        </div>
        <div class="cell">
          <span>Trụ ngày</span>
          <strong>{{ gpsDay.day_pillar }}</strong>
        </div>
        <div class="cell">
          <span>Tiết khí</span>
          <strong>{{ gpsDay.solar_term }}</strong>
        </div>
      </div>
      <p class="g-summary-text">{{ gpsDay.composed_summary }}</p>

      <h5>Triggers ({{ gpsDay.triggers.length }})</h5>
      <ul class="trigger-list">
        <li v-for="(t, idx) in gpsDay.triggers" :key="idx"
          :style="{ borderLeftColor: DOMAIN_COLOR[t.domain] }">
          <div class="t-head">
            <span class="t-hour">{{ t.hour_branch }} <small>{{ t.hour_midpoint }}h</small></span>
            <span class="t-domain" :style="{ color: DOMAIN_COLOR[t.domain] }">{{ t.domain_vi }}</span>
            <span class="t-score">{{ t.score }}</span>
          </div>
          <div class="t-action">{{ t.action_text }}</div>
          <div v-if="t.family_overlay && t.family_overlay.length" class="t-family">
            <span class="fam-label">Gia đình (giờ {{ t.hour_branch }}):</span>
            <span v-for="o in t.family_overlay" :key="o.member_name"
              :class="['fam-tag', { pos: o.score > 0, neg: o.score < 0 }]">
              {{ o.member_name }}({{ o.member_year_branch }}) {{ o.interaction }} {{ o.score >= 0 ? '+' : '' }}{{ o.score }}
            </span>
            <span v-if="t.personal_only_score != null && t.personal_only_score !== t.score" class="fam-shift">
              · cá nhân {{ t.personal_only_score }} → blended {{ t.score }}
            </span>
          </div>
          <div class="t-rule">rule: <code>{{ t.rule_id }}</code></div>
        </li>
      </ul>
    </template>

    <template v-if="predictions.length">
      <h5>Predictions đã pre-register ({{ predictions.length }})</h5>
      <div v-if="accuracy" class="accuracy-block">
        <strong>Accuracy stats:</strong>
        đã có feedback: {{ accuracy.total_feedback }} / {{ predictions.length }}
        · matched: {{ accuracy.matched }}
        · partly: {{ accuracy.partly }}
        · false: {{ accuracy.false }}
        <span v-if="accuracy.match_rate !== null">
          · match rate: <b>{{ (accuracy.match_rate * 100).toFixed(0) }}%</b>
        </span>
        <small v-if="accuracy.total_feedback < accuracy.n_required_for_significance">
          (cần ≥{{ accuracy.n_required_for_significance }} datapoints để có ý nghĩa)
        </small>
      </div>

      <details v-for="[forDate, items] in groupedPredictions" :key="forDate"
        :open="isPast(forDate) && items.some(p => p.status === 'active')">
        <summary>
          {{ forDate }} <span class="ct">({{ items.length }} prediction)</span>
          <span v-if="isPast(forDate)" class="past-tag">đã qua — cần feedback</span>
        </summary>
        <ul class="pred-list">
          <li v-for="p in items" :key="p.prediction_id"
            :class="{ done: p.status === 'feedback_received' }">
            <div class="p-head">
              <span class="p-hour">{{ p.for_hour_branch }}</span>
              <span class="p-domain" :style="{ color: DOMAIN_COLOR[p.domain] }">{{ p.domain }}</span>
              <span class="p-score">{{ p.score }}</span>
              <span class="p-status">{{ p.status }}</span>
            </div>
            <div class="p-action">{{ p.action_text }}</div>
            <div class="p-meta">
              <small>hash: {{ p.payload_hash.slice(0, 12) }}…</small>
              <small>created: {{ p.created_at_utc.slice(0, 16) }}</small>
            </div>
            <div v-if="isPast(forDate) && p.status === 'active'" class="feedback-buttons">
              <button class="fb-btn matched" @click="submitFeedback(p.prediction_id, 'matched')">Đúng</button>
              <button class="fb-btn partly" @click="submitFeedback(p.prediction_id, 'partly')">Một phần</button>
              <button class="fb-btn false" @click="submitFeedback(p.prediction_id, 'false')">Sai</button>
              <button class="fb-btn unknown" @click="submitFeedback(p.prediction_id, 'unknown')">Không nhớ</button>
            </div>
          </li>
        </ul>
      </details>
    </template>

    <p v-else-if="!loading && !gpsDay" class="empty-hint">
      Nhập ngày sinh + ngày mục tiêu (tương lai) để xem điểm kích hoạt.
    </p>
  </section>
</template>

<style scoped>
.gps-panel { display: flex; flex-direction: column; gap: 12px; }

.experimental-banner {
  background: rgba(214, 90, 74, 0.12); border: 1px solid rgba(214, 90, 74, 0.4);
  border-radius: 8px; padding: 8px 12px; font-size: 0.78rem; color: #f0a89a;
  line-height: 1.5;
}
.experimental-banner strong { color: #ff9080; }

.g-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}

.g-form {
  display: grid; grid-template-columns: 1.3fr 1fr 0.6fr auto auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}
.g-form label { display: flex; flex-direction: column; gap: 4px;
  font-size: 0.78rem; color: rgba(255,255,255,0.7); }
.g-form input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 6px 8px; font-size: 0.82rem;
}
.apply-btn, .register-btn {
  padding: 7px 14px; border-radius: 6px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
  border: 1px solid;
}
.apply-btn {
  background: rgba(232,201,90,0.18); border-color: rgba(232,201,90,0.5); color: #e8c95a;
}
.register-btn {
  background: rgba(214,90,74,0.18); border-color: rgba(214,90,74,0.5); color: #ff9080;
}
.register-btn:disabled, .apply-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.g-summary {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
  background: rgba(232,201,90,0.06); padding: 10px; border-radius: 8px;
}
.cell { display: flex; flex-direction: column; gap: 2px; }
.cell span { font-size: 0.7rem; color: rgba(255,255,255,0.5); text-transform: uppercase; }
.cell strong { font-size: 0.92rem; color: #f5e6b1; }

.g-summary-text {
  font-size: 0.84rem; color: rgba(255,255,255,0.85);
  margin: 0; line-height: 1.5;
}

h5 {
  margin: 6px 0 0 0; font-size: 0.85rem;
  color: rgba(255,255,255,0.85); text-transform: uppercase; letter-spacing: 0.4px;
}

.trigger-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 4px;
  max-height: 400px; overflow-y: auto;
}
.trigger-list li {
  background: rgba(255,255,255,0.04); border-left: 3px solid;
  border-radius: 0 6px 6px 0; padding: 6px 10px;
}
.t-head {
  display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap;
  font-size: 0.82rem;
}
.t-hour { color: rgba(255,255,255,0.85); font-weight: 600; min-width: 70px; }
.t-hour small { color: rgba(255,255,255,0.5); margin-left: 3px; }
.t-domain { font-weight: 600; flex: 1; }
.t-score { font-weight: 700; color: #f5e6b1; font-size: 1rem; }
.t-action { font-size: 0.82rem; color: rgba(255,255,255,0.85); margin-top: 3px; line-height: 1.4; }
.t-rule { font-size: 0.7rem; color: rgba(255,255,255,0.4); margin-top: 2px; }
.t-rule code { background: rgba(255,255,255,0.06); padding: 1px 4px; border-radius: 3px; }

.accuracy-block {
  font-size: 0.78rem; color: rgba(255,255,255,0.85);
  background: rgba(74,176,194,0.06); border: 1px solid rgba(74,176,194,0.3);
  border-radius: 6px; padding: 8px 10px;
  display: flex; gap: 6px; flex-wrap: wrap;
}
.accuracy-block strong { color: #9adfe5; }
.accuracy-block small { color: rgba(255,255,255,0.5); margin-left: 6px; }

details {
  background: rgba(255,255,255,0.03); border-radius: 5px; padding: 4px 8px;
}
summary {
  font-size: 0.82rem; color: rgba(255,255,255,0.85); font-weight: 600;
  cursor: pointer; padding: 4px 0;
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
}
.ct { color: rgba(255,255,255,0.5); font-weight: 400; }
.past-tag {
  background: rgba(232,201,90,0.2); color: #e8c95a;
  padding: 1px 6px; border-radius: 3px; font-size: 0.7rem; font-weight: 700;
  margin-left: 4px;
}

.pred-list {
  list-style: none; margin: 0; padding: 4px 0 0 0;
  display: flex; flex-direction: column; gap: 4px;
}
.pred-list li {
  background: rgba(255,255,255,0.03); padding: 6px 8px; border-radius: 4px;
}
.pred-list li.done { opacity: 0.6; }
.p-head {
  display: flex; gap: 8px; align-items: baseline; font-size: 0.78rem;
}
.p-hour { color: rgba(255,255,255,0.85); font-weight: 600; min-width: 50px; }
.p-domain { font-weight: 600; flex: 1; }
.p-score { font-weight: 700; color: #f5e6b1; }
.p-status {
  font-size: 0.7rem; padding: 1px 6px; border-radius: 3px;
  background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.7);
}
.p-action { font-size: 0.78rem; color: rgba(255,255,255,0.85); margin-top: 3px; }
.p-meta {
  font-size: 0.7rem; color: rgba(255,255,255,0.4); margin-top: 2px;
  display: flex; gap: 10px;
}

.feedback-buttons { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
.fb-btn {
  padding: 3px 10px; border-radius: 4px; border: 1px solid;
  font-size: 0.74rem; cursor: pointer; font-weight: 600;
}
.fb-btn.matched { background: rgba(90,176,122,0.15); border-color: rgba(90,176,122,0.5); color: #9adcb0; }
.fb-btn.partly  { background: rgba(232,201,90,0.15); border-color: rgba(232,201,90,0.5); color: #e8c95a; }
.fb-btn.false   { background: rgba(214,90,74,0.15); border-color: rgba(214,90,74,0.5); color: #ff9080; }
.fb-btn.unknown { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.15); color: rgba(255,255,255,0.7); }

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

.t-family {
  font-size: 0.72rem; color: rgba(255,255,255,0.6);
  margin-top: 3px; display: flex; gap: 4px; flex-wrap: wrap; align-items: center;
}
.fam-label { color: rgba(255,255,255,0.45); margin-right: 2px; }
.fam-tag {
  background: rgba(255,255,255,0.06); padding: 1px 6px; border-radius: 3px;
}
.fam-tag.pos { background: rgba(90,176,122,0.12); color: #9adcb0; }
.fam-tag.neg { background: rgba(214,90,74,0.12); color: #ff9080; }
.fam-shift { color: rgba(232,201,90,0.7); font-style: italic; margin-left: 2px; }
</style>
