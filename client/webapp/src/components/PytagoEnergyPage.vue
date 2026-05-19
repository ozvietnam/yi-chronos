<script setup>
import { computed, ref, watch } from "vue";

const props = defineProps({
  lucHaoResult: {
    type: Object,
    default: null
  },
  lucHaoMeta: {
    type: Object,
    default: null
  },
  universeProfile: {
    type: Object,
    default: null
  }
});

const profile = ref({
  fullName: "",
  birthDate: "",
  birthTime: "",
  question: "",
  accountId: "",
  profileVerified: false,
  dataConfirmed: false
});

const VOWELS = new Set(["A", "E", "I", "O", "U"]);

function sumDigits(value) {
  return String(value).split("").reduce((total, char) => total + Number(char), 0);
}

function reduceCoreNumber(number) {
  let n = number;
  while (n > 9 && n !== 11 && n !== 22 && n !== 33) {
    n = sumDigits(n);
  }
  return n;
}

/** Latin hóa tên Việt (đ→d + bỏ dấu) rồi chỉ giữ [A-Za-z] cho chỉ số Pythagoras. */
function toLettersForPythagoras(text) {
  if (!text || typeof text !== "string" || !text.trim()) return "";
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\u0110/gi, "d")
    .replace(/\u0111/g, "d")
    .replace(/[^a-zA-Z]/g, "")
    .toUpperCase();
}

function letterValue(char) {
  const code = char.charCodeAt(0) - 64;
  return ((code - 1) % 9) + 1;
}

function yIsVowel(chars, index) {
  const prev = chars[index - 1];
  const next = chars[index + 1];
  const prevIsVowel = prev ? VOWELS.has(prev) : false;
  const nextIsVowel = next ? VOWELS.has(next) : false;
  return !prevIsVowel && !nextIsVowel;
}

function normalizeBirthDate(dateStr) {
  if (!dateStr) return null;
  const date = new Date(`${dateStr}T00:00:00`);
  if (Number.isNaN(date.getTime())) return null;
  return {
    day: date.getDate(),
    month: date.getMonth() + 1,
    year: date.getFullYear()
  };
}

const nameMetrics = computed(() => {
  const normalized = toLettersForPythagoras(profile.value.fullName);
  if (!normalized) {
    return {
      normalized: "",
      expression: null,
      soulUrge: null,
      personality: null
    };
  }

  const chars = normalized.split("");
  let expressionSum = 0;
  let soulUrgeSum = 0;
  let personalitySum = 0;

  chars.forEach((char, idx) => {
    const val = letterValue(char);
    expressionSum += val;
    const isVowel = char === "Y" ? yIsVowel(chars, idx) : VOWELS.has(char);
    if (isVowel) {
      soulUrgeSum += val;
    } else {
      personalitySum += val;
    }
  });

  return {
    normalized,
    expression: reduceCoreNumber(expressionSum),
    soulUrge: reduceCoreNumber(soulUrgeSum),
    personality: reduceCoreNumber(personalitySum)
  };
});

const lifePathNumber = computed(() => {
  const birth = normalizeBirthDate(profile.value.birthDate);
  if (!birth) return null;
  const day = reduceCoreNumber(birth.day);
  const month = reduceCoreNumber(birth.month);
  const year = reduceCoreNumber(birth.year);
  return reduceCoreNumber(day + month + year);
});

const maturityNumber = computed(() => {
  if (!lifePathNumber.value || !nameMetrics.value.expression) return null;
  return reduceCoreNumber(lifePathNumber.value + nameMetrics.value.expression);
});

const personalCycle = computed(() => {
  const birth = normalizeBirthDate(profile.value.birthDate);
  if (!birth) return { year: null, month: null, day: null };
  const now = new Date();
  const personalYear = reduceCoreNumber(reduceCoreNumber(birth.day) + reduceCoreNumber(birth.month) + reduceCoreNumber(now.getFullYear()));
  const personalMonth = reduceCoreNumber(personalYear + (now.getMonth() + 1));
  const personalDay = reduceCoreNumber(personalMonth + now.getDate());
  return { year: personalYear, month: personalMonth, day: personalDay };
});

function harmonicDistance(a, b) {
  if (!a || !b) return 4;
  const diff = Math.abs(a - b);
  return Math.min(diff, 9 - diff);
}

const alignmentScore = computed(() => {
  const lp = lifePathNumber.value;
  const ex = nameMetrics.value.expression;
  const su = nameMetrics.value.soulUrge;
  const pd = personalCycle.value.day;
  const py = personalCycle.value.year;
  if (!lp || !ex || !su || !pd || !py) return null;

  const resonance = 100
    - harmonicDistance(pd, lp) * 9
    - harmonicDistance(pd, ex) * 6
    - harmonicDistance(pd, su) * 5
    - harmonicDistance(pd, py) * 7;

  return Math.max(0, Math.min(100, Math.round(resonance)));
});

const energyBand = computed(() => {
  const score = alignmentScore.value;
  if (score === null) return null;
  if (score <= 39) return "Band 1 - Phòng thủ năng lượng";
  if (score <= 69) return "Band 2 - Cân bằng và tối ưu";
  return "Band 3 - Tăng tốc có kiểm soát";
});

const vibrationInsight = computed(() => {
  if (!energyBand.value) return "Cần đủ tên + ngày sinh để mở phân tích trường năng lượng.";
  if (energyBand.value.startsWith("Band 1")) {
    return "Trường rung động đang co cụm để tự bảo toàn. Ưu tiên việc nền, tránh quyết định all-in.";
  }
  if (energyBand.value.startsWith("Band 2")) {
    return "Trường rung động ổn định, phù hợp tối ưu hệ thống và chốt các việc quan trọng tầm trung.";
  }
  return "Trường rung động mở và chủ động. Có thể đẩy nhanh tiến độ, nhưng phải giữ kỷ luật chống quá tải.";
});

const actionChecklist = computed(() => {
  const score = alignmentScore.value;
  if (score === null) return [];
  if (score <= 39) {
    return ["Giữ nhịp thấp 1-2 ngày, chốt việc nền", "Không ra quyết định rủi ro cao", "Làm sạch backlog và ngủ đủ để hồi năng lượng"];
  }
  if (score <= 69) {
    return ["Chốt 1 việc chiến lược + 2 việc vận hành", "Đặt KPI trong ngày và review cuối ngày", "Tận dụng giao tiếp rõ ràng để giảm nhiễu"];
  }
  return ["Đẩy việc trọng điểm trong 24h", "Tăng tốc nhưng chia tải cho đội", "Khóa thời gian nghỉ để tránh tụt năng lượng sau đỉnh"];
});

function calcPersonalYear(birth, date) {
  return reduceCoreNumber(reduceCoreNumber(birth.day) + reduceCoreNumber(birth.month) + reduceCoreNumber(date.getFullYear()));
}

function calcPersonalMonth(personalYear, date) {
  return reduceCoreNumber(personalYear + (date.getMonth() + 1));
}

function calcPersonalDay(personalMonth, date) {
  return reduceCoreNumber(personalMonth + date.getDate());
}

function calcDailyAlignment(pd, py, lp, ex, su) {
  const resonance = 100
    - harmonicDistance(pd, lp) * 9
    - harmonicDistance(pd, ex) * 6
    - harmonicDistance(pd, su) * 5
    - harmonicDistance(pd, py) * 7;
  return Math.max(0, Math.min(100, Math.round(resonance)));
}

function scoreBand(score) {
  if (score <= 39) return "Band 1";
  if (score <= 69) return "Band 2";
  return "Band 3";
}

const compareWindows = [7, 14, 21];

const forecastRows = computed(() => {
  const birth = normalizeBirthDate(profile.value.birthDate);
  const lp = lifePathNumber.value;
  const ex = nameMetrics.value.expression;
  const su = nameMetrics.value.soulUrge;
  if (!birth || !lp || !ex || !su) return [];

  const rows = [];
  const start = new Date();
  for (let offset = 0; offset <= 21; offset += 1) {
    const date = new Date(start);
    date.setDate(start.getDate() + offset);
    const py = calcPersonalYear(birth, date);
    const pm = calcPersonalMonth(py, date);
    const pd = calcPersonalDay(pm, date);
    const score = calcDailyAlignment(pd, py, lp, ex, su);
    rows.push({
      offset,
      label: date.toLocaleDateString("vi-VN"),
      pd,
      pm,
      py,
      score,
      band: scoreBand(score)
    });
  }
  return rows;
});

const forecastSummary = computed(() => {
  if (!forecastRows.value.length) return [];
  return compareWindows.map((windowSize) => {
    const subset = forecastRows.value.slice(0, windowSize + 1);
    const best = subset.reduce((max, row) => (row.score > max.score ? row : max), subset[0]);
    const avg = Math.round(subset.reduce((sum, row) => sum + row.score, 0) / subset.length);
    return {
      windowSize,
      avg,
      best
    };
  });
});

const lucHaoTimingCandidates = computed(() => {
  const timing = props.lucHaoResult?.timing_prediction;
  if (!timing) return [];
  const candidates = timing.candidates || [];
  if (!candidates.length && timing.best_match?.offset_days !== undefined) {
    return [
      {
        offset: Number(timing.best_match.offset_days),
        reason: timing.best_match.reason || "Mốc ưu tiên từ ứng kỳ",
        label: timing.best_match.branch ? `Ngày ${timing.best_match.branch}` : "Mốc ưu tiên"
      }
    ];
  }
  return candidates.map((item) => ({
    offset: Number(item.offset_days),
    reason: item.reason,
    label: item.branch ? `Ngày ${item.branch}` : "Mốc công thức"
  }));
});

function detectDomain(text) {
  const source = (text || "").toLowerCase();
  if (!source) return "general";
  if (/(tiền|tài chính|đầu tư|thu nhập|doanh thu|chi phí|nợ)/.test(source)) return "finance";
  if (/(công việc|sự nghiệp|dự án|thăng chức|kinh doanh|khách hàng)/.test(source)) return "work";
  if (/(tình cảm|hôn nhân|yêu|gia đình|vợ|chồng|con cái)/.test(source)) return "relationship";
  if (/(sức khỏe|bệnh|điều trị|tâm lý|mệt|ngủ)/.test(source)) return "health";
  return "general";
}

const effectiveDomain = computed(() => {
  const localDomain = detectDomain(profile.value.question);
  if (localDomain !== "general") return localDomain;
  return detectDomain(props.lucHaoResult?.question_text || "");
});

const domainWeightPreset = {
  finance: { pytago: 0.52, lucHao: 0.48, rankPenalty: 10 },
  work: { pytago: 0.5, lucHao: 0.5, rankPenalty: 9 },
  relationship: { pytago: 0.58, lucHao: 0.42, rankPenalty: 11 },
  health: { pytago: 0.62, lucHao: 0.38, rankPenalty: 12 },
  general: { pytago: 0.55, lucHao: 0.45, rankPenalty: 10 }
};

const syncedQuestionText = computed(() => {
  const fromProfile = profile.value.question.trim();
  if (fromProfile) return fromProfile;
  const m = props.lucHaoMeta?.question_text;
  const r = props.lucHaoResult?.question_text;
  const s = typeof m === "string" ? m.trim() : "";
  const t = typeof r === "string" ? r.trim() : "";
  return s || t;
});

const profileReadiness = computed(() => {
  const hasCore = Boolean(profile.value.fullName.trim() && profile.value.birthDate);
  const hub = props.universeProfile != null;
  const hasAdvanced = Boolean(
    hasCore &&
      syncedQuestionText.value &&
      (hub ||
        (profile.value.birthTime &&
          profile.value.accountId.trim() &&
          profile.value.profileVerified &&
          profile.value.dataConfirmed))
  );
  return {
    hasCore,
    hasAdvanced
  };
});

function applyUniverseProfileSync() {
  const p = props.universeProfile;
  if (!p) return;
  if (p.label != null && String(p.label).trim()) profile.value.fullName = String(p.label).trim();
  const iso = p.birth_datetime_local;
  if (iso && typeof iso === "string") {
    const dPart = iso.split("T")[0];
    if (dPart) profile.value.birthDate = dPart;
    const tm = iso.match(/T(\d{2}:\d{2})/);
    if (tm) profile.value.birthTime = tm[1];
  }
  if (p.id != null) {
    profile.value.accountId = `local-${String(p.id)}`;
    profile.value.profileVerified = true;
    profile.value.dataConfirmed = true;
  }
}

function applyLucQuestionSync() {
  const qRaw =
    (typeof props.lucHaoMeta?.question_text === "string" && props.lucHaoMeta.question_text.trim()) ||
    (typeof props.lucHaoResult?.question_text === "string" && props.lucHaoResult.question_text.trim()) ||
    "";
  if (!qRaw) return;
  if (!profile.value.question.trim()) profile.value.question = qRaw;
}

watch(
  () => props.universeProfile,
  () => applyUniverseProfileSync(),
  { deep: true, immediate: true }
);

watch(
  () => [props.lucHaoMeta, props.lucHaoResult],
  () => applyLucQuestionSync(),
  { deep: true, immediate: true }
);

const timingConsensusV2 = computed(() => {
  if (!forecastRows.value.length || !lucHaoTimingCandidates.value.length || !profileReadiness.value.hasCore) return [];
  const preset = domainWeightPreset[effectiveDomain.value] || domainWeightPreset.general;
  const mode = profileReadiness.value.hasAdvanced ? "advanced" : "safe";

  return lucHaoTimingCandidates.value
    .map((candidate, idx) => {
      const row = forecastRows.value.find((item) => item.offset === candidate.offset);
      if (!row) return null;
      const lucHaoPriority = Math.max(30, 100 - idx * preset.rankPenalty);
      const safeScore = Math.round(row.score * 0.6 + lucHaoPriority * 0.4);
      const advancedScore = Math.round(row.score * preset.pytago + lucHaoPriority * preset.lucHao);
      const consensusScore = mode === "advanced" ? advancedScore : safeScore;
      return {
        ...candidate,
        row,
        consensusScore,
        mode,
        consensusTag: consensusScore >= 75 ? "Đồng thuận mạnh" : consensusScore >= 55 ? "Đồng thuận vừa" : "Cần xác minh thêm"
      };
    })
    .filter(Boolean)
    .sort((a, b) => b.consensusScore - a.consensusScore);
});

const consensusByOffset = computed(() => {
  const map = new Map();
  timingConsensusV2.value.forEach((item) => {
    map.set(item.offset, item);
  });
  return map;
});

function consensusClass(score) {
  if (score >= 75) return "consensus-high";
  if (score >= 55) return "consensus-mid";
  return "consensus-low";
}

function forecastConsensusClass(offset) {
  const item = consensusByOffset.value.get(offset);
  if (!item) return "";
  return consensusClass(item.consensusScore);
}
</script>

<template>
  <section class="panel" aria-label="Trường phái Pytago">
    <div class="panel-title">
      <div>
        <h3>Pytago · Số học & Trường năng lượng</h3>
        <small>Tab chuyên biệt cho số học cá nhân và định hướng năng lượng hành động.</small>
      </div>
    </div>

    <div class="feedback-grid">
      <label>
        Họ tên
        <input v-model="profile.fullName" type="text" placeholder="Nhập họ tên đầy đủ" />
      </label>
      <label>
        Ngày sinh
        <input v-model="profile.birthDate" type="date" />
      </label>
      <label class="full">
        Câu hỏi trọng tâm
        <textarea v-model="profile.question" rows="2" placeholder="Bạn đang cần quyết định điều gì?" />
      </label>
      <label>
        Giờ sinh (tuỳ chọn)
        <input v-model="profile.birthTime" type="time" />
      </label>
      <label>
        Mã tài khoản
        <input v-model="profile.accountId" type="text" placeholder="Ví dụ: KH-2026-001" />
      </label>
      <label class="full inline-check">
        <input v-model="profile.profileVerified" type="checkbox" />
        Tôi đã tạo profile đầy đủ và xác minh thông tin cá nhân.
      </label>
      <label class="full inline-check">
        <input v-model="profile.dataConfirmed" type="checkbox" />
        Tôi xác nhận dữ liệu nhập đã kiểm tra cẩn thận trước khi đối chiếu ứng kỳ.
      </label>
    </div>

    <div class="result-grid" style="margin-top: 12px">
      <article>
        <span>Số đường đời</span>
        <strong>{{ lifePathNumber ?? "—" }}</strong>
      </article>
      <article>
        <span>Số biểu đạt (Expression)</span>
        <strong>{{ nameMetrics.expression ?? "—" }}</strong>
      </article>
      <article>
        <span>Số linh hồn (Soul Urge)</span>
        <strong>{{ nameMetrics.soulUrge ?? "—" }}</strong>
      </article>
      <article>
        <span>Số nhân cách (Personality)</span>
        <strong>{{ nameMetrics.personality ?? "—" }}</strong>
      </article>
      <article>
        <span>Số trưởng thành (Maturity)</span>
        <strong>{{ maturityNumber ?? "—" }}</strong>
      </article>
      <article style="grid-column: 1 / -1">
        <span>Chu kỳ cá nhân hôm nay (Năm/Tháng/Ngày)</span>
        <strong>
          {{ personalCycle.year ?? "—" }} / {{ personalCycle.month ?? "—" }} / {{ personalCycle.day ?? "—" }}
        </strong>
      </article>
      <article style="grid-column: 1 / -1">
        <span>Điểm đồng pha năng lượng trong ngày</span>
        <strong>{{ alignmentScore ?? "Nhập dữ liệu để tính." }}</strong>
      </article>
      <article style="grid-column: 1 / -1">
        <span>Band năng lượng hiện tại</span>
        <strong>{{ energyBand ?? "Nhập dữ liệu để tính trường năng lượng." }}</strong>
      </article>
    </div>

    <div class="analysis-block">
      <h4>Giải nghĩa trường năng lượng & tần số rung động</h4>
      <p>{{ vibrationInsight }}</p>
    </div>

    <div class="analysis-block">
      <h4>Gợi ý vận hành năng lượng</h4>
      <ul>
        <li v-for="(item, index) in actionChecklist" :key="`action-${index}`">{{ item }}</li>
      </ul>
    </div>

    <div class="analysis-block">
      <h4>So sánh ứng kỳ theo cửa sổ 7 / 14 / 21 ngày</h4>
      <div class="timing-candidate-list" v-if="forecastSummary.length">
        <div class="timing-row" v-for="item in forecastSummary" :key="`window-${item.windowSize}`">
          <strong>{{ item.windowSize }} ngày</strong>
          <small>
            Điểm trung bình: {{ item.avg }} ·
            Đỉnh nhịp: D+{{ item.best.offset }} ({{ item.best.label }}) ·
            Score {{ item.best.score }} · {{ item.best.band }} · PD {{ item.best.pd }}
          </small>
        </div>
      </div>
      <p v-else>Nhập đủ dữ liệu để mở bảng so sánh ứng kỳ.</p>
    </div>

    <div class="analysis-block">
      <h4>Tự so khớp với Ứng kỳ Lục Hào (Trang 2)</h4>
      <p>
        Domain hiện tại: <strong>{{ effectiveDomain }}</strong> ·
        Chế độ: <strong>{{ profileReadiness.hasAdvanced ? "Advanced V2" : "Safe V2 (giới hạn)" }}</strong>
      </p>
      <p v-if="!profileReadiness.hasAdvanced">
        Để mở full Advanced V2, khách hàng cần: nhập giờ sinh + câu hỏi rõ + mã tài khoản, đồng thời xác nhận profile và dữ liệu.
      </p>
      <div class="consensus-legend">
        <span class="legend-pill consensus-high">Đồng thuận mạnh</span>
        <span class="legend-pill consensus-mid">Đồng thuận vừa</span>
        <span class="legend-pill consensus-low">Cần xác minh</span>
      </div>
      <div class="timing-candidate-list" v-if="timingConsensusV2.length">
        <div
          class="timing-row"
          :class="consensusClass(item.consensusScore)"
          v-for="(item, idx) in timingConsensusV2"
          :key="`consensus-${idx}`"
        >
          <strong>
            D+{{ item.offset }} · {{ item.row.label }} · {{ item.consensusTag }}
          </strong>
          <small>
            Score đồng thuận: {{ item.consensusScore }} ·
            Pytago {{ item.row.score }} ({{ item.row.band }}) ·
            Lục Hào: {{ item.label }} - {{ item.reason }}
          </small>
        </div>
      </div>
      <p v-else>
        Chưa có dữ liệu ứng kỳ từ trang 2. Gieo quẻ Lục Hào trước để hệ tự đối chiếu.
      </p>
    </div>

    <div class="analysis-block">
      <h4>Lịch năng lượng 21 ngày (đối chiếu trang 2)</h4>
      <div class="timing-candidate-list" v-if="forecastRows.length">
        <div
          class="timing-row"
          :class="forecastConsensusClass(row.offset)"
          v-for="row in forecastRows"
          :key="`forecast-${row.offset}`"
        >
          <strong>D+{{ row.offset }} · {{ row.label }}</strong>
          <small>
            Score {{ row.score }} ({{ row.band }}) ·
            PY/PM/PD: {{ row.py }}/{{ row.pm }}/{{ row.pd }}
            <template v-if="consensusByOffset.get(row.offset)">
              · Đồng thuận: {{ consensusByOffset.get(row.offset).consensusScore }}
            </template>
          </small>
        </div>
      </div>
      <p v-else>Nhập đủ tên + ngày sinh để hiển thị lịch.</p>
    </div>
  </section>
</template>

<style scoped>
.consensus-legend {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.legend-pill {
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid transparent;
}

.timing-row.consensus-high,
.legend-pill.consensus-high {
  background: #dcfce7;
  border-color: #86efac;
  color: #166534;
}

.timing-row.consensus-mid,
.legend-pill.consensus-mid {
  background: #fef9c3;
  border-color: #fde047;
  color: #854d0e;
}

.timing-row.consensus-low,
.legend-pill.consensus-low {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #991b1b;
}

.inline-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.inline-check input[type="checkbox"] {
  width: auto;
}
</style>
