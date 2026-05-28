<script setup>
/**
 * ChinhTinhGallery — preview the 14 Tử Vi chính tinh schema.
 *
 * v1: read-only gallery showing the {keywords, tich_cuc, tieu_cuc} cards.
 * Future: integrate with an-sao algorithm to highlight active stars per chart.
 */

import { computed, onMounted, ref } from "vue";
import { getTuViChinhTinhList } from "../lib/api";

const stars = ref([]);
const oracleCards = ref([]);
const loading = ref(false);
const errorMsg = ref("");
const activeId = ref("");
const selectedOracleCard = ref(null);

const ELEMENT_COLOR = {
  kim: "#c0a878",
  hỏa: "#d65a4a",
  mộc: "#5ab07a",
  thủy: "#3a6cb0",
  thổ: "#9a7b4a",
};

const ORACLE_TITLE_BY_STAR = {
  "Tử Vi": "TỬ VI",
  "Thiên Cơ": "THIÊN CƠ",
  "Thái Dương": "THÁI DƯƠNG",
  "Vũ Khúc": "VŨ KHÚC",
  "Thiên Đồng": "THIÊN ĐỒNG",
  "Liêm Trinh": "LIÊM TRINH",
  "Thiên Phủ": "THIÊN PHỦ",
  "Thái Âm": "THÁI ÂM",
  "Tham Lang": "THAM LANG",
  "Cự Môn": "CỰ MÔN",
  "Thiên Tướng": "THIÊN TƯỚNG",
  "Thiên Lương": "THIÊN LƯƠNG",
  "Thất Sát": "THẤT SÁT",
  "Phá Quân": "PHÁ QUÂN",
};

function normalizeTitle(value) {
  return String(value || "").trim().toUpperCase();
}

function primaryElement(ngu_hanh) {
  // Some stars have alternatives like "mộc / thủy" — use first.
  return ngu_hanh.split(/[\s\/]+/)[0];
}

onMounted(async () => {
  loading.value = true;
  try {
    const [resp, oracleResp] = await Promise.all([
      getTuViChinhTinhList(),
      fetch("/oracle-cards/tu-vi/cards.json").catch(() => null),
    ]);
    if (resp.status === "ok") {
      stars.value = resp.stars;
    } else {
      errorMsg.value = "Không tải được danh sách chính tinh.";
    }
    if (oracleResp?.ok) {
      const manifest = await oracleResp.json();
      oracleCards.value = manifest.cards ?? [];
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
});

function toggle(id) {
  activeId.value = activeId.value === id ? "" : id;
}

function openOracleCard(card) {
  if (card) selectedOracleCard.value = card;
}

const activeStar = computed(() => stars.value.find((s) => s.id === activeId.value));
const oracleCardsByTitle = computed(() => {
  return new Map(oracleCards.value.map((card) => [normalizeTitle(card.title), card]));
});
function oracleCardFor(star) {
  const oracleTitle = ORACLE_TITLE_BY_STAR[star?.ten_vi];
  if (!oracleTitle) return null;
  return oracleCardsByTitle.value.get(normalizeTitle(oracleTitle)) ?? null;
}
const activeOracleCard = computed(() => activeStar.value ? oracleCardFor(activeStar.value) : null);
const latestContextCards = computed(() => {
  return oracleCards.value
    .filter((card) => card.id >= 67 && card.id <= 73)
    .sort((a, b) => a.id - b.id);
});
</script>

<template>
  <section class="panel ct-panel">
    <div class="panel-title">
      <span>Tử Vi — 14 Chính Tinh (schema preview)</span>
      <small>tu_vi_chinh_tinh_v1</small>
    </div>

    <p class="ct-note">
      Đây là <b>schema 14 chính tinh</b> với template diễn giải <b>{keywords, tích cực, tiêu cực}</b>.
      Bấm vào một sao để xem chi tiết. <em>An sao thuật toán (đặt sao vào 12 cung dựa trên giờ sinh)
      sẽ phát triển ở phase tiếp theo.</em>
    </p>

    <p v-if="loading" class="status">Đang tải 14 chính tinh…</p>
    <p v-if="errorMsg" class="status error">{{ errorMsg }}</p>

    <div v-if="stars.length" class="ct-grid">
      <article v-for="s in stars" :key="s.id"
        class="ct-card"
        :class="{ active: activeId === s.id }"
        :style="{ borderLeft: '3px solid ' + ELEMENT_COLOR[primaryElement(s.ngu_hanh)] }"
        @click="toggle(s.id)">
        <button
          v-if="oracleCardFor(s)"
          class="ct-card-art"
          type="button"
          :aria-label="`Ảnh thẻ ${s.ten_vi}`"
          @click.stop="openOracleCard(oracleCardFor(s))"
        >
          <img :src="oracleCardFor(s).image" :alt="`Thẻ ${s.ten_vi}`" loading="lazy" />
        </button>
        <div v-else class="ct-card-art missing" aria-label="Chưa có ảnh đã duyệt">
          <span>Chưa có ảnh duyệt</span>
        </div>
        <header>
          <h4>{{ s.ten_vi }}</h4>
          <small>{{ s.ten_zh }} · {{ s.ngu_hanh }} · {{ s.am_duong }} · hóa khí: {{ s.hoa_khi }}</small>
        </header>
        <div class="kw-line">
          <span v-for="(k, i) in s.keywords" :key="i" class="kw-chip">{{ k }}</span>
        </div>
        <p class="chu-ve" v-if="!activeId || activeId !== s.id">
          <b>Chủ về:</b> {{ s.chu_ve.join(' · ') }}
        </p>
      </article>
    </div>

    <section v-if="latestContextCards.length" class="ct-context-strip">
      <header>
        <div>
          <h3>Đợt mới 67-73 · Tọa Cung đời sống</h3>
          <p>Thẻ ngữ cảnh sẽ tự hiện trong phần luận cung khi lá số có đúng sao, đúng Hóa, đúng cung.</p>
        </div>
        <small>{{ latestContextCards.length }} thẻ đã web-ready</small>
      </header>
      <div class="ct-context-row">
        <button
          v-for="card in latestContextCards"
          :key="card.id"
          type="button"
          class="ct-context-card"
          @click="openOracleCard(card)"
        >
          <img :src="card.image" :alt="card.title" loading="lazy" />
          <span>
            <b>{{ card.id }}. {{ card.title }}</b>
            <small>{{ card.system_name || card.card_type }}</small>
            <em>{{ card.interpretation }}</em>
          </span>
        </button>
      </div>
    </section>

    <!-- Detail card pinned at the bottom when a star is active -->
    <transition name="fade">
      <article v-if="activeStar" class="ct-detail">
        <header>
          <h3>{{ activeStar.ten_vi }} ({{ activeStar.ten_zh }})</h3>
          <button class="close-x" @click="activeId = ''">×</button>
        </header>
        <div v-if="activeOracleCard" class="ct-detail-oracle">
          <button type="button" class="ct-detail-oracle-image" @click="openOracleCard(activeOracleCard)">
            <img :src="activeOracleCard.image" :alt="`Thẻ ${activeStar.ten_vi}`" />
            <span>Mở ảnh lớn</span>
          </button>
          <div>
            <span>Ảnh oracle đã đối chiếu</span>
            <p>{{ activeOracleCard.interpretation }}</p>
            <small v-if="activeOracleCard.quality_note">{{ activeOracleCard.quality_note }}</small>
          </div>
        </div>
        <p class="detail-meta">
          <span>Ngũ hành: <b>{{ activeStar.ngu_hanh }}</b></span>
          <span>Âm-Dương: <b>{{ activeStar.am_duong }}</b></span>
          <span v-if="activeStar.thuoc_dau">Thuộc đẩu: <b>{{ activeStar.thuoc_dau }}</b></span>
        </p>
        <p v-if="activeStar.hoa_khi_full || activeStar.hoa_khi" class="detail-row">
          <b>Hóa khí:</b> {{ activeStar.hoa_khi_full || activeStar.hoa_khi }}
        </p>
        <p v-if="activeStar.chu_tinh_of" class="detail-row q2-field">
          <b>Vai trò:</b> {{ activeStar.chu_tinh_of }}
        </p>
        <p class="detail-row"><b>Chủ về:</b> {{ activeStar.chu_ve.join(' · ') }}</p>

        <!-- ⭐ Q2 enriched fields -->
        <div v-if="activeStar.tuong_mao_q2 || activeStar.tinh_cach_q2" class="detail-q2">
          <div v-if="activeStar.tuong_mao_q2" class="q2-row">
            <b>👤 Tướng mạo (Q2):</b> {{ activeStar.tuong_mao_q2 }}
          </div>
          <div v-if="activeStar.tinh_cach_q2" class="q2-row">
            <b>🎭 Tính cách (Q2):</b> {{ activeStar.tinh_cach_q2 }}
          </div>
        </div>

        <p class="detail-row"><b>Đắc địa:</b>
          <span v-for="(d, i) in activeStar.dac_dia" :key="i" class="dac-chip">{{ d }}</span>
        </p>
        <p v-if="activeStar.lac_dia?.length" class="detail-row">
          <b>Lạc địa:</b>
          <span v-for="(l, i) in activeStar.lac_dia" :key="i" class="lac-chip">{{ l }}</span>
        </p>

        <div v-if="activeStar.uy_che?.length" class="detail-row">
          <b>👑 Uy chế (chế ngự được):</b>
          <span v-for="(u, i) in activeStar.uy_che" :key="i" class="uy-chip">{{ u }}</span>
        </div>
        <div v-if="activeStar.hop_voi_q2?.length" class="detail-row">
          <b>🤝 Hợp:</b>
          <span v-for="(h, i) in activeStar.hop_voi_q2" :key="i" class="hop-chip">{{ h }}</span>
        </div>
        <div v-if="activeStar.ky_voi_q2?.length" class="detail-row">
          <b>⚔️ Kỵ:</b>
          <span v-for="(k, i) in activeStar.ky_voi_q2" :key="i" class="ky-chip">{{ k }}</span>
        </div>

        <details v-if="activeStar.co_dac_biet?.length" class="detail-details">
          <summary>📜 Case đặc biệt</summary>
          <ul>
            <li v-for="(c, i) in activeStar.co_dac_biet" :key="i">{{ c }}</li>
          </ul>
        </details>

        <details v-if="activeStar.bias_nam_sinh?.length" class="detail-details">
          <summary>📅 Bias năm sinh</summary>
          <ul>
            <li v-for="(b, i) in activeStar.bias_nam_sinh" :key="i">{{ b }}</li>
          </ul>
        </details>

        <div class="detail-pos-neg">
          <div class="detail-pos">
            <h6>✦ Tích cực</h6>
            <p>{{ activeStar.tich_cuc }}</p>
          </div>
          <div class="detail-neg">
            <h6>⚠ Tiêu cực</h6>
            <p>{{ activeStar.tieu_cuc }}</p>
          </div>
        </div>

        <p v-if="activeStar.q2_source" class="q2-source">
          📚 Nguồn Q2: {{ activeStar.q2_source }}
        </p>
      </article>
    </transition>

    <Teleport to="body">
      <div
        v-if="selectedOracleCard"
        class="oracle-lightbox"
        role="dialog"
        aria-modal="true"
        :aria-label="`Ảnh lớn ${selectedOracleCard.title}`"
        @click.self="selectedOracleCard = null"
      >
        <button class="oracle-lightbox-close" type="button" @click="selectedOracleCard = null">×</button>
        <figure>
          <img :src="selectedOracleCard.full_image || selectedOracleCard.image" :alt="selectedOracleCard.title" />
          <figcaption>
            <strong>{{ selectedOracleCard.title }}</strong>
            <span>{{ selectedOracleCard.interpretation }}</span>
          </figcaption>
        </figure>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.ct-panel { display: flex; flex-direction: column; gap: 14px; }

.ct-note {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  border-left: 3px solid var(--accent-teal, #5be5d3);
  padding-left: 12px;
  margin: 0;
  line-height: 1.6;
}
.ct-note b { color: var(--accent-gold-soft, #f5e6b1); }
.ct-note em { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-style: italic; }

.status { font-size: 13px; color: var(--text-muted, rgba(230, 238, 245, 0.6)); }
.status.error { color: #d65a4a; }

.ct-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 12px;
}
.ct-card {
  display: grid;
  grid-template-columns: 74px minmax(0, 1fr);
  column-gap: 12px;
  row-gap: 8px;
  align-items: start;
  min-height: 172px;
  background:
    linear-gradient(135deg, rgba(232, 201, 90, 0.07), transparent 44%),
    rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
}
.ct-card:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: translateY(-1px);
}
.ct-card.active {
  background: rgba(232, 201, 90, 0.08);
  border-color: rgba(232, 201, 90, 0.4);
}
.ct-card-art {
  grid-row: 1 / span 3;
  width: 74px;
  aspect-ratio: 2 / 3;
  margin: 0;
  padding: 0;
  border: 1px solid rgba(232, 201, 90, 0.22);
  border-radius: 6px;
  background: #071018;
  overflow: hidden;
  cursor: zoom-in;
}
.ct-card-art img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.ct-card-art.missing {
  display: grid;
  place-items: center;
  border-style: dashed;
  background: rgba(255, 255, 255, 0.025);
}
.ct-card-art.missing span {
  max-width: 54px;
  color: var(--text-muted, rgba(230, 238, 245, 0.48));
  font-size: 10px;
  font-weight: 700;
  line-height: 1.25;
  text-align: center;
}
.ct-card header h4 {
  margin: 0;
  font-size: 15px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.ct-card header small {
  display: block;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  margin-bottom: 6px;
  line-height: 1.35;
}
.kw-line { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.kw-chip {
  background: rgba(91, 229, 211, 0.08);
  border: 1px solid rgba(91, 229, 211, 0.22);
  color: var(--accent-teal, #5be5d3);
  font-size: 10.5px;
  padding: 2px 7px;
  border-radius: 3px;
}
.chu-ve {
  grid-column: 2;
  font-size: 12px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  margin: 8px 0 0 0;
  line-height: 1.5;
}
.chu-ve b { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-weight: 500; }

.ct-context-strip {
  padding: 14px;
  border: 1px solid rgba(232, 201, 90, 0.2);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(232, 201, 90, 0.07), rgba(91, 229, 211, 0.035)),
    rgba(255, 255, 255, 0.025);
}
.ct-context-strip > header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
}
.ct-context-strip h3 {
  margin: 0 0 4px;
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 15px;
}
.ct-context-strip p {
  margin: 0;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  font-size: 12.5px;
  line-height: 1.5;
}
.ct-context-strip > header small {
  color: var(--accent-teal, #5be5d3);
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}
.ct-context-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}
.ct-context-card {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 8px;
  padding: 8px;
  border: 1px solid rgba(232, 201, 90, 0.2);
  border-radius: 7px;
  background: rgba(0, 0, 0, 0.16);
  color: inherit;
  text-align: left;
  cursor: zoom-in;
}
.ct-context-card:hover {
  border-color: rgba(232, 201, 90, 0.48);
  background: rgba(232, 201, 90, 0.07);
}
.ct-context-card img {
  width: 100%;
  aspect-ratio: 2 / 3;
  display: block;
  object-fit: cover;
  border-radius: 5px;
  background: #071018;
}
.ct-context-card span,
.ct-context-card b,
.ct-context-card small,
.ct-context-card em {
  display: block;
  min-width: 0;
}
.ct-context-card b {
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 12px;
  line-height: 1.25;
}
.ct-context-card small {
  margin-top: 3px;
  color: rgba(230, 238, 245, 0.48);
  font-size: 10px;
  line-height: 1.3;
}
.ct-context-card em {
  margin-top: 5px;
  color: rgba(230, 238, 245, 0.74);
  font-size: 11px;
  font-style: normal;
  line-height: 1.4;
}

/* Detail pane */
.ct-detail {
  background: linear-gradient(180deg, rgba(20, 30, 45, 0.5) 0%, rgba(12, 18, 28, 0.5) 100%);
  border: 1px solid rgba(232, 201, 90, 0.32);
  border-radius: 8px;
  padding: 16px 18px;
  position: sticky;
  bottom: 0;
  margin-top: 10px;
}
.ct-detail header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px dashed rgba(232, 201, 90, 0.2);
  padding-bottom: 8px;
  margin-bottom: 10px;
}
.ct-detail header h3 {
  margin: 0;
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 18px;
}
.ct-detail-oracle {
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
  margin: 12px 0;
  padding: 12px;
  border: 1px solid rgba(232, 201, 90, 0.2);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(232, 201, 90, 0.08), transparent 52%),
    rgba(0, 0, 0, 0.14);
}
.ct-detail-oracle-image {
  position: relative;
  display: block;
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: zoom-in;
}
.ct-detail-oracle-image img {
  display: block;
  width: 100%;
  max-height: 240px;
  object-fit: contain;
  border-radius: 6px;
  background: #071018;
}
.ct-detail-oracle-image > span {
  position: absolute;
  right: 8px;
  bottom: 8px;
  padding: 4px 7px;
  border: 1px solid rgba(232, 201, 90, 0.4);
  border-radius: 6px;
  background: rgba(5, 12, 18, 0.78);
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 10px;
  font-weight: 760;
}
.ct-detail-oracle > div > span {
  display: block;
  color: var(--accent-teal, #5be5d3);
  font-size: 11px;
  font-weight: 760;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.ct-detail-oracle p {
  margin: 8px 0 0;
  color: rgba(248, 250, 252, 0.88);
  font-size: 13.5px;
  line-height: 1.65;
}
.ct-detail-oracle small {
  display: block;
  margin-top: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.54));
  font-size: 11.5px;
  line-height: 1.55;
}
.close-x {
  background: transparent;
  border: none;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-size: 22px;
  cursor: pointer;
  padding: 0 6px;
}
.close-x:hover { color: var(--accent-gold, #e8c95a); }

.detail-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  margin: 4px 0;
}
.detail-meta b { color: var(--accent-gold-soft, #f5e6b1); }

.detail-row {
  font-size: 13px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  margin: 6px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  align-items: center;
}
.detail-row b { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-weight: 500; }
.dac-chip {
  background: rgba(90, 176, 122, 0.1);
  border: 1px solid rgba(90, 176, 122, 0.3);
  color: #88d39e;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
}
.lac-chip {
  background: rgba(214, 90, 74, 0.1);
  border: 1px solid rgba(214, 90, 74, 0.3);
  color: #f5b08c;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
}

.detail-pos-neg {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 10px;
}
.detail-pos, .detail-neg {
  padding: 10px 12px;
  border-radius: 5px;
}
.detail-pos {
  background: rgba(90, 176, 122, 0.06);
  border-left: 3px solid #5ab07a;
}
.detail-neg {
  background: rgba(214, 90, 74, 0.06);
  border-left: 3px solid #d65a4a;
}
.detail-pos h6, .detail-neg h6 {
  margin: 0 0 4px 0;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.detail-pos h6 { color: #88d39e; }
.detail-neg h6 { color: #f5b08c; }
.detail-pos p, .detail-neg p {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text-secondary, rgba(230, 238, 245, 0.82));
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(8px); }

/* Q2 enriched fields */
.q2-field { color: var(--accent-teal, #5be5d3); }
.detail-q2 {
  margin: 8px 0;
  padding: 10px 12px;
  background: rgba(91, 229, 211, 0.05);
  border-left: 2px solid #5be5d3;
  border-radius: 0 4px 4px 0;
}
.q2-row {
  font-size: 12.5px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.85));
  line-height: 1.55;
  margin: 4px 0;
}
.q2-row b {
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 500;
}
.uy-chip {
  background: rgba(232, 201, 90, 0.15);
  border: 1px solid rgba(232, 201, 90, 0.3);
  color: #f5e6b1;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
}
.hop-chip {
  background: rgba(90, 176, 122, 0.12);
  border: 1px solid rgba(90, 176, 122, 0.3);
  color: #88d39e;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
}
.ky-chip {
  background: rgba(214, 90, 74, 0.12);
  border: 1px solid rgba(214, 90, 74, 0.3);
  color: #f5b08c;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
}
.detail-details {
  margin: 8px 0;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  font-size: 12px;
}
.detail-details summary {
  cursor: pointer;
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 12px;
  font-weight: 500;
}
.detail-details ul {
  margin: 6px 0 0 16px;
  padding: 0;
}
.detail-details li {
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  line-height: 1.6;
  margin: 3px 0;
}
.q2-source {
  margin-top: 10px;
  font-size: 10.5px;
  color: rgba(230, 238, 245, 0.5);
  font-style: italic;
  text-align: right;
}

.oracle-lightbox {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: grid;
  place-items: center;
  padding: 28px;
  background: rgba(0, 0, 0, 0.86);
  backdrop-filter: blur(6px);
}
.oracle-lightbox-close {
  position: fixed;
  top: 18px;
  right: 18px;
  width: 38px;
  height: 38px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.88);
  color: #e5e7eb;
  font-size: 24px;
  cursor: pointer;
}
.oracle-lightbox figure {
  display: grid;
  grid-template-columns: minmax(260px, 520px) minmax(260px, 420px);
  gap: 18px;
  align-items: center;
  max-width: min(1080px, 100%);
  max-height: 92vh;
  margin: 0;
}
.oracle-lightbox img {
  display: block;
  width: 100%;
  max-height: 92vh;
  object-fit: contain;
  border-radius: 10px;
  background: #050b12;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.72);
}
.oracle-lightbox figcaption {
  display: grid;
  gap: 10px;
  padding: 18px;
  border: 1px solid rgba(232, 201, 90, 0.25);
  border-radius: 8px;
  background: rgba(10, 18, 28, 0.86);
}
.oracle-lightbox figcaption strong {
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 24px;
}
.oracle-lightbox figcaption span {
  color: rgba(230, 238, 245, 0.82);
  font-size: 14px;
  line-height: 1.65;
}

@media (max-width: 720px) {
  .ct-grid { grid-template-columns: 1fr; }
  .ct-context-strip > header {
    display: block;
  }
  .ct-context-strip > header small {
    display: block;
    margin-top: 6px;
  }
  .ct-context-row {
    display: flex;
    overflow-x: auto;
    gap: 10px;
    padding-bottom: 3px;
  }
  .ct-context-card {
    flex: 0 0 152px;
  }
  .ct-card {
    grid-template-columns: 68px minmax(0, 1fr);
    min-height: 154px;
  }
  .ct-card-art { width: 68px; }
  .ct-detail-oracle {
    grid-template-columns: 112px minmax(0, 1fr);
  }
  .detail-pos-neg { grid-template-columns: 1fr; }
}

@media (max-width: 460px) {
  .ct-detail-oracle {
    grid-template-columns: 1fr;
  }
  .ct-detail-oracle img {
    width: min(180px, 100%);
    margin: 0 auto;
  }
  .oracle-lightbox {
    padding: 52px 14px 18px;
  }
  .oracle-lightbox figure {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }
  .oracle-lightbox img {
    max-height: 72vh;
  }
}
</style>
