/**
 * Unified profile store — 4 entity types managed in one place.
 *
 * Entities:
 *   - Person       a real human (self, family member, colleague, etc.)
 *   - Family       a household linking multiple Persons
 *   - Organization a company / team / school
 *   - Event        a confirmed-fact past event used for validation
 *
 * Each entity has a unique ID; all stored in localStorage.
 * The `activePersonId` ref drives which Person is the "self" for school
 * panels (chiêm tinh / Mai Hoa / Lục Hào).
 *
 * Backward-compat note: this module re-exports `familyMembers`,
 * `weddingDatetime`, `serializableMembers`, `setFamily`, `clearFamily`
 * so existing imports from `familyStore.js` keep working through a thin
 * shim — see familyStore.js for the bridge.
 */

import { computed, ref, watch } from "vue";

const STORAGE_KEY = "yi-chronos-profiles-v1";
const LEGACY_FAMILY_KEY = "yi-chronos-family-v1";

// -----------------------------------------------------------------------------
// Reactive state
// -----------------------------------------------------------------------------

export const persons = ref([]);
export const families = ref([]);
export const organizations = ref([]);
export const events = ref([]);
export const activePersonId = ref(null);

// -----------------------------------------------------------------------------
// Persistence
// -----------------------------------------------------------------------------

function loadFromStorage() {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (err) {
    return null;
  }
}

function loadLegacyFamily() {
  // Migrate from familyStore.js (v1) to the new schema on first load.
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(LEGACY_FAMILY_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function persist() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        persons: persons.value,
        families: families.value,
        organizations: organizations.value,
        events: events.value,
        activePersonId: activePersonId.value,
      })
    );
  } catch (err) {
    /* localStorage full or blocked */
  }
}

watch(persons, persist, { deep: true });
watch(families, persist, { deep: true });
watch(organizations, persist, { deep: true });
watch(events, persist, { deep: true });
watch(activePersonId, persist);

// -----------------------------------------------------------------------------
// ID generation
// -----------------------------------------------------------------------------

function newId(prefix) {
  const random = Math.random().toString(36).slice(2, 10);
  const time = Date.now().toString(36);
  return `${prefix}_${time}${random}`;
}

// -----------------------------------------------------------------------------
// Person CRUD
// -----------------------------------------------------------------------------

export const PERSON_ROLES = [
  { value: "self", label: "Bản thân" },
  { value: "spouse", label: "Vợ / Chồng" },
  { value: "child", label: "Con" },
  { value: "parent", label: "Cha / Mẹ" },
  { value: "sibling", label: "Anh chị em" },
  { value: "colleague", label: "Đồng nghiệp" },
  { value: "friend", label: "Bạn" },
  { value: "other", label: "Khác" },
];

export function addPerson(data) {
  const person = {
    id: newId("p"),
    name: data.name || "",
    role: data.role || "other",
    birth_year: Number(data.birth_year) || null,
    birth_datetime_local: data.birth_datetime_local || "",
    birth_location: data.birth_location || "",
    timezone: data.timezone || "Asia/Ho_Chi_Minh",
    notes: data.notes || "",
  };
  persons.value = [...persons.value, person];
  if (!activePersonId.value && person.role === "self") {
    activePersonId.value = person.id;
  }
  return person;
}

export function updatePerson(id, patch) {
  persons.value = persons.value.map((p) => (p.id === id ? { ...p, ...patch } : p));
}

export function removePerson(id) {
  persons.value = persons.value.filter((p) => p.id !== id);
  // Cascade clean from families/orgs/events.
  families.value = families.value.map((f) => ({
    ...f,
    member_ids: f.member_ids.filter((mid) => mid !== id),
  }));
  organizations.value = organizations.value.map((o) => ({
    ...o,
    member_links: o.member_links.filter((m) => m.person_id !== id),
  }));
  events.value = events.value.map((e) => ({
    ...e,
    related_person_ids: e.related_person_ids.filter((pid) => pid !== id),
  }));
  if (activePersonId.value === id) {
    activePersonId.value = null;
  }
}

export function getPersonById(id) {
  return persons.value.find((p) => p.id === id) || null;
}

export const activePerson = computed(() => getPersonById(activePersonId.value));

export function setActivePerson(id) {
  activePersonId.value = id;
}

// -----------------------------------------------------------------------------
// Family CRUD
// -----------------------------------------------------------------------------

export function addFamily(data) {
  const family = {
    id: newId("f"),
    name: data.name || "Gia đình",
    member_ids: data.member_ids || [],
    wedding_datetime_local: data.wedding_datetime_local || "",
    wedding_timezone: data.wedding_timezone || "Asia/Ho_Chi_Minh",
    notes: data.notes || "",
  };
  families.value = [...families.value, family];
  return family;
}

export function updateFamily(id, patch) {
  families.value = families.value.map((f) => (f.id === id ? { ...f, ...patch } : f));
}

export function removeFamily(id) {
  families.value = families.value.filter((f) => f.id !== id);
}

export function getFamilyById(id) {
  return families.value.find((f) => f.id === id) || null;
}

// -----------------------------------------------------------------------------
// Organization CRUD
// -----------------------------------------------------------------------------

export const ORG_TYPES = [
  { value: "company", label: "Công ty" },
  { value: "team", label: "Đội nhóm" },
  { value: "school", label: "Trường học" },
  { value: "association", label: "Hội nhóm" },
  { value: "other", label: "Khác" },
];

export function addOrganization(data) {
  const org = {
    id: newId("o"),
    name: data.name || "",
    type: data.type || "company",
    founded_datetime_local: data.founded_datetime_local || "",
    founded_timezone: data.founded_timezone || "Asia/Ho_Chi_Minh",
    member_links: data.member_links || [], // [{ person_id, role }]
    notes: data.notes || "",
  };
  organizations.value = [...organizations.value, org];
  return org;
}

export function updateOrganization(id, patch) {
  organizations.value = organizations.value.map((o) =>
    o.id === id ? { ...o, ...patch } : o
  );
}

export function removeOrganization(id) {
  organizations.value = organizations.value.filter((o) => o.id !== id);
  events.value = events.value.map((e) => ({
    ...e,
    related_org_ids: e.related_org_ids.filter((oid) => oid !== id),
  }));
}

export function getOrganizationById(id) {
  return organizations.value.find((o) => o.id === id) || null;
}

// -----------------------------------------------------------------------------
// Event CRUD — confirmed-fact past events for school-output validation.
// -----------------------------------------------------------------------------

export const EVENT_OUTCOMES = [
  { value: "favorable", label: "Thuận lợi" },
  { value: "neutral", label: "Trung tính" },
  { value: "challenging", label: "Khó khăn" },
  { value: "unknown", label: "Chưa rõ" },
];

export function addEvent(data) {
  const event = {
    id: newId("e"),
    title: data.title || "",
    datetime_local: data.datetime_local || "",
    timezone: data.timezone || "Asia/Ho_Chi_Minh",
    confirmed_fact: data.confirmed_fact !== false, // default true
    outcome: data.outcome || "unknown",
    related_person_ids: data.related_person_ids || [],
    related_org_ids: data.related_org_ids || [],
    notes: data.notes || "",
  };
  events.value = [...events.value, event];
  return event;
}

export function updateEvent(id, patch) {
  events.value = events.value.map((e) => (e.id === id ? { ...e, ...patch } : e));
}

export function removeEvent(id) {
  events.value = events.value.filter((e) => e.id !== id);
}

export function getEventById(id) {
  return events.value.find((e) => e.id === id) || null;
}

// -----------------------------------------------------------------------------
// Initialization — load from storage + migrate legacy.
// -----------------------------------------------------------------------------

// NOTE: We intentionally do NOT seed any default profile (previously the
// founder's birth data was used as a "single-user convenience" fallback).
// That leaked anh's personal info (DOB, time, email) to every guest of
// kinhdich.online. Guests now start with an empty profile — the
// ProfilesPanel UI prompts them to add their own person.

function initialize() {
  const stored = loadFromStorage();
  if (stored) {
    persons.value = Array.isArray(stored.persons) ? stored.persons : [];
    families.value = Array.isArray(stored.families) ? stored.families : [];
    organizations.value = Array.isArray(stored.organizations) ? stored.organizations : [];
    events.value = Array.isArray(stored.events) ? stored.events : [];
    activePersonId.value = stored.activePersonId || null;
    return;
  }
  // First-run migration from legacy familyStore v1 (anh's own browser may
  // still have legacy data — keep this migration path so we don't wipe it).
  const legacy = loadLegacyFamily();
  if (legacy && Array.isArray(legacy.members) && legacy.members.length) {
    const migrated = legacy.members.map((m) =>
      addPerson({
        name: m.name,
        role: m.role,
        birth_year: m.birth_year,
        birth_datetime_local: m.birth_datetime_local,
      })
    );
    if (migrated.length) {
      addFamily({
        name: "Gia đình",
        member_ids: migrated.map((p) => p.id),
        wedding_datetime_local: legacy.wedding || "",
      });
    }
    return;
  }
  // Fresh install with no legacy data — leave empty. Panels prompt user
  // to log in or add their own birth profile.
}

initialize();

// -----------------------------------------------------------------------------
// Derived helpers for school panels.
// -----------------------------------------------------------------------------

/**
 * Family members in a serializable format for the family-aware API endpoints
 * (used by van_trong_van + gps). Returns members of the FIRST family by default.
 */
export function serializableFamilyMembers(familyId = null) {
  const fam = familyId ? getFamilyById(familyId) : families.value[0];
  if (!fam) return [];
  return fam.member_ids
    .map((pid) => getPersonById(pid))
    .filter((p) => p && p.birth_year && p.name)
    .map((p) => ({
      role: p.role === "self" ? "self"
          : ["spouse", "child", "parent", "sibling"].includes(p.role) ? p.role
          : "other",
      name: p.name,
      birth_year: Number(p.birth_year),
      birth_datetime_local: p.birth_datetime_local || null,
      timezone: p.timezone || "Asia/Ho_Chi_Minh",
    }));
}

export function getActiveSelfBirthDatetime() {
  if (activePerson.value?.birth_datetime_local) {
    return activePerson.value.birth_datetime_local;
  }
  const selfPerson = persons.value.find((p) => p.role === "self");
  return selfPerson?.birth_datetime_local || "";
}

export function getActiveFirstWeddingDatetime() {
  const fam = families.value[0];
  return fam?.wedding_datetime_local || "";
}
