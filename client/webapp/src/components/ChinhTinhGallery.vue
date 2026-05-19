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
const loading = ref(false);
const errorMsg = ref("");
const activeId = ref("");

const ELEMENT_COLOR = {
  kim: "#c0a878",
  hỏa: "#d65a4a",
  mộc: "#5ab07a",
  thủy: "#3a6cb0",
  thổ: "#9a7b4a",
};

function primaryElement(ngu_hanh) {
  // Some stars have alternatives like "mộc / thủy" — use first.
  return ngu_hanh.split(/[\s\/]+/)[0];
}

onMounted(async () => {
  loading.value = true;
  try {
    const resp = await getTuViChinhTinhList();
    if (resp.status === "ok") {
      stars.value = resp.stars;
    } else {
      errorMsg.value = "Không tải được danh sách chính tinh.";
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

const activeStar = computed(() => stars.value.find((s) => s.id === activeId.value));
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

    <!-- Detail card pinned at the bottom when a star is active -->
    <transition name="fade">
      <article v-if="activeStar" class="ct-detail">
        <header>
          <h3>{{ activeStar.ten_vi }} ({{ activeStar.ten_zh }})</h3>
          <button class="close-x" @click="activeId = ''">×</button>
        </header>
        <p class="detail-meta">
          <span>Ngũ hành: <b>{{ activeStar.ngu_hanh }}</b></span>
          <span>Âm-Dương: <b>{{ activeStar.am_duong }}</b></span>
          <span>Hóa khí: <b>{{ activeStar.hoa_khi }}</b></span>
        </p>
        <p class="detail-row"><b>Chủ về:</b> {{ activeStar.chu_ve.join(' · ') }}</p>
        <p class="detail-row"><b>Đắc địa:</b>
          <span v-for="(d, i) in activeStar.dac_dia" :key="i" class="dac-chip">{{ d }}</span>
        </p>
        <p v-if="activeStar.lac_dia?.length" class="detail-row">
          <b>Lạc địa:</b>
          <span v-for="(l, i) in activeStar.lac_dia" :key="i" class="lac-chip">{{ l }}</span>
        </p>
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
      </article>
    </transition>
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
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.ct-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 6px;
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
  font-size: 12px;
  color: var(--text-secondary, rgba(230, 238, 245, 0.72));
  margin: 8px 0 0 0;
  line-height: 1.5;
}
.chu-ve b { color: var(--text-muted, rgba(230, 238, 245, 0.55)); font-weight: 500; }

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

@media (max-width: 720px) {
  .detail-pos-neg { grid-template-columns: 1fr; }
}
</style>
