/**
 * useHexagramModal — singleton-ish modal state for opening hexagram detail.
 *
 * Behavior:
 * - Reading ?que=<slug> from URL on init opens the modal.
 * - openHexagram(kingWenIndex) computes slug and updates URL (?que=...).
 * - closeHexagram() clears URL param.
 * - Slug table is fetched once via /api/hexagram-slugs.
 */

import { onMounted, ref } from "vue";
import { getHexagramSlugs } from "../lib/api";

const slugTable = ref(null);     // { "1": "1-thien-thien-kien", ... }
const slugTableLoading = ref(false);
const openSlug = ref("");

async function ensureSlugTable() {
  if (slugTable.value || slugTableLoading.value) return;
  slugTableLoading.value = true;
  try {
    const resp = await getHexagramSlugs();
    if (resp?.status === "ok") {
      slugTable.value = resp.slugs;
    }
  } catch {
    /* ignore */
  } finally {
    slugTableLoading.value = false;
  }
}

function syncUrl(slug) {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  if (slug) {
    url.searchParams.set("que", slug);
  } else {
    url.searchParams.delete("que");
  }
  window.history.replaceState({}, "", url.toString());
}

function readUrlSlug() {
  if (typeof window === "undefined") return "";
  const url = new URL(window.location.href);
  return url.searchParams.get("que") || "";
}

export function useHexagramModal() {
  onMounted(() => {
    ensureSlugTable();
    const initial = readUrlSlug();
    if (initial) openSlug.value = initial;
  });

  function openHexagram(kingWenIndex) {
    if (!kingWenIndex) return;
    const slug = slugTable.value?.[String(kingWenIndex)];
    if (slug) {
      openSlug.value = slug;
      syncUrl(slug);
    } else {
      // Fallback: API will tolerantly resolve `<kingWenIndex>-x` prefixes.
      const fallback = String(kingWenIndex);
      openSlug.value = fallback;
      syncUrl(fallback);
    }
  }

  function openBySlug(slug) {
    openSlug.value = slug;
    syncUrl(slug);
  }

  function closeHexagram() {
    openSlug.value = "";
    syncUrl("");
  }

  return {
    openSlug,
    openHexagram,
    openBySlug,
    closeHexagram,
  };
}
