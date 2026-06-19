<script setup>
/**
 * HermesAdminPanel — Phòng Quản Trị Hermes (owner-only governance console).
 * 5 panel: Roster · Cổng duyệt (evolve) · Giám sát (metrics) · Chỉ huy (commander) · Audit.
 * Mọi hành động đụng não-chung (toggle/SOUL/duyệt) → owner xác nhận tay; commander chỉ đọc.
 */
import { ref, onMounted } from "vue";
import { sessionToken } from "../stores/authStore.js";

const tab = ref("roster"); // roster | evolve | metrics | commander | audit
const err = ref("");

function authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}
async function api(path, { method = "GET", body } = {}) {
  const r = await fetch(`/api/admin/hermes${path}`, {
    method, headers: authHeaders(), credentials: "include",
    body: body ? JSON.stringify(body) : undefined,
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.detail || `Lỗi ${r.status}`);
  return d;
}

// ── Roster ──────────────────────────────────────────────────────────────
const roster = ref([]);
async function loadRoster() {
  try { roster.value = (await api("/roster")).roster || []; err.value = ""; }
  catch (e) { err.value = e.message; }
}
async function toggleSage(tag) {
  if (!confirm(`Bật/tắt sage "${tag}"? (đụng não-chung)`)) return;
  try { await api(`/sage/${tag}/toggle`, { method: "POST" }); await loadRoster(); }
  catch (e) { err.value = e.message; }
}

// ── SOUL edit ───────────────────────────────────────────────────────────
const soulTag = ref(""); const soulText = ref(""); const soulBusy = ref(false);
async function openSoul(tag) {
  soulTag.value = tag; soulText.value = "…";
  try { soulText.value = (await api(`/sage/${tag}/soul`)).soul || ""; }
  catch (e) { err.value = e.message; soulTag.value = ""; }
}
async function saveSoul() {
  if (!confirm(`Lưu SOUL "${soulTag.value}"? (ghi audit + đổi persona)`)) return;
  soulBusy.value = true;
  try { await api(`/sage/${soulTag.value}/soul`, { method: "PUT", body: { content: soulText.value } });
    soulTag.value = ""; await loadRoster(); }
  catch (e) { err.value = e.message; }
  finally { soulBusy.value = false; }
}

// ── Evolve (cổng duyệt) ──────────────────────────────────────────────────
const pending = ref([]);
async function loadEvolve() {
  try { pending.value = (await api("/evolve/pending")).pending || []; err.value = ""; }
  catch (e) { err.value = e.message; }
}
async function reviewEvolve(id, approve) {
  if (!confirm(`${approve ? "DUYỆT" : "BÁC"} đề xuất #${id}?`)) return;
  try { await api(`/evolve/${id}/review`, { method: "POST", body: { approve, note: "" } }); await loadEvolve(); }
  catch (e) { err.value = e.message; }
}

// ── Metrics ───────────────────────────────────────────────────────────────
const metrics = ref(null);
async function loadMetrics() {
  try { metrics.value = (await api("/metrics")).metrics; err.value = ""; }
  catch (e) { err.value = e.message; }
}

// ── Commander ───────────────────────────────────────────────────────────
const cmdQ = ref(""); const cmdAns = ref(null); const cmdBusy = ref(false);
async function askCommander() {
  if (!cmdQ.value.trim()) return;
  cmdBusy.value = true; cmdAns.value = null;
  try { cmdAns.value = await api("/commander/ask", { method: "POST", body: { question: cmdQ.value } }); }
  catch (e) { err.value = e.message; }
  finally { cmdBusy.value = false; }
}

// ── Audit ─────────────────────────────────────────────────────────────────
const audit = ref([]);
async function loadAudit() {
  try { audit.value = (await api("/audit")).audit || []; err.value = ""; }
  catch (e) { err.value = e.message; }
}

function switchTab(t) {
  tab.value = t;
  if (t === "roster") loadRoster();
  else if (t === "evolve") loadEvolve();
  else if (t === "metrics") loadMetrics();
  else if (t === "audit") loadAudit();
}
function fmtTime(ts) { try { return new Date(ts * 1000).toLocaleString("vi-VN"); } catch { return ts; } }
onMounted(loadRoster);
</script>

<template>
  <div class="hermes-admin">
    <h2>🛡️ Phòng Quản Trị Hermes</h2>
    <p class="sub">Owner-only · mọi hành động được audit · chỉ huy chỉ đọc + đề xuất.</p>

    <nav class="ha-tabs">
      <button :class="{ on: tab === 'roster' }" @click="switchTab('roster')">Roster</button>
      <button :class="{ on: tab === 'evolve' }" @click="switchTab('evolve')">Cổng duyệt</button>
      <button :class="{ on: tab === 'metrics' }" @click="switchTab('metrics')">Giám sát</button>
      <button :class="{ on: tab === 'commander' }" @click="switchTab('commander')">Chỉ huy</button>
      <button :class="{ on: tab === 'audit' }" @click="switchTab('audit')">Audit</button>
    </nav>

    <p v-if="err" class="ha-err">{{ err }}</p>

    <!-- Roster -->
    <section v-if="tab === 'roster'">
      <table class="ha-table">
        <thead><tr><th></th><th>Vai</th><th>Chuyên môn</th><th>SOUL</th><th>v</th><th></th></tr></thead>
        <tbody>
          <tr v-for="s in roster" :key="s.tag">
            <td>{{ s.icon }}</td>
            <td><b>{{ s.name_vi }}</b><br><small>{{ s.tag }}</small></td>
            <td><small>{{ s.specialty }}</small></td>
            <td><small>{{ s.soul_size }}b{{ s.soul_overridden ? " ✎" : "" }}</small></td>
            <td><small>{{ s.knowledge_version }}</small></td>
            <td class="ha-actions">
              <button class="mini" @click="toggleSage(s.tag)">{{ s.enabled ? "🟢 Bật" : "⚪ Tắt" }}</button>
              <button class="mini" @click="openSoul(s.tag)">SOUL</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="soulTag" class="ha-soul">
        <h4>Sửa SOUL — {{ soulTag }}</h4>
        <textarea v-model="soulText" rows="14"></textarea>
        <div>
          <button @click="saveSoul" :disabled="soulBusy">{{ soulBusy ? "Đang lưu…" : "Lưu (audit)" }}</button>
          <button class="ghost" @click="soulTag = ''">Đóng</button>
        </div>
      </div>
    </section>

    <!-- Evolve -->
    <section v-else-if="tab === 'evolve'">
      <p v-if="!pending.length" class="muted">Không có đề xuất chờ duyệt.</p>
      <div v-for="p in pending" :key="p.id" class="ha-card">
        <div><b>#{{ p.id }} · {{ p.kind }}</b> <span class="badge">{{ p.impact }}</span>
          <span class="badge">tin {{ p.confidence }}</span></div>
        <div>{{ p.title }}</div>
        <div class="ha-actions">
          <button class="mini" @click="reviewEvolve(p.id, true)">Duyệt</button>
          <button class="mini ghost" @click="reviewEvolve(p.id, false)">Bác</button>
        </div>
      </div>
    </section>

    <!-- Metrics -->
    <section v-else-if="tab === 'metrics'">
      <div v-if="metrics" class="ha-metrics">
        <div class="m-card"><span class="m-num">{{ metrics.spend?.total_usd ?? "?" }}$</span>
          <span class="m-lbl">/ {{ metrics.spend?.budget_usd ?? "?" }}$ hôm nay</span></div>
        <div class="m-card"><span class="m-num">{{ metrics.paradigm_flags }}</span><span class="m-lbl">cờ paradigm</span></div>
        <div class="m-card"><span class="m-num">{{ metrics.evolve_pending }}</span><span class="m-lbl">chờ duyệt</span></div>
      </div>
      <div v-if="metrics?.by_method" class="ha-byfeat">
        <span v-for="(n, m) in metrics.by_method" :key="m" class="badge">{{ m }}: {{ n }}</span>
      </div>
    </section>

    <!-- Commander -->
    <section v-else-if="tab === 'commander'">
      <p class="muted">Hỏi chỉ huy (operator): "hệ thống thế nào?", "có gì chờ duyệt?"…</p>
      <textarea v-model="cmdQ" rows="2" placeholder="Câu hỏi quản trị…"></textarea>
      <button @click="askCommander" :disabled="cmdBusy">{{ cmdBusy ? "…" : "Hỏi" }}</button>
      <div v-if="cmdAns" class="ha-card">
        <p>{{ cmdAns.answer }}</p>
        <small class="muted">{{ cmdAns.note }}</small>
      </div>
    </section>

    <!-- Audit -->
    <section v-else-if="tab === 'audit'">
      <p v-if="!audit.length" class="muted">Chưa có nhật ký.</p>
      <table class="ha-table" v-else>
        <thead><tr><th>Khi</th><th>Hành động</th><th>Chi tiết</th></tr></thead>
        <tbody>
          <tr v-for="a in audit" :key="a.id">
            <td><small>{{ fmtTime(a.created_at) }}</small></td>
            <td>{{ a.action }}</td>
            <td><small>{{ JSON.stringify(a.details) }}</small></td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.hermes-admin { max-width: 920px; margin: 0 auto; color: var(--read-fg, inherit); }
.hermes-admin h2 { margin-bottom: .2rem; }
.sub, .muted { color: var(--read-muted, #888); font-size: .85rem; }
.ha-tabs { display: flex; gap: .4rem; flex-wrap: wrap; margin: .8rem 0; }
.ha-tabs button { padding: .35rem .8rem; border: 1px solid var(--read-border, #ccc);
  background: transparent; border-radius: 6px; cursor: pointer; color: inherit; }
.ha-tabs button.on { background: var(--read-accent, #6b4); color: #fff; border-color: transparent; }
.ha-err { color: #c33; background: var(--read-err-bg, #fee); padding: .4rem .6rem; border-radius: 6px; }
.ha-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.ha-table th, .ha-table td { text-align: left; padding: .35rem .4rem;
  border-bottom: 1px solid var(--read-border, #eee); vertical-align: top; }
.ha-actions { display: flex; gap: .3rem; }
button.mini { padding: .2rem .5rem; font-size: .8rem; border: 1px solid var(--read-border, #ccc);
  background: transparent; border-radius: 5px; cursor: pointer; color: inherit; }
button.ghost { opacity: .7; }
.ha-card { border: 1px solid var(--read-border, #ddd); border-radius: 8px; padding: .6rem; margin: .5rem 0; }
.badge { display: inline-block; font-size: .75rem; padding: .1rem .45rem; margin-left: .3rem;
  border: 1px solid var(--read-border, #ccc); border-radius: 10px; }
.ha-soul { margin-top: 1rem; border-top: 1px dashed var(--read-border, #ccc); padding-top: .8rem; }
.ha-soul textarea, .hermes-admin textarea { width: 100%; font-family: inherit; font-size: .9rem;
  background: var(--read-bg, #fff); color: inherit; border: 1px solid var(--read-border, #ccc);
  border-radius: 6px; padding: .5rem; }
.ha-metrics { display: flex; gap: 1rem; flex-wrap: wrap; margin: .6rem 0; }
.m-card { border: 1px solid var(--read-border, #ddd); border-radius: 10px; padding: .7rem 1rem; }
.m-num { font-size: 1.5rem; font-weight: 700; display: block; }
.m-lbl { font-size: .8rem; color: var(--read-muted, #888); }
.ha-byfeat { display: flex; gap: .4rem; flex-wrap: wrap; }
</style>
