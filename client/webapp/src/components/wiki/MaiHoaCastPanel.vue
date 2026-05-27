<script setup>
/**
 * MaiHoaCastPanel — gieo quẻ Mai Hoa với philosophy + Master attribution.
 *
 * Cải tiến từ trang Mai Hoa cũ:
 *  - Block Ngoạn Pháp (TÂM là gốc) — quote Thiệu Khang Tiết
 *  - Mnemonic 8 quẻ (tam liên, lục đoạn...)
 *  - Quẻ với attribution + cross-ref Wiki concept
 *  - Save Prediction button → tracking để review sau
 *  - Library of 4 case studies cổ điển
 */
import { ref, computed, onMounted } from "vue";
import HexagramSvg from "./diagrams/HexagramSvg.vue";
import { saveCasting, activePerson } from "../../stores/userDataStore.js";
import { isAuthenticated } from "../../stores/authStore.js";

const CHI_OPTIONS = [
  "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
  "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
];

// Mnemonics 8 quẻ (sách trang 32)
const QUE_MNEMONICS = {
  Càn:  { hexa: "☰", mn: "Tam liên",      desc: "3 vạch liền — Trời, cha, Kim, Tây Bắc (Hậu Thiên)" },
  Đoài: { hexa: "☱", mn: "Thượng khuyết", desc: "Khuyết trên — Đầm, thiếu nữ, Kim, Tây" },
  Ly:   { hexa: "☲", mn: "Trung hư",      desc: "Rỗng giữa — Lửa/Mặt trời, trung nữ, Hoả, Nam" },
  Chấn: { hexa: "☳", mn: "Ngưỡng vu",     desc: "Ngửa ống — Sấm, trưởng nam, Mộc, Đông" },
  Tốn:  { hexa: "☴", mn: "Hạ đoạn",       desc: "Đứt dưới — Gió, trưởng nữ, Mộc, Đông Nam" },
  Khảm: { hexa: "☵", mn: "Trung mãn",     desc: "Đầy giữa — Nước/Trăng, trung nam, Thuỷ, Bắc" },
  Cấn:  { hexa: "☶", mn: "Phúc uyển",     desc: "Úp bát — Núi, thiếu nam, Thổ, Đông Bắc" },
  Khôn: { hexa: "☷", mn: "Lục đoạn",      desc: "6 đoạn — Đất, mẹ, Thổ, Tây Nam" },
};

// Quái Khí Vượng theo mùa (sách trang 24-25)
function quaiKhiSeason(month) {
  if ([1, 2].includes(month)) return { season: "Xuân", vuong: ["Chấn", "Tốn"], suy: ["Khôn", "Cấn"] };
  if ([4, 5].includes(month)) return { season: "Hạ", vuong: ["Ly"], suy: ["Càn", "Đoài"] };
  if ([7, 8].includes(month)) return { season: "Thu", vuong: ["Càn", "Đoài"], suy: ["Chấn", "Tốn"] };
  if ([10, 11].includes(month)) return { season: "Đông", vuong: ["Khảm"], suy: ["Ly"] };
  if ([3, 6, 9, 12].includes(month)) return { season: "Tháng đất (Thìn/Mùi/Tuất/Sửu)", vuong: ["Khôn", "Cấn"], suy: ["Khảm"] };
  return { season: "?", vuong: [], suy: [] };
}

const yearChi = ref("Ngọ");  // 2026 = Bính Ngọ
const month = ref(new Date().getMonth() + 1);
const day = ref(new Date().getDate());
const hourChi = ref(getCurrentHourChi());
const userIntent = ref("");
const intentKey = ref("general");
const intents = ref([]);
// ⭐ 11 chiêm chuyên đề (Mai Hoa Q2)
const chiemTopicKey = ref("");
const chiemTopics = ref([]);
const result = ref(null);
const interpretation = ref(null);
const loading = ref(false);
const error = ref("");
const savedPredId = ref(null);
const tamNote = ref("");

// ⭐ 2026-05-27 — Luận sâu Kinh Dịch (LLM + citation RAG)
const luanSau = ref(null);          // { narrative, provider, citations_used, ... }
const luanSauLoading = ref(false);
const luanSauError = ref("");
const userQuestion = ref("");

// ⭐ Phase A 18/5 — BƯỚC 3 + 4 Tổ sư (Q3 tr.112-114)
const externalOmen = ref("");  // ngoại ứng — hiện tượng bất thường lúc khởi quẻ
const posture = ref("");        // tư thế: nằm/ngồi/đứng/đi/chạy
const POSTURE_OPTIONS = [
  { value: "",      label: "(chưa rõ)" },
  { value: "nằm",   label: "Nằm — chậm nhất" },
  { value: "ngồi",  label: "Ngồi — chậm trễ" },
  { value: "đứng",  label: "Đứng — trung bình" },
  { value: "đi",    label: "Đi bộ — nhanh" },
  { value: "chạy",  label: "Chạy — rất nhanh" },
];

function getCurrentHourChi() {
  const h = new Date().getHours();
  // 23-1=Tý, 1-3=Sửu, 3-5=Dần, 5-7=Mão, 7-9=Thìn, 9-11=Tỵ
  // 11-13=Ngọ, 13-15=Mùi, 15-17=Thân, 17-19=Dậu, 19-21=Tuất, 21-23=Hợi
  if (h >= 23 || h < 1) return "Tý";
  const map = ["Sửu","Sửu","Dần","Dần","Mão","Mão","Thìn","Thìn","Tỵ","Tỵ",
               "Ngọ","Ngọ","Mùi","Mùi","Thân","Thân","Dậu","Dậu","Tuất","Tuất","Hợi","Hợi"];
  return map[h - 1] || "Tý";
}

async function cast(saveIt = false) {
  loading.value = true;
  error.value = "";
  interpretation.value = null;
  try {
    // 1. Cast + optionally save
    const r = await fetch("/api/yi-wiki/cast/niennguyetnhatthoi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        year_chi: yearChi.value,
        month: month.value,
        day: day.value,
        hour_chi: hourChi.value,
        user_intent: userIntent.value,
        save_prediction: saveIt,
      }),
    });
    const d = await r.json();
    if (d.status !== "ok") {
      error.value = d.message || "Lỗi gieo quẻ";
      return;
    }
    result.value = d;
    if (saveIt && d.prediction_id) {
      savedPredId.value = d.prediction_id;
    }
    // 2. Auto-interpret 5 steps with intent + BƯỚC 3 (ngoại ứng) + BƯỚC 4 (tư thế)
    const ir = await fetch("/api/yi-wiki/interpret", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        year_chi: yearChi.value,
        month: month.value,
        day: day.value,
        hour_chi: hourChi.value,
        intent: intentKey.value,
        external_omen: externalOmen.value || null,
        posture: posture.value || null,
        chiem_topic_key: chiemTopicKey.value || "",
      }),
    });
    const idata = await ir.json();
    if (idata.status === "ok") {
      interpretation.value = idata;
    }
    // Auto-save to user_castings (silent — only if logged in)
    if (isAuthenticated.value) {
      const primary = d.derived?.primary || d.primary || {};
      const verdict = primary.name_vi
        ? `Quẻ chính: ${primary.name_vi}${primary.dong_hao ? ` · động hào ${primary.dong_hao}` : ""}`
        : "";
      saveCasting({
        method: "mai_hoa",
        subject_person_key: activePerson.value?.person_key || null,
        question: userIntent.value || null,
        input_json: {
          year_chi: yearChi.value, month: month.value,
          day: day.value, hour_chi: hourChi.value,
          intent: intentKey.value,
          external_omen: externalOmen.value || null,
          posture: posture.value || null,
          chiem_topic_key: chiemTopicKey.value || "",
        },
        result_json: { cast: d, interpretation: idata },
        verdict: verdict.trim() || null,
      });
    }
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

// ⭐ Luận sâu Kinh Dịch — LLM + citation RAG (2026-05-27)
async function callLuanSau() {
  luanSauError.value = "";
  luanSauLoading.value = true;
  luanSau.value = null;
  try {
    const r = await fetch("/api/yi-wiki/maihoa/luan-sau-kinhdich", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        year_chi: yearChi.value,
        month: month.value,
        day: day.value,
        hour_chi: hourChi.value,
        intent: intent.value || "general",
        external_omen: externalOmen.value || null,
        posture: posture.value || null,
        user_question: userQuestion.value || null,
      }),
    });
    const d = await r.json();
    if (d.status === "ok") {
      luanSau.value = d;
    } else {
      luanSauError.value = d.detail || d.message || "Luận sâu thất bại";
    }
  } catch (e) {
    luanSauError.value = String(e.message || e);
  } finally {
    luanSauLoading.value = false;
  }
}

async function loadIntents() {
  try {
    const r = await fetch("/api/yi-wiki/intents");
    const d = await r.json();
    if (d.status === "ok") intents.value = d.intents;
  } catch (e) {}
}
loadIntents();

async function loadChiemTopics() {
  try {
    const r = await fetch("/api/yi-wiki/chiem-topics");
    const d = await r.json();
    if (d.status === "ok") chiemTopics.value = d.topics;
  } catch (e) {}
}
loadChiemTopics();

const cauChuData = ref(null);
async function loadCauChu() {
  try {
    const r = await fetch("/api/yi-wiki/cau-chu");
    const d = await r.json();
    if (d.status === "ok") cauChuData.value = d;
  } catch (e) {}
}
loadCauChu();

async function saveTamNote() {
  if (!savedPredId.value || !tamNote.value.trim()) return;
  await fetch(`/api/yi-wiki/predictions/${savedPredId.value}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tam_note: tamNote.value }),
  });
  alert("Đã lưu tâm note. Em sẽ nhắc anh review sau 7 ngày.");
}

const quaiKhi = computed(() => quaiKhiSeason(month.value));

function quaiBadge(que) {
  if (!quaiKhi.value) return null;
  if (quaiKhi.value.vuong.includes(que)) return { label: "VƯỢNG", color: "#34d399" };
  if (quaiKhi.value.suy.includes(que)) return { label: "SUY", color: "#f87171" };
  return null;
}

// Phân tích Thể-Dụng sơ bộ (chỉ pattern, không đoán)
const theDung = computed(() => {
  if (!result.value) return null;
  const moving = result.value.moving_line;
  // Hào 1-3 = quẻ dưới, 4-6 = quẻ trên
  const dungIsUpper = moving >= 4;
  return {
    the: dungIsUpper ? result.value.chinh_quai.lower : result.value.chinh_quai.upper,
    dung: dungIsUpper ? result.value.chinh_quai.upper : result.value.chinh_quai.lower,
    position: dungIsUpper ? "thượng" : "hạ",
  };
});

const NGU_HANH = {
  Càn: "Kim", Đoài: "Kim",
  Khôn: "Thổ", Cấn: "Thổ",
  Chấn: "Mộc", Tốn: "Mộc",
  Khảm: "Thuỷ", Ly: "Hoả",
};

const SINH_KHAC = {
  // sinh
  "Kim->Thuỷ": "sinh", "Thuỷ->Mộc": "sinh", "Mộc->Hoả": "sinh",
  "Hoả->Thổ": "sinh", "Thổ->Kim": "sinh",
  // khắc
  "Kim->Mộc": "khắc", "Mộc->Thổ": "khắc", "Thổ->Thuỷ": "khắc",
  "Thuỷ->Hoả": "khắc", "Hoả->Kim": "khắc",
};

const relation = computed(() => {
  if (!theDung.value) return null;
  const theHanh = NGU_HANH[theDung.value.the];
  const dungHanh = NGU_HANH[theDung.value.dung];
  if (theHanh === dungHanh) return { type: "tỉ-hoà", text: "Thể-Dụng tỉ hoà (cùng hành) → bình", color: "#94a3b8" };
  const dt = SINH_KHAC[`${dungHanh}->${theHanh}`];
  const td = SINH_KHAC[`${theHanh}->${dungHanh}`];
  if (dt === "sinh") return { type: "tốt-nhất", text: `Dụng sinh Thể (${dungHanh}→${theHanh}) → tốt nhất`, color: "#34d399" };
  if (td === "khắc") return { type: "tốt", text: `Thể khắc Dụng (${theHanh}→${dungHanh}) → tốt (ta thắng)`, color: "#22d3ee" };
  if (td === "sinh") return { type: "mất-sức", text: `Thể sinh Dụng (${theHanh}→${dungHanh}) → mất sức`, color: "#fbbf24" };
  if (dt === "khắc") return { type: "xấu", text: `Dụng khắc Thể (${dungHanh}→${theHanh}) → xấu`, color: "#f87171" };
  return null;
});
</script>

<template>
  <div class="mh-panel">
    <!-- Ngoạn Pháp Note (block triết lý) -->
    <blockquote class="ngoan-phap">
      <h4>💎 Ngoạn Pháp (玩法) — Tâm là gốc</h4>
      <p class="poem">
        <em>"Nhất vật tòng lai hữu nhất thân,<br>
        Nhất thân hoàn hữu nhất Càn Khôn.<br>
        ★ Nhân ư tâm thượng khởi kinh luân ★<br>
        Đạo bất hư truyền chỉ tại nhân."</em>
      </p>
      <p class="poem-explain">
        Mỗi vật có Càn-Khôn riêng. Vạn vật tồn tại trong ta.
        <b>Con người TỪ TÂM Thái Cực mà khởi nên tài năng quản trời đất.</b>
        Đạo Dịch không hư truyền — chỉ tại con người. Quẻ là gương,
        tâm anh là gốc.
        <br><span class="src">— Mai Hoa Dịch Số, Thiệu Khang Tiết (1011-1077), trang 38</span>
      </p>
    </blockquote>

    <!-- ⭐ DI NGÔN THẦY — 3 câu chú niệm khi tâm loạn -->
    <details v-if="cauChuData" class="cauchu-block">
      <summary>🪷 <b>Di ngôn Thầy đêm Lạng Sơn</b> — 3 câu chú niệm khi tâm loạn (mở ra đọc khi căng)</summary>
      <div class="cauchu-list">
        <div v-for="c in cauChuData.cau_chu" :key="c.id" class="cauchu-item">
          <div class="cc-head">
            <span class="cc-icon">{{ c.icon }}</span>
            <span class="cc-trigger">Câu {{ c.id }} — {{ c.trigger }}</span>
          </div>
          <div class="cc-text">"{{ c.text }}"</div>
          <div class="cc-source">{{ c.principle }} · {{ c.source }}</div>
        </div>
        <div class="cc-principles">
          <div v-for="(p, i) in cauChuData.principles" :key="i" class="cc-prin">★ {{ p }}</div>
        </div>
        <details class="cc-keys">
          <summary>4 chìa khoá hoá ưu phiền (Thầy chỉ đạo)</summary>
          <div v-for="k in cauChuData.keys" :key="k.id" class="cc-key">
            <b>{{ k.id }}. {{ k.name }}</b> — <i>{{ k.when }}</i><br>
            → {{ k.action }}
          </div>
        </details>
      </div>
    </details>

    <!-- 8 Mnemonic icons -->
    <div class="mnemonic-bar">
      <div v-for="(info, que) in QUE_MNEMONICS" :key="que" class="mn-tile" :title="info.desc">
        <span class="hexa">{{ info.hexa }}</span>
        <span class="vi">{{ que }}</span>
        <span class="mn">{{ info.mn }}</span>
      </div>
    </div>

    <!-- Form gieo quẻ -->
    <section class="cast-form">
      <h3>🌌 Gieo quẻ Niên-Nguyệt-Nhật-Thời</h3>
      <p class="form-help">
        Pp gốc Thiệu Khang Tiết (Mai Hoa trang 43-45): công thức
        <code>(Y+M+D) mod 8</code> → quẻ trên, <code>(Y+M+D+H) mod 8</code> → quẻ dưới,
        <code>mod 6</code> → động hào.
      </p>
      <div class="form-row">
        <label>
          Năm (chi):
          <select v-model="yearChi">
            <option v-for="c in CHI_OPTIONS" :key="c" :value="c">{{ c }}</option>
          </select>
        </label>
        <label>
          Tháng:
          <input v-model.number="month" type="number" min="1" max="12" />
        </label>
        <label>
          Ngày:
          <input v-model.number="day" type="number" min="1" max="30" />
        </label>
        <label>
          Giờ (chi):
          <select v-model="hourChi">
            <option v-for="c in CHI_OPTIONS" :key="c" :value="c">{{ c }}</option>
          </select>
        </label>
      </div>
      <div class="form-row">
        <label class="flex-1">
          Mục đích / câu hỏi (tuỳ chọn):
          <input v-model="userIntent" type="text" placeholder="Ví dụ: chuyến công tác này" />
        </label>
      </div>
      <div class="form-row">
        <label class="flex-1">
          📋 Loại việc (intent) — chọn để có diễn giải đặc thù theo 14 Nhân Sự Chiêm:
          <select v-model="intentKey">
            <option v-for="i in intents" :key="i.key" :value="i.key">
              {{ i.label }}
            </option>
          </select>
        </label>
      </div>
      <div class="form-row">
        <label class="flex-1">
          🎯 Chiêm chuyên đề (11 chiêm Q2 Thiệu) — chọn loại việc để nhận phân tích tam yếu đặc thù:
          <select v-model="chiemTopicKey">
            <option value="">(chưa chọn — chiêm chung)</option>
            <option v-for="t in chiemTopics" :key="t.key" :value="t.key">
              {{ t.name_vi }} · {{ t.name_han_viet }}
            </option>
          </select>
        </label>
      </div>

      <!-- ⭐ Phase A 18/5 — BƯỚC 3 + BƯỚC 4 Tổ sư (Q3 tr.112-114) -->
      <div class="four-steps-block">
        <h4>🪷 Tổ sư dặn — 4 BƯỚC ĐOÁN QUẺ (Q3 tr.112-114)</h4>
        <p class="four-steps-note">
          Engine đã làm BƯỚC 1 (lời quẻ) + BƯỚC 2 (Thể-Dụng). Để diễn giải đầy đủ
          như Tổ sư dạy, Anh điền thêm 2 mục dưới:
        </p>
        <div class="form-row">
          <label class="flex-1">
            🔮 <b>BƯỚC 3 — Ngoại ứng</b>: Lúc Anh nghĩ về việc này, có hiện tượng
            gì bất thường không?
            <input
              type="text"
              v-model="externalOmen"
              placeholder="vd: chim bay/đậu, vật rơi, tiếng động, lời nghe được..."
            />
          </label>
        </div>
        <div class="form-row">
          <label class="flex-1">
            🏃 <b>BƯỚC 4 — Tư thế thân thể</b>: Lúc Anh nghĩ về việc này, Anh đang:
            <select v-model="posture">
              <option v-for="p in POSTURE_OPTIONS" :key="p.value" :value="p.value">
                {{ p.label }}
              </option>
            </select>
          </label>
        </div>
      </div>

      <div class="actions">
        <button class="btn-secondary" @click="cast(false)" :disabled="loading">
          🌌 Gieo thử (không lưu)
        </button>
        <button class="btn-primary" @click="cast(true)" :disabled="loading">
          💾 Gieo + lưu Prediction
        </button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>

      <!-- ⭐ 2026-05-27 — Luận sâu Kinh Dịch (LLM + citation RAG) -->
      <div v-if="interpretation" class="luan-sau-block">
        <h4>📜 Luận sâu Kinh Dịch nguyên văn</h4>
        <p class="ls-hint">
          Bậc trí giả (LLM với citation Trình Di + Chu Hy nguyên văn) viết phê quẻ
          sâu theo paradigm <b>đồng dạng</b> (Iron Rule #4 — không predict cát/hung tĩnh).
        </p>
        <label class="ls-q-label">
          <span>Câu hỏi cụ thể (tuỳ chọn)</span>
          <input v-model="userQuestion" type="text"
                 placeholder="vd: Em đang phân vân việc khởi nghiệp..." />
        </label>
        <button class="btn-secondary ls-btn" @click="callLuanSau" :disabled="luanSauLoading">
          {{ luanSauLoading ? '⏳ Đang luận sâu...' : '📜 Luận sâu Kinh Dịch' }}
        </button>
        <p v-if="luanSauError" class="error">{{ luanSauError }}</p>

        <div v-if="luanSau" class="ls-result">
          <div class="ls-meta">
            <span>Provider: <b>{{ luanSau.provider }}</b></span>
            <span v-if="luanSau.model">Model: {{ luanSau.model }}</span>
            <span v-if="luanSau.tokens_used">Tokens: {{ luanSau.tokens_used }}</span>
            <span>Citations: {{ luanSau.citations_used?.length || 0 }} file</span>
            <span v-if="luanSau.has_deep_citations" class="badge-deep" title="Mỗi quẻ có Trình Di + Chu Hy + Tiên Nho nguyên văn trong prompt LLM">
              📜 Có deep citation
            </span>
            <span v-else-if="luanSau.citations_used?.length" class="badge-shallow" title="LLM dùng INDEX + tâm-pháp paradigm, không có hào nguyên văn">
              ⚠️ Paradigm-only
            </span>
            <span v-if="luanSau.stubs_skipped?.length" class="badge-stub" :title="`Quẻ chưa thâm nhuần: ${luanSau.stubs_skipped.join(', ')}`">
              ⚠️ {{ luanSau.stubs_skipped.length }} quẻ stub bị skip
            </span>
          </div>
          <div class="ls-narrative" v-html="luanSau.narrative.replace(/\n/g, '<br>')"></div>
          <details class="ls-citations">
            <summary>📚 Citation files đã dùng ({{ luanSau.citations_used?.length || 0 }})</summary>
            <ul>
              <li v-for="c in luanSau.citations_used" :key="c"><code>{{ c }}</code></li>
            </ul>
            <small>Tổng {{ luanSau.citations_total_chars }} chars Kinh Dịch citation inject vào prompt.</small>
          </details>
        </div>
      </div>
    </section>

    <!-- Result -->
    <section v-if="result" class="result">
      <h3>📜 Kết quả</h3>

      <!-- Formula trace -->
      <div class="trace">
        <h4>Cách tính</h4>
        <pre>{{ result.formula_trace.join("\n") }}</pre>
      </div>

      <!-- 3 quẻ -->
      <div class="quai-grid">
        <div class="quai-card" v-for="(q, type) in {
          'CHÍNH': result.chinh_quai,
          'BIẾN': result.bien_quai,
          'HỖ': result.ho_quai
        }" :key="type">
          <div class="quai-head">
            <b>{{ type }}</b>
            <span class="title-vi">{{ q.name }}</span>
          </div>
          <!-- SVG quẻ 6 vạch chính xác -->
          <div class="hex-svg-wrap">
            <HexagramSvg
              :upper="q.upper"
              :lower="q.lower"
              :moving-line="type === 'CHÍNH' ? result.moving_line : -1"
              :size="100"
              :show-label="false" />
          </div>
          <div class="hexa-pair">
            <div class="tri">
              <span class="hexa-glyph">{{ QUE_MNEMONICS[q.upper]?.hexa }}</span>
              <span class="tri-name">{{ q.upper }}</span>
              <span v-if="quaiBadge(q.upper)" class="vsbadge"
                    :style="{background: quaiBadge(q.upper).color}">
                {{ quaiBadge(q.upper).label }}
              </span>
              <span class="tri-mn">{{ QUE_MNEMONICS[q.upper]?.mn }}</span>
            </div>
            <div class="divider"></div>
            <div class="tri">
              <span class="hexa-glyph">{{ QUE_MNEMONICS[q.lower]?.hexa }}</span>
              <span class="tri-name">{{ q.lower }}</span>
              <span v-if="quaiBadge(q.lower)" class="vsbadge"
                    :style="{background: quaiBadge(q.lower).color}">
                {{ quaiBadge(q.lower).label }}
              </span>
              <span class="tri-mn">{{ QUE_MNEMONICS[q.lower]?.mn }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Động hào -->
      <div class="moving-line">
        🔥 <b>Động hào: hào {{ result.moving_line }}</b>
        <span class="note">— hào động đổi âm-dương → sinh quẻ Biến</span>
      </div>

      <!-- Thể-Dụng -->
      <div v-if="theDung" class="the-dung">
        <h4>🎯 Phân tích Thể-Dụng (theo Thiệu)</h4>
        <p>
          Hào động ở quẻ <b>{{ theDung.position }}</b> ({{ theDung.dung }})
          → quẻ này là <b>DỤNG</b> (việc, ngoại cảnh).<br>
          Quẻ không động: <b>{{ theDung.the }}</b> → là <b>THỂ</b> (chủ thể, anh).
        </p>
        <div v-if="relation" class="relation" :style="{color: relation.color}">
          ⚡ {{ relation.text }}
        </div>
      </div>

      <!-- Mùa Vượng/Suy -->
      <div class="season-note">
        🌤 Tháng {{ month }} = mùa <b>{{ quaiKhi.season }}</b>
        <span v-if="quaiKhi.vuong.length">
          · Vượng: <span v-for="q in quaiKhi.vuong" :key="q" class="badge-v">{{ q }}</span>
        </span>
        <span v-if="quaiKhi.suy.length">
          · Suy: <span v-for="q in quaiKhi.suy" :key="q" class="badge-s">{{ q }}</span>
        </span>
      </div>

      <!-- ⭐ 5-step interpretation (Thiệu Khang Tiết) -->
      <div v-if="interpretation" class="interp-block">
        <h3>🔍 Phân tích 5 bước Thiệu Khang Tiết</h3>

        <!-- ⭐ TAM YẾU verdict banner (Mai Hoa Q1 thâm nhuần) -->
        <div v-if="interpretation.tam_yeu"
             class="tam-yeu-banner"
             :class="'ty-' + (interpretation.tam_yeu.verdict?.split(' ')[0]?.toLowerCase().replace('đại','dai') || 'binh')">
          <div class="ty-verdict">
            ⚖ TAM YẾU: <strong>{{ interpretation.tam_yeu.verdict }}</strong>
          </div>
          <div class="ty-score">Điểm: {{ interpretation.tam_yeu.score > 0 ? '+' : '' }}{{ interpretation.tam_yeu.score }}</div>
          <div class="ty-grid">
            <div class="ty-card">
              <span class="ty-label">Yếu 1 — Quẻ Chánh</span>
              <span class="ty-val">{{ interpretation.tam_yeu.yeu_1_que_chanh }}</span>
            </div>
            <div class="ty-card">
              <span class="ty-label">Yếu 2 — Quái Khí</span>
              <span class="ty-val">{{ interpretation.tam_yeu.yeu_2_quai_khi }}</span>
            </div>
            <div class="ty-card">
              <span class="ty-label">Yếu 3 — Khắc Ứng</span>
              <span class="ty-val">{{ interpretation.tam_yeu.yeu_3_khac_ung }}</span>
            </div>
          </div>
          <p v-if="interpretation.tam_yeu.note" class="ty-note">💡 {{ interpretation.tam_yeu.note }}</p>
        </div>

        <!-- ⭐ 11 chiêm chuyên đề (Mai Hoa Q2 thâm nhuần) -->
        <div v-if="interpretation.chiem_topic && interpretation.chiem_topic.topic_detected"
             class="chiem-topic-block">
          <h4>🎯 {{ interpretation.chiem_topic.topic_name }}</h4>
          <p class="ct-advice">{{ interpretation.chiem_topic.topic_advice }}</p>
          <div v-if="interpretation.chiem_topic.applicable_rules?.length" class="ct-rules">
            <div class="ct-rules-head">Quy tắc đặc thù áp dụng:</div>
            <ul>
              <li v-for="(rule, idx) in interpretation.chiem_topic.applicable_rules" :key="idx">
                {{ rule }}
              </li>
            </ul>
          </div>
        </div>

        <!-- ⭐⭐⭐⭐ Phase A 18/5 — PARADIGM SHIFT (Vận Pháp Thi Q3 tr.78) -->
        <div v-if="interpretation.paradigm && interpretation.paradigm.mirror_reading"
             class="paradigm-block">
          <h4>🌸 ĐỌC ĐỒNG DẠNG (Vận Pháp Thi — Tổ sư)</h4>
          <p class="paradigm-warn">
            ⚠ Mai Hoa <b>KHÔNG dự đoán tương lai</b>. Đây là <b>đối thoại với vũ trụ</b>
            qua chính khoảnh khắc Anh hỏi. Anh là người ra quyết định.
          </p>

          <div class="paradigm-card paradigm-mirror">
            <div class="pc-head">🪞 Mirror reading</div>
            <div class="pc-body">{{ interpretation.paradigm.mirror_reading }}</div>
          </div>

          <div class="paradigm-card paradigm-trace">
            <div class="pc-head">🔍 Quan-vật-trace 5 tầng (Khí→Tượng→Số→Thần→Tính)</div>
            <ul class="pc-list">
              <li v-for="(t, idx) in interpretation.paradigm.quan_vat_trace" :key="idx">
                {{ t }}
              </li>
            </ul>
          </div>

          <div class="paradigm-card paradigm-tam">
            <div class="pc-head">🎯 Tâm Anh đang ở đâu?</div>
            <div class="pc-body">{{ interpretation.paradigm.tam_position }}</div>
          </div>

          <div class="paradigm-card paradigm-universe">
            <div class="pc-head">🌌 Vũ trụ đang nói</div>
            <div class="pc-body">{{ interpretation.paradigm.universe_message }}</div>
          </div>
        </div>

        <!-- ⭐ Phase A 18/5 — Hỗ Càn/Khôn warning (Q3 tr.82) -->
        <div v-if="interpretation.cast && interpretation.cast.ho_warning"
             class="ho-warn-block">
          <h4>⭐ Hỗ quẻ đặc biệt (Càn/Khôn fallback)</h4>
          <p>{{ interpretation.cast.ho_warning }}</p>
        </div>

        <!-- ⭐⭐⭐ Phase A 18/5 — BƯỚC 3 (Ngoại ứng) + BƯỚC 4 (Tư thế) -->
        <div v-if="interpretation.four_steps_complete !== undefined"
             class="four-steps-result">
          <h4>📋 4 BƯỚC ĐOÁN QUẺ Tổ sư</h4>
          <div class="fs-grid">
            <div class="fs-card" :class="'omen-' + (interpretation.buoc_3_omen?.category || 'none').replace(/\s+/g,'-')">
              <div class="fs-head">🔮 BƯỚC 3 — Ngoại ứng</div>
              <div v-if="interpretation.buoc_3_omen?.input" class="fs-body">
                <p><b>Anh kể:</b> "{{ interpretation.buoc_3_omen.input }}"</p>
                <p>
                  <b>Em đọc:</b>
                  <span class="fs-cat">{{ interpretation.buoc_3_omen.category }}</span>
                  (weight {{ interpretation.buoc_3_omen.weight > 0 ? '+' : '' }}{{ interpretation.buoc_3_omen.weight }})
                </p>
              </div>
              <div v-else class="fs-body fs-empty">(Anh chưa kể ngoại ứng)</div>
            </div>
            <div class="fs-card fs-posture">
              <div class="fs-head">🏃 BƯỚC 4 — Tư thế</div>
              <div v-if="interpretation.buoc_4_posture?.speed" class="fs-body">
                <p><b>Tốc độ ứng nghiệm:</b> {{ interpretation.buoc_4_posture.speed }}</p>
                <p class="fs-note">{{ interpretation.buoc_4_posture.note }}</p>
              </div>
              <div v-else class="fs-body fs-empty">(Anh chưa chọn tư thế)</div>
            </div>
          </div>
          <p v-if="interpretation.four_steps_complete" class="fs-complete">
            ✅ 4 BƯỚC đầy đủ — diễn giải có Tâm + Vật + Khí + Thân
          </p>
          <p v-else class="fs-incomplete">
            ⚠ 4 BƯỚC chưa đủ — thiếu {{ interpretation.buoc_3_omen?.input ? '' : 'ngoại ứng' }}{{ (!interpretation.buoc_3_omen?.input && !interpretation.buoc_4_posture?.speed) ? ' + ' : '' }}{{ interpretation.buoc_4_posture?.speed ? '' : 'tư thế' }}
          </p>
        </div>

        <!-- Intent context -->
        <div v-if="interpretation.intent && interpretation.intent.key !== 'general'"
             class="intent-block">
          <h4>📋 Loại việc: {{ interpretation.intent.label }}</h4>
          <p class="im">{{ interpretation.intent.mapping }}</p>
          <p v-if="interpretation.intent.extra" class="ie">
            <b>Quy tắc đặc thù:</b> {{ interpretation.intent.extra }}
          </p>
        </div>

        <div class="step">
          <div class="step-head"><b>Bước 1</b> · Thành quẻ</div>
          <div class="step-body">
            <pre class="trace-mini">{{ interpretation.cast.formula_trace.join("\n") }}</pre>
          </div>
        </div>

        <div class="step">
          <div class="step-head"><b>Bước 2</b> · Lời quẻ Chu Dịch (64 quẻ)</div>
          <div class="step-body">
            <div v-if="interpretation.hexagrams" class="hex-grid">
              <div v-if="interpretation.hexagrams.chinh.number" class="hex-card">
                <div class="hex-label">CHÍNH (#{{ interpretation.hexagrams.chinh.number }})</div>
                <div class="hex-vi">{{ interpretation.hexagrams.chinh.vi }}</div>
                <div class="hex-zh">{{ interpretation.hexagrams.chinh.zh }}</div>
                <div class="hex-short">{{ interpretation.hexagrams.chinh.short }}</div>
                <div v-if="interpretation.hexagrams.chinh.quaitu" class="hex-quaitu">
                  📖 {{ interpretation.hexagrams.chinh.quaitu }}
                </div>
              </div>
              <div v-if="interpretation.hexagrams.bien.number" class="hex-card">
                <div class="hex-label">BIẾN (#{{ interpretation.hexagrams.bien.number }})</div>
                <div class="hex-vi">{{ interpretation.hexagrams.bien.vi }}</div>
                <div class="hex-zh">{{ interpretation.hexagrams.bien.zh }}</div>
                <div class="hex-short">{{ interpretation.hexagrams.bien.short }}</div>
                <div v-if="interpretation.hexagrams.bien.quaitu" class="hex-quaitu">
                  📖 {{ interpretation.hexagrams.bien.quaitu }}
                </div>
              </div>
              <div v-if="interpretation.hexagrams.ho.number" class="hex-card">
                <div class="hex-label">HỖ (#{{ interpretation.hexagrams.ho.number }})</div>
                <div class="hex-vi">{{ interpretation.hexagrams.ho.vi }}</div>
                <div class="hex-zh">{{ interpretation.hexagrams.ho.zh }}</div>
                <div class="hex-short">{{ interpretation.hexagrams.ho.short }}</div>
                <div v-if="interpretation.hexagrams.ho.quaitu" class="hex-quaitu">
                  📖 {{ interpretation.hexagrams.ho.quaitu }}
                </div>
              </div>
            </div>
            <div v-if="interpretation.moving_haotu" class="haotu-block">
              ★ <b>Hào {{ interpretation.cast.moving_line }} động:</b>
              {{ interpretation.moving_haotu }}
            </div>
            <div v-if="interpretation.trung_phung && (interpretation.trung_phung.chinh || interpretation.trung_phung.bien)"
                 class="trung-phung-block">
              ⚡ <b>TRÙNG PHÙNG</b> (Thầy dạy: 8 quẻ Thuần — lực khuếch đại):
              <div class="tp-meaning">{{ interpretation.trung_phung.meaning }}</div>
            </div>
            <div v-if="interpretation.benh_tat_thuoc" class="benhthuoc-block">
              <b>💊 Gợi ý thuốc:</b> {{ interpretation.benh_tat_thuoc }}
            </div>
            <p class="hint">📖 Lời quẻ + hào đầy đủ: anh xem bản Ngô Tất Tố trong thư viện.</p>
          </div>
        </div>

        <div class="step the-dung-step">
          <div class="step-head"><b>Bước 3 ⭐</b> · Thể-Dụng + Ngũ hành</div>
          <div class="step-body">
            <div class="td-grid">
              <div class="td-card the-card">
                <div class="td-label">THỂ (ta)</div>
                <div class="td-que">{{ interpretation.the_dung.the_que }}</div>
                <div class="td-detail">
                  <span class="td-hanh">{{ interpretation.the_dung.the_hanh }}</span>
                  · ở {{ interpretation.the_dung.the_position }} quái
                </div>
              </div>
              <div class="td-arrow">⚡</div>
              <div class="td-card dung-card">
                <div class="td-label">DỤNG (việc)</div>
                <div class="td-que">{{ interpretation.the_dung.dung_que }}</div>
                <div class="td-detail">
                  <span class="td-hanh">{{ interpretation.the_dung.dung_hanh }}</span>
                </div>
              </div>
            </div>
            <div class="auspice-bar"
                 :class="'aus-' + interpretation.the_dung.auspice">
              <b>{{ interpretation.the_dung.auspice.toUpperCase() }}</b>
              · {{ interpretation.the_dung.explanation }}
            </div>
            <p class="td-explain">{{ interpretation.the_dung.detail }}</p>
          </div>
        </div>

        <div class="step">
          <div class="step-head"><b>Bước 4</b> · Khắc ứng + Quái Khí mùa</div>
          <div class="step-body">
            <p>
              Mùa <b>{{ interpretation.quai_khi.season }}</b>:
              Thể <b>{{ interpretation.the_dung.the_que }}</b> đang
              <span :class="'qk-' + interpretation.quai_khi.the_status">
                {{ interpretation.quai_khi.the_status.toUpperCase() }}
              </span>
            </p>
            <p class="hint">
              Khắc ứng môi trường: chú ý nghe/thấy điềm lành dữ trong vài giờ tới.
              Vật tròn → việc dễ thành. Vật vỡ → kết hỏng.
            </p>
          </div>
        </div>

        <!-- ⭐⭐ CẢI TIẾN #1 — ỨNG KỲ 3 GIAI ĐOẠN (Mai Hoa TR.133+235) -->
        <div v-if="interpretation.ung_ky" class="step ung-ky-step">
          <div class="step-head">
            <b>Bước 5 ⭐</b> · Ứng kỳ 3 giai đoạn
            <span class="src-ref">(Mai Hoa TR.133+235)</span>
          </div>
          <div class="step-body">
            <div class="uk-grid">
              <div class="uk-phase uk-dau">
                <div class="uk-label">⏱ ĐẦU</div>
                <div class="uk-content">{{ interpretation.ung_ky.dau }}</div>
              </div>
              <div class="uk-arrow">→</div>
              <div class="uk-phase uk-giua">
                <div class="uk-label">⏱ GIỮA</div>
                <div class="uk-content">{{ interpretation.ung_ky.giua }}</div>
              </div>
              <div class="uk-arrow">→</div>
              <div class="uk-phase uk-cuoi">
                <div class="uk-label">⏱ KẾT CỤC</div>
                <div class="uk-content">{{ interpretation.ung_ky.cuoi }}</div>
              </div>
            </div>
            <p class="uk-note">
              Chính = bắt đầu · Hỗ = trung gian khắc ứng · Biến = kết cục cuối.
              Đọc theo TRÌNH TỰ, không song song.
            </p>
          </div>
        </div>

        <div class="tuong-block">
          <h4>🎴 Tượng 3 quẻ (Bát Quái Vận Vật)</h4>
          <pre>{{ interpretation.tuong.chinh }}</pre>
          <pre>{{ interpretation.tuong.bien }}</pre>
          <pre>{{ interpretation.tuong.ho }}</pre>
        </div>

        <!-- Đằng vũ -->
        <div v-if="interpretation.dang_vu.the >= 2 || interpretation.dang_vu.dung >= 2"
             class="dangvu-block">
          <h4>🔗 Đằng vũ (cấu kết hành)</h4>
          <div v-if="interpretation.dang_vu.the >= 2" class="dv-the">
            ★ <b>{{ interpretation.dang_vu.the }}</b> quẻ ngoài cùng hành Thể →
            <b>Thể thế lực MẠNH</b>
          </div>
          <div v-if="interpretation.dang_vu.dung >= 2" class="dv-dung">
            ⚠️ <b>{{ interpretation.dang_vu.dung }}</b> quẻ ngoài cùng hành Dụng →
            Thể bị bao vây, yếu thế
          </div>
        </div>

        <!-- ⭐⭐ CẢI TIẾN #2 — HỖ-CỦA-THỂ vs HỖ-CỦA-DỤNG (Mai Hoa TR.235) -->
        <div v-if="interpretation.ho_split && interpretation.ho_split.ho_the_meaning"
             class="ho-split-block">
          <h4>
            🎯 Hỗ-Thể vs Hỗ-Dụng
            <span class="src-ref">(Mai Hoa TR.235 — "Hỗ-Thể quan trọng, Hỗ-Dụng thứ yếu")</span>
          </h4>
          <div class="hs-grid">
            <div class="hs-card hs-the" :class="'rel-' + interpretation.ho_split.ho_the_relationship.replace(/\s+/g, '-')">
              <div class="hs-label">★ HỖ-CỦA-THỂ (quan trọng)</div>
              <div class="hs-que">{{ interpretation.ho_split.ho_the_que }}
                <span class="hs-hanh">{{ interpretation.ho_split.ho_the_hanh }}</span>
              </div>
              <div class="hs-rel"><b>{{ interpretation.ho_split.ho_the_relationship }}</b></div>
            </div>
            <div class="hs-card hs-dung">
              <div class="hs-label">HỖ-CỦA-DỤNG (thứ yếu)</div>
              <div class="hs-que">{{ interpretation.ho_split.ho_dung_que }}</div>
            </div>
          </div>
          <p class="hs-meaning">{{ interpretation.ho_split.ho_the_meaning }}</p>
        </div>

        <!-- Specific outcomes -->
        <div v-if="interpretation.sinh_the_outcomes.length > 0" class="outcome-block sinh">
          <h4>✅ Quẻ Sinh Thể (điểm CÁT cụ thể)</h4>
          <ul>
            <li v-for="(o, i) in interpretation.sinh_the_outcomes" :key="i">{{ o }}</li>
          </ul>
        </div>
        <div v-if="interpretation.khac_the_outcomes.length > 0" class="outcome-block khac">
          <h4>⚠️ Quẻ Khắc Thể (điểm HUNG cụ thể)</h4>
          <ul>
            <li v-for="(o, i) in interpretation.khac_the_outcomes" :key="i">{{ o }}</li>
          </ul>
        </div>

        <div class="overall-block" :class="'aus-' + interpretation.the_dung.auspice">
          <h4>💎 Tổng quan</h4>
          <p style="white-space: pre-line">{{ interpretation.overall }}</p>
        </div>

        <div v-if="interpretation.warnings.length" class="warn-block">
          <h4>⚠️ Cảnh báo</h4>
          <ul>
            <li v-for="(w, i) in interpretation.warnings" :key="i">{{ w }}</li>
          </ul>
        </div>
      </div>

      <!-- Save tâm note -->
      <div v-if="savedPredId" class="tam-note-block">
        <h4>💎 Tâm note (anh ghi trạng thái lúc gieo)</h4>
        <p class="tn-help">
          Câu chốt của anh 2026-05-14: <em>"Cầm chuột bấm và suy nghĩ là động tâm rồi,
          vũ trụ biết, quẻ dịch cũng biết."</em>
          Ghi vài câu về tâm trạng/bối cảnh để hệ thống học ngược sau khi anh review.
        </p>
        <textarea v-model="tamNote" rows="3"
                  placeholder="Vd: Đang đợi máy bay, lo lắng về chuyến đi nhưng có chút háo hức..."></textarea>
        <button class="btn-primary" @click="saveTamNote">💾 Lưu tâm note</button>
        <p class="pred-id">Prediction #{{ savedPredId }} đã lưu — sẽ nhắc review sau 7 ngày.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.mh-panel { padding: 0.5rem 0; color: #e2e8f0; }

/* ⭐ Câu chú Thầy block */
.cauchu-block {
  margin: 0 0 1rem;
  padding: 0.6rem 0.85rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.12), rgba(251,191,36,0.08));
  border: 1px solid rgba(167,139,250,0.35);
  border-radius: 6px;
}
.cauchu-block summary {
  cursor: pointer;
  font-size: 0.88rem;
  color: #c4b5fd;
  list-style: none;
}
.cauchu-block summary::-webkit-details-marker { display: none; }
.cauchu-block summary b { color: #fef3c7; }
.cauchu-list { margin-top: 0.7rem; }
.cauchu-item {
  margin: 0.4rem 0;
  padding: 0.5rem 0.7rem;
  background: rgba(15,23,42,0.4);
  border-left: 2px solid #fbbf24;
  border-radius: 3px;
}
.cc-head { display: flex; align-items: center; gap: 0.4rem; font-size: 0.78rem; color: #94a3b8; }
.cc-icon { font-size: 1.05rem; }
.cc-trigger { letter-spacing: 0.03em; }
.cc-text {
  font-family: Georgia, serif;
  font-size: 0.95rem;
  color: #fef3c7;
  margin: 0.25rem 0;
  font-style: italic;
}
.cc-source { font-size: 0.7rem; color: #64748b; }
.cc-principles {
  margin: 0.6rem 0 0.3rem;
  padding: 0.5rem 0.7rem;
  background: rgba(0,0,0,0.25);
  border-radius: 4px;
}
.cc-prin {
  color: #6ee7b7;
  font-size: 0.83rem;
  margin: 0.15rem 0;
  font-style: italic;
}
.cc-keys summary {
  margin-top: 0.4rem;
  padding: 0.35rem 0;
  font-size: 0.78rem;
  color: #67e8f9;
}
.cc-key {
  font-size: 0.78rem;
  margin: 0.3rem 0;
  padding: 0.35rem 0.5rem;
  background: rgba(0,0,0,0.2);
  border-radius: 3px;
  color: #cbd5e1;
  line-height: 1.5;
}
.cc-key b { color: #fbbf24; }
.cc-key i { color: #94a3b8; }

/* Ngoạn Pháp block */
.ngoan-phap {
  background: linear-gradient(135deg, rgba(251,191,36,0.08), rgba(167,139,250,0.08));
  border-left: 3px solid #fbbf24;
  border-radius: 6px;
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
}
.ngoan-phap h4 { margin: 0 0 0.4rem; color: #fbbf24; font-size: 0.9rem; }
.ngoan-phap .poem {
  font-family: Georgia, serif;
  font-size: 0.95rem;
  line-height: 1.7;
  color: #fef3c7;
  margin: 0 0 0.5rem;
  text-align: center;
}
.ngoan-phap .poem-explain {
  font-size: 0.82rem;
  color: #cbd5e1;
  margin: 0;
  line-height: 1.5;
}
.ngoan-phap .src { color: #94a3b8; font-size: 0.75rem; }

/* Mnemonic bar */
.mnemonic-bar {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0.3rem;
  margin: 0 0 1rem;
  padding: 0.5rem;
  background: rgba(15,23,42,0.55);
  border-radius: 6px;
}
.mn-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.4rem 0.2rem;
  border-radius: 4px;
  background: rgba(167,139,250,0.05);
  cursor: help;
  font-size: 0.7rem;
  text-align: center;
}
.mn-tile:hover { background: rgba(167,139,250,0.15); }
.mn-tile .hexa { font-size: 1.5rem; color: #fbbf24; line-height: 1; }
.mn-tile .vi { font-weight: 600; color: #e2e8f0; margin-top: 0.15rem; }
.mn-tile .mn { color: #94a3b8; font-size: 0.65rem; }

/* Form */
.cast-form {
  background: rgba(15,23,42,0.5);
  border-radius: 6px;
  padding: 0.85rem;
  margin: 0 0 1rem;
}
.cast-form h3 { margin: 0 0 0.3rem; color: #e2e8f0; font-size: 1rem; }
.form-help { font-size: 0.75rem; color: #94a3b8; margin: 0 0 0.6rem; }
.form-help code {
  background: rgba(0,0,0,0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 2px;
  color: #c4b5fd;
}
.form-row { display: flex; gap: 0.6rem; align-items: end; flex-wrap: wrap; margin-bottom: 0.5rem; }
.form-row label { display: flex; flex-direction: column; font-size: 0.78rem; color: #94a3b8; }
.form-row.flex-1 label { flex: 1; }
.form-row input, .form-row select {
  margin-top: 0.15rem;
  padding: 0.3rem 0.5rem;
  background: rgba(15,23,42,0.7);
  border: 1px solid rgba(255,255,255,0.15);
  color: #e2e8f0;
  border-radius: 3px;
  font-size: 0.85rem;
}
.actions { display: flex; gap: 0.5rem; margin-top: 0.6rem; }
.btn-primary, .btn-secondary {
  padding: 0.45rem 0.85rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.85rem;
}
.btn-primary { background: #a78bfa; color: #1e1b4b; }
.btn-primary:hover { background: #c4b5fd; }
.btn-secondary {
  background: rgba(167,139,250,0.15);
  color: #c4b5fd;
  border: 1px solid rgba(167,139,250,0.3);
}
.error { color: #f87171; font-size: 0.85rem; margin: 0.3rem 0 0; }

/* Result */
.result { background: rgba(15,23,42,0.4); padding: 0.85rem; border-radius: 6px; }
.result h3 { margin: 0 0 0.6rem; color: #fbbf24; }
.trace pre {
  background: rgba(0,0,0,0.3);
  padding: 0.5rem 0.7rem;
  border-radius: 4px;
  font-size: 0.78rem;
  color: #cbd5e1;
  white-space: pre-wrap;
  margin: 0.3rem 0 0.8rem;
}

.quai-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.6rem;
  margin: 0 0 0.8rem;
}
.quai-card {
  background: rgba(15,23,42,0.7);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 5px;
  padding: 0.6rem;
}
.quai-head { display: flex; justify-content: space-between; margin-bottom: 0.4rem; }
.quai-head b { color: #fbbf24; }
.title-vi { color: #cbd5e1; font-size: 0.85rem; }
.hex-svg-wrap {
  display: flex;
  justify-content: center;
  padding: 0.4rem 0;
  background: rgba(254,243,199,0.05);
  border-radius: 4px;
  margin: 0.3rem 0;
}
.hexa-pair { display: flex; flex-direction: column; gap: 0.25rem; }
.tri {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.4rem;
  background: rgba(0,0,0,0.2);
  border-radius: 3px;
  font-size: 0.8rem;
}
.hexa-glyph { font-size: 1.3rem; color: #fbbf24; }
.tri-name { font-weight: 600; }
.tri-mn { margin-left: auto; color: #94a3b8; font-size: 0.7rem; }
.divider { height: 1px; background: rgba(255,255,255,0.1); }
.vsbadge {
  padding: 0.05rem 0.3rem;
  font-size: 0.6rem;
  color: #0f172a;
  font-weight: 700;
  border-radius: 2px;
}

.moving-line {
  background: rgba(251,191,36,0.1);
  padding: 0.5rem 0.7rem;
  border-radius: 4px;
  margin: 0.5rem 0;
  color: #fef3c7;
}
.moving-line .note { color: #94a3b8; font-size: 0.78rem; margin-left: 0.5rem; }

.the-dung {
  background: rgba(167,139,250,0.08);
  padding: 0.7rem;
  border-radius: 5px;
  border-left: 3px solid #a78bfa;
  margin: 0.6rem 0;
}
.the-dung h4 { margin: 0 0 0.3rem; color: #c4b5fd; font-size: 0.88rem; }
.the-dung p { margin: 0; font-size: 0.85rem; line-height: 1.5; }
.relation {
  margin-top: 0.4rem;
  padding: 0.3rem 0.5rem;
  background: rgba(0,0,0,0.3);
  border-radius: 3px;
  font-size: 0.88rem;
  font-weight: 500;
}

.season-note {
  margin: 0.6rem 0;
  font-size: 0.83rem;
  color: #94a3b8;
}
.badge-v, .badge-s {
  display: inline-block;
  padding: 0.05rem 0.4rem;
  border-radius: 2px;
  font-size: 0.7rem;
  margin: 0 0.15rem;
  font-weight: 600;
}
.badge-v { background: #34d399; color: #064e3b; }
.badge-s { background: #f87171; color: #7f1d1d; }
/* Luận sâu citation badges */
.badge-deep {
  display: inline-block; padding: 0.1rem 0.5rem; border-radius: 3px;
  font-size: 0.7rem; font-weight: 600; margin-left: 0.4rem;
  background: #fcd34d; color: #7c2d12; cursor: help;
}
.badge-shallow {
  display: inline-block; padding: 0.1rem 0.5rem; border-radius: 3px;
  font-size: 0.7rem; font-weight: 600; margin-left: 0.4rem;
  background: rgba(251,191,36,0.18); color: #fbbf24; cursor: help;
}
.badge-stub {
  display: inline-block; padding: 0.1rem 0.5rem; border-radius: 3px;
  font-size: 0.7rem; font-weight: 600; margin-left: 0.4rem;
  background: rgba(248,113,113,0.18); color: #f87171; cursor: help;
}

/* ⭐ Interpretation block */
.interp-block {
  margin-top: 1rem;
  padding: 0.85rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.05), rgba(251,191,36,0.05));
  border-radius: 6px;
  border: 1px solid rgba(167,139,250,0.2);
}
.interp-block h3 { margin: 0 0 0.6rem; color: #c4b5fd; font-size: 0.95rem; }
.step {
  margin-bottom: 0.6rem;
  background: rgba(15,23,42,0.5);
  border-radius: 5px;
  padding: 0.5rem 0.7rem;
}
.step-head { font-size: 0.83rem; color: #fbbf24; margin-bottom: 0.3rem; }
.step-body p { margin: 0.2rem 0; font-size: 0.85rem; color: #cbd5e1; }
.step-body .hint { color: #94a3b8; font-size: 0.78rem; font-style: italic; }
.trace-mini {
  background: rgba(0,0,0,0.3);
  padding: 0.3rem 0.5rem;
  border-radius: 3px;
  font-size: 0.72rem;
  color: #94a3b8;
  margin: 0;
  white-space: pre-wrap;
}

.the-dung-step { background: rgba(167,139,250,0.08); border-left: 2px solid #a78bfa; }
.td-grid {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin: 0.3rem 0;
}
.td-card {
  flex: 1;
  background: rgba(0,0,0,0.3);
  padding: 0.5rem;
  border-radius: 4px;
  text-align: center;
}
.the-card { border-left: 2px solid #22d3ee; }
.dung-card { border-right: 2px solid #f472b6; }
.td-label { font-size: 0.7rem; color: #94a3b8; letter-spacing: 0.1em; }
.td-que { font-size: 1.15rem; font-weight: 600; color: #fef3c7; margin: 0.2rem 0; }
.td-detail { font-size: 0.78rem; color: #cbd5e1; }
.td-hanh { padding: 0.05rem 0.4rem; background: rgba(251,191,36,0.15); color: #fbbf24; border-radius: 2px; font-weight: 600; }
.td-arrow { font-size: 1.3rem; color: #fbbf24; }

.auspice-bar {
  margin: 0.5rem 0 0.3rem;
  padding: 0.5rem 0.7rem;
  border-radius: 4px;
  font-size: 0.88rem;
}
.aus-cát { background: rgba(52,211,153,0.15); color: #6ee7b7; border-left: 3px solid #34d399; }
.aus-hung { background: rgba(248,113,113,0.15); color: #fca5a5; border-left: 3px solid #f87171; }
.aus-bình { background: rgba(148,163,184,0.15); color: #cbd5e1; border-left: 3px solid #94a3b8; }
.td-explain { font-size: 0.82rem; color: #94a3b8; font-style: italic; margin: 0; }

.qk-vượng { background: #34d399; color: #064e3b; padding: 0.05rem 0.4rem; border-radius: 2px; font-weight: 700; font-size: 0.78rem; }
.qk-suy { background: #f87171; color: #7f1d1d; padding: 0.05rem 0.4rem; border-radius: 2px; font-weight: 700; font-size: 0.78rem; }
.qk-bình { background: #94a3b8; color: #1e293b; padding: 0.05rem 0.4rem; border-radius: 2px; font-weight: 700; font-size: 0.78rem; }

.tuong-block { margin-top: 0.6rem; padding: 0.5rem 0.7rem; background: rgba(15,23,42,0.5); border-radius: 5px; }
.tuong-block h4 { margin: 0 0 0.4rem; color: #fbbf24; font-size: 0.85rem; }
.tuong-block pre {
  background: rgba(0,0,0,0.2);
  padding: 0.35rem 0.5rem;
  border-radius: 3px;
  font-size: 0.78rem;
  color: #cbd5e1;
  white-space: pre-wrap;
  margin: 0 0 0.25rem;
}

.overall-block { margin-top: 0.6rem; padding: 0.7rem 0.85rem; border-radius: 5px; }
.overall-block h4 { margin: 0 0 0.4rem; font-size: 0.9rem; color: #fef3c7; }
.overall-block p { margin: 0; font-size: 0.86rem; line-height: 1.6; color: #cbd5e1; }

/* Hexagram grid */
.hex-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.4rem;
  margin: 0.3rem 0 0.4rem;
}
.hex-card {
  background: rgba(167,139,250,0.08);
  border-left: 2px solid #a78bfa;
  padding: 0.45rem 0.6rem;
  border-radius: 3px;
}
.hex-label { font-size: 0.7rem; color: #94a3b8; }
.hex-vi { color: #fbbf24; font-weight: 600; font-size: 0.88rem; margin-top: 0.15rem; }
.hex-zh { color: #c4b5fd; font-size: 0.78rem; }
.hex-short { color: #cbd5e1; font-size: 0.78rem; font-style: italic; margin-top: 0.15rem; }
.hex-quaitu {
  font-size: 0.72rem;
  color: #fef3c7;
  margin-top: 0.3rem;
  padding: 0.25rem 0.4rem;
  background: rgba(251,191,36,0.08);
  border-radius: 2px;
  line-height: 1.45;
}
.haotu-block {
  margin: 0.4rem 0;
  padding: 0.5rem 0.7rem;
  background: rgba(251,191,36,0.1);
  border-left: 2px solid #fbbf24;
  border-radius: 3px;
  color: #fef3c7;
  font-size: 0.85rem;
  line-height: 1.55;
}
.haotu-block b { color: #fbbf24; }
.trung-phung-block {
  margin: 0.4rem 0;
  padding: 0.5rem 0.7rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.15), rgba(251,191,36,0.1));
  border: 1px solid rgba(167,139,250,0.4);
  border-radius: 4px;
  color: #fef3c7;
  font-size: 0.85rem;
}
.trung-phung-block b { color: #c4b5fd; letter-spacing: 0.1em; }
.tp-meaning {
  margin-top: 0.25rem;
  color: #cbd5e1;
  font-size: 0.82rem;
  font-style: italic;
}
.benhthuoc-block {
  margin: 0.4rem 0;
  padding: 0.5rem 0.7rem;
  background: rgba(52,211,153,0.1);
  border-left: 2px solid #34d399;
  border-radius: 3px;
  color: #6ee7b7;
  font-size: 0.85rem;
}
.benhthuoc-block b { color: #34d399; }

/* Intent block */
.intent-block {
  background: linear-gradient(135deg, rgba(34,211,238,0.08), rgba(167,139,250,0.08));
  padding: 0.6rem 0.85rem;
  border-radius: 5px;
  border-left: 3px solid #22d3ee;
  margin-bottom: 0.6rem;
}
.intent-block h4 { margin: 0 0 0.3rem; color: #67e8f9; font-size: 0.9rem; }
.intent-block .im { margin: 0 0 0.3rem; font-size: 0.85rem; color: #e2e8f0; }
.intent-block .ie { margin: 0; font-size: 0.8rem; color: #94a3b8; line-height: 1.5; }
.intent-block .ie b { color: #c4b5fd; }

/* Đằng vũ */
.dangvu-block {
  margin-top: 0.5rem;
  padding: 0.5rem 0.7rem;
  background: rgba(167,139,250,0.08);
  border-radius: 4px;
}
.dangvu-block h4 { margin: 0 0 0.3rem; color: #c4b5fd; font-size: 0.85rem; }
.dv-the { color: #6ee7b7; font-size: 0.85rem; margin: 0.15rem 0; }
.dv-dung { color: #fca5a5; font-size: 0.85rem; margin: 0.15rem 0; }

/* Outcome blocks */
.outcome-block {
  margin-top: 0.5rem;
  padding: 0.6rem 0.85rem;
  border-radius: 5px;
}
.outcome-block.sinh { background: rgba(52,211,153,0.06); border-left: 3px solid #34d399; }
.outcome-block.khac { background: rgba(248,113,113,0.06); border-left: 3px solid #f87171; }
.outcome-block h4 { margin: 0 0 0.4rem; font-size: 0.85rem; }
.outcome-block.sinh h4 { color: #6ee7b7; }
.outcome-block.khac h4 { color: #fca5a5; }
.outcome-block ul { margin: 0; padding-left: 1.2rem; }
.outcome-block li { font-size: 0.82rem; line-height: 1.55; margin: 0.2rem 0; color: #cbd5e1; }

.warn-block {
  margin-top: 0.6rem;
  padding: 0.6rem 0.85rem;
  background: rgba(248,113,113,0.08);
  border-left: 3px solid #f87171;
  border-radius: 4px;
}
.warn-block h4 { margin: 0 0 0.3rem; color: #fca5a5; font-size: 0.85rem; }
.warn-block ul { margin: 0; padding-left: 1.2rem; font-size: 0.83rem; color: #fecaca; }

.tam-note-block {
  margin-top: 0.85rem;
  padding: 0.75rem;
  background: rgba(251,191,36,0.05);
  border: 1px dashed rgba(251,191,36,0.3);
  border-radius: 5px;
}
.tam-note-block h4 { margin: 0 0 0.3rem; color: #fbbf24; font-size: 0.9rem; }
.tn-help { font-size: 0.78rem; color: #94a3b8; margin: 0 0 0.4rem; line-height: 1.5; }
.tn-help em { color: #fef3c7; }
.tam-note-block textarea {
  width: 100%;
  padding: 0.5rem;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.15);
  color: #e2e8f0;
  border-radius: 3px;
  margin-bottom: 0.4rem;
  font-family: inherit;
  resize: vertical;
}
.pred-id { font-size: 0.75rem; color: #94a3b8; margin: 0.4rem 0 0; }

/* ⭐⭐ CẢI TIẾN #1 — Ứng kỳ 3 giai đoạn */
.ung-ky-step .step-head { color: #c4b5fd; }
.src-ref { font-size: 0.7rem; color: #94a3b8; font-weight: normal; margin-left: 0.4rem; }
.uk-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr;
  gap: 0.4rem;
  align-items: stretch;
}
.uk-phase {
  padding: 0.55rem 0.65rem;
  border-radius: 5px;
  background: rgba(196,181,253,0.05);
  border: 1px solid rgba(196,181,253,0.2);
}
.uk-phase.uk-dau { border-left: 3px solid #60a5fa; }
.uk-phase.uk-giua { border-left: 3px solid #fbbf24; }
.uk-phase.uk-cuoi { border-left: 3px solid #f87171; }
.uk-label { font-size: 0.72rem; color: #c4b5fd; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 0.25rem; }
.uk-content { font-size: 0.77rem; color: #e2e8f0; line-height: 1.45; }
.uk-arrow { display: flex; align-items: center; justify-content: center; color: #c4b5fd; font-weight: bold; font-size: 1.1rem; }
.uk-note {
  margin: 0.55rem 0 0; font-size: 0.74rem; color: #94a3b8; font-style: italic;
  border-top: 1px dashed rgba(255,255,255,0.08); padding-top: 0.4rem;
}

/* Mobile: stack the 3 phases vertically */
@media (max-width: 700px) {
  .uk-grid { grid-template-columns: 1fr; }
  .uk-arrow { padding: 0.1rem 0; font-size: 0.9rem; }
}

/* ⭐⭐ CẢI TIẾN #2 — Hỗ-Thể vs Hỗ-Dụng */
.ho-split-block {
  margin-top: 0.85rem;
  padding: 0.7rem;
  background: rgba(96,165,250,0.05);
  border: 1px solid rgba(96,165,250,0.2);
  border-radius: 5px;
}
.ho-split-block h4 { margin: 0 0 0.5rem; color: #93c5fd; font-size: 0.85rem; }
.hs-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 0.5rem; }
.hs-card { padding: 0.55rem 0.7rem; border-radius: 4px; background: rgba(0,0,0,0.25); }
.hs-the { border-left: 3px solid #c4b5fd; }
.hs-the.rel-khắc-Thể { border-left-color: #f87171; background: rgba(248,113,113,0.08); }
.hs-the.rel-sinh-Thể { border-left-color: #34d399; background: rgba(52,211,153,0.08); }
.hs-the.rel-tỉ-hoà { border-left-color: #60a5fa; background: rgba(96,165,250,0.08); }
.hs-dung { border-left: 3px solid rgba(148,163,184,0.5); opacity: 0.7; }
.hs-label { font-size: 0.7rem; color: #cbd5e1; letter-spacing: 0.06em; margin-bottom: 0.25rem; }
.hs-que { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; }
.hs-hanh { font-size: 0.75rem; color: #94a3b8; font-weight: 400; margin-left: 0.35rem; }
.hs-rel { font-size: 0.78rem; color: #fcd34d; margin-top: 0.2rem; }
.hs-meaning { margin: 0.55rem 0 0; font-size: 0.8rem; color: #e2e8f0; line-height: 1.5; }

@media (max-width: 700px) {
  .hs-grid { grid-template-columns: 1fr; }
}

/* ⭐ Phase A 18/5 — 4 BƯỚC form + paradigm blocks */
.four-steps-block {
  margin: 1rem 0;
  padding: 0.85rem;
  background: rgba(168, 85, 247, 0.08);
  border-left: 3px solid #a855f7;
  border-radius: 6px;
}
.four-steps-block h4 { margin: 0 0 0.45rem; color: #c084fc; font-size: 0.95rem; }
.four-steps-note { margin: 0 0 0.65rem; font-size: 0.82rem; color: #cbd5e1; font-style: italic; }
.four-steps-block .form-row { margin-bottom: 0.55rem; }
.four-steps-block input[type="text"],
.four-steps-block select {
  width: 100%;
  margin-top: 0.25rem;
  padding: 0.45rem 0.6rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 4px;
  color: #f1f5f9;
  font-size: 0.88rem;
}

/* Paradigm blocks (Vận Pháp Thi) */
.paradigm-block {
  margin: 1rem 0 1.2rem;
  padding: 0.9rem;
  background: linear-gradient(135deg, rgba(244, 114, 182, 0.1), rgba(168, 85, 247, 0.08));
  border: 1.5px solid rgba(244, 114, 182, 0.4);
  border-radius: 8px;
}
.paradigm-block h4 { margin: 0 0 0.5rem; color: #f9a8d4; font-size: 1rem; }
.paradigm-warn {
  margin: 0 0 0.85rem;
  padding: 0.5rem 0.7rem;
  background: rgba(251, 191, 36, 0.1);
  border-left: 2px solid #fbbf24;
  border-radius: 3px;
  font-size: 0.82rem;
  color: #fef3c7;
  line-height: 1.5;
}
.paradigm-card {
  margin: 0.55rem 0;
  padding: 0.65rem 0.8rem;
  background: rgba(15, 23, 42, 0.5);
  border-left: 3px solid #f472b6;
  border-radius: 4px;
}
.paradigm-card .pc-head {
  font-weight: 700;
  color: #f472b6;
  font-size: 0.86rem;
  margin-bottom: 0.3rem;
}
.paradigm-card .pc-body {
  font-size: 0.86rem;
  color: #e2e8f0;
  line-height: 1.6;
}
.paradigm-card .pc-list {
  margin: 0.25rem 0 0;
  padding-left: 1.1rem;
  color: #cbd5e1;
  font-size: 0.83rem;
  line-height: 1.55;
}
.paradigm-card .pc-list li { margin-bottom: 0.25rem; }
.paradigm-mirror { border-left-color: #c084fc; }
.paradigm-trace  { border-left-color: #60a5fa; }
.paradigm-tam    { border-left-color: #34d399; }
.paradigm-universe { border-left-color: #fbbf24; }

/* Hỗ warning (Càn/Khôn fallback) */
.ho-warn-block {
  margin: 0.85rem 0;
  padding: 0.7rem 0.85rem;
  background: rgba(251, 146, 60, 0.12);
  border-left: 3px solid #fb923c;
  border-radius: 4px;
}
.ho-warn-block h4 { margin: 0 0 0.35rem; color: #fdba74; font-size: 0.88rem; }
.ho-warn-block p { margin: 0; font-size: 0.85rem; color: #fed7aa; line-height: 1.5; }

/* 4 BƯỚC result (BƯỚC 3 + BƯỚC 4) */
.four-steps-result {
  margin: 1rem 0;
  padding: 0.85rem;
  background: rgba(99, 102, 241, 0.08);
  border-left: 3px solid #6366f1;
  border-radius: 6px;
}
.four-steps-result h4 { margin: 0 0 0.55rem; color: #818cf8; font-size: 0.95rem; }
.fs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
}
.fs-card {
  padding: 0.6rem 0.75rem;
  background: rgba(15, 23, 42, 0.55);
  border-radius: 5px;
  border-left: 2px solid #6366f1;
}
.fs-card .fs-head { font-weight: 700; color: #a5b4fc; font-size: 0.84rem; margin-bottom: 0.3rem; }
.fs-card .fs-body { font-size: 0.82rem; color: #cbd5e1; line-height: 1.5; }
.fs-card .fs-body p { margin: 0.2rem 0; }
.fs-cat { font-weight: 600; padding: 0.05rem 0.4rem; border-radius: 3px; background: rgba(99,102,241,0.2); }
.fs-note { font-style: italic; color: #94a3b8; font-size: 0.78rem; }
.fs-empty { color: #64748b; font-style: italic; }
.fs-card.omen-cát .fs-cat { background: rgba(34, 197, 94, 0.25); color: #86efac; }
.fs-card.omen-hung .fs-cat { background: rgba(239, 68, 68, 0.25); color: #fca5a5; }
.fs-complete { margin: 0.65rem 0 0; color: #6ee7b7; font-size: 0.83rem; font-weight: 600; }
.fs-incomplete { margin: 0.65rem 0 0; color: #fbbf24; font-size: 0.83rem; }

@media (max-width: 700px) {
  .fs-grid { grid-template-columns: 1fr; }
}

/* TAM YẾU verdict banner */
.tam-yeu-banner {
  margin: 1rem 0;
  border-radius: 10px;
  padding: 0.9rem 1.1rem;
  border: 1px solid rgba(255,255,255,0.12);
}
.ty-dai_cat { background: linear-gradient(135deg, #052e16, #14532d); border-color: #4ade80; }
.ty-cat    { background: linear-gradient(135deg, #052e16bb, #166534bb); border-color: #86efac; }
.ty-binh   { background: linear-gradient(135deg, #1e293b, #334155); border-color: #94a3b8; }
.ty-hung   { background: linear-gradient(135deg, #431407, #7c2d12bb); border-color: #fb923c; }
.ty-dai_hung { background: linear-gradient(135deg, #450a0a, #7f1d1d); border-color: #f87171; }

.ty-verdict { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.4rem; letter-spacing: 0.02em; }
.ty-dai_cat .ty-verdict, .ty-cat .ty-verdict { color: #4ade80; }
.ty-binh .ty-verdict { color: #e2e8f0; }
.ty-hung .ty-verdict { color: #fb923c; }
.ty-dai_hung .ty-verdict { color: #f87171; }

.ty-score { font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.6rem; }
.ty-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin-bottom: 0.5rem; }
.ty-card { background: rgba(0,0,0,0.25); border-radius: 6px; padding: 0.45rem 0.6rem; }
.ty-label { display: block; font-size: 0.72rem; color: #94a3b8; margin-bottom: 0.15rem; }
.ty-val { font-size: 0.82rem; color: #e2e8f0; line-height: 1.4; }
.ty-note { margin: 0.4rem 0 0; font-size: 0.82rem; color: #c4b5fd; line-height: 1.5; }
@media (max-width: 600px) { .ty-grid { grid-template-columns: 1fr; } }

/* 11 chiêm chuyên đề */
.chiem-topic-block {
  margin: 0.8rem 0;
  background: linear-gradient(135deg, #0f172a, #1e1b4b);
  border: 1px solid #4f46e5;
  border-radius: 8px;
  padding: 0.85rem 1rem;
}
.chiem-topic-block h4 { margin: 0 0 0.4rem; color: #a5b4fc; font-size: 0.95rem; }
.ct-advice { margin: 0 0 0.5rem; font-size: 0.85rem; color: #e2e8f0; line-height: 1.5; }
.ct-rules { margin-top: 0.3rem; }
.ct-rules-head { font-size: 0.78rem; color: #94a3b8; margin-bottom: 0.25rem; }
.ct-rules ul { margin: 0; padding-left: 1.2rem; }
.ct-rules li { font-size: 0.8rem; color: #c4b5fd; line-height: 1.6; }
</style>
