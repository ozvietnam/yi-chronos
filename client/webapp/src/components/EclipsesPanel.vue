<script setup>
import { computed, ref } from "vue";
import { getEclipses } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";

const SIGN_VI = {
  aries: "Bạch Dương", taurus: "Kim Ngưu", gemini: "Song Tử",
  cancer: "Cự Giải", leo: "Sư Tử", virgo: "Xử Nữ",
  libra: "Thiên Bình", scorpio: "Bọ Cạp", sagittarius: "Nhân Mã",
  capricorn: "Ma Kết", aquarius: "Bảo Bình", pisces: "Song Ngư"
};
const SIGN_GLYPH = {
  aries: "♈", taurus: "♉", gemini: "♊", cancer: "♋", leo: "♌", virgo: "♍",
  libra: "♎", scorpio: "♏", sagittarius: "♐", capricorn: "♑", aquarius: "♒", pisces: "♓"
};
const NATAL_VI = {
  sun: "Mặt Trời", moon: "Mặt Trăng", mercury: "Thủy", venus: "Kim", mars: "Hỏa",
  ascendant: "Mọc", midheaven: "Đỉnh"
};
const SUBTYPE_VI = {
  total_or_annular: "toàn phần / annular",
  partial: "một phần",
  total: "toàn phần",
  penumbral: "nửa tối"
};

const inputBirth = ref("");
useActivePersonBirth(inputBirth);
const inputLat = ref("");
const inputLon = ref("");
const inputSpan = ref(90);
const onlyMajor = ref(true);
const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");

const filtered = computed(() => {
  if (!data.value) return [];
  return onlyMajor.value
    ? data.value.eclipses.filter((e) => e.importance === "major")
    : data.value.eclipses;
});

const todayAge = computed(() => {
  if (!data.value) return null;
  const birthMs = new Date(data.value.birth_utc).getTime();
  return (Date.now() - birthMs) / (365.25 * 86400 * 1000);
});

async function load() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần ngày giờ sinh";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  try {
    const local = new Date(inputBirth.value);
    if (Number.isNaN(local.getTime())) throw new Error("Định dạng thời điểm không hợp lệ");
    const birthAt = local.toISOString();
    const lat = inputLat.value !== "" ? Number(inputLat.value) : null;
    const lon = inputLon.value !== "" ? Number(inputLon.value) : null;
    data.value = await getEclipses({ birthAt, lat, lon, spanYears: Number(inputSpan.value), onlyActivated: true });
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function setPreset(name) {
  if (name === "hanoi") { inputLat.value = "21.0285"; inputLon.value = "105.8542"; }
  else if (name === "saigon") { inputLat.value = "10.7626"; inputLon.value = "106.6602"; }
}

function fmtDate(iso) {
  return new Intl.DateTimeFormat("vi-VN", { year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(iso));
}

function fmtAge(age) {
  const y = Math.floor(age);
  const m = Math.round((age - y) * 12);
  if (m === 12) return `${y + 1} tuổi`;
  if (m === 0) return `${y} tuổi`;
  return `${y}t ${m}th`;
}
</script>

<template>
  <section class="panel ec-panel">
    <div class="panel-title">
      <span>Eclipse Activations — Nhật/nguyệt thực rơi vào lá số sinh</span>
      <small>{{ data?.eclipses.length || 0 }} kích hoạt</small>
    </div>

    <p class="ec-note">
      Mỗi nhật/nguyệt thực rơi gần một điểm trong lá số sinh sẽ "kích hoạt"
      điểm đó — thường đi kèm sự kiện lớn hoặc thay đổi đột ngột trong khu vực
      sinh đó cai quản.
    </p>

    <div class="ec-form">
      <label><span>Ngày giờ sinh</span><input v-model="inputBirth" type="datetime-local" step="60" /></label>
      <div class="ec-loc">
        <label><span>Vĩ độ</span><input v-model="inputLat" type="number" step="0.0001" /></label>
        <label><span>Kinh độ</span><input v-model="inputLon" type="number" step="0.0001" /></label>
      </div>
      <label><span>Năm</span><input v-model.number="inputSpan" type="number" min="20" max="100" step="10" /></label>
      <div class="ec-presets">
        <button class="preset-btn" @click="setPreset('hanoi')">HN</button>
        <button class="preset-btn" @click="setPreset('saigon')">SG</button>
      </div>
      <button class="apply-btn" @click="load" :disabled="loading">{{ loading ? "..." : "Vẽ" }}</button>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <div class="ec-toggle">
        <label>
          <input type="checkbox" v-model="onlyMajor" />
          <span>chỉ xem kích hoạt lớn ({{ data.eclipses.filter(e => e.importance === 'major').length }})</span>
        </label>
      </div>

      <ul class="ec-list">
        <li v-for="e in filtered" :key="e.date_utc"
          :class="['ec-row', e.eclipse_type, `imp-${e.importance}`,
            todayAge !== null && Math.abs(e.age_years - todayAge) < 1 ? 'now' : '']">
          <div class="head">
            <span class="age">{{ fmtAge(e.age_years) }}</span>
            <span class="dt">{{ fmtDate(e.date_utc) }}</span>
            <span :class="['type', e.eclipse_type]">
              {{ e.eclipse_type === 'solar' ? '☀ Nhật thực' : '☾ Nguyệt thực' }}
              · {{ SUBTYPE_VI[e.eclipse_subtype] }}
            </span>
          </div>
          <div class="loc">
            tại <b>{{ SIGN_GLYPH[e.eclipse_sign] }} {{ SIGN_VI[e.eclipse_sign] }} {{ e.eclipse_sign_degree.toFixed(1) }}°</b>
          </div>
          <div class="acts">
            <span class="lbl">Kích hoạt:</span>
            <span v-for="a in e.activations" :key="a.natal_point"
              :class="['act-tag', `imp-${a.importance}`]">
              {{ NATAL_VI[a.natal_point] }} ({{ a.orb_deg.toFixed(1) }}°)
            </span>
          </div>
        </li>
      </ul>

      <p v-if="filtered.length === 0" class="empty-hint">
        Không có kích hoạt {{ onlyMajor ? "lớn" : "" }} nào trong khoảng này.
      </p>
    </template>

    <p v-else class="empty-hint">Nhập ngày giờ sinh + tọa độ để xem.</p>
  </section>
</template>

<style scoped>
.ec-panel { display: flex; flex-direction: column; gap: 12px; }
.ec-note {
  font-size: 0.82rem; color: rgba(255,255,255,0.7);
  border-left: 2px solid rgba(232,201,90,0.5); padding-left: 10px;
  margin: 0; line-height: 1.5;
}
.ec-form {
  display: grid; grid-template-columns: 1.6fr 1.2fr 0.5fr auto auto;
  gap: 8px; align-items: end;
  background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;
}
.ec-form label { display: flex; flex-direction: column; gap: 4px;
  font-size: 0.74rem; color: rgba(255,255,255,0.7); }
.ec-form input {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
  color: #fff; border-radius: 5px; padding: 5px 7px; font-size: 0.82rem;
}
.ec-loc { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
.ec-presets { display: flex; gap: 2px; }
.preset-btn {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.85); padding: 5px 7px; border-radius: 4px;
  font-size: 0.72rem; cursor: pointer;
}
.apply-btn {
  background: rgba(232,201,90,0.18); border: 1px solid rgba(232,201,90,0.5);
  color: #e8c95a; padding: 7px 14px; border-radius: 6px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
}

.ec-toggle label {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.78rem; color: rgba(255,255,255,0.7); cursor: pointer;
}

.ec-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 4px;
}

.ec-row {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px; padding: 8px 10px;
}
.ec-row.imp-major { border-color: rgba(232,201,90,0.4); background: rgba(232,201,90,0.05); }
.ec-row.now { box-shadow: 0 0 0 1px rgba(232,201,90,0.6); }

.head {
  display: flex; gap: 10px; align-items: baseline;
  font-size: 0.82rem; flex-wrap: wrap;
}
.age { color: #e8c95a; font-weight: 600; min-width: 70px; }
.dt { color: rgba(255,255,255,0.6); font-family: ui-monospace, monospace; font-size: 0.74rem; }
.type {
  font-size: 0.78rem; padding: 1px 6px; border-radius: 3px;
  background: rgba(255,255,255,0.06);
}
.type.solar { color: #e8c95a; }
.type.lunar { color: #b8c4e0; }

.loc { font-size: 0.78rem; color: rgba(255,255,255,0.78); margin-top: 3px; }

.acts {
  display: flex; gap: 4px; flex-wrap: wrap; margin-top: 4px;
  font-size: 0.74rem; align-items: center;
}
.lbl { color: rgba(255,255,255,0.5); }
.act-tag {
  padding: 1px 7px; border-radius: 3px; font-size: 0.72rem;
  background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.8);
}
.act-tag.imp-major { background: rgba(232,201,90,0.18); color: #f5e6b1; font-weight: 600; }
.act-tag.imp-medium { background: rgba(74,176,194,0.15); color: #9adfe5; }

.empty-hint {
  font-size: 0.85rem; color: rgba(255,255,255,0.5);
  text-align: center; padding: 24px 0; margin: 0;
}
</style>
