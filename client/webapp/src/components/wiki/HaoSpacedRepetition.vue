<script setup>
/**
 * HaoSpacedRepetition — Anki-style spaced repetition cho 343 hào card.
 *
 * Algorithm SM-2 đơn giản (Pyotr Wozniak 1985):
 *   - 4 ratings: Again (forget), Hard, Good, Easy
 *   - Track per card: ef (ease factor 1.3-2.5), interval (days), reps, due_date
 *   - State persist localStorage (no backend)
 *
 * UI:
 *   - Front: tên hào (Quẻ N TênQuẻ · Sơ Cửu)
 *   - Click "Show" → Back (Lời hào + tâm pháp)
 *   - 4 rating buttons → calculate next due
 *   - Daily limit: 20 new + reviewed today
 */
import { ref, computed, onMounted } from "vue";

const LS_KEY = "yi_hao_sr_v1";
const DAILY_LIMIT_NEW = 20;

const cards = ref([]);
const state = ref({});  // {card_id: {ef, interval, reps, due_iso}}
const loading = ref(false);
const error = ref("");

const currentIdx = ref(0);
const showBack = ref(false);
const sessionDone = ref(false);

// Stats
const stats = computed(() => {
  const today = new Date().toISOString().slice(0, 10);
  let learned = 0, due = 0, total = cards.value.length;
  for (const c of cards.value) {
    const s = state.value[c.card_id];
    if (s) {
      learned++;
      if (s.due_iso <= today) due++;
    }
  }
  return { learned, due, total, new_left: total - learned };
});

// Queue: due cards first, then new ones (cap DAILY_LIMIT_NEW)
const todayQueue = computed(() => {
  const today = new Date().toISOString().slice(0, 10);
  const dueCards = [];
  const newCards = [];
  for (const c of cards.value) {
    const s = state.value[c.card_id];
    if (s) {
      if (s.due_iso <= today) dueCards.push(c);
    } else {
      newCards.push(c);
    }
  }
  return [...dueCards, ...newCards.slice(0, DAILY_LIMIT_NEW)];
});

const currentCard = computed(() => todayQueue.value[currentIdx.value] || null);

function loadState() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) state.value = JSON.parse(raw);
  } catch (e) { /* ignore */ }
}

function saveState() {
  localStorage.setItem(LS_KEY, JSON.stringify(state.value));
}

async function loadCards() {
  loading.value = true;
  try {
    const r = await fetch("/api/yi-wiki/kinh-dich/cards");
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    cards.value = d.cards;
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

// SM-2 simplified
function rate(quality) {
  // 0 = again, 3 = hard, 4 = good, 5 = easy
  const card = currentCard.value;
  if (!card) return;
  const s = state.value[card.card_id] || { ef: 2.5, interval: 0, reps: 0 };

  if (quality < 3) {
    // Again — reset
    s.reps = 0;
    s.interval = 1;
  } else {
    s.reps += 1;
    if (s.reps === 1) s.interval = 1;
    else if (s.reps === 2) s.interval = 6;
    else s.interval = Math.round(s.interval * s.ef);
    s.ef = Math.max(1.3, s.ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)));
  }

  const due = new Date();
  due.setDate(due.getDate() + s.interval);
  s.due_iso = due.toISOString().slice(0, 10);
  state.value[card.card_id] = s;
  saveState();

  // Next card
  showBack.value = false;
  currentIdx.value++;
  if (currentIdx.value >= todayQueue.value.length) {
    sessionDone.value = true;
  }
}

function restart() {
  currentIdx.value = 0;
  showBack.value = false;
  sessionDone.value = false;
}

function resetAll() {
  if (!confirm("Xoá toàn bộ progress? (Card đã học sẽ thành 'mới')")) return;
  state.value = {};
  saveState();
  restart();
}

// Markdown rendering for back content
function renderBack(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/_([^_]+)_/g, "<i>$1</i>")
    .replace(/\n/g, "<br>");
}

onMounted(() => {
  loadState();
  loadCards();
});
</script>

<template>
  <div class="hsr">
    <header class="hsr-head">
      <h3>🎴 Học 343 Hào — Spaced Repetition</h3>
      <div class="hsr-stats">
        <span><b>{{ stats.learned }}</b>/{{ stats.total }} đã học</span>
        <span class="due"><b>{{ stats.due }}</b> đến hạn ôn</span>
        <span>{{ stats.new_left }} chưa học</span>
        <button class="btn-reset" @click="resetAll" title="Xoá toàn bộ progress">↻ Reset</button>
      </div>
    </header>

    <div v-if="loading" class="hsr-status">Đang tải cards...</div>
    <div v-if="error" class="hsr-error">{{ error }}</div>

    <div v-if="!loading && !error">
      <div v-if="sessionDone || !currentCard" class="hsr-done">
        <p>✨ Hoàn thành phiên hôm nay! Quay lại sau hoặc reset để học thêm.</p>
        <button @click="restart">↻ Học lại</button>
      </div>

      <div v-else class="hsr-card-wrap">
        <div class="hsr-progress">
          {{ currentIdx + 1 }} / {{ todayQueue.length }} hôm nay
        </div>

        <div class="hsr-card">
          <div class="hsr-front">
            <div class="card-prompt">{{ currentCard.front }}</div>
            <div class="card-meta">
              {{ currentCard.hexagram_structure }} · Hào {{ currentCard.hao_num }} ({{ currentCard.lookup_key }})
            </div>
          </div>

          <div v-if="!showBack" class="hsr-show-back">
            <button class="btn-show" @click="showBack = true">Hiển thị lời hào + tâm pháp</button>
          </div>

          <div v-else class="hsr-back" v-html="renderBack(currentCard.back)"></div>
        </div>

        <div v-if="showBack" class="hsr-actions">
          <button class="btn-rate btn-again" @click="rate(0)">
            <b>Quên</b><br><small>1 ngày</small>
          </button>
          <button class="btn-rate btn-hard" @click="rate(3)">
            <b>Khó</b><br><small>~6 ngày</small>
          </button>
          <button class="btn-rate btn-good" @click="rate(4)">
            <b>Ổn</b><br><small>~15 ngày</small>
          </button>
          <button class="btn-rate btn-easy" @click="rate(5)">
            <b>Dễ</b><br><small>~25 ngày</small>
          </button>
        </div>
      </div>
    </div>

    <p class="hsr-foot">
      ⓘ Spaced repetition (SM-2). Progress lưu trong browser localStorage. Mỗi ngày tối đa {{ DAILY_LIMIT_NEW }} card mới.
    </p>
  </div>
</template>

<style scoped>
.hsr {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 8px;
  margin: 0.5rem 0;
}
.hsr-head {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 0.8rem; margin-bottom: 0.6rem;
}
.hsr-head h3 { margin: 0; color: #34d399; font-size: 1rem; }
.hsr-stats {
  display: flex; gap: 0.8rem; font-size: 0.85rem; align-items: center; flex-wrap: wrap;
}
.hsr-stats span { color: #cbd5e1; }
.hsr-stats .due { color: #fbbf24; }
.btn-reset {
  background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171; padding: 0.2rem 0.5rem; border-radius: 4px; cursor: pointer;
  font-size: 0.75rem;
}
.hsr-status, .hsr-error {
  padding: 1rem; text-align: center; color: #94a3b8;
}
.hsr-done {
  text-align: center; padding: 2rem; color: #94a3b8;
}
.hsr-done button {
  background: rgba(167, 139, 250, 0.2); border: 1px solid rgba(167, 139, 250, 0.5);
  color: #c4b5fd; padding: 0.45rem 1rem; border-radius: 6px; cursor: pointer;
  margin-top: 0.5rem;
}
.hsr-progress {
  color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.4rem;
}
.hsr-card {
  background: rgba(15, 23, 42, 0.6); border-radius: 8px;
  border: 1px solid rgba(167, 139, 250, 0.2);
  padding: 1.2rem;
  min-height: 250px;
}
.hsr-front .card-prompt {
  font-size: 1.4rem; font-weight: 600; color: #fbbf24; text-align: center;
  margin-bottom: 0.5rem;
}
.hsr-front .card-meta {
  font-size: 0.85rem; color: #94a3b8; text-align: center;
  margin-bottom: 1rem;
}
.hsr-show-back { text-align: center; margin: 1rem 0; }
.btn-show {
  background: rgba(196, 181, 253, 0.15); border: 1px solid rgba(196, 181, 253, 0.4);
  color: #c4b5fd; padding: 0.6rem 1.5rem; border-radius: 6px; cursor: pointer;
  font-size: 0.95rem;
}
.hsr-back {
  background: rgba(252, 211, 77, 0.05); border-left: 2px solid #fcd34d;
  padding: 0.8rem 1rem; border-radius: 4px;
  font-size: 0.92rem; line-height: 1.6; color: #e2e8f0;
}
.hsr-back :deep(b) { color: #fcd34d; }
.hsr-back :deep(i) { color: #fde68a; }
.hsr-actions {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.4rem;
  margin-top: 1rem;
}
.btn-rate {
  padding: 0.55rem 0.4rem; border-radius: 6px; cursor: pointer; border: none;
  text-align: center; font-size: 0.85rem; transition: filter .15s;
}
.btn-rate:hover { filter: brightness(1.15); }
.btn-rate small { opacity: 0.7; font-size: 0.7rem; }
.btn-again { background: #ef4444; color: white; }
.btn-hard { background: #f59e0b; color: white; }
.btn-good { background: #10b981; color: white; }
.btn-easy { background: #3b82f6; color: white; }
.hsr-foot {
  margin-top: 0.6rem; font-size: 0.75rem; color: #6b7280;
}
</style>
