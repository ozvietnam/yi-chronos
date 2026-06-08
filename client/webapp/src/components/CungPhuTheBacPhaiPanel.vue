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

// Cross-reference panel: Mệnh + Phúc Đức + Đại Vận hiện tại + Thái Dương/Thái Âm
const crossRef = computed(() => result.value?.cross_reference || null);

// Engine v2 — 6 quy luật mới (Tứ Hóa, đào hoa phạm chủ, Tả-Hữu hội, đối cung, Mệnh chủ)
const v2 = computed(() => result.value?.v2 || null);
const v2Bias = computed(() => v2.value?.tu_tham_bias || null);
const v2Rules = computed(() => v2.value?.quy_luat_v2 || null);

// Engine v3 — cross-bind Phúc Đức + Mệnh
const v3Rules = computed(() => result.value?.v3?.quy_luat_v3 || null);
const v3CrossBind = computed(() => result.value?.v3?.cross_bind_phuc_duc || null);

// Engine v4 — Phase 2-5 (13 quy luật cross-bind 12 cung) + meta panorama
const v4Rules = computed(() => result.value?.v4?.quy_luat_v4 || null);
const v4Panorama = computed(() => result.value?.v4?.panorama_hon_nhan || null);
const v4DetectedRules = computed(() => {
  const rules = v4Rules.value || {};
  return Object.entries(rules)
    .filter(([_, r]) => r?.detected)
    .map(([key, r]) => ({ key, paradigm: r.paradigm }));
});

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

function isCurrentDv(dv) {
  const cur = crossRef.value?.dai_van_hien_tai?.current_dai_van;
  return cur && cur.start_age === dv.start_age && cur.end_age === dv.end_age;
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
            <div v-if="v2Rules['7_thai_duong_thai_am_mieu_ham']" class="rule">
              <strong>7. {{ v2Rules['7_thai_duong_thai_am_mieu_ham'].key_star }} (xem kèm):</strong>
              <span :class="v2Rules['7_thai_duong_thai_am_mieu_ham'].verdict === 'cát' ? 'success' : (v2Rules['7_thai_duong_thai_am_mieu_ham'].verdict === 'hung' ? 'warning' : '')">
                {{ v2Rules['7_thai_duong_thai_am_mieu_ham'].paradigm }}
              </span>
            </div>
          </div>
        </details>
      </div>

      <!-- Đại Vận Phu Thê chain -->
      <div v-if="v2Rules?.['8_dai_van_phu_the_chain']?.length" class="card dai-van-card">
        <h3>📅 8 Đại Vận — Cung Phu Thê</h3>
        <table class="dai-van-table">
          <thead>
            <tr><th>Tuổi</th><th>Mệnh ĐV</th><th>Phu Thê ĐV</th><th>Chính tinh</th><th>Cảnh báo</th></tr>
          </thead>
          <tbody>
            <tr v-for="dv in v2Rules['8_dai_van_phu_the_chain'].slice(0, 8)" :key="dv.start_age">
              <td>{{ dv.start_age }}–{{ dv.end_age }}</td>
              <td>{{ dv.menh_branch }}</td>
              <td><strong>{{ dv.phu_the_branch }}</strong></td>
              <td>{{ dv.phu_the_chinh_tinh.join(", ") || "—" }}</td>
              <td>
                <span v-if="dv.canh_bao?.length" class="warning">{{ dv.canh_bao[0] }}</span>
                <span v-else class="muted">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Engine v4: Panorama Toàn cảnh Hôn nhân (meta 26 quy luật) -->
      <div v-if="v4Panorama" class="card panorama-card">
        <h3>🌍 Toàn Cảnh Hôn Nhân (26 quy luật Bắc Phái)</h3>
        <div class="panorama-score">
          <div class="score-item cat">
            <span class="num">{{ v4Panorama.score_cat }}</span>
            <span class="lbl">Điểm cát ✅</span>
          </div>
          <div class="score-item hung">
            <span class="num">{{ v4Panorama.score_hung }}</span>
            <span class="lbl">Cảnh báo ⚠</span>
          </div>
          <div class="score-item overall" :class="v4Panorama.overall.replace(/\s+/g, '-').toLowerCase()">
            <span class="num-text">{{ v4Panorama.overall }}</span>
            <span class="lbl">Kết luận</span>
          </div>
        </div>
        <p class="hint-note">{{ v4Panorama.summary }}</p>

        <details v-if="v4DetectedRules.length" class="v4-details">
          <summary>🔍 Xem {{ v4DetectedRules.length }} quy luật Phase 2-5 đã kích hoạt</summary>
          <ul class="v4-rules-list">
            <li v-for="r in v4DetectedRules" :key="r.key">
              <strong>{{ r.key }}:</strong> {{ r.paradigm }}
            </li>
          </ul>
        </details>
      </div>

      <!-- Engine v3: Cross-bind Phúc Đức + Mệnh -->
      <div v-if="v3CrossBind" class="card cross-bind-card">
        <h3>🔗 Cross-bind Phúc Đức × Mệnh × Phu Thê</h3>
        <p class="hint-note">
          <em>Sách Trung Châu: "Phải xem KÈM cung Phúc Đức + Mệnh — đạo lý hôn nhân + cảnh báo tinh thần cross-bind."</em>
        </p>
        <div v-if="v3CrossBind.phuc_duc_chinh_tinh?.length">
          <strong>Phúc Đức chính tinh:</strong>
          <span v-for="s in v3CrossBind.phuc_duc_chinh_tinh" :key="s" class="star-chip">{{ s }}</span>
        </div>
        <div v-if="v3CrossBind.canh_bao_cross?.length" class="alert warning">
          <strong>⚠ Cảnh báo cross-bind:</strong>
          <ul>
            <li v-for="(c, i) in v3CrossBind.canh_bao_cross" :key="i">{{ c }}</li>
          </ul>
        </div>
        <div v-if="v3CrossBind.diem_cat_cross?.length" class="alert success">
          <strong>✅ Điểm cát cross-bind:</strong>
          <ul>
            <li v-for="(c, i) in v3CrossBind.diem_cat_cross" :key="i">{{ c }}</li>
          </ul>
        </div>
        <details v-if="v3Rules" class="v3-details">
          <summary>Xem chi tiết 4 quy luật cross-bind (Q10-Q13)</summary>
          <div class="rule-grid">
            <div class="rule">
              <strong>Q10: Văn Khúc Hóa Kỵ ở Phúc Đức/Phu Thê/Mệnh:</strong>
              <span :class="v3Rules['10_van_khuc_hoa_ki_cross'].detected ? 'warning' : 'muted'">
                {{ v3Rules['10_van_khuc_hoa_ki_cross'].paradigm }}
              </span>
            </div>
            <div class="rule">
              <strong>Q11: Xương-Khúc giáp Phu Thê:</strong>
              <span :class="v3Rules['11_xuong_khuc_giap_phu_the'].detected ? 'warning' : 'muted'">
                {{ v3Rules['11_xuong_khuc_giap_phu_the'].paradigm }}
              </span>
            </div>
            <div class="rule">
              <strong>Q12: Xương-Khúc chia rẽ cát:</strong>
              <span :class="v3Rules['12_xuong_khuc_chia_re_cat'].detected ? 'success' : 'muted'">
                {{ v3Rules['12_xuong_khuc_chia_re_cat'].paradigm }}
              </span>
            </div>
            <div class="rule">
              <strong>Q13: Địa Không cross tinh thần:</strong>
              <span :class="v3Rules['13_dia_khong_cross_tam_phuc'].detected ? 'warning' : 'muted'">
                {{ v3Rules['13_dia_khong_cross_tam_phuc'].paradigm }}
              </span>
            </div>
          </div>
        </details>
      </div>

      <!-- Lưu Niên Markers -->
      <div v-if="v2Rules?.['9_luu_nien_markers']?.length" class="card luu-nien-card">
        <h3>🌸 Năm Hồng Loan / Thiên Hỉ đến Mệnh-Phu Thê (10 năm)</h3>
        <p class="hint-note">
          <em>Sách Trung Châu: "Lưu niên có Hồng Loan/Thiên Hỉ bay đến cung Mệnh hoặc Phu Thê có thể là ứng kỳ kết hôn / thai sản — NHƯNG cần tinh hệ chính diệu cát lợi ổn định."</em>
        </p>
        <ul class="luu-nien-list">
          <li v-for="m in v2Rules['9_luu_nien_markers']" :key="m.year">
            <strong>{{ m.year }}</strong> ({{ m.year_branch }}): {{ m.triggers.join("; ") }}
          </li>
        </ul>
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

          <!-- ✅ MATCHED — ứng với lá số riêng -->
          <div v-if="(viTriParadigm[sao.ten].matched || []).length" class="match-block">
            <div class="match-block-header">
              <span class="badge badge-match">✓ ỨNG VỚI LÁ SỐ NÀY</span>
              <span class="match-count">{{ viTriParadigm[sao.ten].matched.length }} dòng</span>
            </div>
            <ul class="paradigm-list matched">
              <li v-for="m in viTriParadigm[sao.ten].matched" :key="'m-'+m.key">
                <div class="row-head">
                  <strong>{{ m.label }}:</strong>
                  <span class="text">{{ m.text }}</span>
                </div>
                <div class="row-reason" v-if="m.reason">
                  <em>↪ lý do áp dụng:</em> {{ m.reason }}
                </div>
              </li>
            </ul>
          </div>

          <!-- ❌ UNMATCHED — paradigm chung, KHÔNG áp dụng -->
          <details v-if="(viTriParadigm[sao.ten].unmatched || []).length" class="unmatch-block">
            <summary>
              <span class="badge badge-unmatch">○ Paradigm CHUNG — KHÔNG ứng với lá số</span>
              <span class="match-count">{{ viTriParadigm[sao.ten].unmatched.length }} dòng (xem để hiểu sách nói gì)</span>
            </summary>
            <ul class="paradigm-list unmatched">
              <li v-for="u in viTriParadigm[sao.ten].unmatched" :key="'u-'+u.key">
                <div class="row-head">
                  <strong>{{ u.label }}:</strong>
                  <span class="text muted">{{ u.text }}</span>
                </div>
                <div class="row-reason" v-if="u.reason">
                  <em>↪ vì sao KHÔNG áp dụng:</em> {{ u.reason }}
                </div>
              </li>
            </ul>
          </details>

          <!-- 📚 Citation -->
          <div v-if="viTriParadigm[sao.ten].citation" class="citation">
            📖 <strong>Nguồn:</strong>
            {{ viTriParadigm[sao.ten].citation.book }} —
            <em>{{ viTriParadigm[sao.ten].citation.section }}</em>
          </div>
        </div>
      </div>

      <!-- ─── Cross-Reference Panel — Mệnh + Phúc Đức + Đại Vận + Thái Dương/Thái Âm -->
      <div v-if="crossRef" class="card cross-ref-card">
        <h3>🔗 Cần xem kèm — Render thật cho lá số của bạn</h3>
        <p class="cross-ref-intro">
          Sách Trung Châu §5.3: <em>cung Phu Thê KHÔNG đứng một mình</em> —
          phải đối chiếu 4 yếu tố sau để hiểu chính xác.
        </p>

        <!-- 1. Cung Mệnh -->
        <details v-if="crossRef.cung_menh" class="xr-block" open>
          <summary>
            <span class="xr-badge xr-menh">① Cung Mệnh</span>
            <span class="xr-pos">tại <strong>{{ crossRef.cung_menh.branch }}</strong></span>
          </summary>
          <div class="xr-body">
            <div class="xr-stars">
              <span v-for="s in crossRef.cung_menh.chinh_tinh" :key="'mc-'+s" class="star-chip primary">{{ s }}</span>
              <span v-for="s in crossRef.cung_menh.phu_tinh" :key="'mp-'+s" class="star-chip">{{ s }}</span>
              <span v-for="s in crossRef.cung_menh.sat_tinh" :key="'ms-'+s" class="star-chip warning">{{ s }}</span>
              <span v-for="s in crossRef.cung_menh.sao_q2" :key="'mq-'+s" class="star-chip">{{ s }}</span>
            </div>
            <div v-if="crossRef.cung_menh.hoa_in_palace?.length" class="xr-hoa">
              <span v-for="h in crossRef.cung_menh.hoa_in_palace" :key="h" class="hoa-chip">{{ h }}</span>
            </div>
            <ul class="xr-paradigm">
              <li v-for="(p, i) in crossRef.cung_menh.paradigms" :key="i">{{ p }}</li>
            </ul>
            <p class="xr-note"><em>{{ crossRef.cung_menh.note }}</em></p>
          </div>
        </details>

        <!-- 2. Cung Phúc Đức -->
        <details v-if="crossRef.cung_phuc_duc" class="xr-block" open>
          <summary>
            <span class="xr-badge xr-phuc">② Cung Phúc Đức</span>
            <span class="xr-pos">tại <strong>{{ crossRef.cung_phuc_duc.branch }}</strong></span>
            <span class="xr-tag">cross-bind QUAN TRỌNG NHẤT</span>
          </summary>
          <div class="xr-body">
            <div class="xr-stars">
              <span v-for="s in crossRef.cung_phuc_duc.chinh_tinh" :key="'pc-'+s" class="star-chip primary">{{ s }}</span>
              <span v-for="s in crossRef.cung_phuc_duc.phu_tinh" :key="'pp-'+s" class="star-chip">{{ s }}</span>
              <span v-for="s in crossRef.cung_phuc_duc.sat_tinh" :key="'ps-'+s" class="star-chip warning">{{ s }}</span>
              <span v-for="s in crossRef.cung_phuc_duc.sao_q2" :key="'pq-'+s" class="star-chip">{{ s }}</span>
            </div>
            <div v-if="crossRef.cung_phuc_duc.hoa_in_palace?.length" class="xr-hoa">
              <span v-for="h in crossRef.cung_phuc_duc.hoa_in_palace" :key="h" class="hoa-chip">{{ h }}</span>
            </div>
            <ul v-if="crossRef.cung_phuc_duc.paradigms?.length" class="xr-paradigm">
              <li v-for="(p, i) in crossRef.cung_phuc_duc.paradigms" :key="i">{{ p }}</li>
            </ul>
            <ul v-if="crossRef.cung_phuc_duc.sao_doi_notes?.length" class="xr-sao-doi">
              <li v-for="(n, i) in crossRef.cung_phuc_duc.sao_doi_notes" :key="i"
                  :class="{ ok: n.startsWith('✓'), warn: n.startsWith('⚠') }">
                {{ n }}
              </li>
            </ul>
            <ul v-if="crossRef.cung_phuc_duc.canh_bao_cross?.length" class="xr-canh-bao">
              <li v-for="(c, i) in crossRef.cung_phuc_duc.canh_bao_cross" :key="i">{{ c }}</li>
            </ul>
            <p class="xr-note"><em>{{ crossRef.cung_phuc_duc.note }}</em></p>
          </div>
        </details>

        <!-- 3. Đại Vận hiện tại -->
        <details v-if="crossRef.dai_van_hien_tai" class="xr-block" open>
          <summary>
            <span class="xr-badge xr-dv">③ Đại Vận hiện tại</span>
            <span v-if="crossRef.dai_van_hien_tai.current_age" class="xr-pos">
              tuổi <strong>{{ crossRef.dai_van_hien_tai.current_age }}</strong>
            </span>
          </summary>
          <div class="xr-body">
            <div v-if="crossRef.dai_van_hien_tai.current_dai_van" class="xr-dv-current">
              <strong>Đang trong đại vận {{ crossRef.dai_van_hien_tai.current_dai_van.start_age }}–{{ crossRef.dai_van_hien_tai.current_dai_van.end_age }} tuổi</strong> ·
              Mệnh đại vận tại <strong>{{ crossRef.dai_van_hien_tai.current_dai_van.menh_branch }}</strong> ·
              Phu Thê đại vận tại <strong>{{ crossRef.dai_van_hien_tai.current_dai_van.phu_the_branch }}</strong>
              <span v-if="crossRef.dai_van_hien_tai.current_dai_van.phu_the_chinh_tinh?.length">
                ({{ crossRef.dai_van_hien_tai.current_dai_van.phu_the_chinh_tinh.join(", ") }})
              </span>
            </div>
            <table v-if="crossRef.dai_van_hien_tai.all_dai_van?.length" class="dai-van-table">
              <thead>
                <tr>
                  <th>Tuổi</th>
                  <th>Mệnh đại vận</th>
                  <th>Phu Thê đại vận</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(dv, i) in crossRef.dai_van_hien_tai.all_dai_van" :key="i"
                    :class="{ 'dv-current': isCurrentDv(dv) }">
                  <td>{{ dv.start_age }}–{{ dv.end_age }}</td>
                  <td>{{ dv.menh_branch }}</td>
                  <td>
                    <strong>{{ dv.phu_the_branch }}</strong>
                    <span v-if="dv.phu_the_chinh_tinh?.length" class="muted">
                      ({{ dv.phu_the_chinh_tinh.join(", ") }})
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <p class="xr-note"><em>{{ crossRef.dai_van_hien_tai.note }}</em></p>
          </div>
        </details>

        <!-- 4. Thái Dương / Thái Âm miếu hãm -->
        <details v-if="crossRef.thai_duong_thai_am" class="xr-block" open>
          <summary>
            <span class="xr-badge xr-tdta">④ Thái Dương / Thái Âm — miếu hãm</span>
          </summary>
          <div class="xr-body">
            <div v-if="crossRef.thai_duong_thai_am.thai_duong" class="xr-tdta-row">
              <strong>☀ Thái Dương</strong>
              tại <strong>{{ crossRef.thai_duong_thai_am.thai_duong.branch }}</strong> ·
              <span class="xr-level" :class="'lvl-' + (crossRef.thai_duong_thai_am.thai_duong.level || '').toLowerCase()">
                {{ crossRef.thai_duong_thai_am.thai_duong.level_label || crossRef.thai_duong_thai_am.thai_duong.level }}
              </span>
              <div class="xr-paradigm-single">→ {{ crossRef.thai_duong_thai_am.thai_duong.paradigm }}</div>
            </div>
            <div v-if="crossRef.thai_duong_thai_am.thai_am" class="xr-tdta-row">
              <strong>☾ Thái Âm</strong>
              tại <strong>{{ crossRef.thai_duong_thai_am.thai_am.branch }}</strong> ·
              <span class="xr-level" :class="'lvl-' + (crossRef.thai_duong_thai_am.thai_am.level || '').toLowerCase()">
                {{ crossRef.thai_duong_thai_am.thai_am.level_label || crossRef.thai_duong_thai_am.thai_am.level }}
              </span>
              <div class="xr-paradigm-single">→ {{ crossRef.thai_duong_thai_am.thai_am.paradigm }}</div>
            </div>
            <p class="xr-note"><em>{{ crossRef.thai_duong_thai_am.note }}</em></p>
          </div>
        </details>
      </div>

      <!-- Disclaimer (trí tuệ Iron Rule) -->
      <div class="card disclaimer-card">
        <p class="disclaimer">
          📜 <em>Paradigm Bắc phái Trung Châu = đọc ĐỒNG DẠNG, KHÔNG predict tuyệt đối.
          Cung Phu Thê chỉ phản chiếu KHUYNH HƯỚNG hôn nhân, không phải số phận cố định.</em>
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
/* ─── Dark sepia theme matching project reading-comfort tokens
   --read-bg: #1d1813 (warm dark)
   --read-text: #e9dcc6 (cream)
   --read-heading: #f3e6c8 (light cream)
   --read-han: #d9b977 (amber)
   --read-rule: #c9a14a (gold)
   --read-border: rgba(201, 161, 74, 0.22)

   Tất cả surface dùng translucent dark — dễ đọc, không chói. */

.phu-the-panel {
  padding: 16px;
  font-family: var(--font-family, "Inter", -apple-system, sans-serif);
  color: var(--read-text, #e9dcc6);
  background: var(--read-bg, #1d1813);
  border-radius: 8px;
  line-height: 1.55;
}
.panel-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  border-bottom: 2px solid var(--read-rule, #c9a14a);
  padding-bottom: 10px;
  margin-bottom: 16px;
}
.panel-header h2 {
  margin: 0;
  font-size: 1.45em;
  color: var(--read-heading, #f3e6c8);
}
.school-tag {
  font-size: 0.85em;
  color: var(--read-han, #d9b977);
  font-style: italic;
}

/* ─── Buttons ──────────────────────────────────────────────── */
.btn-primary {
  background: var(--read-han, #d9b977);
  color: #1d1813;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 1.05em;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover { background: var(--read-rule, #c9a14a); }
.btn-secondary {
  background: transparent;
  color: var(--read-han, #d9b977);
  border: 1px solid var(--read-rule, #c9a14a);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
}
.btn-secondary:hover {
  background: rgba(201, 161, 74, 0.12);
}

/* ─── States ──────────────────────────────────────────────── */
.loading { padding: 24px; text-align: center; font-style: italic; color: var(--read-text-dim, rgba(233, 220, 198, 0.72)); }
.error {
  padding: 12px;
  color: #ff8a8a;
  background: rgba(204, 51, 51, 0.15);
  border: 1px solid rgba(204, 51, 51, 0.35);
  border-radius: 6px;
}

.no-chart-hint {
  padding: 14px;
  background: rgba(201, 161, 74, 0.10);
  border: 1px dashed var(--read-rule, #c9a14a);
  border-radius: 6px;
  font-size: 0.95em;
  color: var(--read-text, #e9dcc6);
}
.no-chart-hint ul { margin: 8px 0 8px 20px; }
.no-chart-hint code {
  background: rgba(217, 185, 119, 0.18);
  color: var(--read-han, #d9b977);
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 0.92em;
}
.hint-note {
  color: var(--read-text-dim, rgba(233, 220, 198, 0.72));
  font-size: 0.88em;
  margin-top: 8px;
}

/* ─── Cards: tất cả dùng translucent dark — KHÔNG trắng ──────── */
.result { display: flex; flex-direction: column; gap: 14px; }

.card {
  background: var(--read-surface, #221b14);
  border: 1px solid var(--read-border, rgba(201, 161, 74, 0.22));
  border-radius: 8px;
  padding: 16px;
  color: var(--read-text, #e9dcc6);
}

.card h3 {
  color: var(--read-heading, #f3e6c8);
  margin: 0 0 10px;
  font-size: 1.1em;
}
.card h4 {
  color: var(--read-han, #d9b977);
  margin: 12px 0 6px;
  font-size: 0.98em;
}

/* ─── Cung position card ──────────────────────────────────── */
.cung-card {
  background: linear-gradient(135deg, rgba(217, 185, 119, 0.12) 0%, rgba(201, 161, 74, 0.06) 100%);
  border-color: rgba(217, 185, 119, 0.35);
}
.cung-pos { font-size: 1.1em; margin-bottom: 10px; }
.cung-pos .label { color: var(--read-text-dim, rgba(233, 220, 198, 0.72)); }
.cung-pos .branch {
  font-size: 1.8em;
  font-weight: bold;
  color: var(--read-han, #d9b977);
  margin-left: 10px;
}
.stars-list { display: flex; flex-direction: column; gap: 8px; }
.star-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.star-label {
  font-weight: 600;
  min-width: 110px;
  color: var(--read-text-dim, rgba(233, 220, 198, 0.72));
}
.star-chip {
  background: rgba(217, 185, 119, 0.12);
  border: 1px solid rgba(217, 185, 119, 0.30);
  color: var(--read-text, #e9dcc6);
  padding: 3px 10px;
  border-radius: 14px;
  font-size: 0.92em;
}
.star-chip.primary {
  background: rgba(217, 185, 119, 0.22);
  border-color: var(--read-han, #d9b977);
  color: var(--read-heading, #f3e6c8);
  font-weight: 600;
}
.star-chip.warning {
  background: rgba(204, 51, 51, 0.15);
  border-color: rgba(204, 51, 51, 0.55);
  color: #ff8a8a;
}
.vo-chinh { font-style: italic; color: var(--read-text-faint, rgba(233, 220, 198, 0.5)); }

/* ─── Tổ hợp đôi card ─────────────────────────────────────── */
.to-hop-card {
  background: rgba(91, 229, 211, 0.06);
  border-color: rgba(91, 229, 211, 0.25);
}
.to-hop-note { margin: 0; font-style: italic; color: var(--read-text, #e9dcc6); }

/* ─── Engine v2 — Phân tích bias ──────────────────────────── */
.v2-card {
  background: linear-gradient(135deg, rgba(91, 229, 211, 0.10) 0%, rgba(126, 234, 218, 0.04) 100%);
  border-color: rgba(91, 229, 211, 0.30);
}
.bias-headline {
  font-size: 1.18em;
  font-weight: bold;
  padding: 8px 0;
  color: var(--read-heading, #f3e6c8);
}
.bias-reasons { margin: 4px 0 0 20px; padding: 0; font-size: 0.95em; }
.bias-reasons li { margin: 5px 0; }

.v2-details, .v3-details, .v4-details { margin-top: 12px; }
.v2-details summary,
.v3-details summary,
.v4-details summary {
  cursor: pointer;
  font-weight: 600;
  padding: 6px 8px;
  background: rgba(217, 185, 119, 0.08);
  border-radius: 4px;
  color: var(--read-han, #d9b977);
}
.v2-details summary:hover,
.v3-details summary:hover,
.v4-details summary:hover { background: rgba(217, 185, 119, 0.16); }

.rule-grid { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
.rule { font-size: 0.93em; }
.rule strong {
  display: block;
  margin-bottom: 3px;
  color: var(--read-heading, #f3e6c8);
}
.rule .muted { color: var(--read-text-faint, rgba(233, 220, 198, 0.5)); font-style: italic; }
.rule .success { color: #7eeada; }
.rule .warning { color: #ffb88a; font-weight: 600; }

/* ─── Đại Vận table ───────────────────────────────────────── */
.dai-van-card {
  background: rgba(232, 201, 90, 0.06);
  border-color: rgba(232, 201, 90, 0.30);
}
.dai-van-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92em;
  color: var(--read-text, #e9dcc6);
}
.dai-van-table th,
.dai-van-table td {
  padding: 8px;
  border-bottom: 1px solid var(--read-border, rgba(201, 161, 74, 0.22));
  text-align: left;
}
.dai-van-table th {
  background: rgba(217, 185, 119, 0.12);
  font-weight: 600;
  color: var(--read-han, #d9b977);
}
.dai-van-table td strong { color: var(--read-han, #d9b977); }

/* ─── Lưu Niên markers ────────────────────────────────────── */
.luu-nien-card {
  background: rgba(232, 201, 90, 0.06);
  border-color: rgba(232, 201, 90, 0.30);
}
.luu-nien-list { margin: 8px 0 0 20px; padding: 0; font-size: 0.95em; }
.luu-nien-list li { margin: 5px 0; }
.luu-nien-list strong { color: var(--read-han, #d9b977); }

/* ─── Cross-bind v3 ───────────────────────────────────────── */
.cross-bind-card {
  background: rgba(169, 200, 160, 0.08);
  border-color: rgba(169, 200, 160, 0.30);
}

/* ─── Panorama v4 (meta 26 quy luật) — nổi bật ────────────── */
.panorama-card {
  background: linear-gradient(135deg, rgba(217, 185, 119, 0.18) 0%, rgba(201, 161, 74, 0.10) 100%);
  border-color: var(--read-rule, #c9a14a);
  border-width: 2px;
}
.panorama-card h3 { color: var(--read-han, #d9b977); }
.panorama-score {
  display: flex;
  gap: 12px;
  margin: 14px 0;
  flex-wrap: wrap;
}
.score-item {
  flex: 1;
  min-width: 100px;
  text-align: center;
  padding: 14px 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--read-border, rgba(201, 161, 74, 0.22));
  border-radius: 6px;
}
.score-item .num {
  display: block;
  font-size: 2em;
  font-weight: bold;
}
.score-item .num-text {
  display: block;
  font-size: 1.2em;
  font-weight: bold;
}
.score-item .lbl {
  display: block;
  font-size: 0.85em;
  color: var(--read-text-dim, rgba(233, 220, 198, 0.72));
  margin-top: 4px;
}
.score-item.cat .num { color: #7eeada; }
.score-item.hung .num { color: #ffb88a; }
.score-item.overall.cát-thắng .num-text { color: #7eeada; }
.score-item.overall.hung-thắng .num-text { color: #ffb88a; }
.score-item.overall.trung-hòa .num-text { color: var(--read-han, #d9b977); }
.score-item.overall { border-color: rgba(217, 185, 119, 0.45); }

.v4-rules-list { margin: 8px 0 0 20px; font-size: 0.92em; }
.v4-rules-list li { margin: 6px 0; }
.v4-rules-list strong { color: var(--read-han, #d9b977); }

/* ─── Alerts inline (cảnh báo / điểm cát) ─────────────────── */
.alert.warning {
  background: rgba(204, 51, 51, 0.10);
  border: 1px solid rgba(204, 51, 51, 0.35);
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  color: #ffb88a;
}
.alert.success {
  background: rgba(91, 229, 211, 0.08);
  border: 1px solid rgba(91, 229, 211, 0.35);
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  color: #7eeada;
}
.alert ul { margin: 6px 0 0 20px; }
.alert strong { color: inherit; }

/* ─── Hoa chip (Tứ Hóa highlight) ─────────────────────────── */
.hoa-chip {
  display: inline-block;
  background: var(--read-han, #d9b977);
  color: #1d1813;
  border: 1px solid var(--read-rule, #c9a14a);
  padding: 2px 10px;
  border-radius: 12px;
  margin: 2px 4px 2px 0;
  font-size: 0.88em;
  font-weight: 600;
}

/* ─── Warning card (general) ──────────────────────────────── */
.warning-card {
  background: rgba(204, 51, 51, 0.08);
  border-color: rgba(204, 51, 51, 0.30);
}
.warning-card h3 { color: #ffb88a; }
.warning-card ul { margin: 0; padding-left: 20px; color: #ffb88a; }

/* ─── Per-star paradigm card ──────────────────────────────── */
.star-card {
  background: var(--read-surface, #221b14);
  border-color: rgba(217, 185, 119, 0.22);
}
.star-card h3 { color: var(--read-han, #d9b977); }
.ban-chat, .co-ban { margin: 6px 0; }
.ban-chat strong, .co-ban strong { color: var(--read-heading, #f3e6c8); }

.vi-tri h4 {
  margin: 14px 0 8px;
  font-size: 0.98em;
  color: var(--read-han, #d9b977);
  border-bottom: 1px solid var(--read-border, rgba(201, 161, 74, 0.22));
  padding-bottom: 4px;
}
.paradigm-list { margin: 0; padding-left: 20px; font-size: 0.92em; }
.paradigm-list li { margin: 8px 0; }
.paradigm-list strong { color: var(--read-han, #d9b977); }

/* ─── Match vs Unmatch blocks ────────────────────────────────────── */
.match-block {
  margin-top: 10px;
  padding: 12px;
  background: rgba(91, 229, 211, 0.06);
  border: 1px solid rgba(91, 229, 211, 0.32);
  border-left: 4px solid #5be5d3;
  border-radius: 6px;
}
.match-block-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 0.82em;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.badge-match {
  background: rgba(91, 229, 211, 0.22);
  color: #7eeada;
  border: 1px solid rgba(91, 229, 211, 0.45);
}
.badge-unmatch {
  background: rgba(233, 220, 198, 0.10);
  color: var(--read-text-dim, rgba(233, 220, 198, 0.72));
  border: 1px solid var(--read-border, rgba(201, 161, 74, 0.22));
}
.match-count {
  font-size: 0.84em;
  color: var(--read-text-dim, rgba(233, 220, 198, 0.72));
  font-style: italic;
}
.paradigm-list.matched li {
  border-bottom: 1px dashed rgba(91, 229, 211, 0.18);
  padding-bottom: 8px;
}
.paradigm-list.matched li:last-child { border-bottom: none; }
.row-head {
  line-height: 1.55;
}
.row-head .text {
  margin-left: 6px;
  color: var(--read-text, #e9dcc6);
}
.row-head .text.muted {
  color: var(--read-text-faint, rgba(233, 220, 198, 0.55));
  text-decoration: line-through;
  text-decoration-color: rgba(233, 220, 198, 0.25);
  text-decoration-style: dotted;
}
.row-reason {
  margin-top: 4px;
  padding: 4px 8px;
  font-size: 0.86em;
  color: var(--read-han, #d9b977);
  background: rgba(217, 185, 119, 0.06);
  border-radius: 3px;
  font-style: italic;
}
.unmatch-block {
  margin-top: 10px;
  padding: 8px 12px;
  background: var(--read-bg-soft, rgba(36, 29, 22, 0.5));
  border: 1px dashed var(--read-border, rgba(201, 161, 74, 0.22));
  border-radius: 6px;
  font-size: 0.92em;
}
.unmatch-block summary {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 0;
  user-select: none;
}
.unmatch-block summary:hover { color: var(--read-han, #d9b977); }
.unmatch-block .paradigm-list { margin-top: 8px; }
.unmatch-block .row-reason {
  color: var(--read-text-faint, rgba(233, 220, 198, 0.55));
  background: rgba(204, 51, 51, 0.06);
}
.citation {
  margin-top: 10px;
  padding: 6px 10px;
  font-size: 0.84em;
  background: rgba(217, 185, 119, 0.06);
  border-left: 2px solid var(--read-rule, #c9a14a);
  color: var(--read-text-dim, rgba(233, 220, 198, 0.72));
  border-radius: 3px;
}
.citation strong { color: var(--read-han, #d9b977); }

/* ─── Cross-Reference Panel ──────────────────────────────────────── */
.cross-ref-card {
  background: linear-gradient(135deg, rgba(126, 234, 218, 0.06) 0%, rgba(217, 185, 119, 0.06) 100%);
  border-color: rgba(126, 234, 218, 0.32);
  border-left: 4px solid #7eeada;
}
.cross-ref-card h3 {
  color: #7eeada;
  margin: 0 0 8px;
}
.cross-ref-intro {
  margin: 0 0 12px;
  color: var(--read-text-dim, rgba(233, 220, 198, 0.78));
  font-size: 0.92em;
}

.xr-block {
  margin: 10px 0;
  border: 1px solid var(--read-border, rgba(201, 161, 74, 0.22));
  border-radius: 6px;
  background: var(--read-bg-soft, rgba(36, 29, 22, 0.6));
  padding: 4px 0;
}
.xr-block summary {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  flex-wrap: wrap;
  user-select: none;
}
.xr-block summary:hover { background: rgba(217, 185, 119, 0.06); }

.xr-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.86em;
  font-weight: 700;
  letter-spacing: 0.2px;
}
.xr-menh    { background: rgba(217, 185, 119, 0.18); color: var(--read-han, #d9b977); border: 1px solid var(--read-rule, #c9a14a); }
.xr-phuc    { background: rgba(255, 138, 138, 0.16); color: #ffb88a; border: 1px solid rgba(255, 138, 138, 0.45); }
.xr-dv      { background: rgba(126, 234, 218, 0.16); color: #7eeada; border: 1px solid rgba(126, 234, 218, 0.45); }
.xr-tdta    { background: rgba(255, 217, 102, 0.16); color: #ffd966; border: 1px solid rgba(255, 217, 102, 0.45); }

.xr-pos {
  color: var(--read-text, #e9dcc6);
  font-size: 0.92em;
}
.xr-pos strong { color: var(--read-han, #d9b977); font-size: 1.1em; }

.xr-tag {
  font-size: 0.78em;
  padding: 2px 8px;
  background: rgba(255, 138, 138, 0.10);
  color: #ffb88a;
  border-radius: 3px;
  font-style: italic;
}

.xr-body {
  padding: 4px 14px 12px;
}
.xr-stars {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0;
}
.xr-hoa {
  margin: 6px 0;
}
.xr-paradigm {
  margin: 8px 0 8px 20px;
  padding: 0;
  font-size: 0.93em;
}
.xr-paradigm li {
  margin: 6px 0;
  color: var(--read-text, #e9dcc6);
  line-height: 1.55;
}

.xr-paradigm-single {
  margin: 6px 0 0 18px;
  color: var(--read-text, #e9dcc6);
  font-size: 0.93em;
  line-height: 1.5;
}

.xr-sao-doi {
  list-style: none;
  margin: 8px 0;
  padding: 0;
}
.xr-sao-doi li {
  padding: 4px 10px;
  border-radius: 3px;
  margin: 3px 0;
  font-size: 0.92em;
}
.xr-sao-doi li.ok {
  background: rgba(126, 234, 218, 0.10);
  color: #7eeada;
  border-left: 3px solid #7eeada;
}
.xr-sao-doi li.warn {
  background: rgba(255, 184, 138, 0.10);
  color: #ffb88a;
  border-left: 3px solid #ffb88a;
}

.xr-canh-bao {
  margin: 8px 0 8px 20px;
  padding: 0;
}
.xr-canh-bao li {
  margin: 6px 0;
  color: #ff8a8a;
  font-size: 0.93em;
  line-height: 1.5;
}

.xr-note {
  margin: 10px 0 0;
  padding: 8px 10px;
  background: rgba(217, 185, 119, 0.06);
  border-left: 2px solid var(--read-rule, #c9a14a);
  border-radius: 3px;
  font-size: 0.86em;
  color: var(--read-text-dim, rgba(233, 220, 198, 0.78));
  line-height: 1.5;
}

.xr-dv-current {
  padding: 10px 12px;
  background: rgba(126, 234, 218, 0.12);
  border: 1px solid rgba(126, 234, 218, 0.42);
  border-radius: 6px;
  margin-bottom: 10px;
  color: var(--read-text, #e9dcc6);
  line-height: 1.5;
}
.xr-dv-current strong { color: #7eeada; }

tr.dv-current {
  background: rgba(126, 234, 218, 0.12);
}
tr.dv-current td { font-weight: 600; }
tr.dv-current strong { color: #7eeada; }
td .muted {
  margin-left: 4px;
  font-size: 0.88em;
  color: var(--read-text-dim, rgba(233, 220, 198, 0.72));
}

.xr-tdta-row {
  margin: 10px 0;
  padding: 10px 12px;
  background: rgba(255, 217, 102, 0.06);
  border-left: 3px solid rgba(255, 217, 102, 0.55);
  border-radius: 4px;
  color: var(--read-text, #e9dcc6);
  line-height: 1.55;
}
.xr-tdta-row strong { color: var(--read-han, #d9b977); }
.xr-level {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 0.86em;
  font-weight: 600;
  margin-left: 4px;
}
.xr-level.lvl-miếu  { background: rgba(126, 234, 218, 0.22); color: #7eeada; }
.xr-level.lvl-vượng { background: rgba(126, 234, 218, 0.18); color: #7eeada; }
.xr-level.lvl-đắc   { background: rgba(217, 185, 119, 0.20); color: var(--read-han, #d9b977); }
.xr-level.lvl-bình  { background: rgba(233, 220, 198, 0.12); color: var(--read-text-dim, rgba(233, 220, 198, 0.85)); }
.xr-level.lvl-lạc   { background: rgba(255, 184, 138, 0.16); color: #ffb88a; }
.xr-level.lvl-hãm   { background: rgba(255, 138, 138, 0.18); color: #ff8a8a; }

/* ─── Disclaimer card ─────────────────────────────────────── */
.disclaimer-card {
  background: var(--read-cite-bg, rgba(201, 161, 74, 0.10));
  border-color: var(--read-cite-accent, #d9b977);
  font-size: 0.88em;
}
.disclaimer {
  margin: 0 0 10px;
  color: var(--read-text, #e9dcc6);
  line-height: 1.5;
}
.thay-credit, .source {
  margin-top: 6px;
  color: var(--read-text-dim, rgba(233, 220, 198, 0.72));
  font-size: 0.85em;
}
.thay-credit strong, .source strong { color: var(--read-han, #d9b977); }
</style>
