/**
 * Auth store — current user + session token.
 *
 * Calls `/api/auth/me` on init. If logged in, exposes `currentUser` + `currentPerson`.
 * If guest, `currentUser` is null but `guestPerson` falls back to founder
 * (so panels can still default to anh's 1988 profile without forcing login).
 */
import { ref, computed } from "vue";

const STORAGE_KEY = "yi-chronos-auth-v1";

export const currentUser = ref(null);
export const currentPerson = ref(null);
export const sessionToken = ref(null);
export const isLoadingAuth = ref(false);
export const authError = ref("");

function _persist() {
  if (typeof window === "undefined") return;
  if (sessionToken.value) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ token: sessionToken.value }));
  } else {
    window.localStorage.removeItem(STORAGE_KEY);
  }
}

function _load() {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export const isAuthenticated = computed(() => !!currentUser.value);
export const isOwner = computed(() => currentUser.value?.role === "owner");

function _authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

export async function loadCurrentUser() {
  isLoadingAuth.value = true;
  authError.value = "";
  try {
    const r = await fetch("/api/auth/me", {
      headers: _authHeaders(),
      credentials: "include",
    });
    const d = await r.json();
    if (d.status === "ok") {
      currentUser.value = d.user;
      currentPerson.value = d.person;
    } else {
      // Guest — still expose founder fallback person
      currentUser.value = null;
      currentPerson.value = d.person;
    }
  } catch (err) {
    authError.value = err?.message || String(err);
    currentUser.value = null;
  } finally {
    isLoadingAuth.value = false;
  }
}

export async function login(email, password) {
  isLoadingAuth.value = true;
  authError.value = "";
  try {
    const r = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    });
    const d = await r.json();
    if (!r.ok) {
      authError.value = d?.detail || "Đăng nhập thất bại";
      return { ok: false, error: authError.value };
    }
    currentUser.value = d.user;
    currentPerson.value = d.person;
    sessionToken.value = d.session_token;
    _persist();
    return { ok: true, user: d.user };
  } catch (err) {
    authError.value = err?.message || String(err);
    return { ok: false, error: authError.value };
  } finally {
    isLoadingAuth.value = false;
  }
}

export async function logout() {
  try {
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: _authHeaders(),
      credentials: "include",
    });
  } catch {}
  currentUser.value = null;
  currentPerson.value = null;
  sessionToken.value = null;
  _persist();
}

export async function listUsers() {
  const r = await fetch("/api/auth/users", {
    headers: _authHeaders(),
    credentials: "include",
  });
  if (!r.ok) throw new Error(`listUsers: ${r.status}`);
  return r.json();
}

export async function listPersons() {
  const r = await fetch("/api/auth/persons", {
    headers: _authHeaders(),
    credentials: "include",
  });
  if (!r.ok) throw new Error(`listPersons: ${r.status}`);
  return r.json();
}

export async function switchPerson(personId) {
  const r = await fetch("/api/auth/switch-person", {
    method: "POST",
    headers: _authHeaders(),
    credentials: "include",
    body: JSON.stringify({ person_id: personId }),
  });
  if (!r.ok) {
    const d = await r.json().catch(() => ({}));
    throw new Error(d.detail || `switchPerson: ${r.status}`);
  }
  const d = await r.json();
  currentPerson.value = d.person;
  return d;
}

export async function changePassword(currentPassword, newPassword) {
  const r = await fetch("/api/auth/change-password", {
    method: "POST",
    headers: _authHeaders(),
    credentials: "include",
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || "Đổi mật khẩu thất bại");
  // Refresh me
  await loadCurrentUser();
  return d;
}

export async function registerUser(payload) {
  // payload: { email, display_name, password, default_person_id, role }
  const r = await fetch("/api/auth/register", {
    method: "POST",
    headers: _authHeaders(),
    credentials: "include",
    body: JSON.stringify(payload),
  });
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || "Tạo user thất bại");
  return d;
}

// Bootstrap on import
(function bootstrap() {
  const saved = _load();
  if (saved?.token) sessionToken.value = saved.token;
  loadCurrentUser();
})();
