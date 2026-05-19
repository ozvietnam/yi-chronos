/**
 * wikiTermsStore — load + cache all Tử Vi wiki concepts.
 *
 * Concepts are loaded ONCE on first access. Sorted by length DESC so
 * longest matches win (e.g. "Hóa Lộc" wins over "Lộc").
 */
import { ref, computed } from "vue";

export const concepts = ref([]);
export const loaded = ref(false);
export const loading = ref(false);
export const popupConcept = ref(null);  // currently shown concept in popup

// Build a map for O(1) lookup by canonical_vi (lowercased)
export const byCanonicalVi = computed(() => {
  const out = new Map();
  for (const c of concepts.value) {
    if (c.vi) out.set(c.vi.toLowerCase(), c);
    // Also index aliases
    if (c.aliases) {
      try {
        const parsed = typeof c.aliases === "string" ? JSON.parse(c.aliases) : c.aliases;
        if (Array.isArray(parsed)) {
          for (const a of parsed) out.set(a.toLowerCase(), c);
        } else if (typeof c.aliases === "string") {
          // comma-separated
          for (const a of c.aliases.split(",")) {
            out.set(a.trim().toLowerCase(), c);
          }
        }
      } catch {
        // fall through — treat as comma-separated
        if (typeof c.aliases === "string") {
          for (const a of c.aliases.split(",")) {
            out.set(a.trim().toLowerCase(), c);
          }
        }
      }
    }
  }
  return out;
});

// Sorted by length descending — for greedy matching
export const sortedByLength = computed(() => {
  return [...concepts.value]
    .filter((c) => c.vi && c.vi.length >= 2)
    .sort((a, b) => b.vi.length - a.vi.length);
});

export async function loadConcepts() {
  if (loaded.value || loading.value) return;
  loading.value = true;
  try {
    const r = await fetch("/api/yi-publishing/wiki/all-tuvi");
    const d = await r.json();
    if (d.status === "ok") {
      concepts.value = d.concepts || [];
      loaded.value = true;
    }
  } catch (e) {
    console.error("Failed to load wiki concepts:", e);
  } finally {
    loading.value = false;
  }
}

export function showPopup(concept) {
  popupConcept.value = concept;
}

export function hidePopup() {
  popupConcept.value = null;
}

// Auto-load on first import
loadConcepts();
