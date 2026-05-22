<script setup>
/**
 * Chiếu Đởm Kinh panel — kinh phái khác Tử Vi Đẩu Số chính thống.
 * 18 Phi Tinh + 12 cung × 18 sao matrix + cách cục mới + Nhập Cốt Tiên Kinh tổng đoán.
 * Source: Q4 p0269-p0300 (Phase A thâm nhuần 2026-05-20)
 */
import { computed, ref, onMounted } from "vue";
import { activePerson } from "../stores/userDataStore.js";

const cdkChart = ref(null);
const phiTinh18 = ref(null);
const phiTinhCards = ref([]);
const cachCuc = ref(null);
const nhapCot = ref(null);
const loading = ref(false);
const error = ref("");
const activeStarId = ref(null);
const selectedArtCard = ref(null);

const BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];

const CHART_STAR_ID = {
  "Tử": "tu",
  "Văn": "van",
  "Phúc": "phuc",
  "Lộc": "loc",
  "Ấn": "an",
  "Thọ": "tho",
  "Trượng": "truong",
  "Khố": "kho",
  "Không": "khong",
  "Diêu": "dieu",
  "Quý": "quy",
  "Loan": "hong",
  "Hồng": "hong",
  "Dị": "di",
  "Mao": "mao",
  "Hư": "hu",
  "Quán": "quan",
  "Hình": "hinh",
  "Nhận": "nhan",
  "Khốc": "khoc",
};

const NHAP_COT_STAR_NAME = {
  "Tử": "Tử Vi",
  "Hư": "Thiên Hư",
  "Quý": "Thiên Quý",
  "Ấn": "Thiên Ấn",
  "Thọ": "Thiên Thọ",
  "Không": "Thiên Hư",
  "Loan": "Hồng Loan",
  "Hồng": "Hồng Loan",
  "Khố": "Thiên Khố",
  "Quán": "Thiên Quán",
  "Văn": "Văn Xương",
  "Phúc": "Phúc Lộc",
  "Lộc": "Phúc Lộc",
  "Trượng": "Thiên Trượng",
  "Dị": "Thiên Dị",
  "Mao": "Mao Đầu",
  "Nhận": "Thiên Nhận (Kình Dương)",
  "Hình": "Thiên Hình",
  "Khốc": "Thiên Khốc",
  "Diêu": "Thiên Diêu",
};

const phiTinhCardsByStarId = computed(() => {
  return new Map(phiTinhCards.value.map((card) => [card.star_id, card]));
});

const nhapCotByStar = computed(() => {
  return new Map((nhapCot.value?.per_star_tong_doan || []).map((item) => [item.star, item]));
});

const cdkBranchMap = computed(() => {
  const map = new Map(BRANCHES.map((branch) => [branch, []]));
  for (const [star, branch] of Object.entries(cdkChart.value?.stars || {})) {
    if (!map.has(branch)) map.set(branch, []);
    map.get(branch).push({
      star,
      branch,
      art: chartArtFor(star),
      meaning: starMeaningFor(star, branch),
    });
  }
  return BRANCHES.map((branch) => ({
    branch,
    stars: map.get(branch) || [],
    isMenh: branch === cdkChart.value?.menh_branch,
  }));
});

const cdkMenhStars = computed(() => {
  const menh = cdkChart.value?.menh_branch;
  if (!menh) return [];
  return Object.entries(cdkChart.value?.stars || {})
    .filter(([, branch]) => branch === menh)
    .map(([star, branch]) => ({
      star,
      branch,
      art: chartArtFor(star),
      meaning: starMeaningFor(star, branch),
    }));
});

async function fetchJsonOrNull(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const text = await response.text();
    if (!response.ok || !text) return null;
    return JSON.parse(text);
  } catch (err) {
    console.warn("Cannot load Chiếu Đởm Kinh payload:", url, err);
    return null;
  }
}

function phiTinhArtFor(star) {
  const card = phiTinhCardsByStarId.value.get(star?.id);
  return card?.image ? card : null;
}

function chartArtFor(starName) {
  const starId = CHART_STAR_ID[starName];
  if (!starId) return null;
  const card = phiTinhCardsByStarId.value.get(starId);
  return card?.image ? card : null;
}

function starMeaningFor(starName, branch) {
  const lookupName = NHAP_COT_STAR_NAME[starName] || starName;
  const item = nhapCotByStar.value.get(lookupName);
  const isHy = item?.hy_cung?.includes(branch) || false;
  return {
    lookupName,
    category: item?.category || "chưa phân loại",
    isHy,
    status: item ? (isHy ? "Hỷ cung" : "Không thuộc hỷ cung") : "Chưa có tổng đoán",
    summary: item?.verdict_summary || "Chưa có câu tổng đoán trong Nhập Cốt Tiên Kinh.",
    source: item?.source_ref || "",
  };
}

async function loadAll() {
  loading.value = true;
  error.value = "";
  const person = activePerson.value;
  const genderText = String(person?.gender || person?.gender_optional || "nam").toLowerCase();
  const chartPayload = person?.person_key
    ? { person_key: person.person_key }
    : person?.birth_datetime_local
      ? {
          birth_datetime_local: person.birth_datetime_local,
          timezone: person.timezone || "Asia/Ho_Chi_Minh",
          gender: genderText.includes("nữ") || genderText.includes("nu") ? "nữ" : "nam",
          name: person.name || person.label || "Người",
        }
      : null;
  try {
    const [chart, phi, cards, cach, ncot] = await Promise.all([
      chartPayload ? fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh/cast", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify(chartPayload)
      }) : Promise.resolve(null),
      fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh-phi-tinh"),
      fetchJsonOrNull("/oracle-cards/chieu-dom-kinh/18-phi-tinh/cards.json"),
      fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh-cach-cuc"),
      fetchJsonOrNull("/api/tu-vi/q4/nhap-cot-tien-kinh"),
    ]);
    if (chart && chart.status === "ok") cdkChart.value = chart;
    if (phi?.status === "ok") phiTinh18.value = phi;
    if (cards?.cards) phiTinhCards.value = cards.cards;
    if (cach?.status === "ok") cachCuc.value = cach;
    if (ncot?.status === "ok") nhapCot.value = ncot;
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

onMounted(loadAll);

function toggleStar(id) {
  activeStarId.value = activeStarId.value === id ? null : id;
}

function openArtCard(card) {
  if (card) selectedArtCard.value = card;
}
</script>

<template>
  <section class="cdk-panel">
    <header class="cdk-head">
      <h2>📜 Chiếu Đởm Kinh — Phái khác Tử Vi Đẩu Số</h2>
      <p class="cdk-sub">
        Kinh phái khác trong Q4 (p0269-p0300) — <b>18 Phi Tinh</b> (KHÁC 14 chính tinh chính thống) +
        convention âm-dương ĐẢO + an sao formula riêng.
      </p>
    </header>

    <p v-if="loading" class="cdk-loading">Đang tải...</p>
    <p v-if="error" class="cdk-error">⚠ {{ error }}</p>

    <!-- Anh's chart CDK -->
    <section v-if="cdkChart" class="cdk-chart">
      <h3>🌟 Lá số CDK của anh</h3>
      <div class="cdk-meta">
        <span><b>Mệnh CDK:</b> {{ cdkChart.menh_branch }}</span>
        <span><b>Năm:</b> {{ cdkChart.year_stem }} {{ cdkChart.year_branch }}</span>
        <span><b>Tháng âm:</b> {{ cdkChart.lunar_month }}</span>
        <span><b>Giờ:</b> {{ cdkChart.hour_branch }}</span>
      </div>
      <div class="cdk-chart-guide">
        <div>
          <b>1. An sao</b>
          <span>Engine đặt từng Phi Tinh vào một địa chi: ví dụ “Tử → Hợi” nghĩa là sao Tử đang đóng cung Hợi.</span>
        </div>
        <div>
          <b>2. Ảnh sao</b>
          <span>Ảnh là pháp tượng của sao, không phải ảnh cung. Sao nào đã vẽ sẽ hiện thumbnail; bấm để mở bản gốc.</span>
        </div>
        <div>
          <b>3. Luận nghĩa</b>
          <span>Đọc theo cặp “sao + cung đang đóng”, rồi đối chiếu Đại Hạn CDK bên dưới.</span>
        </div>
      </div>

      <div class="cdk-chart-core">
        <section class="cdk-menh-core">
          <span class="cdk-core-label">Mệnh CDK</span>
          <strong>{{ cdkChart.menh_branch }}</strong>
          <small>Điểm tụ bản mệnh trong hệ Chiếu Đởm Kinh</small>
        </section>
        <section class="cdk-menh-stars">
          <header>
            <span>Sao thủ Mệnh</span>
            <b>{{ cdkMenhStars.length }} sao</b>
          </header>
          <article v-for="item in cdkMenhStars" :key="item.star" class="cdk-menh-star">
            <button
              v-if="item.art"
              type="button"
              class="cdk-chart-art"
              :aria-label="`Mở ảnh ${item.star}`"
              @click.stop="openArtCard(item.art)"
            >
              <img :src="item.art.image" :alt="`Ảnh ${item.star}`" loading="lazy" />
            </button>
            <div>
              <h4>{{ item.star }} tại {{ item.branch }}</h4>
              <p>
                <span :class="['cdk-status-chip', item.meaning.isHy ? 'is-hy' : '']">{{ item.meaning.status }}</span>
                <span class="cdk-cat-chip">{{ item.meaning.category }}</span>
              </p>
              <small>{{ item.meaning.summary }}</small>
            </div>
          </article>
        </section>
      </div>

      <h4 class="cdk-map-title">Bản đồ 12 địa chi — sao nào kích hoạt vùng nào</h4>
      <div class="cdk-branch-map">
        <article
          v-for="cell in cdkBranchMap"
          :key="cell.branch"
          class="cdk-branch-cell"
          :class="{ 'is-menh': cell.isMenh }"
        >
          <header>
            <strong>{{ cell.branch }}</strong>
            <span v-if="cell.isMenh">Mệnh</span>
          </header>
          <div v-if="cell.stars.length" class="cdk-branch-stars">
            <button
              v-for="item in cell.stars"
              :key="item.star"
              type="button"
              class="cdk-branch-star"
              :class="{ 'has-art': item.art, 'is-hy': item.meaning.isHy }"
              @click.stop="item.art ? openArtCard(item.art) : null"
            >
              <img v-if="item.art" :src="item.art.image" :alt="`Ảnh ${item.star}`" loading="lazy" />
              <span>{{ item.star }}</span>
              <small>{{ item.meaning.isHy ? 'hỷ' : item.meaning.category }}</small>
            </button>
          </div>
          <p v-else>Chưa có Phi Tinh đóng</p>
        </article>
      </div>

      <details class="cdk-raw-stars">
        <summary>Bảng sao → cung gốc</summary>
        <div class="cdk-stars-grid">
          <div v-for="(branch, star) in cdkChart.stars" :key="star" class="cdk-star-pos">
            <button
              v-if="chartArtFor(star)"
              type="button"
              class="cdk-chart-art"
              :aria-label="`Mở ảnh ${star}`"
              @click.stop="openArtCard(chartArtFor(star))"
            >
              <img :src="chartArtFor(star).image" :alt="`Ảnh ${star}`" loading="lazy" />
            </button>
            <span class="cdk-star-name">{{ star }}</span>
            <span class="cdk-star-branch">{{ branch }}</span>
          </div>
        </div>
      </details>
      <p v-if="phiTinhCards.length" class="cdk-chart-art-note">
        Lá số này hiện có ảnh minh họa cho
        <b>{{ Object.keys(cdkChart.stars || {}).filter((star) => chartArtFor(star)).length }}</b>
        sao trong bảng. Các sao còn lại sẽ tự hiện khi thợ vẽ đưa PNG đúng tên vào luồng sync.
      </p>
      <details class="cdk-dai-han">
        <summary>Đại Hạn CDK ({{ cdkChart.dai_han_cycles?.length }} cycles)</summary>
        <ul>
          <li v-for="c in cdkChart.dai_han_cycles" :key="c.cycle_index">
            Cycle {{ c.cycle_index }}: <b>{{ c.branch }}</b> (tuổi {{ c.start_age }}-{{ c.end_age }})
          </li>
        </ul>
      </details>
      <p class="cdk-paradigm-note">⚠ {{ cdkChart.paradigm_note }}</p>
    </section>

    <!-- 18 Phi Tinh schema -->
    <section v-if="phiTinh18" class="cdk-section">
      <h3>🌌 18 Phi Tinh — schema</h3>
      <p class="cdk-warning">{{ phiTinh18.warning_convention }}</p>
      <p v-if="phiTinhCards.length" class="cdk-art-status">
        Bộ ảnh Chiếu Đởm Kinh: <b>{{ phiTinhCards.filter((card) => card.image).length }}/18</b> thẻ đã web-ready.
        Ảnh nhỏ dùng WebP nhẹ; bấm ảnh để mở bản gốc.
      </p>
      <div class="cdk-tier-grid">
        <div class="cdk-tier cdk-tier-duong">
          <h4>9 Dương tinh</h4>
          <article v-for="s in phiTinh18.phi_tinh_9_duong" :key="s.id"
            class="cdk-phi-card" :class="{active: activeStarId === s.id}"
            @click="toggleStar(s.id)">
            <button
              v-if="phiTinhArtFor(s)"
              type="button"
              class="cdk-phi-art"
              :aria-label="`Mở ảnh ${s.name_vi}`"
              @click.stop="openArtCard(phiTinhArtFor(s))"
            >
              <img :src="phiTinhArtFor(s).image" :alt="`Ảnh ${s.name_vi}`" loading="lazy" />
            </button>
            <div class="cdk-phi-copy">
              <header>
                <strong>{{ s.name_vi }}</strong>
                <small>({{ s.name_zh }})</small>
              </header>
              <small>{{ s.ngu_hanh }} · {{ s.polarity }}</small>
            </div>
            <div v-if="activeStarId === s.id" class="cdk-phi-detail">
              <p v-if="s.an_position_mieu"><b>Miếu vị:</b> {{ s.an_position_mieu.join(' · ') }}</p>
              <p v-if="s.an_position"><b>An tại:</b> {{ s.an_position }}</p>
              <p v-if="s.an_position_chinh"><b>Chính vị:</b> {{ s.an_position_chinh }}</p>
              <small>Nguồn: {{ s.source_ref }}</small>
            </div>
          </article>
        </div>
        <div class="cdk-tier cdk-tier-am">
          <h4>9 Âm tinh</h4>
          <article v-for="s in phiTinh18.phi_tinh_9_am" :key="s.id"
            class="cdk-phi-card cdk-phi-am" :class="{active: activeStarId === s.id}"
            @click="toggleStar(s.id)">
            <button
              v-if="phiTinhArtFor(s)"
              type="button"
              class="cdk-phi-art"
              :aria-label="`Mở ảnh ${s.name_vi}`"
              @click.stop="openArtCard(phiTinhArtFor(s))"
            >
              <img :src="phiTinhArtFor(s).image" :alt="`Ảnh ${s.name_vi}`" loading="lazy" />
            </button>
            <div class="cdk-phi-copy">
              <header>
                <strong>{{ s.name_vi }}</strong>
                <small>({{ s.name_zh }})</small>
              </header>
              <small>{{ s.ngu_hanh }} · {{ s.polarity }}</small>
            </div>
            <div v-if="activeStarId === s.id" class="cdk-phi-detail">
              <p v-if="s.an_position_mieu"><b>Miếu vị:</b> {{ s.an_position_mieu.join(' · ') }}</p>
              <p v-if="s.an_position_chinh"><b>Chính vị:</b> {{ s.an_position_chinh }}</p>
              <small>Nguồn: {{ s.source_ref }}</small>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 6 cách cục mới -->
    <section v-if="cachCuc" class="cdk-section">
      <h3>📐 6 Cách cục mới — Chiếu Đởm Kinh</h3>
      <article v-for="c in cachCuc.cach_cuc" :key="c.id" class="cdk-cach-card"
               :class="`cdk-cach-${c.polarity.replaceAll('_', '-')}`">
        <header>
          <strong>{{ c.name_vi }}</strong>
          <small class="cdk-zh">{{ c.name_zh }}</small>
          <span class="cdk-polarity-badge">{{ c.polarity }}</span>
        </header>
        <p class="cdk-lesson">{{ c.lesson_short }}</p>
        <details>
          <summary>Câu sách + paradigm</summary>
          <em>« {{ c.source_quote_hv }} »</em>
          <p v-if="c.paradigm_note" class="cdk-paradigm">💡 {{ c.paradigm_note }}</p>
          <small>Nguồn: {{ c.source_ref }}</small>
        </details>
      </article>
    </section>

    <!-- Nhập Cốt Tiên Kinh tổng đoán -->
    <section v-if="nhapCot" class="cdk-section">
      <h3>📚 Nhập Cốt Tiên Kinh — Tổng đoán 4-chữ</h3>
      <p class="cdk-intro">{{ nhapCot.subtitle_meaning }}</p>
      <details>
        <summary>Intro (verbatim Q4 p0297 r005-r007)</summary>
        <em>« {{ nhapCot.intro_hv }} »</em>
        <p>{{ nhapCot.intro_meaning }}</p>
      </details>
      <div class="cdk-tong-doan-grid">
        <article v-for="t in nhapCot.per_star_tong_doan" :key="t.star"
                 class="cdk-tong-doan-card" :class="`cdk-tong-${t.category}`">
          <header>
            <strong>{{ t.star }}</strong>
            <span class="cdk-cat-badge">{{ t.category }}</span>
          </header>
          <p class="cdk-tong-verdict">{{ t.verdict_summary }}</p>
          <p v-if="t.hy_cung" class="cdk-hy-cung">
            <b>Hỷ:</b>
            <span v-for="c in t.hy_cung" :key="c" class="cdk-hy-chip">{{ c }}</span>
          </p>
          <details>
            <summary>Verbatim</summary>
            <em>« {{ t.verdict_quote_hv }} »</em>
            <p v-if="t.warning" class="cdk-warning-inline">⚠ {{ t.warning }}</p>
            <small>{{ t.source_ref }}</small>
          </details>
        </article>
      </div>

      <!-- Ending paradigm -->
      <section v-if="nhapCot.ending_paradigm" class="cdk-ending">
        <h4>🔚 Paradigm kết quyển</h4>
        <blockquote>{{ nhapCot.ending_paradigm.source_quote_hv }}</blockquote>
        <p>{{ nhapCot.ending_paradigm.meaning }}</p>
        <p class="cdk-iron-rule">⚠ {{ nhapCot.ending_paradigm.iron_rule_note }}</p>
      </section>
    </section>

    <div v-if="selectedArtCard" class="cdk-art-lightbox" @click="selectedArtCard = null">
      <figure @click.stop>
        <button type="button" class="cdk-lightbox-close" @click="selectedArtCard = null">×</button>
        <img :src="selectedArtCard.full_image || selectedArtCard.image" :alt="selectedArtCard.title" />
        <figcaption>
          <b>{{ selectedArtCard.index }}. {{ selectedArtCard.title }} {{ selectedArtCard.name_zh }}</b>
          <span>{{ selectedArtCard.polarity }} · {{ selectedArtCard.element }} · {{ selectedArtCard.id }}</span>
        </figcaption>
      </figure>
    </div>
  </section>
</template>

<style scoped>
.cdk-panel {
  padding: 20px;
  background: linear-gradient(180deg, rgba(20, 30, 45, 0.95), rgba(15, 23, 42, 0.95));
  color: #e6eef5;
  border-radius: 10px;
  max-width: 1200px;
  margin: 0 auto;
}
.cdk-head h2 { color: #c4b5fd; margin: 0 0 6px; font-size: 22px; }
.cdk-sub { font-size: 13px; color: rgba(230, 238, 245, 0.78); line-height: 1.6; margin: 0 0 16px; }
.cdk-sub b { color: #fcd34d; }
.cdk-loading { text-align: center; padding: 20px; color: #a78bfa; }
.cdk-error { color: #f87171; padding: 12px; }

.cdk-chart {
  margin: 20px 0;
  padding: 16px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.08), rgba(20, 30, 45, 0.4));
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 8px;
}
.cdk-chart h3 { margin: 0 0 10px; color: #c4b5fd; font-size: 16px; }
.cdk-meta { display: flex; gap: 16px; flex-wrap: wrap; margin: 10px 0; font-size: 13px; }
.cdk-meta b { color: rgba(230, 238, 245, 0.55); margin-right: 4px; font-weight: 500; }
.cdk-chart-guide {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 12px 0;
}
.cdk-chart-guide div {
  padding: 10px 12px;
  background: rgba(2, 6, 23, 0.24);
  border: 1px solid rgba(167, 139, 250, 0.18);
  border-radius: 6px;
}
.cdk-chart-guide b {
  display: block;
  color: #f5e6b1;
  font-size: 12px;
  margin-bottom: 4px;
}
.cdk-chart-guide span {
  display: block;
  color: rgba(230, 238, 245, 0.68);
  font-size: 11.5px;
  line-height: 1.45;
}
.cdk-chart-core {
  display: grid;
  grid-template-columns: minmax(180px, 0.85fr) minmax(0, 2fr);
  gap: 12px;
  align-items: stretch;
  margin: 14px 0;
}
.cdk-menh-core {
  display: grid;
  place-items: center;
  align-content: center;
  min-height: 190px;
  padding: 18px;
  text-align: center;
  border: 1px solid rgba(252, 211, 77, 0.46);
  border-radius: 8px;
  background:
    radial-gradient(circle at center, rgba(252, 211, 77, 0.16), rgba(91, 229, 211, 0.04) 58%, rgba(2, 6, 23, 0.2)),
    rgba(2, 6, 23, 0.28);
}
.cdk-core-label {
  color: rgba(230, 238, 245, 0.58);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}
.cdk-menh-core strong {
  margin: 8px 0;
  color: #fcd34d;
  font-size: 56px;
  line-height: 1;
}
.cdk-menh-core small {
  max-width: 190px;
  color: rgba(230, 238, 245, 0.68);
  font-size: 12px;
  line-height: 1.45;
}
.cdk-menh-stars {
  padding: 12px;
  border: 1px solid rgba(167, 139, 250, 0.24);
  border-radius: 8px;
  background: rgba(2, 6, 23, 0.22);
}
.cdk-menh-stars > header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #f5e6b1;
  font-size: 13px;
  font-weight: 700;
}
.cdk-menh-stars > header b {
  color: #5be5d3;
  font-size: 12px;
}
.cdk-menh-star {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  padding: 10px 0;
  border-top: 1px solid rgba(230, 238, 245, 0.08);
}
.cdk-menh-star:first-of-type { border-top: 0; }
.cdk-menh-star h4 {
  margin: 0 0 5px;
  color: #fcd34d;
  font-size: 14px;
}
.cdk-menh-star p {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin: 0 0 6px;
}
.cdk-menh-star small {
  display: block;
  color: rgba(230, 238, 245, 0.74);
  font-size: 12px;
  line-height: 1.45;
}
.cdk-status-chip,
.cdk-cat-chip {
  display: inline-flex;
  align-items: center;
  min-height: 20px;
  padding: 2px 7px;
  border-radius: 4px;
  background: rgba(148, 163, 184, 0.14);
  color: rgba(230, 238, 245, 0.74);
  font-size: 11px;
  font-weight: 600;
}
.cdk-status-chip.is-hy {
  background: rgba(91, 229, 211, 0.14);
  color: #5be5d3;
}
.cdk-cat-chip {
  background: rgba(252, 211, 77, 0.12);
  color: #f5e6b1;
}
.cdk-map-title {
  margin: 16px 0 8px;
  color: #f5e6b1;
  font-size: 13px;
}
.cdk-branch-map {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}
.cdk-branch-cell {
  min-height: 104px;
  padding: 9px;
  border: 1px solid rgba(230, 238, 245, 0.08);
  border-radius: 7px;
  background: rgba(2, 6, 23, 0.22);
}
.cdk-branch-cell.is-menh {
  border-color: rgba(252, 211, 77, 0.54);
  background: rgba(252, 211, 77, 0.07);
}
.cdk-branch-cell header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 7px;
}
.cdk-branch-cell header strong {
  color: #f5e6b1;
  font-size: 14px;
}
.cdk-branch-cell header span {
  padding: 1px 6px;
  border-radius: 3px;
  background: rgba(252, 211, 77, 0.16);
  color: #fcd34d;
  font-size: 10.5px;
  font-weight: 700;
}
.cdk-branch-cell p {
  margin: 0;
  color: rgba(230, 238, 245, 0.42);
  font-size: 11.5px;
}
.cdk-branch-stars {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.cdk-branch-star {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 6px;
  min-height: 28px;
  width: 100%;
  padding: 4px 6px;
  border: 1px solid rgba(230, 238, 245, 0.08);
  border-radius: 4px;
  background: rgba(15, 23, 42, 0.74);
  color: rgba(230, 238, 245, 0.82);
  text-align: left;
}
.cdk-branch-star.has-art { cursor: zoom-in; }
.cdk-branch-star.is-hy { border-color: rgba(91, 229, 211, 0.3); }
.cdk-branch-star img {
  width: 22px;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  border-radius: 2px;
}
.cdk-branch-star span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #f5e6b1;
  font-size: 12px;
  font-weight: 700;
}
.cdk-branch-star small {
  color: #5be5d3;
  font-size: 10.5px;
}
.cdk-raw-stars {
  margin-top: 12px;
}
.cdk-raw-stars summary {
  cursor: pointer;
  color: rgba(230, 238, 245, 0.58);
  font-size: 12px;
}
.cdk-stars-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 6px; margin: 10px 0;
}
.cdk-star-pos {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.25);
  border-left: 2px solid #a78bfa;
  border-radius: 0 4px 4px 0;
  font-size: 12.5px;
}
.cdk-chart-art {
  width: 32px;
  aspect-ratio: 2 / 3;
  padding: 0;
  border: 1px solid rgba(245, 230, 177, 0.28);
  border-radius: 3px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.28);
  cursor: zoom-in;
}
.cdk-chart-art img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cdk-star-name { color: #f5e6b1; }
.cdk-star-branch { color: #5be5d3; font-weight: 600; }
.cdk-chart-art-note {
  margin: 8px 0 10px;
  color: rgba(230, 238, 245, 0.64);
  font-size: 12px;
}
.cdk-chart-art-note b { color: #fcd34d; }
.cdk-dai-han { margin: 10px 0; font-size: 12px; }
.cdk-dai-han summary { cursor: pointer; color: #fcd34d; }
.cdk-dai-han ul { margin: 6px 0 0 16px; padding: 0; }
.cdk-paradigm-note {
  font-size: 11.5px; color: rgba(230, 238, 245, 0.6);
  font-style: italic; margin: 10px 0 0;
  padding: 8px; background: rgba(167, 139, 250, 0.05);
  border-left: 2px solid #a78bfa;
}

.cdk-section { margin: 24px 0; }
.cdk-section h3 { color: #f5e6b1; font-size: 17px; margin: 0 0 10px; }

.cdk-warning {
  background: rgba(214, 90, 74, 0.1);
  border-left: 3px solid #d65a4a;
  padding: 8px 12px;
  font-size: 12px;
  color: #f5b08c;
  margin: 8px 0;
  border-radius: 0 4px 4px 0;
}
.cdk-art-status {
  margin: 10px 0 12px;
  padding: 9px 12px;
  background: rgba(91, 229, 211, 0.08);
  border-left: 3px solid #5be5d3;
  border-radius: 0 4px 4px 0;
  color: rgba(230, 238, 245, 0.76);
  font-size: 12px;
}
.cdk-art-status b { color: #fcd34d; }

.cdk-tier-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 768px) {
  .cdk-chart-guide,
  .cdk-chart-core,
  .cdk-tier-grid {
    grid-template-columns: 1fr;
  }
  .cdk-branch-map {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
.cdk-tier h4 { color: #fcd34d; font-size: 14px; margin: 0 0 8px; }
.cdk-phi-card {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 3px solid #c4b5fd;
  border-radius: 0 4px 4px 0;
  padding: 8px 12px;
  margin: 5px 0;
  cursor: pointer;
  transition: background 0.15s;
}
.cdk-phi-card:hover { background: rgba(255, 255, 255, 0.06); }
.cdk-phi-card.active { background: rgba(232, 201, 90, 0.1); }
.cdk-phi-am { border-left-color: #f9a8d4; }
.cdk-phi-art {
  width: 58px;
  aspect-ratio: 2 / 3;
  padding: 0;
  overflow: hidden;
  border: 1px solid rgba(245, 230, 177, 0.32);
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.32);
  cursor: zoom-in;
}
.cdk-phi-art img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cdk-phi-copy { min-width: 0; }
.cdk-phi-card header { display: flex; align-items: baseline; gap: 6px; }
.cdk-phi-card strong { color: #f5e6b1; font-size: 14px; }
.cdk-phi-card header small { color: rgba(230, 238, 245, 0.55); font-size: 11px; }
.cdk-phi-copy > small { display: block; font-size: 11px; color: rgba(230, 238, 245, 0.6); margin-top: 2px; }
.cdk-phi-detail {
  grid-column: 1 / -1;
  margin-top: 8px; padding: 8px;
  background: rgba(0, 0, 0, 0.2); border-radius: 4px;
  font-size: 12px; color: rgba(230, 238, 245, 0.82);
}
.cdk-phi-detail p { margin: 3px 0; }
.cdk-phi-detail b { color: #fcd34d; font-weight: 500; }

.cdk-cach-card {
  background: rgba(255, 255, 255, 0.03);
  border-left: 4px solid #94a3b8;
  border-radius: 0 6px 6px 0;
  padding: 12px 14px; margin: 8px 0;
}
.cdk-cach-cát { border-left-color: #5ab07a; }
.cdk-cach-hung { border-left-color: #d65a4a; }
.cdk-cach-kỳ-cách { border-left-color: #fbbf24; }
.cdk-cach-trung-tính { border-left-color: #94a3b8; }
.cdk-cach-card header { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.cdk-cach-card strong { color: #f5e6b1; font-size: 14px; }
.cdk-zh { color: rgba(230, 238, 245, 0.5); font-size: 12px; }
.cdk-polarity-badge {
  font-size: 10.5px; padding: 2px 8px; border-radius: 3px;
  background: rgba(255, 255, 255, 0.08); color: #cbd5e1;
}
.cdk-lesson { margin: 6px 0; font-size: 13px; line-height: 1.55; color: rgba(230, 238, 245, 0.88); }
.cdk-cach-card details { margin-top: 8px; font-size: 12px; }
.cdk-cach-card summary { cursor: pointer; color: rgba(230, 238, 245, 0.55); }
.cdk-cach-card em { color: #f5e6b1; display: block; margin: 6px 0; font-style: italic; }
.cdk-paradigm { color: #c4b5fd; font-size: 11.5px; margin: 6px 0; font-style: italic; }

.cdk-intro { font-size: 13px; color: rgba(230, 238, 245, 0.78); margin: 0 0 12px; line-height: 1.55; }
.cdk-tong-doan-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 10px;
}
.cdk-tong-doan-card {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 3px solid #5be5d3;
  border-radius: 0 4px 4px 0;
  font-size: 12.5px;
}
.cdk-tong-cát { border-left-color: #5ab07a; }
.cdk-tong-hung { border-left-color: #d65a4a; }
.cdk-tong-âm { border-left-color: #f9a8d4; }
.cdk-tong-dương { border-left-color: #fcd34d; }
.cdk-tong-doan-card header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.cdk-tong-doan-card strong { color: #f5e6b1; font-size: 13px; }
.cdk-cat-badge {
  font-size: 10px; padding: 1px 6px; border-radius: 3px;
  background: rgba(255, 255, 255, 0.08); color: #cbd5e1;
}
.cdk-tong-verdict { margin: 6px 0; line-height: 1.5; color: rgba(230, 238, 245, 0.85); }
.cdk-hy-cung { font-size: 11px; margin: 6px 0; }
.cdk-hy-cung b { color: rgba(230, 238, 245, 0.55); margin-right: 4px; }
.cdk-hy-chip {
  display: inline-block;
  margin-right: 4px;
  padding: 1px 6px;
  background: rgba(91, 229, 211, 0.12);
  border-radius: 3px;
  color: #5be5d3;
}
.cdk-tong-doan-card details summary { font-size: 11px; color: rgba(230, 238, 245, 0.5); cursor: pointer; }
.cdk-tong-doan-card em { color: #f5e6b1; display: block; margin: 6px 0; font-style: italic; font-size: 12px; }
.cdk-warning-inline { color: #f5b08c; margin: 4px 0; font-size: 11px; }

.cdk-ending {
  margin: 16px 0;
  padding: 16px;
  background: rgba(167, 139, 250, 0.06);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 6px;
}
.cdk-ending h4 { color: #c4b5fd; margin: 0 0 8px; font-size: 14px; }
.cdk-ending blockquote {
  font-style: italic; color: #f5e6b1;
  border-left: 3px solid #fcd34d;
  padding: 6px 12px; margin: 8px 0;
}
.cdk-iron-rule {
  margin: 10px 0 0; padding: 8px 12px;
  background: rgba(232, 201, 90, 0.06);
  border-left: 2px solid #fcd34d;
  font-size: 12px; color: rgba(230, 238, 245, 0.85);
}
.cdk-art-lightbox {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(2, 6, 23, 0.86);
}
.cdk-art-lightbox figure {
  position: relative;
  width: min(92vw, 620px);
  max-height: 92vh;
  margin: 0;
  padding: 12px;
  background: #0f172a;
  border: 1px solid rgba(245, 230, 177, 0.34);
  border-radius: 8px;
  box-shadow: 0 22px 70px rgba(0, 0, 0, 0.5);
}
.cdk-art-lightbox img {
  display: block;
  width: 100%;
  max-height: 78vh;
  object-fit: contain;
  border-radius: 5px;
  background: #020617;
}
.cdk-art-lightbox figcaption {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: 10px;
  color: rgba(230, 238, 245, 0.72);
  font-size: 12px;
}
.cdk-art-lightbox figcaption b { color: #f5e6b1; }
.cdk-lightbox-close {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border: 1px solid rgba(230, 238, 245, 0.3);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.9);
  color: #e6eef5;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}
@media (max-width: 520px) {
  .cdk-art-lightbox { padding: 10px; }
  .cdk-art-lightbox figcaption { display: block; }
  .cdk-art-lightbox figcaption span { display: block; margin-top: 4px; }
}
</style>
