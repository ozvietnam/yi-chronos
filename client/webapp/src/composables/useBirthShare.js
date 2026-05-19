/**
 * useBirthShare — URL share contract `?birth=YYYY-MM-DD-HH-{nam|nu}`.
 *
 * Matches the kabala.vn community convention so any link from
 * battu.kabala.vn / dich.kabala.vn / matrix.kabala.vn that uses this
 * pattern can be pasted into YI-CHRONOS and auto-fills.
 *
 * Behavior on app mount:
 *   - If URL contains ?birth=..., parse it; create a TEMPORARY in-memory
 *     "URL-driven" Person and activate it. This person is NOT persisted to
 *     localStorage (so it won't pollute the user's profile list).
 *   - If parsing fails, the param is silently ignored.
 *
 * Behavior when a chart is computed:
 *   - Components can call `buildShareLink(...)` to get a URL with the current
 *     active person's birth encoded — copyable to clipboard.
 */

import { ref } from "vue";

import {
  activePerson,
  activePersonId,
  addPerson,
  persons,
} from "../stores/profileStore.js";

const URL_DRIVEN_PERSON_NAME = "👤 Khách (từ URL)";

// -----------------------------------------------------------------------------
// Parse
// -----------------------------------------------------------------------------

/**
 * Parse a birth slug into `{ birthDatetimeLocal, gender, source }`.
 * Returns null on any invalid input.
 *
 * Accepted formats (in priority order):
 *   1. YYYY-MM-DD-HH-{nam|nu|nữ}            e.g. "1995-08-15-10-nam"
 *   2. YYYY-MM-DD-HH                         (gender unknown → null)
 *   3. YYYY-MM-DDTHH:MM:SS                   (ISO local — fallback)
 *
 * Validation:
 *   - Year 1900..2100
 *   - Month 1..12, Day 1..31, Hour 0..23
 *   - Gender ∈ {nam, nữ, nu} (case-insensitive); "nu" normalizes to "nữ"
 */
export function parseBirthSlug(raw) {
  if (!raw || typeof raw !== "string") return null;
  const slug = raw.trim();
  if (!slug) return null;

  // Format 3: ISO datetime fallback.
  if (slug.includes("T")) {
    const iso = slug.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/);
    if (iso) {
      const [, y, m, d, h, mi, s = "00"] = iso;
      if (_isValidDate(+y, +m, +d, +h, +mi, +s)) {
        return {
          birthDatetimeLocal: `${y}-${m}-${d}T${h}:${mi}:${s}`,
          gender: null,
          source: "iso",
        };
      }
    }
  }

  // Format 1 & 2: dash-separated with optional gender suffix.
  const parts = slug.split("-");
  if (parts.length < 4 || parts.length > 5) return null;

  const [y, m, d, h, genderRaw] = parts;
  if (!/^\d{4}$/.test(y)) return null;
  if (!/^\d{1,2}$/.test(m) || !/^\d{1,2}$/.test(d) || !/^\d{1,2}$/.test(h)) return null;

  const year = +y;
  const month = +m;
  const day = +d;
  const hour = +h;
  if (!_isValidDate(year, month, day, hour, 0, 0)) return null;

  let gender = null;
  if (genderRaw !== undefined) {
    const g = genderRaw.toLowerCase();
    if (g === "nam") gender = "nam";
    else if (g === "nu" || g === "nữ" || g === "nuu") gender = "nữ";
    else return null; // unknown gender token → reject the whole slug
  }

  const pad = (n) => String(n).padStart(2, "0");
  return {
    birthDatetimeLocal: `${year}-${pad(month)}-${pad(day)}T${pad(hour)}:00:00`,
    gender,
    source: "kabala",
  };
}

function _isValidDate(y, m, d, h, mi, s) {
  if (y < 1900 || y > 2100) return false;
  if (m < 1 || m > 12) return false;
  if (d < 1 || d > 31) return false;
  if (h < 0 || h > 23) return false;
  if (mi < 0 || mi > 59) return false;
  if (s < 0 || s > 59) return false;
  return true;
}

// -----------------------------------------------------------------------------
// Encode
// -----------------------------------------------------------------------------

/**
 * Encode `{ birthDatetimeLocal, gender }` into a kabala-style slug.
 * Returns null if the datetime is malformed.
 *
 * Examples:
 *   ({ birthDatetimeLocal: "1995-08-15T10:30:00", gender: "nam" })
 *     → "1995-08-15-10-nam"
 *   ({ birthDatetimeLocal: "1995-08-15T10:00:00", gender: null })
 *     → "1995-08-15-10"
 */
export function encodeBirthSlug({ birthDatetimeLocal, gender = null } = {}) {
  if (!birthDatetimeLocal || typeof birthDatetimeLocal !== "string") return null;
  const m = birthDatetimeLocal.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2})(?::\d{2})?(?::\d{2})?$/);
  if (!m) return null;
  const [, y, mo, d, h] = m;
  const stem = `${y}-${mo}-${d}-${h}`;
  if (gender === "nam") return `${stem}-nam`;
  if (gender === "nữ" || gender === "nu") return `${stem}-nu`;
  return stem;
}

// -----------------------------------------------------------------------------
// URL helpers
// -----------------------------------------------------------------------------

export function readBirthFromUrl() {
  if (typeof window === "undefined") return null;
  const url = new URL(window.location.href);
  const raw = url.searchParams.get("birth");
  return parseBirthSlug(raw);
}

/**
 * Construct a full shareable URL with `?birth=<slug>` set.
 * Keeps the current pathname + other query params; drops the hash.
 */
export function buildShareLink({ birthDatetimeLocal, gender = null } = {}) {
  if (typeof window === "undefined") return "";
  const slug = encodeBirthSlug({ birthDatetimeLocal, gender });
  if (!slug) return "";
  const url = new URL(window.location.href);
  url.searchParams.set("birth", slug);
  url.hash = "";
  return url.toString();
}

/**
 * Sync the current URL to a given birth (without page reload).
 * Pass `null` to remove the birth param.
 */
export function syncBirthInUrl({ birthDatetimeLocal, gender = null } = {}) {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  if (birthDatetimeLocal) {
    const slug = encodeBirthSlug({ birthDatetimeLocal, gender });
    if (slug) url.searchParams.set("birth", slug);
  } else {
    url.searchParams.delete("birth");
  }
  window.history.replaceState({}, "", url.toString());
}

// -----------------------------------------------------------------------------
// Apply URL on mount — create ephemeral active person
// -----------------------------------------------------------------------------

const urlDrivenApplied = ref(false);

/**
 * Read the URL once on app mount. If `?birth=` is valid AND no active person
 * is set, create a URL-driven Person and activate it.
 *
 * Idempotent: only runs once per page load.
 *
 * Returns the parsed slug (or null) so the caller can show a banner.
 */
export function applyBirthFromUrlOnMount() {
  if (urlDrivenApplied.value) return null;
  urlDrivenApplied.value = true;

  const parsed = readBirthFromUrl();
  if (!parsed) return null;

  // Don't override if user already has an active person.
  if (activePerson.value && activePerson.value.birth_datetime_local) {
    return parsed;
  }

  // Check if a URL-driven person with the exact same birth already exists
  // (e.g. user reloads page) — reuse it instead of duplicating.
  const existing = persons.value.find(
    (p) =>
      p.name === URL_DRIVEN_PERSON_NAME &&
      p.birth_datetime_local === parsed.birthDatetimeLocal
  );
  if (existing) {
    activePersonId.value = existing.id;
    return parsed;
  }

  const birthYear = Number(parsed.birthDatetimeLocal.slice(0, 4));
  const person = addPerson({
    name: URL_DRIVEN_PERSON_NAME,
    role: "other",
    birth_year: birthYear,
    birth_datetime_local: parsed.birthDatetimeLocal,
    timezone: "Asia/Ho_Chi_Minh",
    notes: "Tạo tự động từ URL ?birth=. Có thể đổi tên / xóa trong tab Profiles.",
  });
  activePersonId.value = person.id;
  return parsed;
}
