/**
 * Backward-compat shim — kept for legacy imports.
 *
 * New code should import from profileStore.js directly.
 * Old code calling `familyMembers`, `weddingDatetime`, `serializableMembers`,
 * `setFamily`, `clearFamily` continues to work transparently — the shim
 * routes through the first Family entity in profileStore.
 */

import { computed } from "vue";
import {
  addFamily,
  addPerson,
  families,
  getFamilyById,
  getPersonById,
  persons,
  removeFamily,
  serializableFamilyMembers,
  updateFamily,
} from "./profileStore.js";

// `familyMembers` returns the editable members array of the first Family.
// Reading: list of { role, name, birth_year, birth_datetime_local } shaped
// like the old API. Writing: mutates Person entities in-place.
export const familyMembers = computed({
  get() {
    const fam = families.value[0];
    if (!fam) return [];
    return fam.member_ids.map((pid) => {
      const p = getPersonById(pid);
      if (!p) return null;
      return {
        role: p.role,
        name: p.name,
        birth_year: p.birth_year,
        birth_datetime_local: p.birth_datetime_local,
        _person_id: p.id,
      };
    }).filter(Boolean);
  },
  set(newMembers) {
    // Replace the first Family's members. Create Persons as needed.
    let fam = families.value[0];
    const memberIds = newMembers.map((m) => {
      if (m._person_id) {
        // Update existing Person.
        const existing = getPersonById(m._person_id);
        if (existing) {
          Object.assign(existing, {
            role: m.role,
            name: m.name,
            birth_year: m.birth_year,
            birth_datetime_local: m.birth_datetime_local || "",
          });
          // Trigger reactivity by replacing array.
          persons.value = [...persons.value];
          return m._person_id;
        }
      }
      const p = addPerson({
        role: m.role,
        name: m.name,
        birth_year: m.birth_year,
        birth_datetime_local: m.birth_datetime_local,
      });
      return p.id;
    });
    if (!fam) {
      fam = addFamily({ name: "Gia đình", member_ids: memberIds });
    } else {
      updateFamily(fam.id, { member_ids: memberIds });
    }
  },
});

export const weddingDatetime = computed({
  get() {
    return families.value[0]?.wedding_datetime_local || "";
  },
  set(value) {
    const fam = families.value[0];
    if (fam) {
      updateFamily(fam.id, { wedding_datetime_local: value });
    } else if (value) {
      addFamily({ name: "Gia đình", member_ids: [], wedding_datetime_local: value });
    }
  },
});

export function setFamily(members, wedding = "") {
  familyMembers.value = members;
  weddingDatetime.value = wedding;
}

export function clearFamily() {
  const fam = families.value[0];
  if (fam) removeFamily(fam.id);
}

export function getSelfBirthDatetime() {
  const self = familyMembers.value.find((m) => m.role === "self");
  return self?.birth_datetime_local || "";
}

export function serializableMembers() {
  return serializableFamilyMembers();
}
