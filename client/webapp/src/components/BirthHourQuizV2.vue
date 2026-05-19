<script setup>
/**
 * BirthHourQuizV2 — multi-round adaptive birth-hour quiz.
 *
 * 4 stages: input → loading → round → result.
 * Calls /api/yi-wiki/birth-hour-quiz-v2/{start,submit-round}.
 */
import { ref, computed } from "vue";

// Stage: 'input' | 'loading' | 'round' | 'result'
const stage = ref("input");

const form = ref({
  birth_date: "1988-05-02",
  timezone: "Asia/Ho_Chi_Minh",
  hour_start: 6,
  hour_end: 12,
  no_idea: false,
  gender: "nam",
});

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
    const d = await r.json();
    if (d.status !== "ok") {
      error.value = d.message || "Không tạo được session";
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
    const d = await r.json();
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
.bhq2 { max-width: 720px; margin: 0 auto; padding: 1rem; }
.bhq2-field { display: block; margin: 0.6rem 0; }
.bhq2-field > span:first-child { display: inline-block; min-width: 110px; font-weight: 500; }
.bhq2-field input, .bhq2-field select { padding: 0.3rem; }
.bhq2-radio { margin-right: 1rem; cursor: pointer; }
.bhq2-hint { color: #666; font-size: 0.9em; margin-bottom: 1rem; }
.bhq2-error { color: #c33; padding: 0.5rem; background: #fee; border-radius: 4px; }
.bhq2-primary {
  padding: 0.6rem 1.4rem; font-size: 1em; background: #4a90e2; color: #fff;
  border: 0; border-radius: 6px; cursor: pointer; margin-top: 1rem; font-weight: 500;
}
.bhq2-primary:disabled { background: #aaa; cursor: not-allowed; }
.bhq2-range { padding: 0.8rem; background: #f7faff; border-radius: 6px; margin: 1rem 0; }
.bhq2-range-inputs { display: flex; gap: 1rem; margin: 0.5rem 0; }
.bhq2-range-inputs input { width: 5em; padding: 0.3rem; }
.bhq2-range-inputs.is-disabled { opacity: 0.4; }
.bhq2-no-idea { display: block; margin-top: 0.5rem; cursor: pointer; }
.bhq2-round-header {
  display: flex; justify-content: space-between; padding: 0.6rem 0;
  border-bottom: 2px solid #4a90e2; margin-bottom: 1rem;
}
.bhq2-cands { color: #666; font-size: 0.9em; }
.bhq2-questions { padding-left: 1.5rem; }
.bhq2-question { margin-bottom: 1.4rem; }
.bhq2-q-text { margin: 0 0 0.4rem 0; }
.bhq2-domain { color: #999; font-size: 0.85em; font-weight: normal; margin-left: 0.5em; }
.bhq2-options { display: flex; flex-direction: column; gap: 0.3rem; padding-left: 1rem; }
.bhq2-option { cursor: pointer; padding: 0.3rem; border-radius: 4px; }
.bhq2-option:hover { background: #f0f8ff; }
.bhq2-option input { margin-right: 0.5rem; }
.bhq2-winner {
  padding: 1.2rem; background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
  border-radius: 10px; margin: 1rem 0; text-align: center;
  border: 2px solid #4a90e2;
}
.bhq2-chi { font-size: 1.8em; font-weight: bold; color: #2a5db0; }
.bhq2-range-text { font-size: 0.6em; color: #666; font-weight: normal; }
.bhq2-conf { margin-top: 0.4rem; color: #333; }
.bhq2-uncertain { color: #d4a000; font-size: 0.9em; }
.bhq2-scores { padding-left: 1.5rem; list-style: none; }
.bhq2-scores li { padding: 0.3rem; border-radius: 4px; }
.bhq2-scores li.is-top { background: #fffbe6; font-weight: 500; }
.bhq2-loading { text-align: center; padding: 3rem; }
.bhq2-small { color: #888; font-size: 0.85em; margin-top: 0.4rem; }
.bhq2-actions { margin-top: 1rem; }
</style>
