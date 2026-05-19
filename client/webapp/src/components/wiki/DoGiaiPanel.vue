<script setup>
/**
 * DoGiaiPanel — UI cross-reference sách số 2 của Thầy.
 *
 * Hiển thị:
 *  - Bát Quái ↔ Bát Tiên (cây cầu văn hoá)
 *  - Tiểu sử Thầy qua bản TQ
 *  - 5 thư pháp gia + câu Liễu Công Quyền
 *  - 2 sách Thầy có trong thư viện
 *  - Đính chính Lục Thần
 */
import { ref, onMounted } from "vue";
import TrigramSvg from "./diagrams/TrigramSvg.vue";
import HaDoSvg from "./diagrams/HaDoSvg.vue";
import LacThuSvg from "./diagrams/LacThuSvg.vue";
import BatQuaiVongSvg from "./diagrams/BatQuaiVongSvg.vue";

const ALL_QUE = ["Càn", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn"];

const BAT_TIEN = [
  { que: "Càn", hexa: "☰", tien_vi: "Lữ Đồng Tân", tien_zh: "吕洞宾",
    reason: "Đạo hiệu Thuần Dương Tử — 3 dương",
    color: "#fbbf24" },
  { que: "Khôn", hexa: "☷", tien_vi: "Hà Tiên Cô", tien_zh: "何仙姑",
    reason: "Nữ duy nhất Bát Tiên — đúng Khôn âm",
    color: "#a78bfa" },
  { que: "Chấn", hexa: "☳", tien_vi: "Tào Quốc Cữu", tien_zh: "曹国舅",
    reason: "Hai vân bản gõ ra tiếng = tiếng sấm",
    color: "#34d399" },
  { que: "Tốn", hexa: "☴", tien_vi: "Hàn Tương Tử", tien_zh: "韩湘子",
    reason: "Tiếng sáo như gió xuân nở trăm hoa",
    color: "#86efac" },
  { que: "Khảm", hexa: "☵", tien_vi: "Thiết Quải Lý", tien_zh: "铁拐李",
    reason: "Tên Huyền (玄, đen) = Khảm sắc đen",
    color: "#60a5fa" },
  { que: "Ly", hexa: "☲", tien_vi: "Hán Chung Ly", tien_zh: "汉钟离",
    reason: "'Trung Ly' = 'Ly trung hư' (rỗng giữa)",
    color: "#f87171" },
  { que: "Cấn", hexa: "☶", tien_vi: "Lam Thái Hoà", tien_zh: "蓝采和",
    reason: "Một chân đi giày — Cấn = ngăn lại",
    color: "#d6cfa3" },
  { que: "Đoài", hexa: "☱", tien_vi: "Trương Quả Lão", tien_zh: "张果老",
    reason: "Được cúng trên đại trạch (đầm)",
    color: "#67e8f9" },
];

const STATS = ref(null);
async function loadStats() {
  try {
    const r = await fetch("/api/yi-wiki/stats");
    const d = await r.json();
    if (d.status === "ok") STATS.value = d.stats;
  } catch (e) {}
}
loadStats();

// ⭐ Load figures (ảnh minh hoạ AI vẽ)
const FIGURES = ref([]);
const LIGHTBOX = ref(null);
async function loadFigures() {
  try {
    const r = await fetch("/api/yi-wiki/figures?corpus_id=thieu-khang-tiet-tq");
    const d = await r.json();
    if (d.status === "ok") FIGURES.value = d.figures;
  } catch (e) {}
}
loadFigures();

const curatedFigures = () => FIGURES.value.filter(f => f.curated);
const originalFigures = () => FIGURES.value.filter(f => !f.curated);
</script>

<template>
  <div class="dogiai">
    <!-- Header -->
    <header class="dg-header">
      <h2>📖 Đồ Giải Mai Hoa Dịch Số — Sách số 2 của Thầy</h2>
      <p class="subtitle">
        <code>图解梅花易数</code> (Đồ Giải Mai Hoa Dịch Số) — Tống Thiệu Khang Tiết nguyên tác,
        <b>Thang Hành Dịch</b> biên soạn. <b>321 trang</b> đã restored. Cross-reference với bản VN của Ông Văn Tùng.
      </p>
    </header>

    <!-- 📐 SVG Diagrams — vẽ chính xác bằng code (giai đoạn 2) -->
    <section class="svg-diagrams">
      <h3>📐 Đồ Hoạ CHÍNH XÁC — SVG render thủ công</h3>
      <p class="hint">
        AI không vẽ được 3 vạch chuẩn — em vẽ bằng SVG code, chính xác 100%.
        8 quẻ + Hà Đồ + Lạc Thư + 2 vòng Bát Quái (Tiên Thiên + Hậu Thiên).
      </p>

      <!-- 8 Quẻ trigram -->
      <h4>🔱 Bát Quái — 8 quẻ 3 vạch (mnemonic chuẩn)</h4>
      <div class="trigram-row">
        <TrigramSvg v-for="q in ALL_QUE" :key="q" :que="q" :size="100" />
      </div>

      <!-- 2 vòng Bát Quái -->
      <h4>🌀 Tiên Thiên + Hậu Thiên Bát Quái Đồ</h4>
      <div class="vong-grid">
        <div class="vong-item">
          <BatQuaiVongSvg type="tien-thien" :size="380" />
          <p class="vong-desc">
            <b>Phục Hy</b> — nói âm dương tiêu trưởng. <b>Thể</b> của Dịch.
            Càn-Khôn đối nhau (trục Nam-Bắc).
          </p>
        </div>
        <div class="vong-item">
          <BatQuaiVongSvg type="hau-thien" :size="380" />
          <p class="vong-desc">
            <b>Chu Văn Vương</b> — nói ngũ hành sinh hoá. <b>Dụng</b> của Dịch.
            Ly-Khảm đối nhau (Hoả-Thuỷ).
          </p>
        </div>
      </div>

      <!-- Hà Đồ + Lạc Thư -->
      <h4>🐉 Hà Đồ + 🐢 Lạc Thư — gốc của số học vũ trụ</h4>
      <div class="vong-grid">
        <div class="vong-item">
          <HaDoSvg :size="340" />
          <p class="vong-desc">
            <b>Phục Hy nhận Hà Đồ</b> từ Long Mã ở sông Hoàng Hà. Vận hành theo
            <b>tương sinh</b> (Thuỷ→Mộc→Hoả→Thổ→Kim). <b>Thể Tiên Thiên</b>.
          </p>
        </div>
        <div class="vong-item">
          <LacThuSvg :size="340" />
          <p class="vong-desc">
            <b>Đại Vũ nhận Lạc Thư</b> từ Linh Quy ở sông Lạc. Vận hành theo
            <b>tương khắc</b>. <b>Dụng Hậu Thiên</b>. Cơ sở của Cửu Trù.
          </p>
        </div>
      </div>
    </section>

    <!-- 🎨 Gallery — Ảnh minh hoạ AI vẽ + figures gốc -->
    <section class="gallery-block">
      <h3>🎨 Đồ Hoạ Minh Hoạ — AI render + figures gốc từ sách</h3>
      <p class="hint">
        6 ảnh chính do AI (Pollinations FLUX) vẽ + figures gốc trích từ bản TQ.
        Click ảnh để xem to.
      </p>

      <h4 v-if="curatedFigures().length">🪷 Ảnh chính (AI render — Song Dynasty ink wash style)</h4>
      <div class="gallery-grid">
        <div v-for="f in curatedFigures()" :key="f.filename"
             class="fig-card"
             @click="LIGHTBOX = f">
          <img :src="f.url" :alt="f.title" loading="lazy" />
          <div class="fig-meta">
            <div class="fig-title">{{ f.title }}</div>
            <div class="fig-desc">{{ f.desc }}</div>
            <div class="fig-source">📖 {{ f.source }}</div>
          </div>
        </div>
      </div>

      <details v-if="originalFigures().length" class="orig-block">
        <summary>📜 Figures gốc trích từ bản TQ ({{ originalFigures().length }} ảnh)</summary>
        <div class="orig-grid">
          <div v-for="f in originalFigures()" :key="f.filename"
               class="orig-thumb"
               @click="LIGHTBOX = f">
            <img :src="f.url" :alt="f.filename" loading="lazy" />
            <span>{{ f.filename }}</span>
          </div>
        </div>
      </details>
    </section>

    <!-- Lightbox -->
    <div v-if="LIGHTBOX" class="lightbox" @click="LIGHTBOX = null">
      <div class="lb-content" @click.stop>
        <img :src="LIGHTBOX.url" :alt="LIGHTBOX.title" />
        <div class="lb-info">
          <h3>{{ LIGHTBOX.title }}</h3>
          <p>{{ LIGHTBOX.desc }}</p>
          <div class="lb-source">📖 {{ LIGHTBOX.source }}</div>
        </div>
        <button class="lb-close" @click="LIGHTBOX = null">✕ Đóng</button>
      </div>
    </div>

    <!-- ⭐ Bát Quái ↔ Bát Tiên -->
    <section class="bat-tien-block">
      <h3>⭐ Bát Quái ↔ Bát Tiên — Cây cầu văn hoá dân gian</h3>
      <p class="hint">
        Bản TQ trang 10 cho mapping 1-1: mỗi quẻ ứng một vị Tiên trong Bát Tiên.
        PP học thuộc 8 quẻ qua câu chuyện dân gian — bậc nhất.
      </p>
      <div class="tien-grid">
        <div v-for="t in BAT_TIEN" :key="t.que" class="tien-card"
             :style="{ borderLeftColor: t.color }">
          <div class="t-head">
            <span class="t-hexa" :style="{color: t.color}">{{ t.hexa }}</span>
            <span class="t-que">{{ t.que }}</span>
          </div>
          <div class="t-tien">
            <b>{{ t.tien_vi }}</b> <span class="zh">({{ t.tien_zh }})</span>
          </div>
          <div class="t-reason">{{ t.reason }}</div>
        </div>
      </div>
    </section>

    <!-- Tiểu sử Thầy -->
    <section class="bio-block">
      <h3>🪷 Tiểu sử Thầy qua bản TQ (trang 70)</h3>
      <div class="bio-content">
        <p>
          <b>Thiệu Khang Tiết</b> (邵雍, 1011-1077) là
          <span class="hl">tam đệ tử (đệ tử thứ ba)</span> của
          <b>Trần Đoán</b> (陈抟, hiệu <b>Phù Diêu Tử 扶摇子</b>).
        </p>
        <p>
          Từ Trần Đoán, Thầy nhận <b>Tiên Thiên Đồ</b> (象数学先天图) — hợp Dịch học
          với Nho học → một trong những người lập nên <b>Lý Học Tống-Minh</b>.
        </p>
        <p>
          <span class="hl">★ Chu Hy</span> (朱熹, Nam Tống tập đại thành Nho gia)
          về sau cũng học số học từ Thiệu.
        </p>

        <h4>4 tác phẩm chính của Thầy</h4>
        <ol>
          <li><b>Hoàng Cực Kinh Thế</b> 皇极经世 — tổng kết tư tưởng đời (Thầy viết 30 năm)</li>
          <li><b>Ngư Tiều Vấn Đối</b> 渔樵问对 — đối thoại Dịch + Nho</li>
          <li><b>Y Xuyên Kích Nhưỡng Tập</b> 伊川击壤集 — thơ ngộ đạo</li>
          <li><b>Mai Hoa Dịch Số</b> 梅花易数 — phương pháp bốc thực dụng</li>
        </ol>

        <div class="legend-quote">
          🪷 <b>Truyền thuyết tạo Mai Hoa</b>: Thầy ngồi trong vườn hoa, thấy chim trên
          cây mai kêu → cảm ngộ → sáng tạo Mai Hoa Dịch Số.
        </div>
      </div>
    </section>

    <!-- ⭐ Liễu Công Quyền + Thư pháp -->
    <section class="thu-phap-block">
      <h3>✒️ Liễu Công Quyền — "Tâm chính tắc bút chính"</h3>
      <div class="lcq-quote">
        <div class="zh-big">用笔在心，心正则笔正</div>
        <div class="vi-big">
          <b>Dụng bút tại TÂM — tâm chính tắc bút chính.</b>
        </div>
        <div class="lcq-meta">
          — Liễu Công Quyền 柳公权 (778-865), thư pháp Đường, trả lời Đường Mục Tông
        </div>
      </div>
      <div class="link-tinh-than">
        <b>★ LIÊN KẾT:</b>
        <ul>
          <li>Mai Hoa (Thầy): <i>"Nhân ư tâm thượng khởi kinh luân"</i></li>
          <li>Liễu Công Quyền: <i>"Tâm chính tắc bút chính"</i></li>
        </ul>
        → MỘT TINH THẦN. Đông Á cổ điển — <b>Dịch + Thư pháp đều xuất từ TÂM</b>.
      </div>
      <div class="other-tp">
        4 thư pháp gia khác bản TQ giới thiệu (cho Hoà Áp Phú):
        Tô Thức (1037-1101 — cùng thời Thầy!) ·
        Triệu Cát (Tống Huy Tông, 1082-1139) ·
        Triệu Mạnh Phủ (1254-1322) ·
        Đổng Kỳ Xương (1555-1636).
      </div>
    </section>

    <!-- Đính chính + tiếp thu -->
    <section class="dinh-chinh-block">
      <h3>🔧 Đính chính từ bản TQ</h3>
      <ul>
        <li>
          <b>Câu Trần + Đằng Xà đều thuộc THỔ</b> (chủ trung ương) —
          em (Claude) đã encode sai Đằng Xà = Hoả ở Lục Thần. Đã fix trong DB hôm nay.
        </li>
        <li>
          <b>Hai pp nạp giáp cổ</b>: Kinh Phòng (đã có) + Ngu Phiên (虞翻, theo chu kỳ trăng).
        </li>
        <li>
          <b>Thập Ứng — Phương Quái</b>: vị trí người hỏi ĐỨNG khi gieo cũng tạo quẻ phụ.
          Cả Thể và Dụng đều xét với phương vị.
        </li>
      </ul>
    </section>

    <!-- Wiki impact -->
    <section v-if="STATS" class="stats-block">
      <h3>📊 Wiki sau khi đọc bản TQ</h3>
      <div class="stats-grid">
        <div class="stat"><span>{{ STATS.authors }}</span> Authors</div>
        <div class="stat"><span>{{ STATS.works }}</span> Works</div>
        <div class="stat"><span>{{ STATS.concepts }}</span> Concepts</div>
        <div class="stat"><span>{{ STATS.methods }}</span> Methods</div>
        <div class="stat"><span>{{ STATS.passages }}</span> Passages</div>
        <div class="stat"><span>{{ STATS.case_studies }}</span> Case Studies</div>
      </div>
      <p class="hint">
        2 corpus: <code>mai-hoa-dich-so-thieu-khang-tiet</code> (VN, 672 pages) +
        <code>thieu-khang-tiet-tq</code> (TQ, 321 pages).
      </p>
    </section>
  </div>
</template>

<style scoped>
.dogiai {
  padding: 1rem;
  color: #e2e8f0;
  max-width: 100%;
  overflow-y: auto;
}

.dg-header { margin-bottom: 1.5rem; }
.dg-header h2 { margin: 0 0 0.4rem; color: #fbbf24; }
.subtitle {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.6;
}
.subtitle code {
  background: rgba(0,0,0,0.3);
  padding: 0.1rem 0.4rem;
  border-radius: 2px;
  color: #c4b5fd;
  font-size: 0.95em;
}
.subtitle b { color: #cbd5e1; }

section { margin-bottom: 1.8rem; }
section h3 {
  color: #c4b5fd;
  font-size: 1rem;
  margin: 0 0 0.5rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(167,139,250,0.2);
}
section h4 { color: #fbbf24; font-size: 0.9rem; margin: 0.7rem 0 0.3rem; }

.hint {
  color: #94a3b8;
  font-size: 0.83rem;
  margin: 0 0 0.7rem;
  line-height: 1.55;
  font-style: italic;
}

/* 📐 SVG Diagrams */
.svg-diagrams {
  background: linear-gradient(135deg, rgba(124,45,18,0.06), rgba(161,98,7,0.04));
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}
.svg-diagrams h4 {
  color: #fbbf24;
  font-size: 0.92rem;
  margin: 0.85rem 0 0.5rem;
  border-bottom: 1px dashed rgba(251,191,36,0.3);
  padding-bottom: 0.3rem;
}
.trigram-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  background: rgba(254,243,199,0.05);
  padding: 0.7rem;
  border-radius: 6px;
  margin-bottom: 0.6rem;
}
.vong-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 1rem;
  margin-bottom: 0.6rem;
}
.vong-item {
  background: rgba(254,243,199,0.05);
  border-radius: 6px;
  padding: 0.85rem;
  text-align: center;
}
.vong-item svg {
  margin: 0 auto;
}
.vong-desc {
  margin: 0.6rem 0 0;
  font-size: 0.82rem;
  color: #cbd5e1;
  line-height: 1.6;
  text-align: left;
}
.vong-desc b { color: #fef3c7; }

/* 🎨 Gallery */
.gallery-block {
  background: linear-gradient(135deg, rgba(167,139,250,0.06), rgba(251,191,36,0.04));
  border-radius: 8px;
  padding: 1rem;
}
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.85rem;
  margin: 0.6rem 0 1rem;
}
.fig-card {
  background: rgba(15,23,42,0.55);
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(167,139,250,0.18);
}
.fig-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 22px rgba(167,139,250,0.25);
  border-color: rgba(251,191,36,0.5);
}
.fig-card img {
  width: 100%;
  display: block;
  aspect-ratio: 1 / 1;
  object-fit: cover;
}
.fig-meta {
  padding: 0.6rem 0.85rem;
}
.fig-title {
  color: #fbbf24;
  font-weight: 600;
  font-size: 0.92rem;
  margin-bottom: 0.3rem;
}
.fig-desc {
  color: #cbd5e1;
  font-size: 0.78rem;
  line-height: 1.55;
  margin-bottom: 0.35rem;
}
.fig-source {
  color: #94a3b8;
  font-size: 0.72rem;
  font-style: italic;
}

.orig-block { margin-top: 0.6rem; }
.orig-block summary {
  cursor: pointer;
  color: #c4b5fd;
  font-size: 0.85rem;
  padding: 0.4rem 0;
}
.orig-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 0.4rem;
  margin-top: 0.5rem;
}
.orig-thumb {
  background: rgba(15,23,42,0.5);
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  text-align: center;
  transition: transform 0.15s;
}
.orig-thumb:hover { transform: scale(1.05); }
.orig-thumb img {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  display: block;
}
.orig-thumb span {
  display: block;
  font-size: 0.65rem;
  color: #94a3b8;
  padding: 0.25rem 0.3rem;
  word-break: break-word;
}

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.92);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  cursor: pointer;
}
.lb-content {
  max-width: 90%;
  max-height: 90%;
  background: rgba(15,23,42,0.95);
  border-radius: 8px;
  padding: 1rem;
  cursor: default;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  position: relative;
}
.lb-content img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 4px;
}
.lb-info h3 { margin: 0 0 0.3rem; color: #fbbf24; }
.lb-info p { margin: 0 0 0.4rem; color: #cbd5e1; font-size: 0.88rem; line-height: 1.6; }
.lb-source { color: #94a3b8; font-size: 0.78rem; font-style: italic; }
.lb-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(167,139,250,0.2);
  color: #c4b5fd;
  border: 1px solid rgba(167,139,250,0.4);
  padding: 0.35rem 0.7rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.78rem;
}
.lb-close:hover { background: rgba(167,139,250,0.4); }

/* Bát Tiên grid */
.tien-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.6rem;
}
.tien-card {
  background: rgba(15,23,42,0.55);
  border-left: 3px solid #fbbf24;
  border-radius: 5px;
  padding: 0.6rem 0.85rem;
}
.t-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}
.t-hexa { font-size: 1.6rem; line-height: 1; }
.t-que { font-weight: 600; font-size: 0.95rem; color: #fef3c7; }
.t-tien { margin: 0.2rem 0; }
.t-tien b { color: #c4b5fd; }
.t-tien .zh { color: #94a3b8; font-size: 0.78em; margin-left: 0.3rem; }
.t-reason {
  font-size: 0.78rem;
  color: #cbd5e1;
  font-style: italic;
  line-height: 1.5;
}

/* Bio */
.bio-block {
  background: rgba(15,23,42,0.4);
  border-radius: 6px;
  padding: 0.85rem 1rem;
}
.bio-content p { line-height: 1.65; font-size: 0.88rem; color: #cbd5e1; margin: 0.4rem 0; }
.bio-content .hl { color: #fbbf24; font-weight: 600; }
.bio-content b { color: #fef3c7; }
.bio-content ol { margin: 0.3rem 0 0.6rem 1.2rem; }
.bio-content li { font-size: 0.86rem; line-height: 1.7; margin: 0.2rem 0; color: #cbd5e1; }
.legend-quote {
  margin-top: 0.7rem;
  padding: 0.6rem 0.85rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.1), rgba(251,191,36,0.06));
  border-left: 3px solid #a78bfa;
  border-radius: 4px;
  color: #fef3c7;
  font-size: 0.87rem;
  line-height: 1.6;
}

/* Liễu Công Quyền block */
.thu-phap-block {
  background: rgba(15,23,42,0.4);
  border-radius: 6px;
  padding: 0.85rem 1rem;
}
.lcq-quote {
  background: linear-gradient(135deg, rgba(251,191,36,0.12), rgba(167,139,250,0.08));
  border-radius: 6px;
  padding: 1rem;
  text-align: center;
  margin-bottom: 0.7rem;
}
.zh-big {
  font-family: 'STKaiti', 'KaiTi', serif;
  font-size: 1.6rem;
  color: #fbbf24;
  letter-spacing: 0.15em;
  margin-bottom: 0.5rem;
}
.vi-big {
  font-size: 0.95rem;
  color: #fef3c7;
  margin-bottom: 0.4rem;
}
.lcq-meta { color: #94a3b8; font-size: 0.78rem; font-style: italic; }
.link-tinh-than {
  background: rgba(0,0,0,0.25);
  padding: 0.6rem 0.85rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #cbd5e1;
  line-height: 1.65;
}
.link-tinh-than b { color: #c4b5fd; }
.link-tinh-than ul { margin: 0.3rem 0 0.4rem 1.2rem; }
.link-tinh-than li { margin: 0.15rem 0; }
.link-tinh-than i { color: #fef3c7; }
.other-tp {
  margin-top: 0.7rem;
  padding: 0.5rem 0.7rem;
  background: rgba(255,255,255,0.03);
  border-radius: 4px;
  font-size: 0.78rem;
  color: #94a3b8;
  line-height: 1.6;
}

/* Đính chính */
.dinh-chinh-block ul {
  margin: 0;
  padding-left: 1.3rem;
}
.dinh-chinh-block li {
  font-size: 0.85rem;
  line-height: 1.7;
  color: #cbd5e1;
  margin: 0.4rem 0;
}
.dinh-chinh-block b { color: #fbbf24; }

/* Stats */
.stats-block {
  background: rgba(15,23,42,0.4);
  border-radius: 6px;
  padding: 0.85rem 1rem;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
  margin: 0.4rem 0 0.6rem;
}
.stat {
  background: rgba(0,0,0,0.3);
  padding: 0.5rem 0.7rem;
  border-radius: 4px;
  text-align: center;
  font-size: 0.78rem;
  color: #94a3b8;
}
.stat span {
  display: block;
  font-size: 1.3rem;
  color: #fbbf24;
  font-weight: 700;
  margin-bottom: 0.15rem;
}
</style>
