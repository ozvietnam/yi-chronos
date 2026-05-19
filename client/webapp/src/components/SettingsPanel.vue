<script setup>
import { ref, onMounted } from "vue";
import {
  listProviders,
  setProviderKey,
  setProviderNotes,
  testProvider,
  resetProviderHealth,
  PLAN_TYPE_LABEL,
  PROVIDER_DISPLAY
} from "../composables/useSettings.js";

const providers = ref([]);
const loading = ref(false);
const error = ref("");
const message = ref("");

// Per-provider local edit state
const keyInput = ref({});       // {name: string}
const notesInput = ref({});     // {name: string}
const planTypeInput = ref({});  // {name: string}
const testResult = ref({});     // {name: {status, latency, response_preview, error}}
const testing = ref({});        // {name: boolean}
const saving = ref({});

const planTypeOptions = Object.entries(PLAN_TYPE_LABEL).map(([k, v]) => ({
  value: k, ...v
}));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await listProviders();
    providers.value = r.providers || [];
    // Initialize local form state from server data
    for (const p of providers.value) {
      if (notesInput.value[p.name] === undefined) {
        notesInput.value[p.name] = p.notes || "";
      }
      if (planTypeInput.value[p.name] === undefined) {
        planTypeInput.value[p.name] = p.plan_type || "";
      }
    }
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

async function saveKey(p) {
  const key = (keyInput.value[p.name] || "").trim();
  if (!key) return;
  saving.value[p.name] = true;
  try {
    await setProviderKey(p.name, key);
    keyInput.value[p.name] = "";
    message.value = `✓ Đã lưu key cho ${p.display_name}`;
    await load();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    saving.value[p.name] = false;
    setTimeout(() => { message.value = ""; }, 4000);
  }
}

async function saveNotes(p) {
  saving.value[p.name] = true;
  try {
    await setProviderNotes(p.name, {
      planType: planTypeInput.value[p.name] || null,
      notes: notesInput.value[p.name] || ""
    });
    message.value = `✓ Đã lưu note cho ${p.display_name}`;
    await load();
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    saving.value[p.name] = false;
    setTimeout(() => { message.value = ""; }, 4000);
  }
}

async function runTest(p) {
  testing.value[p.name] = true;
  testResult.value[p.name] = null;
  try {
    const r = await testProvider(p.name);
    testResult.value[p.name] = r;
  } catch (e) {
    testResult.value[p.name] = { status: "error", error: String(e.message || e) };
  } finally {
    testing.value[p.name] = false;
  }
}

async function resetHealthClick() {
  await resetProviderHealth();
  message.value = "✓ Đã reset trạng thái unhealthy của tất cả providers";
  await load();
  setTimeout(() => { message.value = ""; }, 4000);
}

onMounted(load);
</script>

<template>
  <div class="settings-panel">
    <header class="page-head">
      <h2>⚙️ Cài đặt</h2>
      <button class="btn-ghost" @click="load" :disabled="loading">
        {{ loading ? "Đang tải..." : "↻ Refresh" }}
      </button>
    </header>

    <p v-if="message" class="msg ok">{{ message }}</p>
    <p v-if="error" class="msg error">{{ error }}</p>

    <section class="section">
      <header>
        <h3>🔑 AI Providers (API Keys + Ghi chú)</h3>
        <button class="btn-ghost-sm" @click="resetHealthClick">
          Reset unhealthy marks
        </button>
      </header>
      <p class="hint">
        Quản lý các nhà cung cấp LLM. Ollama (local) tự kết nối — chỉ cần cài
        <code>ollama serve</code> ở port 11434. Các provider cloud cần API key.
      </p>

      <div class="providers-list">
        <article
          v-for="p in providers"
          :key="p.name"
          class="provider-card"
          :class="{ configured: p.is_configured, unhealthy: p.is_unhealthy }"
        >
          <header class="pc-head">
            <div class="pc-title">
              <strong>{{ PROVIDER_DISPLAY[p.name]?.name || p.display_name }}</strong>
              <code class="pc-key">{{ p.name }}</code>
            </div>
            <div class="pc-status">
              <span v-if="p.is_configured" class="badge ok">✓ Configured</span>
              <span v-else class="badge off">✗ Chưa configure</span>
              <span v-if="p.is_unhealthy" class="badge warn">
                ⚠️ Unhealthy: {{ p.unhealthy_reason || "" }}
              </span>
            </div>
          </header>

          <div class="pc-meta">
            <div>
              <span class="ml">Default model:</span>
              <code>{{ p.default_model }}</code>
            </div>
            <details class="models-list" v-if="p.available_models?.length">
              <summary>{{ p.available_models.length }} models có sẵn</summary>
              <ul>
                <li v-for="m in p.available_models" :key="m"><code>{{ m }}</code></li>
              </ul>
            </details>
          </div>

          <!-- API Key input (skip for Ollama / mock) -->
          <div v-if="p.name !== 'ollama' && p.name !== 'mock'" class="pc-row">
            <label>
              <span>API Key {{ p.is_configured ? "(đã có — nhập để thay)" : "" }}:</span>
              <div class="key-row">
                <input
                  v-model="keyInput[p.name]"
                  type="password"
                  :placeholder="p.is_configured ? '••••••••••••••••' : 'sk-... hoặc API key của anh'"
                  autocomplete="off"
                />
                <button class="btn-primary" :disabled="!keyInput[p.name]?.trim() || saving[p.name]"
                        @click="saveKey(p)">
                  Lưu key
                </button>
              </div>
              <small v-if="PROVIDER_DISPLAY[p.name]?.website">
                Lấy key tại:
                <a :href="PROVIDER_DISPLAY[p.name].website" target="_blank">
                  {{ PROVIDER_DISPLAY[p.name].website }}
                </a>
              </small>
            </label>
          </div>

          <!-- Plan type -->
          <div class="pc-row">
            <label>
              <span>Loại plan:</span>
              <select v-model="planTypeInput[p.name]" @change="saveNotes(p)">
                <option value="">(chưa chọn)</option>
                <option v-for="opt in planTypeOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
              <small v-if="planTypeInput[p.name]" class="plan-desc">
                {{ PLAN_TYPE_LABEL[planTypeInput[p.name]]?.desc }}
              </small>
            </label>
          </div>

          <!-- Free-form notes -->
          <div class="pc-row">
            <label>
              <span>Ghi chú (anh ghi gì cũng được — quota, billing, mục đích...):</span>
              <textarea
                v-model="notesInput[p.name]"
                rows="2"
                placeholder="VD: $20/tháng coding plan · dùng cho conflict review · còn 90% quota"
                @blur="saveNotes(p)"
              ></textarea>
            </label>
          </div>

          <!-- Test button -->
          <div class="pc-row test-row">
            <button class="btn-test" :disabled="testing[p.name] || !p.is_configured" @click="runTest(p)">
              {{ testing[p.name] ? "Đang test..." : "🧪 Test kết nối" }}
            </button>
            <div v-if="testResult[p.name]" class="test-result"
                 :class="`tr-${testResult[p.name].status}`">
              <span v-if="testResult[p.name].status === 'ok'">
                ✓ OK · {{ testResult[p.name].latency_seconds }}s ·
                model <code>{{ testResult[p.name].model }}</code><br/>
                <em>"{{ testResult[p.name].response_preview }}"</em>
              </span>
              <span v-else-if="testResult[p.name].status === 'not_configured'">
                ⚠️ Provider chưa configured (thiếu key hoặc server tắt)
              </span>
              <span v-else>
                ✗ {{ testResult[p.name].error }}
              </span>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.settings-panel {
  padding: 1rem;
  color: #e2e8f0;
  max-width: 980px;
  margin: 0 auto;
}
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.page-head h2 { margin: 0; color: #c4b5fd; }
.btn-ghost {
  padding: 0.4rem 0.85rem;
  background: rgba(167, 139, 250, 0.1);
  color: #c4b5fd;
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-ghost-sm {
  padding: 0.25rem 0.6rem;
  background: rgba(100, 116, 139, 0.15);
  color: #94a3b8;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.75rem;
}
.btn-primary {
  padding: 0.4rem 0.85rem;
  background: #a78bfa;
  color: #1e1b4b;
  font-weight: 600;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-test {
  padding: 0.35rem 0.8rem;
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-test:disabled { opacity: 0.4; cursor: not-allowed; }

.msg {
  margin: 0 0 1rem;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
}
.msg.ok { background: rgba(34, 197, 94, 0.15); color: #86efac; }
.msg.error { background: rgba(239, 68, 68, 0.1); color: #fca5a5; }

.section { margin-bottom: 2rem; }
.section header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.section header h3 { margin: 0; color: #cbd5e1; }
.hint {
  color: #94a3b8;
  font-size: 0.85rem;
  margin: 0 0 1rem;
}
.hint code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 2px;
  font-size: 0.78rem;
}

.providers-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.provider-card {
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 0.85rem 1rem;
}
.provider-card.configured { border-left: 3px solid #86efac; }
.provider-card.unhealthy { border-left: 3px solid #f87171; }

.pc-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.pc-title { display: flex; align-items: baseline; gap: 0.5rem; }
.pc-title strong { color: #f1f5f9; font-size: 1rem; }
.pc-key {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.4rem;
  border-radius: 2px;
  color: #94a3b8;
  font-size: 0.75rem;
}
.pc-status { display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap; }
.badge {
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  font-size: 0.72rem;
}
.badge.ok { background: rgba(34, 197, 94, 0.15); color: #86efac; }
.badge.off { background: rgba(100, 116, 139, 0.15); color: #94a3b8; }
.badge.warn { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }

.pc-meta {
  margin-bottom: 0.75rem;
  font-size: 0.78rem;
  color: #94a3b8;
}
.ml { color: #64748b; margin-right: 0.3rem; }
.pc-meta code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 2px;
}
.models-list {
  margin-top: 0.4rem;
  font-size: 0.75rem;
}
.models-list summary {
  cursor: pointer;
  color: #94a3b8;
}
.models-list ul {
  list-style: none;
  padding: 0.3rem 0 0 0.5rem;
  margin: 0;
}
.models-list li { padding: 0.1rem 0; color: #cbd5e1; }

.pc-row {
  margin-bottom: 0.7rem;
}
.pc-row label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.82rem;
  color: #cbd5e1;
}
.pc-row label > span { color: #94a3b8; font-size: 0.8rem; }
.pc-row label small { color: #64748b; font-size: 0.72rem; }
.pc-row label small a { color: #93c5fd; text-decoration: underline; }
.plan-desc { font-style: italic; }

.key-row { display: flex; gap: 0.5rem; }
.key-row input {
  flex: 1;
  padding: 0.35rem 0.6rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 4px;
  font-family: monospace;
}
select, textarea {
  padding: 0.35rem 0.6rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  border-radius: 4px;
  font-family: inherit;
}
textarea { resize: vertical; min-height: 50px; }

.test-row {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  flex-wrap: wrap;
}
.test-result {
  flex: 1;
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  font-size: 0.82rem;
  min-width: 200px;
}
.test-result.tr-ok { background: rgba(34, 197, 94, 0.1); color: #86efac; }
.test-result.tr-error { background: rgba(239, 68, 68, 0.1); color: #fca5a5; }
.test-result.tr-not_configured { background: rgba(251, 191, 36, 0.1); color: #fbbf24; }
.test-result em { color: #cbd5e1; }
.test-result code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.1rem 0.3rem;
  border-radius: 2px;
}
</style>
