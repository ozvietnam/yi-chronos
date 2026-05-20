<script setup>
/**
 * Chiếu Đởm Kinh panel — kinh phái khác Tử Vi Đẩu Số chính thống.
 * 18 Phi Tinh + 12 cung × 18 sao matrix + cách cục mới + Nhập Cốt Tiên Kinh tổng đoán.
 * Source: Q4 p0269-p0300 (Phase A thâm nhuần 2026-05-20)
 */
import { ref, onMounted } from "vue";
import { activePerson } from "../stores/userDataStore.js";

const cdkChart = ref(null);
const phiTinh18 = ref(null);
const cachCuc = ref(null);
const nhapCot = ref(null);
const loading = ref(false);
const error = ref("");
const activeStarId = ref(null);

async function loadAll() {
  loading.value = true;
  error.value = "";
  const pk = activePerson.value?.person_key;
  try {
    const [chart, phi, cach, ncot] = await Promise.all([
      pk ? fetch("/api/tu-vi/q4/chieu-dom-kinh/cast", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({person_key: pk})
      }).then(r => r.json()) : Promise.resolve(null),
      fetch("/api/tu-vi/q4/chieu-dom-kinh-phi-tinh").then(r => r.json()),
      fetch("/api/tu-vi/q4/chieu-dom-kinh-cach-cuc").then(r => r.json()),
      fetch("/api/tu-vi/q4/nhap-cot-tien-kinh").then(r => r.json()),
    ]);
    if (chart && chart.status === "ok") cdkChart.value = chart;
    if (phi.status === "ok") phiTinh18.value = phi;
    if (cach.status === "ok") cachCuc.value = cach;
    if (ncot.status === "ok") nhapCot.value = ncot;
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
      <div class="cdk-stars-grid">
        <div v-for="(branch, star) in cdkChart.stars" :key="star" class="cdk-star-pos">
          <span class="cdk-star-name">{{ star }}</span>
          <span class="cdk-star-branch">{{ branch }}</span>
        </div>
      </div>
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
      <div class="cdk-tier-grid">
        <div class="cdk-tier cdk-tier-duong">
          <h4>9 Dương tinh</h4>
          <article v-for="s in phiTinh18.phi_tinh_9_duong" :key="s.id"
            class="cdk-phi-card" :class="{active: activeStarId === s.id}"
            @click="toggleStar(s.id)">
            <header>
              <strong>{{ s.name_vi }}</strong>
              <small>({{ s.name_zh }})</small>
            </header>
            <small>{{ s.ngu_hanh }} · {{ s.polarity }}</small>
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
            <header>
              <strong>{{ s.name_vi }}</strong>
              <small>({{ s.name_zh }})</small>
            </header>
            <small>{{ s.ngu_hanh }} · {{ s.polarity }}</small>
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
.cdk-stars-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 6px; margin: 10px 0;
}
.cdk-star-pos {
  display: flex; justify-content: space-between;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.25);
  border-left: 2px solid #a78bfa;
  border-radius: 0 4px 4px 0;
  font-size: 12.5px;
}
.cdk-star-name { color: #f5e6b1; }
.cdk-star-branch { color: #5be5d3; font-weight: 600; }
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

.cdk-tier-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 768px) { .cdk-tier-grid { grid-template-columns: 1fr; } }
.cdk-tier h4 { color: #fcd34d; font-size: 14px; margin: 0 0 8px; }
.cdk-phi-card {
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
.cdk-phi-card header { display: flex; align-items: baseline; gap: 6px; }
.cdk-phi-card strong { color: #f5e6b1; font-size: 14px; }
.cdk-phi-card header small { color: rgba(230, 238, 245, 0.55); font-size: 11px; }
.cdk-phi-card > small { display: block; font-size: 11px; color: rgba(230, 238, 245, 0.6); margin-top: 2px; }
.cdk-phi-detail {
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
</style>
