<script setup>
import { ref } from "vue";
import { castThanSo } from "../lib/api.js";

const form = ref({
  name: "",
  birthDate: "",
  system: "pythagorean",
  targetYear: new Date().getFullYear(),
});

const loading = ref(false);
const error = ref("");
const result = ref(null);

async function submit() {
  error.value = "";
  result.value = null;
  if (!form.value.name.trim() || !form.value.birthDate) {
    error.value = "Vui lòng nhập đầy đủ Họ tên và Ngày sinh.";
    return;
  }
  loading.value = true;
  try {
    result.value = await castThanSo({
      name: form.value.name,
      birthDate: form.value.birthDate,
      system: form.value.system,
      targetYear: Number(form.value.targetYear) || null,
    });
  } catch (err) {
    error.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

const CORE_ORDER = [
  ["life_path", "Số Đường Đời"],
  ["expression", "Số Sứ Mệnh"],
  ["soul_urge", "Số Linh Hồn"],
  ["personality", "Số Nhân Cách"],
  ["birthday", "Số Ngày Sinh"],
  ["maturity", "Số Trưởng Thành"],
];
</script>

<template>
  <div class="than-so-panel">
    <header class="ts-head">
      <h2>🔢 Thần Số Học</h2>
      <p class="ts-sub">Đọc cấu trúc qua <strong>Tên + Ngày sinh</strong> — Pythagoras &amp; đối chiếu Chaldean.</p>
    </header>

    <form class="ts-form" @submit.prevent="submit">
      <label>
        Họ tên đầy đủ (theo khai sinh)
        <input v-model="form.name" type="text" placeholder="Nguyễn Văn An" autocomplete="off" />
      </label>
      <div class="ts-row">
        <label>
          Ngày sinh
          <input v-model="form.birthDate" type="date" />
        </label>
        <label>
          Hệ phái
          <select v-model="form.system">
            <option value="pythagorean">Pythagoras</option>
            <option value="chaldean">Chaldean</option>
          </select>
        </label>
        <label>
          Năm xem
          <input v-model="form.targetYear" type="number" min="1900" max="2200" />
        </label>
      </div>
      <button type="submit" :disabled="loading">{{ loading ? "Đang luận…" : "Lập lá số" }}</button>
    </form>

    <p v-if="error" class="ts-error">{{ error }}</p>

    <section v-if="result" class="ts-result">
      <p class="ts-paradigm">{{ result.reading.paradigm_note }}</p>

      <h3>Số cốt lõi ({{ result.input.system }})</h3>
      <div class="ts-grid">
        <article v-for="[key, label] in CORE_ORDER" :key="key" class="ts-card">
          <div class="ts-num">{{ result.core[key].value }}</div>
          <div class="ts-label">{{ label }}</div>
          <div class="ts-arch">{{ result.reading.core[key]?.archetype_vi }}</div>
          <p v-if="result.reading.core[key]?.dong_dang" class="ts-dd">{{ result.reading.core[key].dong_dang }}</p>
        </article>
      </div>

      <div v-if="result.cross_reference" class="ts-xref">
        <strong>Đối chiếu Chaldean:</strong>
        Sứ Mệnh {{ result.cross_reference.expression }} ·
        Linh Hồn {{ result.cross_reference.soul_urge }} ·
        Nhân Cách {{ result.cross_reference.personality }}
        <em>({{ result.cross_reference.note }})</em>
      </div>

      <div v-if="result.reading.karmic_debts.length" class="ts-karmic">
        <h3>Số nợ nghiệp (bài học cần rèn)</h3>
        <ul>
          <li v-for="kd in result.reading.karmic_debts" :key="kd.number">
            <strong>{{ kd.number }}</strong> — {{ kd.theme_vi }}: {{ kd.this_life }}
          </li>
        </ul>
      </div>

      <h3>Chu kỳ (lớp Biến)</h3>
      <div class="ts-cycles">
        <div v-if="result.cycles.personal_year">
          <strong>Năm cá nhân {{ result.cycles.personal_year.target_year }}:</strong>
          {{ result.cycles.personal_year.value }}
        </div>
        <table>
          <thead><tr><th>Đỉnh vận</th><th>Số</th><th>Tuổi</th></tr></thead>
          <tbody>
            <tr v-for="p in result.cycles.pinnacles" :key="p.index">
              <td>Đỉnh {{ p.index }}</td><td>{{ p.value }}</td><td>{{ p.age_range }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <details class="ts-breakdown">
        <summary>Chi tiết quy đổi tên ({{ result.input.name_normalized }})</summary>
        <span v-for="(b, i) in result.core.breakdown" :key="i" class="ts-letter" :class="{ vowel: b.is_vowel }">
          {{ b.letter }}<sub>{{ b.value }}</sub>
        </span>
      </details>
    </section>
  </div>
</template>

<style scoped>
.than-so-panel { max-width: 880px; margin: 0 auto; padding: 1rem; }
.ts-head h2 { margin: 0; }
.ts-sub { color: #666; margin: 0.25rem 0 1rem; }
.ts-form label { display: flex; flex-direction: column; font-size: 0.85rem; gap: 0.25rem; margin-bottom: 0.6rem; }
.ts-form input, .ts-form select { padding: 0.45rem; border: 1px solid #ccc; border-radius: 6px; }
.ts-row { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.ts-row label { flex: 1; min-width: 120px; }
.ts-form button { padding: 0.55rem 1.2rem; border: 0; border-radius: 6px; background: #6b4ea8; color: #fff; cursor: pointer; }
.ts-form button:disabled { opacity: 0.6; cursor: default; }
.ts-error { color: #c0392b; }
.ts-paradigm { background: #f3eefb; border-left: 3px solid #6b4ea8; padding: 0.6rem 0.8rem; border-radius: 4px; font-style: italic; }
.ts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.75rem; }
.ts-card { border: 1px solid #e3dcf2; border-radius: 8px; padding: 0.7rem; text-align: center; }
.ts-num { font-size: 1.9rem; font-weight: 700; color: #6b4ea8; }
.ts-label { font-size: 0.8rem; color: #555; }
.ts-arch { font-weight: 600; margin: 0.2rem 0; }
.ts-dd { font-size: 0.75rem; color: #777; }
.ts-xref { margin: 0.8rem 0; padding: 0.5rem; background: #fafafa; border-radius: 6px; font-size: 0.9rem; }
.ts-xref em { color: #888; font-size: 0.8rem; }
.ts-cycles table { border-collapse: collapse; margin-top: 0.5rem; }
.ts-cycles th, .ts-cycles td { border: 1px solid #ddd; padding: 0.3rem 0.7rem; font-size: 0.85rem; }
.ts-breakdown { margin-top: 1rem; }
.ts-letter { display: inline-block; padding: 0.1rem 0.3rem; margin: 0.1rem; border-radius: 4px; background: #eee; }
.ts-letter.vowel { background: #d9c9f5; }
</style>
