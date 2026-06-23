<script setup>
// 🔬 Nhà của phái Tử Vi Đằng Sơn — "Tử Vi Hoàn Toàn Khoa Học"
// Gom các tác phẩm THẬT của phái: cấu trúc tính-được (/api/natal-universe) +
// lá số 3D nền vũ trụ + video Đại Vận + sách + NHỊP THÁNG (lưu nguyệt la-bàn-chú-ý).
// Paradigm: tính được TÍNH ≠ tính MỆNH; nhịp tháng = la bàn chú-ý, không phải bói.
import { ref, computed } from "vue";
import { activeBirthDatetime } from "../stores/userDataStore.js";
import { getNatalUniverse, getLuuNguyet } from "../lib/api";

const emit = defineEmits(["go-universe"]);
const data = ref(null);
const loading = ref(false);
const err = ref("");
const year = new Date().getFullYear();

const HANH = { thuy: "#6aa9e6", moc: "#5fc46a", hoa: "#ef7a6a", tho: "#e0b94a", kim: "#aeb4bb" };
function hcol(s) {
  const k = { "thủy": "thuy", "mộc": "moc", "hỏa": "hoa", "thổ": "tho", "kim": "kim" }[(s || "").split("/")[0].trim()] || "kim";
  return HANH[k];
}
const HOA_COL = { "Lộc": "#5fc46a", "Quyền": "#ef7a6a", "Khoa": "#6aa9e6", "Kỵ": "#9aa6b0" };

async function load() {
  const at = activeBirthDatetime.value;
  if (!at) { err.value = "Chưa có ngày sinh — vào tab Hồ sơ chọn 'Bản thân' trước."; return; }
  loading.value = true; err.value = "";
  try { data.value = await getNatalUniverse({ at, year }); }
  catch (e) { err.value = e?.message || String(e); }
  finally { loading.value = false; }
}

// 🧭 Nhịp tháng (lưu nguyệt) — la bàn chú-ý, đa năm, load on click
const rhythm = ref(null);
const rLoading = ref(false);
const rErr = ref("");
const selYear = ref(null);
async function loadRhythm() {
  const at = activeBirthDatetime.value;
  if (!at) { rErr.value = "Chưa có ngày sinh — vào tab Hồ sơ chọn 'Bản thân' trước."; return; }
  rLoading.value = true; rErr.value = "";
  try {
    rhythm.value = await getLuuNguyet({ at, yearStart: year, yearEnd: year + 5 });
    selYear.value = rhythm.value?.years?.[0]?.year ?? year;
  } catch (e) { rErr.value = e?.message || String(e); }
  finally { rLoading.value = false; }
}
const selYearData = computed(() => rhythm.value?.years?.find((y) => y.year === selYear.value) || null);
function pal(h) { return h && h.palace ? h.palace : "—"; }
</script>

<template>
  <div class="ds">
    <header class="ds-head">
      <h2>🔬 Đằng Sơn — Tử Vi Hoàn Toàn Khoa Học</h2>
      <p class="ds-tag">Phái duy-lý / cấu-trúc · <b>tính được cái TÍNH, không tính sự VẬN HÀNH</b></p>
    </header>

    <div class="ds-paradigm">
      Lá số là một <b>hàm tất định</b> của thời điểm sinh — an sao, ngũ hành, Tứ Hóa, độ sáng đều
      <i>tính được tuyệt đối</i>. Nhưng cái tính-được ấy là <b>cấu trúc bẩm phú (TÍNH)</b>, không phải
      kết cục (MỆNH = động từ, việc anh vận hành). Đọc đồng dạng — <b>không bói</b>.
    </div>

    <!-- Cấu trúc tính-được -->
    <section class="ds-card">
      <div class="ds-card-h">
        <h3>Cấu trúc tính-được của lá số</h3>
        <button class="ds-btn" :disabled="loading" @click="load">
          {{ loading ? "Đang tính…" : data ? "Tính lại" : "Lập hồ sơ tính-được" }}
        </button>
      </div>
      <p v-if="err" class="ds-err">{{ err }}</p>

      <div v-if="data" class="ds-struct">
        <p class="ds-meta">
          Mệnh <b>{{ data.dia_ban.menh_chi }}</b> · Cục <b>{{ data.dia_ban.cuc }}</b> ·
          Tử Vi an <b>{{ data.dia_ban.tu_vi_chi }}</b> · {{ data.dia_ban.year_can_chi }}
        </p>
        <div class="ds-grid">
          <div v-for="c in data.dia_ban.cung" :key="c.chi" class="ds-cung" :class="{ menh: c.is_menh }">
            <div class="ds-chi">{{ c.chi }}<span v-if="c.is_menh" class="ds-menh">★ Mệnh</span></div>
            <div v-if="!c.chinh_tinh.length" class="ds-empty">vô chính diệu</div>
            <div v-for="st in c.chinh_tinh" :key="st.name" class="ds-sao"
                 :style="{ color: hcol(st.ngu_hanh) }">
              <span :class="{ dac: st.do_sang === 'đắc', ham: st.do_sang === 'hãm' }">{{ st.name }}</span>
              <span v-if="st.hoa" class="ds-hoa" :style="{ background: HOA_COL[st.hoa] }">{{ st.hoa }}</span>
              <span class="ds-ds">{{ st.do_sang }}</span>
            </div>
          </div>
        </div>
        <p v-if="data.luu_nien" class="ds-luu">
          🌗 Lá số "thở" theo năm — <b>{{ data.luu_nien.year }}</b> ({{ data.luu_nien.can_chi }}):
          lưu Hóa Lộc → <b>{{ data.luu_nien.tu_hoa['Lộc'] }}</b>, Quyền → {{ data.luu_nien.tu_hoa['Quyền'] }},
          Kỵ → {{ data.luu_nien.tu_hoa['Kỵ'] }}.
        </p>
      </div>
      <p v-else-if="!err" class="ds-hint">Bấm để engine tính 14 chính tinh + ngũ hành + Tứ Hóa + độ sáng — toàn hàm tất định, sai số người bằng 0.</p>
    </section>

    <!-- 🧭 Nhịp tháng — la bàn chú-ý -->
    <section class="ds-card">
      <div class="ds-card-h">
        <h3>🧭 Nhịp tháng — la bàn chú-ý</h3>
        <button class="ds-btn" :disabled="rLoading" @click="loadRhythm">
          {{ rLoading ? "Đang tính…" : rhythm ? "Tính lại" : "Xem nhịp tháng" }}
        </button>
      </div>
      <p class="ds-paradigm-sm">
        Mỗi tháng âm, cấu trúc rọi sáng một cung: <b style="color:#5fc46a">Lộc</b> = cửa mở phía ngoài ·
        <b style="color:#e0884a">Kỵ</b> = nút thắt phía trong. Đây là <i>la bàn chú-ý</i> — tháng này nên
        để tâm vào đâu — <b>không phải bói kết cục</b> (soi mịn chỉ dịch tiêu điểm, không co độ bất định).
      </p>
      <p v-if="rErr" class="ds-err">{{ rErr }}</p>

      <div v-if="rhythm">
        <div class="ds-years">
          <button v-for="y in rhythm.years" :key="y.year" class="ds-year"
                  :class="{ on: y.year === selYear }" @click="selYear = y.year">
            {{ y.year }}<small>{{ y.year_stem }}</small>
          </button>
        </div>
        <div v-if="selYearData" class="ds-months">
          <div v-for="m in selYearData.months" :key="m.month" class="ds-month">
            <div class="ds-mhead">Tháng {{ m.month }}<span>{{ m.month_can_chi }}</span></div>
            <div class="ds-flow loc"><span class="dot"></span>{{ pal(m.hoa['Lộc']) }}</div>
            <div class="ds-flow ky"><span class="dot"></span>{{ pal(m.hoa['Kỵ']) }}</div>
          </div>
        </div>
      </div>
      <p v-else-if="!rErr" class="ds-hint">12 tháng × 6 năm tới — cung nào sáng Lộc/Kỵ mỗi tháng, engine tính tất định. Dùng như lịch quan-sát: tháng nào nên đặt tâm vào cung nào.</p>
    </section>

    <!-- Tác phẩm của phái -->
    <section class="ds-card">
      <h3>Tác phẩm của phái</h3>
      <div class="ds-works">
        <button class="ds-work" @click="emit('go-universe')">
          <span class="ds-emoji">🌌</span>
          <span><b>Lá số trên nền vũ trụ THẬT (3D)</b><small>14 sao tính-được phủ lên thiên văn thật · xoay/zoom</small></span>
        </button>
        <a class="ds-work" href="/dai-van.html" target="_blank" rel="noopener">
          <span class="ds-emoji">🎬</span>
          <span><b>Video Đại Vận</b><small>phim khoa học 1-3 phút · thuyết minh · chủ thể đang nói thì sáng</small></span>
        </a>
      </div>
    </section>
  </div>
</template>

<style scoped>
.ds { color: #dbe4ea; font-size: 15px; line-height: 1.6; }
.ds-head h2 { color: #e6c45a; font-size: 22px; margin: .2em 0 .15em; }
.ds-tag { color: #9aa6b0; margin: 0 0 14px; font-size: 14px; }
.ds-paradigm { background: #16140c; border: 1px solid #5a4a1e; border-radius: 10px; padding: 13px 16px; margin: 0 0 18px; font-size: 14.5px; color: #e9d9a8; }
.ds-card { background: #0e141b; border: 1px solid #26323f; border-radius: 12px; padding: 16px 18px; margin: 0 0 16px; }
.ds-card-h { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
.ds-card h3 { color: #e6c45a; font-size: 16.5px; margin: .1em 0 .5em; }
.ds-card-h h3 { margin: 0; }
.ds-btn { border: 1px solid rgba(232,168,56,.55); background: rgba(18,14,8,.74); color: #ffd98a; border-radius: 999px; padding: 7px 16px; font-size: 13.5px; font-weight: 700; cursor: pointer; }
.ds-btn:disabled { opacity: .6; cursor: default; }
.ds-err { color: #ef7a6a; font-size: 13.5px; }
.ds-hint { color: #8a9aa6; font-size: 13.5px; }
.ds-meta { color: #c4d0d8; margin: 6px 0 12px; font-size: 14px; }
.ds-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
.ds-cung { background: #0b1016; border: 1px solid #26323f; border-radius: 8px; padding: 8px 10px; }
.ds-cung.menh { border-color: #e6c45a; box-shadow: 0 0 0 1px rgba(230,196,90,.3); }
.ds-chi { color: #8a9aa6; font-size: 12.5px; margin-bottom: 4px; display: flex; justify-content: space-between; }
.ds-menh { color: #e6c45a; font-weight: 700; }
.ds-empty { color: #5a6670; font-style: italic; font-size: 13px; }
.ds-sao { display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 14.5px; margin: 2px 0; }
.ds-sao .dac { text-shadow: 0 0 8px currentColor; font-size: 15.5px; }
.ds-sao .ham { opacity: .62; }
.ds-hoa { color: #0b1016; font-size: 10px; font-weight: 800; padding: 1px 5px; border-radius: 4px; }
.ds-ds { color: #6a7680; font-size: 11px; font-style: italic; }
.ds-luu { background: #0b1016; border: 1px solid #26323f; border-radius: 8px; padding: 10px 12px; margin-top: 12px; font-size: 14px; color: #c4d0d8; }
.ds-paradigm-sm { color: #c9b98a; font-size: 13.5px; margin: 2px 0 12px; line-height: 1.5; }
.ds-years { display: flex; flex-wrap: wrap; gap: 7px; margin: 4px 0 12px; }
.ds-year { background: #0b1016; border: 1px solid #26323f; color: #c4d0d8; border-radius: 8px; padding: 5px 12px; font-size: 13.5px; font-weight: 700; cursor: pointer; display: flex; flex-direction: column; align-items: center; line-height: 1.15; }
.ds-year small { color: #8a9aa6; font-size: 10px; font-weight: 400; }
.ds-year.on { border-color: #e6c45a; color: #ffd98a; background: #16140c; }
.ds-months { display: grid; grid-template-columns: repeat(auto-fill, minmax(134px, 1fr)); gap: 8px; }
.ds-month { background: #0b1016; border: 1px solid #26323f; border-radius: 8px; padding: 8px 10px; }
.ds-mhead { color: #c4d0d8; font-size: 13px; font-weight: 700; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: baseline; }
.ds-mhead span { color: #8a9aa6; font-weight: 400; font-size: 11px; }
.ds-flow { display: flex; align-items: center; gap: 6px; font-size: 13.5px; margin: 2px 0; }
.ds-flow .dot { width: 7px; height: 7px; border-radius: 50%; flex: none; }
.ds-flow.loc { color: #cfe8c0; } .ds-flow.loc .dot { background: #5fc46a; }
.ds-flow.ky { color: #e8cdb0; } .ds-flow.ky .dot { background: #e0884a; }
.ds-works { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.ds-work { display: flex; align-items: center; gap: 12px; text-align: left; text-decoration: none; background: #0b1016; border: 1px solid #26323f; border-radius: 10px; padding: 13px 15px; color: #dbe4ea; cursor: pointer; }
.ds-work:hover { border-color: #e6c45a; }
.ds-work .ds-emoji { font-size: 26px; }
.ds-work b { display: block; color: #e6c45a; font-size: 14.5px; }
.ds-work small { color: #8a9aa6; font-size: 12.5px; }
@media (max-width: 620px) { .ds-works { grid-template-columns: 1fr; } }
</style>
