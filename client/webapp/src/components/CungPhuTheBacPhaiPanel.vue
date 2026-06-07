<script setup>
/**
 * CungPhuTheBacPhaiPanel — Luận cung Phu Thê theo BẮC PHÁI Trung Châu (Vương Đình Chỉ).
 *
 * Source: Trung Châu Tử Vi Đẩu Số 2, section 5.3 (Vương Đình Chỉ)
 * Engine: engine/tu_vi/chiem_phu_the.py
 * API: POST /api/tu-vi/cung-phu-the/bac-phai
 *
 * Feature flagship cho chủ đề "bạn trẻ + hôn nhân + gia đình".
 * Public access — không cần VIP (paradigm lookup từ seed JSON).
 */
import { ref, computed } from "vue";

// PER-USER props — App.vue truyền activePerson từ store
// (guest dùng local store, authenticated dùng API user_persons).
// KHÔNG có hardcode founder fallback.
const props = defineProps({
  personKey: { type: String, default: "" },
  birthDatetimeLocal: { type: String, default: "" },
  gender: { type: String, default: "" },
  name: { type: String, default: "" },
});

// Phải có ít nhất birth_datetime_local + gender để cast lá số
const canFetch = computed(
  () => Boolean(props.birthDatetimeLocal && props.gender)
);

const loading = ref(false);
const error = ref("");
const result = ref(null);

const cungPhuThe = computed(() => result.value?.data?.cung_phu_the || null);
const chinhTinh = computed(() => result.value?.data?.chinh_tinh || []);
const phuTinh = computed(() => result.value?.data?.phu_tinh || []);
const satTinh = computed(() => result.value?.data?.sat_tinh || []);
const lucSat = computed(() => result.value?.data?.luc_sat_trong_cung || []);
const hoaKi = computed(() => result.value?.data?.hoa_ki_trong_cung || []);
const toHopDoi = computed(() => result.value?.data?.to_hop_doi || null);
const canhBao = computed(() => result.value?.data?.canh_bao || []);
const banChatSao = computed(() => result.value?.data?.luan_giai?.ban_chat_sao || []);
const viTriParadigm = computed(() => result.value?.data?.luan_giai?.vi_tri_paradigm || {});
const toHopSummary = computed(() => result.value?.data?.luan_giai?.to_hop_summary || null);
const thayToSu = computed(() => result.value?.thay_to_su || []);

// Engine v2 — 6 quy luật mới (Tứ Hóa, đào hoa phạm chủ, Tả-Hữu hội, đối cung, Mệnh chủ)
const v2 = computed(() => result.value?.v2 || null);
const v2Bias = computed(() => v2.value?.tu_tham_bias || null);
const v2Rules = computed(() => v2.value?.quy_luat_v2 || null);

async function fetchLuanGiai() {
  loading.value = true;
  error.value = "";
  try {
    const body = {
      person_key: props.personKey,
      birth_datetime_local: props.birthDatetimeLocal,
      gender: props.gender,
      name: props.name || "Người dùng",
    };
    const r = await fetch("/api/tu-vi/cung-phu-the/bac-phai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await r.json();
    if (data.status === "ok") {
      result.value = data;
    } else {
      error.value = data.message || "Lỗi không xác định";
    }
  } catch (e) {
    error.value = String(e);
  } finally {
    loading.value = false;
  }
}

function fmtFieldName(k) {
  return k.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
</script>

<template>
  <div class="phu-the-panel">
    <header class="panel-header">
      <h2>💑 Cung Phu Thê — Bắc Phái</h2>
      <div class="school-tag">Trung Châu · Vương Đình Chỉ</div>
    </header>

    <div v-if="!canFetch" class="no-chart-hint">
      <p>🪐 Chưa có lá số. Vui lòng:</p>
      <ul>
        <li>👉 Mở tab <strong>"Hồ sơ"</strong> để nhập ngày-giờ sinh của Anh/Chị,</li>
        <li>Hoặc dùng URL share: <code>?birth=YYYY-MM-DD-HH-{nam|nu}</code></li>
      </ul>
      <p class="hint-note">
        <em>Tính năng dùng lá số CỦA RIÊNG bạn — KHÔNG dùng lá số của người khác.</em>
      </p>
    </div>

    <button
      v-else-if="!result && !loading"
      class="btn-primary"
      @click="fetchLuanGiai"
    >
      🔮 Luận cung Phu Thê của <strong>{{ name || "bạn" }}</strong>
    </button>

    <div v-if="loading" class="loading">
      Đang xem lá số của bạn...
    </div>
    <div v-if="error" class="error">
      ⚠ {{ error }}
    </div>

    <div v-if="result" class="result">
      <!-- Cung position + stars -->
      <div class="card cung-card">
        <div class="cung-pos">
          <span class="label">Cung Phu Thê tại</span>
          <span class="branch">{{ cungPhuThe?.branch }}</span>
        </div>
        <div v-if="chinhTinh.length" class="stars-list">
          <div class="star-row">
            <span class="star-label">⭐ Chính tinh:</span>
            <span v-for="s in chinhTinh" :key="s" class="star-chip primary">{{ s }}</span>
          </div>
          <div v-if="phuTinh.length" class="star-row">
            <span class="star-label">☆ Phụ tinh:</span>
            <span v-for="s in phuTinh" :key="s" class="star-chip">{{ s }}</span>
          </div>
          <div v-if="satTinh.length" class="star-row">
            <span class="star-label">⚠ Sát tinh:</span>
            <span v-for="s in satTinh" :key="s" class="star-chip warning">{{ s }}</span>
          </div>
        </div>
        <div v-else class="vo-chinh">Vô chính diệu — mượn sao đối cung</div>
      </div>

      <!-- Tổ hợp đôi summary -->
      <div v-if="toHopSummary" class="card to-hop-card">
        <h3>🔗 Tổ hợp đôi</h3>
        <p class="to-hop-note">{{ toHopSummary.noi_dung }}</p>
      </div>

      <!-- Engine v2: 6 quy luật mới -->
      <div v-if="v2Rules" class="card v2-card">
        <h3>🔬 Phân tích 6 quy luật (Engine v2)</h3>

        <div v-if="v2Bias" class="bias-conclusion">
          <div class="bias-headline">{{ v2Bias.ket_luan }}</div>
          <ul class="bias-reasons">
            <li v-for="(ly, i) in v2Bias.ly_do" :key="i">{{ ly }}</li>
          </ul>
        </div>

        <details class="v2-details">
          <summary>Xem chi tiết 6 quy luật</summary>
          <div class="rule-grid">
            <div class="rule">
              <strong>1. Tứ Hóa tại chính tinh:</strong>
              <span v-if="Object.keys(v2Rules['1_tu_hoa_at_chinh_tinh'] || {}).length">
                <span v-for="(star, key) in v2Rules['1_tu_hoa_at_chinh_tinh']" :key="key" class="hoa-chip">
                  {{ star }} Hóa {{ key }}
                </span>
              </span>
              <span v-else class="muted">không</span>
            </div>
            <div class="rule">
              <strong>2. Đào hoa phạm chủ:</strong>
              <span :class="v2Rules['2_dao_hoa_pham_chu'].detected ? 'warning' : 'success'">
                {{ v2Rules['2_dao_hoa_pham_chu'].paradigm }}
              </span>
            </div>
            <div class="rule">
              <strong>3. Xương-Khúc:</strong>
              <span>{{ v2Rules['3_xuong_khuc_anh_huong'].note }}</span>
            </div>
            <div class="rule">
              <strong>4. Tả-Hữu hội chiếu tam phương:</strong>
              <span :class="v2Rules['4_ta_huu_doi_hoi_chieu'].detected ? 'success' : 'muted'">
                {{ v2Rules['4_ta_huu_doi_hoi_chieu'].note }}
              </span>
            </div>
            <div class="rule">
              <strong>5. Đối cung (Quan Lộc):</strong>
              <span>{{ v2Rules['5_doi_cung_vo_chinh_dieu'].paradigm }}</span>
            </div>
            <div class="rule">
              <strong>6. Mệnh chủ ({{ v2Rules['6_menh_chu_anh_huong'].menh_chu }}):</strong>
              <span>{{ v2Rules['6_menh_chu_anh_huong'].paradigm }}</span>
            </div>
          </div>
        </details>
      </div>

      <!-- Cảnh báo -->
      <div v-if="canhBao.length" class="card warning-card">
        <h3>⚠ Cảnh báo paradigm</h3>
        <ul>
          <li v-for="(cb, i) in canhBao" :key="i">{{ cb }}</li>
        </ul>
      </div>

      <!-- Per-star paradigm -->
      <div v-for="sao in banChatSao" :key="sao.ten" class="card star-card">
        <h3>⭐ {{ sao.ten }}</h3>
        <p v-if="sao.ban_chat" class="ban-chat">
          <strong>Bản chất:</strong> {{ sao.ban_chat }}
        </p>
        <p v-if="sao.co_ban" class="co-ban">
          <strong>Cơ bản:</strong> {{ sao.co_ban }}
        </p>

        <div v-if="viTriParadigm[sao.ten]" class="vi-tri">
          <h4>Tại cung {{ viTriParadigm[sao.ten].branch_pair }}:</h4>
          <ul class="paradigm-list">
            <li v-for="(value, key) in viTriParadigm[sao.ten].data" :key="key">
              <strong>{{ fmtFieldName(key) }}:</strong>
              <span v-if="typeof value === 'string'">{{ value }}</span>
              <span v-else-if="Array.isArray(value)">{{ value.join(', ') }}</span>
              <span v-else>{{ value }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Disclaimer -->
      <div class="card disclaimer-card">
        <p class="disclaimer">
          📜 <em>{{ result?.data?.iron_rule_disclaimer }}</em>
        </p>
        <div class="thay-credit">
          <strong>Thầy tổ sư:</strong> {{ thayToSu.join(", ") }}
        </div>
        <div class="source">
          <strong>Nguồn:</strong> {{ result?.data?.source }}
        </div>
      </div>

      <button class="btn-secondary" @click="result = null">
        🔄 Đoán lại
      </button>
    </div>
  </div>
</template>

<style scoped>
.phu-the-panel {
  padding: 16px;
  font-family: var(--font-family, sans-serif);
  color: var(--read-text, #1a1a1a);
  background: var(--read-bg, #fafaf7);
  border-radius: 8px;
}
.panel-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  border-bottom: 2px solid var(--read-accent, #8b5a3c);
  padding-bottom: 8px;
  margin-bottom: 16px;
}
.panel-header h2 {
  margin: 0;
  font-size: 1.4em;
  color: var(--read-heading, #4a2c1a);
}
.school-tag {
  font-size: 0.85em;
  color: var(--read-muted, #8a7a6a);
  font-style: italic;
}
.btn-primary {
  background: var(--read-accent, #8b5a3c);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 1.05em;
  cursor: pointer;
}
.btn-secondary {
  background: transparent;
  color: var(--read-accent, #8b5a3c);
  border: 1px solid var(--read-accent, #8b5a3c);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
}
.loading { padding: 24px; text-align: center; font-style: italic; }
.no-chart-hint {
  padding: 14px;
  background: #fff8e6;
  border: 1px dashed #d4a574;
  border-radius: 6px;
  font-size: 0.95em;
}
.no-chart-hint ul { margin: 8px 0 8px 20px; }
.no-chart-hint code {
  background: #fde9c8;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 0.92em;
}
.hint-note { color: var(--read-muted, #8a7a6a); font-size: 0.88em; margin-top: 8px; }
.error { padding: 12px; color: #c33; background: #fee; border-radius: 6px; }
.result { display: flex; flex-direction: column; gap: 12px; }
.card {
  background: var(--read-card-bg, #fff);
  border: 1px solid var(--read-border, #e8e0d3);
  border-radius: 6px;
  padding: 14px;
}
.cung-card { background: linear-gradient(135deg, #faf2e8 0%, #f5e8d5 100%); }
.cung-pos { font-size: 1.1em; margin-bottom: 8px; }
.cung-pos .branch {
  font-size: 1.6em;
  font-weight: bold;
  color: var(--read-accent, #8b5a3c);
  margin-left: 8px;
}
.stars-list { display: flex; flex-direction: column; gap: 8px; }
.star-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.star-label { font-weight: 600; min-width: 100px; }
.star-chip {
  background: #fff5e6;
  border: 1px solid #d4a574;
  padding: 3px 10px;
  border-radius: 14px;
  font-size: 0.92em;
}
.star-chip.primary {
  background: #fff0d6;
  border-color: var(--read-accent, #8b5a3c);
  color: var(--read-heading, #4a2c1a);
  font-weight: 600;
}
.star-chip.warning {
  background: #fee;
  border-color: #c33;
  color: #c33;
}
.vo-chinh { font-style: italic; color: var(--read-muted, #8a7a6a); }
.to-hop-card { background: #e8f2fa; border-color: #b5d9e8; }
.v2-card { background: linear-gradient(135deg, #f5e8f5 0%, #e8e5f5 100%); border-color: #b5a8d4; }
.bias-headline {
  font-size: 1.15em;
  font-weight: bold;
  padding: 8px 0;
  color: var(--read-heading, #4a2c1a);
}
.bias-reasons { margin: 4px 0 0 20px; padding: 0; font-size: 0.95em; }
.bias-reasons li { margin: 4px 0; }
.v2-details { margin-top: 12px; }
.v2-details summary { cursor: pointer; font-weight: 600; padding: 4px 0; }
.rule-grid { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
.rule { font-size: 0.92em; }
.rule strong { display: block; margin-bottom: 2px; }
.rule .muted { color: var(--read-muted, #8a7a6a); font-style: italic; }
.rule .success { color: #2d7a3e; }
.rule .warning { color: #c33; font-weight: 600; }
.hoa-chip {
  display: inline-block;
  background: #ffd966;
  border: 1px solid #c08000;
  padding: 2px 8px;
  border-radius: 10px;
  margin: 2px 4px 2px 0;
  font-size: 0.88em;
}
.to-hop-card h3 { margin: 0 0 6px; }
.to-hop-note { margin: 0; font-style: italic; }
.warning-card { background: #fef5f5; border-color: #f0c0c0; }
.warning-card h3 { color: #b04040; margin: 0 0 8px; }
.warning-card ul { margin: 0; padding-left: 20px; }
.star-card h3 { color: var(--read-heading, #4a2c1a); margin: 0 0 8px; }
.ban-chat, .co-ban { margin: 4px 0; }
.vi-tri h4 { margin: 12px 0 6px; font-size: 0.95em; color: var(--read-accent, #8b5a3c); }
.paradigm-list { margin: 0; padding-left: 20px; font-size: 0.92em; }
.paradigm-list li { margin: 4px 0; }
.disclaimer-card { background: #f5f0e8; font-size: 0.88em; }
.disclaimer { margin: 0 0 8px; color: var(--read-muted, #6a5a4a); }
.thay-credit, .source { margin-top: 6px; color: var(--read-muted, #8a7a6a); font-size: 0.85em; }
</style>
