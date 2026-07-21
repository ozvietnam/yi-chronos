<script setup>
import { ref, onMounted, watch } from "vue";
import { castThanSo, thanSoReportPdf } from "../lib/api.js";
import { activePerson } from "../stores/userDataStore.js";

const form = ref({
  name: "",
  currentName: "",
  birthDate: "",
  system: "pythagorean",
  nameOrder: "vn",
  targetYear: new Date().getFullYear(),
});

const loading = ref(false);
const pdfLoading = ref(false);
const error = ref("");
const result = ref(null);
const showDeep = ref(true);
const calendarLimit = ref(12);

async function submit() {
  error.value = "";
  result.value = null;
  if (!form.value.name.trim() || !form.value.birthDate) {
    error.value = "Vui lòng nhập đầy đủ Họ tên khai sinh và Ngày sinh.";
    return;
  }
  loading.value = true;
  try {
    const now = new Date();
    result.value = await castThanSo({
      name: form.value.name,
      birthDate: form.value.birthDate,
      system: form.value.system,
      nameOrder: form.value.nameOrder,
      currentName: form.value.currentName.trim() || null,
      targetYear: Number(form.value.targetYear) || null,
      targetMonth: now.getMonth() + 1,
      targetDay: now.getDate(),
    });
  } catch (err) {
    error.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

async function downloadPdf() {
  if (!form.value.name.trim() || !form.value.birthDate) return;
  pdfLoading.value = true;
  error.value = "";
  try {
    const url = await thanSoReportPdf({
      name: form.value.name,
      birthDate: form.value.birthDate,
      currentName: form.value.currentName.trim() || null,
      nameOrder: form.value.nameOrder,
      targetYear: Number(form.value.targetYear) || null,
    });
    const a = document.createElement("a");
    a.href = url;
    a.download = `ThanSo_${form.value.birthDate}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    error.value = err?.message || String(err);
  } finally {
    pdfLoading.value = false;
  }
}

let _lastSynced = null;
function syncFromActive(force) {
  const p = activePerson.value;
  const bd = p?.birth_datetime_local ? p.birth_datetime_local.split("T")[0] : "";
  if (!bd) return;
  if (force || !form.value.birthDate || form.value.birthDate === _lastSynced) {
    const changed = form.value.birthDate !== bd || form.value.name !== (p.name || "");
    form.value.birthDate = bd;
    if (p.name) form.value.name = p.name;
    _lastSynced = bd;
    if ((changed || force) && form.value.name.trim() && bd) submit();
  }
}
onMounted(() => syncFromActive(false));
watch(() => activePerson.value?.person_key, () => syncFromActive(true));

const CORE_ORDER = [
  ["life_path", "Số Đường Đời"],
  ["expression", "Số Sứ Mệnh"],
  ["soul_urge", "Số Linh Hồn"],
  ["personality", "Số Nhân Cách"],
  ["birthday", "Số Ngày Sinh"],
  ["maturity", "Số Trưởng Thành"],
];

const ARC = {
  1: "Khởi đầu / gieo hạt",
  2: "Vun đắp / quan hệ",
  3: "Sáng tạo / giao tiếp",
  4: "Xây nền / kỷ luật",
  5: "Thay đổi / tự do",
  6: "Trách nhiệm / nhà",
  7: "Nội quán / học sâu",
  8: "Gặt hái / quyền lực",
  9: "Hoàn tất / buông",
};
</script>

<template>
  <div class="than-so-panel">
    <header class="ts-head">
      <h2>Thần Số Học Pythagoras</h2>
      <p class="ts-sub">
        Lá số chuẩn Decoz — một nguồn tính từ API. Đọc cấu trúc, không bói cát/hung.
      </p>
    </header>

    <form class="ts-form" @submit.prevent="submit">
      <label>
        Họ tên khai sinh đầy đủ
        <input v-model="form.name" type="text" placeholder="Nguyễn Văn An" autocomplete="off" />
      </label>
      <label>
        Tên đang dùng <span class="ts-opt">(tuỳ chọn — Minor numbers)</span>
        <input v-model="form.currentName" type="text" placeholder="An Nguyễn" autocomplete="off" />
      </label>
      <div class="ts-row">
        <label>
          Ngày sinh
          <input v-model="form.birthDate" type="date" />
        </label>
        <label>
          Thứ tự tên
          <select v-model="form.nameOrder">
            <option value="vn">Việt (Họ…Tên)</option>
            <option value="western">Western (First…Last)</option>
          </select>
        </label>
        <label>
          Hệ chữ cái
          <select v-model="form.system">
            <option value="pythagorean">Pythagoras</option>
            <option value="chaldean">Chaldean (đối chiếu tên)</option>
          </select>
        </label>
        <label>
          Năm xem
          <input v-model="form.targetYear" type="number" min="1900" max="2200" />
        </label>
      </div>
      <div class="ts-actions">
        <button type="submit" :disabled="loading">{{ loading ? "Đang lập…" : "Lập lá số" }}</button>
        <button type="button" class="ts-pdf" :disabled="pdfLoading || !form.name || !form.birthDate" @click="downloadPdf">
          {{ pdfLoading ? "Đang xuất PDF…" : "Tải PDF báo cáo" }}
        </button>
      </div>
    </form>

    <p v-if="error" class="ts-error">{{ error }}</p>

    <section v-if="result" class="ts-result">
      <p class="ts-paradigm">{{ result.reading.paradigm_note }}</p>
      <p v-if="result.deep_reading?.disclaimer" class="ts-disclaimer">{{ result.deep_reading.disclaimer }}</p>
      <p class="ts-meta">
        Chuẩn hoá: <code>{{ result.input.name_normalized }}</code>
        · schema {{ result.schema_version }}
      </p>

      <h3>Số cốt lõi</h3>
      <div class="ts-grid">
        <article v-for="[key, label] in CORE_ORDER" :key="key" class="ts-card">
          <div class="ts-num">{{ result.core[key].value }}</div>
          <div class="ts-label">{{ label }}</div>
          <div class="ts-arch">{{ result.reading.core[key]?.archetype_vi }}</div>
          <p v-if="result.core[key].karmic_debt" class="ts-kd">Nợ {{ result.core[key].karmic_debt }}</p>
        </article>
      </div>

      <div v-if="result.extended" class="ts-extended">
        <h3>Số mở rộng</h3>
        <div class="ts-grid ts-grid-sm">
          <article class="ts-card">
            <div class="ts-num">{{ result.extended.attitude.value }}</div>
            <div class="ts-label">Thái Độ</div>
          </article>
          <article class="ts-card">
            <div class="ts-num">{{ result.extended.balance.value }}</div>
            <div class="ts-label">Cân Bằng</div>
          </article>
          <article class="ts-card">
            <div class="ts-num">{{ result.extended.rational_thought.value }}</div>
            <div class="ts-label">Tư Duy Lý Trí</div>
          </article>
          <article class="ts-card">
            <div class="ts-num">{{ result.extended.subconscious_self.value }}</div>
            <div class="ts-label">Tiềm Thức</div>
          </article>
          <article class="ts-card">
            <div class="ts-num">{{ (result.extended.hidden_passion.values || []).join(', ') || '—' }}</div>
            <div class="ts-label">Đam Mê Tiềm Ẩn</div>
          </article>
          <article class="ts-card">
            <div class="ts-num">{{ (result.extended.karmic_lessons.values || []).join(', ') || 'đủ 1–9' }}</div>
            <div class="ts-label">Bài Học (thiếu)</div>
          </article>
        </div>
        <div class="ts-bridges" v-if="result.extended.bridges">
          <strong>Cầu nối:</strong>
          ĐĐ↔SM {{ result.extended.bridges.life_path_expression.value }} ·
          LH↔NC {{ result.extended.bridges.soul_personality.value }} ·
          ĐĐ↔NS {{ result.extended.bridges.life_path_birthday.value }}
        </div>
        <div class="ts-letters-meta">
          <span v-if="result.extended.cornerstone?.letter">
            Cornerstone <strong>{{ result.extended.cornerstone.letter }}</strong>
            ({{ result.extended.cornerstone.value }})
          </span>
          <span v-if="result.extended.capstone?.letter">
            Capstone <strong>{{ result.extended.capstone.letter }}</strong>
            ({{ result.extended.capstone.value }})
          </span>
          <span v-if="result.extended.first_vowel?.letter">
            First Vowel <strong>{{ result.extended.first_vowel.letter }}</strong>
            ({{ result.extended.first_vowel.value }})
          </span>
          <span v-if="result.cycles.age_digit">
            Age Digit <strong>{{ result.cycles.age_digit.value }}</strong>
          </span>
        </div>
        <div class="ts-planes" v-if="result.extended.planes_of_expression">
          <strong>Mặt phẳng:</strong>
          <span v-for="(pl, key) in result.extended.planes_of_expression.planes" :key="key">
            {{ pl.name_vi }} {{ pl.value }}
          </span>
        </div>
        <div v-if="result.extended.minor" class="ts-minor">
          <strong>Minor (tên đang dùng):</strong>
          Expression {{ result.extended.minor.expression.value }} ·
          Soul {{ result.extended.minor.soul_urge.value }} ·
          Personality {{ result.extended.minor.personality.value }}
        </div>
      </div>

      <div v-if="result.cross_reference" class="ts-xref">
        <strong>Đối chiếu Chaldean (tên):</strong>
        Sứ Mệnh {{ result.cross_reference.expression }} ·
        Linh Hồn {{ result.cross_reference.soul_urge }} ·
        Nhân Cách {{ result.cross_reference.personality }}
      </div>

      <div v-if="result.reading.karmic_debts?.length" class="ts-karmic">
        <h3>Số nợ nghiệp</h3>
        <ul>
          <li v-for="kd in result.reading.karmic_debts" :key="kd.number">
            <strong>{{ kd.number }}</strong> — {{ kd.theme_vi }}: {{ kd.this_life }}
          </li>
        </ul>
      </div>

      <h3>Chu kỳ & Duality</h3>
      <div class="ts-cycles">
        <div class="ts-cycle-row">
          <span v-if="result.cycles.personal_year">
            <strong>Năm CN {{ result.cycles.personal_year.target_year }}:</strong>
            {{ result.cycles.personal_year.value }}
            <em>({{ ARC[result.cycles.personal_year.value] }})</em>
          </span>
          <span v-if="result.cycles.personal_month">
            <strong>Tháng CN:</strong> {{ result.cycles.personal_month.value }}
          </span>
          <span v-if="result.cycles.personal_day">
            <strong>Ngày CN:</strong> {{ result.cycles.personal_day.value }}
          </span>
        </div>
        <div v-if="result.cycles.essence" class="ts-cycle-row">
          <span>
            <strong>Essence (tuổi {{ result.cycles.age }}):</strong>
            {{ result.cycles.essence.value }}
          </span>
          <span v-if="result.cycles.duality">
            <strong>Duality:</strong>
            {{ result.cycles.duality.essence }} × {{ result.cycles.duality.personal_year }}
          </span>
          <span v-if="result.cycles.transits">
            Transit:
            P {{ result.cycles.transits.physical?.letter }} /
            M {{ result.cycles.transits.mental?.letter }} /
            S {{ result.cycles.transits.spiritual?.letter }}
          </span>
        </div>

        <div v-if="result.deep_reading?.cycles?.personal_year" class="ts-year-guide">
          <p>{{ result.deep_reading.cycles.personal_year.read }}</p>
          <ul>
            <li v-for="(a, i) in result.deep_reading.cycles.personal_year.improve" :key="i">{{ a }}</li>
          </ul>
          <p v-if="result.deep_reading.cycles.duality" class="ts-duality">
            {{ result.deep_reading.cycles.duality.read }}
          </p>
        </div>

        <div v-if="result.method_audit" class="ts-audit">
          <h4>Kiểm chứng công thức Life Path</h4>
          <p>{{ result.method_audit.note }}</p>
          <p>
            Decoz A: <strong>{{ result.method_audit.decoz_method_a.value }}</strong>
            <template v-if="result.method_audit.decoz_method_a.karmic_debt">
              (nợ {{ result.method_audit.decoz_method_a.karmic_debt }})
            </template>
            · Shortcut chữ số: {{ result.method_audit.shortcut_digit_string.value }}
            · Shortcut cộng đơn vị: {{ result.method_audit.shortcut_unit_sum.value }}
          </p>
          <p v-if="result.method_audit.diverged || result.method_audit.karmic_hidden_by_shortcut" class="ts-audit-warn">
            Shortcut lệch hoặc che Karmic — YI giữ Method A.
          </p>
        </div>

        <table>
          <thead><tr><th>Đỉnh vận</th><th>Số</th><th>Tuổi</th></tr></thead>
          <tbody>
            <tr v-for="p in result.cycles.pinnacles" :key="'p'+p.index">
              <td>Đỉnh {{ p.index }}</td><td>{{ p.value }}</td><td>{{ p.age_range }}</td>
            </tr>
          </tbody>
        </table>
        <table>
          <thead><tr><th>Thử thách</th><th>Số</th><th></th></tr></thead>
          <tbody>
            <tr v-for="c in result.cycles.challenges" :key="'c'+c.index">
              <td>Thử thách {{ c.index }}</td>
              <td>{{ c.value }}</td>
              <td>{{ c.main ? 'Chính' : '' }}</td>
            </tr>
          </tbody>
        </table>
        <table v-if="result.cycles.period_cycles">
          <thead><tr><th>Chu kỳ đời</th><th>Số</th><th>Tuổi</th></tr></thead>
          <tbody>
            <tr v-for="p in result.cycles.period_cycles" :key="'per'+p.index">
              <td>{{ p.name_vi }}</td><td>{{ p.value }}</td><td>{{ p.age_range }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="result.cycles.personal_calendar?.length" class="ts-calendar">
        <h3>
          Lịch Personal Month
          <button type="button" class="ts-link" @click="calendarLimit = calendarLimit === 12 ? 24 : 12">
            {{ calendarLimit === 12 ? 'Xem 24 tháng' : 'Thu gọn 12 tháng' }}
          </button>
        </h3>
        <div class="ts-cal-grid">
          <article
            v-for="row in result.cycles.personal_calendar.slice(0, calendarLimit)"
            :key="row.label"
            class="ts-cal-cell"
          >
            <div class="ts-cal-label">{{ row.label }}</div>
            <div class="ts-cal-num">{{ row.personal_month }}</div>
            <div class="ts-cal-arc">{{ ARC[row.personal_month] }}</div>
            <div class="ts-cal-py">Năm {{ row.personal_year }}</div>
          </article>
        </div>
      </div>

      <div v-if="result.cycles.transit_timeline?.length" class="ts-timeline">
        <h3>Transit / Essence — 9 tuổi tới</h3>
        <p v-if="result.deep_reading?.cycles?.transit_timeline_hint" class="ts-meta">
          {{ result.deep_reading.cycles.transit_timeline_hint }}
        </p>
        <table>
          <thead>
            <tr>
              <th>Tuổi</th><th>P</th><th>M</th><th>S</th><th>Essence</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in result.cycles.transit_timeline" :key="'tt'+row.age">
              <td>{{ row.age }}</td>
              <td>{{ row.physical?.letter }}</td>
              <td>{{ row.mental?.letter }}</td>
              <td>{{ row.spiritual?.letter }}</td>
              <td><strong>{{ row.essence }}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="result.deep_reading" class="ts-deep">
        <h3>
          Luận READ → GAP → IMPROVE
          <button type="button" class="ts-link" @click="showDeep = !showDeep">
            {{ showDeep ? 'Thu gọn' : 'Mở' }}
          </button>
        </h3>
        <div v-show="showDeep">
          <article
            v-for="[key] in CORE_ORDER"
            :key="'deep'+key"
            class="ts-deep-card"
            v-show="result.deep_reading.core?.[key]"
          >
            <h4>
              {{ result.deep_reading.core[key].name_vi }}
              = {{ result.deep_reading.core[key].value }}
            </h4>
            <p><strong>READ:</strong> {{ result.deep_reading.core[key].read }}</p>
            <p><strong>GAP:</strong> {{ result.deep_reading.core[key].gap }}</p>
            <p><strong>IMPROVE:</strong> {{ result.deep_reading.core[key].improve }}</p>
          </article>
        </div>
      </div>

      <details class="ts-breakdown">
        <summary>Chi tiết quy đổi tên ({{ result.input.name_normalized }})</summary>
        <span v-for="(b, i) in result.core.breakdown" :key="i" class="ts-letter" :class="{ vowel: b.is_vowel }">
          {{ b.letter }}<sub>{{ b.value }}</sub>
        </span>
        <div v-if="result.core.expression.parts?.length" class="ts-parts">
          <p v-for="(pt, i) in result.core.expression.parts" :key="i">
            {{ pt.part }}: {{ pt.raw }} → {{ pt.reduced }}
            <em v-if="pt.karmic_debt"> (nợ {{ pt.karmic_debt }})</em>
          </p>
        </div>
      </details>
    </section>
  </div>
</template>

<style scoped>
.than-so-panel { max-width: 960px; margin: 0 auto; padding: 1rem; }
.ts-head h2 { margin: 0; font-family: Georgia, "Times New Roman", serif; }
.ts-sub { color: #5a5348; margin: 0.25rem 0 1rem; }
.ts-opt { color: #888; font-weight: 400; font-size: 0.8rem; }
.ts-form label { display: flex; flex-direction: column; font-size: 0.85rem; gap: 0.25rem; margin-bottom: 0.6rem; }
.ts-form input, .ts-form select { padding: 0.45rem; border: 1px solid #c9c0b0; border-radius: 4px; background: #faf8f4; }
.ts-row { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.ts-row label { flex: 1; min-width: 120px; }
.ts-actions { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.ts-form button { padding: 0.55rem 1.2rem; border: 0; border-radius: 4px; background: #2c4a3e; color: #fff; cursor: pointer; }
.ts-form button.ts-pdf { background: #5c4030; }
.ts-form button:disabled { opacity: 0.6; cursor: default; }
.ts-error { color: #a33; }
.ts-paradigm { background: #f0ebe2; border-left: 3px solid #2c4a3e; padding: 0.6rem 0.8rem; font-style: italic; }
.ts-disclaimer { font-size: 0.78rem; color: #666; }
.ts-meta { font-size: 0.8rem; color: #777; }
.ts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.75rem; }
.ts-grid-sm { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
.ts-card { border: 1px solid #ddd4c4; border-radius: 4px; padding: 0.7rem; text-align: center; background: #fffefb; }
.ts-num { font-size: 1.8rem; font-weight: 700; color: #2c4a3e; }
.ts-label { font-size: 0.78rem; color: #555; }
.ts-arch { font-weight: 600; margin: 0.2rem 0; font-size: 0.85rem; }
.ts-kd { font-size: 0.72rem; color: #8a5a2a; }
.ts-extended { margin: 1rem 0; }
.ts-bridges, .ts-planes, .ts-minor, .ts-xref, .ts-letters-meta { margin: 0.6rem 0; font-size: 0.9rem; }
.ts-letters-meta span { margin-right: 1rem; display: inline-block; }
.ts-planes span { margin-right: 0.75rem; }
.ts-audit { background: #f5f1e8; padding: 0.7rem 0.9rem; border-radius: 4px; margin: 0.6rem 0; font-size: 0.86rem; }
.ts-audit-warn { color: #8a4b1a; font-weight: 600; }
.ts-duality { font-style: italic; color: #555; margin-top: 0.4rem; }
.ts-timeline { margin: 1.2rem 0; }
.ts-timeline table { border-collapse: collapse; }
.ts-timeline th, .ts-timeline td { border: 1px solid #ddd; padding: 0.25rem 0.55rem; font-size: 0.82rem; }
.ts-cycles table { border-collapse: collapse; margin-top: 0.5rem; margin-right: 1rem; display: inline-table; vertical-align: top; }
.ts-cycles th, .ts-cycles td { border: 1px solid #ddd; padding: 0.3rem 0.7rem; font-size: 0.85rem; }
.ts-cycle-row { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 0.5rem; }
.ts-cycle-row em { color: #666; font-size: 0.85rem; }
.ts-year-guide { background: #f7f3ea; padding: 0.7rem 0.9rem; border-radius: 4px; margin: 0.6rem 0; font-size: 0.9rem; }
.ts-calendar { margin: 1.2rem 0; }
.ts-cal-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 0.5rem; }
.ts-cal-cell { border: 1px solid #e0d6c6; padding: 0.5rem; text-align: center; background: #fffefb; }
.ts-cal-label { font-size: 0.72rem; color: #777; }
.ts-cal-num { font-size: 1.4rem; font-weight: 700; color: #2c4a3e; }
.ts-cal-arc { font-size: 0.68rem; color: #555; }
.ts-cal-py { font-size: 0.65rem; color: #999; }
.ts-deep { margin: 1.2rem 0; }
.ts-deep-card { border-top: 1px solid #e5ddd0; padding: 0.7rem 0; }
.ts-deep-card h4 { margin: 0 0 0.35rem; font-size: 0.95rem; }
.ts-deep-card p { margin: 0.25rem 0; font-size: 0.86rem; line-height: 1.45; }
.ts-link { background: none; border: none; color: #2c4a3e; text-decoration: underline; cursor: pointer; font-size: 0.8rem; margin-left: 0.5rem; }
.ts-breakdown { margin-top: 1rem; }
.ts-letter { display: inline-block; padding: 0.1rem 0.3rem; margin: 0.1rem; border-radius: 3px; background: #eee; }
.ts-letter.vowel { background: #dce8e2; }
.ts-parts { margin-top: 0.5rem; font-size: 0.85rem; }
</style>
