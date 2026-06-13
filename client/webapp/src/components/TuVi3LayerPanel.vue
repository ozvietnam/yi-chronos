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

        <!-- Tóm tắt + tên cách cục (luôn hiện, súc tích) -->
        <div v-if="cachCucNamed.length" class="cc-summary">
          🏆 Cách cục trong lá số:
          <span v-for="cc in cachCucNamed" :key="cc.slug" :class="['cc-chip', cc.loai]">{{ cc.ten }}</span>
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

        <!-- Tứ Hóa năm sinh -->
        <div v-if="tuHoa.length" class="tu-hoa-bar">
          <span v-for="t in tuHoa" :key="t.hoa" :class="['tu-hoa-chip', t.hoa]">
            {{ formatStar(t.hoa) }}: {{ formatStar(t.star) }} ({{ formatFn(t.palace_fn) || formatPalace(t.palace_chi) }})
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
const daiVan = computed(() => result.value?.lop_3_sach_co?.dai_van_hien_tai || null)

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

function escapeHtml(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
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

function renderMarkdown(text) {
  return text
    .replace(/^## (.+)$/gm, '<h4>$1</h4>')
    .replace(/^\*\*(.+?)\*\*/gm, '<strong>$1</strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
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
    // Bài luận mượt là MẶC ĐỊNH — tự chạy ngay sau khi có lá số
    if (props.birthDatetimeLocal) loadNarrative()
  } catch (e) {
    error.value = `Lỗi: ${e.message}`
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadGlossary(); load(); })
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
.cc-summary { margin: 6px 0 4px; font-size: 0.92em; color: #444; }
.cc-chip {
  display: inline-block; margin: 0 4px; padding: 2px 10px;
  border-radius: 10px; font-size: 0.85em;
}
.cc-chip.cat { background: #e8f5e9; color: #1b5e20; }
.cc-chip.hung { background: #ffebee; color: #b71c1c; }
.cc-chip.hung_hoa_cat, .cc-chip.trung_tinh { background: #fff3e0; color: #b35900; }
</style>
