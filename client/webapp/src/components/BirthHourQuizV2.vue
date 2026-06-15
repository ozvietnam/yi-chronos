<script setup>
/**
 * BirthHourQuizV2 — multi-round adaptive birth-hour quiz.
 *
 * 4 stages: input → loading → round → result.
 * Calls /api/yi-wiki/birth-hour-quiz-v2/{start,submit-round}.
 */
import { ref, computed, onMounted, watch } from "vue";
import { activePerson } from "../stores/userDataStore.js";

// Stage: 'input' | 'loading' | 'round' | 'result'
const stage = ref("input");

const form = ref({
  birth_date: "",
  timezone: "Asia/Ho_Chi_Minh",
  hour_start: 6,
  hour_end: 12,
  no_idea: false,
  gender: "nam",
});

// Tự điền ngày sinh + giới tính từ profile (giờ là cái cần dò nên giữ khoảng tìm).
function _syncBirth() {
  const p = activePerson.value;
  if (p?.birth_datetime_local) form.value.birth_date = p.birth_datetime_local.split("T")[0];
  if (p?.gender) form.value.gender = p.gender;
}
onMounted(_syncBirth);
watch(() => activePerson.value?.person_key, _syncBirth);

const session = ref(null);        // { session_id, strategy, candidates }
const currentRound = ref(null);   // { round_num, total_rounds, questions }
const answers = ref({});          // { trait_id: option_id }
const finalResult = ref(null);
const error = ref("");
const loading = ref(false);

async function startQuiz() {
  loading.value = true;
  stage.value = "loading";
  error.value = "";
  try {
    const body = {
      birth_date: form.value.birth_date,
      timezone: form.value.timezone,
      hour_range: form.value.no_idea
        ? null
        : { start: form.value.hour_start, end: form.value.hour_end },
      gender: form.value.gender,
    };
    const r = await fetch("/api/yi-wiki/birth-hour-quiz-v2/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const text = await r.text();
    let d;
    try {
      d = JSON.parse(text);
    } catch {
      error.value = `Server lỗi (HTTP ${r.status}): ${text.slice(0, 200)}`;
      stage.value = "input";
      return;
    }
    if (d.status !== "ok") {
      error.value = (d.message || "Không tạo được session") +
                    (d.hint ? ` — ${d.hint}` : "");
      stage.value = "input";
      return;
    }
    session.value = d;
    currentRound.value = d.round_1;
    answers.value = {};
    stage.value = "round";
  } catch (e) {
    error.value = String(e);
    stage.value = "input";
  } finally {
    loading.value = false;
  }
}

async function submitRound() {
  loading.value = true;
  error.value = "";
  try {
    const r = await fetch("/api/yi-wiki/birth-hour-quiz-v2/submit-round", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session.value.session_id,
        round_num: currentRound.value.round_num,
        answers: answers.value,
      }),
    });
    const text = await r.text();
    let d;
    try {
      d = JSON.parse(text);
    } catch {
      error.value = `Server lỗi (HTTP ${r.status}): ${text.slice(0, 200)}`;
      return;
    }
    if (d.status === "CONTINUE") {
      currentRound.value = d.next_round;
      answers.value = {};
    } else if (d.status === "FINAL" || d.status === "FINAL_UNCERTAIN") {
      finalResult.value = d.final_result;
      stage.value = "result";
    } else {
      error.value = d.message || "Lỗi không rõ";
    }
  } catch (e) {
    error.value = String(e);
  } finally {
    loading.value = false;
  }
}

function restart() {
  stage.value = "input";
  session.value = null;
  currentRound.value = null;
  answers.value = {};
  finalResult.value = null;
  error.value = "";
}

const allAnswered = computed(() => {
  if (!currentRound.value) return false;
  return currentRound.value.questions.every(q => answers.value[q.id]);
});

const sortedScores = computed(() => {
  if (!finalResult.value?.scores) return [];
  return Object.entries(finalResult.value.scores)
    .sort((a, b) => b[1] - a[1]);
});
</script>

<template>
  <div class="bhq2">
    <!-- Stage 1: INPUT -->
    <section v-if="stage === 'input'" class="bhq2-input">
      <h2>🕐 Tìm lại giờ sinh — bộ trắc nghiệm bát tự</h2>
      <p class="bhq2-hint">
        Engine sẽ tạo nhiều giả thiết bát tự (theo các giờ chi khác nhau)
        và đặt câu hỏi về ngoại hình + tính cách để khoanh vùng giờ sinh thực.
      </p>

      <label class="bhq2-field">
        <span>Ngày sinh</span>
        <input type="date" v-model="form.birth_date" />
      </label>

      <label class="bhq2-field">
        <span>Múi giờ</span>
        <select v-model="form.timezone">
          <option value="Asia/Ho_Chi_Minh">Asia/Ho_Chi_Minh (VN)</option>
          <option value="Asia/Shanghai">Asia/Shanghai (TQ)</option>
        </select>
      </label>

      <div class="bhq2-field">
        <span>Giới tính</span>
        <label class="bhq2-radio">
          <input type="radio" value="nam" v-model="form.gender" /> Nam
        </label>
        <label class="bhq2-radio">
          <input type="radio" value="nữ" v-model="form.gender" /> Nữ
        </label>
      </div>

      <div class="bhq2-range">
        <p><b>Anh nhớ giờ trong khoảng nào?</b></p>
        <div class="bhq2-range-inputs" :class="{ 'is-disabled': form.no_idea }">
          <label>
            Từ: <input type="number" min="0" max="23"
                       v-model.number="form.hour_start"
                       :disabled="form.no_idea" />h
          </label>
          <label>
            Đến: <input type="number" min="0" max="23"
                        v-model.number="form.hour_end"
                        :disabled="form.no_idea" />h
          </label>
        </div>
        <label class="bhq2-no-idea">
          <input type="checkbox" v-model="form.no_idea" />
          Không nhớ gì (sẽ chia 3 vòng quét toàn bộ 24h)
        </label>
      </div>

      <button class="bhq2-primary" @click="startQuiz" :disabled="loading">
        {{ loading ? "Đang chuẩn bị..." : "Bắt đầu trắc nghiệm →" }}
      </button>
      <p v-if="error" class="bhq2-error">{{ error }}</p>
    </section>

    <!-- Stage 2: LOADING -->
    <section v-else-if="stage === 'loading'" class="bhq2-loading">
      <p>⏳ Đang phân tích bát tự...</p>
      <p class="bhq2-small">
        Engine derive 19 traits × candidates. LLM (DeepSeek-Reasoner) nuận
        tính cách + life events. Mất ~10-30 giây.
      </p>
    </section>

    <!-- Stage 3: ROUND -->
    <section v-else-if="stage === 'round'" class="bhq2-round">
      <header class="bhq2-round-header">
        <span><b>Vòng {{ currentRound.round_num }}/{{ currentRound.total_rounds }}</b></span>
        <span class="bhq2-cands">còn {{ session.candidates.length }} ứng cử ban đầu</span>
      </header>

      <ol class="bhq2-questions">
        <li v-for="q in currentRound.questions" :key="q.id" class="bhq2-question">
          <p class="bhq2-q-text">
            <b>{{ q.question }}</b>
            <small class="bhq2-domain">({{ q.domain }})</small>
          </p>
          <div class="bhq2-options">
            <label v-for="opt in q.options" :key="opt.id" class="bhq2-option">
              <input type="radio" :name="q.id" :value="opt.id" v-model="answers[q.id]" />
              <span>{{ opt.label }}</span>
            </label>
          </div>
        </li>
      </ol>

      <button class="bhq2-primary" @click="submitRound"
              :disabled="!allAnswered || loading">
        {{ loading ? "Đang chấm điểm..." : `Submit Vòng ${currentRound.round_num} →` }}
      </button>
      <p v-if="!allAnswered" class="bhq2-small">
        Trả lời đủ {{ currentRound.questions.length }} câu để submit.
      </p>
      <p v-if="error" class="bhq2-error">{{ error }}</p>
    </section>

    <!-- Stage 4: RESULT -->
    <section v-else-if="stage === 'result'" class="bhq2-result">
      <h3>🎯 Giờ sinh có khả năng cao nhất</h3>
      <div class="bhq2-winner" v-if="finalResult.top_chi">
        <div class="bhq2-chi">
          {{ finalResult.top_chi }}
          <span class="bhq2-range-text">
            ({{ finalResult.hour_ranges[finalResult.top_chi] }})
          </span>
        </div>
        <div class="bhq2-conf">
          Confidence: <b>{{ finalResult.confidence }}</b>
          <span v-if="finalResult.status === 'FINAL_UNCERTAIN'" class="bhq2-uncertain">
            · vẫn còn nhập nhằng
          </span>
        </div>
      </div>

      <h4>📊 Điểm số per candidate</h4>
      <ul class="bhq2-scores">
        <li v-for="[chi, score] in sortedScores" :key="chi"
            :class="{ 'is-top': chi === finalResult.top_chi }">
          <b>{{ chi }}</b>: {{ score.toFixed(1) }} điểm
        </li>
      </ul>

      <p class="bhq2-small">
        💡 Confidence Cao = chênh ≥5 điểm với ứng cử thứ 2. Vừa = 2-5 điểm. Thấp = &lt;2.
      </p>

      <div class="bhq2-actions">
        <button class="bhq2-primary" @click="restart">🔄 Trắc nghiệm lại</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Dark theme matching YI-CHRONOS site palette (slate-900 + amber + purple). */
.bhq2 {
  max-width: 720px;
  margin: 0 auto;
  padding: 0.5rem;
  color: #e2e8f0;
}
.bhq2 h2, .bhq2 h3, .bhq2 h4 { color: #fbbf24; margin: 0 0 0.8rem; }
.bhq2 h2 { font-size: 1.15rem; }
.bhq2 h3 { font-size: 1rem; }
.bhq2-hint { color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem; line-height: 1.5; }
.bhq2-error {
  color: #fca5a5;
  padding: 0.7rem 0.9rem;
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.4);
  border-radius: 6px;
  font-size: 0.85rem;
  margin-top: 0.8rem;
}
.bhq2-small { color: #94a3b8; font-size: 0.78rem; margin-top: 0.4rem; }

/* Form fields */
.bhq2-field {
  display: block;
  margin: 0.8rem 0;
  font-size: 0.85rem;
}
.bhq2-field > span:first-child {
  display: block;
  margin-bottom: 0.3rem;
  color: #94a3b8;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.bhq2-field input[type="date"],
.bhq2-field input[type="number"],
.bhq2-field select {
  padding: 0.5rem 0.7rem;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(167,139,250,0.3);
  border-radius: 6px;
  color: #e2e8f0;
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
}
.bhq2-field select:focus,
.bhq2-field input:focus {
  outline: none;
  border-color: #a78bfa;
}
.bhq2-radio {
  display: inline-flex;
  align-items: center;
  margin-right: 1.2rem;
  cursor: pointer;
  color: #e2e8f0;
}
.bhq2-radio input { margin-right: 0.4rem; }

/* Range slider area */
.bhq2-range {
  padding: 0.9rem 1rem;
  background: rgba(167,139,250,0.08);
  border: 1px solid rgba(167,139,250,0.2);
  border-radius: 8px;
  margin: 1rem 0;
}
.bhq2-range p { margin: 0 0 0.5rem; color: #cbd5e1; font-size: 0.85rem; }
.bhq2-range-inputs {
  display: flex;
  gap: 1.2rem;
  margin: 0.6rem 0;
  flex-wrap: wrap;
  align-items: center;
}
.bhq2-range-inputs label { color: #cbd5e1; font-size: 0.85rem; }
.bhq2-range-inputs input { width: 4em; padding: 0.3rem 0.5rem; }
.bhq2-range-inputs.is-disabled { opacity: 0.4; }
.bhq2-no-idea {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.6rem;
  cursor: pointer;
  color: #cbd5e1;
  font-size: 0.85rem;
}

/* Primary button */
.bhq2-primary {
  padding: 0.7rem 1.4rem;
  font-size: 0.92rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.9), rgba(251,191,36,0.8));
  color: #0f172a;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 600;
}
.bhq2-primary:disabled {
  background: rgba(148,163,184,0.3);
  color: #94a3b8;
  cursor: not-allowed;
}

/* Round header + progress */
.bhq2-round-header {
  display: flex;
  justify-content: space-between;
  padding: 0.6rem 0;
  border-bottom: 1px solid rgba(167,139,250,0.3);
  margin-bottom: 1rem;
  color: #fbbf24;
  font-size: 0.9rem;
}
.bhq2-cands { color: #94a3b8; font-size: 0.8rem; }

/* Question list */
.bhq2-questions { padding-left: 1.2rem; }
.bhq2-question {
  margin-bottom: 1.3rem;
  padding: 0.6rem 0.8rem;
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(167,139,250,0.15);
  border-radius: 6px;
}
.bhq2-q-text { margin: 0 0 0.6rem; color: #e2e8f0; font-size: 0.9rem; }
.bhq2-domain {
  color: #c4b5fd;
  font-size: 0.75rem;
  font-weight: normal;
  margin-left: 0.5em;
  font-style: italic;
}
.bhq2-options {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-left: 0.5rem;
}
.bhq2-option {
  cursor: pointer;
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  color: #cbd5e1;
  font-size: 0.85rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}
.bhq2-option:hover { background: rgba(167,139,250,0.1); }
.bhq2-option input { margin-top: 0.18rem; }

/* Result winner card */
.bhq2-winner {
  padding: 1.4rem;
  background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(167,139,250,0.12));
  border: 2px solid rgba(251,191,36,0.5);
  border-radius: 10px;
  margin: 1rem 0;
  text-align: center;
}
.bhq2-chi { font-size: 1.6rem; font-weight: bold; color: #fbbf24; }
.bhq2-range-text { font-size: 0.65em; color: #c4b5fd; font-weight: normal; }
.bhq2-conf { margin-top: 0.5rem; color: #e2e8f0; font-size: 0.9rem; }
.bhq2-uncertain { color: #fbbf24; font-size: 0.8rem; }

/* Scores */
.bhq2-scores { padding-left: 1.2rem; list-style: none; margin: 0.5rem 0; }
.bhq2-scores li {
  padding: 0.35rem 0.6rem;
  border-radius: 4px;
  color: #cbd5e1;
  font-size: 0.85rem;
}
.bhq2-scores li.is-top {
  background: rgba(251,191,36,0.15);
  color: #fbbf24;
  font-weight: 500;
}

.bhq2-loading {
  text-align: center;
  padding: 3rem 1rem;
  color: #cbd5e1;
}
.bhq2-actions { margin-top: 1.2rem; }
</style>
