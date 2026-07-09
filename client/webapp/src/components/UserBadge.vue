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
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import {
  currentUser, currentPerson, isAuthenticated, isOwner, sessionToken,
  logout, listPersons, switchPerson, listUsers, changePassword, registerUser, login, signup,
  forgotPassword, resetPassword,
} from "../stores/authStore.js";
import WalletModal from "./WalletModal.vue";

const showLogin = ref(false);
const loginTab = ref("login"); // 'login' | 'signup' | 'forgot'
const forgotForm = ref({ email: "" });
const forgotError = ref("");
const forgotSuccess = ref("");
const forgotBusy = ref(false);

// Đặt lại mật khẩu — kích hoạt khi URL có ?reset_token=... (link trong email).
const showResetModal = ref(false);
const resetToken = ref("");
const resetForm = ref({ next: "", confirm: "" });
const resetError = ref("");
const resetSuccess = ref("");
const resetBusy = ref(false);
const signupForm = ref({ email: "", display_name: "", password: "", confirm: "" });
const signupError = ref("");
const signupBusy = ref(false);
const showMenu = ref(false);
const rootBadge = ref(null); // gốc .user-badge — dùng để phát hiện click ra ngoài menu 👤
const showPasswordModal = ref(false);
const showUsersModal = ref(false);
const showSwitchPersonModal = ref(false);
const showWallet = ref(false);
const walletBalance = ref(null);   // số dư hiện trên chip (at-a-glance)
async function loadWalletBalance() {
  if (!isAuthenticated.value) { walletBalance.value = null; return; }
  try {
    const h = {}; if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
    const r = await fetch("/api/wallet", { headers: h, credentials: "include" });
    if (r.ok) { const d = await r.json(); walletBalance.value = d.balance ?? null; }
  } catch (e) { /* im lặng — chip không có xu thì thôi */ }
}
onMounted(loadWalletBalance);
watch(isAuthenticated, loadWalletBalance);

// Link trong email "quên mật khẩu" trỏ về /?reset_token=xxx — bắt token ngay
// khi trang tải, mở modal đặt lại mật khẩu, rồi xoá param khỏi URL (đừng để
// f5/share link vô tình dùng lại token cũ hoặc lộ token trong lịch sử trình duyệt).
onMounted(() => {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("reset_token");
  if (token) {
    resetToken.value = token;
    showResetModal.value = true;
    params.delete("reset_token");
    const rest = params.toString();
    const cleanUrl = window.location.pathname + (rest ? `?${rest}` : "") + window.location.hash;
    window.history.replaceState({}, "", cleanUrl);
  }
});

// Menu 👤 (showMenu) trước đây KHÔNG tự ẩn khi bấm ra ngoài — chỉ đóng khi bấm
// đúng 1 trong các item bên trong. Thêm click-ra-ngoài + Esc, cùng pattern với
// NavDropdown.vue (menu "Trường phái" đã làm đúng, dùng lại ở đây cho nhất quán).
function onDocClickCloseMenu(e) {
  if (!showMenu.value) return;
  if (rootBadge.value && rootBadge.value.contains(e.target)) return;
  showMenu.value = false;
}
function onEscCloseMenu(e) {
  if (e.key === "Escape") showMenu.value = false;
}
onMounted(() => {
  document.addEventListener("click", onDocClickCloseMenu);
  document.addEventListener("keydown", onEscCloseMenu);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClickCloseMenu);
  document.removeEventListener("keydown", onEscCloseMenu);
});

// IMPORTANT: do NOT pre-fill with anh's own email. Previously this was
// `ceo@ngantin.vn` as a dev convenience — meant every visitor clicking
// "Đăng nhập" saw the owner's email pre-filled. Leak. Leave blank.
const loginForm = ref({ email: "", password: "" });
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

// Nút hiện/ẩn mật khẩu — 1 cờ show/hide riêng cho mỗi ô password trong file.
const showPw = ref({
  login: false, signupPw: false, signupConfirm: false,
  pwCurrent: false, pwNext: false, pwConfirm: false, newUserPw: false,
  resetNext: false, resetConfirm: false,
});
function togglePw(key) { showPw.value[key] = !showPw.value[key]; }

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

async function handleSignup() {
  signupError.value = "";
  const f = signupForm.value;
  if (!f.email || !f.display_name || !f.password) {
    signupError.value = "Vui lòng điền đầy đủ thông tin";
    return;
  }
  if (f.password.length < 6) {
    signupError.value = "Mật khẩu tối thiểu 6 ký tự";
    return;
  }
  if (f.password !== f.confirm) {
    signupError.value = "Mật khẩu xác nhận không khớp";
    return;
  }
  signupBusy.value = true;
  try {
    const r = await signup(f.email, f.display_name, f.password);
    if (r.ok) {
      showLogin.value = false;
      signupForm.value = { email: "", display_name: "", password: "", confirm: "" };
      loginTab.value = "login";
    } else {
      signupError.value = r.error || "Đăng ký thất bại";
    }
  } finally {
    signupBusy.value = false;
  }
}

async function handleForgotPassword() {
  forgotError.value = ""; forgotSuccess.value = "";
  if (!forgotForm.value.email) {
    forgotError.value = "Vui lòng nhập email";
    return;
  }
  forgotBusy.value = true;
  try {
    const r = await forgotPassword(forgotForm.value.email);
    if (r.ok) {
      forgotSuccess.value = r.message || "Nếu email này đã đăng ký, liên kết đặt lại mật khẩu vừa được gửi.";
      forgotForm.value.email = "";
    } else {
      forgotError.value = r.error || "Gửi yêu cầu thất bại";
    }
  } finally {
    forgotBusy.value = false;
  }
}

async function handleResetPassword() {
  resetError.value = ""; resetSuccess.value = "";
  if (resetForm.value.next.length < 8) {
    resetError.value = "Mật khẩu mới phải ≥ 8 ký tự";
    return;
  }
  if (resetForm.value.next !== resetForm.value.confirm) {
    resetError.value = "Mật khẩu xác nhận không khớp";
    return;
  }
  resetBusy.value = true;
  try {
    const r = await resetPassword(resetToken.value, resetForm.value.next);
    if (r.ok) {
      resetSuccess.value = "✓ Đã đặt lại mật khẩu. Đăng nhập lại với mật khẩu mới.";
      resetForm.value = { next: "", confirm: "" };
      setTimeout(() => {
        showResetModal.value = false;
        resetSuccess.value = "";
        showLogin.value = true;
        loginTab.value = "login";
      }, 1800);
    } else {
      resetError.value = r.error || "Liên kết không hợp lệ hoặc đã hết hạn";
    }
  } finally {
    resetBusy.value = false;
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
  <div class="user-badge" ref="rootBadge">
    <!-- Logged-in state -->
    <template v-if="isAuthenticated">
      <button class="ub-pill" @click="showMenu = !showMenu" :title="personLabel">
        <span class="ub-avatar">👤</span>
        <span class="ub-name">{{ displayName }}</span>
        <span class="ub-role" :class="{ 'is-owner': isOwner }">{{ userRole }}</span>
        <span v-if="walletBalance !== null" class="ub-xu" title="Ví xu của tôi">🪙 {{ walletBalance }}</span>
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
        <button v-if="isOwner" class="ub-item" @click="openSwitchPerson">🔄 Chuyển hồ sơ</button>
        <button class="ub-item" @click="showWallet = true; showMenu = false">🪙 Ví xu của tôi<span v-if="walletBalance !== null" class="ub-item-bal">{{ walletBalance }} xu</span></button>
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

    <!-- Login / Signup modal -->
    <Teleport to="body"><WalletModal v-if="showWallet" @close="showWallet = false; loadWalletBalance()" /></Teleport>

    <Teleport to="body"><div v-if="showLogin" class="ub-modal-backdrop" @click.self="showLogin = false">
      <div class="ub-modal">
        <div class="ub-tabs">
          <button :class="{ active: loginTab === 'login' }" @click="loginTab = 'login'">🔑 Đăng nhập</button>
          <button :class="{ active: loginTab === 'signup' }" @click="loginTab = 'signup'">✨ Đăng ký</button>
        </div>

        <!-- Login form -->
        <form v-if="loginTab === 'login'" @submit.prevent="handleLogin">
          <label>Email
            <input v-model="loginForm.email" type="email" autofocus required />
          </label>
          <label>Mật khẩu
            <div class="ub-pw-wrap">
              <input v-model="loginForm.password" :type="showPw.login ? 'text' : 'password'" required />
              <button type="button" class="ub-pw-toggle" @click="togglePw('login')"
                      :aria-label="showPw.login ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.login ? '🙈' : '👁️' }}</button>
            </div>
          </label>
          <p v-if="loginError" class="ub-error">{{ loginError }}</p>
          <p class="ub-hint">
            <a href="#" class="ub-link" @click.prevent="loginTab = 'forgot'; forgotError = ''; forgotSuccess = ''">Quên mật khẩu?</a>
            · Chưa có tài khoản? Bấm tab <b>Đăng ký</b> bên trên.
          </p>
          <div class="ub-modal-actions">
            <button type="button" class="ub-btn-secondary" @click="showLogin = false">Huỷ</button>
            <button type="submit" class="ub-btn-primary">Đăng nhập</button>
          </div>
        </form>

        <!-- Forgot password form -->
        <form v-else-if="loginTab === 'forgot'" @submit.prevent="handleForgotPassword">
          <label>Email tài khoản
            <input v-model="forgotForm.email" type="email" autofocus required placeholder="email@example.com" />
          </label>
          <p v-if="forgotError" class="ub-error">{{ forgotError }}</p>
          <p v-if="forgotSuccess" class="ub-success">{{ forgotSuccess }}</p>
          <p class="ub-hint">Liên kết đặt lại mật khẩu sẽ được gửi qua email, hết hạn sau 30 phút.</p>
          <div class="ub-modal-actions">
            <button type="button" class="ub-btn-secondary" @click="loginTab = 'login'">← Quay lại đăng nhập</button>
            <button type="submit" class="ub-btn-primary" :disabled="forgotBusy">
              {{ forgotBusy ? "⏳ Đang gửi..." : "Gửi liên kết" }}
            </button>
          </div>
        </form>

        <!-- Signup form -->
        <form v-else-if="loginTab === 'signup'" @submit.prevent="handleSignup">
          <label>Email
            <input v-model="signupForm.email" type="email" autofocus required placeholder="email@example.com" />
          </label>
          <label>Tên hiển thị
            <input v-model="signupForm.display_name" type="text" required placeholder="Nguyễn Văn A" />
          </label>
          <label>Mật khẩu
            <div class="ub-pw-wrap">
              <input v-model="signupForm.password" :type="showPw.signupPw ? 'text' : 'password'" required minlength="6" placeholder="≥ 6 ký tự" />
              <button type="button" class="ub-pw-toggle" @click="togglePw('signupPw')"
                      :aria-label="showPw.signupPw ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.signupPw ? '🙈' : '👁️' }}</button>
            </div>
          </label>
          <label>Xác nhận mật khẩu
            <div class="ub-pw-wrap">
              <input v-model="signupForm.confirm" :type="showPw.signupConfirm ? 'text' : 'password'" required minlength="6" />
              <button type="button" class="ub-pw-toggle" @click="togglePw('signupConfirm')"
                      :aria-label="showPw.signupConfirm ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.signupConfirm ? '🙈' : '👁️' }}</button>
            </div>
          </label>
          <p v-if="signupError" class="ub-error">{{ signupError }}</p>
          <p class="ub-hint">Đăng ký miễn phí, không cần xác thực email. Bạn sẽ tự động đăng nhập.</p>
          <div class="ub-modal-actions">
            <button type="button" class="ub-btn-secondary" @click="showLogin = false">Huỷ</button>
            <button type="submit" class="ub-btn-primary" :disabled="signupBusy">
              {{ signupBusy ? "⏳ Đang tạo..." : "✨ Tạo tài khoản" }}
            </button>
          </div>
        </form>
      </div>
    </div></Teleport>

    <!-- Change password modal -->
    <Teleport to="body"><div v-if="showPasswordModal" class="ub-modal-backdrop" @click.self="showPasswordModal = false">
      <div class="ub-modal">
        <h3>🔐 Đổi mật khẩu</h3>
        <p v-if="currentUser?.must_change_password" class="ub-warn">
          ⚠️ Lần đăng nhập đầu — anh phải đổi mật khẩu mặc định.
        </p>
        <form @submit.prevent="submitChangePassword">
          <label>Mật khẩu hiện tại
            <div class="ub-pw-wrap">
              <input v-model="passwordForm.current" :type="showPw.pwCurrent ? 'text' : 'password'" required />
              <button type="button" class="ub-pw-toggle" @click="togglePw('pwCurrent')"
                      :aria-label="showPw.pwCurrent ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.pwCurrent ? '🙈' : '👁️' }}</button>
            </div>
          </label>
          <label>Mật khẩu mới (≥ 8 ký tự)
            <div class="ub-pw-wrap">
              <input v-model="passwordForm.next" :type="showPw.pwNext ? 'text' : 'password'" minlength="8" required />
              <button type="button" class="ub-pw-toggle" @click="togglePw('pwNext')"
                      :aria-label="showPw.pwNext ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.pwNext ? '🙈' : '👁️' }}</button>
            </div>
          </label>
          <label>Xác nhận mật khẩu mới
            <div class="ub-pw-wrap">
              <input v-model="passwordForm.confirm" :type="showPw.pwConfirm ? 'text' : 'password'" required />
              <button type="button" class="ub-pw-toggle" @click="togglePw('pwConfirm')"
                      :aria-label="showPw.pwConfirm ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.pwConfirm ? '🙈' : '👁️' }}</button>
            </div>
          </label>
          <p v-if="passwordError" class="ub-error">{{ passwordError }}</p>
          <p v-if="passwordSuccess" class="ub-success">{{ passwordSuccess }}</p>
          <div class="ub-modal-actions">
            <button type="button" class="ub-btn-secondary" @click="showPasswordModal = false">Đóng</button>
            <button type="submit" class="ub-btn-primary">Đổi mật khẩu</button>
          </div>
        </form>
      </div>
    </div></Teleport>

    <!-- Reset password modal — mở khi URL có ?reset_token=... (link trong email) -->
    <Teleport to="body"><div v-if="showResetModal" class="ub-modal-backdrop" @click.self="showResetModal = false">
      <div class="ub-modal">
        <h3>🔑 Đặt lại mật khẩu</h3>
        <form @submit.prevent="handleResetPassword">
          <label>Mật khẩu mới (≥ 8 ký tự)
            <div class="ub-pw-wrap">
              <input v-model="resetForm.next" :type="showPw.resetNext ? 'text' : 'password'" minlength="8" required autofocus />
              <button type="button" class="ub-pw-toggle" @click="togglePw('resetNext')"
                      :aria-label="showPw.resetNext ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.resetNext ? '🙈' : '👁️' }}</button>
            </div>
          </label>
          <label>Xác nhận mật khẩu mới
            <div class="ub-pw-wrap">
              <input v-model="resetForm.confirm" :type="showPw.resetConfirm ? 'text' : 'password'" required />
              <button type="button" class="ub-pw-toggle" @click="togglePw('resetConfirm')"
                      :aria-label="showPw.resetConfirm ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.resetConfirm ? '🙈' : '👁️' }}</button>
            </div>
          </label>
          <p v-if="resetError" class="ub-error">{{ resetError }}</p>
          <p v-if="resetSuccess" class="ub-success">{{ resetSuccess }}</p>
          <div class="ub-modal-actions">
            <button type="button" class="ub-btn-secondary" @click="showResetModal = false">Đóng</button>
            <button type="submit" class="ub-btn-primary" :disabled="resetBusy">
              {{ resetBusy ? "⏳ Đang xử lý..." : "Đặt lại mật khẩu" }}
            </button>
          </div>
        </form>
      </div>
    </div></Teleport>

    <!-- Switch person modal -->
    <Teleport to="body"><div v-if="showSwitchPersonModal" class="ub-modal-backdrop" @click.self="showSwitchPersonModal = false">
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
    </div></Teleport>

    <!-- Users management (owner only) -->
    <Teleport to="body"><div v-if="showUsersModal" class="ub-modal-backdrop" @click.self="showUsersModal = false">
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
          <label>Password (≥ 8 ký tự)
            <div class="ub-pw-wrap">
              <input v-model="newUserForm.password" :type="showPw.newUserPw ? 'text' : 'password'" minlength="8" required />
              <button type="button" class="ub-pw-toggle" @click="togglePw('newUserPw')"
                      :aria-label="showPw.newUserPw ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'">{{ showPw.newUserPw ? '🙈' : '👁️' }}</button>
            </div>
          </label>
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
    </div></Teleport>
  </div>
</template>

<!-- Not scoped: modal is Teleported to <body>, so styles must be global.
     All selectors are prefixed with `.ub-` to avoid collisions. -->
<style>
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
  display: flex;
  align-items: center;
  gap: 6px;
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
.ub-item-bal { margin-left: auto; font-size: 0.78rem; font-weight: 600; color: #e8c95a; }
.ub-danger { color: #fca5a5; }
.ub-danger:hover { background: rgba(239, 68, 68, 0.15); }

/* Số dư xu trên chip header (at-a-glance) */
.ub-xu {
  font-size: 0.74rem;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 999px;
  white-space: nowrap;
  color: #e8c95a;
  background: rgba(232, 201, 90, 0.16);
  border: 1px solid rgba(232, 201, 90, 0.4);
}

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
  max-height: 90vh;
  overflow-y: auto;
  color: #e2e8f0;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6);
  /* Ensure form inputs have breathing room — signup form has 4 fields + hint */
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.ub-modal form { display: flex; flex-direction: column; gap: 0.55rem; }
.ub-modal-wide { max-width: 800px; }
.ub-modal h3 { margin: 0 0 0.8rem 0; color: #fde68a; }
.ub-tabs {
  display: flex; gap: 0; margin-bottom: 1rem;
  border-bottom: 1px solid #334155;
}
.ub-tabs button {
  flex: 1; background: transparent; border: none; color: #94a3b8;
  padding: 0.6rem 0.4rem; cursor: pointer; font-size: 0.9rem;
  font-weight: 600; border-bottom: 2px solid transparent;
  transition: all 0.15s;
}
.ub-tabs button:hover { color: #cbd5e1; }
.ub-tabs button.active {
  color: #fde68a; border-bottom-color: #f59e0b;
}
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

/* Nút hiện/ẩn mật khẩu (👁️/🙈) — icon tuyệt đối bên phải ô input */
.ub-pw-wrap { position: relative; }
.ub-pw-wrap input { padding-right: 2.1rem; }
.ub-pw-toggle {
  position: absolute; right: 0.35rem; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer;
  font-size: 0.95rem; line-height: 1; padding: 2px 4px;
  opacity: 0.75;
}
.ub-pw-toggle:hover { opacity: 1; }
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
.ub-link { color: #60a5fa; text-decoration: none; }
.ub-link:hover { text-decoration: underline; }

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

@media (max-width: 560px) {
  .ub-pill {
    max-width: min(52vw, 220px);
    padding: 0.4rem 0.65rem 0.4rem 0.5rem;
    font-size: 0.8rem;
  }
  .ub-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 7.5rem;
  }
  .ub-role,
  .ub-caret {
    display: none;
  }
  .ub-xu {
    font-size: 0.7rem;
    padding: 1px 5px;
  }
  .ub-menu {
    position: fixed;
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    min-width: 0;
    border-radius: 12px 12px 0 0;
    padding: 0.6rem 0.6rem calc(0.6rem + env(safe-area-inset-bottom, 0px));
    max-height: 78vh;
    overflow-y: auto;
    z-index: 1600;
  }
  .ub-modal-backdrop {
    align-items: flex-end;
    padding: 0;
  }
  .ub-modal {
    width: 100%;
    max-width: none;
    border-radius: 12px 12px 0 0;
    max-height: 92vh;
    padding: 1rem 1.1rem calc(1rem + env(safe-area-inset-bottom, 0px));
  }
  .ub-modal-wide {
    max-width: none;
  }
  .ub-users-table {
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}
</style>
