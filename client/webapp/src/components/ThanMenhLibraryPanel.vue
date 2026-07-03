<script setup>
/**
 * ☯ Thân — Mệnh: đồng cung vs khác cung (B3 Thư viện Tử Vi).
 *
 * ⚠️ "Mệnh" ở ĐÂY = QUAN HỆ Thân↔Mệnh, KHÔNG phải tên 12 cung (Anh chỉnh rõ 2026-07-03).
 *   • Đồng cung: Thân và Mệnh chung 1 cung → "tốt càng tốt, xấu càng xấu" (dồn lực).
 *   • Khác cung: Thân đóng 1 trong 6 cung khác → trọng tâm/hậu vận dồn về đó.
 *
 * GROUNDED (Iron #9): chỉ hiện atom ĐÃ DUYỆT + nguồn. Nguyên tắc chung (Vũ Tài Lục)
 * làm headline; luận sâu theo tuổi/vị trí (Nghiệm Lý Toàn Thư) để trong <details>.
 */
import { ref } from "vue";

const open = ref(false);
const loading = ref(false);
const error = ref("");
const dongCung = ref(null);
const khacCung = ref(null);
const loaded = ref(false);

async function ensureLoaded() {
  if (loaded.value || loading.value) return;
  loading.value = true;
  error.value = "";
  try {
    const resp = await fetch("/api/tu-vi/than-menh");
    const d = await resp.json();
    if (d.status !== "ok") throw new Error("API trả " + d.status);
    dongCung.value = d.dong_cung || null;
    khacCung.value = d.khac_cung || null;
    loaded.value = true;
  } catch (e) {
    error.value = "Không tải được Thân-Mệnh: " + (e?.message || e);
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
  <section class="tml-block">
    <button type="button" class="tml-toggle" @click="toggle">
      <span>☯ Thân — Mệnh: đồng cung vs khác cung (quan hệ, không phải tên cung)</span>
      <small>{{ open ? "thu gọn ▲" : "mở ra ▼" }}</small>
    </button>

    <div v-if="open" class="tml-body">
      <p v-if="loading" class="tml-note">Đang tải…</p>
      <p v-else-if="error" class="tml-error">{{ error }}</p>

      <template v-else-if="dongCung || khacCung">
        <!-- ── Đồng cung ── -->
        <div v-if="dongCung" class="tml-sec">
          <h5 class="tml-sec-title">① Thân Mệnh <b>đồng cung</b> — Thân và Mệnh chung một cung</h5>
          <blockquote v-if="dongCung.nguyen_tac" class="tml-principle">
            "{{ dongCung.nguyen_tac.text }}"
            <cite>— {{ dongCung.nguyen_tac.source }}</cite>
          </blockquote>
          <p v-else class="tml-chuanguon">Chưa có nguyên tắc chung đã duyệt cho phần này.</p>

          <details v-if="(dongCung.luan || []).length" class="tml-luan">
            <summary>📖 Luận sâu theo tuổi &amp; vị trí ({{ dongCung.luan.length }} trích, có nguồn)</summary>
            <article v-for="(x, i) in dongCung.luan" :key="i" class="tml-luan-item">
              <p class="tml-luan-q" v-if="x.q">{{ x.q }}</p>
              <p class="tml-luan-a">{{ x.text }}</p>
              <p class="tml-luan-src">— {{ x.source }}</p>
            </article>
          </details>
        </div>

        <!-- ── Khác cung ── -->
        <div v-if="khacCung" class="tml-sec">
          <h5 class="tml-sec-title">② Thân <b>khác cung</b> Mệnh — Thân đóng ở một trong 6 cung</h5>
          <p class="tml-intro">{{ khacCung.intro }}</p>
          <div class="tml-vitri-grid">
            <article
              v-for="v in khacCung.vi_tri" :key="v.palace"
              class="tml-vitri"
              :class="{ empty: v.chua_co_nguon }"
            >
              <h6>Thân cư {{ v.palace }}</h6>
              <template v-if="(v.y_nghia || []).length">
                <p v-for="(y, i) in v.y_nghia" :key="i" class="tml-vitri-text">
                  {{ y.text }}
                  <span class="tml-vitri-src">— {{ y.source }}</span>
                </p>
              </template>
              <p v-else class="tml-chuanguon">Chưa có nguồn — để trống.</p>
            </article>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.tml-block { margin-top: 14px; }
.tml-toggle {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  gap: 10px; text-align: left; padding: 11px 14px; cursor: pointer;
  background: var(--read-surface, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.15));
  border-radius: 10px;
  color: var(--read-text, rgba(230, 238, 245, 0.92));
  font-size: calc(14px * var(--reading-scale, 1)); font-weight: 600;
}
.tml-toggle small { color: var(--read-text-faint, rgba(230, 238, 245, 0.55)); font-weight: 400; }
.tml-body { padding: 12px 4px 4px; }
.tml-note, .tml-error { color: var(--read-text-muted, rgba(230, 238, 245, 0.7)); font-size: calc(13px * var(--reading-scale, 1)); }
.tml-error { color: #f5a08c; }
.tml-sec { margin-bottom: 18px; }
.tml-sec-title {
  margin: 0 0 8px; font-size: calc(13.5px * var(--reading-scale, 1)); font-weight: 600;
  color: var(--read-text, rgba(230, 238, 245, 0.9));
}
.tml-sec-title b { color: var(--read-han, #e8c95a); }
.tml-principle {
  margin: 0; padding: 10px 14px;
  border-left: 3px solid var(--read-rule, rgba(232, 201, 90, 0.5));
  background: var(--read-surface, rgba(255, 255, 255, 0.02));
  border-radius: 0 8px 8px 0;
  font-size: calc(14px * var(--reading-scale, 1)); line-height: 1.65;
  color: var(--read-text, rgba(230, 238, 245, 0.92));
}
.tml-principle cite {
  display: block; margin-top: 6px; font-style: normal;
  font-size: calc(11.5px * var(--reading-scale, 1));
  color: var(--read-text-faint, rgba(230, 238, 245, 0.55));
}
.tml-luan { margin-top: 10px; }
.tml-luan > summary {
  cursor: pointer; font-size: calc(12.5px * var(--reading-scale, 1)); font-weight: 600;
  color: var(--read-accent, #7ec8e3); padding: 4px 0;
}
.tml-luan-item {
  margin: 8px 0 0; padding: 8px 10px;
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.12));
  border-radius: 8px;
}
.tml-luan-q {
  margin: 0 0 4px; font-size: calc(12px * var(--reading-scale, 1)); font-weight: 600;
  color: var(--read-han, #e8c95a); opacity: 0.9;
}
.tml-luan-a {
  margin: 0; font-size: calc(12.5px * var(--reading-scale, 1)); line-height: 1.6;
  color: var(--read-text-dim, rgba(230, 238, 245, 0.82));
}
.tml-luan-src {
  margin: 4px 0 0; font-size: calc(11px * var(--reading-scale, 1));
  color: var(--read-text-faint, rgba(230, 238, 245, 0.5));
}
.tml-intro {
  margin: 0 0 10px; font-size: calc(13px * var(--reading-scale, 1)); line-height: 1.65;
  color: var(--read-text-dim, rgba(230, 238, 245, 0.8));
  border-left: 2px solid var(--read-border, rgba(230, 238, 245, 0.25)); padding-left: 10px;
}
.tml-vitri-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px;
}
.tml-vitri {
  border: 1px solid var(--read-border, rgba(230, 238, 245, 0.16));
  border-radius: 9px; padding: 9px 11px;
  background: var(--read-surface, rgba(255, 255, 255, 0.02));
}
.tml-vitri.empty { opacity: 0.6; }
.tml-vitri h6 {
  margin: 0 0 5px; font-size: calc(12.5px * var(--reading-scale, 1)); font-weight: 700;
  color: var(--read-accent, #7ec8e3);
}
.tml-vitri-text {
  margin: 5px 0 0; font-size: calc(12px * var(--reading-scale, 1)); line-height: 1.55;
  color: var(--read-text-dim, rgba(230, 238, 245, 0.8));
}
.tml-vitri-src {
  display: block; font-size: calc(10.5px * var(--reading-scale, 1));
  color: var(--read-text-faint, rgba(230, 238, 245, 0.45)); margin-top: 2px;
}
.tml-chuanguon {
  margin: 6px 0 0; font-size: calc(11.5px * var(--reading-scale, 1)); font-style: italic;
  color: var(--read-text-faint, rgba(230, 238, 245, 0.5));
}
</style>
