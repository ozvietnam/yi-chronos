<template>
  <div class="tu-vi-3layer-panel">
    <h2>🌌 Luận giải Tử Vi 3-Layer × 4 hệ phái</h2>

    <div v-if="loading" class="loading">Đang luận giải lá số...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="result">
      <!-- Lớp 1: Chuyện về anh -->
      <section class="lop-1">
        <h3>💬 Lớp 1 — Chuyện về anh</h3>
        <div class="content" v-html="renderMarkdown(result.lop_1_chuyen_ve_anh)"></div>
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

        <div v-for="(palace_data, palace) in result.lop_3_sach_co.per_palace" :key="palace" class="palace-block">
          <h4>🏛 Cung {{ formatPalace(palace) }}</h4>
          <div v-for="(cv, star) in palace_data.cross_views" :key="star" class="star-block">
            <h5>⭐ {{ formatStar(star) }} <span class="badge">{{ cv.total_atoms }} atoms</span></h5>
            <template v-for="(atoms, school) in cv.schools" :key="school">
            <div v-if="atoms && atoms.length > 0" class="school-view">
              <strong class="school-name">{{ result.lop_3_sach_co.schools_summary[school] }}:</strong>
              <ul>
                <li v-for="atom in atoms" :key="atom.atom_id" class="atom">
                  <div class="quote">"{{ atom.source_quote }}"</div>
                  <div v-if="atom.viet_thuan" class="paraphrase">→ {{ atom.viet_thuan }}</div>
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
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  // "1988-06-05T23:30" — nếu có thì gọi from-birth, không thì founder-demo
  birthDatetimeLocal: { type: String, default: null },
  timezone: { type: String, default: 'Asia/Ho_Chi_Minh' },
  gender: { type: String, default: 'nam' },
})

const loading = ref(true)
const error = ref(null)
const result = ref(null)

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
}

function formatPalace(p) {
  return PALACE_NAMES[p] || p
}

function formatStar(s) {
  return STAR_NAMES[s] || s
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

onMounted(load)
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
</style>
