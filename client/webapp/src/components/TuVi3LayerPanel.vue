<template>
  <div class="tu-vi-3layer-panel">
    <h2>🌌 Luận giải Tử Vi 3-Layer × 4 hệ phái</h2>

    <div v-if="loading" class="loading">Đang luận giải lá số...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="result">
      <!-- Lớp 1: Chuyện về anh -->
      <section class="lop-1">
        <h3>💬 Lớp 1 — Chuyện về anh
          <button class="narrative-btn" :disabled="narrativeLoading" @click="loadNarrative">
            {{ narrativeLoading ? '⏳ Đang viết...' : narrative ? '🔄 Viết lại' : '✨ Luận mượt (AI)' }}
          </button>
        </h3>
        <div v-if="narrative" class="content narrative-text" v-html="renderMarkdown(narrative)"></div>
        <div v-else class="content" v-html="renderMarkdown(result.lop_1_chuyen_ve_anh)"></div>
        <small v-if="narrative" class="narrative-meta">✨ AI luận theo paradigm đọc đồng dạng — mệnh 7 phần, người 3 phần</small>
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

      <!-- Lớp 3: Sách cổ nói -->
      <section class="lop-3">
        <h3>📚 Lớp 3 — Sách cổ nói (4 hệ phái)</h3>

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
.tu-vi-3layer-panel {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
}

h2 {
  color: #6a4c93;
  border-bottom: 2px solid #6a4c93;
  padding-bottom: 8px;
}

section {
  margin: 32px 0;
  padding: 20px;
  border-radius: 8px;
}

.lop-1 { background: #fff8e7; border-left: 4px solid #f4a261; }
.lop-2 { background: #e7f3ff; border-left: 4px solid #2a9d8f; }
.lop-3 { background: #f0f0f0; border-left: 4px solid #6a4c93; }

h3 { margin-top: 0; }

.warnings {
  margin-top: 16px;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
}

.warning {
  margin: 8px 0;
  padding: 8px 12px;
  border-radius: 4px;
}
.warning.severity-info { background: #d1ecf1; }
.warning.severity-warning { background: #fff3cd; }
.warning.severity-danger { background: #f8d7da; }
.warning.severity-neutral { background: #e9ecef; }

.citation { font-size: 0.85em; color: #555; margin-top: 4px; }

.schools-legend {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.school-tag {
  padding: 4px 12px;
  background: #6a4c93;
  color: white;
  border-radius: 12px;
  font-size: 0.85em;
}

.palace-block {
  margin: 20px 0;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
}

.star-block {
  margin: 16px 0;
  padding-left: 12px;
  border-left: 2px solid #ddd;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  background: #6a4c93;
  color: white;
  border-radius: 8px;
  font-size: 0.75em;
}

.school-view {
  margin: 12px 0;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 4px;
}

.school-name { color: #6a4c93; }

.atom { margin: 12px 0; }

.quote {
  font-style: italic;
  background: #fff8e7;
  padding: 8px;
  border-left: 3px solid #f4a261;
}

.paraphrase {
  margin-top: 4px;
  color: #2a9d8f;
}

.meta {
  font-size: 0.8em;
  color: #888;
  margin-top: 4px;
}

.metadata {
  margin-top: 32px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
  text-align: center;
  color: #555;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 1.1em;
}
.error { color: #d9534f; }

/* Wiki glossary term — gạch chấm + tooltip native */
:deep(.hv-term) {
  border-bottom: 1px dotted #6a4c93;
  cursor: help;
  color: #5a3d80;
}

.dai-van-section {
  margin: 20px 0;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #2a9d8f;
}

.tu-hoa-bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
.tu-hoa-chip {
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 0.82em;
  background: #ede7f6;
  color: #4a2d70;
}
.tu-hoa-chip.hoa_loc { background: #e8f5e9; color: #1b5e20; }
.tu-hoa-chip.hoa_quyen { background: #fff3e0; color: #b35900; }
.tu-hoa-chip.hoa_khoa { background: #e3f2fd; color: #0d47a1; }
.tu-hoa-chip.hoa_ky { background: #ffebee; color: #b71c1c; }
.phu-tinh-block { border-left-color: #b8a5d8; }
.badge-phu { background: #9575cd; }

.mh-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 8px;
  font-size: 0.7em;
  margin-right: 6px;
}
.mh-good { background: #e8f5e9; color: #1b5e20; }
.mh-bad { background: #ffebee; color: #b71c1c; }
.mh-mid { background: #eceff1; color: #455a64; }
.atom-lech { opacity: 0.62; }
.dieu-kien-note {
  font-size: 0.8em;
  color: #b35900;
  background: #fff8e1;
  padding: 3px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
}

.to-hop-section {
  margin: 20px 0;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px dashed #6a4c93;
}
.to-hop-hint { font-size: 0.85em; color: #666; margin: 4px 0 12px; }
.to-hop-block { margin: 16px 0; padding-left: 12px; border-left: 2px solid #c9b8e8; }
.to-hop-meta { font-size: 0.88em; color: #444; margin: 6px 0 10px; }
.rel-tag {
  display: inline-block;
  margin: 0 6px 4px 0;
  padding: 1px 8px;
  background: #ede7f6;
  color: #5a3d80;
  border-radius: 8px;
  font-size: 0.72em;
}

.narrative-btn {
  float: right;
  padding: 4px 14px;
  border: 1px solid #f4a261;
  background: #fff;
  color: #c2410c;
  border-radius: 14px;
  cursor: pointer;
  font-size: 0.75em;
}
.narrative-btn:disabled { opacity: 0.6; cursor: wait; }
.narrative-text { white-space: pre-wrap; line-height: 1.8; }
.narrative-meta { display: block; margin-top: 8px; color: #888; }
</style>
