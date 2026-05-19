<script setup>
/**
 * AdminPanel — owner-only management dashboard.
 *
 * 3 sub-tabs: Dashboard / Users / Audit log
 */
import { ref, onMounted, computed, watch } from "vue";
import { sessionToken, currentUser, isOwner } from "../stores/authStore.js";

const subTab = ref("dashboard"); // 'dashboard' | 'users' | 'audit'

function authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

// ── Dashboard ──────────────────────────────────────────────────────────────
const dashboardData = ref(null);
const dashboardLoading = ref(false);
const dashboardError = ref("");

async function loadDashboard() {
  dashboardLoading.value = true; dashboardError.value = "";
  try {
    const r = await fetch("/api/admin/dashboard", { headers: authHeaders(), credentials: "include" });
    const d = await r.json();
    if (!r.ok) { dashboardError.value = d.detail || "Lỗi tải dashboard"; return; }
    dashboardData.value = d;
  } catch (e) { dashboardError.value = e.message; }
  finally { dashboardLoading.value = false; }
}

// Build inline SVG line chart for signup_trend
const trendChart = computed(() => {
  const trend = dashboardData.value?.signup_trend || [];
  if (!trend.length) return null;
  const W = 540, H = 70, P = 20;
  const max = Math.max(1, ...trend.map(t => t.count));
  const dx = (W - 2 * P) / (trend.length - 1);
  const points = trend.map((t, i) => {
    const x = P + i * dx;
    const y = H - P - (t.count / max) * (H - 2 * P);
    return [x, y, t];
  });
  const poly = points.map(p => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  return { W, H, P, max, points, poly };
});

// ── Users ──────────────────────────────────────────────────────────────────
const usersData = ref({ users: [], total: 0 });
const usersLoading = ref(false);
const usersError = ref("");
const userSearch = ref("");
const userRoleFilter = ref("");
const userStatusFilter = ref("");
const userBirthYear = ref("");
const userSort = ref("created_at_desc");
const userLimit = ref(50);
const userOffset = ref(0);
const selectedUserId = ref(null);
const userDetail = ref(null);
const userDetailLoading = ref(false);
const selectedUserIds = ref(new Set());
const bulkAction = ref("clear_cache");
const bulkBusy = ref(false);

async function loadUsers() {
  usersLoading.value = true; usersError.value = "";
  try {
    const qs = new URLSearchParams({
      search: userSearch.value,
      role: userRoleFilter.value,
      status: userStatusFilter.value,
      sort: userSort.value,
      limit: userLimit.value,
      offset: userOffset.value,
    });
    if (userBirthYear.value) qs.set("birth_year", userBirthYear.value);
    const r = await fetch(`/api/admin/users?${qs}`, { headers: authHeaders(), credentials: "include" });
    const d = await r.json();
    if (!r.ok) { usersError.value = d.detail || "Lỗi tải users"; return; }
    usersData.value = d;
  } catch (e) { usersError.value = e.message; }
  finally { usersLoading.value = false; }
}

async function openUserDetail(userId) {
  selectedUserId.value = userId;
  userDetail.value = null;
  userDetailLoading.value = true;
  try {
    const r = await fetch(`/api/admin/users/${userId}`, { headers: authHeaders(), credentials: "include" });
    const d = await r.json();
    if (r.ok) userDetail.value = d;
  } finally {
    userDetailLoading.value = false;
  }
}

function closeUserDetail() {
  selectedUserId.value = null;
  userDetail.value = null;
}

async function toggleRole(user) {
  const newRole = user.role === "owner" ? "user" : "owner";
  if (!confirm(`Đổi vai trò ${user.email} từ "${user.role}" sang "${newRole}"?`)) return;
  const r = await fetch(`/api/admin/users/${user.user_id}`, {
    method: "PATCH", headers: authHeaders(), credentials: "include",
    body: JSON.stringify({ role: newRole }),
  });
  const d = await r.json();
  if (r.ok) { await loadUsers(); if (selectedUserId.value === user.user_id) openUserDetail(user.user_id); }
  else alert(d.detail || "Lỗi đổi role");
}

async function resetPassword(user) {
  if (!confirm(`Reset mật khẩu ${user.email}? Một mật khẩu tạm sẽ được tạo và user phải đổi ngay khi login.`)) return;
  const r = await fetch(`/api/admin/users/${user.user_id}`, {
    method: "PATCH", headers: authHeaders(), credentials: "include",
    body: JSON.stringify({ reset_password: true }),
  });
  const d = await r.json();
  if (r.ok) {
    alert(`✅ Mật khẩu tạm: ${d.temp_password}\n\n⚠️ COPY NGAY — không hiện lại!`);
    await loadUsers();
  } else alert(d.detail || "Lỗi reset password");
}

async function deleteUser(user) {
  if (!confirm(`⚠️ XOÁ vĩnh viễn ${user.email} (và toàn bộ persons + castings + cache)?\n\nKhông thể hoàn tác!`)) return;
  const r = await fetch(`/api/admin/users/${user.user_id}`, {
    method: "DELETE", headers: authHeaders(), credentials: "include",
  });
  const d = await r.json();
  if (r.ok) {
    alert(`✅ Đã xoá. Cache cleared: ${(d.person_keys_wiped || []).join(", ") || "(none)"}`);
    closeUserDetail();
    await loadUsers();
  } else alert(d.detail || "Lỗi xoá");
}

async function toggleSuspend(user) {
  const willSuspend = !user.is_suspended;
  let reason = "";
  if (willSuspend) {
    reason = prompt(`Lý do tạm khoá ${user.email}?`, "");
    if (reason === null) return; // cancelled
  } else {
    if (!confirm(`Mở khoá ${user.email}?`)) return;
  }
  const r = await fetch(`/api/admin/users/${user.user_id}/suspend`, {
    method: "POST", headers: authHeaders(), credentials: "include",
    body: JSON.stringify({ is_suspended: willSuspend, reason }),
  });
  const d = await r.json();
  if (r.ok) {
    await loadUsers();
    if (selectedUserId.value === user.user_id) openUserDetail(user.user_id);
  } else alert(d.detail || "Lỗi");
}

async function rerunPipeline(user) {
  if (!confirm(`Chạy lại 4 phép phân tích cho ${user.email}?\n(cost ~$0.02, ~25s nền)`)) return;
  const r = await fetch(`/api/admin/users/${user.user_id}/rerun-pipeline`, {
    method: "POST", headers: authHeaders(), credentials: "include",
  });
  const d = await r.json();
  if (r.ok) alert(`⏳ Đã queue. ${d.person_key} sẽ có data mới trong ~30s.`);
  else alert(d.detail || "Lỗi");
}

async function clearUserCache(user) {
  if (!confirm(`Xoá toàn bộ cache phân tích của ${user.email}?\n(Disk free + bắt user phải chạy lại)`)) return;
  const r = await fetch(`/api/admin/users/${user.user_id}/cache`, {
    method: "DELETE", headers: authHeaders(), credentials: "include",
  });
  const d = await r.json();
  if (r.ok) {
    alert(`✅ Đã xoá: ${(d.deleted_paths || []).join(", ") || "(không có gì)"}`);
    if (selectedUserId.value === user.user_id) openUserDetail(user.user_id);
  } else alert(d.detail || "Lỗi");
}

function viewUserPdf(user) {
  fetch(`/api/admin/users/${user.user_id}/report-pdf`, {
    headers: authHeaders(), credentials: "include",
  })
    .then(r => r.ok ? r.blob() : r.json().then(e => { throw new Error(e.detail); }))
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `admin-bao-cao-uid${user.user_id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    })
    .catch(e => alert(e.message));
}

function toggleUserSelect(uid) {
  if (selectedUserIds.value.has(uid)) selectedUserIds.value.delete(uid);
  else selectedUserIds.value.add(uid);
  // Force reactivity
  selectedUserIds.value = new Set(selectedUserIds.value);
}

function selectAllVisible() {
  const all = new Set(usersData.value.users.map(u => u.user_id));
  selectedUserIds.value = all;
}

function clearSelection() {
  selectedUserIds.value = new Set();
}

async function runBulkAction() {
  const ids = Array.from(selectedUserIds.value);
  if (!ids.length) { alert("Chưa chọn user nào"); return; }
  const labels = { delete: "XOÁ VĨNH VIỄN", suspend: "Tạm khoá", unsuspend: "Mở khoá",
                   reset_password: "Reset mật khẩu", clear_cache: "Xoá cache" };
  if (!confirm(`${labels[bulkAction.value]} ${ids.length} user?\n\nIDs: ${ids.join(", ")}`)) return;
  let reason = "";
  if (bulkAction.value === "suspend") {
    reason = prompt("Lý do (chung cho tất cả):", "") || "";
  }
  bulkBusy.value = true;
  try {
    const r = await fetch("/api/admin/users/bulk", {
      method: "POST", headers: authHeaders(), credentials: "include",
      body: JSON.stringify({ user_ids: ids, action: bulkAction.value, reason }),
    });
    const d = await r.json();
    if (r.ok) {
      const ok = d.results.filter(x => x.status === "ok").length;
      const err = d.results.length - ok;
      alert(`✅ ${ok} thành công, ${err} lỗi`);
      clearSelection();
      await loadUsers();
    } else alert(d.detail);
  } finally { bulkBusy.value = false; }
}

// Cost summary
const costsData = ref(null);
const costsLoading = ref(false);
async function loadCosts() {
  costsLoading.value = true;
  try {
    const r = await fetch("/api/admin/costs", { headers: authHeaders(), credentials: "include" });
    costsData.value = await r.json();
  } finally { costsLoading.value = false; }
}

function exportCsv() {
  // Use fetch + blob để gửi auth header (download via <a> không gửi header tự nhiên)
  fetch("/api/admin/export-csv", { headers: authHeaders(), credentials: "include" })
    .then(r => r.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `yi-users-${new Date().toISOString().slice(0,10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    });
}

// ── Audit log ──────────────────────────────────────────────────────────────
const auditData = ref({ entries: [], total: 0 });
const auditLoading = ref(false);
const auditError = ref("");
const auditActionFilter = ref("");
const auditOffset = ref(0);
const auditLimit = ref(100);

async function loadAudit() {
  auditLoading.value = true; auditError.value = "";
  try {
    const qs = new URLSearchParams({
      action: auditActionFilter.value,
      limit: auditLimit.value,
      offset: auditOffset.value,
    });
    const r = await fetch(`/api/admin/audit-log?${qs}`, { headers: authHeaders(), credentials: "include" });
    const d = await r.json();
    if (!r.ok) { auditError.value = d.detail || "Lỗi tải audit"; return; }
    auditData.value = d;
  } catch (e) { auditError.value = e.message; }
  finally { auditLoading.value = false; }
}

// ── Init based on tab ──────────────────────────────────────────────────────
watch(subTab, (newTab) => {
  if (newTab === "dashboard" && !dashboardData.value) loadDashboard();
  if (newTab === "users" && !usersData.value.users.length) loadUsers();
  if (newTab === "audit" && !auditData.value.entries.length) loadAudit();
}, { immediate: false });

onMounted(() => {
  if (isOwner.value) loadDashboard();
});

// Format helpers
function fmtTime(ts) {
  if (!ts) return "—";
  return new Date(ts * 1000).toLocaleString("vi", { dateStyle: "short", timeStyle: "short" });
}
function fmtRelative(ts) {
  if (!ts) return "—";
  const diff = Date.now() / 1000 - ts;
  if (diff < 60) return `${Math.floor(diff)}s trước`;
  if (diff < 3600) return `${Math.floor(diff / 60)}p trước`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h trước`;
  return `${Math.floor(diff / 86400)}d trước`;
}
const actionIcon = {
  login_ok: "🔓", login_fail: "🚫", signup: "✨", logout: "👋",
  change_password: "🔐", setup_profile: "👤",
  admin_set_role: "👑", admin_reset_pwd: "🔑", admin_delete_user: "🗑",
  admin_update_user: "✏️",
};
</script>

<template>
  <div v-if="!isOwner" class="ap-no-access">
    <h2>🚫 Yêu cầu quyền chủ hệ thống</h2>
    <p>Trang này chỉ dành cho owner. Bạn đang đăng nhập với vai trò user thường.</p>
  </div>

  <div v-else class="ap-wrap">
    <header class="ap-head">
      <h2>👥 Admin Dashboard</h2>
      <p>Quản lý users · audit log · cấu hình hệ thống</p>
    </header>

    <nav class="ap-sub-tabs">
      <button :class="{ active: subTab === 'dashboard' }" @click="subTab = 'dashboard'">📊 Tổng quan</button>
      <button :class="{ active: subTab === 'users' }" @click="subTab = 'users'">👥 Users</button>
      <button :class="{ active: subTab === 'audit' }" @click="subTab = 'audit'">📜 Audit log</button>
    </nav>

    <!-- ─── DASHBOARD ─────────────────────────────────────────────────────── -->
    <section v-if="subTab === 'dashboard'" class="ap-section">
      <button class="ap-refresh" @click="loadDashboard" :disabled="dashboardLoading">
        {{ dashboardLoading ? "⏳" : "🔄" }} Refresh
      </button>
      <p v-if="dashboardError" class="ap-error">{{ dashboardError }}</p>

      <div v-if="dashboardData" class="ap-kpi-grid">
        <div class="ap-kpi"><span class="ap-kpi-v">{{ dashboardData.kpis.total_users }}</span><span class="ap-kpi-l">Users</span></div>
        <div class="ap-kpi"><span class="ap-kpi-v">{{ dashboardData.kpis.signups_30d }}</span><span class="ap-kpi-l">Signups 30 ngày</span></div>
        <div class="ap-kpi"><span class="ap-kpi-v">{{ dashboardData.kpis.signups_7d }}</span><span class="ap-kpi-l">Signups 7 ngày</span></div>
        <div class="ap-kpi"><span class="ap-kpi-v">{{ dashboardData.kpis.active_7d }}</span><span class="ap-kpi-l">Active 7 ngày</span></div>
        <div class="ap-kpi"><span class="ap-kpi-v">{{ dashboardData.kpis.total_persons }}</span><span class="ap-kpi-l">Persons</span></div>
        <div class="ap-kpi"><span class="ap-kpi-v">{{ dashboardData.kpis.total_castings }}</span><span class="ap-kpi-l">Castings</span></div>
        <div class="ap-kpi"><span class="ap-kpi-v">{{ dashboardData.disk_usage_mb }} MB</span><span class="ap-kpi-l">Cache disk</span></div>
        <div class="ap-kpi" :class="{ warn: dashboardData.kpis.failed_logins_7d > 5 }">
          <span class="ap-kpi-v">{{ dashboardData.kpis.failed_logins_7d }}</span>
          <span class="ap-kpi-l">Login fail 7 ngày</span>
        </div>
        <div class="ap-kpi" :class="{ warn: dashboardData.kpis.suspended_users > 0 }">
          <span class="ap-kpi-v">{{ dashboardData.kpis.suspended_users || 0 }}</span>
          <span class="ap-kpi-l">Đang khoá</span>
        </div>
      </div>

      <!-- Cost summary -->
      <div class="ap-card">
        <h3>
          💰 Chi phí DeepSeek (lifetime)
          <button class="ap-btn-mini" @click="loadCosts">{{ costsLoading ? "⏳" : "↻" }}</button>
        </h3>
        <p v-if="!costsData" class="ap-empty">Bấm ↻ để load (scan disk có thể mất 1-2s)</p>
        <div v-else>
          <p><b>Tổng: ${{ costsData.total_cost_usd?.toFixed(4) }}</b> · {{ costsData.total_files_scanned }} files</p>
          <table class="ap-table">
            <thead><tr><th>User</th><th>Cost USD</th><th>Files</th></tr></thead>
            <tbody>
              <tr v-for="b in costsData.breakdown.slice(0, 10)" :key="b.user_id">
                <td>{{ b.email }}</td>
                <td>${{ b.cost_usd.toFixed(4) }}</td>
                <td>{{ b.files_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="trendChart" class="ap-card">
        <h3>📈 Signup trend — 30 ngày qua</h3>
        <svg :width="trendChart.W" :height="trendChart.H" viewBox="0 0 540 70" preserveAspectRatio="none">
          <polyline :points="trendChart.poly" fill="none" stroke="#f59e0b" stroke-width="2" />
          <circle v-for="(p, i) in trendChart.points" :key="i"
                  :cx="p[0]" :cy="p[1]" r="2.5" fill="#fbbf24">
            <title>{{ p[2].label }}: {{ p[2].count }} signup</title>
          </circle>
        </svg>
        <small class="ap-trend-axis">Hôm nay ← → 30 ngày trước · max/day: {{ trendChart.max }}</small>
      </div>

      <div v-if="dashboardData?.top_users?.length" class="ap-card">
        <h3>🏆 Top users by castings</h3>
        <table class="ap-table">
          <thead><tr><th>Email</th><th>Role</th><th>Castings</th><th>Persons</th><th>Last login</th></tr></thead>
          <tbody>
            <tr v-for="u in dashboardData.top_users" :key="u.user_id">
              <td>{{ u.email }}</td>
              <td><span class="ap-role-pill" :class="u.role">{{ u.role }}</span></td>
              <td>{{ u.castings_count }}</td>
              <td>{{ u.persons_count }}</td>
              <td>{{ fmtRelative(u.last_login_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ─── USERS ─────────────────────────────────────────────────────────── -->
    <section v-if="subTab === 'users'" class="ap-section">
      <div class="ap-toolbar">
        <input v-model="userSearch" placeholder="🔍 Tìm email / tên..."
               @input="userOffset = 0; loadUsers()" />
        <select v-model="userRoleFilter" @change="userOffset = 0; loadUsers()">
          <option value="">Tất cả vai trò</option>
          <option value="owner">Owner</option>
          <option value="user">User</option>
        </select>
        <select v-model="userStatusFilter" @change="userOffset = 0; loadUsers()">
          <option value="">Tất cả trạng thái</option>
          <option value="active">Active</option>
          <option value="suspended">Đã khoá</option>
          <option value="inactive_30d">Chưa login > 30d</option>
        </select>
        <input v-model="userBirthYear" type="number" placeholder="Năm sinh (1990)"
               style="width: 130px" @input="userOffset = 0; loadUsers()" />
        <select v-model="userSort" @change="loadUsers">
          <option value="created_at_desc">Mới nhất</option>
          <option value="created_at_asc">Cũ nhất</option>
          <option value="last_login_desc">Login gần đây</option>
          <option value="email_asc">Email A-Z</option>
          <option value="castings_desc">Nhiều castings</option>
        </select>
        <button class="ap-btn-ghost" @click="loadUsers">🔄</button>
        <button class="ap-btn-ghost" @click="exportCsv">📥 CSV</button>
      </div>

      <!-- Bulk action bar — hiện khi có chọn -->
      <div v-if="selectedUserIds.size > 0" class="ap-bulk-bar">
        <span><b>{{ selectedUserIds.size }}</b> user đã chọn</span>
        <select v-model="bulkAction">
          <option value="clear_cache">🧹 Xoá cache</option>
          <option value="suspend">🚫 Tạm khoá</option>
          <option value="unsuspend">🔓 Mở khoá</option>
          <option value="reset_password">🔑 Reset password</option>
          <option value="delete">🗑 Xoá vĩnh viễn</option>
        </select>
        <button class="ap-btn-warn" @click="runBulkAction" :disabled="bulkBusy">
          {{ bulkBusy ? "⏳ Đang chạy..." : "▶ Thực hiện" }}
        </button>
        <button class="ap-btn-ghost" @click="clearSelection">Bỏ chọn</button>
      </div>

      <p v-if="usersError" class="ap-error">{{ usersError }}</p>
      <p class="ap-meta">{{ usersData.total }} users tổng cộng</p>

      <table class="ap-table ap-table-clickable">
        <thead>
          <tr>
            <th><button class="ap-btn-mini" @click="selectAllVisible" title="Chọn tất cả trang này">☑</button></th>
            <th>#</th><th>Email</th><th>Tên</th><th>Role</th><th>St</th>
            <th>Castings</th><th>Persons</th><th>Last login</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in usersData.users" :key="u.user_id"
              :class="{ selected: selectedUserId === u.user_id, must_change: u.must_change_password, suspended: u.is_suspended }">
            <td><input type="checkbox" :checked="selectedUserIds.has(u.user_id)" @change="toggleUserSelect(u.user_id)" /></td>
            <td>{{ u.user_id }}</td>
            <td>
              <a href="#" @click.prevent="openUserDetail(u.user_id)">{{ u.email }}</a>
              <span v-if="u.must_change_password" class="ap-flag" title="Phải đổi mật khẩu">⚠️</span>
            </td>
            <td>{{ u.display_name }}</td>
            <td><span class="ap-role-pill" :class="u.role">{{ u.role === 'owner' ? '👑' : 'U' }}</span></td>
            <td>
              <span v-if="u.is_suspended" class="ap-status-pill suspended" :title="u.suspend_reason">🚫 Khoá</span>
              <span v-else class="ap-status-pill active">✓</span>
            </td>
            <td>{{ u.castings_count }}</td>
            <td>{{ u.persons_count }}</td>
            <td><small>{{ fmtRelative(u.last_login_at) }}</small></td>
            <td class="ap-actions">
              <button class="ap-btn-sm" @click="rerunPipeline(u)" title="Chạy lại 4 phép phân tích">🔁</button>
              <button class="ap-btn-sm" @click="viewUserPdf(u)" title="Tải PDF lá số của user">📄</button>
              <button class="ap-btn-sm" @click="clearUserCache(u)" title="Xoá cache">🧹</button>
              <button class="ap-btn-sm" :class="u.is_suspended ? 'ap-btn-ok' : 'ap-btn-warn'"
                      @click="toggleSuspend(u)" :title="u.is_suspended ? 'Mở khoá' : 'Khoá'">
                {{ u.is_suspended ? '🔓' : '🚫' }}
              </button>
              <button class="ap-btn-sm" @click="toggleRole(u)" title="Toggle role">
                {{ u.role === 'owner' ? '👤' : '👑' }}
              </button>
              <button class="ap-btn-sm" @click="resetPassword(u)" title="Reset password">🔑</button>
              <button class="ap-btn-sm ap-btn-danger" @click="deleteUser(u)" title="Xoá">🗑</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="usersData.total > userLimit" class="ap-pagination">
        <button :disabled="userOffset === 0" @click="userOffset = Math.max(0, userOffset - userLimit); loadUsers()">◀</button>
        <span>{{ userOffset + 1 }} - {{ Math.min(userOffset + userLimit, usersData.total) }} / {{ usersData.total }}</span>
        <button :disabled="userOffset + userLimit >= usersData.total"
                @click="userOffset += userLimit; loadUsers()">▶</button>
      </div>

      <!-- User detail drawer -->
      <Teleport to="body">
        <div v-if="selectedUserId" class="ap-drawer-backdrop" @click.self="closeUserDetail">
          <div class="ap-drawer">
            <button class="ap-drawer-close" @click="closeUserDetail">✕</button>
            <div v-if="userDetailLoading" class="ap-loading">Đang tải...</div>
            <div v-else-if="userDetail">
              <h3>
                {{ userDetail.user.email }}
                <span v-if="userDetail.user.is_suspended" class="ap-status-pill suspended">🚫 Khoá</span>
              </h3>
              <div class="ap-detail-grid">
                <div><span>User ID</span><b>{{ userDetail.user.user_id }}</b></div>
                <div><span>Tên</span><b>{{ userDetail.user.display_name }}</b></div>
                <div><span>Role</span><b>{{ userDetail.user.role }}</b></div>
                <div><span>Tạo lúc</span><b>{{ fmtTime(userDetail.user.created_at) }}</b></div>
                <div><span>Login gần nhất</span><b>{{ fmtRelative(userDetail.user.last_login_at) }}</b></div>
                <div><span>Phải đổi pwd</span><b>{{ userDetail.user.must_change_password ? 'Có' : 'Không' }}</b></div>
                <div><span>Cache size</span><b>{{ userDetail.cache_size_mb }} MB</b></div>
                <div><span>Cost lifetime</span><b>${{ (userDetail.total_cost_usd || 0).toFixed(4) }}</b></div>
                <div><span>Castings tổng</span><b>{{ userDetail.castings_total }}</b></div>
                <div v-if="userDetail.user.is_suspended" class="ap-suspend-info">
                  <span>Lý do khoá</span><b>{{ userDetail.user.suspend_reason || '—' }}</b>
                </div>
              </div>

              <div class="ap-quick-actions">
                <button class="ap-btn-warn" @click="rerunPipeline(userDetail.user)">🔁 Chạy lại pipeline</button>
                <button class="ap-btn-ghost" @click="viewUserPdf(userDetail.user)">📄 Tải PDF</button>
                <button class="ap-btn-ghost" @click="clearUserCache(userDetail.user)">🧹 Clear cache</button>
                <button class="ap-btn-warn" @click="toggleSuspend(userDetail.user)">
                  {{ userDetail.user.is_suspended ? '🔓 Mở khoá' : '🚫 Khoá' }}
                </button>
              </div>

              <h4>👥 Persons ({{ userDetail.persons.length }})</h4>
              <ul class="ap-list">
                <li v-for="p in userDetail.persons" :key="p.id">
                  <strong>{{ p.name }}</strong>
                  <small>({{ p.relationship }}) · {{ p.gender }} · sinh {{ p.birth_datetime_local }}</small>
                </li>
                <li v-if="!userDetail.persons.length" class="ap-empty">Chưa có person nào</li>
              </ul>

              <h4>🎴 Gieo quẻ gần đây ({{ userDetail.recent_castings.length }})</h4>
              <ul class="ap-list">
                <li v-for="c in userDetail.recent_castings" :key="c.id">
                  <span class="ap-method">{{ c.method }}</span>
                  <small>{{ c.question || '(không có câu hỏi)' }} · {{ fmtRelative(c.created_at) }}</small>
                  <span v-if="c.verdict" class="ap-verdict">{{ c.verdict }}</span>
                </li>
                <li v-if="!userDetail.recent_castings.length" class="ap-empty">Chưa có gieo quẻ nào</li>
              </ul>
            </div>
          </div>
        </div>
      </Teleport>
    </section>

    <!-- ─── AUDIT LOG ─────────────────────────────────────────────────────── -->
    <section v-if="subTab === 'audit'" class="ap-section">
      <div class="ap-toolbar">
        <select v-model="auditActionFilter" @change="auditOffset = 0; loadAudit()">
          <option value="">Tất cả action</option>
          <option value="login_ok">✓ Login</option>
          <option value="login_fail">✗ Login fail</option>
          <option value="signup">+ Signup</option>
          <option value="logout">Logout</option>
          <option value="change_password">Đổi password</option>
          <option value="setup_profile">Setup profile</option>
          <option value="admin_reset_pwd">Admin: reset pwd</option>
          <option value="admin_update_user">Admin: update user</option>
          <option value="admin_delete_user">Admin: delete user</option>
        </select>
        <button class="ap-btn-ghost" @click="loadAudit">🔄</button>
      </div>

      <p v-if="auditError" class="ap-error">{{ auditError }}</p>
      <p class="ap-meta">{{ auditData.total }} entries</p>

      <table class="ap-table">
        <thead>
          <tr><th></th><th>Time</th><th>Action</th><th>Email</th><th>User ID</th><th>IP</th><th>Details</th></tr>
        </thead>
        <tbody>
          <tr v-for="e in auditData.entries" :key="e.id">
            <td>{{ actionIcon[e.action] || '·' }}</td>
            <td><small>{{ fmtTime(e.created_at) }}</small></td>
            <td>{{ e.action }}</td>
            <td>{{ e.target_email || '—' }}</td>
            <td>{{ e.user_id || e.actor_user_id || '—' }}</td>
            <td><small>{{ e.ip_address || '—' }}</small></td>
            <td><small class="ap-truncate">{{ e.details ? JSON.stringify(e.details) : '' }}</small></td>
          </tr>
        </tbody>
      </table>

      <div v-if="auditData.total > auditLimit" class="ap-pagination">
        <button :disabled="auditOffset === 0" @click="auditOffset = Math.max(0, auditOffset - auditLimit); loadAudit()">◀</button>
        <span>{{ auditOffset + 1 }} - {{ Math.min(auditOffset + auditLimit, auditData.total) }} / {{ auditData.total }}</span>
        <button :disabled="auditOffset + auditLimit >= auditData.total"
                @click="auditOffset += auditLimit; loadAudit()">▶</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.ap-no-access {
  padding: 3rem; text-align: center; color: #fca5a5;
}
.ap-wrap {
  padding: 1rem 1.5rem; color: #e2e8f0;
  font-family: "Charter", "Iowan Old Style", Georgia, serif;
}
.ap-head h2 { margin: 0 0 0.2rem; color: #fde68a; }
.ap-head p { margin: 0 0 1rem; color: #94a3b8; font-size: 0.85rem; }

.ap-sub-tabs {
  display: flex; gap: 0; border-bottom: 1px solid #334155; margin-bottom: 1rem;
}
.ap-sub-tabs button {
  background: transparent; border: none; color: #94a3b8;
  padding: 0.6rem 1.2rem; cursor: pointer; font-size: 0.9rem; font-weight: 600;
  border-bottom: 2px solid transparent;
}
.ap-sub-tabs button:hover { color: #cbd5e1; }
.ap-sub-tabs button.active { color: #fde68a; border-bottom-color: #f59e0b; }

.ap-section { position: relative; }
.ap-refresh {
  position: absolute; top: 0; right: 0;
  background: #334155; border: 1px solid #475569; color: #cbd5e1;
  padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;
}

.ap-error { color: #fca5a5; padding: 0.5rem; background: rgba(239,68,68,0.1); border-radius: 4px; }
.ap-loading { padding: 2rem; text-align: center; color: #94a3b8; }
.ap-meta { color: #64748b; font-size: 0.8rem; margin: 0 0 0.5rem; }

/* KPI cards */
.ap-kpi-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.6rem; margin: 1rem 0;
}
.ap-kpi {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border: 1px solid #334155; border-radius: 6px;
  padding: 0.7rem 0.9rem;
  display: flex; flex-direction: column;
}
.ap-kpi.warn { border-color: #f59e0b; }
.ap-kpi-v { font-size: 1.4rem; font-weight: 700; color: #fde68a; }
.ap-kpi-l { font-size: 0.75rem; color: #94a3b8; margin-top: 0.2rem; }

.ap-card {
  background: #0f172a; border: 1px solid #334155; border-radius: 6px;
  padding: 0.8rem 1rem; margin: 0.8rem 0;
}
.ap-card h3 { margin: 0 0 0.5rem; color: #fde68a; font-size: 1rem; }
.ap-card svg { display: block; width: 100%; max-width: 540px; }
.ap-trend-axis { display: block; color: #64748b; font-size: 0.7rem; margin-top: 0.3rem; }

/* Table */
.ap-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.ap-table th { text-align: left; padding: 0.4rem 0.5rem; border-bottom: 1px solid #334155; color: #94a3b8; font-weight: 600; }
.ap-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #1e293b; }
.ap-table tr:hover { background: rgba(255,255,255,0.02); }
.ap-table-clickable tr.selected { background: rgba(245,158,11,0.1); }
.ap-table tr.must_change td:nth-child(2) { color: #fbbf24; }
.ap-table small { color: #94a3b8; font-size: 0.75rem; }
.ap-table a { color: #60a5fa; text-decoration: none; }
.ap-table a:hover { text-decoration: underline; }
.ap-truncate { display: inline-block; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.ap-role-pill {
  padding: 1px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600;
  background: #334155; color: #cbd5e1;
}
.ap-role-pill.owner { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }

.ap-flag { color: #fbbf24; margin-left: 0.3rem; }

/* Toolbar */
.ap-toolbar {
  display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; margin-bottom: 0.6rem;
}
.ap-toolbar input, .ap-toolbar select {
  background: #0f172a; border: 1px solid #334155; color: #f1f5f9;
  padding: 0.35rem 0.5rem; border-radius: 4px; font-size: 0.85rem;
}
.ap-toolbar input { min-width: 200px; }
.ap-btn-ghost {
  background: #334155; border: 1px solid #475569; color: #cbd5e1;
  padding: 0.35rem 0.7rem; border-radius: 4px; cursor: pointer; font-size: 0.82rem;
}
.ap-btn-ghost:hover { background: #475569; }

/* Actions */
.ap-actions { display: flex; gap: 0.2rem; }
.ap-btn-sm {
  background: #334155; border: 1px solid #475569; color: #cbd5e1;
  width: 26px; height: 26px; border-radius: 4px; cursor: pointer; font-size: 0.85rem;
}
.ap-btn-sm:hover { background: #475569; }
.ap-btn-danger { background: rgba(239,68,68,0.2); border-color: #ef4444; }
.ap-btn-danger:hover { background: rgba(239,68,68,0.35); }
.ap-btn-warn { background: rgba(245,158,11,0.2); border-color: #f59e0b; color: #fde68a; }
.ap-btn-warn:hover { background: rgba(245,158,11,0.35); }
.ap-btn-ok { background: rgba(16,185,129,0.2); border-color: #10b981; color: #86efac; }
.ap-btn-ok:hover { background: rgba(16,185,129,0.35); }
.ap-btn-mini {
  background: transparent; border: 1px solid #475569; color: #cbd5e1;
  width: 22px; height: 22px; border-radius: 3px; cursor: pointer; font-size: 0.7rem;
  padding: 0;
}
.ap-btn-mini:hover { background: #475569; }

.ap-bulk-bar {
  display: flex; gap: 0.5rem; align-items: center;
  background: linear-gradient(135deg, rgba(217,119,6,0.15), rgba(217,119,6,0.05));
  border: 1px solid rgba(245,158,11,0.4); border-radius: 6px;
  padding: 0.5rem 0.8rem; margin-bottom: 0.6rem;
}
.ap-bulk-bar > span { color: #fde68a; font-size: 0.85rem; }
.ap-bulk-bar select {
  background: #0f172a; border: 1px solid #475569; color: #f1f5f9;
  padding: 0.3rem 0.5rem; border-radius: 4px;
}

.ap-status-pill {
  padding: 1px 6px; border-radius: 10px; font-size: 0.7rem; font-weight: 600;
}
.ap-status-pill.active { background: rgba(16,185,129,0.15); color: #86efac; }
.ap-status-pill.suspended { background: rgba(239,68,68,0.2); color: #fca5a5; }

.ap-table tr.suspended td { opacity: 0.55; }
.ap-table tr.suspended td:nth-child(3) a { text-decoration: line-through; }

.ap-table th:first-child, .ap-table td:first-child { width: 26px; text-align: center; }

/* Pagination */
.ap-pagination {
  display: flex; gap: 0.5rem; align-items: center; justify-content: center;
  margin-top: 1rem; color: #94a3b8; font-size: 0.85rem;
}
.ap-pagination button {
  background: #334155; border: 1px solid #475569; color: #cbd5e1;
  padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer;
}
.ap-pagination button:disabled { opacity: 0.4; cursor: not-allowed; }

/* Drawer */
.ap-drawer-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
  z-index: 2500; display: flex; justify-content: flex-end;
}
.ap-drawer {
  background: #0f172a; border-left: 2px solid #f59e0b;
  width: 100%; max-width: 540px; height: 100vh;
  padding: 1.5rem; overflow-y: auto;
  position: relative; color: #e2e8f0;
  box-shadow: -10px 0 40px rgba(0,0,0,0.6);
}
.ap-drawer-close {
  position: absolute; top: 0.7rem; right: 0.8rem;
  background: rgba(255,255,255,0.1); border: none; color: #cbd5e1;
  width: 32px; height: 32px; border-radius: 4px; cursor: pointer;
}
.ap-drawer h3 { margin: 0 0 0.6rem; color: #fde68a; }
.ap-drawer h4 { margin: 1rem 0 0.4rem; color: #fbbf24; font-size: 0.9rem; }
.ap-detail-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.3rem 1rem;
  margin: 0.6rem 0; font-size: 0.85rem;
}
.ap-detail-grid > div { padding: 0.2rem 0; border-bottom: 1px solid #1e293b; }
.ap-detail-grid span { color: #94a3b8; margin-right: 0.5rem; }
.ap-suspend-info { grid-column: 1 / -1; color: #fca5a5; }

.ap-quick-actions {
  display: flex; gap: 0.4rem; flex-wrap: wrap; margin: 0.8rem 0;
  padding: 0.5rem; background: rgba(245,158,11,0.05);
  border: 1px dashed rgba(245,158,11,0.3); border-radius: 4px;
}
.ap-quick-actions button {
  padding: 0.4rem 0.7rem; border-radius: 4px; cursor: pointer; font-size: 0.82rem;
}
.ap-list { list-style: none; padding: 0; margin: 0; }
.ap-list li {
  padding: 0.35rem 0.5rem; border-bottom: 1px solid #1e293b;
  font-size: 0.82rem; display: flex; gap: 0.4rem; align-items: baseline;
}
.ap-list li small { color: #94a3b8; }
.ap-empty { color: #64748b; font-style: italic; }
.ap-method {
  background: rgba(96,165,250,0.15); color: #93c5fd;
  padding: 1px 6px; border-radius: 3px; font-size: 0.72rem; font-family: monospace;
}
.ap-verdict {
  background: rgba(245,158,11,0.15); color: #fbbf24;
  padding: 1px 6px; border-radius: 3px; font-size: 0.72rem;
  margin-left: auto;
}
</style>
