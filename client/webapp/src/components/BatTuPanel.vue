<script setup>
import { computed, ref, watch } from "vue";
import { castBatTu, castHaLac } from "../lib/api";
import { useActivePersonBirth } from "../stores/useActivePersonBirth.js";
import { saveCasting, activePerson } from "../stores/userDataStore.js";
import { isAuthenticated } from "../stores/authStore.js";
import HexagramImage from "./HexagramImage.vue";
import HexagramDetailModal from "./HexagramDetailModal.vue";
import AuspiciousDayPanel from "./wiki/AuspiciousDayPanel.vue";
import { useHexagramModal } from "../composables/useHexagramModal";

// ── State ─────────────────────────────────────────────────────────────────────

const inputBirth = ref("");
const inputGender = ref("nam");
const inputTimezone = ref("Asia/Ho_Chi_Minh");

const batTuData = ref(null);
const haLacData = ref(null);
const loading = ref(false);
const errorMsg = ref("");

useActivePersonBirth(inputBirth);

const { openSlug, openHexagram, closeHexagram } = useHexagramModal();

// ── Visual maps ──────────────────────────────────────────────────────────────

const ELEMENT_COLOR = {
  kim: "#c0a878",
  hỏa: "#d65a4a",
  mộc: "#5ab07a",
  thủy: "#3a6cb0",
  thổ: "#9a7b4a",
};

const ELEMENT_GLYPH = {
  kim: "金", "mộc": "木", "thủy": "水", "hỏa": "火", "thổ": "土",
};

const THAP_THAN_COLOR = {
  "Tỷ Kiên":   "#c4c4c4",
  "Kiếp Tài":  "#9a9a9a",
  "Thực Thần": "#5ab07a",
  "Thương Quan": "#5be5d3",
  "Thiên Tài":  "#e8c95a",
  "Chính Tài":  "#d4af37",
  "Thất Sát":   "#d65a4a",
  "Chính Quan": "#5b8ee5",
  "Thiên Ấn":   "#c25a78",
  "Chính Ấn":   "#e0a8b8",
  "Bản thân":   "#f5e6b1",
};

// ── Actions ──────────────────────────────────────────────────────────────────

async function castAll() {
  if (!inputBirth.value) {
    errorMsg.value = "Cần nhập datetime sinh thần.";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  batTuData.value = null;
  haLacData.value = null;
  try {
    const [bt, hl] = await Promise.all([
      castBatTu({
        birthDatetimeLocal: inputBirth.value,
        timezone: inputTimezone.value,
        gender: inputGender.value,
      }),
      castHaLac({
        birthDatetimeLocal: inputBirth.value,
        timezone: inputTimezone.value,
        gender: inputGender.value,
      }),
    ]);
    batTuData.value = bt.bat_tu_state;
    haLacData.value = hl.ha_lac_state;

    // Auto-save to user_castings (silent — only if logged in)
    if (isAuthenticated.value && bt.bat_tu_state) {
      const dm = bt.bat_tu_state.tu_tru?.day_master;
      const cc = bt.bat_tu_state.cach_cuc?.cach_name;
      const verdict = `${dm?.stem || ""} ${dm?.element || ""}${cc ? " · " + cc : ""}`.trim();
      saveCasting({
        method: "bat_tu",
        subject_person_key: activePerson.value?.person_key || null,
        question: null,
        input_json: {
          birth_datetime_local: inputBirth.value,
          timezone: inputTimezone.value,
          gender: inputGender.value,
        },
        result_json: { bat_tu: bt, ha_lac: hl },
        verdict: verdict || null,
      });
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

function reset() {
  batTuData.value = null;
  haLacData.value = null;
  errorMsg.value = "";
}

// ── Derived ──────────────────────────────────────────────────────────────────

const dayMasterStem = computed(() => batTuData.value?.tu_tru?.day_master?.stem);
const dayMasterElement = computed(() => batTuData.value?.tu_tru?.day_master?.element);

const elementBarMax = computed(() => {
  if (!batTuData.value) return 1;
  const counts = batTuData.value.ngu_hanh.counts;
  return Math.max(...Object.values(counts), 1);
});

const orderedPillars = computed(() => {
  if (!batTuData.value) return [];
  const ps = batTuData.value.tu_tru.pillars;
  return ["year", "month", "day", "hour"].map((pos) => ps[pos]);
});

const orderedDecades = computed(() => haLacData.value?.decade_trajectory || []);

function cachCucPolarityClass(polarity) {
  if (!polarity) return "neutral";
  if (polarity.includes("lành") || polarity.includes("phú") || polarity.includes("quý")) return "favorable";
  if (polarity.includes("dữ") || polarity.includes("hung") || polarity.includes("phá")) return "challenging";
  return "mixed";
}

function formatSolarDateTime(iso) {
  if (!iso) return "";
  // "2026-05-19T22:00" → "19/05/2026 22:00"
  const [d, t] = iso.split("T");
  if (!d) return iso;
  const [y, m, day] = d.split("-");
  const time = (t || "").slice(0, 5);
  return time ? `${day}/${m}/${y} ${time}` : `${day}/${m}/${y}`;
}
</script>

<template>
  <section class="panel bt-panel">
    <div class="panel-title">
      <span>Bát Tự &amp; Hà Lạc Lý Số</span>
      <small>{{ batTuData?.method_id || "bat_tu_tu_tru_v1" }} + bat_tu_ha_lac_v1</small>
    </div>

    <p class="bt-note">
      <b>Bát Tự</b> = Tứ Trụ (Năm/Tháng/Ngày/Giờ) — phân tích Thiên Can + Địa Chi, Lục Thần,
      Ngũ Hành cân bằng. <b>Hà Lạc</b> = cross-module suy ra <b>2 quẻ Tiên thiên + Hậu thiên</b>
      của người + <b>chuỗi 12 hào ~ 84-90 năm</b> theo sách Học Năng 1974.
      <br />
      ⭐ Đây là tính năng moat — Kabala.vn có nhắc nhưng không ship.
    </p>

    <div class="bt-form">
      <label>
        <span>Sinh thần (datetime-local)</span>
        <input v-model="inputBirth" type="datetime-local" />
      </label>
      <label>
        <span>Giới tính</span>
        <select v-model="inputGender">
          <option value="nam">TA Nam</option>
          <option value="nữ">TA Nữ</option>
        </select>
      </label>
      <label>
        <span>Múi giờ</span>
        <input v-model="inputTimezone" type="text" />
      </label>
      <div class="bt-actions">
        <button class="apply-btn" @click="castAll" :disabled="loading">
          {{ loading ? "Đang luận..." : "Luận Bát Tự + Hà Lạc" }}
        </button>
        <button v-if="batTuData" class="secondary-btn" @click="reset" type="button">
          ✕ Luận lại
        </button>
      </div>
    </div>

    <p v-if="errorMsg" class="status-message error">{{ errorMsg }}</p>

    <!-- ── Bát Tự results ──────────────────────────────────────────── -->
    <template v-if="batTuData">
      <!-- Sinh thần dương + âm + tiết khí -->
      <div class="birth-summary" v-if="batTuData.tu_tru?.lunar">
        <div class="bs-row">
          <span class="bs-label">☀ Dương lịch</span>
          <span class="bs-val">{{ formatSolarDateTime(batTuData.birth_datetime_local) }}</span>
          <span class="bs-weekday">· {{ batTuData.tu_tru.lunar.weekday_vi }}</span>
        </div>
        <div class="bs-row">
          <span class="bs-label">🌙 Âm lịch</span>
          <span class="bs-val">
            ngày {{ batTuData.tu_tru.lunar.day }} tháng {{ batTuData.tu_tru.lunar.month }}{{
              batTuData.tu_tru.lunar.is_leap_month ? ' (nhuận)' : ''
            }} năm {{ batTuData.tu_tru.lunar.year }}
          </span>
          <span class="bs-ganzhi">· {{ batTuData.tu_tru.ganzhi_raw.year }} niên</span>
        </div>
        <div class="bs-row" v-if="batTuData.tu_tru.solar_term">
          <span class="bs-label">🌾 Tiết khí</span>
          <span class="bs-val">{{ batTuData.tu_tru.solar_term.name_vi }}</span>
        </div>
      </div>

      <h4 class="section-h">Tứ Trụ — 4 trụ</h4>
      <div class="pillar-grid">
        <article v-for="p in orderedPillars" :key="p.position"
          class="pillar-card" :class="{ 'is-day-master': p.position === 'day' }">
          <header class="pillar-head">
            <h5>{{ p.position_vi }}</h5>
            <small>{{ p.domain_vi }}</small>
          </header>
          <div class="pillar-stem-branch">
            <div class="pillar-stem"
              :style="{ background: ELEMENT_COLOR[p.stem_element] + '22', color: ELEMENT_COLOR[p.stem_element] }">
              <span class="char">{{ p.stem }}</span>
              <small>{{ ELEMENT_GLYPH[p.stem_element] }} {{ p.stem_element }} ({{ p.stem_polarity }})</small>
            </div>
            <div class="pillar-branch"
              :style="{ background: ELEMENT_COLOR[p.branch_element] + '15', color: ELEMENT_COLOR[p.branch_element] }">
              <span class="char">{{ p.branch }}</span>
              <small>{{ ELEMENT_GLYPH[p.branch_element] }} {{ p.branch_element }}</small>
            </div>
          </div>
          <div class="pillar-thapthan">
            <span class="tt-tag" :style="{ borderColor: THAP_THAN_COLOR[p.stem_thap_than] || '#aaa', color: THAP_THAN_COLOR[p.stem_thap_than] || '#aaa' }">
              {{ p.stem_thap_than }}
            </span>
          </div>
          <ul class="pillar-hidden" v-if="p.hidden_stems_with_thap_than?.length">
            <li v-for="h in p.hidden_stems_with_thap_than" :key="h.stem">
              <em>{{ h.stem }}</em> → {{ h.thap_than }}
            </li>
          </ul>
        </article>
      </div>

      <h4 class="section-h">Nhật chủ (Day Master) — {{ dayMasterStem }} ({{ dayMasterElement }})</h4>
      <div class="dm-card">
        <div class="dm-strength" :data-tag="batTuData.ngu_hanh.day_master_assessment.strength_tag">
          <span class="dm-label">Cường độ</span>
          <strong>{{ batTuData.ngu_hanh.day_master_assessment.strength_label }}</strong>
          <small>Support {{ batTuData.ngu_hanh.day_master_assessment.support_score }} · Drain {{ batTuData.ngu_hanh.day_master_assessment.drain_score }}</small>
        </div>
        <div class="dm-breakdown">
          <div v-for="(score, key) in batTuData.ngu_hanh.day_master_assessment.breakdown" :key="key" class="dm-bar">
            <span class="dm-bar-label">{{ key.replace(/_/g, ' ') }}</span>
            <div class="dm-bar-track">
              <div class="dm-bar-fill" :style="{ width: (score / elementBarMax * 100) + '%' }"></div>
            </div>
            <span class="dm-bar-value">{{ score }}</span>
          </div>
        </div>
      </div>

      <h4 class="section-h">Ngũ hành phân bố</h4>
      <div class="elements-grid">
        <div v-for="(count, el) in batTuData.ngu_hanh.counts" :key="el" class="element-cell"
          :style="{ borderLeft: '3px solid ' + ELEMENT_COLOR[el] }">
          <span class="element-name" :style="{ color: ELEMENT_COLOR[el] }">{{ ELEMENT_GLYPH[el] }} {{ el }}</span>
          <strong>{{ count }}</strong>
          <div class="element-bar">
            <div :style="{ width: (count / elementBarMax * 100) + '%', background: ELEMENT_COLOR[el] }"></div>
          </div>
        </div>
      </div>

      <!-- ── Cách Cục ────────────────────────────────────────────── -->
      <template v-if="batTuData.cach_cuc">
        <h4 class="section-h">Cách Cục — pattern cổ điển của lá số</h4>
        <article class="cach-cuc-card" :data-polarity="cachCucPolarityClass(batTuData.cach_cuc.polarity)">
          <header>
            <h3>{{ batTuData.cach_cuc.cach_name }}</h3>
            <span class="cc-polarity">{{ batTuData.cach_cuc.polarity }}</span>
          </header>
          <p class="cc-based-on">
            <span class="cc-label">Xác định dựa trên:</span>
            <b>{{ batTuData.cach_cuc.based_on }}</b>
            <span v-if="batTuData.cach_cuc.based_on_thap_than">
              → Thập Thần: <em>{{ batTuData.cach_cuc.based_on_thap_than }}</em>
            </span>
          </p>
          <p class="cc-essence">{{ batTuData.cach_cuc.essence }}</p>
          <div class="cc-prosand-cons">
            <div class="cc-fav">
              <h6>✦ Thuận / Hợp</h6>
              <p>{{ batTuData.cach_cuc.favorable }}</p>
            </div>
            <div class="cc-ky">
              <h6>⚠ Kỵ / Tránh</h6>
              <p>{{ batTuData.cach_cuc.ky }}</p>
            </div>
          </div>
          <p class="cc-note"><em>{{ batTuData.cach_cuc.note }}</em></p>
        </article>
      </template>

      <!-- ── Dụng Thần / Hỷ Thần / Kỵ Thần ──────────────────────── -->
      <h4 class="section-h">Dụng Thần — hành cốt yếu cho nhật chủ</h4>
      <div class="dung-than-card">
        <div class="dt-trio">
          <div class="dt-cell dt-dung"
            :style="{ background: ELEMENT_COLOR[batTuData.dung_than.dung_than_element] + '15', borderColor: ELEMENT_COLOR[batTuData.dung_than.dung_than_element] }">
            <span class="dt-label">★ Dụng Thần</span>
            <strong :style="{ color: ELEMENT_COLOR[batTuData.dung_than.dung_than_element] }">
              {{ ELEMENT_GLYPH[batTuData.dung_than.dung_than_element] }} {{ batTuData.dung_than.dung_than_element }}
            </strong>
            <small>{{ batTuData.dung_than.dung_than_role_vi }}</small>
          </div>
          <div class="dt-cell dt-hy"
            :style="{ background: ELEMENT_COLOR[batTuData.dung_than.hy_than_element] + '10', borderColor: ELEMENT_COLOR[batTuData.dung_than.hy_than_element] + '88' }">
            <span class="dt-label">Hỷ Thần</span>
            <strong :style="{ color: ELEMENT_COLOR[batTuData.dung_than.hy_than_element] }">
              {{ ELEMENT_GLYPH[batTuData.dung_than.hy_than_element] }} {{ batTuData.dung_than.hy_than_element }}
            </strong>
            <small>hỗ trợ Dụng Thần</small>
          </div>
          <div class="dt-cell dt-ky"
            :style="{ background: '#d65a4a0a', borderColor: '#d65a4a88' }">
            <span class="dt-label">⚠ Kỵ Thần</span>
            <strong style="color: #d65a4a">
              {{ ELEMENT_GLYPH[batTuData.dung_than.ky_than_element] }} {{ batTuData.dung_than.ky_than_element }}
            </strong>
            <small>kẻ địch của Dụng Thần</small>
          </div>
        </div>
        <p class="dt-reason">{{ batTuData.dung_than.dung_than_reason }}</p>
        <p class="dt-note"><em>{{ batTuData.dung_than.note }}</em></p>
      </div>

      <!-- ── Vòng Trường Sinh ────────────────────────────────────── -->
      <h4 class="section-h">Vòng Trường Sinh — sức sống Day Master tại mỗi trụ</h4>
      <div class="truongsinh-grid">
        <article v-for="(p, pos) in batTuData.truong_sinh.pillars" :key="pos"
          class="ts-cell" :data-score="p.strength_score >= 2 ? 'high' : p.strength_score <= -2 ? 'low' : 'mid'">
          <header>
            <h6>{{ p.pillar_position_vi }}</h6>
            <small>{{ p.branch }}</small>
          </header>
          <strong>{{ p.phase }}</strong>
          <span class="ts-score" :data-positive="p.strength_score > 0">
            {{ p.strength_score >= 0 ? '+' : '' }}{{ p.strength_score }}
          </span>
        </article>
      </div>
      <p class="ts-total">
        Tổng điểm sức sống: <b>{{ batTuData.truong_sinh.total_strength_score }}</b>
        — Trường Sinh khởi tại {{ batTuData.truong_sinh.truong_sinh_start_branch }}.
      </p>

      <!-- ── Thần Sát ─────────────────────────────────────────────── -->
      <h4 class="section-h">Thần Sát — sao phụ trong lá số</h4>
      <div v-if="!batTuData.than_sat.length" class="ts-empty">
        Lá số này không có sao Thần Sát nào trong 15 sao cốt lõi đang sàng.
      </div>
      <ul v-else class="than-sat-list">
        <li v-for="(s, i) in batTuData.than_sat" :key="i" class="ts-star" :data-polarity="s.polarity">
          <div class="ts-star-head">
            <strong>{{ s.name }}</strong>
            <span class="ts-tag">{{ s.short_tag }}</span>
            <span class="ts-polarity">{{ s.polarity }}</span>
            <small class="ts-where">tại trụ {{ s.found_at_pillar }} ({{ s.branch_or_stem }})</small>
          </div>
          <p class="ts-desc">{{ s.description }}</p>
        </li>
      </ul>

      <!-- ── Đại Vận ──────────────────────────────────────────────── -->
      <h4 class="section-h">Đại Vận — chu kỳ 10 năm</h4>
      <p class="dv-meta">
        Hướng: <b>{{ batTuData.dai_van.direction_label }}</b> ·
        Tuổi bắt đầu vận: <b>{{ batTuData.dai_van.starting_age }}</b>
        <small>({{ batTuData.dai_van.starting_age_estimation }})</small>
        <span v-if="batTuData.dai_van.distance_days_to_reference_tiet_khi !== null && batTuData.dai_van.distance_days_to_reference_tiet_khi !== undefined" class="dv-distance">
          · {{ batTuData.dai_van.distance_days_to_reference_tiet_khi }} ngày từ tiết khí gần nhất
          <small v-if="batTuData.dai_van.reference_tiet_khi_date">
            ({{ batTuData.dai_van.reference_tiet_khi_date.slice(0, 10) }})
          </small>
        </span>
      </p>
      <ol class="dai-van-list">
        <li v-for="c in batTuData.dai_van.cycles" :key="c.cycle_index" class="dv-cycle">
          <div class="dv-age">
            <strong>{{ c.start_age }}-{{ c.end_age }}</strong>
            <small>tuổi</small>
          </div>
          <div class="dv-stembr">
            <span class="dv-stem">{{ c.stem }}</span>
            <span class="dv-branch">{{ c.branch }}</span>
          </div>
          <span class="dv-index">V{{ c.cycle_index }}</span>
        </li>
      </ol>
      <p class="dv-note" v-if="batTuData.dai_van.starting_age_note">
        <em>{{ batTuData.dai_van.starting_age_note }}</em>
      </p>
    </template>

    <!-- ── Hà Lạc results ──────────────────────────────────────────── -->
    <template v-if="haLacData">
      <h4 class="section-h ha-lac-h">
        ⭐ Hà Lạc Lý Số — 2 quẻ cốt mệnh
      </h4>
      <p class="ha-lac-intro">
        Thiên số <b>{{ haLacData.number_pools.tien_raw }}</b> → {{ haLacData.number_pools.tien_reduced }} ·
        Địa số <b>{{ haLacData.number_pools.dia_raw }}</b> → {{ haLacData.number_pools.dia_reduced }}
        · Năm {{ haLacData.year_stem_polarity }} ({{ haLacData.gender }})
      </p>

      <div class="halac-quai-pair">
        <article class="halac-quai" data-which="tien">
          <header>
            <h5>Tiên thiên quái (先天卦)</h5>
            <small>Mệnh cốt — gốc đời người</small>
          </header>
          <div class="halac-quai-body" @click="openHexagram(haLacData.tien_thien_quai.king_wen_index)" title="Mở chi tiết quẻ">
            <HexagramImage :king-wen="haLacData.tien_thien_quai.king_wen_index" :size="80" />
            <div>
              <strong>{{ haLacData.tien_thien_quai.name_vi }}</strong>
              <small>quẻ {{ haLacData.tien_thien_quai.king_wen_index }}</small>
              <p>Thượng: {{ haLacData.tien_thien_quai.upper_trigram }} / Hạ: {{ haLacData.tien_thien_quai.lower_trigram }}</p>
              <p class="nd-tag">🌟 Nguyên đường: <b>hào {{ haLacData.tien_thien_quai.nguyen_duong_line }}</b></p>
            </div>
          </div>
        </article>

        <div class="halac-arrow">→</div>

        <article class="halac-quai" data-which="hau">
          <header>
            <h5>Hậu thiên quái (後天卦)</h5>
            <small>Vận dụng — cách thức vận hành</small>
          </header>
          <div class="halac-quai-body" @click="openHexagram(haLacData.hau_thien_quai.king_wen_index)" title="Mở chi tiết quẻ">
            <HexagramImage :king-wen="haLacData.hau_thien_quai.king_wen_index" :size="80" />
            <div>
              <strong>{{ haLacData.hau_thien_quai.name_vi }}</strong>
              <small>quẻ {{ haLacData.hau_thien_quai.king_wen_index }}</small>
              <p>Thượng: {{ haLacData.hau_thien_quai.upper_trigram }} / Hạ: {{ haLacData.hau_thien_quai.lower_trigram }}</p>
              <p class="nd-tag">🌟 Nguyên đường: <b>hào {{ haLacData.hau_thien_quai.nguyen_duong_line }}</b></p>
            </div>
          </div>
        </article>
      </div>

      <h4 class="section-h">Lộ trình 12 hào — {{ haLacData.lifespan_span.total_years }} năm cuộc đời</h4>
      <ol class="trajectory">
        <li v-for="stage in orderedDecades" :key="stage.stage_index"
          class="traj-stage"
          :class="{ 'is-nd': stage.is_nguyen_duong, [`is-${stage.hexagram}`]: true, [`pol-${stage.polarity}`]: true }">
          <div class="traj-age">
            <strong>{{ stage.age_start }}-{{ stage.age_end }}</strong>
            <small>tuổi</small>
          </div>
          <div class="traj-info">
            <span class="traj-label">{{ stage.label }}</span>
            <span class="traj-meta">{{ stage.hexagram === 'tien' ? 'Tiên thiên' : 'Hậu thiên' }} · hào {{ stage.line_position }} · {{ stage.polarity }}</span>
          </div>
        </li>
      </ol>

      <p v-if="haLacData.notes?.length" class="halac-notes-block">
        <b>Ghi chú thuật toán:</b>
        <span v-for="(n, i) in haLacData.notes" :key="i">{{ n }}</span>
      </p>

      <p class="halac-interpretation">
        <b>Hướng diễn giải:</b> {{ haLacData.interpretation_hint }}
      </p>

      <p class="footer-ref">Nguồn: {{ haLacData.source_ref }}</p>
    </template>

    <!-- 📅 Chọn ngày tốt — Bát Tự + Mai Hoa + Hoàng Đạo -->
    <div class="bt-auspicious-section">
      <hr class="bt-divider" />
      <AuspiciousDayPanel />
    </div>

    <HexagramDetailModal
      v-if="openSlug"
      :slug="openSlug"
      @close="closeHexagram"
    />
  </section>
</template>

<style scoped>
.bt-panel { display: flex; flex-direction: column; gap: 14px; }

.bt-note {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  border-left: 3px solid var(--accent-gold, #e8c95a);
  padding-left: 12px;
  margin: 0;
  line-height: 1.6;
}
.bt-note b { color: var(--accent-gold-soft, #f5e6b1); }

.bt-form {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
}
.bt-form label { display: flex; flex-direction: column; gap: 4px; }
.bt-form label span {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}
.bt-actions {
  grid-column: 1 / -1;
  display: flex; gap: 8px; align-items: center;
}

.birth-summary {
  margin: 12px 0 4px 0;
  padding: 10px 14px;
  background: rgba(245, 230, 177, 0.05);
  border-left: 3px solid var(--accent-gold-soft, #f5e6b1);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.bs-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: baseline;
  font-size: 13px;
  line-height: 1.5;
}
.bs-label {
  min-width: 90px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.bs-val {
  color: var(--text-strong, #e6eef5);
  font-weight: 500;
}
.bs-weekday, .bs-ganzhi {
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-size: 12px;
}
.bs-ganzhi {
  color: var(--accent-gold-soft, #f5e6b1);
  font-style: italic;
}

.section-h {
  margin: 14px 0 6px 0;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 700;
}
.ha-lac-h { color: var(--accent-gold-soft, #f5e6b1); font-size: 14px; }

/* ── Pillars grid ──────────────────────────────────────────────────────── */
.pillar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}
.pillar-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 7px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pillar-card.is-day-master {
  border-color: rgba(232, 201, 90, 0.45);
  background: rgba(232, 201, 90, 0.06);
  box-shadow: 0 0 0 1px rgba(232, 201, 90, 0.2);
}
.pillar-head h5 {
  margin: 0; font-size: 14px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.pillar-head small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.pillar-stem-branch { display: flex; gap: 6px; }
.pillar-stem, .pillar-branch {
  flex: 1;
  padding: 6px 8px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 1px;
  align-items: center;
}
.pillar-stem .char, .pillar-branch .char {
  font-size: 17px;
  font-weight: 700;
}
.pillar-stem small, .pillar-branch small {
  font-size: 10px;
  opacity: 0.85;
}
.pillar-thapthan { text-align: center; }
.tt-tag {
  display: inline-block;
  border: 1px solid;
  padding: 3px 9px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.04);
}
.pillar-hidden {
  list-style: none;
  margin: 0;
  padding: 6px 8px;
  background: rgba(0, 0, 0, 0.18);
  border-radius: 3px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.pillar-hidden li {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  line-height: 1.4;
}
.pillar-hidden em { color: var(--accent-gold-soft, #f5e6b1); font-style: normal; }

/* ── Day Master card ───────────────────────────────────────────────────── */
.dm-card {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 12px;
  background: rgba(232, 201, 90, 0.05);
  border: 1px solid rgba(232, 201, 90, 0.22);
  border-radius: 7px;
  padding: 12px;
}
.dm-strength { display: flex; flex-direction: column; gap: 4px; }
.dm-label {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.dm-strength strong {
  font-size: 16px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.dm-strength[data-tag="strong"] strong { color: #ffaf5e; }
.dm-strength[data-tag="weak"] strong { color: #5be5d3; }
.dm-strength[data-tag="balanced"] strong { color: #5ab07a; }
.dm-strength small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}
.dm-breakdown { display: flex; flex-direction: column; gap: 4px; }
.dm-bar {
  display: grid;
  grid-template-columns: 130px 1fr 40px;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}
.dm-bar-label { color: var(--text-muted, rgba(230, 238, 245, 0.6)); }
.dm-bar-track {
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  overflow: hidden;
}
.dm-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #5ab07a 0%, #e8c95a 100%);
  border-radius: 3px;
}
.dm-bar-value { text-align: right; font-family: ui-monospace, monospace; color: var(--text-primary, #e6eef5); }

/* ── Elements grid ─────────────────────────────────────────────────────── */
.elements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}
.element-cell {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 5px;
  padding: 8px 10px;
}
.element-name {
  font-size: 12px;
  font-weight: 700;
}
.element-cell strong {
  display: block;
  font-size: 18px;
  color: var(--text-primary, #e6eef5);
  margin: 2px 0 6px;
}
.element-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
}
.element-bar > div { height: 100%; border-radius: 2px; }

/* ── Hà Lạc section ────────────────────────────────────────────────────── */
.ha-lac-intro {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  font-family: ui-monospace, monospace;
  background: rgba(91, 229, 211, 0.04);
  border: 1px solid rgba(91, 229, 211, 0.2);
  padding: 8px 12px;
  border-radius: 5px;
  margin: 0;
}
.ha-lac-intro b { color: var(--accent-teal, #5be5d3); }

.halac-quai-pair {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  align-items: center;
}
.halac-quai {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 7px;
  padding: 12px;
}
.halac-quai[data-which="tien"] { border-left: 3px solid var(--accent-gold, #e8c95a); }
.halac-quai[data-which="hau"]  { border-left: 3px solid var(--accent-teal, #5be5d3); }
.halac-quai header h5 {
  margin: 0 0 2px 0;
  font-size: 13px;
  color: var(--text-primary, #e6eef5);
}
.halac-quai header small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}
.halac-quai-body {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  cursor: pointer;
  margin-top: 8px;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.15s;
}
.halac-quai-body:hover { background: rgba(91, 229, 211, 0.06); }
.halac-quai-body > div { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.halac-quai-body strong {
  font-size: 18px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.halac-quai-body small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}
.halac-quai-body p {
  margin: 2px 0;
  font-size: 12px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
}
.nd-tag { color: var(--accent-teal, #5be5d3) !important; }
.nd-tag b { color: var(--accent-gold, #e8c95a); }
.halac-arrow {
  font-size: 28px;
  color: var(--accent-gold, #e8c95a);
  text-align: center;
}

/* ── Decade trajectory ─────────────────────────────────────────────────── */
.trajectory {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 6px;
}
.traj-stage {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 5px;
  padding: 8px 10px;
  display: flex;
  gap: 10px;
  align-items: center;
}
.traj-stage.is-nd {
  background: rgba(232, 201, 90, 0.09);
  border-color: rgba(232, 201, 90, 0.4);
}
.traj-stage.is-hau { border-left: 3px solid var(--accent-teal, #5be5d3); }
.traj-stage.is-tien { border-left: 3px solid var(--accent-gold, #e8c95a); }
.traj-age {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 50px;
}
.traj-age strong {
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.traj-age small {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.traj-info { display: flex; flex-direction: column; gap: 1px; }
.traj-label {
  font-size: 12px;
  color: var(--text-primary, #e6eef5);
}
.traj-meta {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}

.halac-notes-block {
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  background: rgba(214, 90, 74, 0.06);
  border-left: 2px solid #d65a4a;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0;
}
.halac-notes-block b { color: #f5b08c; }

.halac-interpretation {
  font-size: 13px;
  font-style: italic;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  border-left: 2px solid var(--accent-teal, #5be5d3);
  padding-left: 12px;
  margin: 0;
}

.footer-ref {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.4));
  text-align: right;
  font-style: italic;
  margin: 0;
}

/* ── Cách Cục ──────────────────────────────────────────────────────────── */
.cach-cuc-card {
  background: rgba(232, 201, 90, 0.04);
  border: 1px solid rgba(232, 201, 90, 0.2);
  border-radius: 8px;
  padding: 14px 16px;
}
.cach-cuc-card[data-polarity="favorable"] { border-left: 3px solid #5ab07a; }
.cach-cuc-card[data-polarity="mixed"]     { border-left: 3px solid #c0a878; }
.cach-cuc-card[data-polarity="challenging"] { border-left: 3px solid #d65a4a; }
.cach-cuc-card[data-polarity="neutral"]   { border-left: 3px solid #9a9a9a; }

.cach-cuc-card header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1px dashed rgba(232, 201, 90, 0.2);
  padding-bottom: 8px;
  margin-bottom: 10px;
}
.cach-cuc-card header h3 {
  margin: 0;
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 16px;
}
.cc-polarity {
  font-size: 11px;
  padding: 3px 9px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  font-weight: 600;
}
.cc-based-on {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.65));
}
.cc-based-on b { color: var(--accent-gold-soft, #f5e6b1); }
.cc-based-on em { color: var(--accent-teal, #5be5d3); font-style: normal; }
.cc-label {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.45));
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-right: 4px;
}
.cc-essence {
  margin: 0 0 10px 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary, #e6eef5);
  font-weight: 500;
}
.cc-prosand-cons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}
.cc-fav, .cc-ky { padding: 10px 12px; border-radius: 5px; }
.cc-fav {
  background: rgba(90, 176, 122, 0.06);
  border-left: 3px solid #5ab07a;
}
.cc-ky {
  background: rgba(214, 90, 74, 0.06);
  border-left: 3px solid #d65a4a;
}
.cc-fav h6, .cc-ky h6 {
  margin: 0 0 4px 0;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.cc-fav h6 { color: #88d39e; }
.cc-ky h6  { color: #f5b08c; }
.cc-fav p, .cc-ky p {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text-secondary, rgba(230, 238, 245, 0.82));
}
.cc-note {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-style: italic;
  margin: 0;
}

/* ── Dụng Thần ─────────────────────────────────────────────────────────── */
.dung-than-card {
  background: rgba(232, 201, 90, 0.04);
  border: 1px solid rgba(232, 201, 90, 0.2);
  border-radius: 8px;
  padding: 14px;
}
.dt-trio {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}
.dt-cell {
  border: 1px solid;
  border-radius: 6px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.dt-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  font-weight: 700;
}
.dt-cell strong {
  font-size: 18px;
  font-weight: 700;
}
.dt-cell small {
  font-size: 11px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.7));
}
.dt-reason {
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-primary, #e6eef5);
  margin: 0 0 8px 0;
}
.dt-note {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-style: italic;
  margin: 0;
  border-top: 1px dashed rgba(255, 255, 255, 0.06);
  padding-top: 8px;
}
.dt-note em { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-style: italic; }
.dv-distance { color: var(--accent-teal, #5be5d3); font-size: 12px; }
.dv-distance small { color: var(--text-muted, rgba(230, 238, 245, 0.4)); }

/* ── Trường Sinh ───────────────────────────────────────────────────────── */
.truongsinh-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}
.ts-cell {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 6px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ts-cell[data-score="high"] { border-left: 3px solid #5ab07a; }
.ts-cell[data-score="mid"]  { border-left: 3px solid #9a9a9a; }
.ts-cell[data-score="low"]  { border-left: 3px solid #d65a4a; }
.ts-cell header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ts-cell h6 {
  margin: 0;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.ts-cell header small {
  font-size: 14px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.7));
  font-weight: 600;
}
.ts-cell strong {
  font-size: 15px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.ts-score {
  font-size: 12px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  color: #d65a4a;
}
.ts-score[data-positive="true"] { color: #5ab07a; }
.ts-total {
  margin: 6px 0 0 0;
  font-size: 12px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.7));
}
.ts-total b { color: var(--accent-gold-soft, #f5e6b1); }

/* ── Thần Sát ──────────────────────────────────────────────────────────── */
.ts-empty {
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-style: italic;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
}
.than-sat-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 8px;
}
.ts-star {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 5px;
  padding: 10px 12px;
}
.ts-star[data-polarity="lành"] { border-left: 3px solid #5ab07a; }
.ts-star[data-polarity="dữ"] { border-left: 3px solid #d65a4a; }
.ts-star[data-polarity="trung tính"] { border-left: 3px solid #c0a878; }
.ts-star-head { display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
.ts-star-head strong {
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.ts-tag {
  background: rgba(91, 229, 211, 0.08);
  border: 1px solid rgba(91, 229, 211, 0.25);
  color: var(--accent-teal, #5be5d3);
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
}
.ts-polarity {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
}
.ts-where {
  font-size: 10.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  margin-left: auto;
}
.ts-desc {
  margin: 4px 0 0 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-secondary, rgba(230, 238, 245, 0.75));
}

/* ── Đại Vận ────────────────────────────────────────────────────────────── */
.dv-meta {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  margin: 0;
}
.dv-meta b { color: var(--accent-gold-soft, #f5e6b1); }
.dv-meta small { color: var(--text-muted, rgba(230, 238, 245, 0.5)); }
.dai-van-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 6px;
}
.dv-cycle {
  background: rgba(232, 201, 90, 0.05);
  border: 1px solid rgba(232, 201, 90, 0.18);
  border-radius: 5px;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}
.dv-age { display: flex; flex-direction: column; align-items: center; min-width: 46px; }
.dv-age strong {
  font-size: 12px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.dv-age small {
  font-size: 9.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
}
.dv-stembr {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
}
.dv-stem {
  font-size: 14px;
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 700;
}
.dv-branch {
  font-size: 13px;
  color: var(--text-primary, #e6eef5);
}
.dv-index {
  position: absolute;
  top: 4px;
  right: 6px;
  font-size: 9.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.4));
  font-weight: 700;
}
.dv-note {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  font-style: italic;
  margin: 4px 0 0 0;
}

@media (max-width: 720px) {
  .halac-quai-pair { grid-template-columns: 1fr; }
  .halac-arrow { transform: rotate(90deg); }
  .bt-form { grid-template-columns: 1fr; }
  .dm-card { grid-template-columns: 1fr; }
  .dt-trio { grid-template-columns: 1fr; }
  .cc-prosand-cons { grid-template-columns: 1fr; }
}

/* Auspicious day section — separator between Hà Lạc trajectory and date picker */
.bt-auspicious-section {
  margin-top: 2.5rem;
}
.bt-divider {
  border: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-color, #ddd), transparent);
  margin: 1.5rem 0 1rem;
}
</style>
