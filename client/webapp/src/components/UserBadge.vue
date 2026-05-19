<script setup>
/**
 * UserBadge — header widget showing current user + login/logout.
 *
 * - When guest: shows "Đăng nhập" button → opens LoginModal
 * - When logged in: shows display_name + dropdown:
 *     - Đổi mật khẩu
 *     - Chuyển hồ sơ (impersonate)
 *     - Đăng xuất
 * - Owner sees extra "Quản lý user" item
 */
import { ref, computed } from "vue";
import {
  currentUser, currentPerson, isAuthenticated, isOwner,
  logout, listPersons, switchPerson, listUsers, changePassword, registerUser, login,
} from "../stores/authStore.js";

const showLogin = ref(false);
const showMenu = ref(false);
const showPasswordModal = ref(false);
const showUsersModal = ref(false);
const showSwitchPersonModal = ref(false);

const loginForm = ref({ email: "ceo@ngantin.vn", password: "" });
const loginError = ref("");
const passwordForm = ref({ current: "", next: "", confirm: "" });
const passwordError = ref("");
const passwordSuccess = ref("");
const persons = ref([]);
const users = ref([]);
const usersLoading = ref(false);
const newUserForm = ref({
  email: "", display_name: "", password: "", default_person_id: "", role: "user",
});
const newUserError = ref("");
const newUserSuccess = ref("");

const displayName = computed(() => currentUser.value?.display_name || "Khách");
const userRole = computed(() => currentUser.value?.role === "owner" ? "Chủ" : "User");
const personLabel = computed(() => {
  const p = currentPerson.value;
  if (!p) return "(chưa chọn hồ sơ)";
  return `${p.name || p.full_name || p.person_id} · ${p.birth_datetime_local || ""}`;
});

async function handleLogin() {
  loginError.value = "";
  const r = await login(loginForm.value.email, loginForm.value.password);
  if (r.ok) {
    showLogin.value = false;
    loginForm.value.password = "";
    if (currentUser.value?.must_change_password) {
      showPasswordModal.value = true;
    }
  } else {
    loginError.value = r.error || "Đăng nhập thất bại";
  }
}

async function handleLogout() {
  await logout();
  showMenu.value = false;
}

async function openSwitchPerson() {
  showMenu.value = false;
  try {
    const d = await listPersons();
    persons.value = d.persons || [];
    showSwitchPersonModal.value = true;
  } catch (e) {
    alert(`Lỗi tải danh sách: ${e.message}`);
  }
}

async function pickPerson(personId) {
  try {
    await switchPerson(personId);
    showSwitchPersonModal.value = false;
  } catch (e) {
    alert(e.message);
  }
}

async function openUsers() {
  showMenu.value = false;
  usersLoading.value = true;
  try {
    const d = await listUsers();
    users.value = d.users || [];
    const p = await listPersons();
    persons.value = p.persons || [];
    showUsersModal.value = true;
  } catch (e) {
    alert(`Lỗi tải users: ${e.message}`);
  } finally {
    usersLoading.value = false;
  }
}

async function submitNewUser() {
  newUserError.value = "";
  newUserSuccess.value = "";
  if (!newUserForm.value.email || !newUserForm.value.password) {
    newUserError.value = "Email + password bắt buộc";
    return;
  }
  if (newUserForm.value.password.length < 8) {
    newUserError.value = "Password ≥ 8 ký tự";
    return;
  }
  try {
    await registerUser({
      email: newUserForm.value.email,
      display_name: newUserForm.value.display_name || newUserForm.value.email,
      password: newUserForm.value.password,
      default_person_id: newUserForm.value.default_person_id || null,
      role: newUserForm.value.role,
    });
    newUserSuccess.value = `✓ Đã tạo user ${newUserForm.value.email}`;
    newUserForm.value = { email: "", display_name: "", password: "", default_person_id: "", role: "user" };
    // Refresh users
    const d = await listUsers();
    users.value = d.users || [];
  } catch (e) {
    newUserError.value = e.message;
  }
}

async function submitChangePassword() {
  passwordError.value = "";
  passwordSuccess.value = "";
  if (passwordForm.value.next !== passwordForm.value.confirm) {
    passwordError.value = "Mật khẩu mới + xác nhận không khớp";
    return;
  }
  if (passwordForm.value.next.length < 8) {
    passwordError.value = "Mật khẩu mới ≥ 8 ký tự";
    return;
  }
  try {
    await changePassword(passwordForm.value.current, passwordForm.value.next);
    passwordSuccess.value = "✓ Đã đổi mật khẩu";
    passwordForm.value = { current: "", next: "", confirm: "" };
    setTimeout(() => { showPasswordModal.value = false; passwordSuccess.value = ""; }, 1200);
  } catch (e) {
    passwordError.value = e.message;
  }
}
</script>

<template>
  <div class="user-badge">
    <!-- Logged-in state -->
    <template v-if="isAuthenticated">
      <button class="ub-pill" @click="showMenu = !showMenu" :title="personLabel">
        <span class="ub-avatar">👤</span>
        <span class="ub-name">{{ displayName }}</span>
        <span class="ub-role" :class="{ 'is-owner': isOwner }">{{ userRole }}</span>
        <span class="ub-caret">▾</span>
      </button>
      <div v-if="showMenu" class="ub-menu" @click.stop>
        <div class="ub-menu-header">
          <strong>{{ displayName }}</strong>
          <small>{{ currentUser?.email }}</small>
        </div>
        <div class="ub-menu-person" v-if="currentPerson">
          <span class="ub-mp-label">Hồ sơ đang dùng:</span>
          <strong>{{ currentPerson.name || currentPerson.full_name }}</strong>
          <small>{{ currentPerson.birth_datetime_local }}</small>
        </div>
        <button class="ub-item" @click="openSwitchPerson">🔄 Chuyển hồ sơ</button>
        <button class="ub-item" @click="showPasswordModal = true; showMenu = false">🔐 Đổi mật khẩu</button>
        <button v-if="isOwner" class="ub-item" @click="openUsers">👥 Quản lý user</button>
        <button class="ub-item ub-danger" @click="handleLogout">⎋ Đăng xuất</button>
      </div>
    </template>

    <!-- Guest state -->
    <template v-else>
      <button class="ub-pill ub-guest" @click="showLogin = true">
        🔑 Đăng nhập
      </button>
    </template>

    <!-- Login modal -->
    <div v-if="showLogin" class="ub-modal-backdrop" @click.self="showLogin = false">
      <div class="ub-modal">
        <h3>🔑 Đăng nhập YI-CHRONOS</h3>
        <form @submit.prevent="handleLogin">
          <label>Email
            <input v-model="loginForm.email" type="email" autofocus required />
          </label>
          <label>Mật khẩu
            <input v-model="loginForm.password" type="password" required />
          </label>
          <p v-if="loginError" class="ub-error">{{ loginError }}</p>
          <p class="ub-hint">Mặc định: <code>ceo@ngantin.vn</code> · password <code>anh-founder-2026</code> (đổi sau khi đăng nhập).</p>
          <div class="ub-modal-actions">
            <button type="button" class="ub-btn-secondary" @click="showLogin = false">Huỷ</button>
            <button type="submit" class="ub-btn-primary">Đăng nhập</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change password modal -->
    <div v-if="showPasswordModal" class="ub-modal-backdrop" @click.self="showPasswordModal = false">
      <div class="ub-modal">
        <h3>🔐 Đổi mật khẩu</h3>
        <p v-if="currentUser?.must_change_password" class="ub-warn">
          ⚠️ Lần đăng nhập đầu — anh phải đổi mật khẩu mặc định.
        </p>
        <form @submit.prevent="submitChangePassword">
          <label>Mật khẩu hiện tại
            <input v-model="passwordForm.current" type="password" required />
          </label>
          <label>Mật khẩu mới (≥ 8 ký tự)
            <input v-model="passwordForm.next" type="password" minlength="8" required />
          </label>
          <label>Xác nhận mật khẩu mới
            <input v-model="passwordForm.confirm" type="password" required />
          </label>
          <p v-if="passwordError" class="ub-error">{{ passwordError }}</p>
          <p v-if="passwordSuccess" class="ub-success">{{ passwordSuccess }}</p>
          <div class="ub-modal-actions">
            <button type="button" class="ub-btn-secondary" @click="showPasswordModal = false">Đóng</button>
            <button type="submit" class="ub-btn-primary">Đổi mật khẩu</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Switch person modal -->
    <div v-if="showSwitchPersonModal" class="ub-modal-backdrop" @click.self="showSwitchPersonModal = false">
      <div class="ub-modal">
        <h3>🔄 Chuyển hồ sơ đang dùng</h3>
        <p class="ub-hint">
          Mặc định là <code>_founder</code> (anh). Nếu xem cho ai khác, chọn hồ sơ tương ứng.
        </p>
        <ul class="ub-person-list">
          <li v-for="p in persons" :key="p.person_id">
            <button class="ub-person-pick"
                    :class="{ active: currentPerson?.person_id === p.person_id }"
                    @click="pickPerson(p.person_id)">
              <strong>{{ p.name }}</strong>
              <small>{{ p.birth_datetime_local }} · {{ p.gender }}</small>
              <span v-if="p.relationship_to_founder === 'self'" class="ub-tag">Anh</span>
            </button>
          </li>
        </ul>
        <div class="ub-modal-actions">
          <button class="ub-btn-secondary" @click="showSwitchPersonModal = false">Đóng</button>
        </div>
      </div>
    </div>

    <!-- Users management (owner only) -->
    <div v-if="showUsersModal" class="ub-modal-backdrop" @click.self="showUsersModal = false">
      <div class="ub-modal ub-modal-wide">
        <h3>👥 Quản lý user</h3>

        <h4 class="ub-section-h">Users hiện tại ({{ users.length }})</h4>
        <table class="ub-users-table">
          <thead>
            <tr><th>ID</th><th>Email</th><th>Tên</th><th>Role</th><th>Default person</th><th>Last login</th></tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.user_id" :class="{ owner: u.role === 'owner' }">
              <td>{{ u.user_id }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.display_name }}</td>
              <td>{{ u.role === 'owner' ? '👑 Chủ' : 'User' }}</td>
              <td>{{ u.default_person_id || '—' }}</td>
              <td>{{ u.last_login_at ? new Date(u.last_login_at * 1000).toLocaleString('vi') : '—' }}</td>
            </tr>
          </tbody>
        </table>

        <h4 class="ub-section-h">+ Tạo user mới</h4>
        <form class="ub-newuser-form" @submit.prevent="submitNewUser">
          <label>Email <input v-model="newUserForm.email" type="email" required /></label>
          <label>Tên hiển thị <input v-model="newUserForm.display_name" /></label>
          <label>Password (≥ 8 ký tự) <input v-model="newUserForm.password" type="password" minlength="8" required /></label>
          <label>Role
            <select v-model="newUserForm.role">
              <option value="user">User</option>
              <option value="owner">Owner</option>
            </select>
          </label>
          <label>Hồ sơ mặc định (person_id, tùy chọn)
            <select v-model="newUserForm.default_person_id">
              <option value="">— Không —</option>
              <option v-for="p in persons" :key="p.person_id" :value="p.person_id">
                {{ p.person_id }} — {{ p.name }}
              </option>
            </select>
          </label>
          <p v-if="newUserError" class="ub-error">{{ newUserError }}</p>
          <p v-if="newUserSuccess" class="ub-success">{{ newUserSuccess }}</p>
          <button type="submit" class="ub-btn-primary">Tạo user</button>
        </form>

        <div class="ub-modal-actions">
          <button class="ub-btn-secondary" @click="showUsersModal = false">Đóng</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-badge { position: relative; display: inline-flex; align-items: center; }

.ub-pill {
  display: inline-flex; align-items: center; gap: 0.4rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  padding: 0.35rem 0.8rem 0.35rem 0.55rem;
  color: #e2e8f0;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s;
}
.ub-pill:hover { background: rgba(255, 255, 255, 0.10); }
.ub-guest { background: linear-gradient(135deg, #2563eb, #1d4ed8); border-color: #1d4ed8; }
.ub-guest:hover { background: linear-gradient(135deg, #3b82f6, #2563eb); }

.ub-avatar { font-size: 0.95em; }
.ub-name { font-weight: 600; }
.ub-role {
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 3px;
  background: rgba(100, 116, 139, 0.4);
  color: #cbd5e1;
}
.ub-role.is-owner { background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff; }
.ub-caret { opacity: 0.5; font-size: 0.7em; }

.ub-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 0.4rem;
  min-width: 250px;
  z-index: 100;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
}
.ub-menu-header {
  padding: 0.4rem 0.6rem 0.5rem 0.6rem;
  border-bottom: 1px solid #1e293b;
  display: flex; flex-direction: column; gap: 1px;
}
.ub-menu-header strong { color: #f1f5f9; font-size: 0.9rem; }
.ub-menu-header small { color: #64748b; font-size: 0.72rem; }
.ub-menu-person {
  padding: 0.35rem 0.6rem;
  background: #1e293b;
  margin: 0.3rem 0;
  border-radius: 3px;
  font-size: 0.78rem;
  display: flex; flex-direction: column; gap: 1px;
}
.ub-mp-label { color: #64748b; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; }
.ub-menu-person strong { color: #fde68a; }
.ub-menu-person small { color: #94a3b8; }
.ub-item {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  color: #cbd5e1;
  padding: 0.45rem 0.6rem;
  font-size: 0.83rem;
  cursor: pointer;
  border-radius: 3px;
}
.ub-item:hover { background: #1e293b; color: #f1f5f9; }
.ub-danger { color: #fca5a5; }
.ub-danger:hover { background: rgba(239, 68, 68, 0.15); }

.ub-modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex; justify-content: center; align-items: center;
  z-index: 1500;
  backdrop-filter: blur(4px);
}
.ub-modal {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
  max-width: 480px;
  width: 90%;
  max-height: 88vh;
  overflow-y: auto;
  color: #e2e8f0;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6);
}
.ub-modal-wide { max-width: 800px; }
.ub-modal h3 { margin: 0 0 0.8rem 0; color: #fde68a; }
.ub-modal h4.ub-section-h {
  margin: 0.9rem 0 0.4rem 0;
  font-size: 0.85rem;
  color: #94a3b8;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.3rem;
}
.ub-modal label {
  display: block;
  margin-bottom: 0.6rem;
  font-size: 0.8rem;
  color: #94a3b8;
}
.ub-modal label input,
.ub-modal label select {
  display: block;
  width: 100%;
  margin-top: 0.25rem;
  background: #1e293b;
  border: 1px solid #475569;
  color: #e2e8f0;
  padding: 0.45rem 0.6rem;
  border-radius: 4px;
  font-size: 0.9rem;
}
.ub-modal label input:focus { outline: none; border-color: #60a5fa; }
.ub-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.9rem;
  padding-top: 0.7rem;
  border-top: 1px solid #1e293b;
}
.ub-btn-primary, .ub-btn-secondary {
  padding: 0.45rem 0.95rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.ub-btn-primary {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  font-weight: 600;
}
.ub-btn-primary:hover { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.ub-btn-secondary { background: #334155; color: #e2e8f0; }
.ub-btn-secondary:hover { background: #475569; }

.ub-error { background: #7f1d1d; border: 1px solid #ef4444; color: #fca5a5; padding: 0.4rem 0.6rem; border-radius: 3px; font-size: 0.78rem; margin: 0.5rem 0; }
.ub-success { background: #064e3b; border: 1px solid #10b981; color: #6ee7b7; padding: 0.4rem 0.6rem; border-radius: 3px; font-size: 0.78rem; margin: 0.5rem 0; }
.ub-warn { background: #78350f; border: 1px solid #f59e0b; color: #fde68a; padding: 0.4rem 0.6rem; border-radius: 3px; font-size: 0.78rem; margin: 0 0 0.6rem 0; }
.ub-hint { color: #94a3b8; font-size: 0.72rem; line-height: 1.5; }
.ub-hint code { background: #1e293b; padding: 1px 4px; border-radius: 2px; }

.ub-person-list { list-style: none; padding: 0; margin: 0.5rem 0; max-height: 50vh; overflow-y: auto; }
.ub-person-list li { margin-bottom: 0.3rem; }
.ub-person-pick {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 0.7rem;
  background: #1e293b;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.45rem 0.65rem;
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
}
.ub-person-pick:hover { background: #283248; }
.ub-person-pick.active { background: linear-gradient(135deg, #1d4ed8, #1e3a8a); border-color: #2563eb; color: #fff; }
.ub-person-pick strong { flex: 1; }
.ub-person-pick small { color: #94a3b8; font-size: 0.72rem; }
.ub-tag { background: #b45309; color: #fde68a; padding: 1px 6px; border-radius: 2px; font-size: 0.7rem; }

.ub-users-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; margin-bottom: 0.5rem; }
.ub-users-table th { background: #1e293b; padding: 0.3rem 0.5rem; text-align: left; border-bottom: 1px solid #334155; color: #94a3b8; }
.ub-users-table td { padding: 0.3rem 0.5rem; border-bottom: 1px solid #1e293b; }
.ub-users-table tr.owner td:nth-child(4) { color: #fbbf24; font-weight: 600; }

.ub-newuser-form label { display: block; }
.ub-newuser-form button[type=submit] { margin-top: 0.5rem; }
</style>
