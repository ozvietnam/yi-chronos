/**
 * Profiles demo / multi-user không đăng nhập — lưu localStorage.
 */
const STORAGE_KEY = "yi-chronos-demo-profiles";

/**
 * Demo founder profile — DEPRECATED.
 * KHÔNG dùng trong production. Privacy 2026-05-27: founder data chỉ phục
 * vụ qua API auth-gated, không expose qua frontend hardcoded.
 * Giữ stub này tránh break import nhưng trả empty profile.
 */
export function createDemoLaMinhThangProfile() {
  return createEmptyProfile("Hồ sơ demo (cần điền)");
}

export function createEmptyProfile(label = "Hồ sơ mới") {
  return {
    id: typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `p_${Date.now()}`,
    label,
    birth_datetime_local: "",
    timezone: "Asia/Ho_Chi_Minh",
    location_ref: "",
    birth_precision: "exact",
    gender_optional: null
  };
}

/** Chỉ các field backend chấp nhận cho /api/personal-profile */
export function toPersonalProfileApiPayload(formOrProfile) {
  const {
    birth_datetime_local,
    timezone,
    location_ref,
    birth_precision,
    gender_optional
  } = formOrProfile;
  return {
    birth_datetime_local,
    timezone,
    location_ref: location_ref || null,
    birth_precision,
    gender_optional: gender_optional ?? null
  };
}

/** @returns {{ profiles: object[], activeId: string }} */
export function loadProfilesState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      const demo = createDemoLaMinhThangProfile();
      return { profiles: [demo], activeId: demo.id };
    }
    const parsed = JSON.parse(raw);
    const profiles = Array.isArray(parsed.profiles) ? parsed.profiles : null;
    const activeId =
      typeof parsed.activeId === "string" &&
      profiles?.some((p) => p.id === parsed.activeId)
        ? parsed.activeId
        : profiles?.[0]?.id;
    if (!profiles?.length) {
      const demo = createDemoLaMinhThangProfile();
      return { profiles: [demo], activeId: demo.id };
    }
    return {
      profiles: profiles.map(normalizeStoredProfile),
      activeId: activeId || profiles[0].id
    };
  } catch {
    const demo = createDemoLaMinhThangProfile();
    return { profiles: [demo], activeId: demo.id };
  }
}

function normalizeStoredProfile(p) {
  if (!p || typeof p !== "object") return createEmptyProfile();
  return {
    id: typeof p.id === "string" ? p.id : createEmptyProfile().id,
    label: typeof p.label === "string" ? p.label : "Không tên",
    birth_datetime_local:
      typeof p.birth_datetime_local === "string" ? p.birth_datetime_local : "1990-01-01T12:00:00",
    timezone: typeof p.timezone === "string" ? p.timezone : "Asia/Ho_Chi_Minh",
    location_ref: typeof p.location_ref === "string" ? p.location_ref : "",
    birth_precision: ["exact", "approx", "unknown"].includes(p.birth_precision)
      ? p.birth_precision
      : "exact",
    gender_optional: p.gender_optional ?? null
  };
}

export function persistProfilesState({ profiles, activeId }) {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        profiles,
        activeId
      })
    );
  } catch {
    /* ignore quota / privacy mode */
  }
}
