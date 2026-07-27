/**
 * tuviPersonStore — chọn người để phân tích Tử Vi.
 *
 * MỘT NGUỒN SỰ THẬT (Anh chốt 2026-07-18): người đang xem = `activePerson`
 * của userDataStore (= hồ sơ tài khoản đang chọn). Muốn xem người khác →
 * chọn lại profile (setActivePerson). tuviPersonStore chỉ là VIEW mỏng lên
 * activePerson để các panel Tử Vi (DaiVan/LuuNien/CachCuc/PhuThaiVi/VanHan) dùng.
 * KHÔNG còn override riêng lệch với account picker.
 */
import { computed, ref, watch } from "vue";
import { currentPerson, sessionToken } from "./authStore.js";
import { activePerson, setActivePerson, personLabel } from "./userDataStore.js";

// Fallback DUY NHẤT cho person ad-hoc không có key (guest gõ tay, chưa lưu hồ sơ).
// activePerson (hồ sơ tài khoản) LUÔN ưu tiên → hai picker không bao giờ lệch.
const _override = ref(null);

export const tuviPerson = computed(
  () => activePerson.value || currentPerson.value || _override.value || null,
);

export const tuviPersonKey = computed(() => {
  const p = tuviPerson.value;
  if (!p) return "_founder";
  return p.person_id || p.person_key || "_founder";
});

export const tuviPersonName = computed(() => {
  const p = tuviPerson.value;
  if (!p) return "anh (Founder)";
  return personLabel(p);           // coi 'self'/'_founder'/rỗng như chưa có tên → nhãn quan hệ
});

export const tuviPersonBirth = computed(() => tuviPerson.value?.birth_datetime_local || "");
export const tuviPersonGender = computed(() => tuviPerson.value?.gender || "nam");

export function setTuviPerson(person) {
  // Chọn người Tử Vi = chọn lại profile tài khoản (một nguồn). Person có key
  // (hồ sơ đã lưu) → đặt active person; ad-hoc không key → giữ tạm ở _override.
  const key = person?.person_key || person?.person_id;
  if (key) {
    setActivePerson(key);
    _override.value = null;
  } else {
    _override.value = person || null;
  }
}

export function clearTuviPersonOverride() {
  _override.value = null;
}

// ── Persons list cache ──────────────────────────────────────────────────────
export const availablePersons = ref([]);
export const loadingPersons = ref(false);

function _authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (sessionToken.value) h["X-Session-Token"] = sessionToken.value;
  return h;
}

export async function fetchAvailablePersons() {
  loadingPersons.value = true;
  try {
    const r = await fetch("/api/auth/persons", {
      headers: _authHeaders(),
      credentials: "include",
    });
    if (!r.ok) {
      // Guest fallback — empty (no leak of founder profile).
      // After 2026-05-27 privacy audit + Iron Rule #7: do NOT expose founder
      // birth to logged-out users. UI should prompt login instead.
      availablePersons.value = [];
      return;
    }
    const d = await r.json();
    availablePersons.value = d.persons || [];
  } catch (e) {
    availablePersons.value = [];
  } finally {
    loadingPersons.value = false;
  }
}

// Auto-refresh persons list when auth changes.
watch(currentPerson, () => fetchAvailablePersons(), { immediate: false });

// ── Analyze API helpers ─────────────────────────────────────────────────────

export async function fetchCachedAnalysis(personKey, kind) {
  const r = await fetch(`/api/tu-vi/analyze/${encodeURIComponent(personKey)}/${kind}`, {
    headers: _authHeaders(),
    credentials: "include",
  });
  return r.json();
}

export async function runAnalysis(personKey, kind, options = {}) {
  const body = {
    person_key: personKey,
    luu_nien_start: options.luu_nien_start ?? 2026,
    luu_nien_end: options.luu_nien_end ?? 2030,
    luu_nguyet_year: options.luu_nguyet_year ?? 2026,
    phu_top_n: options.phu_top_n ?? 5,
    force: !!options.force,
  };
  // If person not in DB (ad-hoc), pass birth directly
  if (options.birth_datetime_local) {
    body.birth_datetime_local = options.birth_datetime_local;
    body.gender = options.gender;
    body.name = options.name;
  }
  const r = await fetch(`/api/tu-vi/analyze/${kind}`, {
    method: "POST",
    headers: _authHeaders(),
    credentials: "include",
    body: JSON.stringify(body),
  });
  return r.json();
}

export async function runAllAnalyses(personKey, options = {}) {
  return runAnalysis(personKey, "all", options);
}

// ── Background job runner ───────────────────────────────────────────────────
export async function runFullPipelineBackground(personKey) {
  const r = await fetch(`/api/tu-vi/run-all/${encodeURIComponent(personKey)}`, {
    method: "POST",
    headers: _authHeaders(),
    credentials: "include",
  });
  return r.json();
}

export async function pollJobStatus(jobId) {
  const r = await fetch(`/api/tu-vi/job-status/${encodeURIComponent(jobId)}`, {
    headers: _authHeaders(),
    credentials: "include",
  });
  return r.json();
}

export function pdfReportUrl(personKey) {
  return `/api/tu-vi/report-pdf/${encodeURIComponent(personKey)}`;
}

