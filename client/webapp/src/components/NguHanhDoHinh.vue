<script setup>
/**
 * ☯ Đồ hình tương tác Âm Dương — Thái cực · Tiên thiên · Hậu thiên · Hà Đồ.
 * Dữ liệu từ /api/tu-vi/do-hinh-co (bồi từ vòng đọc sâu Lê Văn Sửu p21-40).
 * Anh duyệt 2026-06-13: đầu tư đồ hình luôn; trục thời gian làm trục chính.
 *
 * SVG thuần, hover/click hiện diễn giải. Tọa độ 8 cung quanh vòng tròn theo
 * key vị trí ("trên", "trên-phải", ... thuận chiều kim đồng hồ).
 */
import { ref, computed, onMounted } from "vue";

const loading = ref(false);
const error = ref("");
const data = ref(null);
const tab = ref("thai_cuc");
const hovered = ref(null);

const TABS = [
  { id: "thai_cuc", label: "☯ Thái cực" },
  { id: "tien_thien", label: "Tiên thiên" },
  { id: "hau_thien", label: "Hậu thiên" },
  { id: "ha_do", label: "Hà Đồ" },
  { id: "lac_thu", label: "Lạc Thư" },
  { id: "nhiet_am", label: "Nhiệt·Ẩm" },
  { id: "skch", label: "Sinh·Khắc·Chế·Hóa" },
  { id: "dong_ho", label: "🕓 Đồng hồ 12 canh" },
];

// vị trí 8 cung → (x, y) trên vòng bán kính R quanh tâm (cx, cy)
const POS_ANGLE = {
  "trên": -90, "trên-phải": -45, "phải": 0, "dưới-phải": 45,
  "dưới": 90, "dưới-trái": 135, "trái": 180, "trên-trái": -135,
};
function xy(pos, cx, cy, r) {
  const a = (POS_ANGLE[pos] * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
}

const HANH_COLOR = {
  "mộc": "#5ab07a", "hỏa": "#d6593a", "thổ": "#c0a878",
  "kim": "#dcdce6", "thủy": "#6ea0dc",
};

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const resp = await fetch("/api/tu-vi/do-hinh-co");
    const d = await resp.json();
    if (d.status !== "ok") throw new Error("API " + d.status);
    data.value = d;
  } catch (e) {
    error.value = "Không tải được đồ hình: " + (e?.message || e);
  } finally {
    loading.value = false;
  }
}
onMounted(load);

// trigram bars: lines = [hào dưới, giữa, trên]; vẽ từ trên xuống nên đảo
function barRows(lines) {
  return [...lines].reverse(); // index0 = hào thượng (vẽ trên cùng)
}

// Hà Đồ: vị trí ngũ phương → tọa độ (tránh object literal inline trong template)
const HADO_XY = {
  "trên": [120, 52], "dưới": [120, 188], "trái": [52, 120],
  "phải": [188, 120], "giữa": [120, 120],
};
function hadoXY(viTri) {
  return HADO_XY[viTri] || [120, 120];
}

const tienThien = computed(() => data.value?.tien_thien?.cung || []);
const hauThien = computed(() => data.value?.hau_thien?.cung || []);
const haDo = computed(() => data.value?.ha_do?.diem || []);
const lacThu = computed(() => data.value?.lac_thu?.o || []);
// Lạc Thư: ô lưới (row,col) → toạ độ SVG (3×3, ô 56px, tâm 120,120)
function lacXY(row, col) {
  return [64 + col * 56, 64 + row * 56];
}
const nhietAm = computed(() => data.value?.nhiet_am?.diem || []);
// Tọa độ nhiệt(x 0..100) ẩm(y 0..100) → SVG: x phải = nhiệt cao, y trên = ẩm cao
function naXY(nhiet, am) {
  return [40 + (nhiet / 100) * 160, 200 - (am / 100) * 160];
}

// ── Ngũ giác Sinh·Khắc·Chế·Hóa ──────────────────────────────────────────────
const skchData = computed(() => data.value?.sinh_khac_che_hoa || null);
const nguGiac = computed(() => skchData.value?.ngu_giac || []);
// 5 đỉnh ngũ giác: đỉnh 0 trên đỉnh, thuận chiều kim đồng hồ, 72° mỗi bước
function pentXY(hanh) {
  const idx = nguGiac.value.indexOf(hanh);
  if (idx < 0) return [120, 120];
  const ang = ((-90 + idx * 72) * Math.PI) / 180;
  return [120 + 88 * Math.cos(ang), 120 + 88 * Math.sin(ang)];
}
// thu hai đầu đoạn về phía nhau (chừa chỗ cho node + mũi tên)
function edge(h1, h2, pad) {
  const a = pentXY(h1), b = pentXY(h2);
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len, uy = dy / len;
  return { x1: a[0] + ux * pad, y1: a[1] + uy * pad, x2: b[0] - ux * pad, y2: b[1] - uy * pad };
}
const skchHover = ref(null);
const hoverRel = computed(() => {
  const s = skchData.value, h = skchHover.value;
  if (!s || !h) return null;
  const con = (s.sinh.find((p) => p[0] === h) || [])[1];
  const me = (s.sinh.find((p) => p[1] === h) || [])[0];
  const khac = (s.khac.find((p) => p[0] === h) || [])[1];
  const biKhac = (s.khac.find((p) => p[1] === h) || [])[0];
  const ch = s.che_hoa.find((d) => d.khac[1] === h); // hành này bị khắc → có chế/hóa cứu
  return { hanh: h, con, me, khac, biKhac,
    che: ch?.che?.hanh, hoa: ch?.hoa?.hanh, keKhac: ch?.khac?.[0] };
});

// ── Đồng hồ sinh học 12 canh giờ ────────────────────────────────────────────
const dongHo = computed(() => data.value?.dong_ho_12_canh?.kinh || []);
const dhHover = ref(null);
// 12 vị trí quanh đồng hồ: index 0 (Tý) ở đỉnh, thuận chiều kim đồng hồ
function clockXY(i, r) {
  const ang = ((-90 + i * 30) * Math.PI) / 180;
  return [120 + r * Math.cos(ang), 120 + r * Math.sin(ang)];
}
</script>

<template>
  <section class="dh-block">
    <div class="dh-tabs">
      <button v-for="t in TABS" :key="t.id" type="button"
        class="dh-tab" :class="{ active: tab === t.id }" @click="tab = t.id">
        {{ t.label }}
      </button>
    </div>

    <p v-if="loading" class="dh-note">Đang tải đồ hình…</p>
    <p v-else-if="error" class="dh-error">{{ error }}</p>

    <template v-else-if="data">
      <!-- ☯ THÁI CỰC -->
      <div v-show="tab === 'thai_cuc'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Thái cực đồ">
          <defs>
            <clipPath id="tc-clip"><circle cx="120" cy="120" r="100" /></clipPath>
          </defs>
          <g clip-path="url(#tc-clip)">
            <rect x="20" y="20" width="200" height="200" fill="#e9e4d6" />
            <!-- nửa đen (âm) + lưỡi S: hai nửa cá cắn đuôi -->
            <path d="M120,20 A100,100 0 0,1 120,220 A50,50 0 0,1 120,120 A50,50 0 0,0 120,20 Z"
              fill="#1c2230" />
            <circle cx="120" cy="70" r="16" fill="#e9e4d6" /><!-- điểm trắng trong đen -->
            <circle cx="120" cy="170" r="16" fill="#1c2230" /><!-- điểm đen trong trắng -->
          </g>
          <circle cx="120" cy="120" r="100" fill="none" stroke="#e8c95a" stroke-width="2" />
          <text x="120" y="16" text-anchor="middle" class="dh-axis">Dương ▲</text>
          <text x="120" y="236" text-anchor="middle" class="dh-axis">▼ Âm</text>
        </svg>
        <div class="dh-info">
          <p>{{ data.thai_cuc.mo_ta }}</p>
          <p class="dh-tacgia">✦ {{ data.thai_cuc.tac_gia }}</p>
          <ul>
            <li v-for="(t, i) in data.thai_cuc.tinh_chat" :key="i">{{ t }}</li>
          </ul>
        </div>
      </div>

      <!-- TIÊN THIÊN -->
      <div v-show="tab === 'tien_thien'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Tiên thiên bát quái">
          <circle cx="120" cy="120" r="104" fill="none" stroke="rgba(232,201,90,0.3)" stroke-width="1" />
          <g v-for="c in tienThien" :key="c.que.ten">
            <g :transform="`translate(${xy(c.pos,120,120,86)[0]},${xy(c.pos,120,120,86)[1]})`"
               class="dh-que" @mouseenter="hovered = c" @mouseleave="hovered = null">
              <!-- 3 hào -->
              <g v-for="(h, ri) in barRows(c.que.lines)" :key="ri">
                <rect v-if="h === 1" :x="-15" :y="ri * 7 - 9" width="30" height="4" rx="1"
                  :fill="HANH_COLOR[c.que.hanh]" />
                <template v-else>
                  <rect :x="-15" :y="ri * 7 - 9" width="12" height="4" rx="1" :fill="HANH_COLOR[c.que.hanh]" />
                  <rect :x="3" :y="ri * 7 - 9" width="12" height="4" rx="1" :fill="HANH_COLOR[c.que.hanh]" />
                </template>
              </g>
              <text :y="22" text-anchor="middle" class="dh-que-label">{{ c.que.ten }}</text>
            </g>
          </g>
          <text x="120" y="124" text-anchor="middle" class="dh-center">THỂ</text>
        </svg>
        <div class="dh-info">
          <p><b>{{ data.tien_thien.ten }}</b></p>
          <p>{{ data.tien_thien.y_nghia }}</p>
          <p v-if="hovered" class="dh-hover">
            {{ hovered.que.symbol }} <b>{{ hovered.que.ten }}</b> ({{ hovered.que.tuong }} · {{ hovered.que.hanh }})
            — đối tâm với <b>{{ hovered.doi_tam }}</b>, trái dấu âm dương = lực hút bền vững.
          </p>
        </div>
      </div>

      <!-- HẬU THIÊN -->
      <div v-show="tab === 'hau_thien'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Hậu thiên bát quái">
          <circle cx="120" cy="120" r="104" fill="none" stroke="rgba(232,201,90,0.3)" stroke-width="1" />
          <g v-for="c in hauThien" :key="c.que.ten">
            <g :transform="`translate(${xy(c.pos,120,120,86)[0]},${xy(c.pos,120,120,86)[1]})`"
               class="dh-que" @mouseenter="hovered = c" @mouseleave="hovered = null">
              <g v-for="(h, ri) in barRows(c.que.lines)" :key="ri">
                <rect v-if="h === 1" :x="-15" :y="ri * 7 - 9" width="30" height="4" rx="1"
                  :fill="HANH_COLOR[c.que.hanh]" />
                <template v-else>
                  <rect :x="-15" :y="ri * 7 - 9" width="12" height="4" rx="1" :fill="HANH_COLOR[c.que.hanh]" />
                  <rect :x="3" :y="ri * 7 - 9" width="12" height="4" rx="1" :fill="HANH_COLOR[c.que.hanh]" />
                </template>
              </g>
              <text :y="22" text-anchor="middle" class="dh-que-label">{{ c.que.ten }}</text>
              <text :y="32" text-anchor="middle" class="dh-que-sub">{{ c.huong }}</text>
            </g>
          </g>
          <text x="120" y="124" text-anchor="middle" class="dh-center">DỤNG</text>
        </svg>
        <div class="dh-info">
          <p><b>{{ data.hau_thien.ten }}</b></p>
          <p>{{ data.hau_thien.y_nghia }}</p>
          <p v-if="hovered" class="dh-hover">
            {{ hovered.que.symbol }} <b>{{ hovered.que.ten }}</b> — {{ hovered.huong }},
            {{ hovered.mua }} ({{ hovered.tiet }}): {{ hovered.giai }}
          </p>
        </div>
      </div>

      <!-- HÀ ĐỒ -->
      <div v-show="tab === 'ha_do'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Hà Đồ">
          <g v-for="d in haDo" :key="d.phuong">
            <g :transform="`translate(${hadoXY(d.vi_tri)[0]},${hadoXY(d.vi_tri)[1]})`"
               class="dh-hado" @mouseenter="hovered = d" @mouseleave="hovered = null">
              <circle r="26" :fill="HANH_COLOR[d.hanh] + '22'" :stroke="HANH_COLOR[d.hanh]" stroke-width="1.5" />
              <text y="-3" text-anchor="middle" class="dh-hado-num">{{ d.sinh }}<tspan class="dh-hado-sep"> · </tspan>{{ d.thanh }}</text>
              <text y="12" text-anchor="middle" class="dh-hado-hanh">{{ d.hanh }}</text>
            </g>
          </g>
          <line x1="120" y1="78" x2="120" y2="162" stroke="rgba(232,201,90,0.25)" stroke-dasharray="3 3" />
          <line x1="78" y1="120" x2="162" y2="120" stroke="rgba(232,201,90,0.25)" stroke-dasharray="3 3" />
        </svg>
        <div class="dh-info">
          <p><b>{{ data.ha_do.ten }}</b></p>
          <p>{{ data.ha_do.y_nghia }}</p>
          <p v-if="hovered && hovered.phuong" class="dh-hover">
            <b>{{ hovered.phuong }}</b> — số sinh <b>{{ hovered.sinh }}</b> (
            {{ hovered.sinh % 2 ? 'dương/lẻ' : 'âm/chẵn' }}) ↔ số thành <b>{{ hovered.thanh }}</b>,
            cách nhau 5 = hành <b>{{ hovered.hanh }}</b>.
          </p>
        </div>
      </div>

      <!-- LẠC THƯ — ma phương cửu cung -->
      <div v-show="tab === 'lac_thu'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Lạc Thư ma phương">
          <rect x="36" y="36" width="168" height="168" rx="6" fill="none" stroke="rgba(232,201,90,0.3)" />
          <line x1="92" y1="36" x2="92" y2="204" stroke="rgba(232,201,90,0.18)" />
          <line x1="148" y1="36" x2="148" y2="204" stroke="rgba(232,201,90,0.18)" />
          <line x1="36" y1="92" x2="204" y2="92" stroke="rgba(232,201,90,0.18)" />
          <line x1="36" y1="148" x2="204" y2="148" stroke="rgba(232,201,90,0.18)" />
          <g v-for="o in lacThu" :key="o.so"
             :transform="`translate(${lacXY(o.row,o.col)[0]},${lacXY(o.row,o.col)[1]})`"
             class="dh-lac" @mouseenter="hovered = o" @mouseleave="hovered = null">
            <circle r="20" :fill="o.loai === 'duong' ? 'rgba(232,201,90,0.14)' : 'rgba(110,160,220,0.14)'"
              :stroke="o.loai === 'duong' ? '#e8c95a' : '#6ea0dc'" stroke-width="1.5" />
            <text y="-1" text-anchor="middle" class="dh-lac-num">{{ o.so }}</text>
            <text y="12" text-anchor="middle" class="dh-lac-sub">{{ o.loai === 'duong' ? 'lẻ·nhiệt' : 'chẵn·ẩm' }}</text>
          </g>
        </svg>
        <div class="dh-info">
          <p><b>{{ data.lac_thu.ten }}</b></p>
          <p>{{ data.lac_thu.y_nghia }}</p>
          <p class="dh-tong">Σ mỗi hàng · cột · chéo = <b>{{ data.lac_thu.tong }}</b></p>
          <p v-if="hovered && hovered.so" class="dh-hover">
            Số <b>{{ hovered.so }}</b> — {{ hovered.phuong }},
            {{ hovered.loai === 'duong' ? 'số lẻ = dương = nhiệt độ' : 'số chẵn = âm = độ ẩm' }}.
          </p>
        </div>
      </div>

      <!-- NGŨ HÀNH = TỌA ĐỘ NHIỆT × ẨM (lượng hóa Lê Văn Sửu) -->
      <div v-show="tab === 'nhiet_am'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Ngũ hành tọa độ nhiệt ẩm">
          <!-- trục -->
          <line x1="40" y1="200" x2="200" y2="200" stroke="rgba(232,201,90,0.35)" />
          <line x1="40" y1="200" x2="40" y2="40" stroke="rgba(232,201,90,0.35)" />
          <text x="204" y="204" class="dh-axis">nhiệt →</text>
          <text x="36" y="34" text-anchor="end" class="dh-axis">ẩm ↑</text>
          <text x="40" y="214" text-anchor="middle" class="dh-axis">0</text>
          <text x="200" y="214" text-anchor="middle" class="dh-axis">100% (dương)</text>
          <text x="30" y="44" text-anchor="end" class="dh-axis">100% (âm)</text>
          <!-- điểm 5 hành -->
          <g v-for="d in nhietAm" :key="d.hanh"
             :transform="`translate(${naXY(d.nhiet,d.am)[0]},${naXY(d.nhiet,d.am)[1]})`"
             class="dh-na" @mouseenter="hovered = d" @mouseleave="hovered = null">
            <circle r="18" :fill="HANH_COLOR[d.hanh] + '22'" :stroke="HANH_COLOR[d.hanh]" stroke-width="2" />
            <text y="-2" text-anchor="middle" class="dh-na-hanh" :fill="HANH_COLOR[d.hanh]">{{ d.hanh }}</text>
            <text y="10" text-anchor="middle" class="dh-na-khi">{{ d.khi }}</text>
          </g>
        </svg>
        <div class="dh-info">
          <p><b>{{ data.nhiet_am.ten }}</b></p>
          <p>{{ data.nhiet_am.y_nghia }}</p>
          <p v-if="hovered && hovered.khi" class="dh-hover">
            <b>{{ hovered.hanh }}</b> ({{ hovered.phuong }}, khí {{ hovered.khi }}):
            nhiệt <b>{{ hovered.nhiet }}%</b> · ẩm <b>{{ hovered.am }}%</b>.
          </p>
        </div>
      </div>

      <!-- NGŨ GIÁC: SINH · KHẮC · CHẾ · HÓA (Hình 3-14) -->
      <div v-show="tab === 'skch'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Ngũ giác sinh khắc chế hóa">
          <defs>
            <marker id="ar-sinh" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill="#5ab07a" />
            </marker>
            <marker id="ar-khac" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill="#d6593a" />
            </marker>
          </defs>
          <template v-if="skchData">
            <!-- cạnh ngoài = tương sinh -->
            <line v-for="(p, i) in skchData.sinh" :key="'s' + i"
              :x1="edge(p[0], p[1], 22).x1" :y1="edge(p[0], p[1], 22).y1"
              :x2="edge(p[0], p[1], 22).x2" :y2="edge(p[0], p[1], 22).y2"
              stroke="#5ab07a" stroke-width="2" marker-end="url(#ar-sinh)" opacity="0.85" />
            <!-- sao 5 cánh trong = tương khắc -->
            <line v-for="(p, i) in skchData.khac" :key="'k' + i"
              :x1="edge(p[0], p[1], 22).x1" :y1="edge(p[0], p[1], 22).y1"
              :x2="edge(p[0], p[1], 22).x2" :y2="edge(p[0], p[1], 22).y2"
              stroke="#d6593a" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#ar-khac)" opacity="0.7" />
            <!-- 5 đỉnh hành -->
            <g v-for="h in nguGiac" :key="h"
               :transform="`translate(${pentXY(h)[0]},${pentXY(h)[1]})`"
               class="dh-na" @mouseenter="skchHover = h" @mouseleave="skchHover = null">
              <circle r="20" :fill="HANH_COLOR[h] + '26'" :stroke="HANH_COLOR[h]"
                :stroke-width="skchHover === h ? 3 : 2" />
              <text y="4" text-anchor="middle" class="dh-na-hanh" :fill="HANH_COLOR[h]">{{ h }}</text>
            </g>
          </template>
        </svg>
        <div class="dh-info">
          <p><b>{{ data.sinh_khac_che_hoa.ten }}</b></p>
          <p>{{ data.sinh_khac_che_hoa.y_nghia }}</p>
          <p class="dh-legend">
            <span class="lg lg-sinh">━▶ tương sinh (cạnh ngoài)</span>
            <span class="lg lg-khac">┈▶ tương khắc (sao trong)</span>
          </p>
          <p v-if="hoverRel" class="dh-hover">
            <b>{{ hoverRel.hanh }}</b> — mẹ <b>{{ hoverRel.me }}</b> sinh ra nó,
            nó sinh con <b>{{ hoverRel.con }}</b>; nó khắc <b>{{ hoverRel.khac }}</b>,
            bị <b>{{ hoverRel.biKhac }}</b> khắc.
            <template v-if="hoverRel.che">
              <br />Khi bị <b>{{ hoverRel.keKhac }}</b> khắc quá:
              <b>{{ hoverRel.che }}</b> (con nó) chế · <b>{{ hoverRel.hoa }}</b> thông quan hóa.
            </template>
          </p>
          <p v-else class="dh-note">Rê chuột vào từng hành để xem mẹ-con-khắc-chế-hóa.</p>
          <details class="dh-skch-list">
            <summary>5 thế khắc → chế · hóa</summary>
            <ul>
              <li v-for="(d, i) in skchData?.che_hoa || []" :key="i">
                <b>{{ d.khac[0] }}</b> khắc <b>{{ d.khac[1] }}</b> →
                chế: <span class="ch-che">{{ d.che.hanh }}</span> ·
                hóa: <span class="ch-hoa">{{ d.hoa.hanh }}</span>
              </li>
            </ul>
          </details>
        </div>
      </div>

      <!-- ĐỒNG HỒ SINH HỌC 12 CANH GIỜ (Thập nhị kinh nạp địa chi) -->
      <div v-show="tab === 'dong_ho'" class="dh-pane">
        <svg viewBox="0 0 240 240" class="dh-svg" role="img" aria-label="Đồng hồ sinh học 12 canh giờ">
          <circle cx="120" cy="120" r="104" fill="none" stroke="rgba(232,201,90,0.25)" stroke-width="1" />
          <circle cx="120" cy="120" r="62" fill="none" stroke="rgba(232,201,90,0.12)" stroke-width="1" />
          <g v-for="(k, i) in dongHo" :key="k.chi">
            <!-- nan hoa nối tâm -->
            <line :x1="clockXY(i, 62)[0]" :y1="clockXY(i, 62)[1]"
              :x2="clockXY(i, 88)[0]" :y2="clockXY(i, 88)[1]"
              :stroke="HANH_COLOR[k.hanh]" stroke-width="1" opacity="0.3" />
            <g :transform="`translate(${clockXY(i, 88)[0]},${clockXY(i, 88)[1]})`"
               class="dh-na" @mouseenter="dhHover = k" @mouseleave="dhHover = null">
              <circle r="17" :fill="HANH_COLOR[k.hanh] + '26'" :stroke="HANH_COLOR[k.hanh]"
                :stroke-width="dhHover && dhHover.chi === k.chi ? 3 : 1.8" />
              <text y="-2" text-anchor="middle" class="dh-dh-chi">{{ k.chi }}</text>
              <text y="9" text-anchor="middle" class="dh-dh-kinh">{{ k.kinh.split(' ')[0] }}</text>
            </g>
          </g>
          <text x="120" y="116" text-anchor="middle" class="dh-center" style="font-size:10px">12 CANH</text>
          <text x="120" y="130" text-anchor="middle" class="dh-dh-kinh">nhịp thời sinh học</text>
        </svg>
        <div class="dh-info">
          <p><b>{{ data.dong_ho_12_canh.ten }}</b></p>
          <p>{{ data.dong_ho_12_canh.y_nghia }}</p>
          <p v-if="dhHover" class="dh-hover">
            <b>{{ dhHover.chi }}</b> ({{ dhHover.gio }}) — kinh <b>{{ dhHover.kinh }}</b>,
            hành <b :style="{ color: HANH_COLOR[dhHover.hanh] }">{{ dhHover.hanh }}</b> vượng.
          </p>
          <p v-else class="dh-note">Rê chuột vào từng canh giờ để xem kinh/tạng phủ vượng.</p>
          <p class="dh-nguon">— {{ data.dong_ho_12_canh.nguon }}</p>
        </div>
      </div>

      <p class="dh-truc">🕓 Trục chính: {{ data.truc_chinh }}</p>
      <p class="dh-nguon">— {{ data.nguon }}</p>
    </template>
  </section>
</template>

<style scoped>
.dh-block {
  margin: 12px 0;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(232, 201, 90, 0.18);
  border-radius: 8px;
}
.dh-tabs { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.dh-tab {
  padding: 5px 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: var(--text-primary, rgba(230, 238, 245, 0.85));
  font-size: 12.5px;
  cursor: pointer;
}
.dh-tab.active { border-color: var(--accent-gold, #e8c95a); background: rgba(232, 201, 90, 0.12); color: var(--accent-gold, #e8c95a); }
.dh-note, .dh-error { font-size: 12.5px; color: var(--text-secondary, rgba(230,238,245,0.7)); }
.dh-error { color: #f5a08c; }
.dh-pane { display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start; }
.dh-svg {
  width: 240px; height: 240px; flex-shrink: 0;
  background: radial-gradient(circle at 50% 45%, rgba(232,201,90,0.05), transparent 70%);
  border-radius: 8px;
}
.dh-axis { fill: var(--text-secondary, rgba(230,238,245,0.5)); font-size: 9px; }
.dh-que { cursor: pointer; }
.dh-que:hover .dh-que-label { fill: var(--accent-gold, #e8c95a); }
.dh-que-label { fill: var(--text-primary, rgba(230,238,245,0.9)); font-size: 11px; }
.dh-que-sub { fill: var(--text-secondary, rgba(230,238,245,0.55)); font-size: 8.5px; }
.dh-center { fill: rgba(232,201,90,0.5); font-size: 13px; font-weight: 700; letter-spacing: 2px; }
.dh-hado { cursor: pointer; }
.dh-hado-num { fill: var(--text-primary, rgba(230,238,245,0.95)); font-size: 13px; font-weight: 600; }
.dh-hado-sep { fill: var(--text-secondary, rgba(230,238,245,0.5)); }
.dh-hado-hanh { fill: var(--text-secondary, rgba(230,238,245,0.7)); font-size: 9px; }
.dh-lac { cursor: pointer; }
.dh-lac-num { fill: var(--text-primary, rgba(230,238,245,0.95)); font-size: 15px; font-weight: 700; }
.dh-lac-sub { fill: var(--text-secondary, rgba(230,238,245,0.55)); font-size: 7.5px; }
.dh-tong { color: var(--accent-gold, #e8c95a) !important; font-size: 12px !important; }
.dh-na { cursor: pointer; }
.dh-na-hanh { font-size: 12px; font-weight: 700; }
.dh-na-khi { fill: var(--text-secondary, rgba(230,238,245,0.6)); font-size: 8px; }
.dh-info { flex: 1; min-width: 200px; }
.dh-info p { margin: 0 0 6px 0; font-size: 12.5px; line-height: 1.55; color: var(--text-secondary, rgba(230,238,245,0.8)); }
.dh-info b { color: var(--text-primary, rgba(230,238,245,0.92)); }
.dh-tacgia { color: var(--accent-gold, #e8c95a) !important; font-style: italic; }
.dh-info ul { margin: 4px 0 0 0; padding-left: 16px; }
.dh-info li { font-size: 12px; line-height: 1.5; color: var(--text-secondary, rgba(230,238,245,0.75)); }
.dh-hover {
  margin-top: 8px !important; padding: 7px 10px;
  background: rgba(232, 201, 90, 0.07);
  border-left: 2px solid rgba(232, 201, 90, 0.5);
  border-radius: 4px; font-size: 12px !important;
}
.dh-legend { display: flex; flex-wrap: wrap; gap: 10px; margin: 6px 0 !important; }
.lg { font-size: 11px !important; padding: 2px 6px; border-radius: 4px; }
.lg-sinh { color: #5ab07a !important; background: rgba(90,176,122,0.1); }
.lg-khac { color: #d6593a !important; background: rgba(214,89,58,0.1); }
.dh-skch-list { margin-top: 8px; }
.dh-skch-list summary { cursor: pointer; font-size: 12px; color: var(--accent-gold, #e8c95a); }
.dh-skch-list ul { margin: 6px 0 0 0; padding-left: 16px; }
.dh-skch-list li { font-size: 12px; line-height: 1.7; color: var(--text-secondary, rgba(230,238,245,0.8)); }
.ch-che { color: #d6593a; font-weight: 600; }
.ch-hoa { color: #5ab07a; font-weight: 600; }
.dh-dh-chi { fill: var(--text-primary, rgba(230,238,245,0.95)); font-size: 10px; font-weight: 700; }
.dh-dh-kinh { fill: var(--text-secondary, rgba(230,238,245,0.62)); font-size: 7px; }
.dh-truc { margin: 10px 0 2px 0; font-size: 11.5px; color: var(--text-secondary, rgba(230,238,245,0.65)); }
.dh-nguon { margin: 0; font-size: 11px; font-style: italic; color: var(--text-secondary, rgba(230,238,245,0.5)); }
</style>
