/**
 * Pure-function utilities for Mai Hoa time-based hexagram derivation.
 *
 * Extracted from MaiHoaClock3D.vue. No DOM, no Three.js — testable in isolation.
 *
 * Convention follows core/hexagram.py TRIGRAM_BITS:
 *   character[0] = top line, character[2] = bottom line
 *   1 = yang, 0 = yin
 */

export const EARTHLY_BRANCHES = [
  "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
  "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
];

export const TRIGRAM_BY_NUMBER = {
  1: "Càn",
  2: "Đoài",
  3: "Ly",
  4: "Chấn",
  5: "Tốn",
  6: "Khảm",
  7: "Cấn",
  8: "Khôn"
};

export const TRIGRAM_BITS = {
  Càn: "111",
  Đoài: "011",
  Ly: "101",
  Chấn: "001",
  Tốn: "110",
  Khảm: "010",
  Cấn: "100",
  Khôn: "000"
};

/**
 * Modulo operation that returns `modulo` instead of 0 for zero remainders,
 * matching the Mai Hoa convention where hexagram numbers are 1-indexed.
 */
export function safeMod(value, modulo) {
  const remainder = value % modulo;
  return remainder === 0 ? modulo : remainder;
}

/**
 * Decompose a Date into year/month/day/hour/minute/second within a timezone.
 * Uses Intl.DateTimeFormat for IANA timezone correctness.
 */
export function zonedDateParts(date, timeZone) {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  });
  const parts = formatter.formatToParts(date);
  const map = {};
  parts.forEach((part) => {
    if (part.type !== "literal") map[part.type] = Number(part.value);
  });
  return {
    year: map.year,
    month: map.month,
    day: map.day,
    hour: map.hour,
    minute: map.minute,
    second: map.second
  };
}

/**
 * Year branch number 1..12 with Tý=1 (1984 = Giáp Tý anchor).
 */
export function yearBranchNumber(year) {
  const branchIndex = ((year - 1984) % 12 + 12) % 12;
  return branchIndex + 1;
}

/**
 * Hour branch number 1..12 with Tý=23:00-00:59, Sửu=01:00-02:59, ...
 */
export function hourBranchNumber(hour24) {
  return ((Math.floor((hour24 + 1) / 2) % 12) + 12) % 12 + 1;
}

/**
 * Compute the full Mai Hoa state from a Date + IANA timezone.
 *
 * Produces upper/lower trigram numbers (1..8) and moving line (1..6) using
 * the standard Niên-Nguyệt-Nhật-Thời formula:
 *   upper  = (yearNum + monthNum + dayNum) mod 8
 *   lower  = (yearNum + monthNum + dayNum + hourNum) mod 8
 *   moving = (yearNum + monthNum + dayNum + hourNum) mod 6
 */
export function computeMaiHoaState(date, timeZone) {
  const parts = zonedDateParts(date, timeZone);
  const yearNum = yearBranchNumber(parts.year);
  const monthNum = parts.month;
  const dayNum = parts.day;
  const hourNum = hourBranchNumber(parts.hour);
  const upper = safeMod(yearNum + monthNum + dayNum, 8);
  const lower = safeMod(yearNum + monthNum + dayNum + hourNum, 8);
  const moving = safeMod(yearNum + monthNum + dayNum + hourNum, 6);
  return {
    ...parts,
    yearNum,
    monthNum,
    dayNum,
    hourNum,
    upper,
    lower,
    moving,
    upperTrigram: TRIGRAM_BY_NUMBER[upper],
    lowerTrigram: TRIGRAM_BY_NUMBER[lower],
    hourBranch: EARTHLY_BRANCHES[hourNum - 1]
  };
}

/**
 * Build human-readable formula strings from a Mai Hoa state.
 */
export function buildFormulaText(state) {
  return {
    upper: `(${state.yearNum} + ${state.monthNum} + ${state.dayNum}) mod 8 = ${state.upper}`,
    lower: `(${state.yearNum} + ${state.monthNum} + ${state.dayNum} + ${state.hourNum}) mod 8 = ${state.lower}`,
    moving: `(${state.yearNum} + ${state.monthNum} + ${state.dayNum} + ${state.hourNum}) mod 6 = ${state.moving}`
  };
}
