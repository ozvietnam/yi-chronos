<script setup>
/**
 * QuickTasksPanel — 3 tác vụ nhanh đầu trang.
 *
 * 1. Xem ngày giờ tốt xấu (chọn ngày)
 * 2. Trắc nghiệm xác định giờ sinh
 * 3. Xem 2 người có hợp nhau trong hôn nhân
 */
import { ref, computed, onMounted, watch } from "vue";
import LifeOverviewModal from "./LifeOverviewModal.vue";
import BirthHourQuizV2 from "./BirthHourQuizV2.vue";
import { activePerson } from "../stores/userDataStore.js";
import { CalendarCheck, Clock, HeartHandshake, ScrollText, Flower } from "lucide-vue-next";

const emit = defineEmits(["open-tab"]);

const activeTask = ref(null);  // null | 'quiz' | 'marriage'
// 'auspicious' không cần modal, anh đi qua tab Wiki
// Quiz v2 self-manages state inside BirthHourQuizV2 component.

// ─── Marriage Compat ──────────────────────────────────
const mForm = ref({
  birth_a_date: "",
  birth_a_hour: 8,
  name_a: "Anh",
  gender_a: "nam",
  birth_b_date: "1990-06-15",
  birth_b_hour: 14,
  name_b: "Đối phương",
  gender_b: "nữ",
});

// Người A (bản thân) tự điền từ profile; người B giữ để nhập đối phương.
let _lastSyncedA = null;
function _syncBirthA(force) {
  const p = activePerson.value;
  const dt = p?.birth_datetime_local;
  if (!dt) return;
  const d = dt.split("T")[0];
  if (force || !mForm.value.birth_a_date || mForm.value.birth_a_date === _lastSyncedA) {
    mForm.value.birth_a_date = d;
    const hh = parseInt((dt.split("T")[1] || "").slice(0, 2), 10);
    if (!Number.isNaN(hh)) mForm.value.birth_a_hour = hh;
    if (p.name) mForm.value.name_a = p.name;
    if (p.gender) mForm.value.gender_a = p.gender;
    _lastSyncedA = d;
  }
}
onMounted(() => _syncBirthA(false));
watch(() => activePerson.value?.person_key, () => _syncBirthA(true));
const mResult = ref(null);
const mLoading = ref(false);
const mError = ref("");

async function submitMarriage() {
  mLoading.value = true;
  mError.value = "";
  mResult.value = null;
  try {
    const a_iso = `${mForm.value.birth_a_date}T${String(mForm.value.birth_a_hour).padStart(2,'0')}:00:00`;
    const b_iso = `${mForm.value.birth_b_date}T${String(mForm.value.birth_b_hour).padStart(2,'0')}:00:00`;
    // Deep engine (bat_tu/compatibility): nạp âm + 5-hợp Can + cung phối + dụng thần
    // complementarity + spouse-check theo giới tính. Paradigm Iron Rule #4+6 (đọc khí,
    // không phán cứng) — thay engine "con giáp" nông + verdict cứng (#27).
    const r = await fetch("/api/bat-tu/compatibility", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        person_a_birth: a_iso,
        person_b_birth: b_iso,
        person_a_gender: mForm.value.gender_a,
        person_b_gender: mForm.value.gender_b,
        relationship_type: "spouse",
      }),
    });
    const d = await r.json();
    if (!r.ok || !d.compatibility) {
      mError.value = d.detail || d.message || "Lỗi";
      return;
    }
    mResult.value = d.compatibility;
  } catch (e) {
    mError.value = String(e.message || e);
  } finally {
    mLoading.value = false;
  }
}

function openTask(task) {
  if (task === "auspicious") {
    // Tab Wiki → sub-tab auspicious
    emit("open-tab", "wiki");
    return;
  }
  activeTask.value = task;
  // quiz v2 self-loads on mount inside BirthHourQuizV2
}

function closeTask() {
  activeTask.value = null;
}
</script>

<template>
  <div class="quick-tasks">
    <div class="qt-header">
      <h3 class="qt-h3"><Flower :size="18" :stroke-width="2" color="#e8c95a" /> Tác vụ nhanh — Thầy gửi đệ tử</h3>
      <p class="qt-hint">Ba việc thường dùng nhất — click 1 cái để bắt đầu</p>
    </div>

    <div class="qt-grid">
      <!-- Card 1: Xem ngày giờ -->
      <div class="qt-card auspicious" @click="openTask('auspicious')">
        <div class="qt-icon"><CalendarCheck :size="30" :stroke-width="2" color="#fbbf24" /></div>
        <div class="qt-body">
          <h4>Xem ngày giờ tốt xấu</h4>
          <p>Chọn ngày đẹp theo Bát Tự + Mai Hoa cho việc lớn: chuyển nhà, khai trương, hôn nhân, khởi công...</p>
          <span class="qt-cta">Bắt đầu →</span>
        </div>
      </div>

      <!-- Card 2: Trắc nghiệm giờ sinh -->
      <div class="qt-card quiz" @click="openTask('quiz')">
        <div class="qt-icon"><Clock :size="30" :stroke-width="2" color="#a78bfa" /></div>
        <div class="qt-body">
          <h4>Trắc nghiệm xác định giờ sinh</h4>
          <p>Không nhớ giờ sinh? Trả lời 8 câu trắc nghiệm về tính cách + thói quen → đoán giờ sinh likely</p>
          <span class="qt-cta">Bắt đầu →</span>
        </div>
      </div>

      <!-- Card 3: Hợp tuổi hôn nhân -->
      <div class="qt-card marriage" @click="openTask('marriage')">
        <div class="qt-icon"><HeartHandshake :size="30" :stroke-width="2" color="#f472b6" /></div>
        <div class="qt-body">
          <h4>Hợp tuổi hôn nhân</h4>
          <p>Phân tích 2 người có hợp trong hôn nhân không? Xét Nạp âm + Lục Xung/Lục Hợp + Nhật chủ</p>
          <span class="qt-cta">Bắt đầu →</span>
        </div>
      </div>

      <!-- Card 4: Tổng quan cuộc đời -->
      <div class="qt-card lifeoverview" @click="openTask('life')">
        <div class="qt-icon"><ScrollText :size="30" :stroke-width="2" color="#34d399" /></div>
        <div class="qt-body">
          <h4>Tổng quan cuộc đời (~30 trang)</h4>
          <p>Báo cáo đầy đủ: Tứ Trụ + Dụng thần + Đại Vận + Hà Lạc + Sự nghiệp + Hôn nhân + Sức khoẻ + Phương hướng. <b>Có thể in / xuất PDF A4.</b></p>
          <span class="qt-cta">Lập báo cáo →</span>
        </div>
      </div>
    </div>

    <!-- Modal: Life Overview -->
    <LifeOverviewModal v-if="activeTask === 'life'" @close="closeTask" />

    <!-- ─── Modal: Quiz v2 (bát tự hypothesis comparison) ──── -->
    <div v-if="activeTask === 'quiz'" class="qt-modal" @click.self="closeTask">
      <div class="qt-modal-content qt-modal-wide">
        <button class="qt-close" @click="closeTask">✕</button>
        <BirthHourQuizV2 />
      </div>
    </div>

    <!-- ─── Modal: Marriage Compat ────────────────────── -->
    <div v-if="activeTask === 'marriage'" class="qt-modal" @click.self="closeTask">
      <div class="qt-modal-content">
        <button class="qt-close" @click="closeTask">✕</button>
        <h2>💕 Hợp tuổi hôn nhân</h2>
        <p class="qt-modal-hint">
          Luận sâu Bát Tự: Nạp âm · Hợp Can · Cung phối · Dụng thần bù trợ · Soi Tài/Quan theo
          giới tính (Thiệu Vĩ Hoa). Đọc cấu hình khí — KHÔNG phán cứng nên/không nên cưới.
        </p>

        <div class="m-form">
          <div class="m-person">
            <h4>Người A</h4>
            <input v-model="mForm.name_a" placeholder="Tên / vai trò" />
            <div class="m-row">
              <input v-model="mForm.birth_a_date" type="date" />
              <select v-model.number="mForm.birth_a_hour">
                <option v-for="h in 24" :key="h-1" :value="h-1">{{ String(h-1).padStart(2,'0') }}h</option>
              </select>
            </div>
            <select v-model="mForm.gender_a" class="m-gender">
              <option value="nam">Nam</option>
              <option value="nữ">Nữ</option>
            </select>
          </div>
          <div class="m-person">
            <h4>Người B</h4>
            <input v-model="mForm.name_b" placeholder="Tên / vai trò" />
            <div class="m-row">
              <input v-model="mForm.birth_b_date" type="date" />
              <select v-model.number="mForm.birth_b_hour">
                <option v-for="h in 24" :key="h-1" :value="h-1">{{ String(h-1).padStart(2,'0') }}h</option>
              </select>
            </div>
            <select v-model="mForm.gender_b" class="m-gender">
              <option value="nam">Nam</option>
              <option value="nữ">Nữ</option>
            </select>
          </div>
        </div>
        <button class="btn-primary" @click="submitMarriage" :disabled="mLoading">
          {{ mLoading ? "Đang luận..." : "💕 Luận hợp tuổi" }}
        </button>
        <p v-if="mError" class="err">❌ {{ mError }}</p>

        <!-- Result (deep engine — đọc cấu hình khí, không verdict cứng) -->
        <div v-if="mResult" class="m-result">
          <div class="m-overall">
            <span class="m-overall-label">{{ mResult.overall?.label }}</span>
            <p class="m-summary">{{ mResult.overall?.narrative }}</p>
          </div>

          <div class="m-layers">
            <div v-if="mResult.nap_am" class="m-layer">
              <h5>📿 Nạp âm</h5>
              <p>{{ mResult.nap_am.a?.name }} ⚭ {{ mResult.nap_am.b?.name }}
                — {{ mResult.nap_am.relation?.narrative || mResult.nap_am.relation?.type }}</p>
            </div>
            <div v-if="mResult.day_master_compat" class="m-layer">
              <h5>🌟 Nhật chủ (Day Master)</h5>
              <p>{{ mResult.day_master_compat.narrative || mResult.day_master_compat.type }}</p>
            </div>
            <div v-if="mResult.cung_phoi" class="m-layer">
              <h5>🏠 Cung phối (chi ngày)</h5>
              <p>{{ mResult.cung_phoi.a_chi }} ⚭ {{ mResult.cung_phoi.b_chi }}<span
                v-for="i in (mResult.cung_phoi.interactions || [])" :key="i.type"> · {{ i.type }}</span></p>
            </div>
            <div v-if="mResult.ngu_hanh_dynamics" class="m-layer">
              <h5>🌊 Ngũ hành bù trợ</h5>
              <p>{{ mResult.ngu_hanh_dynamics.narrative }}</p>
            </div>
            <div v-if="mResult.spouse_check" class="m-layer m-spouse">
              <h5>💑 Soi Phu/Thê (Tài·Quan theo giới tính)</h5>
              <p>{{ mResult.spouse_check.narrative }}</p>
            </div>
          </div>

          <p v-if="mResult.closing" class="m-closing">{{ mResult.closing }}</p>
          <p v-if="mResult.paradigm_guard" class="m-paradigm">🪷 {{ mResult.paradigm_guard }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.quick-tasks { margin: 1rem 0 1.5rem; }

.qt-header { margin-bottom: 0.7rem; }
.qt-header h3 { margin: 0 0 0.25rem; color: #fbbf24; font-size: 1rem; }
.qt-h3 { display: flex; align-items: center; gap: 6px; }
.qt-hint { margin: 0; font-size: 0.82rem; color: #94a3b8; }

.qt-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.7rem;
}
@media (max-width: 640px) {
  .qt-grid { grid-template-columns: 1fr; }
}
.qt-card {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 0.85rem 1rem;
  background: rgba(15,23,42,0.55);
  border: 1px solid rgba(167,139,250,0.18);
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.qt-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(167,139,250,0.18);
  border-color: rgba(251,191,36,0.4);
}
.qt-card.auspicious { border-left: 3px solid #fbbf24; }
.qt-card.quiz { border-left: 3px solid #a78bfa; }
.qt-card.marriage { border-left: 3px solid #f472b6; }
.qt-card.lifeoverview { border-left: 3px solid #34d399; }
.qt-icon { line-height: 1; flex-shrink: 0; display: flex; align-items: center; }
.qt-body { flex: 1; }
.qt-body h4 { margin: 0 0 0.3rem; color: #fef3c7; font-size: 0.95rem; }
.qt-body p { margin: 0 0 0.4rem; color: #cbd5e1; font-size: 0.8rem; line-height: 1.55; }
.qt-cta { color: #c4b5fd; font-size: 0.8rem; }

/* Modal */
.qt-modal {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 1500;
  display: flex; align-items: center; justify-content: center;
  padding: 2rem;
  overflow-y: auto;
}
.qt-modal-content {
  background: #0f172a;
  border: 1px solid rgba(167,139,250,0.4);
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
  max-width: 720px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  color: #e2e8f0;
}
.qt-close {
  position: absolute; top: 0.6rem; right: 0.8rem;
  background: rgba(167,139,250,0.2);
  color: #c4b5fd;
  border: none; padding: 0.25rem 0.6rem;
  border-radius: 4px; cursor: pointer; font-size: 0.85rem;
}
.qt-modal-content h2 { margin: 0 0 0.4rem; color: #fbbf24; }
.qt-modal-hint { font-size: 0.8rem; color: #94a3b8; margin: 0 0 0.85rem; line-height: 1.55; }

/* Quiz */
.quiz-q {
  margin-bottom: 0.85rem;
  padding: 0.6rem 0.85rem;
  background: rgba(15,23,42,0.5);
  border-radius: 4px;
  border-left: 2px solid #a78bfa;
}
.q-label { margin: 0 0 0.4rem; color: #fef3c7; font-size: 0.88rem; }
.q-label b { color: #c4b5fd; }
.q-options { display: flex; flex-direction: column; gap: 0.3rem; }
.q-options label {
  display: flex; align-items: flex-start; gap: 0.4rem;
  padding: 0.3rem 0.4rem;
  font-size: 0.83rem;
  color: #cbd5e1;
  cursor: pointer;
  border-radius: 3px;
}
.q-options label:hover { background: rgba(167,139,250,0.08); }
.quiz-actions { margin-top: 0.85rem; display: flex; gap: 0.5rem; }

/* Quiz result */
.qr-headline {
  text-align: center;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(251,191,36,0.1), rgba(167,139,250,0.06));
  border-radius: 6px;
  margin-bottom: 0.85rem;
}
.qr-most { font-size: 1.4rem; color: #fbbf24; font-weight: 700; }
.qr-range { font-size: 0.95rem; color: #c4b5fd; margin: 0.2rem 0; }
.qr-conf { font-size: 0.85rem; color: #cbd5e1; }
.qr-trait { font-size: 0.88rem; padding: 0.3rem 0; color: #cbd5e1; line-height: 1.6; }
.qr-trait b { color: #fbbf24; }
.qr-top3 { display: grid; gap: 0.4rem; }
.qr-top-item {
  padding: 0.5rem 0.7rem;
  background: rgba(15,23,42,0.5);
  border-radius: 4px;
  font-size: 0.82rem;
}
.qr-top-item .qr-chi { color: #fef3c7; }
.qr-top-item .qr-score { color: #c4b5fd; font-size: 0.78rem; }
.qr-top-item .qr-trait-small { color: #94a3b8; font-size: 0.75rem; font-style: italic; }

/* Marriage form */
.m-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
  margin-bottom: 0.7rem;
}
.m-person {
  background: rgba(15,23,42,0.5);
  padding: 0.7rem 0.85rem;
  border-radius: 5px;
}
.m-person h4 { margin: 0 0 0.3rem; color: #c4b5fd; font-size: 0.88rem; }
.m-person input, .m-person select {
  width: 100%;
  padding: 0.35rem 0.5rem;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  color: #e2e8f0;
  border-radius: 3px;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
  box-sizing: border-box;
}
.m-row { display: flex; gap: 0.3rem; }
.m-row input, .m-row select { flex: 1; margin-bottom: 0; }

.btn-primary, .btn-secondary {
  padding: 0.5rem 1rem;
  border: none; border-radius: 4px; cursor: pointer; font-weight: 600;
  font-size: 0.88rem;
}
.btn-primary { background: #a78bfa; color: #1e1b4b; }
.btn-primary:hover { background: #c4b5fd; }
.btn-secondary { background: rgba(167,139,250,0.2); color: #c4b5fd; }

.err { color: #f87171; margin: 0.3rem 0 0; }

/* Marriage result */
.m-result { margin-top: 0.85rem; }
/* Paradigm-neutral overall (no good/bad coloring — đọc khí, không phán cứng) */
.m-overall {
  padding: 0.6rem 0.85rem;
  background: rgba(167,139,250,0.10);
  border-left: 3px solid rgba(167,139,250,0.5);
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
.m-overall-label { font-weight: 700; color: #cbb6f5; font-size: 0.9rem; }
.m-gender { margin-top: 0.4rem; width: 100%; }
.m-spouse { border-left-color: #f9a8d4 !important; }
.m-closing { font-size: 0.83rem; color: #cbd5e1; line-height: 1.6; margin: 0.6rem 0 0.3rem; font-style: italic; }
.m-paradigm { font-size: 0.75rem; color: #94a3b8; line-height: 1.5; margin: 0.3rem 0 0; }
.m-summary { font-size: 0.85rem; color: #cbd5e1; padding: 0.3rem 0 0.5rem; line-height: 1.6; }

.m-pillars {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0.6rem;
  align-items: center;
  margin: 0.6rem 0;
}
.m-p-cell {
  background: rgba(15,23,42,0.55);
  padding: 0.6rem 0.85rem;
  border-radius: 5px;
  font-size: 0.8rem;
  color: #cbd5e1;
  line-height: 1.6;
}
.m-p-cell b { color: #fbbf24; display: block; margin-bottom: 0.3rem; }
.m-vs { font-size: 1.6rem; color: #f472b6; text-align: center; }

.m-layers { display: flex; flex-direction: column; gap: 0.4rem; margin: 0.6rem 0; }
.m-layer { background: rgba(15,23,42,0.45); padding: 0.5rem 0.75rem; border-radius: 4px; }
.m-layer h5 { margin: 0 0 0.2rem; color: #c4b5fd; font-size: 0.85rem; }
.m-layer p { margin: 0; font-size: 0.83rem; color: #cbd5e1; line-height: 1.55; }

.m-bless, .m-warn { padding: 0.5rem 0.75rem; border-radius: 4px; margin: 0.4rem 0; }
.m-bless { background: rgba(52,211,153,0.08); border-left: 2px solid #34d399; }
.m-warn { background: rgba(248,113,113,0.08); border-left: 2px solid #f87171; }
.m-bless h5 { color: #6ee7b7; margin: 0 0 0.3rem; font-size: 0.85rem; }
.m-warn h5 { color: #fca5a5; margin: 0 0 0.3rem; font-size: 0.85rem; }
.m-bless ul, .m-warn ul { margin: 0; padding-left: 1.2rem; font-size: 0.82rem; line-height: 1.6; }
</style>
