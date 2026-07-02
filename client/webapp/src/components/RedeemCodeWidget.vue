<script setup>
/**
 * RedeemCodeWidget — user nhập MÃ QUÀ → cộng xu (ví trung tâm → AppChat tự đồng bộ).
 * Gọi /api/wallet/redeem (login). 1 lần/user theo cấu hình mã. Anh chốt 2026-06-23.
 */
import { ref } from "vue";
import { sessionToken } from "../stores/authStore.js";

const emit = defineEmits(["redeemed"]);  // báo cha (WalletModal) refresh số dư sau khi đổi mã
const code = ref("");
const busy = ref(false);
const msg = ref("");
const ok = ref(false);

const REASON = {
  not_found: "Mã không tồn tại.", inactive: "Mã đã tắt.", expired: "Mã hết hạn.",
  exhausted: "Mã đã hết lượt.", already_redeemed: "Bạn đã dùng mã này rồi.",
  empty: "Nhập mã đã.",
};

async function redeem() {
  if (!code.value.trim() || busy.value) return;
  busy.value = true; msg.value = ""; ok.value = false;
  try {
    const h = { "Content-Type": "application/json" };
    if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
    const r = await fetch("/api/wallet/redeem", {
      method: "POST", headers: h, credentials: "include",
      body: JSON.stringify({ code: code.value.trim() }),
    });
    const d = await r.json();
    if (r.status === 401) { msg.value = "Cần đăng nhập để nhập mã."; return; }
    if (d.status === "ok") {
      ok.value = true;
      msg.value = `🎉 +${d.xu} xu! Số dư: ${d.balance} xu.`;
      code.value = "";
      emit("redeemed", d);
    } else {
      msg.value = REASON[d.reason] || `Không đổi được mã (${d.reason || "lỗi"}).`;
    }
  } catch (e) { msg.value = String(e.message || e); }
  finally { busy.value = false; }
}
</script>

<template>
  <div class="redeem-widget">
    <div class="rw-head">🎟️ <b>Nhập mã quà</b> — tặng xu cho tài khoản</div>
    <div class="rw-row">
      <input v-model="code" placeholder="Nhập mã (vd OZFREIGHT)" class="rw-in"
             @keydown.enter.prevent="redeem" />
      <button class="rw-btn" :disabled="busy || !code.trim()" @click="redeem">
        {{ busy ? "…" : "Đổi mã" }}
      </button>
    </div>
    <p v-if="msg" class="rw-msg" :class="{ ok }">{{ msg }}</p>
  </div>
</template>

<style scoped>
.redeem-widget { border: 1px solid var(--read-border, #e3e3e3); border-radius: 10px;
  padding: 0.8rem 1rem; margin: 0 0 1rem; background: var(--read-bg-soft, rgba(124,58,237,0.04)); }
.rw-head { font-size: 0.95rem; margin-bottom: 0.5rem; color: var(--read-fg, inherit); }
.rw-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.rw-in { flex: 1; min-width: 160px; padding: 0.5rem 0.7rem; border-radius: 8px;
  border: 1px solid var(--read-border, #ccc); background: var(--read-bg, #fff);
  color: inherit; font-size: 0.95rem; text-transform: uppercase; }
.rw-btn { padding: 0.5rem 1.1rem; border: none; border-radius: 8px; font-weight: 600;
  cursor: pointer; background: linear-gradient(135deg, #7c3aed, #a78bfa); color: #fff; }
.rw-btn:disabled { opacity: 0.6; cursor: wait; }
.rw-msg { margin: 0.5rem 0 0; font-size: 0.88rem; color: #c2410c; }
.rw-msg.ok { color: #16a34a; font-weight: 600; }
</style>
