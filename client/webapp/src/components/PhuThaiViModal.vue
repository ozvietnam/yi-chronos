<script setup>
/**
 * PhuThaiViModal — hiển thị Phú Thái Vi (太微赋) — bài phú mở đầu Q1 Tử Vi
 * Đẩu Số Toàn Thư của Trần Đoàn / Phan Hy Doãn.
 *
 * Source: data/yi_publishing/translations/tuvidauso-zh/p0016 + p0017
 * Load via API: /api/yi-publishing/pages/tuvidauso-zh/16 + 17
 *
 * Hiển thị 2 lớp: Hán-Việt (italic) + Luận giải (main).
 */
import { ref, onMounted, computed } from "vue";

const props = defineProps({
  visible: { type: Boolean, default: false },
});
const emit = defineEmits(["close"]);

const loading = ref(false);
const error = ref("");
const passages = ref([]);  // [{hanviet, luangiai, giaithichdande}]
const sourceMeta = ref({
  book: "Tử Vi Đẩu Số Toàn Thư",
  hanzi: "紫微斗数全书",
  chapter: "Quyển 1 · Phú Thái Vi (太微赋)",
  author: "Trần Đoàn (Hy Di tiên sinh) — Phan Hy Doãn bổ tập",
  source_pages: "TVDSTT Q.1 — tr.16-17",
});

// View mode: which layers to show
const showHanViet = ref(true);
const showLuanGiai = ref(false);
const showDanDa = ref(true);   // default ON — đây là lớp chính cho người mới

async function loadPhu() {
  loading.value = true;
  error.value = "";
  passages.value = [];
  try {
    // Try Layer 3 endpoint first (preferred — has all 3 layers)
    const r3 = await fetch("/api/yi-publishing/phu/phu-thai-vi");
    if (r3.ok) {
      const d = await r3.json();
      if (d.status === "ok" && d.passages?.length) {
        passages.value = d.passages.map((p) => ({
          hanviet: p.hanviet || "",
          luangiai: p.luangiai || "",
          giaithichdande: p.giaithichdande || "",
        }));
        return;
      }
    }
    // Fallback: load 2-layer from raw translation pages
    const out = [];
    for (const pg of [16, 17]) {
      const r = await fetch(`/api/yi-publishing/pages/tuvidauso-zh/${pg}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      if (d.status !== "ok") continue;
      for (const region of d.regions || []) {
        if (!["text", "title", "paragraph"].includes(region.type)) continue;
        for (const line of region.lines || []) {
          const tr = line.translation || {};
          const hv = tr.text_vi || "";
          const lg = tr.text_vi_luangiai || "";
          if (hv || lg) {
            out.push({ hanviet: hv, luangiai: lg, giaithichdande: "" });
          }
        }
      }
    }
    passages.value = out;
  } catch (e) {
    error.value = e.message || String(e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (props.visible) loadPhu();
});

import { watch } from "vue";
watch(() => props.visible, (v) => { if (v && !passages.value.length) loadPhu(); });
</script>

<template>
  <div v-if="visible" class="ptv-modal-backdrop" @click.self="emit('close')">
    <div class="ptv-modal">
      <header class="ptv-head">
        <div>
          <h2>📜 Phú Thái Vi</h2>
          <p class="ptv-hanzi">{{ sourceMeta.hanzi.substring(0, 5) }} 太微赋</p>
        </div>
        <button class="ptv-close" @click="emit('close')" aria-label="Đóng">✕</button>
      </header>

      <div class="ptv-meta">
        <div><b>{{ sourceMeta.book }}</b> · {{ sourceMeta.chapter }}</div>
        <div class="ptv-author">{{ sourceMeta.author }}</div>
        <div class="ptv-cite">Nguồn: {{ sourceMeta.source_pages }}</div>
      </div>

      <div class="ptv-intro">
        <p>
          <em>Phú Thái Vi</em> là bài phú mở đầu Quyển 1 của <b>Tử Vi Đẩu Số Toàn Thư</b>, đặt nền móng
          cho toàn bộ học thuyết. Đây là <b>QUY TẮC CHUNG cho mọi lá số</b> (không phải lá số riêng anh).
          Mỗi câu là một <b>nguyên lý đoán mệnh</b> được Trần Đoàn cô đọng hơn 1000 năm trước.
        </p>
      </div>

      <!-- Layer toggle — chọn cách đọc -->
      <div class="ptv-layer-toggle">
        <label :class="{ active: showDanDa }">
          <input type="checkbox" v-model="showDanDa" />
          🟢 Giải thích dân dã <small>(người mới nên đọc)</small>
        </label>
        <label :class="{ active: showLuanGiai }">
          <input type="checkbox" v-model="showLuanGiai" />
          🟡 Luận giải học thuật <small>(có thuật ngữ Tử Vi)</small>
        </label>
        <label :class="{ active: showHanViet }">
          <input type="checkbox" v-model="showHanViet" />
          📜 Hán-Việt nguyên văn <small>(đối chiếu)</small>
        </label>
      </div>

      <div v-if="loading" class="ptv-loading">Đang tải Phú...</div>
      <div v-if="error" class="ptv-error">Lỗi: {{ error }}</div>

      <div v-if="passages.length" class="ptv-passages">
        <div v-for="(p, idx) in passages" :key="idx" class="ptv-passage">
          <p class="ptv-hanviet" v-if="showHanViet && p.hanviet">
            <span class="ptv-marker">音</span>
            <span>{{ p.hanviet }}</span>
          </p>
          <p class="ptv-luangiai" v-if="showLuanGiai && p.luangiai">
            <span class="ptv-marker">義</span>
            <span>{{ p.luangiai }}</span>
          </p>
          <p class="ptv-danda" v-if="showDanDa && p.giaithichdande">
            <span class="ptv-marker ptv-marker-danda">解</span>
            <span>{{ p.giaithichdande }}</span>
          </p>
          <p class="ptv-danda ptv-danda-missing" v-else-if="showDanDa && !p.giaithichdande">
            <em>(chưa có giải thích dân dã)</em>
          </p>
        </div>
      </div>

      <footer class="ptv-foot">
        <small>
          📚 Phú này là <b>tuyên ngôn nền tảng</b> của Tử Vi Đẩu Số.
          Dùng để đối chiếu khi luận đoán mệnh — mỗi câu là 1 quy tắc.
        </small>
        <button class="ptv-close-btn" @click="emit('close')">Đóng</button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.ptv-modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(6px);
  z-index: 2000;
  display: flex; justify-content: center; align-items: center;
  padding: 1rem;
}
.ptv-modal {
  background: linear-gradient(180deg, #faf6ed 0%, #f5efe0 100%);
  color: #1a1410;
  border: 2px solid #b8a890;
  border-radius: 10px;
  max-width: 820px;
  width: 100%;
  max-height: 92vh;
  display: flex; flex-direction: column;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7);
  font-family: "Charter", "Iowan Old Style", Georgia, serif;
}
.ptv-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 1.2rem 1.5rem 0.5rem;
  border-bottom: 2px solid #b8a890;
}
.ptv-head h2 { margin: 0; color: #4a1a1a; font-size: 1.6rem; }
.ptv-hanzi {
  margin: 0.2rem 0 0;
  font-family: "Songti SC", "Noto Serif CJK SC", serif;
  color: #6d2727; font-size: 1.1rem; letter-spacing: 0.1em;
}
.ptv-close {
  background: none; border: none; font-size: 1.3rem;
  color: #6d4a2a; cursor: pointer; padding: 0.3rem 0.5rem;
}
.ptv-close:hover { color: #4a1a1a; }

.ptv-meta {
  padding: 0.5rem 1.5rem;
  font-size: 0.82rem;
  color: #5a4a3a;
  border-bottom: 1px dashed #b8a890;
}
.ptv-meta b { color: #4a1a1a; }
.ptv-author { font-style: italic; margin-top: 0.15rem; }
.ptv-cite { color: #8b6a4a; font-size: 0.75rem; margin-top: 0.15rem; }

.ptv-intro {
  padding: 0.7rem 1.5rem;
  font-size: 0.88rem;
  color: #2a2410;
  background: rgba(184, 168, 144, 0.15);
  border-bottom: 1px solid #c8b896;
}
.ptv-intro p { margin: 0; line-height: 1.7; }
.ptv-intro em { color: #6d2727; font-weight: 600; }
.ptv-intro b { color: #4a1a1a; }

.ptv-passages {
  flex: 1; overflow-y: auto;
  padding: 0.7rem 1.5rem 0.8rem;
}
.ptv-passage {
  margin: 0.45rem 0;
  padding: 0.55rem 0.7rem;
  background: rgba(255, 255, 255, 0.55);
  border-left: 3px solid #c8b896;
  border-radius: 0 4px 4px 0;
  page-break-inside: avoid;
}
.ptv-hanviet, .ptv-luangiai {
  margin: 0;
  display: flex; gap: 0.4rem; align-items: flex-start;
  line-height: 1.6;
}
.ptv-hanviet {
  font-style: italic;
  color: #5a3a1a;
  font-size: 0.92rem;
  border-bottom: 1px dashed rgba(184, 168, 144, 0.5);
  padding-bottom: 0.35rem;
  margin-bottom: 0.35rem;
}
.ptv-luangiai {
  color: #1a1410;
  font-size: 1rem;
}
.ptv-marker {
  font-family: "Songti SC", serif;
  font-style: normal;
  font-weight: 700;
  color: #8b3a2a;
  font-size: 0.95em;
  flex-shrink: 0;
  width: 1.3em;
}

/* Layer toggle */
.ptv-layer-toggle {
  display: flex; flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.6rem 1.5rem;
  border-bottom: 1px solid #c8b896;
  background: rgba(184, 168, 144, 0.08);
}
.ptv-layer-toggle label {
  display: inline-flex; align-items: center; gap: 0.35rem;
  background: rgba(255,255,255,0.4);
  border: 1px solid #c8b896;
  padding: 0.3rem 0.7rem;
  border-radius: 4px;
  cursor: pointer; font-size: 0.78rem;
  color: #6d4a2a;
  transition: all 0.15s;
  user-select: none;
}
.ptv-layer-toggle label.active {
  background: #4a1a1a; color: #fde68a;
  border-color: #4a1a1a;
}
.ptv-layer-toggle label small {
  opacity: 0.7; font-size: 0.72rem;
}
.ptv-layer-toggle input[type="checkbox"] { accent-color: #fde68a; }

/* Layer 3 — Giải thích dân dã */
.ptv-danda {
  margin: 0.35rem 0 0 0;
  display: flex; gap: 0.4rem; align-items: flex-start;
  line-height: 1.65;
  color: #1a1410;
  font-size: 1rem;
  background: rgba(16, 185, 129, 0.08);
  padding: 0.4rem 0.55rem;
  border-radius: 3px;
  border-left: 3px solid #10b981;
}
.ptv-marker-danda {
  color: #047857;
}
.ptv-danda-missing {
  color: #94a3b8;
  font-style: italic;
  background: transparent;
  border-left: 3px solid #94a3b8;
}

.ptv-loading, .ptv-error {
  padding: 1.5rem;
  text-align: center;
  color: #6d4a2a;
}
.ptv-error { color: #8b1a1a; }

.ptv-foot {
  padding: 0.75rem 1.5rem;
  border-top: 1px solid #c8b896;
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(184, 168, 144, 0.15);
}
.ptv-foot small { color: #5a4a3a; font-size: 0.75rem; max-width: 70%; }
.ptv-foot small b { color: #4a1a1a; }
.ptv-close-btn {
  background: linear-gradient(135deg, #6d2727, #4a1a1a);
  color: #fff; border: none;
  padding: 0.5rem 1.1rem;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.88rem;
}
.ptv-close-btn:hover { background: linear-gradient(135deg, #8b3a2a, #6d2727); }
</style>
