<script setup>
/**
 * ✴️ Vòng sao / Phụ tinh — roster đầy đủ (B4 Thư viện Tử Vi, Anh chốt 2026-07-03).
 *
 * 89 phụ/vòng sao (loại 14 chính tinh — đã có hồ sơ sâu ở panel Chính Tinh). Nội dung
 * từ kho sao_noi_dung lớp 'def', CHỈ dòng đã DUYỆT ĐỐI KHÁNG (quote có trong sách +
 * dịch không bịa ý — pipeline verify_sao_noi_dung.py). Mỗi trích kèm NGUỒN đích danh;
 * quote gốc mở được để đối chiếu (quote-or-silence, minh bạch).
 */
import { computed, ref } from "vue";

const open = ref(false);
const loading = ref(false);
const error = ref("");
const stars = ref([]);
const disclaimer = ref("");
const loaded = ref(false);
const selected = ref(null);
const kw = ref("");

const filtered = computed(() => {
  const q = kw.value.trim().toLowerCase();
  if (!q) return stars.value;
  return stars.value.filter(
    (s) => s.sao_vi.toLowerCase().includes(q) || (s.sao_zh || "").includes(q),
  );
});

const selectedTotalCount = computed(() => {
  if (!selected.value) return 0;
  return (
    (selected.value.items?.length || 0) +
    (selected.value.cung_items?.length || 0) +
    (selected.value.ket_hop_items?.length || 0)
  );
});

async function ensureLoaded() {
  if (loaded.value || loading.value) return;
  loading.value = true;
  error.value = "";
  try {
    const resp = await fetch("/api/tu-vi/vong-sao");
    const d = await resp.json();
    if (d.status !== "ok") throw new Error("API trả " + d.status);
    stars.value = d.stars || [];
    disclaimer.value = d.disclaimer || "";
    selected.value = stars.value[0] || null;
    loaded.value = true;
  } catch (e) {
    error.value = "Không tải được vòng sao: " + (e?.message || e);
  } finally {
    loading.value = false;
  }
}

async function toggle() {
  open.value = !open.value;
  if (open.value) await ensureLoaded();
}
</script>

<template>
  <section class="vsl-block">
    <button type="button" class="vsl-toggle" @click="toggle">
      <span>✴️ Vòng sao &amp; Phụ tinh — roster đầy đủ (đã duyệt, có nguồn)</span>
      <small>{{ open ? "thu gọn ▲" : "mở ra ▼" }}</small>
    </button>

    <div v-if="open" class="vsl-body">
      <p v-if="loading" class="vsl-note">Đang tải…</p>
      <p v-else-if="error" class="vsl-error">{{ error }}</p>

      <template v-else-if="stars.length">
        <p class="vsl-disclaimer">{{ disclaimer }}</p>
        <input v-model="kw" class="vsl-search" type="search"
          :placeholder="`Tìm trong ${stars.length} phụ/vòng sao (vd Kình Dương, Lộc Tồn, Bạch Hổ)…`" />

        <div class="vsl-grid">
          <button
            v-for="s in filtered" :key="s.sao_vi"
            type="button"
            class="vsl-chip"
            :class="{ active: selected === s }"
            @click="selected = s"
          >{{ s.sao_vi }}<small v-if="s.sao_zh">{{ s.sao_zh }}</small></button>
        </div>
        <p v-if="!filtered.length" class="vsl-note">Không có sao khớp "{{ kw }}".</p>

        <article v-if="selected" class="vsl-detail">
          <h5>
            {{ selected.sao_vi }}
            <span v-if="selected.sao_zh" class="vsl-zh">{{ selected.sao_zh }}</span>
            <small>{{ selectedTotalCount }} trích có nguồn</small>
          </h5>

          <template v-if="selected.items.length">
            <h6 class="vsl-sub">Định nghĩa chung</h6>
            <div v-for="(it, i) in selected.items" :key="'d' + i" class="vsl-item">
              <p class="vsl-dich">{{ it.dich }}</p>
              <div class="vsl-meta">
                <span class="vsl-src">📖 {{ it.nguon }}</span>
                <details v-if="it.quote_goc" class="vsl-quote">
                  <summary>quote gốc</summary>
                  <p>{{ it.quote_goc }}</p>
                </details>
              </div>
            </div>
          </template>

          <template v-if="selected.cung_items.length">
            <h6 class="vsl-sub">Theo cung an</h6>
            <div v-for="(it, i) in selected.cung_items" :key="'c' + i" class="vsl-item">
              <p class="vsl-dich"><span class="vsl-cung-tag">{{ it.cung }}</span>{{ it.dich }}</p>
              <div class="vsl-meta">
                <span class="vsl-src">📖 {{ it.nguon }}</span>
                <details v-if="it.quote_goc" class="vsl-quote">
                  <summary>quote gốc</summary>
                  <p>{{ it.quote_goc }}</p>
                </details>
              </div>
            </div>
          </template>

          <template v-if="selected.ket_hop_items.length">
            <h6 class="vsl-sub">Kết hợp với sao khác</h6>
            <div v-for="(it, i) in selected.ket_hop_items" :key="'k' + i" class="vsl-item">
              <p class="vsl-dich">{{ it.dich }}</p>
              <div class="vsl-meta">
                <span class="vsl-src">📖 {{ it.nguon }}</span>
                <details v-if="it.quote_goc" class="vsl-quote">
                  <summary>quote gốc</summary>
                  <p>{{ it.quote_goc }}</p>
                </details>
              </div>
            </div>
          </template>
        </article>
      </template>
      <p v-else class="vsl-note">Chưa có phụ/vòng sao nào đã duyệt.</p>
    </div>
  </section>
</template>

<style scoped>
.vsl-block { margin-top: 14px; }
.vsl-toggle {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  gap: 10px; text-align: left; padding: 11px 14px; cursor: pointer;
  background: var(--read-surface, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.15));
  border-radius: 10px;
  color: var(--read-text, rgba(230, 238, 245, 0.92));
  font-size: calc(14px * var(--reading-scale, 1)); font-weight: 600;
}
.vsl-toggle small { color: var(--read-text-faint, rgba(230, 238, 245, 0.55)); font-weight: 400; }
.vsl-body { padding: 12px 4px 4px; }
.vsl-note, .vsl-error { color: var(--read-text-muted, rgba(230, 238, 245, 0.7)); font-size: calc(13px * var(--reading-scale, 1)); }
.vsl-error { color: #f5a08c; }
.vsl-disclaimer {
  margin: 0 0 10px; font-size: calc(12px * var(--reading-scale, 1)); line-height: 1.6;
  color: var(--read-text-faint, rgba(230, 238, 245, 0.6)); font-style: italic;
  border-left: 2px solid var(--read-border, rgba(230, 238, 245, 0.2)); padding-left: 9px;
}
.vsl-search {
  width: 100%; box-sizing: border-box; padding: 8px 12px; margin-bottom: 10px;
  background: var(--read-surface, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.2)); border-radius: 8px;
  color: var(--read-text, rgba(230, 238, 245, 0.92));
  font-size: calc(13px * var(--reading-scale, 1));
}
.vsl-grid {
  display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px;
  max-height: 168px; overflow-y: auto;
}
.vsl-chip {
  display: inline-flex; align-items: baseline; gap: 4px; cursor: pointer;
  padding: 5px 10px; border-radius: 999px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.2));
  background: var(--read-surface, rgba(255, 255, 255, 0.02));
  color: var(--read-text-dim, rgba(230, 238, 245, 0.82));
  font-size: calc(12px * var(--reading-scale, 1));
}
.vsl-chip small { color: var(--read-text-faint, rgba(230, 238, 245, 0.45)); font-size: calc(10px * var(--reading-scale, 1)); }
.vsl-chip.active {
  border-color: var(--read-accent, #7ec8e3); color: var(--read-accent, #7ec8e3);
  background: var(--read-accent-bg, rgba(126, 200, 227, 0.12));
}
.vsl-detail {
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.16));
  border-radius: 10px; padding: 12px 14px;
  background: var(--read-surface, rgba(255, 255, 255, 0.02));
}
.vsl-detail h5 {
  margin: 0 0 10px; font-size: calc(15px * var(--reading-scale, 1)); font-weight: 700;
  color: var(--read-text, rgba(230, 238, 245, 0.95)); display: flex; align-items: baseline; gap: 8px;
}
.vsl-zh { color: var(--read-han, #e8c95a); font-weight: 500; font-size: calc(13px * var(--reading-scale, 1)); }
.vsl-detail h5 small {
  margin-left: auto; font-weight: 400;
  font-size: calc(11px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.5));
}
.vsl-sub {
  margin: 14px 0 4px; font-size: calc(11px * var(--reading-scale, 1)); font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.04em;
  color: var(--read-accent, #7ec8e3);
}
.vsl-sub:first-of-type { margin-top: 0; }
.vsl-cung-tag {
  display: inline-block; margin-right: 7px; padding: 1px 8px; border-radius: 999px;
  font-size: calc(10px * var(--reading-scale, 1)); font-weight: 600;
  background: var(--read-accent-bg, rgba(126, 200, 227, 0.15));
  color: var(--read-accent, #7ec8e3); vertical-align: middle;
}
.vsl-item {
  padding: 9px 0; border-top: 1px solid var(--read-border, rgba(230, 238, 245, 0.1));
}
.vsl-item:first-of-type { border-top: none; }
.vsl-dich {
  margin: 0; font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.65;
  color: var(--read-text, rgba(230, 238, 245, 0.88));
}
.vsl-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: 5px; }
.vsl-src { font-size: calc(11px * var(--reading-scale, 1)); color: var(--read-text-faint, rgba(230, 238, 245, 0.55)); }
.vsl-quote > summary {
  cursor: pointer; font-size: calc(11px * var(--reading-scale, 1));
  color: var(--read-accent, #7ec8e3);
}
.vsl-quote p {
  margin: 5px 0 0; font-size: calc(12px * var(--reading-scale, 1)); line-height: 1.6;
  color: var(--read-text-dim, rgba(230, 238, 245, 0.72));
  padding-left: 9px; border-left: 2px solid var(--read-rule, rgba(232, 201, 90, 0.35));
}
</style>
