<script setup>
/**
 * WalletModal — VÍ XU CỦA TÔI (user tự quản): số dư · lượt free hôm nay · điểm danh
 * nhận xu · nhập mã quà (RedeemCodeWidget) · lịch sử cộng/trừ.
 * Gọi GET /api/wallet + /api/wallet/transactions + POST /api/wallet/claim-daily
 * (login, session). Trước đây chỉ AdminPanel có UI xu (quản người khác) — user thường
 * không có chỗ xem ví mình (Anh phát hiện gap 2026-07-02).
 */
import { ref, onMounted } from "vue";
import { sessionToken } from "../stores/authStore.js";
import RedeemCodeWidget from "./RedeemCodeWidget.vue";

const emit = defineEmits(["close"]);

const wallet = ref(null);      // {balance, xu_cost, free_quick_remaining, free_quick_per_day, daily_bonus_xu}
const tx = ref([]);
const loading = ref(true);
const claimBusy = ref(false);
const claimMsg = ref("");
const claimOk = ref(false);

function authHeaders(json = false) {
  const h = json ? { "Content-Type": "application/json" } : {};
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

async function load() {
  loading.value = true;
  try {
    const [w, t] = await Promise.all([
      fetch("/api/wallet", { headers: authHeaders(), credentials: "include" }).then((r) => r.ok ? r.json() : null),
      fetch("/api/wallet/transactions?limit=40", { headers: authHeaders(), credentials: "include" }).then((r) => r.ok ? r.json() : null),
    ]);
    wallet.value = w;
    tx.value = (t && t.transactions) || [];
  } catch (e) { /* giữ im — hiện trạng thái rỗng */ }
  finally { loading.value = false; }
}

async function claimDaily() {
  if (claimBusy.value) return;
  claimBusy.value = true; claimMsg.value = ""; claimOk.value = false;
  try {
    const r = await fetch("/api/wallet/claim-daily", {
      method: "POST", headers: authHeaders(true), credentials: "include", body: "{}",
    });
    const d = await r.json();
    if (d.ok || d.status === "ok" || d.claimed) {
      claimOk.value = true;
      claimMsg.value = d.xu ? `🎉 +${d.xu} xu điểm danh!` : "Đã nhận thưởng hôm nay.";
    } else {
      claimMsg.value = d.reason === "already_claimed" || d.already_claimed
        ? "Hôm nay Anh đã điểm danh rồi — mai quay lại nhé." : (d.reason || "Chưa nhận được, thử lại sau.");
    }
    await load();  // refresh số dư + lịch sử
  } catch (e) { claimMsg.value = String(e.message || e); }
  finally { claimBusy.value = false; }
}

// nhãn thân thiện cho reason ledger (khớp _CAT_SQL của xu_wallet)
function reasonLabel(reason) {
  if (!reason) return "Giao dịch";
  if (reason.startsWith("cross_paradigm")) return "Gieo Duyên";
  if (reason.startsWith("refund")) return "Hoàn xu";
  if (reason.startsWith("admin:")) return "Điều chỉnh (admin)";
  if (/daily|bonus|welcome|login/i.test(reason)) return "Điểm danh / thưởng";
  const M = { hermes_quick: "Hỏi nhanh Hermes", hermes_council: "Hội đồng Hermes",
    tu_vi_phe_menh_sau: "Đọc sâu lá số", promo: "Mã quà", topup: "Nạp xu" };
  return M[reason] || reason;
}
function fmtDay(ts, day) {
  if (day) return day;
  try { return new Date((ts || 0) * 1000).toLocaleDateString("vi-VN"); } catch { return ""; }
}

onMounted(load);
</script>

<template>
  <div class="wm-overlay" @click.self="emit('close')">
    <div class="wm-card" role="dialog" aria-label="Ví xu của tôi">
      <div class="wm-head">
        <h3>🪙 Ví xu của tôi</h3>
        <button class="wm-x" @click="emit('close')" aria-label="Đóng">✕</button>
      </div>

      <div v-if="loading" class="wm-loading">Đang tải ví…</div>

      <template v-else-if="wallet">
        <!-- Số dư -->
        <div class="wm-balance">
          <div class="wm-bal-num">{{ wallet.balance ?? 0 }}</div>
          <div class="wm-bal-lbl">xu đang có</div>
        </div>

        <!-- Free hôm nay -->
        <div class="wm-free" v-if="wallet.free_quick_per_day">
          Hỏi nhanh miễn phí hôm nay: <b>{{ wallet.free_quick_remaining ?? 0 }}/{{ wallet.free_quick_per_day }}</b>
          <span class="wm-hint"> · luận sâu 1 lượt = {{ wallet.xu_cost ?? 30 }} xu</span>
        </div>

        <!-- Điểm danh -->
        <button class="wm-claim" :disabled="claimBusy" @click="claimDaily">
          {{ claimBusy ? "…" : `🎁 Điểm danh nhận ${wallet.daily_bonus_xu || ''} xu` }}
        </button>
        <p v-if="claimMsg" class="wm-claim-msg" :class="{ ok: claimOk }">{{ claimMsg }}</p>

        <!-- Nhập mã quà (tái dùng widget sẵn) -->
        <RedeemCodeWidget @redeemed="load" />

        <!-- Lịch sử -->
        <div class="wm-tx-head">Lịch sử gần đây</div>
        <div v-if="!tx.length" class="wm-tx-empty">Chưa có giao dịch nào.</div>
        <ul v-else class="wm-tx">
          <li v-for="(t, i) in tx" :key="i" class="wm-tx-row">
            <span class="wm-tx-reason">{{ reasonLabel(t.reason) }}</span>
            <span class="wm-tx-day">{{ fmtDay(t.ts, t.day) }}</span>
            <span class="wm-tx-delta" :class="t.delta >= 0 ? 'plus' : 'minus'">
              {{ t.delta >= 0 ? "+" : "" }}{{ t.delta }}
            </span>
          </li>
        </ul>
      </template>

      <div v-else class="wm-loading">Cần đăng nhập để xem ví.</div>
    </div>
  </div>
</template>

<style scoped>
.wm-overlay { position: fixed; inset: 0; z-index: 1600; display: flex;
  align-items: flex-start; justify-content: center; padding: 6vh 1rem 2rem;
  background: rgba(0, 0, 0, 0.6); overflow-y: auto; }
.wm-card { width: 100%; max-width: 440px; border-radius: 14px;
  border: 1px solid var(--read-border, rgba(255,255,255,0.14));
  background: var(--read-surface, #171a1f); color: var(--read-text, #e6eef5);
  box-shadow: 0 24px 60px rgba(0,0,0,0.5); padding: 1.1rem 1.2rem 1.3rem; }
.wm-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.7rem; }
.wm-head h3 { margin: 0; font-size: 1.1rem; color: var(--read-heading, inherit); }
.wm-x { background: none; border: none; color: var(--read-text-faint, #9aa); font-size: 1.1rem;
  cursor: pointer; padding: 4px 8px; border-radius: 6px; }
.wm-x:hover { background: rgba(255,255,255,0.08); }
.wm-loading { text-align: center; color: var(--read-text-faint, #9aa); padding: 1.4rem 0; }

.wm-balance { text-align: center; padding: 0.8rem; border-radius: 12px; margin-bottom: 0.7rem;
  background: linear-gradient(135deg, rgba(232,201,90,0.16), rgba(124,58,237,0.12));
  border: 1px solid var(--border-accent, rgba(232,201,90,0.4)); }
.wm-bal-num { font-size: 2.2rem; font-weight: 700; color: var(--accent-gold, #e8c95a); line-height: 1.1; }
.wm-bal-lbl { font-size: 0.82rem; color: var(--read-text-faint, #9aa); }
.wm-free { font-size: 0.85rem; color: var(--read-text-dim, #b8c2cc); margin-bottom: 0.7rem; text-align: center; }
.wm-hint { color: var(--read-text-faint, #9aa); }

.wm-claim { width: 100%; padding: 0.6rem; border: none; border-radius: 10px; font-weight: 600;
  font-size: 0.95rem; cursor: pointer; margin-bottom: 0.4rem;
  background: linear-gradient(135deg, #e8c95a, #d4a017); color: #2b2b2b; }
.wm-claim:disabled { opacity: 0.6; cursor: wait; }
.wm-claim-msg { margin: 0 0 0.7rem; font-size: 0.85rem; text-align: center; color: var(--read-text-dim, #b8c2cc); }
.wm-claim-msg.ok { color: #86efac; font-weight: 600; }

.wm-tx-head { font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.5px;
  color: var(--read-text-faint, #9aa); margin: 0.6rem 0 0.4rem; font-weight: 700; }
.wm-tx-empty { font-size: 0.85rem; color: var(--read-text-faint, #9aa); }
.wm-tx { list-style: none; margin: 0; padding: 0; max-height: 240px; overflow-y: auto; }
.wm-tx-row { display: grid; grid-template-columns: 1fr auto auto; gap: 8px; align-items: center;
  padding: 0.42rem 0.2rem; border-bottom: 1px solid var(--read-border, rgba(255,255,255,0.07)); font-size: 0.86rem; }
.wm-tx-reason { color: var(--read-text, #e6eef5); }
.wm-tx-day { color: var(--read-text-faint, #9aa); font-size: 0.78rem; }
.wm-tx-delta { font-weight: 700; font-variant-numeric: tabular-nums; min-width: 44px; text-align: right; }
.wm-tx-delta.plus { color: #86efac; }
.wm-tx-delta.minus { color: #fca5a5; }
</style>
