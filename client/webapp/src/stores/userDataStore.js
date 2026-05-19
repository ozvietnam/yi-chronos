/**
 * userDataStore — reactive store cho user-namespaced data (persons + castings).
 *
 * Khi đã login: load từ /api/auth/my/persons (DB)
 * Khi guest: dùng profileStore.js (localStorage) — backward compat
 *
 * Mỗi user có data RIÊNG (FOREIGN KEY user_id trong users.sqlite3).
 * Founder (anh) login = thấy data anh; testuser login = thấy data testuser.
 */
import { ref, computed, watch } from "vue";
import { currentUser, sessionToken, isAuthenticated } from "./authStore.js";
import {
  persons as guestPersons,
  activePerson as guestActivePerson,
} from "./profileStore.js";

// ─── API-backed state (when logged in) ──────────────────────────────────────
export const apiPersons = ref([]);
export const apiActivePersonKey = ref(null);
export const isSyncing = ref(false);
export const syncError = ref("");

function _headers() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

// ─── Reactive merged source ─────────────────────────────────────────────────

/**
 * persons: list of person objects.
 * - When logged in: API-backed (user_persons table).
 * - When guest: localStorage profileStore.persons.
 */
export const persons = computed(() => {
  if (isAuthenticated.value) return apiPersons.value;
  return guestPersons.value;
});

/**
 * activePerson: the person whose birth is used as default in panels.
 */
export const activePerson = computed(() => {
  if (isAuthenticated.value) {
    const key = apiActivePersonKey.value;
    if (key) {
      const found = apiPersons.value.find((p) => p.person_key === key);
      if (found) return found;
    }
    // default: 'self' role
    return apiPersons.value.find((p) => p.relationship === "self")
        || apiPersons.value[0]
        || null;
  }
  return guestActivePerson.value;
});

export const activeBirthDatetime = computed(() => {
  const p = activePerson.value;
  return p?.birth_datetime_local || "";
});

// ─── API operations ──────────────────────────────────────────────────────────

export async function loadMyPersons() {
  if (!isAuthenticated.value) return;
  isSyncing.value = true;
  syncError.value = "";
  try {
    const r = await fetch("/api/auth/my/persons", {
      headers: _headers(),
      credentials: "include",
    });
    if (!r.ok) throw new Error(`loadMyPersons: ${r.status}`);
    const d = await r.json();
    apiPersons.value = d.persons || [];
    // Set active if not yet set
    if (!apiActivePersonKey.value && apiPersons.value.length) {
      const self = apiPersons.value.find((p) => p.relationship === "self");
      apiActivePersonKey.value = (self || apiPersons.value[0]).person_key;
    }
  } catch (err) {
    syncError.value = err.message;
  } finally {
    isSyncing.value = false;
  }
}

export async function addMyPerson(payload) {
  // payload: { person_key, name, relationship, gender, birth_datetime_local, birth_year, ... }
  const r = await fetch("/api/auth/my/persons", {
    method: "POST",
    headers: _headers(),
    credentials: "include",
    body: JSON.stringify(payload),
  });
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || `addMyPerson: ${r.status}`);
  await loadMyPersons();
  return d;
}

export async function updateMyPerson(id, patch) {
  const r = await fetch(`/api/auth/my/persons/${id}`, {
    method: "PATCH",
    headers: _headers(),
    credentials: "include",
    body: JSON.stringify(patch),
  });
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || `updateMyPerson: ${r.status}`);
  await loadMyPersons();
  return d;
}

export async function deleteMyPerson(id) {
  const r = await fetch(`/api/auth/my/persons/${id}`, {
    method: "DELETE",
    headers: _headers(),
    credentials: "include",
  });
  if (!r.ok) {
    const d = await r.json().catch(() => ({}));
    throw new Error(d.detail || `deleteMyPerson: ${r.status}`);
  }
  await loadMyPersons();
}

export function setActivePerson(personKey) {
  apiActivePersonKey.value = personKey;
}

// ─── Auto-save casting helper ───────────────────────────────────────────────

/**
 * saveCasting — gọi sau khi cast quẻ thành công.
 * Tự động ghi vào user_castings (silent fail nếu guest, không cản trở).
 *
 * @param {object} req — { method, subject_person_key?, question?, input_json?, result_json, verdict?, tags?, note? }
 */
export async function saveCasting(req) {
  if (!isAuthenticated.value) return null;  // guest skip
  try {
    const r = await fetch("/api/auth/my/castings", {
      method: "POST",
      headers: _headers(),
      credentials: "include",
      body: JSON.stringify(req),
    });
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
}

export async function listMyCastings({ method = null, limit = 50, offset = 0 } = {}) {
  if (!isAuthenticated.value) return { castings: [], count: 0 };
  const params = new URLSearchParams();
  if (method) params.set("method", method);
  params.set("limit", limit);
  params.set("offset", offset);
  const r = await fetch(`/api/auth/my/castings?${params}`, {
    headers: _headers(),
    credentials: "include",
  });
  if (!r.ok) throw new Error(`listMyCastings: ${r.status}`);
  return r.json();
}

export async function deleteCasting(id) {
  const r = await fetch(`/api/auth/my/castings/${id}`, {
    method: "DELETE",
    headers: _headers(),
    credentials: "include",
  });
  if (!r.ok) throw new Error(`deleteCasting: ${r.status}`);
}

// ─── Favorites ───────────────────────────────────────────────────────────────

export async function saveFavorite(kind, label, payload_json) {
  if (!isAuthenticated.value) return null;
  try {
    const r = await fetch("/api/auth/my/favorites", {
      method: "POST",
      headers: _headers(),
      credentials: "include",
      body: JSON.stringify({ kind, label, payload_json }),
    });
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
}

export async function listFavorites(kind = null) {
  if (!isAuthenticated.value) return { favorites: [], count: 0 };
  const params = kind ? `?kind=${encodeURIComponent(kind)}` : "";
  const r = await fetch(`/api/auth/my/favorites${params}`, {
    headers: _headers(),
    credentials: "include",
  });
  if (!r.ok) throw new Error(`listFavorites: ${r.status}`);
  return r.json();
}

// ─── Auto-load when login/logout ────────────────────────────────────────────

watch(currentUser, (val) => {
  if (val) {
    loadMyPersons();
  } else {
    apiPersons.value = [];
    apiActivePersonKey.value = null;
  }
}, { immediate: true });
