<script setup>
/**
 * YI-Hermes Chat — floating concierge chat overlay.
 *
 * Pinned to bottom-right corner, expands when clicked.
 * Context-aware: knows active tab + active person.
 */

import { computed, nextTick, ref, watch } from "vue";
import { yiHermesChat } from "../lib/api";
import { activePerson } from "../stores/profileStore.js";

const props = defineProps({
  activeTab: { type: String, default: "" },
});

const isOpen = ref(false);
const turns = ref([]);   // {role: 'user'|'hermes', content, intent?, tokens_used?}
const inputText = ref("");
const sending = ref(false);
const errorMsg = ref("");
const messagesRef = ref(null);

const personContext = computed(() => {
  const p = activePerson.value;
  return p
    ? {
        active_person_name: p.name,
        active_person_birth: p.birth_datetime_local,
        user_gender: p.gender || "nam",
      }
    : {};
});

const placeholderText = computed(() =>
  turns.value.length === 0
    ? "Chào em! Hỏi em về tử vi, thuật ngữ, hoặc lá số đang xem..."
    : "Anh hỏi tiếp..."
);

async function scrollToBottom() {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
}

async function sendMessage() {
  const msg = inputText.value.trim();
  if (!msg || sending.value) return;

  turns.value.push({ role: "user", content: msg });
  inputText.value = "";
  sending.value = true;
  errorMsg.value = "";
  await scrollToBottom();

  try {
    const ctx = {
      active_tab: props.activeTab,
      ...personContext.value,
    };
    const result = await yiHermesChat({
      userMessage: msg,
      context: ctx,
      history: turns.value.slice(0, -1).map((t) => ({
        role: t.role,
        content: t.content,
        intent: t.intent || "",
        tokens_used: t.tokens_used || 0,
      })),
    });
    const r = result.response;
    turns.value.push({
      role: "hermes",
      content: r.content,
      intent: r.intent,
      provider: r.provider,
      model: r.model,
      tokens_used: r.tokens_used,
      suggest_council: r.suggest_council,
    });
  } catch (err) {
    errorMsg.value = err?.message || String(err);
  } finally {
    sending.value = false;
    await scrollToBottom();
  }
}

function clearChat() {
  turns.value = [];
  errorMsg.value = "";
}

const quickPrompts = [
  { label: "🔎 Giải thích Dụng Thần", text: "Dụng Thần" },
  { label: "📖 Đọc chart hiện tại", text: "Đọc giúp em chart em đang xem" },
  { label: "🏛️ 7 trường phái khác nhau thế nào?", text: "Cho em hỏi 7 trường phái Đông Tây khác nhau gì" },
  { label: "⚖️ Hỏi Hội Đồng", text: "Em muốn hỏi Hội Đồng về quyết định lớn" },
];

function useQuickPrompt(text) {
  inputText.value = text;
}

function intentBadge(intent) {
  const map = {
    greeting: { emoji: "👋", label: "chào" },
    glossary_hit: { emoji: "📚", label: "từ điển" },
    question: { emoji: "💭", label: "câu hỏi" },
    question_fallback: { emoji: "🔄", label: "fallback" },
    route_to_council: { emoji: "⚖️", label: "→ hội đồng" },
  };
  return map[intent] || { emoji: "💬", label: intent };
}
</script>

<template>
  <!-- Floating button -->
  <button
    v-if="!isOpen"
    class="hermes-fab"
    type="button"
    @click="isOpen = true"
    title="Chat với Hermes — trợ lý YI-CHRONOS"
  >
    <span class="fab-icon">💬</span>
    <span class="fab-text">Hermes</span>
  </button>

  <!-- Chat overlay -->
  <Teleport to="body">
    <div v-if="isOpen" class="hermes-overlay">
      <div class="hermes-panel">
        <header class="hermes-header">
          <div class="header-title">
            <span class="header-icon">💬</span>
            <div>
              <h3>Hermes</h3>
              <small>Trợ lý YI-CHRONOS</small>
            </div>
          </div>
          <div class="header-actions">
            <button type="button" class="icon-btn" @click="clearChat" title="Xoá lịch sử trong cuộc trò chuyện">
              🗑
            </button>
            <button type="button" class="icon-btn close" @click="isOpen = false" title="Đóng">
              ×
            </button>
          </div>
        </header>

        <div class="hermes-messages" ref="messagesRef">
          <!-- Welcome / quick prompts when empty -->
          <div v-if="turns.length === 0" class="welcome">
            <p class="welcome-greeting">
              <b>Chào anh!</b> Em là Hermes — trợ lý hiểu mọi module của YI-CHRONOS.
            </p>
            <p class="welcome-hint">
              Em có thể: giải thích thuật ngữ tử vi · đọc chart đang xem · gọi Hội Đồng cho câu hỏi quan trọng.
            </p>
            <div class="quick-prompts">
              <button
                v-for="qp in quickPrompts"
                :key="qp.label"
                type="button"
                class="quick-prompt"
                @click="useQuickPrompt(qp.text)"
              >
                {{ qp.label }}
              </button>
            </div>
          </div>

          <!-- Turn list -->
          <div v-for="(t, i) in turns" :key="i" class="turn" :data-role="t.role">
            <div class="turn-bubble">
              <header v-if="t.role === 'hermes' && t.intent" class="turn-meta">
                <span class="intent-badge">
                  {{ intentBadge(t.intent).emoji }} {{ intentBadge(t.intent).label }}
                </span>
                <span v-if="t.provider" class="provider-tag">{{ t.provider }}</span>
                <span v-if="t.tokens_used > 0" class="token-tag">{{ t.tokens_used }}t</span>
              </header>
              <div class="turn-content" v-html="renderMarkdown(t.content)"></div>
              <div v-if="t.suggest_council" class="council-cta">
                <button type="button" class="council-btn">⚖️ Gọi Hội Đồng (sắp có)</button>
              </div>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="sending" class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <div class="hermes-input-row">
          <textarea
            v-model="inputText"
            class="hermes-input"
            :placeholder="placeholderText"
            rows="2"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
          <button
            type="button"
            class="send-btn"
            :disabled="sending || !inputText.trim()"
            @click="sendMessage"
          >
            {{ sending ? "..." : "↑" }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
/* Inline markdown renderer (light) — bold, italic, code, paragraph, lists. */
function renderMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Bold + italic
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
  // Inline code
  html = html.replace(/`(.+?)`/g, "<code>$1</code>");
  // Line breaks → <br>; double break → paragraph
  html = html.split("\n\n").map((para) => {
    if (/^[-•*] /m.test(para)) {
      const items = para.split(/\n/).map((line) => line.replace(/^[-•*]\s+/, "")).filter(Boolean);
      return "<ul>" + items.map((i) => `<li>${i}</li>`).join("") + "</ul>";
    }
    return `<p>${para.replace(/\n/g, "<br>")}</p>`;
  }).join("");
  return html;
}

export default { methods: { renderMarkdown } };
</script>

<style scoped>
.hermes-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 950;
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #5be5d3, #e8c95a);
  color: #0a0e14;
  border: none;
  border-radius: 999px;
  padding: 12px 18px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(91, 229, 211, 0.35);
  transition: transform 0.15s, box-shadow 0.15s;
}
.hermes-fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(91, 229, 211, 0.45);
}
.fab-icon { font-size: 18px; }

.hermes-overlay {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
  width: min(420px, calc(100vw - 32px));
  max-height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
  pointer-events: none;
}
.hermes-overlay > * { pointer-events: auto; }

.hermes-panel {
  background: linear-gradient(180deg, rgba(20, 30, 45, 0.97) 0%, rgba(12, 18, 28, 0.97) 100%);
  border: 1px solid rgba(91, 229, 211, 0.3);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  max-height: 70vh;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(8px);
  overflow: hidden;
}

.hermes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(91, 229, 211, 0.05);
}
.header-title { display: flex; align-items: center; gap: 10px; }
.header-icon { font-size: 22px; }
.header-title h3 { margin: 0; font-size: 15px; color: var(--accent-teal, #5be5d3); }
.header-title small { display: block; font-size: 10.5px; color: var(--text-muted, rgba(230, 238, 245, 0.5)); }
.header-actions { display: flex; gap: 4px; }
.icon-btn {
  background: transparent;
  border: none;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-size: 16px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}
.icon-btn:hover { background: rgba(255, 255, 255, 0.06); color: var(--accent-gold, #e8c95a); }
.icon-btn.close { font-size: 22px; }

.hermes-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.welcome { display: flex; flex-direction: column; gap: 8px; }
.welcome-greeting {
  margin: 0;
  font-size: 13px;
  color: var(--text-primary, #e6eef5);
  line-height: 1.5;
}
.welcome-greeting b { color: var(--accent-gold-soft, #f5e6b1); }
.welcome-hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  line-height: 1.5;
}
.quick-prompts { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
.quick-prompt {
  background: rgba(91, 229, 211, 0.06);
  border: 1px solid rgba(91, 229, 211, 0.22);
  color: var(--accent-teal, #5be5d3);
  padding: 7px 11px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  text-align: left;
}
.quick-prompt:hover { background: rgba(91, 229, 211, 0.14); }

.turn { display: flex; }
.turn[data-role="user"] { justify-content: flex-end; }
.turn[data-role="hermes"] { justify-content: flex-start; }

.turn-bubble {
  max-width: 86%;
  padding: 9px 12px;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.55;
}
.turn[data-role="user"] .turn-bubble {
  background: linear-gradient(135deg, rgba(232, 201, 90, 0.12), rgba(232, 201, 90, 0.06));
  border: 1px solid rgba(232, 201, 90, 0.28);
  color: var(--text-primary, #e6eef5);
  border-top-right-radius: 3px;
}
.turn[data-role="hermes"] .turn-bubble {
  background: rgba(91, 229, 211, 0.05);
  border: 1px solid rgba(91, 229, 211, 0.18);
  color: var(--text-secondary, rgba(230, 238, 245, 0.85));
  border-top-left-radius: 3px;
}

.turn-meta {
  display: flex;
  gap: 5px;
  margin-bottom: 5px;
  font-size: 10px;
  flex-wrap: wrap;
}
.intent-badge {
  background: rgba(91, 229, 211, 0.15);
  color: var(--accent-teal, #5be5d3);
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 700;
}
.provider-tag, .token-tag {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  padding: 1px 5px;
  border-radius: 2px;
  font-family: ui-monospace, monospace;
}

.turn-content :deep(p) { margin: 4px 0; }
.turn-content :deep(p:first-child) { margin-top: 0; }
.turn-content :deep(p:last-child) { margin-bottom: 0; }
.turn-content :deep(strong) { color: var(--accent-gold-soft, #f5e6b1); }
.turn-content :deep(em) { color: var(--accent-teal, #5be5d3); font-style: normal; }
.turn-content :deep(code) {
  background: rgba(0, 0, 0, 0.3);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  color: var(--accent-teal, #5be5d3);
}
.turn-content :deep(ul) {
  margin: 5px 0;
  padding-left: 20px;
}
.turn-content :deep(li) {
  margin: 2px 0;
  font-size: 12.5px;
}

.council-cta { margin-top: 8px; }
.council-btn {
  background: linear-gradient(135deg, #e8c95a, #d68a4a);
  color: #0a0e14;
  border: none;
  padding: 6px 12px;
  border-radius: 5px;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
}
.typing-indicator span {
  width: 6px;
  height: 6px;
  background: var(--accent-teal, #5be5d3);
  border-radius: 50%;
  animation: typing-bounce 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.15s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.3s; }
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.error-msg {
  margin: 0 16px 8px 16px;
  padding: 6px 10px;
  background: rgba(214, 90, 74, 0.1);
  color: #f5b08c;
  border-radius: 4px;
  font-size: 11.5px;
}

.hermes-input-row {
  display: flex;
  gap: 6px;
  padding: 10px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.2);
}
.hermes-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: var(--text-primary, #e6eef5);
  padding: 8px 10px;
  font-size: 13px;
  resize: none;
  font-family: inherit;
}
.hermes-input:focus {
  outline: none;
  border-color: var(--accent-teal, #5be5d3);
}
.send-btn {
  background: var(--accent-teal, #5be5d3);
  color: #0a0e14;
  border: none;
  width: 38px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
}
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.send-btn:not(:disabled):hover { background: var(--accent-gold, #e8c95a); }

@media (max-width: 480px) {
  .hermes-overlay {
    width: calc(100vw - 16px);
    bottom: 16px;
    right: 8px;
  }
  .hermes-fab { bottom: 16px; right: 16px; padding: 10px 14px; }
  .fab-text { display: none; }
}
</style>
