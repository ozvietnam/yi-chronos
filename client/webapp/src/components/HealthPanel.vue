<script setup>
import { ref, computed } from "vue";
import { batTuSucKhoeSau, dongYFull, dongYMonthlyHealth } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";
import RefBlock from "./RefBlock.vue";

const inputBirth = ref("");
const inputGender = ref("nam");
const inputTimezone = ref("Asia/Ho_Chi_Minh");
const inputChanThuong = ref("");
const inputAge = ref(null);

useActivePersonBirth(inputBirth);

const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");

// Đông Y full (mới)
const dongYData = ref(null);
const dongYLoading = ref(false);
const dongYError = ref("");

// Monthly health view (mới)
const monthlyData = ref(null);
const monthlyLoading = ref(false);
const monthlyError = ref("");
const monthlyYear = ref(2026);

async function analyzeMonthly() {
  if (!inputBirth.value) { monthlyError.value = "Cần ngày-giờ sinh."; return; }
  monthlyLoading.value = true;
  monthlyError.value = "";
  try {
    monthlyData.value = await dongYMonthlyHealth({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
      year: Number(monthlyYear.value),
    });
  } catch (e) {
    monthlyError.value = e.message || String(e);
  } finally {
    monthlyLoading.value = false;
  }
}

async function analyzeDongY() {
  if (!inputBirth.value) { dongYError.value = "Cần ngày-giờ sinh."; return; }
  dongYLoading.value = true;
  dongYError.value = "";
  try {
    dongYData.value = await dongYFull({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
      chanThuong: inputChanThuong.value.trim(),
    });
  } catch (e) {
    dongYError.value = e.message || String(e);
  } finally {
    dongYLoading.value = false;
  }
}

const ELEMENT_GLYPH = { mộc: "木", hỏa: "火", thổ: "土", kim: "金", thủy: "水" };
const ELEMENT_COLOR = {
  mộc: "#5ab07a", hỏa: "#d65a4a", thổ: "#9a7b4a",
  kim: "#c0a878", thủy: "#3a6cb0",
};

const presetChanThuong = [
  "Đứt gân đầu gối — mổ rồi đang hồi phục",
  "Đau lưng kéo dài",
  "Mất ngủ, lo nghĩ nhiều",
  "Tiêu hóa kém, ăn không ngon",
  "Da khô, dị ứng theo mùa",
  "Hay buồn vô cớ, hơi ngắn",
];

async function analyze() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần ngày-giờ sinh.";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  try {
    data.value = await batTuSucKhoeSau({
      birthDatetimeLocal: inputBirth.value,
      timezone: inputTimezone.value,
      gender: inputGender.value,
      chanThuong: inputChanThuong.value.trim(),
      currentAge: inputAge.value ? Number(inputAge.value) : null,
    });
  } catch (e) {
    errorMsg.value = e.message || String(e);
  } finally {
    loading.value = false;
  }
}

function renderMd(s) {
  if (!s) return "";
  let html = String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  html = html.replace(/^# (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h4>$1</h4>");
  html = html.replace(/^### (.+)$/gm, "<h5>$1</h5>");
  html = html.replace(/(?:^|\n)- (.+)/g, "\n<li>$1</li>");
  html = html.replace(/(<li>.*?<\/li>)(\n<li>.*?<\/li>)+/gs, m => "<ul>" + m + "</ul>");
  html = html.replace(/(<li>.*?<\/li>)(?!<\/ul>|<li>)/g, "<ul>$1</ul>");
  html = html.replace(/_([^_\n]+)_/g, "<em>$1</em>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  html = html.split(/\n\n+/).map(p => p.trim()).filter(Boolean)
    .map(p => (p.startsWith("<h") || p.startsWith("<ul") ? p : `<p>${p.replace(/\n/g, "<br>")}</p>`))
    .join("\n");
  return html;
}

const sk = computed(() => data.value?.suc_khoe_sau);
</script>

<template>
  <section class="health-panel">
    <header class="hp-header">
      <h2>🌿 Sức Khỏe Sâu — Bát Tự × Đông Y</h2>
      <p class="hp-intro">
        Đọc cấu trúc thân thể qua paradigm <b>Ngũ hành ↔ Tạng phủ</b> (Hoàng Đế Nội Kinh)
        + Day Master Bát Tự + Nguyên Lưu khí.
      </p>
      <p class="hp-iron-rule">
        🪷 <b>Iron Rule:</b> KHÔNG dự đoán "khi nào hồi phục". Chỉ đọc cấu trúc khí
        + lời khuyên thực tiễn. <em>Đức năng thắng số.</em>
      </p>
    </header>

    <div class="hp-form">
      <div class="hp-row">
        <label>Ngày-giờ sinh
          <input type="datetime-local" v-model="inputBirth" />
        </label>
        <label>Giới
          <select v-model="inputGender">
            <option value="nam">Nam</option>
            <option value="nữ">Nữ</option>
          </select>
        </label>
        <label>Tuổi hiện tại
          <input type="number" v-model="inputAge" placeholder="VD: 37" min="0" max="120" />
        </label>
      </div>

      <label class="hp-ct-label">
        Đang có vấn đề gì với thân thể? <small>(nói thật để em phân tích đúng — em không lưu data)</small>
      </label>
      <textarea v-model="inputChanThuong" rows="3"
        placeholder="VD: đứt gân đầu gối, mổ 5 tháng trước, chân yếu..."></textarea>
      <div class="hp-preset">
        <span>Gợi ý:</span>
        <button v-for="p in presetChanThuong" :key="p" type="button"
          class="hp-preset-btn" @click="inputChanThuong = p">{{ p }}</button>
      </div>

      <div class="hp-btn-group">
        <button class="hp-btn" :disabled="loading" @click="analyze">
          {{ loading ? "⏳ Đang..." : "🌿 Bát Tự × Đông Y (engine cũ)" }}
        </button>
        <button class="hp-btn hp-btn-dy" :disabled="dongYLoading" @click="analyzeDongY">
          {{ dongYLoading ? "⏳ Đang..." : "☯ Đông Y Chuyên Sâu (4 module)" }}
        </button>
        <button class="hp-btn hp-btn-month" :disabled="monthlyLoading" @click="analyzeMonthly">
          {{ monthlyLoading ? "⏳ Đang..." : `📅 Lịch 12 Tháng (${monthlyYear})` }}
        </button>
        <input type="number" v-model="monthlyYear" min="2020" max="2100" class="hp-year-input" />
      </div>
      <p v-if="errorMsg" class="hp-error">{{ errorMsg }}</p>
      <p v-if="dongYError" class="hp-error">{{ dongYError }}</p>
      <p v-if="monthlyError" class="hp-error">{{ monthlyError }}</p>
    </div>

    <!-- ── Lịch 12 Tháng Sức Khỏe ────────────────────────────────────── -->
    <template v-if="monthlyData">
      <header class="hp-dy-header">
        <h3>📅 Lịch Sức Khỏe 12 Tháng — {{ monthlyData.monthly_view.current_year }}</h3>
        <p>{{ monthlyData.monthly_view.summary.tong_quat }}</p>
      </header>

      <article class="hp-card" style="border-left-color: #d4af37;">
        <h3>🎯 Chiến lược cả năm</h3>
        <ul>
          <li v-for="(s, i) in monthlyData.monthly_view.summary.loi_khuyen_chien_luoc" :key="'s'+i">{{ s }}</li>
        </ul>
      </article>

      <article v-if="monthlyData.monthly_view.summary.thang_can_trong.length" class="hp-card" style="border-left-color: #e85a78;">
        <h3>⚠️ Tháng cẩn trọng</h3>
        <ul>
          <li v-for="(t, i) in monthlyData.monthly_view.summary.thang_can_trong" :key="'r'+i">{{ t }}</li>
        </ul>
      </article>

      <article v-if="monthlyData.monthly_view.summary.thang_tot_nhat.length" class="hp-card" style="border-left-color: #5ab07a;">
        <h3>✨ Tháng tốt nhất</h3>
        <ul>
          <li v-for="(t, i) in monthlyData.monthly_view.summary.thang_tot_nhat" :key="'g'+i">{{ t }}</li>
        </ul>
      </article>

      <article class="hp-card">
        <h3>🗓 12 Tháng chi tiết</h3>
        <div class="hp-month-grid">
          <div v-for="m in monthlyData.monthly_view.months" :key="m.month_index" class="hp-month-cell"
            :data-level="m.level">
            <div class="hp-month-head">
              <span class="hp-month-lvl">{{ m.level }}</span>
              <strong>T{{ m.month_index }}</strong>
              <small>{{ m.tiet_khi }}</small>
            </div>
            <div class="hp-month-can-chi">{{ m.stem }} {{ m.branch }} <small>({{ m.branch_element }})</small></div>
            <div class="hp-month-meaning">{{ m.level_meaning }}</div>
            <div class="hp-month-tang">🩺 {{ m.tang_dac_biet }}</div>
            <div class="hp-month-ts">🔢 <code>{{ m.tuong_so_goi_y }}</code></div>
            <div v-if="m.cross_chan_thuong" class="hp-month-cross">{{ m.cross_chan_thuong }}</div>
            <details class="hp-month-detail">
              <summary>Chi tiết</summary>
              <div><b>Giờ vượng:</b> {{ m.gio_vuong }}</div>
              <div><b>Nên:</b><ul><li v-for="(h,j) in m.hanh_dong" :key="j">{{ h }}</li></ul></div>
              <div><b>Tránh:</b><ul><li v-for="(t,j) in m.tranh" :key="j">{{ t }}</li></ul></div>
            </details>
          </div>
        </div>
      </article>

      <p class="hp-iron-rule-footer">{{ monthlyData.monthly_view.paradigm_note }}</p>
    </template>

    <!-- ── Đông Y Full (4 module mới) ─────────────────────────────────── -->
    <template v-if="dongYData">
      <header class="hp-dy-header">
        <h3>☯ Đông Y Chuyên Sâu</h3>
        <p>📚 Source: <em>"Chữa bệnh theo Chu Dịch"</em> (Lý Ngọc Sơn + Lý Kiện Dân) + Hoàng Đế Nội Kinh</p>
      </header>

      <!-- 1. Tạng phủ chẩn đoán -->
      <article class="hp-card hp-dy-card" style="border-left-color: #5ab07a;">
        <h3>🩺 Tạng phủ chẩn đoán</h3>
        <div v-if="dongYData.tang_phu_chan_doan.result.primary_que">
          <p><b>Quẻ chính:</b>
            <span class="hp-big-que">{{ dongYData.tang_phu_chan_doan.result.matched_que_list[0].hieu }}</span>
            <b>{{ dongYData.tang_phu_chan_doan.result.primary_que }}</b>
            (số {{ dongYData.tang_phu_chan_doan.result.matched_que_list[0].so_tien_thien }})
            → Tạng <b>{{ dongYData.tang_phu_chan_doan.result.primary_tang }}</b>
            (hành {{ dongYData.tang_phu_chan_doan.result.primary_hanh }})</p>
          <p><b>Tất cả quẻ liên quan:</b></p>
          <ul>
            <li v-for="(m, i) in dongYData.tang_phu_chan_doan.result.matched_que_list" :key="i">
              <span class="hp-big-que">{{ m.hieu }}</span> <b>{{ m.que }}</b>
              ({{ m.so_tien_thien }}, {{ m.hanh }}) → {{ m.tang }} chủ <em>{{ m.co_the }}</em>
            </li>
          </ul>
          <p><b>Biểu hiện khi yếu:</b></p>
          <ul>
            <li v-for="(b, i) in dongYData.tang_phu_chan_doan.result.primary_bieu_hien_yeu" :key="'bh'+i">{{ b }}</li>
          </ul>
          <p><b>Liên đới qua sinh-khắc:</b></p>
          <ul>
            <li v-for="(r, i) in dongYData.tang_phu_chan_doan.result.related_tang_via_sinh_khac" :key="'r'+i">
              <b>{{ r.relation.toUpperCase() }}</b>: {{ r.tang }} (hành {{ r.hanh }}) — {{ r.y_nghia }}
            </li>
          </ul>
        </div>
      </article>

      <!-- 2. Kinh Lạc -->
      <article class="hp-card hp-dy-card" style="border-left-color: #5b8ee5;" v-if="dongYData.kinh_lac.result">
        <h3>🌐 Kinh Lạc — {{ dongYData.kinh_lac.result.kinh_chinh }}</h3>
        <p><b>Giờ vượng:</b> {{ dongYData.kinh_lac.result.gio_duong }}
          — đây là giờ khí huyết chảy mạnh, dưỡng tốt nhất</p>
        <p><b>Cặp biểu-lý:</b> {{ dongYData.kinh_lac.result.kinh_chinh }} ↔ {{ dongYData.kinh_lac.result.cap_doi_bieu_ly }}</p>
        <p><b>Chức năng:</b> {{ dongYData.kinh_lac.result.kinh_info.function }}</p>
        <p><b>Triệu chứng bệnh:</b> {{ dongYData.kinh_lac.result.kinh_info.trieu_chung_benh.join(", ") }}</p>
      </article>

      <!-- 3. Âm dương cân bằng -->
      <article class="hp-card hp-dy-card" style="border-left-color: #d4af37;">
        <h3>☯ Âm Dương Cân Bằng</h3>
        <div class="hp-ad-grid">
          <div><small>Âm/Dương</small><strong>{{ dongYData.am_duong.result.am_count }} / {{ dongYData.am_duong.result.duong_count }}</strong>
            <em>{{ dongYData.am_duong.result.am_duong_ratio }}</em></div>
          <div><small>Nhiệt/Hàn</small><strong>{{ dongYData.am_duong.result.nhiet_count }} / {{ dongYData.am_duong.result.han_count }}</strong>
            <em>{{ dongYData.am_duong.result.nhiet_han_balance }}</em></div>
        </div>
        <p><b>Nguyên âm / Nguyên dương:</b> {{ dongYData.am_duong.result.nguyen_am_vs_nguyen_duong }}</p>
        <div class="hp-ad-cols">
          <div><h5>🍵 Thực phẩm</h5>
            <ul><li v-for="(a,i) in dongYData.am_duong.result.advice_thuc_pham" :key="'tp'+i">{{ a }}</li></ul></div>
          <div><h5>🚶 Vận động</h5>
            <ul><li v-for="(a,i) in dongYData.am_duong.result.advice_van_dong" :key="'vd'+i">{{ a }}</li></ul></div>
          <div><h5>🌙 Giấc ngủ</h5>
            <ul><li v-for="(a,i) in dongYData.am_duong.result.advice_giac_ngu" :key="'gn'+i">{{ a }}</li></ul></div>
        </div>
      </article>

      <!-- 4. Liệu pháp tượng số -->
      <article class="hp-card hp-dy-card" style="border-left-color: #c25a78;">
        <h3>🔢 Liệu Pháp Tượng Số (paradigm cổ độc đáo)</h3>
        <div class="hp-ts-primary">
          <span class="hp-ts-number">{{ dongYData.lieu_phap_tuong_so.result.primary_formula.tuong_so }}</span>
          <div>
            <b>{{ dongYData.lieu_phap_tuong_so.result.primary_formula.y_nghia }}</b>
            <p>{{ dongYData.lieu_phap_tuong_so.result.primary_formula.phan_tich }}</p>
          </div>
        </div>
        <p><b>Chỉ định:</b></p>
        <ul>
          <li v-for="(c, i) in dongYData.lieu_phap_tuong_so.result.primary_formula.chi_dinh" :key="'cd'+i">{{ c }}</li>
        </ul>
        <p class="hp-ts-trich"><em>{{ dongYData.lieu_phap_tuong_so.result.primary_formula.trich_sach }}</em></p>
        <div class="hp-ts-huongdan" v-html="renderMd(dongYData.lieu_phap_tuong_so.result.huong_dan_doc)"></div>
        <div class="hp-ts-warning">{{ dongYData.lieu_phap_tuong_so.result.iron_rule_warning }}</div>

        <div v-if="dongYData.lieu_phap_tuong_so.result.matched_formulas.length > 1">
          <p><b>Công thức khác liên quan:</b></p>
          <ul>
            <li v-for="(f, i) in dongYData.lieu_phap_tuong_so.result.matched_formulas.slice(1)" :key="'f'+i">
              <b>{{ f.tuong_so }}</b>: {{ f.y_nghia }}
            </li>
          </ul>
        </div>
      </article>

      <p class="hp-iron-rule-footer">{{ dongYData.iron_rule_note }}</p>
      <RefBlock kind="cite">{{ dongYData.sources.join(" · ") }}</RefBlock>
    </template>

    <template v-if="sk">
      <!-- Snapshot -->
      <article class="hp-card hp-snapshot" :style="{ borderLeftColor: ELEMENT_COLOR[sk.day_master_element] }">
        <h3>{{ ELEMENT_GLYPH[sk.day_master_element] }} Tạng phủ bẩm sinh</h3>
        <div class="hp-snapshot-grid">
          <div>
            <small>Day Master</small>
            <strong>{{ sk.day_master_element.toUpperCase() }}</strong>
          </div>
          <div>
            <small>Tạng chủ</small>
            <strong>{{ sk.constitution_tang }}</strong>
          </div>
          <div>
            <small>Chủ về (Thể)</small>
            <strong>{{ sk.constitution_the }}</strong>
          </div>
          <div>
            <small>Cường độ</small>
            <strong :data-strength="sk.constitution_strength">{{ sk.constitution_strength.toUpperCase() }}</strong>
          </div>
        </div>
      </article>

      <!-- Chấn thương analysis -->
      <article class="hp-card hp-chan-thuong" v-if="sk.chan_thuong_input">
        <h3>🩹 Chấn thương đang có</h3>
        <p class="hp-ct-input"><em>"{{ sk.chan_thuong_input }}"</em></p>
        <ul v-if="sk.chan_thuong_analysis.matches.length">
          <li v-for="(m, i) in sk.chan_thuong_analysis.matches" :key="i">
            <strong>{{ m.keyword }}</strong> <span class="hp-tag" :style="{background: ELEMENT_COLOR[m.element.split(' ')[0]] || '#888'}">{{ m.element }}</span>
            <p>{{ m.y_nghia }}</p>
          </li>
        </ul>
        <p v-else class="hp-empty">Engine chưa match keyword — phân tích tổng thể.</p>
      </article>

      <!-- Tạng cần dưỡng -->
      <article class="hp-card hp-weakness">
        <h3>⚠️ Tạng cần dưỡng ({{ sk.weakness_tang_list.length }})</h3>
        <div v-for="(w, i) in sk.weakness_tang_list" :key="i" class="hp-weakness-item"
          :style="{ borderLeftColor: ELEMENT_COLOR[w.element] }">
          <h4>{{ ELEMENT_GLYPH[w.element] }} {{ w.tang }} <small>(chủ {{ w.the }})</small></h4>
          <p class="hp-reason">{{ w.reason }}</p>
          <ul class="hp-bieu-hien">
            <li v-for="(b, j) in w.bieu_hien" :key="j">{{ b }}</li>
          </ul>
        </div>
      </article>

      <!-- Lời khuyên thực tiễn -->
      <article class="hp-card hp-advice">
        <h3>🍵 Lời khuyên thực tiễn</h3>
        <div class="hp-advice-grid">
          <div class="hp-col hp-duong">
            <h4>✅ Nên ăn</h4>
            <ul>
              <li v-for="(f, i) in sk.dietary_duong" :key="i">{{ f }}</li>
            </ul>
          </div>
          <div class="hp-col hp-tranh">
            <h4>❌ Tránh</h4>
            <ul>
              <li v-for="(f, i) in sk.dietary_tranh" :key="i">{{ f }}</li>
            </ul>
          </div>
          <div class="hp-col hp-vd">
            <h4>🚶 Vận động + giờ</h4>
            <ul>
              <li v-for="(v, i) in sk.lifestyle" :key="i">{{ v }}</li>
            </ul>
          </div>
        </div>
      </article>

      <!-- Đại vận hồi phục -->
      <article class="hp-card hp-dv">
        <h3>🔄 Vận hồi phục</h3>
        <p>{{ sk.dai_van_hoi_phuc }}</p>
      </article>

      <!-- Iron rule -->
      <p class="hp-iron-rule-footer">{{ sk.iron_rule_note }}</p>

      <!-- Full markdown -->
      <details class="hp-md-details">
        <summary>📜 Xem markdown đầy đủ</summary>
        <div class="hp-md" v-html="renderMd(data.markdown)"></div>
      </details>
    </template>
  </section>
</template>

<style scoped>
.health-panel {
  display: flex; flex-direction: column; gap: 16px; max-width: 980px; margin: 0 auto;
}
.hp-header h2 {
  color: #5ab07a; margin: 0 0 8px 0;
  font-size: 24px; font-weight: 600;
}
.hp-intro { font-size: 14px; color: rgba(230,238,245,0.85); margin: 0 0 6px 0; }
.hp-iron-rule {
  font-size: 13px; color: rgba(245,230,177,0.85);
  background: rgba(245,230,177,0.06);
  padding: 8px 12px; border-left: 3px solid #d4af37;
  border-radius: 4px; margin: 0;
}
.hp-form {
  background: rgba(20,20,40,0.4); padding: 16px; border-radius: 8px;
  display: flex; flex-direction: column; gap: 12px;
}
.hp-row { display: flex; gap: 12px; flex-wrap: wrap; }
.hp-row label, .hp-ct-label {
  display: flex; flex-direction: column; gap: 4px;
  font-size: 13px; flex: 1; min-width: 180px;
  color: rgba(230,238,245,0.85);
}
.hp-row input, .hp-row select, .hp-form textarea {
  padding: 8px 10px; border: 1px solid rgba(230,238,245,0.2);
  background: rgba(10,10,25,0.6); color: #e6eef5; border-radius: 4px;
  font-size: 14px;
}
.hp-form textarea { resize: vertical; font-family: inherit; }
.hp-preset { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; font-size: 12px; }
.hp-preset-btn {
  background: rgba(90,176,122,0.15); color: #8be0a3;
  border: 1px solid rgba(90,176,122,0.3); padding: 4px 8px; border-radius: 12px;
  font-size: 12px; cursor: pointer;
}
.hp-preset-btn:hover { background: rgba(90,176,122,0.3); }
.hp-btn {
  background: linear-gradient(135deg, #5ab07a 0%, #3a6cb0 100%);
  color: white; border: none; padding: 12px 22px; border-radius: 6px;
  font-weight: 600; cursor: pointer; font-size: 15px;
  align-self: flex-start;
}
.hp-btn:disabled { opacity: 0.5; cursor: wait; }
.hp-error { color: #e85a78; font-size: 13px; }

.hp-card {
  background: rgba(20,20,40,0.4); padding: 16px 18px; border-radius: 8px;
  border-left: 3px solid #5ab07a;
}
.hp-card h3 { color: #f5e6b1; margin: 0 0 12px 0; font-size: 17px; }
.hp-card h4 { color: #c0e8d0; margin: 8px 0; font-size: 15px; }
.hp-snapshot-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;
}
.hp-snapshot-grid > div {
  background: rgba(10,10,25,0.5); padding: 10px; border-radius: 4px;
  text-align: center;
}
.hp-snapshot-grid small { display: block; color: rgba(230,238,245,0.6); font-size: 11px; }
.hp-snapshot-grid strong { display: block; margin-top: 4px; color: #f5e6b1; font-size: 15px; }
.hp-snapshot-grid strong[data-strength="yếu"] { color: #e85a78; }
.hp-snapshot-grid strong[data-strength="vừa"] { color: #e8c95a; }
.hp-snapshot-grid strong[data-strength="mạnh"] { color: #5ab07a; }

.hp-chan-thuong { border-left-color: #e85a78; }
.hp-ct-input { font-size: 14px; color: rgba(245,230,177,0.9); }
.hp-tag { font-size: 11px; padding: 2px 8px; margin: 0 6px; border-radius: 3px; color: white; }
.hp-empty { font-style: italic; color: rgba(230,238,245,0.6); }

.hp-weakness { border-left-color: #e8c95a; }
.hp-weakness-item {
  background: rgba(10,10,25,0.5); padding: 10px 14px; border-radius: 4px;
  border-left: 2px solid #e8c95a; margin-bottom: 10px;
}
.hp-reason { font-size: 13px; color: rgba(230,238,245,0.7); margin: 4px 0 8px 0; }
.hp-bieu-hien { padding-left: 18px; }
.hp-bieu-hien li { font-size: 13px; margin: 2px 0; }

.hp-advice-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.hp-col ul { padding-left: 16px; font-size: 13px; }
.hp-col li { margin-bottom: 4px; line-height: 1.5; }
.hp-duong h4 { color: #5ab07a; }
.hp-tranh h4 { color: #e85a78; }
.hp-vd h4 { color: #3a8eb0; }

.hp-dv { border-left-color: #d4af37; }
.hp-iron-rule-footer {
  font-size: 13px; color: rgba(245,230,177,0.85);
  background: rgba(245,230,177,0.06); padding: 10px 14px; border-radius: 4px;
  border-left: 3px solid #d4af37;
}
.hp-md-details summary {
  cursor: pointer; font-weight: 600; color: rgba(245,230,177,0.8);
  padding: 8px 0;
}
.hp-md {
  margin-top: 8px; padding: 16px; background: rgba(10,10,25,0.6);
  border-radius: 6px; font-size: 13px; line-height: 1.7;
  max-height: 600px; overflow-y: auto;
}
.hp-md :deep(h1) { font-size: 20px; color: #5ab07a; }
.hp-md :deep(h2) { font-size: 17px; color: #f5e6b1; margin-top: 20px; }
.hp-md :deep(h3) { font-size: 15px; color: #c0e8d0; }
.hp-md :deep(ul) { padding-left: 20px; }

/* ── Đông Y Full ────────────────────────────────────────────────────── */
.hp-btn-group { display: flex; gap: 10px; flex-wrap: wrap; }
.hp-btn-dy { background: linear-gradient(135deg, #c25a78 0%, #d4af37 100%); }
.hp-dy-header { margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(245,230,177,0.15); }
.hp-dy-header h3 { color: #d4af37; margin: 0; font-size: 20px; }
.hp-dy-header p { font-size: 13px; color: rgba(230,238,245,0.7); margin: 4px 0 0 0; }
.hp-dy-card h3 { color: #f5e6b1; font-size: 16px; }
.hp-dy-card p { font-size: 13px; margin: 6px 0; }
.hp-dy-card ul { padding-left: 18px; font-size: 13px; }
.hp-big-que { font-size: 22px; margin: 0 6px; color: #d4af37; }
.hp-ad-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 10px;
}
.hp-ad-grid > div {
  background: rgba(10,10,25,0.5); padding: 10px; border-radius: 4px; text-align: center;
}
.hp-ad-grid small { display: block; color: rgba(230,238,245,0.6); font-size: 11px; }
.hp-ad-grid strong { display: block; color: #f5e6b1; font-size: 16px; margin: 4px 0; }
.hp-ad-grid em { font-size: 12px; color: rgba(245,230,177,0.7); }
.hp-ad-cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
.hp-ad-cols h5 { color: #c0e8d0; font-size: 13px; margin: 4px 0; }
.hp-ad-cols ul { font-size: 12px; }
.hp-ts-primary {
  display: flex; gap: 16px; align-items: center;
  background: rgba(194,90,120,0.1); padding: 12px; border-radius: 6px; margin: 10px 0;
}
.hp-ts-number {
  font-size: 36px; font-weight: 700; color: #d4af37; font-family: monospace;
  background: rgba(212,175,55,0.1); padding: 8px 16px; border-radius: 6px;
  border: 1px solid #d4af37;
}
.hp-ts-primary > div { flex: 1; }
.hp-ts-primary > div b { color: #f5e6b1; }
.hp-ts-primary > div p { font-size: 12px; color: rgba(230,238,245,0.7); margin: 4px 0 0 0; }
.hp-ts-trich { font-size: 12px; color: rgba(245,230,177,0.7); padding: 6px; border-left: 2px solid #c25a78; }
.hp-ts-huongdan {
  background: rgba(10,10,25,0.5); padding: 10px; border-radius: 4px;
  font-size: 13px; margin: 10px 0;
}
.hp-ts-warning {
  font-size: 12px; padding: 8px 12px;
  background: rgba(232,90,120,0.1); color: #e85a78;
  border-left: 3px solid #e85a78; border-radius: 4px; margin-top: 10px;
}

/* ── Lịch 12 Tháng ──────────────────────────────────────────────────── */
.hp-btn-month { background: linear-gradient(135deg, #d4af37 0%, #5b8ee5 100%); }
.hp-year-input {
  width: 80px; padding: 8px 10px; border: 1px solid rgba(230,238,245,0.2);
  background: rgba(10,10,25,0.6); color: #e6eef5; border-radius: 4px; font-size: 14px;
}
.hp-month-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px; margin-top: 12px;
}
.hp-month-cell {
  background: rgba(10,10,25,0.5); padding: 10px 12px; border-radius: 6px;
  border-left: 3px solid #888; font-size: 12px;
}
.hp-month-cell[data-level="🟢"] { border-left-color: #5ab07a; background: rgba(90,176,122,0.08); }
.hp-month-cell[data-level="🟡"] { border-left-color: #e8c95a; background: rgba(232,201,90,0.08); }
.hp-month-cell[data-level="🟠"] { border-left-color: #d68f4a; background: rgba(214,143,74,0.08); }
.hp-month-cell[data-level="🔴"] { border-left-color: #e85a78; background: rgba(232,90,120,0.12); }
.hp-month-head { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.hp-month-head strong { color: #f5e6b1; font-size: 14px; }
.hp-month-head small { color: rgba(230,238,245,0.6); font-size: 11px; }
.hp-month-lvl { font-size: 16px; }
.hp-month-can-chi { color: #d4af37; font-size: 13px; margin-bottom: 4px; }
.hp-month-meaning { color: rgba(230,238,245,0.85); margin-bottom: 4px; font-size: 12px; }
.hp-month-tang { color: #8be0a3; font-size: 11px; margin-bottom: 2px; }
.hp-month-ts { font-size: 11px; }
.hp-month-ts code { background: rgba(212,175,55,0.15); color: #f5e6b1; padding: 1px 6px; border-radius: 3px; }
.hp-month-cross {
  margin-top: 6px; padding: 6px 8px; background: rgba(232,90,120,0.08);
  border-left: 2px solid #e85a78; font-size: 11px; color: #f5cbd0;
}
.hp-month-detail { margin-top: 6px; font-size: 11px; }
.hp-month-detail summary { cursor: pointer; color: rgba(245,230,177,0.7); }
.hp-month-detail ul { padding-left: 16px; margin: 4px 0; }
.hp-month-detail li { margin: 2px 0; }
</style>
