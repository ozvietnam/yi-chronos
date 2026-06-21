<script setup>
/**
 * HoiHermesPanel — Trang "Hỏi Hermes" đầy đủ (Anh chốt 2026-06-20).
 * Chọn sage muốn hỏi → Hội Đồng đa-sage luận cho người đang xem → xem TỪNG tiếng nói + tổng
 * hợp arbiter. Không chọn sage = Trọng tài tự định tuyến. Login-gated; tốn gói/free/xu.
 */
import { ref, computed, onMounted } from "vue";
import { activePerson } from "../stores/userDataStore.js";
import { sessionToken } from "../stores/authStore.js";

const sages = ref([]);
const picked = ref(new Set());      // tag sage user chọn; rỗng = auto (Trọng tài tự chọn)
const question = ref("");
const result = ref(null);
const loading = ref(false);
const err = ref("");

const personName = computed(() => activePerson.value?.name || "người đang xem");
const personKey = computed(() => activePerson.value?.person_key || "self");
const hasBirth = computed(() => !!activePerson.value?.birth_datetime_local);

function authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

async function loadSages() {
  try {
    const r = await fetch("/api/hermes/sages", { headers: authHeaders(), credentials: "include" });
    const d = await r.json();
    if (r.ok) sages.value = d.sages || [];
  } catch { /* picker là tùy chọn — lỗi không chặn */ }
}

function toggle(tag) {
  const s = new Set(picked.value);
  s.has(tag) ? s.delete(tag) : s.add(tag);
  picked.value = s;
}

async function askCouncil() {
  if (!question.value.trim()) { err.value = "Nhập câu hỏi đã."; return; }
  if (!hasBirth.value) { err.value = "Người đang xem chưa có giờ sinh — chọn người có giờ sinh để Hội Đồng đọc lá số."; return; }
  loading.value = true; err.value = ""; result.value = null;
  try {
    const agents = picked.value.size ? [...picked.value] : null;   // null = Trọng tài tự chọn
    const r = await fetch("/api/hermes/council", {
      method: "POST", headers: authHeaders(), credentials: "include",
      body: JSON.stringify({ question: question.value, person_key: personKey.value, agents }),
    });
    const d = await r.json();
    if (!r.ok) { err.value = d.detail || `Lỗi ${r.status}`; return; }
    result.value = d;
  } catch (e) { err.value = String(e.message || e); }
  finally { loading.value = false; }
}
onMounted(loadSages);
</script>

<template>
  <div class="hoi-hermes">
    <header class="hh-head">
      <h2>⚖️ Hỏi Hermes — Hội Đồng đa trường phái</h2>
      <p class="hh-sub">Hỏi về <b>{{ personName }}</b> · các sage luận theo lá số rồi đối biện, arbiter
        tổng hợp. <b>Không chọn sage</b> = Trọng tài tự chọn người hợp nhất. Đọc đồng dạng — không tiên tri.</p>
    </header>

    <!-- Chọn sage -->
    <div class="hh-pickers">
      <button v-for="s in sages" :key="s.tag" type="button"
        class="hh-chip" :class="{ on: picked.has(s.tag) }" @click="toggle(s.tag)">
        <span>{{ s.icon }}</span> {{ s.name_vi }}
      </button>
      <span v-if="!picked.size" class="hh-auto">↳ đang để Trọng tài tự chọn</span>
    </div>

    <!-- Câu hỏi -->
    <textarea v-model="question" rows="3" class="hh-q"
      placeholder="Hỏi Hội Đồng một điều lớn… (vd: con đang phân vân đổi hướng sự nghiệp, xin các thầy soi giúp)"></textarea>
    <div class="hh-actions">
      <button class="hh-ask" :disabled="loading" @click="askCouncil">
        {{ loading ? "⚖️ Đang triệu tập Hội Đồng… (~1 phút)" : "⚖️ Hỏi Hội Đồng" }}
      </button>
      <span v-if="picked.size" class="hh-note">{{ picked.size }} sage được chọn</span>
    </div>
    <p v-if="err" class="hh-err">⚠ {{ err }}</p>

    <!-- Kết quả -->
    <div v-if="result" class="hh-result">
      <p v-if="result.status === 'denied'" class="hh-err">
        Hết lượt Hội Đồng miễn phí hôm nay{{ result.xu_cost ? ` — cần ${result.xu_cost} xu (còn ${result.have ?? 0})` : "" }}.
      </p>
      <p v-else-if="result.status && result.status !== 'done'" class="hh-err">
        {{ result.reply || result.reason || result.status }}
      </p>
      <template v-else>
        <!-- Tổng hợp arbiter -->
        <section class="hh-synth">
          <h3>🜂 Tổng hợp Hội Đồng
            <span v-if="result.paradigm_ok === false" class="hh-flag">⚠ có giọng tiên tri — đọc thận trọng</span>
            <span v-if="result.cached" class="hh-cached">đã hỏi hôm nay</span>
          </h3>
          <div class="hh-synth-body">{{ result.synthesis }}</div>
        </section>
        <!-- Tiếng nói từng sage -->
        <section v-if="result.voices && result.voices.length" class="hh-voices">
          <h4>Tiếng nói từng thầy ({{ result.voices.length }})</h4>
          <details v-for="v in result.voices" :key="v.agent_id" class="hh-voice">
            <summary>{{ v.name || v.agent_id }}</summary>
            <div class="hh-voice-body">{{ v.content }}</div>
          </details>
        </section>
      </template>
    </div>
  </div>
</template>

<style scoped>
.hoi-hermes { max-width: 920px; margin: 0 auto; color: var(--read-fg, inherit); }
.hh-head h2 { margin-bottom: .2rem; }
.hh-sub { color: var(--read-muted, #888); font-size: .9rem; line-height: 1.6; }
.hh-pickers { display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; margin: .9rem 0; }
.hh-chip { padding: .35rem .7rem; border: 1px solid var(--read-border, #ccc); background: transparent;
  border-radius: 20px; cursor: pointer; color: inherit; font-size: .88rem; }
.hh-chip.on { background: var(--read-accent, #7c3aed); color: #fff; border-color: transparent; }
.hh-auto { font-size: .82rem; color: var(--read-muted, #888); font-style: italic; }
.hh-q { width: 100%; font-family: inherit; font-size: 1rem; padding: .6rem; border-radius: 8px;
  border: 1px solid var(--read-border, #ccc); background: var(--read-bg, #fff); color: inherit; }
.hh-actions { display: flex; gap: .8rem; align-items: center; margin: .6rem 0; }
.hh-ask { padding: .6rem 1.2rem; border: none; border-radius: 8px; font-weight: 700; font-size: 1rem;
  cursor: pointer; background: linear-gradient(135deg, #6d28d9, #a78bfa); color: #fff;
  box-shadow: 0 2px 10px rgba(109,40,217,.3); }
.hh-ask:disabled { opacity: .65; cursor: wait; }
.hh-note { font-size: .82rem; color: var(--read-muted, #888); }
.hh-err { color: #c2410c; background: rgba(217,119,6,.08); padding: .5rem .7rem; border-radius: 6px; }
.hh-result { margin-top: 1rem; }
.hh-synth { border: 1px solid var(--read-border, #ddd); border-left: 3px solid #7c3aed;
  border-radius: 0 8px 8px 0; padding: .8rem 1rem; background: rgba(124,58,237,.05); }
.hh-synth h3 { margin: 0 0 .5rem; font-size: 1.05rem; display: flex; gap: .6rem; align-items: center; flex-wrap: wrap; }
.hh-synth-body { white-space: pre-wrap; line-height: 1.7; font-size: 1rem; }
.hh-flag { font-size: .75rem; color: #c2410c; font-weight: 500; }
.hh-cached { font-size: .72rem; color: var(--read-muted, #888); font-weight: 400; }
.hh-voices { margin-top: 1rem; }
.hh-voices h4 { margin: 0 0 .5rem; font-size: .92rem; color: var(--read-muted, #888); }
.hh-voice { border: 1px solid var(--read-border, #e3e3e3); border-radius: 8px; margin-bottom: .5rem; padding: .2rem .6rem; }
.hh-voice summary { cursor: pointer; padding: .45rem 0; font-weight: 600; font-size: .95rem; }
.hh-voice-body { white-space: pre-wrap; line-height: 1.65; font-size: .94rem; padding: .2rem 0 .6rem; }
</style>
