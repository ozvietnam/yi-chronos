/**
 * Composable: bind a panel's `inputBirth` ref to the active person's
 * birth datetime, auto-filling on mount and when active person changes,
 * but never overwriting a user's manual edit.
 *
 * Source: userDataStore.activePerson (computed) — merges:
 *   - API-backed user_persons when logged in
 *   - localStorage profileStore when guest
 * Founder fallback handled by /api/auth/me guest response.
 */

import { onMounted, watch } from "vue";

import { activePerson } from "./userDataStore.js";

export function useActivePersonBirth(birthRef, opts = {}) {
  const { onLatLon, onSpan } = opts;

  function fill() {
    if (!birthRef.value && activePerson.value?.birth_datetime_local) {
      birthRef.value = activePerson.value.birth_datetime_local;
    }
  }

  onMounted(fill);
  watch(() => activePerson.value?.birth_datetime_local, (val) => {
    if (val && !birthRef.value) birthRef.value = val;
  });

  // Optional: also propagate location if panel has lat/lon (Western panels do).
  // Caller passes onLatLon callback that receives { lat, lon } strings.
  if (onLatLon) {
    onMounted(() => {
      const loc = activePerson.value?.birth_location;
      if (!loc) return;
      onLatLon(loc);
    });
  }
}
