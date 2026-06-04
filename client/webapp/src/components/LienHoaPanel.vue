<script setup>
import { computed, ref } from "vue";
import { castLienHoa } from "../lib/api";
import LienHoaOnboardingDrawer from "./LienHoaOnboardingDrawer.vue";
import HexagramImage from "./HexagramImage.vue";
import HexagramDetailModal from "./HexagramDetailModal.vue";
import RefBlock from "./RefBlock.vue";
import { useHexagramModal } from "../composables/useHexagramModal";

const { openSlug, openHexagram, closeHexagram } = useHexagramModal();

const LUC_THAN_COLOR = {
  TA: "#e8c95a",
  H: "#9adfe5",
  P: "#5ab07a",
  C: "#d68a4a",
  Q: "#d65a4a",
  T: "#c25a78",
};

const LUC_THAN_LABEL = {
  TA: "TA",
  H: "Huynh Đệ",
  P: "Phụ Mẫu",
  C: "Tử Tôn",
  Q: "Quan Quỷ",
  T: "Thê Tài",
};

const DOMAIN_ICON = {
  life_arc: "☯",
  wealth: "💰",
  marriage: "❤",
  house: "🏠",
  health: "🌿",
  travel: "🧭",
};

const DOMAIN_ICON_EXTRA = {
  children: "👶",
  study: "📚",
  lawsuit: "⚖️",
  career: "💼",
};

const ELEMENT_COLOR = {
  kim: "#c0a878",
  hỏa: "#d65a4a",
  mộc: "#5ab07a",
  thủy: "#3a6cb0",
  thổ: "#9a7b4a",
};

const inputP = ref("");
const inputT = ref("");
const inputQuestion = ref("");
const inputGender = ref("nam");
const data = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const expandedIdx = ref(null);

async function gieo() {
  errorMsg.value = "";
  if (!inputP.value || !inputT.value) {
    errorMsg.value = "Cần nhập đủ số tay Phải và tay Trái.";
    return;
  }
  if (Number(inputP.value) < 1 || Number(inputT.value) < 1) {
    errorMsg.value = "Số phải lớn hơn hoặc bằng 1.";
    return;
  }
  loading.value = true;
  try {
    const result = await castLienHoa({
      numberRightHand: Number(inputP.value),
      numberLeftHand: Number(inputT.value),
      questionText: inputQuestion.value,
      gender: inputGender.value,
    });
    data.value = result.lien_hoa_state;
    expandedIdx.value = 0;
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function randomGieo() {
  // Helper nếu user không tiện rút thăm hương — vẫn cho 2 số ngẫu nhiên 1-99.
  inputP.value = String(Math.floor(Math.random() * 99) + 1);
  inputT.value = String(Math.floor(Math.random() * 99) + 1);
}

function resetForm() {
  data.value = null;
  inputP.value = "";
  inputT.value = "";
  inputQuestion.value = "";
  expandedIdx.value = null;
}

const synthesisParagraphs = computed(() => {
  const full = data.value?.luan_su_deeper?.composed_synthesis_full || "";
  return full.split("\n\n").filter((p) => p.trim());
});

const kt_narrative_by_index = computed(() => {
  const out = {};
  for (const n of data.value?.luan_su_deeper?.per_kts_narratives || []) {
    out[n.index] = n;
  }
  return out;
});

const summaryByLucThan = computed(() => {
  if (!data.value) return {};
  const counts = { TA: 0, H: 0, P: 0, C: 0, Q: 0, T: 0 };
  for (const kt of data.value.khong_thoi) {
    counts[kt.chu_su] = (counts[kt.chu_su] || 0) + 1;
  }
  return counts;
});
</script>

<template>
  <section class="panel lh-panel">
    <div class="panel-title">
      <span>Liên Hoa Độn Pháp — gieo quẻ bằng 2 số tâm ý</span>
      <small>{{ data?.method_id || "lien_hoa_don_v1" }}</small>
    </div>

    <p class="lh-note">
      Nhập 2 con số từ tay <b>Phải</b> và tay <b>Trái</b> (rút chân hương, đếm lá, hoặc viết 10 số rồi bốc).
      Hệ thống tự sinh <b>Bản Quái Kiện</b> với 5, 9 hoặc 13 <b>Không thời sự</b> liên hoàn —
      mỗi không thời chứa Chánh + Hổ + Biến quái + 6 lục thân tag.
      <br />
      Khác Mai Hoa Niên-Nguyệt-Nhật-Thời (tự động theo giờ), Liên Hoa cần anh chủ động đưa số tâm ý.
    </p>

    <LienHoaOnboardingDrawer />

    <div class="lh-form">
      <label>
        <span>Số tay Phải (P)</span>
        <input v-model="inputP" type="number" min="1" placeholder="1–99 hoặc lớn hơn" />
      </label>
      <label>
        <span>Số tay Trái (T)</span>
        <input v-model="inputT" type="number" min="1" placeholder="1–99 hoặc lớn hơn" />
      </label>
      <label>
        <span>Giới tính người cầu sự</span>
        <select v-model="inputGender">
          <option value="nam">TA Nam</option>
          <option value="nữ">TA Nữ</option>
        </select>
      </label>
      <label class="full">
        <span>Câu hỏi / sự việc đang mưu cầu (tuỳ chọn)</span>
        <input v-model="inputQuestion" type="text" placeholder="vd: Có nên mở quán cà phê?" />
      </label>
      <div class="lh-actions">
        <button class="apply-btn" @click="gieo" :disabled="loading">
          {{ loading ? "Đang luận..." : "Gieo quẻ" }}
        </button>
        <button class="secondary-btn" @click="randomGieo" type="button" :disabled="loading">
          🎲 Số ngẫu nhiên
        </button>
        <button v-if="data" class="secondary-btn" @click="resetForm" type="button">
          ✕ Gieo lại
        </button>
      </div>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <template v-if="data">
      <div class="lh-summary">
        <div class="sum-cell sum-cell-with-image">
          <HexagramImage
            :king-wen="data.khong_thoi[0].chanh.king_wen_index"
            :size="46"
            :title="`Quẻ ${data.khong_thoi[0].chanh.king_wen_index} ${data.khong_thoi[0].chanh.name_vi}`"
          />
          <div>
            <span>Quẻ Tiên đề</span>
            <strong>{{ data.khong_thoi[0].chanh.name_vi }}</strong>
            <small>quẻ {{ data.khong_thoi[0].chanh.king_wen_index }} · {{ data.khong_thoi[0].upper_num }}/{{ data.khong_thoi[0].lower_num }} hào {{ data.khong_thoi[0].hao }}</small>
          </div>
        </div>
        <div class="sum-cell">
          <span>TA quái tiên đề</span>
          <strong>{{ data.ta_reference_trigram }} <em>({{ data.ta_reference_element }})</em></strong>
        </div>
        <div class="sum-cell">
          <span>Số đợt độn</span>
          <strong>{{ data.dot_count }} đợt</strong>
          <small>{{ data.khong_thoi_count }} không thời sự</small>
        </div>
        <div class="sum-cell">
          <span>Hoàn thành</span>
          <strong :style="{ color: data.completed ? '#5ab07a' : '#d65a4a' }">
            {{ data.completed ? "✓ TA giành lại chủ sự" : "✗ Chưa hoàn thành" }}
          </strong>
        </div>
      </div>

      <RefBlock kind="note">{{ data.note }}</RefBlock>

      <h5>Phân bố chủ sự</h5>
      <div class="chu-su-bar">
        <div v-for="(count, key) in summaryByLucThan" :key="key"
          v-show="count > 0"
          class="chu-su-chip"
          :style="{ borderColor: LUC_THAN_COLOR[key], color: LUC_THAN_COLOR[key] }">
          {{ LUC_THAN_LABEL[key] }}: <b>{{ count }}</b>
        </div>
      </div>

      <template v-if="data.luan_su">
        <h5>Luận sự — dịch quẻ theo sách Liên Hoa Độn Pháp</h5>
        <div class="luan-su-summary">
          <div class="luan-banner">
            <span class="banner-icon">✦</span>
            <p>{{ data.luan_su.composed_summary }}</p>
          </div>
          <div class="luan-meta">
            <div class="luan-cell">
              <span>Mệnh cung TA (Hổ quái Tiên đề)</span>
              <strong :style="{ color: LUC_THAN_COLOR[data.luan_su.menh_cung_lt] }">
                {{ data.luan_su.menh_cung_lt_name }}
              </strong>
            </div>
            <div class="luan-cell">
              <span>Dạng Chánh quái Tiên đề</span>
              <strong>{{ data.luan_su.chanh_dang_tien_de }}</strong>
            </div>
          </div>
        </div>

        <div class="domain-grid">
          <div v-for="reading in data.luan_su.domain_readings" :key="reading.domain"
            class="domain-card" :data-domain="reading.domain">
            <div class="domain-head">
              <span class="domain-icon">{{ DOMAIN_ICON[reading.domain] || "•" }}</span>
              <h6>{{ reading.domain_vi }}</h6>
            </div>
            <div class="domain-verdict">{{ reading.verdict }}</div>
            <p class="domain-explain">{{ reading.explanation }}</p>
            <ul v-if="reading.evidence?.length" class="domain-evidence">
              <li v-for="(e, i) in reading.evidence" :key="i">{{ e }}</li>
            </ul>
          </div>
        </div>

        <!-- Deeper extra domains -->
        <template v-if="data.luan_su_deeper">
          <h5 class="deeper-h">Luận sự mở rộng — 4 lĩnh vực bổ sung</h5>
          <div class="domain-grid">
            <div v-for="reading in data.luan_su_deeper.extra_domain_readings" :key="reading.domain"
              class="domain-card" :data-domain="reading.domain">
              <div class="domain-head">
                <span class="domain-icon">{{ DOMAIN_ICON_EXTRA[reading.domain] || "•" }}</span>
                <h6>{{ reading.domain_vi }}</h6>
              </div>
              <div class="domain-verdict">{{ reading.verdict }}</div>
              <p class="domain-explain">{{ reading.explanation }}</p>
              <ul v-if="reading.evidence?.length" class="domain-evidence">
                <li v-for="(e, i) in reading.evidence" :key="i">{{ e }}</li>
              </ul>
            </div>
          </div>

          <h5 class="deeper-h">Tổng kết luận</h5>
          <article class="synthesis-card">
            <p v-for="(para, i) in synthesisParagraphs" :key="i" class="synthesis-p">{{ para }}</p>
          </article>
        </template>
      </template>

      <h5>Bản Quái Kiện — {{ data.khong_thoi.length }} không thời sự</h5>
      <ul class="kt-list">
        <li v-for="(kt, idx) in data.khong_thoi" :key="kt.index"
          :class="['kt-card', { expanded: expandedIdx === idx, tien_de: idx === 0 }]"
          @click="expandedIdx = expandedIdx === idx ? null : idx">
          <div class="kt-head">
            <span class="kt-index">{{ kt.label }}</span>
            <span class="kt-coords">
              <code>{{ kt.upper_num }}/{{ kt.lower_num }}</code> hào <b>{{ kt.hao }}</b>
            </span>
            <span class="kt-chanh">
              <HexagramImage :king-wen="kt.chanh.king_wen_index" :size="22" />
              <b>Chánh:</b>
              <a
                class="hex-link"
                href="#"
                @click.stop.prevent="openHexagram(kt.chanh.king_wen_index)"
                title="Mở chi tiết quẻ"
              >
                {{ kt.chanh.name_vi }}
                <small>(quẻ {{ kt.chanh.king_wen_index }})</small>
              </a>
            </span>
            <span class="kt-chu-su" :style="{ background: LUC_THAN_COLOR[kt.chu_su] + '22', color: LUC_THAN_COLOR[kt.chu_su] }">
              Chủ sự: {{ kt.chu_su_name }}
            </span>
          </div>

          <div v-if="expandedIdx === idx" class="kt-detail">
            <div class="three-quai">
              <div class="quai-block clickable" @click.stop="openHexagram(kt.chanh.king_wen_index)" title="Mở chi tiết quẻ">
                <h6>Chánh quái</h6>
                <HexagramImage :king-wen="kt.chanh.king_wen_index" :size="36" />
                <div class="quai-name">{{ kt.chanh.name_vi }}</div>
                <div class="quai-binary">{{ kt.chanh.binary }}</div>
                <div class="quai-trigrams">
                  <span :style="{ color: ELEMENT_COLOR[kt.tagged[0].element] }">
                    <b>thượng</b> {{ kt.tagged[0].trigram }}
                    <em :style="{ color: LUC_THAN_COLOR[kt.tagged[0].luc_than] }">[{{ kt.tagged[0].luc_than }}]</em>
                  </span>
                  <span :style="{ color: ELEMENT_COLOR[kt.tagged[1].element] }">
                    <b>hạ</b> {{ kt.tagged[1].trigram }}
                    <em :style="{ color: LUC_THAN_COLOR[kt.tagged[1].luc_than] }">[{{ kt.tagged[1].luc_than }}]</em>
                  </span>
                </div>
              </div>

              <div class="quai-block menh clickable" @click.stop="openHexagram(kt.ho.king_wen_index)" title="Mở chi tiết quẻ">
                <h6>Hổ quái (Mệnh cung)</h6>
                <HexagramImage :king-wen="kt.ho.king_wen_index" :size="36" />
                <div class="quai-name">{{ kt.ho.name_vi }}</div>
                <div class="quai-binary">{{ kt.ho.binary }}</div>
                <div class="quai-trigrams">
                  <span :style="{ color: ELEMENT_COLOR[kt.tagged[2].element] }">
                    <b>thượng</b> {{ kt.tagged[2].trigram }}
                    <em :style="{ color: LUC_THAN_COLOR[kt.tagged[2].luc_than] }">[{{ kt.tagged[2].luc_than }}]</em>
                  </span>
                  <span :style="{ color: ELEMENT_COLOR[kt.tagged[3].element] }">
                    <b>hạ</b> {{ kt.tagged[3].trigram }}
                    <em :style="{ color: LUC_THAN_COLOR[kt.tagged[3].luc_than] }">[{{ kt.tagged[3].luc_than }}]</em>
                  </span>
                </div>
                <div class="menh-tag">★ Mệnh cung TA ở {{ kt.menh_cung_side === 'upper' ? 'thượng' : 'hạ' }}</div>
              </div>

              <div class="quai-block clickable" @click.stop="openHexagram(kt.bien.king_wen_index)" title="Mở chi tiết quẻ">
                <h6>Biến quái</h6>
                <HexagramImage :king-wen="kt.bien.king_wen_index" :size="36" />
                <div class="quai-name">{{ kt.bien.name_vi }}</div>
                <div class="quai-binary">{{ kt.bien.binary }}</div>
                <div class="quai-trigrams">
                  <span :style="{ color: ELEMENT_COLOR[kt.tagged[4].element] }">
                    <b>thượng</b> {{ kt.tagged[4].trigram }}
                    <em :style="{ color: LUC_THAN_COLOR[kt.tagged[4].luc_than] }">[{{ kt.tagged[4].luc_than }}]</em>
                  </span>
                  <span :style="{ color: ELEMENT_COLOR[kt.tagged[5].element] }">
                    <b>hạ</b> {{ kt.tagged[5].trigram }}
                    <em :style="{ color: LUC_THAN_COLOR[kt.tagged[5].luc_than] }">[{{ kt.tagged[5].luc_than }}]</em>
                  </span>
                </div>
              </div>
            </div>

            <div class="kt-meta">
              <span><b>TA quái KTS này:</b> {{ kt.ta_trigram }}</span>
              <span><b>SỰ quái KTS này:</b> {{ kt.su_trigram }}</span>
              <span><b>Side động:</b> {{ kt.su_side === 'upper' ? 'thượng' : 'hạ' }}</span>
            </div>

            <div v-if="kt_narrative_by_index[kt.index]" class="kt-narrative">
              <div class="kt-narrative-role">
                <span class="kt-narrative-icon">⌛</span>
                <span><b>Vai trò:</b> {{ kt_narrative_by_index[kt.index].role_in_sequence }}</span>
              </div>
              <p class="kt-narrative-phase">{{ kt_narrative_by_index[kt.index].phase_meaning }}</p>
              <p class="kt-narrative-trans" v-if="kt_narrative_by_index[kt.index].transition_to_next">
                <em>→ {{ kt_narrative_by_index[kt.index].transition_to_next }}</em>
              </p>
            </div>
          </div>
        </li>
      </ul>

      <RefBlock kind="cite">{{ data.source_ref }}</RefBlock>
    </template>

    <HexagramDetailModal
      v-if="openSlug"
      :slug="openSlug"
      @close="closeHexagram"
    />
  </section>
</template>

<style scoped>
.lh-panel { display: flex; flex-direction: column; gap: 14px; }

.lh-note {
  font-size: 13px; color: var(--text-secondary, rgba(230,238,245,0.72));
  border-left: 3px solid var(--accent-gold, #e8c95a);
  padding-left: 12px; margin: 0; line-height: 1.6;
}
.lh-note b { color: var(--accent-gold-soft, #f5e6b1); }

.lh-form {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;
  background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255,255,255,0.08));
}
.lh-form .full { grid-column: 1 / -1; }
.lh-form label { display: flex; flex-direction: column; gap: 4px; }
.lh-form label span {
  font-size: 11px; color: var(--text-muted, rgba(230,238,245,0.5));
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
}
.lh-actions {
  grid-column: 1 / -1;
  display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
}

.apply-btn {
  background: rgba(232,201,90,0.2); border: 1px solid var(--border-accent, rgba(232,201,90,0.5));
  color: var(--accent-gold, #e8c95a); padding: 9px 18px; border-radius: 7px;
  font-size: 14px; font-weight: 700; cursor: pointer;
}
.apply-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.secondary-btn {
  background: rgba(255,255,255,0.05); border: 1px solid var(--border-medium, rgba(255,255,255,0.14));
  color: var(--text-secondary, rgba(230,238,245,0.7)); padding: 7px 14px;
  border-radius: 6px; font-size: 13px; cursor: pointer;
}

.lh-summary {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 10px;
  background: rgba(232,201,90,0.06);
  border: 1px solid var(--border-accent, rgba(232,201,90,0.3));
  padding: 12px; border-radius: 8px;
}
.sum-cell { display: flex; flex-direction: column; gap: 2px; }
.sum-cell-with-image { flex-direction: row; align-items: center; gap: 10px; }
.sum-cell-with-image > div { display: flex; flex-direction: column; gap: 2px; }
.sum-cell span:first-child {
  font-size: 10px; color: var(--text-muted, rgba(230,238,245,0.5));
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
}
.sum-cell strong { font-size: 16px; color: var(--accent-gold-soft, #f5e6b1); }
.sum-cell small { font-size: 11px; color: var(--text-muted, rgba(230,238,245,0.5)); }
.sum-cell strong em { font-style: normal; font-size: 13px; color: var(--text-muted, rgba(230,238,245,0.6)); }

h5 {
  margin: 6px 0 0 0; font-size: 12px;
  color: var(--text-muted, rgba(230,238,245,0.55));
  text-transform: uppercase; letter-spacing: 0.6px; font-weight: 700;
}

.chu-su-bar { display: flex; gap: 6px; flex-wrap: wrap; }
.chu-su-chip {
  padding: 4px 10px; border-radius: 4px;
  border: 1px solid; background: rgba(255,255,255,0.03);
  font-size: 12px; font-weight: 600;
}

.kt-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 5px; }

.kt-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-soft, rgba(255,255,255,0.08));
  border-radius: 7px; padding: 9px 12px; cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.kt-card:hover { background: rgba(255,255,255,0.07); }
.kt-card.tien_de {
  border-color: var(--border-accent, rgba(232,201,90,0.35));
  background: rgba(232,201,90,0.05);
}
.kt-card.expanded { background: rgba(232,201,90,0.05); }

.kt-head {
  display: grid; grid-template-columns: 90px 110px 1fr 160px;
  gap: 10px; align-items: center; font-size: 13px;
}
.kt-index { color: var(--accent-gold, #e8c95a); font-weight: 700; font-size: 12px; }
.kt-coords code {
  background: rgba(0,0,0,0.3); padding: 1px 6px; border-radius: 3px;
  font-size: 12px; color: var(--text-secondary, rgba(230,238,245,0.78));
}
.kt-coords b { color: var(--accent-gold-soft, #f5e6b1); }
.kt-chanh { color: var(--text-primary, #e6eef5); display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.hex-link {
  color: var(--accent-teal, #5be5d3);
  text-decoration: none;
  border-bottom: 1px dashed rgba(91, 229, 211, 0.35);
  cursor: pointer;
  transition: color 0.12s, border-color 0.12s;
}
.hex-link:hover {
  color: var(--accent-gold, #e8c95a);
  border-bottom-color: rgba(232, 201, 90, 0.55);
}
.kt-chanh b { color: var(--text-muted, rgba(230,238,245,0.55)); font-weight: 500; }
.kt-chanh small { color: var(--text-muted, rgba(230,238,245,0.45)); font-size: 11px; }
.kt-chu-su {
  padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: 700;
  text-align: center;
}

.kt-detail {
  margin-top: 10px; padding-top: 10px;
  border-top: 1px solid var(--border-soft, rgba(255,255,255,0.08));
  display: flex; flex-direction: column; gap: 10px;
}

.three-quai {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;
}

.quai-block {
  background: rgba(255,255,255,0.03); padding: 10px;
  border: 1px solid var(--border-soft, rgba(255,255,255,0.08));
  border-radius: 6px; display: flex; flex-direction: column; gap: 4px;
}
.quai-block.menh {
  border-color: var(--border-accent, rgba(232,201,90,0.35));
  background: rgba(232,201,90,0.06);
}
.quai-block.clickable { cursor: pointer; transition: background 0.15s, transform 0.12s; }
.quai-block.clickable:hover {
  background: rgba(91, 229, 211, 0.08);
  border-color: rgba(91, 229, 211, 0.35);
  transform: translateY(-1px);
}
.quai-block.menh.clickable:hover {
  background: rgba(232, 201, 90, 0.12);
}
.quai-block h6 {
  margin: 0; font-size: 11px;
  color: var(--text-muted, rgba(230,238,245,0.5));
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700;
}
.quai-block .hexagram-image { align-self: center; margin: 2px 0; }
.quai-name {
  font-size: 16px; font-weight: 700; color: var(--accent-gold-soft, #f5e6b1);
}
.quai-binary {
  font-family: ui-monospace, monospace; font-size: 13px;
  color: var(--text-muted, rgba(230,238,245,0.6));
}
.quai-trigrams { display: flex; flex-direction: column; gap: 2px; font-size: 12px; }
.quai-trigrams b { color: var(--text-muted, rgba(230,238,245,0.45)); font-weight: 500; }
.quai-trigrams em { font-style: normal; font-weight: 700; margin-left: 3px; }
.menh-tag {
  font-size: 10px; color: var(--accent-gold, #e8c95a);
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700;
  margin-top: 4px;
}

.kt-meta {
  display: flex; gap: 16px; flex-wrap: wrap;
  font-size: 12px; color: var(--text-secondary, rgba(230,238,245,0.7));
}
.kt-meta b { color: var(--text-muted, rgba(230,238,245,0.5)); font-weight: 500; }

.luan-su-summary {
  display: flex; flex-direction: column; gap: 10px;
  background: rgba(91,229,211,0.05);
  border: 1px solid rgba(91,229,211,0.28);
  padding: 14px; border-radius: 8px;
}
.luan-banner {
  display: flex; gap: 12px; align-items: flex-start;
}
.banner-icon {
  font-size: 20px; color: var(--accent-teal, #5be5d3);
  line-height: 1; padding-top: 2px;
}
.luan-banner p {
  margin: 0; font-size: 14px; line-height: 1.55;
  color: var(--text-primary, #e6eef5);
}
.luan-meta {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
  padding-top: 8px;
  border-top: 1px dashed rgba(91,229,211,0.22);
}
.luan-cell { display: flex; flex-direction: column; gap: 3px; }
.luan-cell span {
  font-size: 10px; color: var(--text-muted, rgba(230,238,245,0.5));
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
}
.luan-cell strong { font-size: 16px; font-weight: 700; }

.deeper-h {
  margin: 18px 0 6px 0;
  font-size: 12px;
  color: var(--accent-teal, #5be5d3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 700;
  border-bottom: 1px dashed rgba(91, 229, 211, 0.25);
  padding-bottom: 4px;
}

.synthesis-card {
  background: linear-gradient(180deg, rgba(91, 229, 211, 0.06) 0%, rgba(232, 201, 90, 0.04) 100%);
  border: 1px solid rgba(91, 229, 211, 0.25);
  border-radius: 8px;
  padding: 16px 18px;
}
.synthesis-p {
  margin: 0 0 10px 0;
  font-size: 13.5px;
  line-height: 1.65;
  color: var(--text-primary, #e6eef5);
}
.synthesis-p:last-child { margin-bottom: 0; }
.synthesis-p:first-child { color: var(--accent-gold-soft, #f5e6b1); font-weight: 500; }
.synthesis-p:last-child {
  border-left: 3px solid var(--accent-teal, #5be5d3);
  padding-left: 12px;
  color: var(--accent-teal, #5be5d3);
}

.kt-narrative {
  margin-top: 8px;
  padding: 9px 12px;
  background: rgba(91, 229, 211, 0.04);
  border-left: 3px solid var(--accent-teal, #5be5d3);
  border-radius: 0 5px 5px 0;
}
.kt-narrative-role {
  display: flex;
  gap: 8px;
  align-items: baseline;
  font-size: 12px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
}
.kt-narrative-role b { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-weight: 500; }
.kt-narrative-icon { font-size: 13px; }
.kt-narrative-phase {
  margin: 4px 0 0 0;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text-primary, #e6eef5);
}
.kt-narrative-trans {
  margin: 3px 0 0 0;
  font-size: 11.5px;
  color: var(--accent-teal, #5be5d3);
}
.kt-narrative-trans em { font-style: italic; }

.domain-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 10px;
}
.domain-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-soft, rgba(255,255,255,0.08));
  border-radius: 8px; padding: 12px;
  display: flex; flex-direction: column; gap: 6px;
}
.domain-card[data-domain="marriage"] { border-left: 3px solid #c25a78; }
.domain-card[data-domain="wealth"]   { border-left: 3px solid #e8c95a; }
.domain-card[data-domain="house"]    { border-left: 3px solid #9a7b4a; }
.domain-card[data-domain="health"]   { border-left: 3px solid #5ab07a; }
.domain-card[data-domain="travel"]   { border-left: 3px solid #5be5d3; }
.domain-card[data-domain="life_arc"] { border-left: 3px solid #d68a4a; }
.domain-card[data-domain="children"] { border-left: 3px solid #f5b08c; }
.domain-card[data-domain="study"]    { border-left: 3px solid #88d39e; }
.domain-card[data-domain="lawsuit"]  { border-left: 3px solid #d65a4a; }
.domain-card[data-domain="career"]   { border-left: 3px solid #5b8ee5; }
.domain-head { display: flex; align-items: center; gap: 8px; }
.domain-icon { font-size: 16px; }
.domain-head h6 {
  margin: 0; font-size: 12px;
  color: var(--text-muted, rgba(230,238,245,0.6));
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700;
}
.domain-verdict {
  font-size: 15px; font-weight: 700;
  color: var(--accent-gold-soft, #f5e6b1);
}
.domain-explain {
  margin: 0; font-size: 13px; line-height: 1.5;
  color: var(--text-secondary, rgba(230,238,245,0.78));
}
.domain-evidence {
  list-style: none; margin: 4px 0 0 0; padding: 6px 10px;
  background: rgba(0,0,0,0.18); border-radius: 4px;
  display: flex; flex-direction: column; gap: 2px;
}
.domain-evidence li {
  font-size: 11px; color: var(--text-muted, rgba(230,238,245,0.55));
  line-height: 1.45;
}
.domain-evidence li::before { content: "› "; color: var(--accent-teal, #5be5d3); }
</style>
