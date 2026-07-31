<template>
  <div class="tu-vi-3layer-panel">
    <h2>🌌 Luận giải Tử Vi 3-Layer × 4 hệ phái</h2>

    <div v-if="loading" class="loading">Đang luận giải lá số...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="result">
      <!-- Lớp 1: Chuyện về anh — bài luận mượt là MẶC ĐỊNH (tự chạy) -->
      <section class="lop-1">
        <h3>💬 Chuyện về anh
          <button v-if="narrative" class="narrative-btn" :disabled="narrativeLoading" @click="loadNarrative">
            {{ narrativeLoading ? '⏳ Đang viết...' : '🔄 Viết lại' }}
          </button>
        </h3>
        <div v-if="narrativeLoading && !narrative" class="content narrative-loading">
          ✍️ Đang luận lá số của anh từ kho sách 5 hệ phái... (10-15 giây)
        </div>
        <div v-else-if="narrative" class="content narrative-text" v-html="renderMarkdown(narrative)"></div>
        <div v-else class="content" v-html="renderMarkdown(result.lop_1_chuyen_ve_anh)"></div>
        <small v-if="narrative" class="narrative-meta">✨ AI luận theo paradigm đọc đồng dạng — mệnh 7 phần, người 3 phần · bám {{ result.metadata.atoms_pulled }} trích sách</small>
      </section>

      <!-- Món chính: luận theo CHỦ ĐỀ ĐỜI SỐNG — bấm món nào nấu món đó -->
      <section class="mon-chinh">
        <h3>🍽️ Luận sâu theo chủ đề</h3>
        <p class="mc-hint">Chọn một mảng đời anh muốn nghe kỹ — thầy sẽ luận riêng từng món.</p>
        <div class="mc-cards">
          <button v-for="m in chuDeList" :key="m.slug"
                  :class="['mc-card', { active: chuDeActive === m.slug }]"
                  :disabled="chuDeLoading"
                  @click="loadChuDe(m.slug)">
            <span class="mc-icon">{{ m.icon }}</span>
            <span class="mc-ten">{{ m.ten }}</span>
          </button>
        </div>
        <div v-if="chuDeLoading" class="content narrative-loading">
          ✍️ Đang luận món "{{ chuDeTen }}" từ kho sách... (10-15 giây)
        </div>
        <div v-else-if="chuDeText" class="content narrative-text mc-text" v-html="renderMarkdown(chuDeText)"></div>
        <small v-if="chuDeText" class="narrative-meta">✨ Luận gộp các mảng liên quan — mệnh là động từ: cấu trúc này vận hành mạnh nhất khi anh chủ động</small>

        <!-- Bài đọc DETERMINISTIC: Con cái (phương pháp nam-đẩu/bắc-đẩu cổ điển) -->
        <div v-if="tuTucReading" class="mc-det-card">
          <h5>🍼 Con cái — đọc theo sao cổ điển</h5>
          <ul>
            <li><b>Giới tính (xu hướng):</b> {{ tuTucReading.gioi_tinh_con.xu_huong }}<br>
              <small>{{ tuTucReading.gioi_tinh_con.ly_do }}</small></li>
            <li><b>Số con (xu hướng):</b> {{ tuTucReading.so_con.xu_huong }}<br>
              <small>{{ (tuTucReading.so_con.yeu_to || []).join('; ') }}</small></li>
            <li v-if="tuTucReading.phuc_con && tuTucReading.phuc_con.co"><b>Phúc con:</b> {{ tuTucReading.phuc_con.mo_ta }}</li>
          </ul>
          <p class="mc-det-caveat">⚖ {{ tuTucReading.caveat }}</p>
        </div>

        <!-- Bài đọc DETERMINISTIC: Tình duyên (đào hoa-cấu-trúc / độc thân / duyên xa) -->
        <div v-if="phuTheSignals" class="mc-det-card">
          <h5>💞 Tín hiệu tình duyên — đọc cấu trúc</h5>
          <ul>
            <li v-if="phuTheSignals.dao_hoa_field">
              <b>Trường đào hoa ({{ phuTheSignals.dao_hoa_field.muc }}):</b> {{ phuTheSignals.dao_hoa_field.mo_ta }}<br>
              <small>→ {{ phuTheSignals.dao_hoa_field.hanh_dong }}</small></li>
            <li><b>Duyên đến muộn / độc thân:</b> {{ phuTheSignals.doc_than_risk.muc }}
              <small v-if="(phuTheSignals.doc_than_risk.yeu_to || []).length">({{ phuTheSignals.doc_than_risk.yeu_to.join('; ') }})</small></li>
            <li v-if="phuTheSignals.duyen_xa"><b>Duyên xa:</b> {{ phuTheSignals.duyen_xa.mo_ta }}</li>
          </ul>
          <p class="mc-det-caveat">⚖ {{ phuTheSignals.caveat }}</p>
        </div>

        <!-- Sau khi nghe món tổng quan: 2 hành động đào sâu + soi mình -->
        <div v-if="chuDeText && !chuDeLoading" class="mc-actions">
          <button class="mc-deep-btn" :disabled="sauLoading" @click="loadChuDeSau(chuDeActive)">
            🔍 Đào sâu — 2 trụ kinh điển + trích nguồn
          </button>
          <button class="mc-quiz-btn" :disabled="giaViLoading" @click="loadGiaVi(chuDeActive)">
            💬 Soi mình — vài câu hỏi để thầy hiểu anh hơn
          </button>
        </div>

        <!-- Món sâu: bài 2 trụ + bảng xuất xứ nguyên liệu -->
        <div v-if="sauLoading" class="content narrative-loading">📚 Đang mở kho sách 2 trụ, đối chiếu Trung Châu × Trần Đoàn... (15-20 giây)</div>
        <p v-else-if="sauErr" class="mc-sau-err">{{ sauErr }} <button class="mc-deep-btn" @click="loadChuDeSau(chuDeActive)">Thử lại</button></p>
        <div v-else-if="sauText" class="mc-sau">
          <div class="content narrative-text mc-text" v-html="renderMarkdown(sauText)"></div>
          <details v-if="sauNguyenLieu.length" class="mc-nguyenlieu">
            <summary>📜 Xuất xứ nguyên liệu ({{ sauNguyenLieu.length }} sao — sách & trang)</summary>
            <div v-for="(n, i) in sauNguyenLieu" :key="i" class="nl-row">
              <strong>{{ n.sao_vi }} @ {{ n.cung_vi }}</strong>
              <span :class="['nl-badge', n.hoi_tu ? 'hoi' : 'don']">{{ n.hoi_tu ? '🟢 2 trụ hội tụ' : '⚪ 1 trụ' }}</span>
              <ul><li v-for="(src, j) in n.nguon" :key="j">{{ src }}</li></ul>
            </div>
          </details>
        </div>

        <!-- Soi mình: câu hỏi gia vị → lưu phản hồi -->
        <div v-if="giaViLoading" class="content narrative-loading">💭 Đang chuẩn bị vài câu hỏi...</div>
        <div v-else-if="giaViList.length" class="mc-quiz">
          <p class="quiz-hint">Trả lời giúp thầy biết đúng/sai để lần sau luận chuẩn hơn cho riêng anh:</p>
          <div v-for="(q, i) in giaViList" :key="i" class="quiz-row" :class="{ done: feedbackSent[q.atom_id] }">
            <div class="quiz-q">{{ q.cau_hoi }}</div>
            <div v-if="!feedbackSent[q.atom_id]" class="quiz-opts">
              <button @click="sendFeedback(q, 'dung')">Đúng</button>
              <button @click="sendFeedback(q, 'chua')">Chưa rõ</button>
              <button @click="sendFeedback(q, 'khong')">Không</button>
            </div>
            <div v-else class="quiz-thanks">✓ Cảm ơn anh — đã ghi nhận</div>
          </div>
          <div class="quiz-tn">
            <textarea v-model="traiNghiem" placeholder="Anh muốn kể thêm trải nghiệm của mình? (công việc, biến cố, điều đang trăn trở...) — thầy sẽ nhớ để luận sát hơn" rows="2"></textarea>
            <button :disabled="!traiNghiem.trim()" @click="sendTraiNghiem">Gửi</button>
          </div>
          <p v-if="feedbackNeedLogin" class="quiz-login">💡 Đăng nhập để thầy lưu phản hồi và nhớ anh giữa các lần xem.</p>
        </div>
      </section>

      <!-- Góc nhìn phái Thiên Lương (đọc tuổi trước sao, Thái Tuế chủ đạo) -->
      <section v-if="thienLuong" class="thien-luong">
        <h3>🌿 Góc nhìn phái Thiên Lương <small>(đọc tuổi trước sao · Thái Tuế = chánh danh)</small></h3>
        <div class="tl-row"><b>Bậc tuổi:</b> bậc {{ thienLuong.bac_tuoi.bac }} — {{ thienLuong.bac_tuoi.quan_he }} ({{ thienLuong.bac_tuoi.can }}{{ thienLuong.bac_tuoi.chi }}): {{ thienLuong.bac_tuoi.y_nghia }}</div>
        <div class="tl-row"><b>Tư cách (vòng Thái Tuế):</b> Mệnh = <em>{{ thienLuong.tu_cach_menh.vong }}</em> · Thân = <em>{{ thienLuong.tu_cach_than.vong }}</em>
          <div class="tl-sub">{{ thienLuong.tu_cach_menh.mo_ta }}</div></div>
        <div class="tl-row"><b>Âm dương Mệnh:</b> {{ thienLuong.am_duong_menh.nhan_dinh }}</div>
        <div class="tl-row"><b>Đức bản mệnh:</b> {{ thienLuong.duc_ban_menh }}</div>
        <div v-if="thienLuong.dong_luc_doi_nguoi" class="tl-row"><b>Động lực đời:</b> {{ thienLuong.dong_luc_doi_nguoi }}</div>
        <small class="tl-note">{{ thienLuong.tong_chi }}</small>
      </section>

      <!-- Lớp 2: Vì sao -->
      <section class="lop-2">
        <h3>💡 Lớp 2 — Vì sao</h3>
        <div class="content" v-html="renderMarkdown(result.lop_2_vi_sao)"></div>

        <!-- Paradigm warnings detail -->
        <div class="warnings">
          <h4>Cảnh báo paradigm</h4>
          <div v-for="(w, i) in result.warnings" :key="i" :class="['warning', `severity-${w.severity}`]">
            <strong>[{{ w.type }}]</strong> {{ w.msg }}
            <div v-if="w.citation" class="citation">📜 {{ w.citation }}</div>
          </div>
        </div>
      </section>

      <!-- Lớp 3: Sách cổ nói — DẪN CHỨNG, ẩn mặc định (atoms thô) -->
      <section class="lop-3">
        <h3>📚 Dẫn chứng từ sách cổ</h3>

        <!-- Điểm nổi bật toàn lá (engine quét — luôn hiện trước) -->
        <div v-if="highlights.length" class="hl-section">
          <h4>⭐ Điểm nổi bật nhất lá số</h4>
          <div v-for="(h, i) in highlights" :key="i" class="hl-row">
            <span class="hl-vitri">{{ h.vi_tri }}</span>
            <span class="hl-mota">{{ h.mo_ta }}</span>
          </div>
        </div>

        <!-- Tóm tắt + tên cách cục (luôn hiện, súc tích) -->
        <div v-if="cachCucNamed.length" class="cc-summary">
          🏆 Cách cục trong lá số:
          <span v-for="cc in cachCucNamed" :key="cc.slug" :class="['cc-chip', cc.loai]">{{ cc.ten }}</span>
        </div>

        <!-- Tứ Hóa năm sinh (trục động — luôn hiện) -->
        <div v-if="tuHoa.length" class="tu-hoa-bar">
          <span v-for="t in tuHoa" :key="t.hoa" :class="['tu-hoa-chip', t.hoa]">
            {{ formatStar(t.hoa) }}: {{ formatStar(t.star) }} ({{ formatFn(t.palace_fn) || formatPalace(t.palace_chi) }})
          </span>
        </div>

        <!-- Bộ phụ tinh theo cặp + thế (luôn hiện — Anh quan tâm) -->
        <div v-if="boPhuTinhList.length" class="bo-pt-section">
          <h4>✦ Bộ phụ tinh — xem theo CẶP + THẾ</h4>
          <p class="to-hop-hint">Phụ tinh không xem lẻ: ghép thành bộ (cặp sao) và xét thế với cung — đồng cung / giáp (kẹp) / hội chiếu / xung chiếu.</p>
          <div v-for="row in boPhuTinhList" :key="row.chi" class="bo-pt-cung">
            <strong>🏛 {{ formatPalace(row.chi) }}:</strong>
            <span v-for="b in row.bos" :key="b.slug" :class="['bo-pt-chip', b.loai]" :title="b.the_vi + (b.du_cap ? ' · đủ cặp' : ' · lẻ')">
              <img v-if="boPhuTinhImage(b)" :src="boPhuTinhImage(b)" :alt="`Ảnh ${b.ten}`" loading="lazy" />
              {{ b.ten }} <em>{{ b.the_vi }}</em>{{ b.du_cap ? '' : '*' }}
            </span>
          </div>
          <p class="bo-pt-note">* = bộ lẻ (chỉ 1 sao có thế). Màu: <span class="bo-pt-chip sat">sát</span> <span class="bo-pt-chip hung">hung</span> <span class="bo-pt-chip cat">cát</span> <span class="bo-pt-chip dao_hoa">đào hoa</span></p>
        </div>

        <button class="atoms-toggle" @click="showAtoms = !showAtoms">
          {{ showAtoms ? '▲ Thu gọn dẫn chứng' : `📖 Xem dẫn chứng chi tiết từ sách (${result.metadata.atoms_pulled} trích dẫn, 5 hệ phái)` }}
        </button>

        <div v-show="showAtoms">
        <div class="schools-legend">
          <span v-for="(name, code) in result.lop_3_sach_co.schools_summary" :key="code" class="school-tag">
            {{ name }}
          </span>
        </div>

        <!-- Đại vận hiện tại (BIẾN) -->
        <div v-if="daiVan" class="dai-van-section">
          <h4>🧭 Đại vận hiện tại — vận {{ daiVan.cycle_index }} (tuổi {{ daiVan.start_age }}–{{ daiVan.end_age }}), cung {{ formatPalace(daiVan.chi) }}</h4>
          <p class="to-hop-hint">Cung đại vận luận như Mệnh tạm 10 năm. {{ daiVan.citation }}</p>
          <p v-if="daiVan.vo_chinh_dieu" class="to-hop-hint">↪ Cung vận vô chính diệu — mượn sao đối cung: {{ (daiVan.stars || []).map(formatStar).join(', ') }}</p>
          <div v-for="(cv, star) in (daiVan.cross_views || {})" :key="'dv-' + star" class="star-block">
            <h5>⭐ {{ formatStar(star) }} (tọa cung vận)
              <span v-if="cv.mieu_ham" :class="['mh-badge', mhClass(cv.mieu_ham)]">{{ cv.mieu_ham }} tại cung vận</span>
              <span class="badge">{{ cv.total_atoms }} atoms</span>
            </h5>
            <template v-for="(atoms, school) in cv.schools" :key="school">
            <div v-if="atoms && atoms.length > 0" class="school-view">
              <strong class="school-name">{{ result.lop_3_sach_co.schools_summary[school] }}:</strong>
              <ul>
                <li v-for="atom in atoms" :key="atom.atom_id" class="atom">
                  <div class="quote" v-html="'&quot;' + annotateTerms(atom.source_quote) + '&quot;'"></div>
                  <div v-if="atom.viet_thuan" class="paraphrase" v-html="'→ ' + annotateTerms(atom.viet_thuan)"></div>
                  <div class="meta">📍 trang {{ atom.page_start }} · confidence {{ atom.confidence }}</div>
                </li>
              </ul>
            </div>
            </template>
          </div>
        </div>

        <!-- Cách cục có tên riêng — máy match điều kiện chính xác -->
        <div v-if="cachCucNamed.length" class="cc-named-section">
          <h4>🏆 Cách cục có tên trong lá số</h4>
          <div v-for="cc in cachCucNamed" :key="cc.slug" class="cc-named-block">
            <h5>
              <span :class="['cc-loai', cc.loai]">{{ cc.loai === 'cat' ? 'CÁT' : cc.loai === 'hung' ? 'HUNG' : 'TÙY HÓA' }}</span>
              {{ cc.ten }}
              <span class="badge">{{ cc.total_atoms }} atoms</span>
            </h5>
            <p class="cc-dieu-kien">{{ cc.dieu_kien }}</p>
            <template v-for="(atoms, school) in cc.schools" :key="school">
            <div v-if="atoms && atoms.length > 0" class="school-view">
              <strong class="school-name">{{ result.lop_3_sach_co.schools_summary[school] }}:</strong>
              <ul>
                <li v-for="atom in atoms" :key="atom.atom_id" class="atom">
                  <div class="quote" v-html="'&quot;' + annotateTerms(atom.source_quote) + '&quot;'"></div>
                  <div v-if="atom.viet_thuan" class="paraphrase" v-html="'→ ' + annotateTerms(atom.viet_thuan)"></div>
                  <div class="meta">📍 trang {{ atom.page_start }}</div>
                </li>
              </ul>
            </div>
            </template>
          </div>
        </div>

        <!-- Tổ hợp cung: tam phương tứ chính / giáp / mượn sao (chống "luận máy móc" — Trung Châu) -->
        <div v-if="toHopList.length" class="to-hop-section">
          <h4>🔗 Tổ hợp cung — tam phương tứ chính · giáp · mượn sao</h4>
          <p class="to-hop-hint">Trung Châu dạy: chỉ xét 1 cung đơn lẻ = "luận đoán máy móc". Phần này gom sao hội chiếu từ tam hợp + xung chiếu rồi đối chiếu sách.</p>
          <div v-for="th in toHopList" :key="th.cung" class="to-hop-block">
            <h5>🏛 Cung {{ formatPalace(th.cung) }}
              <span class="badge">{{ th.total_atoms }} atoms tổ hợp</span>
            </h5>
            <div class="to-hop-meta">
              Tứ chính: {{ th.to_hop.tu_chinh.tu_chinh.map(formatPalace).join(' · ') }}
              — hội chiếu: {{ th.to_hop.hoi_chieu_stars.map(formatStar).join(', ') }}
              <template v-if="th.to_hop.muon_sao.vo_chinh_dieu && th.to_hop.muon_sao.borrowed_from">
                <br>↪ Vô chính diệu — mượn sao từ {{ formatPalace(th.to_hop.muon_sao.borrowed_from) }}:
                {{ th.to_hop.muon_sao.stars.map(formatStar).join(', ') }}
              </template>
              <template v-if="th.to_hop.giap.thien_tuong_note">
                <br>⚠ {{ th.to_hop.giap.thien_tuong_note }}
              </template>
            </div>
            <template v-for="(atoms, school) in th.schools" :key="school">
            <div v-if="atoms && atoms.length > 0" class="school-view">
              <strong class="school-name">{{ result.lop_3_sach_co.schools_summary[school] }}:</strong>
              <ul>
                <li v-for="atom in atoms" :key="atom.atom_id" class="atom">
                  <span v-for="rel in (atom.relations || [])" :key="rel" class="rel-tag">{{ formatRelation(rel) }}</span>
                  <div class="quote" v-html="'&quot;' + annotateTerms(atom.source_quote) + '&quot;'"></div>
                  <div v-if="atom.viet_thuan" class="paraphrase" v-html="'→ ' + annotateTerms(atom.viet_thuan)"></div>
                  <div class="meta">📍 trang {{ atom.page_start }} · confidence {{ atom.confidence }}</div>
                </li>
              </ul>
            </div>
            </template>
          </div>
        </div>

        <div v-for="(palace_data, palace) in result.lop_3_sach_co.per_palace" :key="palace" class="palace-block">
          <h4>🏛 Cung {{ formatPalace(palace) }}</h4>
          <div v-for="(cv, star) in palace_data.cross_views" :key="star" class="star-block">
            <h5>⭐ {{ formatStar(star) }}
              <span v-if="cv.mieu_ham" :class="['mh-badge', mhClass(cv.mieu_ham)]">{{ cv.mieu_ham }}</span>
              <span class="badge">{{ cv.total_atoms }} atoms</span>
            </h5>
            <template v-for="(atoms, school) in cv.schools" :key="school">
            <div v-if="atoms && atoms.length > 0" class="school-view">
              <strong class="school-name">{{ result.lop_3_sach_co.schools_summary[school] }}:</strong>
              <ul>
                <li v-for="atom in atoms" :key="atom.atom_id" :class="['atom', { 'atom-lech': atom.dieu_kien_khop === false }]">
                  <div v-if="atom.dieu_kien_note" class="dieu-kien-note">⚠ {{ atom.dieu_kien_note }}</div>
                  <div class="quote" v-html="'&quot;' + annotateTerms(atom.source_quote) + '&quot;'"></div>
                  <div v-if="atom.viet_thuan" class="paraphrase" v-html="'→ ' + annotateTerms(atom.viet_thuan)"></div>
                  <div class="meta">📍 trang {{ atom.page_start }} · confidence {{ atom.confidence }}</div>
                </li>
              </ul>
            </div>
            </template>
          </div>

          <!-- Phụ tinh / sát tinh / Tứ Hóa cùng cung -->
          <div v-for="(cv, star) in (palace_data.phu_tinh_views || {})" :key="'pt-' + star" class="star-block phu-tinh-block">
            <h5>✦ {{ formatStar(star) }} <span class="badge badge-phu">{{ cv.total_atoms }} atoms phụ tinh</span></h5>
            <template v-for="(atoms, school) in cv.schools" :key="school">
            <div v-if="atoms && atoms.length > 0" class="school-view">
              <strong class="school-name">{{ result.lop_3_sach_co.schools_summary[school] }}:</strong>
              <ul>
                <li v-for="atom in atoms" :key="atom.atom_id" class="atom">
                  <div class="quote" v-html="'&quot;' + annotateTerms(atom.source_quote) + '&quot;'"></div>
                  <div v-if="atom.viet_thuan" class="paraphrase" v-html="'→ ' + annotateTerms(atom.viet_thuan)"></div>
                  <div class="meta">📍 trang {{ atom.page_start }} · confidence {{ atom.confidence }}</div>
                </li>
              </ul>
            </div>
            </template>
          </div>
        </div>
        </div><!-- /v-show showAtoms -->
      </section>

      <!-- Metadata footer -->
      <footer class="metadata">
        <p>📊 {{ result.metadata.atoms_pulled }} atoms pulled từ {{ result.metadata.schools_count }} hệ phái</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { renderMarkdown, escapeHtml } from '../utils/tuviMarkdown.js'  // XSS-safe (escape-first)

const props = defineProps({
  // "1988-06-05T23:30" — nếu có thì gọi from-birth, không thì founder-demo
  birthDatetimeLocal: { type: String, default: null },
  timezone: { type: String, default: 'Asia/Ho_Chi_Minh' },
  gender: { type: String, default: 'nam' },
})

const loading = ref(true)
const error = ref(null)
const result = ref(null)
const narrative = ref(null)
const narrativeLoading = ref(false)
const showAtoms = ref(false)  // dẫn chứng thô ẩn mặc định — atoms là hậu trường

// Góc nhìn Thiên Lương (lazy theo lá số)
const thienLuong = ref(null)
async function loadThienLuong() {
  if (!props.birthDatetimeLocal) return
  try {
    const r = await fetch('/api/tu-vi/thien-luong', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ birth: props.birthDatetimeLocal, gender: props.gender }),
    })
    const d = await r.json()
    if (!d.error) thienLuong.value = d
  } catch { /* để trống nếu lỗi */ }
}

// Món chính theo chủ đề
const chuDeList = ref([])
const chuDeActive = ref(null)
const chuDeText = ref(null)
const chuDeTen = ref('')
const chuDeLoading = ref(false)
const tuTucReading = ref(null)    // bài đọc Con Cái deterministic (Gia đạo)
const phuTheSignals = ref(null)   // tín hiệu Tình Duyên deterministic
const chuDeCache = {}  // slug → {narrative, tuTuc, phuThe} đã luận (đỡ gọi lại trong phiên)

async function loadChuDeList() {
  try {
    const res = await fetch('/api/tu-vi/3-layer/chu-de')
    const data = await res.json()
    chuDeList.value = data.chu_de || []
  } catch { /* để trống nếu lỗi */ }
}

// Món sâu 2 trụ + xuất xứ
const sauText = ref(null)
const sauErr = ref('')
const sauNguyenLieu = ref([])
const sauLoading = ref(false)
const sauCache = {}
// Gia vị: câu hỏi soi mình + phản hồi
const giaViList = ref([])
const giaViLoading = ref(false)
const giaViCache = {}
const feedbackSent = ref({})
const feedbackNeedLogin = ref(false)
const traiNghiem = ref('')

function _birthBody(extra) {
  return JSON.stringify({
    birth_datetime_local: props.birthDatetimeLocal,
    timezone: props.timezone, gender: props.gender, ...extra,
  })
}

async function loadChuDeSau(slug) {
  if (!props.birthDatetimeLocal || !slug) return
  if (sauCache[slug]) { sauText.value = sauCache[slug].t; sauNguyenLieu.value = sauCache[slug].n; return }
  sauLoading.value = true; sauText.value = null; sauNguyenLieu.value = []; sauErr.value = ''
  try {
    const res = await fetch('/api/tu-vi/3-layer/chu-de-sau', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: _birthBody({ chu_de: slug }),
    })
    const data = await res.json()
    if (data.narrative) {
      sauText.value = data.narrative; sauNguyenLieu.value = data.nguyen_lieu || []
      sauCache[slug] = { t: data.narrative, n: sauNguyenLieu.value }
    } else {
      sauErr.value = data.error || 'Chưa luận sâu được, anh thử lại sau giây lát.'
    }
  } catch { sauErr.value = 'Lỗi kết nối, thử lại.' } finally { sauLoading.value = false }
}

async function loadGiaVi(slug) {
  if (!props.birthDatetimeLocal || !slug) return
  if (giaViCache[slug]) { giaViList.value = giaViCache[slug]; return }
  giaViLoading.value = true; giaViList.value = []
  try {
    const res = await fetch('/api/tu-vi/3-layer/gia-vi', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: _birthBody({ chu_de: slug }),
    })
    const data = await res.json()
    giaViList.value = data.cau_hoi || []; giaViCache[slug] = giaViList.value
  } catch { /* lỗi */ } finally { giaViLoading.value = false }
}

async function sendFeedback(q, answer) {
  try {
    const res = await fetch('/api/tu-vi/3-layer/feedback', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chu_de: chuDeActive.value, atom_id: q.atom_id, sao: q.sao_vi, cau_hoi: q.cau_hoi, answer }),
    })
    if (res.status === 401) { feedbackNeedLogin.value = true; return }
    feedbackSent.value = { ...feedbackSent.value, [q.atom_id]: answer }
  } catch { /* lỗi mạng */ }
}

async function sendTraiNghiem() {
  if (!traiNghiem.value.trim()) return
  try {
    const res = await fetch('/api/tu-vi/3-layer/feedback', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chu_de: chuDeActive.value, free_text: traiNghiem.value.trim() }),
    })
    if (res.status === 401) { feedbackNeedLogin.value = true; return }
    traiNghiem.value = ''
  } catch { /* lỗi */ }
}

async function loadChuDe(slug) {
  if (!props.birthDatetimeLocal) return
  chuDeActive.value = slug
  const m = chuDeList.value.find(x => x.slug === slug)
  chuDeTen.value = m ? m.ten : ''
  // reset món sâu + gia vị khi đổi món
  sauText.value = null; sauNguyenLieu.value = []; giaViList.value = []
  feedbackSent.value = {}; feedbackNeedLogin.value = false; traiNghiem.value = ''
  tuTucReading.value = null; phuTheSignals.value = null
  if (chuDeCache[slug]) {
    const c = chuDeCache[slug]
    chuDeText.value = c.narrative; tuTucReading.value = c.tuTuc; phuTheSignals.value = c.phuThe
    return
  }
  chuDeLoading.value = true
  chuDeText.value = null
  try {
    const res = await fetch('/api/tu-vi/3-layer/chu-de', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        birth_datetime_local: props.birthDatetimeLocal,
        timezone: props.timezone,
        gender: props.gender,
        chu_de: slug,
      }),
    })
    const data = await res.json()
    // Bài đọc deterministic hiện độc lập với narrative LLM (kể cả khi LLM lỗi/rate-limit).
    tuTucReading.value = data.tu_tuc_reading || null
    phuTheSignals.value = data.phu_the_signals || null
    if (data.narrative) chuDeText.value = data.narrative
    if (data.narrative || tuTucReading.value || phuTheSignals.value) {
      chuDeCache[slug] = { narrative: data.narrative || null, tuTuc: tuTucReading.value, phuThe: phuTheSignals.value }
    }
  } catch { /* lỗi → để trống */ } finally {
    chuDeLoading.value = false
  }
}

async function loadNarrative() {
  if (!props.birthDatetimeLocal) return
  narrativeLoading.value = true
  try {
    const res = await fetch('/api/tu-vi/3-layer/narrative', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        birth_datetime_local: props.birthDatetimeLocal,
        timezone: props.timezone,
        gender: props.gender,
        force: !!narrative.value,  // đã có → user bấm lại = viết lại
      }),
    })
    const data = await res.json()
    if (data.narrative) narrative.value = data.narrative
  } catch { /* giữ template nếu lỗi */ } finally {
    narrativeLoading.value = false
  }
}

const PALACE_NAMES = {
  ty: 'Tý', suu: 'Sửu', dan: 'Dần', mao: 'Mão', thin: 'Thìn', ti: 'Tỵ',
  ngo: 'Ngọ', mui: 'Mùi', than: 'Thân', dau: 'Dậu', tuat: 'Tuất', hoi: 'Hợi',
}

const STAR_NAMES = {
  tu_vi: 'Tử Vi', thien_co: 'Thiên Cơ', thai_duong: 'Thái Dương',
  vu_khuc: 'Vũ Khúc', thien_dong: 'Thiên Đồng', liem_trinh: 'Liêm Trinh',
  thien_phu: 'Thiên Phủ', thai_am: 'Thái Âm', tham_lang: 'Tham Lang',
  cu_mon: 'Cự Môn', thien_tuong: 'Thiên Tướng', thien_luong: 'Thiên Lương',
  that_sat: 'Thất Sát', pha_quan: 'Phá Quân',
  // Phụ tinh + sát tinh + Tứ Hóa
  ta_phu: 'Tả Phụ', huu_bat: 'Hữu Bật', van_xuong: 'Văn Xương', van_khuc: 'Văn Khúc',
  thien_khoi: 'Thiên Khôi', thien_viet: 'Thiên Việt',
  kinh_duong: 'Kình Dương', da_la: 'Đà La', hoa_tinh: 'Hỏa Tinh', linh_tinh: 'Linh Tinh',
  dia_khong: 'Địa Không', dia_kiep: 'Địa Kiếp', loc_ton: 'Lộc Tồn',
  hoa_loc: 'Hóa Lộc', hoa_quyen: 'Hóa Quyền', hoa_khoa: 'Hóa Khoa', hoa_ky: 'Hóa Kỵ',
}

const FN_NAMES = {
  menh: 'Mệnh', huynh_de: 'Huynh Đệ', phu_the: 'Phu Thê', tu_tuc: 'Tử Tức',
  tai_bach: 'Tài Bạch', tat_ach: 'Tật Ách', thien_di: 'Thiên Di', no_boc: 'Nô Bộc',
  quan_loc: 'Quan Lộc', dien_trach: 'Điền Trạch', phuc_duc: 'Phúc Đức', phu_mau: 'Phụ Mẫu',
}

function formatFn(f) {
  return f ? (FN_NAMES[f] || f) : null
}

const tuHoa = computed(() => result.value?.la_so_input?.tu_hoa || [])
const cachCucNamed = computed(() => result.value?.lop_3_sach_co?.cach_cuc_named || [])
const highlights = computed(() => result.value?.highlights || [])
// Bộ phụ tinh: chỉ hiện cung có bộ ĐÁNG KỂ (đủ cặp, hoặc sát/hung)
const boPhuTinhList = computed(() => {
  const all = result.value?.lop_3_sach_co?.bo_phu_tinh_per_palace || {}
  const rows = []
  for (const [chi, bos] of Object.entries(all)) {
    const keep = (bos || []).filter(b => b.du_cap || b.loai === 'sat' || b.loai === 'hung')
    if (keep.length) rows.push({ chi, bos: keep })
  }
  return rows
})
const daiVan = computed(() => result.value?.lop_3_sach_co?.dai_van_hien_tai || null)

const BO_PHU_TINH_ART = {
  'kinh_da:giap': '/oracle-cards/tu-vi/web_ready/170-kinh-da-giap-cung.webp',
  'ta_huu:hoi_chieu': '/oracle-cards/tu-vi/web_ready/171-ta-huu-hoi-chieu.webp',
  'xuong_khuc:dong_cung': '/oracle-cards/tu-vi/web_ready/172-xuong-khuc-dong-cung.webp',
  'khong_kiep:xung_chieu': '/oracle-cards/tu-vi/web_ready/173-khong-kiep-xung-chieu.webp',
  'loc_ma:dong_cung': '/oracle-cards/tu-vi/web_ready/174-loc-ma-dong-hoi.webp',
  'loc_ma:hoi_chieu': '/oracle-cards/tu-vi/web_ready/174-loc-ma-dong-hoi.webp',
  'hoa_linh:dong_cung': '/oracle-cards/tu-vi/web_ready/175-hoa-linh-kich-phat.webp',
  'hoa_linh:giap': '/oracle-cards/tu-vi/web_ready/175-hoa-linh-kich-phat.webp',
  'hoa_linh:xung_chieu': '/oracle-cards/tu-vi/web_ready/175-hoa-linh-kich-phat.webp',
  'hoa_linh:hoi_chieu': '/oracle-cards/tu-vi/web_ready/175-hoa-linh-kich-phat.webp',
}

function boPhuTinhImage(b) {
  return BO_PHU_TINH_ART[`${b?.slug}:${b?.the}`] || null
}

function formatPalace(p) {
  return PALACE_NAMES[p] || p
}

function formatStar(s) {
  return STAR_NAMES[s] || s
}

const RELATION_NAMES = {
  tam_phuong: 'Tam phương tứ chính', tam_hop: 'Tam hợp', hoi_chieu: 'Hội chiếu',
  xung_chieu: 'Xung chiếu', giap: 'Giáp cung', muon_sao: 'Mượn sao',
}

function formatRelation(r) {
  return RELATION_NAMES[r] || r
}

function mhClass(level) {
  if (!level) return ''
  if (level.includes('miếu') || level.includes('vượng') || level.includes('đắc')) return 'mh-good'
  if (level.includes('hãm') || level.includes('lạc')) return 'mh-bad'
  return 'mh-mid'
}

// Tổ hợp cung — chỉ lấy cung có atoms, ưu tiên Mệnh/Thân trước
const toHopList = computed(() => {
  const all = result.value?.lop_3_sach_co?.to_hop_per_palace || {}
  return Object.values(all).filter(v => v.total_atoms > 0)
})

// ── Wiki glossary tooltip (Hán-Việt) ──────────────────────────────
const glossaryTerms = ref({})  // term → note

async function loadGlossary() {
  try {
    // Full glossary từ wiki concept_index (787+ concepts) — wiki = glossary layer
    const res = await fetch('/api/yi-wiki/glossary/tu-vi-full')
    const data = await res.json()
    const flat = {}
    for (const [term, info] of Object.entries(data.terms || {})) {
      if (info?.note) {
        flat[term] = info.note
        for (const alias of (info.aliases || [])) flat[alias] = info.note
      }
    }
    glossaryTerms.value = flat
  } catch { /* glossary optional — bỏ qua nếu lỗi */ }
}

let _termRegex = null  // cached alternation regex — rebuild khi glossary đổi

function buildTermRegex() {
  const terms = Object.keys(glossaryTerms.value)
  if (!terms.length) return null
  // Sort dài trước để match "Tuần Không Vong" trước "Tuần"; 1 regex gộp = 1 pass/text
  terms.sort((a, b) => b.length - a.length)
  const escaped = terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  return new RegExp(`(${escaped.join('|')})`, 'g')
}

function annotateTerms(text) {
  const html = escapeHtml(text)
  if (!_termRegex) _termRegex = buildTermRegex()
  if (!_termRegex) return html
  return html.replace(_termRegex, (m) => {
    const note = escapeHtml(glossaryTerms.value[m] || '')
    return note ? `<span class="hv-term" title="${note}">${m}</span>` : m
  })
}

async function load() {
  loading.value = true
  error.value = null
  try {
    let res
    if (props.birthDatetimeLocal) {
      res = await fetch('/api/tu-vi/3-layer/from-birth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          birth_datetime_local: props.birthDatetimeLocal,
          timezone: props.timezone,
          gender: props.gender,
        }),
      })
    } else {
      res = await fetch('/api/tu-vi/3-layer/founder-demo')
    }
    const data = await res.json()
    if (data.detail) throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
    result.value = data
    narrative.value = null  // reset khi đổi lá số
    // Reset món chính khi đổi lá số (cache theo phiên giữ riêng, nhưng UI về trạng thái chọn)
    chuDeActive.value = null; chuDeText.value = null
    Object.keys(chuDeCache).forEach(k => delete chuDeCache[k])
    thienLuong.value = null
    // Bài luận mượt là MẶC ĐỊNH — tự chạy ngay sau khi có lá số
    if (props.birthDatetimeLocal) { loadNarrative(); loadThienLuong() }
  } catch (e) {
    error.value = `Lỗi: ${e.message}`
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadGlossary(); loadChuDeList(); load(); })
watch(() => props.birthDatetimeLocal, load)
</script>

<style scoped>
/* Theme-aware: dùng --read-* tokens (tự đổi sáng/tối) — KHÔNG hardcode nền/chữ */
.tu-vi-3layer-panel {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  line-height: 1.6;
  color: var(--read-text);
}

h2 {
  color: var(--read-heading);
  border-bottom: 2px solid var(--read-rule);
  padding-bottom: 8px;
}
h3, h4, h5 { color: var(--read-heading); }

section {
  margin: 32px 0;
  padding: 20px;
  border-radius: 8px;
  background: var(--read-surface);
  border: 1px solid var(--read-border);
}

.lop-1 { border-left: 4px solid #f4a261; }
.lop-2 { border-left: 4px solid #2a9d8f; }
.lop-3 { border-left: 4px solid #8a6fc2; }

h3 { margin-top: 0; }

.warnings {
  margin-top: 16px;
  padding: 12px;
  background: var(--read-bg-soft);
  border-radius: 6px;
}

.warning {
  margin: 8px 0;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid var(--read-border);
}
.warning.severity-info { background: rgba(42, 157, 143, 0.14); border-left-color: #2a9d8f; }
.warning.severity-warning { background: rgba(244, 162, 97, 0.16); border-left-color: #f4a261; }
.warning.severity-danger { background: rgba(217, 83, 79, 0.16); border-left-color: #d9534f; }
.warning.severity-neutral { background: var(--read-bg-soft); }

.citation { font-size: 0.85em; color: var(--read-text-dim); margin-top: 4px; }

.schools-legend {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.school-tag {
  padding: 4px 12px;
  background: #6a4c93;
  color: #fff;
  border-radius: 12px;
  font-size: 0.85em;
}

.palace-block {
  margin: 20px 0;
  padding: 12px;
  background: var(--read-bg-soft);
  border-radius: 6px;
}

.star-block {
  margin: 16px 0;
  padding-left: 12px;
  border-left: 2px solid var(--read-border);
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  background: #6a4c93;
  color: #fff;
  border-radius: 8px;
  font-size: 0.75em;
}

.school-view {
  margin: 12px 0;
  padding: 8px 12px;
  background: var(--read-surface);
  border-radius: 4px;
  border: 1px solid var(--read-border);
}

.school-name { color: var(--read-link); }

.atom { margin: 12px 0; }

.quote {
  font-style: italic;
  background: var(--read-cite-bg);
  color: var(--read-text);
  padding: 8px;
  border-left: 3px solid var(--read-cite-accent);
}

.paraphrase {
  margin-top: 4px;
  color: var(--read-note-accent);
}

.meta {
  font-size: 0.8em;
  color: var(--read-text-faint);
  margin-top: 4px;
}

.metadata {
  margin-top: 32px;
  padding: 12px;
  background: var(--read-bg-soft);
  border-radius: 6px;
  text-align: center;
  color: var(--read-text-dim);
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 1.1em;
  color: var(--read-text);
}
.error { color: #e57373; }

:deep(.hv-term) {
  border-bottom: 1px dotted var(--read-link);
  cursor: help;
  color: var(--read-link);
}

.dai-van-section {
  margin: 20px 0;
  padding: 12px;
  background: var(--read-bg-soft);
  border-radius: 6px;
  border: 1px solid #2a9d8f;
}

.cc-named-section {
  margin: 20px 0;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #d4af37;
}
.cc-named-block { margin: 14px 0; padding-left: 12px; border-left: 2px solid #e8d48a; }
.cc-dieu-kien { font-size: 0.88em; color: #555; margin: 4px 0 8px; }
.cc-loai {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 8px;
  font-size: 0.7em;
  vertical-align: middle;
}
.cc-loai.cat { background: #e8f5e9; color: #1b5e20; }
.cc-loai.hung { background: #ffebee; color: #b71c1c; }
.cc-loai.hung_hoa_cat, .cc-loai.trung_tinh { background: #fff3e0; color: #b35900; }

.tu-hoa-bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
.tu-hoa-chip {
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 0.82em;
  background: rgba(124, 93, 191, 0.18);
  color: var(--read-text);
  border: 1px solid rgba(124, 93, 191, 0.4);
}
.tu-hoa-chip.hoa_loc { background: rgba(76, 175, 80, 0.16); border-color: rgba(76, 175, 80, 0.45); }
.tu-hoa-chip.hoa_quyen { background: rgba(255, 152, 0, 0.16); border-color: rgba(255, 152, 0, 0.45); }
.tu-hoa-chip.hoa_khoa { background: rgba(33, 150, 243, 0.16); border-color: rgba(33, 150, 243, 0.45); }
.tu-hoa-chip.hoa_ky { background: rgba(229, 57, 53, 0.16); border-color: rgba(229, 57, 53, 0.45); }
.phu-tinh-block { border-left-color: #8a6fc2; }
.badge-phu { background: #7e57c2; }

.mh-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 8px;
  font-size: 0.7em;
  margin-right: 6px;
  color: var(--read-text);
  border: 1px solid var(--read-border);
}
.mh-good { background: rgba(76, 175, 80, 0.18); border-color: rgba(76, 175, 80, 0.5); }
.mh-bad { background: rgba(229, 57, 53, 0.18); border-color: rgba(229, 57, 53, 0.5); }
.mh-mid { background: var(--read-bg-soft); }
.atom-lech { opacity: 0.62; }
.dieu-kien-note {
  font-size: 0.8em;
  color: var(--read-text);
  background: rgba(255, 152, 0, 0.16);
  border-left: 3px solid #f4a261;
  padding: 3px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
}

.to-hop-section {
  margin: 20px 0;
  padding: 12px;
  background: var(--read-bg-soft);
  border-radius: 6px;
  border: 1px dashed #8a6fc2;
}
.to-hop-hint { font-size: 0.85em; color: var(--read-text-dim); margin: 4px 0 12px; }
.to-hop-block { margin: 16px 0; padding-left: 12px; border-left: 2px solid var(--read-border); }
.to-hop-meta { font-size: 0.88em; color: var(--read-text-dim); margin: 6px 0 10px; }
.rel-tag {
  display: inline-block;
  margin: 0 6px 4px 0;
  padding: 1px 8px;
  background: rgba(124, 93, 191, 0.18);
  color: var(--read-text);
  border: 1px solid rgba(124, 93, 191, 0.4);
  border-radius: 8px;
  font-size: 0.72em;
}

.narrative-btn {
  float: right;
  padding: 4px 14px;
  border: 1px solid #f4a261;
  background: var(--read-surface);
  color: #f4a261;
  border-radius: 14px;
  cursor: pointer;
  font-size: 0.75em;
}
.narrative-btn:disabled { opacity: 0.6; cursor: wait; }
.narrative-text { white-space: pre-wrap; line-height: 1.8; }
.narrative-meta { display: block; margin-top: 8px; color: var(--read-text-faint); }
.narrative-loading { color: #6a4c93; font-style: italic; padding: 16px 0; }

/* Bộ phụ tinh */
.bo-pt-section { margin: 16px 0; padding: 12px; background: #fff; border-radius: 6px; border: 1px solid #b8a5d8; }
.bo-pt-cung { margin: 8px 0; line-height: 1.9; }
.bo-pt-chip {
  display: inline-flex; align-items: center; gap: 5px; margin: 2px 4px; padding: 1px 9px;
  border-radius: 10px; font-size: 0.82em;
}
.bo-pt-chip img {
  width: 20px;
  height: 28px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid rgba(106, 76, 147, 0.28);
  flex: 0 0 auto;
}
.bo-pt-chip em { font-style: normal; opacity: 0.7; font-size: 0.9em; }
.bo-pt-chip.sat { background: #ffebee; color: #b71c1c; }
.bo-pt-chip.hung { background: #fff3e0; color: #b35900; }
.bo-pt-chip.cat { background: #e8f5e9; color: #1b5e20; }
.bo-pt-chip.dao_hoa { background: #fce4ec; color: #ad1457; }
.bo-pt-note { font-size: 0.8em; color: #777; margin-top: 8px; }

/* Đảo sân khấu: dẫn chứng thô ẩn sau nút */
.atoms-toggle {
  width: 100%;
  padding: 10px 16px;
  margin: 8px 0 4px;
  border: 1px dashed #6a4c93;
  background: #faf8ff;
  color: #5a3d80;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  text-align: left;
}
.atoms-toggle:hover { background: #f0ebfa; }
.thien-luong { margin: 18px 0; padding: 16px 18px; background: #f3f9f3; border: 1px solid #c9e0c9; border-radius: 12px; }
.thien-luong h3 { margin: 0 0 10px; color: #2e7d32; }
.thien-luong h3 small { color: #6a8a6a; font-weight: 400; font-size: 0.62em; }
.tl-row { margin: 7px 0; font-size: 0.92em; color: var(--read-text,#333); line-height: 1.55; }
.tl-row b { color: #2e7d32; }
.tl-row em { color: #1b5e20; font-style: normal; font-weight: 600; }
.tl-sub { margin: 3px 0 0 8px; font-size: 0.9em; color: var(--read-text-faint,#667); }
.tl-note { display: block; margin-top: 10px; font-size: 0.8em; font-style: italic; color: var(--read-text-faint,#888); line-height: 1.5; }
.mon-chinh { margin: 18px 0; }
.mc-hint { margin: 2px 0 10px; color: var(--read-text-faint); font-size: 0.9em; }
.mc-cards { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }
.mc-card { display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 110px; padding: 12px 14px; background: var(--read-surface, #fff); border: 1.5px solid var(--read-border, #d8d8d8); border-radius: 12px; cursor: pointer; transition: all .15s; font: inherit; color: var(--read-text, #333); }
.mc-card:hover:not(:disabled) { border-color: #b8860b; transform: translateY(-2px); box-shadow: 0 3px 10px rgba(0,0,0,.08); }
.mc-card.active { border-color: #b8860b; background: #fffaf0; box-shadow: 0 2px 8px rgba(184,134,11,.18); }
.mc-card:disabled { opacity: .55; cursor: wait; }
.mc-icon { font-size: 1.6em; }
.mc-ten { font-size: 0.84em; font-weight: 500; text-align: center; line-height: 1.25; }
.mc-text { background: #fffdf7; border-left: 3px solid #b8860b; padding: 14px 16px; border-radius: 6px; }
.mc-det-card { margin: 12px 0; padding: 12px 14px; border-radius: 8px;
  background: var(--read-surface, #faf7ef); border: 1px solid var(--read-border, #e6ddc4);
  border-left: 3px solid #6b8e5a; }
.mc-det-card h5 { margin: 0 0 8px; font-size: 14px; color: var(--read-text, #3a3320); }
.mc-det-card ul { margin: 0; padding-left: 18px; }
.mc-det-card li { margin: 5px 0; color: var(--read-text, #3a3320); font-size: 13.5px; line-height: 1.5; }
.mc-det-card small { color: var(--read-text-faint, #8a7f60); }
.mc-det-caveat { margin: 8px 0 0; padding-top: 8px; border-top: 1px dashed var(--read-border, #e6ddc4);
  font-size: 12.5px; font-style: italic; color: var(--read-text-faint, #8a7f60); }
.mc-actions { display: flex; flex-wrap: wrap; gap: 10px; margin: 14px 0; }
.mc-deep-btn, .mc-quiz-btn { padding: 9px 16px; border-radius: 20px; border: 1.5px solid #b8860b; background: transparent; color: #8a6d1a; font: inherit; font-size: 0.9em; cursor: pointer; transition: all .15s; }
.mc-deep-btn:hover:not(:disabled), .mc-quiz-btn:hover:not(:disabled) { background: #b8860b; color: #fff; }
.mc-deep-btn:disabled, .mc-quiz-btn:disabled { opacity: .55; cursor: wait; }
.mc-sau { margin-top: 12px; }
.mc-nguyenlieu { margin-top: 10px; font-size: 0.86em; }
.mc-nguyenlieu summary { cursor: pointer; color: #8a6d1a; font-weight: 500; padding: 6px 0; }
.nl-row { padding: 8px 0; border-top: 1px dashed var(--read-border, #e0e0e0); }
.nl-badge { margin-left: 8px; font-size: 0.85em; }
.nl-badge.hoi { color: #2e7d32; } .nl-badge.don { color: #999; }
.nl-row ul { margin: 4px 0 0; padding-left: 18px; color: var(--read-text-faint, #777); }
.nl-row li { margin: 2px 0; }
.mc-quiz { margin-top: 14px; padding: 14px 16px; background: #f7faff; border: 1px solid #cdd9ee; border-radius: 10px; }
.quiz-hint { margin: 0 0 10px; font-size: 0.9em; color: #45607f; }
.quiz-row { padding: 8px 0; border-top: 1px solid #e6edf7; }
.quiz-row:first-of-type { border-top: none; }
.quiz-q { font-size: 0.95em; margin-bottom: 6px; color: var(--read-text, #333); }
.quiz-opts { display: flex; gap: 8px; }
.quiz-opts button { padding: 4px 14px; border-radius: 14px; border: 1px solid #b0c4de; background: #fff; color: #3a5070; font: inherit; font-size: 0.85em; cursor: pointer; }
.quiz-opts button:hover { background: #4a6fa5; color: #fff; border-color: #4a6fa5; }
.quiz-thanks { font-size: 0.85em; color: #2e7d32; }
.quiz-row.done { opacity: 0.7; }
.quiz-tn { margin-top: 12px; display: flex; gap: 8px; align-items: flex-end; }
.quiz-tn textarea { flex: 1; padding: 8px; border-radius: 8px; border: 1px solid #cdd9ee; font: inherit; font-size: 0.88em; resize: vertical; }
.quiz-tn button { padding: 8px 16px; border-radius: 8px; border: none; background: #4a6fa5; color: #fff; font: inherit; cursor: pointer; }
.quiz-tn button:disabled { opacity: .5; cursor: not-allowed; }
.quiz-login { margin: 10px 0 0; font-size: 0.85em; color: #8a6d1a; }
.hl-section { margin: 12px 0; padding: 12px 14px; background: #fffdf5; border: 1px solid #d4af37; border-radius: 8px; }
.hl-section h4 { margin: 0 0 8px; color: #8a6d1a; }
.hl-row { margin: 6px 0; font-size: 0.92em; line-height: 1.5; }
.hl-vitri { display: inline-block; min-width: 64px; padding: 1px 8px; margin-right: 8px; background: #f0e6c0; color: #6a5212; border-radius: 8px; font-size: 0.85em; font-weight: 500; }
.hl-mota { color: #3a3a38; }
.cc-summary { margin: 6px 0 4px; font-size: 0.92em; color: #444; }
.cc-chip {
  display: inline-block; margin: 0 4px; padding: 2px 10px;
  border-radius: 10px; font-size: 0.85em;
}
.cc-chip.cat { background: #e8f5e9; color: #1b5e20; }
.cc-chip.hung { background: #ffebee; color: #b71c1c; }
.cc-chip.hung_hoa_cat, .cc-chip.trung_tinh { background: #fff3e0; color: #b35900; }
</style>
