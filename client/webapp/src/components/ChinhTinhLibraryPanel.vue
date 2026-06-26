<script setup>
/**
 * 📖 Hồ sơ 14 Chính Tinh + Vô Chính Diệu — thư viện nghiên cứu sâu.
 *
 * Anh chốt 2026-06-12: "trang mình chưa nghiên cứu sâu 14 chính tinh rõ nét,
 * chưa đưa âm dương ngũ hành vào làm kiến thức nền tảng."
 *
 * 3 tầng mỗi sao: metadata cổ truyền Q2 (hành/âm dương/hóa khí/chủ về)
 * + Ngũ Uẩn 5 lớp (Tử Vi Bôn Ba) + bảng miếu-hãm 12 chi (độ khó bài học).
 * Mở đầu = kiến thức nền Âm Dương Ngũ Hành (định nghĩa + vòng sinh khắc).
 */
import { computed, ref } from "vue";
import NguHanhDoHinh from "./NguHanhDoHinh.vue";

const open = ref(false);
const loading = ref(false);
const error = ref("");
const nenTang = ref(null);
const profiles = ref([]);
const oracleCards = ref([]);
const paradigmNote = ref("");
const disclaimer = ref("");
const selected = ref(null);
const selectedOracleCard = ref(null);
const showCung12 = ref(false);

// Chân dung v3 8 lớp của sao đang chọn (l1..l8). null nếu API chưa trả v3.
const v3 = computed(() => selected.value?.v3 || null);

// Lớp 5 — nhãn giai đoạn đời người (dict {nho, thieu_nien, trung_nien, ve_gia}).
const L5_LABELS = {
  nho: "Khi còn nhỏ",
  thieu_nien: "Thiếu niên",
  trung_nien: "Trung niên",
  ve_gia: "Về già",
};

const PURE_CHINH_TINH_SLUG = Object.freeze({
  "Tử Vi": "tu-vi",
  "Thiên Cơ": "thien-co",
  "Thái Dương": "thai-duong",
  "Vũ Khúc": "vu-khuc",
  "Thiên Đồng": "thien-dong",
  "Liêm Trinh": "liem-trinh",
  "Thiên Phủ": "thien-phu",
  "Thái Âm": "thai-am",
  "Tham Lang": "tham-lang",
  "Cự Môn": "cu-mon",
  "Thiên Tướng": "thien-tuong",
  "Thiên Lương": "thien-luong",
  "Thất Sát": "that-sat",
  "Phá Quân": "pha-quan",
});

const UAN_LABELS = {
  sac: "Sắc — biểu hiện ra ngoài",
  tho: "Thọ — cảm xúc",
  tuong: "Tưởng — cách nhìn cuộc đời",
  hanh: "Hành — phản ứng & thói quen",
  thuc: "Thức — niềm tin sâu nhất",
};
const UAN_KEYS = ["sac", "tho", "tuong", "hanh", "thuc"];

async function toggle() {
  open.value = !open.value;
  if (open.value && !profiles.value.length && !loading.value) {
    loading.value = true;
    error.value = "";
    try {
      const [profileResp, cardResp] = await Promise.all([
        fetch("/api/tu-vi/star-profiles"),
        fetch("/oracle-cards/tu-vi/cards.json"),
      ]);
      const d = await profileResp.json();
      if (d.status !== "ok") throw new Error("API trả " + d.status);
      nenTang.value = d.nen_tang;
      profiles.value = d.profiles || [];
      paradigmNote.value = d.paradigm_note || "";
      disclaimer.value = d.disclaimer || "";
      selected.value = profiles.value[0] || null;
      if (cardResp.ok) {
        const manifest = await cardResp.json();
        oracleCards.value = manifest.cards || [];
      }
    } catch (e) {
      error.value = "Không tải được hồ sơ sao: " + (e?.message || e);
    } finally {
      loading.value = false;
    }
  }
}

function uanOf(profile, key) {
  const u = profile?.ngu_uan?.ngu_uan?.[key];
  if (!u) return null;
  if (typeof u === "string") return { mo_ta: u };
  return u;
}

// Lớp 3 v3 = list 5 bước {buoc, mo_ta}. rec-only = dict 5 uẩn cũ → render qua uanOf.
const l3Steps = computed(() => {
  const l3 = v3.value?.l3_ngu_uan;
  return Array.isArray(l3) ? l3 : null;
});

// Lớp 5 — biến dict {nho,...} thành list có thứ tự + nhãn đẹp.
const l5Entries = computed(() => {
  const l5 = v3.value?.l5_theo_doi_nguoi;
  if (!l5 || typeof l5 !== "object") return [];
  return Object.keys(L5_LABELS)
    .filter((k) => l5[k])
    .map((k) => ({ label: L5_LABELS[k], text: l5[k] }));
});

// Lớp 7 — v3 trả string; rec cũ trả array vi_du_song/quotes.
const l7Examples = computed(() => {
  const e = v3.value?.l7_vi_du_song;
  if (typeof e === "string" && e.trim()) return [e];
  if (Array.isArray(e)) return e;
  return (
    selected.value?.ngu_uan?.vi_du_song ||
    selected.value?.ngu_uan?.vi_du_an_du ||
    []
  );
});

function levelClass(lv) {
  if (lv === "miếu" || lv === "vượng") return "lv-thuan";
  if (lv === "đắc") return "lv-kha";
  if (lv === "hãm" || lv === "lạc") return "lv-kho";
  return "lv-binh";
}

const oracleCardsBySlug = computed(() => {
  return new Map(oracleCards.value.map((card) => [card.slug, card]));
});

function oracleCardForProfile(profile) {
  const slug = PURE_CHINH_TINH_SLUG[profile?.co_ban?.ten_vi];
  return slug ? oracleCardsBySlug.value.get(slug) || null : null;
}

function openOracle(card) {
  if (card) selectedOracleCard.value = card;
}
</script>

<template>
  <section class="ctl-block">
    <button type="button" class="ctl-toggle" @click="toggle">
      <span>📖 Hồ sơ 14 Chính Tinh — kiến thức nền Âm Dương Ngũ Hành</span>
      <small>{{ open ? "thu gọn ▲" : "mở ra ▼" }}</small>
    </button>

    <div v-if="open" class="ctl-body">
      <p v-if="loading" class="ctl-note">Đang tải hồ sơ sao…</p>
      <p v-else-if="error" class="ctl-error">{{ error }}</p>

      <template v-else-if="profiles.length">
        <!-- ── Kiến thức nền ── -->
        <div v-if="nenTang" class="ctl-nen">
          <p class="ctl-nen-line"><b>Âm dương:</b> {{ nenTang.dinh_nghia.am_duong }}</p>
          <p class="ctl-nen-line"><b>Ngũ hành:</b> {{ nenTang.dinh_nghia.ngu_hanh }}</p>
          <div class="ctl-vong">
            <span class="ctl-vong-label">Vòng sinh:</span>
            <template v-for="(pair, i) in nenTang.vong_sinh" :key="'s' + i">
              <span class="nh-badge" :data-hanh="pair[0]">{{ pair[0] }}</span>
              <span class="ctl-arrow">→</span>
            </template>
            <span class="nh-badge" data-hanh="mộc">mộc</span>
          </div>
          <div class="ctl-vong">
            <span class="ctl-vong-label">Vòng khắc:</span>
            <template v-for="(pair, i) in nenTang.vong_khac" :key="'k' + i">
              <span class="nh-badge" :data-hanh="pair[0]">{{ pair[0] }}</span>
              <span class="ctl-arrow">⊣</span>
            </template>
            <span class="nh-badge" data-hanh="mộc">mộc</span>
          </div>
          <p class="ctl-nen-line ctl-nen-sinh-khac">{{ nenTang.dinh_nghia.sinh_khac }}</p>
          <!-- Bản chất "khí hóa" (Tuệ Tĩnh) + cảnh báo "không phải 5 vật chất" -->
          <p v-if="nenTang.dinh_nghia.khi_hoa" class="ctl-nen-line ctl-khihoa">
            🌬️ <b>Bản chất (khí hóa):</b> {{ nenTang.dinh_nghia.khi_hoa }}
          </p>
          <p v-if="nenTang.dinh_nghia.khong_phai_dinh_menh" class="ctl-nen-line ctl-khongdinhmenh">
            ⚖ {{ nenTang.dinh_nghia.khong_phai_dinh_menh }}
          </p>
          <p v-if="nenTang.tu_vi_dung_sinh_khac" class="ctl-nen-line ctl-tuvisinhkhac">
            ✦ {{ nenTang.tu_vi_dung_sinh_khac }}
          </p>
          <details v-if="(nenTang.ung_dung_da_mon || []).length" class="ctl-nguongoc">
            <summary>🧭 10 lĩnh vực ngũ hành phủ khắp Đông phương học</summary>
            <p class="ctl-nen-line">{{ nenTang.ung_dung_da_mon.join(" · ") }}</p>
          </details>
          <!-- Nguồn gốc học thuyết — bồi từ vòng đọc sâu Lê Văn Sửu (2026-06-13) -->
          <details v-if="nenTang.nguon_goc" class="ctl-nguongoc">
            <summary>🌱 Nguồn gốc học thuyết (Lê Văn Sửu)</summary>
            <p class="ctl-nen-line">{{ nenTang.nguon_goc.tom_tat }}</p>
            <p class="ctl-nen-line">{{ nenTang.nguon_goc.bon_quy_luat }}</p>
            <p class="ctl-nen-line">{{ nenTang.nguon_goc.the_dung }}</p>
            <p class="ctl-nen-line">{{ nenTang.nguon_goc.truc_thoi_gian }}</p>
            <p class="ctl-nen-line ctl-nguongoc-cite">— {{ nenTang.nguon_goc.nguon }}</p>
          </details>
          <!-- ☯ Đồ hình tương tác: Thái cực · Tiên thiên · Hậu thiên · Hà Đồ -->
          <NguHanhDoHinh />
        </div>

        <!-- ── Lưới chọn sao ── -->
        <div class="ctl-grid">
          <button
            v-for="p in profiles" :key="p.co_ban.ten_vi"
            type="button"
            class="ctl-chip"
            :class="{ active: selected === p }"
            :data-hanh="(p.co_ban.ngu_hanh || '').split('/')[0].trim()"
            @click="selected = p"
          >
            <img
              v-if="oracleCardForProfile(p)"
              :src="oracleCardForProfile(p).image"
              :alt="`Thẻ ${p.co_ban.ten_vi}`"
              loading="lazy"
            />
            <span>
              {{ p.co_ban.ten_vi }}
              <small v-if="p.co_ban.ngu_hanh">{{ p.co_ban.am_duong }} {{ p.co_ban.ngu_hanh }}</small>
            </span>
          </button>
        </div>

        <!-- ── Hồ sơ sao đang chọn ── -->
        <article v-if="selected" class="ctl-detail">
          <div class="ctl-detail-shell">
            <button
              v-if="oracleCardForProfile(selected)"
              type="button"
              class="ctl-oracle-art"
              @click="openOracle(oracleCardForProfile(selected))"
            >
              <img :src="oracleCardForProfile(selected).image" :alt="`Thẻ ${selected.co_ban.ten_vi}`" loading="lazy" />
              <span>Mở ảnh lớn</span>
            </button>
            <div v-else class="ctl-oracle-art ctl-oracle-art-missing">
              <span>Chưa có ảnh</span>
            </div>
            <header class="ctl-head">
              <h5>
                {{ selected.co_ban.ten_vi }}
                <span v-if="selected.co_ban.ten_zh" class="ctl-zh">{{ selected.co_ban.ten_zh }}</span>
              </h5>
              <div class="ctl-head-badges">
                <span v-if="selected.co_ban.ngu_hanh" class="nh-badge"
                  :data-hanh="(selected.co_ban.ngu_hanh || '').split('/')[0].trim()">
                  {{ selected.co_ban.am_duong }} {{ selected.co_ban.ngu_hanh }}
                </span>
                <span v-if="selected.co_ban.hoa_khi" class="ctl-hoakhi">hóa khí: {{ selected.co_ban.hoa_khi }}</span>
                <span v-if="(selected.co_ban.chu_ve || []).length" class="ctl-chuve">
                  chủ về: {{ selected.co_ban.chu_ve.join(", ") }}
                </span>
              </div>
              <p v-if="(selected.co_ban.keywords || []).length" class="ctl-kw">
                {{ selected.co_ban.keywords.join(" · ") }}
              </p>
              <p v-if="oracleCardForProfile(selected)?.interpretation" class="ctl-art-meaning">
                {{ oracleCardForProfile(selected).interpretation }}
              </p>
            </header>
          </div>

          <!-- ☸ Quán chiếu Ngũ Uẩn — TÁCH LỚP (chân dung v3 8 lớp l1..l8):
               nguồn v3.l* trước, fallback ngu_uan cũ. tóm gọn nổi, chi tiết bung -->
          <div v-if="v3 || selected.ngu_uan" class="ctl-nu">
            <!-- TÓM GỌN: Gốc Tham (mệnh đề định vị) + 1 dòng hướng tu tập -->
            <div class="ctl-nu-summary">
              <p
                v-if="v3?.l2_goc_tham || selected.ngu_uan?.goc_tham || selected.ngu_uan?.menh_de_dinh_vi"
                class="ctl-nu-goctham"
              >
                <span class="ctl-nu-lbl">Gốc tham</span>
                {{ v3?.l2_goc_tham || selected.ngu_uan?.goc_tham || selected.ngu_uan?.menh_de_dinh_vi }}
              </p>
              <p
                v-if="v3?.l6_duong_ra || selected.ngu_uan?.duong_ra || selected.ngu_uan?.can_de_phat_huy"
                class="ctl-nu-duongra"
              >
                <span class="ctl-nu-lbl ctl-nu-lbl-out">Hướng tu tập</span>
                {{ v3?.l6_duong_ra || selected.ngu_uan?.duong_ra || selected.ngu_uan?.can_de_phat_huy }}
              </p>
            </div>

            <!-- LỚP 1 — Căn cơ Âm Dương / Ngũ Hành -->
            <details
              v-if="v3?.l1_am_duong_ngu_hanh || selected.ngu_uan?.am_duong_ngu_hanh"
              class="ctl-nu-layer"
            >
              <summary><b>1.</b> Căn cơ tạo hóa — Âm Dương / Ngũ Hành</summary>
              <p class="ctl-nu-body">{{ v3?.l1_am_duong_ngu_hanh || selected.ngu_uan?.am_duong_ngu_hanh }}</p>
            </details>

            <!-- LỚP 3 — Ngũ Uẩn tiến trình tâm (Sắc→Thọ→Tưởng→Hành→Thức) -->
            <details class="ctl-nu-layer">
              <summary><b>3.</b> Ngũ Uẩn — tiến trình tâm (Sắc→Thọ→Tưởng→Hành→Thức)</summary>
              <div class="ctl-nu-body">
                <!-- v3: list 5 bước {buoc, mo_ta} -->
                <dl v-if="l3Steps" class="ctl-uan">
                  <template v-for="(step, i) in l3Steps" :key="'l3' + i">
                    <dt>{{ step.buoc }}</dt>
                    <dd>{{ step.mo_ta }}</dd>
                  </template>
                </dl>
                <!-- fallback: dict 5 uẩn cũ -->
                <dl v-else class="ctl-uan">
                  <template v-for="key in UAN_KEYS" :key="key">
                    <template v-if="uanOf(selected, key)">
                      <dt>{{ UAN_LABELS[key] }}</dt>
                      <dd>
                        {{ uanOf(selected, key).mo_ta }}
                        <span v-if="uanOf(selected, key).khi_manh" class="ctl-manh">
                          ▲ Khi mạnh: {{ uanOf(selected, key).khi_manh }}</span>
                        <span v-if="uanOf(selected, key).khi_lech" class="ctl-lech">
                          ▽ Khi lệch: {{ uanOf(selected, key).khi_lech }}</span>
                      </dd>
                    </template>
                  </template>
                </dl>
              </div>
            </details>

            <!-- LỚP 4 — Khí vượng ↔ Khí suy. v3.l4 = DICT {dac_dia, ham_dia, active}.
                 Có vị trí (active) → đánh dấu nhánh đang ứng; chưa biết → hiện CẢ HAI nhãn ĐẮC/HÃM. -->
            <details
              v-if="v3?.l4_khi_vuong_suy || selected.ngu_uan?.khi_vuong_suy || selected.sao_o_dau_thi"
              class="ctl-nu-layer"
            >
              <summary><b>4.</b> Khí vượng ↔ Khí suy</summary>
              <div class="ctl-nu-body">
                <template v-if="v3?.l4_khi_vuong_suy">
                  <p
                    v-if="v3.l4_khi_vuong_suy.dac_dia"
                    class="ctl-nu-kvs ctl-manh"
                    :class="{ 'ctl-kvs-active': v3.l4_khi_vuong_suy.active === 'dac_dia' }"
                  >
                    <span class="ctl-kvs-tag ctl-kvs-tag-dac">ĐẮC</span>
                    <span v-if="v3.l4_khi_vuong_suy.active === 'dac_dia'" class="ctl-kvs-now">● đang ứng</span>
                    {{ v3.l4_khi_vuong_suy.dac_dia }}
                  </p>
                  <p
                    v-if="v3.l4_khi_vuong_suy.ham_dia"
                    class="ctl-nu-kvs ctl-lech"
                    :class="{ 'ctl-kvs-active': v3.l4_khi_vuong_suy.active === 'ham_dia' }"
                  >
                    <span class="ctl-kvs-tag ctl-kvs-tag-ham">HÃM</span>
                    <span v-if="v3.l4_khi_vuong_suy.active === 'ham_dia'" class="ctl-kvs-now">● đang ứng</span>
                    {{ v3.l4_khi_vuong_suy.ham_dia }}
                  </p>
                </template>
                <template v-else-if="selected.ngu_uan?.khi_vuong_suy && typeof selected.ngu_uan.khi_vuong_suy === 'object'">
                  <p v-if="selected.ngu_uan.khi_vuong_suy.dac_dia" class="ctl-nu-kvs ctl-manh">
                    <span class="ctl-kvs-tag ctl-kvs-tag-dac">ĐẮC</span>
                    {{ selected.ngu_uan.khi_vuong_suy.dac_dia }}
                  </p>
                  <p v-if="selected.ngu_uan.khi_vuong_suy.ham_dia" class="ctl-nu-kvs ctl-lech">
                    <span class="ctl-kvs-tag ctl-kvs-tag-ham">HÃM</span>
                    {{ selected.ngu_uan.khi_vuong_suy.ham_dia }}
                  </p>
                </template>
                <p v-else-if="selected.ngu_uan?.khi_vuong_suy" class="ctl-nu-kvs">{{ selected.ngu_uan.khi_vuong_suy }}</p>
                <p v-if="selected.sao_o_dau_thi" class="ctl-odau">☞ {{ selected.sao_o_dau_thi }}</p>
              </div>
            </details>

            <!-- LỚP 5 — Theo đời người (v3.l5 = dict {nho, thieu_nien, trung_nien, ve_gia}) -->
            <details
              v-if="l5Entries.length || selected.ngu_uan?.theo_doi_nguoi"
              class="ctl-nu-layer"
            >
              <summary><b>5.</b> Theo đời người</summary>
              <div class="ctl-nu-body">
                <template v-if="l5Entries.length">
                  <p v-for="e in l5Entries" :key="e.label" class="ctl-nu-doinguoi">
                    <span class="ctl-nu-lbl">{{ e.label }}</span> {{ e.text }}
                  </p>
                </template>
                <template v-else-if="typeof selected.ngu_uan?.theo_doi_nguoi === 'object'">
                  <p v-for="(val, giai) in selected.ngu_uan.theo_doi_nguoi" :key="giai" class="ctl-nu-doinguoi">
                    <span class="ctl-nu-lbl">{{ giai }}</span> {{ val }}
                  </p>
                </template>
                <p v-else class="ctl-nu-doinguoi">{{ selected.ngu_uan?.theo_doi_nguoi }}</p>
              </div>
            </details>

            <!-- LỚP 6 — Khe tỉnh thức + Hướng tu tập -->
            <details
              v-if="v3?.l6_khe_tinh_thuc || v3?.l6_duong_ra || selected.ngu_uan?.khe_tinh_thuc || selected.ngu_uan?.duong_ra || selected.ngu_uan?.can_de_phat_huy"
              class="ctl-nu-layer"
            >
              <summary><b>6.</b> Khe tỉnh thức + Hướng tu tập</summary>
              <div class="ctl-nu-body">
                <p v-if="v3?.l6_khe_tinh_thuc || selected.ngu_uan?.khe_tinh_thuc" class="ctl-nu-khe">
                  ⟡ {{ v3?.l6_khe_tinh_thuc || selected.ngu_uan?.khe_tinh_thuc }}
                </p>
                <p v-if="v3?.l6_duong_ra || selected.ngu_uan?.duong_ra" class="ctl-nu-duongra-full">
                  🚪 {{ v3?.l6_duong_ra || selected.ngu_uan?.duong_ra }}
                </p>
                <p v-if="selected.ngu_uan?.can_de_phat_huy" class="ctl-can">
                  ✦ Cần để phát huy: {{ selected.ngu_uan.can_de_phat_huy }}
                </p>
              </div>
            </details>

            <!-- LỚP 7 — Ví dụ sống (v3.l7 = string; rec cũ = array) + quotes gốc -->
            <details
              v-if="l7Examples.length || (selected.ngu_uan?.quotes || []).length"
              class="ctl-nu-layer"
            >
              <summary><b>7.</b> Ví dụ sống &amp; ẩn dụ</summary>
              <div class="ctl-nu-body">
                <ul v-if="l7Examples.length" class="ctl-andu">
                  <li v-for="(a, i) in l7Examples" :key="'l7' + i">🌿 {{ a }}</li>
                </ul>
                <blockquote
                  v-for="(q, i) in (selected.ngu_uan?.quotes || []).slice(0, 3)"
                  :key="'q' + i"
                  class="ctl-quote"
                >“{{ q }}”</blockquote>
              </div>
            </details>

            <!-- LỚP 8 — Căn cứ / nguồn & cơ sở dẫn chứng (v3.l8_can_cu) -->
            <details
              v-if="v3?.l8_can_cu || selected.ngu_uan?.can_cu"
              class="ctl-nu-layer"
            >
              <summary><b>8.</b> Căn cứ — nguồn &amp; cơ sở dẫn chứng</summary>
              <p class="ctl-nu-body ctl-nu-cancu">{{ v3?.l8_can_cu || selected.ngu_uan?.can_cu }}</p>
            </details>
          </div>

          <!-- Tích cực / tiêu cực cổ truyền -->
          <p v-if="selected.co_ban.tich_cuc" class="ctl-pos">✦ {{ selected.co_ban.tich_cuc }}</p>
          <p v-if="selected.co_ban.tieu_cuc" class="ctl-neg">⚠ {{ selected.co_ban.tieu_cuc }}</p>

          <!-- 📜 Luận giải sâu đa phái (build từ atoms 6 nguồn, có trích trang) -->
          <div v-if="selected.luan_giai_sau" class="ctl-deep">
            <h6 class="ctl-deep-title">📜 Luận giải sâu đa phái
              <small>tổng hợp từ {{ selected.luan_giai_sau.built_from_atoms }} atoms · 6 nguồn</small>
            </h6>
            <p v-if="selected.luan_giai_sau.tong_quan?.hinh_tuong" class="ctl-deep-p">
              <b>Hình tượng:</b> {{ selected.luan_giai_sau.tong_quan.hinh_tuong }}</p>
            <p v-if="selected.luan_giai_sau.tong_quan?.ban_chat" class="ctl-deep-p">
              <b>Bản chất:</b> {{ selected.luan_giai_sau.tong_quan.ban_chat }}</p>
            <p v-if="selected.luan_giai_sau.tong_quan?.y_nghia_hanh_hoa_khi" class="ctl-deep-p">
              <b>Hành & hóa khí:</b> {{ selected.luan_giai_sau.tong_quan.y_nghia_hanh_hoa_khi }}</p>

            <div v-if="(selected.luan_giai_sau.goc_nhin_cac_phai || []).length" class="ctl-deep-phai">
              <p v-for="g in selected.luan_giai_sau.goc_nhin_cac_phai" :key="g.phai" class="ctl-deep-phai-item">
                <span class="ctl-deep-phai-name">{{ g.phai }}:</span> {{ g.diem_nhan }}
              </p>
            </div>

            <button type="button" class="ctl-deep-cung-toggle" @click="showCung12 = !showCung12">
              🏛 Tại 12 cung {{ showCung12 ? "▲" : "▼" }}
            </button>
            <dl v-if="showCung12" class="ctl-deep-cung">
              <template v-for="(v, cung) in selected.luan_giai_sau.tai_12_cung" :key="cung">
                <dt>{{ cung }} <small v-if="v.nguon_mong">· nguồn mỏng</small></dt>
                <dd>
                  {{ v.luan }}
                  <span v-if="(v.nguon || []).length" class="ctl-deep-nguon">— {{ v.nguon.join(" · ") }}</span>
                </dd>
              </template>
            </dl>

            <p v-if="selected.luan_giai_sau.than_cu" class="ctl-deep-p">
              <b>Thân cư:</b> {{ selected.luan_giai_sau.than_cu }}</p>
            <p v-if="selected.luan_giai_sau.sat_tinh_cat_tinh" class="ctl-deep-p">
              <b>Gặp sát / cát tinh:</b> {{ selected.luan_giai_sau.sat_tinh_cat_tinh }}</p>

            <div v-if="(selected.luan_giai_sau.cau_phu_kinh_dien || []).length" class="ctl-deep-phu">
              <p class="ctl-deep-phu-label">Câu phú kinh điển:</p>
              <blockquote v-for="(cp, i) in selected.luan_giai_sau.cau_phu_kinh_dien" :key="'cp' + i" class="ctl-quote">
                “{{ cp.phu }}”<span v-if="cp.giai"> — {{ cp.giai }}</span>
                <small v-if="cp.nguon"> ({{ cp.nguon }})</small>
              </blockquote>
            </div>

            <p v-if="selected.luan_giai_sau.khac_biet_cac_phai" class="ctl-deep-khacbiet">
              ⚖ Khác biệt giữa các phái: {{ selected.luan_giai_sau.khac_biet_cac_phai }}</p>
            <p v-if="selected.luan_giai_sau.dao_duc_ghi_chu" class="ctl-paradigm">
              {{ selected.luan_giai_sau.dao_duc_ghi_chu }}</p>
          </div>

          <!-- Miếu hãm 12 chi -->
          <div v-if="Object.keys(selected.mieu_ham_12_chi || {}).length" class="ctl-mh">
            <span class="ctl-mh-label">Độ khó bài học tại 12 đất cung:</span>
            <span v-for="(lv, chi) in selected.mieu_ham_12_chi" :key="chi"
              class="ctl-mh-chip" :class="levelClass(lv)">
              {{ chi }}<b v-if="lv"> {{ lv }}</b><b v-else> —</b>
            </span>
          </div>

        </article>

        <p v-if="paradigmNote" class="ctl-paradigm">{{ paradigmNote }}</p>
        <!-- Iron #9 — lá chắn đạo đức: Tử Vi mượn khung Phật để soi tâm -->
        <p v-if="disclaimer" class="ctl-disclaimer">⚖ {{ disclaimer }}</p>
      </template>
    </div>

    <Teleport to="body">
      <div
        v-if="selectedOracleCard"
        class="ctl-lightbox"
        role="dialog"
        aria-modal="true"
        :aria-label="`Ảnh lớn ${selectedOracleCard.title}`"
        @click.self="selectedOracleCard = null"
      >
        <button class="ctl-lightbox-close" type="button" @click="selectedOracleCard = null">×</button>
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
.ctl-block { margin: 14px 0; }
.ctl-toggle {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  background: rgba(232, 201, 90, 0.07);
  border: 1px solid rgba(232, 201, 90, 0.25);
  border-radius: 6px;
  color: var(--accent-gold, #e8c95a);
  font-size: 13px;
  cursor: pointer;
  text-align: left;
}
.ctl-toggle small { color: var(--text-secondary, rgba(230, 238, 245, 0.6)); }
.ctl-body {
  margin-top: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 6px;
}
.ctl-note, .ctl-error { font-size: 12.5px; color: var(--text-secondary, rgba(230,238,245,0.7)); }
.ctl-error { color: #f5a08c; }

.ctl-nen {
  padding: 8px 10px;
  border-left: 2px solid rgba(232, 201, 90, 0.4);
  margin-bottom: 12px;
}
.ctl-nen-line { margin: 2px 0; font-size: 12.5px; line-height: 1.55; color: var(--text-secondary, rgba(230,238,245,0.8)); }
.ctl-nen-sinh-khac { font-style: italic; opacity: 0.85; }
.ctl-khihoa, .ctl-khongdinhmenh, .ctl-tuvisinhkhac { margin-top: 6px; }
.ctl-khihoa b { color: var(--accent-gold, #e8c95a); }
.ctl-khongdinhmenh { border-left: 2px solid rgba(232,201,90,0.35); padding-left: 8px; }
.ctl-tuvisinhkhac { color: var(--accent-gold, #e8c95a); opacity: 0.92; }
.ctl-nguongoc { margin-top: 8px; }
.ctl-nguongoc summary {
  font-size: 12px; color: var(--accent-gold, #e8c95a);
  cursor: pointer; opacity: 0.9;
}
.ctl-nguongoc p { margin-top: 6px; }
.ctl-nguongoc-cite { font-style: italic; opacity: 0.6; font-size: 11px; }
.ctl-vong { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; margin: 5px 0; }
.ctl-vong-label { font-size: 11.5px; color: var(--text-secondary, rgba(230,238,245,0.6)); margin-right: 4px; }
.ctl-arrow { font-size: 11px; color: var(--text-secondary, rgba(230,238,245,0.55)); }

.ctl-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}
.ctl-chip {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  min-height: 54px;
  padding: 6px 9px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: var(--text-primary, rgba(230, 238, 245, 0.9));
  font-size: 12.5px;
  cursor: pointer;
  text-align: left;
}
.ctl-chip img {
  width: 34px;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  border-radius: 4px;
  background: #071018;
  border: 1px solid rgba(232, 201, 90, 0.18);
}
.ctl-chip span { min-width: 0; }
.ctl-chip small { font-size: 10px; color: var(--text-secondary, rgba(230,238,245,0.55)); }
.ctl-chip.active { border-color: var(--accent-gold, #e8c95a); background: rgba(232, 201, 90, 0.1); }

/* màu 5 hành cho viền chip */
.ctl-chip[data-hanh="mộc"], .nh-badge[data-hanh="mộc"] { border-color: rgba(90,176,122,0.55); }
.ctl-chip[data-hanh="hỏa"], .nh-badge[data-hanh="hỏa"] { border-color: rgba(214,90,74,0.55); }
.ctl-chip[data-hanh="thổ"], .nh-badge[data-hanh="thổ"] { border-color: rgba(192,168,120,0.6); }
.ctl-chip[data-hanh="kim"], .nh-badge[data-hanh="kim"] { border-color: rgba(220,220,230,0.45); }
.ctl-chip[data-hanh="thủy"], .nh-badge[data-hanh="thủy"] { border-color: rgba(110,160,220,0.55); }
.nh-badge {
  font-size: 11.5px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: var(--text-primary, rgba(230, 238, 245, 0.9));
}
.nh-badge[data-hanh="mộc"] { color: #8fd6a6; }
.nh-badge[data-hanh="hỏa"] { color: #f5a08c; }
.nh-badge[data-hanh="thổ"] { color: #d9c08e; }
.nh-badge[data-hanh="kim"] { color: #e3e6ee; }
.nh-badge[data-hanh="thủy"] { color: #9cc3f0; }

.ctl-detail { border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 10px; }
.ctl-detail-shell {
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
  margin-bottom: 10px;
}
.ctl-oracle-art {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;
  padding: 0;
  border: 1px solid rgba(232, 201, 90, 0.24);
  border-radius: 8px;
  background: #071018;
  overflow: hidden;
  cursor: zoom-in;
}
.ctl-oracle-art img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.ctl-oracle-art > span {
  position: absolute;
  right: 7px;
  bottom: 7px;
  padding: 4px 7px;
  border: 1px solid rgba(232, 201, 90, 0.38);
  border-radius: 6px;
  background: rgba(5, 12, 18, 0.78);
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 10px;
  font-weight: 760;
}
.ctl-oracle-art-missing {
  display: grid;
  place-items: center;
  cursor: default;
  border-style: dashed;
}
.ctl-head h5 { margin: 0 0 4px 0; font-size: 14.5px; color: var(--accent-gold, #e8c95a); }
.ctl-zh { font-weight: 400; margin-left: 6px; opacity: 0.7; }
.ctl-head-badges { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.ctl-hoakhi, .ctl-chuve { font-size: 11.5px; color: var(--text-secondary, rgba(230,238,245,0.7)); font-style: italic; }
.ctl-kw { margin: 5px 0 0 0; font-size: 12px; color: var(--text-secondary, rgba(230,238,245,0.65)); font-style: italic; }
.ctl-art-meaning {
  margin: 8px 0 0 0;
  padding: 8px 10px;
  border-left: 2px solid rgba(232, 201, 90, 0.38);
  background: rgba(232, 201, 90, 0.045);
  color: var(--text-secondary, rgba(230,238,245,0.78));
  font-size: 12.5px;
  line-height: 1.55;
}
.ctl-dinh-vi { margin: 8px 0 4px 0; font-size: 13px; line-height: 1.6; color: var(--text-primary, rgba(230,238,245,0.92)); }
.ctl-odau {
  margin: 4px 0 0 0; font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.55;
  color: var(--read-text, rgba(230,238,245,0.85));
  border-left: 2px solid var(--read-rule, rgba(232, 201, 90, 0.4)); padding-left: 8px;
}
.ctl-uan { margin: 4px 0; }
.ctl-uan dt { font-size: calc(11.5px * var(--reading-scale, 1)); font-weight: 600; color: var(--read-han, #e8c95a); opacity: 0.9; margin-top: 7px; }
.ctl-uan dd { margin: 2px 0 0 0; font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6; color: var(--read-text-dim, rgba(230,238,245,0.8)); }
.ctl-manh { display: block; margin-top: 3px; color: #88d39e; }
.ctl-lech { display: block; margin-top: 2px; color: #f5b08c; }
.ctl-can { margin: 8px 0 0 0; font-size: 12.5px; line-height: 1.55; color: var(--read-text, rgba(230,238,245,0.88)); }

/* ── ☸ Quán chiếu Ngũ Uẩn — TÁCH LỚP 8 lớp ── */
.ctl-nu { margin: 10px 0 4px 0; }
.ctl-nu-summary {
  margin: 0 0 8px 0;
  padding: 8px 10px;
  background: var(--read-cite-bg, rgba(201, 161, 74, 0.10));
  border-left: 2px solid var(--read-cite-accent, #d9b977);
  border-radius: 4px;
}
.ctl-nu-goctham, .ctl-nu-duongra {
  margin: 0;
  font-size: calc(12.5px * var(--reading-scale, 1));
  line-height: 1.55;
  color: var(--read-text, rgba(230, 238, 245, 0.9));
}
.ctl-nu-duongra { margin-top: 5px; }
.ctl-nu-lbl {
  display: inline-block;
  font-size: calc(10.5px * var(--reading-scale, 1));
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--read-han, #d9b977);
  margin-right: 6px;
}
.ctl-nu-lbl-out { color: var(--read-note-accent, #a9c8a0); }
.ctl-nu-layer {
  margin: 5px 0;
  border: 1px solid var(--read-border, rgba(232, 201, 90, 0.18));
  border-radius: 5px;
  background: var(--read-surface, rgba(0, 0, 0, 0.12));
}
.ctl-nu-layer > summary {
  list-style: none;
  cursor: pointer;
  padding: 7px 10px;
  font-size: calc(12px * var(--reading-scale, 1));
  font-weight: 600;
  color: var(--read-heading, #f3e6c8);
  user-select: none;
}
.ctl-nu-layer > summary::-webkit-details-marker { display: none; }
.ctl-nu-layer > summary::after {
  content: "▼";
  float: right;
  font-size: 9px;
  opacity: 0.5;
  transition: transform 0.15s ease;
}
.ctl-nu-layer[open] > summary::after { transform: rotate(180deg); }
.ctl-nu-layer > summary b { color: var(--read-han, #d9b977); margin-right: 4px; }
.ctl-nu-layer > summary:hover { background: var(--read-cite-bg, rgba(201, 161, 74, 0.08)); }
.ctl-nu-body { padding: 2px 10px 9px 10px; }
.ctl-nu-kvs, .ctl-nu-doinguoi, .ctl-nu-khe, .ctl-nu-duongra-full {
  margin: 3px 0 0 0;
  font-size: calc(12.5px * var(--reading-scale, 1));
  line-height: 1.6;
  color: var(--read-text-dim, rgba(230, 238, 245, 0.8));
}
.ctl-nu-doinguoi .ctl-nu-lbl { color: var(--read-note-accent, #a9c8a0); }

/* Lớp 4 — nhãn ĐẮC / HÃM + nhánh đang ứng */
.ctl-kvs-tag {
  display: inline-block;
  margin-right: 6px;
  padding: 1px 7px;
  border-radius: 999px;
  font-size: calc(10px * var(--reading-scale, 1));
  font-weight: 800;
  letter-spacing: 0.05em;
  vertical-align: middle;
}
.ctl-kvs-tag-dac { color: #0f1c12; background: #88d39e; }
.ctl-kvs-tag-ham { color: #2a0f0a; background: #f5a08c; }
.ctl-kvs-now {
  margin-right: 6px;
  font-size: calc(10px * var(--reading-scale, 1));
  font-weight: 700;
  color: var(--accent-gold, #e8c95a);
}
.ctl-nu-kvs.ctl-kvs-active {
  padding: 4px 8px;
  border-radius: 5px;
  background: rgba(232, 201, 90, 0.08);
  border-left: 2px solid var(--accent-gold, #e8c95a);
}
/* Lớp 8 — căn cứ / nguồn (văn dẫn chứng dài, cỡ chữ nhỏ hơn) */
.ctl-nu-cancu {
  font-size: calc(11.5px * var(--reading-scale, 1));
  opacity: 0.85;
  white-space: pre-wrap;
}

.ctl-pos { margin: 6px 0 0 0; font-size: 12px; color: #88d39e; line-height: 1.5; }
.ctl-neg { margin: 3px 0 0 0; font-size: 12px; color: #f5b08c; line-height: 1.5; }
.ctl-mh { margin: 10px 0 0 0; display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }
.ctl-mh-label { font-size: 11.5px; color: var(--text-secondary, rgba(230,238,245,0.6)); width: 100%; }
.ctl-mh-chip {
  font-size: 11px; padding: 2px 7px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12); color: var(--text-secondary, rgba(230,238,245,0.75));
}
.ctl-mh-chip.lv-thuan { border-color: rgba(90,176,122,0.5); color: #88d39e; }
.ctl-mh-chip.lv-kha { border-color: rgba(192,168,120,0.55); color: #d9c08e; }
.ctl-mh-chip.lv-kho { border-color: rgba(214,90,74,0.5); color: #f5a08c; }
.ctl-andu { margin: 4px 0 0 0; padding-left: 4px; list-style: none; }
.ctl-andu li { font-size: calc(12px * var(--reading-scale, 1)); line-height: 1.55; color: var(--read-text-dim, rgba(230,238,245,0.75)); }
.ctl-quote {
  margin: 8px 0 0 0; padding: 6px 10px;
  border-left: 2px solid var(--read-cite-accent, rgba(232, 201, 90, 0.45));
  background: var(--read-cite-bg, rgba(232, 201, 90, 0.04));
  font-size: calc(12px * var(--reading-scale, 1)); font-style: italic; line-height: 1.55;
  color: var(--read-text, rgba(230,238,245,0.85));
}
.ctl-paradigm {
  margin: 12px 0 0 0; font-size: 11.5px; font-style: italic;
  color: var(--text-secondary, rgba(230,238,245,0.55));
}
.ctl-disclaimer {
  margin: 8px 0 0 0;
  padding: 7px 10px;
  font-size: 11px;
  line-height: 1.55;
  border-radius: 6px;
  border: 1px dashed rgba(232, 201, 90, 0.3);
  background: rgba(232, 201, 90, 0.04);
  color: var(--text-secondary, rgba(230,238,245,0.6));
}
/* 📜 Luận giải sâu đa phái */
.ctl-deep {
  margin-top: 14px;
  padding: 10px 12px;
  background: rgba(232, 201, 90, 0.04);
  border: 1px solid rgba(232, 201, 90, 0.2);
  border-radius: 6px;
}
.ctl-deep-title { margin: 0 0 8px 0; font-size: 13px; color: var(--accent-gold, #e8c95a); }
.ctl-deep-title small { font-weight: 400; margin-left: 6px; color: var(--text-secondary, rgba(230,238,245,0.55)); }
.ctl-deep-p { margin: 6px 0 0 0; font-size: 12.5px; line-height: 1.6; color: var(--text-secondary, rgba(230,238,245,0.82)); }
.ctl-deep-p b { color: var(--text-primary, rgba(230,238,245,0.92)); }
.ctl-deep-phai { margin: 8px 0; padding-left: 8px; border-left: 2px solid rgba(255,255,255,0.1); }
.ctl-deep-phai-item { margin: 4px 0; font-size: 12px; line-height: 1.55; color: var(--text-secondary, rgba(230,238,245,0.75)); }
.ctl-deep-phai-name { font-weight: 600; color: var(--text-primary, rgba(230,238,245,0.88)); }
.ctl-deep-cung-toggle {
  margin: 8px 0 0 0; padding: 5px 10px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.14);
  border-radius: 6px; color: var(--text-primary, rgba(230,238,245,0.88));
  font-size: 12px; cursor: pointer;
}
.ctl-deep-cung { margin: 8px 0 0 0; }
.ctl-deep-cung dt { font-size: 12px; font-weight: 600; color: var(--accent-gold, #e8c95a); margin-top: 8px; }
.ctl-deep-cung dt small { font-weight: 400; color: #f5b08c; }
.ctl-deep-cung dd { margin: 2px 0 0 0; font-size: 12.5px; line-height: 1.6; color: var(--text-secondary, rgba(230,238,245,0.8)); }
.ctl-deep-nguon { display: block; margin-top: 2px; font-size: 11px; font-style: italic; color: var(--text-secondary, rgba(230,238,245,0.5)); }
.ctl-deep-phu-label { margin: 8px 0 0 0; font-size: 12px; font-weight: 600; color: var(--text-primary, rgba(230,238,245,0.85)); }
.ctl-deep-khacbiet {
  margin: 8px 0 0 0; font-size: 12px; line-height: 1.55; font-style: italic;
  color: var(--text-secondary, rgba(230,238,245,0.7));
  border-left: 2px solid rgba(232, 201, 90, 0.35); padding-left: 8px;
}

.ctl-lightbox {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(2, 6, 12, 0.84);
  backdrop-filter: blur(8px);
}
.ctl-lightbox-close {
  position: fixed;
  top: 18px;
  right: 20px;
  width: 38px;
  height: 38px;
  border: 1px solid rgba(232, 201, 90, 0.35);
  border-radius: 50%;
  background: rgba(5, 12, 18, 0.86);
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 26px;
  cursor: pointer;
}
.ctl-lightbox figure {
  width: min(92vw, 980px);
  max-height: 92vh;
  margin: 0;
  display: grid;
  grid-template-columns: minmax(260px, 420px) minmax(240px, 1fr);
  gap: 18px;
  align-items: center;
}
.ctl-lightbox img {
  width: 100%;
  max-height: 88vh;
  object-fit: contain;
  border-radius: 10px;
  background: #071018;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.42);
}
.ctl-lightbox figcaption {
  display: grid;
  gap: 10px;
  padding: 16px;
  border: 1px solid rgba(232, 201, 90, 0.22);
  border-radius: 10px;
  background: rgba(5, 12, 18, 0.72);
}
.ctl-lightbox figcaption strong {
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 18px;
}
.ctl-lightbox figcaption span {
  color: rgba(248, 250, 252, 0.84);
  font-size: 13.5px;
  line-height: 1.65;
}

@media (max-width: 720px) {
  .ctl-detail-shell {
    grid-template-columns: 112px minmax(0, 1fr);
  }
  .ctl-grid {
    grid-template-columns: repeat(auto-fit, minmax(136px, 1fr));
  }
  .ctl-lightbox {
    padding: 14px;
  }
  .ctl-lightbox figure {
    grid-template-columns: 1fr;
    width: min(94vw, 520px);
  }
  .ctl-lightbox img {
    max-height: 68vh;
  }
}
</style>
