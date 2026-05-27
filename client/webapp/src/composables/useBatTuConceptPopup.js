/**
 * useBatTuConceptPopup — click a Bát Tự label (Thập Thần, Cách Cục, Trường Sinh phase,
 * Dụng Thần, Đại Vận, Thần Sát, ...) → fetch wiki concept by canonical name → open the
 * shared WikiPopup.
 *
 * The popup component expects shape { id, vi, zh, note, aliases }, so we adapt the
 * wiki API row to that shape.
 */
import { getConceptByName } from "./useWiki.js";
import { showPopup } from "../stores/wikiTermsStore.js";

const cache = new Map();
const BAT_TU_SCHOOL = "tu_binh_ba_tu";

function adaptToPopup(row) {
  if (!row) return null;
  return {
    id: row.concept_id,
    vi: row.canonical_vi,
    zh: row.canonical_zh,
    note: row.short_note,
    aliases: row.aliases,
  };
}

/**
 * Open the popup for the concept whose canonical name matches `name`.
 * Prefers Bát Tự / Tử Bình school entries (e.g. "Thất Sát 七殺" rather than the
 * Tử Vi homonym "Thất Sát 七杀"). Falls back to ANY school if not found,
 * and finally to a stub popup if the concept is missing entirely.
 */
export async function openConceptPopup(name) {
  if (!name) return;
  const cacheKey = `${BAT_TU_SCHOOL}|${name}`;
  let row = cache.get(cacheKey);
  if (row === undefined) {
    try {
      row = await getConceptByName(name, BAT_TU_SCHOOL);
    } catch (e) {
      console.warn(`[bat-tu] concept lookup failed for ${name}:`, e);
      row = null;
    }
    cache.set(cacheKey, row);
  }
  if (row) {
    showPopup(adaptToPopup(row));
    return;
  }
  // Stub fallback so click feels alive even when wiki entry is missing
  showPopup({
    id: null,
    vi: name,
    zh: null,
    note: "(Chưa có giải nghĩa trong wiki — sẽ bổ sung dần khi đọc thêm sách.)",
    aliases: null,
  });
}
