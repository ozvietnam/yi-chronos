/**
 * Profiles demo / multi-user không đăng nhập — lưu localStorage.
 */
const STORAGE_KEY = "yi-chronos-demo-profiles";

/** Mặc định mở app: Lại Minh Thắng, sinh DL 05/06/1988 Hà Nội (giờ 12:00 mẫu; đổi trong form khi có giờ thật). */
export function createDemoLaMinhThangProfile() {
  return {
    id: "demo-la-minh-thang",
    label: "Lại Minh Thắng",
    birth_datetime_local: "1988-06-05T12:00:00",
    timezone: "Asia/Ho_Chi_Minh",
    location_ref: "Hà Nội",
    birth_precision: "exact",
    gender_optional: null
  };
}

export function createEmptyProfile(label = "Hồ sơ mới") {
  return {
    id: typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `p_${Date.now()}`,
    label,
    birth_datetime_local: "1990-01-01T12:00:00",
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
