<script setup>
/**
 * TuViVsCDKCompare — So sánh chéo Bắc Phái (TVĐS 14 chính tinh) vs Chiếu Đởm Kinh (18 Phi Tinh).
 *
 * Hai paradigm song hành cho cùng 1 lá số. Show side-by-side để user thấy:
 * - Cùng birth → 2 cách an sao, 2 mệnh khác nhau
 * - Cùng vòng đại vận tuổi → cung khác, sao khác → vận khí khác
 * - Đối chiếu chéo = đa trường phái độc lập (Iron Rule #3)
 */
import { ref, computed, onMounted, watch } from "vue";
import { activePerson } from "../stores/userDataStore.js";

const tuviChart = ref(null);     // TVĐS chính thống
const cdkChart = ref(null);      // Chiếu Đởm Kinh
const cdkEval = ref(null);       // 6 cách cục matcher
const loading = ref(false);
const error = ref("");

const BRANCH_INFO = {
  "Tý": { conGiap: "Chuột", phuongVi: "Bắc", nguHanh: "Thủy", amDuong: "Dương" },
  "Sửu": { conGiap: "Trâu", phuongVi: "Bắc-Đông Bắc", nguHanh: "Thổ", amDuong: "Âm" },
  "Dần": { conGiap: "Hổ", phuongVi: "Đông-Đông Bắc", nguHanh: "Mộc", amDuong: "Dương" },
  "Mão": { conGiap: "Mèo/Thỏ", phuongVi: "Đông", nguHanh: "Mộc", amDuong: "Âm" },
  "Thìn": { conGiap: "Rồng", phuongVi: "Đông-Đông Nam", nguHanh: "Thổ", amDuong: "Dương" },
  "Tỵ": { conGiap: "Rắn", phuongVi: "Nam-Đông Nam", nguHanh: "Hỏa", amDuong: "Âm" },
  "Ngọ": { conGiap: "Ngựa", phuongVi: "Nam", nguHanh: "Hỏa", amDuong: "Dương" },
  "Mùi": { conGiap: "Dê", phuongVi: "Nam-Tây Nam", nguHanh: "Thổ", amDuong: "Âm" },
  "Thân": { conGiap: "Khỉ", phuongVi: "Tây-Tây Nam", nguHanh: "Kim", amDuong: "Dương" },
  "Dậu": { conGiap: "Gà", phuongVi: "Tây", nguHanh: "Kim", amDuong: "Âm" },
  "Tuất": { conGiap: "Chó", phuongVi: "Tây-Tây Bắc", nguHanh: "Thổ", amDuong: "Dương" },
  "Hợi": { conGiap: "Lợn", phuongVi: "Bắc-Tây Bắc", nguHanh: "Thủy", amDuong: "Âm" },
};

async function loadCharts() {
  const person = activePerson.value;
  if (!person?.birth_datetime_local && !person?.person_key) {
    error.value = "Chưa có thông tin sinh thần.";
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    const genderText = String(person?.gender || 'nam').toLowerCase();
    const gender = genderText.includes('nữ') || genderText.includes('nu') ? 'nữ' : 'nam';
    // Resolve birth_datetime_local if person uses key (lookup from activePerson which has it cached)
    const birth = person.birth_datetime_local;
    const timezone = person.timezone || 'Asia/Ho_Chi_Minh';
    // TVĐS cast: only accept birth_datetime_local direct (no person_key)
    const tuviPayload = { birth_datetime_local: birth, timezone, gender };
    // CDK cast + eval: accept person_key OR birth
    const cdkPayload = person.person_key
      ? { person_key: person.person_key }
      : { birth_datetime_local: birth, gender, timezone, name: person.name || 'Người' };
    const tuviOpts = { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify(tuviPayload) };
    const cdkOpts = { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify(cdkPayload) };
    const [tuviResp, cdkResp, evalResp] = await Promise.all([
      fetch('/api/tu-vi/cast', tuviOpts).then(r => r.json()),
      fetch('/api/tu-vi/q4/chieu-dom-kinh/cast', cdkOpts).then(r => r.json()),
      fetch('/api/tu-vi/q4/cdk/eval-cach-cuc', cdkOpts).then(r => r.json()),
    ]);
    // TVĐS response = {la_so: {...}} (no status field). CDK = {status: "ok", ...}
    if (tuviResp.la_so) tuviChart.value = tuviResp.la_so;
    if (cdkResp.status === 'ok') cdkChart.value = cdkResp;
    if (evalResp.status === 'ok') cdkEval.value = evalResp;
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

watch(activePerson, loadCharts);
onMounted(loadCharts);

const tuviMenh = computed(() => {
  const c = tuviChart.value;
  if (!c) return null;
  const stars = { ...(c.chinh_tinh || {}), ...(c.phu_tinh || {}), ...(c.sat_tinh || {}) };
  const menhStars = Object.entries(stars)
    .filter(([_, idx]) => ['Tý','Sửu','Dần','Mão','Thìn','Tỵ','Ngọ','Mùi','Thân','Dậu','Tuất','Hợi'][idx] === c.menh_branch)
    .map(([star]) => star);
  return {
    branch: c.menh_branch,
    stars: menhStars,
    menhChu: c.menh_chu,
    thanChu: c.than_chu,
    cuc: c.cuc_name,
    daiVanCount: (c.dai_van || []).length,
    tuHoa: c.tu_hoa,
  };
});

const cdkMenh = computed(() => {
  const c = cdkChart.value;
  if (!c) return null;
  const menhStars = Object.entries(c.stars || {})
    .filter(([_, b]) => b === c.menh_branch)
    .map(([star]) => star);
  return {
    branch: c.menh_branch,
    stars: menhStars,
    daiHanCount: (c.dai_han_cycles || []).length,
  };
});

const compareRows = computed(() => {
  if (!tuviMenh.value || !cdkMenh.value) return [];
  const rows = [
    {
      label: "Paradigm",
      tuvi: "Bắc Phái — Trần Đoàn chính tổ",
      cdk: "Phái khác — convention âm-dương ĐẢO",
      note: "Hai trường phái độc lập, đối chiếu chéo (Iron Rule #3)",
    },
    {
      label: "Số sao chính",
      tuvi: "14 chính tinh + Tứ Hóa + phụ-sát tinh",
      cdk: "18 Phi Tinh (KHÁC 14 chính tinh)",
      note: "Một số tên overlap (Tử Vi, Văn Xương) nhưng paradigm khác",
    },
    {
      label: "Cung Mệnh",
      tuvi: `${tuviMenh.value.branch} (${BRANCH_INFO[tuviMenh.value.branch]?.conGiap || '?'})`,
      cdk: `${cdkMenh.value.branch} (${BRANCH_INFO[cdkMenh.value.branch]?.conGiap || '?'})`,
      note: tuviMenh.value.branch === cdkMenh.value.branch
        ? "✓ Cùng địa chi — paradigm khác nhau nhưng kết quả trùng"
        : "⚠ KHÁC địa chi — paradigm khác cho ra kết quả khác",
    },
    {
      label: "Sao thủ Mệnh",
      tuvi: tuviMenh.value.stars.join(', ') || '(vô chính tinh)',
      cdk: cdkMenh.value.stars.join(', ') || '(vô)',
      note: "Sao TVĐS = từ 14 chính tinh + tứ hóa | Sao CDK = từ 18 Phi Tinh",
    },
    {
      label: "Mệnh chủ (linh hồn cốt lõi)",
      tuvi: tuviMenh.value.menhChu || '(không xác định)',
      cdk: "(CDK không dùng khái niệm Mệnh chủ riêng)",
      note: "Mệnh chủ TVĐS = sao chủ cung Mệnh theo bảng Phú Thái Vi Q.2",
    },
    {
      label: "Thân chủ (hành động ra đời)",
      tuvi: tuviMenh.value.thanChu || '(không xác định)',
      cdk: "(CDK không tách Thân chủ)",
      note: "Thân chủ TVĐS = sao chủ cung Thân (đại diện biểu hiện)",
    },
    {
      label: "Cục",
      tuvi: tuviMenh.value.cuc || '?',
      cdk: "(không dùng cục riêng — chỉ dùng 12 chi raw)",
      note: "Cục TVĐS quyết định tuổi khởi đại vận",
    },
    {
      label: "Tứ Hóa năm sinh",
      tuvi: Object.entries(tuviMenh.value.tuHoa || {}).map(([k, v]) => `${k}→${v}`).join(' · '),
      cdk: "(CDK không dùng Tứ Hóa)",
      note: "Tứ Hóa = 4 sao biến (Lộc/Quyền/Khoa/Kỵ) năm sinh — chỉ TVĐS",
    },
    {
      label: "Số vòng Đại Vận",
      tuvi: `${tuviMenh.value.daiVanCount} vòng × 10 năm = ${tuviMenh.value.daiVanCount * 10} năm`,
      cdk: `${cdkMenh.value.daiHanCount} vòng × 10 năm = ${cdkMenh.value.daiHanCount * 10} năm`,
      note: "TVĐS = 12 cung chức năng (Mệnh/Tài/Quan/...). CDK = 8 vòng đi qua chi",
    },
    {
      label: "6 Cách cục đặc thù CDK",
      tuvi: "(545 cách cục riêng Q1 Phú Thái Vi)",
      cdk: cdkEval.value
        ? `${cdkEval.value.matched_count}/6 trúng${cdkEval.value.matched_count > 0 ? ': ' + cdkEval.value.matched.map(c => c.name_vi).join(', ') : ''}`
        : '?',
      note: "Cách cục CDK = 6 mẫu lá số đặc biệt Q4 p0275 (Thân nịch giang hồ, Phú môn, etc.)",
    },
  ];
  return rows;
});
</script>

<template>
  <section class="cmp-panel">
    <header class="cmp-head">
      <h2>⚖️ So sánh chéo: TVĐS Bắc Phái vs Chiếu Đởm Kinh</h2>
      <p class="cmp-sub">
        Hai paradigm song hành cho cùng một lá số. Cùng birth → 2 cách an sao, 2 mệnh khác nhau.
        Iron Rule #3: <b>đa trường phái độc lập, không ép vào 1</b>.
      </p>
    </header>

    <p v-if="loading" class="cmp-loading">Đang tải dữ liệu 2 paradigm...</p>
    <p v-if="error" class="cmp-error">⚠ {{ error }}</p>

    <div v-if="compareRows.length" class="cmp-table">
      <div class="cmp-row cmp-header">
        <div class="cmp-col cmp-col-label">Đặc điểm</div>
        <div class="cmp-col cmp-col-tuvi">
          <strong>🌌 TVĐS chính thống (Bắc phái)</strong>
          <small>14 chính tinh · Trần Đoàn</small>
        </div>
        <div class="cmp-col cmp-col-cdk">
          <strong>📜 Chiếu Đởm Kinh (phái khác)</strong>
          <small>18 Phi Tinh · convention âm-dương ĐẢO</small>
        </div>
      </div>
      <article v-for="(row, i) in compareRows" :key="i" class="cmp-row">
        <div class="cmp-col cmp-col-label">{{ row.label }}</div>
        <div class="cmp-col cmp-col-tuvi">{{ row.tuvi }}</div>
        <div class="cmp-col cmp-col-cdk">{{ row.cdk }}</div>
        <div class="cmp-row-note">💡 {{ row.note }}</div>
      </article>
    </div>

    <footer class="cmp-foot">
      <p>
        <b>Tinh thần Iron Rule #3:</b> Mỗi trường phái có cách an sao, cách luận giải riêng.
        TVĐS phù hợp xem cung chức năng (sự nghiệp/hôn nhân/tài lộc). CDK phù hợp xem
        bản chất sâu xa + thần sát đặc thù. Anh dùng cả 2 = đối chiếu chéo, tăng độ chính xác.
      </p>
    </footer>
  </section>
</template>

<style scoped>
.cmp-panel {
  padding: 18px;
  background:
    linear-gradient(135deg, rgba(252, 211, 77, 0.04) 0%, rgba(167, 139, 250, 0.04) 100%),
    rgba(2, 6, 23, 0.4);
  border: 1px solid rgba(167, 139, 250, 0.22);
  border-radius: 10px;
  margin: 16px 0;
}
.cmp-head h2 {
  margin: 0 0 8px;
  color: #fcd34d;
  font-size: 17px;
}
.cmp-sub {
  margin: 0 0 14px;
  color: rgba(230, 238, 245, 0.78);
  font-size: 12.5px;
  line-height: 1.55;
}
.cmp-sub b { color: #5be5d3; }
.cmp-loading, .cmp-error {
  padding: 10px;
  color: rgba(230, 238, 245, 0.65);
  font-size: 13px;
}
.cmp-error { color: #fca5a5; }

.cmp-table {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: rgba(230, 238, 245, 0.06);
  border-radius: 8px;
  overflow: hidden;
}
.cmp-row {
  display: grid;
  grid-template-columns: 0.7fr 1.3fr 1.3fr;
  gap: 1px;
  background: rgba(2, 6, 23, 0.6);
}
.cmp-row.cmp-header {
  background: rgba(252, 211, 77, 0.08);
}
.cmp-row.cmp-header .cmp-col {
  padding: 10px 12px;
  font-size: 12.5px;
}
.cmp-row.cmp-header .cmp-col-label {
  font-weight: 700;
  color: rgba(230, 238, 245, 0.84);
}
.cmp-row.cmp-header .cmp-col-tuvi {
  border-left: 3px solid #fcd34d;
}
.cmp-row.cmp-header .cmp-col-cdk {
  border-left: 3px solid #c4b5fd;
}
.cmp-row.cmp-header .cmp-col strong {
  display: block;
  color: #f5e6b1;
  font-size: 13px;
}
.cmp-row.cmp-header .cmp-col small {
  display: block;
  color: rgba(230, 238, 245, 0.6);
  font-size: 11px;
  margin-top: 2px;
}
.cmp-col {
  padding: 10px 12px;
  background: rgba(2, 6, 23, 0.55);
  font-size: 13px;
  color: rgba(230, 238, 245, 0.92);
  line-height: 1.5;
}
.cmp-col-label {
  font-weight: 700;
  color: #fcd34d;
  background: rgba(2, 6, 23, 0.7);
  font-size: 12.5px;
}
.cmp-col-tuvi {
  border-left: 3px solid rgba(252, 211, 77, 0.35);
}
.cmp-col-cdk {
  border-left: 3px solid rgba(196, 181, 253, 0.35);
}
.cmp-row-note {
  grid-column: 1 / -1;
  padding: 6px 14px 9px 16px;
  background: rgba(2, 6, 23, 0.45);
  color: rgba(91, 229, 211, 0.85);
  font-size: 11.5px;
  font-style: italic;
}
.cmp-foot {
  margin-top: 12px;
  padding: 12px 14px;
  background: rgba(91, 229, 211, 0.06);
  border-left: 3px solid rgba(91, 229, 211, 0.4);
  border-radius: 0 6px 6px 0;
  color: rgba(230, 238, 245, 0.88);
  font-size: 12.5px;
  line-height: 1.55;
}
.cmp-foot b { color: #5be5d3; }

@media (max-width: 720px) {
  .cmp-row {
    grid-template-columns: 1fr;
  }
  .cmp-col-tuvi, .cmp-col-cdk {
    border-left: none;
    border-top: 2px solid rgba(252, 211, 77, 0.3);
  }
  .cmp-col-cdk {
    border-top-color: rgba(196, 181, 253, 0.35);
  }
}
</style>
