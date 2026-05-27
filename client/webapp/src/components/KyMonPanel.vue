<script setup>
import { ref, computed } from "vue";

const now = new Date();
const form = ref({
  year: now.getFullYear(),
  month: now.getMonth() + 1,
  day: now.getDate(),
  hour: now.getHours(),
  minute: now.getMinutes(),
  method: "chabu",
  question: ""
});

const state = ref(null);
const loading = ref(false);
const error = ref("");

// Lo Thu 9 cung layout (3x3 grid):
//   4 巽 Tốn  | 9 離 Ly   | 2 坤 Khôn
//   3 震 Chấn | 5 中 Trung | 7 兌 Đoài
//   8 艮 Cấn  | 1 坎 Khảm | 6 乾 Càn
const LO_THU_ORDER = ["Tốn", "Ly", "Khôn", "Chấn", "Trung", "Đoài", "Cấn", "Khảm", "Càn"];
const LO_THU_NUMBERS = { "Tốn": 4, "Ly": 9, "Khôn": 2, "Chấn": 3, "Trung": 5, "Đoài": 7, "Cấn": 8, "Khảm": 1, "Càn": 6 };

const cungGrid = computed(() => {
  if (!state.value) return [];
  const lookup = (arr, key) => Object.fromEntries((arr || []).map(c => [c.cung_vn, c]));
  const thien = lookup(state.value.thien_ban);
  const dia = lookup(state.value.dia_ban);
  const mon = lookup(state.value.mon);
  const tinh = lookup(state.value.tinh);
  const than = lookup(state.value.than);

  return LO_THU_ORDER.map(cungVn => ({
    cung_vn: cungVn,
    cung_zh: thien[cungVn]?.cung_zh || dia[cungVn]?.cung_zh || "",
    direction: thien[cungVn]?.direction || "",
    cung_ngu_hanh: thien[cungVn]?.cung_ngu_hanh || "",
    lo_thu_num: LO_THU_NUMBERS[cungVn],
    thien_ban: thien[cungVn],
    dia_ban: dia[cungVn],
    mon: mon[cungVn],
    tinh: tinh[cungVn],
    than: than[cungVn],
    is_trung: cungVn === "Trung"
  }));
});

async function cast() {
  loading.value = true;
  error.value = "";
  state.value = null;
  try {
    const r = await fetch("/api/ky-mon/cast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        year: parseInt(form.value.year),
        month: parseInt(form.value.month),
        day: parseInt(form.value.day),
        hour: parseInt(form.value.hour),
        minute: parseInt(form.value.minute),
        method: form.value.method,
        question_text: form.value.question || null
      })
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const j = await r.json();
    state.value = j.ky_mon_state;
  } catch (e) {
    error.value = String(e);
  } finally {
    loading.value = false;
  }
}

function setNow() {
  const d = new Date();
  form.value.year = d.getFullYear();
  form.value.month = d.getMonth() + 1;
  form.value.day = d.getDate();
  form.value.hour = d.getHours();
  form.value.minute = d.getMinutes();
}

const catHungClass = (label) => {
  if (label === "đại cát") return "ch-dai-cat";
  if (label === "cát") return "ch-cat";
  if (label === "trung bình") return "ch-trung";
  if (label === "hung") return "ch-hung";
  if (label === "đại hung") return "ch-dai-hung";
  return "";
};
</script>

<template>
  <div class="ky-mon-panel">
    <header class="km-header">
      <h2>⊞ Kỳ Môn Độn Giáp <span class="km-zh">奇門遁甲</span></h2>
      <p class="km-subtitle">
        Trường phái <strong>Đế vương chi học</strong> — Tổ sư <strong>Lưu Bá Ôn</strong> (1311–1375).
        Bàn 9 cung × 8 môn × 9 tinh × 8 thần phản chiếu cấu trúc năng lượng thời-không.
      </p>
      <p class="km-paradigm">
        <em>Paradigm: ĐỌC ĐỒNG DẠNG — Khí (bàn) → Tính (bản chất khoảnh khắc) → Đối ứng tâm cảnh.
        KHÔNG phải predict cát hung tuyệt đối.</em>
      </p>
    </header>

    <section class="km-form">
      <h3>An cục</h3>
      <div class="km-form-grid">
        <label>Năm <input type="number" v-model.number="form.year" min="1900" max="2100" /></label>
        <label>Tháng <input type="number" v-model.number="form.month" min="1" max="12" /></label>
        <label>Ngày <input type="number" v-model.number="form.day" min="1" max="31" /></label>
        <label>Giờ <input type="number" v-model.number="form.hour" min="0" max="23" /></label>
        <label>Phút <input type="number" v-model.number="form.minute" min="0" max="59" /></label>
        <label>Phương pháp
          <select v-model="form.method">
            <option value="chabu">Chabu 拆補 (giờ, phổ thông)</option>
            <option value="zhirun">Zhirun 置閏 (giờ, lịch nhuận)</option>
            <option value="minute">Phân gia 分家 (phút, chính xác)</option>
            <option value="gpan">Kim Hàm Ngọc Kính 金函玉鏡 (ngày)</option>
          </select>
        </label>
      </div>
      <label class="km-question">Câu hỏi (tuỳ chọn)
        <input type="text" v-model="form.question" placeholder="VD: Khoảnh khắc này phản chiếu điều gì?" />
      </label>
      <div class="km-actions">
        <button type="button" @click="setNow" class="btn-secondary">⏱ Bây giờ</button>
        <button type="button" @click="cast" :disabled="loading" class="btn-primary">
          {{ loading ? "Đang an cục..." : "An cục KMDG" }}
        </button>
      </div>
      <p v-if="error" class="km-error">⚠️ {{ error }}</p>
    </section>

    <section v-if="state" class="km-result">
      <div class="km-info-bar">
        <div class="km-info-item">
          <span class="km-info-label">Tứ trụ</span>
          <span class="km-info-value mono">{{ state.tu_tru_zh }}</span>
        </div>
        <div class="km-info-item">
          <span class="km-info-label">Tiết khí</span>
          <span class="km-info-value">{{ state.tiet_khi_vn }} ({{ state.tiet_khi_zh }})</span>
        </div>
        <div class="km-info-item">
          <span class="km-info-label">Bài cục</span>
          <span class="km-info-value">
            {{ state.bai_cuc?.duong_am }} {{ state.bai_cuc?.cuc_so }} — {{ state.bai_cuc?.nguyen }}
          </span>
        </div>
        <div class="km-info-item">
          <span class="km-info-label">Tuần thủ</span>
          <span class="km-info-value mono">{{ state.tuan_thu }}</span>
        </div>
        <div class="km-info-item" v-if="state.tuan_khong">
          <span class="km-info-label">Tuần không</span>
          <span class="km-info-value mono">Nhật: {{ state.tuan_khong['日空'] }} · Thời: {{ state.tuan_khong['時空'] }}</span>
        </div>
      </div>

      <div class="km-tri-phu" v-if="state.tri_phu_tri_su">
        <h4>Trị Phù – Trị Sử (trục bàn)</h4>
        <div class="km-tri-phu-grid">
          <div><span class="lbl">Trị Phù thiên can:</span> <span class="mono">{{ state.tri_phu_tri_su.tri_phu_can?.join(", ") }}</span></div>
          <div><span class="lbl">Trị Phù tinh-cung:</span> <span class="mono">{{ state.tri_phu_tri_su.tri_phu_tinh_cung?.join(" → ") }}</span></div>
          <div><span class="lbl">Trị Sử môn-cung:</span> <span class="mono">{{ state.tri_phu_tri_su.tri_su_mon_cung?.join(" → ") }}</span></div>
        </div>
      </div>

      <h3 class="km-grid-title">Bàn Kỳ Môn (Lạc Thư cửu cung)</h3>
      <div class="km-grid">
        <div v-for="cell in cungGrid" :key="cell.cung_vn" class="km-cell" :class="{ 'km-trung': cell.is_trung }">
          <div class="km-cell-header">
            <span class="km-cell-num">{{ cell.lo_thu_num }}</span>
            <span class="km-cell-cung">{{ cell.cung_vn }} {{ cell.cung_zh }}</span>
            <span class="km-cell-dir">{{ cell.direction }}</span>
          </div>
          <div class="km-cell-body">
            <div v-if="cell.than" class="km-row" :class="catHungClass(cell.than.cat_hung)">
              <span class="km-row-lbl">Thần</span>
              <span class="km-row-val">{{ cell.than.than_vn }}</span>
              <span class="km-row-cat">{{ cell.than.cat_hung }}</span>
            </div>
            <div v-if="cell.tinh" class="km-row" :class="catHungClass(cell.tinh.cat_hung)">
              <span class="km-row-lbl">Tinh</span>
              <span class="km-row-val">{{ cell.tinh.tinh_vn }}</span>
              <span class="km-row-cat">{{ cell.tinh.cat_hung }}</span>
            </div>
            <div v-if="cell.mon" class="km-row" :class="catHungClass(cell.mon.cat_hung)">
              <span class="km-row-lbl">Môn</span>
              <span class="km-row-val">{{ cell.mon.mon_vn }}</span>
              <span class="km-row-cat">{{ cell.mon.cat_hung }}</span>
            </div>
            <div v-if="cell.thien_ban?.can_vn" class="km-row km-row-can">
              <span class="km-row-lbl">Thiên</span>
              <span class="km-row-val mono">{{ cell.thien_ban.can_vn }} {{ cell.thien_ban.can_zh }}</span>
              <span class="km-row-tag" v-if="cell.thien_ban.is_tam_ky">tam kỳ</span>
              <span class="km-row-tag" v-else-if="cell.thien_ban.is_luc_nghi">lục nghi</span>
            </div>
            <div v-if="cell.dia_ban?.can_vn" class="km-row km-row-can">
              <span class="km-row-lbl">Địa</span>
              <span class="km-row-val mono">{{ cell.dia_ban.can_vn }} {{ cell.dia_ban.can_zh }}</span>
              <span class="km-row-tag" v-if="cell.dia_ban.is_tam_ky">tam kỳ</span>
              <span class="km-row-tag" v-else-if="cell.dia_ban.is_luc_nghi">lục nghi</span>
            </div>
          </div>
        </div>
      </div>

      <p class="km-paradigm-note">
        <strong>Lời nhắc:</strong> {{ state.paradigm_note }}
      </p>
    </section>

    <section v-else class="km-intro">
      <h3>Giới thiệu trường phái</h3>
      <p>
        <strong>Kỳ Môn Độn Giáp</strong> (奇門遁甲) là môn cổ thuật phức tạp nhất Đông phương —
        được mệnh danh "<strong>Đế vương chi học</strong>" vì xưa kia chỉ truyền cho mưu sĩ
        bậc cao (Khương Tử Nha → Trương Lương → Gia Cát Lượng → Lưu Bá Ôn).
      </p>
      <p>
        Bàn Kỳ Môn = bản đồ năng lượng thời-không tại 1 thời điểm cụ thể, gồm:
      </p>
      <ul>
        <li><strong>9 cung Lạc Thư</strong> — vị trí không gian (Bắc/Đông/...)</li>
        <li><strong>8 môn</strong> (Hưu/Sinh/Thương/Đỗ/Cảnh/Tử/Kinh/Khai) — cánh cửa hành động</li>
        <li><strong>9 tinh</strong> (Thiên Bồng/Nhậm/Xung/Phụ/Cầm/Tâm/Trụ/Anh/Nhuế) — loại khí</li>
        <li><strong>8 thần</strong> (Trị Phù/Đằng Xà/Thái Âm/Lục Hợp/Câu Trần/Chu Tước/Cửu Địa/Cửu Thiên) — thái độ vũ trụ</li>
        <li><strong>Thiên bàn + Địa bàn</strong> — 10 thiên can (3 kỳ + 6 nghi + Giáp ẩn)</li>
      </ul>
      <p>
        Nhập thời gian phía trên + bấm <em>An cục KMDG</em> để xem bàn đầu tiên.
      </p>
    </section>
  </div>
</template>

<style scoped>
.ky-mon-panel { max-width: 1200px; margin: 0 auto; padding: 16px; color: #e2e8f0; }
.km-header h2 { margin: 0; font-size: 1.6rem; color: #d4a574; }
.km-zh { font-size: 1.1rem; opacity: 0.7; margin-left: 8px; }
.km-subtitle { margin: 8px 0 4px; color: #cbd5e1; }
.km-paradigm { margin: 4px 0 16px; font-size: 0.9rem; color: #94a3b8; }

.km-form { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.km-form h3 { margin: 0 0 12px; color: #d4a574; font-size: 1.1rem; }
.km-form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; }
.km-form-grid label { display: flex; flex-direction: column; font-size: 0.85rem; color: #94a3b8; }
.km-form-grid input, .km-form-grid select { margin-top: 4px; padding: 6px 8px; background: #0f172a; border: 1px solid #334155; color: #e2e8f0; border-radius: 4px; }
.km-question { display: flex; flex-direction: column; margin-top: 12px; font-size: 0.85rem; color: #94a3b8; }
.km-question input { margin-top: 4px; padding: 6px 8px; background: #0f172a; border: 1px solid #334155; color: #e2e8f0; border-radius: 4px; }
.km-actions { display: flex; gap: 8px; margin-top: 16px; }
.btn-primary { background: #d4a574; color: #1e293b; border: none; padding: 8px 16px; border-radius: 4px; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: transparent; color: #94a3b8; border: 1px solid #334155; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
.km-error { color: #fca5a5; margin-top: 12px; }

.km-result { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; }
.km-info-bar { display: flex; flex-wrap: wrap; gap: 16px; padding: 12px; background: #0f172a; border-radius: 6px; margin-bottom: 16px; }
.km-info-item { display: flex; flex-direction: column; gap: 2px; }
.km-info-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
.km-info-value { font-size: 0.95rem; color: #e2e8f0; }
.mono { font-family: "JetBrains Mono", "SF Mono", monospace; }

.km-tri-phu { background: #0f172a; padding: 12px; border-radius: 6px; margin-bottom: 16px; border-left: 3px solid #d4a574; }
.km-tri-phu h4 { margin: 0 0 8px; color: #d4a574; font-size: 0.95rem; }
.km-tri-phu-grid { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; }
.km-tri-phu-grid .lbl { color: #94a3b8; margin-right: 8px; }

.km-grid-title { color: #d4a574; margin: 16px 0 8px; }
.km-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.km-cell { background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 8px; min-height: 180px; display: flex; flex-direction: column; }
.km-cell.km-trung { background: #1a1f2e; border-color: #d4a574; border-style: dashed; }
.km-cell-header { display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; padding-bottom: 6px; border-bottom: 1px solid #334155; margin-bottom: 6px; }
.km-cell-num { background: #d4a574; color: #1e293b; width: 20px; height: 20px; border-radius: 50%; display: grid; place-items: center; font-weight: 700; font-size: 0.75rem; }
.km-cell-cung { font-weight: 600; color: #e2e8f0; }
.km-cell-dir { color: #64748b; font-size: 0.7rem; }
.km-cell-body { display: flex; flex-direction: column; gap: 3px; font-size: 0.8rem; flex: 1; }
.km-row { display: grid; grid-template-columns: 40px 1fr auto; gap: 4px; align-items: center; padding: 2px 4px; border-radius: 3px; }
.km-row-lbl { color: #64748b; font-size: 0.7rem; }
.km-row-val { color: #e2e8f0; }
.km-row-cat { font-size: 0.65rem; opacity: 0.7; }
.km-row-tag { font-size: 0.6rem; padding: 1px 4px; border-radius: 2px; background: #d4a574; color: #1e293b; }
.km-row-can { background: rgba(212, 165, 116, 0.05); }

.ch-dai-cat { background: rgba(134, 239, 172, 0.12); }
.ch-cat { background: rgba(134, 239, 172, 0.06); }
.ch-trung { background: rgba(148, 163, 184, 0.05); }
.ch-hung { background: rgba(252, 165, 165, 0.06); }
.ch-dai-hung { background: rgba(252, 165, 165, 0.12); }

.km-paradigm-note { margin-top: 16px; padding: 12px; background: rgba(212, 165, 116, 0.08); border-left: 3px solid #d4a574; border-radius: 4px; font-size: 0.85rem; color: #cbd5e1; font-style: italic; }

.km-intro { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; color: #cbd5e1; }
.km-intro h3 { color: #d4a574; margin: 0 0 12px; }
.km-intro p { margin: 8px 0; }
.km-intro ul { margin: 8px 0; padding-left: 20px; }
.km-intro li { margin: 4px 0; }

@media (max-width: 768px) {
  .km-grid { grid-template-columns: 1fr; }
  .km-cell { min-height: auto; }
}
</style>
