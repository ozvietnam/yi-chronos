<script setup>
/**
 * MyPublicationsPanel — Hồ sơ kết quả sinh thành của user.
 *
 * List tất cả bản đã gen (Phê mệnh sâu, CDK 12 cung, Đại Hạn, Lưu Niên, Tổng đoán, Master).
 * Download PDF/DOCX/MD. Share via token. Archive. View stats.
 */
import { ref, computed, onMounted } from "vue";

const data = ref(null);
const shares = ref([]);
const loading = ref(false);
const error = ref("");
const filterPerson = ref("");
const showShareModal = ref(null);
const shareNote = ref("");
const shareExpiresIn = ref(7);
const shareMaxAccesses = ref(null);
const lastShareLink = ref("");

async function loadAll() {
  loading.value = true;
  error.value = "";
  try {
    const url = filterPerson.value
      ? `/api/user/publications?person_key=${encodeURIComponent(filterPerson.value)}`
      : '/api/user/publications';
    const r = await fetch(url, { credentials: 'include' });
    if (!r.ok) {
      error.value = `HTTP ${r.status}`;
      return;
    }
    data.value = await r.json();
    // Also load shares
    const sr = await fetch('/api/user/publications/shares/mine', { credentials: 'include' });
    if (sr.ok) {
      const sd = await sr.json();
      shares.value = sd.shares || [];
    }
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

function fileURL(pubId, fmt) {
  return `/api/user/publications/${pubId}/file/${fmt}`;
}

async function downloadFile(pubId, fmt) {
  const url = fileURL(pubId, fmt);
  const r = await fetch(url, { credentials: 'include' });
  if (!r.ok) {
    alert('Download failed: HTTP ' + r.status);
    return;
  }
  const blob = await r.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  const cd = r.headers.get('content-disposition');
  let fname = `publication_${pubId}.${fmt}`;
  if (cd) {
    const m = cd.match(/filename="?([^";]+)"?/);
    if (m) fname = m[1];
  }
  a.download = fname;
  a.click();
  URL.revokeObjectURL(a.href);
}

async function archive(pubId) {
  if (!confirm('Lưu trữ bản này? File giữ nguyên trên đĩa, chỉ ẩn khỏi danh sách.')) return;
  const r = await fetch(`/api/user/publications/${pubId}/archive`, {
    method: 'POST', credentials: 'include',
  });
  if (r.ok) loadAll();
  else alert('Archive failed');
}

async function openShareModal(pub) {
  showShareModal.value = pub;
  shareNote.value = "";
  shareExpiresIn.value = 7;
  shareMaxAccesses.value = null;
  lastShareLink.value = "";
}

async function createShare() {
  const pub = showShareModal.value;
  if (!pub) return;
  const r = await fetch('/api/user/publications/share', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      publication_id: pub.id,
      expires_in_days: shareExpiresIn.value || null,
      max_accesses: shareMaxAccesses.value || null,
      note: shareNote.value || null,
    }),
  });
  const d = await r.json();
  if (d.ok) {
    const fullUrl = `${window.location.origin}/api/share/${d.token}`;
    lastShareLink.value = fullUrl;
    loadAll();  // refresh shares list
  } else {
    alert('Share failed: ' + (d.error || '?'));
  }
}

async function revokeShare(shareId) {
  if (!confirm('Hủy share link này?')) return;
  await fetch(`/api/user/publications/shares/${shareId}`, {
    method: 'DELETE', credentials: 'include',
  });
  loadAll();
}

function copyLink(url) {
  navigator.clipboard.writeText(url).then(() => alert('✓ Đã copy link!'));
}

function formatDate(unix) {
  if (!unix) return '?';
  return new Date(unix * 1000).toLocaleString('vi-VN');
}

function formatBytes(chars) {
  if (chars > 1000) return `${(chars / 1000).toFixed(1)}k chars`;
  return `${chars} chars`;
}

const personKeys = computed(() => {
  const set = new Set((data.value?.publications || []).map(p => p.person_key));
  return Array.from(set);
});

const visiblePublications = computed(() => {
  if (!data.value?.publications) return [];
  return filterPerson.value
    ? data.value.publications.filter(p => p.person_key === filterPerson.value)
    : data.value.publications;
});

onMounted(loadAll);
</script>

<template>
  <section class="pub-panel">
    <header class="pub-head">
      <div>
        <h2>📚 Kết quả đã sinh của tôi</h2>
        <p class="pub-sub">
          Tất cả bản đã sinh thành — PDF · Word · Markdown. Share token cho người thân.
        </p>
      </div>
      <button class="pub-refresh" @click="loadAll" :disabled="loading">
        {{ loading ? '⏳' : '🔄' }} Làm mới
      </button>
    </header>

    <!-- Stats -->
    <div v-if="data?.stats" class="pub-stats">
      <div class="pub-stat-card">
        <small>📦 Tổng bản</small>
        <strong>{{ data.stats.publication_count }}</strong>
      </div>
      <div class="pub-stat-card">
        <small>📝 Tổng chữ</small>
        <strong>{{ data.stats.total_chars > 1000 ? (data.stats.total_chars / 1000).toFixed(1) + 'k' : data.stats.total_chars }}</strong>
      </div>
      <div class="pub-stat-card">
        <small>💰 Tổng chi phí</small>
        <strong>${{ data.stats.total_cost_usd?.toFixed(4) || '0' }}</strong>
      </div>
      <div class="pub-stat-card">
        <small>👤 Người được luận</small>
        <strong>{{ data.stats.person_count }}</strong>
      </div>
    </div>

    <!-- Person filter -->
    <div v-if="personKeys.length > 1" class="pub-filter">
      <span>Lọc theo người:</span>
      <button :class="{ active: !filterPerson }" @click="filterPerson = ''; loadAll()">Tất cả</button>
      <button v-for="pk in personKeys" :key="pk"
              :class="{ active: filterPerson === pk }"
              @click="filterPerson = pk; loadAll()">
        {{ pk }}
      </button>
    </div>

    <p v-if="loading" class="pub-loading">Đang tải...</p>
    <p v-if="error" class="pub-error">⚠ {{ error }}</p>
    <p v-if="!loading && !visiblePublications.length" class="pub-empty">
      Chưa có bản nào. Hãy mở Tử Vi / CDK panel và bấm "Luận sâu" để sinh thành bản đầu tiên.
    </p>

    <!-- Publication cards -->
    <div class="pub-grid">
      <article v-for="pub in visiblePublications" :key="pub.id"
               :class="['pub-card', pub.pub_type === 'master' && 'is-master']">
        <header class="pub-card-head">
          <div>
            <h3>{{ pub.title }}</h3>
            <small>
              👤 {{ pub.person_key }} ·
              📝 {{ formatBytes(pub.total_chars || 0) }} ·
              💰 ${{ (pub.cost_usd || 0).toFixed(4) }}
            </small>
          </div>
          <span v-if="pub.pub_type === 'master'" class="pub-master-badge">⭐ MASTER</span>
        </header>
        <div class="pub-meta">
          <small>📅 {{ formatDate(pub.generated_at) }}</small>
          <small v-if="pub.provider">🤖 {{ pub.provider }} ({{ pub.model || '?' }})</small>
          <small v-if="pub.version">🏷 {{ pub.version }}</small>
        </div>
        <div class="pub-actions">
          <button v-if="pub.formats.pdf" class="pub-btn pub-btn-pdf"
                  @click="downloadFile(pub.id, 'pdf')">
            📕 PDF
          </button>
          <button v-if="pub.formats.docx" class="pub-btn pub-btn-docx"
                  @click="downloadFile(pub.id, 'docx')">
            📄 Word
          </button>
          <button v-if="pub.formats.md" class="pub-btn pub-btn-md"
                  @click="downloadFile(pub.id, 'md')">
            📝 MD
          </button>
          <button v-if="pub.formats.json" class="pub-btn pub-btn-json"
                  @click="downloadFile(pub.id, 'json')">
            🗂 JSON
          </button>
          <button class="pub-btn pub-btn-share" @click="openShareModal(pub)">
            🔗 Chia sẻ
          </button>
          <button class="pub-btn pub-btn-archive" @click="archive(pub.id)">
            🗑 Lưu trữ
          </button>
        </div>
      </article>
    </div>

    <!-- Active shares -->
    <section v-if="shares.length" class="pub-shares">
      <h3>🔗 Link đang chia sẻ ({{ shares.length }})</h3>
      <article v-for="s in shares" :key="s.id" class="pub-share-card">
        <div class="pub-share-info">
          <strong>{{ s.pub_title }}</strong>
          <small>{{ s.person_key }} · {{ s.access_count }} lượt xem{{ s.max_accesses ? '/' + s.max_accesses : '' }}</small>
          <small v-if="s.expires_at">⏰ Hết hạn: {{ formatDate(s.expires_at) }}</small>
          <small v-if="s.note">💬 {{ s.note }}</small>
        </div>
        <div class="pub-share-actions">
          <code class="pub-share-link">{{ window.location.origin }}{{ s.share_url }}</code>
          <button @click="copyLink(window.location.origin + s.share_url)">📋 Copy</button>
          <button class="danger" @click="revokeShare(s.id)">🗑 Hủy</button>
        </div>
      </article>
    </section>

    <!-- Share modal -->
    <Teleport to="body">
      <div v-if="showShareModal" class="pub-modal-bg" @click.self="showShareModal = null">
        <div class="pub-modal">
          <button class="pub-modal-close" @click="showShareModal = null">✕</button>
          <h3>🔗 Chia sẻ: {{ showShareModal.title }}</h3>
          <label>Hết hạn sau (ngày):
            <input type="number" v-model.number="shareExpiresIn" min="0" placeholder="7 (mặc định)" />
            <small>Để 0 = không hết hạn</small>
          </label>
          <label>Số lượt xem tối đa:
            <input type="number" v-model.number="shareMaxAccesses" placeholder="Để trống = không giới hạn" />
          </label>
          <label>Ghi chú (tùy chọn):
            <input type="text" v-model="shareNote" placeholder="Vd: Chia sẻ cho vợ" />
          </label>
          <button class="pub-modal-create" @click="createShare">🔗 Tạo link chia sẻ</button>
          <div v-if="lastShareLink" class="pub-modal-result">
            <strong>✓ Link đã tạo:</strong>
            <code>{{ lastShareLink }}</code>
            <button @click="copyLink(lastShareLink)">📋 Copy</button>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.pub-panel {
  padding: 20px;
  max-width: 1100px;
  margin: 0 auto;
}
.pub-head {
  display: flex; justify-content: space-between; align-items: center;
  gap: 14px; margin-bottom: 16px;
}
.pub-head h2 { margin: 0; color: #fcd34d; font-size: 20px; }
.pub-sub { margin: 4px 0 0; color: rgba(230, 238, 245, 0.7); font-size: 13px; }
.pub-refresh {
  padding: 6px 12px; background: rgba(167, 139, 250, 0.16);
  color: #c4b5fd; border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 6px; cursor: pointer;
}
.pub-stats {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px; margin-bottom: 14px;
}
.pub-stat-card {
  padding: 12px; background: rgba(2, 6, 23, 0.45);
  border: 1px solid rgba(167, 139, 250, 0.2); border-radius: 8px;
  text-align: center;
}
.pub-stat-card small { display: block; color: rgba(230, 238, 245, 0.6); font-size: 11px; }
.pub-stat-card strong { display: block; color: #fcd34d; font-size: 20px; margin-top: 4px; }

.pub-filter {
  display: flex; gap: 6px; flex-wrap: wrap; align-items: center;
  margin-bottom: 14px; font-size: 12.5px;
}
.pub-filter span { color: rgba(230, 238, 245, 0.7); }
.pub-filter button {
  padding: 4px 10px; background: rgba(2, 6, 23, 0.4);
  color: rgba(230, 238, 245, 0.8); border: 1px solid rgba(230, 238, 245, 0.1);
  border-radius: 12px; cursor: pointer; font-size: 11.5px;
}
.pub-filter button.active {
  background: rgba(252, 211, 77, 0.18); color: #fcd34d;
  border-color: #fcd34d;
}

.pub-loading, .pub-error, .pub-empty {
  padding: 14px; text-align: center;
  color: rgba(230, 238, 245, 0.65); font-size: 13px;
}
.pub-error { color: #fca5a5; }

.pub-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 12px;
}
.pub-card {
  padding: 14px; background: rgba(2, 6, 23, 0.5);
  border: 1px solid rgba(167, 139, 250, 0.18); border-radius: 10px;
  transition: border-color 160ms;
}
.pub-card:hover { border-color: rgba(252, 211, 77, 0.32); }
.pub-card.is-master {
  border-color: #fcd34d; border-width: 2px;
  background: linear-gradient(135deg, rgba(252,211,77,0.06), rgba(2,6,23,0.5));
}
.pub-card-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 8px; margin-bottom: 8px;
}
.pub-card h3 { margin: 0; color: #fcd34d; font-size: 14.5px; line-height: 1.3; }
.pub-card-head small { color: rgba(230, 238, 245, 0.7); font-size: 11.5px; }
.pub-master-badge {
  padding: 3px 8px; background: #fcd34d; color: #1f1306;
  border-radius: 11px; font-size: 10px; font-weight: 700;
}
.pub-meta {
  display: flex; gap: 12px; flex-wrap: wrap;
  margin-bottom: 10px; font-size: 11px;
  color: rgba(230, 238, 245, 0.6);
}
.pub-actions {
  display: flex; flex-wrap: wrap; gap: 5px;
}
.pub-btn {
  padding: 5px 10px; border-radius: 5px; cursor: pointer;
  font-size: 11.5px; font-weight: 600;
  border: 1px solid transparent; transition: transform 100ms;
}
.pub-btn:hover { transform: translateY(-1px); }
.pub-btn-pdf { background: rgba(248, 113, 113, 0.16); color: #fca5a5; border-color: rgba(248,113,113,0.3); }
.pub-btn-docx { background: rgba(91, 229, 211, 0.16); color: #5be5d3; border-color: rgba(91,229,211,0.3); }
.pub-btn-md { background: rgba(196, 181, 253, 0.16); color: #c4b5fd; border-color: rgba(196,181,253,0.3); }
.pub-btn-json { background: rgba(252, 211, 77, 0.12); color: #fcd34d; border-color: rgba(252,211,77,0.25); }
.pub-btn-share { background: rgba(252, 211, 77, 0.2); color: #fcd34d; border-color: #fcd34d; }
.pub-btn-archive { background: rgba(230, 238, 245, 0.08); color: rgba(230,238,245,0.7); border-color: rgba(230,238,245,0.15); }

.pub-shares {
  margin-top: 20px; padding-top: 16px;
  border-top: 1px solid rgba(230, 238, 245, 0.1);
}
.pub-shares h3 { color: #5be5d3; font-size: 15px; margin: 0 0 10px; }
.pub-share-card {
  padding: 10px 12px; margin-bottom: 8px;
  background: rgba(2, 6, 23, 0.45);
  border: 1px solid rgba(91, 229, 211, 0.2); border-radius: 8px;
  display: flex; justify-content: space-between; align-items: center;
  gap: 10px; flex-wrap: wrap;
}
.pub-share-info strong { display: block; color: #fcd34d; font-size: 13px; }
.pub-share-info small { display: block; color: rgba(230, 238, 245, 0.65); font-size: 11px; }
.pub-share-actions { display: flex; gap: 5px; align-items: center; }
.pub-share-link {
  padding: 3px 8px; background: rgba(2, 6, 23, 0.6);
  color: #5be5d3; font-size: 11px; border-radius: 4px;
  font-family: monospace; max-width: 240px; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap;
}
.pub-share-actions button {
  padding: 4px 8px; background: rgba(91, 229, 211, 0.16); color: #5be5d3;
  border: 1px solid rgba(91, 229, 211, 0.3); border-radius: 5px;
  font-size: 11px; cursor: pointer;
}
.pub-share-actions button.danger {
  background: rgba(248, 113, 113, 0.16); color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.3);
}

.pub-modal-bg {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999; padding: 16px;
}
.pub-modal {
  background: #0f1b2a; padding: 24px; border-radius: 12px;
  max-width: 500px; width: 100%;
  border: 1px solid rgba(252, 211, 77, 0.3);
  position: relative;
}
.pub-modal-close {
  position: absolute; top: 10px; right: 12px;
  background: transparent; color: rgba(230, 238, 245, 0.6);
  border: none; font-size: 20px; cursor: pointer;
}
.pub-modal h3 { color: #fcd34d; margin: 0 0 14px; font-size: 16px; }
.pub-modal label {
  display: block; margin-bottom: 12px;
  color: rgba(230, 238, 245, 0.85); font-size: 12.5px;
}
.pub-modal label small {
  display: block; color: rgba(230, 238, 245, 0.55);
  font-size: 11px; margin-top: 2px;
}
.pub-modal input {
  width: 100%; margin-top: 4px;
  padding: 6px 10px; background: rgba(2, 6, 23, 0.6);
  color: #f5e6b1; border: 1px solid rgba(230, 238, 245, 0.15);
  border-radius: 6px; font-size: 13px;
}
.pub-modal-create {
  width: 100%; padding: 10px;
  background: linear-gradient(135deg, #fcd34d, #f59e0b);
  color: #1f1306; font-weight: 700; border: none;
  border-radius: 8px; cursor: pointer; margin-top: 6px;
}
.pub-modal-result {
  margin-top: 14px; padding: 10px;
  background: rgba(91, 229, 211, 0.08);
  border-left: 3px solid #5be5d3; border-radius: 0 6px 6px 0;
}
.pub-modal-result strong { display: block; color: #5be5d3; font-size: 12.5px; }
.pub-modal-result code {
  display: block; padding: 6px 8px; margin: 6px 0;
  background: rgba(2, 6, 23, 0.6); color: #f5e6b1;
  border-radius: 4px; font-size: 11.5px; word-break: break-all;
}
.pub-modal-result button {
  padding: 5px 10px; background: #5be5d3; color: #0f1a25;
  border: none; border-radius: 5px; font-size: 12px; cursor: pointer;
}
</style>
