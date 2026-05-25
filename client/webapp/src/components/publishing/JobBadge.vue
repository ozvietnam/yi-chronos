<script setup>
/**
 * JobBadge — compact badge on Library header showing active OCR jobs.
 *
 * Expand → panel với danh sách active + recent jobs + cancel button.
 *
 * Props:
 *   active-jobs  — list of currently running/pending jobs
 *   recent-jobs  — recent completed jobs (last 10)
 *   expanded     — boolean: show full panel
 *
 * Emits:
 *   toggle()
 *   cancel(job_id)
 */
import { computed } from "vue";

const props = defineProps({
  activeJobs: { type: Array, default: () => [] },
  recentJobs: { type: Array, default: () => [] },
  expanded: { type: Boolean, default: false },
});
const emit = defineEmits(["toggle", "cancel"]);

const primaryJob = computed(() => props.activeJobs[0] || null);

const compactText = computed(() => {
  if (!primaryJob.value) return "Không có job nào đang chạy";
  const j = primaryJob.value;
  const cur = j.progress?.current || 0;
  const total = j.progress?.total || 0;
  const pct = total > 0 ? Math.round((cur / total) * 100) : 0;
  return `🔍 ${j.book_id} — ${cur}/${total} (${pct}%)`;
});

const etaText = computed(() => {
  const eta = primaryJob.value?.eta_seconds;
  if (eta == null) return "";
  if (eta < 60) return `~${eta}s`;
  if (eta < 3600) return `~${Math.round(eta / 60)}p`;
  return `~${Math.floor(eta / 3600)}h${Math.round((eta % 3600) / 60)}p`;
});

function statusIcon(status) {
  return { running: "🔍", done: "✅", failed: "❌", cancelled: "🛑", pending: "⏳" }[status] || "❓";
}

function statusLabel(status) {
  return (
    { running: "Đang chạy", done: "Xong", failed: "Lỗi", cancelled: "Đã huỷ", pending: "Chờ" }[
      status
    ] || status
  );
}

function formatTime(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
}

function pctOf(j) {
  const t = j.progress?.total || 0;
  if (t === 0) return 0;
  return Math.round(((j.progress?.current || 0) / t) * 100);
}
</script>

<template>
  <div class="job-badge" :class="{ expanded }">
    <button type="button" class="badge-compact" @click="emit('toggle')">
      <span class="badge-text">{{ compactText }}</span>
      <span v-if="etaText" class="badge-eta">· còn {{ etaText }}</span>
      <span class="badge-arrow">{{ expanded ? "▾" : "▸" }}</span>
    </button>

    <div v-if="expanded" class="badge-panel">
      <div v-if="activeJobs.length === 0" class="empty-active">
        Không có job nào đang chạy.
      </div>
      <div v-else class="active-list">
        <h4>🔍 Đang chạy ({{ activeJobs.length }})</h4>
        <div v-for="j in activeJobs" :key="j.job_id" class="job-row job-active">
          <div class="job-head">
            <span class="job-icon">{{ statusIcon(j.status) }}</span>
            <strong>{{ j.book_id }}</strong>
            <code class="job-id">{{ j.job_id }}</code>
            <button type="button" class="cancel-btn" @click="emit('cancel', j.job_id)">
              ✕ Huỷ
            </button>
          </div>
          <div class="job-bar-row">
            <div class="job-bar-wrap">
              <div class="job-bar" :style="{ width: pctOf(j) + '%' }"></div>
            </div>
            <span class="job-bar-text">
              {{ j.progress?.current || 0 }}/{{ j.progress?.total || 0 }}
              ({{ pctOf(j) }}%)
            </span>
          </div>
          <div class="job-meta">
            Stage: <em>{{ j.progress?.stage || "—" }}</em>
            <span v-if="j.started_at"> · Bắt đầu {{ formatTime(j.started_at) }}</span>
            <span v-if="j.eta_seconds != null"> · ETA {{ Math.round(j.eta_seconds / 60) }}p</span>
          </div>
        </div>
      </div>

      <div v-if="recentJobs.length" class="recent-list">
        <h4>Lịch sử gần đây ({{ recentJobs.length }})</h4>
        <div
          v-for="j in recentJobs.filter(jj => !activeJobs.find(aj => aj.job_id === jj.job_id))"
          :key="j.job_id"
          class="job-row"
        >
          <span class="job-icon">{{ statusIcon(j.status) }}</span>
          <strong>{{ j.book_id }}</strong>
          <span class="job-status">{{ statusLabel(j.status) }}</span>
          <span v-if="j.ended_at" class="job-time">{{ formatTime(j.ended_at) }}</span>
          <span v-if="j.error" class="job-error" :title="j.error">
            ⚠ {{ j.error.substring(0, 50) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.job-badge {
  margin: 0.25rem 0;
}

.badge-compact {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 180, 60, 0.12);
  border: 1px solid rgba(255, 180, 60, 0.3);
  color: #ffd88a;
  padding: 0.55rem 0.95rem;
  border-radius: 8px;
  font-size: 0.88rem;
  cursor: pointer;
  text-align: left;
}

.badge-compact:hover {
  background: rgba(255, 180, 60, 0.2);
}

.badge-text {
  flex: 1;
  font-weight: 600;
}

.badge-eta {
  color: rgba(255, 216, 138, 0.7);
  font-size: 0.82rem;
}

.badge-arrow {
  font-size: 0.85rem;
  opacity: 0.7;
}

.badge-panel {
  margin-top: 0.5rem;
  background: rgba(40, 25, 12, 0.6);
  border: 1px solid rgba(255, 180, 60, 0.25);
  border-radius: 8px;
  padding: 0.85rem 1rem;
}

.badge-panel h4 {
  margin: 0 0 0.5rem;
  font-size: 0.88rem;
  color: #ffd88a;
}

.empty-active {
  color: rgba(220, 200, 240, 0.5);
  font-size: 0.88rem;
  padding: 0.5rem 0;
}

.active-list,
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.recent-list {
  margin-top: 0.85rem;
  padding-top: 0.85rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.job-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  font-size: 0.85rem;
  color: #e0d3ff;
  flex-wrap: wrap;
}

.job-row.job-active {
  flex-direction: column;
  align-items: stretch;
  background: rgba(255, 180, 60, 0.06);
  border: 1px solid rgba(255, 180, 60, 0.18);
  padding: 0.55rem 0.7rem;
}

.job-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.job-head strong {
  color: #ffd88a;
}

.job-id {
  font-family: monospace;
  font-size: 0.74rem;
  color: rgba(220, 200, 240, 0.5);
  background: rgba(255, 255, 255, 0.04);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  margin-left: auto;
}

.cancel-btn {
  background: rgba(255, 100, 100, 0.18);
  border: 1px solid rgba(255, 100, 100, 0.35);
  color: #ff9aa0;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.78rem;
  cursor: pointer;
}

.cancel-btn:hover {
  background: rgba(255, 100, 100, 0.32);
}

.job-bar-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.4rem;
}

.job-bar-wrap {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.job-bar {
  height: 100%;
  background: linear-gradient(90deg, #ffb74d, #ff9800);
  transition: width 0.4s ease;
}

.job-bar-text {
  font-size: 0.78rem;
  font-variant-numeric: tabular-nums;
  color: rgba(220, 200, 240, 0.8);
}

.job-meta {
  margin-top: 0.25rem;
  font-size: 0.76rem;
  color: rgba(220, 200, 240, 0.6);
}

.job-meta em {
  color: #d8c7ff;
  font-style: normal;
}

.job-status {
  font-size: 0.78rem;
  color: rgba(220, 200, 240, 0.65);
}

.job-time {
  margin-left: auto;
  font-variant-numeric: tabular-nums;
  font-size: 0.78rem;
  color: rgba(220, 200, 240, 0.5);
}

.job-error {
  flex-basis: 100%;
  font-size: 0.75rem;
  color: #ff9aa0;
  padding-left: 1.5rem;
}
</style>
