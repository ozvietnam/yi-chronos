<script setup>
/**
 * 🗓️ Vận hạn GROUNDED — Đại Vận / Lưu Niên (năm) / Lưu Nguyệt (tháng) / Tuần (10 ngày).
 *
 * Anh giao 2026-07-14: "vận hạn theo tuần/tháng, làm kỹ, dùng sách/thư viện/công thức".
 * Đọc theo cổ pháp THỂ-DỤNG + Tứ Hóa rọi cung (paradigm đồng dạng, KHÔNG predict).
 * Nội dung sao CHỈ từ kho đã DUYỆT (founder_verified=1); thiếu nguồn → nói rõ, không bịa.
 * Endpoint: POST /api/tu-vi/van-han (block tất định + luận LLM biên-tập-từ-nguồn).
 */
import { computed, ref, watch } from "vue";
import { tuviPersonBirth, tuviPersonGender, tuviPersonName } from "../stores/tuviPersonStore.js";

// Ngày sinh: ưu tiên props (chart VỪA AN SAO ở panel cha) → fallback store (người đang chọn).
// Bảo đảm "nhập ngày sinh → an sao → vận hạn" luôn khớp đúng lá số user vừa lập, không lệ thuộc
// đồng bộ giữa authStore.currentPerson và userDataStore.activePerson.
const props = defineProps({
  birthDatetimeLocal: { type: String, default: "" },
  gender: { type: String, default: "" },
});
const birthVal = computed(() => props.birthDatetimeLocal || tuviPersonBirth.value);
const genderVal = computed(() => props.gender || tuviPersonGender.value || "nam");

const open = ref(false);
const tang = ref("luu_nguyet");   // default tháng — đúng trọng tâm Anh cần
const year = ref(2026);
const month = ref(1);
const tuan = ref(1);
const day = ref(1);
const cycle = ref(1);

const block = ref(null);
const luan = ref("");
const loading = ref(false);
const luanLoading = ref(false);
const error = ref("");
const monthsOverview = ref([]);   // 12 tháng skeleton (khi xem lưu nguyệt)
const leapNote = ref("");

// 🎢 Bức tranh cuộc đời thăng trầm — đường cong KHÍ động↔tĩnh (tất định)
const arc = ref(null);
const arcLoading = ref(false);
const arcBuoc = ref("dai_van");   // "dai_van" (cả đời theo tuổi) | "thang" | "nam"
const arcTuNam = ref(2026);
const arcDenNam = ref(2030);
const arcSel = ref(null);         // mốc đang rê chuột (hiện dòng "đọc")

const TANG_TABS = [
  { key: "life_arc", label: "🎢 Bức tranh", sub: "thăng trầm" },
  { key: "dai_van", label: "Đại Vận", sub: "10 năm" },
  { key: "luu_nien", label: "Lưu Niên", sub: "năm" },
  { key: "luu_nguyet", label: "Lưu Nguyệt", sub: "tháng" },
  { key: "tuan", label: "Tuần", sub: "10 ngày" },
  { key: "luu_nhat", label: "Lưu Nhật", sub: "ngày" },
];
const HANH_HUE = { "DÙNG": "#5ab07a", "TĨNH": "#7ec8e3", "CẨN": "#d6a05a" };
const TUAN_LABEL = { 1: "Thượng tuần", 2: "Trung tuần", 3: "Hạ tuần" };
const HOA_COLOR = { "Lộc": "loc", "Quyền": "quyen", "Khoa": "khoa", "Kỵ": "ky" };

const litHoa = computed(() =>
  (block.value?.tu_hoa_van || []).filter((h) => !h.cung.startsWith("(")),
);

function body() {
  const b = {
    birth_datetime_local: birthVal.value,
    gender: genderVal.value,
    tang: tang.value,
    want_llm: false,
  };
  if (tang.value === "dai_van") b.cycle_index = cycle.value;
  if (["luu_nien", "luu_nguyet", "tuan", "luu_nhat"].includes(tang.value)) b.year = year.value;
  if (["luu_nguyet", "tuan", "luu_nhat"].includes(tang.value)) b.month = month.value;
  if (tang.value === "tuan") b.tuan = tuan.value;
  if (tang.value === "luu_nhat") b.day = day.value;
  return b;
}

// ── 🎢 Bức tranh cuộc đời — nạp đường cong KHÍ (tất định, 0-LLM) ──────────────
async function loadArc() {
  if (!birthVal.value) { error.value = "Chưa có ngày giờ sinh — an sao lá số trước đã."; return; }
  arcLoading.value = true; error.value = ""; arc.value = null; arcSel.value = null;
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
      body: JSON.stringify({
        birth_datetime_local: birthVal.value,
        gender: genderVal.value,
        tang: "life_arc", buoc: arcBuoc.value,
        tu_nam: arcTuNam.value, den_nam: arcDenNam.value,
      }),
    });
    const d = await resp.json();
    if (d.status !== "ok") throw new Error(d.reason || d.status || "lỗi");
    arc.value = d;
  } catch (e) {
    error.value = "Không vẽ được bức tranh: " + (e?.message || e);
  } finally { arcLoading.value = false; }
}

// Hình học đường cong: khí ∈ [-1,1] → y quanh đường giữa (động phía trên, tĩnh phía dưới).
const arcGeom = computed(() => {
  const pts = arc.value?.diem;
  if (!pts?.length) return null;
  const step = arcBuoc.value === "dai_van" ? 48 : arcBuoc.value === "nam" ? 34 : 15;
  const padX = 34, midY = 82, amp = 62, h = arcBuoc.value === "dai_van" ? 182 : 164;
  const w = padX * 2 + Math.max(1, pts.length - 1) * step;
  const coords = pts.map((p, i) => ({
    p, x: padX + i * step, y: +(midY - p.khi * amp).toFixed(1),
  }));
  const line = coords.map((c, i) => (i ? "L" : "M") + c.x + " " + c.y).join(" ");
  const area = "M" + coords[0].x + " " + midY + " " +
    coords.map((c) => "L" + c.x + " " + c.y).join(" ") +
    " L" + coords[coords.length - 1].x + " " + midY + " Z";
  return { coords, line, area, w, h, midY, padX };
});

// Click 1 mốc trên bức tranh → nhảy sang tầng chi tiết (tháng/năm) để LUẬN đầy đủ.
function pickArcPoint(p) {
  if (arcBuoc.value === "dai_van") { cycle.value = p.cycle_index; tang.value = "dai_van"; }
  else if (arcBuoc.value === "nam") { year.value = p.year; tang.value = "luu_nien"; }
  else { year.value = p.year; month.value = p.month; tang.value = "luu_nguyet"; }
}

async function loadBlock() {
  if (tang.value === "life_arc") { if (!arc.value) await loadArc(); return; }
  if (!birthVal.value) { error.value = "Chưa có ngày giờ sinh — an sao lá số trước đã."; return; }
  loading.value = true; error.value = ""; luan.value = "";
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" },
      credentials: "include", body: JSON.stringify(body()),
    });
    const d = await resp.json();
    if (d.status !== "ok") throw new Error(d.reason || d.status || "lỗi");
    block.value = d.block;
  } catch (e) {
    error.value = "Không tải được vận hạn: " + (e?.message || e);
    block.value = null;
  } finally { loading.value = false; }
}

async function genLuan() {
  luanLoading.value = true; luan.value = "";
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" },
      credentials: "include", body: JSON.stringify({ ...body(), want_llm: true }),
    });
    const d = await resp.json();
    if (d.status !== "ok") throw new Error(d.reason || "lỗi");
    luan.value = d.luan || "(kho sách chưa đủ nguồn để luận tầng này — không suy đoán bừa)";
  } catch (e) {
    luan.value = "Không sinh được luận: " + (e?.message || e);
  } finally { luanLoading.value = false; }
}

async function loadMonthsOverview() {
  monthsOverview.value = []; leapNote.value = "";
  if (tang.value !== "luu_nguyet" || !birthVal.value) return;
  try {
    const resp = await fetch("/api/tu-vi/van-han", {
      method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
      body: JSON.stringify({ ...body(), tang: "luu_nguyet_overview", year: year.value }),
    });
    const d = await resp.json();
    if (d.status === "ok") { monthsOverview.value = d.months || []; leapNote.value = d.thang_nhuan_note || ""; }
  } catch (e) { /* im lặng — strip là phụ trợ */ }
}

watch([tang, year, month, tuan, day, cycle], () => { if (open.value) loadBlock(); });
watch([tang, year], () => { if (open.value) loadMonthsOverview(); });
watch([arcBuoc, arcTuNam, arcDenNam], () => { if (open.value && tang.value === "life_arc") loadArc(); });

function today() {
  const d = new Date();
  year.value = d.getFullYear();
  month.value = d.getMonth() + 1;
  day.value = d.getDate();
  // tuần theo ngày dương (thô — tầng tuần là vi mô)
  tuan.value = d.getDate() <= 10 ? 1 : d.getDate() <= 20 ? 2 : 3;
}

async function toggle() {
  open.value = !open.value;
  if (open.value && !block.value) { await loadBlock(); await loadMonthsOverview(); }
}
</script>

<template>
  <section class="vh-block">
    <button type="button" class="vh-toggle" @click="toggle">
      <span>🗓️ Vận hạn — Đại Vận · Lưu Niên · Lưu Nguyệt · Tuần (đọc Thể-Dụng, có nguồn)</span>
      <small>{{ open ? "thu gọn ▲" : "mở ra ▼" }}</small>
    </button>

    <div v-if="open" class="vh-body">
      <!-- Chọn tầng -->
      <nav class="vh-tangs">
        <button v-for="t in TANG_TABS" :key="t.key" type="button"
          class="vh-tang" :class="{ active: tang === t.key }" @click="tang = t.key">
          {{ t.label }}<small>{{ t.sub }}</small>
        </button>
      </nav>

      <!-- Bộ chọn thời điểm theo tầng -->
      <div class="vh-picker">
        <template v-if="tang === 'life_arc'">
          <label>Bước
            <select v-model="arcBuoc">
              <option value="dai_van">Cả đời theo tuổi (Đại vận)</option>
              <option value="thang">Theo tháng (mạch thở)</option>
              <option value="nam">Theo năm (khái quát)</option>
            </select>
          </label>
          <template v-if="arcBuoc !== 'dai_van'">
            <label>Từ năm <input type="number" v-model.number="arcTuNam" min="1930" max="2100" /></label>
            <label>Đến năm <input type="number" v-model.number="arcDenNam" min="1930" max="2100" /></label>
          </template>
        </template>
        <template v-else-if="tang === 'dai_van'">
          <label>Vận số <input type="number" v-model.number="cycle" min="1" max="12" /></label>
        </template>
        <template v-else>
          <label>Năm <small>(dương)</small>
            <input type="number" v-model.number="year" min="1930" max="2100" /></label>
          <label v-if="['luu_nguyet','tuan','luu_nhat'].includes(tang)">Tháng <small>(dương)</small>
            <input type="number" v-model.number="month" min="1" max="12" /></label>
          <label v-if="tang === 'luu_nhat'">Ngày <small>(dương)</small>
            <input type="number" v-model.number="day" min="1" max="31" /></label>
          <label v-if="tang === 'tuan'">Tuần
            <select v-model.number="tuan">
              <option :value="1">Thượng tuần (1-10)</option>
              <option :value="2">Trung tuần (11-20)</option>
              <option :value="3">Hạ tuần (21-cuối)</option>
            </select>
          </label>
          <button v-if="tang !== 'luu_nien'" type="button" class="vh-today" @click="today">📅 Hôm nay</button>
        </template>
      </div>

      <!-- Overview 12 tháng (nhịp cả năm — chọn tháng) -->
      <div v-if="tang === 'luu_nguyet' && monthsOverview.length" class="vh-monthstrip">
        <button v-for="mo in monthsOverview" :key="mo.month" type="button"
          class="vh-mo" :class="{ active: month === mo.month }" @click="month = mo.month"
          :title="`Dương T${mo.month} ≈ âm tháng ${mo.am_thang} — cung ${mo.cung_the}`">
          <b>T{{ mo.month }}</b><small>â.{{ mo.am_thang }} · {{ mo.cung_the }}</small>
        </button>
      </div>
      <p v-if="leapNote" class="vh-leapnote">🌙 {{ leapNote }}</p>

      <!-- 🎢 BỨC TRANH CUỘC ĐỜI THĂNG TRẦM — đường cong KHÍ động↔tĩnh -->
      <div v-if="tang === 'life_arc'" class="vh-arc">
        <p v-if="arcLoading" class="vh-note">Đang vẽ bức tranh khí…</p>
        <p v-else-if="error" class="vh-error">{{ error }}</p>
        <template v-else-if="arc && arcGeom">
          <!-- Nền bẩm sinh foreground (soil-before-seed) -->
          <div v-if="arc.nen_menh" class="vh-nen">
            🌱 <b>Nền bẩm sinh</b> (không đổi cả đời): Mệnh chủ <b>{{ arc.nen_menh.menh_chu }}</b> ·
            Thân chủ <b>{{ arc.nen_menh.than_chu }}</b> ·
            <b>{{ arc.nen_menh.cuc?.cuc_name }}</b><span v-if="arc.nen_menh.cuc?.element"> (hành nền {{ arc.nen_menh.cuc.element }})</span> ·
            Thân cư {{ arc.nen_menh.than_cung }}<span v-if="arc.nen_menh.menh_than_dong_cung"> (Mệnh-Thân đồng cung)</span>.
            <small>Mọi tầng vận hạn VẬN HÀNH trên nền này (mệnh là động từ, không phải số định sẵn).</small>
          </div>

          <p class="vh-arc-axis-note">↕ {{ arc.truc_note }}</p>

          <!-- Đường cong -->
          <div class="vh-arc-scroll">
            <svg class="vh-arc-svg" :viewBox="`0 0 ${arcGeom.w} ${arcGeom.h}`" :width="arcGeom.w" :height="arcGeom.h">
              <!-- vùng động (trên) / tĩnh (dưới) -->
              <text :x="6" :y="18" class="vh-arc-zone">ĐỘNG ↑</text>
              <text :x="6" :y="arcGeom.h - 8" class="vh-arc-zone">TĨNH ↓</text>
              <line :x1="arcGeom.padX" :y1="arcGeom.midY" :x2="arcGeom.w - 6" :y2="arcGeom.midY" class="vh-arc-mid" />
              <path :d="arcGeom.area" class="vh-arc-area" />
              <path :d="arcGeom.line" class="vh-arc-line" />
              <g v-for="(c, i) in arcGeom.coords" :key="i">
                <circle :cx="c.x" :cy="c.y" :r="c.p.diem_quay ? 5 : 3.5"
                  :fill="HANH_HUE[c.p.duong_hanh]"
                  :class="['vh-arc-dot', { quay: c.p.diem_quay }]"
                  @mouseenter="arcSel = c.p" @click="pickArcPoint(c.p)">
                  <title>{{ c.p.label }} — {{ c.p.doc }}</title>
                </circle>
                <!-- nhãn tuổi (chỉ Đại vận cả đời) -->
                <text v-if="arcBuoc === 'dai_van'" :x="c.x" :y="arcGeom.h - 4"
                  class="vh-arc-tick">{{ c.p.label }}</text>
              </g>
            </svg>
          </div>

          <!-- Chú giải đường hành -->
          <div class="vh-arc-legend">
            <span><i class="vh-lg" :style="{background: HANH_HUE['DÙNG']}"></i>DÙNG (khí mở)</span>
            <span><i class="vh-lg" :style="{background: HANH_HUE['TĨNH']}"></i>TĨNH (khí thu)</span>
            <span><i class="vh-lg" :style="{background: HANH_HUE['CẨN']}"></i>CẨN (điểm quay)</span>
            <span class="vh-arc-hint">· rê chuột xem 1 dòng · bấm 1 mốc → luận đầy đủ</span>
          </div>

          <!-- Dòng "đọc" mốc đang rê -->
          <div v-if="arcSel" class="vh-arc-sel" :style="{borderLeftColor: HANH_HUE[arcSel.duong_hanh]}">
            <b>{{ arcSel.label }}</b> · <span class="vh-arc-chip">{{ arcSel.duong_hanh }}</span>
            <p>{{ arcSel.doc }}</p>
            <button type="button" class="vh-arc-go" @click="pickArcPoint(arcSel)">→ Luận đầy đủ mốc này</button>
          </div>
          <p v-else class="vh-arc-hint2">Rê chuột lên một mốc để đọc, hoặc bấm để mở luận đầy đủ tháng/năm đó.</p>

          <p class="vh-arc-disc">☸️ {{ arc.disclaimer }}</p>
        </template>
      </div>

      <p v-if="tang !== 'life_arc' && loading" class="vh-note">Đang tra vận hạn…</p>
      <p v-else-if="tang !== 'life_arc' && error" class="vh-error">{{ error }}</p>

      <div v-else-if="tang !== 'life_arc' && block" class="vh-result">
        <!-- Âm lịch tương ứng (minh bạch dương→âm) -->
        <p v-if="block.am_lich" class="vh-amlich">
          📆 Dương lịch tháng {{ block.month }}/{{ block.year }}
          <b>≈ âm lịch tháng {{ block.am_lich.thang }}<span v-if="block.am_lich.nhuan"> (nhuận)</span>, năm {{ block.am_lich.nam_can_chi }}</b>
        </p>
        <p v-else-if="block.lunar_day" class="vh-amlich">
          📆 Dương lịch {{ block.solar }} <b>≈ âm lịch ngày {{ block.lunar_day }} tháng {{ block.lunar_month }} năm {{ block.lunar_year_can_chi }}, can ngày {{ block.day_can }}</b>
        </p>

        <!-- Nền bẩm sinh foreground (soil-before-seed — Mệnh chủ/Thân chủ/Cục) -->
        <div v-if="block.nen_menh" class="vh-nen">
          🌱 <b>Nền:</b> Mệnh chủ <b>{{ block.nen_menh.menh_chu }}</b> · Thân chủ <b>{{ block.nen_menh.than_chu }}</b> ·
          <b>{{ block.nen_menh.cuc?.cuc_name }}</b><span v-if="block.nen_menh.cuc?.element"> ({{ block.nen_menh.cuc.element }})</span> ·
          Thân cư {{ block.nen_menh.than_cung }}
        </div>

        <!-- Bối cảnh Đại Vận bao trùm (lồng tầng — lấy đại vận làm chủ) -->
        <div v-if="block.bao_tram_dai_van" class="vh-baotram">
          🌗 <b>Trong Đại Vận V{{ block.bao_tram_dai_van.cycle_index }}</b>
          (tuổi {{ block.bao_tram_dai_van.khoang_tuoi[0] }}–{{ block.bao_tram_dai_van.khoang_tuoi[1] }}) —
          cung {{ block.bao_tram_dai_van.cung }}
          <span v-if="block.bao_tram_dai_van.sao.length">({{ block.bao_tram_dai_van.sao.join(', ') }})</span>.
          Tầng này là <b>một bước</b> trong đại vận đó.
        </div>

        <!-- Bối cảnh Lưu Niên bao trùm (lồng tầng năm — giữa đại vận và tháng) -->
        <div v-if="block.bao_tram_luu_nien" class="vh-baotram vh-baotram-nien">
          📅 <b>Trong Lưu Niên {{ block.bao_tram_luu_nien.nam_can_chi }}</b> —
          lưu niên Mệnh cung {{ block.bao_tram_luu_nien.cung }}
          <span v-if="block.bao_tram_luu_nien.sao.length">({{ block.bao_tram_luu_nien.sao.join(', ') }})</span>.
        </div>

        <div class="vh-thedung">
          <span class="vh-vitri">an Mệnh tại <b>{{ block.vi_tri }}</b></span>
          <p>{{ block.dien_giai_the_dung }}</p>
        </div>

        <!-- Tứ Hóa rọi cung (cấu trúc, không phải dẫn sách) -->
        <div v-if="litHoa.length" class="vh-hoa-group">
          <h6 class="vh-sub">Tứ Hóa của tầng rọi vào cung — sân khấu MỜI QUAN-SÁT</h6>
          <div class="vh-hoa-grid">
            <div v-for="h in litHoa" :key="h.hoa" class="vh-hoa" :data-hoa="HOA_COLOR[h.hoa]">
              <span class="vh-hoa-name">{{ h.hoa }}</span>
              <span class="vh-hoa-star">{{ h.sao }}</span>
              <span class="vh-hoa-cung">→ {{ h.cung }}</span>
              <small>{{ h.nghia }}</small>
            </div>
          </div>
        </div>

        <!-- ★ TRỤ CỘT: Tứ Hóa chồng tầng (phi tinh) -->
        <div v-if="(block.phi_hoa?.trung_phung || []).length" class="vh-phihoa">
          <h6 class="vh-sub">✦ Tứ Hóa chồng tầng — điểm kích hoạt của kỳ này</h6>
          <div v-for="(t, i) in block.phi_hoa.trung_phung" :key="i" class="vh-tp" :class="{ cat: t.cat === true, hung: t.cat === false }">
            <b>{{ t.loai }}</b> · {{ t.sao }} @ {{ t.cung }}
            <small>{{ t.tang_hoa.map(x => x.tang + '·' + x.hoa).join(' + ') }} — {{ t.nghia }}</small>
            <em v-if="t.nguyen_ly" class="vh-nl">↻ {{ t.nguyen_ly }}</em>
          </div>
        </div>
        <div v-if="(block.phi_hoa?.tu_hoa || []).length" class="vh-tuhoa">
          <div v-for="(t, i) in block.phi_hoa.tu_hoa" :key="i" class="vh-th-item">
            <span class="vh-th-chip">{{ t.cung }} tự hóa {{ t.hoa }}</span>
            <small>{{ t.nghia.split('—').slice(1).join('—').trim() || t.nghia }}</small>
          </div>
        </div>

        <p v-if="block.thang_nhuan_note" class="vh-leapnote">{{ block.thang_nhuan_note }}</p>
        <p v-if="block.luu_y_vi_mo" class="vh-vimo">⚠ {{ block.luu_y_vi_mo }}</p>

        <!-- ★ LUẬN GIẢI — trọng tâm giao diện -->
        <div class="vh-luan-zone">
          <button v-if="!luan && !block.chua_co_nguon" type="button" class="vh-luan-btn"
            :disabled="luanLoading" @click="genLuan">
            {{ luanLoading ? "Đang luận…" : "✍️ Luận vận hạn tầng này" }}
          </button>
          <p v-else-if="block.chua_co_nguon" class="vh-chuanguon">Chưa đủ nguồn để luận — không gieo rác.</p>
          <div v-if="luan" class="vh-luan">{{ luan }}</div>
        </div>

        <!-- 📚 Chi tiết & dẫn sách — ẩn mặc định (Anh: giao diện tập trung luận giải) -->
        <details class="vh-sources">
          <summary>📚 Chi tiết &amp; dẫn sách (cung theo vận · tam phương tứ chính · sao · nguyên tắc)</summary>
          <div class="vh-sources-body">
            <div v-if="(block.cung_van_rules || []).length" class="vh-cungrule">
              <p class="vh-cungrule-head">📐 <b>Đọc cung {{ block.cung_the }} theo vận:</b></p>
              <p v-for="(r, i) in block.cung_van_rules" :key="i" class="vh-cungrule-item">
                • {{ r.rule }} <span class="vh-src">📖 {{ r.nguon }}</span>
              </p>
            </div>
            <div v-if="(block.hoi_chieu || []).length" class="vh-hoichieu">
              <h6 class="vh-sub">Tam phương tứ chính hội chiếu</h6>
              <div class="vh-hc-grid">
                <div v-for="(h, i) in block.hoi_chieu" :key="i" class="vh-hc">
                  <span class="vh-hc-qh">{{ h.quan_he }}</span>
                  <span class="vh-hc-cung">{{ h.cung }} ({{ h.vi_tri }})</span>
                  <small>{{ (h.sao || []).join(', ') || 'Vô Chính Diệu' }}</small>
                  <p v-for="(s, j) in (h.sao_nguon || [])" :key="j" class="vh-hc-nguon">{{ s.sao }}: {{ s.dich }}</p>
                </div>
              </div>
            </div>
            <div class="vh-sao">
              <h6 class="vh-sub">Sao tại cung vận Mệnh: {{ (block.sao || []).join(', ') || 'Vô Chính Diệu' }}
                <span v-if="block.sao_muon_xung" class="vh-muon">(mượn sao cung xung)</span></h6>
              <template v-if="block.sao_nguon && block.sao_nguon.length">
                <div v-for="(s, i) in block.sao_nguon" :key="i" class="vh-sao-item">
                  <p><b>{{ s.sao }}:</b> {{ s.dich }}</p><span class="vh-src">📖 {{ s.nguon }}</span>
                </div>
              </template>
              <p v-else class="vh-chuanguon">Kho sách chưa có nội dung đã duyệt cho cung này — để trống.</p>
            </div>
            <p class="vh-principle-in"><b>Nguyên tắc Thể-Dụng</b> ({{ block.nguyen_tac.nguon }}): {{ block.nguyen_tac.text }}</p>
          </div>
        </details>
      </div>
    </div>
  </section>
</template>

<style scoped>
.vh-block { margin-top: 14px; }
.vh-toggle {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  gap: 10px; text-align: left; padding: 11px 14px; cursor: pointer;
  background: var(--read-surface, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.15)); border-radius: 10px;
  color: var(--read-text, rgba(230, 238, 245, 0.92));
  font-size: calc(14px * var(--reading-scale, 1)); font-weight: 600;
}
.vh-toggle small { color: var(--read-text-faint, rgba(230, 238, 245, 0.55)); font-weight: 400; }
.vh-body { padding: 12px 4px 4px; }
.vh-note, .vh-error { color: var(--read-text-muted, rgba(230, 238, 245, 0.7)); font-size: calc(13px * var(--reading-scale, 1)); }
.vh-error { color: #f5a08c; }
.vh-tangs { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.vh-tang {
  display: inline-flex; flex-direction: column; align-items: center; cursor: pointer;
  padding: 6px 14px; border-radius: 9px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.2));
  background: var(--read-surface, rgba(255, 255, 255, 0.02));
  color: var(--read-text-dim, rgba(230, 238, 245, 0.82));
  font-size: calc(13px * var(--reading-scale, 1)); font-weight: 600;
}
.vh-tang small { font-weight: 400; font-size: calc(10px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); }
.vh-tang.active { border-color: var(--read-accent, #7ec8e3); color: var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126, 200, 227, 0.12)); }
.vh-picker { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 12px; }
.vh-picker label { font-size: calc(12.5px * var(--reading-scale, 1)); color: var(--read-text-dim, rgba(230, 238, 245, 0.8)); display: inline-flex; align-items: center; gap: 6px; }
.vh-picker input, .vh-picker select {
  padding: 4px 8px; border-radius: 6px; width: 84px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.2));
  background: var(--read-surface, rgba(255, 255, 255, 0.04)); color: var(--read-text, rgba(230, 238, 245, 0.92));
}
.vh-picker select { width: auto; }
.vh-picker label small { color: var(--read-text-faint, rgba(230,238,245,0.45)); font-size: calc(10px * var(--reading-scale, 1)); }
.vh-today { padding: 4px 12px; border-radius: 7px; cursor: pointer; border: 1px solid var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126,200,227,0.12)); color: var(--read-accent, #7ec8e3); font-size: calc(12px * var(--reading-scale, 1)); font-weight: 600; }
.vh-amlich { margin: 0 0 10px; font-size: calc(12px * var(--reading-scale, 1)); color: var(--read-text-dim, rgba(230,238,245,0.82)); }
.vh-amlich b { color: var(--read-han, #e8c95a); }
.vh-monthstrip { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }
.vh-mo { display: inline-flex; flex-direction: column; align-items: center; padding: 4px 9px; border-radius: 7px; cursor: pointer; border: 1px solid var(--read-border, rgba(230,238,245,0.18)); background: var(--read-surface, rgba(255,255,255,0.02)); color: var(--read-text-dim, rgba(230,238,245,0.8)); font-size: calc(11px * var(--reading-scale, 1)); }
.vh-mo small { color: var(--read-text-faint, rgba(230,238,245,0.5)); font-size: calc(9.5px * var(--reading-scale, 1)); }
.vh-mo.active { border-color: var(--read-accent, #7ec8e3); color: var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126,200,227,0.12)); }
.vh-leapnote { margin: 0 0 10px; font-size: calc(11.5px * var(--reading-scale, 1)); line-height: 1.55; color: var(--read-han, #e8c95a); opacity: 0.85; }
.vh-result { border: 1px solid var(--read-border, rgba(230, 238, 245, 0.14)); border-radius: 10px; padding: 12px 14px; background: var(--read-surface, rgba(255, 255, 255, 0.02)); }
.vh-baotram { margin-bottom: 10px; padding: 8px 11px; border-radius: 8px; background: rgba(253,230,138,0.06); border: 1px solid rgba(253,230,138,0.22); font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-dim, rgba(230,238,245,0.85)); }
.vh-hc-nguon { margin: 3px 0 0; font-size: calc(10.5px * var(--reading-scale, 1)); line-height: 1.5; color: var(--read-text-faint, rgba(230,238,245,0.62)); }
.vh-thedung { margin-bottom: 12px; }
.vh-vitri { font-size: calc(13px * var(--reading-scale, 1)); color: var(--read-accent, #7ec8e3); }
.vh-thedung p { margin: 4px 0 0; font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text, rgba(230, 238, 245, 0.88)); }
.vh-cungrule { margin-bottom: 12px; padding: 8px 11px; border-radius: 8px; border-left: 3px solid var(--read-rule, rgba(232, 201, 90, 0.5)); background: var(--read-surface, rgba(255, 255, 255, 0.02)); }
.vh-cungrule-head { margin: 0 0 3px; font-size: calc(12.5px * var(--reading-scale, 1)); color: var(--read-text, rgba(230, 238, 245, 0.9)); }
.vh-cungrule-item { margin: 3px 0 0; font-size: calc(12px * var(--reading-scale, 1)); line-height: 1.55; color: var(--read-text-dim, rgba(230, 238, 245, 0.8)); }
.vh-sub { margin: 0 0 6px; font-size: calc(12px * var(--reading-scale, 1)); font-weight: 600; color: var(--read-han, #e8c95a); opacity: 0.9; }
.vh-hoichieu { margin-bottom: 12px; }
.vh-hc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
.vh-hc { border: 1px solid var(--read-border, rgba(230,238,245,0.14)); border-radius: 8px; padding: 6px 9px; font-size: calc(11.5px * var(--reading-scale, 1)); }
.vh-hc-qh { color: var(--read-text-faint, rgba(230,238,245,0.55)); }
.vh-hc-cung { display: block; color: var(--read-accent, #7ec8e3); font-weight: 600; margin: 1px 0; }
.vh-hc small { color: var(--read-text-dim, rgba(230,238,245,0.78)); }
.vh-hoa-group { margin-bottom: 12px; }
.vh-hoa-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 8px; }
.vh-hoa { border: 1px solid var(--read-border, rgba(230, 238, 245, 0.16)); border-left-width: 3px; border-radius: 8px; padding: 7px 10px; font-size: calc(12px * var(--reading-scale, 1)); }
.vh-hoa[data-hoa="loc"] { border-left-color: #5ab07a; }
.vh-hoa[data-hoa="quyen"] { border-left-color: #d6a05a; }
.vh-hoa[data-hoa="khoa"] { border-left-color: #7ec8e3; }
.vh-hoa[data-hoa="ky"] { border-left-color: #d65a4a; }
.vh-hoa-name { font-weight: 700; color: var(--read-text, rgba(230, 238, 245, 0.92)); }
.vh-hoa-star { margin-left: 5px; color: var(--read-text-dim, rgba(230, 238, 245, 0.8)); }
.vh-hoa-cung { display: block; color: var(--read-accent, #7ec8e3); margin-top: 2px; }
.vh-hoa small { display: block; color: var(--read-text-faint, rgba(230, 238, 245, 0.55)); margin-top: 2px; }
.vh-sao { margin-bottom: 10px; }
.vh-muon { font-weight: 400; font-size: calc(10.5px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); }
.vh-sao-item { padding: 6px 0; border-top: 1px solid var(--read-border, rgba(230, 238, 245, 0.1)); }
.vh-sao-item:first-of-type { border-top: none; }
.vh-sao-item p { margin: 0; font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-dim, rgba(230, 238, 245, 0.82)); }
.vh-src { font-size: calc(10.5px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); }
.vh-chuanguon { font-size: calc(12px * var(--reading-scale, 1)); font-style: italic; color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); margin: 6px 0 0; }
.vh-vimo { font-size: calc(11.5px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.6)); margin: 8px 0; }
.vh-principle > summary { cursor: pointer; font-size: calc(11.5px * var(--reading-scale, 1)); color: var(--read-accent, #7ec8e3); margin: 8px 0; }
.vh-principle p { margin: 4px 0 0; font-size: calc(12px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-dim, rgba(230, 238, 245, 0.75)); padding-left: 9px; border-left: 2px solid var(--read-rule, rgba(232, 201, 90, 0.35)); }
.vh-luan-zone { margin-top: 10px; }
.vh-luan-btn {
  padding: 7px 14px; border-radius: 8px; cursor: pointer;
  border: 1px solid var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126, 200, 227, 0.12));
  color: var(--read-accent, #7ec8e3); font-size: calc(12.5px * var(--reading-scale, 1)); font-weight: 600;
}
.vh-luan-btn:disabled { opacity: 0.6; cursor: default; }
.vh-luan { margin-top: 10px; padding: 14px 16px; border-radius: 10px; background: var(--read-surface, rgba(255, 255, 255, 0.04)); border-left: 3px solid var(--read-accent, #7ec8e3); font-size: calc(13.5px * var(--reading-scale, 1)); line-height: 1.8; color: var(--read-text, rgba(230, 238, 245, 0.92)); white-space: pre-wrap; }
.vh-phihoa { margin-bottom: 12px; }
.vh-tp { padding: 7px 10px; margin-top: 6px; border-radius: 8px; border-left: 3px solid var(--read-border, rgba(230,238,245,0.3)); background: var(--read-surface, rgba(255,255,255,0.02)); font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.55; color: var(--read-text-dim, rgba(230,238,245,0.85)); }
.vh-tp.cat { border-left-color: #5ab07a; }
.vh-tp.hung { border-left-color: #d65a4a; }
.vh-tp small { display: block; margin-top: 2px; color: var(--read-text-faint, rgba(230,238,245,0.6)); }
.vh-nl { display: block; margin-top: 4px; font-style: normal; font-size: calc(11.5px * var(--reading-scale, 1)); line-height: 1.5; color: var(--read-accent, #b99bd6); opacity: 0.9; }
.vh-tuhoa { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.vh-th-item { display: flex; flex-wrap: wrap; align-items: baseline; gap: 7px; }
.vh-th-item small { color: var(--read-text-faint, rgba(230,238,245,0.6)); font-size: calc(11.5px * var(--reading-scale, 1)); line-height: 1.5; }
.vh-th-chip { flex: none; padding: 2px 9px; border-radius: 999px; border: 1px solid var(--read-border, rgba(230,238,245,0.2)); font-size: calc(11px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230,238,245,0.6)); }
.vh-luan-zone { margin: 14px 0; }
.vh-sources { margin-top: 14px; }
.vh-sources > summary { cursor: pointer; font-size: calc(12px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230,238,245,0.5)); padding: 6px 0; }
.vh-sources-body { padding-top: 6px; opacity: 0.92; }
.vh-principle-in { margin: 8px 0 0; font-size: calc(11.5px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-faint, rgba(230,238,245,0.6)); padding-left: 9px; border-left: 2px solid var(--read-rule, rgba(232,201,90,0.3)); }

/* 🌱 Nền bẩm sinh foreground */
.vh-nen { margin-bottom: 10px; padding: 8px 11px; border-radius: 8px; background: rgba(90,176,122,0.06); border: 1px solid rgba(90,176,122,0.22); font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-dim, rgba(230,238,245,0.85)); }
.vh-nen b { color: var(--read-han, #e8c95a); }
.vh-nen small { display: block; margin-top: 3px; color: var(--read-text-faint, rgba(230,238,245,0.55)); font-size: calc(11px * var(--reading-scale, 1)); }
.vh-baotram-nien { background: rgba(126,200,227,0.05); border-color: rgba(126,200,227,0.2); }

/* 🎢 Bức tranh cuộc đời thăng trầm */
.vh-arc { border: 1px solid var(--read-border, rgba(230,238,245,0.14)); border-radius: 10px; padding: 12px 14px; background: var(--read-surface, rgba(255,255,255,0.02)); }
.vh-arc-axis-note { margin: 4px 0 8px; font-size: calc(11.5px * var(--reading-scale, 1)); line-height: 1.55; color: var(--read-text-faint, rgba(230,238,245,0.6)); }
.vh-arc-scroll { overflow-x: auto; overflow-y: hidden; padding-bottom: 4px; }
.vh-arc-svg { display: block; }
.vh-arc-zone { fill: var(--read-text-faint, rgba(230,238,245,0.4)); font-size: 9px; font-weight: 700; letter-spacing: 0.5px; }
.vh-arc-tick { fill: var(--read-text-faint, rgba(230,238,245,0.5)); font-size: 8.5px; text-anchor: middle; }
.vh-arc-mid { stroke: var(--read-border, rgba(230,238,245,0.25)); stroke-width: 1; stroke-dasharray: 3 3; }
.vh-arc-area { fill: rgba(126,200,227,0.07); }
.vh-arc-line { fill: none; stroke: var(--read-accent, #7ec8e3); stroke-width: 1.4; opacity: 0.7; }
.vh-arc-dot { cursor: pointer; stroke: var(--read-bg, #10161d); stroke-width: 1; transition: r 0.1s; }
.vh-arc-dot:hover { stroke: var(--read-text, #fff); stroke-width: 1.5; }
.vh-arc-dot.quay { stroke: #d6a05a; stroke-width: 1.5; }
.vh-arc-legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; font-size: calc(11px * var(--reading-scale, 1)); color: var(--read-text-dim, rgba(230,238,245,0.75)); align-items: center; }
.vh-arc-legend span { display: inline-flex; align-items: center; gap: 5px; }
.vh-lg { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.vh-arc-hint { color: var(--read-text-faint, rgba(230,238,245,0.5)); }
.vh-arc-sel { margin-top: 10px; padding: 9px 12px; border-radius: 8px; border-left: 3px solid var(--read-accent, #7ec8e3); background: var(--read-surface, rgba(255,255,255,0.03)); }
.vh-arc-sel p { margin: 4px 0 6px; font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text, rgba(230,238,245,0.9)); }
.vh-arc-chip { padding: 1px 8px; border-radius: 999px; border: 1px solid var(--read-border, rgba(230,238,245,0.25)); font-size: calc(10.5px * var(--reading-scale, 1)); color: var(--read-text-dim, rgba(230,238,245,0.8)); }
.vh-arc-go { padding: 4px 11px; border-radius: 7px; cursor: pointer; border: 1px solid var(--read-accent, #7ec8e3); background: var(--read-accent-bg, rgba(126,200,227,0.12)); color: var(--read-accent, #7ec8e3); font-size: calc(11.5px * var(--reading-scale, 1)); font-weight: 600; }
.vh-arc-hint2 { margin-top: 10px; font-size: calc(11.5px * var(--reading-scale, 1)); font-style: italic; color: var(--read-text-faint, rgba(230,238,245,0.5)); }
.vh-arc-disc { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--read-border, rgba(230,238,245,0.1)); font-size: calc(11px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-faint, rgba(230,238,245,0.6)); }
</style>
