<script setup>
/**
 * 🔢 Ngũ Cục — 5 Cục (Thủy 2 · Mộc 3 · Kim 4 · Thổ 5 · Hỏa 6) cho Thư viện Tử Vi.
 *
 * B2 của đợt mở rộng Thư viện (Anh giao 2026-07-03). Cục = con số NỀN của lá số.
 *
 * Kỷ luật quote-or-silence (Iron #9): CHỈ hiện tầng grounded — hành nền + tính chất
 * element (Lê Văn Sửu, ngũ hành nền) + vai trò CƠ HỌC dẫn-xuất-được từ phép an sao.
 * Tầng "chất người từng cục" (Thủy nhị là kiểu người thế nào…) CHƯA có nguồn cổ thư
 * → nói rõ "đang chờ đọc sách", KHÔNG bịa.
 */
import { ref } from "vue";

const open = ref(false);
const loading = ref(false);
const error = ref("");
const items = ref([]);
const vaiTro = ref("");
const source = ref("");
const loaded = ref(false);

async function ensureLoaded() {
  if (loaded.value || loading.value) return;
  loading.value = true;
  error.value = "";
  try {
    const resp = await fetch("/api/tu-vi/cuc-list");
    const d = await resp.json();
    if (d.status !== "ok") throw new Error("API trả " + d.status);
    items.value = d.items || [];
    vaiTro.value = d.vai_tro || "";
    source.value = d.source || "";
    loaded.value = true;
  } catch (e) {
    error.value = "Không tải được danh sách Cục: " + (e?.message || e);
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
  <section class="ncl-block">
    <button type="button" class="ncl-toggle" @click="toggle">
      <span>🔢 Ngũ Cục — con số nền của lá số (Thủy 2 · Mộc 3 · Kim 4 · Thổ 5 · Hỏa 6)</span>
      <small>{{ open ? "thu gọn ▲" : "mở ra ▼" }}</small>
    </button>

    <div v-if="open" class="ncl-body">
      <p v-if="loading" class="ncl-note">Đang tải…</p>
      <p v-else-if="error" class="ncl-error">{{ error }}</p>

      <template v-else-if="items.length">
        <!-- Vai trò cơ học — grounded, dẫn-xuất-được từ phép an sao -->
        <p v-if="vaiTro" class="ncl-vaitro">{{ vaiTro }}</p>

        <div class="ncl-grid">
          <article
            v-for="c in items" :key="c.cuc"
            class="ncl-card"
            :data-hanh="c.element_key"
          >
            <header class="ncl-card-head">
              <h5>{{ c.cuc_name }}</h5>
              <span class="nh-badge" :data-hanh="c.element_key">{{ c.element }}</span>
            </header>
            <p class="ncl-nature">{{ c.nature }}</p>
            <!-- Tầng "chất người" chưa có nguồn → nói thật, không bịa -->
            <p v-if="c.chua_co_nguon" class="ncl-chuanguon">
              Chất người của cục này (đọc sâu) — chưa có nguồn cổ thư, đang chờ đọc sách.
            </p>
          </article>
        </div>

        <p v-if="source" class="ncl-cite">— {{ source }}</p>
      </template>
    </div>
  </section>
</template>

<style scoped>
.ncl-block { margin-top: 14px; }
.ncl-toggle {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  gap: 10px; text-align: left; padding: 11px 14px; cursor: pointer;
  background: var(--read-surface, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.15));
  border-radius: 10px;
  color: var(--read-text, rgba(230, 238, 245, 0.92));
  font-size: calc(14px * var(--reading-scale, 1)); font-weight: 600;
}
.ncl-toggle small { color: var(--read-text-faint, rgba(230, 238, 245, 0.55)); font-weight: 400; }
.ncl-body { padding: 12px 4px 4px; }
.ncl-note, .ncl-error { color: var(--read-text-muted, rgba(230, 238, 245, 0.7)); font-size: calc(13px * var(--reading-scale, 1)); }
.ncl-error { color: #f5a08c; }
.ncl-vaitro {
  color: var(--read-text-dim, rgba(230, 238, 245, 0.8));
  font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.65;
  border-left: 2px solid var(--read-rule, rgba(232, 201, 90, 0.4));
  padding-left: 10px; margin: 0 0 14px;
}
.ncl-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 10px;
}
.ncl-card {
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.16));
  border-left-width: 3px;
  border-radius: 9px; padding: 10px 12px;
  background: var(--read-surface, rgba(255, 255, 255, 0.02));
}
.ncl-card[data-hanh="mộc"] { border-left-color: rgba(90, 176, 122, 0.7); }
.ncl-card[data-hanh="hỏa"] { border-left-color: rgba(214, 90, 74, 0.7); }
.ncl-card[data-hanh="thổ"] { border-left-color: rgba(192, 168, 120, 0.75); }
.ncl-card[data-hanh="kim"] { border-left-color: rgba(220, 220, 230, 0.6); }
.ncl-card[data-hanh="thủy"] { border-left-color: rgba(110, 160, 220, 0.7); }
.ncl-card-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.ncl-card-head h5 {
  margin: 0; font-size: calc(14px * var(--reading-scale, 1)); font-weight: 700;
  color: var(--read-text, rgba(230, 238, 245, 0.92));
}
.ncl-nature {
  margin: 7px 0 0; font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.6;
  color: var(--read-text-dim, rgba(230, 238, 245, 0.82));
}
.ncl-chuanguon {
  margin: 8px 0 0; font-size: calc(11.5px * var(--reading-scale, 1)); line-height: 1.55;
  color: var(--read-text-faint, rgba(230, 238, 245, 0.5)); font-style: italic;
}
.ncl-cite {
  margin: 12px 0 0; text-align: right;
  font-size: calc(11.5px * var(--reading-scale, 1));
  color: var(--read-text-faint, rgba(230, 238, 245, 0.5));
}
.nh-badge {
  display: inline-block; padding: 1px 8px; border-radius: 999px;
  font-size: calc(11px * var(--reading-scale, 1)); font-weight: 600;
  border: 1px solid transparent;
}
.nh-badge[data-hanh="mộc"] { color: #8fd6a6; border-color: rgba(90, 176, 122, 0.55); }
.nh-badge[data-hanh="hỏa"] { color: #f5a08c; border-color: rgba(214, 90, 74, 0.55); }
.nh-badge[data-hanh="thổ"] { color: #d9c08e; border-color: rgba(192, 168, 120, 0.6); }
.nh-badge[data-hanh="kim"] { color: #e3e6ee; border-color: rgba(220, 220, 230, 0.45); }
.nh-badge[data-hanh="thủy"] { color: #9cc3f0; border-color: rgba(110, 160, 220, 0.55); }
</style>
