<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { getHexagramBySlug } from "../lib/api";
import HexagramImage from "./HexagramImage.vue";

const props = defineProps({
  slug: { type: String, default: "" },
});
const emit = defineEmits(["close"]);

const loading = ref(false);
const errorMsg = ref("");
const data = ref(null);

async function load(slug) {
  if (!slug) return;
  loading.value = true;
  errorMsg.value = "";
  data.value = null;
  try {
    const resp = await getHexagramBySlug(slug);
    if (resp.status === "ok") {
      data.value = resp;
    } else {
      errorMsg.value = `Không tìm thấy quẻ với slug "${slug}".`;
    }
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

watch(() => props.slug, (s) => load(s), { immediate: true });

const record = computed(() => data.value?.record || null);

function close() {
  emit("close");
}

function handleEsc(e) {
  if (e.key === "Escape") close();
}

onMounted(() => document.addEventListener("keydown", handleEsc));
onUnmounted(() => document.removeEventListener("keydown", handleEsc));

async function copyShareLink() {
  const url = new URL(window.location.href);
  url.searchParams.set("que", data.value.canonical_slug);
  url.hash = "";
  try {
    await navigator.clipboard.writeText(url.toString());
    copied.value = true;
    setTimeout(() => (copied.value = false), 1800);
  } catch {
    /* ignore — fallback nothing */
  }
}
const copied = ref(false);
</script>

<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="modal" role="dialog" aria-modal="true">
      <button class="close-btn" type="button" @click="close" aria-label="Đóng">×</button>

      <p v-if="loading" class="status">Đang tải quẻ…</p>
      <p v-if="errorMsg" class="status error">{{ errorMsg }}</p>

      <template v-if="record">
        <header class="modal-head">
          <HexagramImage :king-wen="record.king_wen_index" :size="72" />
          <div>
            <h3>
              Quẻ {{ record.king_wen_index }} — {{ record.name_vi }}
            </h3>
            <p class="slug-row">
              <code>{{ data.canonical_slug }}</code>
              <button class="copy-btn" type="button" @click="copyShareLink">
                {{ copied ? "✓ Đã sao chép" : "🔗 Sao chép link chia sẻ" }}
              </button>
            </p>
          </div>
        </header>

        <section class="kw-section" v-if="record.tu_khoa_hanh_dong?.length">
          <h6>Từ khóa hành động</h6>
          <div class="kw-list">
            <span v-for="(k, i) in record.tu_khoa_hanh_dong" :key="i" class="kw-chip">{{ k }}</span>
          </div>
        </section>

        <div class="reading-grid">
          <article v-if="record.an_bai_the_su" class="reading-card highlight">
            <h6>An bài thế sự</h6>
            <p>{{ record.an_bai_the_su }}</p>
          </article>
          <article v-if="record.the_gian_su_vu" class="reading-card">
            <h6>Thế gian sự vụ</h6>
            <p>{{ record.the_gian_su_vu }}</p>
          </article>
          <article v-if="record.nhap_the" class="reading-card">
            <h6>Nhập thế</h6>
            <p>{{ record.nhap_the }}</p>
          </article>
          <article v-if="record.xuat_the" class="reading-card">
            <h6>Xuất thế</h6>
            <p>{{ record.xuat_the }}</p>
          </article>
          <article v-if="record.the_gian_van" class="reading-card">
            <h6>Thế gian vận</h6>
            <p>{{ record.the_gian_van }}</p>
          </article>
          <article v-if="record.dien_giai_ngan_gon" class="reading-card">
            <h6>Diễn giải ngắn gọn</h6>
            <p>{{ record.dien_giai_ngan_gon }}</p>
          </article>
        </div>

        <p class="footer-note">
          Nguồn dữ liệu v2 — Tam Thiên Dịch Số + Kinh Dịch Trọn Bộ (Ngô Tất Tố).
        </p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(8, 12, 20, 0.78);
  backdrop-filter: blur(4px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  animation: fadeIn 0.15s;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal {
  position: relative;
  max-width: 720px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  background: linear-gradient(180deg, rgba(20, 30, 45, 0.98) 0%, rgba(12, 18, 28, 0.98) 100%);
  border: 1px solid var(--border-accent, rgba(232, 201, 90, 0.4));
  border-radius: 12px;
  padding: 24px 28px;
  color: var(--text-primary, #e6eef5);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.5);
}

.close-btn {
  position: absolute;
  top: 12px;
  right: 14px;
  background: transparent;
  border: none;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-size: 26px;
  line-height: 1;
  cursor: pointer;
  padding: 4px 8px;
}
.close-btn:hover { color: var(--accent-gold, #e8c95a); }

.status { font-size: 13px; color: var(--text-muted, rgba(230, 238, 245, 0.6)); }
.status.error { color: #d65a4a; }

.modal-head {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
  border-bottom: 1px dashed rgba(232, 201, 90, 0.22);
  padding-bottom: 16px;
}
.modal-head h3 {
  margin: 0;
  font-size: 22px;
  color: var(--accent-gold-soft, #f5e6b1);
}

.slug-row {
  margin: 6px 0 0 0;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.slug-row code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 8px;
  border-radius: 3px;
  color: var(--accent-teal, #5be5d3);
}
.copy-btn {
  background: rgba(91, 229, 211, 0.08);
  border: 1px solid rgba(91, 229, 211, 0.3);
  color: var(--accent-teal, #5be5d3);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11.5px;
  cursor: pointer;
}
.copy-btn:hover { background: rgba(91, 229, 211, 0.15); }

.kw-section { margin-bottom: 16px; }
.kw-section h6 {
  margin: 0 0 6px 0;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
}
.kw-list { display: flex; gap: 6px; flex-wrap: wrap; }
.kw-chip {
  background: rgba(232, 201, 90, 0.1);
  border: 1px solid rgba(232, 201, 90, 0.3);
  color: var(--accent-gold-soft, #f5e6b1);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.reading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 10px;
}
.reading-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 6px;
  padding: 12px 14px;
}
.reading-card.highlight {
  background: rgba(232, 201, 90, 0.06);
  border-color: rgba(232, 201, 90, 0.3);
  grid-column: 1 / -1;
}
.reading-card h6 {
  margin: 0 0 6px 0;
  font-size: 11px;
  color: var(--accent-teal, #5be5d3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
}
.reading-card p {
  margin: 0;
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--text-secondary, rgba(230, 238, 245, 0.82));
}

.footer-note {
  margin: 16px 0 0 0;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.4));
  font-style: italic;
  text-align: right;
}
</style>
