<script setup>
import { ref, computed } from "vue";
import { batTuSucKhoeSau } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";

const inputBirth = ref("");
const inputGender = ref("nam");
const inputTimezone = ref("Asia/Ho_Chi_Minh");
const inputChanThuong = ref("");
const inputAge = ref(null);

useActivePersonBirth(inputBirth);

const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");

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

      <button class="hp-btn" :disabled="loading" @click="analyze">
        {{ loading ? "⏳ Đang phân tích..." : "🌿 Đọc cấu trúc thân thể" }}
      </button>
      <p v-if="errorMsg" class="hp-error">{{ errorMsg }}</p>
    </div>

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
</style>
