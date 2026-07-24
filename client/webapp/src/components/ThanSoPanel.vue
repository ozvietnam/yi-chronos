<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { castThanSo, thanSoReportPdf, thanSoGlossary, thanSoCompatibility, thanSoCompatibilityPdf } from "../lib/api.js";
import { activePerson } from "../stores/userDataStore.js";
import ActivePersonBar from "./ActivePersonBar.vue";

const form = ref({
  name: "",
  currentName: "",
  birthDate: "",
  system: "pythagorean",
  nameOrder: "vn",
  targetYear: new Date().getFullYear(),
});

const compatForm = ref({
  nameB: "",
  birthDateB: "",
  nameOrderB: "vn",
  relationshipType: "partner",
});
const compatLoading = ref(false);
const compatPdfLoading = ref(false);
const compatResult = ref(null);

const loading = ref(false);
const pdfLoading = ref(false);
const error = ref("");
const result = ref(null);
const showDeep = ref(true);
const calendarLimit = ref(12);
const glossary = ref(null);
const glossaryOpen = ref(null);

async function loadGlossary() {
  try {
    glossary.value = await thanSoGlossary();
  } catch {
    glossary.value = null;
  }
}

function openGlossary(num) {
  if (num == null) return;
  glossaryOpen.value = String(Array.isArray(num) ? num[0] : num);
}

const CORE_ORDER = [
  ["life_path", "Số Đường Đời"],
  ["expression", "Số Sứ Mệnh"],
  ["soul_urge", "Số Linh Hồn"],
  ["personality", "Số Nhân Cách"],
  ["birthday", "Số Ngày Sinh"],
  ["maturity", "Số Trưởng Thành"],
];

const glossaryEntry = computed(() => {
  if (!glossary.value?.numbers || glossaryOpen.value == null) return null;
  return glossary.value.numbers[glossaryOpen.value] || null;
});

const lifePathCore = computed(() => result.value?.core?.life_path || null);
const otherCore = computed(() =>
  CORE_ORDER.filter(([key]) => key !== "life_path").map(([key, label]) => ({
    key,
    label,
    node: result.value?.core?.[key],
    arch: result.value?.reading?.core?.[key]?.archetype_vi,
  })),
);
const plainSummary = computed(() => result.value?.reading?.plain_summary || null);
const karmicDebts = computed(() => result.value?.reading?.karmic_debts || []);
function karmicLabel(kd) {
  if (kd == null) return "";
  return `Bài học kèm ${kd}`;
}
function karmicShort(kd) {
  const hit = (karmicDebts.value || []).find((d) => d.number === kd);
  if (!hit) return karmicLabel(kd);
  const theme = (hit.theme_vi || "").replace(/^Bài học kèm về\s*/i, "");
  return theme ? `Bài học kèm ${kd}: ${theme}` : karmicLabel(kd);
}

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

async function submitCompat() {
  error.value = "";
  compatResult.value = null;
  if (!form.value.name.trim() || !form.value.birthDate) {
    error.value = "Nhập họ tên + ngày sinh người A (form trên) trước.";
    return;
  }
  if (!compatForm.value.nameB.trim() || !compatForm.value.birthDateB) {
    error.value = "Nhập đầy đủ họ tên + ngày sinh người B.";
    return;
  }
  compatLoading.value = true;
  try {
    compatResult.value = await thanSoCompatibility({
      nameA: form.value.name,
      birthDateA: form.value.birthDate,
      nameOrderA: form.value.nameOrder,
      nameB: compatForm.value.nameB,
      birthDateB: compatForm.value.birthDateB,
      nameOrderB: compatForm.value.nameOrderB,
      relationshipType: compatForm.value.relationshipType,
      targetYear: Number(form.value.targetYear) || null,
    });
  } catch (err) {
    error.value = err?.message || String(err);
  } finally {
    compatLoading.value = false;
  }
}

async function downloadCompatPdf() {
  if (!form.value.name.trim() || !compatForm.value.nameB.trim()) return;
  compatPdfLoading.value = true;
  error.value = "";
  try {
    const url = await thanSoCompatibilityPdf({
      nameA: form.value.name,
      birthDateA: form.value.birthDate,
      nameOrderA: form.value.nameOrder,
      nameB: compatForm.value.nameB,
      birthDateB: compatForm.value.birthDateB,
      nameOrderB: compatForm.value.nameOrderB,
      relationshipType: compatForm.value.relationshipType,
      targetYear: Number(form.value.targetYear) || null,
    });
    const a = document.createElement("a");
    a.href = url;
    a.download = `ThanSo_Compat_${form.value.birthDate}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    error.value = err?.message || String(err);
  } finally {
    compatPdfLoading.value = false;
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
onMounted(() => {
  syncFromActive(false);
  loadGlossary();
});
watch(() => activePerson.value?.person_key, () => syncFromActive(true));

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
      <p class="ts-brand">Pytago</p>
      <h2>Thần Số Học · Pythagoras</h2>
      <p class="ts-sub">
        Lá số Decoz — đọc cấu trúc tâm–thân qua số, không bói cát/hung.
      </p>
    </header>

    <form class="ts-form" @submit.prevent="submit">
      <label class="ts-field ts-field-wide">
        <span>Họ tên khai sinh</span>
        <input v-model="form.name" type="text" placeholder="Nguyễn Văn An" autocomplete="off" />
      </label>
      <label class="ts-field ts-field-wide">
        <span>Tên đang dùng <em class="ts-opt">tuỳ chọn · Minor</em></span>
        <input v-model="form.currentName" type="text" placeholder="tên thường gọi (nếu khác)" autocomplete="off" />
      </label>
      <ActivePersonBar />
      <label class="ts-field">
        <span>Thứ tự tên</span>
        <select v-model="form.nameOrder">
          <option value="vn">Việt (Họ…Tên)</option>
          <option value="western">Western (First…Last)</option>
        </select>
      </label>
      <label class="ts-field">
        <span>Hệ chữ cái</span>
        <select v-model="form.system">
          <option value="pythagorean">Pythagoras</option>
          <option value="chaldean">Chaldean (đối chiếu)</option>
        </select>
      </label>
      <label class="ts-field">
        <span>Năm xem</span>
        <input v-model="form.targetYear" type="number" min="1900" max="2200" />
      </label>
      <div class="ts-actions">
        <button type="submit" class="ts-btn-primary" :disabled="loading">
          {{ loading ? "Đang lập…" : "Lập lá số" }}
        </button>
        <button
          type="button"
          class="ts-btn-ghost"
          :disabled="pdfLoading || !form.name || !form.birthDate"
          @click="downloadPdf"
        >
          {{ pdfLoading ? "Đang xuất PDF…" : "Tải PDF" }}
        </button>
      </div>
    </form>

    <p v-if="error" class="ts-error" role="alert">{{ error }}</p>

    <section v-if="result" class="ts-result">
      <!-- Hero: Life Path — first after cast (không để disclaimer che) -->
      <div
        v-if="lifePathCore"
        class="ts-hero"
        role="button"
        tabindex="0"
        @click="openGlossary(lifePathCore.value)"
        @keydown.enter="openGlossary(lifePathCore.value)"
      >
        <div class="ts-hero-glow" aria-hidden="true" />
        <div class="ts-hero-num">{{ lifePathCore.value }}</div>
        <div class="ts-hero-body">
          <p class="ts-hero-label">Số Đường Đời</p>
          <p class="ts-hero-arch">{{ result.reading.core.life_path?.archetype_vi }}</p>
          <p class="ts-hero-name">{{ result.input.name_raw }} · {{ result.input.birth_date }}</p>
          <p v-if="lifePathCore.karmic_debt" class="ts-kd">{{ karmicShort(lifePathCore.karmic_debt) }}</p>
        </div>
        <div v-if="result.cycles?.personal_year" class="ts-hero-cycle">
          <span class="ts-hero-cycle-label">Năm CN {{ result.cycles.personal_year.target_year }}</span>
          <span class="ts-hero-cycle-num">{{ result.cycles.personal_year.value }}</span>
          <span class="ts-hero-cycle-arc">{{ ARC[result.cycles.personal_year.value] }}</span>
        </div>
      </div>

      <!-- Tóm tắt người thường đọc được — ngay dưới hero -->
      <section v-if="plainSummary" class="ts-plain">
        <h3 class="ts-section-h">{{ plainSummary.title_vi }}</h3>
        <p class="ts-plain-intro">{{ plainSummary.intro_vi }}</p>
        <p v-if="plainSummary.karmic_intro_vi" class="ts-plain-karmic-intro">
          {{ plainSummary.karmic_intro_vi }}
        </p>
        <ul class="ts-plain-list">
          <li v-for="(b, i) in plainSummary.bullets" :key="'ps'+i">{{ b }}</li>
        </ul>
        <div v-if="plainSummary.one_practice_vi" class="ts-plain-practice">
          <span class="ts-plain-practice-k">Việc nhỏ tuần này</span>
          <p>{{ plainSummary.one_practice_vi }}</p>
        </div>
      </section>

      <section v-if="karmicDebts.length" class="ts-karmic-panel">
        <h3 class="ts-section-h">Bài học kèm — «nợ» nghĩa là gì?</h3>
        <p class="ts-plain-intro">
          Không phải án kiếp trước. Khi cộng ra 13 / 14 / 16 / 19 rồi mới rút về 4 / 5 / 7 / 1,
          hệ ghi nhận thêm một thói quen cần luyện.
        </p>
        <article v-for="kd in karmicDebts" :key="'kd'+kd.number" class="ts-karmic-card">
          <header class="ts-karmic-head">
            <span class="ts-karmic-num">{{ kd.number }}→{{ kd.reduces_to }}</span>
            <div>
              <h4>{{ kd.theme_vi || ('Bài học kèm ' + kd.number) }}</h4>
              <p class="ts-meta">Trên {{ kd.source }} · {{ kd.where_vi }}</p>
            </div>
          </header>
          <p class="ts-karmic-plain">{{ kd.plain_vi || kd.this_life }}</p>
          <p v-if="kd.practice_vi" class="ts-karmic-practice">
            <span class="ts-rgi-k ts-rgi-improve">Luyện</span> {{ kd.practice_vi }}
          </p>
          <p v-if="kd.avoid_vi" class="ts-karmic-avoid">
            <span class="ts-rgi-k ts-rgi-gap">Tránh</span> {{ kd.avoid_vi }}
          </p>
        </article>
      </section>

      <details class="ts-fold ts-fold-quiet">
        <summary>Paradigm · disclaimer</summary>
        <div class="ts-note ts-note-teal">
          <p>{{ result.reading.paradigm_note }}</p>
          <p v-if="result.deep_reading?.disclaimer" class="ts-disclaimer">{{ result.deep_reading.disclaimer }}</p>
        </div>
        <p class="ts-meta">
          Chuẩn hoá <code>{{ result.input.name_normalized }}</code>
          · schema {{ result.schema_version }}
        </p>
      </details>

      <h3 class="ts-section-h">Số cốt lõi</h3>
      <div class="ts-grid">
        <article
          v-for="item in otherCore"
          :key="item.key"
          class="ts-card ts-click"
          @click="openGlossary(item.node?.value)"
        >
          <div class="ts-num">{{ item.node?.value }}</div>
          <div class="ts-label">{{ item.label }}</div>
          <div class="ts-arch">{{ item.arch }}</div>
          <p v-if="item.node?.karmic_debt" class="ts-kd">{{ karmicLabel(item.node.karmic_debt) }}</p>
        </article>
      </div>

      <div v-if="glossaryEntry" class="ts-glossary">
        <button type="button" class="ts-link" @click="glossaryOpen = null">Đóng</button>
        <h4>Số {{ glossaryOpen }} — {{ glossaryEntry.archetype_vi }}</h4>
        <p><strong>Thế mạnh:</strong> {{ glossaryEntry.strengths }}</p>
        <p><strong>Bóng:</strong> {{ glossaryEntry.shadow }}</p>
        <p class="ts-dd">{{ glossaryEntry.dong_dang }}</p>
      </div>

      <div v-if="result.deep_reading?.synthesis" class="ts-synth">
        <h3 class="ts-section-h">Tên và ngày sinh có cùng pha không?</h3>
        <div class="ts-rgi">
          <p><span class="ts-rgi-k">Đọc</span> {{ result.deep_reading.synthesis.read }}</p>
          <p><span class="ts-rgi-k ts-rgi-gap">Chỗ lệch</span> {{ result.deep_reading.synthesis.gap }}</p>
          <p><span class="ts-rgi-k ts-rgi-improve">Việc nhỏ</span> {{ result.deep_reading.synthesis.improve }}</p>
        </div>
        <ol v-if="result.deep_reading.synthesis.steps?.length" class="ts-steps">
          <li v-for="(s, i) in result.deep_reading.synthesis.steps" :key="'st'+i">{{ s }}</li>
        </ol>
        <p v-if="result.deep_reading.layers?.cheiro_birth_layers" class="ts-meta">
          {{ result.deep_reading.layers.cheiro_birth_layers.read }}
        </p>
        <p
          v-if="result.deep_reading.core?.birthday?.cheiro_birth"
          class="ts-meta"
        >
          Cheiro Birth {{ result.deep_reading.core.birthday.value }}:
          {{ result.deep_reading.core.birthday.cheiro_birth.planet_vi }} —
          {{ result.deep_reading.core.birthday.cheiro_birth.archetype_vi }}
          <template v-if="result.deep_reading.core.birthday.cheiro_birth.conflict_with_decoz">
            · dual lens với Decoz
          </template>
        </p>
      </div>

      <div v-if="result.cycles" class="ts-cycles-band">
        <h3 class="ts-section-h">Chu kỳ hiện tại</h3>
        <div class="ts-cycle-pills">
          <div v-if="result.cycles.personal_year" class="ts-pill">
            <span class="ts-pill-k">Năm CN</span>
            <span class="ts-pill-v">{{ result.cycles.personal_year.value }}</span>
            <span class="ts-pill-s">{{ ARC[result.cycles.personal_year.value] }}</span>
          </div>
          <div v-if="result.cycles.personal_month" class="ts-pill">
            <span class="ts-pill-k">Tháng CN</span>
            <span class="ts-pill-v">{{ result.cycles.personal_month.value }}</span>
          </div>
          <div v-if="result.cycles.personal_day" class="ts-pill">
            <span class="ts-pill-k">Ngày CN</span>
            <span class="ts-pill-v">{{ result.cycles.personal_day.value }}</span>
          </div>
          <div v-if="result.cycles.essence" class="ts-pill">
            <span class="ts-pill-k">Essence · tuổi {{ result.cycles.age }}</span>
            <span class="ts-pill-v">{{ result.cycles.essence.value }}</span>
          </div>
          <div v-if="result.cycles.duality" class="ts-pill ts-pill-wide">
            <span class="ts-pill-k">Duality</span>
            <span class="ts-pill-v">{{ result.cycles.duality.essence }} × {{ result.cycles.duality.personal_year }}</span>
            <span v-if="result.cycles.transits" class="ts-pill-s">
              Transit P {{ result.cycles.transits.physical?.letter }} /
              M {{ result.cycles.transits.mental?.letter }} /
              S {{ result.cycles.transits.spiritual?.letter }}
            </span>
          </div>
        </div>

        <div v-if="result.deep_reading?.cycles?.personal_year" class="ts-note">
          <p>{{ result.deep_reading.cycles.personal_year.read }}</p>
          <ul v-if="result.deep_reading.cycles.personal_year.improve?.length">
            <li v-for="(a, i) in result.deep_reading.cycles.personal_year.improve" :key="i">{{ a }}</li>
          </ul>
          <p v-if="result.deep_reading.cycles.duality" class="ts-duality">
            {{ result.deep_reading.cycles.duality.read }}
          </p>
        </div>
      </div>

      <details class="ts-fold" open>
        <summary>Đỉnh vận · Thử thách · Chu kỳ đời</summary>
        <div class="ts-tables">
          <table>
            <thead><tr><th>Đỉnh vận</th><th>Số</th><th>Tuổi</th></tr></thead>
            <tbody>
              <tr v-for="p in result.cycles.pinnacles" :key="'p'+p.index">
                <td>Đỉnh {{ p.index }}</td>
                <td class="ts-td-num">{{ p.value }}</td>
                <td>{{ p.age_range }}</td>
              </tr>
            </tbody>
          </table>
          <table>
            <thead><tr><th>Thử thách</th><th>Số</th><th></th></tr></thead>
            <tbody>
              <tr v-for="c in result.cycles.challenges" :key="'c'+c.index">
                <td>Thử thách {{ c.index }}</td>
                <td class="ts-td-num">{{ c.value }}</td>
                <td>{{ c.main ? "Chính" : "" }}</td>
              </tr>
            </tbody>
          </table>
          <table v-if="result.cycles.period_cycles">
            <thead><tr><th>Chu kỳ đời</th><th>Số</th><th>Tuổi</th></tr></thead>
            <tbody>
              <tr v-for="p in result.cycles.period_cycles" :key="'per'+p.index">
                <td>{{ p.name_vi }}</td>
                <td class="ts-td-num">{{ p.value }}</td>
                <td>{{ p.age_range }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="result.deep_reading?.cycles?.pinnacles?.length" class="ts-pin-deep">
          <article v-for="(p, i) in result.deep_reading.cycles.pinnacles" :key="'pd'+i" class="ts-deep-card">
            <p>{{ p.read }}</p>
            <ul v-if="p.improve?.length">
              <li v-for="(a, j) in p.improve" :key="'pi'+j">{{ a }}</li>
            </ul>
          </article>
        </div>
        <div v-if="result.deep_reading?.cycles?.challenges?.length" class="ts-chal-deep">
          <article v-for="(c, i) in result.deep_reading.cycles.challenges" :key="'cd'+i" class="ts-deep-card">
            <p>{{ c.read }}</p>
            <ul v-if="c.improve?.length">
              <li v-for="(a, j) in c.improve" :key="'ci'+j">{{ a }}</li>
            </ul>
          </article>
        </div>
      </details>

      <div v-if="result.cycles.personal_year_calendar?.length" class="ts-year-cal">
        <h3 class="ts-section-h">9 năm cá nhân tới</h3>
        <div class="ts-cal-grid">
          <article
            v-for="row in result.cycles.personal_year_calendar"
            :key="'py'+row.year"
            class="ts-cal-cell ts-click"
            @click="openGlossary(row.personal_year)"
          >
            <div class="ts-cal-label">{{ row.year }}</div>
            <div class="ts-cal-num">{{ row.personal_year }}</div>
            <div class="ts-cal-arc">{{ ARC[row.personal_year] }}</div>
          </article>
        </div>
      </div>

      <div v-if="result.cycles.personal_calendar?.length" class="ts-calendar">
        <h3 class="ts-section-h">
          Lịch Personal Month
          <button type="button" class="ts-link" @click="calendarLimit = calendarLimit === 12 ? 24 : 12">
            {{ calendarLimit === 12 ? "Xem 24 tháng" : "Thu gọn 12" }}
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

      <details v-if="result.cycles.personal_day_window?.length" class="ts-fold">
        <summary>21 ngày cá nhân tới</summary>
        <div class="timing-list">
          <div
            v-for="row in result.cycles.personal_day_window"
            :key="row.date"
            class="timing-row"
          >
            <strong>D+{{ row.offset }} · {{ row.date }}</strong>
            <small>
              PY/PM/PD {{ row.personal_year }}/{{ row.personal_month }}/{{ row.personal_day }}
              · {{ ARC[row.personal_day] }}
            </small>
          </div>
        </div>
      </details>

      <details v-if="result.cycles.transit_timeline?.length" class="ts-fold">
        <summary>Transit / Essence — 9 tuổi tới</summary>
        <p v-if="result.deep_reading?.cycles?.transit_timeline_hint" class="ts-meta">
          {{ result.deep_reading.cycles.transit_timeline_hint }}
        </p>
        <table class="ts-table-full">
          <thead>
            <tr><th>Tuổi</th><th>P</th><th>M</th><th>S</th><th>Essence</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in result.cycles.transit_timeline" :key="'tt'+row.age">
              <td>{{ row.age }}</td>
              <td>{{ row.physical?.letter }}</td>
              <td>{{ row.mental?.letter }}</td>
              <td>{{ row.spiritual?.letter }}</td>
              <td class="ts-td-num">{{ row.essence }}</td>
            </tr>
          </tbody>
        </table>
      </details>

      <details v-if="result.extended" class="ts-fold">
        <summary>Số mở rộng · Inclusion · Balliett</summary>
        <div class="ts-grid ts-grid-sm">
          <article class="ts-card ts-card-quiet">
            <div class="ts-num">{{ result.extended.attitude.value }}</div>
            <div class="ts-label">Thái Độ</div>
          </article>
          <article class="ts-card ts-card-quiet">
            <div class="ts-num">{{ result.extended.balance.value }}</div>
            <div class="ts-label">Cân Bằng</div>
          </article>
          <article class="ts-card ts-card-quiet">
            <div class="ts-num">{{ result.extended.rational_thought.value }}</div>
            <div class="ts-label">Tư Duy Lý Trí</div>
          </article>
          <article class="ts-card ts-card-quiet">
            <div class="ts-num">{{ result.extended.subconscious_self.value }}</div>
            <div class="ts-label">Tiềm Thức</div>
          </article>
          <article class="ts-card ts-card-quiet">
            <div class="ts-num">{{ (result.extended.hidden_passion.values || []).join(", ") || "—" }}</div>
            <div class="ts-label">Đam Mê Tiềm Ẩn</div>
          </article>
          <article class="ts-card ts-card-quiet">
            <div class="ts-num">{{ (result.extended.karmic_lessons.values || []).join(", ") || "đủ 1–9" }}</div>
            <div class="ts-label">Bài Học (thiếu)</div>
          </article>
        </div>
        <div class="ts-meta-row" v-if="result.extended.bridges">
          <strong>Cầu nối</strong>
          ĐĐ↔SM {{ result.extended.bridges.life_path_expression.value }} ·
          LH↔NC {{ result.extended.bridges.soul_personality.value }} ·
          ĐĐ↔NS {{ result.extended.bridges.life_path_birthday.value }}
        </div>
        <div class="ts-meta-row ts-letters-meta">
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
        <div class="ts-meta-row" v-if="result.extended.planes_of_expression">
          <strong>Mặt phẳng</strong>
          <span v-for="(pl, key) in result.extended.planes_of_expression.planes" :key="key">
            {{ pl.name_vi }} {{ pl.value }}
          </span>
        </div>
        <div v-if="result.extended.minor" class="ts-meta-row">
          <strong>Minor</strong>
          Expression {{ result.extended.minor.expression.value }} ·
          Soul {{ result.extended.minor.soul_urge.value }} ·
          Personality {{ result.extended.minor.personality.value }}
        </div>
        <div v-if="result.extended.inclusion_table" class="ts-inclusion">
          <strong>{{ result.extended.inclusion_table.name_vi }}</strong>
          <span class="ts-meta"> · {{ result.extended.inclusion_table.provenance }}</span>
          <div class="ts-incl-grid">
            <span
              v-for="n in 9"
              :key="'inc'+n"
              class="ts-incl-cell"
              :class="{
                miss: !(result.extended.inclusion_table.frequency[String(n)] > 0),
                above: (result.extended.inclusion_table.above_average || []).includes(n),
              }"
            >
              {{ n }}×{{ result.extended.inclusion_table.frequency[String(n)] || 0 }}
            </span>
          </div>
          <p v-if="result.extended.inclusion_table.average != null" class="ts-meta">
            TB {{ result.extended.inclusion_table.average }}
            · trên TB: {{ (result.extended.inclusion_table.above_average || []).join(", ") || "—" }}
            · dưới TB: {{ (result.extended.inclusion_table.below_average || []).join(", ") || "—" }}
          </p>
          <p class="ts-meta">{{ result.extended.inclusion_table.intensity_note || result.extended.inclusion_table.note }}</p>
        </div>

        <div v-if="result.balliett" class="ts-balliett">
          <h4 class="ts-section-h">Balliett — màu · âm · Life Song</h4>
          <p class="ts-meta">{{ result.balliett.provenance?.note }}</p>
          <div v-if="result.balliett.life_song" class="ts-balliett-grid">
            <p>
              <strong>Birth digit</strong>
              {{ result.balliett.life_song.birth_digit }}
              <template v-if="result.balliett.life_song.keynote">
                · keynote <em class="ts-keynote">{{ result.balliett.life_song.keynote }}</em>
              </template>
              <template v-if="result.balliett.life_song.colors?.length">
                · {{ result.balliett.life_song.colors.join(", ") }}
              </template>
            </p>
            <p v-if="result.balliett.birth_digit?.wanamaker_mode" class="ts-meta">
              Wanamaker: {{ (result.balliett.birth_digit.birth_numbers || []).join(", ") }}
            </p>
            <p v-if="result.balliett.life_song.spiritual_birthday">
              <strong>Spiritual Birthday (ngày luyện)</strong>
              {{ (result.balliett.life_song.spiritual_birthday.days_in_month || []).join(", ") }}
              mỗi tháng
              <span class="ts-meta"> — {{ result.balliett.life_song.spiritual_birthday.yi_reframe }}</span>
            </p>
            <p class="ts-meta">{{ result.balliett.life_song.practice_vi }}</p>
            <p v-if="result.balliett.life_song.chart_status === 'missing_ocr'" class="ts-meta">
              {{ result.balliett.life_song.chart_note_vi }}
            </p>
          </div>
          <div v-if="result.deep_reading?.layers?.balliett_tone" class="ts-rgi">
            <p><span class="ts-rgi-k">Read</span> {{ result.deep_reading.layers.balliett_tone.read }}</p>
            <p><span class="ts-rgi-k ts-rgi-gap">Gap</span> {{ result.deep_reading.layers.balliett_tone.gap }}</p>
            <p><span class="ts-rgi-k ts-rgi-improve">Improve</span> {{ result.deep_reading.layers.balliett_tone.improve }}</p>
          </div>
        </div>
      </details>

      <div v-if="result.cross_reference" class="ts-xref">
        <strong>Đối chiếu Chaldean</strong>
        Sứ Mệnh {{ result.cross_reference.expression }} ·
        Linh Hồn {{ result.cross_reference.soul_urge }} ·
        Nhân Cách {{ result.cross_reference.personality }}
        <template v-if="result.cross_reference.name_compound_flat">
          <p>
            Số kép tên {{ result.cross_reference.name_compound_flat.raw }}
            → {{ result.cross_reference.name_compound_flat.reduced }}
            <template v-if="result.cross_reference.name_compound_flat.compound_reading">
              — {{ result.cross_reference.name_compound_flat.compound_reading.symbol }}:
              {{ result.cross_reference.name_compound_flat.compound_reading.meaning_vi }}
            </template>
          </p>
        </template>
        <p v-if="result.cross_reference.birthday_compound" class="ts-meta">
          Số kép ngày {{ result.cross_reference.birthday_compound.value }}
          (→ {{ result.cross_reference.birthday_compound.resolved }}):
          {{ result.cross_reference.birthday_compound.symbol }}
        </p>
      </div>

      <details v-if="result.method_audit" class="ts-fold">
        <summary>Kiểm chứng công thức (cho người muốn soi cách tính)</summary>
        <div class="ts-audit">
          <p>{{ result.method_audit.note }}</p>
          <p>
            Decoz A: <strong>{{ result.method_audit.decoz_method_a.value }}</strong>
            <template v-if="result.method_audit.decoz_method_a.karmic_debt">
              (bài học kèm {{ result.method_audit.decoz_method_a.karmic_debt }})
            </template>
            · Shortcut chữ số: {{ result.method_audit.shortcut_digit_string.value }}
            · Shortcut cộng đơn vị: {{ result.method_audit.shortcut_unit_sum.value }}
          </p>
          <p v-if="result.method_audit.diverged || result.method_audit.karmic_hidden_by_shortcut" class="ts-audit-warn">
            Shortcut lệch hoặc che bài học kèm — YI giữ Method A.
          </p>
          <template v-if="result.method_audit.expression">
            <p>{{ result.method_audit.expression.note }}</p>
            <p>
              Expression Decoz: <strong>{{ result.method_audit.expression.decoz_per_part.value }}</strong>
              · Flat: {{ result.method_audit.expression.flat_full_name_shortcut.value }}
            </p>
            <ul class="ts-audit-parts" v-if="result.method_audit.expression.decoz_per_part.parts?.length">
              <li v-for="(pt, i) in result.method_audit.expression.decoz_per_part.parts" :key="'ea'+i">
                {{ pt.part }}: {{ pt.raw }} → {{ pt.reduced }}
                <em v-if="pt.karmic_debt"> (bài học kèm {{ pt.karmic_debt }})</em>
              </li>
            </ul>
          </template>
        </div>
      </details>

      <div v-if="result.deep_reading" class="ts-deep">
        <h3 class="ts-section-h">
          Đọc từng số · chỗ lệch · việc nhỏ
          <button type="button" class="ts-link" @click="showDeep = !showDeep">
            {{ showDeep ? "Thu gọn" : "Mở" }}
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
              <span class="ts-deep-val">{{ result.deep_reading.core[key].value }}</span>
            </h4>
            <div class="ts-rgi">
              <p><span class="ts-rgi-k">Đọc</span> {{ result.deep_reading.core[key].read }}</p>
              <p><span class="ts-rgi-k ts-rgi-gap">Chỗ lệch</span> {{ result.deep_reading.core[key].gap }}</p>
              <p><span class="ts-rgi-k ts-rgi-improve">Việc nhỏ</span> {{ result.deep_reading.core[key].improve }}</p>
            </div>
          </article>
        </div>
      </div>

      <details class="ts-fold ts-breakdown">
        <summary>Chi tiết quy đổi tên ({{ result.input.name_normalized }})</summary>
        <span v-for="(b, i) in result.core.breakdown" :key="i" class="ts-letter" :class="{ vowel: b.is_vowel }">
          {{ b.letter }}<sub>{{ b.value }}</sub>
        </span>
        <div v-if="result.core.expression.parts?.length" class="ts-parts">
          <p v-for="(pt, i) in result.core.expression.parts" :key="i">
            {{ pt.part }}: {{ pt.raw }} → {{ pt.reduced }}
            <em v-if="pt.karmic_debt"> (bài học kèm {{ pt.karmic_debt }})</em>
          </p>
        </div>
      </details>
    </section>

    <details class="ts-fold ts-compat-box">
      <summary>Tương hợp với người B</summary>
      <p class="ts-sub ts-sub-inline">
        So sánh Life Path · Expression · Soul Urge · Personality — đọc cấu trúc đôi, không phán hợp/khắc.
      </p>
      <form class="ts-form ts-form-compat" @submit.prevent="submitCompat">
        <label class="ts-field ts-field-wide">
          <span>Họ tên người B</span>
          <input v-model="compatForm.nameB" type="text" placeholder="Trần Thị Bình" autocomplete="off" />
        </label>
        <label class="ts-field">
          <span>Ngày sinh B</span>
          <input v-model="compatForm.birthDateB" type="date" />
        </label>
        <label class="ts-field">
          <span>Thứ tự tên B</span>
          <select v-model="compatForm.nameOrderB">
            <option value="vn">Việt (Họ…Tên)</option>
            <option value="western">Western</option>
          </select>
        </label>
        <label class="ts-field">
          <span>Loại quan hệ</span>
          <select v-model="compatForm.relationshipType">
            <option value="partner">Đối tác</option>
            <option value="spouse">Vợ/chồng</option>
            <option value="family">Gia đình</option>
            <option value="colleague">Đồng nghiệp</option>
            <option value="friend">Bạn bè</option>
          </select>
        </label>
        <div class="ts-actions">
          <button type="submit" class="ts-btn-primary" :disabled="compatLoading">
            {{ compatLoading ? "Đang so…" : "So tương hợp" }}
          </button>
          <button
            type="button"
            class="ts-btn-ghost"
            :disabled="compatPdfLoading || !compatForm.nameB || !compatForm.birthDateB"
            @click="downloadCompatPdf"
          >
            {{ compatPdfLoading ? "Đang xuất…" : "PDF tương hợp" }}
          </button>
        </div>
      </form>
      <div v-if="compatResult" class="ts-compat-result">
        <div class="ts-compat-score">
          <strong>{{ compatResult.overall.percent }}</strong>
          <span>/100 · {{ compatResult.overall.label_vi }}</span>
        </div>
        <div class="ts-note ts-note-teal">
          <p>{{ compatResult.paradigm_note }}</p>
          <p class="ts-disclaimer">{{ compatResult.disclaimer }}</p>
        </div>
        <div class="ts-rgi">
          <p><span class="ts-rgi-k">Read</span> {{ compatResult.overall.read }}</p>
          <p><span class="ts-rgi-k ts-rgi-gap">Gap</span> {{ compatResult.overall.gap }}</p>
          <p><span class="ts-rgi-k ts-rgi-improve">Improve</span> {{ compatResult.overall.improve }}</p>
        </div>
        <table class="ts-table-full">
          <thead>
            <tr><th>Lớp</th><th>A</th><th>B</th><th>Khí</th></tr>
          </thead>
          <tbody>
            <tr v-for="asp in compatResult.aspects" :key="asp.key">
              <td>{{ asp.name_vi }}</td>
              <td class="ts-click ts-td-num" @click="openGlossary(asp.a)">{{ asp.a }}</td>
              <td class="ts-click ts-td-num" @click="openGlossary(asp.b)">{{ asp.b }}</td>
              <td>{{ asp.label_vi }}</td>
            </tr>
          </tbody>
        </table>
        <article v-for="asp in compatResult.aspects" :key="'cd'+asp.key" class="ts-deep-card">
          <h4>{{ asp.name_vi }}: {{ asp.a }} × {{ asp.b }}</h4>
          <div class="ts-rgi">
            <p><span class="ts-rgi-k">Read</span> {{ asp.read }}</p>
            <p><span class="ts-rgi-k ts-rgi-gap">Gap</span> {{ asp.gap }}</p>
            <p><span class="ts-rgi-k ts-rgi-improve">Improve</span> {{ asp.improve }}</p>
          </div>
        </article>
        <p v-if="compatResult.composite_life_path" class="ts-meta">{{ compatResult.composite_life_path.read }}</p>
        <p v-if="compatResult.personal_year?.read" class="ts-meta">{{ compatResult.personal_year.read }}</p>
      </div>
    </details>
  </div>
</template>

<style scoped>
.than-so-panel {
  --ts-gold: var(--accent-gold, #e8c95a);
  --ts-gold-soft: var(--accent-gold-soft, #f5e6b1);
  --ts-teal: var(--accent-teal, #5be5d3);
  --ts-surface: rgba(255, 255, 255, 0.035);
  --ts-surface-strong: rgba(255, 255, 255, 0.055);
  position: relative;
  max-width: 960px;
  margin: 0 auto;
  padding: 0.25rem 0.35rem 1.5rem;
  color: var(--text-primary, #e6eef5);
}

/* ── Header ─────────────────────────────────────────────── */
.ts-head {
  position: relative;
  margin-bottom: 1.1rem;
  padding: 1.1rem 1rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background:
    radial-gradient(ellipse 70% 80% at 12% 0%, rgba(232, 201, 90, 0.14), transparent 55%),
    radial-gradient(ellipse 50% 60% at 100% 100%, rgba(91, 229, 211, 0.08), transparent 50%),
    var(--ts-surface);
  overflow: hidden;
}
.ts-brand {
  margin: 0 0 0.15rem;
  font-size: clamp(2rem, 5vw, 2.75rem);
  font-weight: 700;
  letter-spacing: 0.04em;
  line-height: 1.05;
  color: var(--ts-gold);
  text-shadow: 0 0 40px rgba(232, 201, 90, 0.25);
}
.ts-head h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}
.ts-sub {
  margin: 0.45rem 0 0;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-size: 0.88rem;
  line-height: 1.45;
  max-width: 42rem;
}
.ts-sub-inline { margin: 0.35rem 0 0.85rem; }
.ts-opt {
  color: var(--text-faint, rgba(230, 238, 245, 0.35));
  font-style: normal;
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
  font-size: 0.72rem;
  margin-left: 0.35rem;
}

/* ── Form ───────────────────────────────────────────────── */
.ts-form {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: var(--ts-surface);
}
.ts-form-compat { margin-top: 0.5rem; }
.ts-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.ts-field-wide { grid-column: 1 / -1; }
.ts-field span {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.ts-form input,
.ts-form select {
  width: 100%;
  box-sizing: border-box;
  padding: 0.5rem 0.65rem;
  border-radius: 6px;
  border: 1px solid var(--border-medium, rgba(255, 255, 255, 0.14));
  background: var(--bg-input, rgba(0, 0, 0, 0.35));
  color: var(--text-primary, #e6eef5);
  font: inherit;
  font-size: 0.9rem;
}
.ts-form input:focus,
.ts-form select:focus {
  outline: none;
  border-color: var(--border-accent, rgba(232, 201, 90, 0.35));
  box-shadow: 0 0 0 2px rgba(232, 201, 90, 0.12);
}
.ts-form select option { background: #0d1620; color: #e6eef5; }
.ts-actions {
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 2px;
}
.ts-btn-primary,
.ts-btn-ghost {
  padding: 0.55rem 1.15rem;
  border-radius: 7px;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, opacity 0.15s;
}
.ts-btn-primary {
  border: 1px solid rgba(232, 201, 90, 0.45);
  background: linear-gradient(180deg, rgba(232, 201, 90, 0.22), rgba(232, 201, 90, 0.1));
  color: var(--ts-gold-soft);
}
.ts-btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, rgba(232, 201, 90, 0.32), rgba(232, 201, 90, 0.16));
}
.ts-btn-ghost {
  border: 1px solid var(--border-medium, rgba(255, 255, 255, 0.14));
  background: transparent;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}
.ts-btn-ghost:hover:not(:disabled) {
  border-color: var(--border-accent, rgba(232, 201, 90, 0.35));
  color: var(--ts-gold-soft);
}
.ts-btn-primary:disabled,
.ts-btn-ghost:disabled { opacity: 0.45; cursor: default; }

.ts-error {
  margin: 0.75rem 0 0;
  padding: 0.55rem 0.75rem;
  border-radius: 6px;
  border-left: 3px solid var(--accent-red, #ff9080);
  background: rgba(255, 144, 128, 0.08);
  color: var(--accent-red, #ff9080);
  font-size: 0.88rem;
}

/* ── Result chrome ──────────────────────────────────────── */
.ts-result { margin-top: 1.25rem; display: flex; flex-direction: column; gap: 0.85rem; }
.ts-section-h {
  margin: 0.35rem 0 0.15rem;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.65px;
  text-transform: uppercase;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.ts-meta {
  margin: 0;
  font-size: 0.78rem;
  color: var(--text-faint, rgba(230, 238, 245, 0.35));
}
.ts-meta code {
  color: var(--ts-teal);
  font-size: 0.8rem;
}
.ts-disclaimer {
  margin: 0.35rem 0 0;
  font-size: 0.75rem;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-style: normal;
}
.ts-note {
  padding: 0.7rem 0.85rem;
  border-radius: 8px;
  border-left: 3px solid var(--ts-gold);
  background: rgba(232, 201, 90, 0.06);
  font-size: 0.88rem;
  line-height: 1.5;
}
.ts-note p { margin: 0; }
.ts-note ul { margin: 0.4rem 0 0 1.1rem; padding: 0; }
.ts-note-teal {
  border-left-color: var(--ts-teal);
  background: rgba(91, 229, 211, 0.06);
}
.ts-duality {
  margin-top: 0.45rem !important;
  font-style: italic;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}

/* ── Hero Life Path ─────────────────────────────────────── */
.ts-hero {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem 1.25rem;
  align-items: center;
  padding: 1.15rem 1.25rem;
  border-radius: 14px;
  border: 1px solid rgba(232, 201, 90, 0.35);
  background:
    radial-gradient(circle at 8% 50%, rgba(232, 201, 90, 0.18), transparent 45%),
    var(--ts-surface-strong);
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
  animation: ts-hero-in 0.55s ease-out both;
}
@keyframes ts-hero-in {
  from { opacity: 0; transform: translateY(10px) scale(0.985); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.ts-hero:hover {
  border-color: rgba(232, 201, 90, 0.55);
  box-shadow: 0 0 28px rgba(232, 201, 90, 0.12);
}
.ts-hero-glow {
  position: absolute;
  inset: -40% -20% auto auto;
  width: 55%;
  height: 140%;
  background: radial-gradient(circle, rgba(91, 229, 211, 0.08), transparent 70%);
  pointer-events: none;
}
.ts-hero-num {
  position: relative;
  font-size: clamp(3rem, 8vw, 4.25rem);
  font-weight: 700;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  color: var(--ts-gold);
  text-shadow: 0 0 32px rgba(232, 201, 90, 0.35);
  min-width: 1.2em;
  text-align: center;
}
.ts-hero-label {
  margin: 0;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}
.ts-hero-arch {
  margin: 0.2rem 0 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ts-gold-soft);
}
.ts-hero-name {
  margin: 0.3rem 0 0;
  font-size: 0.78rem;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.ts-fold-quiet {
  background: transparent;
  border-color: transparent;
  padding-left: 0;
  padding-right: 0;
}
.ts-fold-quiet > summary {
  color: var(--text-faint, rgba(230, 238, 245, 0.35));
  font-weight: 600;
}
.ts-hero-cycle {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.1rem;
  padding-left: 1rem;
  border-left: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  min-width: 7rem;
}
.ts-hero-cycle-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-faint, rgba(230, 238, 245, 0.35));
}
.ts-hero-cycle-num {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--ts-teal);
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}
.ts-hero-cycle-arc {
  font-size: 0.7rem;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-align: right;
  max-width: 9rem;
}

/* ── Cards / grids ──────────────────────────────────────── */
.ts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.65rem;
}
.ts-grid-sm { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
.ts-card {
  text-align: center;
  padding: 0.85rem 0.55rem;
  border-radius: 10px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: var(--ts-surface);
  transition: border-color 0.15s, background 0.15s, transform 0.15s;
  animation: ts-card-in 0.45s ease-out both;
}
.ts-grid > .ts-card:nth-child(1) { animation-delay: 0.04s; }
.ts-grid > .ts-card:nth-child(2) { animation-delay: 0.08s; }
.ts-grid > .ts-card:nth-child(3) { animation-delay: 0.12s; }
.ts-grid > .ts-card:nth-child(4) { animation-delay: 0.16s; }
.ts-grid > .ts-card:nth-child(5) { animation-delay: 0.2s; }
@keyframes ts-card-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.ts-card-quiet .ts-num { font-size: 1.35rem; color: var(--ts-teal); }
.ts-click { cursor: pointer; }
.ts-card.ts-click:hover {
  border-color: rgba(232, 201, 90, 0.4);
  background: rgba(232, 201, 90, 0.06);
  transform: translateY(-2px);
}
.ts-num {
  font-size: 1.75rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--ts-gold);
  line-height: 1.1;
}
.ts-label {
  margin-top: 0.25rem;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.4px;
  text-transform: uppercase;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.ts-arch {
  margin-top: 0.25rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  line-height: 1.3;
}
.ts-kd {
  margin: 0.3rem 0 0;
  font-size: 0.7rem;
  color: var(--accent-red, #ff9080);
  line-height: 1.35;
}

/* ── Plain summary (người thường) ───────────────────────── */
.ts-plain {
  padding: 0.95rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background:
    radial-gradient(ellipse 80% 60% at 0% 0%, rgba(91, 229, 211, 0.07), transparent 55%),
    var(--ts-surface);
}
.ts-plain-intro {
  margin: 0.15rem 0 0.55rem;
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}
.ts-plain-karmic-intro {
  margin: 0 0 0.65rem;
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  border-left: 3px solid var(--accent-red, #ff9080);
  background: rgba(255, 144, 128, 0.07);
  font-size: 0.84rem;
  line-height: 1.45;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}
.ts-plain-list {
  margin: 0;
  padding-left: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.ts-plain-list li {
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text-primary, #e6eef5);
}
.ts-plain-practice {
  margin-top: 0.85rem;
  padding: 0.7rem 0.8rem;
  border-radius: 8px;
  border: 1px solid rgba(91, 229, 211, 0.28);
  background: rgba(91, 229, 211, 0.07);
}
.ts-plain-practice-k {
  display: block;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.55px;
  text-transform: uppercase;
  color: var(--ts-teal);
  margin-bottom: 0.25rem;
}
.ts-plain-practice p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.45;
  color: var(--text-primary, #e6eef5);
}

.ts-karmic-panel { display: flex; flex-direction: column; gap: 0.65rem; }
.ts-karmic-card {
  padding: 0.85rem 0.95rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 144, 128, 0.22);
  background: rgba(255, 144, 128, 0.05);
}
.ts-karmic-head {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 0.45rem;
}
.ts-karmic-num {
  flex-shrink: 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--accent-red, #ff9080);
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
  padding-top: 0.1rem;
}
.ts-karmic-head h4 {
  margin: 0;
  font-size: 0.92rem;
  color: var(--ts-gold-soft);
}
.ts-karmic-plain {
  margin: 0.35rem 0;
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text-primary, #e6eef5);
}
.ts-karmic-practice,
.ts-karmic-avoid {
  margin: 0.4rem 0 0;
  font-size: 0.84rem;
  line-height: 1.45;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}

.ts-glossary {
  padding: 0.85rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--border-accent, rgba(232, 201, 90, 0.35));
  background: rgba(232, 201, 90, 0.07);
}
.ts-glossary h4 {
  margin: 0.25rem 0 0.45rem;
  color: var(--ts-gold-soft);
  font-size: 1rem;
}
.ts-glossary p { margin: 0.3rem 0; font-size: 0.86rem; line-height: 1.45; }
.ts-dd { color: var(--text-secondary, rgba(230, 238, 245, 0.72)); font-style: italic; }

/* ── Cycle pills ────────────────────────────────────────── */
.ts-cycle-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.ts-pill {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: var(--ts-surface);
  min-width: 5.5rem;
}
.ts-pill-wide { flex: 1 1 12rem; }
.ts-pill-k {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.45px;
  text-transform: uppercase;
  color: var(--text-faint, rgba(230, 238, 245, 0.35));
}
.ts-pill-v {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--ts-teal);
  font-variant-numeric: tabular-nums;
  line-height: 1.15;
}
.ts-pill-s {
  font-size: 0.72rem;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}

/* ── READ / GAP / IMPROVE ───────────────────────────────── */
.ts-rgi { display: flex; flex-direction: column; gap: 0.4rem; }
.ts-rgi p {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.5;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}
.ts-rgi-k {
  display: inline-block;
  min-width: 4.2rem;
  margin-right: 0.35rem;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.55px;
  text-transform: uppercase;
  color: var(--ts-gold);
}
.ts-rgi-gap { color: var(--accent-red, #ff9080); }
.ts-rgi-improve { color: var(--ts-teal); }
.ts-synth {
  padding: 0.85rem 0.95rem;
  border-radius: 10px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: var(--ts-surface);
}
.ts-steps {
  margin: 0.5rem 0 0 1.1rem;
  padding: 0;
  font-size: 0.82rem;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.ts-deep-card {
  padding: 0.75rem 0;
  border-top: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
}
.ts-deep-card:first-of-type { border-top: 0; padding-top: 0.25rem; }
.ts-deep-card h4 {
  margin: 0 0 0.4rem;
  font-size: 0.92rem;
  color: var(--ts-gold-soft);
  display: flex;
  align-items: baseline;
  gap: 0.45rem;
}
.ts-deep-val {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--ts-gold);
  font-variant-numeric: tabular-nums;
}

/* ── Folds / tables / cal ───────────────────────────────── */
.ts-fold {
  border-radius: 10px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: var(--ts-surface);
  padding: 0.15rem 0.85rem 0.85rem;
}
.ts-fold > summary {
  cursor: pointer;
  list-style: none;
  padding: 0.7rem 0 0.45rem;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.55px;
  text-transform: uppercase;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}
.ts-fold > summary::-webkit-details-marker { display: none; }
.ts-fold > summary::before {
  content: "▸";
  display: inline-block;
  margin-right: 0.4rem;
  color: var(--ts-gold);
  transition: transform 0.15s;
}
.ts-fold[open] > summary::before { transform: rotate(90deg); }

.ts-tables {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.35rem;
}
.ts-tables table,
.ts-table-full {
  border-collapse: collapse;
  width: auto;
  min-width: 12rem;
}
.ts-table-full { width: 100%; margin-top: 0.4rem; }
.ts-tables th,
.ts-tables td,
.ts-table-full th,
.ts-table-full td,
.ts-compat-result th,
.ts-compat-result td {
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  padding: 0.35rem 0.65rem;
  font-size: 0.82rem;
  text-align: left;
}
.ts-tables th,
.ts-table-full th,
.ts-compat-result th {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-weight: 600;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.ts-td-num {
  font-weight: 700;
  color: var(--ts-teal);
  font-variant-numeric: tabular-nums;
}

.ts-cal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.45rem;
}
.ts-cal-cell {
  text-align: center;
  padding: 0.55rem 0.35rem;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: rgba(0, 0, 0, 0.2);
}
.ts-cal-cell.ts-click:hover {
  border-color: rgba(91, 229, 211, 0.4);
}
.ts-cal-label {
  font-size: 0.68rem;
  color: var(--text-faint, rgba(230, 238, 245, 0.35));
}
.ts-cal-num {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--ts-teal);
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}
.ts-cal-arc {
  font-size: 0.65rem;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  line-height: 1.25;
}
.ts-cal-py {
  margin-top: 0.15rem;
  font-size: 0.62rem;
  color: var(--text-faint, rgba(230, 238, 245, 0.35));
}

.timing-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  max-height: 260px;
  overflow: auto;
  margin-top: 0.35rem;
}
.timing-row {
  padding: 0.4rem 0.55rem;
  border-radius: 6px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: rgba(0, 0, 0, 0.18);
  font-size: 0.82rem;
}
.timing-row small {
  display: block;
  margin-top: 0.15rem;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}

.ts-link {
  background: none;
  border: none;
  padding: 0;
  color: var(--ts-teal);
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
  font: inherit;
  font-size: 0.78rem;
  font-weight: 500;
  text-transform: none;
  letter-spacing: 0;
}
.ts-link:hover { color: var(--ts-gold); }

.ts-meta-row {
  margin: 0.55rem 0;
  font-size: 0.85rem;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}
.ts-meta-row strong { color: var(--ts-gold-soft); margin-right: 0.35rem; }
.ts-letters-meta span { margin-right: 0.85rem; display: inline-block; }
.ts-xref {
  padding: 0.7rem 0.85rem;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  background: var(--ts-surface);
  font-size: 0.86rem;
  line-height: 1.45;
}
.ts-xref strong { color: var(--ts-gold-soft); }
.ts-karmic ul {
  margin: 0.35rem 0 0;
  padding-left: 1.1rem;
  font-size: 0.86rem;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
}
.ts-karmic strong { color: var(--accent-red, #ff9080); }

.ts-inclusion { margin: 0.7rem 0; font-size: 0.86rem; }
.ts-incl-grid { display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.4rem 0; }
.ts-incl-cell {
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
  font-size: 0.78rem;
  background: rgba(91, 229, 211, 0.1);
  color: var(--ts-teal);
  border: 1px solid rgba(91, 229, 211, 0.2);
}
.ts-incl-cell.miss {
  background: rgba(255, 144, 128, 0.08);
  color: var(--accent-red, #ff9080);
  border-color: rgba(255, 144, 128, 0.2);
}
.ts-incl-cell.above { font-weight: 700; background: rgba(91, 229, 211, 0.18); }

.ts-balliett { margin-top: 0.85rem; padding-top: 0.5rem; border-top: 1px solid var(--border-soft); }
.ts-balliett-grid p { margin: 0.35rem 0; font-size: 0.86rem; line-height: 1.45; }
.ts-keynote { color: var(--ts-gold); font-style: normal; font-weight: 700; }

.ts-audit { font-size: 0.84rem; color: var(--text-secondary); }
.ts-audit-warn { color: var(--accent-red, #ff9080); font-weight: 600; }
.ts-audit-parts { margin: 0.35rem 0 0.5rem 1rem; padding: 0; font-size: 0.8rem; }

.ts-letter {
  display: inline-block;
  padding: 0.15rem 0.35rem;
  margin: 0.12rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  font-size: 0.85rem;
  border: 1px solid var(--border-soft);
}
.ts-letter.vowel {
  background: rgba(91, 229, 211, 0.12);
  border-color: rgba(91, 229, 211, 0.25);
  color: var(--ts-teal);
}
.ts-parts { margin-top: 0.55rem; font-size: 0.84rem; color: var(--text-secondary); }

/* ── Compat ─────────────────────────────────────────────── */
.ts-compat-box { margin-top: 1rem; }
.ts-compat-score {
  display: flex;
  align-items: baseline;
  gap: 0.45rem;
  margin: 0.65rem 0;
}
.ts-compat-score strong {
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--ts-teal);
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
.ts-compat-score span {
  font-size: 0.9rem;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}

/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 720px) {
  .ts-form { grid-template-columns: 1fr 1fr; }
  .ts-hero {
    grid-template-columns: auto 1fr;
  }
  .ts-hero-cycle {
    grid-column: 1 / -1;
    flex-direction: row;
    align-items: baseline;
    gap: 0.55rem;
    border-left: 0;
    border-top: 1px solid var(--border-soft);
    padding: 0.55rem 0 0;
    min-width: 0;
  }
  .ts-hero-cycle-arc { text-align: left; max-width: none; }
}
@media (max-width: 480px) {
  .ts-form { grid-template-columns: 1fr; }
  .ts-brand { font-size: 1.85rem; }
}
</style>
